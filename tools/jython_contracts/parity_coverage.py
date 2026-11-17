"""Parity test coverage measurement.

Measures:
1. Wrapper coverage: which Java public methods have Python wrappers
2. Test coverage: which wrapped methods have exact behavioral parity tests

Inheritance rules (see ``build_java_type_index`` / ``build_python_type_index``):
- Java: a method on a per-class surface includes members declared on that type
  plus public members inherited from direct supertypes (extends/implements), when
  the subclass does not declare the same name.
- Python wrapping: ``Class.method`` counts as wrapped if the method appears on the
  class or any entry in the wrapper module's AST MRO for that class (bases), with
  camelCase/snake_case aliasing.
- Java supertype bridge: if type *C* has Java supertype *S* and Python wraps
  ``S.method``, then ``C.method`` counts as wrapped (interface implementation or
  parent patch), including when *C* redeclares the method in Java.
- Tests: ``S.method`` counts toward ``C.method`` only when *C* does **not** declare
  ``method`` in Java (pure inheritance — same inherited API).
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

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
            "matrices / commutator(S,T) / weakCommutator / centralityFailure "
            "are bound (witnesses as IntArray coordinates). commutator-with-report "
            "ProgressReport overloads stay unbound.",
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
    """Scan a Java file for public library-surface methods and constructors.

    Returns qualified keys ``ClassName.method`` (constructors use ``ClassName.ClassName``).
    Overloads are collapsed by method name within each type.
    """
    if not java_file.exists():
        return set()
    qualified: Set[str] = set()
    for typ in scan_java_file(java_file).types:
        cls = typ.simple_name
        for member in typ.members:
            if member.exclusion is not None:
                continue
            if member.kind == "constructor":
                qualified.add(f"{cls}.{cls}")
            elif member.kind == "method":
                qualified.add(f"{cls}.{member.name}")
    return qualified


_JAVA_TYPE_HEADER_RE = re.compile(
    r"(?:public\s+|protected\s+|private\s+)?"
    r"(?:(?:abstract|static|final|strictfp)\s+)*"
    r"(?P<kind>class|interface|enum)\s+(?P<name>\w+)"
    r"(?:\s+extends\s+(?P<extends>[^<{]+?))?"
    r"(?:\s+implements\s+(?P<implements>[^<{]+?))?"
    r"\s*\{",
    re.MULTILINE,
)


def _parse_java_supertype_names(fragment: Optional[str]) -> List[str]:
    if not fragment:
        return []
    text = re.sub(r"<[^>]*>", "", fragment)
    text = text.split("{", 1)[0]
    parts = re.split(r"\s*,\s*|\s+&\s*", text.strip())
    out: List[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        simple = part.split(".")[-1].strip()
        if simple and simple not in _SKIP_JAVA_TYPES:
            out.append(simple)
    return out


_SKIP_JAVA_TYPES = frozenset({"Object", "Enum", "Cloneable", "Serializable", "Comparable"})


def scan_java_type_supers(java_file: Path) -> Dict[str, List[str]]:
    """Map each public type in a file to direct Java supertypes (simple names)."""
    if not java_file.exists():
        return {}
    try:
        text = java_file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}
    supers: Dict[str, List[str]] = {}
    for m in _JAVA_TYPE_HEADER_RE.finditer(text):
        name = m.group("name")
        parents: List[str] = []
        if m.group("extends"):
            parents.extend(_parse_java_supertype_names(m.group("extends")))
        if m.group("implements"):
            parents.extend(_parse_java_supertype_names(m.group("implements")))
        supers[name] = parents
    return supers


@dataclass(frozen=True)
class JavaTypeIndex:
    """Global Java public-type hierarchy and per-type declared method names."""

    supers: Dict[str, Tuple[str, ...]]
    declared: Dict[str, FrozenSet[str]]


def build_java_type_index(java_root: Optional[Path] = None) -> JavaTypeIndex:
    root = java_root or (PROJECT_ROOT / "org" / "uacalc")
    supers: Dict[str, Tuple[str, ...]] = {}
    declared: Dict[str, Set[str]] = {}
    if not root.exists():
        return JavaTypeIndex(supers={}, declared={})
    for java_file in root.rglob("*.java"):
        for cls, parents in scan_java_type_supers(java_file).items():
            supers[cls] = tuple(parents)
        for typ in scan_java_file(java_file).types:
            if typ.visibility != "public":
                continue
            names: Set[str] = set()
            for member in typ.members:
                if member.exclusion is not None:
                    continue
                if member.kind == "constructor":
                    names.add(typ.simple_name)
                elif member.kind == "method":
                    names.add(member.name)
            if names:
                declared.setdefault(typ.simple_name, set()).update(names)
    return JavaTypeIndex(
        supers=supers,
        declared={k: frozenset(v) for k, v in declared.items()},
    )


def _transitive_java_supers(
    cls: str, supers: Dict[str, Tuple[str, ...]]
) -> Tuple[str, ...]:
    seen: Set[str] = set()
    order: List[str] = []

    def walk(name: str) -> None:
        for parent in supers.get(name, ()):
            if parent in seen or parent in _SKIP_JAVA_TYPES:
                continue
            seen.add(parent)
            order.append(parent)
            walk(parent)

    walk(cls)
    return tuple(order)


def expand_java_methods_with_inheritance(
    declared_qualified: Set[str],
    java_index: JavaTypeIndex,
) -> Set[str]:
    """Add inherited ``Class.method`` keys for types that do not declare ``method``."""
    by_class: Dict[str, Set[str]] = {}
    for q in declared_qualified:
        if "." not in q:
            continue
        cls, meth = q.split(".", 1)
        by_class.setdefault(cls, set()).add(meth)

    expanded = set(declared_qualified)
    for cls, meths in by_class.items():
        for parent in _transitive_java_supers(cls, java_index.supers):
            for pm in java_index.declared.get(parent, ()):
                if pm not in meths:
                    expanded.add(f"{cls}.{pm}")
    return expanded


@dataclass(frozen=True)
class PythonTypeIndex:
    """AST-derived Python class bases and per-class direct method names."""

    bases: Dict[str, Tuple[str, ...]]
    declared: Dict[str, FrozenSet[str]]


def _class_bases_from_node(class_node: ast.ClassDef) -> Tuple[str, ...]:
    bases: List[str] = []
    for base in class_node.bases:
        if isinstance(base, ast.Name) and base.id[0].isupper():
            bases.append(base.id)
        elif isinstance(base, ast.Attribute) and isinstance(base.attr, str):
            if base.attr[0].isupper():
                bases.append(base.attr)
    return tuple(bases)


def build_python_type_index(python_root: Optional[Path] = None) -> PythonTypeIndex:
    root = python_root or (PROJECT_ROOT / "python" / "org" / "uacalc")
    bases: Dict[str, Tuple[str, ...]] = {}
    declared: Dict[str, Set[str]] = {}
    if not root.exists():
        return PythonTypeIndex(bases={}, declared={})
    for py_file in root.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            name = node.name
            if not name or not name[0].isupper():
                continue
            bases[name] = _class_bases_from_node(node)
            methods: Set[str] = {name}
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == "__init__":
                        methods.add(name)
                    elif _is_exported_name(item.name):
                        methods.add(item.name)
            declared.setdefault(name, set()).update(methods)
    return PythonTypeIndex(
        bases=bases,
        declared={k: frozenset(v) for k, v in declared.items()},
    )


def _transitive_python_bases(
    cls: str, bases: Dict[str, Tuple[str, ...]]
) -> Tuple[str, ...]:
    seen: Set[str] = set()
    order: List[str] = []

    def walk(name: str) -> None:
        for parent in bases.get(name, ()):
            if parent in seen:
                continue
            seen.add(parent)
            order.append(parent)
            walk(parent)

    walk(cls)
    return tuple(order)


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


def _lib_to_java_class(name: str) -> Optional[str]:
    if name.startswith("_Lib") and len(name) > 4:
        return name[4:]
    if name and name[0].isupper() and not name.startswith("_"):
        return name
    return None


def _resolve_type_expr(node: ast.expr) -> Optional[str]:
    if isinstance(node, ast.Name):
        return _lib_to_java_class(node.id)
    if isinstance(node, ast.Attribute):
        return _lib_to_java_class(node.attr)
    return None


def _add_qualified(qualified: Set[str], class_name: str, method_name: str) -> None:
    if not class_name or not method_name or not _is_exported_name(method_name):
        return
    qualified.add(f"{class_name}.{method_name}")
    camel = _snake_to_camel(method_name)
    if camel != method_name:
        qualified.add(f"{class_name}.{camel}")


def _is_class_aliases_assign_target(target: ast.expr) -> bool:
    if isinstance(target, ast.Name) and target.id == "_CLASS_ALIASES":
        return True
    if isinstance(target, ast.Subscript):
        sl = target.slice
        if isinstance(sl, ast.Constant) and sl.value == "_CLASS_ALIASES":
            return True
    return False


def _record_class_aliases(assign: ast.Assign, qualified: Set[str]) -> None:
    if not any(_is_class_aliases_assign_target(t) for t in assign.targets):
        return
    inner = assign.value
    if not isinstance(inner, ast.Dict):
        return
    for cls_key, method_map in zip(inner.keys, inner.values):
        if not isinstance(cls_key, ast.Constant) or not isinstance(cls_key.value, str):
            continue
        cls_name = cls_key.value
        if isinstance(method_map, ast.Dict):
            for jk in method_map.keys:
                if isinstance(jk, ast.Constant) and isinstance(jk.value, str):
                    _add_qualified(qualified, cls_name, jk.value)


def _record_bind_call(call: ast.Call, qualified: Set[str]) -> None:
    func = call.func
    fname = ""
    if isinstance(func, ast.Name):
        fname = func.id
    elif isinstance(func, ast.Attribute):
        fname = func.attr
    if fname not in {"_bind", "setattr"} or len(call.args) < 2:
        return
    cls = _resolve_type_expr(call.args[0])
    arg = call.args[1]
    if cls and isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        _add_qualified(qualified, cls, arg.value)


def _record_class_surface(class_node: ast.ClassDef, qualified: Set[str]) -> None:
    cls = class_node.name
    if cls and cls[0].isupper():
        _add_qualified(qualified, cls, cls)
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if item.name == "__init__":
                _add_qualified(qualified, cls, cls)
            elif _is_exported_name(item.name):
                _add_qualified(qualified, cls, item.name)
        elif isinstance(item, ast.ClassDef):
            _record_class_surface(item, qualified)


def scan_python_wrapper_methods(python_file: Path) -> Set[str]:
    """Scan a Python wrapper file for per-class wrapped surface.

    Returns ``ClassName.method`` keys (constructors ``ClassName.ClassName``).
    """
    if not python_file.exists():
        return set()

    qualified: Set[str] = set()
    content = python_file.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                _record_class_surface(node, qualified)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    if name and name[0].isupper():
                        _add_qualified(qualified, name, name)
            elif isinstance(node, ast.Assign):
                _record_class_aliases(node, qualified)
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id[0].isupper():
                        _add_qualified(qualified, target.id, target.id)
            elif isinstance(node, ast.Call):
                _record_bind_call(node, qualified)
    except SyntaxError:
        pass

    return qualified


def _direct_python_match(java_q: str, python_qualified: Set[str]) -> bool:
    if java_q in python_qualified:
        return True
    if "." not in java_q:
        return False
    cls, meth = java_q.split(".", 1)
    alt = f"{cls}.{_snake_to_camel(meth)}"
    if alt in python_qualified:
        return True
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", meth).lower()
    if snake != meth and f"{cls}.{snake}" in python_qualified:
        return True
    return False


def _java_method_wrapped(
    java_q: str,
    python_qualified: Set[str],
    *,
    java_index: Optional[JavaTypeIndex] = None,
    python_index: Optional[PythonTypeIndex] = None,
) -> bool:
    """Whether Java ``Class.method`` is considered wrapped in Python."""
    if _direct_python_match(java_q, python_qualified):
        return True
    if "." not in java_q:
        return False
    cls, meth = java_q.split(".", 1)

    if python_index is not None:
        for base in _transitive_python_bases(cls, python_index.bases):
            if _direct_python_match(f"{base}.{meth}", python_qualified):
                return True

    if java_index is not None:
        for parent in _transitive_java_supers(cls, java_index.supers):
            if _direct_python_match(f"{parent}.{meth}", python_qualified):
                return True

    return False


def _java_method_tested(
    java_q: str,
    tested_qualified: Set[str],
    *,
    java_index: Optional[JavaTypeIndex] = None,
) -> bool:
    """Whether a behavioral golden exists for ``Class.method``, with inheritance."""
    if java_q in tested_qualified:
        return True
    if java_index is None or "." not in java_q:
        return False
    cls, meth = java_q.split(".", 1)
    if meth in java_index.declared.get(cls, ()):
        return False
    for parent in _transitive_java_supers(cls, java_index.supers):
        if f"{parent}.{meth}" in tested_qualified:
            return True
    return False


def scan_behavioral_test_methods(parity_dir: Path) -> Set[str]:
    """Scan parity test directory for behavioral test methods.

    Returns qualified ``ClassName.method`` keys where available.
    """
    methods: Set[str] = set()

    def _add_tested(method_full: str) -> None:
        method_full = method_full.strip()
        if method_full:
            methods.add(method_full)

    golden_data_dir = parity_dir / "golden_data"
    if golden_data_dir.exists():
        for golden_file in golden_data_dir.glob("*_jython.json"):
            try:
                data = json.loads(golden_file.read_text(encoding="utf-8"))
                for test_case in data.get("test_cases", []):
                    _add_tested(test_case.get("method", ""))
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
                _add_tested(match.group(1))

    return methods


def clear_parity_coverage_caches() -> None:
    """Clear cached Java/Python indexes (for tests that patch ``PROJECT_ROOT``)."""
    _cached_java_index.cache_clear()
    _cached_python_index.cache_clear()
    _cached_global_python_qualified.cache_clear()


@lru_cache(maxsize=1)
def _cached_java_index() -> JavaTypeIndex:
    return build_java_type_index()


@lru_cache(maxsize=1)
def _cached_python_index() -> PythonTypeIndex:
    return build_python_type_index()


@lru_cache(maxsize=1)
def _cached_global_python_qualified() -> FrozenSet[str]:
    root = PROJECT_ROOT / "python" / "org" / "uacalc"
    qualified: Set[str] = set()
    if root.exists():
        for py_file in root.rglob("*.py"):
            qualified.update(scan_python_wrapper_methods(py_file))
    return frozenset(qualified)


def build_parity_coverage(
    packages: Optional[List[str]] = None
) -> ParityCoverageReport:
    """Build parity coverage report for specified packages.
    
    Args:
        packages: List of package names (e.g., ["io", "lat", "terms"]).
                 If None, scans all packages with parity tests.
    """
    report = ParityCoverageReport()
    java_index = _cached_java_index()
    python_index = _cached_python_index()
    global_python = set(_cached_global_python_qualified())
    
    # Find packages to scan
    if packages is None:
        parity_root = PROJECT_ROOT / "tests" / "parity"
        packages = [
            p.name for p in parity_root.iterdir()
            if p.is_dir()
            and not p.name.startswith('_')
            # Cross-package randomized snapshots, not a Java org.uacalc.* dir.
            and p.name != "random"
        ]
        # UI packages have no parity tests but hold most GUI exclusions.
        for extra in ("ui", "nbui"):
            if extra not in packages:
                packages.append(extra)
    
    for package in packages:
        coverage = PackageCoverage(package=package)
        
        # Scan Java sources for public library surface (exclusions categorised)
        java_package_dir = _java_package_dir(package)
        declared_java: Set[str] = set()
        if java_package_dir.exists():
            # Nested alg.* packages have their own coverage buckets; only
            # util/ui/nbui should recurse into subdirectories.
            java_iter = (
                java_package_dir.rglob("*.java")
                if package in {"util", "ui", "nbui"}
                else java_package_dir.glob("*.java")
            )
            for java_file in java_iter:
                declared_java.update(scan_java_public_methods(java_file))
                for cat, names in scan_java_exclusions(java_file).items():
                    coverage.excluded_by_category.setdefault(cat, set()).update(names)
                for cat, n in scan_java_exclusion_counts(java_file).items():
                    coverage.excluded_counts[cat] = coverage.excluded_counts.get(cat, 0) + n
        # Per-class Java surface = members declared on each type (not inherited keys).
        coverage.java_methods = declared_java
        
        # Python wrappers: global org.uacalc scan for inheritance / cross-package binds
        python_names: Set[str] = set(global_python)
        python_package_dir = _python_package_dir(package)
        if python_package_dir.exists():
            py_iter = (
                python_package_dir.rglob("*.py")
                if package == "util"
                else python_package_dir.glob("*.py")
            )
            for python_file in py_iter:
                python_names.update(scan_python_wrapper_methods(python_file))
        coverage.wrapped_methods = {
            java_q
            for java_q in coverage.java_methods
            if _java_method_wrapped(
                java_q,
                python_names,
                java_index=java_index,
                python_index=python_index,
            )
        }
        
        # Scan behavioral tests
        parity_dir = PROJECT_ROOT / "tests" / "parity" / package
        if parity_dir.exists():
            tested_raw = scan_behavioral_test_methods(parity_dir)
            coverage.tested_methods = {
                java_q
                for java_q in coverage.java_methods
                if _java_method_tested(
                    java_q, tested_raw, java_index=java_index
                )
            }
            # A Java method with a golden/behavioral case is wrapped enough to call.
            coverage.wrapped_methods.update(coverage.tested_methods)
        
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
    verbose: bool = False,
    list_limit: Optional[int] = None,
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
    lines.append(
        "  Inheritance: Java extends/implements + Python MRO (see module docstring)"
    )
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
                ordered = sorted(coverage.unwrapped_methods)
                lines.append(f"  Unwrapped methods ({len(ordered)}):")
                shown = ordered if list_limit is None else ordered[:list_limit]
                for method in shown:
                    lines.append(f"    - {method}")
                if list_limit is not None and len(ordered) > list_limit:
                    lines.append(f"    ... and {len(ordered) - list_limit} more")
        
        if verbose or show_untested:
            if coverage.untested_methods:
                ordered = sorted(coverage.untested_methods)
                lines.append(f"  Wrapped but untested methods ({len(ordered)}):")
                shown = ordered if list_limit is None else ordered[:list_limit]
                for method in shown:
                    lines.append(f"    - {method}")
                if list_limit is not None and len(ordered) > list_limit:
                    lines.append(f"    ... and {len(ordered) - list_limit} more")
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
