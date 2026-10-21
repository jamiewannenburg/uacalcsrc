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
from .java_surface import (
    CATEGORY_REASONS,
    EXCLUSION_CATEGORIES,
    excluded_names_by_category,
    excluded_occurrence_counts,
    scan_java_file,
)

# Remaining genuine out-of-scope / unbound public surface (not scanner FPs).
# Scanner FPs now appear under "Excluded by category" instead of here.
PENDING_BINDINGS = {
    "alg": [
        (
            "CloserTiming ProgressReport",
            "CloserTiming(algebra, report) accepts report=None only; a live "
            "org.uacalc.ui.tm.ProgressReport is out of scope.",
        ),
    ],
    "lat": [
        (
            "getDiagram / getVertices",
            "Swing/latdraw diagram helpers on BasicLattice; drawing is out of scope",
        ),
        (
            "LatticeGraphData drawing helpers",
            "to_networkx/to_dot/to_mermaid are Python extras, not Java org.uacalc.lat",
        ),
        (
            "POElem class (org.latdraw.orderedset)",
            "not in org.uacalc.lat; filter/ideal/covers/leq/univ are covered via "
            "BasicLattice and uacalc_lib OrderedSet dual-runtime goldens",
        ),
    ],
    "terms": [
        (
            "Terms.testFlatten",
            "Java development helper; not wrapped",
        ),
    ],
    "eq": [
        (
            "ProgressReport overloads",
            "org.uacalc.ui.tm.ProgressReport is not bound",
        ),
    ],
    "element": [
        (
            "Element instantiation",
            "Java interface; CPython rejects Element()",
        ),
    ],
    "example": [
        (
            "GUI / interactive demos",
            "16 packaged demo classes are ported under python/org/uacalc/example. "
            "GUI/interactive mains and incomplete ParallelClose/ParallelClose8 "
            "are strict xfail or skip. uacalc_lib.example stays empty.",
        ),
    ],
    "parallel": [
        (
            "ForkJoinPool / Thread / ProgressReport / CloserTiming / increment",
            "doOneStep accepts these Java thread-internal args and ignores them; "
            "timing and thread counts are not asserted.",
        ),
    ],
    "group": [
        (
            "to_basic_algebra / automorphism_group / new_safe",
            "Rust extras; Java PermutationGroup has no Aut(A) or conversion. "
            "uacalc_lib to_basic_algebra uses the underlying set {0..n-1}, not |G|",
        ),
    ],
    "util": [
        (
            "IntArray.getArray live alias / setIntArray replace",
            "uacalc_lib IntArray is copy-on-write; Java returns/replaces the backing int[]",
        ),
        (
            "LongList.stream / parallelStream",
            "Java 8 Stream API is not bound",
        ),
        (
            "SimpleList writeObject/readObject",
            "custom sharing-graph serialization is not bound",
        ),
    ],
    "sublat": [
        (
            "getDiagram and ProgressReport monitor overloads",
            "Swing/latdraw and org.uacalc.ui.tm.ProgressReport are out of scope",
        ),
        (
            "SubalgebraLattice.con / sub of the lattice itself",
            "BasicLattice from a BasicSet universe cannot yet extract i32 join/meet tables",
        ),
    ],
    "conlat": [
        (
            "ProgressReport overloads / UI (getDiagram, getConTable)",
            "org.uacalc.ui.tm.ProgressReport and Swing/latdraw are not bound",
        ),
        (
            "BasicPartition.generalizedWeakClosure / closureAt / projection / termMap",
            "SubProductAlgebra/Term overloads are not bound; no Python reimplementation",
        ),
        (
            "CongruenceLattice type theory / commutator SubProduct overloads",
            "typeSet/type/typeJI/subtrace/getTypeFinder are wrapped in the "
            "org shim (TypeFinder + originating algebra stashed on con()). "
            "matrices / commutator-with-report / SubProduct overloads stay unbound.",
        ),
    ],
    "alg_op": [
        (
            "Operations.makeOperationFromScript (Groovy)",
            "Groovy scripting is not wrapped",
        ),
        (
            "OperationWithDefaultValue defaultValue==-2 random tables",
            "Java uses UI RandomGenerator; Python uses random "
            "(strict xfail ow_random_xfail)",
        ),
    ],
}

# tests/parity/<name> → Java/Python package path under org/uacalc (posix).
NESTED_PACKAGE_PATHS = {
    "alg_op": "alg/op",
    "conlat": "alg/conlat",
    "sublat": "alg/sublat",
    "parallel": "alg/parallel",
}


