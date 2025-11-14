"""
Tests for Polymorphisms class.
"""

import unittest
import uacalc_lib


class TestPolymorphisms(unittest.TestCase):
    """Test Polymorphisms class."""
    
    def test_constructor_basic(self):
        """Test basic constructor."""
        Partition = uacalc_lib.alg.Partition
        Polymorphisms = uacalc_lib.alg.Polymorphisms
        
        pars = [Partition.zero(3), Partition.one(3)]
        poly = Polymorphisms(1, pars, False, None)
        
        self.assertEqual(poly.get_alg_size(), 3)
        self.assertEqual(poly.get_arity(), 1)
        self.assertEqual(poly.get_table_size(), 3)
        self.assertEqual(poly.num_partitions(), 2)
        self.assertFalse(poly.is_idempotent())
    
    def test_constructor_with_fixed_values(self):
        """Test constructor with fixed values."""
        Partition = uacalc_lib.alg.Partition
        Polymorphisms = uacalc_lib.alg.Polymorphisms
        
        pars = [Partition.zero(3)]
        fixed_values = [0, 1, 2]
        poly = Polymorphisms(2, pars, True, fixed_values)
        
        self.assertEqual(poly.get_alg_size(), 3)
        self.assertEqual(poly.get_arity(), 2)
        self.assertEqual(poly.get_table_size(), 9)
        self.assertTrue(poly.is_idempotent())
        self.assertEqual(poly.get_fixed_values(), fixed_values)
    
    def test_constructor_different_arity(self):
        """Test constructor with different arity."""
        Partition = uacalc_lib.alg.Partition
        Polymorphisms = uacalc_lib.alg.Polymorphisms
        
        pars = [Partition.zero(4)]
        poly = Polymorphisms(3, pars, False, None)
        
        self.assertEqual(poly.get_alg_size(), 4)
        self.assertEqual(poly.get_arity(), 3)
        self.assertEqual(poly.get_table_size(), 64)
    
    def test_make_graph(self):
        """Test make_graph method."""
        Partition = uacalc_lib.alg.Partition
        Polymorphisms = uacalc_lib.alg.Polymorphisms
        
        pars = [Partition.zero(3)]
        poly = Polymorphisms(1, pars, False, None)
        
        self.assertFalse(poly.has_graph())
        poly.make_graph()
        self.assertTrue(poly.has_graph())
    
    def test_partial_op_table(self):
        """Test partial operation table methods."""
        Partition = uacalc_lib.alg.Partition
        Polymorphisms = uacalc_lib.alg.Polymorphisms
        
        pars = [Partition.zero(3)]
        poly = Polymorphisms(1, pars, False, None)
        
        self.assertIsNone(poly.get_partial_op_table())
        
        table = [0, 1, 2]
        poly.set_partial_op_table(table)
        self.assertEqual(poly.get_partial_op_table(), table)
    
    def test_string_representation(self):
        """Test string representation."""
        Partition = uacalc_lib.alg.Partition
        Polymorphisms = uacalc_lib.alg.Polymorphisms
        
        pars = [Partition.zero(3), Partition.one(3)]
        poly = Polymorphisms(1, pars, False, None)
        
        s = str(poly)
        self.assertIn("arity=1", s)
        self.assertIn("partitions=2", s)
        self.assertIn("alg_size=3", s)
    
    def test_equality(self):
        """Test equality comparison."""
        Partition = uacalc_lib.alg.Partition
        Polymorphisms = uacalc_lib.alg.Polymorphisms
        
        pars1 = [Partition.zero(3), Partition.one(3)]
        pars2 = [Partition.zero(3), Partition.one(3)]
        pars3 = [Partition.zero(3)]
        
        poly1 = Polymorphisms(1, pars1, False, None)
        poly2 = Polymorphisms(1, pars2, False, None)
        poly3 = Polymorphisms(1, pars3, False, None)
        
        self.assertEqual(poly1, poly2)
        self.assertNotEqual(poly1, poly3)
    
    def test_hash(self):
        """Test hash function."""
        Partition = uacalc_lib.alg.Partition
        Polymorphisms = uacalc_lib.alg.Polymorphisms
        
        pars1 = [Partition.zero(3), Partition.one(3)]
        pars2 = [Partition.zero(3), Partition.one(3)]
        
        poly1 = Polymorphisms(1, pars1, False, None)
        poly2 = Polymorphisms(1, pars2, False, None)
        
        self.assertEqual(hash(poly1), hash(poly2))


if __name__ == '__main__':
    unittest.main()

