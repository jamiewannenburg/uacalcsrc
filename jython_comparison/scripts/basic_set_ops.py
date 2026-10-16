# coding: utf-8
# Dual-runtime parity script for BasicSet.
from __future__ import print_function

from org.uacalc.alg.sublat import BasicSet


def _show(label, val):
    print(label + "=" + str(val))


def test():
    empty = BasicSet.EMPTY_SET
    a = BasicSet([2, 0, 1])
    b = BasicSet([1, 2, 3])
    _show("empty", empty)
    _show("a", a)
    _show("size", a.universeSize())
    _show("get0", a.get(0))
    _show("contains1", a.contains(1))
    _show("contains9", a.contains(9))
    _show("leq", a.leq(BasicSet([0, 1, 2, 3])))
    _show("inter", a.intersection(b))
    _show("union_bug", BasicSet([0, 2]).union(BasicSet([1, 3])))
    _show("diff", a.setDifference(BasicSet([1])))
    _show("cmp", a.compareTo(b))
    _show("toString", a.toString() if hasattr(a, "toString") else str(a))


if __name__ == "__main__":
    test()
