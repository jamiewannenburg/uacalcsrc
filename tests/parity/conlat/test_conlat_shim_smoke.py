"""Smoke tests for ``org.uacalc.alg.conlat`` shim (core-alg-conlat slice)."""

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


def _lib_alg_conlat():
    try:
        import uacalc_lib  # noqa: PLC0415
    except ImportError:
        pytest.skip("uacalc_lib not available")
    _alg = getattr(uacalc_lib, "alg")
    sub = getattr(_alg, "conlat", None)
    if sub is not None:
        return sub
    try:
        return importlib.import_module("uacalc_lib.alg.conlat")
    except ImportError:
        return None


def test_org_uacalc_alg_conlat_import_smoke():
    _ensure_python_org_on_path()
    import org.uacalc.alg.conlat as cl  # noqa: PLC0415

    assert cl.__name__ == "org.uacalc.alg.conlat"


def test_conlat_shim_public_names_match_uacalc_lib():
    lib = _lib_alg_conlat()
    _ensure_python_org_on_path()
    import org.uacalc.alg.conlat as shim  # noqa: PLC0415

    if lib is None:
        lib_public: set[str] = set()
    else:
        lib_public = {n for n in dir(lib) if not n.startswith("_")}
    shim_public = {n for n in dir(shim) if not n.startswith("_")}
    assert shim_public == lib_public
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib, name)


def test_conlat_minimal_if_bindings():
    lib = _lib_alg_conlat()
    if lib is None or not any(not n.startswith("_") for n in dir(lib)):
        pytest.skip("uacalc_lib.alg.conlat not bound; no CPython re-exports yet")
    _ensure_python_org_on_path()
    import org.uacalc.alg.conlat as shim  # noqa: PLC0415

    import uacalc_lib  # noqa: PLC0415

    CGL = getattr(shim, "CongruenceLattice", None)
    if CGL is None:
        pytest.skip("CongruenceLattice not exposed on org.uacalc.alg.conlat shim")
    alg = uacalc_lib.alg.BasicAlgebra("T", [0, 1, 2], [])
    lat = CGL(alg)
    assert lat is not None
