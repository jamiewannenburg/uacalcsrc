# coding: utf-8
# Dual-runtime parity script for org.uacalc.element.
from __future__ import print_function

import sys

from org.uacalc.element import Element, SubProductElement
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import FreeAlgebra, SubProductAlgebra, BigProductAlgebra
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
    for attr in ("getArray", "get_array", "toArray", "to_array"):
        fn = getattr(elem, attr, None)
        if callable(fn):
            try:
                return "[" + ",".join(str(int(x)) for x in fn()) + "]"
            except TypeError:
                continue
    try:
        return "[" + ",".join(str(int(x)) for x in list(elem)) + "]"
    except TypeError:
        return str(elem)


def _names(lst):
    if lst is None:
        return "None"
    out = []
    for v in list(lst):
        getter = getattr(v, "getName", None)
        out.append(getter() if getter is not None else str(v))
    return ",".join(out)


def _varmap(m):
    if m is None:
        return "None"
    items = m.entrySet() if hasattr(m, "entrySet") else m.items()
    parts = []
    for item in items:
        if hasattr(item, "getKey"):
            k, v = item.getKey(), item.getValue()
        else:
            k, v = item
        getter = getattr(k, "getName", None)
        name = getter() if getter is not None else str(k)
        parts.append(name + "->" + _coords(v))
    parts.sort()
    return "{" + ",".join(parts) + "}"


def _dump(label, e):
    _show(label + "_toString", lambda: e.toString() if hasattr(e, "toString") else str(e))
    _show(label + "_index", lambda: e.index())
    _show(label + "_term", lambda: e.getTerm())
    _show(label + "_vars", lambda: _names(e.getVariableList()))
    _show(label + "_varmap", lambda: _varmap(e.getVariableMap()))
    _show(label + "_alg", lambda: e.getAlgebra().getName())
    _show(label + "_parent", lambda: e.getParent())
    _show(label + "_parentArr", lambda: e.getParentArray())
    _show(label + "_parentIdx", lambda: e.parentIndexArray())
    _show(label + "_eq_self", lambda: e == e)
    e2 = SubProductElement(e.getAlgebra().getElement(e.index()), e.getAlgebra())
    _show(label + "_eq_copy", lambda: e == e2)
    _show(label + "_hash_stable", lambda: hash(e) == hash(e))


def test():
    print("HAS_ELEMENT=" + str(Element is not None))
    print("HAS_SUB=" + str(SubProductElement is not None))
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
    lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")

    f1 = FreeAlgebra(c2, 1)
    f1.setName("F1")
    _dump("f1_0", SubProductElement(f1.getElement(0), f1))
    _dump("f1_1", SubProductElement(f1.getElement(1), f1))

    f2 = FreeAlgebra(c2, 2)
    f2.setName("F2")
    n = int(f2.cardinality())
    _dump("f2_0", SubProductElement(f2.getElement(0), f2))
    _dump("f2_last", SubProductElement(f2.getElement(n - 1), f2))

    f3 = FreeAlgebra(c3, 2)
    f3.setName("F3")
    _dump("f3_0", SubProductElement(f3.getElement(0), f3))

    flat = FreeAlgebra(lat2, 2)
    flat.setName("Flat")
    _dump("flat_0", SubProductElement(flat.getElement(0), flat))

    bp2 = BigProductAlgebra(c2, 2)
    sp = SubProductAlgebra("SP", bp2, [IntArray([0, 0]), IntArray([1, 1])], True)
    _dump("sp_0", SubProductElement(sp.getElement(0), sp))
    _dump("sp_1", SubProductElement(sp.getElement(1), sp))

    spn = SubProductAlgebra("SPn", bp2, [IntArray([0, 0]), IntArray([1, 1])], False)
    e_n = SubProductElement(spn.getElement(0), spn)
    _show("spn_term", lambda: e_n.getTerm())
    _show("spn_toString", lambda: e_n.toString() if hasattr(e_n, "toString") else str(e_n))
    _show("spn_index", lambda: e_n.index())
    _show("spn_vars", lambda: e_n.getVariableList())

    bp3 = BigProductAlgebra(c2, 3)
    sp3 = SubProductAlgebra(
        "SP3",
        bp3,
        [IntArray([0, 0, 0]), IntArray([1, 1, 1]), IntArray([0, 1, 0])],
        True,
    )
    _dump("sp3_0", SubProductElement(sp3.getElement(0), sp3))

    bpm = BigProductAlgebra([c2, c3], [1, 1])
    spm = SubProductAlgebra("SPmix", bpm, [IntArray([0, 0]), IntArray([1, 1])], True)
    _dump("spm_0", SubProductElement(spm.getElement(0), spm))


if __name__ == "__main__":
    test()
