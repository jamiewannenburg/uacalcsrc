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
        "Rust gap: AlgebraFromMinimalSets op_s getOperation returns null on "
        "Java/Jython but a truthy op on the org.uacalc shim."
    ),
    "jython_comparison/scripts/algebras_smoke.py": (
        "Java bug: Algebras.findInClone([], c2) raises NullPointerException on "
        "Java vs IllegalArgumentException on the shim (EXC category differs)."
    ),
    "jython_comparison/scripts/closer_smoke.py": (
        "Java bug: Closer(None, gens) does not throw on Java (prints handle) "
        "while the shim reports EXC ctor_null: NullPointerException."
    ),
    "jython_comparison/scripts/example_ops.py": (
        "Wrapper gap: example package stdout differs (fp_eq, demo mains, heavy demos); "
        "script completes on both runtimes after probe hardening."
    ),
    "jython_comparison/scripts/io_surface.py": (
        "Wrapper gap: AlgebraIO list readers return cardinality 1 vs 2 on list files; "
        "writerXML throws NPE on Jython during AlgebraWriter.writeBasicAlgebra."
    ),
    "jython_comparison/scripts/matrix_power_algebra_smoke.py": (
        "Rust gap: MatrixPowerAlgebra getElement(0) NPE on shim; op_plus False vs True on Java."
    ),
    "jython_comparison/scripts/parameterized_algebra_smoke.py": (
        "Java bug: ParameterizedAlgebra.getParameterMap with null parameterNames "
        "throws NPE on Java only (null_names / set_names probes)."
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