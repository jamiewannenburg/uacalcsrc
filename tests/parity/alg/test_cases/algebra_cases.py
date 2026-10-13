"""Test case specifications for org.uacalc.alg Algebra/SmallAlgebra/BasicAlgebra."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.alg import Algebra, SmallAlgebra, BasicAlgebra
from org.uacalc.alg.op import Operations, OperationSymbol
from org.uacalc.io import AlgebraIO
def _op(name, arity, size, table):
    make = getattr(Operations, "makeIntOperation", None)
    if make is None:
        make = Operations.make_int_operation
    return make(OperationSymbol(name, arity), size, table)
xor2 = _op("xor", 2, 2, [0, 1, 1, 0])
and2 = _op("and", 2, 2, [0, 0, 0, 1])
id1 = _op("id", 1, 2, [0, 1])
c0 = Operations.makeConstantIntOperation(2, 0)
alg = BasicAlgebra("Xor2", 2, [xor2])
alg_and = BasicAlgebra("And2", 2, [and2])
alg_id = BasicAlgebra("Id2", 2, [id1])
alg_const = BasicAlgebra("C2", 2, [c0])
alg_list = BasicAlgebra("Listed", ["a", "b"], [id1])
alg_empty = BasicAlgebra("E", 3, [])
# Java GeneralAlgebra.monitor is static; reset between golden cases.
alg.setMonitor(None)
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_OP = dict(skip_string_check=True, notes="Java Operation toString is Class@hex; values compared.")
_MAP = dict(skip_string_check=True, notes="Java Map toString vs Python dict.")
_LIST = dict(skip_string_check=True, notes="Java List/Set toString vs Python list.")
_ALG = dict(skip_string_check=True, notes="Java Algebra toString is Class@hex; values compared.")
_LAT = dict(skip_string_check=True, notes="Java lattice toString is Class@hex; values compared.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")

TEST_CASES = [
    TestCaseSpec(
        id="algebra_cardinality_unknown",
        method="Algebra.CARDINALITY_UNKNOWN",
        setup=_SETUP,
        call="Algebra.CARDINALITY_UNKNOWN",
        description="Algebra.CARDINALITY_UNKNOWN constant",
    ),
    TestCaseSpec(
        id="algebra_cardinality_finite",
        method="Algebra.CARDINALITY_FINITE",
        setup=_SETUP,
        call="Algebra.CARDINALITY_FINITE",
        description="Algebra.CARDINALITY_FINITE constant",
    ),
    TestCaseSpec(
        id="algebra_cardinality_infinite",
        method="Algebra.CARDINALITY_INFINITE",
        setup=_SETUP,
        call="Algebra.CARDINALITY_INFINITE",
        description="Algebra.CARDINALITY_INFINITE constant",
    ),
    TestCaseSpec(
        id="algebra_cardinality_countable",
        method="Algebra.CARDINALITY_COUNTABLE",
        setup=_SETUP,
        call="Algebra.CARDINALITY_COUNTABLE",
        description="Algebra.CARDINALITY_COUNTABLE constant",
    ),
    TestCaseSpec(
        id="algebra_cardinality_countably_infinite",
        method="Algebra.CARDINALITY_COUNTABLY_INFINITE",
        setup=_SETUP,
        call="Algebra.CARDINALITY_COUNTABLY_INFINITE",
        description="Algebra.CARDINALITY_COUNTABLY_INFINITE constant",
    ),
    TestCaseSpec(
        id="alg_get_name",
        method="Algebra.getName",
        setup=_SETUP,
        call="alg.getName()",
        description="getName of xor algebra",
    ),
    TestCaseSpec(
        id="alg_set_name",
        method="Algebra.setName",
        setup=_SETUP + "\nalg.setName('Renamed')\n",
        call="alg.getName()",
        description="setName then getName",
    ),
    TestCaseSpec(
        id="alg_cardinality",
        method="Algebra.cardinality",
        setup=_SETUP,
        call="alg.cardinality()",
        description="cardinality of size-2 algebra",
    ),
    TestCaseSpec(
        id="alg_input_size",
        method="Algebra.inputSize",
        setup=_SETUP,
        call="alg.inputSize()",
        description="inputSize for binary op on 2 elements",
    ),
    TestCaseSpec(
        id="alg_is_unary_false",
        method="Algebra.isUnary",
        setup=_SETUP,
        call="alg.isUnary()",
        description="xor algebra is not unary",
        **_BOOL
    ),
    TestCaseSpec(
        id="alg_is_unary_true",
        method="Algebra.isUnary",
        setup=_SETUP,
        call="alg_id.isUnary()",
        description="unary id algebra is unary",
        **_BOOL
    ),
    TestCaseSpec(
        id="alg_universe",
        method="Algebra.universe",
        setup=_SETUP,
        call="sorted(alg.universe())",
        description="universe of int-universe algebra",
        **_LIST
    ),
    TestCaseSpec(
        id="alg_iterator",
        method="Algebra.iterator",
        setup=_SETUP,
        call="list(alg.iterator())",
        description="iterator yields 0..n-1 in order",
        **_LIST
    ),
    TestCaseSpec(
        id="alg_operations",
        method="Algebra.operations",
        setup=_SETUP,
        call="alg.operations()",
        description="operations() list for xor algebra",
        **_OP
    ),
    TestCaseSpec(
        id="alg_get_operation",
        method="Algebra.getOperation",
        setup=_SETUP,
        call='alg.getOperation(OperationSymbol("xor", 2)).intValueAt([1, 0])',
        description="getOperation finds xor and evaluates",
    ),
    TestCaseSpec(
        id="alg_get_operation_missing",
        method="Algebra.getOperation",
        setup=_SETUP,
        call='alg.getOperation(OperationSymbol("nope", 1))',
        description="getOperation missing symbol returns null",
        **_NONE
    ),
    TestCaseSpec(
        id="alg_get_operation_null",
        method="Algebra.getOperation",
        setup=_SETUP,
        call="alg.getOperation(None)",
        description="getOperation(null) returns null",
        **_NONE
    ),
    TestCaseSpec(
        id="alg_get_operations_map_keys",
        method="Algebra.getOperationsMap",
        setup=_SETUP,
        call="""sorted(str(k) for k in (alg.getOperationsMap().keySet() if hasattr(alg.getOperationsMap(), "keySet") else alg.getOperationsMap()))""",
        description="getOperationsMap keys",
        **_LIST
    ),
    TestCaseSpec(
        id="alg_get_description_unset",
        method="Algebra.getDescription",
        setup=_SETUP,
        call="alg.getDescription()",
        description="getDescription when unset is null",
        **_NONE
    ),
    TestCaseSpec(
        id="alg_set_description",
        method="Algebra.setDescription",
        setup=_SETUP + "\nalg.setDescription('notes')\n",
        call="alg.getDescription()",
        description="setDescription then getDescription",
    ),
    TestCaseSpec(
        id="alg_similarity_type",
        method="Algebra.similarityType",
        setup=_SETUP,
        call="alg.similarityType()",
        description="similarityType of xor algebra",
    ),
    TestCaseSpec(
        id="alg_update_similarity_type",
        method="Algebra.updateSimilarityType",
        setup=_SETUP,
        call="alg.updateSimilarityType()",
        description="updateSimilarityType is void",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="alg_is_similar_to_self",
        method="Algebra.isSimilarTo",
        setup=_SETUP,
        call="alg.isSimilarTo(alg)",
        description="algebra is similar to itself",
        **_BOOL
    ),
    TestCaseSpec(
        id="alg_is_similar_to_other",
        method="Algebra.isSimilarTo",
        setup=_SETUP,
        call="alg.isSimilarTo(alg_id)",
        description="xor is not similar to unary id",
        **_BOOL
    ),
    TestCaseSpec(
        id="alg_is_similar_to_null",
        method="Algebra.isSimilarTo",
        setup=_SETUP,
        call="alg.isSimilarTo(None)",
        description="isSimilarTo(null) raises NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="alg_make_operation_tables",
        method="Algebra.makeOperationTables",
        setup=_SETUP,
        call="alg.makeOperationTables()",
        description="makeOperationTables is void",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="alg_constant_operations_empty",
        method="Algebra.constantOperations",
        setup=_SETUP,
        call="len(alg.constantOperations())",
        description="xor algebra has no constant operations",
    ),
    TestCaseSpec(
        id="alg_constant_operations_one",
        method="Algebra.constantOperations",
        setup=_SETUP,
        call="alg_const.constantOperations()",
        description="constantOperations for arity-0 op",
        **_OP
    ),
    TestCaseSpec(
        id="alg_is_idempotent_xor",
        method="Algebra.isIdempotent",
        setup=_SETUP,
        call="alg.isIdempotent()",
        description="xor algebra is not idempotent",
        **_BOOL
    ),
    TestCaseSpec(
        id="alg_is_idempotent_and",
        method="Algebra.isIdempotent",
        setup=_SETUP,
        call="alg_and.isIdempotent()",
        description="AND algebra is idempotent",
        **_BOOL
    ),
    TestCaseSpec(
        id="alg_is_total",
        method="Algebra.isTotal",
        setup=_SETUP,
        call="alg.isTotal()",
        description="table xor algebra is total",
        **_BOOL
    ),
    TestCaseSpec(
        id="alg_monitoring_default",
        method="Algebra.monitoring",
        setup=_SETUP,
        call="alg.monitoring()",
        description="monitoring default is false",
        **_BOOL
    ),
    TestCaseSpec(
        id="alg_get_monitor_default",
        method="Algebra.getMonitor",
        setup=_SETUP,
        call="alg.getMonitor()",
        description="getMonitor default is null",
        **_NONE
    ),
    TestCaseSpec(
        id="alg_set_monitor",
        method="Algebra.setMonitor",
        setup=_SETUP,
        call="alg.setMonitor('rpt')",
        description="setMonitor(non-ProgressReport) raises TypeError",
        expected_exception="TypeError",
    ),
    TestCaseSpec(
        id="alg_monitoring_after_set",
        method="Algebra.monitoring",
        setup=_SETUP + """
