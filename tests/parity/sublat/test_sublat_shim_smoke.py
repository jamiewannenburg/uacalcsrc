"""Smoke tests for ``org.uacalc.alg.sublat`` shim (core-alg-sublat slice)."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _ensure_python_org_on_path() -> None:
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


def _lib_alg_sublat():
    try:
        import uacalc_lib  # noqa: PLC0415
    except ImportError:
        pytest.skip("uacalc_lib not available")
    _alg = getattr(uacalc_lib, "alg")
    sub = getattr(_alg, "sublat", None)
    if sub is not None:
        return sub
    try:
        return importlib.import_module("uacalc_lib.alg.sublat")
    except ImportError:
        return None


def test_org_uacalc_alg_sublat_import_smoke():
    _ensure_python_org_on_path()
    import org.uacalc.alg.sublat as sl  # noqa: PLC0415

    assert sl.__name__ == "org.uacalc.alg.sublat"


def test_sublat_shim_public_names_match_uacalc_lib():
    lib = _lib_alg_sublat()
    _ensure_python_org_on_path()
    import org.uacalc.alg.sublat as shim  # noqa: PLC0415

    if lib is None:
        lib_public: set[str] = set()
    else:
        lib_public = {n for n in dir(lib) if not n.startswith("_")}
    shim_public = {n for n in dir(shim) if not n.startswith("_")}
    assert shim_public == lib_public
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib, name)


def test_sublat_minimal_if_bindings():
    lib = _lib_alg_sublat()
    if lib is None or not any(not n.startswith("_") for n in dir(lib)):
        pytest.skip("uacalc_lib.alg.sublat not bound; no CPython re-exports yet")
    _ensure_python_org_on_path()
    import org.uacalc.alg.sublat as shim  # noqa: PLC0415

    bs = getattr(shim, "BasicSet", None)
    if bs is None:
        pytest.skip("BasicSet not exposed on org.uacalc.alg.sublat shim")
    s = bs([0, 1])
    assert s.size() == 2
