"""Test case specifications for org.uacalc.terms behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_IMPORTS = """
from org.uacalc.terms import Terms, NonVariableTerm, VariableImp, Variable
from org.uacalc.alg.op import OperationSymbol
"""

TEST_CASES = [
    TestCaseSpec(
        id="string_to_term_variable",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("x0")',
        description="Parse a variable term",
    ),
    TestCaseSpec(
        id="string_to_term_unary_op",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("f(x0)")',
        description="Parse a term with unary operation",
    ),
    TestCaseSpec(
        id="string_to_term_binary_op",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("f(x0,x1)")',
        description="Parse a term with a valid binary operation name",
    ),
    TestCaseSpec(
        id="string_to_term_nested",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("f(g(x0,x1))")',
        description="Parse a nested term",
    ),
    TestCaseSpec(
        id="string_to_term_plus_invalid",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("+(x0,x1)")',
        description="'+' is not a valid Java operation name",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="string_to_term_empty",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("")',
        description="Empty string is not a term",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="make_constant_term_c",
        method="NonVariableTerm.makeConstantTerm",
        setup=_IMPORTS,
        call='NonVariableTerm.makeConstantTerm(OperationSymbol("c", 0))',
        description="Create constant term from a nullary OperationSymbol",
    ),
    TestCaseSpec(
        id="make_constant_term_e",
        method="NonVariableTerm.makeConstantTerm",
        setup=_IMPORTS,
        call='NonVariableTerm.makeConstantTerm(OperationSymbol("e", 0))',
        description="Create constant term e()",
    ),
    TestCaseSpec(
        id="is_valid_var_string_x0",
        method="Terms.isValidVarString",
        setup=_IMPORTS,
        call='Terms.isValidVarString("x0")',
        description="x0 is a valid variable name",
        skip_string_check=True,
        notes="Java str(true) vs Python str(True).",
    ),
    TestCaseSpec(
        id="is_valid_var_string_empty",
        method="Terms.isValidVarString",
        setup=_IMPORTS,
        call='Terms.isValidVarString("")',
        description="Empty string is not a valid variable name",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="is_valid_op_name_f",
        method="Terms.isValidOpNameString",
        setup=_IMPORTS,
        call='Terms.isValidOpNameString("f")',
        description="f is a valid operation name",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="is_valid_op_name_plus",
        method="Terms.isValidOpNameString",
        setup=_IMPORTS,
        call='Terms.isValidOpNameString("+")',
        description="'+' is not a valid operation name",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="flatten_associative",
        method="Terms.flatten",
        setup=_IMPORTS
        + """
x = VariableImp("x")
fsym = OperationSymbol("f", 2, True)
inner = NonVariableTerm(fsym, [x, x])
nested = NonVariableTerm(fsym, [x, inner])
""",
        call="Terms.flatten(nested)",
        description="Flatten associative nested f(x,f(x,x)) to f(x,x,x)",
    ),
    TestCaseSpec(
        id="variable_imp_x0",
        method="VariableImp.getName",
        setup=_IMPORTS + """
v = VariableImp("x0")
""",
        call="v.getName()",
        description="VariableImp constructor and getName",
    ),
    TestCaseSpec(
        id="variable_imp_isa_variable",
        method="VariableImp.isaVariable",
        setup=_IMPORTS + """
v = VariableImp("y")
""",
        call="v.isaVariable()",
        description="VariableImp.isaVariable is true",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="non_variable_isa_variable",
        method="NonVariableTerm.isaVariable",
        setup=_IMPORTS + """
t = NonVariableTerm.makeConstantTerm(OperationSymbol("c", 0))
""",
        call="t.isaVariable()",
        description="Constant term isaVariable is false",
        skip_string_check=True,
    ),
]