def _java_package_dir(package: str) -> Path:
    rel = NESTED_PACKAGE_PATHS.get(package, package)
    return PROJECT_ROOT / "org" / "uacalc" / rel


def _python_package_dir(package: str) -> Path:
    rel = NESTED_PACKAGE_PATHS.get(package, package)
    return PROJECT_ROOT / "python" / "org" / "uacalc" / rel


@dataclass
class ParityCoverageReport:
    """Coverage report for parity testing."""
    
    by_package: Dict[str, PackageCoverage] = field(default_factory=dict)
    total_java_methods: int = 0
    total_wrapped_methods: int = 0
    total_tested_methods: int = 0
    total_excluded_methods: int = 0


@dataclass
class PackageCoverage:
    """Coverage for one package."""
    
    package: str
    java_methods: Set[str] = field(default_factory=set)  # Public library surface
    wrapped_methods: Set[str] = field(default_factory=set)  # Wrapped in Python
    tested_methods: Set[str] = field(default_factory=set)  # Have behavioral tests
    excluded_by_category: Dict[str, Set[str]] = field(default_factory=dict)
    excluded_counts: Dict[str, int] = field(default_factory=dict)
    
    @property
    def unwrapped_methods(self) -> Set[str]:
        return self.java_methods - self.wrapped_methods
    
    @property
    def untested_methods(self) -> Set[str]:
        return self.wrapped_methods - self.tested_methods

    @property
    def excluded_methods(self) -> Set[str]:
        names: Set[str] = set()
        for group in self.excluded_by_category.values():
            names.update(group)
        return names - self.java_methods

    @property
    def excluded_occurrence_count(self) -> int:
        return sum(self.excluded_counts.values())
    
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
    """Scan a Java file for public library-surface methods and constructors."""
    if not java_file.exists():
        return set()
    names: Set[str] = set()
    for typ in scan_java_file(java_file).types:
        names.update(typ.public_surface)
    return names


def scan_java_exclusions(java_file: Path) -> Dict[str, Set[str]]:
    if not java_file.exists():
        return {}
    return excluded_names_by_category(scan_java_file(java_file).types)


def scan_java_exclusion_counts(java_file: Path) -> Dict[str, int]:
    if not java_file.exists():
        return {}
    return excluded_occurrence_counts(scan_java_file(java_file).types)


def _snake_to_camel(name: str) -> str:
    if "_" not in name:
        return name
    parts = [p for p in name.split("_") if p]
    if not parts:
        return name
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


def _is_exported_name(name: str) -> bool:
    return bool(name) and not name.startswith("_")


