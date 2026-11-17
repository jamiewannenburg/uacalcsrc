"""Parity cases for wrapped org.uacalc.eq constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.eq import Equation, Presentation
from org.uacalc.terms import NonVariableTerm, VariableImp
from org.uacalc.alg.op import OperationSymbol
plus = OperationSymbol("+", 2)
x = VariableImp("x")
y = VariableImp("y")
eq_xy = Equation(x, y)
eq_xx = Equation(x, x)
pres = Presentation([x, y], [eq_xy])
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
    _c("ctor_equation_xy", "Equation.Equation",
       "str(eq_xy.leftSide()) + '=' + str(eq_xy.rightSide())",
       "Equation(x, y) constructor"),
    _c("ctor_equation_xx", "Equation.Equation",
       "str(eq_xx.leftSide())", "Equation(x, x) constructor"),
    _c("ctor_presentation", "Presentation.Presentation",
       "len(list(pres.getRelations()))",
       "Presentation constructor relation count"),
]
