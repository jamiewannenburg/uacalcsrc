# coding: utf-8
# Dual-runtime parity script for AlgebraFromMinimalSets.
from __future__ import print_function

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parity_probe import probe as _show, section

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import AlgebraFromMinimalSets
from org.uacalc.alg.op import OperationSymbol



def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    a = AlgebraFromMinimalSets("fromC2", c2)
    print("named=" + str(a.getName()))
    print("card=" + str(a.cardinality()))
    a.setName("Min")
    print("renamed=" + str(a.getName()))
    print("type=" + str(a.algebraType()))
    print("nops=" + str(len(list(a.operations()))))
    print("univList=" + str(a.getUniverseList()))
    _show("getElement0", lambda: a.getElement(0))
    _show("eidx0", lambda: a.elementIndex(0))
    _show("op_s", lambda: a.getOperation(OperationSymbol("s", 1)) is not None)
    unnamed = AlgebraFromMinimalSets(c2)
    print("unnamed_card=" + str(unnamed.cardinality()))


if __name__ == "__main__":
    test()
