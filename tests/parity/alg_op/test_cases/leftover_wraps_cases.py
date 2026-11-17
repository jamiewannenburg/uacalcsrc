"""Golden parity cases for leftover org.uacalc.alg.op wrappers."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.alg.op import OperationSymbol
plus = OperationSymbol("+", 2)
unary = OperationSymbol("u", 1)
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_NONE = dict(skip_string_check=True, notes="Java exception vs Python.")

TEST_CASES = [
    TestCaseSpec(
        id="os_set_associative_true",
        method="OperationSymbol.setAssociative",
        setup=_SETUP,
        call="plus.setAssociative(True) or plus.isAssociative()",
        description="binary OperationSymbol can be marked associative",
        **_BOOL
    ),
    TestCaseSpec(
        id="os_set_associative_unary_iae",
        method="OperationSymbol.setAssociative",
        setup=_SETUP,
        call="unary.setAssociative(True)",
        description="unary setAssociative(True) is IllegalArgumentException",
        compare_exception_message=False,
        **_NONE
    ),
    TestCaseSpec(
        id="os_get_operation_symbol_11",
        method="OperationSymbol.getOperationSymbol",
        setup=_SETUP,
        call="OperationSymbol.getOperationSymbol(11).name()[:2]",
        description="getOperationSymbol(11) uses the uniform high-arity prefix",
    ),
    TestCaseSpec(
        id="os_get_operation_symbol_12",
        method="OperationSymbol.getOperationSymbol",
        setup=_SETUP,
        call="OperationSymbol.getOperationSymbol(12).name()[:2]",
        description="getOperationSymbol(12) uses the uniform high-arity prefix",
    ),
]
