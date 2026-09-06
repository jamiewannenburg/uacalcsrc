# coding: utf-8
# Dual-runtime parity script for IntArray (~/uacalc free_algebras.py get/set/clone).
from __future__ import print_function

from org.uacalc.util import IntArray


def test():
    a = IntArray(3)
    a.set(0, 7)
    a.set(1, 8)
    a.set(2, 9)
    print("get0=" + str(a.get(0)))
    print("get1=" + str(a.get(1)))
    print("size=" + str(a.universeSize()))

    b = a.clone()
    a.set(0, 1)
    print("orig0=" + str(a.get(0)))
    print("clone0=" + str(b.get(0)))

    c = IntArray([4, 5])
    print("list0=" + str(c.get(0)))
    print("list1=" + str(c.get(1)))
    print("list_size=" + str(c.universeSize()))
    print("has_getArray=" + str(hasattr(c, "getArray")))


if __name__ == "__main__":
    test()