try:
    alg.setMonitor('rpt')
except Exception:
    pass
""",
        call="alg.monitoring()",
        description="monitoring stays false after rejected setMonitor",
        **_BOOL
    ),
    TestCaseSpec(
        id="small_algebra_type",
        method="SmallAlgebra.algebraType",
        setup=_SETUP,
        call="str(alg.algebraType())",
        description="algebraType is BASIC",
    ),
    TestCaseSpec(
        id="small_get_element",
        method="SmallAlgebra.getElement",
        setup=_SETUP,
        call="alg.getElement(1)",
        description="getElement(1) on int universe",
    ),
    TestCaseSpec(
        id="small_get_element_unbounded",
        method="SmallAlgebra.getElement",
        setup=_SETUP,
        call="alg.getElement(99)",
        description="int-universe getElement ignores bounds",
    ),
    TestCaseSpec(
        id="small_get_element_null",
        method="SmallAlgebra.getElement",
        setup=_SETUP,
        call="alg.getElement(None)",
        description="getElement(null) raises TypeError (Jython cannot coerce None to int)",
        expected_exception="TypeError",
    ),
    TestCaseSpec(
        id="small_element_index",
        method="SmallAlgebra.elementIndex",
        setup=_SETUP,
        call="alg.elementIndex(1)",
        description="elementIndex of 1",
    ),
    TestCaseSpec(
        id="small_element_index_oob",
        method="SmallAlgebra.elementIndex",
        setup=_SETUP,
        call="alg.elementIndex(9)",
        description="elementIndex out of range is -1",
    ),
    TestCaseSpec(
        id="small_element_index_cast",
        method="SmallAlgebra.elementIndex",
        setup=_SETUP,
        call='alg.elementIndex("x")',
        description="elementIndex ClassCast on int universe is -1",
    ),
    TestCaseSpec(
        id="small_element_index_null",
        method="SmallAlgebra.elementIndex",
        setup=_SETUP,
        call="alg.elementIndex(None)",
        description="elementIndex(null) raises NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="small_get_universe_list_int",
        method="SmallAlgebra.getUniverseList",
        setup=_SETUP,
        call="alg.getUniverseList()",
        description="int-universe getUniverseList is null",
        **_NONE
    ),
    TestCaseSpec(
        id="small_get_universe_order_int",
        method="SmallAlgebra.getUniverseOrder",
        setup=_SETUP,
        call="alg.getUniverseOrder()",
        description="int-universe getUniverseOrder is null",
        **_NONE
    ),
    TestCaseSpec(
        id="small_get_universe_list_list",
        method="SmallAlgebra.getUniverseList",
        setup=_SETUP,
        call="alg_list.getUniverseList()",
        description="list-universe getUniverseList",
        **_LIST
    ),
    TestCaseSpec(
        id="small_get_element_list",
        method="SmallAlgebra.getElement",
        setup=_SETUP,
        call="alg_list.getElement(1)",
        description="getElement on list universe",
    ),
    TestCaseSpec(
        id="small_get_element_list_oob",
        method="SmallAlgebra.getElement",
        setup=_SETUP,
        call="alg_list.getElement(9)",
        description="list-universe getElement OOB",
        expected_exception="IndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="small_element_index_list_missing",
        method="SmallAlgebra.elementIndex",
        setup=_SETUP,
        call='alg_list.elementIndex("missing")',
        description="list-universe missing element NPEs",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="small_con",
        method="SmallAlgebra.con",
        setup=_SETUP,
        call="alg.con().cardinality()",
        description="con() congruence lattice cardinality",
    ),
    TestCaseSpec(
        id="small_sub",
        method="SmallAlgebra.sub",
        setup=_SETUP,
        call="alg.sub().cardinality()",
        description="sub() subalgebra lattice cardinality",
    ),
    TestCaseSpec(
        id="small_reset_con_and_sub",
        method="SmallAlgebra.resetConAndSub",
        setup=_SETUP,
        call="alg.resetConAndSub()",
        description="resetConAndSub is void",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="small_parent",
        method="SmallAlgebra.parent",
        setup=_SETUP,
        call="alg.parent()",
        description="BasicAlgebra parent is null",
        **_NONE
    ),
    TestCaseSpec(
        id="small_parents",
        method="SmallAlgebra.parents",
        setup=_SETUP,
        call="alg.parents()",
        description="BasicAlgebra parents is null",
        **_NONE
    ),
    TestCaseSpec(
        id="small_convert_default_ops",
        method="SmallAlgebra.convertToDefaultValueOps",
        setup=_SETUP + "\nalg.convertToDefaultValueOps()\n",
        call='alg.getOperation(OperationSymbol("xor", 2)).intValueAt([1, 0])',
        description="convertToDefaultValueOps preserves xor values",
    ),
    TestCaseSpec(
        id="basic_int_universe",
        method="BasicAlgebra.intUniverse",
        setup=_SETUP,
        call="alg.intUniverse()",
        description="int constructor reports intUniverse",
        **_BOOL
    ),
    TestCaseSpec(
        id="basic_list_int_universe",
        method="BasicAlgebra.intUniverse",
        setup=_SETUP,
        call="alg_list.intUniverse()",
        description="list constructor is not intUniverse",
        **_BOOL
    ),
    TestCaseSpec(
        id="basic_set_universe_list",
        method="BasicAlgebra.setUniverseList",
        setup=_SETUP + "\nalg_list.setUniverseList(['x', 'y'])\n",
        call="alg_list.getUniverseList()",
        description="setUniverseList then getUniverseList",
        **_LIST
    ),
    TestCaseSpec(
        id="basic_set_universe_order",
        method="BasicAlgebra.setUniverseOrder",
        setup=_SETUP + "\nalg_list.setUniverseOrder(None)\n",
        call="alg_list.getUniverseOrder()",
        description="setUniverseOrder(null)",
        **_NONE
    ),
    TestCaseSpec(
        id="basic_empty_cardinality",
        method="BasicAlgebra.cardinality",
        setup=_SETUP,
        call="alg_empty.cardinality()",
        description="empty-ops algebra cardinality",
    ),
    TestCaseSpec(
        id="io_roundtrip_write_read",
        method="AlgebraIO.writeAlgebraFile",
        setup=r"""
import os, tempfile
from org.uacalc.alg import BasicAlgebra
from org.uacalc.alg.op import Operations, OperationSymbol
from org.uacalc.io import AlgebraIO
make = getattr(Operations, "makeIntOperation", None)
if make is None:
    make = Operations.make_int_operation
op = make(OperationSymbol("xor", 2), 2, [0, 1, 1, 0])
alg = BasicAlgebra("Xor2", 2, [op])
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(alg, path)
result = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="result",
        description="write algebra in this runtime then read it back",
        **_ALG
    ),
    TestCaseSpec(
        id="io_read_cyclic2_as_small",
        method="SmallAlgebra.getName",
        setup=_SETUP,
        call='AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")',
        description="AlgebraIO-loaded algebra as SmallAlgebra/BasicAlgebra",
        **_ALG
    ),
]
