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


def test_make_constant_term_isinstance_and_constructor():
    """``NonVariableTerm`` must stay the library class so isinstance works.

    Expected strings/depth/length/variable lists are the Java UACalc outputs
    from compiling ``org/uacalc`` (OpenJDK 21) and running
    ``NonVariableTerm.makeConstantTerm`` / ``new NonVariableTerm(...)``.
    """
    lib_terms = _uacalc_lib_terms()
    _ensure_python_org_on_path()
    from org.uacalc.alg.op import OperationSymbol  # noqa: PLC0415
    from org.uacalc.terms import NonVariableTerm, VariableImp  # noqa: PLC0415

    assert NonVariableTerm is lib_terms.NonVariableTerm

    sym = OperationSymbol("e", 0)
    const = NonVariableTerm.makeConstantTerm(sym)
    assert isinstance(const, NonVariableTerm)
    assert str(const) == "e()"
    assert const.depth() == 1
    assert const.length() == 1
    assert [getattr(v, "getName", lambda: v)() for v in list(const.getVariableList())] == []
    assert const.isaVariable() is False

    x = VariableImp("x")
    f = OperationSymbol("f", 2)
    compound = NonVariableTerm(f, [x, const])
    assert isinstance(compound, NonVariableTerm)
    assert str(compound) == "f(x,e())"
    assert compound.depth() == 2
    assert compound.length() == 3
    assert [v.getName() for v in list(compound.getVariableList())] == ["x"]


def test_make_constant_term_java_outputs():
    """Constant-term and compound-term values must match Java UACalc exactly."""
    _uacalc_lib_terms()
    _ensure_python_org_on_path()
    from org.uacalc.alg.op import OperationSymbol  # noqa: PLC0415
    from org.uacalc.terms import NonVariableTerm, VariableImp  # noqa: PLC0415

    for name in ("e", "zero", "identity"):
        term = NonVariableTerm.makeConstantTerm(OperationSymbol(name, 0))
        assert isinstance(term, NonVariableTerm)
        assert str(term) == "{}()".format(name)
        assert term.depth() == 1
        assert term.length() == 1
        assert [v.getName() for v in list(term.getVariableList())] == []

    x = VariableImp("x")
    y = VariableImp("y")
    const_identity = NonVariableTerm.makeConstantTerm(OperationSymbol("identity", 0))
    compound = NonVariableTerm(OperationSymbol("g", 3), [x, y, const_identity])
    assert str(compound) == "g(x,y,identity())"
    assert compound.depth() == 2
    assert compound.length() == 4
