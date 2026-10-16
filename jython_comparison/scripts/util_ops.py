# coding: utf-8
# Dual-runtime parity script for org.uacalc.util and util.virtuallist.
from __future__ import print_function

import sys

from org.uacalc.util import (
    IntArray,
    Horner,
    SequenceGenerator,
    PermutationGenerator,
    ArrayString,
    SimpleList,
)
from org.uacalc.util.virtuallist import LongList, VirtualLists, TupleWithMin

if sys.platform.startswith("java"):
    from jarray import array as _jarray

    def _ia(vals):
        return _jarray([int(x) for x in vals], "i")

    def _snap(a):
        return [int(a[i]) for i in range(len(a))]
else:
    def _ia(vals):
        return [int(x) for x in vals]

    def _snap(a):
        return [int(x) for x in list(a)]


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def _tolist(a):
    if a is None:
        return None
    try:
        return [int(a[i]) for i in range(len(a))]
    except Exception:
        try:
            return [int(x) for x in a]
        except Exception:
            return a


def _collect(factory, start, *args):
    a = _ia(list(start))
    inc = factory(a, *args)
    out = [_snap(a)]
    n = 0
    while inc.increment():
        out.append(_snap(a))
        n += 1
        if n > 2000:
            break
    return out


def test():
    a = IntArray(3)
    a.set(0, 7)
    a.set(1, 8)
    a.set(2, 9)
    _show("ia_get0", lambda: a.get(0))
    _show("ia_size", lambda: a.universeSize())
    _show("ia_arr", lambda: _tolist(a.getArray()))
    _show("ia_toarr", lambda: _tolist(a.toArray()) if hasattr(a, "toArray") else _tolist(a.getArray()))
    b = a.clone()
    a.set(0, 1)
    _show("ia_clone0", lambda: b.get(0))
    _show("ia_toString", lambda: a.toString())
    _show("ia_hash", lambda: a.hashCode())
    _show("ia_eq", lambda: IntArray([1, 2]).equals(IntArray([1, 2])))
    _show("ia_const", lambda: IntArray([2, 2]).isConstant())
    _show("ia_idemp", lambda: IntArray([0, 1]).isIdempotent())
    _show("ia_static", lambda: IntArray.intArrayToString([1, 2]))
    _show("ia_parse", lambda: _tolist(IntArray.stringToArray("1, 2")))
    _show("ia_eqarr", lambda: IntArray.equalIntArrays([1], [1]))

    _show("horner", lambda: Horner.horner([1, 2], [3, 4]))
    _show("hornerInv", lambda: _tolist(Horner.hornerInv(9, [3, 4])))
    _show("reverseArray", lambda: _tolist(Horner.reverseArray([1, 2, 3])))
    _show("leftRightReverse", lambda: _tolist(Horner.leftRightReverse(list(range(8)), 2, 3)))

    _show("seq", lambda: _collect(SequenceGenerator.sequenceIncrementor, [0, 0], 1))
    _show("seq_left", lambda: _collect(SequenceGenerator.leftSequenceIncrementor, [0, 0], 1))
    _show("seq_nondec", lambda: _collect(SequenceGenerator.nondecreasingSequenceIncrementor, [0, 0], 2))
    _show("seq_inc", lambda: _collect(SequenceGenerator.increasingSequenceIncrementor, [0, 1], 3))
    _show("init_part", lambda: _tolist(SequenceGenerator.initialPartition(4, 2)))
    _show(
        "part",
        lambda: _collect(
            SequenceGenerator.partitionArrayIncrementor,
            SequenceGenerator.initialPartition(4, 2),
            2,
        ),
    )

    g = PermutationGenerator(3)
    _show("nextIndex", lambda: g.nextIndex())
    _show("perm_arr", lambda: _collect(PermutationGenerator.arrayIncrementor, [0, 1]))
    _show("perm_list", lambda: _collect(PermutationGenerator.listIncrementor, [0, 1]))
    it = PermutationGenerator.iterator(2)
    perms = []
    while it.hasNext():
        perms.append(_tolist(it.next()))
    _show("perm_iter", lambda: perms)
    g.reset()
    _show("reset_idx", lambda: g.nextIndex())

    _show("as_toString", lambda: ArrayString.toString([1, [2, 3]]))

    sl = SimpleList.makeList().cons(3).cons(2).cons(1)
    _show("sl_empty", lambda: SimpleList.makeList().isEmpty())
    _show("sl_first", lambda: sl.first())
    _show("sl_rest0", lambda: sl.rest().first())
    _show("sl_size", lambda: sl.size())
    _show("sl_contains", lambda: sl.contains(2))
    _show("sl_indexOf", lambda: sl.indexOf(3))
    _show("sl_toString", lambda: sl.toString())
    _show("sl_append", lambda: sl.append(SimpleList.makeList(4)).size())
    _show("sl_reverse", lambda: sl.reverse().first())
    _show("sl_copy", lambda: sl.copyList().first())

    _show("ll_tuples", lambda: [LongList.intTuples(2, 2).size(), _tolist(LongList.intTuples(2, 2).get(0))])
    _show("ll_min", lambda: LongList.intTuplesWithMin(2, 3, 1).size())
    _show("ll_fix", lambda: LongList.fixedSizedSubsets(2, 4).size())
    _show("ll_sub", lambda: LongList.subsets(3).size())
    _show("ll_perm", lambda: LongList.permutations(3).size())
    _show("ll_fac", lambda: LongList.factorial(5))
    _show("ll_bin", lambda: LongList.binomial(6, 2))
    _show("ll_log", lambda: LongList.log2(16))
    _show("ll_pow", lambda: LongList.pow2(4))
    _show("vl_tuples", lambda: VirtualLists.intTuples(2, 2).size())
    _show("vl_min", lambda: VirtualLists.intTuplesWithMin(2, 3, 1).size())
    _show("vl_idx", lambda: _tolist(VirtualLists.arrayIndexerWithMin(0, 3, 4, 2)))
    tw = TupleWithMin(3, 4, 2)
    _show("twm_size", lambda: tw.size())
    _show("twm_get0", lambda: _tolist(tw.get(0)))


if __name__ == "__main__":
    test()
