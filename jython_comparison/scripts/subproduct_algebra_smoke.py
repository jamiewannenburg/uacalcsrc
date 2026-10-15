# coding: utf-8
# Dual-runtime parity script for SubProductAlgebra.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import BigProductAlgebra, SubProductAlgebra
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.util import IntArray


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def _arr(obj):
    if obj is None:
        return None
    fn = getattr(obj, "getArray", None) or getattr(obj, "to_array", None)
    if callable(fn):
        return list(fn())
    return list(obj)


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
    bp = BigProductAlgebra(c2, 2)
    sp = SubProductAlgebra("SP", bp, [IntArray([0, 0]), IntArray([1, 1])])
    print("named=" + str(sp.getName()))
    print("card=" + str(sp.cardinality()))
    sp.setName("Diag")
    print("renamed=" + str(sp.getName()))
    print("type=" + str(sp.algebraType()))
    _show("gens", lambda: [_arr(g) for g in sp.generators()])
    _show("univList", lambda: [_arr(row) for row in sp.getUniverseList()])
    _show("univOrder", lambda: sp.getUniverseOrder())
    _show("getElement0", lambda: _arr(sp.getElement(0)))
    _show("eidx", lambda: sp.elementIndex(IntArray([1, 1])))
    _show("prod_n", lambda: sp.getProductAlgebra().getNumberOfFactors())
    _show("super_n", lambda: sp.superAlgebra().getNumberOfFactors())
    _show("terms", lambda: sp.getTerms())
    _show("op_table", lambda: _tbl(sp, plus))
    sp.makeOperationTables()
    _show("op_table_after", lambda: _tbl(sp, plus))
    _show("convert", lambda: sp.convertToDefaultValueOps())
    _show("con_card", lambda: sp.con().cardinality())
    _show("sub_card", lambda: sp.sub().cardinality())


if __name__ == "__main__":
    test()
