"""Compare Jython package-surface snapshots across Jython 2.7.x versions.

Jython 2.7.3 typically lists only names the golden script imported. Jython 2.7.4
(and some JDKs) enumerate every public class in the jar package, which can both
add names and omit an imported name that ``dir(package)`` no longer reports.
The checked-in SAMPLE_* lines must still match exactly.
"""

from __future__ import annotations


def assert_jython_surface_contains_golden(actual: str, expected: str) -> None:
    actual_lines = [ln for ln in actual.strip().splitlines() if ln]
    expected_lines = [ln for ln in expected.strip().splitlines() if ln]

    def _meta(lines: list[str], prefix: str) -> str:
        for ln in lines:
            if ln.startswith(prefix):
                return ln.split(":", 1)[1].strip()
        raise AssertionError("missing {0} line".format(prefix))

    assert _meta(actual_lines, "MODULE:") == _meta(expected_lines, "MODULE:")
    assert _meta(actual_lines, "RUNTIME:") == _meta(expected_lines, "RUNTIME:")

    def _names(lines: list[str]) -> set[str]:
        return {ln.split(":", 1)[1].strip() for ln in lines if ln.startswith("NAME:")}

    actual_names = _names(actual_lines)
    expected_names = _names(expected_lines)
    missing = expected_names - actual_names
    extra = actual_names - expected_names
    if missing and not extra:
        raise AssertionError(
            "Jython surface missing expected names with no extras: {0}".format(
                sorted(missing)
            )
        )

    def _samples(lines: list[str]) -> list[str]:
        return [ln for ln in lines if ln.startswith("SAMPLE_")]

    assert _samples(actual_lines) == _samples(expected_lines)
