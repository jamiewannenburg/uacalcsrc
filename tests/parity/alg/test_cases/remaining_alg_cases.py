"""Golden parity cases for the remaining org.uacalc.alg types."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import (
    AlgebraFromMinimalSets, AlgebraWithGeneratingVector, GeneralAlgebra,
    MatrixPowerAlgebra, ParameterizedAlgebra, PolinLikeAlgebra,
    ReductAlgebra, UnaryTermsMonoid,
)
from org.uacalc.alg.op import OperationSymbol, Operations
from org.uacalc.terms import NonVariableTerm, Variable
from org.uacalc.util import IntArray
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
plus = OperationSymbol("+", 2)
id1 = Operations.makeIntOperation(OperationSymbol("id", 1), 2, [0, 1])
afms = AlgebraFromMinimalSets("fromC2", c2)
mp = MatrixPowerAlgebra("mp", c2, 1)
mp2 = MatrixPowerAlgebra(c2, 1)
pol = PolinLikeAlgebra("pol", c2, c2, None, 0, 0)
try:
    from java.util import HashSet
    _univ = HashSet()
    _univ.add(0)
    _univ.add(1)
except ImportError:
    _univ = [0, 1]
ga = GeneralAlgebra("G", _univ, [id1])
awgv = AlgebraWithGeneratingVector(c2, [0, 1])
awgv2 = AlgebraWithGeneratingVector(c2, [0, 1])
parm = ParameterizedAlgebra()
try:
    parm.parameterNames = ["n", "m"]
except Exception:
    field = parm.getClass().getDeclaredField("parameterNames")
    field.setAccessible(True)
    from java.util import ArrayList
    _names = ArrayList()
    _names.add("n")
    _names.add("m")
    field.set(parm, _names)
plus_term = NonVariableTerm(plus, [Variable.x, Variable.y])
reduct = ReductAlgebra("R", c2, [plus_term])
utm = UnaryTermsMonoid(c2)

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
    return elem

def _op_names(alg):
    names = []
    for op in list(alg.operations()):
        sym = op.symbol()
        name = sym.name() if callable(getattr(sym, "name", None)) else str(sym)
        names.append(str(name))
    names.sort()
    return names

def _tbl(alg, sym=plus):
    op = alg.getOperation(sym)
    if op is None:
        return None
    n = int(alg.cardinality())
    ar = int(op.arity())
    if ar == 1:
        return [int(op.intValueAt([i])) for i in range(n)]
    return [int(op.intValueAt([i, j])) for i in range(n) for j in range(n)]
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List/Set toString vs Python list.")
_ALG = dict(skip_string_check=True, notes="Java Algebra toString is Class@hex; values compared.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")
_MAP = dict(skip_string_check=True, notes="Java Map toString vs Python dict.")

TEST_CASES = [
    # --- AlgebraFromMinimalSets ---
    TestCaseSpec(
        id="afms_card",
        method="AlgebraFromMinimalSets.cardinality",
        setup=_SETUP,
        call="afms.cardinality()",
        description="default size over cyclic2 is 3*2-2 = 4",
    ),
    TestCaseSpec(
        id="afms_get_name",
        method="AlgebraFromMinimalSets.getName",
        setup=_SETUP,
        call="afms.getName()",
        description="named AlgebraFromMinimalSets getName",
    ),
    TestCaseSpec(
        id="afms_set_name",
        method="AlgebraFromMinimalSets.setName",
        setup=_SETUP + "\nafms.setName('Min')\n",
        call="afms.getName()",
        description="AlgebraFromMinimalSets setName",
    ),
    TestCaseSpec(
        id="afms_algebra_type",
        method="AlgebraFromMinimalSets.algebraType",
        setup=_SETUP,
        call="str(afms.algebraType())",
        description="algebraType is BASIC",
    ),
    TestCaseSpec(
        id="afms_nops",
        method="AlgebraFromMinimalSets.operations",
        setup=_SETUP,
        call="_op_names(afms)",
        description="default ops are unary s plus lifted op-+",
        **_LIST
    ),
    TestCaseSpec(
        id="afms_univ_list",
        method="AlgebraFromMinimalSets.getUniverseList",
        setup=_SETUP,
        call="afms.getUniverseList()",
        description="int universe getUniverseList is null",
        **_NONE
    ),
    TestCaseSpec(
        id="afms_get_element",
        method="AlgebraFromMinimalSets.getElement",
        setup=_SETUP,
        call="afms.getElement(0)",
        description="int-universe getElement(0) is 0",
    ),
    TestCaseSpec(
        id="afms_unnamed_card",
        method="AlgebraFromMinimalSets.cardinality",
        setup=_SETUP,
        call="AlgebraFromMinimalSets(c2).cardinality()",
        description="1-arg constructor default cardinality",
    ),
    TestCaseSpec(
        id="afms_roundtrip",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(afms, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality(), _op_names(read)]",
        description="write AlgebraFromMinimalSets, read back card and op names",
        **_LIST
    ),
    # --- MatrixPowerAlgebra ---
    TestCaseSpec(
        id="mp_card",
        method="MatrixPowerAlgebra.cardinality",
        setup=_SETUP,
        call="mp.cardinality()",
        description="matrix power 1 over c2 has card 2",
    ),
    TestCaseSpec(
        id="mp_get_name",
        method="MatrixPowerAlgebra.getName",
        setup=_SETUP,
        call="mp.getName()",
        description="named matrix power getName",
    ),
    TestCaseSpec(
        id="mp_unnamed_name",
        method="MatrixPowerAlgebra.getName",
        setup=_SETUP,
        call="mp2.getName()",
        description="Java default name is root^[power]",
    ),
    TestCaseSpec(
        id="mp_algebra_type",
        method="MatrixPowerAlgebra.algebraType",
        setup=_SETUP,
        call="str(mp.algebraType())",
        description="algebraType is MATRIX_POWER",
    ),
    TestCaseSpec(
        id="mp_get_power",
        method="MatrixPowerAlgebra.getPower",
        setup=_SETUP,
        call="mp.getPower()",
        description="getPower is 1",
    ),
    TestCaseSpec(
        id="mp_get_root",
        method="MatrixPowerAlgebra.getRoot",
        setup=_SETUP,
        call="mp.getRoot().getName()",
        description="getRoot is the original algebra",
        **_ALG
    ),
    TestCaseSpec(
        id="mp_get_power_algebra",
        method="MatrixPowerAlgebra.getPowerAlgebra",
        setup=_SETUP,
        call="mp.getPowerAlgebra().cardinality()",
        description="getPowerAlgebra has the same cardinality as the matrix power",
        **_ALG
    ),
    TestCaseSpec(
        id="mp_parent",
        method="MatrixPowerAlgebra.parent",
        setup=_SETUP,
        call="mp.parent().getName()",
        description="parent is the root",
        **_ALG
    ),
    TestCaseSpec(
        id="mp_parents",
        method="MatrixPowerAlgebra.parents",
        setup=_SETUP,
        call="[a.getName() for a in mp.parents()]",
        description="parents is a singleton root list",
        **_LIST
    ),
    TestCaseSpec(
        id="mp_get_element",
        method="MatrixPowerAlgebra.getElement",
        setup=_SETUP,
        call="_coords(mp.getElement(0))",
        description="getElement(0) Horner tuple",
        **_LIST
    ),
    TestCaseSpec(
        id="mp_power_zero",
        method="MatrixPowerAlgebra.__init__",
        setup=_SETUP,
        call="MatrixPowerAlgebra(c2, 0)",
        description="power 0 hits ProductAlgebra makeOperations IOBE",
        expected_exception="IndexOutOfBoundsException",
    ),
    TestCaseSpec(
        id="mp_convert_uoe",
        method="MatrixPowerAlgebra.convertToDefaultValueOps",
        setup=_SETUP,
        call="mp.convertToDefaultValueOps()",
        description="convertToDefaultValueOps is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="mp_empty_name_typo",
        method="MatrixPowerAlgebra.getName",
        setup=_SETUP + r"""
