"""Golden parity cases for Subalgebra, ProductAlgebra, PowerAlgebra, Quotient, SubProduct."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import (
    ProductAlgebra, PowerAlgebra, QuotientAlgebra, Subalgebra,
    SubProductAlgebra, BigProductAlgebra, SmallAlgebra,
)
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.util import IntArray
from org.uacalc.alg.conlat import Partition
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
plus = OperationSymbol("+", 2)
prod = ProductAlgebra("C2xC2", [c2, c2])
prod_list = ProductAlgebra([c2, c2])
pwr = PowerAlgebra("C2^2", c2, 2)
pwr_unnamed = PowerAlgebra(c2, 2)
s0 = Subalgebra("S0", c2, [0])
full = Subalgebra(c2, [0, 1])
cong = c2.con().Cg(0, 1)
zero_cong = c2.con().zero()
q = QuotientAlgebra("Q", c2, cong)
q_unnamed = QuotientAlgebra(c2, cong)
q_zero = QuotientAlgebra("Qz", c2, zero_cong)
bp = BigProductAlgebra(c2, 2)
sp = SubProductAlgebra("SP", bp, [IntArray([0, 0]), IntArray([1, 1])])

def _tbl(alg):
    op = alg.getOperation(plus)
    n = int(alg.cardinality())
    return [int(op.intValueAt([i, j])) for i in range(n) for j in range(n)]

def _elems(alg):
    n = int(alg.cardinality())
    out = []
    for i in range(n):
        el = alg.getElement(i)
        try:
            out.append([int(x) for x in list(el)])
        except TypeError:
            out.append(el if not hasattr(el, "toString") else str(el))
    return out
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_OP = dict(skip_string_check=True, notes="Java Operation toString is Class@hex; values compared.")
_LIST = dict(skip_string_check=True, notes="Java List/Set toString vs Python list.")
_ALG = dict(skip_string_check=True, notes="Java Algebra toString is Class@hex; values compared.")
_LAT = dict(skip_string_check=True, notes="Java lattice toString is Class@hex; values compared.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")

TEST_CASES = [
    TestCaseSpec(
        id="prod_named_card",
        method="ProductAlgebra.cardinality",
        setup=_SETUP,
        call="prod.cardinality()",
        description="named ProductAlgebra(c2,c2) has cardinality 4",
    ),
    TestCaseSpec(
        id="prod_list_card",
        method="ProductAlgebra.cardinality",
        setup=_SETUP,
        call="prod_list.cardinality()",
        description="ProductAlgebra([c2,c2]) cardinality 4",
    ),
    TestCaseSpec(
        id="prod_get_name",
        method="ProductAlgebra.getName",
        setup=_SETUP,
        call="prod.getName()",
        description="named product getName",
    ),
    TestCaseSpec(
        id="prod_set_name",
        method="ProductAlgebra.setName",
        setup=_SETUP + "\nprod.setName('P')\n",
        call="prod.getName()",
        description="product setName then getName",
    ),
    TestCaseSpec(
        id="prod_algebra_type",
        method="ProductAlgebra.algebraType",
        setup=_SETUP,
        call="str(prod.algebraType())",
        description="product algebraType is PRODUCT",
    ),
    TestCaseSpec(
        id="prod_number_of_factors",
        method="ProductAlgebra.numberOfFactors",
        setup=_SETUP,
        call="len(list(prod.factors()))",
        description="product of two factors",
    ),
    TestCaseSpec(
        id="prod_calc_card",
        method="ProductAlgebra.calcCard",
        setup=_SETUP,
        call="ProductAlgebra.calcCard([2, 2])",
        description="calcCard([2,2]) is 4",
    ),
    TestCaseSpec(
        id="prod_calc_card_zero",
        method="ProductAlgebra.calcCard",
        setup=_SETUP,
        call="ProductAlgebra.calcCard([2, 0, 3])",
        description="calcCard with an empty factor is 0",
    ),
    TestCaseSpec(
        id="prod_calc_card_empty",
        method="ProductAlgebra.calcCard",
        setup=_SETUP,
        call="ProductAlgebra.calcCard([])",
        description="Java empty product cardinality is 1",
        xfail_reason="owner: uacalc_lib ProductAlgebra.calc_card_safe rejects empty sizes; Java returns 1",
    ),
    TestCaseSpec(
        id="prod_empty_ctor",
        method="ProductAlgebra.cardinality",
        setup=_SETUP,
        call="ProductAlgebra([]).cardinality()",
        description="Java ProductAlgebra([]) throws IOBE in makeOperations",
        expected_exception="IndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="prod_get_element",
        method="ProductAlgebra.getElement",
        setup=_SETUP,
        call="[list(prod.getElement(i)) for i in range(prod.cardinality())]",
        description="getElement is Horner.hornerInv tuples",
        **_LIST
    ),
    TestCaseSpec(
        id="prod_element_index",
        method="ProductAlgebra.elementIndex",
        setup=_SETUP,
        call="prod.elementIndex(IntArray([1, 0]))",
        description="elementIndex(IntArray) is Horner encoding",
    ),
    TestCaseSpec(
        id="prod_element_index_not_int_array",
        method="ProductAlgebra.elementIndex",
        setup=_SETUP,
        call="prod.elementIndex([1, 0])",
        description="elementIndex(non-IntArray) is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="prod_universe_list",
        method="ProductAlgebra.getUniverseList",
        setup=_SETUP,
        call="[list(row) for row in prod.getUniverseList()]",
        description="universe list last-index-fastest",
        **_LIST
    ),
    TestCaseSpec(
        id="prod_universe_order",
        method="ProductAlgebra.getUniverseOrder",
        setup=_SETUP,
        call="prod.getUniverseOrder()",
        description="product getUniverseOrder is null",
        **_NONE
    ),
    TestCaseSpec(
        id="prod_factors",
        method="ProductAlgebra.factors",
        setup=_SETUP,
        call="[a.getName() for a in prod.factors()]",
        description="factors names",
        **_LIST
    ),
    TestCaseSpec(
        id="prod_parents",
        method="ProductAlgebra.parents",
        setup=_SETUP,
        call="[a.cardinality() for a in prod.parents()]",
        description="parents match factor cardinalities",
        **_LIST
    ),
    TestCaseSpec(
        id="prod_parent",
        method="ProductAlgebra.parent",
        setup=_SETUP,
        call="prod.parent()",
        description="product parent is null",
        **_NONE
    ),
    TestCaseSpec(
        id="prod_projection",
        method="ProductAlgebra.projection",
        setup=_SETUP,
        call="prod.projection(1).cardinality()",
        description="projection of a factor",
    ),
    TestCaseSpec(
        id="prod_projection_oob",
        method="ProductAlgebra.projection",
        setup=_SETUP,
        call="prod.projection(9)",
        description="projection out of range",
        expected_exception="IndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="prod_projection_kernel",
        method="ProductAlgebra.projectionKernel",
        setup=_SETUP,
        call="prod.projectionKernel(0)",
        description="projectionKernel is an unfinished Java stub (null)",
        **_NONE
    ),
    TestCaseSpec(
        id="prod_sg_close",
        method="ProductAlgebra.sgClose",
        setup=_SETUP,
        call="prod.sgClose([])",
        description="sgClose is an unfinished Java stub (empty)",
        **_LIST
    ),
    TestCaseSpec(
        id="prod_op_table",
        method="ProductAlgebra.getOperation",
        setup=_SETUP,
        call="_tbl(prod)",
        description="product + table",
        **_LIST
    ),
    TestCaseSpec(
        id="prod_make_tables",
        method="ProductAlgebra.makeOperationTables",
        setup=_SETUP + "\nprod.makeOperationTables()\n",
        call="_tbl(prod)",
        description="makeOperationTables then + table",
        **_LIST
    ),
    TestCaseSpec(
        id="prod_convert_uoe",
        method="ProductAlgebra.convertToDefaultValueOps",
        setup=_SETUP,
        call="prod.convertToDefaultValueOps()",
        description="convertToDefaultValueOps is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="prod_con",
        method="ProductAlgebra.con",
        setup=_SETUP,
        call="prod.con().cardinality()",
        description="product congruence lattice cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="prod_sub",
        method="ProductAlgebra.sub",
        setup=_SETUP,
        call="prod.sub().cardinality()",
        description="product subalgebra lattice cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="prod_sg",
        method="ProductAlgebra.Sg",
        setup=_SETUP,
        call="prod.Sg([IntArray([0, 0])]).cardinality()",
        description="Sg of the zero tuple",
    ),
    TestCaseSpec(
        id="pwr_named_card",
        method="PowerAlgebra.cardinality",
        setup=_SETUP,
        call="pwr.cardinality()",
        description="PowerAlgebra C2^2 cardinality 4",
    ),
    TestCaseSpec(
        id="pwr_unnamed_card",
        method="PowerAlgebra.cardinality",
        setup=_SETUP,
        call="pwr_unnamed.cardinality()",
        description="PowerAlgebra(c2, 2) cardinality 4",
    ),
    TestCaseSpec(
        id="pwr_unnamed_name",
        method="PowerAlgebra.getName",
        setup=_SETUP,
        call="pwr_unnamed.getName()",
        description="2-arg PowerAlgebra default name is empty",
    ),
    TestCaseSpec(
        id="pwr_algebra_type",
        method="PowerAlgebra.algebraType",
        setup=_SETUP,
        call="str(pwr.algebraType())",
        description="power algebraType is POWER",
    ),
    TestCaseSpec(
        id="pwr_get_power",
        method="PowerAlgebra.getPower",
        setup=_SETUP,
        call="pwr.getPower()",
        description="getPower is 2",
    ),
    TestCaseSpec(
        id="pwr_get_root",
        method="PowerAlgebra.getRoot",
        setup=_SETUP,
        call="pwr.getRoot().getName()",
        description="getRoot is c2",
        **_ALG
    ),
    TestCaseSpec(
        id="pwr_parent",
        method="PowerAlgebra.parent",
        setup=_SETUP,
        call="pwr.parent().getName()",
        description="power parent is the root",
        **_ALG
    ),
    TestCaseSpec(
        id="pwr_parents",
        method="PowerAlgebra.parents",
        setup=_SETUP,
        call="[a.getName() for a in pwr.parents()]",
        description="power parents is a singleton list of the root",
        **_LIST
    ),
    TestCaseSpec(
        id="pwr_get_element",
        method="PowerAlgebra.getElement",
        setup=_SETUP,
        call="[list(pwr.getElement(i)) for i in range(pwr.cardinality())]",
        description="power getElement Horner tuples",
        **_LIST
    ),
    TestCaseSpec(
        id="pwr_element_index",
        method="PowerAlgebra.elementIndex",
        setup=_SETUP,
        call="pwr.elementIndex(IntArray([0, 1]))",
        description="Java PowerAlgebra.elementIndex is always -1 (universe iterator yields ArrayLists)",
    ),
    TestCaseSpec(
        id="pwr_universe_list",
        method="PowerAlgebra.getUniverseList",
        setup=_SETUP,
        call="[list(row) for row in pwr.getUniverseList()]",
        description="power universe list last-index-fastest",
        **_LIST
    ),
    TestCaseSpec(
        id="pwr_convert_uoe",
        method="PowerAlgebra.convertToDefaultValueOps",
        setup=_SETUP,
        call="pwr.convertToDefaultValueOps()",
        description="power convertToDefaultValueOps is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="pwr_zero",
        method="PowerAlgebra.cardinality",
        setup=_SETUP,
        call="PowerAlgebra(c2, 0).cardinality()",
        description="Java PowerAlgebra(alg, 0) throws IOBE in makeOperations",
        expected_exception="IndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="pwr_con",
        method="PowerAlgebra.con",
        setup=_SETUP,
        call="pwr.con().cardinality()",
        description="power congruence lattice cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="pwr_sub",
        method="PowerAlgebra.sub",
        setup=_SETUP,
        call="pwr.sub().cardinality()",
        description="power subalgebra lattice cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="sub_named_card",
        method="Subalgebra.cardinality",
        setup=_SETUP,
        call="s0.cardinality()",
        description="singleton subalgebra cardinality 1",
    ),
    TestCaseSpec(
        id="sub_full_card",
        method="Subalgebra.cardinality",
        setup=_SETUP,
        call="full.cardinality()",
        description="full subalgebra cardinality 2",
    ),
    TestCaseSpec(
        id="sub_algebra_type",
        method="Subalgebra.algebraType",
        setup=_SETUP,
        call="str(s0.algebraType())",
        description="subalgebra algebraType is SUBALGEBRA",
    ),
    TestCaseSpec(
        id="sub_subuniv",
        method="Subalgebra.getSubuniverseArray",
        setup=_SETUP,
        call="list(s0.getSubuniverseArray())",
        description="getSubuniverseArray of {0}",
        **_LIST
    ),
    TestCaseSpec(
        id="sub_index_found",
        method="Subalgebra.index",
        setup=_SETUP,
        call="s0.index(0)",
        description="index of a present super-element",
    ),
    TestCaseSpec(
        id="sub_index_missing",
        method="Subalgebra.index",
        setup=_SETUP,
        call="s0.index(1)",
        description="missing index is Java Arrays.binarySearch encoding",
    ),
    TestCaseSpec(
        id="sub_get_element",
        method="Subalgebra.getElement",
        setup=_SETUP,
        call="s0.getElement(0)",
        description="getElement delegates to the super algebra",
    ),
    TestCaseSpec(
        id="sub_get_element_oob",
        method="Subalgebra.getElement",
        setup=_SETUP,
        call="s0.getElement(3)",
        description="getElement OOB is ArrayIndexOutOfBoundsException",
        expected_exception="ArrayIndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="sub_element_index",
        method="Subalgebra.elementIndex",
        setup=_SETUP,
        call="s0.elementIndex(0)",
        description="elementIndex of a super element in the subalgebra",
    ),
    TestCaseSpec(
        id="sub_universe_list",
        method="Subalgebra.getUniverseList",
        setup=_SETUP,
        call="s0.getUniverseList()",
        description="Subalgebra getUniverseList is null",
        **_NONE
    ),
    TestCaseSpec(
        id="sub_super",
        method="Subalgebra.superAlgebra",
        setup=_SETUP,
        call="s0.superAlgebra().getName()",
        description="superAlgebra is c2",
        **_ALG
    ),
    TestCaseSpec(
        id="sub_op_table",
        method="Subalgebra.getOperation",
        setup=_SETUP,
        call="_tbl(s0)",
        description="restricted + table on the singleton",
        **_LIST
    ),
    TestCaseSpec(
        id="sub_convert_uoe",
        method="Subalgebra.convertToDefaultValueOps",
        setup=_SETUP,
        call="s0.convertToDefaultValueOps()",
        description="Subalgebra convertToDefaultValueOps is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sub_con",
        method="Subalgebra.con",
        setup=_SETUP,
        call="s0.con().cardinality()",
        description="singleton subalgebra con cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="sub_sub",
        method="Subalgebra.sub",
        setup=_SETUP,
        call="s0.sub().cardinality()",
        description="singleton subalgebra sub cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="sub_restrict_partition",
        method="Subalgebra.restrictPartition",
        setup=_SETUP,
        call="str(full.restrictPartition(cong))",
        description="restrict the total congruence to the full subalgebra",
    ),
    TestCaseSpec(
        id="sub_congruence_as_algebra",
        method="Subalgebra.congruenceAsAlgebra",
        setup=_SETUP,
        call="[Subalgebra.congruenceAsAlgebra(c2, cong).cardinality(), list(Subalgebra.congruenceAsAlgebra(c2, cong).getSubuniverseArray())]",
        description="total congruence as a subalgebra of A^2",
        **_LIST
    ),
    TestCaseSpec(
        id="sub_universe",
        method="Subalgebra.universe",
        setup=_SETUP,
        call="list(s0.universe())",
        description="subalgebra universe iterates getElement",
        **_LIST
    ),
    TestCaseSpec(
        id="quot_card",
        method="QuotientAlgebra.cardinality",
        setup=_SETUP,
        call="q.cardinality()",
        description="C2 / total congruence has cardinality 1",
    ),
    TestCaseSpec(
        id="quot_zero_card",
        method="QuotientAlgebra.cardinality",
        setup=_SETUP,
        call="q_zero.cardinality()",
        description="C2 / zero congruence has cardinality 2",
    ),
    TestCaseSpec(
        id="quot_unnamed_name",
        method="QuotientAlgebra.getName",
        setup=_SETUP,
        call="q_unnamed.getName()",
        description="2-arg QuotientAlgebra default name is empty",
    ),
    TestCaseSpec(
        id="quot_algebra_type",
        method="QuotientAlgebra.algebraType",
        setup=_SETUP,
        call="str(q.algebraType())",
        description="quotient algebraType is QUOTIENT",
    ),
    TestCaseSpec(
        id="quot_super",
        method="QuotientAlgebra.superAlgebra",
        setup=_SETUP,
        call="q.superAlgebra().getName()",
        description="quotient superAlgebra is c2",
        **_ALG
    ),
    TestCaseSpec(
        id="quot_congruence",
        method="QuotientAlgebra.getCongruence",
        setup=_SETUP,
        call="str(q.getCongruence())",
        description="getCongruence toString",
    ),
    TestCaseSpec(
        id="quot_get_element",
        method="QuotientAlgebra.getElement",
        setup=_SETUP,
        call="str(q.getElement(0))",
        description="getElement is a QuotientElement",
    ),
    TestCaseSpec(
        id="quot_element_index",
        method="QuotientAlgebra.elementIndex",
        setup=_SETUP,
        call="q_zero.elementIndex(1)",
        description="Java elementIndex returns a super representative, not the quotient index",
    ),
    TestCaseSpec(
        id="quot_rep_index",
        method="QuotientAlgebra.representativeIndex",
        setup=_SETUP,
        call="q_zero.representativeIndex(1)",
        description="representativeIndex is binarySearch on representatives",
    ),
    TestCaseSpec(
        id="quot_canonical",
        method="QuotientAlgebra.canonicalHomomorphism",
        setup=_SETUP,
        call="[q_zero.canonicalHomomorphism(0), q_zero.canonicalHomomorphism(1)]",
        description="canonicalHomomorphism of each super element",
        **_LIST
    ),
    TestCaseSpec(
        id="quot_universe_list",
        method="QuotientAlgebra.getUniverseList",
        setup=_SETUP,
        call="q.getUniverseList()",
        description="QuotientAlgebra getUniverseList is null",
        **_NONE
    ),
    TestCaseSpec(
        id="quot_universe",
        method="QuotientAlgebra.universe",
        setup=_SETUP,
        call="list(q_zero.universe())",
        description="universe iterates super representatives, not QuotientElements",
        **_LIST
    ),
    TestCaseSpec(
        id="quot_op_table",
        method="QuotientAlgebra.getOperation",
        setup=_SETUP,
        call="_tbl(q_zero)",
        description="quotient + table on C2/zero",
        **_LIST
    ),
    TestCaseSpec(
        id="quot_convert_uoe",
        method="QuotientAlgebra.convertToDefaultValueOps",
        setup=_SETUP,
        call="q.convertToDefaultValueOps()",
        description="quotient convertToDefaultValueOps is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="quot_con",
        method="QuotientAlgebra.con",
        setup=_SETUP,
        call="q_zero.con().cardinality()",
        description="quotient congruence lattice cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="quot_sub",
        method="QuotientAlgebra.sub",
        setup=_SETUP,
        call="q_zero.sub().cardinality()",
        description="quotient subalgebra lattice cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="qe_to_string",
        method="QuotientElement.toString",
        setup=_SETUP,
        call="q.getElement(0).toString()",
        description="QuotientElement toString is elem/congruence",
    ),
    TestCaseSpec(
        id="qe_get_index",
        method="QuotientElement.getIndex",
        setup=_SETUP,
        call="q.getElement(0).getIndex()",
        description="QuotientElement getIndex",
    ),
    TestCaseSpec(
        id="qe_get_index_in_super",
        method="QuotientElement.getIndexInSuperAlgebra",
        setup=_SETUP,
        call="q.getElement(0).getIndexInSuperAlgebra()",
        description="QuotientElement getIndexInSuperAlgebra",
    ),
    TestCaseSpec(
        id="qe_get_algebra",
        method="QuotientElement.getAlgebra",
        setup=_SETUP,
        call="q.getElement(0).getAlgebra().getName()",
        description="QuotientElement getAlgebra",
        **_ALG
    ),
    TestCaseSpec(
        id="qe_super",
        method="QuotientElement.superAlgebra",
        setup=_SETUP,
        call="q.getElement(0).superAlgebra().getName()",
        description="QuotientElement superAlgebra",
        **_ALG
    ),
    TestCaseSpec(
        id="qe_congruence",
        method="QuotientElement.getCongruence",
        setup=_SETUP,
        call="str(q.getElement(0).getCongruence())",
        description="QuotientElement getCongruence",
    ),
    TestCaseSpec(
        id="sp_card",
        method="SubProductAlgebra.cardinality",
        setup=_SETUP,
        call="sp.cardinality()",
        description="diagonal subproduct of C2^2 has cardinality 2",
    ),
    TestCaseSpec(
        id="sp_algebra_type",
        method="SubProductAlgebra.algebraType",
        setup=_SETUP,
        call="str(sp.algebraType())",
        description="subproduct algebraType is SUBPRODUCT",
    ),
    TestCaseSpec(
        id="sp_generators",
        method="SubProductAlgebra.generators",
        setup=_SETUP,
        call="[list(g.to_array() if hasattr(g, 'to_array') else g.getArray()) for g in sp.generators()]",
        description="subproduct generators",
        **_LIST
    ),
    TestCaseSpec(
        id="sp_universe_list",
        method="SubProductAlgebra.getUniverseList",
        setup=_SETUP,
        call="[list(row.to_array() if hasattr(row, 'to_array') else row.getArray()) for row in sp.getUniverseList()]",
        description="subproduct universe list",
        **_LIST
    ),
    TestCaseSpec(
        id="sp_get_element",
        method="SubProductAlgebra.getElement",
        setup=_SETUP,
        call="[list(sp.getElement(i).to_array() if hasattr(sp.getElement(i), 'to_array') else sp.getElement(i).getArray()) for i in range(sp.cardinality())]",
        description="subproduct getElement is IntArray",
        **_LIST
    ),
    TestCaseSpec(
        id="sp_element_index",
        method="SubProductAlgebra.elementIndex",
        setup=_SETUP,
        call="sp.elementIndex(IntArray([1, 1]))",
        description="subproduct elementIndex of a generator",
    ),
    TestCaseSpec(
        id="sp_product_algebra",
        method="SubProductAlgebra.getProductAlgebra",
        setup=_SETUP,
        call="sp.getProductAlgebra().getNumberOfFactors()",
        description="getProductAlgebra factor count",
    ),
    TestCaseSpec(
        id="sp_super",
        method="SubProductAlgebra.superAlgebra",
        setup=_SETUP,
        call="sp.superAlgebra().getNumberOfFactors()",
        description="superAlgebra is the big product",
    ),
    TestCaseSpec(
        id="sp_get_terms",
        method="SubProductAlgebra.getTerms",
        setup=_SETUP,
        call="sp.getTerms()",
        description="getTerms is null when findTerms is false",
        **_NONE
    ),
    TestCaseSpec(
        id="sp_op_table",
        method="SubProductAlgebra.getOperation",
        setup=_SETUP,
        call="_tbl(sp)",
        description="subproduct + table",
        **_LIST
    ),
    TestCaseSpec(
        id="sp_convert_uoe",
        method="SubProductAlgebra.convertToDefaultValueOps",
        setup=_SETUP,
        call="sp.convertToDefaultValueOps()",
        description="subproduct convertToDefaultValueOps is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="sp_con",
        method="SubProductAlgebra.con",
        setup=_SETUP,
        call="sp.con().cardinality()",
        description="subproduct congruence lattice cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="sp_sub",
        method="SubProductAlgebra.sub",
        setup=_SETUP,
        call="sp.sub().cardinality()",
        description="subproduct subalgebra lattice cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="prod_roundtrip_write_read",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(prod, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality(), _tbl(read), read.con().cardinality(), read.sub().cardinality()]",
        description="write ProductAlgebra, read back, compare card/tables/con/sub",
        **_LIST
    ),
    TestCaseSpec(
        id="pwr_roundtrip_write_read",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(pwr, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality(), _tbl(read), read.con().cardinality(), read.sub().cardinality()]",
        description="write PowerAlgebra, read back, compare card/tables/con/sub",
        **_LIST
    ),
    TestCaseSpec(
        id="quot_roundtrip_write_read",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(q_zero, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality(), _tbl(read), read.con().cardinality(), read.sub().cardinality()]",
        description="write QuotientAlgebra, read back, compare card/tables/con/sub",
        **_LIST
    ),
    TestCaseSpec(
        id="sub_roundtrip_write_read",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(full, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality(), _tbl(read), read.con().cardinality(), read.sub().cardinality()]",
        description="write Subalgebra, read back, compare card/tables/con/sub",
        **_LIST
    ),
    TestCaseSpec(
        id="sp_roundtrip_write_read",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(sp, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality(), _tbl(read), read.con().cardinality(), read.sub().cardinality()]",
        description="write SubProductAlgebra, read back, compare card/tables/con/sub",
        **_LIST
    ),
]
