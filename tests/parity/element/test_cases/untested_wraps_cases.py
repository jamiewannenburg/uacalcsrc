"""Parity cases for wrapped org.uacalc.element constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.element import SubProductElement
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import FreeAlgebra, SubProductAlgebra, BigProductAlgebra
from org.uacalc.util import IntArray
c2 = AlgebraIO.readAlgebraFile('resources/algebras/cyclic2.ua')
f1 = FreeAlgebra(c2, 1)
f1.setName('F1')
bp2 = BigProductAlgebra(c2, 2)
sp = SubProductAlgebra('SP', bp2, [IntArray([0, 0]), IntArray([1, 1])], True)
e_f1_0 = SubProductElement(f1.getElement(0), f1)
e_sp_0 = SubProductElement(sp.getElement(0), sp)
"""

_ALG = dict(skip_string_check=True, notes="Java Algebra toString is Class@hex.")


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
    _c("ctor_spe_free", "SubProductElement.SubProductElement",
       "e_f1_0.getAlgebra().getName()", "SubProductElement of F(1) constructor", **_ALG),
    _c("ctor_spe_subprod", "SubProductElement.SubProductElement",
       "e_sp_0.getAlgebra().getName()", "SubProductElement of a subproduct constructor", **_ALG),
    _c("inh_elem_parent", "Element.getParent", "e_f1_0.getParent()", "Element getParent on F(1) element", **_ALG),
    _c("inh_elem_parent_arr", "Element.getParentArray",
       "list(e_f1_0.getParentArray())", "Element getParentArray", skip_string_check=True),
    _c("inh_elem_index", "Element.index", "int(e_f1_0.index())", "Element index"),
    _c("inh_elem_parent_idx", "Element.parentIndexArray",
       "list(e_f1_0.parentIndexArray())", "Element parentIndexArray", skip_string_check=True),
    _c("inh_elem_tostr", "Element.toString", "e_f1_0.toString()", "Element toString", skip_string_check=True),
]
