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


def test_fplat_shim_public_names_match_uacalc_lib():
    lib_fplat = _uacalc_lib_fplat()
    _ensure_python_org_on_path()
    import org.uacalc.fplat as shim  # noqa: PLC0415

    lib_public = {n for n in dir(lib_fplat) if not n.startswith("_")}
    shim_public = {n for n in dir(shim) if not n.startswith("_")}
    assert shim_public == lib_public
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib_fplat, name)


def test_fplat_minimal_if_bindings():
    _uacalc_lib_fplat()
    _ensure_python_org_on_path()
    import org.uacalc.fplat as fp  # noqa: PLC0415

    L = fp.PartiallyDefinedLattice("T", [], [])
    assert "T" in str(L)
