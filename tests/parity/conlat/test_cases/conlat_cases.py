"""Test case specifications for org.uacalc.alg.conlat Partition / BasicPartition / CongruenceLattice."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.alg.conlat import BasicPartition, Partition, CongruenceLattice
from org.uacalc.io import AlgebraIO
zero3 = BasicPartition.zero(3)
one3 = BasicPartition.one(3)
p01 = BasicPartition('|0 1|2|')
p12 = BasicPartition('|0|1 2|')
p_arr = BasicPartition([-2, 0, -1])
alg = AlgebraIO.readAlgebraFile('resources/algebras/cyclic2.ua')
con = CongruenceLattice(alg)
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java array/List/Set toString vs Python list.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")
_LAT = dict(skip_string_check=True, notes="Java lattice toString is Class@hex; values compared.")
_ALG = dict(skip_string_check=True, notes="Java Algebra toString is Class@hex; values compared.")
_REL = dict(skip_string_check=True, notes="Java BasicBinaryRelation toString vs Python.")

TEST_CASES = [
    TestCaseSpec(
        id="bp_zero_str",
        method="BasicPartition.zero",
        setup=_SETUP,
        call="zero3",
        description="zero(3) block string",
    ),
    TestCaseSpec(
        id="bp_one_str",
        method="BasicPartition.one",
        setup=_SETUP,
        call="one3",
        description="one(3) block string",
    ),
    TestCaseSpec(
        id="bp_from_string",
        method="BasicPartition.BasicPartition",
        setup=_SETUP,
        call="p01",
        description="BasicPartition from bar string",
    ),
    TestCaseSpec(
        id="bp_from_brackets",
        method="BasicPartition.BasicPartition",
        setup=_SETUP,
        call="BasicPartition('[[0 1][2]]')",
        description="BasicPartition from bracket string",
    ),
    TestCaseSpec(
        id="bp_from_array",
        method="BasicPartition.BasicPartition",
        setup=_SETUP,
        call="p_arr",
        description="BasicPartition from array",
    ),
    TestCaseSpec(
        id="bp_universe_size",
        method="Partition.universeSize",
        setup=_SETUP,
        call="p01.universeSize()",
        description="universeSize of |0 1|2|",
    ),
    TestCaseSpec(
        id="bp_number_of_blocks",
        method="Partition.numberOfBlocks",
        setup=_SETUP,
        call="p01.numberOfBlocks()",
        description="numberOfBlocks of |0 1|2|",
    ),
    TestCaseSpec(
        id="bp_is_related_true",
        method="Partition.isRelated",
        setup=_SETUP,
        call="p01.isRelated(0, 1)",
        description="0 related to 1",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_is_related_false",
        method="Partition.isRelated",
        setup=_SETUP,
        call="p01.isRelated(0, 2)",
        description="0 not related to 2",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_representative",
        method="Partition.representative",
        setup=_SETUP,
        call="p01.representative(1)",
        description="representative of 1 in |0 1|2|",
    ),
    TestCaseSpec(
        id="bp_is_representative",
        method="Partition.isRepresentative",
        setup=_SETUP,
        call="p01.isRepresentative(0)",
        description="0 is a representative",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_representatives",
        method="Partition.representatives",
        setup=_SETUP,
        call="list(p01.representatives())",
        description="representatives list",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_block_index",
        method="Partition.blockIndex",
        setup=_SETUP,
        call="p01.blockIndex(1)",
        description="blockIndex of 1",
    ),
    TestCaseSpec(
        id="bp_get_blocks",
        method="Partition.getBlocks",
        setup=_SETUP,
        call="[[int(x) for x in blk] for blk in p01.getBlocks()]",
        description="getBlocks nested lists",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_to_array",
        method="Partition.toArray",
        setup=_SETUP,
        call="list(p01.toArray())",
        description="toArray",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_get_array",
        method="BasicPartition.getArray",
        setup=_SETUP,
        call="list(p01.getArray())",
        description="getArray",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_join",
        method="Partition.join",
        setup=_SETUP,
        call="p01.join(p12)",
        description="join of two partitions",
    ),
    TestCaseSpec(
        id="bp_meet",
        method="Partition.meet",
        setup=_SETUP,
        call="p01.meet(p12)",
        description="meet of two partitions",
    ),
    TestCaseSpec(
        id="bp_leq_true",
        method="Partition.leq",
        setup=_SETUP,
        call="p01.leq(one3)",
        description="p01 leq one",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_leq_false",
        method="Partition.leq",
        setup=_SETUP,
        call="one3.leq(p01)",
        description="one not leq p01",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_is_zero",
        method="Partition.isZero",
        setup=_SETUP,
        call="zero3.isZero()",
        description="zero isZero",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_is_uniform_one",
        method="Partition.isUniform",
        setup=_SETUP,
        call="one3.isUniform()",
        description="one is uniform",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_is_uniform_p01",
        method="Partition.isUniform",
        setup=_SETUP,
        call="p01.isUniform()",
        description="|0 1|2| is not uniform",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_is_initial_lex",
        method="Partition.isInitialLexRepresentative",
        setup=_SETUP,
        call="zero3.isInitialLexRepresentative()",
        description="zero is initial lex representative",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_rank",
        method="BasicPartition.rank",
        setup=_SETUP,
        call="p01.rank()",
        description="rank = n - numberOfBlocks",
    ),
    TestCaseSpec(
        id="bp_tostring_default",
        method="Partition.toString",
        setup=_SETUP,
        call="p01.toString()",
        description="toString BLOCK",
    ),
    TestCaseSpec(
        id="bp_tostring_maxlen",
        method="Partition.toString",
        setup=_SETUP,
        call="one3.toString(3)",
        description="toString(maxLen)",
    ),
    TestCaseSpec(
        id="bp_tostring_internal",
        method="Partition.toString",
        setup=_SETUP,
        call="p01.toString(Partition.PrintType.INTERNAL)",
        description="toString(INTERNAL)",
    ),
    TestCaseSpec(
        id="bp_tostring_ewk",
        method="Partition.toString",
        setup=_SETUP,
        call="p01.toString(Partition.PrintType.EWK)",
        description="toString(EWK)",
    ),
    TestCaseSpec(
        id="bp_tostring_human",
        method="Partition.toString",
        setup=_SETUP,
        call="p01.toString(Partition.PrintType.HUMAN)",
        description="toString(HUMAN)",
    ),
    TestCaseSpec(
        id="bp_tostring_sq",
        method="Partition.toString",
        setup=_SETUP,
        call="p01.toString(Partition.PrintType.SQ_BRACE_BLOCK)",
        description="toString(SQ_BRACE_BLOCK)",
    ),
    TestCaseSpec(
        id="bp_equals",
        method="Partition.equals",
        setup=_SETUP,
        call="p01.equals(BasicPartition('|0 1|2|'))",
        description="equals after reconstruct",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_hash_code",
        method="BasicPartition.hashCode",
        setup=_SETUP,
        call="p01.hashCode()",
        description="Java IntArray hashCode",
    ),
    TestCaseSpec(
        id="bp_compare_to",
        method="BasicPartition.compareTo",
        setup=_SETUP,
        call="p01.compareTo(one3)",
        description="compareTo by rank then array",
    ),
    TestCaseSpec(
        id="bp_get_pairs",
        method="Partition.getPairs",
        setup=_SETUP,
        call="sorted((int(p.get(0) if hasattr(p, 'get') else p[0]), int(p.get(1) if hasattr(p, 'get') else p[1])) for p in p01.getPairs())",
        description="getPairs as lists",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_compose",
        method="Partition.compose",
        setup=_SETUP,
        call="(lambda r: sorted((int(p.get(0) if hasattr(p, 'get') else p[0]), int(p.get(1) if hasattr(p, 'get') else p[1])) for p in r.getPairs()))(p01.compose(p12))",
        description="compose two partitions as sorted pairs",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_join_blocks",
        method="Partition.joinBlocks",
        setup=_SETUP,
        call="(lambda q: (q.joinBlocks(0, 2), str(q))[1])(BasicPartition.zero(3))",
        description="joinBlocks 0 and 2 on zero(3)",
    ),
    TestCaseSpec(
        id="bp_normalize",
        method="Partition.normalize",
        setup=_SETUP,
        call="(lambda q: (q.normalize(), str(q))[1])(BasicPartition([-1, -1, -1]))",
        description="normalize zero array",
    ),
    TestCaseSpec(
        id="bp_string_to_partition",
        method="BasicPartition.stringToPartition",
        setup=_SETUP,
        call="list(BasicPartition.stringToPartition('|0 1|2|', -1))",
        description="stringToPartition returns int array",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_string_to_partition_null",
        method="BasicPartition.stringToPartition",
        setup=_SETUP,
        call="BasicPartition.stringToPartition('not-a-partition', -1)",
        description="unrecognized format returns null",
        **_NONE
    ),
    TestCaseSpec(
        id="bp_jb_to_partition",
        method="BasicPartition.jbToPartition",
        setup=_SETUP,
        call="BasicPartition.jbToPartition([0, 0, 2, 0])",
        description="jbToPartition kernel form",
    ),
    TestCaseSpec(
        id="bp_perm_level_pair",
        method="BasicPartition.permutabilityLevel",
        setup=_SETUP,
        call="BasicPartition.permutabilityLevel(0, 2, p01, p12)",
        description="permutabilityLevel(a,b,par0,par1)",
    ),
    TestCaseSpec(
        id="bp_perm_level_join",
        method="BasicPartition.permutabilityLevel",
        setup=_SETUP,
        call="BasicPartition.permutabilityLevel(p01, p12)",
        description="permutabilityLevel(par0, par1)",
    ),
    TestCaseSpec(
        id="bp_leq_arrays",
        method="BasicPartition.leq",
        setup=_SETUP,
        call="BasicPartition.leq(list(p01.toArray()), list(one3.toArray()))",
        description="static leq(int[], int[])",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_part_to_kiss",
        method="BasicPartition.partToKissString",
        setup=_SETUP,
        call="BasicPartition.partToKissString(list(p01.toArray()))",
        description="partToKissString",
    ),
    TestCaseSpec(
        id="bp_direct_product",
        method="BasicPartition.directProduct",
        setup=_SETUP,
        call="BasicPartition.directProduct(p01, p12)",
        description="directProduct",
    ),
    TestCaseSpec(
        id="bp_first_projection",
        method="BasicPartition.firstProjection",
        setup=_SETUP,
        call="BasicPartition.firstProjection(2)",
        description="firstProjection(2)",
    ),
    TestCaseSpec(
        id="bp_second_projection",
        method="BasicPartition.secondProjection",
        setup=_SETUP,
        call="BasicPartition.secondProjection(2)",
        description="secondProjection(2)",
    ),
    TestCaseSpec(
        id="bp_join_closure",
        method="BasicPartition.joinClosure",
        setup=_SETUP,
        call="[str(p) for p in BasicPartition.joinClosure([p01, p12])]",
        description="joinClosure strings",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_meet_closure",
        method="BasicPartition.meetClosure",
        setup=_SETUP,
        call="[str(p) for p in BasicPartition.meetClosure([p01, p12])]",
        description="meetClosure strings",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_sub_universe",
        method="BasicPartition.subUniverseGenerated",
        setup=_SETUP,
        call="sorted(str(p) for p in BasicPartition.subUniverseGenerated([p01, p12]))",
        description="subUniverseGenerated strings",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_from_matrix",
        method="BasicPartition.partitionFromMatrix",
        setup=_SETUP,
        call="BasicPartition.partitionFromMatrix([[0, 1], [1, 0]])",
        description="partitionFromMatrix 2x2",
    ),
    TestCaseSpec(
        id="bp_unary_polys",
        method="BasicPartition.unaryPolymorphisms",
        setup=_SETUP,
        call="len(BasicPartition.unaryPolymorphisms([BasicPartition.zero(2)], None))",
        description="unaryPolymorphisms of zero(2) count",
    ),
    TestCaseSpec(
        id="bp_binary_polys",
        method="BasicPartition.binaryPolymorphisms",
        setup=_SETUP,
        call="len(BasicPartition.binaryPolymorphisms([BasicPartition.zero(2)]))",
        description="binaryPolymorphisms of zero(2) count",
    ),
    TestCaseSpec(
        id="bp_unary_poly_alg",
        method="BasicPartition.unaryPolymorphismsAlgebra",
        setup=_SETUP,
        call="BasicPartition.unaryPolymorphismsAlgebra([BasicPartition.zero(2)]).cardinality()",
        description="unaryPolymorphismsAlgebra cardinality",
        **_ALG
    ),
    TestCaseSpec(
        id="bp_is_hereditary",
        method="BasicPartition.isHereditary",
        setup=_SETUP,
        call="BasicPartition.isHereditary([BasicPartition.zero(2)])",
        description="isHereditary always true after computing",
        **_BOOL
    ),
    TestCaseSpec(
        id="bp_func_to_jis",
        method="BasicPartition.funcToJIs",
        setup=_SETUP,
        call="BasicPartition.funcToJIs(1)",
        description="funcToJIs returns null",
        **_NONE
    ),
    TestCaseSpec(
        id="bp_join_null",
        method="Partition.join",
        setup=_SETUP,
        call="p01.join(None)",
        description="join(null) is NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="bp_ctor_null_string",
        method="BasicPartition.BasicPartition",
        setup=_SETUP,
        call="BasicPartition(None)",
        description="BasicPartition(null) is NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="bp_ctor_bad_string",
        method="BasicPartition.BasicPartition",
        setup=_SETUP,
        call="BasicPartition('not-a-partition')",
        description="BasicPartition(unrecognized) NPEs on null array",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="bp_ctor_empty_string",
        method="BasicPartition.BasicPartition",
        setup=_SETUP,
        call="BasicPartition('')",
        description="BasicPartition('') StringIndexOutOfBoundsException",
        expected_exception="StringIndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="bp_ctor_bad_bracket",
        method="BasicPartition.BasicPartition",
        setup=_SETUP,
        call="BasicPartition('[0 1]')",
        description="single-bracket string is IllegalArgumentException",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="bp_normalize_runtime",
        method="BasicPartition.normalize",
        setup=_SETUP,
        call="BasicPartition.normalize([0, 0, 2, 0])",
        description="static normalize part[0]==0 is RuntimeException",
        expected_exception="RuntimeException",
    ),
    TestCaseSpec(
        id="bp_is_related_oob",
        method="Partition.isRelated",
        setup=_SETUP,
        call="p01.isRelated(0, 9)",
        description="isRelated OOB is IndexOutOfBoundsException",
        expected_exception="IndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="bp_value_roundtrip",
        method="Partition",
        setup=_SETUP
        + r"""
