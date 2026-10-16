# coding: utf-8
# Dual-runtime parity script for GeneralAlgebra.
from __future__ import print_function

import sys

from org.uacalc.alg import GeneralAlgebra
from org.uacalc.alg.op import Operations, OperationSymbol


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


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


if __name__ == "__main__":
    test()
