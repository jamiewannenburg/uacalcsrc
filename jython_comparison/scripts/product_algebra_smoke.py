# coding: utf-8
# Dual-runtime parity script for ProductAlgebra (~/uacalc jep_check / sc_joins).
from __future__ import print_function

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import ProductAlgebra


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    p = ProductAlgebra("C2xC2", [c2, c2])
    print("named=" + str(p.getName()))
    print("card=" + str(p.cardinality()))
    p.setName("P")
    print("renamed=" + str(p.getName()))
    print("has_getOperation=" + str(hasattr(p, "getOperation")))

    p2 = ProductAlgebra([c2, c2])
    print("list_card=" + str(p2.cardinality()))


if __name__ == "__main__":
    test()
