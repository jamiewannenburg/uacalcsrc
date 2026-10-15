# coding: utf-8
# Dual-runtime parity script for Closer (Java/Jython source of truth).
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import Closer, BigProductAlgebra
from org.uacalc.util import IntArray


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def _coords(elem):
    if elem is None:
        return "None"
    try:
        return "[" + ",".join(str(int(x)) for x in list(elem)) + "]"
    except TypeError:
        pass
    for attr in ("getArray", "get_array", "toArray", "to_array"):
        fn = getattr(elem, attr, None)
        if callable(fn):
            return "[" + ",".join(str(int(x)) for x in fn()) + "]"
    return str(elem).replace(" ", "")


def _ias(lst):
    if lst is None:
        return "None"
    return "[" + ",".join(_coords(x) for x in list(lst)) + "]"


def _tm(m):
    if m is None:
        return "None"
    items = []
    for k in m:
        items.append(_coords(k) + ":" + str(m[k]).replace(" ", ""))
    items.sort()
    return "{" + ",".join(items) + "}"


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    bp = BigProductAlgebra(c2, 2)
    g00 = IntArray([0, 0])
    g11 = IntArray([1, 1])
    closer = Closer(bp, [g00, g11])
    closer_tm = Closer(bp, [g00, g11], True)
    print("answer_before=" + str(closer.getAnswer()))
    print("gens=" + _ias(closer.getGenerators()))
    print("maxSize=" + str(closer.getmaxSize()))
    print("termMap_none=" + _tm(closer.getTermMap()))
    print("termMap_made=" + _tm(closer_tm.getTermMap()))
    _show("sgClose", lambda: _ias(closer.sgClose()))
    print("answer_after=" + _ias(closer.getAnswer()))
    closer2 = Closer(bp, [g00, g11])
    _show("close_power", lambda: _ias(closer2.close()))
    bp_prod = BigProductAlgebra([c2, c2])
    cl_mixed = Closer(bp_prod, [g00])
    _show("close_not_power", lambda: cl_mixed.close())
    _show("setImage_ok", lambda: closer.setImageAlgebra(c2) or closer.getImageAlgebra().cardinality())
    _show("setHomo_gens", lambda: closer.setHomomorphism([0, 1]))
    _show("setHomo_wrong", lambda: closer.setHomomorphism([0]))
    closer.setMaxSize(3)
    print("maxSize_set=" + str(closer.getmaxSize()))
    print("suppress=" + str(closer.isSuppressOutput()))
    closer.setSuppressOutput(True)
    print("suppress_set=" + str(closer.isSuppressOutput()))
    _show("ctor_null", lambda: Closer(None, [g00]))


if __name__ == "__main__":
    test()
