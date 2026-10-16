"""Test case specifications for org.uacalc.eq behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = """
from org.uacalc.eq import Equation, Equations, Presentation
from org.uacalc.terms import Terms, NonVariableTerm, VariableImp, Variable
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.io import AlgebraIO

def _map(*pairs):
    try:
        from java.util import HashMap
        m = HashMap()
        for k, v in pairs:
            m.put(k, v)
        return m
    except ImportError:
        return dict(pairs)

def _names(lst):
    if lst is None:
        return None
    out = []
    for v in list(lst):
        getter = getattr(v, "getName", None)
        if getter is not None:
            out.append(getter())
        else:
            out.append(str(v))
    return ",".join(out)

def _syms(coll):
    if coll is None:
        return None
    parts = sorted([x.name() + "/" + str(int(x.arity())) for x in list(coll)])
    return ",".join(parts)

def _failmap(m):
    if m is None:
        return None
    items = m.entrySet() if hasattr(m, "entrySet") else m.items()
    out = {}
    for item in items:
        if hasattr(item, "getKey"):
            k, v = item.getKey(), item.getValue()
        else:
            k, v = item
        getter = getattr(k, "getName", None)
        name = getter() if getter is not None else str(k)
        out[name] = int(v)
    return out

c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
plus = OperationSymbol("+", 2)
f = OperationSymbol("f", 2)
g3 = OperationSymbol("g", 3)
x = VariableImp("x")
y = VariableImp("y")
z = VariableImp("z")
fxy = NonVariableTerm(plus, [x, y])
eq_xx = Equation(x, x)
eq_xy = Equation(x, y)
eq_plus = Equation(fxy, x)
pres = Presentation([x, y], [eq_xy])
"""

TEST_CASES = [
    TestCaseSpec(
        id="equation_left_side",
        method="Equation.leftSide",
        setup=_SETUP,
        call="str(eq_xy.leftSide())",
        description="leftSide of x = y is the term x",
    ),
    TestCaseSpec(
        id="equation_right_side",
        method="Equation.rightSide",
        setup=_SETUP,
        call="str(eq_xy.rightSide())",
        description="rightSide of x = y is the term y",
    ),
    TestCaseSpec(
        id="equation_to_string",
        method="Equation.toString",
        setup=_SETUP,
        call="eq_xy.toString()",
        description="Equation toString is 'left = right'",
    ),
    TestCaseSpec(
        id="equation_get_variable_list",
        method="Equation.getVariableList",
        setup=_SETUP,
        call="_names(eq_xy.getVariableList())",
        description="Variable list merges left then right-only vars",
    ),
    TestCaseSpec(
        id="equation_get_operation_symbols",
        method="Equation.getOperationSymbols",
        setup=_SETUP,
        call="_syms(eq_plus.getOperationSymbols())",
        description="Operation symbols from both sides",
    ),
    TestCaseSpec(
        id="equation_find_failure_holds",
        method="Equation.findFailure",
        setup=_SETUP,
        call="eq_xx.findFailure(c2)",
        description="x = x holds on cyclic2",
    ),
    TestCaseSpec(
        id="equation_find_failure_xy",
        method="Equation.findFailure",
        setup=_SETUP,
        call="eq_xy.findFailure(c2)",
        description="x = y fails on cyclic2 at the first differing tuple",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="equation_find_failure_map_holds",
        method="Equation.findFailureMap",
        setup=_SETUP,
        call="_failmap(eq_xx.findFailureMap(c2))",
        description="findFailureMap is null when the equation holds",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="equation_find_failure_map_xy",
        method="Equation.findFailureMap",
        setup=_SETUP,
        call="_failmap(eq_xy.findFailureMap(c2))",
        description="findFailureMap for x = y on cyclic2",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="equation_plus_failure",
        method="Equation.findFailure",
        setup=_SETUP,
        call="eq_plus.findFailure(c2)",
        description="+(x,y) = x fails on cyclic2",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="equations_associative_law",
        method="Equations.associativeLaw",
        setup=_SETUP,
        call="str(Equations.associativeLaw(f))",
        description="Associative law for a binary symbol",
    ),
    TestCaseSpec(
        id="equations_associative_law_arity",
        method="Equations.associativeLaw",
        setup=_SETUP,
        call="Equations.associativeLaw(OperationSymbol('h', 1))",
        description="Associative law requires arity 2",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="equations_cyclic_law",
        method="Equations.cyclicLaw",
        setup=_SETUP,
        call="str(Equations.cyclicLaw(g3))",
        description="Cyclic law for a ternary symbol",
    ),
    TestCaseSpec(
        id="equations_first_second_symmetric_law",
        method="Equations.firstSecondSymmetricLaw",
        setup=_SETUP,
        call="str(Equations.firstSecondSymmetricLaw(g3))",
        description="First-second symmetric law for a ternary symbol",
    ),
    TestCaseSpec(
        id="equations_first_second_arity",
        method="Equations.firstSecondSymmetricLaw",
        setup=_SETUP,
        call="Equations.firstSecondSymmetricLaw(OperationSymbol('h', 1))",
        description="First-second symmetric law requires arity >= 2",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="presentation_get_variables",
        method="Presentation.getVariables",
        setup=_SETUP,
        call="_names(pres.getVariables())",
        description="Presentation variables in constructor order",
    ),
    TestCaseSpec(
        id="presentation_get_relations",
        method="Presentation.getRelations",
        setup=_SETUP,
        call="[str(e) for e in list(pres.getRelations())]",
        description="Presentation relations are Equation objects",
    ),
    TestCaseSpec(
        id="presentation_empty_relations",
        method="Presentation.getRelations",
        setup=_SETUP,
        call="[str(e) for e in list(Presentation([x], []).getRelations())]",
        description="Empty relation list",
    ),
]
