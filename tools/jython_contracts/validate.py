"""Validate Jython contracts against the python/org shim."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from . import ORG_SHIM_ROOT, PROJECT_ROOT
from .registry import Contract, load_all_contracts, normalize_surface, normalize_testing


@dataclass
class ValidationIssue:
    severity: str  # error | warning
    target: str
    message: str


def _shim_module_path(java_package: str) -> Path:
    """Map org.uacalc.alg -> python/org/uacalc/alg/__init__.py"""
    if not java_package.startswith("org.uacalc"):
        raise ValueError(f"Expected org.uacalc.* package, got {java_package}")
    rel = java_package[len("org.") :].replace(".", "/")
    return PROJECT_ROOT / "python" / "org" / rel / "__init__.py"


def _package_of(target: str, level: str) -> str:
    if level == "package":
        return target
    return target.rsplit(".", 1)[0]


def _read_shim(package: str) -> Optional[str]:
    path = _shim_module_path(package)
    if not path.exists():
        return None
    parts = [path.read_text(encoding="utf-8")]
    # Jython bridges often live in a sibling _jython_compat.py (io, alg, …).
    compat = path.parent / "_jython_compat.py"
    if compat.exists():
        parts.append(compat.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _assigned_aliases_in_shim(shim_source: str) -> Dict[str, Set[str]]:
    """
    Detect patterns like:
      cls.getUniverseList = cls.get_universe_list
      SomeClass.getName = SomeClass.name
      _CLASS_ALIASES = { 'BasicAlgebra': { 'getUniverseList': 'get_universe_list', ... } }
    Returns mapping class_name -> set of camelCase alias names assigned.
    """
    result: Dict[str, Set[str]] = {}

    def _ingest_class_aliases_dict(node: ast.AST) -> None:
        if not isinstance(node, ast.Assign):
            return
        for target in node.targets:
            if not (isinstance(target, ast.Name) and target.id == "_CLASS_ALIASES"):
                continue
            if not isinstance(node.value, ast.Dict):
                continue
            for key, val in zip(node.value.keys, node.value.values):
                if key is None or not isinstance(val, ast.Dict):
                    continue
                class_name = _ast_str(key)
                if class_name is None:
                    continue
                aliases: Set[str] = set()
                for alias_key in val.keys:
                    name = _ast_str(alias_key) if alias_key is not None else None
                    if name is not None:
                        aliases.add(name)
                result.setdefault(class_name, set()).update(aliases)

    try:
        tree = ast.parse(shim_source)
        for node in ast.walk(tree):
            _ingest_class_aliases_dict(node)
    except SyntaxError:
        pass

    # Direct: ClassName.alias = ClassName.something
    for m in re.finditer(
        r"(\w+)\.([A-Za-z_]\w*)\s*=\s*\1\.([A-Za-z_]\w*)",
        shim_source,
    ):
        cls, alias, _impl = m.group(1), m.group(2), m.group(3)
        result.setdefault(cls, set()).add(alias)

    # cls.alias = cls.impl after cls = globals()['Name'] or if 'Name' in globals
    current: Optional[str] = None
    for line in shim_source.splitlines():
        m_if = re.search(r"""if\s+['"](\w+)['"]\s+in\s+globals\(\)""", line)
        if m_if:
            current = m_if.group(1)
            continue
        m_cls = re.search(r"""cls\s*=\s*globals\(\)\[['\"](\w+)['\"]\]""", line)
        if m_cls:
            current = m_cls.group(1)
            continue
        m_assign = re.search(r"cls\.([A-Za-z_]\w*)\s*=\s*cls\.([A-Za-z_]\w*)", line)
        if m_assign and current:
            result.setdefault(current, set()).add(m_assign.group(1))
    return result


