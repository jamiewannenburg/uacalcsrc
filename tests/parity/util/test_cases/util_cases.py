"""Test case specifications for org.uacalc.util behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
import sys
from org.uacalc.util import (
    IntArray, Horner, SequenceGenerator, PermutationGenerator,
    ArrayString, SimpleList, ArrayIncrementor,
)
from org.uacalc.util.virtuallist import LongList, VirtualLists, TupleWithMin

if sys.platform.startswith('java'):
    from jarray import array as _jarray
    def _ia(vals):
        return _jarray([int(x) for x in vals], 'i')
    def _snap(a):
        return [int(a[i]) for i in range(len(a))]
else:
    def _ia(vals):
        return [int(x) for x in vals]
    def _snap(a):
        return [int(x) for x in list(a)]

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

def _jlist(vals):
    if sys.platform.startswith('java'):
        from java.util import ArrayList
        lst = ArrayList()
        for v in vals:
            lst.add(v)
        return lst
    return list(vals)

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

def _collect_list(factory, start, *args):
    a = _jlist(list(start))
    inc = factory(a, *args)
    out = [_snap(a)]
    n = 0
    while inc.increment():
        out.append(_snap(a))
        n += 1
        if n > 2000:
            break
    return out

def _as_arr(vals):
    if sys.platform.startswith('java'):
        from jarray import array
        from java.lang import Object
        if vals and isinstance(vals[0], (list, tuple)):
            return array([_as_arr(v) for v in vals], Object)
        return array([int(x) for x in vals], 'i')
    return vals

def _array_string(obj):
    if sys.platform.startswith('java'):
        from java.lang import Object, Class
        cls = Class.forName('org.uacalc.util.ArrayString')
        m = cls.getMethod('toString', [Object])
        return m.invoke(None, [obj])
    return ArrayString.toString(obj)

def _ia_vals(ia):
    n = ia.universeSize()
    if n < 0:
        return None
    return [int(ia.get(i)) for i in range(n)]

def _ll_all(ll):
    out = []
    sz = int(ll.size())
    for k in range(sz):
        out.append(_tolist(ll.get(k)))
    return out

def _iter_perms(n):
    it = PermutationGenerator.iterator(n)
    out = []
    while it.hasNext():
        out.append(_tolist(it.next()))
    return out

def _sl_vals(sl):
    out = []
    cur = sl
    while True:
        empty = cur.isEmpty() if hasattr(cur, 'isEmpty') else cur.is_empty()
        if empty:
            break
        out.append(cur.first())
        cur = cur.rest()
    return out
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java array/List toString vs Python list.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")

_GETARRAY_XFAIL = (
    "Java IntArray.getArray returns the live backing int[]; uacalc_lib "
    "returns a copy. Owner: keep IntArray copy-on-write. "
    "Do not change Java expected values."
)
_SETINT_XFAIL = (
    "Java IntArray.setIntArray replaces the backing array (may change size); "
    "uacalc_lib cannot replace the store. Owner: copy-on-write IntArray. "
    "Do not change Java expected values."
)
_STREAM_XFAIL = (
    "Java 8 LongList.stream / parallelStream are not bound. "
    "Owner: Stream API out of scope for the org shim."
)
_SERIAL_XFAIL = (
    "SimpleList custom writeObject/readObject sharing graph is not bound. "
    "Owner: serialization roadmap; core list ops are covered."
)

TEST_CASES = [
    # ----- IntArray constructors / get / set / clone -----
    TestCaseSpec(
        id="ia_size3_zeros",
        method="IntArray.universeSize",
        setup=_SETUP,
        call="_ia_vals(IntArray(3))",
        description="IntArray(3) is [0,0,0]",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_size0",
        method="IntArray.universeSize",
        setup=_SETUP,
        call="[IntArray(0).universeSize(), _ia_vals(IntArray(0))]",
        description="IntArray(0) is empty with size 0",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_size1",
        method="IntArray.get",
        setup=_SETUP,
        call="_ia_vals(IntArray(1))",
        description="IntArray(1) is [0]",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_from_list",
        method="IntArray.get",
        setup=_SETUP,
        call="_ia_vals(IntArray([4, 5, 6]))",
        description="IntArray([4,5,6]) stores those values",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_empty_list",
        method="IntArray.universeSize",
        setup=_SETUP,
        call="IntArray([]).universeSize()",
        description="IntArray([]) has size 0",
    ),
    TestCaseSpec(
        id="ia_null_ctor_size",
        method="IntArray.universeSize",
        setup=_SETUP,
        call="IntArray().universeSize()",
        description="IntArray() sentinel has size -1",
    ),
    TestCaseSpec(
        id="ia_null_ctor_get_npe",
        method="IntArray.get",
        setup=_SETUP,
        call="IntArray().get(0)",
        description="IntArray() get NPEs",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="ia_get_set_clone",
        method="IntArray.clone",
        setup=_SETUP,
        call=(
            "(lambda a: (a.set(0,7), a.set(1,8), a.set(2,9), "
            "setattr(__import__('sys').modules[__name__] if False else a, '_c', a.clone()), "
            "None)[-1] or [a.get(0), a.clone().get(0) if False else None])"
        ),
        description="placeholder replaced below",
    ),
]

# Replace the awkward clone case with a clearer setup-based one.
TEST_CASES[-1] = TestCaseSpec(
    id="ia_get_set_clone",
    method="IntArray.clone",
    setup=_SETUP + r"""
