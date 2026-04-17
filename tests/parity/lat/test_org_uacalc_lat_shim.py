"""Smoke tests for ``org.uacalc.lat`` shim (CPython delegates to ``uacalc_lib.lat``)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]


def _ensure_python_org_on_path() -> None:
    """So ``import org.uacalc...`` resolves to python/org/."""
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


try:
    import uacalc_lib  # noqa: F401
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)


def test_org_uacalc_lat_matches_uacalc_lib_lat_exports():
    if not hasattr(uacalc_lib, "lat"):
        pytest.skip(
            "uacalc_lib.lat not available (native extension not built or stub import)"
        )

    _ensure_python_org_on_path()
    import org.uacalc.lat as lat_pkg  # pylint: disable=import-outside-toplevel

    _lat = getattr(uacalc_lib, "lat")
    assert lat_pkg.BasicLattice is _lat.BasicLattice
    assert lat_pkg.DiamondLattice is _lat.DiamondLattice

    direct = _lat.DiamondLattice()
    shim = lat_pkg.DiamondLattice()
    assert shim.cardinality() == direct.cardinality() == 4