_payload = list(p01.toArray())
_txt = p01.toString()
_p_arr = BasicPartition(_payload)
_p_str = BasicPartition(_txt)
_rt = {
    "equals_arr": bool(p01.equals(_p_arr)),
    "equals_str": bool(p01.equals(_p_str)),
    "toString": str(p01),
    "toString_arr": str(_p_arr),
    "toString_str": str(_p_str),
    "join": str(p01.join(p12)),
    "join_arr": str(_p_arr.join(p12)),
    "meet": str(p01.meet(p12)),
    "meet_arr": str(_p_arr.meet(p12)),
    "leq": bool(p01.leq(one3)),
    "leq_arr": bool(_p_arr.leq(one3)),
}
""",
        call="_rt",
        description="Round-trip partition via array and toString: join, meet, leq, equals, toString",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="cl_ctor_cyclic2",
        method="CongruenceLattice.CongruenceLattice",
        setup=_SETUP,
        call="con",
        description="CongruenceLattice of cyclic2",
        **_LAT
    ),
    TestCaseSpec(
        id="cl_cardinality",
        method="CongruenceLattice.cardinality",
        setup=_SETUP,
        call="con.cardinality()",
        description="Con(cyclic2) cardinality",
    ),
    TestCaseSpec(
        id="cl_zero",
        method="CongruenceLattice.zero",
        setup=_SETUP,
        call="con.zero()",
        description="zero congruence",
    ),
    TestCaseSpec(
        id="cl_one",
        method="CongruenceLattice.one",
        setup=_SETUP,
        call="con.one()",
        description="one congruence",
    ),
    TestCaseSpec(
        id="cl_universe",
        method="CongruenceLattice.universe",
        setup=_SETUP,
        call="sorted(str(p) for p in con.universe())",
        description="universe strings",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_get_universe_list",
        method="CongruenceLattice.getUniverseList",
        setup=_SETUP,
        call="sorted(str(p) for p in con.getUniverseList())",
        description="getUniverseList strings",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_principals",
        method="CongruenceLattice.principals",
        setup=_SETUP,
        call="sorted(str(p) for p in con.principals())",
        description="principals",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_join_irreducibles",
        method="CongruenceLattice.joinIrreducibles",
        setup=_SETUP,
        call="sorted(str(p) for p in con.joinIrreducibles())",
        description="joinIrreducibles",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_meet_irreducibles",
        method="CongruenceLattice.meetIrreducibles",
        setup=_SETUP,
        call="sorted(str(p) for p in con.meetIrreducibles())",
        description="meetIrreducibles",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_atoms",
        method="CongruenceLattice.atoms",
        setup=_SETUP,
        call="sorted(str(p) for p in con.atoms())",
        description="atoms",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_is_distributive",
        method="CongruenceLattice.isDistributive",
        setup=_SETUP,
        call="con.isDistributive()",
        description="isDistributive cyclic2",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_cg",
        method="CongruenceLattice.Cg",
        setup=_SETUP,
        call="con.Cg(0, 1)",
        description="Cg(0,1)",
    ),
    TestCaseSpec(
        id="cl_tg",
        method="CongruenceLattice.Tg",
        setup=_SETUP,
        call="(lambda r: sorted((int(p.get(0) if hasattr(p, 'get') else p[0]), int(p.get(1) if hasattr(p, 'get') else p[1])) for p in r.getPairs()))(con.Tg(0, 1))",
        description="Tg(0,1) as sorted pairs",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_get_name",
        method="CongruenceLattice.getName",
        setup=_SETUP,
        call="con.getName()",
        description="getName Con(alg)",
    ),
    TestCaseSpec(
        id="cl_is_total",
        method="CongruenceLattice.isTotal",
        setup=_SETUP,
        call="con.isTotal()",
        description="isTotal true",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_is_unary",
        method="CongruenceLattice.isUnary",
        setup=_SETUP,
        call="con.isUnary()",
        description="isUnary false",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_is_idempotent",
        method="CongruenceLattice.isIdempotent",
        setup=_SETUP,
        call="con.isIdempotent()",
        description="isIdempotent true",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_operations",
        method="CongruenceLattice.operations",
        setup=_SETUP,
        call="con.operations()",
        description="operations is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_get_operation",
        method="CongruenceLattice.getOperation",
        setup=_SETUP,
        call="con.getOperation(None)",
        description="getOperation is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_constant_ops",
        method="CongruenceLattice.constantOperations",
        setup=_SETUP,
        call="list(con.constantOperations())",
        description="constantOperations empty",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_set_name",
        method="CongruenceLattice.setName",
        setup=_SETUP,
        call="con.setName('x')",
        description="setName is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="cl_coatoms",
        method="CongruenceLattice.coatoms",
        setup=_SETUP,
        call="con.coatoms()",
        description="coatoms is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="cl_complements",
        method="CongruenceLattice.complements",
        setup=_SETUP,
        call="sorted(str(p) for p in con.complements(con.zero()))",
        description="complements of zero",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_join_lat",
        method="CongruenceLattice.join",
        setup=_SETUP,
        call="con.join(con.zero(), con.one())",
        description="lattice join zero, one",
    ),
    TestCaseSpec(
        id="cl_meet_lat",
        method="CongruenceLattice.meet",
        setup=_SETUP,
        call="con.meet(con.zero(), con.one())",
        description="lattice meet zero, one",
    ),
    TestCaseSpec(
        id="cl_leq_lat",
        method="CongruenceLattice.leq",
        setup=_SETUP,
        call="con.leq(con.zero(), con.one())",
        description="lattice leq zero, one",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_join_list",
        method="CongruenceLattice.join",
        setup=_SETUP,
        call="con.join([con.zero(), con.one()])",
        description="join(List)",
    ),
    TestCaseSpec(
        id="cl_universe_found",
        method="CongruenceLattice.universeFound",
        setup=_SETUP,
        call="(con.universe(), con.universeFound())[1]",
        description="universeFound after universe()",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_is_drawable",
        method="CongruenceLattice.isDrawable",
        setup=_SETUP,
        call="con.isDrawable()",
        description="isDrawable cyclic2",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_is_smaller_than",
        method="CongruenceLattice.isSmallerThan",
        setup=_SETUP,
        call="con.isSmallerThan(10)",
        description="isSmallerThan(10)",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_join_irreducible",
        method="CongruenceLattice.joinIrreducible",
        setup=_SETUP,
        call="con.joinIrreducible(con.one())",
        description="joinIrreducible(one)",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_monitoring",
        method="CongruenceLattice.monitoring",
        setup=_SETUP,
        call="(con.setMonitor(None), con.monitoring())[1]",
        description="monitoring after setMonitor(None)",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_get_monitor",
        method="CongruenceLattice.getMonitor",
        setup=_SETUP,
        call="con.getMonitor()",
        description="getMonitor default None",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_set_monitor_bad",
        method="CongruenceLattice.setMonitor",
        setup=_SETUP,
        call="con.setMonitor(1)",
        description="setMonitor(int) TypeError",
        expected_exception="TypeError",
    ),
    TestCaseSpec(
        id="cl_minimal_elements",
        method="CongruenceLattice.minimalElements",
        setup=_SETUP,
        call="[str(p) for p in CongruenceLattice.minimalElements([con.one(), con.zero()])]",
        description="minimalElements topological",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_ctor_null",
        method="CongruenceLattice.CongruenceLattice",
        setup=_SETUP,
        call="CongruenceLattice(None)",
        description="CongruenceLattice(null) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="cl_value_roundtrip",
        method="CongruenceLattice",
        setup=_SETUP
        + r"""
