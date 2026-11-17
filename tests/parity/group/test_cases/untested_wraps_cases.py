"""Parity cases for wrapped org.uacalc.group constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.group import PermutationGroup
from org.uacalc.util import IntArray

def _ia(vals):
    return IntArray([int(x) for x in list(vals)])

swap2 = _ia([1, 0])
id2 = PermutationGroup.id(2)
s2 = PermutationGroup('S2', [swap2])
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
    _c("ctor_perm_group_s2", "PermutationGroup.PermutationGroup",
       "s2.getName()", "PermutationGroup constructor name"),
    _c("ctor_perm_group_empty", "PermutationGroup.PermutationGroup",
       "PermutationGroup('G', []).getName()", "PermutationGroup empty generators"),
]
