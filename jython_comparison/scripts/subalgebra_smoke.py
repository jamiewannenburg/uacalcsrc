# coding: utf-8
# Dual-runtime parity script for Subalgebra (Java/Jython source of truth).
#
# Known CPython / uacalc_lib gaps (do not hide; backend should match Java):
# - Java constructors: Subalgebra(alg, int[]), (alg, IntArray),
#   (name, alg, int[]), (name, alg, IntArray). BasicSet extends IntArray, so
#   Subalgebra(alg, BasicSet) is the IntArray overload (used by
#   SubalgebraLattice.Sg / iterator).
# - superAlgebra() returns the SmallAlgebra; the binding only exposes
#   super_algebra_name() (a string).
# - index(k) is Java Arrays.binarySearch (negative insertion-point encoding
#   when missing). Binding returns -1 when missing. This script locks
#   found indices exactly and missing as "negative".
# - getSubuniverseArray / getElement / elementIndex exist as snake_case on
#   the binding; Java names are the camelCase forms below.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import Subalgebra
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.alg.sublat import SubalgebraLattice
from org.uacalc.util import IntArray


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


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


def _norm_set(s):
    text = str(s).replace(" ", "")
    return text.replace("[", "{").replace("]", "}")


def _ints(arr):
    return "[" + ",".join(str(int(x)) for x in _as_list(arr)) + "]"


def _nops(alg):
    return str(len(_as_list(alg.operations())))


def _op_table(alg, sym):
    op = alg.getOperation(sym)
    if op is None:
        return "None"
    n = int(alg.cardinality())
    cells = []
    for i in range(n):
        for j in range(n):
            cells.append(str(int(op.intValueAt([i, j]))))
    return ",".join(cells)


def _super_info(alg):
    sup = alg.superAlgebra()
    return str(sup.getName()) + ":" + str(sup.cardinality())


def _index_found(sub, k):
    return str(int(sub.index(k)))


def _index_missing(sub, k):
    return str(int(sub.index(k)) < 0)


def _pick_singleton(sl):
    chosen = None
    for univ in sl.iterator():
        if _norm_set(univ) == "{0}":
            chosen = univ
            break
    if chosen is None:
        raise RuntimeError("cyclic2 SubalgebraLattice missing {0}")
    return chosen


def _dump_sub(label, s, plus_sym, expect_indices, missing_indices):
    print(label + "_renamed=" + str(s.getName()))
    print(label + "_card=" + str(s.cardinality()))
    _show(label + "_subuniv", lambda: _ints(s.getSubuniverseArray()))
    _show(label + "_nops", lambda: _nops(s))
    _show(label + "_op_table", lambda: _op_table(s, plus_sym))
    _show(label + "_super", lambda: _super_info(s))
    # Java Subalgebra.getUniverseList() returns null.
    _show(label + "_univList", lambda: s.getUniverseList())
    _show(label + "_algType", lambda: str(s.algebraType()))
    for k in expect_indices:
        _show(label + "_index_" + str(k), lambda k=k: _index_found(s, k))
    for k in missing_indices:
        _show(label + "_missing_" + str(k), lambda k=k: _index_missing(s, k))

    def _elems():
        n = int(s.cardinality())
        return "[" + ",".join(str(s.getElement(i)) for i in range(n)) + "]"

    _show(label + "_getElement", _elems)

    def _eidx():
        n = int(s.cardinality())
        return "[" + ",".join(str(s.elementIndex(s.getElement(i))) for i in range(n)) + "]"

    _show(label + "_elementIndex", _eidx)


def test():
    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    plus_sym = OperationSymbol("+", 2)
    sl = SubalgebraLattice(alg)
    chosen = _pick_singleton(sl)

    # Java: Subalgebra(alg, IntArray); BasicSet extends IntArray.
    s = Subalgebra(alg, chosen)
    s.setName("S0")
    _dump_sub("S0", s, plus_sym, [0], [1])

    # Java: Subalgebra(name, alg, int[]).
    full = Subalgebra("Full", alg, [0, 1])
    _dump_sub("Full", full, plus_sym, [0, 1], [])

    # Java: Subalgebra(alg, IntArray) from an explicit IntArray.
    ia = IntArray([0])
    s_ia = Subalgebra(alg, ia)
    s_ia.setName("Sia")
    _dump_sub("Sia", s_ia, plus_sym, [0], [1])

    _show("S0_con_card", lambda: s.con().cardinality())
    _show("S0_sub_card", lambda: s.sub().cardinality())


if __name__ == "__main__":
    test()
