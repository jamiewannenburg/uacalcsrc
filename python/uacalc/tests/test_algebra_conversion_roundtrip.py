"""Round-trip tests for Jamie-style algebra/operation conversion (org.uacalc)."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from org.uacalc.alg import BasicAlgebra
from org.uacalc.alg.op import AbstractOperation, OperationSymbol, IntOperation
from org.uacalc.eq import Equation
from org.uacalc.terms import VariableImp
from org.uacalc.io import AlgebraIO


class _SubBasicAlgebra(BasicAlgebra):
    """User subclass of the Jython-facing BasicAlgebra wrapper."""


def _flip_bin_op(card: int):
    class Flip(AbstractOperation):
        def intValueAt(self, args):
            return (int(args[0]) + int(args[1]) + 1) % card

    return Flip("flip", 2, card)


def test_nullary_mace4_style_uses_algebra_cardinality():
    """Mace4 nullary ops use AbstractOperation set size 1; coercion must use |A|."""

    class Const(AbstractOperation):
        def intValueAt(self, _args):
            return 2

    card = 3
    op = Const("e", 0, 1)
    alg = BasicAlgebra("mace4-nullary", card, [op])
    assert alg.cardinality() == card
    const = alg.getOperation(OperationSymbol("e", 0))
    assert const.intValueAt([]) == 2


def test_callable_defined_operations_round_trip():
    card = 4

    def plus_mod(args):
        return (int(args[0]) + int(args[1])) % card

    op = IntOperation.from_int_value_at("plus", 2, card, plus_mod)
    alg = BasicAlgebra("callable", card, [op])
    plus = alg.getOperation(OperationSymbol("plus", 2))
    for a in range(card):
        for b in range(card):
            assert plus.intValueAt([a, b]) == (a + b) % card


def test_labeled_universe_order_preserved_in_get_universe():
    order = ["z", "a", "m"]
    alg = BasicAlgebra("labels", order, [_flip_bin_op(3)])
    assert alg.get_universe() == order
    assert alg.getElement(0) == "z"
    assert alg.getElement(1) == "a"
    assert alg.elementIndex("m") == 2


def test_subclass_wrapper_accepted_by_find_failure_map():
    card = 2
    xor = IntOperation.binary_xor("xor")
    sub = _SubBasicAlgebra("sub", card, [xor])
    x, y = VariableImp("x"), VariableImp("y")
    eq = Equation(x, y)
    assert eq.findFailureMap(sub) is not None


def test_failure_map_values_use_universe_labels():
    order = ["red", "green"]
    alg = BasicAlgebra("colors", order, [_flip_bin_op(2)])
    x, y = VariableImp("x"), VariableImp("y")
    eq = Equation(x, y)
    result = eq.findFailureMap(alg)
    assert result is not None
    vals = list(result.values())
    assert all(v in order for v in vals)


def test_dense_integer_ua_write_round_trip():
    """Java-style dense integer universes round-trip through write/read."""
    alg = BasicAlgebra("c4", 4, [_flip_bin_op(4)])
    with tempfile.NamedTemporaryFile(suffix=".ua", delete=False) as tmp:
        path = Path(tmp.name)
    try:
        AlgebraIO.writeAlgebraFile(alg, str(path))
        back = AlgebraIO.readAlgebraFile(str(path))
        assert back.cardinality() == 4
        flip = back.getOperation(OperationSymbol("flip", 2))
        assert flip.intValueAt([0, 1]) == alg.getOperation(
            OperationSymbol("flip", 2)
        ).intValueAt([0, 1])
    finally:
        path.unlink(missing_ok=True)