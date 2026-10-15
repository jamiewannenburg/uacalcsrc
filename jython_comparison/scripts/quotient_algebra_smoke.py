# coding: utf-8
# Dual-runtime parity script for QuotientAlgebra / QuotientElement.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import QuotientAlgebra
from org.uacalc.alg.op import OperationSymbol


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
    cong = c2.con().Cg(0, 1)
    zero = c2.con().zero()
    q = QuotientAlgebra("Q", c2, cong)
    print("named=" + str(q.getName()))
    print("card=" + str(q.cardinality()))
    q.setName("Quot")
    print("renamed=" + str(q.getName()))
    print("type=" + str(q.algebraType()))
    print("super=" + str(q.superAlgebra().getName()))
    print("cong=" + str(q.getCongruence()))
    _show("univList", lambda: q.getUniverseList())
    _show("univOrder", lambda: q.getUniverseOrder())
    qe = q.getElement(0)
    print("qe=" + str(qe))
    print("qe_toString=" + str(qe.toString()))
    print("qe_index=" + str(qe.getIndex()))
    print("qe_super_index=" + str(qe.getIndexInSuperAlgebra()))
    print("qe_alg=" + str(qe.getAlgebra().getName()))
    print("qe_super=" + str(qe.superAlgebra().getName()))
    print("qe_cong=" + str(qe.getCongruence()))
    _show("eidx0", lambda: q.elementIndex(0))
    _show("repIdx", lambda: q.representativeIndex(0))
    _show("canon", lambda: q.canonicalHomomorphism(1))
    _show("convert", lambda: q.convertToDefaultValueOps())
    _show("con_card", lambda: q.con().cardinality())
    _show("sub_card", lambda: q.sub().cardinality())

    qz = QuotientAlgebra(c2, zero)
    print("unnamed=" + str(qz.getName()))
    print("zero_card=" + str(qz.cardinality()))
    print("universe=" + str(list(qz.universe())))
    print("op_table=" + _tbl(qz, plus))
    qz.makeOperationTables()
    print("op_table_after=" + _tbl(qz, plus))


if __name__ == "__main__":
    test()
