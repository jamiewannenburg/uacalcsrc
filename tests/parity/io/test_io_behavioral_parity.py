"""Behavioral parity tests for org.uacalc.io.

Classification: BEHAVIORAL - exact functional parity with golden outputs.
These tests compare CPython outputs against Jython/Java golden data for exact match.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure test base is on path
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import BehavioralParityTest

pytestmark = pytest.mark.behavioral


class TestAlgebraIOBehavioralParity(BehavioralParityTest):
    """Behavioral parity tests for AlgebraIO using golden data."""
    
    package = "io"
    golden_file = "AlgebraIO_jython.json"
    
    def test_read_cyclic2(self):
        """Test reading cyclic2.ua algebra file."""
        self.run_golden_test_case("read_cyclic2")
    
    def test_read_cyclic3(self):
        """Test reading cyclic3.ua algebra file."""
        self.run_golden_test_case("read_cyclic3")
    
    def test_read_lat2(self):
        """Test reading lat2.ua algebra file."""
        self.run_golden_test_case("read_lat2")
    
    def test_read_n5(self):
        """Test reading n5.ua algebra file."""
        self.run_golden_test_case("read_n5")
    
    def test_read_invalid(self):
        """Test that reading invalid file raises BadAlgebraFileException."""
        self.run_golden_test_case("read_invalid")
    
    def test_read_nonexistent(self):
        """Test that reading nonexistent file raises exception."""
        self.run_golden_test_case("read_nonexistent")


# Note: This test class will only run if golden data exists.
# Generate golden data with: python3 tools/generate_golden_data.py --package io
# 
# The golden data contains exact expected outputs from Java/Jython for:
# - Algebra name, cardinality, operation count
# - Exception types and messages for error cases
# - String representations
#
# Any mismatch indicates:
# - A bug in the Rust/Python implementation (fix it)
# - An intentional difference (document in KNOWN_DIFFERENCES.md)
# - Incorrect golden data (verify against Java UACalc)
