"""
Tests for MaltsevProductDecomposition class.

This module tests the Python bindings for the MaltsevProductDecomposition class,
which represents a decomposition of an idempotent algebra into a quotient
and block subalgebras.
"""

import unittest
import os
import sys

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import uacalc_lib
    HAS_UACALC = True
except ImportError:
    HAS_UACALC = False


@unittest.skipUnless(HAS_UACALC, "uacalc_lib not available")
class TestMaltsevProductDecomposition(unittest.TestCase):
    """Test cases for MaltsevProductDecomposition class."""
    
    def test_basic_creation(self):
        """Test basic creation of MaltsevProductDecomposition."""
        # Create a basic algebra with 4 elements
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicSmallAlgebra("TestAlgebra", 4, [])
        
        # Create a congruence with blocks {0,1}, {2,3}
        congruence = Partition([-2, 0, -2, 2])
        
        # Create decomposition
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Verify properties
        self.assertEqual(decomp.cardinality(), 4)
        self.assertEqual(decomp.get_congruence().number_of_blocks(), 2)
        self.assertEqual(decomp.get_block_count(), 2)  # Two blocks with >1 element
        self.assertEqual(decomp.get_quotient_cardinality(), 2)  # Two equivalence classes
    
    def test_single_block_congruence(self):
        """Test decomposition with single block congruence."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicSmallAlgebra("TestAlgebra", 3, [])
        
        # Create a congruence with one block {0,1,2}
        congruence = Partition([-3, 0, 0])
        
        # Create decomposition
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Verify properties
        self.assertEqual(decomp.cardinality(), 3)
        self.assertEqual(decomp.get_congruence().number_of_blocks(), 1)
        self.assertEqual(decomp.get_block_count(), 1)  # One block with >1 element
        self.assertEqual(decomp.get_quotient_cardinality(), 1)  # One equivalence class
    
    def test_zero_congruence(self):
        """Test decomposition with zero congruence (all singleton blocks)."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicSmallAlgebra("TestAlgebra", 3, [])
        
        # Create zero congruence (all singleton blocks)
        congruence = Partition([-1, -1, -1])
        
        # Create decomposition
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Verify properties
        self.assertEqual(decomp.cardinality(), 3)
        self.assertEqual(decomp.get_congruence().number_of_blocks(), 3)
        self.assertEqual(decomp.get_block_count(), 0)  # No blocks with >1 element
        self.assertEqual(decomp.get_quotient_cardinality(), 3)  # Three equivalence classes
    
    def test_get_congruence(self):
        """Test getting the congruence partition."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicSmallAlgebra("TestAlgebra", 4, [])
        congruence = Partition([-2, 0, -2, 2])
        orig_blocks = congruence.number_of_blocks()
        
        # Create decomposition
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Get congruence and verify
        returned_cong = decomp.get_congruence()
        self.assertEqual(returned_cong.number_of_blocks(), orig_blocks)
        self.assertEqual(returned_cong.size(), 4)
    
    def test_invalid_congruence_size(self):
        """Test that creating decomposition with mismatched sizes raises error."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicSmallAlgebra("TestAlgebra", 4, [])
        
        # Create congruence with wrong size (5 elements)
        congruence = Partition([-2, 0, -2, 2, -1])
        
        # Should raise ValueError with size mismatch
        with self.assertRaises(ValueError) as context:
            MaltsevProductDecomposition(algebra, congruence)
        
        self.assertIn("does not match", str(context.exception))
    
    def test_str_repr(self):
        """Test string and repr methods."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicSmallAlgebra("TestAlgebra", 4, [])
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
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        Partition = uacalc_lib.alg.Partition
        MaltsevProductDecomposition = uacalc_lib.alg.MaltsevProductDecomposition
        
        algebra = BasicSmallAlgebra("TestAlgebra", 6, [])
        
        # Create congruence with blocks {0,1,2}, {3,4}, {5}
        congruence = Partition([-3, 0, 0, -2, 3, -1])
        
        # Create decomposition
        decomp = MaltsevProductDecomposition(algebra, congruence)
        
        # Verify properties
        self.assertEqual(decomp.cardinality(), 6)
        self.assertEqual(decomp.get_congruence().number_of_blocks(), 3)
        self.assertEqual(decomp.get_block_count(), 2)  # Two blocks with >1 element
        self.assertEqual(decomp.get_quotient_cardinality(), 3)  # Three equivalence classes


if __name__ == '__main__':
    unittest.main()
