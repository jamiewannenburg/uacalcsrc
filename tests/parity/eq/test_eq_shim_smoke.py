"""Smoke tests for ``org.uacalc.eq`` shim (core-eq slice)."""

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


def _uacalc_lib_eq():
    try:
        import uacalc_lib  # noqa: PLC0415
    except ImportError:
        pytest.skip("uacalc_lib not available")
    try:
        return getattr(uacalc_lib, "eq")
    except AttributeError as exc:
        pytest.skip(f"uacalc_lib.eq not available: {exc}")


def test_org_uacalc_eq_import_smoke():
    _uacalc_lib_eq()
    _ensure_python_org_on_path()
    import org.uacalc.eq as eq  # noqa: PLC0415

    assert eq.__name__ == "org.uacalc.eq"


def test_eq_shim_public_names_match_uacalc_lib():
    lib_eq = _uacalc_lib_eq()
    _ensure_python_org_on_path()
    import org.uacalc.eq as shim  # noqa: PLC0415

    lib_public = {n for n in dir(lib_eq) if not n.startswith("_")}
    shim_public = {n for n in dir(shim) if not n.startswith("_")}
    assert shim_public == lib_public
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib_eq, name)


def test_eq_minimal_if_bindings():
    import uacalc_lib  # noqa: PLC0415

    _uacalc_lib_eq()
    _ensure_python_org_on_path()
    import org.uacalc.eq as eq  # noqa: PLC0415

    op = uacalc_lib.alg.OperationSymbol("*", 2)
    out = eq.associative_law(op)
    text = out if isinstance(out, str) else str(out)
    assert "=" in text
