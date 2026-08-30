"""Smoke tests for ``org.uacalc.alg.parallel`` shim (core-alg-parallel slice)."""

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


def _lib_alg_parallel():
    try:
        import uacalc_lib  # noqa: PLC0415
    except ImportError:
        pytest.skip("uacalc_lib not available")
    _alg = getattr(uacalc_lib, "alg")
    sub = getattr(_alg, "parallel", None)
    if sub is not None:
        return sub
    try:
        return importlib.import_module("uacalc_lib.alg.parallel")
    except ImportError:
        return None


def test_org_uacalc_alg_parallel_import_smoke():
    _ensure_python_org_on_path()
    import org.uacalc.alg.parallel as par  # noqa: PLC0415

    assert par.__name__ == "org.uacalc.alg.parallel"


def test_parallel_shim_public_names_match_uacalc_lib():
    lib = _lib_alg_parallel()
    _ensure_python_org_on_path()
    import org.uacalc.alg.parallel as shim  # noqa: PLC0415

    if lib is None:
        lib_public: set[str] = set()
    else:
        lib_public = {n for n in dir(lib) if not n.startswith("_")}
    shim_public = {n for n in dir(shim) if not n.startswith("_")}
    assert shim_public == lib_public
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib, name)


def test_parallel_minimal_if_bindings():
    lib = _lib_alg_parallel()
    if lib is None or not any(not n.startswith("_") for n in dir(lib)):
        pytest.skip("uacalc_lib.alg.parallel not bound; no CPython re-exports yet")
    _ensure_python_org_on_path()
    import org.uacalc.alg.parallel as shim  # noqa: PLC0415

    pool = getattr(shim, "Pool", None)
    if pool is None:
        pytest.skip("Pool not exposed on org.uacalc.alg.parallel shim")
    # Static helpers used by legacy scripts / java_wrapper Pool tests
    assert pool.is_initialized() in (True, False)
