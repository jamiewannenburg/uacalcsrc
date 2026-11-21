"""Parity cases for wrapped org.uacalc.example methods/constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.example import FiniteField, KKMVWExample, TupleStream, Type1, Kearnes, HasKaryNU, ParallelClose8
from org.uacalc.io import AlgebraIO
from org.uacalc.util import IntArray
c2 = AlgebraIO.readAlgebraFile('resources/algebras/cyclic2.ua')
lat2 = AlgebraIO.readAlgebraFile('resources/algebras/lat2.ua')
kkm = KKMVWExample(2)
ts = TupleStream([10, 20, 30])
# GF(2) = FiniteField(2,1) never calls nextVector, so it constructs even
# when CPimport-3500.txt is missing. Larger fields NPE in Java.
ff21 = FiniteField(2, 1)

def _ia(obj):
    if obj is None:
        return None
    for attr in ('getArray', 'get_array', 'toArray', 'to_array'):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                return [int(x) for x in list(fn())]
            except TypeError:
                continue
    try:
        return [int(x) for x in list(obj)]
    except TypeError:
        return str(obj)

def _alg_info(alg):
    name = alg.getName() if hasattr(alg, 'getName') else alg.name()
    ops = alg.operations()
    nops = 0 if ops is None else len(list(ops))
    return [str(name), int(alg.cardinality()), nops]
"""

_SKIP = dict(skip_string_check=True)
_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List toString vs Python list.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")

_REDUCT_XFAIL = (
    "Rust gap: Type1.reductAlg builds a size-8 matrix-power reduct and looks up "
    "terms by IntArray identity"
)
_HASKARY_XFAIL = (
    "Environment: HasKaryNU.hasNUHorowitz uses ProgressReport and a large "
    "BigProduct close (heavy / GUI-adjacent)"
)
_PARALLEL8_XFAIL = (
    "Known Java bug: Incomplete Java 8 stream ParallelClose8; constructor is not "
    "a portable API"
)
_CONWAY_XFAIL = (
    "Environment: FiniteField.conwayPolynomial loads CPimport-3500.txt from the "
    "classpath; the UACalc jar does not ship that resource, so Java returns null"
)


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
    _c("inh_ff_convert", "FiniteField.convertToDefaultValueOps",
       "(ff21.convertToDefaultValueOps(), ff21.cardinality())[1]", "FiniteField convertToDefaultValueOps"),
    _c("inh_ff_univ_list", "FiniteField.getUniverseList",
       "list(ff21.getUniverseList())", "FiniteField getUniverseList", **_LIST),
    _c("inh_ff_univ_order", "FiniteField.getUniverseOrder",
       "ff21.getUniverseOrder()", "FiniteField getUniverseOrder", **_NONE),
    _c("ctor_finite_field_21", "FiniteField.FiniteField",
       "ff21.cardinality()", "FiniteField(2,1) constructor"),
    _c("ctor_finite_field_31", "FiniteField.FiniteField",
       "FiniteField(3, 1).cardinality()",
       "FiniteField(3,1) NPEs without Conway polynomials",
       xfail_reason=_CONWAY_XFAIL, **_SKIP),
    _c("ctor_kkm", "KKMVWExample.KKMVWExample",
       "kkm is not None", "KKMVWExample(2) constructor", **_BOOL),
    _c("ctor_tuple_stream", "TupleStream.TupleStream",
       "ts is not None", "TupleStream constructor", **_BOOL),
    _c("ff_get_polynomial_21", "FiniteField.getPolynomial",
       "list(ff21.getPolynomial() or [])",
       "Java getPolynomial is null without classpath Conway data",
       xfail_reason=_CONWAY_XFAIL, **_LIST),
    _c("ff_plus_01", "FiniteField.plus",
       "_ia(ff21.plus(ff21.getElement(0), ff21.getElement(1)))",
       "GF(2) plus(0,1)", **_LIST),
    _c("ff_plus_11", "FiniteField.plus",
       "_ia(ff21.plus(ff21.getElement(1), ff21.getElement(1)))",
       "GF(2) plus(1,1)", **_LIST),
    _c("ff_times_11", "FiniteField.times",
       "_ia(ff21.times(ff21.getElement(1), ff21.getElement(1)))",
       "GF(2) times(1,1)", **_LIST),
    _c("ff_times_01", "FiniteField.times",
       "_ia(ff21.times(ff21.getElement(0), ff21.getElement(1)))",
       "GF(2) times(0,1)", **_LIST),
    _c("ctor_parallel_close8", "ParallelClose8.ParallelClose8",
       "ParallelClose8(None, [], None)",
       "ParallelClose8 constructor",
       xfail_reason=_PARALLEL8_XFAIL, **_SKIP),
    _c("ff_negation_1", "FiniteField.negation",
       "_ia(ff21.negation(ff21.getElement(1)))", "GF(2) negation(1)", **_LIST),
    _c("ff_negation_0", "FiniteField.negation",
       "_ia(ff21.negation(ff21.getElement(0)))", "GF(2) negation(0)", **_LIST),
    _c("ff_negation_int_1", "FiniteField.negationInt",
       "ff21.negationInt(1)", "GF(2) negationInt(1)"),
    _c("ff_negation_int_0", "FiniteField.negationInt",
       "ff21.negationInt(0)", "GF(2) negationInt(0)"),
    _c("ff_algebra_type", "FiniteField.algebraType",
       "str(ff21.algebraType())", "FiniteField algebraType"),
    _c("ff_get_element_0", "FiniteField.getElement",
       "_ia(ff21.getElement(0))", "FiniteField getElement(0)", **_LIST),
    _c("ff_get_element_1", "FiniteField.getElement",
       "_ia(ff21.getElement(1))", "FiniteField getElement(1)", **_LIST),
    _c("ff_element_index_0", "FiniteField.elementIndex",
       "ff21.elementIndex(ff21.getElement(0))", "elementIndex of zero"),
    _c("ff_element_index_1", "FiniteField.elementIndex",
       "ff21.elementIndex(ff21.getElement(1))", "elementIndex of one"),
    _c("kearnes_make_ops_len", "Kearnes.makeKearnesOps",
       "len(list(Kearnes.makeKearnesOps(3)))", "makeKearnesOps(3) length"),
    _c("kearnes_make_ops_join", "Kearnes.makeKearnesOps",
       "list(Kearnes.makeKearnesOps(3))[0].intValueAt([1, 2])",
       "makeKearnesOps(3) first op at (1,2)"),
    _c("type1_subtraces_c2", "Type1.subtraces",
       "[_ia(a) for a in list(Type1.subtraces(c2, list(c2.con().joinIrreducibles())[0]))]",
       "Type1.subtraces of the unique JI of Con(C2)", **_LIST),
    _c("type1_reduct_c2", "Type1.reductAlg",
       "_alg_info(Type1.reductAlg(c2))",
       "Type1.reductAlg of C2", xfail_reason=_REDUCT_XFAIL, **_SKIP),
    _c("haskary_nu_c2", "HasKaryNU.hasNUHorowitz",
       "HasKaryNU.hasNUHorowitz(c2, 2)",
       "hasNUHorowitz on C2 arity 2",
       xfail_reason=_HASKARY_XFAIL, **_SKIP),
]
