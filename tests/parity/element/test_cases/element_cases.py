"""Test case specifications for org.uacalc.element behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.element import Element, SubProductElement
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import FreeAlgebra, SubProductAlgebra, BigProductAlgebra
from org.uacalc.util import IntArray
c2 = AlgebraIO.readAlgebraFile('resources/algebras/cyclic2.ua')
c3 = AlgebraIO.readAlgebraFile('resources/algebras/cyclic3.ua')
lat2 = AlgebraIO.readAlgebraFile('resources/algebras/lat2.ua')
f1 = FreeAlgebra(c2, 1)
f1.setName('F1')
f2 = FreeAlgebra(c2, 2)
f2.setName('F2')
f3 = FreeAlgebra(c3, 2)
f3.setName('F3')
flat = FreeAlgebra(lat2, 2)
flat.setName('Flat')
bp2 = BigProductAlgebra(c2, 2)
bp3 = BigProductAlgebra(c2, 3)
bpm = BigProductAlgebra([c2, c3], [1, 1])
g00 = IntArray([0, 0])
g11 = IntArray([1, 1])
g01 = IntArray([0, 1])
sp = SubProductAlgebra('SP', bp2, [g00, g11], True)
spn = SubProductAlgebra('SPn', bp2, [g00, g11], False)
sp3 = SubProductAlgebra('SP3', bp3, [IntArray([0, 0, 0]), IntArray([1, 1, 1]), IntArray([0, 1, 0])], True)
spm = SubProductAlgebra('SPmix', bpm, [IntArray([0, 0]), IntArray([1, 1])], True)
e_f1_0 = SubProductElement(f1.getElement(0), f1)
e_f1_1 = SubProductElement(f1.getElement(1), f1)
e_f2_0 = SubProductElement(f2.getElement(0), f2)
e_f2_last = SubProductElement(f2.getElement(int(f2.cardinality()) - 1), f2)
e_f3_0 = SubProductElement(f3.getElement(0), f3)
e_flat_0 = SubProductElement(flat.getElement(0), flat)
e_sp_0 = SubProductElement(sp.getElement(0), sp)
e_sp_1 = SubProductElement(sp.getElement(1), sp)
e_spn_0 = SubProductElement(spn.getElement(0), spn)
e_sp3_0 = SubProductElement(sp3.getElement(0), sp3)
e_spm_0 = SubProductElement(spm.getElement(0), spm)

def _coords(elem):
    if elem is None:
        return None
    for attr in ('getArray', 'get_array', 'toArray', 'to_array'):
        fn = getattr(elem, attr, None)
        if callable(fn):
            try:
                return [int(x) for x in fn()]
            except TypeError:
                continue
    try:
        return [int(x) for x in list(elem)]
    except TypeError:
        return str(elem)

def _names(lst):
    if lst is None:
        return None
    out = []
    for v in list(lst):
        getter = getattr(v, 'getName', None)
        out.append(getter() if getter is not None else str(v))
    return out

def _varmap(m):
    if m is None:
        return None
    items = m.entrySet() if hasattr(m, 'entrySet') else m.items()
    out = {}
    for item in items:
        if hasattr(item, 'getKey'):
            k, v = item.getKey(), item.getValue()
        else:
            k, v = item
        getter = getattr(k, 'getName', None)
        name = getter() if getter is not None else str(k)
        out[name] = _coords(v)
    return out

def _term(t):
    if t is None:
        return None
    return str(t)

def _cls(o):
    n = type(o).__name__.split('.')[-1]
    if n.startswith('Py') and len(n) > 2:
        n = n[2:]
    return n
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")
_ALG = dict(skip_string_check=True, notes="Java Algebra toString is Class@hex; values compared.")
_LIST = dict(skip_string_check=True, notes="Java List/Map toString vs Python list/dict.")
TEST_CASES = [
    TestCaseSpec(
        id="f1_0_index",
        method="SubProductElement.index",
        setup=_SETUP,
        call="e_f1_0.index()",
        description="index of generator 0 in F(1) over C2",
    ),
    TestCaseSpec(
        id="f1_1_index",
        method="SubProductElement.index",
        setup=_SETUP,
        call="e_f1_1.index()",
        description="index of element 1 in F(1) over C2",
    ),
    TestCaseSpec(
        id="f1_0_term",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="_term(e_f1_0.getTerm())",
        description="getTerm of F(1) generator",
    ),
    TestCaseSpec(
        id="f1_1_term",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="_term(e_f1_1.getTerm())",
        description="getTerm of F(1) derived element",
    ),
    TestCaseSpec(
        id="f1_0_vars",
        method="SubProductElement.getVariableList",
        setup=_SETUP,
        call="_names(e_f1_0.getVariableList())",
        description="getVariableList of F(1) generator",
        **_LIST
    ),
    TestCaseSpec(
        id="f1_1_vars",
        method="SubProductElement.getVariableList",
        setup=_SETUP,
        call="_names(e_f1_1.getVariableList())",
        description="getVariableList of F(1) derived element",
        **_LIST
    ),
    TestCaseSpec(
        id="f1_0_varmap",
        method="SubProductElement.getVariableMap",
        setup=_SETUP,
        call="_varmap(e_f1_0.getVariableMap())",
        description="getVariableMap of F(1) generator",
        **_LIST
    ),
    TestCaseSpec(
        id="f1_0_alg_name",
        method="SubProductElement.getAlgebra",
        setup=_SETUP,
        call="e_f1_0.getAlgebra().getName()",
        description="getAlgebra name of F(1) element",
        **_ALG
    ),
    TestCaseSpec(
        id="f1_0_alg_card",
        method="SubProductElement.getAlgebra",
        setup=_SETUP,
        call="e_f1_0.getAlgebra().cardinality()",
        description="getAlgebra cardinality of F(1)",
        **_ALG
    ),
    TestCaseSpec(
        id="f1_0_parent",
        method="SubProductElement.getParent",
        setup=_SETUP,
        call="e_f1_0.getParent()",
        description="getParent is the Java stub null",
        **_NONE
    ),
    TestCaseSpec(
        id="f1_0_parent_array",
        method="SubProductElement.getParentArray",
        setup=_SETUP,
        call="e_f1_0.getParentArray()",
        description="getParentArray is the Java stub null",
        **_NONE
    ),
    TestCaseSpec(
        id="f1_0_parent_index_array",
        method="SubProductElement.parentIndexArray",
        setup=_SETUP,
        call="e_f1_0.parentIndexArray()",
        description="parentIndexArray is the Java stub null",
        **_NONE
    ),
    TestCaseSpec(
        id="f1_0_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_f1_0.toString() if hasattr(e_f1_0, 'toString') else str(e_f1_0)",
        description="toString of F(1) generator includes term and mapping",
    ),
    TestCaseSpec(
        id="f1_1_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_f1_1.toString() if hasattr(e_f1_1, 'toString') else str(e_f1_1)",
        description="toString of F(1) derived element",
    ),
    TestCaseSpec(
        id="f1_0_eq_self",
        method="SubProductElement.equals",
        setup=_SETUP,
        call="e_f1_0 == e_f1_0",
        description="identity equality holds",
        **_BOOL
    ),
    TestCaseSpec(
        id="f1_0_eq_copy",
        method="SubProductElement.equals",
        setup=_SETUP,
        call="e_f1_0 == SubProductElement(f1.getElement(0), f1)",
        description="separately constructed elements are not equal (Object identity)",
        **_BOOL
    ),
    TestCaseSpec(
        id="f1_0_hash_stable",
        method="SubProductElement.hashCode",
        setup=_SETUP,
        call="hash(e_f1_0) == hash(e_f1_0)",
        description="hash is stable for the same instance",
        **_BOOL
    ),
    TestCaseSpec(
        id="f2_0_index",
        method="SubProductElement.index",
        setup=_SETUP,
        call="e_f2_0.index()",
        description="index of first F(2) over C2 element",
    ),
    TestCaseSpec(
        id="f2_0_term",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="_term(e_f2_0.getTerm())",
        description="getTerm of first F(2) over C2 element",
    ),
    TestCaseSpec(
        id="f2_0_vars",
        method="SubProductElement.getVariableList",
        setup=_SETUP,
        call="_names(e_f2_0.getVariableList())",
        description="getVariableList of first F(2) over C2 element",
        **_LIST
    ),
    TestCaseSpec(
        id="f2_0_varmap",
        method="SubProductElement.getVariableMap",
        setup=_SETUP,
        call="_varmap(e_f2_0.getVariableMap())",
        description="getVariableMap of first F(2) over C2 element",
        **_LIST
    ),
    TestCaseSpec(
        id="f2_0_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_f2_0.toString() if hasattr(e_f2_0, 'toString') else str(e_f2_0)",
        description="toString of first F(2) over C2 element",
    ),
    TestCaseSpec(
        id="f2_last_term",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="_term(e_f2_last.getTerm())",
        description="getTerm of last F(2) over C2 element",
    ),
    TestCaseSpec(
        id="f2_last_vars",
        method="SubProductElement.getVariableList",
        setup=_SETUP,
        call="_names(e_f2_last.getVariableList())",
        description="getVariableList of last F(2) over C2 element",
        **_LIST
    ),
    TestCaseSpec(
        id="f2_last_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_f2_last.toString() if hasattr(e_f2_last, 'toString') else str(e_f2_last)",
        description="toString of last F(2) over C2 element",
    ),
    TestCaseSpec(
        id="f2_card",
        method="SubProductElement.getAlgebra",
        setup=_SETUP,
        call="e_f2_0.getAlgebra().cardinality()",
        description="F(2) over C2 cardinality via getAlgebra",
        **_ALG
    ),
    TestCaseSpec(
        id="f3_0_term",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="_term(e_f3_0.getTerm())",
        description="getTerm of F(2) over C3 generator",
    ),
    TestCaseSpec(
        id="f3_0_vars",
        method="SubProductElement.getVariableList",
        setup=_SETUP,
        call="_names(e_f3_0.getVariableList())",
        description="getVariableList of F(2) over C3 generator",
        **_LIST
    ),
    TestCaseSpec(
        id="f3_0_varmap",
        method="SubProductElement.getVariableMap",
        setup=_SETUP,
        call="_varmap(e_f3_0.getVariableMap())",
        description="getVariableMap of F(2) over C3 generator",
        **_LIST
    ),
    TestCaseSpec(
        id="f3_0_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_f3_0.toString() if hasattr(e_f3_0, 'toString') else str(e_f3_0)",
        description="toString of F(2) over C3 generator",
    ),
    TestCaseSpec(
        id="f3_card",
        method="SubProductElement.getAlgebra",
        setup=_SETUP,
        call="e_f3_0.getAlgebra().cardinality()",
        description="F(2) over C3 cardinality via getAlgebra",
        **_ALG
    ),
    TestCaseSpec(
        id="flat_0_term",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="_term(e_flat_0.getTerm())",
        description="getTerm of F(2) over lat2 generator",
    ),
    TestCaseSpec(
        id="flat_0_vars",
        method="SubProductElement.getVariableList",
        setup=_SETUP,
        call="_names(e_flat_0.getVariableList())",
        description="getVariableList of F(2) over lat2 generator",
        **_LIST
    ),
    TestCaseSpec(
        id="flat_0_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_flat_0.toString() if hasattr(e_flat_0, 'toString') else str(e_flat_0)",
        description="toString of F(2) over lat2 generator",
    ),
    TestCaseSpec(
        id="sp_0_index",
        method="SubProductElement.index",
        setup=_SETUP,
        call="e_sp_0.index()",
        description="index of first C2^2 diagonal subproduct element",
    ),
    TestCaseSpec(
        id="sp_0_term",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="_term(e_sp_0.getTerm())",
        description="getTerm of C2^2 diagonal generator",
    ),
    TestCaseSpec(
        id="sp_1_term",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="_term(e_sp_1.getTerm())",
        description="getTerm of second C2^2 diagonal element",
    ),
    TestCaseSpec(
        id="sp_0_vars",
        method="SubProductElement.getVariableList",
        setup=_SETUP,
        call="_names(e_sp_0.getVariableList())",
        description="getVariableList of C2^2 diagonal generator",
        **_LIST
    ),
    TestCaseSpec(
        id="sp_0_varmap",
        method="SubProductElement.getVariableMap",
        setup=_SETUP,
        call="_varmap(e_sp_0.getVariableMap())",
        description="getVariableMap of C2^2 diagonal generator",
        **_LIST
    ),
    TestCaseSpec(
        id="sp_0_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_sp_0.toString() if hasattr(e_sp_0, 'toString') else str(e_sp_0)",
        description="toString of C2^2 diagonal generator",
    ),
    TestCaseSpec(
        id="sp_1_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_sp_1.toString() if hasattr(e_sp_1, 'toString') else str(e_sp_1)",
        description="toString of second C2^2 diagonal element",
    ),
    TestCaseSpec(
        id="sp_alg_name",
        method="SubProductElement.getAlgebra",
        setup=_SETUP,
        call="e_sp_0.getAlgebra().getName()",
        description="getAlgebra name of subproduct element",
        **_ALG
    ),
    TestCaseSpec(
        id="sp_parent",
        method="SubProductElement.getParent",
        setup=_SETUP,
        call="e_sp_0.getParent()",
        description="subproduct getParent is null",
        **_NONE
    ),
    TestCaseSpec(
        id="spn_term_null",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="e_spn_0.getTerm()",
        description="getTerm is null when findTerms is false",
        **_NONE
    ),
    TestCaseSpec(
        id="spn_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_spn_0.toString() if hasattr(e_spn_0, 'toString') else str(e_spn_0)",
        description="toString without terms is just the IntArray",
    ),
    TestCaseSpec(
        id="spn_index",
        method="SubProductElement.index",
        setup=_SETUP,
        call="e_spn_0.index()",
        description="index still works without terms",
    ),
    TestCaseSpec(
        id="spn_vars_npe",
        method="SubProductElement.getVariableList",
        setup=_SETUP,
        call="e_spn_0.getVariableList()",
        description="getVariableList NPEs when getTerm is null",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="sp3_0_term",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="_term(e_sp3_0.getTerm())",
        description="getTerm of C2^3 three-generator subproduct",
    ),
    TestCaseSpec(
        id="sp3_0_vars",
        method="SubProductElement.getVariableList",
        setup=_SETUP,
        call="_names(e_sp3_0.getVariableList())",
        description="getVariableList of C2^3 three-generator subproduct",
        **_LIST
    ),
    TestCaseSpec(
        id="sp3_0_varmap",
        method="SubProductElement.getVariableMap",
        setup=_SETUP,
        call="_varmap(e_sp3_0.getVariableMap())",
        description="getVariableMap of C2^3 three-generator subproduct",
        **_LIST
    ),
    TestCaseSpec(
        id="sp3_0_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_sp3_0.toString() if hasattr(e_sp3_0, 'toString') else str(e_sp3_0)",
        description="toString of C2^3 three-generator subproduct",
    ),
    TestCaseSpec(
        id="sp3_card",
        method="SubProductElement.getAlgebra",
        setup=_SETUP,
        call="e_sp3_0.getAlgebra().cardinality()",
        description="C2^3 three-generator subproduct cardinality",
        **_ALG
    ),
    TestCaseSpec(
        id="spm_0_term",
        method="SubProductElement.getTerm",
        setup=_SETUP,
        call="_term(e_spm_0.getTerm())",
        description="getTerm of mixed C2 x C3 subproduct",
    ),
    TestCaseSpec(
        id="spm_0_vars",
        method="SubProductElement.getVariableList",
        setup=_SETUP,
        call="_names(e_spm_0.getVariableList())",
        description="getVariableList of mixed C2 x C3 subproduct",
        **_LIST
    ),
    TestCaseSpec(
        id="spm_0_varmap",
        method="SubProductElement.getVariableMap",
        setup=_SETUP,
        call="_varmap(e_spm_0.getVariableMap())",
        description="getVariableMap of mixed C2 x C3 subproduct",
        **_LIST
    ),
    TestCaseSpec(
        id="spm_0_to_string",
        method="SubProductElement.toString",
        setup=_SETUP,
        call="e_spm_0.toString() if hasattr(e_spm_0, 'toString') else str(e_spm_0)",
        description="toString of mixed C2 x C3 subproduct",
    ),
    TestCaseSpec(
        id="spm_card",
        method="SubProductElement.getAlgebra",
        setup=_SETUP,
        call="e_spm_0.getAlgebra().cardinality()",
        description="mixed C2 x C3 subproduct cardinality",
        **_ALG
    ),
    TestCaseSpec(
        id="element_is_exported",
        method="Element.getAlgebra",
        setup=_SETUP,
        call="Element is not None",
        description="Element interface is importable",
        **_BOOL
    ),
]
