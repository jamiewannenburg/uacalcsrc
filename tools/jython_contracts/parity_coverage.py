"""Parity test coverage measurement.

Measures:
1. Wrapper coverage: which Java public methods have Python wrappers
2. Test coverage: which wrapped methods have exact behavioral parity tests
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from . import PROJECT_ROOT


@dataclass
class ParityCoverageReport:
    """Coverage report for parity testing."""
    
    by_package: Dict[str, PackageCoverage] = field(default_factory=dict)
    total_java_methods: int = 0
    total_wrapped_methods: int = 0
    total_tested_methods: int = 0


@dataclass
class PackageCoverage:
    """Coverage for one package."""
    
    package: str
    java_methods: Set[str] = field(default_factory=set)  # Public methods in Java
    wrapped_methods: Set[str] = field(default_factory=set)  # Wrapped in Python
    tested_methods: Set[str] = field(default_factory=set)  # Have behavioral tests
    
    @property
    def unwrapped_methods(self) -> Set[str]:
        return self.java_methods - self.wrapped_methods
    
    @property
    def untested_methods(self) -> Set[str]:
        return self.wrapped_methods - self.tested_methods
    
    @property
    def wrapper_coverage_pct(self) -> float:
        if not self.java_methods:
            return 100.0
        return 100.0 * len(self.wrapped_methods) / len(self.java_methods)
    
    @property
    def test_coverage_pct(self) -> float:
        if not self.wrapped_methods:
            return 100.0
        return 100.0 * len(self.tested_methods) / len(self.wrapped_methods)


def scan_java_public_methods(java_file: Path) -> Set[str]:
    """Scan a Java file for public methods.
    
    Returns set of method names (simple names, not fully qualified).
    """
    if not java_file.exists():
        return set()
    
    content = java_file.read_text(encoding='utf-8', errors='ignore')
    methods = set()
    
    # Simple regex for public methods (not perfect but good enough)
    # Match: public [static] [final] ReturnType methodName(...)
    pattern = r'\bpublic\s+(?:static\s+)?(?:final\s+)?(?:\w+(?:<[^>]+>)?(?:\[\])?)\s+(\w+)\s*\('
    for match in re.finditer(pattern, content):
        method_name = match.group(1)
        # Skip constructors (same name as class)
        if not method_name[0].isupper():  # Methods start with lowercase
            methods.add(method_name)
    
    return methods


def _snake_to_camel(name: str) -> str:
    if "_" not in name:
        return name
    parts = [p for p in name.split("_") if p]
    if not parts:
        return name
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


def _is_method_name(name: str) -> bool:
    return bool(name) and name[0].islower() and not name.startswith("_")


def scan_python_wrapper_methods(python_file: Path) -> Set[str]:
    """Scan a Python wrapper file for exported methods.

    Returns Java-style (camelCase) method names that are wrapped.
    """
    if not python_file.exists():
        return set()

    raw: Set[str] = set()
    content = python_file.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                raw.add(node.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    raw.add(alias.asname or alias.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        raw.add(target.id)
    except SyntaxError:
        pass

    methods = set()
    for name in raw:
        if not _is_method_name(name):
            continue
        methods.add(name)
        methods.add(_snake_to_camel(name))
    return methods


def scan_behavioral_test_methods(parity_dir: Path) -> Set[str]:
    """Scan parity test directory for behavioral test methods.
    
    Returns set of method names covered by behavioral tests.
    """
    methods = set()
    
    # Check for golden data files
    golden_data_dir = parity_dir / "golden_data"
    if golden_data_dir.exists():
        for golden_file in golden_data_dir.glob("*_jython.json"):
            try:
                data = json.loads(golden_file.read_text(encoding='utf-8'))
                for test_case in data.get('test_cases', []):
                    method_full = test_case.get('method', '')
                    # Extract method name from "ClassName.methodName"
                    if '.' in method_full:
                        method_name = method_full.split('.')[-1]
                        methods.add(method_name)
            except (json.JSONDecodeError, OSError):
                pass
    
    cases_dir = parity_dir / "test_cases"
    if cases_dir.exists():
        for cases_file in cases_dir.glob("*_cases.py"):
            try:
                content = cases_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for match in re.finditer(r'method\s*=\s*["\']([^"\']+)["\']', content):
                method_full = match.group(1)
                methods.add(method_full.split(".")[-1] if "." in method_full else method_full)

    # Also check test files with @pytest.mark.behavioral
    for test_file in parity_dir.glob("test_*_behavioral_parity.py"):
        try:
            content = test_file.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Look for test methods with behavioral marker
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    # Check if behavioral marker is present
                    has_behavioral = any(
                        isinstance(dec, ast.Name) and 'behavioral' in dec.id.lower()
                        or isinstance(dec, ast.Attribute) and 'behavioral' in dec.attr.lower()
                        for dec in node.decorator_list
                    )
                    if has_behavioral:
                        # Extract method name from test name
                        # e.g., test_read_cyclic2 -> readCyclic2 or read_cyclic2
                        method_part = node.name.replace('test_', '', 1)
                        methods.add(method_part)
        except (SyntaxError, OSError):
            pass
    
    return methods


def build_parity_coverage(
    packages: Optional[List[str]] = None
) -> ParityCoverageReport:
    """Build parity coverage report for specified packages.
    
    Args:
        packages: List of package names (e.g., ["io", "lat", "terms"]).
                 If None, scans all packages with parity tests.
    """
    report = ParityCoverageReport()
    
    # Find packages to scan
    if packages is None:
        parity_root = PROJECT_ROOT / "tests" / "parity"
        packages = [
            p.name for p in parity_root.iterdir()
            if p.is_dir() and not p.name.startswith('_')
        ]
    
    for package in packages:
        coverage = PackageCoverage(package=package)
        
        # Scan Java sources for public methods
        java_package_dir = PROJECT_ROOT / "org" / "uacalc" / package
        if java_package_dir.exists():
            for java_file in java_package_dir.glob("*.java"):
                methods = scan_java_public_methods(java_file)
                coverage.java_methods.update(methods)
        
        # Scan Python wrappers (package dir, including _jython_compat)
        python_package_dir = PROJECT_ROOT / "python" / "org" / "uacalc" / package
        if python_package_dir.exists():
            python_names: Set[str] = set()
            for python_file in python_package_dir.glob("*.py"):
                python_names.update(scan_python_wrapper_methods(python_file))
            # Wrapped := Java public methods that exist on the Python shim
            # (camelCase Java name or snake_case equivalent).
            coverage.wrapped_methods = {
                java_name
                for java_name in coverage.java_methods
                if java_name in python_names or _snake_to_camel(java_name) in python_names
            }
        
        # Scan behavioral tests
        parity_dir = PROJECT_ROOT / "tests" / "parity" / package
        if parity_dir.exists():
            tested = scan_behavioral_test_methods(parity_dir) & coverage.java_methods
            coverage.tested_methods.update(tested)
            # A Java method with a golden/behavioral case is wrapped enough to call.
            coverage.wrapped_methods.update(tested)
        
        report.by_package[package] = coverage
        report.total_java_methods += len(coverage.java_methods)
        report.total_wrapped_methods += len(coverage.wrapped_methods)
        report.total_tested_methods += len(coverage.tested_methods)
    
    return report


def format_parity_coverage(
    report: ParityCoverageReport,
    *,
    show_unwrapped: bool = False,
    show_untested: bool = False,
    verbose: bool = False
) -> str:
    """Format parity coverage report as text."""
    lines = []
    lines.append("Parity Test Coverage Report")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Measures:")
    lines.append("  1. Wrapper coverage: Java public methods wrapped in Python")
    lines.append("  2. Test coverage: Wrapped methods with behavioral parity tests")
    lines.append("")
    
    # Per-package summary
    lines.append(f"{'Package':<15} {'Java':<8} {'Wrapped':<10} {'Tested':<10} {'Wrapper %':<12} {'Test %':<10}")
    lines.append("-" * 70)
    
    for package, coverage in sorted(report.by_package.items()):
        lines.append(
            f"{package:<15} "
            f"{len(coverage.java_methods):<8} "
            f"{len(coverage.wrapped_methods):<10} "
            f"{len(coverage.tested_methods):<10} "
            f"{coverage.wrapper_coverage_pct:>6.1f}%     "
            f"{coverage.test_coverage_pct:>6.1f}%"
        )
        
        if verbose or show_unwrapped:
            if coverage.unwrapped_methods:
                lines.append(f"  Unwrapped methods ({len(coverage.unwrapped_methods)}):")
                for method in sorted(coverage.unwrapped_methods)[:20]:  # Limit output
                    lines.append(f"    - {method}")
                if len(coverage.unwrapped_methods) > 20:
                    lines.append(f"    ... and {len(coverage.unwrapped_methods) - 20} more")
        
        if verbose or show_untested:
            if coverage.untested_methods:
                lines.append(f"  Wrapped but untested methods ({len(coverage.untested_methods)}):")
                for method in sorted(coverage.untested_methods)[:20]:
                    lines.append(f"    - {method}")
                if len(coverage.untested_methods) > 20:
                    lines.append(f"    ... and {len(coverage.untested_methods) - 20} more")
    
    lines.append("-" * 70)
    
    # Totals
    total_wrapper_pct = (
        100.0 * report.total_wrapped_methods / report.total_java_methods
        if report.total_java_methods > 0 else 100.0
    )
    total_test_pct = (
        100.0 * report.total_tested_methods / report.total_wrapped_methods
        if report.total_wrapped_methods > 0 else 100.0
    )
    
    lines.append(
        f"{'TOTAL':<15} "
        f"{report.total_java_methods:<8} "
        f"{report.total_wrapped_methods:<10} "
        f"{report.total_tested_methods:<10} "
        f"{total_wrapper_pct:>6.1f}%     "
        f"{total_test_pct:>6.1f}%"
    )
    lines.append("")
    
    # Summary
    untested_total = report.total_wrapped_methods - report.total_tested_methods
    lines.append("Summary:")
    lines.append(f"  - {report.total_java_methods} Java public methods found")
    lines.append(f"  - {report.total_wrapped_methods} wrapped in Python ({total_wrapper_pct:.1f}%)")
    lines.append(f"  - {report.total_tested_methods} have behavioral parity tests ({total_test_pct:.1f}%)")
    lines.append(f"  - {untested_total} wrapped methods need behavioral tests")
    
    return "\n".join(lines)