def scan_python_wrapper_methods(python_file: Path) -> Set[str]:
    """Scan a Python wrapper file for exported methods and class names.

    Returns Java-style (camelCase) names that are wrapped, including
    constructor names (ClassDef / imported class names).
    """
    if not python_file.exists():
        return set()

    raw: Set[str] = set()
    content = python_file.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
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
        if not _is_exported_name(name):
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
        # UI packages have no parity tests but hold most GUI exclusions.
        for extra in ("ui", "nbui"):
            if extra not in packages:
                packages.append(extra)
    
    for package in packages:
        coverage = PackageCoverage(package=package)
        
        # Scan Java sources for public library surface (exclusions categorised)
        java_package_dir = _java_package_dir(package)
        if java_package_dir.exists():
            # Nested alg.* packages have their own coverage buckets; only
            # util/ui/nbui should recurse into subdirectories.
            java_iter = (
                java_package_dir.rglob("*.java")
                if package in {"util", "ui", "nbui"}
                else java_package_dir.glob("*.java")
            )
            for java_file in java_iter:
                coverage.java_methods.update(scan_java_public_methods(java_file))
                for cat, names in scan_java_exclusions(java_file).items():
                    coverage.excluded_by_category.setdefault(cat, set()).update(names)
                for cat, n in scan_java_exclusion_counts(java_file).items():
                    coverage.excluded_counts[cat] = coverage.excluded_counts.get(cat, 0) + n
        
        # Scan Python wrappers (package dir, including _jython_compat)
        python_package_dir = _python_package_dir(package)
        if python_package_dir.exists():
            python_names: Set[str] = set()
            py_iter = (
                python_package_dir.rglob("*.py")
                if package == "util"
                else python_package_dir.glob("*.py")
            )
            for python_file in py_iter:
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
        report.total_excluded_methods += coverage.excluded_occurrence_count
    
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
    lines.append("  1. Wrapper coverage: Java public library surface wrapped in Python")
    lines.append("  2. Test coverage: Wrapped methods with behavioral parity tests")
    lines.append("  3. Exclusions: scanner false-positives categorised (not in Java column)")
    lines.append("")
    
    # Per-package summary
    lines.append(
        f"{'Package':<15} {'Java':<8} {'Wrapped':<10} {'Tested':<10} "
        f"{'Unwrapped':<10} {'Excluded':<10} {'Wrapper %':<12} {'Test %':<10}"
    )
    lines.append("-" * 95)
    
    for package, coverage in sorted(report.by_package.items()):
        if (
            not coverage.java_methods
            and not coverage.excluded_methods
            and not coverage.wrapped_methods
        ):
            continue
        lines.append(
            f"{package:<15} "
            f"{len(coverage.java_methods):<8} "
            f"{len(coverage.wrapped_methods):<10} "
            f"{len(coverage.tested_methods):<10} "
            f"{len(coverage.unwrapped_methods):<10} "
            f"{coverage.excluded_occurrence_count:<10} "
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
        if coverage.excluded_counts:
            lines.append(
                f"  Excluded by category ({coverage.excluded_occurrence_count} members):"
            )
            for cat in EXCLUSION_CATEGORIES:
                n = coverage.excluded_counts.get(cat) or 0
                names = coverage.excluded_by_category.get(cat) or set()
                if not n:
                    continue
                reason = CATEGORY_REASONS.get(cat, cat)
                sample = ", ".join(sorted(names)[:8])
                extra = f", ... +{len(names) - 8}" if len(names) > 8 else ""
                lines.append(
                    f"    - {cat} ({n} members, {len(names)} names): {reason}. "
                    f"e.g. {sample}{extra}"
                )
        pending = PENDING_BINDINGS.get(package, [])
        if pending:
            lines.append(f"  Pending bindings ({len(pending)}):")
            for name, reason in pending:
                lines.append(f"    - {name}: {reason}")
    
    lines.append("-" * 95)
    
    # Totals
    total_wrapper_pct = (
        100.0 * report.total_wrapped_methods / report.total_java_methods
        if report.total_java_methods > 0 else 100.0
    )
    total_test_pct = (
        100.0 * report.total_tested_methods / report.total_wrapped_methods
        if report.total_wrapped_methods > 0 else 100.0
    )
    unwrapped_total = report.total_java_methods - report.total_wrapped_methods
    
    lines.append(
        f"{'TOTAL':<15} "
        f"{report.total_java_methods:<8} "
        f"{report.total_wrapped_methods:<10} "
        f"{report.total_tested_methods:<10} "
        f"{unwrapped_total:<10} "
        f"{report.total_excluded_methods:<10} "
        f"{total_wrapper_pct:>6.1f}%     "
        f"{total_test_pct:>6.1f}%"
    )
    lines.append("")
    
    # Summary
    untested_total = report.total_wrapped_methods - report.total_tested_methods
    lines.append("Summary:")
    lines.append(f"  - {report.total_java_methods} Java public library-surface methods")
    lines.append(f"  - {report.total_wrapped_methods} wrapped in Python ({total_wrapper_pct:.1f}%)")
    lines.append(f"  - {report.total_tested_methods} have behavioral parity tests ({total_test_pct:.1f}%)")
    lines.append(f"  - {unwrapped_total} public methods still unwrapped")
    lines.append(
        f"  - {report.total_excluded_methods} excluded member declarations "
        f"(anonymous inner class, commented-out, GUI widgets, main, "
        f"package-private, legacy, …)"
    )
    global_excl: Dict[str, int] = {}
    for coverage in report.by_package.values():
        for cat, n in coverage.excluded_counts.items():
            global_excl[cat] = global_excl.get(cat, 0) + n
    if global_excl:
        parts = [
            f"{cat} {global_excl[cat]}"
            for cat in EXCLUSION_CATEGORIES
            if cat in global_excl
        ]
        lines.append("      by category: " + ", ".join(parts))
    lines.append(f"  - {untested_total} wrapped methods need behavioral tests")
    pending_shown = [
        (package, name, reason)
        for package, items in sorted(PENDING_BINDINGS.items())
        if package in report.by_package
        for name, reason in items
    ]
    if pending_shown:
        lines.append(
            "  - {0} pending uacalc_lib bindings (see per-package notes)".format(
                len(pending_shown)
            )
        )
        for package, name, reason in pending_shown:
            lines.append("      {0}.{1}: {2}".format(package, name, reason))
    
    return "\n".join(lines)
