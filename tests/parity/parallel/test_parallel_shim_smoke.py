"""Smoke tests for ``org.uacalc.alg.parallel`` shim (core-alg-parallel slice)."""

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


def test_org_uacalc_alg_parallel_import_smoke():
    _ensure_python_org_on_path()
    import org.uacalc.alg.parallel as par  # noqa: PLC0415

    assert par.__name__ == "org.uacalc.alg.parallel"


def test_parallel_shim_exposes_pool_and_single_close():
    _ensure_python_org_on_path()
    import org.uacalc.alg.parallel as shim  # noqa: PLC0415

    assert hasattr(shim, "Pool")
    assert hasattr(shim, "SingleClose")
    assert hasattr(shim.SingleClose, "doOneStep")
    pool = shim.Pool()
    assert pool.is_initialized() in (True, False)


def test_parallel_minimal_if_bindings():
    _ensure_python_org_on_path()
    import org.uacalc.alg.parallel as shim  # noqa: PLC0415

    pool = getattr(shim, "Pool", None)
    if pool is None:
        pytest.skip("Pool not exposed on org.uacalc.alg.parallel shim")
    assert pool.is_initialized() in (True, False)
    assert hasattr(shim, "SingleClose")
