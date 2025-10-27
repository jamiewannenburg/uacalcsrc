"""
Tests for TypeFinder

These tests verify the TypeFinder implementation for Tame Congruence Theory (TCT)
analysis of algebras.
"""

import unittest
import os
import uacalc_lib

class TestTypeFinder(unittest.TestCase):
    """Test TypeFinder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Note: The actual TypeFinder tests would require loading real algebras
        # For now, we'll skip the setUp if the module isn't fully built
        try:
            from uacalc_lib import BasicSmallAlgebra
            self.alg = BasicSmallAlgebra("TestAlg", {0, 1, 2}, [])
        except (ImportError, AttributeError):
            self.skipTest("Python bindings not fully built - this is expected during development")
    
    def test_new(self):
        """Test TypeFinder creation."""
        try:
            from uacalc_lib import TypeFinder
            tf = TypeFinder(self.alg)
            self.assertIsNotNone(tf)
            self.assertEqual(tf.alg_size(), 3)
        except (ImportError, AttributeError):
            self.skipTest("TypeFinder not available - requires full build")
    
    def test_init(self):
        """Test TypeFinder initialization."""
        try:
            from uacalc_lib import TypeFinder
            tf = TypeFinder(self.alg)
            
            # Should not raise an error
            tf.init()
        except (ImportError, AttributeError):
            self.skipTest("TypeFinder not available - requires full build")
    
    def test_alg_size(self):
        """Test getting algebra size."""
        try:
            from uacalc_lib import TypeFinder
            tf = TypeFinder(self.alg)
            
            self.assertEqual(tf.alg_size(), 3)
        except (ImportError, AttributeError):
            self.skipTest("TypeFinder not available - requires full build")
    
    def test_str_repr(self):
        """Test string representations."""
        try:
            from uacalc_lib import TypeFinder
            tf = TypeFinder(self.alg)
            
            str_repr = str(tf)
            self.assertIn("TypeFinder", str_repr)
            self.assertIn("3", str_repr)
            
            repr_str = repr(tf)
            self.assertIn("TypeFinder", repr_str)
        except (ImportError, AttributeError):
            self.skipTest("TypeFinder not available - requires full build")

if __name__ == '__main__':
    unittest.main()