a = IntArray(3)
a.set(0, 7)
a.set(1, 8)
a.set(2, 9)
b = a.clone()
a.set(0, 1)
clone_vals = _ia_vals(b)
orig_vals = _ia_vals(a)
""",
    call="[orig_vals, clone_vals, a.universeSize()]",
    description="clone is independent after set",
    **_LIST
)

TEST_CASES.extend([
    TestCaseSpec(
        id="ia_to_string",
        method="IntArray.toString",
        setup=_SETUP,
        call="IntArray([1, 2, 3]).toString()",
        description="toString uses comma-space",
    ),
    TestCaseSpec(
        id="ia_to_string_empty",
        method="IntArray.toString",
        setup=_SETUP,
        call="IntArray(0).toString()",
        description="empty toString is []",
    ),
    TestCaseSpec(
        id="ia_equals_same",
        method="IntArray.equals",
        setup=_SETUP,
        call="IntArray([1, 2]).equals(IntArray([1, 2]))",
        description="equals by contents",
        **_BOOL
    ),
    TestCaseSpec(
        id="ia_equals_diff",
        method="IntArray.equals",
        setup=_SETUP,
        call="IntArray([1, 2]).equals(IntArray([1, 3]))",
        description="unequal contents",
        **_BOOL
    ),
    TestCaseSpec(
        id="ia_equals_null",
        method="IntArray.equals",
        setup=_SETUP,
        call="IntArray([1]).equals(None)",
        description="equals(null) is false",
        **_BOOL
    ),
    TestCaseSpec(
        id="ia_hashcode",
        method="IntArray.hashCode",
        setup=_SETUP,
        call="IntArray([1, 2, 3]).hashCode()",
        description="Java 31-polynomial hashCode",
    ),
    TestCaseSpec(
        id="ia_hashcode_empty",
        method="IntArray.hashCode",
        setup=_SETUP,
        call="IntArray(0).hashCode()",
        description="empty hashCode is 1",
    ),
    TestCaseSpec(
        id="ia_static_string",
        method="IntArray.intArrayToString",
        setup=_SETUP,
        call="IntArray.intArrayToString([7, 8])",
        description="static intArrayToString",
    ),
    TestCaseSpec(
        id="ia_string_to_array",
        method="IntArray.stringToArray",
        setup=_SETUP,
        call="_tolist(IntArray.stringToArray('1, 2  3'))",
        description="stringToArray splits on comma/space",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_equal_int_arrays",
        method="IntArray.equalIntArrays",
        setup=_SETUP,
        call="[IntArray.equalIntArrays([1,2],[1,2]), IntArray.equalIntArrays([1],[2])]",
        description="equalIntArrays",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_is_constant",
        method="IntArray.isConstant",
        setup=_SETUP,
        call="[IntArray([2,2,2]).isConstant(), IntArray([2,3]).isConstant(), IntArray(0).isConstant()]",
        description="isConstant including empty",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_is_idempotent",
        method="IntArray.isIdempotent",
        setup=_SETUP,
        call="[IntArray([0,1,2]).isIdempotent(), IntArray([1,1,2]).isIdempotent(), IntArray(0).isIdempotent()]",
        description="isIdempotent including empty",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_blocks",
        method="IntArray.satisfiesBlocksConstraint",
        setup=_SETUP,
        call="IntArray([5,5,9,9]).satisfiesBlocksConstraint([[0,1],[2,3]])",
        description="constant on each block",
        **_BOOL
    ),
    TestCaseSpec(
        id="ia_blocks_fail",
        method="IntArray.satisfiesBlocksConstraint",
        setup=_SETUP,
        call="IntArray([5,6,9,9]).satisfiesBlocksConstraint([[0,1],[2,3]])",
        description="not constant on first block",
        **_BOOL
    ),
    TestCaseSpec(
        id="ia_values",
        method="IntArray.satisfiesValuesConstraint",
        setup=_SETUP,
        call="IntArray([3,4,5]).satisfiesValuesConstraint([[0,3],[2,5]])",
        description="values constraint holds",
        **_BOOL
    ),
    TestCaseSpec(
        id="ia_set_constraint",
        method="IntArray.satisfiesSetConstraint",
        setup=_SETUP,
        call="IntArray([1,4,7]).satisfiesSetConstraint(1, set([3,4,5]))",
        description="set constraint at index 1",
        **_BOOL
    ),
    TestCaseSpec(
        id="ia_lex_cmp",
        method="IntArray.lexicographicComparitor",
        setup=_SETUP,
        call="IntArray.lexicographicComparitor().compare(IntArray([1,2]), IntArray([1,3]))",
        description="lexicographic comparator",
    ),
    TestCaseSpec(
        id="ia_getarray_copy",
        method="IntArray.getArray",
        setup=_SETUP + r"""
