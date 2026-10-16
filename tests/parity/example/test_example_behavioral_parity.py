"""Behavioral parity tests for org.uacalc.example demo classes."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import BehavioralParityTest
from tests.parity.example.test_cases.example_cases import TEST_CASES

pytestmark = pytest.mark.behavioral


class TestExampleBehavioralParity(BehavioralParityTest):
    package = "example"
    golden_file = "example_jython.json"


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
        TestExampleBehavioralParity,
        "test_{0}".format(_case.id),
        _bind(_case),
    )
