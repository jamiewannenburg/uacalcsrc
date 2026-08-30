"""Load, merge, and update hierarchical Jython compatibility contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

from . import (
    CONTRACTS_DIR,
    JAVA_ROOT,
    PROJECT_ROOT,
    VALID_LEVELS,
    VALID_STATUSES,
)

SURFACE_KEYS = ("package_export", "aliases", "static_methods", "str_parity")


@dataclass
class Contract:
    """A single package- or file-level contract loaded from YAML."""

    target: str
    level: str
    status: str
    java_source: Optional[str] = None
    notes: str = ""
    ignore_reason: Optional[str] = None
    surface: Dict[str, Any] = field(default_factory=dict)
    testing: Dict[str, Any] = field(default_factory=dict)
    path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "level": self.level,
            "status": self.status,
            "java_source": self.java_source,
            "notes": self.notes,
            "ignore_reason": self.ignore_reason,
            "surface": normalize_surface(self.surface),
            "testing": normalize_testing(self.testing),
        }


def normalize_surface(surface: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    surface = surface or {}
    aliases = surface.get("aliases") or {}
    if not isinstance(aliases, dict):
        raise ValueError("surface.aliases must be a mapping")
    static_methods = surface.get("static_methods") or []
    if not isinstance(static_methods, list):
        raise ValueError("surface.static_methods must be a list")
    return {
        "package_export": bool(surface.get("package_export", True)),
        "aliases": {str(k): str(v) for k, v in aliases.items()},
        "static_methods": [str(m) for m in static_methods],
        "str_parity": bool(surface.get("str_parity", False)),
    }


def empty_surface() -> Dict[str, Any]:
    return normalize_surface({})


def normalize_testing(testing: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    testing:
      notes: free-form how-to-test / expected observations
      task_refs: optional links to tasks/*.md Testing Strategy sections
      scripts:
        - path: jython_comparison/scripts/foo.py
          covers: [getName, AlgebraIO.readAlgebraFile, ...]
          ignore_lines: ["Universe:"]   # optional stdout prefixes to skip in diff
    """
    testing = testing or {}
    notes = testing.get("notes") or ""
    task_refs = testing.get("task_refs") or []
    if not isinstance(task_refs, list):
        raise ValueError("testing.task_refs must be a list")
    scripts_raw = testing.get("scripts") or []
    if not isinstance(scripts_raw, list):
        raise ValueError("testing.scripts must be a list")
    scripts: List[Dict[str, Any]] = []
    for entry in scripts_raw:
        if isinstance(entry, str):
            scripts.append({"path": entry, "covers": [], "ignore_lines": []})
            continue
        if not isinstance(entry, dict) or not entry.get("path"):
            raise ValueError("testing.scripts entries need a path")
        covers = entry.get("covers") or []
        ignore_lines = entry.get("ignore_lines") or []
        if not isinstance(covers, list) or not isinstance(ignore_lines, list):
            raise ValueError("testing.scripts covers/ignore_lines must be lists")
        scripts.append(
            {
                "path": str(entry["path"]),
                "covers": [str(c) for c in covers],
                "ignore_lines": [str(x) for x in ignore_lines],
            }
        )
    return {
        "notes": str(notes),
        "task_refs": [str(t) for t in task_refs],
        "scripts": scripts,
    }


def empty_testing() -> Dict[str, Any]:
    return normalize_testing({})


def merge_testing(*blocks: Dict[str, Any]) -> Dict[str, Any]:
    """Merge testing blocks; later wins for notes, scripts unioned by path (later wins)."""
    notes_parts: List[str] = []
    task_refs: List[str] = []
    scripts_by_path: Dict[str, Dict[str, Any]] = {}
    for block in blocks:
        if not block:
            continue
        t = normalize_testing(block)
        if t["notes"].strip():
            notes_parts.append(t["notes"].strip())
        for ref in t["task_refs"]:
            if ref not in task_refs:
                task_refs.append(ref)
        for script in t["scripts"]:
            scripts_by_path[script["path"]] = script
    return {
        "notes": "\n\n".join(notes_parts),
        "task_refs": task_refs,
        "scripts": list(scripts_by_path.values()),
    }