ia = IntArray([1, 2, 3])
arr = ia.getArray()
arr[0] = 99
live = ia.get(0)
""",
        call="live",
        description="getArray live alias (Java mutates IntArray)",
        xfail_reason=_GETARRAY_XFAIL,
    ),
    TestCaseSpec(
        id="ia_setintarray_replace",
        method="IntArray.setIntArray",
        setup=_SETUP + r"""
ia = IntArray([1, 2])
ia.setIntArray([9, 8, 7])
vals = _ia_vals(ia)
sz = ia.universeSize()
""",
        call="[sz, vals]",
        description="setIntArray can change length in Java",
        xfail_reason=_SETINT_XFAIL,
        **_LIST
    ),

    # ----- Horner -----
    TestCaseSpec(
        id="horner_sizes_roundtrip",
        method="Horner.hornerInv",
        setup=_SETUP + r"""
sizes = [2, 3, 4]
pairs = []
for i in range(24):
    t = _tolist(Horner.hornerInv(i, sizes))
    k = Horner.horner(t, sizes)
    pairs.append([t, k])
""",
        call="pairs",
        description="horner/hornerInv round-trip over 2x3x4",
        **_LIST
    ),
    TestCaseSpec(
        id="horner_same_size_roundtrip",
        method="Horner.horner",
        setup=_SETUP + r"""
pairs = []
for i in range(27):
    t = _tolist(Horner.hornerInv(i, 3, 3))
    k = Horner.horner(t, 3)
    pairs.append([t, k])
