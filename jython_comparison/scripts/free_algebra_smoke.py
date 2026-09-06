# coding: utf-8
# Dual-runtime parity script for FreeAlgebra ctor used by ~/uacalc free_algebras.py.
from __future__ import print_function

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import FreeAlgebra


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    f = FreeAlgebra(c2, 1, True, True)
    # Default names differ (Free(1, C2) vs F(1) over C2); lock rename + card.
    f.setName("F1")
    print("renamed=" + str(f.getName()))
    print("card=" + str(f.cardinality()))
    print("idx_probe=" + str(hasattr(f, "elementIndex")))
    print("getOp_probe=" + str(hasattr(f, "getOperation")))


if __name__ == "__main__":
    test()
