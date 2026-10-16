# coding: utf-8
# Dual-runtime parity script for ParameterizedAlgebra.
from __future__ import print_function

import sys

from org.uacalc.alg import ParameterizedAlgebra


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def test():
    p = ParameterizedAlgebra()
    _show("null_names", lambda: p.getParameterMap([1]))
    p.parameterNames = ["n", "m"]
    print("map=" + str(p.getParameterMap([2, 3])))
    print("extra=" + str(p.getParameterMap([2, 3, 9])))
    _show("too_few", lambda: p.getParameterMap([2]))


if __name__ == "__main__":
    test()
