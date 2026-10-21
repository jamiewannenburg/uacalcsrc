"""Derive and check ``testing.scripts[].covers`` lists against test metadata.

YAML ``covers`` lists have drifted from the scripts and golden cases they
claim to describe. Coverage now derives the exercised Java names from:

* dual-runtime script source (``Class.method(`` calls)
* ``method=`` fields in ``tests/parity/*/test_cases/*_cases.py``
* ``method`` fields in golden JSON
* ``testing.task_refs`` files

``check-covers`` fails CI when a script's YAML list does not match the
methods that script actually references (intersected with the contract
surface). ``update-covers`` rewrites the YAML lists in place.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from . import PROJECT_ROOT
from .registry import (
    CONTRACTS_DIR,
    Contract,
    load_all_contracts,
    normalize_surface,
    normalize_testing,
    surface_symbols,
)

_CALL_RE = re.compile(r"\b([A-Z]\w*)\.(\w+)\s*\(")
_CTOR_RE = re.compile(r"\b([A-Z]\w*)\s*\(")
_METHOD_FIELD_RE = re.compile(r"""method\s*=\s*['"]([^'"]+)['"]""")

# Java package prefix -> tests/parity/<dir>
_PARITY_DIR = {
    "org.uacalc.alg.op": "alg_op",
    "org.uacalc.alg.conlat": "conlat",
    "org.uacalc.alg.sublat": "sublat",
    "org.uacalc.alg.parallel": "parallel",
}


def _parity_dir_for_target(target: str) -> Optional[Path]:
    if not target.startswith("org.uacalc."):
        return None
    for prefix, folder in _PARITY_DIR.items():
        if target == prefix or target.startswith(prefix + "."):
            return PROJECT_ROOT / "tests" / "parity" / folder
    rest = target[len("org.uacalc.") :]
    top = rest.split(".", 1)[0]
    path = PROJECT_ROOT / "tests" / "parity" / top
    return path if path.is_dir() else None


def _simple_name(target: str, level: str) -> Optional[str]:
    if level != "file":
        return None
    return target.rsplit(".", 1)[-1]


def methods_referenced_in_source(source: str) -> Dict[str, Set[str]]:
    """Map Java class simple name -> method/constructor names referenced."""
    by_class: Dict[str, Set[str]] = {}
    for cls, meth in _CALL_RE.findall(source):
        by_class.setdefault(cls, set()).add(meth)
    for cls in _CTOR_RE.findall(source):
        by_class.setdefault(cls, set()).add(cls)
    for match in _METHOD_FIELD_RE.findall(source):
        if "." in match:
            cls, meth = match.rsplit(".", 1)
            by_class.setdefault(cls, set()).add(meth)
        else:
            by_class.setdefault("", set()).add(match)
    return by_class


def methods_referenced_in_file(path: Path) -> Dict[str, Set[str]]:
    if not path.is_file():
        return {}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    if path.suffix == ".json":
        by_class: Dict[str, Set[str]] = {}
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return {}
        for case in data.get("test_cases") or []:
            method_full = case.get("method") or ""
            if "." in method_full:
                cls, meth = method_full.rsplit(".", 1)
                by_class.setdefault(cls, set()).add(meth)
            elif method_full:
                by_class.setdefault("", set()).add(method_full)
        return by_class
    return methods_referenced_in_source(text)


def _union_for_class(maps: Iterable[Dict[str, Set[str]]], cls: str) -> Set[str]:
    out: Set[str] = set()
    for mapping in maps:
        out.update(mapping.get(cls) or set())
        out.update(mapping.get("") or set())
    return out


def golden_and_case_maps(target: str) -> List[Dict[str, Set[str]]]:
    parity = _parity_dir_for_target(target)
    maps: List[Dict[str, Set[str]]] = []
    if parity is None:
        return maps
    cases = parity / "test_cases"
    if cases.is_dir():
        for path in sorted(cases.glob("*_cases.py")):
            maps.append(methods_referenced_in_file(path))
    golden = parity / "golden_data"
    if golden.is_dir():
        for path in sorted(golden.glob("*_jython.json")):
            maps.append(methods_referenced_in_file(path))
    return maps


def _symbol_mentioned(source: str, symbol: str) -> bool:
    """True if ``symbol`` is invoked in Python source (Class.sym / .sym / sym)."""
    simple = symbol.split(".")[-1]
    if not simple:
        return False
    escaped = re.escape(simple)
    if re.search(rf"\.{escaped}\s*\(", source):
        return True
    if re.search(rf"\b{escaped}\s*\(", source):
        return True
    if re.search(rf"method\s*=\s*['\"][^'\"]*\b{escaped}['\"]", source):
        return True
    return False


def derived_script_covers(contract: Contract, script_path: str) -> List[str]:
    """Covers list a script should declare for this contract."""
    surface = surface_symbols(contract.surface)
    path = PROJECT_ROOT / script_path
    if not path.is_file():
        return []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return sorted({sym for sym in surface if _symbol_mentioned(source, sym)})


def derived_contract_covers(contract: Contract) -> Set[str]:
    """All surface symbols exercised by scripts, task_refs, and goldens."""
    surface = set(surface_symbols(contract.surface))
    simple = _simple_name(contract.target, contract.level) or ""
    maps: List[Dict[str, Set[str]]] = []
    testing = normalize_testing(contract.testing)
    for script in testing["scripts"]:
        maps.append(methods_referenced_in_file(PROJECT_ROOT / script["path"]))
    for ref in testing["task_refs"]:
        maps.append(methods_referenced_in_file(PROJECT_ROOT / ref))
    maps.extend(golden_and_case_maps(contract.target))
    names = _union_for_class(maps, simple) if simple else set()
    if not simple:
        for mapping in maps:
            for group in mapping.values():
                names.update(group)
    return names & surface


class CoverMismatch:
    def __init__(self, target: str, script: str, yaml_covers: List[str], derived: List[str]):
        self.target = target
        self.script = script
        self.yaml_covers = yaml_covers
        self.derived = derived

    @property
    def missing(self) -> List[str]:
        return sorted(set(self.derived) - set(self.yaml_covers))

    @property
    def extra(self) -> List[str]:
        return sorted(set(self.yaml_covers) - set(self.derived))


def collect_cover_mismatches(
    contracts_dir: Optional[Path] = None,
) -> List[CoverMismatch]:
    contracts = load_all_contracts(contracts_dir or CONTRACTS_DIR)
    mismatches: List[CoverMismatch] = []
    for target, contract in sorted(contracts.items()):
        if contract.status == "ignored":
            continue
        testing = normalize_testing(contract.testing)
        for script in testing["scripts"]:
            derived = derived_script_covers(contract, script["path"])
            yaml_covers = sorted(set(script["covers"]))
            if yaml_covers != derived:
                mismatches.append(
                    CoverMismatch(target, script["path"], yaml_covers, derived)
                )
    return mismatches


def format_cover_mismatches(mismatches: List[CoverMismatch]) -> str:
    if not mismatches:
        return "OK: testing.scripts covers lists match derived script metadata.\n"
    lines = [
        f"{len(mismatches)} stale testing.scripts covers list(s):",
        "Run: python3 tools/jython_contracts_cli.py update-covers",
        "",
    ]
    for item in mismatches:
        lines.append(f"{item.target}  {item.script}")
        if item.missing:
            lines.append(f"  missing: {', '.join(item.missing)}")
        if item.extra:
            lines.append(f"  extra:   {', '.join(item.extra)}")
        lines.append(f"  derived: {item.derived}")
    return "\n".join(lines) + "\n"


def _format_covers_yaml(covers: List[str], indent: str) -> str:
    if not covers:
        return f"{indent}covers: []\n"
    lines = [f"{indent}covers:"]
    for name in covers:
        lines.append(f"{indent}  - {name}")
    return "\n".join(lines) + "\n"


def _replace_script_covers_block(text: str, script_path: str, covers: List[str]) -> str:
    """Replace the covers list belonging to ``path: <script_path>``."""
    path_re = re.compile(
        r"^([ \t]+)- path: " + re.escape(script_path) + r"[ \t]*\n",
        re.MULTILINE,
    )
    match = path_re.search(text)
    if not match:
        return text
    indent = match.group(1) + "  "
    # From just after the path line, find `covers:` at indent
    rest_start = match.end()
    covers_re = re.compile(
        r"^" + re.escape(indent) + r"covers:[ \t]*(?:\[\][ \t]*)?\n"
        r"(?:" + re.escape(indent) + r"  -[^\n]*\n)*",
        re.MULTILINE,
    )
    sub = covers_re.search(text, rest_start)
    if not sub:
        # insert covers after the path line
        insertion = _format_covers_yaml(covers, indent)
        return text[:rest_start] + insertion + text[rest_start:]
    return text[: sub.start()] + _format_covers_yaml(covers, indent) + text[sub.end() :]


def update_cover_lists(contracts_dir: Optional[Path] = None) -> int:
    """Rewrite stale YAML covers lists. Returns number of files changed."""
    contracts = load_all_contracts(contracts_dir or CONTRACTS_DIR)
    changed = 0
    by_path: Dict[Path, List[Tuple[str, List[str]]]] = {}
    for contract in contracts.values():
        if contract.status == "ignored" or contract.path is None:
            continue
        testing = normalize_testing(contract.testing)
        updates: List[Tuple[str, List[str]]] = []
        for script in testing["scripts"]:
            derived = derived_script_covers(contract, script["path"])
            if sorted(script["covers"]) != derived:
                updates.append((script["path"], derived))
        if updates:
            by_path.setdefault(contract.path, []).extend(updates)
    for path, updates in by_path.items():
        text = path.read_text(encoding="utf-8")
        original = text
        for script_path, covers in updates:
            text = _replace_script_covers_block(text, script_path, covers)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    return changed
