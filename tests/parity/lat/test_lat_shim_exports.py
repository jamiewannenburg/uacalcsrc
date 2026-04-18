"""``org.uacalc.lat`` namespace and key imports on CPython (Jython-style parity)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

_EXPECTED_DIR_SUBSET = (
    "BasicLattice",
    "BooleanLattice",
    "DiamondLattice",
    "DivisibilityOrder",
    "LatticeGraphData",
    "NaturalOrder",
    "OrderedSet",
    "OrderedSetBasicSet",
    "OrderedSetPartition",
    "PrefixOrder",
)


def _ensure_python_org_on_path() -> None:
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


try:
    import uacalc_lib  # noqa: F401
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)


def test_org_uacalc_lat_dir_includes_core_java_names():
    _ensure_python_org_on_path()
    import org.uacalc.lat as lat_pkg  # pylint: disable=import-outside-toplevel

    names = set(n for n in dir(lat_pkg) if not n.startswith("_"))
    for n in _EXPECTED_DIR_SUBSET:
        assert n in names, f"missing {n} in dir(org.uacalc.lat)"


def test_org_uacalc_lat_key_types_match_uacalc_lib():
    if not hasattr(uacalc_lib, "lat"):
        pytest.skip("uacalc_lib.lat not available")

    _ensure_python_org_on_path()
    import org.uacalc.lat as lat_pkg  # pylint: disable=import-outside-toplevel

    _lat = getattr(uacalc_lib, "lat")
    assert lat_pkg.BasicLattice is _lat.BasicLattice
    assert lat_pkg.BooleanLattice is _lat.BooleanLattice
    assert lat_pkg.DiamondLattice is _lat.DiamondLattice
