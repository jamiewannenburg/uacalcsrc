"""Parity cases for wrapped org.uacalc.alg methods/constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import (
    AlgebraFromMinimalSets, AlgebraWithGeneratingVector, BasicAlgebra,
    BigProductAlgebra, Closer, CloserTiming, FreeAlgebra, GeneralAlgebra,
    Homomorphism, MaltsevDecompositionIterator, MaltsevProductDecomposition,
    MatrixPowerAlgebra, PolinLikeAlgebra, PowerAlgebra, ProductAlgebra,
    QuotientAlgebra, QuotientElement, ReductAlgebra, SubProductAlgebra,
    Subalgebra, UnaryTermsMonoid,
)
from org.uacalc.alg.op import OperationSymbol, Operations
from org.uacalc.util import IntArray
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
n5 = AlgebraIO.readAlgebraFile("resources/algebras/n5.ua")
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
id1 = Operations.makeIntOperation(OperationSymbol("id", 1), 2, [0, 1])
plus = OperationSymbol("+", 2)
bp2 = BigProductAlgebra(c2, 2)
bp3 = BigProductAlgebra(c3, 2)
g00 = IntArray([0, 0])
g11 = IntArray([1, 1])
g01 = IntArray([0, 1])
sp = SubProductAlgebra("SP", bp2, [g00, g11])
cong = n5.con().Cg(0, 1)
decomp = MaltsevProductDecomposition(n5, cong)
q = QuotientAlgebra(c2, c2.con().Cg(0, 1))
qe = QuotientElement(q, 0)
closer = Closer(bp2, [g00, g11], True)
closer.setSuppressOutput(True)
prod = ProductAlgebra("C2xC2", [c2, c2])
pwr = PowerAlgebra("C2^2", c2, 2)
s0 = Subalgebra("S0", c2, [0])
h = Homomorphism(c2, c2, {0: 0, 1: 1})
afms = AlgebraFromMinimalSets("fromC2", c2)
awgv = AlgebraWithGeneratingVector(c2, [0, 1])
mp = MatrixPowerAlgebra("mp", c2, 1)
pol = PolinLikeAlgebra("pol", c2, c2, None, 0, 0)
try:
    from java.util import HashSet
    _univ = HashSet()
    _univ.add(0)
    _univ.add(1)
except ImportError:
    _univ = [0, 1]
ga = GeneralAlgebra("G", _univ, [id1])
utm = UnaryTermsMonoid(c2)
f1 = FreeAlgebra(c2, 1)
ct = CloserTiming(bp2, None)
basic = BasicAlgebra("B", 2, [id1])

def _ias(lst):
    if lst is None:
        return None
    out = []
    for x in list(lst):
        try:
            out.append([int(v) for v in list(x)])
        except TypeError:
            getter = getattr(x, "getArray", None) or getattr(x, "to_array", None) or getattr(x, "get_array", None)
            out.append([int(v) for v in getter()] if callable(getter) else x)
    return out

def _sorted_ias(lst):
    got = _ias(lst)
    if got is None:
        return None
    return sorted(got)

def _term_str(t):
    if t is None:
        return None
    return str(t).replace(" ", "")

def _alg_card(alg):
    if alg is None:
        return None
    return int(alg.cardinality())

def _term_map():
    try:
        from java.util.concurrent import ConcurrentHashMap
        return ConcurrentHashMap()
    except ImportError:
        return {}

def _par_close(alg, gens):
    cl = Closer(alg, gens, True)
    setter = getattr(cl, 'setSuppressOutput', None) or getattr(cl, 'set_suppress_output', None)
    if callable(setter):
        setter(True)
    tm = _term_map()
    orig = cl.getTermMap()
    if orig is not None:
        try:
            tm.putAll(orig)
        except Exception:
            try:
                for k in orig:
                    tm[k] = orig[k]
            except Exception:
                pass
    return _sorted_ias(cl.sgCloseParallel(list(cl.getGenerators()), 0, tm))
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List toString vs Python list.")
_ALG = dict(skip_string_check=True, notes="Java Algebra toString is Class@hex; values compared.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")
_TERM = dict(skip_string_check=True, notes="Term toString spacing.")
_LAT = dict(skip_string_check=True, notes="Java lattice toString is Class@hex; values compared.")


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
    _c("ctor_basic_algebra", "BasicAlgebra.BasicAlgebra",
       "basic.cardinality()", "BasicAlgebra constructor cardinality"),
    _c("ctor_basic_algebra_c3", "BasicAlgebra.BasicAlgebra",
       "BasicAlgebra('C3copy', int(c3.cardinality()), list(c3.operations())).cardinality()",
       "BasicAlgebra copy of cyclic3 cardinality"),
    _c("ctor_big_product", "BigProductAlgebra.BigProductAlgebra",
       "bp2.cardinality()", "BigProductAlgebra(C2, 2) constructor"),
    _c("ctor_big_product_c3", "BigProductAlgebra.BigProductAlgebra",
       "bp3.cardinality()", "BigProductAlgebra(C3, 2) constructor"),
    _c("ctor_closer", "Closer.Closer",
       "len(list(closer.getGenerators()))", "Closer constructor stores generators"),
    _c("ctor_closer_timing", "CloserTiming.CloserTiming",
       "ct is not None", "CloserTiming(algebra, None) constructs", **_BOOL),
    _c("ctor_free_algebra", "FreeAlgebra.FreeAlgebra",
       "f1.cardinality()", "FreeAlgebra(C2, 1) constructor"),
    _c("ctor_general_algebra", "GeneralAlgebra.GeneralAlgebra",
       "ga.cardinality()", "GeneralAlgebra constructor cardinality"),
    _c("ctor_homomorphism", "Homomorphism.Homomorphism",
       "h.kernel().numberOfBlocks()", "Homomorphism constructor kernel"),
    _c("ctor_mdi", "MaltsevDecompositionIterator.MaltsevDecompositionIterator",
       "MaltsevDecompositionIterator(n5).hasNext()",
       "MaltsevDecompositionIterator constructor", **_BOOL),
    _c("ctor_mpd", "MaltsevProductDecomposition.MaltsevProductDecomposition",
       "decomp.getAlgebra().cardinality()", "MaltsevProductDecomposition constructor", **_ALG),
    _c("ctor_matrix_power", "MatrixPowerAlgebra.MatrixPowerAlgebra",
       "mp.cardinality()", "MatrixPowerAlgebra constructor"),
    _c("ctor_polin", "PolinLikeAlgebra.PolinLikeAlgebra",
       "pol.getName()", "PolinLikeAlgebra constructor name"),
    _c("ctor_power", "PowerAlgebra.PowerAlgebra",
       "pwr.cardinality()", "PowerAlgebra constructor"),
    _c("ctor_product", "ProductAlgebra.ProductAlgebra",
       "prod.cardinality()", "ProductAlgebra constructor"),
    _c("ctor_quotient", "QuotientAlgebra.QuotientAlgebra",
       "q.cardinality()", "QuotientAlgebra constructor"),
    _c("ctor_quotient_element", "QuotientElement.QuotientElement",
       "qe.getIndex()", "QuotientElement constructor index", **_ALG),
    _c("ctor_reduct", "ReductAlgebra.ReductAlgebra",
       "ReductAlgebra('R', c2, []).cardinality()", "ReductAlgebra constructor"),
    _c("ctor_subproduct", "SubProductAlgebra.SubProductAlgebra",
       "sp.cardinality()", "SubProductAlgebra constructor"),
    _c("ctor_subalgebra", "Subalgebra.Subalgebra",
       "s0.cardinality()", "Subalgebra constructor"),
    _c("ctor_utm", "UnaryTermsMonoid.UnaryTermsMonoid",
       "utm.getName() if hasattr(utm, 'getName') else utm.name()",
       "UnaryTermsMonoid constructor"),
    _c("ctor_afms", "AlgebraFromMinimalSets.AlgebraFromMinimalSets",
       "afms.getName()", "AlgebraFromMinimalSets constructor"),
    _c("ctor_awgv", "AlgebraWithGeneratingVector.AlgebraWithGeneratingVector",
       "awgv.getName() if hasattr(awgv, 'getName') else True",
       "AlgebraWithGeneratingVector constructor", **_ALG),
    _c("mpd_get_block_algebras", "MaltsevProductDecomposition.getBlockAlgebras",
       "len(list(decomp.getBlockAlgebras() or []))",
       "getBlockAlgebras after construction"),
    _c("mpd_get_block_algebras_empty", "MaltsevProductDecomposition.getBlockAlgebras",
       "(decomp.setBlockAlgebras([]), len(list(decomp.getBlockAlgebras())))[1]",
       "getBlockAlgebras after setBlockAlgebras([])"),
    _c("mpd_get_quotient_algebra", "MaltsevProductDecomposition.getQuotientAlgebra",
       "_alg_card(decomp.getQuotientAlgebra())",
       "getQuotientAlgebra of N5/Cg(0,1)", **_ALG),
    _c("mpd_get_quotient_after_set", "MaltsevProductDecomposition.getQuotientAlgebra",
       "(decomp.setQuotientAlgebra(c2), _alg_card(decomp.getQuotientAlgebra()))[1]",
       "getQuotientAlgebra after setQuotientAlgebra(C2)", **_ALG),
    _c("bpa_get_constant_term_missing", "BigProductAlgebra.getConstantTerm",
       "bp2.getConstantTerm(g00)",
       "Java NPEs on a non-constant; Python raises ValueError",
       xfail_reason=(
           "Known Java bug: getConstantTerm of a non-constant tuple NPEs on "
           "null constantTerm; Python raises ValueError instead"
       ), **_NONE),
    _c("bpa_get_constant_term_from_list", "BigProductAlgebra.getConstantTerm",
       "[_term_str(bp2.getConstantTerm(c)) for c in list(bp2.getConstants() or [])]",
       "getConstantTerm of each C2^2 constant", **_TERM),
    _c("bpa_get_constant_term_c3", "BigProductAlgebra.getConstantTerm",
       "[_term_str(bp3.getConstantTerm(c)) for c in list(bp3.getConstants() or [])]",
       "getConstantTerm of each C3^2 constant", **_TERM),
    _c("closer_sg_close_parallel_c2", "Closer.sgCloseParallel",
       "_par_close(bp2, [g00, g11])",
       "sgCloseParallel 3-arg on C2^2 diagonal gens", **_LIST),
    _c("closer_sg_close_parallel_all", "Closer.sgCloseParallel",
       "_par_close(bp2, [g00, g01, g11])",
       "sgCloseParallel 3-arg on C2^2 three gens", **_LIST),
    _c("closer_sg_close_parallel_c3", "Closer.sgCloseParallel",
       "_par_close(bp3, [IntArray([0, 0]), IntArray([1, 1])])",
       "sgCloseParallel 3-arg on C3^2 diagonal gens", **_LIST),
    _c("closer_sg_close_parallel_matches_seq", "Closer.sgCloseParallel",
       "_par_close(bp2, [g00, g11]) == _sorted_ias(Closer(bp2, [g00, g11], True).sgClose())",
       "sgCloseParallel universe equals sequential sgClose", **_BOOL),
    # per-class inherited / redeclared GeneralAlgebra surface
    _c("inh_basic_algebra_type", "BasicAlgebra.algebraType",
       "str(c2.algebraType())", "BasicAlgebra algebraType via c2"),
    _c("inh_basic_con_card", "BasicAlgebra.con",
       "int(c2.con().cardinality())", "BasicAlgebra con()", **_LAT),
    _c("inh_basic_sub_card", "BasicAlgebra.sub",
       "int(c2.sub().cardinality())", "BasicAlgebra sub()", **_LAT),
    _c("inh_basic_convert_dvo", "BasicAlgebra.convertToDefaultValueOps",
       "(c2.convertToDefaultValueOps(), True)[1]", "BasicAlgebra convertToDefaultValueOps", skip_string_check=True),
    _c("inh_basic_element_index", "BasicAlgebra.elementIndex",
       "int(c2.elementIndex(1))", "BasicAlgebra elementIndex"),
    _c("inh_basic_get_element", "BasicAlgebra.getElement",
       "int(c2.getElement(0))", "BasicAlgebra getElement"),
    _c("inh_basic_univ_list", "BasicAlgebra.getUniverseList",
       "list(c2.getUniverseList())", "BasicAlgebra getUniverseList", **_LIST),
    _c("inh_basic_univ_order", "BasicAlgebra.getUniverseOrder",
       "c2.getUniverseOrder()", "BasicAlgebra getUniverseOrder", **_NONE),
    _c("inh_basic_reset_con_sub", "BasicAlgebra.resetConAndSub",
       "(c2.resetConAndSub(), int(c2.con().cardinality()))[1]",
       "BasicAlgebra resetConAndSub", **_LAT),
    _c("inh_ga_constant_ops", "GeneralAlgebra.constantOperations",
       "len(list(ga.constantOperations()))", "GeneralAlgebra constantOperations", **_LIST),
    _c("inh_ga_get_description", "GeneralAlgebra.getDescription",
       "ga.getDescription()", "GeneralAlgebra getDescription", **_NONE),
    _c("inh_ga_set_description", "GeneralAlgebra.setDescription",
       "(ga.setDescription('d'), ga.getDescription())[1]", "GeneralAlgebra setDescription"),
    _c("inh_ga_get_monitor", "GeneralAlgebra.getMonitor",
       "ga.getMonitor()", "GeneralAlgebra getMonitor", **_NONE),
    _c("inh_ga_set_monitor", "GeneralAlgebra.setMonitor",
       "ga.setMonitor(None)", "GeneralAlgebra setMonitor null", skip_string_check=True),
    _c("inh_ga_ops_map", "GeneralAlgebra.getOperationsMap",
       "sorted(str(k) for k in (ga.getOperationsMap().keySet() if hasattr(ga.getOperationsMap(), 'keySet') else ga.getOperationsMap()))",
       "GeneralAlgebra getOperationsMap", **_LIST),
    _c("inh_ga_input_size", "GeneralAlgebra.inputSize",
       "int(ga.inputSize())", "GeneralAlgebra inputSize"),
    _c("inh_ga_is_idempotent", "GeneralAlgebra.isIdempotent",
       "ga.isIdempotent()", "GeneralAlgebra isIdempotent", **_BOOL),
    _c("inh_ga_is_similar", "GeneralAlgebra.isSimilarTo",
       "ga.isSimilarTo(ga)", "GeneralAlgebra isSimilarTo self", **_BOOL),
    _c("inh_ga_is_total", "GeneralAlgebra.isTotal",
       "ga.isTotal()", "GeneralAlgebra isTotal", **_BOOL),
    _c("inh_ga_is_unary", "GeneralAlgebra.isUnary",
       "ga.isUnary()", "GeneralAlgebra isUnary", **_BOOL),
    _c("inh_ga_iterator", "GeneralAlgebra.iterator",
       "list(ga.iterator())", "GeneralAlgebra iterator", **_LIST),
    _c("inh_ga_make_tables", "GeneralAlgebra.makeOperationTables",
       "ga.makeOperationTables()", "GeneralAlgebra makeOperationTables", skip_string_check=True),
    _c("inh_ga_monitoring", "GeneralAlgebra.monitoring",
       "ga.monitoring()", "GeneralAlgebra monitoring", **_BOOL),
    _c("inh_ga_reset", "GeneralAlgebra.resetConAndSub",
       "(ga.resetConAndSub(), int(ga.con().cardinality()))[1]", "GeneralAlgebra resetConAndSub", **_LAT),
    _c("inh_ga_sim_type", "GeneralAlgebra.similarityType",
       "ga.similarityType()", "GeneralAlgebra similarityType"),
    _c("inh_ga_univ", "GeneralAlgebra.universe",
       "sorted(list(ga.universe()))", "GeneralAlgebra universe", **_LIST),
    _c("inh_ga_update_st", "GeneralAlgebra.updateSimilarityType",
       "ga.updateSimilarityType()", "GeneralAlgebra updateSimilarityType", skip_string_check=True),
    _c("inh_mpd_get_cong", "MaltsevProductDecomposition.getCongruence",
       "decomp.getCongruence().numberOfBlocks()", "MaltsevProductDecomposition getCongruence"),
    _c("inh_mp_con", "MatrixPowerAlgebra.con",
       "int(mp.con().cardinality())", "MatrixPowerAlgebra con()", **_LAT),
    _c("inh_mp_sub", "MatrixPowerAlgebra.sub",
       "int(mp.sub().cardinality())", "MatrixPowerAlgebra sub()", **_LAT),
    _c("inh_mp_elem_idx", "MatrixPowerAlgebra.elementIndex",
       "int(mp.elementIndex(0))", "MatrixPowerAlgebra elementIndex"),
    _c("inh_mp_univ_list", "MatrixPowerAlgebra.getUniverseList",
       "list(mp.getUniverseList())", "MatrixPowerAlgebra getUniverseList", **_LIST),
    _c("inh_mp_univ_order", "MatrixPowerAlgebra.getUniverseOrder",
       "mp.getUniverseOrder()", "MatrixPowerAlgebra getUniverseOrder", **_NONE),
    _c("inh_pol_con", "PolinLikeAlgebra.con",
       "int(pol.con().cardinality())", "PolinLikeAlgebra con()", **_LAT),
    _c("inh_pol_univ_order", "PolinLikeAlgebra.getUniverseOrder",
       "pol.getUniverseOrder()", "PolinLikeAlgebra getUniverseOrder", **_NONE),
    _c("inh_pol_sub", "PolinLikeAlgebra.sub",
       "int(pol.sub().cardinality())", "PolinLikeAlgebra sub()", **_LAT),
    _c("inh_q_univ_order", "QuotientAlgebra.getUniverseOrder",
       "q.getUniverseOrder()", "QuotientAlgebra getUniverseOrder", **_NONE),
    _c("inh_q_make_tables", "QuotientAlgebra.makeOperationTables",
       "(q.makeOperationTables(), q.cardinality())[1]", "QuotientAlgebra makeOperationTables"),
    _c("inh_red_con", "ReductAlgebra.con",
       "int(ReductAlgebra('R', c2, []).con().cardinality())", "ReductAlgebra con()", **_LAT),
    _c("inh_red_convert", "ReductAlgebra.convertToDefaultValueOps",
       "ReductAlgebra('R', c2, []).convertToDefaultValueOps()",
       "ReductAlgebra convertToDefaultValueOps rejects non-basic algebras"),
    _c("inh_red_elem_idx", "ReductAlgebra.elementIndex",
       "int(ReductAlgebra('R', c2, []).elementIndex(0))", "ReductAlgebra elementIndex"),
    _c("inh_red_get_elem", "ReductAlgebra.getElement",
       "int(ReductAlgebra('R', c2, []).getElement(1))", "ReductAlgebra getElement"),
    _c("inh_red_univ_order", "ReductAlgebra.getUniverseOrder",
       "ReductAlgebra('R', c2, []).getUniverseOrder()", "ReductAlgebra getUniverseOrder", **_NONE),
    _c("inh_red_make_tables", "ReductAlgebra.makeOperationTables",
       "(ReductAlgebra('R', c2, []).makeOperationTables(), 1)[1]",
       "ReductAlgebra makeOperationTables"),
    _c("inh_red_sub", "ReductAlgebra.sub",
       "int(ReductAlgebra('R', c2, []).sub().cardinality())", "ReductAlgebra sub()", **_LAT),
    _c("inh_sp_get_elem_term", "SubProductAlgebra.getElementFromTerm",
       "sp.getElementFromTerm(sp.getTerm(sp.getElement(0)))", "SubProductAlgebra getElementFromTerm",
       xfail_reason=(
           "Known Java bug: SubProductAlgebra(name, product, gens) passes "
           "findTerms=false, so terms stays null. getTerm returns null, but "
           "getElementFromTerm reads terms.length and throws NullPointerException. "
           "Python returns null, matching getTerm, instead of copying that NPE."
       )),
    _c("inh_sp_get_term", "SubProductAlgebra.getTerm",
       "str(sp.getTerm(sp.getElement(0))).replace(' ', '')", "SubProductAlgebra getTerm", **_TERM),
    _c("inh_sp_univ_order", "SubProductAlgebra.getUniverseOrder",
       "sp.getUniverseOrder()", "SubProductAlgebra getUniverseOrder", **_NONE),
    _c("inh_sp_var_map", "SubProductAlgebra.getVariableToGeneratorMap",
       "len(list(sp.getVariableToGeneratorMap().keySet()) if hasattr(sp.getVariableToGeneratorMap(), 'keySet') else sp.getVariableToGeneratorMap())",
       "SubProductAlgebra getVariableToGeneratorMap"),
    _c("inh_sp_vars", "SubProductAlgebra.getVariables",
       "sp.getVariables()", "SubProductAlgebra getVariables", **_LIST),
    _c("inh_sp_make_tables", "SubProductAlgebra.makeOperationTables",
       "(sp.makeOperationTables(), sp.cardinality())[1]", "SubProductAlgebra makeOperationTables"),
    _c("inh_subalg_univ_order", "Subalgebra.getUniverseOrder",
       "s0.getUniverseOrder()", "Subalgebra getUniverseOrder", **_NONE),
    _c("inh_subalg_make_tables", "Subalgebra.makeOperationTables",
       "(s0.makeOperationTables(), s0.cardinality())[1]", "Subalgebra makeOperationTables"),
    _c("inh_utm_univ_order", "UnaryTermsMonoid.getUniverseOrder",
       "utm.getUniverseOrder()", "UnaryTermsMonoid getUniverseOrder", **_NONE),
    _c("inh_utm_make_tables", "UnaryTermsMonoid.makeOperationTables",
       "(utm.makeOperationTables(), utm.cardinality())[1]", "UnaryTermsMonoid makeOperationTables"),
]
