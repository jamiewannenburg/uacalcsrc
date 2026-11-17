# coding: utf-8
# Dual-runtime parity script for org.uacalc.fplat.PartiallyDefinedLattice.
from __future__ import print_function

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parity_probe import probe as _show, section

import sys

from org.uacalc.fplat import PartiallyDefinedLattice
from org.uacalc.lat import Order
from org.uacalc.terms import VariableImp


def _name(v):
    if v is None:
        return v.getName()
    fn = getattr(v, "getName", None) or getattr(v, "get_name", None)
    if callable(fn):
        return str(fn())
    return str(v)


def _names(lst):
    if lst is None:
        return None
    out = []
    for group in lst:
        if group is None:
            out.append(None)
        else:
            out.append([_name(v) for v in list(group)])
    return out


def _field(obj, java_name, getter=None):
    if getter:
        fn = getattr(obj, getter, None)
        if callable(fn):
            return fn()
    if hasattr(obj, java_name):
        return getattr(obj, java_name)
    try:
        f = obj.getClass().getDeclaredField(java_name)
        f.setAccessible(True)
        return f.get(obj)
    except Exception:
        return None


class NameOrder(Order):
    def leq(self, a, b):
        return _name(a) <= _name(b)


class AntiOrder(Order):
    def leq(self, a, b):
        return _name(a) == _name(b)


def main():
    x = VariableImp("x")
    y = VariableImp("y")
    z = VariableImp("z")
    nat = NameOrder()
    anti = AntiOrder()
    lat = PartiallyDefinedLattice("T", nat, [[x, y]], [[y, z]])
    empty = PartiallyDefinedLattice("empty", nat, [], [])
    _show("leq_xy", lambda: lat.leq(x, y))
    _show("leq_yx", lambda: lat.leq(y, x))
    _show("leq_xx", lambda: lat.leq(x, x))
    _show("leq_anti_xy", lambda: PartiallyDefinedLattice("A", anti, [], []).leq(x, y))
    _show("joins", lambda: _names(_field(lat, "definedJoins", "getDefinedJoins")))
    _show("meets", lambda: _names(_field(lat, "definedMeets", "getDefinedMeets")))
    _show("joins_empty", lambda: _names(_field(empty, "definedJoins", "getDefinedJoins")))
    _show("toString_nonempty", lambda: len(lat.toString()) > 0)
    _show("leq_null_order", lambda: PartiallyDefinedLattice("N", None, [], []).leq(x, y))
    _show("leq_null_left", lambda: lat.leq(None, y))


if __name__ == "__main__":
    main()
