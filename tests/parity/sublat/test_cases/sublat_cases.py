"""Test case specifications for org.uacalc.alg.sublat BasicSet / SubalgebraLattice."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.alg.sublat import BasicSet, SubalgebraLattice
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import ProductAlgebra, QuotientAlgebra
empty = BasicSet.EMPTY_SET
s01 = BasicSet([0, 1])
s02 = BasicSet([0, 2])
s13 = BasicSet([1, 3])
s12 = BasicSet([1, 2])
s012 = BasicSet([0, 1, 2])
s123 = BasicSet([1, 2, 3])
c2 = AlgebraIO.readAlgebraFile('resources/algebras/cyclic2.ua')
lat2 = AlgebraIO.readAlgebraFile('resources/algebras/lat2.ua')
m3 = AlgebraIO.readAlgebraFile('resources/algebras/m3.ua')
n5 = AlgebraIO.readAlgebraFile('resources/algebras/n5.ua')
c3 = AlgebraIO.readAlgebraFile('resources/algebras/cyclic3.ua')
ba2 = AlgebraIO.readAlgebraFile('resources/algebras/ba2.ua')
sl = SubalgebraLattice(c2)
sl2 = SubalgebraLattice(lat2)
slm = SubalgebraLattice(m3)
def _cls(o):
    n = type(o).__name__.split('.')[-1]
    if n.startswith('Py') and len(n) > 2:
        n = n[2:]
    return n
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List/Set toString vs Python list.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")
_LAT = dict(skip_string_check=True, notes="Java lattice toString is Class@hex; values compared.")
_ALG = dict(skip_string_check=True, notes="Java Algebra toString is Class@hex; values compared.")
_SET = dict(skip_string_check=True, notes="BasicSet identity toString vs Python; elements compared.")

_CON_XFAIL = (
    "SubalgebraLattice.con() builds Con of the lattice via BasicLattice; "
    "uacalc_lib BasicLattice from a BasicSet universe cannot yet extract i32 "
    "join/meet tables (get_element is i32-ops only)."
)
_SUB_XFAIL = (
    "SubalgebraLattice.sub() builds Sub of the lattice via BasicLattice; "
    "uacalc_lib BasicLattice from a BasicSet universe cannot yet extract i32 "
    "join/meet tables (get_element is i32-ops only)."
)
_DIAGRAM_XFAIL = (
    "getDiagram() returns a latdraw Diagram; Swing/latdraw GUI is out of scope."
)
_UNION_DUP_XFAIL = (
    "Java BasicSet.normalize only sorts, so union can keep duplicate values "
    "([5, 5, 6]); uacalc_lib BasicSet::new dedupes. Owner: keep library sets unique."
)

TEST_CASES = [
    TestCaseSpec(
        id="bs_empty_str",
        method="BasicSet.EMPTY_SET",
        setup=_SETUP,
        call="empty",
        description="EMPTY_SET string",
    ),
    TestCaseSpec(
        id="bs_ctor_sort",
        method="BasicSet.BasicSet",
        setup=_SETUP,
        call="s01",
        description="BasicSet([0, 1])",
    ),
    TestCaseSpec(
        id="bs_ctor_unsorted",
        method="BasicSet.BasicSet",
        setup=_SETUP,
        call="BasicSet([2, 0, 1])",
        description="constructor sorts",
    ),
    TestCaseSpec(
        id="bs_universe_size",
        method="BasicSet.universeSize",
        setup=_SETUP,
        call="s01.universeSize()",
        description="universeSize of {0,1}",
    ),
    TestCaseSpec(
        id="bs_get",
        method="BasicSet.get",
        setup=_SETUP,
        call="s01.get(1)",
        description="get(1)",
    ),
    TestCaseSpec(
        id="bs_to_array",
        method="BasicSet.toArray",
        setup=_SETUP,
        call="list(s01.toArray())",
        description="toArray",
        **_LIST
    ),
    TestCaseSpec(
        id="bs_get_array",
        method="BasicSet.getArray",
        setup=_SETUP,
        call="list(s01.getArray())",
        description="getArray",
        **_LIST
    ),
    TestCaseSpec(
        id="bs_to_string",
        method="BasicSet.toString",
        setup=_SETUP,
        call="s01.toString() if hasattr(s01, 'toString') else str(s01)",
        description="toString [0, 1]",
    ),
    TestCaseSpec(
        id="bs_str",
        method="BasicSet.toString",
        setup=_SETUP,
        call="str(s012)",
        description="str of {0,1,2}",
    ),
    TestCaseSpec(
        id="bs_contains_true",
        method="BasicSet.contains",
        setup=_SETUP,
        call="s01.contains(0)",
        description="contains 0",
        **_BOOL
    ),
    TestCaseSpec(
        id="bs_contains_false",
        method="BasicSet.contains",
        setup=_SETUP,
        call="s01.contains(2)",
        description="contains 2",
        **_BOOL
    ),
    TestCaseSpec(
        id="bs_leq_true",
        method="BasicSet.leq",
        setup=_SETUP,
        call="s01.leq(s012)",
        description="instance leq subset",
        **_BOOL
    ),
    TestCaseSpec(
        id="bs_leq_false",
        method="BasicSet.leq",
        setup=_SETUP,
        call="s012.leq(s01)",
        description="instance leq not subset",
        **_BOOL
    ),
    TestCaseSpec(
        id="bs_leq_static",
        method="BasicSet.leq",
        setup=_SETUP,
        call="BasicSet.leq([0], [0, 1])",
        description="static leq arrays",
        **_BOOL
    ),
    TestCaseSpec(
        id="bs_intersection",
        method="BasicSet.intersection",
        setup=_SETUP,
        call="s012.intersection(s123)",
        description="intersection",
    ),
    TestCaseSpec(
        id="bs_intersection_static",
        method="BasicSet.intersection",
        setup=_SETUP,
        call="BasicSet.intersection(s012, s123)",
        description="static intersection",
    ),
    TestCaseSpec(
        id="bs_difference",
        method="BasicSet.setDifference",
        setup=_SETUP,
        call="s012.setDifference(s12)",
        description="setDifference",
    ),
    TestCaseSpec(
        id="bs_union_index_bug",
        method="BasicSet.union",
        setup=_SETUP,
        call="s02.union(s13)",
        description="Java union uses contains(index); {0,2} u {1,3} drops 1",
    ),
    TestCaseSpec(
        id="bs_union_static",
        method="BasicSet.union",
        setup=_SETUP,
        call="BasicSet.union(BasicSet([0]), BasicSet([1]))",
        description="static union disjoint",
    ),
    TestCaseSpec(
        id="bs_union_keeps_dups",
        method="BasicSet.union",
        setup=_SETUP,
        call="BasicSet([5, 6]).union(BasicSet([5]))",
        description="Java union+normalize keeps sorted duplicates",
        xfail_reason=_UNION_DUP_XFAIL,
    ),
    TestCaseSpec(
        id="bs_compare_to",
        method="BasicSet.compareTo",
        setup=_SETUP,
        call="s01.compareTo(s012)",
        description="compareTo by size then lex",
    ),
    TestCaseSpec(
        id="bs_empty_leq",
        method="BasicSet.leq",
        setup=_SETUP,
        call="empty.leq(s01)",
        description="empty leq any",
        **_BOOL
    ),
    TestCaseSpec(
        id="bs_get_oob",
        method="BasicSet.get",
        setup=_SETUP,
        call="s01.get(9)",
        description="get OOB",
        expected_exception="ArrayIndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="bs_ctor_null",
        method="BasicSet.BasicSet",
        setup=_SETUP,
        call="BasicSet(None)",
        description="BasicSet(null) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="sl_ctor_cyclic2",
        method="SubalgebraLattice.SubalgebraLattice",
        setup=_SETUP,
        call="(_cls(sl), sl.cardinality())",
        description="SubalgebraLattice of cyclic2 constructs",
        **_LAT
    ),
    TestCaseSpec(
        id="sl_card_c2",
        method="SubalgebraLattice.cardinality",
        setup=_SETUP,
        call="sl.cardinality()",
        description="Sub(C2) cardinality 3",
    ),
    TestCaseSpec(
        id="sl_card_lat2",
        method="SubalgebraLattice.cardinality",
        setup=_SETUP,
        call="sl2.cardinality()",
        description="Sub(lat2) cardinality 4",
    ),
    TestCaseSpec(
        id="sl_card_m3",
        method="SubalgebraLattice.cardinality",
        setup=_SETUP,
        call="slm.cardinality()",
        description="Sub(M3) cardinality 20",
    ),
    TestCaseSpec(
        id="sl_card_n5",
        method="SubalgebraLattice.cardinality",
        setup=_SETUP,
        call="SubalgebraLattice(n5).cardinality()",
        description="Sub(N5) cardinality 23",
    ),
    TestCaseSpec(
        id="sl_card_c3",
        method="SubalgebraLattice.cardinality",
        setup=_SETUP,
        call="SubalgebraLattice(c3).cardinality()",
        description="Sub(C3) cardinality 3",
    ),
    TestCaseSpec(
        id="sl_card_ba2",
        method="SubalgebraLattice.cardinality",
        setup=_SETUP,
        call="SubalgebraLattice(ba2).cardinality()",
        description="Sub(BA2) cardinality 1",
    ),
    TestCaseSpec(
        id="sl_zero",
        method="SubalgebraLattice.zero",
        setup=_SETUP,
        call="sl.zero()",
        description="zero subalgebra of C2",
    ),
    TestCaseSpec(
        id="sl_one",
        method="SubalgebraLattice.one",
        setup=_SETUP,
        call="sl.one()",
        description="one subalgebra of C2",
    ),
    TestCaseSpec(
        id="sl_universe",
        method="SubalgebraLattice.universe",
        setup=_SETUP,
        call="sorted(str(x) for x in sl.universe())",
        description="universe strings C2",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_universe_lat2",
        method="SubalgebraLattice.universe",
        setup=_SETUP,
        call="sorted(str(x) for x in sl2.universe())",
        description="universe strings lat2",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_universe_m3",
        method="SubalgebraLattice.universe",
        setup=_SETUP,
        call="sorted(str(x) for x in slm.universe())",
        description="universe strings M3",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_iterator",
        method="SubalgebraLattice.iterator",
        setup=_SETUP,
        call="sorted(str(x) for x in sl.iterator())",
        description="iterator strings",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_sg0",
        method="SubalgebraLattice.sg",
        setup=_SETUP,
        call="sl.sg([0])",
        description="sg([0]) BasicSet",
    ),
    TestCaseSpec(
        id="sl_sg_empty",
        method="SubalgebraLattice.sg",
        setup=_SETUP,
        call="sl.sg([])",
        description="sg([]) is zero",
    ),
    TestCaseSpec(
        id="sl_sg_set_null",
        method="SubalgebraLattice.sg",
        setup=_SETUP,
        call="sl.sg(set([0]))",
        description="sg(Set) is identically null",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_Sg_card",
        method="SubalgebraLattice.Sg",
        setup=_SETUP,
        call="sl.Sg([0]).cardinality()",
        description="Sg([0]) returns Subalgebra of card 1",
        **_ALG
    ),
    TestCaseSpec(
        id="sl_Sg_name",
        method="SubalgebraLattice.Sg",
        setup=_SETUP,
        call="sl.Sg([0]).getName()",
        description="Sg name Subalgebra Of C2",
    ),
    TestCaseSpec(
        id="sl_Sg_from_set",
        method="SubalgebraLattice.Sg",
        setup=_SETUP,
        call="sl.Sg(sl.sg([0])).cardinality()",
        description="Sg(BasicSet)",
        **_ALG
    ),
    TestCaseSpec(
        id="sl_one_generated",
        method="SubalgebraLattice.oneGeneratedSubalgebras",
        setup=_SETUP,
        call="[str(x) for x in sl.oneGeneratedSubalgebras()]",
        description="one-generated subalgebras C2",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_one_generated_m3",
        method="SubalgebraLattice.oneGeneratedSubalgebras",
        setup=_SETUP,
        call="[str(x) for x in slm.oneGeneratedSubalgebras()]",
        description="one-generated subalgebras M3",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_join_irreducibles",
        method="SubalgebraLattice.joinIrreducibles",
        setup=_SETUP,
        call="[str(x) for x in sl.joinIrreducibles()]",
        description="join irreducibles C2",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_join_irreducibles_lat2",
        method="SubalgebraLattice.joinIrreducibles",
        setup=_SETUP,
        call="[str(x) for x in sl2.joinIrreducibles()]",
        description="join irreducibles lat2",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_join_irreducible_true",
        method="SubalgebraLattice.joinIrreducible",
        setup=_SETUP,
        call="sl.joinIrreducible(sl.sg([0]))",
        description="joinIrreducible(sg(0))",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_meet_irreducibles",
        method="SubalgebraLattice.meetIrreducibles",
        setup=_SETUP,
        call="sl.meetIrreducibles()",
        description="meetIrreducibles is null (Java stub)",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_atoms",
        method="SubalgebraLattice.atoms",
        setup=_SETUP,
        call="sl.atoms()",
        description="atoms is null (Java TODO)",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_coatoms",
        method="SubalgebraLattice.coatoms",
        setup=_SETUP,
        call="sl.coatoms()",
        description="coatoms is null (Java TODO)",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_join",
        method="SubalgebraLattice.join",
        setup=_SETUP,
        call="sl.join(sl.zero(), sl.one())",
        description="join zero, one",
    ),
    TestCaseSpec(
        id="sl_join_proper",
        method="SubalgebraLattice.join",
        setup=_SETUP,
        call="sl2.join(sl2.sg([0]), sl2.sg([1]))",
        description="join of two atoms of lat2",
    ),
    TestCaseSpec(
        id="sl_join_list",
        method="SubalgebraLattice.join",
        setup=_SETUP,
        call="sl.join([sl.zero(), sl.one()])",
        description="join(List) is identically null",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_meet",
        method="SubalgebraLattice.meet",
        setup=_SETUP,
        call="sl.meet(sl.zero(), sl.one())",
        description="meet is identically null (Java stub)",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_leq",
        method="SubalgebraLattice.leq",
        setup=_SETUP,
        call="sl.leq(sl.zero(), sl.one())",
        description="leq zero, one",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_filter",
        method="SubalgebraLattice.filter",
        setup=_SETUP,
        call="sorted(str(x) for x in sl.filter(sl.sg([0])))",
        description="filter of sg(0)",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_min_gen_c2",
        method="SubalgebraLattice.findMinimalSizedGeneratingSet",
        setup=_SETUP,
        call="sl.findMinimalSizedGeneratingSet()",
        description="minimal generating set C2",
    ),
    TestCaseSpec(
        id="sl_min_gen_lat2",
        method="SubalgebraLattice.findMinimalSizedGeneratingSet",
        setup=_SETUP,
        call="sl2.findMinimalSizedGeneratingSet()",
        description="minimal generating set lat2",
    ),
    TestCaseSpec(
        id="sl_min_gen_m3",
        method="SubalgebraLattice.findMinimalSizedGeneratingSet",
        setup=_SETUP,
        call="slm.findMinimalSizedGeneratingSet()",
        description="minimal generating set M3",
    ),
    TestCaseSpec(
        id="sl_get_name_prefix",
        method="SubalgebraLattice.getName",
        setup=_SETUP,
        call="sl.getName()[:4]",
        description="getName starts with Sub(",
    ),
    TestCaseSpec(
        id="sl_get_description_prefix",
        method="SubalgebraLattice.getDescription",
        setup=_SETUP,
        call="sl.getDescription()[:22]",
        description="getDescription prefix",
    ),
    TestCaseSpec(
        id="sl_set_description",
        method="SubalgebraLattice.setDescription",
        setup=_SETUP,
        call="(sl.setDescription('hello'), sl.getDescription())[1]",
        description="setDescription round-trip",
    ),
    TestCaseSpec(
        id="sl_set_name",
        method="SubalgebraLattice.setName",
        setup=_SETUP,
        call="sl.setName('x')",
        description="setName is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sl_is_total",
        method="SubalgebraLattice.isTotal",
        setup=_SETUP,
        call="sl.isTotal()",
        description="isTotal true",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_is_unary",
        method="SubalgebraLattice.isUnary",
        setup=_SETUP,
        call="sl.isUnary()",
        description="isUnary false",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_is_idempotent",
        method="SubalgebraLattice.isIdempotent",
        setup=_SETUP,
        call="sl.isIdempotent()",
        description="isIdempotent true",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_operations",
        method="SubalgebraLattice.operations",
        setup=_SETUP,
        call="sl.operations()",
        description="operations is null",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_get_operation",
        method="SubalgebraLattice.getOperation",
        setup=_SETUP,
        call="sl.getOperation(None)",
        description="getOperation is null",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_get_ops_map",
        method="SubalgebraLattice.getOperationsMap",
        setup=_SETUP,
        call="sl.getOperationsMap()",
        description="getOperationsMap is null",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_constant_ops",
        method="SubalgebraLattice.constantOperations",
        setup=_SETUP,
        call="list(sl.constantOperations())",
        description="constantOperations empty",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_universe_found",
        method="SubalgebraLattice.universeFound",
        setup=_SETUP,
        call="(sl.universe(), sl.universeFound())[1]",
        description="universeFound after universe()",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_is_drawable",
        method="SubalgebraLattice.isDrawable",
        setup=_SETUP,
        call="sl.isDrawable()",
        description="isDrawable C2",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_is_smaller_than",
        method="SubalgebraLattice.isSmallerThan",
        setup=_SETUP,
        call="sl.isSmallerThan(10)",
        description="isSmallerThan(10)",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_is_smaller_than_false",
        method="SubalgebraLattice.isSmallerThan",
        setup=_SETUP,
        call="sl.isSmallerThan(2)",
        description="isSmallerThan(2) false",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_input_size",
        method="SubalgebraLattice.inputSize",
        setup=_SETUP,
        call="sl.inputSize()",
        description="inputSize of Sub(C2)",
    ),
    TestCaseSpec(
        id="sl_similarity",
        method="SubalgebraLattice.isSimilarTo",
        setup=_SETUP,
        call="sl.isSimilarTo(sl)",
        description="isSimilarTo self",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_make_universe",
        method="SubalgebraLattice.makeUniverse",
        setup=_SETUP,
        call="(sl.makeUniverse(), sl.cardinality())[1]",
        description="makeUniverse then cardinality",
    ),
    TestCaseSpec(
        id="sl_make_jis",
        method="SubalgebraLattice.makeJoinIrreducibles",
        setup=_SETUP,
        call="(sl.makeJoinIrreducibles(), len(sl.joinIrreducibles()))[1]",
        description="makeJoinIrreducibles then count",
    ),
    TestCaseSpec(
        id="sl_stop_make",
        method="SubalgebraLattice.stopMakeUniverse",
        setup=_SETUP,
        call="sl.stopMakeUniverse()",
        description="stopMakeUniverse is void",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="sl_size_computed",
        method="SubalgebraLattice.getSizeComputed",
        setup=_SETUP,
        call="(sl.cardinality(), sl.getSizeComputed())[1]",
        description="getSizeComputed after universe",
    ),
    TestCaseSpec(
        id="bs_normalize",
        method="BasicSet.normalize",
        setup=_SETUP,
        call="(s01.normalize(), str(s01))[1]",
        description="normalize is in-place sort",
    ),
    TestCaseSpec(
        id="sl_similarity_type_eq",
        method="SubalgebraLattice.similarityType",
        setup=_SETUP,
        call="sl.similarityType() is not None",
        description="similarityType is lattice type",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_update_sim",
        method="SubalgebraLattice.updateSimilarityType",
        setup=_SETUP,
        call="sl.updateSimilarityType()",
        description="updateSimilarityType is void",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="sl_make_op_tables",
        method="SubalgebraLattice.makeOperationTables",
        setup=_SETUP,
        call="sl.makeOperationTables()",
        description="makeOperationTables is void",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="sl_monitoring",
        method="SubalgebraLattice.monitoring",
        setup=_SETUP,
        call="(sl.setMonitor(None), sl.monitoring())[1]",
        description="monitoring after setMonitor(None)",
        **_BOOL
    ),
    TestCaseSpec(
        id="sl_get_monitor",
        method="SubalgebraLattice.getMonitor",
        setup=_SETUP,
        call="sl.getMonitor()",
        description="getMonitor default None",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_set_monitor_bad",
        method="SubalgebraLattice.setMonitor",
        setup=_SETUP,
        call="sl.setMonitor(1)",
        description="setMonitor(int) TypeError",
        expected_exception="TypeError",
    ),
    TestCaseSpec(
        id="sl_ctor_null",
        method="SubalgebraLattice.SubalgebraLattice",
        setup=_SETUP,
        call="SubalgebraLattice(None)",
        description="SubalgebraLattice(null) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="sl_no_duplicates",
        method="SubalgebraLattice.noDuplicates",
        setup=_SETUP,
        call="list(SubalgebraLattice.noDuplicates([1, 1, 2, 2, 3]))",
        description="noDuplicates sorted blocks",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_make_sg",
        method="SubalgebraLattice.makeSg",
        setup=_SETUP,
        call="sl.makeSg([0])",
        description="makeSg([0])",
    ),
    TestCaseSpec(
        id="sl_join_closure",
        method="SubalgebraLattice.joinClosure",
        setup=_SETUP,
        call="sorted(str(x) for x in sl.joinClosure([sl.sg([0])]))",
        description="joinClosure of sg(0)",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_get_algebra_name",
        method="SubalgebraLattice.getAlgebra",
        setup=_SETUP,
        call="sl.getAlgebra().getName()",
        description="getAlgebra name C2",
        **_ALG
    ),
    TestCaseSpec(
        id="sl_get_basic_lattice_card",
        method="SubalgebraLattice.getBasicLattice",
        setup=_SETUP,
        call="sl.getBasicLattice().cardinality()",
        description="getBasicLattice cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="sl_max_drawable",
        method="SubalgebraLattice.MAX_DRAWABLE_SIZE",
        setup=_SETUP,
        call="SubalgebraLattice.MAX_DRAWABLE_SIZE",
        description="MAX_DRAWABLE_SIZE 100",
    ),
    TestCaseSpec(
        id="sl_make_universe_k",
        method="SubalgebraLattice.getMakeUniverseK",
        setup=_SETUP,
        call="(sl.cardinality(), sl.getMakeUniverseK())[1]",
        description="getMakeUniverseK stays 0",
    ),
    TestCaseSpec(
        id="sl_homo_id",
        method="SubalgebraLattice.extendToHomomorphism",
        setup=_SETUP,
        call="dict((int(k), int(v)) for k, v in (SubalgebraLattice.extendToHomomorphism([0], [0], c2, c2) or {}).items())",
        description="extendToHomomorphism identity on 0",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_homo_none",
        method="SubalgebraLattice.extendToHomomorphism",
        setup=_SETUP,
        call="SubalgebraLattice.extendToHomomorphism([0], [1], c2, c2)",
        description="no homo 0 -> 1 on C2",
        **_NONE
    ),
    TestCaseSpec(
        id="sl_homo_len",
        method="SubalgebraLattice.extendToHomomorphism",
        setup=_SETUP,
        call="SubalgebraLattice.extendToHomomorphism([0], [0, 1], c2, c2)",
        description="mismatched gens IAE",
        expected_exception="IllegalArgumentException",
        compare_exception_message=True,
    ),
    TestCaseSpec(
        id="sl_product_card",
        method="SubalgebraLattice.cardinality",
        setup=_SETUP,
        call="ProductAlgebra('C2xC2', [c2, c2]).sub().cardinality()",
        description="Sub(C2xC2) cardinality 6",
    ),
    TestCaseSpec(
        id="sl_product_universe",
        method="SubalgebraLattice.universe",
        setup=_SETUP,
        call="sorted(str(x) for x in ProductAlgebra('C2xC2', [c2, c2]).sub().universe())",
        description="Sub(C2xC2) universe",
        **_LIST
    ),
    TestCaseSpec(
        id="sl_quot_card",
        method="SubalgebraLattice.cardinality",
        setup=_SETUP,
        call="QuotientAlgebra('Q', c2, c2.con().zero()).sub().cardinality()",
        description="Sub(C2/0) cardinality 3",
    ),
    TestCaseSpec(
        id="sl_con",
        method="SubalgebraLattice.con",
        setup=_SETUP,
        call="sl.con().cardinality()",
        description="Con(Sub(C2)) cardinality",
        xfail_reason=_CON_XFAIL,
        **_LAT
    ),
    TestCaseSpec(
        id="sl_sub",
        method="SubalgebraLattice.sub",
        setup=_SETUP,
        call="sl.sub().cardinality()",
        description="Sub(Sub(C2)) cardinality",
        xfail_reason=_SUB_XFAIL,
        **_LAT
    ),
    TestCaseSpec(
        id="sl_get_diagram",
        method="SubalgebraLattice.getDiagram",
        setup=_SETUP,
        call="sl.getDiagram()",
        description="getDiagram latdraw GUI",
        xfail_reason=_DIAGRAM_XFAIL,
        **_NONE
    ),
    TestCaseSpec(
        id="sl_value_roundtrip",
        method="SubalgebraLattice",
        setup=_SETUP
        + r"""
_univ = sorted(str(x) for x in sl.universe())
_z = sl.zero()
_o = sl.one()
_a = sl.sg([0])
_rt = {
    'card': int(sl.cardinality()),
    'univ': _univ,
    'join': str(sl.join(_z, _o)),
    'meet_is_null': sl.meet(_z, _o) is None,
    'leq': bool(sl.leq(_z, _o)),
    'sg0': str(_a),
    'onegens': [str(x) for x in sl.oneGeneratedSubalgebras()],
    'jis': [str(x) for x in sl.joinIrreducibles()],
    'mingen': str(sl.findMinimalSizedGeneratingSet()),
}
""",
        call="_rt",
        description="Round-trip Sub(C2): card, universe, join, meet-null, leq, sg, JIs",
        skip_string_check=True,
    ),
]
