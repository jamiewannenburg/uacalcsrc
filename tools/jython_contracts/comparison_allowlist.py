"""Per-script Jython vs CPython stdout comparison overrides.

``run_comparison.py`` applies ``ignore_line_patterns`` / ``ignore_json_paths`` during
comparison. ``allow_remaining_mismatch`` is only for scripts whose entire stdout is
an expected gap (Rust/smoke), not for narrowing within a large snapshot script.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class ScriptComparisonOverrides:
    reason: str
    ignore_line_patterns: Tuple[str, ...] = ()
    ignore_json_paths: Tuple[str, ...] = ()
    allow_remaining_mismatch: bool = False


# Repo-relative posix path -> comparison overrides
KNOWN_OUTPUT_DIFFERENCES: Dict[str, ScriptComparisonOverrides] = {
    "jython_comparison/scripts/algebra_from_minimal_sets_smoke.py": ScriptComparisonOverrides(
        reason=(
            "Rust gap: AlgebraFromMinimalSets op_s getOperation returns null on "
            "Java/Jython but a truthy op on the org.uacalc shim."
        ),
        allow_remaining_mismatch=True,
    ),
    "jython_comparison/scripts/matrix_power_algebra_smoke.py": ScriptComparisonOverrides(
        reason=(
            "Rust gap: MatrixPowerAlgebra getElement(0) NPE on shim; "
            "op_plus False vs True on Java."
        ),
        allow_remaining_mismatch=True,
    ),
    "jython_comparison/scripts/basic_set_ops.py": ScriptComparisonOverrides(
        reason=(
            "Known Java bug: BasicSet.union uses lst.contains(i) on the index; "
            "{0,2}∪{1,3} is [0,2,3] on Java/Jython vs [0,1,2,3] on CPython."
        ),
        ignore_line_patterns=(r"^union=.*",),
    ),
    "jython_comparison/scripts/random_parity.py": ScriptComparisonOverrides(
        reason=(
            "Known Java bug: BasicSet.union index typo; only basicset.union "
            "differs from Java."
        ),
        ignore_json_paths=("basicset.union",),
    ),
}


def repo_relative_script(script: Path, repo: Path) -> str:
    try:
        rel = script.resolve().relative_to(repo.resolve())
    except ValueError:
        rel = script
    return rel.as_posix()


def script_comparison_overrides(script: Path, repo: Path) -> Optional[ScriptComparisonOverrides]:
    return KNOWN_OUTPUT_DIFFERENCES.get(repo_relative_script(script, repo))


def known_difference_reason(script: Path, repo: Path) -> Optional[str]:
    """Human-readable note when comparison succeeds only via overrides."""
    overrides = script_comparison_overrides(script, repo)
    if overrides is None:
        return None
    if overrides.allow_remaining_mismatch or overrides.ignore_line_patterns or overrides.ignore_json_paths:
        return overrides.reason
    return overrides.reason