_univ = [str(p) for p in con.universe()]
_parts = list(con.universe())
_z = con.zero()
_o = con.one()
_rt = {
    "card": int(con.cardinality()),
    "univ": sorted(_univ),
    "join": str(_z.join(_o)),
    "meet": str(_z.meet(_o)),
    "leq": bool(_z.leq(_o)),
    "eq_zero": bool(_z.equals(BasicPartition.zero(_z.universeSize()))),
    "toString_zero": str(_z),
    "toString_one": str(_o),
}
""",
        call="_rt",
        description="Round-trip Con(cyclic2) partitions: join, meet, leq, equals, toString",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="bp_get",
        method="BasicPartition.get",
        setup=_SETUP,
        call="p01.get(1)",
        description="IntArray get(1) on |0 1|2|",
    ),
    TestCaseSpec(
        id="bp_iterator",
        method="Partition.iterator",
        setup=_SETUP,
        call="sorted((int(p.get(0) if hasattr(p, 'get') else p[0]), int(p.get(1) if hasattr(p, 'get') else p[1])) for p in p01.iterator())",
        description="iterator over pairs",
        **_LIST
    ),
    TestCaseSpec(
        id="bp_meet_null",
        method="Partition.meet",
        setup=_SETUP,
        call="p01.meet(None)",
        description="meet(null) is NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="bp_leq_null",
        method="Partition.leq",
        setup=_SETUP,
        call="p01.leq(None)",
        description="leq(null) is NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="bp_unary_empty",
        method="BasicPartition.unaryPolymorphisms",
        setup=_SETUP,
        call="BasicPartition.unaryPolymorphisms([], None)",
        description="unaryPolymorphisms empty list is IndexOutOfBoundsException",
        expected_exception="IndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="bp_binary_poly_alg",
        method="BasicPartition.binaryPolymorphismsAlgebra",
        setup=_SETUP,
        call="BasicPartition.binaryPolymorphismsAlgebra([BasicPartition.zero(2)], None).cardinality()",
        description="binaryPolymorphismsAlgebra cardinality",
        **_ALG
    ),
    TestCaseSpec(
        id="bp_static_normalize",
        method="BasicPartition.normalize",
        setup=_SETUP,
        call="(lambda a: (BasicPartition.normalize(a), list(a))[1])([-1, -1, -1])",
        description="static normalize of zero array",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_get_description",
        method="CongruenceLattice.getDescription",
        setup=_SETUP,
        call="con.getDescription()",
        description="getDescription default",
        **_LAT
    ),
    TestCaseSpec(
        id="cl_set_description",
        method="CongruenceLattice.setDescription",
        setup=_SETUP,
        call="(con.setDescription('d'), con.getDescription())[1]",
        description="setDescription then get",
    ),
    TestCaseSpec(
        id="cl_get_ops_map",
        method="CongruenceLattice.getOperationsMap",
        setup=_SETUP,
        call="con.getOperationsMap()",
        description="getOperationsMap is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_make_op_tables",
        method="CongruenceLattice.makeOperationTables",
        setup=_SETUP,
        call="con.makeOperationTables()",
        description="makeOperationTables is void",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="cl_iterator",
        method="CongruenceLattice.iterator",
        setup=_SETUP,
        call="sorted(str(p) for p in con.iterator())",
        description="iterator over universe",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_cg_part",
        method="CongruenceLattice.Cg",
        setup=_SETUP,
        call="con.Cg(con.zero())",
        description="Cg(Partition)",
    ),
    TestCaseSpec(
        id="cl_meet_list",
        method="CongruenceLattice.meet",
        setup=_SETUP,
        call="con.meet([con.zero(), con.one()])",
        description="meet(List)",
    ),
    TestCaseSpec(
        id="cl_generating_pair",
        method="CongruenceLattice.generatingPair",
        setup=_SETUP,
        call="(lambda p: None if p is None else [int(p.get(i)) for i in range(p.universeSize())])(con.generatingPair(con.one()))",
        description="generatingPair of one",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_find_coatom",
        method="CongruenceLattice.findCoatomAbove",
        setup=_SETUP,
        call="con.findCoatomAbove(con.zero())",
        description="findCoatomAbove(zero)",
    ),
    TestCaseSpec(
        id="cl_find_join_irred",
        method="CongruenceLattice.findJoinIrred",
        setup=_SETUP,
        call="con.findJoinIrred(con.zero(), con.one())",
        description="findJoinIrred(zero, one)",
    ),
    TestCaseSpec(
        id="cl_find_meet_irred",
        method="CongruenceLattice.findMeetIrred",
        setup=_SETUP,
        call="con.findMeetIrred(con.zero(), con.one())",
        description="findMeetIrred(zero, one)",
    ),
    TestCaseSpec(
        id="cl_find_principal_chain",
        method="CongruenceLattice.findPrincipalChain",
        setup=_SETUP,
        call="[str(p) for p in con.findPrincipalChain()]",
        description="findPrincipalChain",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_find_upper_cover",
        method="CongruenceLattice.findUpperCover",
        setup=_SETUP,
        call="con.findUpperCover(con.zero())",
        description="findUpperCover(zero)",
    ),
    TestCaseSpec(
        id="cl_irredundant",
        method="CongruenceLattice.irredundantMeetDecomposition",
        setup=_SETUP,
        call="sorted(str(p) for p in con.irredundantMeetDecomposition())",
        description="irredundantMeetDecomposition",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_perm_level",
        method="CongruenceLattice.permutabilityLevel",
        setup=_SETUP,
        call="con.permutabilityLevel()",
        description="permutabilityLevel of cyclic2",
    ),
    TestCaseSpec(
        id="cl_basic_lattice",
        method="CongruenceLattice.getBasicLattice",
        setup=_SETUP,
        call="con.getBasicLattice().cardinality()",
        description="getBasicLattice cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="cl_idempotent_polys",
        method="CongruenceLattice.idempotentPolynomials",
        setup=_SETUP,
        call="len(con.idempotentPolynomials())",
        description="idempotentPolynomials count",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_meet_irreducible",
        method="CongruenceLattice.meetIrreducible",
        setup=_SETUP,
        call="con.meetIrreducible(con.zero())",
        description="meetIrreducible(zero)",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_join_prime",
        method="CongruenceLattice.joinPrime",
        setup=_SETUP,
        call="con.joinPrime(con.one())",
        description="joinPrime(one)",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_lower_star",
        method="CongruenceLattice.lowerStar",
        setup=_SETUP,
        call="con.lowerStar(con.one())",
        description="lowerStar(one)",
    ),
    TestCaseSpec(
        id="cl_make_universe",
        method="CongruenceLattice.makeUniverse",
        setup=_SETUP,
        call="(con.makeUniverse(), con.universeFound())[1]",
        description="makeUniverse then universeFound",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_make_principals",
        method="CongruenceLattice.makePrincipals",
        setup=_SETUP,
        call="(con.makePrincipals(None), len(con.principals()))[1]",
        description="makePrincipals then count",
    ),
    TestCaseSpec(
        id="cl_make_atoms",
        method="CongruenceLattice.makeAtoms",
        setup=_SETUP,
        call="(con.makeAtoms(), len(con.atoms()))[1]",
        description="makeAtoms then count",
    ),
    TestCaseSpec(
        id="cl_make_jis",
        method="CongruenceLattice.makeJoinIrreducibles",
        setup=_SETUP,
        call="(con.makeJoinIrreducibles(None), len(con.joinIrreducibles()))[1]",
        description="makeJoinIrreducibles then count",
    ),
    TestCaseSpec(
        id="cl_input_size",
        method="CongruenceLattice.inputSize",
        setup=_SETUP,
        call="con.inputSize()",
        description="inputSize lattice type",
    ),
    TestCaseSpec(
        id="cl_get_algebra",
        method="CongruenceLattice.getAlgebra",
        setup=_SETUP,
        call="con.getAlgebra().cardinality()",
        description="getAlgebra cardinality",
        **_ALG
    ),
    TestCaseSpec(
        id="cl_similarity_type",
        method="CongruenceLattice.similarityType",
        setup=_SETUP,
        call="str(con.similarityType())",
        description="similarityType is lattice",
    ),
    TestCaseSpec(
        id="cl_is_similar_to",
        method="CongruenceLattice.isSimilarTo",
        setup=_SETUP,
        call="con.isSimilarTo(con)",
        description="isSimilarTo self",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_update_sim",
        method="CongruenceLattice.updateSimilarityType",
        setup=_SETUP,
        call="con.updateSimilarityType()",
        description="updateSimilarityType is void",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="cl_upper_covers",
        method="CongruenceLattice.upperCoversMap",
        setup=_SETUP,
        call="(lambda m: sorted(str(k) for k in (m.keySet() if hasattr(m, 'keySet') else m)))(con.upperCoversMap())",
        description="upperCoversMap keys",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_perm_witnesses",
        method="CongruenceLattice.getPermutabilityLevelWitnesses",
        setup=_SETUP,
        call="(lambda w: None if w is None else sorted(str(p) for p in w))((con.permutabilityLevel(), con.getPermutabilityLevelWitnesses())[1])",
        description="permutability witnesses after computing level",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_jis_found",
        method="CongruenceLattice.joinIrreduciblesFound",
        setup=_SETUP,
        call="(con.joinIrreducibles(), con.joinIrreduciblesFound())[1]",
        description="joinIrreduciblesFound after joinIrreducibles",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_delta",
        method="CongruenceLattice.Delta",
        setup=_SETUP,
        call="con.Delta(con.zero(), con.one())",
        description="Delta(zero, one)",
    ),
    TestCaseSpec(
        id="cl_commutator2",
        method="CongruenceLattice.commutator2",
        setup=_SETUP,
        call="con.commutator2(con.zero(), con.one())",
        description="commutator2(zero, one)",
    ),
    TestCaseSpec(
        id="cl_centralizes",
        method="CongruenceLattice.centralizes",
        setup=_SETUP,
        call="con.centralizes(con.Tg(0, 0), con.Tg(0, 1), con.zero())",
        description="centralizes S, T, delta",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_matrices_card",
        method="CongruenceLattice.matrices",
        setup=_SETUP,
        call="con.matrices(con.Tg(0, 0), con.Tg(0, 1), None).cardinality()",
        description="M(S,T) cardinality for Tg(0,0), Tg(0,1) on C2",
    ),
    TestCaseSpec(
        id="cl_commutator_tg",
        method="CongruenceLattice.commutator",
        setup=_SETUP,
        call="str(con.commutator(con.Tg(0, 0), con.Tg(0, 1)))",
        description="commutator of Tg(0,0) and Tg(0,1) on C2",
    ),
    TestCaseSpec(
        id="cl_weak_commutator_tg",
        method="CongruenceLattice.weakCommutator",
        setup=_SETUP,
        call="str(con.weakCommutator(con.Tg(0, 0), con.Tg(0, 1)))",
        description="weakCommutator of Tg(0,0) and Tg(0,1) on C2",
    ),
]
