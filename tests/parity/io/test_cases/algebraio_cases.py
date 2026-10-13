"""Test case specifications for org.uacalc.io.AlgebraIO behavioral parity."""

from pathlib import Path
import sys

# Add parity test base to path
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

# Test cases for AlgebraIO
TEST_CASES = [
    TestCaseSpec(
        id="read_cyclic2",
        method="AlgebraIO.readAlgebraFile",
        args=["resources/algebras/cyclic2.ua"],
        description="Read cyclic2 algebra from file"
    ),
    TestCaseSpec(
        id="read_cyclic3",
        method="AlgebraIO.readAlgebraFile",
        args=["resources/algebras/cyclic3.ua"],
        description="Read cyclic3 algebra from file"
    ),
    TestCaseSpec(
        id="read_lat2",
        method="AlgebraIO.readAlgebraFile",
        args=["resources/algebras/lat2.ua"],
        description="Read lat2 algebra from file"
    ),
    TestCaseSpec(
        id="read_n5",
        method="AlgebraIO.readAlgebraFile",
        args=["resources/algebras/n5.ua"],
        description="Read n5 algebra from file"
    ),
    TestCaseSpec(
        id="read_invalid",
        method="AlgebraIO.readAlgebraFile",
        args=["resources/algebras/invalid_parity.ua"],
        description="Reading invalid file should raise BadAlgebraFileException",
        expected_exception="BadAlgebraFileException"
    ),
    TestCaseSpec(
        id="read_nonexistent",
        method="AlgebraIO.readAlgebraFile",
        args=["resources/algebras/nonexistent.ua"],
        description="Reading nonexistent file should raise exception",
        expected_exception="FileNotFoundException"
    ),
]
