"""Parity cases for wrapped org.uacalc.fplat constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.fplat import PartiallyDefinedLattice
from org.uacalc.lat import Order
from org.uacalc.terms import VariableImp

def _name(v):
    fn = getattr(v, 'getName', None) or getattr(v, 'get_name', None)
    if callable(fn):
        return str(fn())
    return str(v)

class NameOrder(Order):
    def leq(self, a, b):
        return _name(a) <= _name(b)

x = VariableImp('x')
y = VariableImp('y')
nat = NameOrder()
named = PartiallyDefinedLattice('T', nat, [[x, y]], [[y, x]])
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")


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
    _c("ctor_pdl_named", "PartiallyDefinedLattice.PartiallyDefinedLattice",
       "named.leq(x, y)", "PartiallyDefinedLattice constructor", **_BOOL),
    _c("ctor_pdl_empty", "PartiallyDefinedLattice.PartiallyDefinedLattice",
       "PartiallyDefinedLattice('empty', nat, [], []).leq(x, x)",
       "empty PartiallyDefinedLattice constructor", **_BOOL),
]
