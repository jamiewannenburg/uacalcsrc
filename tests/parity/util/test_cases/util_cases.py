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

def _iter_vals(it):
    out = []
    while it.hasNext():
        out.append(it.next())
    return out

def _enum_vals(en):
    out = []
    while en.hasMoreElements():
        out.append(en.nextElement())
    return out

def _arr_vals(a):
    if a is None:
        return None
    return [a[i] for i in range(len(a))]

def _dest(n, fill=None):
    vals = [fill] * n
    if sys.platform.startswith('java'):
        from jarray import array
        from java.lang import Object
        return array(vals, Object)
    return vals
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
_APP_REV_XFAIL = (
    "Java SimpleList.app / rev are commented out of the live class; "
    "the scanner still sees them. Python aliases them to append/reverse. "
    "Owner: do not expose commented-out Java. Do not change Java expected values."
)
_PARALLEL_XFAIL = (
    "Java 8 LongList.parallelStream is not bound. "
    "Owner: Stream API out of scope for the org shim."
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
    TestCaseSpec(
        id="ll_parallel_stream",
        method="LongList.parallelStream",
        setup=_SETUP,
        call="LongList.intTuples(2, 2).parallelStream()",
        description="Java 8 parallelStream not bound",
        xfail_reason=_PARALLEL_XFAIL,
    ),
])

