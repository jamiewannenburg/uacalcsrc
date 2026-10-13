"""Test case specifications for org.uacalc.terms behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

# Test cases for Terms
TEST_CASES = [
    TestCaseSpec(
        id="string_to_term_variable",
        method="Terms.stringToTerm",
        args=["x0"],
        description="Parse a variable term"
    ),
    TestCaseSpec(
        id="string_to_term_unary_op",
        method="Terms.stringToTerm",
        args=["f(x0)"],
        description="Parse a term with unary operation"
    ),
    TestCaseSpec(
        id="string_to_term_binary_op",
        method="Terms.stringToTerm",
        args=["+(x0,x1)"],
        description="Parse a term with binary operation"
    ),
    TestCaseSpec(
        id="string_to_term_nested",
        method="Terms.stringToTerm",
        args=["f(g(x0,x1))"],
        description="Parse a nested term"
    ),
    TestCaseSpec(
        id="make_constant_term_0",
        method="NonVariableTerm.makeConstantTerm",
        args=[0],
        description="Create constant term for value 0"
    ),
    TestCaseSpec(
        id="make_constant_term_5",
        method="NonVariableTerm.makeConstantTerm",
        args=[5],
        description="Create constant term for value 5"
    ),
]
