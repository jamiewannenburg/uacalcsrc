# coding: utf-8
# Dual-runtime parity script for PowerAlgebra (Java/Jython source of truth).
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import PowerAlgebra
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.util import IntArray


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def _tbl(alg, sym):
    op = alg.getOperation(sym)
    n = int(alg.cardinality())
    cells = []
    for i in range(n):
        for j in range(n):
            cells.append(str(int(op.intValueAt([i, j]))))
    return ",".join(cells)


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    plus = OperationSymbol("+", 2)
    p = PowerAlgebra("C2^2", c2, 2)
    print("named=" + str(p.getName()))
    print("card=" + str(p.cardinality()))
    p.setName("Pow")
    print("renamed=" + str(p.getName()))
    print("type=" + str(p.algebraType()))
    print("power=" + str(p.getPower()))
    print("root=" + str(p.getRoot().getName()))
    print("parent=" + str(p.parent().getName()))
    print("parents=" + str([a.getName() for a in p.parents()]))
    print("nfact=" + str(p.getPower()))
    _show("getElement1", lambda: list(p.getElement(1)))
    _show("eidx", lambda: p.elementIndex(IntArray([0, 1])))
    _show("univList", lambda: [list(row) for row in p.getUniverseList()])
    _show("factors", lambda: [a.getName() for a in p.factors()])
    _show("proj", lambda: p.projection(0).getName())
    _show("op_table", lambda: _tbl(p, plus))
    p.makeOperationTables()
    _show("op_table_after", lambda: _tbl(p, plus))
    _show("convert", lambda: p.convertToDefaultValueOps())
    _show("con_card", lambda: p.con().cardinality())
    _show("sub_card", lambda: p.sub().cardinality())

    p2 = PowerAlgebra(c2, 2)
    print("unnamed=" + str(p2.getName()))
    print("unnamed_card=" + str(p2.cardinality()))


if __name__ == "__main__":
    test()
