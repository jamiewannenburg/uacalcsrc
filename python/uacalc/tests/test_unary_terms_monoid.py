"""
Tests for UnaryTermsMonoid.

This module tests the UnaryTermsMonoid class which represents the monoid
of all unary terms over a generating algebra, with term composition as the
binary operation.
"""

import unittest
import uacalc_lib


class TestUnaryTermsMonoid(unittest.TestCase):
    """Test UnaryTermsMonoid functionality."""
    
    def test_creation(self):
        """Test creating a UnaryTermsMonoid."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        # Create a simple generating algebra
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        
        # Create UnaryTermsMonoid
        monoid = UnaryTermsMonoid(base_alg)
        
        self.assertIsNotNone(monoid)
        self.assertIn("UnaryTerms", monoid.name())
        self.assertIn("TestBase", monoid.name())
    
    def test_creation_with_id(self):
        """Test creating a UnaryTermsMonoid with include_id flag."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        # Create a simple generating algebra
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        
        # Create UnaryTermsMonoid with include_id
        monoid = UnaryTermsMonoid.new_with_id(base_alg, True)
        
        self.assertIsNotNone(monoid)
        self.assertEqual(monoid.algebra_type(), "UNARY_TERMS_MONOID")
    
    def test_algebra_type(self):
        """Test algebra_type method."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        self.assertEqual(monoid.algebra_type(), "UNARY_TERMS_MONOID")
    
    def test_cardinality(self):
        """Test cardinality method."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        # For an algebra with no operations, the only unary term is x (the variable)
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # Should have at least 1 term (the variable)
        self.assertGreater(monoid.cardinality(), 0)
    
    def test_name_operations(self):
        """Test name getter and setter."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # Check original name
        original_name = monoid.name()
        self.assertIn("UnaryTerms", original_name)
        
        # Set new name
        monoid.set_name("MyMonoid")
        self.assertEqual(monoid.name(), "MyMonoid")
    
    def test_is_unary(self):
        """Test is_unary method."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # UnaryTermsMonoid has a binary product operation, so is_unary should be False
        self.assertFalse(monoid.is_unary())
    
    def test_is_idempotent(self):
        """Test is_idempotent method."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # Check if the monoid is idempotent (depends on the algebra structure)
        result = monoid.is_idempotent()
        self.assertIsInstance(result, bool)
    
    def test_is_total(self):
        """Test is_total method."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # Check if the monoid is total (all operations should be total)
        result = monoid.is_total()
        self.assertIsInstance(result, bool)
    
    def test_operations_count(self):
        """Test operations_count method."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # Should have exactly one operation (the product operation)
        self.assertEqual(monoid.operations_count(), 1)
    
    def test_get_universe_list(self):
        """Test get_universe_list method."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        universe = monoid.get_universe_list()
        self.assertIsNotNone(universe)
        self.assertGreater(len(universe), 0)
        self.assertEqual(len(universe), monoid.cardinality())
    
    def test_get_element(self):
        """Test get_element method."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # Get first element
        elem0 = monoid.get_element(0)
        self.assertIsNotNone(elem0)
        
        # Out of bounds should return None
        card = monoid.cardinality()
        elem_out = monoid.get_element(card)
        self.assertIsNone(elem_out)
    
    def test_element_index(self):
        """Test element_index method."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # Get an element and find its index
        elem = monoid.get_element(0)
        if elem is not None:
            idx = monoid.element_index(elem)
            self.assertEqual(idx, 0)
    
    def test_str_and_repr(self):
        """Test __str__ and __repr__ methods."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # Test __str__
        str_repr = str(monoid)
        self.assertIn("UnaryTermsMonoid", str_repr)
        
        # Test __repr__
        repr_str = repr(monoid)
        self.assertIn("UnaryTermsMonoid", repr_str)
        self.assertIn("cardinality", repr_str)
    
    def test_len(self):
        """Test __len__ method."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # __len__ should return cardinality
        self.assertEqual(len(monoid), monoid.cardinality())
    
    def test_with_different_base_sizes(self):
        """Test UnaryTermsMonoid with different base algebra sizes."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        # Test with size 2
        base_alg2 = BasicSmallAlgebra("Base2", [0, 1])
        monoid2 = UnaryTermsMonoid(base_alg2)
        self.assertGreater(monoid2.cardinality(), 0)
        
        # Test with size 4
        base_alg4 = BasicSmallAlgebra("Base4", [0, 1, 2, 3])
        monoid4 = UnaryTermsMonoid(base_alg4)
        self.assertGreater(monoid4.cardinality(), 0)
    
    def test_product_operation_exists(self):
        """Test that the product operation exists and is binary."""
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        UnaryTermsMonoid = uacalc_lib.alg.UnaryTermsMonoid
        
        base_alg = BasicSmallAlgebra("TestBase", [0, 1, 2])
        monoid = UnaryTermsMonoid(base_alg)
        
        # Should have exactly 1 operation
        ops_count = monoid.operations_count()
        self.assertEqual(ops_count, 1)
        
        # The monoid should not be unary (has binary product)
        self.assertFalse(monoid.is_unary())


if __name__ == '__main__':
    unittest.main()
