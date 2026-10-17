"""Golden parity cases for leftover org.uacalc.alg.conlat types."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.alg.conlat import (
    BasicBinaryRelation, BasicPartition, BinaryRelation, CentralityData,
    Polymorphisms, Subtrace, TypeFinder,
)
from org.uacalc.io import AlgebraIO
from org.uacalc.util import IntArray
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
m3 = AlgebraIO.readAlgebraFile("resources/algebras/m3.ua")
n5 = AlgebraIO.readAlgebraFile("resources/algebras/n5.ua")
tf_c2 = TypeFinder(c2)
tf_c3 = TypeFinder(c3)
tf_lat2 = TypeFinder(lat2)
tf_m3 = TypeFinder(m3)
tf_n5 = TypeFinder(n5)
st = Subtrace(0, 1, True)
st_t = Subtrace(1, 2, False, 3)
rel = BasicBinaryRelation(3)
rel.add(0, 1)
rel.add(0, 2)
ident = BasicBinaryRelation.identity(3)
beta_rel = BasicBinaryRelation(3)
beta_rel.add(1, 0)
coll = BasicBinaryRelation([IntArray([0, 1]), IntArray([1, 0])], 3)
zero3 = BasicPartition.zero(3)
cd = CentralityData(ident, ident, zero3)
poly = Polymorphisms(1, [BasicPartition.zero(2)], True, None)
jis_c2 = list(c2.con().joinIrreducibles())

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

def _ias(lst):
    if lst is None:
        return None
    return [_ia(x) for x in list(lst)]

def _st(s):
    if s is None:
        return None
    return [int(s.first()), int(s.second()), int(s.type()), bool(s.hasInvolution()), str(s.toString())]

def _hs():
    try:
        from java.util import HashSet
        return HashSet()
    except ImportError:
        return set()

def _al():
    try:
        from java.util import ArrayList
        return ArrayList()
    except ImportError:
        return []

def _ia_sorted(coll):
    rows = [_ia(x) for x in list(coll)]
    rows.sort()
    return rows

def _next_snap(tf, pair):
    univHS = _hs()
    unordered = _hs()
    univ = _al()
    result = tf.nextPairForSubtrace(pair, univHS, unordered, univ)
    return [_ia(result), _ia_sorted(univHS), _ia_sorted(unordered), [_ia(x) for x in list(univ)]]
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List/Set toString vs Python list.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")

TEST_CASES = [
    TestCaseSpec(
        id="st_ctor3_str",
        method="Subtrace.toString",
        setup=_SETUP,
        call="st.toString()",
        description="Subtrace(0,1,True) toString",
    ),
    TestCaseSpec(
        id="st_ctor4_str",
        method="Subtrace.toString",
        setup=_SETUP,
        call="st_t.toString()",
        description="Subtrace(1,2,False,3) toString",
    ),
    TestCaseSpec(
        id="st_brief",
        method="Subtrace.toString",
        setup=_SETUP,
        call="st.toString(True)",
        description="Subtrace brief toString",
    ),
    TestCaseSpec(
        id="st_first_second",
        method="Subtrace.first",
        setup=_SETUP,
        call="[st.first(), st.second(), st.type(), st.hasInvolution()]",
        description="Subtrace first/second/type/hasInvolution",
        **_LIST
    ),
    TestCaseSpec(
        id="st_set_type",
        method="Subtrace.setType",
        setup=_SETUP,
        call="(st.setType(4), st.type())[1]",
        description="setType then type()",
    ),
    TestCaseSpec(
        id="st_set_get_universe",
        method="Subtrace.getSubtraceUniverse",
        setup=_SETUP,
        call="(st.setSubtraceUniverse([IntArray([0,1]), IntArray([1,0])]), _ias(st.getSubtraceUniverse()))[1]",
        description="set/get subtrace universe",
        **_LIST
    ),
    TestCaseSpec(
        id="st_set_get_matrix",
        method="Subtrace.getMatrixUniverse",
        setup=_SETUP,
        call="(st.setMatrixUniverse([IntArray([0,0,1,1])]), _ias(st.getMatrixUniverse()))[1]",
        description="set/get matrix universe",
        **_LIST
    ),
    TestCaseSpec(
        id="bbr_str",
        method="BasicBinaryRelation.toString",
        setup=_SETUP,
        call="rel.toString()",
        description="BasicBinaryRelation toString",
    ),
    TestCaseSpec(
        id="bbr_universe_size",
        method="BinaryRelation.universeSize",
        setup=_SETUP,
        call="rel.universeSize()",
        description="universeSize 3",
    ),
    TestCaseSpec(
        id="bbr_is_related",
        method="BinaryRelation.isRelated",
        setup=_SETUP,
        call="[rel.isRelated(0,1), rel.isRelated(1,0)]",
        description="isRelated true/false",
        **_LIST
    ),
    TestCaseSpec(
        id="bbr_get_pairs",
        method="BinaryRelation.getPairs",
        setup=_SETUP,
        call="_ias(rel.getPairs())",
        description="getPairs as int lists",
        **_LIST
    ),
    TestCaseSpec(
        id="bbr_compose",
        method="BinaryRelation.compose",
        setup=_SETUP,
        call="rel.compose(beta_rel).toString()",
        description="compose with (1,0)",
    ),
    TestCaseSpec(
        id="bbr_identity",
        method="BasicBinaryRelation.identity",
        setup=_SETUP,
        call="ident.toString()",
        description="identity(3) toString",
    ),
    TestCaseSpec(
        id="bbr_reflexive_symmetric",
        method="BasicBinaryRelation.isReflexive",
        setup=_SETUP,
        call="[ident.isReflexive(), ident.isSymmetric(), rel.isReflexive(), rel.isSymmetric()]",
        description="isReflexive/isSymmetric identity vs rel",
        **_LIST
    ),
    TestCaseSpec(
        id="bbr_compare_to",
        method="BasicBinaryRelation.compareTo",
        setup=_SETUP,
        call="rel.compareTo(ident)",
        description="compareTo by pair count",
    ),
    TestCaseSpec(
        id="bbr_from_collection",
        method="BasicBinaryRelation.BasicBinaryRelation",
        setup=_SETUP,
        call="coll.toString()",
        description="constructor from collection",
    ),
    TestCaseSpec(
        id="cd_accessors",
        method="CentralityData.getDelta",
        setup=_SETUP,
        call="[cd.getLeft().toString(), cd.getRight().toString(), str(cd.getDelta())]",
        description="getLeft/getRight/getDelta",
        **_LIST
    ),
    TestCaseSpec(
        id="cd_compare_to",
        method="CentralityData.compareTo",
        setup=_SETUP,
        call="cd.compareTo(cd)",
        description="compareTo self is 0",
    ),
    TestCaseSpec(
        id="cd_to_string",
        method="CentralityData.toString",
        setup=_SETUP,
        call="cd.toString()",
        description="CentralityData toString with null failures",
    ),
    TestCaseSpec(
        id="cd_failures",
        method="CentralityData.getCentralityFailure",
        setup=_SETUP,
        call="(cd.setCentralityFailure(None), cd.setWeakCentralityFailure(None), cd.setStrongRectangularityFailure(None), [cd.getCentralityFailure(), cd.getWeakCentralityFailure(), cd.getStrongRectangularityFailure()])[3]",
        description="failure getters after null setters",
        **_LIST
    ),
    TestCaseSpec(
        id="poly_ctor",
        method="Polymorphisms.Polymorphisms",
        setup=_SETUP,
        call="poly.get_arity() if hasattr(poly, 'get_arity') else 1",
        description="Polymorphisms constructor succeeds",
    ),
    TestCaseSpec(
        id="poly_empty",
        method="Polymorphisms.Polymorphisms",
        setup=_SETUP,
        call="Polymorphisms(1, [], True, None)",
        description="empty partition list is IndexOutOfBoundsException",
        expected_exception="IndexOutOfBoundsException",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="tf_c2_typeset",
        method="TypeFinder.findTypeSet",
        setup=_SETUP,
        call="sorted(list(tf_c2.findTypeSet()))",
        description="cyclic2 TCT type set",
        **_LIST
    ),
    TestCaseSpec(
        id="tf_c3_typeset",
        method="TypeFinder.findTypeSet",
        setup=_SETUP,
        call="sorted(list(tf_c3.findTypeSet()))",
        description="cyclic3 TCT type set",
        **_LIST
    ),
    TestCaseSpec(
        id="tf_lat2_typeset",
        method="TypeFinder.findTypeSet",
        setup=_SETUP,
        call="sorted(list(tf_lat2.findTypeSet()))",
        description="lat2 TCT type set",
        **_LIST
    ),
    TestCaseSpec(
        id="tf_m3_typeset",
        method="TypeFinder.findTypeSet",
        setup=_SETUP,
        call="sorted(list(tf_m3.findTypeSet()))",
        description="m3 TCT type set",
        **_LIST
    ),
    TestCaseSpec(
        id="tf_n5_typeset",
        method="TypeFinder.findTypeSet",
        setup=_SETUP,
        call="sorted(list(tf_n5.findTypeSet()))",
        description="n5 TCT type set",
        **_LIST
    ),
    TestCaseSpec(
        id="tf_c2_subtrace",
        method="TypeFinder.findSubtrace",
        setup=_SETUP,
        call="_st(tf_c2.findSubtrace(jis_c2[0]))",
        description="cyclic2 findSubtrace of unique JI",
        **_LIST
    ),
    TestCaseSpec(
        id="tf_c2_find_type",
        method="TypeFinder.findType",
        setup=_SETUP,
        call="tf_c2.findType(jis_c2[0])",
        description="cyclic2 findType of unique JI",
    ),
    TestCaseSpec(
        id="tf_c2_is_subtrace",
        method="TypeFinder.isSubtrace",
        setup=_SETUP,
        call="tf_c2.isSubtrace(c2.con().generatingPair(jis_c2[0]), jis_c2[0])",
        description="cyclic2 generating pair is a subtrace",
        **_BOOL
    ),
    TestCaseSpec(
        id="tf_init_alpha",
        method="TypeFinder.init",
        setup=_SETUP,
        call="(TypeFinder(c2, c2.con().zero()).init(c2.con().zero()), sorted(list(TypeFinder(c2, c2.con().zero()).findTypeSet())))[1]",
        description="TypeFinder(alg, alpha) then findTypeSet",
        **_LIST
    ),
    TestCaseSpec(
        id="tf_next_pair_c2",
        method="TypeFinder.nextPairForSubtrace",
        setup=_SETUP,
        call="_next_snap(tf_c2, IntArray([0, 1]))",
        description="nextPairForSubtrace mutates univ/univHS on C2 from (0,1)",
        **_LIST
    ),
    TestCaseSpec(
        id="tf_next_pair_c3",
        method="TypeFinder.nextPairForSubtrace",
        setup=_SETUP,
        call="_next_snap(tf_c3, IntArray([0, 1]))",
        description="nextPairForSubtrace mutates univ/univHS on C3 from (0,1)",
        **_LIST
    ),
    TestCaseSpec(
        id="tf_next_pair_lat2",
        method="TypeFinder.nextPairForSubtrace",
        setup=_SETUP,
        call="_next_snap(tf_lat2, IntArray([0, 1]))",
        description="nextPairForSubtrace mutates univ/univHS on lat2 from (0,1)",
        **_LIST
    ),
    TestCaseSpec(
        id="tf_next_pair_npe",
        method="TypeFinder.nextPairForSubtrace",
        setup=_SETUP,
        call="tf_c2.nextPairForSubtrace(IntArray([0, 1]), None, None, None)",
        description="nextPairForSubtrace NPE when the sets/list are null",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="cl_type_set_c2",
        method="CongruenceLattice.typeSet",
        setup=_SETUP,
        call="sorted(int(x) for x in list(c2.con().typeSet()))",
        description="Con(C2) TCT type set",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_type_set_lat2",
        method="CongruenceLattice.typeSet",
        setup=_SETUP,
        call="sorted(int(x) for x in list(lat2.con().typeSet()))",
        description="Con(lat2) TCT type set",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_type_set_c3",
        method="CongruenceLattice.typeSet",
        setup=_SETUP,
        call="sorted(int(x) for x in list(c3.con().typeSet()))",
        description="Con(C3) TCT type set",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_type_ji_c2",
        method="CongruenceLattice.typeJI",
        setup=_SETUP,
        call="c2.con().typeJI(jis_c2[0], None)",
        description="typeJI of the unique JI in Con(C2)",
    ),
    TestCaseSpec(
        id="cl_type_c2",
        method="CongruenceLattice.type",
        setup=_SETUP,
        call="c2.con().type(jis_c2[0])",
        description="type() of the unique JI in Con(C2)",
    ),
    TestCaseSpec(
        id="cl_get_algebra_c2",
        method="CongruenceLattice.getAlgebra",
        setup=_SETUP,
        call="c2.con().getAlgebra().cardinality()",
        description="getAlgebra round-trips the originating algebra",
    ),
    TestCaseSpec(
        id="cl_get_type_finder_c2",
        method="CongruenceLattice.getTypeFinder",
        setup=_SETUP,
        call="sorted(list(c2.con().getTypeFinder().findTypeSet()))",
        description="getTypeFinder().findTypeSet matches TypeFinder(c2)",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_subtrace_c2",
        method="CongruenceLattice.subtrace",
        setup=_SETUP,
        call="_st(c2.con().subtrace(jis_c2[0]))",
        description="subtrace of the unique JI in Con(C2)",
        **_LIST
    ),
]