""",
        call="pairs",
        description="same-size horner round-trip over 3^3",
        **_LIST
    ),
    TestCaseSpec(
        id="horner_arity1",
        method="Horner.horner",
        setup=_SETUP,
        call="[Horner.horner([5], 10), _tolist(Horner.hornerInv(5, 10, 1))]",
        description="arity-1 encode/decode",
        **_LIST
    ),
    TestCaseSpec(
        id="horner_arity0_same_size",
        method="Horner.hornerInv",
        setup=_SETUP,
        call="_tolist(Horner.hornerInv(7, 3, 0))",
        description="hornerInv same-size length 0 returns empty",
        **_LIST
    ),
    TestCaseSpec(
        id="horner_empty_args_sizes",
        method="Horner.horner",
        setup=_SETUP,
        call="Horner.horner([], [2])",
        description="empty args with sizes AIOOBE",
        expected_exception="ArrayIndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="horner_dest_sizes",
        method="Horner.hornerInv",
        setup=_SETUP,
        call="_tolist(Horner.hornerInv(11, [2, 3, 4], [0, 0, 0]))",
        description="hornerInv dest overload (sizes)",
        **_LIST
    ),
    TestCaseSpec(
        id="horner_dest_same_size",
        method="Horner.hornerInv",
        setup=_SETUP,
        call="_tolist(Horner.hornerInv(11, 3, 3, [0, 0, 0]))",
        description="hornerInv dest overload (same size)",
        **_LIST
    ),
    TestCaseSpec(
        id="horner_reverse_array",
        method="Horner.reverseArray",
        setup=_SETUP,
        call="_tolist(Horner.reverseArray([1, 2, 3, 4]))",
        description="reverseArray",
        **_LIST
    ),
    TestCaseSpec(
        id="horner_left_right_reverse",
        method="Horner.leftRightReverse",
        setup=_SETUP,
        call="_tolist(Horner.leftRightReverse([0, 1, 2, 3, 4, 5, 6, 7], 2, 3))",
        description="leftRightReverse on 2^3 table",
        **_LIST
    ),
    TestCaseSpec(
        id="horner_integer_args",
        method="Horner.horner",
        setup=_SETUP,
        call="Horner.horner([1, 2, 3], 10)",
        description="horner(Integer[], size) same as int[]",
    ),

    # ----- SequenceGenerator incrementors -----
    TestCaseSpec(
        id="seq_right_2x3",
        method="SequenceGenerator.sequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.sequenceIncrementor, [0, 0], 2)",
        description="right incrementor max=2, arity 2 full sequence",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_right_3x2",
        method="SequenceGenerator.sequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.sequenceIncrementor, [0, 0, 0], 1)",
        description="right incrementor max=1, arity 3",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_right_size1",
        method="SequenceGenerator.sequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.sequenceIncrementor, [0], 3)",
        description="right incrementor size 1",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_right_empty",
        method="SequenceGenerator.sequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.sequenceIncrementor, [], 3)",
        description="right incrementor empty array stays empty",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_maxs",
        method="SequenceGenerator.sequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.sequenceIncrementor, [0, 0, 0], [1, 0, 2])",
        description="per-coordinate maxs",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_min",
        method="SequenceGenerator.sequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.sequenceIncrementor, [0, 0], 2, 1)",
        description="sequenceIncrementor with min",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_min_jump",
        method="SequenceGenerator.sequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.sequenceIncrementor, [0, 0, 4], 5, 4, 3)",
        description="sequenceIncrementor with min and jump=3",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_left",
        method="SequenceGenerator.leftSequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.leftSequenceIncrementor, [0, 0, 0], 1)",
        description="left incrementor arity 3 max 1",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_nondec",
        method="SequenceGenerator.nondecreasingSequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.nondecreasingSequenceIncrementor, [0, 0, 0], 2)",
        description="nondecreasing sequences arity 3 max 2",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_nondec_lastmin",
        method="SequenceGenerator.nondecreasingSequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.nondecreasingSequenceIncrementor, [0, 0, 2], 3, 2)",
        description="nondecreasing with lastMin=2",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_inc",
        method="SequenceGenerator.increasingSequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.increasingSequenceIncrementor, [0, 1, 2], 5)",
        description="strictly increasing from [0,1,2] max 5",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_inc_midstart",
        method="SequenceGenerator.increasingSequenceIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.increasingSequenceIncrementor, [1, 2, 4], 5)",
        description="increasing reentrant from [1,2,4]",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_inc_old",
        method="SequenceGenerator.increasingSequenceIncrementorOld",
        setup=_SETUP,
        call="_collect(SequenceGenerator.increasingSequenceIncrementorOld, [0, 1, 2], 4)",
        description="increasingSequenceIncrementorOld",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_init_partition",
        method="SequenceGenerator.initialPartition",
        setup=_SETUP,
        call="_tolist(SequenceGenerator.initialPartition(5, 2))",
        description="initial JB partition size 5 blocks 2",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_partition",
        method="SequenceGenerator.partitionArrayIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.partitionArrayIncrementor, SequenceGenerator.initialPartition(5, 2), 2)",
        description="all 2-block JB partitions of 5",
        **_LIST
    ),
    TestCaseSpec(
        id="seq_partition_midstart",
        method="SequenceGenerator.partitionArrayIncrementor",
        setup=_SETUP,
        call="_collect(SequenceGenerator.partitionArrayIncrementor, [0, 0, 2, 0, 2], 2)",
        description="partition incrementor from mid-start",
        **_LIST
    ),

    # ----- PermutationGenerator -----
    TestCaseSpec(
        id="perm_next_index_n3",
        method="PermutationGenerator.nextIndex",
        setup=_SETUP + r"""
