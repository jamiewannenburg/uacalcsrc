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
        pytest.skip("CPython-only skip/xfail registry")
    _ensure_python_org_on_path()
    from org.uacalc.example._demos import GUI_OR_INTERACTIVE  # noqa: PLC0415

    assert "ParallelClose8" in GUI_OR_INTERACTIVE
    assert "FilteringAlgebras.main" in GUI_OR_INTERACTIVE
    assert "HasKaryNU.main" in GUI_OR_INTERACTIVE


@pytest.mark.skip(reason="ForkJoinPool timing demo; not a packaged org.uacalc.example class")
def test_parallel_close_unpackaged():
    raise AssertionError("unreachable")


@pytest.mark.skip(reason="Computes Con(F(4)) of the Lyndon algebra; too heavy for parity")
def test_conlyndon_f3_main_too_heavy():
    raise AssertionError("unreachable")


@pytest.mark.skip(reason="HasKaryNU.hasNUHorowitz uses ProgressReport and a large BigProduct close")
def test_haskary_nu_progress_report():
    raise AssertionError("unreachable")


@pytest.mark.skip(reason="FilteringAlgebras.main uses Malcev.sdMeetIdempotent (Malcev is out of scope)")
def test_filtering_algebras_main_malcev():
    raise AssertionError("unreachable")


@pytest.mark.skip(reason="Type1.main prints subtraces of a size-5 matrix power; interactive/demo main")
def test_type1_main_matrix_power():
    raise AssertionError("unreachable")


@pytest.mark.skip(reason="TupleStream.main is a serial vs parallel timing benchmark")
def test_tuple_stream_main_timing():
    raise AssertionError("unreachable")


@pytest.mark.skip(reason="NoSymGroup.main writes SymTestGroup.ua and runs a large HasConstantTuple search")
def test_nosymgroup_main_search():
    raise AssertionError("unreachable")
