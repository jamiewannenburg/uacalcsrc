"""Smoke tests for ``org.uacalc.terms`` shim (core-terms slice)."""

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


def _uacalc_lib_terms():
    try:
        import uacalc_lib  # noqa: PLC0415
    except ImportError:
        pytest.skip("uacalc_lib not available")
    try:
        return getattr(uacalc_lib, "terms")
    except AttributeError as exc:
        pytest.skip(f"uacalc_lib.terms not available: {exc}")


def test_org_uacalc_terms_import_smoke():
    _uacalc_lib_terms()
    _ensure_python_org_on_path()
    import org.uacalc.terms as terms  # noqa: PLC0415

    assert terms.__name__ == "org.uacalc.terms"


def test_terms_shim_public_names_match_uacalc_lib():
    """Shim re-exports ``uacalc_lib.terms`` and adds Jython ``Terms`` / ``Variable``."""
    lib_terms = _uacalc_lib_terms()
    _ensure_python_org_on_path()
    import org.uacalc.terms as shim  # noqa: PLC0415

    lib_public = {n for n in dir(lib_terms) if not n.startswith("_")}
    shim_public = {n for n in dir(shim) if not n.startswith("_")}
    assert lib_public <= shim_public
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib_terms, name)
    assert "Terms" in shim_public
    assert "Variable" in shim_public
    assert shim.Variable is shim.VariableImp


def test_terms_minimal_if_bindings():
    _uacalc_lib_terms()
    _ensure_python_org_on_path()
    import org.uacalc.terms as terms  # noqa: PLC0415

    assert terms.is_valid_var_string("x") is True
