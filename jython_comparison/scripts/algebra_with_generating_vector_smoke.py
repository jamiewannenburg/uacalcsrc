# coding: utf-8
# Dual-runtime parity script for AlgebraWithGeneratingVector.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import AlgebraWithGeneratingVector
from org.uacalc.eq import Equation
from org.uacalc.terms import Variable


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    v = AlgebraWithGeneratingVector(c2, [0, 1])
    print("alg=" + str(v.getAlgebra().getName()))
    print("card=" + str(v.getAlgebra().cardinality()))
    print("vec=" + str(list(v.getVector())))
    print("toString=" + str(v.toString()))
    v2 = AlgebraWithGeneratingVector(c2, [0, 1])
    print("isImage=" + str(v.isImageOf(v2)))
    print("compare=" + str(v.compareTo(v2)))
    print("equals=" + str(v.equals(v2)))
    parts = AlgebraWithGeneratingVector.siDecompose(c2, [1])
    print("si_n=" + str(len(list(parts))))
    empty_rels = AlgebraWithGeneratingVector.siDecompose(c2, [1], [])
    print("si_empty_rels=" + str(len(list(empty_rels))))
    id_rel = AlgebraWithGeneratingVector.siDecompose(
        c2, [0, 1], [Equation(Variable.x, Variable.x)]
    )
    print("si_id_rel=" + str(len(list(id_rel))))
    xy = AlgebraWithGeneratingVector.siDecompose(
        c2, [0, 1], [Equation(Variable.x, Variable.y)]
    )
    print("si_xy_n=" + str(len(list(xy))))


if __name__ == "__main__":
    test()