def surface_symbols(surface: Dict[str, Any]) -> List[str]:
    """Public-facing symbols declared on a contract surface (for coverage)."""
    s = normalize_surface(surface)
    symbols: List[str] = []
    for alias in s["aliases"]:
        symbols.append(alias)
    for method in s["static_methods"]:
        symbols.append(method)
    if s["str_parity"]:
        symbols.append("__str__")
    return symbols


def collect_script_entries(
    contracts: Optional[Dict[str, Contract]] = None,
    contracts_dir: Path = CONTRACTS_DIR,
) -> List[Dict[str, Any]]:
    """All unique parity scripts referenced by contracts, keyed by path."""
    contracts = contracts if contracts is not None else load_all_contracts(contracts_dir)
    by_path: Dict[str, Dict[str, Any]] = {}
    for contract in contracts.values():
        testing = normalize_testing(contract.testing)
        for script in testing["scripts"]:
            path = script["path"]
            if path not in by_path:
                by_path[path] = {
                    "path": path,
                    "covers": list(script["covers"]),
                    "ignore_lines": list(script["ignore_lines"]),
                    "contracts": [contract.target],
                }
            else:
                for c in script["covers"]:
                    if c not in by_path[path]["covers"]:
                        by_path[path]["covers"].append(c)
                for line in script["ignore_lines"]:
                    if line not in by_path[path]["ignore_lines"]:
                        by_path[path]["ignore_lines"].append(line)
                by_path[path]["contracts"].append(contract.target)
    return list(by_path.values())


def contract_path_for(target: str, contracts_dir: Path = CONTRACTS_DIR) -> Path:
    return contracts_dir / f"{target}.yaml"


def infer_level(target: str) -> str:
    """Infer package vs file from whether a matching .java type exists."""
    java_path = fqcn_to_java_path(target)
    if java_path is not None and java_path.exists():
        return "file"
    package_dir = PROJECT_ROOT / "org" / target.replace(".", "/")
    if package_dir.is_dir():
        return "package"
    # Heuristic: Capitalized final segment => file/class
    final = target.rsplit(".", 1)[-1]
    if final and final[0].isupper():
        return "file"
    return "package"


def fqcn_to_java_path(fqcn: str) -> Optional[Path]:
    if not fqcn.startswith("org.uacalc."):
        rel = fqcn.replace(".", "/") + ".java"
        candidate = PROJECT_ROOT / "org" / rel
        return candidate if candidate.exists() else PROJECT_ROOT / "org" / rel
    rel = fqcn[len("org.") :].replace(".", "/") + ".java"
    return PROJECT_ROOT / "org" / rel


def java_path_to_fqcn(java_path: Path) -> str:
    rel = java_path.resolve().relative_to((PROJECT_ROOT / "org").resolve())
    return "org." + str(rel.with_suffix("")).replace("/", ".")


def package_prefixes(target: str) -> List[str]:
    """Return package prefixes from most general to most specific (excluding target if file)."""
    parts = target.split(".")
    prefixes = []
    for i in range(1, len(parts)):
        prefixes.append(".".join(parts[:i]))
    return prefixes


def ancestor_package_targets(target: str, level: Optional[str] = None) -> List[str]:
    """Package contract targets that apply to this target, general → specific."""
    level = level or infer_level(target)
    parts = target.split(".")
    if level == "file":
        parts = parts[:-1]
    result = []
    # Only consider packages under org.uacalc
    for i in range(2, len(parts) + 1):  # start at org.uacalc
        pkg = ".".join(parts[:i])
        if pkg.startswith("org.uacalc"):
            result.append(pkg)
    return result


def load_contract(path: Path) -> Contract:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Contract must be a mapping: {path}")
    target = data.get("target")
    if not target:
        # Derive from filename
        target = path.stem
    level = data.get("level") or infer_level(target)
    status = data.get("status", "pending")
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid level {level!r} in {path}")
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status {status!r} in {path}")
    if status == "ignored" and not data.get("ignore_reason"):
        raise ValueError(f"status=ignored requires ignore_reason in {path}")
    return Contract(
        target=target,
        level=level,
        status=status,
        java_source=data.get("java_source"),
        notes=data.get("notes") or "",
        ignore_reason=data.get("ignore_reason"),
        surface=normalize_surface(data.get("surface")),
        testing=normalize_testing(data.get("testing")),
        path=path,
    )


