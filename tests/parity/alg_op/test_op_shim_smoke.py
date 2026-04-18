"""Smoke tests for ``org.uacalc.alg.op`` shim (core-alg-op slice)."""

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


def _lib_alg_op():
    try:
        import uacalc_lib  # noqa: PLC0415
    except ImportError:
        pytest.skip("uacalc_lib not available")
    _alg = getattr(uacalc_lib, "alg")
    sub = getattr(_alg, "op", None)
    if sub is not None:
        return sub
    try:
        return importlib.import_module("uacalc_lib.alg.op")
    except ImportError:
        return None


def test_org_uacalc_alg_op_import_smoke():
    _ensure_python_org_on_path()
    import org.uacalc.alg.op as op  # noqa: PLC0415

    assert op.__name__ == "org.uacalc.alg.op"


def test_op_shim_public_names_match_uacalc_lib():
    """Re-exported symbols match ``uacalc_lib.alg.op`` when that submodule exists."""
    lib_op = _lib_alg_op()
    _ensure_python_org_on_path()
    import org.uacalc.alg.op as shim  # noqa: PLC0415

    if lib_op is None:
        lib_public: set[str] = set()
    else:
        lib_public = {n for n in dir(lib_op) if not n.startswith("_")}
    shim_public = {n for n in dir(shim) if not n.startswith("_")}
    assert shim_public == lib_public
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib_op, name)


def test_op_minimal_if_bindings():
    lib_op = _lib_alg_op()
    if lib_op is None or not any(not n.startswith("_") for n in dir(lib_op)):
        pytest.skip("uacalc_lib.alg.op not bound; no CPython re-exports yet")
    _ensure_python_org_on_path()
    import org.uacalc.alg.op as shim  # noqa: PLC0415

    sym = getattr(shim, "OperationSymbol", None)
    if sym is None:
        pytest.skip("OperationSymbol not exposed on org.uacalc.alg.op shim")
    s = sym("*", 2)
    assert s is not None