from org.uacalc.alg import BasicAlgebra
empty = BasicAlgebra("", 2, [id1])
mp_typo = MatrixPowerAlgebra(empty, 1)
""",
        call="mp_typo.getName()",
        description="empty-string root name is still concatenated as ^[power]",
    ),
    TestCaseSpec(
        id="mp_roundtrip",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(mp, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality(), read.getName()]",
        description="write MatrixPowerAlgebra, read back card and name",
        **_LIST
    ),
    # --- PolinLikeAlgebra ---
    TestCaseSpec(
        id="pol_card",
        method="PolinLikeAlgebra.cardinality",
        setup=_SETUP,
        call="pol.cardinality()",
        description="polin of two c2s has card 4",
    ),
    TestCaseSpec(
        id="pol_get_name",
        method="PolinLikeAlgebra.getName",
        setup=_SETUP,
        call="pol.getName()",
        description="polin getName",
    ),
    TestCaseSpec(
        id="pol_algebra_type",
        method="PolinLikeAlgebra.algebraType",
        setup=_SETUP,
        call="str(pol.algebraType())",
        description="algebraType is POLIN_LIKE",
    ),
    TestCaseSpec(
        id="pol_get_element",
        method="PolinLikeAlgebra.getElement",
        setup=_SETUP,
        call="pol.getElement(0)",
        description="Java getElement stub is null",
        **_NONE
    ),
    TestCaseSpec(
        id="pol_element_index",
        method="PolinLikeAlgebra.elementIndex",
        setup=_SETUP,
        call="pol.elementIndex(0)",
        description="Java elementIndex stub is -1",
    ),
    TestCaseSpec(
        id="pol_univ_list",
        method="PolinLikeAlgebra.getUniverseList",
        setup=_SETUP,
        call="pol.getUniverseList()",
        description="getUniverseList is null",
        **_NONE
    ),
    TestCaseSpec(
        id="pol_nops",
        method="PolinLikeAlgebra.operations",
        setup=_SETUP,
        call="len(list(pol.operations()))",
        description="polinized ops plus unary ^+",
    ),
    TestCaseSpec(
        id="pol_convert_uoe",
        method="PolinLikeAlgebra.convertToDefaultValueOps",
        setup=_SETUP,
        call="pol.convertToDefaultValueOps()",
        description="convertToDefaultValueOps is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="pol_roundtrip",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(pol, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality()]",
        description="write PolinLikeAlgebra, read back cardinality",
        **_LIST
    ),
    # --- GeneralAlgebra ---
    TestCaseSpec(
        id="ga_card",
        method="GeneralAlgebra.cardinality",
        setup=_SETUP,
        call="ga.cardinality()",
        description="GeneralAlgebra({0,1}) cardinality 2",
    ),
    TestCaseSpec(
        id="ga_get_name",
        method="GeneralAlgebra.getName",
        setup=_SETUP,
        call="ga.getName()",
        description="GeneralAlgebra getName",
    ),
    TestCaseSpec(
        id="ga_set_name",
        method="GeneralAlgebra.setName",
        setup=_SETUP + "\nga.setName('Gen')\n",
        call="ga.getName()",
        description="GeneralAlgebra setName",
    ),
    TestCaseSpec(
        id="ga_nops",
        method="GeneralAlgebra.operations",
        setup=_SETUP,
        call="len(list(ga.operations()))",
        description="3-arg constructor installs one operation",
    ),
    TestCaseSpec(
        id="ga_get_operation",
        method="GeneralAlgebra.getOperation",
        setup=_SETUP,
        call="ga.getOperation(OperationSymbol('id', 1)) is not None",
        description="getOperation by symbol finds id",
        **_BOOL
    ),
    TestCaseSpec(
        id="ga_parent",
        method="GeneralAlgebra.parent",
        setup=_SETUP,
        call="ga.parent()",
        description="GeneralAlgebra.parent is null",
        **_NONE
    ),
    TestCaseSpec(
        id="ga_parents",
        method="GeneralAlgebra.parents",
        setup=_SETUP,
        call="ga.parents()",
        description="GeneralAlgebra.parents is null",
        **_NONE
    ),
    TestCaseSpec(
        id="ga_con_uoe",
        method="GeneralAlgebra.con",
        setup=_SETUP,
        call="ga.con()",
        description="con() throws UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="ga_sub_uoe",
        method="GeneralAlgebra.sub",
        setup=_SETUP,
        call="ga.sub()",
        description="sub() throws UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="ga_no_ops",
        method="GeneralAlgebra.operations",
        setup=_SETUP,
        call="GeneralAlgebra('U', _univ).operations()",
        description="2-arg constructor leaves operations() null",
        **_NONE
    ),
    # --- AlgebraWithGeneratingVector ---
    TestCaseSpec(
        id="awgv_alg_name",
        method="AlgebraWithGeneratingVector.getAlgebra",
        setup=_SETUP,
        call="awgv.getAlgebra().getName()",
        description="getAlgebra returns the original algebra",
        **_ALG
    ),
    TestCaseSpec(
        id="awgv_vector",
        method="AlgebraWithGeneratingVector.getVector",
        setup=_SETUP,
        call="list(awgv.getVector())",
        description="getVector is the constructor vector",
        **_LIST
    ),
    TestCaseSpec(
        id="awgv_to_string",
        method="AlgebraWithGeneratingVector.toString",
        setup=_SETUP,
        call="awgv.toString()",
        description="Java toString uses ArrayString without spaces",
    ),
    TestCaseSpec(
        id="awgv_is_image",
        method="AlgebraWithGeneratingVector.isImageOf",
        setup=_SETUP,
        call="awgv.isImageOf(awgv2)",
        description="identical vectors are images of each other",
        **_BOOL
    ),
    TestCaseSpec(
        id="awgv_compare",
        method="AlgebraWithGeneratingVector.compareTo",
        setup=_SETUP,
        call="awgv.compareTo(awgv2)",
        description="mutual images compare 0",
    ),
    TestCaseSpec(
        id="awgv_si_decompose",
        method="AlgebraWithGeneratingVector.siDecompose",
        setup=_SETUP,
        call="len(list(AlgebraWithGeneratingVector.siDecompose(c2, [1])))",
        description="siDecompose of cyclic2 generated by 1",
    ),
    # --- ParameterizedAlgebra ---
    TestCaseSpec(
        id="parm_map",
        method="ParameterizedAlgebra.getParameterMap",
        setup=_SETUP,
        call="dict(parm.getParameterMap([2, 3]))",
        description="getParameterMap pairs names with values",
        **_MAP
    ),
    TestCaseSpec(
        id="parm_extra_ignored",
        method="ParameterizedAlgebra.getParameterMap",
        setup=_SETUP,
        call="dict(parm.getParameterMap([2, 3, 9]))",
        description="extra values are ignored",
        **_MAP
    ),
    TestCaseSpec(
        id="parm_too_few",
        method="ParameterizedAlgebra.getParameterMap",
        setup=_SETUP,
        call="parm.getParameterMap([2])",
        description="too few values is NoSuchElementException",
        expected_exception="NoSuchElementException",
    ),
    TestCaseSpec(
        id="parm_null_names",
        method="ParameterizedAlgebra.getParameterMap",
        setup=_SETUP,
        call="ParameterizedAlgebra().getParameterMap([1])",
        description="null parameterNames is NPE",
        expected_exception="NullPointerException",
    ),
    # --- ReductAlgebra ---
    TestCaseSpec(
        id="reduct_card",
        method="ReductAlgebra.cardinality",
        setup=_SETUP,
        call="reduct.cardinality()",
        description="reduct of c2 has card 2",
    ),
    TestCaseSpec(
        id="reduct_get_name",
        method="ReductAlgebra.getName",
        setup=_SETUP,
        call="reduct.getName()",
        description="named reduct getName",
    ),
    TestCaseSpec(
        id="reduct_algebra_type",
        method="ReductAlgebra.algebraType",
        setup=_SETUP,
        call="str(reduct.algebraType())",
        description="algebraType is REDUCT",
    ),
    TestCaseSpec(
        id="reduct_super",
        method="ReductAlgebra.superAlgebra",
        setup=_SETUP,
        call="reduct.superAlgebra().getName()",
        description="superAlgebra is the original algebra",
        **_ALG
    ),
    TestCaseSpec(
        id="reduct_nops",
        method="ReductAlgebra.operations",
        setup=_SETUP,
        call="len(list(reduct.operations()))",
        description="non-variable + term yields one operation",
    ),
    TestCaseSpec(
        id="reduct_univ_list",
        method="ReductAlgebra.getUniverseList",
        setup=_SETUP,
        call="reduct.getUniverseList()",
        description="getUniverseList is null",
        **_NONE
    ),
    TestCaseSpec(
        id="reduct_var_term",
        method="ReductAlgebra.operations",
        setup=_SETUP,
        call="len(list(ReductAlgebra(c2, [Variable.x]).operations()))",
        description="variable terms produce no operations",
    ),
    TestCaseSpec(
        id="reduct_roundtrip",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(reduct, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality()]",
        description="write ReductAlgebra, read back cardinality",
        **_LIST
    ),
    # --- UnaryTermsMonoid ---
    TestCaseSpec(
        id="utm_card",
        method="UnaryTermsMonoid.cardinality",
        setup=_SETUP,
        call="utm.cardinality()",
        description="UnaryTermsMonoid(c2) cardinality is |FreeAlgebra(c2,1)|",
    ),
    TestCaseSpec(
        id="utm_get_name",
        method="UnaryTermsMonoid.getName",
        setup=_SETUP,
        call="utm.getName()",
        description="default name is UnaryTerms(c2 name)",
    ),
    TestCaseSpec(
        id="utm_algebra_type",
        method="UnaryTermsMonoid.algebraType",
        setup=_SETUP,
        call="str(utm.algebraType())",
        description="algebraType is UNARY_TERMS_MONOID",
    ),
    TestCaseSpec(
        id="utm_is_unary",
        method="UnaryTermsMonoid.isUnary",
        setup=_SETUP,
        call="utm.isUnary()",
        description="Java isUnary is false (binary PRODUCT)",
        **_BOOL
    ),
    TestCaseSpec(
        id="utm_nops",
        method="UnaryTermsMonoid.operations",
        setup=_SETUP,
        call="len(list(utm.operations()))",
        description="one binary PRODUCT operation",
    ),
    TestCaseSpec(
        id="utm_parent",
        method="UnaryTermsMonoid.parent",
        setup=_SETUP,
        call="utm.parent().getName()",
        description="parent is the generating algebra",
        **_ALG
    ),
    TestCaseSpec(
        id="utm_get_element",
        method="UnaryTermsMonoid.getElement",
        setup=_SETUP,
        call="utm.getElement(0)",
        description="Java getElement stub is null",
        **_NONE
    ),
    TestCaseSpec(
        id="utm_element_index",
        method="UnaryTermsMonoid.elementIndex",
        setup=_SETUP,
        call="utm.elementIndex(0)",
        description="Java elementIndex stub is 0",
    ),
    TestCaseSpec(
        id="utm_con",
        method="UnaryTermsMonoid.con",
        setup=_SETUP,
        call="utm.con()",
        description="Java con() is null",
        **_NONE
    ),
    TestCaseSpec(
        id="utm_sub",
        method="UnaryTermsMonoid.sub",
        setup=_SETUP,
        call="utm.sub()",
        description="Java sub() is null",
        **_NONE
    ),
    TestCaseSpec(
        id="utm_convert_uoe",
        method="UnaryTermsMonoid.convertToDefaultValueOps",
        setup=_SETUP,
        call="utm.convertToDefaultValueOps()",
        description="convertToDefaultValueOps is UOE",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="utm_roundtrip",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + r"""
import os, tempfile
fd, path = tempfile.mkstemp(suffix=".ua")
os.close(fd)
AlgebraIO.writeAlgebraFile(utm, path)
read = AlgebraIO.readAlgebraFile(path)
os.unlink(path)
""",
        call="[read.cardinality()]",
        description="write UnaryTermsMonoid, read back cardinality",
        **_LIST
    ),
]
