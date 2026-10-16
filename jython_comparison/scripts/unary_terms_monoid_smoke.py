# coding: utf-8
# Dual-runtime parity script for UnaryTermsMonoid.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import UnaryTermsMonoid


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    u = UnaryTermsMonoid(c2)
    print("named=" + str(u.getName()))
    print("card=" + str(u.cardinality()))
    u.setName("U")
    print("renamed=" + str(u.getName()))
    print("type=" + str(u.algebraType()))
    print("unary=" + str(u.isUnary()))
    print("nops=" + str(len(list(u.operations()))))
    print("parent=" + str(u.parent().getName()))
    print("getElement0=" + str(u.getElement(0)))
    print("eidx=" + str(u.elementIndex(0)))
    print("con=" + str(u.con()))
    print("sub=" + str(u.sub()))
    _show("convert", lambda: u.convertToDefaultValueOps())


if __name__ == "__main__":
    test()
