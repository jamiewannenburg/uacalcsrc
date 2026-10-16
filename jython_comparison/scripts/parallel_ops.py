# coding: utf-8
# Dual-runtime parity script for org.uacalc.alg.parallel.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import Closer, BigProductAlgebra
from org.uacalc.alg.parallel import Pool, SingleClose
from org.uacalc.util import IntArray


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except:  # noqa: E722 — Jython 2: Java exceptions
        e = sys.exc_info()[1]
        name = type(e).__name__
        if "." in name:
            name = name.rsplit(".", 1)[-1]
        print(label + "=EXC:" + name)


def _coords(elem):
    if elem is None:
        return None
    try:
        return [int(x) for x in list(elem)]
    except TypeError:
        pass
    for attr in ("getArray", "get_array", "toArray", "to_array"):
        fn = getattr(elem, attr, None)
        if callable(fn):
            return [int(x) for x in fn()]
    return str(elem)


def _sorted_ias(lst):
    if lst is None:
        return None
    return sorted([_coords(x) for x in list(lst)])


def _quiet(closer):
    fn = getattr(closer, "setSuppressOutput", None) or getattr(
        closer, "set_suppress_output", None
    )
    if callable(fn):
        fn(True)
    return closer


def _seq_close(alg, gens):
    old = getattr(Closer, "doParallel", False)
    try:
        Closer.doParallel = False
        return _sorted_ias(_quiet(Closer(alg, gens)).sgClose())
    finally:
        Closer.doParallel = old


def main():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    bp2 = BigProductAlgebra(c2, 2)
    g00 = IntArray([0, 0])
    g11 = IntArray([1, 1])
    _show("pool_name", lambda: Pool.__name__)
    _show("pool_ctor", lambda: Pool().__class__.__name__)
    _show("single_close_name", lambda: SingleClose.__name__)
    _show("seq_c2_diag", lambda: _seq_close(bp2, [g00, g11]))
    # SingleClose.doOneStep on IntOperation is UOE in Java; CPython's
    # value_at_arrays path differs. Covered as a strict xfail golden.


if __name__ == "__main__":
    main()
