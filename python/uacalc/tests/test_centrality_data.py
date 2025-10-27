"""
Test suite for CentralityData class.

Tests the Rust implementation of CentralityData against expected behavior.
"""

import unittest
import sys
import os

# Add parent directory to path to import uacalc_lib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    import uacalc_lib
    UACALC_AVAILABLE = True
except ImportError:
    UACALC_AVAILABLE = False


@unittest.skipUnless(UACALC_AVAILABLE, "uacalc_lib not available")
class TestCentralityData(unittest.TestCase):
    """Test CentralityData implementation."""
    
    def test_creation(self):
        """Test creating a CentralityData object."""
        # Import classes through uacalc_lib module
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create binary relations
        left = BasicBinaryRelation(3)
        left.add(0, 1)
        
        right = BasicBinaryRelation(3)
        right.add(1, 2)
        
        # Create partition
        delta = Partition.zero(3)
        
        # Create CentralityData
        data = CentralityData(left, right, delta)
        
        self.assertIsNotNone(data)
        self.assertEqual(data.universe_size(), 3)
        self.assertEqual(data.delta_blocks(), 3)
    
    def test_getters(self):
        """Test getter methods."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        left = BasicBinaryRelation(3)
        right = BasicBinaryRelation(3)
        delta = Partition.zero(3)
        
        data = CentralityData(left, right, delta)
        
        self.assertEqual(data.universe_size(), 3)
        self.assertEqual(data.delta_blocks(), 3)
    
    def test_validation(self):
        """Test validation of universe sizes."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create relations with mismatched sizes
        left = BasicBinaryRelation(3)
        right = BasicBinaryRelation(4)
        delta = Partition.zero(3)
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            data = CentralityData(left, right, delta)
    
    def test_comparison(self):
        """Test comparison methods."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        left1 = BasicBinaryRelation(3)
        right1 = BasicBinaryRelation(3)
        delta1 = Partition.zero(3)
        data1 = CentralityData(left1, right1, delta1)
        
        left2 = BasicBinaryRelation(3)
        right2 = BasicBinaryRelation(3)
        delta2 = Partition.one(3)
        data2 = CentralityData(left2, right2, delta2)
        
        # Test compare_to
        cmp = data1.compare_to(data2)
        self.assertIsInstance(cmp, int)
        
        # Test comparison operators
        self.assertNotEqual(data1, data2)
    
    def test_string_representation(self):
        """Test string representation."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        left = BasicBinaryRelation(2)
        left.add(0, 1)
        right = BasicBinaryRelation(2)
        right.add(1, 0)
        delta = Partition.zero(2)
        
        data = CentralityData(left, right, delta)
        
        # Test __str__
        str_rep = str(data)
        self.assertIsInstance(str_rep, str)
        self.assertIn("left:", str_rep)
        self.assertIn("right:", str_rep)
        self.assertIn("delta:", str_rep)
        
        # Test __repr__
        repr_rep = repr(data)
        self.assertIsInstance(repr_rep, str)
        self.assertIn("CentralityData", repr_rep)


if __name__ == '__main__':
    unittest.main()
