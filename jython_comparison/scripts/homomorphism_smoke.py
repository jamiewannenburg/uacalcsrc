# coding: utf-8
# Dual-runtime parity script for Homomorphism (Java/Jython source of truth).
from __future__ import print_function

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parity_probe import probe as _show, section

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import Homomorphism


def _as_list(obj):
    if obj is None:
        return []
    try:
        return list(obj)
    except TypeError:
        pass
    n = getattr(obj, "length", None)
    if n is not None and not callable(n):
        return [obj[i] for i in range(int(n))]
    return [obj]


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


def _hmap(m):
    items = []
    for k in m:
        items.append(str(int(k)) + ":" + str(int(m[k])))
    items.sort()
    return "{" + ",".join(items) + "}"


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    h = Homomorphism(c2, c2, {0: 0, 1: 1})
    const0 = Homomorphism(c2, c2, {0: 0, 1: 0})
    print("domain=" + str(h.getDomain().getName()))
    print("range_card=" + str(h.getRange().cardinality()))
    print("map=" + _hmap(h.getMap()))
    _show("kernel_id", lambda: str(h.kernel()))
    _show("kernel_const", lambda: str(const0.kernel()))
    _show("toString_prefix", lambda: h.toString().split(" : ")[0])

    def _prod():
        rows = Homomorphism.productHomo([h, const0])
        return "[" + ",".join(_coords(r) for r in _as_list(rows)) + "]"

    _show("productHomo", _prod)
    _show("productHomo_empty", lambda: Homomorphism.productHomo([]))
    _show("productHomo_null", lambda: Homomorphism.productHomo(None))
    _show("ctor_null_domain", lambda: Homomorphism(None, c2, {0: 0, 1: 1}))
    _show("kernel_incomplete", lambda: Homomorphism(c2, c2, {0: 0}).kernel())

    def _after_set_map():
        h.setMap({0: 0, 1: 0})
        return _hmap(h.getMap())

    _show("after_setMap", _after_set_map)

    def _after_set_domain_range():
        h.setDomain(c2)
        h.setRange(c2)
        return str(h.getDomain().cardinality()) + "," + str(h.getRange().getName())

    _show("after_set_domain_range", _after_set_domain_range)


if __name__ == "__main__":
    test()