def _ast_str(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    # Python <3.8 compatibility (unlikely here, but cheap)
    if hasattr(ast, "Str") and isinstance(node, getattr(ast, "Str")):
        return node.s  # type: ignore[attr-defined]
    return None


def _static_methods_in_shim(shim_source: str) -> Dict[str, Set[str]]:
    """
    Find class bodies with methods, e.g. AlgebraIO.readAlgebraFile.
    Walks nested If/etc so shims gated on is_jython are still seen.
    """
    result: Dict[str, Set[str]] = {}
    try:
        tree = ast.parse(shim_source)
    except SyntaxError:
        for m in re.finditer(
            r"class\s+(\w+)\s*:(.*?)(?=\nclass\s|\Z)",
            shim_source,
            re.DOTALL,
        ):
            cls, body = m.group(1), m.group(2)
            methods = set(re.findall(r"def\s+(\w+)\s*\(", body))
            result[cls] = methods
        return result

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods: Set[str] = set()
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.add(item.name)
            result[node.name] = methods
    return result


def _simple_name(target: str, level: str) -> str:
    if level == "package":
        return target.rsplit(".", 1)[-1]
    return target.rsplit(".", 1)[-1]


def validate_contracts(
    contracts_dir=None,
) -> List[ValidationIssue]:
    contracts = load_all_contracts(contracts_dir) if contracts_dir else load_all_contracts()
    issues: List[ValidationIssue] = []

    for target, contract in sorted(contracts.items()):
        # Schema / consistency
        if contract.status == "ignored" and not contract.ignore_reason:
            issues.append(
                ValidationIssue("error", target, "ignored status without ignore_reason")
            )

        if contract.level == "file" and contract.java_source:
            java_path = PROJECT_ROOT / contract.java_source
            if not java_path.exists():
                issues.append(
                    ValidationIssue(
                        "error",
                        target,
                        f"java_source does not exist: {contract.java_source}",
                    )
                )

        surface = normalize_surface(contract.surface)
        has_surface = bool(surface["aliases"] or surface["static_methods"] or surface["str_parity"])

        try:
            testing = normalize_testing(contract.testing)
        except ValueError as e:
            issues.append(ValidationIssue("error", target, str(e)))
            testing = normalize_testing({})

        for script in testing["scripts"]:
            script_path = PROJECT_ROOT / script["path"]
            if not script_path.is_file():
                issues.append(
                    ValidationIssue(
                        "error",
                        target,
                        f"testing script not found: {script['path']}",
                    )
                )
        for ref in testing["task_refs"]:
            ref_path = PROJECT_ROOT / ref
            if not ref_path.exists():
                issues.append(
                    ValidationIssue(
                        "warning",
                        target,
                        f"testing.task_refs path not found: {ref}",
                    )
                )

        if (
            contract.status == "implemented"
            and has_surface
            and not testing["scripts"]
            and not testing["notes"].strip()
        ):
            issues.append(
                ValidationIssue(
                    "warning",
                    target,
                    "implemented surface has no testing.notes or testing.scripts",
                )
            )

        if contract.status == "pending" and has_surface:
            issues.append(
                ValidationIssue(
                    "warning",
                    target,
                    "contract declares surface but status is still pending",
                )
            )

        if contract.status == "ignored":
            continue

        if not has_surface and contract.status == "implemented" and contract.level == "file":
            issues.append(
                ValidationIssue(
                    "warning",
                    target,
                    "implemented file contract has empty surface",
                )
            )

        package = _package_of(contract.target, contract.level)
        shim = _read_shim(package)
        if shim is None:
            if contract.status == "implemented" or has_surface:
                issues.append(
                    ValidationIssue(
                        "error",
                        target,
                        f"no python/org shim module for package {package}",
                    )
                )
            continue

        aliases_by_class = _assigned_aliases_in_shim(shim)
        statics_by_class = _static_methods_in_shim(shim)
        simple = _simple_name(contract.target, contract.level)

        if contract.level == "file":
            expected_aliases = surface["aliases"]
            present = aliases_by_class.get(simple, set())
            # Also accept aliases applied when class name used directly
            for alias in expected_aliases:
                if alias not in present:
                    # Search looser: any assignment of .alias =
                    if not re.search(rf"\b{re.escape(alias)}\s*=", shim):
                        issues.append(
                            ValidationIssue(
                                "error",
                                target,
                                f"alias {alias!r} -> {expected_aliases[alias]!r} "
                                f"not found on {simple} in shim {package}",
                            )
                        )

            for method in surface["static_methods"]:
                # static_methods may be listed as Class.method or method
                if "." in method:
                    cls_name, meth = method.split(".", 1)
                else:
                    cls_name, meth = simple, method
                methods = statics_by_class.get(cls_name, set())
                if meth not in methods and not re.search(
                    rf"def\s+{re.escape(meth)}\s*\(", shim
                ):
                    issues.append(
                        ValidationIssue(
                            "error",
                            target,
                            f"static method {cls_name}.{meth} not found in shim",
                        )
                    )
        else:
            # Package-level: check static_methods and any aliases mentioned
            for method in surface["static_methods"]:
                if "." in method:
                    cls_name, meth = method.split(".", 1)
                else:
                    # Ambiguous at package level
                    cls_name, meth = None, method
                if cls_name:
                    methods = statics_by_class.get(cls_name, set())
                    if meth not in methods:
                        issues.append(
                            ValidationIssue(
                                "error",
                                target,
                                f"static method {cls_name}.{meth} not found in shim",
                            )
                        )
                else:
                    if not re.search(rf"def\s+{re.escape(meth)}\s*\(", shim):
                        issues.append(
                            ValidationIssue(
                                "error",
                                target,
                                f"static method {meth} not found in shim",
                            )
                        )

            for alias, impl in surface["aliases"].items():
                if not re.search(rf"\b{re.escape(alias)}\s*=", shim):
                    issues.append(
                        ValidationIssue(
                            "warning",
                            target,
                            f"package-level alias {alias!r} not found in shim "
                            f"(prefer file-level contracts for class aliases)",
                        )
                    )

    return issues


def format_issues(issues: List[ValidationIssue]) -> str:
    if not issues:
        return "OK: all contracts valid.\n"
    lines = []
    errors = sum(1 for i in issues if i.severity == "error")
    warnings = sum(1 for i in issues if i.severity == "warning")
    for issue in issues:
        lines.append(f"{issue.severity.upper()}: {issue.target}: {issue.message}")
    lines.append(f"\n{errors} error(s), {warnings} warning(s)")
    return "\n".join(lines) + "\n"
