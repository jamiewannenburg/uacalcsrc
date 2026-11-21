"""Smoke tests for ``org.uacalc.lat`` shim (CPython delegates to ``uacalc_lib.lat``)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _ensure_python_org_on_path() -> None:
    """So ``import org.uacalc...`` resolves to python/org/."""
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


import sys as _sys

_TOOLS = REPO_ROOT / "tools"
if str(_TOOLS) not in _sys.path:
    _sys.path.insert(0, str(_TOOLS))
from strict_testing import guard_import_skip, guard_skip  # noqa: E402

try:
    import uacalc_lib  # noqa: F401
except ImportError as _exc:
    guard_import_skip("uacalc_lib", _exc)


def test_org_uacalc_lat_matches_uacalc_lib_lat_exports():
    if not hasattr(uacalc_lib, "lat"):
        guard_skip(
            "uacalc_lib.lat not available (native extension not built or stale build)"
        )
    _lat = uacalc_lib.lat

    _ensure_python_org_on_path()
    import org.uacalc.lat as lat_pkg  # pylint: disable=import-outside-toplevel
    assert lat_pkg.BasicLattice is _lat.BasicLattice
    assert lat_pkg.DiamondLattice is _lat.DiamondLattice

    direct = _lat.DiamondLattice()
    shim = lat_pkg.DiamondLattice()
    assert shim.cardinality() == direct.cardinality() == 4
