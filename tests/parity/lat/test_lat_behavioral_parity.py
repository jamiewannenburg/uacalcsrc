"""Behavioral parity tests for org.uacalc.lat.

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


class TestLatticesBehavioralParity(BehavioralParityTest):
    """Behavioral parity tests for Lattices static methods."""
    
    package = "lat"
    golden_file = "Lattices_jython.json"
    
    def test_lattice_from_join_2chain(self):
        """Test latticeFromJoin with 2-element chain."""
        self.run_golden_test_case("lattice_from_join_2chain")
    
    def test_lattice_from_meet_2chain(self):
        """Test latticeFromMeet with 2-element chain."""
        self.run_golden_test_case("lattice_from_meet_2chain")
    
    def test_lattice_from_join_diamond(self):
        """Test latticeFromJoin with diamond lattice M3."""
        self.run_golden_test_case("lattice_from_join_diamond")
