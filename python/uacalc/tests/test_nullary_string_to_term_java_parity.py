"""Goldens: Java Terms.stringToTerm nullary / constant syntax (Jython = source of truth)."""
from __future__ import annotations

from pathlib import Path

import pytest

from org.uacalc._exceptions import IllegalArgumentException, NullPointerException
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.io import AlgebraIO
from org.uacalc.terms import NonVariableTerm, Terms, Variable, VariableImp

REPO = Path(__file__).resolve().parents[3]
B2 = REPO / "tests" / "jython_scripts" / "phd" / "input" / "b2.ua"


@pytest.fixture(scope="module")
def b2():
    assert B2.is_file(), "run tools/copy_phd_scripts.py first"
    return AlgebraIO.readAlgebraFile(str(B2))


def test_bare_e_is_variable():
    t = Terms.stringToTerm("e")
    assert t.isaVariable()
    assert str(t) == "e"


def test_bare_e_int_eval_needs_binding(b2):
    t = Terms.stringToTerm("e")
    with pytest.raises(NullPointerException):
        t.intEval(b2, {Variable.x: 0})


@pytest.mark.xfail(
    reason=(
        "Known Java bug: Terms.stringToTerm rejects every nullary op() with "
        "IAE empty string; Rust accepts e()."
    ),
    strict=True,
)
def test_e_call_parses_like_java():
    with pytest.raises(IllegalArgumentException):
        Terms.stringToTerm("e()")


def test_make_constant_term_e_evaluates(b2):
    c = NonVariableTerm.makeConstantTerm(OperationSymbol("e", 0))
    assert c.intEval(b2, {Variable.x: 0}) == 1


def test_shim_e_call_int_eval_matches_make_constant(b2):
    """Document current shim behaviour (differs from Java string parser)."""
    t = Terms.stringToTerm("e()")
    assert not t.isaVariable()
    assert t.intEval(b2, {Variable.x: 0}) == 1


def test_variable_e_with_binding(b2):
    vi = VariableImp("e")
    assert Terms.stringToTerm("e").intEval(b2, {vi: 1}) == 1