# coding: utf-8
# Dual-runtime parity script for GeneralAlgebra.
from __future__ import print_function

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parity_probe import probe as _show, section

import sys

from org.uacalc.alg import GeneralAlgebra
from org.uacalc.alg.op import Operations, OperationSymbol



def test():
    try:
        from java.util import HashSet
        univ = HashSet()
        univ.add(0)
        univ.add(1)
    except ImportError:
        univ = [0, 1]
    id1 = Operations.makeIntOperation(OperationSymbol("id", 1), 2, [0, 1])
    g = GeneralAlgebra("G", univ, [id1])
    print("named=" + str(g.getName()))
    print("card=" + str(g.cardinality()))
    g.setName("Gen")
    print("renamed=" + str(g.getName()))
    print("nops=" + str(len(list(g.operations()))))
    print("parent=" + str(g.parent()))
    print("parents=" + str(g.parents()))
    _show("getOp", lambda: g.getOperation(OperationSymbol("id", 1)) is not None)
    _show("con", lambda: g.con())
    _show("sub", lambda: g.sub())
    g2 = GeneralAlgebra("U", univ)
    ops = g2.operations()
    print("noops=" + str(0 if ops is None else len(list(ops))))
    try:
        from java.util import HashSet
        empty = HashSet()
    except ImportError:
        empty = []
    g0 = GeneralAlgebra("E", empty)
    print("empty_card=" + str(g0.cardinality()))
    eops = g0.operations()
    print("empty_ops=" + str(0 if eops is None else len(list(eops))))


if __name__ == "__main__":
    test()
