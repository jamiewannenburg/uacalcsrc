"""Golden parity cases for FreeAlgebra, Homomorphism, Closer, and Algebras."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import (
    FreeAlgebra, Homomorphism, Closer, Algebras,
    BigProductAlgebra, ProductAlgebra, SmallAlgebra,
)
from org.uacalc.alg.op import OperationSymbol, Operations, SimilarityType
from org.uacalc.util import IntArray
from org.uacalc.alg.conlat import Partition
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
plus = OperationSymbol("+", 2)
f1 = FreeAlgebra(c2, 1)
f1.setName("F1")
f1thin = FreeAlgebra(c2, 1, True, True)
f1thin.setName("F1thin")
fnamed = FreeAlgebra("NamedF", c2, 1)
bp = BigProductAlgebra(c2, 2)
g00 = IntArray([0, 0])
g11 = IntArray([1, 1])
g01 = IntArray([0, 1])
g10 = IntArray([1, 0])
closer = Closer(bp, [g00, g11])
closer_tm = Closer(bp, [g00, g11], True)
id_map = {0: 0, 1: 1}
h = Homomorphism(c2, c2, id_map)
const0 = Homomorphism(c2, c2, {0: 0, 1: 0})
id1 = Operations.makeIntOperation(OperationSymbol("id", 1), 2, [0, 1])
swap1 = Operations.makeIntOperation(OperationSymbol("swap", 1), 2, [1, 0])
zero_p = c2.con().zero()
one_p = c2.con().one()

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

def _terms(lst):
    if lst is None:
        return None
    return [str(t).replace(" ", "") for t in list(lst)]

def _tbl(alg):
    op = alg.getOperation(plus)
    n = int(alg.cardinality())
    return [int(op.intValueAt([i, j])) for i in range(n) for j in range(n)]

def _tm(m):
    if m is None:
        return None
    items = []
    for k in m:
        items.append([_coords(k), str(m[k]).replace(" ", "")])
    items.sort(key=lambda row: (row[0], row[1]))
    return items

def _hmap(m):
    if m is None:
        return None
    items = []
    for k in m:
        items.append([int(k), int(m[k])])
    items.sort()
    return items

def _homo_img(m):
    if m is None:
        return None
    items = []
    for k in m:
        items.append([_coords(k), int(m[k])])
    items.sort(key=lambda row: (row[0], row[1]))
    return items

def _op_vals(op):
    if op is None:
        return None
    n = int(op.getSetSize()) if hasattr(op, "getSetSize") else int(op.get_set_size())
    return [int(op.intValueAt([i])) for i in range(n)]

def _varmap(alg):
    m = alg.getVariableToGeneratorMap()
    if m is None:
        return None
    items = []
    iterable = m.entrySet() if hasattr(m, "entrySet") else (m.items() if hasattr(m, "items") else None)
    if iterable is not None:
        for item in iterable:
            if hasattr(item, "getKey"):
                k, v = item.getKey(), item.getValue()
            else:
                k, v = item
            items.append([str(k).replace(" ", ""), _coords(v)])
    else:
        for k in m:
            items.append([str(k).replace(" ", ""), _coords(m[k])])
    items.sort()
    return items
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_OP = dict(skip_string_check=True, notes="Java Operation toString is Class@hex; values compared.")
_LIST = dict(skip_string_check=True, notes="Java List/Set toString vs Python list.")
_ALG = dict(skip_string_check=True, notes="Java Algebra toString is Class@hex; values compared.")
_MAP = dict(skip_string_check=True, notes="Java Map toString vs Python dict.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")
_LAT = dict(skip_string_check=True, notes="Java lattice/partition identity toString; values compared.")

TEST_CASES = [
    # --- FreeAlgebra ---
    TestCaseSpec(
        id="fa_card",
        method="FreeAlgebra.cardinality",
        setup=_SETUP,
        call="f1.cardinality()",
        description="FreeAlgebra(c2, 1) cardinality 2",
    ),
    TestCaseSpec(
        id="fa_named_name",
        method="FreeAlgebra.getName",
        setup=_SETUP,
        call="fnamed.getName()",
        description="FreeAlgebra(name, c2, 1) getName",
    ),
    TestCaseSpec(
        id="fa_set_name",
        method="FreeAlgebra.setName",
        setup=_SETUP + "\nf1.setName('F')\n",
        call="f1.getName()",
        description="FreeAlgebra setName then getName",
    ),
    TestCaseSpec(
        id="fa_algebra_type",
        method="FreeAlgebra.algebraType",
        setup=_SETUP,
        call="str(f1.algebraType())",
        description="FreeAlgebra algebraType is FREE",
    ),
    TestCaseSpec(
        id="fa_get_element",
        method="FreeAlgebra.getElement",
        setup=_SETUP,
        call="[_coords(f1.getElement(i)) for i in range(f1.cardinality())]",
        description="F(1) getElement IntArray coords",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_element_index",
        method="FreeAlgebra.elementIndex",
        setup=_SETUP,
        call="[f1.elementIndex(f1.getElement(i)) for i in range(f1.cardinality())]",
        description="F(1) elementIndex round-trip",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_universe_list",
        method="FreeAlgebra.getUniverseList",
        setup=_SETUP,
        call="_ias(f1.getUniverseList())",
        description="F(1) getUniverseList coords",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_get_terms",
        method="FreeAlgebra.getTerms",
        setup=_SETUP,
        call="_terms(f1.getTerms())",
        description="F(1) getTerms",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_get_term",
        method="FreeAlgebra.getTerm",
        setup=_SETUP,
        call="[str(f1.getTerm(f1.getElement(i))).replace(' ', '') for i in range(f1.cardinality())]",
        description="F(1) getTerm per element",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_get_element_from_term",
        method="FreeAlgebra.getElementFromTerm",
        setup=_SETUP,
        call="[_coords(f1.getElementFromTerm(f1.getTerm(f1.getElement(i)))) for i in range(f1.cardinality())]",
        description="F(1) getElementFromTerm round-trip",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_product_algebra",
        method="FreeAlgebra.getProductAlgebra",
        setup=_SETUP,
        call="[f1.getProductAlgebra().cardinality(), f1.getProductAlgebra().getNumberOfFactors()]",
        description="unthinned F(1) product is C2^2",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_super_algebra",
        method="FreeAlgebra.superAlgebra",
        setup=_SETUP,
        call="f1.superAlgebra().cardinality()",
        description="superAlgebra is the product",
        **_ALG
    ),
    TestCaseSpec(
        id="fa_generators",
        method="FreeAlgebra.generators",
        setup=_SETUP,
        call="_ias(f1.generators())",
        description="F(1) generators",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_get_variables",
        method="FreeAlgebra.getVariables",
        setup=_SETUP,
        call="_terms(f1.getVariables())",
        description="F(1) getVariables",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_varmap_c2_f1",
        method="FreeAlgebra.getVariableToGeneratorMap",
        setup=_SETUP,
        call="_varmap(f1)",
        description="F(1) over cyclic2 variable-to-generator map",
        **_MAP
    ),
    TestCaseSpec(
        id="fa_varmap_c2_f2",
        method="FreeAlgebra.getVariableToGeneratorMap",
        setup=_SETUP + "\nf2 = FreeAlgebra(c2, 2)\nf2.setName('F2')\n",
        call="_varmap(f2)",
        description="F(2) over cyclic2 variable-to-generator map",
        **_MAP
    ),
    TestCaseSpec(
        id="fa_idempotent_terms",
        method="FreeAlgebra.getIdempotentTerms",
        setup=_SETUP,
        call="_terms(f1.getIdempotentTerms())",
        description="F(1) getIdempotentTerms is [x]",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_operations",
        method="FreeAlgebra.operations",
        setup=_SETUP,
        call="len(list(f1.operations()))",
        description="F(1) operations count",
    ),
    TestCaseSpec(
        id="fa_get_operation",
        method="FreeAlgebra.getOperation",
        setup=_SETUP,
        call="_tbl(f1)",
        description="F(1) + table",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_thin_card",
        method="FreeAlgebra.cardinality",
        setup=_SETUP,
        call="f1thin.cardinality()",
        description="thinned F(1) cardinality 2",
    ),
    TestCaseSpec(
        id="fa_thin_product",
        method="FreeAlgebra.getProductAlgebra",
        setup=_SETUP,
        call="[f1thin.getProductAlgebra().cardinality(), f1thin.getProductAlgebra().getNumberOfFactors()]",
        description="thinned F(1) product has 1 factor",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_null_report",
        method="FreeAlgebra.cardinality",
        setup=_SETUP,
        call="FreeAlgebra(c2, 1, None).cardinality()",
        description="FreeAlgebra(alg, n, None) is ProgressReport overload",
    ),
    TestCaseSpec(
        id="fa_from_product",
        method="FreeAlgebra.cardinality",
        setup=_SETUP,
        call="FreeAlgebra('FromProd', f1.getProductAlgebra(), f1.generators(), f1.getUniverseList()).cardinality()",
        description="FreeAlgebra(name, prod, gens, univ) cardinality",
    ),
    TestCaseSpec(
        id="fa_switch_xy_one_gen",
        method="FreeAlgebra.switchXandYAutomorphism",
        setup=_SETUP,
        call="f1.switchXandYAutomorphism()",
        description="switchXandYAutomorphism on F(1) is null",
        **_NONE
    ),
    TestCaseSpec(
        id="fa_switch_xy_two_gens",
        method="FreeAlgebra.switchXandYAutomorphism",
        setup=_SETUP + "\nf2 = FreeAlgebra(c2, 2)\nf2.setName('F2')\n",
        call="_op_vals(f2.switchXandYAutomorphism())",
        description="switchXandYAutomorphism on F(2) table",
        **_OP
    ),
    TestCaseSpec(
        id="fa_find_eq_npe",
        method="FreeAlgebra.findEquationOfAnotB",
        setup=_SETUP,
        call="FreeAlgebra.findEquationOfAnotB(c2, c2, [0])",
        description="3-arg findEquationOfAnotB always NPEs (null report)",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="fa_find_eq_report_type",
        method="FreeAlgebra.findEquationOfAnotB",
        setup=_SETUP,
        call="FreeAlgebra.findEquationOfAnotB(c2, c2, [0], 'not-a-report')",
        description="non-None ProgressReport is not bound",
        expected_exception="TypeError",
    ),
    TestCaseSpec(
        id="fa_roundtrip_write_read",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(f1, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality(), _tbl(read), _terms(f1.getTerms())]",
        description="write FreeAlgebra, read back, compare card/table; terms from original",
        skip_string_check=True,
        xfail_reason=(
            "Known Java bug: AlgebraReader has no freeAlgebra end-element "
            "handler, so write-then-read returns the generating algebra (C2 "
            "table [0,1,1,0]) instead of F(1) (table [1,0,0,1]). Python "
            "rebuilds F(n). Java golden values are left unchanged."
        ),
        notes=(
            "Java rereads C2. Python rebuilds F(1). See KNOWN_DIFFERENCES.md."
        ),
    ),
    # --- Homomorphism ---
    TestCaseSpec(
        id="hom_get_domain",
        method="Homomorphism.getDomain",
        setup=_SETUP,
        call="h.getDomain().getName()",
        description="identity homo getDomain name",
        **_ALG
    ),
    TestCaseSpec(
        id="hom_get_range",
        method="Homomorphism.getRange",
        setup=_SETUP,
        call="h.getRange().cardinality()",
        description="identity homo getRange cardinality",
        **_ALG
    ),
    TestCaseSpec(
        id="hom_get_map",
        method="Homomorphism.getMap",
        setup=_SETUP,
        call="_hmap(h.getMap())",
        description="identity homo getMap",
        **_MAP
    ),
    TestCaseSpec(
        id="hom_set_map",
        method="Homomorphism.setMap",
        setup=_SETUP + "\nh.setMap({0: 0, 1: 0})\n",
        call="_hmap(h.getMap())",
        description="setMap then getMap",
        **_MAP
    ),
    TestCaseSpec(
        id="hom_set_domain",
        method="Homomorphism.setDomain",
        setup=_SETUP + "\nh.setDomain(c2)\n",
        call="h.getDomain().cardinality()",
        description="setDomain then getDomain cardinality",
        **_ALG
    ),
    TestCaseSpec(
        id="hom_set_range",
        method="Homomorphism.setRange",
        setup=_SETUP + "\nh.setRange(c2)\n",
        call="h.getRange().getName()",
        description="setRange then getRange name",
        **_ALG
    ),
    TestCaseSpec(
        id="hom_kernel_id",
        method="Homomorphism.kernel",
        setup=_SETUP,
        call="str(h.kernel())",
        description="identity homo kernel is zero",
    ),
    TestCaseSpec(
        id="hom_kernel_const",
        method="Homomorphism.kernel",
        setup=_SETUP,
        call="str(const0.kernel())",
        description="constant homo kernel is one",
    ),
    TestCaseSpec(
        id="hom_kernel_incomplete",
        method="Homomorphism.kernel",
        setup=_SETUP,
        call="str(Homomorphism(c2, c2, {0: 0}).kernel())",
        description="kernel with last key missing does not NPE (Java left-side get only)",
    ),
    TestCaseSpec(
        id="hom_kernel_missing_first",
        method="Homomorphism.kernel",
        setup=_SETUP,
        call="Homomorphism(c2, c2, {1: 1}).kernel()",
        description="kernel NPEs when map.get(i) is null for a non-last i",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="hom_to_string_prefix",
        method="Homomorphism.toString",
        setup=_SETUP,
        call="h.toString().split(' : ')[0]",
        description="toString prefix homomorphism: C2 --> C2",
    ),
    TestCaseSpec(
        id="hom_product_homo",
        method="Homomorphism.productHomo",
        setup=_SETUP,
        call="[_coords(row) for row in Homomorphism.productHomo([h, const0])]",
        description="productHomo of id and const0",
        **_LIST
    ),
    TestCaseSpec(
        id="hom_product_homo_empty",
        method="Homomorphism.productHomo",
        setup=_SETUP,
        call="Homomorphism.productHomo([])",
        description="empty productHomo is IOBE",
        expected_exception="IndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="hom_product_homo_null",
        method="Homomorphism.productHomo",
        setup=_SETUP,
        call="Homomorphism.productHomo(None)",
        description="productHomo(null) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="hom_ctor_null_domain",
        method="Homomorphism.getDomain",
        setup=_SETUP,
        call="Homomorphism(None, c2, id_map)",
        description="Homomorphism(null, range, map) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="hom_ctor_null_map",
        method="Homomorphism.getMap",
        setup=_SETUP,
        call="Homomorphism(c2, c2, None).kernel()",
        description="Homomorphism with null map NPEs in kernel (map.get(i))",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="hom_roundtrip_kernel",
        method="Homomorphism.kernel",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(c2, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
h2 = Homomorphism(read, read, {0: 0, 1: 1})
""",
        call="[str(h.kernel()), str(h2.kernel()), _hmap(h2.getMap())]",
        description="write/read C2, rebuild identity homo, compare kernels and map",
        **_LIST
    ),
    # --- Closer ---
    TestCaseSpec(
        id="cl_get_answer_before",
        method="Closer.getAnswer",
        setup=_SETUP,
        call="closer.getAnswer()",
        description="getAnswer is null before close",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_sg_close",
        method="Closer.sgClose",
        setup=_SETUP,
        call="_ias(closer.sgClose())",
        description="sgClose of diagonal gens in C2^2",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_sg_close_from",
        method="Closer.sgClose",
        setup=_SETUP,
        call="sorted(_ias(Closer(bp, [g00]).sgClose([g00, g11], 0, None)))",
        description="sgClose(elems, closedMark, termMap) from diagonal gens",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_get_answer_after",
        method="Closer.getAnswer",
        setup=_SETUP + "\ncloser.sgClose()\n",
        call="_ias(closer.getAnswer())",
        description="getAnswer after sgClose",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_sg_close_power",
        method="Closer.sgClosePower",
        setup=_SETUP,
        call="_ias(closer.sgClosePower())",
        description="sgClosePower of diagonal gens in C2^2",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_close_power",
        method="Closer.close",
        setup=_SETUP,
        call="_ias(closer.close())",
        description="close() stub copies gens on a power",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_close_not_power",
        method="Closer.close",
        setup=_SETUP + r"""
bp_prod = BigProductAlgebra([c2, c2])
cl_mixed = Closer(bp_prod, [IntArray([0, 0])])
""",
        call="cl_mixed.close()",
        description="close() on a non-power is IAE",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="cl_get_max_size_default",
        method="Closer.getmaxSize",
        setup=_SETUP,
        call="closer.getmaxSize()",
        description="default getmaxSize is -1",
    ),
    TestCaseSpec(
        id="cl_set_max_size",
        method="Closer.setMaxSize",
        setup=_SETUP + "\ncloser.setMaxSize(3)\n",
        call="closer.getmaxSize()",
        description="setMaxSize then getmaxSize",
    ),
    TestCaseSpec(
        id="cl_get_generators",
        method="Closer.getGenerators",
        setup=_SETUP,
        call="_ias(closer.getGenerators())",
        description="getGenerators unique-ifies",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_set_generators",
        method="Closer.setGenerators",
        setup=_SETUP + "\ncloser.setGenerators([g00, g00, g11])\n",
        call="_ias(closer.getGenerators())",
        description="setGenerators drops duplicates, keeps order",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_get_term_map_none",
        method="Closer.getTermMap",
        setup=_SETUP,
        call="closer.getTermMap()",
        description="2-arg ctor leaves termMap null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_get_term_map_made",
        method="Closer.getTermMap",
        setup=_SETUP,
        call="_tm(closer_tm.getTermMap())",
        description="makeTermMap True maps gens to x,y",
        **_MAP
    ),
    TestCaseSpec(
        id="cl_set_term_map",
        method="Closer.setTermMap",
        setup=_SETUP + "\ncloser.setTermMap(closer_tm.getTermMap())\n",
        call="_tm(closer.getTermMap())",
        description="setTermMap copies the map",
        **_MAP
    ),
    TestCaseSpec(
        id="cl_sg_close_term_map",
        method="Closer.getTermMap",
        setup=_SETUP + "\ncloser_tm.sgClose()\n",
        call="_tm(closer_tm.getTermMap())",
        description="term map after sgClose",
        **_MAP
    ),
    TestCaseSpec(
        id="cl_get_element_to_find",
        method="Closer.getElementToFind",
        setup=_SETUP,
        call="closer.getElementToFind()",
        description="default elementToFind is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_set_element_to_find",
        method="Closer.setElementToFind",
        setup=_SETUP + "\ncloser.setElementToFind(g01)\n",
        call="_coords(closer.getElementToFind())",
        description="setElementToFind then get",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_get_elements_to_find",
        method="Closer.getElementsToFind",
        setup=_SETUP,
        call="closer.getElementsToFind()",
        description="default elementsToFind is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_set_elements_to_find",
        method="Closer.setElementsToFind",
        setup=_SETUP + "\ncloser.setElementsToFind([g00, g00, g11], [g00, g11])\n",
        call="_ias(closer.getElementsToFind())",
        description="setElementsToFind unique-ifies",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_all_elements_found",
        method="Closer.allElementsFound",
        setup=_SETUP,
        call="closer.allElementsFound()",
        description="default allElementsFound is false",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_get_blocks",
        method="Closer.getBlocks",
        setup=_SETUP,
        call="closer.getBlocks()",
        description="default blocks is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_set_blocks",
        method="Closer.setBlocks",
        setup=_SETUP + "\ncloser.setBlocks([[0, 1], [1, 0]])\n",
        call="[list(row) for row in closer.getBlocks()]",
        description="setBlocks then getBlocks",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_get_values",
        method="Closer.getValues",
        setup=_SETUP,
        call="closer.getValues()",
        description="default values is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_set_values",
        method="Closer.setValues",
        setup=_SETUP + "\ncloser.setValues([[0, 1], [1, 0]])\n",
        call="[list(row) for row in closer.getValues()]",
        description="setValues then getValues",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_get_set_constraint",
        method="Closer.getSetConstraint",
        setup=_SETUP,
        call="closer.getSetConstraint()",
        description="default set constraint is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_set_constraint_set",
        method="Closer.setConstraintSet",
        setup=_SETUP + r"""
try:
    from java.util import HashSet
    _cs = HashSet()
    _cs.add(0)
    _cs.add(1)
except ImportError:
    _cs = set([0, 1])
closer.setConstraintSet(_cs)
""",
        call="sorted(list(closer.getSetConstraint()))",
        description="setConstraintSet then getSetConstraint",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_get_index_constraint_set",
        method="Closer.getIndexForConstraintSet",
        setup=_SETUP,
        call="closer.getIndexForConstraintSet()",
        description="default indexForConstraintSet is -1",
    ),
    TestCaseSpec(
        id="cl_set_index_constraint_set",
        method="Closer.setIndexForConstraintSet",
        setup=_SETUP + "\ncloser.setIndexForConstraintSet(1)\n",
        call="closer.getIndexForConstraintSet()",
        description="setIndexForConstraintSet then get",
    ),
    TestCaseSpec(
        id="cl_get_index_cong",
        method="Closer.getIndexForCongruenceConstraint",
        setup=_SETUP,
        call="closer.getIndexForCongruenceConstraint()",
        description="default indexForCongruenceConstraint is 0",
    ),
    TestCaseSpec(
        id="cl_set_index_cong",
        method="Closer.setIndexForCongruenceConstraint",
        setup=_SETUP + "\ncloser.setIndexForCongruenceConstraint(1)\n",
        call="closer.getIndexForCongruenceConstraint()",
        description="setIndexForCongruenceConstraint then get",
    ),
    TestCaseSpec(
        id="cl_get_cong_elem_index",
        method="Closer.getCongruenceConstraintElemIndex",
        setup=_SETUP,
        call="closer.getCongruenceConstraintElemIndex()",
        description="default congruenceConstraintElemIndex is 0",
    ),
    TestCaseSpec(
        id="cl_set_cong_elem_index",
        method="Closer.setCongruenceConstraintElemIndex",
        setup=_SETUP + "\ncloser.setCongruenceConstraintElemIndex(1)\n",
        call="closer.getCongruenceConstraintElemIndex()",
        description="setCongruenceConstraintElemIndex then get",
    ),
    TestCaseSpec(
        id="cl_get_cong_constraint",
        method="Closer.getCongruenceForCongruenceConstraint",
        setup=_SETUP,
        call="closer.getCongruenceForCongruenceConstraint()",
        description="default congruence constraint partition is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_set_cong_constraint",
        method="Closer.setCongruenceForCongruenceConstraint",
        setup=_SETUP + "\ncloser.setCongruenceForCongruenceConstraint(zero_p)\n",
        call="str(closer.getCongruenceForCongruenceConstraint())",
        description="setCongruenceForCongruenceConstraint then get",
    ),
    TestCaseSpec(
        id="cl_setup_cong_constraint",
        method="Closer.setupCongruenceConstraint",
        setup=_SETUP + "\ncloser.setupCongruenceConstraint(one_p, 1, 0)\n",
        call="[str(closer.getCongruenceForCongruenceConstraint()), closer.getIndexForCongruenceConstraint(), closer.getCongruenceConstraintElemIndex()]",
        description="setupCongruenceConstraint sets the three fields",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_get_failing_eq",
        method="Closer.getFailingEquation",
        setup=_SETUP,
        call="closer.getFailingEquation()",
        description="default failingEquation is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_get_image_algebra",
        method="Closer.getImageAlgebra",
        setup=_SETUP,
        call="closer.getImageAlgebra()",
        description="default imageAlgebra is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_set_image_algebra",
        method="Closer.setImageAlgebra",
        setup=_SETUP + "\ncloser.setImageAlgebra(c2)\n",
        call="closer.getImageAlgebra().cardinality()",
        description="setImageAlgebra similar C2",
        **_ALG
    ),
    TestCaseSpec(
        id="cl_set_image_algebra_dissimilar",
        method="Closer.setImageAlgebra",
        setup=_SETUP,
        call="closer.setImageAlgebra(AlgebraIO.readAlgebraFile('resources/algebras/lat2.ua'))",
        description="setImageAlgebra dissimilar is IAE",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="cl_get_homomorphism",
        method="Closer.getHomomorphism",
        setup=_SETUP,
        call="closer.getHomomorphism()",
        description="default homomorphism map is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_set_homomorphism_gens",
        method="Closer.setHomomorphism",
        setup=_SETUP + "\ncloser.setHomomorphism([0, 1])\n",
        call="_homo_img(closer.getHomomorphism())",
        description="setHomomorphism(int[]) from gens",
        **_MAP
    ),
    TestCaseSpec(
        id="cl_set_homomorphism_wrong_n",
        method="Closer.setHomomorphism",
        setup=_SETUP,
        call="closer.setHomomorphism([0])",
        description="setHomomorphism wrong length is IAE",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="cl_get_term_map_for_ops",
        method="Closer.getTermMapForOperations",
        setup=_SETUP,
        call="closer.getTermMapForOperations()",
        description="default termMapForOperations is null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_set_root_algebra",
        method="Closer.setRootAlgebra",
        setup=_SETUP + "\ncloser.setRootAlgebra(c2)\n",
        call="True",
        description="setRootAlgebra accepts similar C2",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_set_operations",
        method="Closer.setOperations",
        setup=_SETUP + "\ncloser.setOperations(list(c2.operations()))\n",
        call="True",
        description="setOperations accepts C2 ops",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_is_suppress_output",
        method="Closer.isSuppressOutput",
        setup=_SETUP,
        call="closer.isSuppressOutput()",
        description="default isSuppressOutput is false",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_set_suppress_output",
        method="Closer.setSuppressOutput",
        setup=_SETUP + "\ncloser.setSuppressOutput(True)\n",
        call="closer.isSuppressOutput()",
        description="setSuppressOutput then get",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_ctor_null_alg",
        method="Closer.getGenerators",
        setup=_SETUP,
        call="Closer(None, [g00]).sgClose()",
        description="Closer(null, gens).sgClose() NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="cl_ctor_null_gens",
        method="Closer.getGenerators",
        setup=_SETUP,
        call="Closer(bp, None)",
        description="Closer(alg, null) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="cl_roundtrip_term_map",
        method="Closer.getTermMap",
        setup=_SETUP + r"""
import os, tempfile
closer_tm.sgClose()
prod = f1.getProductAlgebra()
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(f1, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[_tm(closer_tm.getTermMap()), read.cardinality()]",
        description="Closer term map plus FreeAlgebra write/read cardinality",
        **_LIST
    ),
    # --- Algebras ---
    TestCaseSpec(
        id="algs_is_endomorphism_id",
        method="Algebras.isEndomorphism",
        setup=_SETUP,
        call="Algebras.isEndomorphism(id1, c2)",
        description="identity unary is an endomorphism of C2",
        **_BOOL
    ),
    TestCaseSpec(
        id="algs_is_endomorphism_swap",
        method="Algebras.isEndomorphism",
        setup=_SETUP,
        call="Algebras.isEndomorphism(swap1, c2)",
        description="swap unary is not an endomorphism of C2",
        **_BOOL
    ),
    TestCaseSpec(
        id="algs_is_endomorphism_null",
        method="Algebras.isEndomorphism",
        setup=_SETUP,
        call="Algebras.isEndomorphism(None, c2)",
        description="isEndomorphism(null, alg) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="algs_is_homomorphism_id",
        method="Algebras.isHomomorphism",
        setup=_SETUP,
        call="Algebras.isHomomorphism([0, 1], c2, c2)",
        description="identity map is a homomorphism",
        **_BOOL
    ),
    TestCaseSpec(
        id="algs_is_homomorphism_const1",
        method="Algebras.isHomomorphism",
        setup=_SETUP,
        call="Algebras.isHomomorphism([1, 1], c2, c2)",
        description="constant-1 map is not a homomorphism of C2",
        **_BOOL
    ),
    TestCaseSpec(
        id="algs_is_homomorphism_null",
        method="Algebras.isHomomorphism",
        setup=_SETUP,
        call="Algebras.isHomomorphism(None, c2, c2)",
        description="isHomomorphism(null, ...) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="algs_matrix_power",
        method="Algebras.matrixPower",
        setup=_SETUP,
        call="[Algebras.matrixPower(c2, 1).cardinality(), Algebras.matrixPower(c2, 1).getName()]",
        description="matrixPower(c2, 1) card and name",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_matrix_power_zero",
        method="Algebras.matrixPower",
        setup=_SETUP,
        call="Algebras.matrixPower(c2, 0)",
        description="matrixPower k=0 is IOBE",
        expected_exception="IndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="algs_matrix_power_null",
        method="Algebras.matrixPower",
        setup=_SETUP,
        call="Algebras.matrixPower(None, 1)",
        description="matrixPower(null, k) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="algs_full_trans",
        method="Algebras.fullTransformationSemigroup",
        setup=_SETUP,
        call="[Algebras.fullTransformationSemigroup(2, True, True).cardinality(), Algebras.fullTransformationSemigroup(2, True, True).getName()]",
        description="fullTransformationSemigroup n=2",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_full_trans_too_big",
        method="Algebras.fullTransformationSemigroup",
        setup=_SETUP,
        call="Algebras.fullTransformationSemigroup(10, False, False)",
        description="fullTransformationSemigroup n=10 is IAE",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="algs_ternary_disc",
        method="Algebras.ternaryDiscriminatorAlgebra",
        setup=_SETUP,
        call="[Algebras.ternaryDiscriminatorAlgebra(2).cardinality(), Algebras.ternaryDiscriminatorAlgebra(2).getName()]",
        description="ternaryDiscriminatorAlgebra(2)",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_random_arities",
        method="Algebras.makeRandomAlgebra",
        setup=_SETUP,
        call="[Algebras.makeRandomAlgebra(2, [1]).cardinality(), Algebras.makeRandomAlgebra(2, [1]).getName()]",
        description="makeRandomAlgebra(n, arities) name and card only",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_random_simtype_seed",
        method="Algebras.makeRandomAlgebra",
        setup=_SETUP,
        call="[Algebras.makeRandomAlgebra(2, c2.similarityType(), 42).cardinality(), Algebras.makeRandomAlgebra(2, c2.similarityType(), 42).getName()]",
        description="makeRandomAlgebra(n, simType, seed) name and card",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_random_null",
        method="Algebras.makeRandomAlgebra",
        setup=_SETUP,
        call="Algebras.makeRandomAlgebra(2, None)",
        description="makeRandomAlgebra(n, null) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="algs_find_in_clone",
        method="Algebras.findInClone",
        setup=_SETUP,
        call="sorted([[str(k), str(Algebras.findInClone([id1], c2, None)[k]).replace(' ', '')] for k in Algebras.findInClone([id1], c2, None)])",
        description="findInClone identity unary on C2",
        **_MAP
    ),
    TestCaseSpec(
        id="algs_find_in_clone_empty",
        method="Algebras.findInClone",
        setup=_SETUP,
        call="Algebras.findInClone([], c2, None)",
        description="findInClone empty ops is IAE",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="algs_find_in_clone_null",
        method="Algebras.findInClone",
        setup=_SETUP,
        call="Algebras.findInClone(None, c2, None)",
        description="findInClone null ops is IAE",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="algs_member_qv",
        method="Algebras.memberOfQuasivariety",
        setup=_SETUP,
        call="None if Algebras.memberOfQuasivariety(c2, c2, None) is None else sorted([str(x.kernel()) for x in Algebras.memberOfQuasivariety(c2, c2, None)])",
        description="memberOfQuasivariety(C2, C2) kernels",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_member_qv_list",
        method="Algebras.memberOfQuasivariety",
        setup=_SETUP,
        call="None if Algebras.memberOfQuasivariety(c2, [c2], None) is None else len(list(Algebras.memberOfQuasivariety(c2, [c2], None)))",
        description="memberOfQuasivariety(C2, [C2]) list overload",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_member_qv_null",
        method="Algebras.memberOfQuasivariety",
        setup=_SETUP,
        call="Algebras.memberOfQuasivariety(None, c2, None)",
        description="memberOfQuasivariety(null, B) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="algs_member_qv_subs",
        method="Algebras.memberOfQuasivarietyGenByProperSubs",
        setup=_SETUP,
        call="None if Algebras.memberOfQuasivarietyGenByProperSubs(c2, None) is None else len(list(Algebras.memberOfQuasivarietyGenByProperSubs(c2, None)))",
        description="memberOfQuasivarietyGenByProperSubs(C2)",
        **_NONE
    ),
    TestCaseSpec(
        id="algs_quasi_crit_congs",
        method="Algebras.quasiCriticalCongruences",
        setup=_SETUP,
        call="sorted([str(p) for p in Algebras.quasiCriticalCongruences(c2, None)])",
        description="quasiCriticalCongruences(C2)",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_quasi_critical",
        method="Algebras.quasiCritical",
        setup=_SETUP,
        call="None if Algebras.quasiCritical(c2) is None else sorted([str(k) for k in Algebras.quasiCritical(c2)])",
        description="quasiCritical(C2) keys",
        **_MAP
    ),
    TestCaseSpec(
        id="algs_unary_clone",
        method="Algebras.unaryClone",
        setup=_SETUP,
        call="[_coords(row) for row in Algebras.unaryClone([zero_p, one_p], zero_p, one_p)]",
        description="unaryClone on C2 zero/one",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_unary_clone_alg_2arg",
        method="Algebras.unaryCloneAlgFromPartitions",
        setup=_SETUP,
        call="Algebras.unaryCloneAlgFromPartitions([zero_p], [zero_p])",
        description="2-arg unaryCloneAlgFromPartitions always null (Java stub)",
        **_NONE
    ),
    TestCaseSpec(
        id="algs_unary_clone_alg_3arg",
        method="Algebras.unaryCloneAlgFromPartitions",
        setup=_SETUP,
        call="Algebras.unaryCloneAlgFromPartitions([zero_p, one_p], zero_p, one_p).cardinality()",
        description="3-arg unaryCloneAlgFromPartitions cardinality",
        **_ALG
    ),
    TestCaseSpec(
        id="algs_unary_clone_null",
        method="Algebras.unaryClone",
        setup=_SETUP,
        call="Algebras.unaryClone(None, zero_p, one_p)",
        description="unaryClone(null, ...) NPE",
        expected_exception="NullPointerException",
    ),
]

_WIDE = _SETUP + r"""
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
ba2 = AlgebraIO.readAlgebraFile("resources/algebras/ba2.ua")
z3 = AlgebraIO.readAlgebraFile("resources/algebras/z3.ua")
n5 = AlgebraIO.readAlgebraFile("resources/algebras/n5.ua")
m3 = AlgebraIO.readAlgebraFile("resources/algebras/m3.ua")

def _symname(op):
    sym = None
    if hasattr(op, "symbol"):
        try:
            sym = op.symbol() if callable(op.symbol) else op.symbol
        except Exception:
            sym = None
    if sym is None:
        return ""
    getter = getattr(sym, "name", None) or getattr(sym, "getName", None)
    if callable(getter):
        return str(getter())
    return str(sym)

def _op_table_any(op, n):
    ar = int(op.arity())
    iva = op.intValueAt
    if ar == 0:
        return [int(iva([]))]
    if ar == 1:
        return [int(iva([i])) for i in range(n)]
    if ar == 2:
        return [int(iva([i, j])) for i in range(n) for j in range(n)]
    return []

def _fa_snap(base, n):
    f = FreeAlgebra(base, n)
    card = int(f.cardinality())
    ops = []
    for op in list(f.operations()):
        ops.append([_symname(op), int(op.arity()), _op_table_any(op, card)])
    ops.sort()
    return [card, _ias(f.generators()), _ias(f.getUniverseList()), _terms(f.getTerms()), ops]

def _fa_snap_report(base, n):
    # Java FreeAlgebra(alg, n, report=null): thinGens=true, decompose=true.
    f = FreeAlgebra(base, n, None)
    card = int(f.cardinality())
    ops = []
    for op in list(f.operations()):
        ops.append([_symname(op), int(op.arity()), _op_table_any(op, card)])
    ops.sort()
    return [card, _ias(f.generators()), _ias(f.getUniverseList()), _terms(f.getTerms()), ops]

def _fa_roundtrip(base, n):
    import os, tempfile
    f = FreeAlgebra(base, n)
    live = _fa_snap(base, n)
    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    AlgebraIO.writeAlgebraFile(f, path)
    read = AlgebraIO.readAlgebraFile(path)
    os.unlink(path)
    card = int(read.cardinality())
    ops = []
    for op in list(read.operations()):
        ops.append([_symname(op), int(op.arity()), _op_table_any(op, card)])
    ops.sort()
    return [live, [card, ops]]

def _qcc(path):
    a = AlgebraIO.readAlgebraFile(path)
    return sorted([str(p) for p in Algebras.quasiCriticalCongruences(a, None)])
"""

TEST_CASES.extend([
    TestCaseSpec(
        id="fa_live_c2_f2",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap(c2, 2)",
        description="live F(2) over cyclic2: card/gens/universe/terms/ops",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_live_c2_f3",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap(c2, 3)",
        description="live F(3) over cyclic2: card/gens/universe/terms/ops",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_live_c3_f1",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap(c3, 1)",
        description="live F(1) over cyclic3: card/gens/universe/terms/ops",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_live_c3_f2",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap(c3, 2)",
        description="live F(2) over cyclic3: card/gens/universe/terms/ops",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_live_lat2_f1",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap(lat2, 1)",
        description="live F(1) over lat2: card/gens/universe/terms/ops",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_live_lat2_f2",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap(lat2, 2)",
        description="live F(2) over lat2: card/gens/universe/terms/ops",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_live_ba2_f1",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap(ba2, 1)",
        description="live F(1) over ba2: card/gens/universe/terms/ops",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_live_z3_f1",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap(z3, 1)",
        description="live F(1) over z3: card/gens/universe/terms/ops",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_live_n5_f1",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap(n5, 1)",
        description="live F(1) over n5: card/gens/universe/terms/ops",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_live_m3_f1",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap(m3, 1)",
        description="live F(1) over M3: card/gens/universe/terms/ops",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_roundtrip_c3_f1",
        method="AlgebraIO.writeAlgebraFile",
        setup=_WIDE,
        call="_fa_roundtrip(c3, 1)",
        description="write/read F(1) over cyclic3: live snap plus read card/tables",
        skip_string_check=True,
        xfail_reason=(
            "Known Java bug: AlgebraReader has no freeAlgebra end-element "
            "handler, so write-then-read returns C3 (table "
            "[0,1,2,1,2,0,2,0,1]) instead of F(1) "
            "([1,2,0,2,0,1,0,1,2]). Python rebuilds F(n). Java golden "
            "values are left unchanged."
        ),
        notes=(
            "Java rereads C3. Python rebuilds F(1). See KNOWN_DIFFERENCES.md."
        ),
    ),
    TestCaseSpec(
        id="fa_roundtrip_lat2_f1",
        method="AlgebraIO.writeAlgebraFile",
        setup=_WIDE,
        call="_fa_roundtrip(lat2, 1)",
        description="write/read F(1) over lat2: live snap plus read card/tables",
        skip_string_check=True,
        xfail_reason=(
            "Known Java bug: AlgebraReader has no freeAlgebra end-element "
            "handler, so write-then-read returns lat2 (card 2) instead of "
            "F(1) (card 1). Python rebuilds F(n). Java golden values are "
            "left unchanged."
        ),
        notes=(
            "Java rereads lat2 (card 2). Python rebuilds F(1) (card 1). "
            "See KNOWN_DIFFERENCES.md."
        ),
    ),
    TestCaseSpec(
        id="fa_roundtrip_ba2_f1",
        method="AlgebraIO.writeAlgebraFile",
        setup=_WIDE,
        call="_fa_roundtrip(ba2, 1)",
        description="write/read F(1) over ba2: live snap plus read card/tables",
        skip_string_check=True,
        xfail_reason=(
            "Known Java bug: AlgebraReader has no freeAlgebra end-element "
            "handler, so write-then-read returns ba2 (card 2) instead of "
            "F(1) (card 4). Python rebuilds F(n). Java golden values are "
            "left unchanged."
        ),
        notes=(
            "Java rereads ba2 (card 2). Python rebuilds F(1) (card 4). "
            "See KNOWN_DIFFERENCES.md."
        ),
    ),
    TestCaseSpec(
        id="algs_quasi_crit_c3",
        method="Algebras.quasiCriticalCongruences",
        setup=_WIDE,
        call="_qcc('resources/algebras/cyclic3.ua')",
        description="quasiCriticalCongruences(cyclic3)",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_quasi_crit_lat2",
        method="Algebras.quasiCriticalCongruences",
        setup=_WIDE,
        call="_qcc('resources/algebras/lat2.ua')",
        description="quasiCriticalCongruences(lat2)",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_quasi_crit_ba2",
        method="Algebras.quasiCriticalCongruences",
        setup=_WIDE,
        call="_qcc('resources/algebras/ba2.ua')",
        description="quasiCriticalCongruences(ba2)",
        **_LIST
    ),
    TestCaseSpec(
        id="algs_quasi_crit_z3",
        method="Algebras.quasiCriticalCongruences",
        setup=_WIDE,
        call="_qcc('resources/algebras/z3.ua')",
        description="quasiCriticalCongruences(z3)",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_varmap_c3_f1",
        method="FreeAlgebra.getVariableToGeneratorMap",
        setup=_WIDE,
        call="_varmap(FreeAlgebra(c3, 1))",
        description="F(1) over cyclic3 variable-to-generator map",
        **_MAP
    ),
    TestCaseSpec(
        id="fa_varmap_lat2_f1",
        method="FreeAlgebra.getVariableToGeneratorMap",
        setup=_WIDE,
        call="_varmap(FreeAlgebra(lat2, 1))",
        description="F(1) over lat2 variable-to-generator map",
        **_MAP
    ),
    TestCaseSpec(
        id="fa_varmap_n5_f1",
        method="FreeAlgebra.getVariableToGeneratorMap",
        setup=_WIDE,
        call="_varmap(FreeAlgebra(n5, 1))",
        description="F(1) over n5 variable-to-generator map",
        **_MAP
    ),
    TestCaseSpec(
        id="fa_varmap_m3_f1",
        method="FreeAlgebra.getVariableToGeneratorMap",
        setup=_WIDE,
        call="_varmap(FreeAlgebra(m3, 1))",
        description="F(1) over m3 variable-to-generator map",
        **_MAP
    ),
    TestCaseSpec(
        id="fa_decompose_c2_f2",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap_report(c2, 2)",
        description="F(2) over cyclic2 with Java report constructor (decompose=true)",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_decompose_lat2_f2",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap_report(lat2, 2)",
        description="F(2) over lat2 with Java report constructor (decompose=true)",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_decompose_z3_f2",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap_report(z3, 2)",
        description="F(2) over z3 with Java report constructor (decompose=true)",
        **_LIST
    ),
    TestCaseSpec(
        id="fa_decompose_c2c2_f2",
        method="FreeAlgebra.cardinality",
        setup=_WIDE,
        call="_fa_snap_report(ProductAlgebra([c2, c2]), 2)",
        description="F(2) over non-SI C2xC2 with Java report constructor (decompose=true)",
        **_LIST
    ),
])
