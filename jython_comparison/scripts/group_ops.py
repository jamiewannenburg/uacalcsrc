# coding: utf-8
# Dual-runtime parity script for org.uacalc.group.PermutationGroup.
from __future__ import print_function

import sys

from org.uacalc.group import PermutationGroup
from org.uacalc.util import IntArray


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except:  # noqa: E722 — Jython 2: Java UOE is not always a Python Exception
        e = sys.exc_info()[1]
        name = type(e).__name__
        if "." in name:
            name = name.rsplit(".", 1)[-1]
        # Exception *messages* differ (Java NPE text vs empty Python); types match.
        print(label + "=EXC:" + name)


def _arr(a):
    if a is None:
        return None
    for attr in ("getArray", "toArray", "to_array", "get_array"):
        fn = getattr(a, attr, None)
        if callable(fn):
            try:
                return [int(x) for x in list(fn())]
            except TypeError:
                continue
    try:
        return [int(x) for x in list(a)]
    except TypeError:
        return str(a)


def _ia(vals):
    return IntArray([int(x) for x in list(vals)])


def _sym_name(op):
    s = op.symbol()
    fn = getattr(s, "name", None)
    if callable(fn):
        return str(fn())
    return str(s)


def _close(gens):
    gens = list(gens)
    if not gens:
        return []
    n = len(_arr(gens[0]))
    ident = PermutationGroup.id(n)
    seen = []
    keys = set()

    def add(p):
        k = tuple(_arr(p))
        if k not in keys:
            keys.add(k)
            seen.append(p)
            return True
        return False

    add(ident)
    for g in gens:
        add(g)
        add(PermutationGroup.inv(g))
    changed = True
    while changed:
        changed = False
        current = list(seen)
        for a in current:
            for b in current:
                if add(PermutationGroup.prod(a, b)):
                    changed = True
    return [_arr(x) for x in seen]


def main():
    swap2 = _ia([1, 0])
    cyc3 = _ia([1, 2, 0])
    trans3 = _ia([1, 0, 2])
    _show("id0", lambda: _arr(PermutationGroup.id(0)))
    _show("id1", lambda: _arr(PermutationGroup.id(1)))
    _show("id3", lambda: _arr(PermutationGroup.id(3)))
    _show("id3_toString", lambda: PermutationGroup.id(3).toString())
    _show("prod_s2", lambda: _arr(PermutationGroup.prod(swap2, swap2)))
    _show("inv_s2", lambda: _arr(PermutationGroup.inv(swap2)))
    _show("prod_s3", lambda: _arr(PermutationGroup.prod(trans3, cyc3)))
    _show("inv_cyc3", lambda: _arr(PermutationGroup.inv(cyc3)))
    g = PermutationGroup("S2", [swap2])
    _show("s2_name", lambda: g.getName())
    _show("s2_card", lambda: g.cardinality())
    _show("s2_univ", lambda: g.universe())
    _show("s2_ops", lambda: g.operations())
    _show("s2_inputSize", lambda: g.inputSize())
    g3 = PermutationGroup("S3", [trans3, cyc3], [_ia([0, 1, 2])])
    _show("s3_card_with_univ_list", lambda: g3.cardinality())
    empty = PermutationGroup("Trivial", [])
    _show("empty_card", lambda: empty.cardinality())
    deg1 = PermutationGroup("S1", [_ia([0])])
    _show("s1_card", lambda: deg1.cardinality())
    pop = PermutationGroup.makeProdOp(6)
    _show("makeProdOp_arity", lambda: pop.arity())
    _show("makeProdOp_setSize", lambda: pop.getSetSize())
    _show("makeProdOp_symbol", lambda: _sym_name(pop))
    _show("makeProdOp_tableBased", lambda: pop.isTableBased())
    _show("makeProdOp_value", lambda: _arr(pop.valueAt([trans3, cyc3])))
    iop = PermutationGroup.makeInvOp(6)
    _show("makeInvOp_value", lambda: _arr(iop.valueAt([cyc3])))
    dop = PermutationGroup.makeIdOp(6, 3)
    _show("makeIdOp_value", lambda: _arr(dop.valueAt([])))
    _show("makeIdOp_value_null_args", lambda: _arr(dop.valueAt(None)))
    _show("close_s2", lambda: _close([swap2]))
    _show("close_s3_card", lambda: len(_close([trans3, cyc3])))
    _show("close_c4", lambda: _close([_ia([1, 2, 3, 0])]))
    _show("close_d4_card", lambda: len(_close([_ia([1, 2, 3, 0]), _ia([0, 3, 2, 1])])))
    _show("prod_null", lambda: PermutationGroup.prod(None, swap2))
    _show("id_neg", lambda: PermutationGroup.id(-1))
    _show("s2_isTotal", lambda: g.isTotal())
    _show("s2_con", lambda: g.con())


if __name__ == "__main__":
    main()