g = PermutationGenerator(3)
idxs = []
for i in range(8):
    idxs.append(g.nextIndex())
""",
        call="idxs",
        description="nextIndex sequence for n=3 including terminal -1",
        **_LIST
    ),
    TestCaseSpec(
        id="perm_next_index_n1",
        method="PermutationGenerator.nextIndex",
        setup=_SETUP,
        call="PermutationGenerator(1).nextIndex()",
        description="n=1 nextIndex is -1",
    ),
    TestCaseSpec(
        id="perm_min1",
        method="PermutationGenerator.__init__",
        setup=_SETUP,
        call="PermutationGenerator(0)",
        description="n<1 raises IllegalArgumentException",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="perm_iterator_n3",
        method="PermutationGenerator.iterator",
        setup=_SETUP,
        call="_iter_perms(3)",
        description="full iterator listing n=3",
        **_LIST
    ),
    TestCaseSpec(
        id="perm_iterator_n1",
        method="PermutationGenerator.iterator",
        setup=_SETUP,
        call="_iter_perms(1)",
        description="iterator n=1 is [[0]]",
        **_LIST
    ),
    TestCaseSpec(
        id="perm_array_inc",
        method="PermutationGenerator.arrayIncrementor",
        setup=_SETUP,
        call="_collect(PermutationGenerator.arrayIncrementor, [0, 1, 2])",
        description="arrayIncrementor full n=3",
        **_LIST
    ),
    TestCaseSpec(
        id="perm_array_inc_dups",
        method="PermutationGenerator.arrayIncrementor",
        setup=_SETUP,
        call="_collect(PermutationGenerator.arrayIncrementor, [1, 1, 2])",
        description="arrayIncrementor skips equal swaps",
        **_LIST
    ),
    TestCaseSpec(
        id="perm_list_inc",
        method="PermutationGenerator.listIncrementor",
        setup=_SETUP,
        call="_collect_list(PermutationGenerator.listIncrementor, [0, 1])",
        description="listIncrementor n=2",
        **_LIST
    ),
    TestCaseSpec(
        id="perm_reset",
        method="PermutationGenerator.reset",
        setup=_SETUP + r"""
g = PermutationGenerator(3)
g.nextIndex()
g.reset()
first = g.nextIndex()
""",
        call="first",
        description="reset returns to identity before nextIndex",
    ),

    # ----- ArrayString -----
    TestCaseSpec(
        id="as_flat",
        method="ArrayString.toString",
        setup=_SETUP,
        call="_array_string(_as_arr([1, 2, 3]))",
        description="flat array no spaces",
    ),
    TestCaseSpec(
        id="as_nested",
        method="ArrayString.toString",
        setup=_SETUP,
        call="_array_string(_as_arr([[1, 2], [3]]))",
        description="nested arrays",
    ),
    TestCaseSpec(
        id="as_empty",
        method="ArrayString.toString",
        setup=_SETUP,
        call="_array_string(_as_arr([]))",
        description="empty array",
    ),
    TestCaseSpec(
        id="as_null",
        method="ArrayString.toString",
        setup=_SETUP,
        call="_array_string(None)",
        description="static ArrayString.toString(null) is 'null'",
    ),
    TestCaseSpec(
        id="as_scalar",
        method="ArrayString.toString",
        setup=_SETUP,
        call="_array_string(7)",
        description="non-array uses String.valueOf",
    ),

    # ----- SimpleList -----
    TestCaseSpec(
        id="sl_empty",
        method="SimpleList.isEmpty",
        setup=_SETUP,
        call="SimpleList.makeList().isEmpty()",
        description="makeList() is empty",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_make_one",
        method="SimpleList.first",
        setup=_SETUP,
        call="[SimpleList.makeList(5).first(), SimpleList.makeList(5).size(), SimpleList.makeList(5).rest().isEmpty()]",
        description="makeList(obj) is a singleton",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_cons_chain",
        method="SimpleList.cons",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
vals = _sl_vals(sl)
""",
        call="[vals, sl.size(), sl.toString()]",
        description="cons builds (1 2 3)",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_append_reverse",
        method="SimpleList.append",
        setup=_SETUP + r"""
a = SimpleList.makeList().cons(2).cons(1)
b = SimpleList.makeList().cons(4).cons(3)
vals = [_sl_vals(a.append(b)), _sl_vals(a.reverse()), _sl_vals(a.copyList())]
""",
        call="vals",
        description="append / reverse / copyList",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_contains_index",
        method="SimpleList.contains",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
