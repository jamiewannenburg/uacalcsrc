# coding: utf-8
# Dual-runtime parity script for PolinLikeAlgebra.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import PolinLikeAlgebra
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
    p = PolinLikeAlgebra("pol", c2, c2, None, 0, 0)
    print("named=" + str(p.getName()))
    print("card=" + str(p.cardinality()))
    p.setName("P")
    print("renamed=" + str(p.getName()))
    print("type=" + str(p.algebraType()))
    print("nops=" + str(len(list(p.operations()))))
    print("univList=" + str(p.getUniverseList()))
    print("getElement0=" + str(p.getElement(0)))
    print("eidx=" + str(p.elementIndex(0)))
    _show("op_plus", lambda: p.getOperation(plus) is not None)
    _show("convert", lambda: p.convertToDefaultValueOps())


if __name__ == "__main__":
    test()