TEST_CASES.extend([
    # ----- IntArray remaining -----
    TestCaseSpec(
        id="ia_set_values",
        method="IntArray.set",
        setup=_SETUP + r"""
a = IntArray(3)
a.set(0, 7)
a.set(1, 8)
a.set(2, 9)
vals = _ia_vals(a)
""",
        call="vals",
        description="IntArray.set writes each index",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_set_oob",
        method="IntArray.set",
        setup=_SETUP,
        call="IntArray([1, 2]).set(2, 9)",
        description="IntArray.set out of bounds",
        expected_exception="ArrayIndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="ia_set_empty",
        method="IntArray.set",
        setup=_SETUP,
        call="IntArray(0).set(0, 1)",
        description="set on empty IntArray AIOOBE",
        expected_exception="ArrayIndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="ia_toarray",
        method="IntArray.toArray",
        setup=_SETUP,
        call="[_tolist(IntArray([4, 5]).toArray()), _tolist(IntArray(0).toArray()), _tolist(IntArray([9]).toArray())]",
        description="toArray copy of several sizes",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_compare_sizes",
        method="IntArray.compare",
        setup=_SETUP,
        call=(
            "[IntArray.lexicographicComparitor().compare(IntArray([1]), IntArray([1, 0])), "
            "IntArray.lexicographicComparitor().compare(IntArray([2, 0]), IntArray([1])), "
            "IntArray.lexicographicComparitor().compare(IntArray([]), IntArray([])), "
            "IntArray.lexicographicComparitor().compare(IntArray([1]), IntArray([1]))]"
        ),
        description="lex compare different lengths including empty",
        **_LIST
    ),
    TestCaseSpec(
        id="ia_cong_constraint",
        method="IntArray.satisfiesCongruenceConstraint",
        setup=_SETUP + r"""
from org.uacalc.alg.conlat import BasicPartition
p01 = BasicPartition('|0 1|2|')
ia = IntArray([0, 1, 2])
""",
        call=(
            "[ia.satisfiesCongruenceConstraint(0, p01, 1), "
            "ia.satisfiesCongruenceConstraint(0, p01, 2), "
            "ia.satisfiesCongruenceConstraint(2, p01, 2), "
            "IntArray([1, 1, 1]).satisfiesCongruenceConstraint(1, p01, 0)]"
        ),
        description="congruence constraint vs |0 1|2|",
        **_LIST
    ),

    # ----- ArrayIncrementor.increment -----
    TestCaseSpec(
        id="inc_flags_right",
        method="ArrayIncrementor.increment",
        setup=_SETUP + r"""
a = _ia([0, 0])
inc = SequenceGenerator.sequenceIncrementor(a, 1)
flags = []
n = 0
while True:
    flags.append(inc.increment())
    n += 1
    if (not flags[-1]) or n > 20:
        break
""",
        call="flags",
        description="increment returns True until exhausted then False",
        **_LIST
    ),
    TestCaseSpec(
        id="inc_empty_false",
        method="ArrayIncrementor.increment",
        setup=_SETUP,
        call="SequenceGenerator.sequenceIncrementor(_ia([]), 3).increment()",
        description="increment on empty array is False",
        **_BOOL
    ),

    # ----- LongList binomial / pow2 / size -----
    TestCaseSpec(
        id="ll_binomial_table",
        method="LongList.binomial",
        setup=_SETUP,
        call="[[LongList.binomial(n, r) for r in range(0, n+1)] for n in range(0, 8)]",
        description="binomial rows n=0..7",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_pow2_range",
        method="LongList.pow2",
        setup=_SETUP,
        call="[LongList.pow2(r) for r in range(0, 8)]",
        description="pow2(0..7)",
        **_LIST
    ),
    TestCaseSpec(
        id="ll_size_variants",
        method="LongList.size",
        setup=_SETUP,
        call=(
            "[int(LongList.intTuples(0, 5).size()), int(LongList.intTuples(1, 4).size()), "
            "int(LongList.intTuples(2, 3).size()), int(LongList.subsets(0).size()), "
            "int(LongList.permutations(1).size()), int(TupleWithMin(2, 3, 1).size())]"
        ),
        description="size of empty, arity-1, and small virtual lists",
        **_LIST
    ),

    # ----- VirtualLists foo / bar / baz / testPow -----
    TestCaseSpec(
        id="vl_foo_samples",
        method="VirtualLists.foo",
        setup=_SETUP,
        call="[[VirtualLists.foo(k, r) for k in [1, 10, 100, 1000]] for r in [2, 3, 5]]",
        description="foo(k,r) samples",
        **_LIST
    ),
    TestCaseSpec(
        id="vl_bar_samples",
        method="VirtualLists.bar",
        setup=_SETUP,
        call="[[VirtualLists.bar(k, r) for k in [1, 10, 100, 1000]] for r in [2, 3, 5]]",
        description="bar(k,r) samples",
        **_LIST
    ),
    TestCaseSpec(
        id="vl_baz_samples",
        method="VirtualLists.baz",
        setup=_SETUP,
        call="[VirtualLists.baz(k, 3) for k in [1, 8, 20, 50]]",
        description="baz(k,3) return values (Java also prints)",
        **_LIST
    ),
    TestCaseSpec(
        id="vl_test_pow",
        method="VirtualLists.testPow",
        setup=_SETUP,
        call="VirtualLists.testPow(1000)",
        description="testPow is void; Java prints, both return None",
        **_NONE
    ),

    # ----- PermutationGenerator iterator next / hasNext / remove -----
    TestCaseSpec(
        id="perm_has_next_n2",
        method="PermutationGenerator.hasNext",
        setup=_SETUP + r"""
it = PermutationGenerator.iterator(2)
flags = []
while it.hasNext():
    flags.append(True)
    it.next()
flags.append(it.hasNext())
""",
        call="flags",
        description="hasNext through all n=2 perms then False",
        **_LIST
    ),
    TestCaseSpec(
        id="perm_next_n1",
        method="PermutationGenerator.next",
        setup=_SETUP,
        call="_iter_perms(1)",
        description="next via iterator n=1",
        **_LIST
    ),
    TestCaseSpec(
        id="perm_remove_uoe",
        method="PermutationGenerator.remove",
        setup=_SETUP,
        call="PermutationGenerator.iterator(2).remove()",
        description="iterator.remove UOE",
        expected_exception="UnsupportedOperationException",
    ),

    # ----- SimpleList remaining -----
    TestCaseSpec(
        id="sl_make_list_empty_and_one",
        method="SimpleList.makeList",
        setup=_SETUP,
        call=(
            "[SimpleList.makeList().isEmpty(), SimpleList.makeList().size(), "
            "_sl_vals(SimpleList.makeList(7)), SimpleList.makeList(7).size()]"
        ),
        description="makeList() empty and makeList(obj) singleton",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_size_chain",
        method="SimpleList.size",
        setup=_SETUP,
        call=(
            "[SimpleList.makeList().size(), SimpleList.makeList(1).size(), "
            "SimpleList.makeList().cons(3).cons(2).cons(1).size()]"
        ),
        description="size empty / 1 / 3",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_rest_chain",
        method="SimpleList.rest",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
empty = SimpleList.makeList()
""",
        call="[_sl_vals(sl.rest()), _sl_vals(sl.rest().rest()), empty.rest().isEmpty()]",
        description="rest chain including empty.rest is empty",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_reverse_and_revappend",
        method="SimpleList.reverse",
        setup=_SETUP + r"""
a = SimpleList.makeList().cons(2).cons(1)
b = SimpleList.makeList().cons(4).cons(3)
empty = SimpleList.makeList()
""",
        call="[_sl_vals(a.reverse()), _sl_vals(a.reverse(b)), _sl_vals(empty.reverse()), _sl_vals(empty.reverse(b))]",
        description="reverse() and reverse(lst) revappend, including empty",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_copy_list",
        method="SimpleList.copyList",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
c = sl.copyList()
""",
        call="[_sl_vals(c), _sl_vals(SimpleList.makeList().copyList()), sl.size() == c.size()]",
        description="copyList deep copy including empty",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_index_of_last",
        method="SimpleList.indexOf",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(1).cons(2).cons(1)
""",
        call="[sl.indexOf(1), sl.indexOf(2), sl.indexOf(9), SimpleList.makeList().indexOf(1)]",
        description="indexOf first match, missing, empty",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_last_index_of",
        method="SimpleList.lastIndexOf",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(1).cons(2).cons(1)
""",
        call="[sl.lastIndexOf(1), sl.lastIndexOf(2), sl.lastIndexOf(9), SimpleList.makeList().lastIndexOf(1)]",
        description="lastIndexOf duplicates, missing, empty",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_contains_all",
        method="SimpleList.containsAll",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
need = SimpleList.makeList().cons(3).cons(1)
missing = SimpleList.makeList().cons(9).cons(1)
""",
        call="[sl.containsAll(need), sl.containsAll(missing), sl.containsAll(SimpleList.makeList()), SimpleList.makeList().containsAll(need)]",
        description="containsAll including empty collection",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_toarray_no_dest",
        method="SimpleList.toArray",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
""",
        call="[_arr_vals(sl.toArray()), _arr_vals(SimpleList.makeList().toArray()), _arr_vals(SimpleList.makeList(7).toArray())]",
        description="toArray() empty, size 1, size 3",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_toarray_dest_fit",
        method="SimpleList.toArray",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(2).cons(1)
out = sl.toArray(_dest(4, 'x'))
""",
        call="_arr_vals(out)",
        description="toArray(dest) fills and null-pads",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_toarray_dest_short",
        method="SimpleList.toArray",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
out = sl.toArray(_dest(1, 'x'))
""",
        call="_arr_vals(out)",
        description="toArray(dest) reallocates when dest is short",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_add_all_uoe",
        method="SimpleList.addAll",
        setup=_SETUP,
        call="SimpleList.makeList(1).addAll(SimpleList.makeList(2))",
        description="addAll throws UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sl_remove_uoe",
        method="SimpleList.remove",
        setup=_SETUP,
        call="SimpleList.makeList(1).remove(1)",
        description="remove throws UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sl_remove_all_uoe",
        method="SimpleList.removeAll",
        setup=_SETUP,
        call="SimpleList.makeList(1).removeAll(SimpleList.makeList(1))",
        description="removeAll throws UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sl_retain_all_uoe",
        method="SimpleList.retainAll",
        setup=_SETUP,
        call="SimpleList.makeList(1).retainAll(SimpleList.makeList(1))",
        description="retainAll throws UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sl_set_uoe",
        method="SimpleList.set",
        setup=_SETUP,
        call="SimpleList.makeList(1).set(0, 2)",
        description="List.set throws UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sl_app_commented",
        method="SimpleList.app",
        setup=_SETUP,
        call="_sl_vals(SimpleList.makeList(1).app(SimpleList.makeList(2)))",
        description="app is commented out in Java",
        xfail_reason=_APP_REV_XFAIL,
        **_LIST
    ),
    TestCaseSpec(
        id="sl_rev_commented",
        method="SimpleList.rev",
        setup=_SETUP,
        call="_sl_vals(SimpleList.makeList().cons(2).cons(1).rev())",
        description="rev is commented out in Java",
        xfail_reason=_APP_REV_XFAIL,
        **_LIST
    ),
    TestCaseSpec(
        id="sl_elements_enum",
        method="SimpleList.elements",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
empty = SimpleList.makeList()
one = SimpleList.makeList(7)
""",
        call="[_enum_vals(sl.elements()), _enum_vals(empty.elements()), _enum_vals(one.elements())]",
        description="elements() Enumeration full walk",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_has_more_elements",
        method="SimpleList.hasMoreElements",
        setup=_SETUP + r"""
en = SimpleList.makeList().cons(2).cons(1).elements()
flags = [en.hasMoreElements()]
en.nextElement()
flags.append(en.hasMoreElements())
en.nextElement()
flags.append(en.hasMoreElements())
""",
        call="flags",
        description="hasMoreElements before/during/after walk",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_next_element",
        method="SimpleList.nextElement",
        setup=_SETUP,
        call="_enum_vals(SimpleList.makeList().cons(3).cons(2).cons(1).elements())",
        description="nextElement full sequence",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_next_element_empty",
        method="SimpleList.nextElement",
        setup=_SETUP,
        call="SimpleList.makeList().elements().nextElement()",
        description="nextElement on empty Enumeration returns null",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_get_iterator",
        method="SimpleList.getIterator",
        setup=_SETUP,
        call="[_iter_vals(SimpleList.makeList().cons(2).cons(1).getIterator()), _iter_vals(SimpleList.makeList().getIterator())]",
        description="getIterator walk including empty",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_front_iterator",
        method="SimpleList.frontIterator",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
tail = sl.rest()
whole = sl.frontIterator(SimpleList.makeList())
""",
        call="[_iter_vals(sl.frontIterator(tail)), _iter_vals(sl.frontIterator(sl)), _iter_vals(whole)]",
        description="frontIterator stops at rest-identity tail",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_list_iterator_forward",
        method="SimpleList.listIterator",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
it = sl.listIterator()
fwd = []
while it.hasNext():
    fwd.append([it.nextIndex(), it.next()])
""",
        call="fwd",
        description="listIterator forward nextIndex/next",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_list_iterator_back",
        method="SimpleList.hasPrevious",
        setup=_SETUP + r"""
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
it = sl.listIterator()
while it.hasNext():
    it.next()
back = []
while it.hasPrevious():
    back.append([it.previousIndex(), it.previous()])
""",
        call="back",
        description="listIterator backward previousIndex/previous",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_previous",
        method="SimpleList.previous",
        setup=_SETUP + r"""
it = SimpleList.makeList().cons(2).cons(1).listIterator(2)
""",
        call="[it.previous(), it.previous()]",
        description="previous from end of size-2 list",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_previous_index_start",
        method="SimpleList.previousIndex",
        setup=_SETUP,
        call="SimpleList.makeList().cons(1).listIterator().previousIndex()",
        description="previousIndex at start is -1",
    ),
    TestCaseSpec(
        id="sl_list_iterator_at",
        method="SimpleList.listIterator",
        setup=_SETUP,
        call="_iter_vals(SimpleList.makeList().cons(3).cons(2).cons(1).listIterator(1))",
        description="listIterator(1) starts at index 1",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_list_iterator_oob",
        method="SimpleList.listIterator",
        setup=_SETUP,
        call="SimpleList.makeList(1).listIterator(2)",
        description="listIterator past size IOBE",
        expected_exception="IndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="sl_list_iterator_empty",
        method="SimpleList.hasNext",
        setup=_SETUP + r"""
it = SimpleList.makeList().listIterator()
""",
        call="[it.hasNext(), it.hasPrevious(), it.nextIndex(), it.previousIndex()]",
        description="listIterator on empty list",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_list_iterator_remove_uoe",
        method="SimpleList.remove",
        setup=_SETUP,
        call="SimpleList.makeList(1).listIterator().remove()",
        description="listIterator.remove UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sl_next_exhausted",
        method="SimpleList.next",
        setup=_SETUP,
        call="SimpleList.makeList().iterator().next()",
        description="next on empty Enumeration iterator returns null",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_previous_exhausted",
        method="SimpleList.previous",
        setup=_SETUP,
        call="SimpleList.makeList(1).listIterator().previous()",
        description="previous at start NSE",
        expected_exception="NoSuchElementException",
    ),
    TestCaseSpec(
        id="sl_get_oob",
        method="SimpleList.get",
        setup=_SETUP,
        call="SimpleList.makeList(1).get(1)",
        description="get past end IOBE",
        expected_exception="IndexOutOfBoundsException",
    ),
])