""",
        call="[sl.contains(2), sl.contains(9), sl.indexOf(3), sl.get(1)]",
        description="contains / indexOf / get",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_add_uoe",
        method="SimpleList.add",
        setup=_SETUP,
        call="SimpleList.makeList(1).add(2)",
        description="add throws UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sl_clear_uoe",
        method="SimpleList.clear",
        setup=_SETUP,
        call="SimpleList.makeList(1).clear()",
        description="clear throws UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sl_ctor_pair",
        method="SimpleList.cons",
        setup=_SETUP,
        call="_sl_vals(SimpleList(1, SimpleList.makeList(2)))",
        description="SimpleList(obj, rest) constructor",
        **_LIST
    ),
    # ----- virtuallist -----
    TestCaseSpec(
        id="ll_int_tuples",
        method="LongList.intTuples",
        setup=_SETUP,
        call="_ll_all(LongList.intTuples(2, 3))",
        description="all length-2 tuples base 3",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_int_tuples_len1",
        method="LongList.intTuples",
        setup=_SETUP,
        call="_ll_all(LongList.intTuples(1, 4))",
        description="length-1 tuples",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_int_tuples_len0",
        method="LongList.intTuples",
        setup=_SETUP,
        call="[int(LongList.intTuples(0, 5).size()), _ll_all(LongList.intTuples(0, 5))]",
        description="length-0 tuples",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_int_tuples_neg",
        method="LongList.intTuples",
        setup=_SETUP,
        call="LongList.intTuples(-1, 2)",
        description="negative args IAE",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="ll_tuples_with_min",
        method="LongList.intTuplesWithMin",
        setup=_SETUP,
        call="_ll_all(LongList.intTuplesWithMin(3, 4, 2))",
        description="intTuplesWithMin(3,4,2) full list",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_fixed_subsets",
        method="LongList.fixedSizedSubsets",
        setup=_SETUP,
        call="_ll_all(LongList.fixedSizedSubsets(2, 4))",
        description="2-subsets of 4",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_subsets",
        method="LongList.subsets",
        setup=_SETUP,
        call="_ll_all(LongList.subsets(3))",
        description="all subsets of 3",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_permutations",
        method="LongList.permutations",
        setup=_SETUP,
        call="_ll_all(LongList.permutations(3))",
        description="all perms of 3 via LongList",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_factorial_binom",
        method="LongList.factorial",
        setup=_SETUP,
        call="[LongList.factorial(0), LongList.factorial(5), LongList.binomial(6, 2), LongList.pow2(4), LongList.log2(16)]",
        description="factorial / binomial / pow2 / log2",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_log2_nonpos",
        method="LongList.log2",
        setup=_SETUP,
        call="LongList.log2(0)",
        description="log2(0) IAE",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="vl_int_tuples",
        method="VirtualLists.intTuples",
        setup=_SETUP,
        call="_ll_all(VirtualLists.intTuples(2, 3))",
        description="VirtualLists.intTuples matches LongList",
        **_LIST
    ),
    TestCaseSpec(
        id="vl_tuples_min",
        method="VirtualLists.intTuplesWithMin",
        setup=_SETUP,
        call="_ll_all(VirtualLists.intTuplesWithMin(3, 4, 2))",
        description="VirtualLists.intTuplesWithMin full list",
        **_LIST
    ),
    TestCaseSpec(
        id="vl_indexer",
        method="VirtualLists.arrayIndexerWithMin",
        setup=_SETUP + r"""
out = []
for i in range(56):
    out.append(_tolist(VirtualLists.arrayIndexerWithMin(i, 3, 4, 2)))
""",
        call="out",
        description="arrayIndexerWithMin all 56 entries",
        **_LIST
    ),
    TestCaseSpec(
        id="twm_full",
        method="TupleWithMin.get",
        setup=_SETUP + r"""
t = TupleWithMin(3, 4, 2)
vals = _ll_all(t)
""",
        call="[int(t.size()), vals]",
        description="TupleWithMin(3,4,2) full list",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_stream",
        method="LongList.stream",
        setup=_SETUP,
        call="LongList.intTuples(2, 2).stream()",
        description="Java 8 stream not bound",
        xfail_reason=_STREAM_XFAIL,
    ),
])