def save_contract(contract: Contract, contracts_dir: Path = CONTRACTS_DIR) -> Path:
    contracts_dir.mkdir(parents=True, exist_ok=True)
    path = contract.path or contract_path_for(contract.target, contracts_dir)
    contract.path = path
    data = contract.to_dict()
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return path


def load_all_contracts(contracts_dir: Path = CONTRACTS_DIR) -> Dict[str, Contract]:
    contracts: Dict[str, Contract] = {}
    if not contracts_dir.exists():
        return contracts
    for path in sorted(contracts_dir.glob("*.yaml")):
        if path.name.lower() == "readme.yaml":
            continue
        contract = load_contract(path)
        contracts[contract.target] = contract
    return contracts


def merge_surfaces(*surfaces: Dict[str, Any]) -> Dict[str, Any]:
    """Merge surfaces; later entries win on conflicts."""
    result = empty_surface()
    for surface in surfaces:
        if not surface:
            continue
        s = normalize_surface(surface)
        # package_export / str_parity: later wins
        result["package_export"] = s["package_export"]
        result["str_parity"] = s["str_parity"]
        # aliases: merge, later overwrites keys
        result["aliases"].update(s["aliases"])
        # static_methods: union preserving order, later additions appended
        seen = set(result["static_methods"])
        for method in s["static_methods"]:
            if method not in seen:
                result["static_methods"].append(method)
                seen.add(method)
            # If redefined conceptually we keep first listing; surface methods are names only
        # Prefer later list if it explicitly replaces? Plan says file wins — for lists,
        # if later has any static_methods, replace entirely when later is non-empty and
        # we want file override. Simpler: union is fine for additive surface.
    return result


def merge_contracts(chain: List[Contract]) -> Contract:
    """Merge general→refined contracts; last wins for status/notes/surface conflicts."""
    if not chain:
        raise ValueError("Cannot merge empty contract chain")
    base = chain[0]
    status = base.status
    ignore_reason = base.ignore_reason
    notes_parts = [base.notes.strip()] if base.notes and base.notes.strip() else []
    java_source = base.java_source
    surfaces = [base.surface]
    testing_blocks = [base.testing]
    target = chain[-1].target
    level = chain[-1].level

    for contract in chain[1:]:
        status = contract.status
        if contract.ignore_reason:
            ignore_reason = contract.ignore_reason
        elif contract.status != "ignored":
            ignore_reason = None
        if contract.notes:
            notes_parts.append(contract.notes.strip())
        if contract.java_source:
            java_source = contract.java_source
        surfaces.append(contract.surface)
        testing_blocks.append(contract.testing)
        target = contract.target
        level = contract.level

    return Contract(
        target=target,
        level=level,
        status=status,
        java_source=java_source,
        notes="\n\n".join(p for p in notes_parts if p),
        ignore_reason=ignore_reason,
        surface=merge_surfaces(*surfaces),
        testing=merge_testing(*testing_blocks),
        path=chain[-1].path,
    )


def resolution_chain(
    target: str,
    contracts: Optional[Dict[str, Contract]] = None,
    contracts_dir: Path = CONTRACTS_DIR,
) -> List[Contract]:
    """
    Load contracts from most general package to most refined file for target.
    Only includes contracts that exist on disk.
    """
    contracts = contracts if contracts is not None else load_all_contracts(contracts_dir)
    level = infer_level(target)
    chain: List[Contract] = []
    for pkg in ancestor_package_targets(target, level=level):
        if pkg in contracts and contracts[pkg].level == "package":
            chain.append(contracts[pkg])
        elif pkg in contracts:
            chain.append(contracts[pkg])
    if target in contracts:
        # Avoid duplicating if target is a package already added
        if not chain or chain[-1].target != target:
            chain.append(contracts[target])
    return chain


