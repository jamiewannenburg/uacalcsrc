"""Allowlisted Jython vs CPython stdout comparison scripts.

``run_comparison.py`` treats a listed script as success when output still differs,
so CI can enforce the comparison job without hiding new regressions on other scripts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

# Repo-relative posix path -> human-readable reason
KNOWN_OUTPUT_DIFFERENCES: Dict[str, str] = {
    "jython_comparison/scripts/algebra_from_minimal_sets_smoke.py": (
        "Rust gap: AlgebraFromMinimalSets from cyclic2 reports unary operation "
        "`s` via getOperation; Java/Jython returns null for that symbol."
    ),
    "jython_comparison/scripts/algebras_smoke.py": (
        "Java bug: Jython subprocess exits after Operations commute INFO "
        "(fails to commute) before later Algebras smoke lines run."
    ),
    "jython_comparison/scripts/closer_smoke.py": (
        "Jython exit 1: Java Closer paths abort before CPython-only stdout tail."
    ),
    "jython_comparison/scripts/element_ops.py": (
        "Jython exit 1: extended SubProductElement probes abort the script early."
    ),
    "jython_comparison/scripts/example_ops.py": (
        "Jython exit 1: example package Java-only helpers stop the script early."
    ),
    "jython_comparison/scripts/free_algebra_smoke.py": (
        "Jython exit 1: findEq NullPointerException on Java path before stdout tail."
    ),
    "jython_comparison/scripts/general_algebra_smoke.py": (
        "Jython exit 1: GeneralAlgebra smoke stops before con/sub/empty lines."
    ),
    "jython_comparison/scripts/homomorphism_smoke.py": (
        "Jython exit 1: homomorphism smoke aborts before productHomo extra cases."
    ),
    "jython_comparison/scripts/io_surface.py": (
        "Jython exit 1: AlgebraIO list/reader surface differs before full stdout."
    ),
    "jython_comparison/scripts/malcev_smoke.py": (
        "Jython exit 1: Malcev/Jonsson paths abort before malcev_null case."
    ),
    "jython_comparison/scripts/matrix_power_algebra_smoke.py": (
        "Rust gap: PyMatrixPowerAlgebra getElement(0) is not iterable on CPython; "
        "Jython exits on Java-only checks before convert."
    ),
    "jython_comparison/scripts/parameterized_algebra_smoke.py": (
        "Jython exit 1: ParameterizedAlgebra constructor paths missing on Java run."
    ),
    "jython_comparison/scripts/polin_like_algebra_smoke.py": (
        "Jython exit 1: PolinLikeAlgebra smoke aborts before convert case."
    ),
    "jython_comparison/scripts/power_algebra_smoke.py": (
        "Jython exit 1: PowerAlgebra smoke aborts before convert/con/sub tail."
    ),
    "jython_comparison/scripts/product_algebra_smoke.py": (
        "Jython exit 1: ProductAlgebra smoke aborts before universeList/con tail."
    ),
    "jython_comparison/scripts/quotient_algebra_smoke.py": (
        "Jython exit 1: QuotientAlgebra smoke aborts before convert/con tail."
    ),
    "jython_comparison/scripts/subalgebra_smoke.py": (
        "Jython exit 1: Subalgebra smoke aborts before convert/restrict tail."
    ),
    "jython_comparison/scripts/subproduct_algebra_smoke.py": (
        "Jython exit 1: SubProductAlgebra convertToDefaultValueOps throws on "
        "Java without being caught before extra con/sub lines."
    ),
    "jython_comparison/scripts/unary_terms_monoid_smoke.py": (
        "Jython exit 1: UnaryTermsMonoid smoke aborts before convert case."
    ),
}


def repo_relative_script(script: Path, repo: Path) -> str:
    try:
        rel = script.resolve().relative_to(repo.resolve())
    except ValueError:
        rel = script
    return rel.as_posix()


def known_difference_reason(script: Path, repo: Path) -> Optional[str]:
    return KNOWN_OUTPUT_DIFFERENCES.get(repo_relative_script(script, repo))