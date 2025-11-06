"""
Tests for MaltsevProductDecomposition class.

This module tests the Python bindings for the MaltsevProductDecomposition class,
which represents a decomposition of an idempotent algebra into a quotient
and block subalgebras. Includes Java comparison tests for validation.
"""

import unittest
import os
import sys
import json
import subprocess
import pytest

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import uacalc_lib
    HAS_UACALC = True
except ImportError:
    HAS_UACALC = False

from test_utils import build_java_command


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    wrapper_class = "java_wrapper.src.alg.MaltsevProductDecompositionWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")
        
        output = json.loads(result.stdout)
        # The data field contains a JSON object, so we need to parse it again if it's a string
        if "data" in output and isinstance(output["data"], str):
            output["data"] = json.loads(output["data"])
        return output
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Java wrapper output: {e}")


@unittest.skipUnless(HAS_UACALC, "uacalc_lib not available")
class TestMaltsevProductDecomposition(unittest.TestCase):
    """Test cases for MaltsevProductDecomposition class."""
    
    def test_basic_creation(self):
        """Test basic creation of MaltsevProductDecomposition."""
        # Create a basic algebra with 4 elements
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicAlgebra("TestAlgebra", [0, 1, 2, 3])
        
        # Create a congruence with blocks {0,1}, {2,3}
        congruence = Partition([-2, 0, -2, 2])
        
        # Create decomposition
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Verify properties
        self.assertEqual(decomp.cardinality(), 4)
        self.assertEqual(decomp.get_congruence().number_of_blocks(), 2)
        self.assertEqual(decomp.get_block_count(), 2)  # Two blocks with >1 element
        self.assertEqual(decomp.get_quotient_cardinality(), 2)  # Two equivalence classes
        
        # Java comparison test
        java_result = run_java_wrapper("test", [])
        self.assertEqual(decomp.cardinality(), java_result["data"]["algebra_cardinality"])
        self.assertEqual(decomp.get_congruence().number_of_blocks(), java_result["data"]["congruence_blocks"])
        self.assertEqual(decomp.get_block_count(), java_result["data"]["block_count"])
        self.assertEqual(decomp.get_quotient_cardinality(), java_result["data"]["quotient_cardinality"])
    
    def test_single_block_congruence(self):
        """Test decomposition with single block congruence."""
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicAlgebra("TestAlgebra", [0, 1, 2])
        
        # Create a congruence with one block {0,1,2}
        congruence = Partition([-3, 0, 0])
        
        # Create decomposition
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Verify properties
        self.assertEqual(decomp.cardinality(), 3)
        self.assertEqual(decomp.get_congruence().number_of_blocks(), 1)
        self.assertEqual(decomp.get_block_count(), 1)  # One block with >1 element
        self.assertEqual(decomp.get_quotient_cardinality(), 1)  # One equivalence class
        
        # Java comparison test - create new decomposition with same parameters
        java_result = run_java_wrapper("new", ["--cardinality", "3", "--congruence", "-3,0,0"])
        self.assertEqual(decomp.cardinality(), java_result["data"]["algebra_cardinality"])
        self.assertEqual(decomp.get_congruence().number_of_blocks(), java_result["data"]["congruence_blocks"])
        self.assertEqual(decomp.get_block_count(), java_result["data"]["block_count"])
        self.assertEqual(decomp.get_quotient_cardinality(), java_result["data"]["quotient_cardinality"])
    
    def test_zero_congruence(self):
        """Test decomposition with zero congruence (all singleton blocks)."""
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicAlgebra("TestAlgebra", [0, 1, 2])
        
        # Create zero congruence (all singleton blocks)
        congruence = Partition([-1, -1, -1])
        
        # Create decomposition
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Verify properties
        self.assertEqual(decomp.cardinality(), 3)
        self.assertEqual(decomp.get_congruence().number_of_blocks(), 3)
        self.assertEqual(decomp.get_block_count(), 0)  # No blocks with >1 element
        self.assertEqual(decomp.get_quotient_cardinality(), 3)  # Three equivalence classes
        
        # Java comparison test - create new decomposition with same parameters
        java_result = run_java_wrapper("new", ["--cardinality", "3", "--congruence", "-1,-1,-1"])
        self.assertEqual(decomp.cardinality(), java_result["data"]["algebra_cardinality"])
        self.assertEqual(decomp.get_congruence().number_of_blocks(), java_result["data"]["congruence_blocks"])
        self.assertEqual(decomp.get_block_count(), java_result["data"]["block_count"])
        self.assertEqual(decomp.get_quotient_cardinality(), java_result["data"]["quotient_cardinality"])
    
    def test_get_congruence(self):
        """Test getting the congruence partition."""
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicAlgebra("TestAlgebra", [0, 1, 2, 3])
        congruence = Partition([-2, 0, -2, 2])
        orig_blocks = congruence.number_of_blocks()
        
        # Create decomposition
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Get congruence and verify
        returned_cong = decomp.get_congruence()
        self.assertEqual(returned_cong.number_of_blocks(), orig_blocks)
        self.assertEqual(returned_cong.universe_size(), 4)
        
        # Java comparison test - create new decomposition and get congruence
        java_result = run_java_wrapper("new", ["--cardinality", "4", "--congruence", "-2,0,-2,2"])
        self.assertEqual(returned_cong.number_of_blocks(), java_result["data"]["congruence_blocks"])
        self.assertEqual(returned_cong.universe_size(), 4)  # We know the universe size from the algebra
    
    def test_invalid_congruence_size(self):
        """Test that creating decomposition with mismatched sizes raises error."""
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicAlgebra("TestAlgebra", [0, 1, 2, 3])
        
        # Create congruence with wrong size (5 elements)
        congruence = Partition([-2, 0, -2, 2, -1])
        
        # Should raise ValueError with size mismatch
        with self.assertRaises(ValueError) as context:
            MaltsevProductDecomposition(algebra, congruence)
        
        self.assertIn("does not match", str(context.exception))
    
    def test_str_repr(self):
        """Test string and repr methods."""
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicAlgebra("TestAlgebra", [0, 1, 2, 3])
        congruence = Partition([-2, 0, -2, 2])
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Test __str__
        str_output = str(decomp)
        self.assertIn("MaltsevProductDecomposition", str_output)
        self.assertIn("TestAlgebra", str_output)
        
        # Test __repr__
        repr_output = repr(decomp)
        self.assertIn("MaltsevProductDecomposition", repr_output)
        self.assertIn("blocks=", repr_output)
    
    def test_larger_algebra(self):
        """Test decomposition with larger algebra."""
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicAlgebra("TestAlgebra", [0, 1, 2, 3, 4, 5])
        
        # Create congruence with blocks {0,1,2}, {3,4}, {5}
        congruence = Partition([-3, 0, 0, -2, 3, -1])
        
        # Create decomposition
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Verify properties
        self.assertEqual(decomp.cardinality(), 6)
        self.assertEqual(decomp.get_congruence().number_of_blocks(), 3)
        self.assertEqual(decomp.get_block_count(), 2)  # Two blocks with >1 element
        self.assertEqual(decomp.get_quotient_cardinality(), 3)  # Three equivalence classes
        
        # Java comparison test - create new decomposition with same parameters
        java_result = run_java_wrapper("new", ["--cardinality", "6", "--congruence", "-3,0,0,-2,3,-1"])
        self.assertEqual(decomp.cardinality(), java_result["data"]["algebra_cardinality"])
        self.assertEqual(decomp.get_congruence().number_of_blocks(), java_result["data"]["congruence_blocks"])
        self.assertEqual(decomp.get_block_count(), java_result["data"]["block_count"])
        self.assertEqual(decomp.get_quotient_cardinality(), java_result["data"]["quotient_cardinality"])


if __name__ == '__main__':
    unittest.main()
