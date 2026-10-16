# coding: utf-8
# Dual-runtime parity script for MatrixPowerAlgebra.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import MatrixPowerAlgebra
from org.uacalc.alg.op import OperationSymbol


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    plus = OperationSymbol("+", 2)
    m = MatrixPowerAlgebra("mp", c2, 1)
    print("named=" + str(m.getName()))
    print("card=" + str(m.cardinality()))
    m.setName("M1")
    print("renamed=" + str(m.getName()))
    print("type=" + str(m.algebraType()))
    print("power=" + str(m.getPower()))
    print("root=" + str(m.getRoot().getName()))
    print("parent=" + str(m.parent().getName()))
    print("parents=" + str([a.getName() for a in m.parents()]))
    _show("getElement0", lambda: list(m.getElement(0)))
    _show("op_plus", lambda: m.getOperation(plus) is not None)
    _show("convert", lambda: m.convertToDefaultValueOps())
    m2 = MatrixPowerAlgebra(c2, 1)
    print("unnamed=" + str(m2.getName()))


if __name__ == "__main__":
    test()
