"""Parity cases for wrapped org.uacalc.terms constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.terms import NonVariableTerm, VariableImp
from org.uacalc.alg.op import OperationSymbol
plus = OperationSymbol("+", 2)
x = VariableImp("x")
y = VariableImp("y")
fxy = NonVariableTerm(plus, [x, y])
"""


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
    _c("ctor_variable_imp", "VariableImp.VariableImp",
       "x.getName()", "VariableImp constructor"),
    _c("ctor_variable_imp_y", "VariableImp.VariableImp",
       "y.getName()", "VariableImp('y') constructor"),
    _c("ctor_non_variable_term", "NonVariableTerm.NonVariableTerm",
       "str(fxy).replace(' ', '')", "NonVariableTerm constructor"),
]
