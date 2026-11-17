"""Parity cases for wrapped org.uacalc.util methods/constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
import sys
from org.uacalc.util import IntArray, PermutationGenerator, SimpleList
from org.uacalc.util.virtuallist import TupleWithMin

def _ia_vals(a):
    if a is None:
        return None
    try:
        return [int(x) for x in list(a)]
    except TypeError:
        fn = getattr(a, "getArray", None) or getattr(a, "toArray", None)
        if callable(fn):
            return [int(x) for x in list(fn())]
        return str(a)

def _sl_vals(sl):
    if sl is None:
        return None
    out = []
    n = int(sl.size()) if hasattr(sl, "size") else len(list(sl))
    for i in range(n):
        out.append(sl.get(i))
    return out

ia = IntArray([1, 2, 3])
pg = PermutationGenerator(3)
sl = SimpleList.makeList().cons(3).cons(2).cons(1)
twm = TupleWithMin(3, 4, 2)
"""

_LIST = dict(skip_string_check=True, notes="Java List toString vs Python list.")
_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")


def _c(cid, method, call, description, **kw):
    return TestCaseSpec(
        id=cid,
        method=method,
        setup=_SETUP,
        call=call,
        description=description,
        **kw
    )


TEST_CASES = [
    _c("ctor_int_array", "IntArray.IntArray",
       "_ia_vals(ia)", "IntArray constructor", **_LIST),
    _c("ctor_int_array_empty", "IntArray.IntArray",
       "_ia_vals(IntArray([]))", "IntArray empty constructor", **_LIST),
    _c("ctor_perm_gen", "PermutationGenerator.PermutationGenerator",
       "int(pg.nextIndex()) >= 0",
       "PermutationGenerator constructor nextIndex", **_BOOL),
    _c("ctor_simple_list", "SimpleList.SimpleList",
       "_sl_vals(SimpleList(1, SimpleList.makeList(2)))",
       "SimpleList(obj, rest) constructor", **_LIST),
    _c("ctor_tuple_with_min", "TupleWithMin.TupleWithMin",
       "int(twm.size())",
       "TupleWithMin constructor size"),
    _c("sl_sublist_full", "SimpleList.subList",
       "_sl_vals(sl.subList(0, 3))", "subList of the whole list", **_LIST),
    _c("sl_sublist_middle", "SimpleList.subList",
       "_sl_vals(sl.subList(1, 2))", "subList of a singleton middle", **_LIST),
    _c("sl_sublist_empty", "SimpleList.subList",
       "_sl_vals(sl.subList(1, 1))", "subList empty range", **_LIST),
]
