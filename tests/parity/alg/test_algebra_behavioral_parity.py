"""Behavioral parity tests for org.uacalc.alg Algebra, SmallAlgebra, BasicAlgebra."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import BehavioralParityTest
from tests.parity.alg.test_cases.algebra_cases import TEST_CASES as _ALG_CASES
from tests.parity.alg.test_cases.sub_prod_quot_cases import TEST_CASES as _SPQ_CASES
from tests.parity.alg.test_cases.free_hom_closer_cases import TEST_CASES as _FHC_CASES
from tests.parity.alg.test_cases.remaining_alg_cases import TEST_CASES as _REM_CASES

TEST_CASES = list(_ALG_CASES) + list(_SPQ_CASES) + list(_FHC_CASES) + list(_REM_CASES)

pytestmark = pytest.mark.behavioral


class TestAlgebraBehavioralParity(BehavioralParityTest):
    package = "alg"
    golden_file = "alg_jython.json"


def _bind(case):
    def test(self):
        self.run_golden_test_case(case.id)

    test.__name__ = "test_{0}".format(case.id)
    test.__doc__ = case.description
    if case.xfail_reason:
        test = pytest.mark.xfail(reason=case.xfail_reason, strict=True)(test)
    return test


for _case in TEST_CASES:
    setattr(
        TestAlgebraBehavioralParity, "test_{0}".format(_case.id), _bind(_case)
    )
