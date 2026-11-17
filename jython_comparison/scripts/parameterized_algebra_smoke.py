# coding: utf-8
# Dual-runtime parity script for ParameterizedAlgebra.
from __future__ import print_function

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parity_probe import probe as _show, section

import sys

from org.uacalc.alg import ParameterizedAlgebra



def _set_parameter_names(p, names):
    if sys.platform.startswith("java"):
        from java.util import ArrayList

        lst = ArrayList()
        for n in names:
            lst.add(n)
        p.parameterNames = lst
    else:
        p.parameterNames = list(names)


def test():
    p = ParameterizedAlgebra()
    _show("null_names", lambda: p.getParameterMap([1]))
    section("set_names", lambda: _set_parameter_names(p, ["n", "m"]))
    _show("map", lambda: p.getParameterMap([2, 3]))
    _show("extra", lambda: p.getParameterMap([2, 3, 9]))
    _show("too_few", lambda: p.getParameterMap([2]))


if __name__ == "__main__":
    test()
