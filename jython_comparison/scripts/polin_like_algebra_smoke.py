# coding: utf-8
# Dual-runtime parity script for PolinLikeAlgebra.
from __future__ import print_function

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parity_probe import probe as _show, section

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import PolinLikeAlgebra
from org.uacalc.alg.op import OperationSymbol



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
    _show("construct", lambda: PolinLikeAlgebra.constructPolinAlgebra(c2, 0))
    _show("polinize00", lambda: p.polinizeOperation(plus).intValueAt([0, 0]))
    _show("intValueAt00", lambda: p.getOperation(plus).intValueAt([0, 0]))
    _show("convert", lambda: p.convertToDefaultValueOps())


if __name__ == "__main__":
    test()
