"""Parity cases for wrapped org.uacalc.alg.conlat methods/constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.alg.conlat import (
    BasicBinaryRelation, BasicPartition, CentralityData, Subtrace, TypeFinder,
)
from org.uacalc.io import AlgebraIO
from org.uacalc.util import IntArray
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
n5 = AlgebraIO.readAlgebraFile("resources/algebras/n5.ua")
m3 = AlgebraIO.readAlgebraFile("resources/algebras/m3.ua")
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
ident = BasicBinaryRelation.identity(3)
zero3 = BasicPartition.zero(3)
one3 = BasicPartition.one(3)
cd = CentralityData(ident, ident, zero3)
st = Subtrace(0, 1, True)
tf_c2 = TypeFinder(c2)
rel = BasicBinaryRelation(3)
rel.add(0, 1)
rel.add(0, 2)
rel_sym = BasicBinaryRelation(3)
rel_sym.add(0, 1)
rel_sym.add(1, 0)
z_c2 = c2.con().zero()
o_c2 = c2.con().one()
z_n5 = n5.con().zero()
o_n5 = n5.con().one()
z_m3 = m3.con().zero()
o_m3 = m3.con().one()

def _ia(obj):
    if obj is None:
        return None
    try:
        return [int(x) for x in list(obj)]
    except TypeError:
        pass
    for attr in ("getArray", "get_array", "toArray", "to_array"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            return [int(x) for x in fn()]
    return str(obj)

def _par(p):
    if p is None:
        return None
    fn = getattr(p, "toArray", None) or getattr(p, "to_array", None)
    if callable(fn):
        return [int(x) for x in list(fn())]
    return str(p)

def _fail(obj):
    if obj is None:
        return None
    fn = getattr(obj, "toString", None)
    if callable(fn):
        return str(fn())
    return str(obj)

def _rel(p):
    if p is None:
        return None
    fn = getattr(p, "toBinaryRelation", None) or getattr(p, "to_binary_relation", None)
    if callable(fn):
        return fn()
    return p
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List toString vs Python list.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")
_REL = dict(skip_string_check=True, notes="BinaryRelation toString vs Python.")


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
    _c("ctor_centrality_data", "CentralityData.CentralityData",
       "cd.getDelta().numberOfBlocks()", "CentralityData constructor"),
    _c("ctor_subtrace", "Subtrace.Subtrace",
       "[int(st.first()), int(st.second()), bool(st.hasInvolution())]",
       "Subtrace constructor", **_LIST),
    _c("ctor_typefinder", "TypeFinder.TypeFinder",
       "sorted(int(x) for x in list(tf_c2.findTypeSet()))",
       "TypeFinder constructor findTypeSet of C2", **_LIST),
    _c("bbr_add_pairs", "BasicBinaryRelation.add",
       "sorted(str(p) for p in list(rel.getPairs()))",
       "add(0,1) then add(0,2)", **_LIST),
    _c("bbr_add_then_size", "BasicBinaryRelation.add",
       "(lambda r: (r.add(0, 1), len(list(r.getPairs())))[1])(BasicBinaryRelation(2))",
       "add then pair-count on a 2-element relation"),
    _c("bbr_is_symmetric_ident", "BasicBinaryRelation.isSymmetric",
       "ident.isSymmetric()", "identity is symmetric", **_BOOL),
    _c("bbr_is_symmetric_not", "BasicBinaryRelation.isSymmetric",
       "rel.isSymmetric()", "one-way pairs are not symmetric", **_BOOL),
    _c("bbr_is_symmetric_yes", "BasicBinaryRelation.isSymmetric",
       "rel_sym.isSymmetric()", "two-way pair is symmetric", **_BOOL),
    _c("cd_get_left", "CentralityData.getLeft",
       "cd.getLeft().toString()", "getLeft of identity relation", **_REL),
    _c("cd_get_right", "CentralityData.getRight",
       "cd.getRight().toString()", "getRight of identity relation", **_REL),
    _c("cd_get_left_n5", "CentralityData.getLeft",
       "CentralityData(_rel(z_n5), _rel(z_n5), z_n5).getLeft().universeSize()",
       "getLeft universeSize on an N5-based CentralityData"),
    _c("cd_set_centrality_failure", "CentralityData.setCentralityFailure",
       "(cd.setCentralityFailure(None), cd.getCentralityFailure())[1]",
       "setCentralityFailure(None)", **_NONE),
    _c("cd_set_weak_failure", "CentralityData.setWeakCentralityFailure",
       "(cd.setWeakCentralityFailure(None), cd.getWeakCentralityFailure())[1]",
       "setWeakCentralityFailure(None)", **_NONE),
    _c("cd_set_strong_failure", "CentralityData.setStrongRectangularityFailure",
       "(cd.setStrongRectangularityFailure(None), cd.getStrongRectangularityFailure())[1]",
       "setStrongRectangularityFailure(None)", **_NONE),
    _c("cd_get_weak_failure_default", "CentralityData.getWeakCentralityFailure",
       "CentralityData(ident, ident, zero3).getWeakCentralityFailure()",
       "getWeakCentralityFailure default is null", **_NONE),
    _c("cd_get_strong_failure_default", "CentralityData.getStrongRectangularityFailure",
       "CentralityData(ident, ident, zero3).getStrongRectangularityFailure()",
       "getStrongRectangularityFailure default is null", **_NONE),
    _c("cl_centrality_failure_c2", "CongruenceLattice.centralityFailure",
       "_fail(c2.con().centralityFailure(_rel(z_c2), _rel(o_c2), o_c2))",
       "centralityFailure(zero, one, one) on C2", **_NONE),
    _c("cl_centrality_failure_n5", "CongruenceLattice.centralityFailure",
       "_fail(n5.con().centralityFailure(_rel(z_n5), _rel(o_n5), o_n5))",
       "centralityFailure(zero, one, one) on N5", **_NONE),
    _c("cl_weak_centrality_failure_c2", "CongruenceLattice.weakCentralityFailure",
       "_fail(c2.con().weakCentralityFailure(_rel(z_c2), _rel(o_c2), o_c2))",
       "weakCentralityFailure(zero, one, one) on C2", **_NONE),
    _c("cl_weak_centrality_failure_n5", "CongruenceLattice.weakCentralityFailure",
       "_fail(n5.con().weakCentralityFailure(_rel(z_n5), _rel(o_n5), o_n5))",
       "weakCentralityFailure(zero, one, one) on N5", **_NONE),
    _c("cl_strong_rect_failure_c2", "CongruenceLattice.strongRectangularityFailure",
       "_fail(c2.con().strongRectangularityFailure(_rel(z_c2), _rel(o_c2), o_c2))",
       "strongRectangularityFailure(zero, one, one) on C2", **_NONE),
    _c("cl_strong_rect_failure_m3", "CongruenceLattice.strongRectangularityFailure",
       "_fail(m3.con().strongRectangularityFailure(_rel(z_m3), _rel(o_m3), o_m3))",
       "strongRectangularityFailure(zero, one, one) on M3", **_NONE),
    _c("cl_strong_rect_commutator_c2", "CongruenceLattice.strongRectangularityCommutator",
       "_par(c2.con().strongRectangularityCommutator(_rel(z_c2), _rel(o_c2)))",
       "strongRectangularityCommutator(zero, one) on C2", **_LIST),
    _c("cl_strong_rect_commutator_n5", "CongruenceLattice.strongRectangularityCommutator",
       "_par(n5.con().strongRectangularityCommutator(_rel(z_n5), _rel(o_n5)))",
       "strongRectangularityCommutator(zero, one) on N5", **_LIST),
    _c("cl_strong_rect_commutator_m3", "CongruenceLattice.strongRectangularityCommutator",
       "_par(m3.con().strongRectangularityCommutator(_rel(z_m3), _rel(o_m3)))",
       "strongRectangularityCommutator(zero, one) on M3", **_LIST),
    _c("inh_bbr_compose", "BasicBinaryRelation.compose",
       "rel.compose(rel_sym).toString()", "BasicBinaryRelation compose", **_REL),
    _c("inh_bbr_pairs", "BasicBinaryRelation.getPairs",
       "len(list(rel.getPairs()))", "BasicBinaryRelation getPairs"),
    _c("inh_bbr_is_related", "BasicBinaryRelation.isRelated",
       "rel.isRelated(0, 1)", "BasicBinaryRelation isRelated", **_BOOL),
    _c("inh_bbr_iter", "BasicBinaryRelation.iterator",
       "len(list(rel.iterator()))", "BasicBinaryRelation iterator"),
    _c("inh_bbr_univ", "BasicBinaryRelation.universeSize",
       "int(rel.universeSize())", "BasicBinaryRelation universeSize"),
    _c("inh_bp_block_idx", "BasicPartition.blockIndex",
       "int(zero3.blockIndex(0))", "BasicPartition blockIndex"),
    _c("inh_bp_compose", "BasicPartition.compose",
       "(lambda p1, p2: p1.compose(p2).numberOfBlocks())(BasicPartition('|0 1|2|'), BasicPartition('|0|1 2|'))",
       "BasicPartition compose"),
    _c("inh_bp_blocks", "BasicPartition.getBlocks",
       "[_ia(b) for b in list(zero3.getBlocks())]", "BasicPartition getBlocks", **_LIST),
    _c("inh_bp_pairs", "BasicPartition.getPairs",
       "len(list(zero3.getPairs()))", "BasicPartition getPairs"),
    _c("inh_bp_init_lex", "BasicPartition.isInitialLexRepresentative",
       "zero3.isInitialLexRepresentative()", "BasicPartition isInitialLexRepresentative", **_BOOL),
    _c("inh_bp_is_related", "BasicPartition.isRelated",
       "BasicPartition('|0 1|2|').isRelated(0, 1)", "BasicPartition isRelated", **_BOOL),
    _c("inh_bp_is_rep", "BasicPartition.isRepresentative",
       "zero3.isRepresentative(0)", "BasicPartition isRepresentative", **_BOOL),
    _c("inh_bp_is_uniform", "BasicPartition.isUniform",
       "zero3.isUniform()", "BasicPartition isUniform", **_BOOL),
    _c("inh_bp_is_zero", "BasicPartition.isZero",
       "zero3.isZero()", "BasicPartition isZero", **_BOOL),
    _c("inh_bp_join", "BasicPartition.join",
       "(lambda p1, p2: p1.join(p2).numberOfBlocks())(BasicPartition('|0 1|2|'), BasicPartition('|0|1 2|'))",
       "BasicPartition join"),
    _c("inh_bp_join_blocks", "BasicPartition.joinBlocks",
       "BasicPartition('|0 1|2|').joinBlocks(0, 2).numberOfBlocks()", "BasicPartition joinBlocks"),
    _c("inh_bp_meet", "BasicPartition.meet",
       "(lambda p1, p2: p1.meet(p2).numberOfBlocks())(BasicPartition('|0 1|2|'), BasicPartition('|0|1 2|'))",
       "BasicPartition meet"),
    _c("inh_bp_nblocks", "BasicPartition.numberOfBlocks",
       "int(zero3.numberOfBlocks())", "BasicPartition numberOfBlocks"),
    _c("inh_bp_rep", "BasicPartition.representative",
       "int(BasicPartition('|0 1|2|').representative(1))", "BasicPartition representative"),
    _c("inh_bp_reps", "BasicPartition.representatives",
       "list(one3.representatives())", "BasicPartition representatives", **_LIST),
    _c("inh_bp_tostr", "BasicPartition.toString",
       "zero3.toString()", "BasicPartition toString", skip_string_check=True),
    _c("inh_st_type", "Subtrace.type", "int(st.type())", "Subtrace type"),
]
