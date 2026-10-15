# coding: utf-8
# Dual-runtime parity script for ProductAlgebra (Java/Jython source of truth).
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import ProductAlgebra
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
    p = ProductAlgebra("C2xC2", [c2, c2])
    print("named=" + str(p.getName()))
    print("card=" + str(p.cardinality()))
    p.setName("P")
    print("renamed=" + str(p.getName()))
    print("type=" + str(p.algebraType()))
    print("nfact=" + str(len(list(p.factors()))))
    print("calcCard=" + str(ProductAlgebra.calcCard([2, 2])))
    _show("getElement0", lambda: list(p.getElement(0)))
    _show("eidx", lambda: p.elementIndex(IntArray([1, 0])))
    _show("eidx_list", lambda: p.elementIndex([1, 0]))
    _show("univList", lambda: [list(row) for row in p.getUniverseList()])
    _show("univOrder", lambda: p.getUniverseOrder())
    _show("factors", lambda: [a.getName() for a in p.factors()])
    _show("parents", lambda: [a.cardinality() for a in p.parents()])
    _show("parent", lambda: p.parent())
    _show("proj", lambda: p.projection(0).getName())
    _show("projK", lambda: p.projectionKernel(0))
    _show("sgClose", lambda: p.sgClose([]))
    _show("op_table", lambda: _tbl(p, plus))
    p.makeOperationTables()
    _show("op_table_after", lambda: _tbl(p, plus))
    _show("convert", lambda: p.convertToDefaultValueOps())
    _show("con_card", lambda: p.con().cardinality())
    _show("sub_card", lambda: p.sub().cardinality())
    _show("Sg", lambda: p.Sg([IntArray([0, 0])]).cardinality())

    p2 = ProductAlgebra([c2, c2])
    print("list_card=" + str(p2.cardinality()))


if __name__ == "__main__":
    test()
