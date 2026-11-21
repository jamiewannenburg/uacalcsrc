#!/usr/bin/env python3
"""Fail CI when an xfail / ignore reason lacks an allowed category prefix."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

ALLOWED_PREFIXES = (
    "Known Java bug:",
    "Rust gap:",
    "Wrapper bug:",
    "Environment:",
)

IGNORE_ATTR_RE = re.compile(r'#\[ignore\s*=\s*"([^"]+)"\]')
XFAIL_KWARG_RE = re.compile(
    r"pytest\.mark\.xfail\s*\([^)]*reason\s*=\s*"
    r'(?:"([^"]*)"|\'([^\']*)\'|r"([^"]*)"|r\'([^\']*)\')',
    re.DOTALL,
)


def _ok(reason: str) -> bool:
    reason = (reason or "").strip()
    if not reason:
        return True
    return any(reason.startswith(p) for p in ALLOWED_PREFIXES)


def _scan_py_xfail_markers(path: Path, violations: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for m in XFAIL_KWARG_RE.finditer(text):
        reason = next(g for g in m.groups() if g is not None)
        if not _ok(reason):
            violations.append(f"{path}: pytest.mark.xfail: {reason[:120]!r}")


def _scan_case_module(path: Path, violations: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if "xfail_reason" not in text:
        return
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        violations.append(f"{path}: parse error: {exc}")
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Name)
            and func.id == "TestCaseSpec"
            or isinstance(func, ast.Attribute)
            and func.attr == "TestCaseSpec"
        ):
            continue
        for kw in node.keywords:
            if kw.arg != "xfail_reason":
                continue
            reason = _const_str(kw.value)
            if reason is not None and not _ok(reason):
                violations.append(f"{path}: TestCaseSpec xfail_reason: {reason[:120]!r}")


def _const_str(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return None
    if isinstance(node, ast.Tuple):
        parts = [_const_str(elt) for elt in node.elts]
        if all(p is not None for p in parts):
            return "".join(parts)  # type: ignore[arg-type]
    if isinstance(node, ast.Name):
        return None
    return None


def _scan_rs_ignores(path: Path, violations: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for m in IGNORE_ATTR_RE.finditer(text):
        reason = m.group(1)
        if not _ok(reason):
            violations.append(f"{path}: #[ignore]: {reason[:120]!r}")
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("//!"):
            continue
        if "#[ignore]" in line and "ignore =" not in line:
            violations.append(
                f"{path}:{line_no}: #[ignore] without reason (use #[ignore = \"...\"])"
            )


def _scan_loaded_case_specs(violations: list[str]) -> None:
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    try:
        from generate_golden_data import load_test_cases
    except ImportError:
        return
    packages = [
        p.name
        for p in (REPO_ROOT / "tests" / "parity").iterdir()
        if p.is_dir() and (p / "test_cases").is_dir()
    ]
    for package in sorted(packages):
        try:
            specs = load_test_cases(package, None)
        except Exception as exc:
            violations.append(f"package {package}: cannot load cases: {exc}")
            continue
        for spec in specs:
            reason = spec.xfail_reason
            if reason and not _ok(reason):
                violations.append(
                    f"tests/parity/{package}: case {spec.id!r}: {reason[:120]!r}"
                )


def main() -> int:
    violations: list[str] = []
    _scan_loaded_case_specs(violations)

    scan_py_roots = (
        REPO_ROOT / "tests" / "parity",
        REPO_ROOT / "python" / "uacalc" / "tests",
    )
    for root in scan_py_roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.py")):
            rel = path.relative_to(REPO_ROOT)
            if rel.match("tests/parity/**/test_cases/*.py"):
                _scan_case_module(path, violations)
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if "xfail" in text:
                _scan_py_xfail_markers(path, violations)

    for path in sorted((REPO_ROOT / "src").rglob("*.rs")):
        if "ignore" in path.read_text(encoding="utf-8", errors="ignore"):
            _scan_rs_ignores(path, violations)
    for path in (REPO_ROOT / "tests").rglob("*.rs"):
        _scan_rs_ignores(path, violations)

    if violations:
        print("Xfail/ignore reasons must start with one of:", ", ".join(ALLOWED_PREFIXES))
        for item in violations:
            print("  -", item)
        return 1
    print("All xfail/ignore reasons use allowed prefixes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())