def effective_contract(
    target: str,
    contracts: Optional[Dict[str, Contract]] = None,
    contracts_dir: Path = CONTRACTS_DIR,
) -> Optional[Contract]:
    chain = resolution_chain(target, contracts=contracts, contracts_dir=contracts_dir)
    if not chain:
        return None
    return merge_contracts(chain)


def effective_status(
    target: str,
    contracts: Optional[Dict[str, Contract]] = None,
    contracts_dir: Path = CONTRACTS_DIR,
) -> str:
    """
    Effective status for a type/package.
    Package ignored covers children unless a more refined contract overrides.
    No contract => pending.
    """
    eff = effective_contract(target, contracts=contracts, contracts_dir=contracts_dir)
    if eff is None:
        # Inherited ignore from nearest ancestor package even without file contract
        contracts = contracts if contracts is not None else load_all_contracts(contracts_dir)
        for pkg in reversed(ancestor_package_targets(target, level="file")):
            if pkg in contracts:
                return contracts[pkg].status
        return "pending"
    return eff.status


def discover_java_types(
    java_root: Path = JAVA_ROOT,
    exclude_packages: Iterable[str] = (),
) -> List[Tuple[str, Path]]:
    """
    Discover public top-level types under org/uacalc.
    Returns list of (fqcn, path) sorted by fqcn.
    """
    exclude = set(exclude_packages)
    results: List[Tuple[str, Path]] = []
    if not java_root.exists():
        return results

    public_type = re.compile(
        r"^\s*public\s+(?:abstract\s+|final\s+)*(?:class|interface|enum)\s+(\w+)",
        re.MULTILINE,
    )

    for path in sorted(java_root.rglob("*.java")):
        if path.name == "package-info.java":
            continue
        rel = path.relative_to(java_root)
        # First path component under uacalc
        parts = rel.parts
        if parts and parts[0] in exclude:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        # Prefer type matching filename
        stem = path.stem
        fqcn = "org.uacalc." + str(rel.with_suffix("")).replace("/", ".")
        # Verify a public type with that name exists (or any public type)
        names = public_type.findall(text)
        if stem in names or (names and stem == names[0]):
            results.append((fqcn, path))
        elif names:
            # Nested/extra public types in file — still index primary by filename if public
            # Only include if filename type is declared somehow
            type_decl = re.search(
                rf"^\s*public\s+(?:abstract\s+|final\s+)*(?:class|interface|enum)\s+{re.escape(stem)}\b",
                text,
                re.MULTILINE,
            )
            if type_decl:
                results.append((fqcn, path))
        else:
            # Non-public primary — skip
            continue
    return results


def init_contract(
    target: str,
    level: Optional[str] = None,
    status: str = "pending",
    contracts_dir: Path = CONTRACTS_DIR,
    force: bool = False,
) -> Contract:
    level = level or infer_level(target)
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid level: {level}")
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    path = contract_path_for(target, contracts_dir)
    if path.exists() and not force:
        raise FileExistsError(f"Contract already exists: {path}")

    java_source = None
    if level == "file":
        jp = fqcn_to_java_path(target)
        if jp is not None:
            try:
                java_source = str(jp.resolve().relative_to(PROJECT_ROOT.resolve()))
            except ValueError:
                java_source = str(jp)

    contract = Contract(
        target=target,
        level=level,
        status=status,
        java_source=java_source,
        notes="",
        ignore_reason=None,
        surface=empty_surface(),
        testing=empty_testing(),
        path=path,
    )
    save_contract(contract, contracts_dir)
    return contract


def set_status(
    target: str,
    status: str,
    reason: Optional[str] = None,
    contracts_dir: Path = CONTRACTS_DIR,
) -> Contract:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    if status == "ignored" and not reason:
        raise ValueError("--reason is required when status is ignored")

    path = contract_path_for(target, contracts_dir)
    if path.exists():
        contract = load_contract(path)
    else:
        contract = init_contract(target, contracts_dir=contracts_dir)

    contract.status = status
    contract.ignore_reason = reason if status == "ignored" else None
    save_contract(contract, contracts_dir)
    return contract


def format_contract(contract: Contract) -> str:
    return yaml.safe_dump(contract.to_dict(), default_flow_style=False, sort_keys=False)
