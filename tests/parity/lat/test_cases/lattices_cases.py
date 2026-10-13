"""Test case specifications for org.uacalc.lat.Lattices behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

# Test cases for Lattices static methods
TEST_CASES = [
    TestCaseSpec(
        id="lattice_from_join_2chain",
        method="Lattices.latticeFromJoin",
        args=[
            # Join table for 2-element chain: 0 < 1
            # join(0,0)=0, join(0,1)=1, join(1,0)=1, join(1,1)=1
            [[0, 1], [1, 1]]
        ],
        description="Build 2-element chain from join table",
        skip_string_check=True  # Lattice string repr may vary
    ),
    TestCaseSpec(
        id="lattice_from_meet_2chain",
        method="Lattices.latticeFromMeet",
        args=[
            # Meet table for 2-element chain: 0 < 1
            # meet(0,0)=0, meet(0,1)=0, meet(1,0)=0, meet(1,1)=1
            [[0, 0], [0, 1]]
        ],
        description="Build 2-element chain from meet table",
        skip_string_check=True
    ),
    TestCaseSpec(
        id="lattice_from_join_diamond",
        method="Lattices.latticeFromJoin",
        args=[
            # Diamond M3: 0 at bottom, 1/2 incomparable, 3 at top
            [[0, 3, 3, 3],
             [3, 1, 3, 3],
             [3, 3, 2, 3],
             [3, 3, 3, 3]]
        ],
        description="Build diamond lattice M3 from join table",
        skip_string_check=True
    ),
]
