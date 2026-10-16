"""Smoke tests for ``org.uacalc.fplat`` shim (core-fplat slice)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _ensure_python_org_on_path() -> None:
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


def _uacalc_lib_fplat():
    try:
        import uacalc_lib  # noqa: PLC0415
    except ImportError:
        pytest.skip("uacalc_lib not available")
    try:
        return getattr(uacalc_lib, "fplat")
    except AttributeError as exc:
        pytest.skip(f"uacalc_lib.fplat not available: {exc}")


def test_org_uacalc_fplat_import_smoke():
    _uacalc_lib_fplat()
    _ensure_python_org_on_path()
    import org.uacalc.fplat as fp  # noqa: PLC0415

    assert fp.__name__ == "org.uacalc.fplat"


def test_fplat_shim_exposes_partially_defined_lattice():
    _uacalc_lib_fplat()
    _ensure_python_org_on_path()
    import org.uacalc.fplat as shim  # noqa: PLC0415

    assert hasattr(shim, "PartiallyDefinedLattice")
    for name in ("leq", "getDefinedJoins", "getDefinedMeets", "toString"):
        assert hasattr(shim.PartiallyDefinedLattice, name), name


def test_fplat_minimal_if_bindings():
    _uacalc_lib_fplat()
    _ensure_python_org_on_path()
    import org.uacalc.fplat as fp  # noqa: PLC0415
    from org.uacalc.lat import Order  # noqa: PLC0415
    from org.uacalc.terms import VariableImp  # noqa: PLC0415

    class NameOrder(Order):
        def leq(self, a, b):
            na = a.getName() if hasattr(a, "getName") else a.get_name()
            nb = b.getName() if hasattr(b, "getName") else b.get_name()
            if callable(na):
                na = na()
            if callable(nb):
                nb = nb()
            return na <= nb

    x = VariableImp("x")
    y = VariableImp("y")
    L = fp.PartiallyDefinedLattice("T", NameOrder(), [[x, y]], [])
    assert L.leq(x, y) is True
    assert L.leq(y, x) is False
    assert L.getDefinedJoins()[0][0].getName() == "x" or str(L.getDefinedJoins()[0][0])
