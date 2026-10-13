"""Behavioral parity tests for org.uacalc.terms.

Classification: BEHAVIORAL - exact functional parity with golden outputs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import BehavioralParityTest

pytestmark = pytest.mark.behavioral


@pytest.mark.skipif(
    not (REPO_ROOT / "tests" / "parity" / "terms" / "golden_data" / "Terms_jython.json").exists(),
    reason="Golden data not generated. Run: python3 tools/generate_golden_data.py --package terms"
)
class TestTermsBehavioralParity(BehavioralParityTest):
    """Behavioral parity tests for Terms methods."""
    
    package = "terms"
    golden_file = "Terms_jython.json"
    
    def test_string_to_term_variable(self):
        """Test parsing a variable term."""
        self.run_golden_test_case("string_to_term_variable")
    
    def test_string_to_term_unary_op(self):
        """Test parsing a term with unary operation."""
        self.run_golden_test_case("string_to_term_unary_op")
    
    def test_string_to_term_binary_op(self):
        """Test parsing a term with binary operation."""
        self.run_golden_test_case("string_to_term_binary_op")
    
    def test_string_to_term_nested(self):
        """Test parsing a nested term."""
        self.run_golden_test_case("string_to_term_nested")
    
    def test_make_constant_term_0(self):
        """Test creating constant term for value 0."""
        self.run_golden_test_case("make_constant_term_0")
    
    def test_make_constant_term_5(self):
        """Test creating constant term for value 5."""
        self.run_golden_test_case("make_constant_term_5")
