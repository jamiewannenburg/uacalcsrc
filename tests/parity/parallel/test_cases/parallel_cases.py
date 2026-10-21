"""Test case specifications for org.uacalc.alg.parallel behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
import sys
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import Closer, BigProductAlgebra
from org.uacalc.alg.parallel import Pool, SingleClose
from org.uacalc.util import IntArray
from org.uacalc.terms import VariableImp

c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
m3 = AlgebraIO.readAlgebraFile("resources/algebras/m3.ua")
n5 = AlgebraIO.readAlgebraFile("resources/algebras/n5.ua")
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
bp2 = BigProductAlgebra(c2, 2)
bp3 = BigProductAlgebra(c3, 2)
bp_m3 = BigProductAlgebra(m3, 1)
bp_n5 = BigProductAlgebra(n5, 1)
bp_lat2 = BigProductAlgebra(lat2, 2)
g00 = IntArray([0, 0])
g11 = IntArray([1, 1])
g01 = IntArray([0, 1])
g10 = IntArray([1, 0])
g0 = IntArray([0])
g1 = IntArray([1])
g2 = IntArray([2])

def _coords(elem):
    if elem is None:
        return None
    try:
        return [int(x) for x in list(elem)]
    except TypeError:
        pass
    for attr in ("getArray", "get_array", "toArray", "to_array"):
        fn = getattr(elem, attr, None)
        if callable(fn):
            return [int(x) for x in fn()]
    return str(elem)

def _ias(lst):
    if lst is None:
        return None
    return [_coords(x) for x in list(lst)]

def _sorted_ias(lst):
    got = _ias(lst)
    if got is None:
        return None
    return sorted(got)

def _quiet(closer):
    fn = getattr(closer, 'setSuppressOutput', None) or getattr(closer, 'set_suppress_output', None)
    if callable(fn):
        fn(True)
    return closer

def _seq_close(alg, gens):
    old = getattr(Closer, 'doParallel', False)
    try:
        Closer.doParallel = False
        return _sorted_ias(_quiet(Closer(alg, gens)).sgClose())
    finally:
        Closer.doParallel = old

def _par_close(alg, gens):
    old = getattr(Closer, 'doParallel', False)
    try:
        Closer.doParallel = True
        # Java sgCloseParallel NPEs if termMap is null; makeTermMap=True.
        return _sorted_ias(_quiet(Closer(alg, gens, True)).sgClose())
    finally:
        Closer.doParallel = old

def _one_step(univ, op, min_i, max_i):
    univ = list(univ)
    if sys.platform.startswith('java'):
        from java.util.concurrent import ConcurrentHashMap, ForkJoinPool
        from java.util.concurrent.atomic import AtomicInteger
        from java.lang import Thread
        mmap = ConcurrentHashMap()
        for i, el in enumerate(univ):
            mmap.put(el, VariableImp('x' + str(i)))
        sc = SingleClose(univ, mmap, op, min_i, max_i, AtomicInteger(len(univ)))
        results = sc.doOneStep(ForkJoinPool(), Thread.currentThread(), None, None)
    else:
        sc = SingleClose(univ, None, op, min_i, max_i, len(univ))
        results = sc.doOneStep()
    out = []
    if results is None:
        return None
    for chunk in results:
        if chunk is None:
            continue
        for x in chunk:
            out.append(_coords(x))
    out.sort()
    return out

def _ops(alg):
    ops = getattr(alg, 'operations', None)
    if callable(ops):
        ops = ops()
    if ops is None:
        ops = alg.getOperations()
    return list(ops)

def _first_op(alg):
    return _ops(alg)[0]

c2_op = _first_op(c2)
m3_join = _ops(m3)[0]

Closer.doParallel = False
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_STR = dict(skip_string_check=True, notes="Java Object.toString is Class@hex.")
_LIST = dict(skip_string_check=True, notes="Java List toString vs Python list.")


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
    # --- Pool surface ---
    _c("pool_class_name", "Pool", "Pool.__name__", "Pool is importable"),
    _c("pool_construct", "Pool", "Pool().__class__.__name__", "Pool() default constructor"),
    _c("pool_toString", "Pool.toString", "len(Pool().toString()) > 0", "Pool toString is non-empty (Java Class@hex)", **_BOOL),
    # --- sequential closures (Java source of truth) ---
    _c("seq_c2_2_diag", "Closer.sgClose", "_seq_close(bp2, [g00, g11])", "sequential close C2^2 diagonal gens", **_LIST),
    _c("seq_c2_2_all", "Closer.sgClose", "_seq_close(bp2, [g00, g01, g10, g11])", "sequential close C2^2 all tuples", **_LIST),
    _c("seq_c2_2_zero", "Closer.sgClose", "_seq_close(bp2, [g00])", "sequential close C2^2 from zero", **_LIST),
    _c("seq_c3_2_diag", "Closer.sgClose", "_seq_close(bp3, [IntArray([0,0]), IntArray([1,1]), IntArray([2,2])])", "sequential close C3^2 diagonal", **_LIST),
    _c("seq_m3_1", "Closer.sgClose", "_seq_close(bp_m3, [g0, g1])", "sequential close M3^1 two gens", **_LIST),
    _c("seq_n5_1", "Closer.sgClose", "_seq_close(bp_n5, [g0])", "sequential close N5^1 from zero", **_LIST),
    _c("seq_lat2_2", "Closer.sgClose", "_seq_close(bp_lat2, [g00, g11])", "sequential close lat2^2 diagonal", **_LIST),
    # --- parallel closures: same sorted universe as sequential ---
    _c("par_c2_2_diag", "Closer.sgClose", "_par_close(bp2, [g00, g11])", "parallel close C2^2 diagonal gens", **_LIST),
    _c("par_c2_2_all", "Closer.sgClose", "_par_close(bp2, [g00, g01, g10, g11])", "parallel close C2^2 all tuples", **_LIST),
    _c("par_c2_2_zero", "Closer.sgClose", "_par_close(bp2, [g00])", "parallel close C2^2 from zero", **_LIST),
    _c("par_c3_2_diag", "Closer.sgClose", "_par_close(bp3, [IntArray([0,0]), IntArray([1,1]), IntArray([2,2])])", "parallel close C3^2 diagonal", **_LIST),
    _c("par_m3_1", "Closer.sgClose", "_par_close(bp_m3, [g0, g1])", "parallel close M3^1 two gens", **_LIST),
    _c("par_n5_1", "Closer.sgClose", "_par_close(bp_n5, [g0])", "parallel close N5^1 from zero", **_LIST),
    _c("par_lat2_2", "Closer.sgClose", "_par_close(bp_lat2, [g00, g11])", "parallel close lat2^2 diagonal", **_LIST),
    _c("par_matches_seq_c2", "Closer.sgClose", "_par_close(bp2, [g00, g11]) == _seq_close(bp2, [g00, g11])", "parallel C2^2 equals sequential", **_BOOL),
    _c("par_matches_seq_m3", "Closer.sgClose", "_par_close(bp_m3, [g0, g1]) == _seq_close(bp_m3, [g0, g1])", "parallel M3 equals sequential", **_BOOL),
    _c("par_matches_seq_n5", "Closer.sgClose", "_par_close(bp_n5, [g0]) == _seq_close(bp_n5, [g0])", "parallel N5 equals sequential", **_BOOL),
    # --- SingleClose.doOneStep on small universes (increment=1, deterministic) ---
    _c("single_close_class", "SingleClose", "SingleClose.__name__", "SingleClose is importable"),
    _c(
        "single_close_c2_one_step",
        "SingleClose.doOneStep",
        "_one_step([IntArray([1])], c2_op, 0, 0)",
        "one pass of SingleClose on C2 from {1}",
        xfail_reason=(
            "Java IntOperation.valueAt(int[][]) throws UnsupportedOperationException, "
            "so SingleClose.doOneStep on a table operation does not produce elements. "
            "Rust uses value_at_arrays and returns the closure step. Not faked: this "
            "is a Java limitation. Parallel element-set parity is covered by "
            "Closer.doParallel / sgClose. CPython BigProductAlgebra.operations() is bound."
        ),
        **_LIST
    ),
    _c(
        "single_close_m3_one_step",
        "SingleClose.doOneStep",
        "_one_step([IntArray([1]), IntArray([2])], m3_join, 0, 1)",
        "one pass of SingleClose on M3 join of 1 and 2",
        xfail_reason=(
            "Java IntOperation.valueAt(int[][]) throws UnsupportedOperationException, "
            "so SingleClose.doOneStep on a table operation does not produce elements. "
            "Rust uses value_at_arrays. Not faked: this is a Java limitation. "
            "Parallel element-set parity is covered by Closer.doParallel sgClose goldens."
        ),
        **_LIST
    ),
]
