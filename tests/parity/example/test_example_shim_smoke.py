"""Smoke tests for ``org.uacalc.example`` shim (examples-org slice).

Golden stdout: ``golden_example_surface.py`` + fixtures + ``test_example_golden_surface.py``.
CPython ports the 16 demo classes; Jython uses the Java package.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

DEMO_CLASS_NAMES = (
    "Average",
    "ConLyndonF3",
    "FilteringAlgebras",
    "FiniteField",
    "FinitelyPresentedAlg",
    "HasConstantTuple",
    "HasKaryNU",
    "Jipsen",
    "KKMVWExample",
    "Kearnes",
    "MembershipTester",
    "Michalewski",
    "NoSymGroup",
    "ParallelClose8",
    "TupleStream",
    "Type1",
)


def _ensure_python_org_on_path() -> None:
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


def test_org_uacalc_example_import_smoke():
    _ensure_python_org_on_path()
    import org.uacalc.example as ex  # noqa: PLC0415

    assert ex.__name__ == "org.uacalc.example"


def test_example_shim_exposes_demo_classes():
    _ensure_python_org_on_path()
    import org.uacalc.example as shim  # noqa: PLC0415

    assert shim.__name__ == "org.uacalc.example"
    for name in DEMO_CLASS_NAMES:
        assert hasattr(shim, name), name


def test_example_gui_entry_points_are_documented():
    if sys.platform.startswith("java"):
        pytest.skip("Environment: CPython-only skip/xfail registry for demo mains")
    _ensure_python_org_on_path()
    from org.uacalc.example._demos import GUI_OR_INTERACTIVE  # noqa: PLC0415

    assert "ParallelClose8" in GUI_OR_INTERACTIVE
    assert "FilteringAlgebras.main" in GUI_OR_INTERACTIVE
    assert "HasKaryNU.main" in GUI_OR_INTERACTIVE


