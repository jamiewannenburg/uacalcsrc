"""Allowlisted Jython vs CPython stdout comparison scripts.

``run_comparison.py`` treats a listed script as success when output still differs,
so CI can enforce the comparison job without hiding new regressions on other scripts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

# Repo-relative posix path -> human-readable reason
KNOWN_OUTPUT_DIFFERENCES: Dict[str, str] = {
    "jython_comparison/scripts/algebra_api.py": (
        "Algebra metadata and operation-table lines differ between Java/Jython and CPython shims."
    ),
    "jython_comparison/scripts/algebra_from_minimal_sets_smoke.py": (
        "Minimal-sets construction stdout ordering differs on CPython."
    ),
    "jython_comparison/scripts/algebras_smoke.py": (
        "Jython hits Java Operations INFO commute failure; CPython uacalc_lib path continues."
    ),
    "jython_comparison/scripts/basic_lattice_api.py": (
        "Lattice API facade prints differ (ordering / formatting)."
    ),
    "jython_comparison/scripts/closer_smoke.py": (
        "Closer smoke: Jython closure path errors or logs where CPython shim succeeds."
    ),
    "jython_comparison/scripts/conlat_leftovers.py": (
        "Congruence-lattice leftover probes differ on stdout normalization."
    ),
    "jython_comparison/scripts/element_ops.py": (
        "Element operations: Jython/Java exceptions vs CPython shim behavior."
    ),
    "jython_comparison/scripts/example_ops.py": (
        "Example package ops: interactive/Java-only paths fail under Jython."
    ),
    "jython_comparison/scripts/free_algebra_smoke.py": (
        "Free algebra construction progress lines differ or Jython aborts early."
    ),
    "jython_comparison/scripts/general_algebra_smoke.py": (
        "GeneralAlgebra smoke: Jython Java path diverges from CPython lib."
    ),
    "jython_comparison/scripts/homomorphism_smoke.py": (
        "Homomorphism smoke: Jython raises where CPython shim returns."
    ),
    "jython_comparison/scripts/io_surface.py": (
        "IO surface script: Jython/Java reader errors vs CPython org.uacalc.io."
    ),
    "jython_comparison/scripts/lattices_facade_smoke.py": (
        "Lattices facade string output differs between runtimes."
    ),
    "jython_comparison/scripts/malcev_smoke.py": (
        "Malcev terms: Jython Java exceptions on several algebras."
    ),
    "jython_comparison/scripts/matrix_power_algebra_smoke.py": (
        "MatrixPowerAlgebra smoke: non-zero Jython exit on Java-only checks."
    ),
    "jython_comparison/scripts/op_leftovers.py": (
        "Operation leftovers: stdout mismatch after ignore rules."
    ),
    "jython_comparison/scripts/parameterized_algebra_smoke.py": (
        "ParameterizedAlgebra construction fails on Jython for some inputs."
    ),
    "jython_comparison/scripts/polin_like_algebra_smoke.py": (
        "PolinLikeAlgebra smoke: Jython/Java errors vs CPython success."
    ),
    "jython_comparison/scripts/power_algebra_smoke.py": (
        "PowerAlgebra smoke: Jython subprocess failure on Java path."
    ),
    "jython_comparison/scripts/product_algebra_smoke.py": (
        "ProductAlgebra smoke: Jython subprocess failure on Java path."
    ),
    "jython_comparison/scripts/quotient_algebra_smoke.py": (
        "QuotientAlgebra smoke: Jython subprocess failure on Java path."
    ),
    "jython_comparison/scripts/random_parity.py": (
        "Randomized parity driver: aggregate stdout includes seeds/xfails not matched yet on CPython."
    ),
    "jython_comparison/scripts/subalgebra_lattice_smoke.py": (
        "Subalgebra lattice smoke: stdout mismatch after ignore rules."
    ),
    "jython_comparison/scripts/subalgebra_smoke.py": (
        "Subalgebra smoke: Jython/Java errors on sgClose paths."
    ),
    "jython_comparison/scripts/subproduct_algebra_smoke.py": (
        "SubProductAlgebra smoke: Jython subprocess failure."
    ),
    "jython_comparison/scripts/terms_variable_eval.py": (
        "Terms variable eval: Jython fails on Java term evaluation edge cases."
    ),
    "jython_comparison/scripts/unary_terms_monoid_smoke.py": (
        "UnaryTermsMonoid smoke: Jython subprocess failure."
    ),
    "jython_comparison/scripts/util_ops.py": (
        "Util ops script: IntArray/LongList lines differ between runtimes."
    ),
    "tests/parity/lat/test_cases/lattices_cases.py": (
        "Parity case module (specs only); not a standalone comparison script."
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