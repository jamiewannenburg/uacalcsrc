"""
Tests for BasicAlgebra (BasicAlgebra in Java).

This module tests the BasicAlgebra class which represents small algebras
with a map from {0, ..., n-1} to the elements of the algebra.

Note: This is a partial implementation that excludes con() and sub() methods
(congruence and subalgebra lattices).
"""

import unittest
import uacalc_lib

BasicAlgebra = uacalc_lib.alg.BasicAlgebra
IntOperation = uacalc_lib.alg.IntOperation

class TestBasicAlgebra(unittest.TestCase):
    """Test BasicAlgebra functionality."""
    def test_creation(self):
        """Test creating a BasicAlgebra."""
        
        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        self.assertEqual(alg.name(), "test")
        self.assertEqual(alg.cardinality(), 5)
        self.assertEqual(alg.algebra_type(), "Basic")
    
    def test_int_universe(self):
        """Test int_universe method."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # Initially, universe list is not cached so int_universe returns True
        self.assertTrue(alg.int_universe())
    
    def test_get_element(self):
        """Test getting elements by index."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # Get elements
        elem0 = alg.get_element(0)
        elem2 = alg.get_element(2)
        elem4 = alg.get_element(4)
        
        self.assertIsNotNone(elem0)
        self.assertIsNotNone(elem2)
        self.assertIsNotNone(elem4)
        self.assertIn(elem0, [0, 1, 2, 3, 4])
        self.assertIn(elem2, [0, 1, 2, 3, 4])
        self.assertIn(elem4, [0, 1, 2, 3, 4])
        
        # Out of bounds should return -1
        self.assertEqual(alg.get_element(10), -1)
    
    def test_element_index(self):
        """Test getting element indices."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # Get indices
        idx0 = alg.element_index(0)
        idx2 = alg.element_index(2)
        idx4 = alg.element_index(4)
        
        self.assertGreaterEqual(idx0, 0)
        self.assertLess(idx0, 5)
        self.assertGreaterEqual(idx2, 0)
        self.assertLess(idx2, 5)
        self.assertGreaterEqual(idx4, 0)
        self.assertLess(idx4, 5)
        
        # Non-existent element should return -1
        self.assertEqual(alg.element_index(100), -1)
    
    def test_get_universe_list(self):
        """Test getting the universe as a list."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        universe_list = alg.get_universe_list()
        self.assertIsNotNone(universe_list)
        self.assertEqual(len(universe_list), 5)
        
        # Check that all elements are present
        for elem in [0, 1, 2, 3, 4]:
            self.assertIn(elem, universe_list)
    
    def test_get_universe_order(self):
        """Test getting the universe order map."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        universe_order = alg.get_universe_order()
        self.assertIsNotNone(universe_order)
        self.assertEqual(len(universe_order), 5)
        
        # Check that all elements have indices
        for elem in [0, 1, 2, 3, 4]:
            self.assertIn(elem, universe_order)
            self.assertGreaterEqual(universe_order[elem], 0)
            self.assertLess(universe_order[elem], 5)
    
    def test_algebra_type(self):
        """Test algebra type."""

        alg = BasicAlgebra("test", [0, 1, 2] ,[])
        
        self.assertEqual(alg.algebra_type(), "Basic")
    
    def test_cardinality(self):
        """Test cardinality with different sizes."""

        
        alg3 = BasicAlgebra("test3", [0, 1, 2] ,[])
        self.assertEqual(alg3.cardinality(), 3)
        
        alg10 = BasicAlgebra("test10", list(range(10 )),[])
        self.assertEqual(alg10.cardinality(), 10)
    
    def test_name_operations(self):
        """Test name getter and setter."""

        alg = BasicAlgebra("original", [0, 1, 2, 3, 4] ,[])
        
        self.assertEqual(alg.name(), "original")
        
        # Set new name
        alg.set_name("renamed")
        self.assertEqual(alg.name(), "renamed")
    
    def test_description_operations(self):
        """Test description getter and setter."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # Initially no description
        self.assertIsNone(alg.description())
        
        # Set description
        alg.set_description("A test algebra")
        self.assertEqual(alg.description(), "A test algebra")
        
        # Clear description
        alg.set_description(None)
        self.assertIsNone(alg.description())
    
    def test_reset_con_and_sub(self):
        """Test reset_con_and_sub method (partial implementation)."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # This should not raise an error (even though con/sub are not implemented)
        try:
            alg.reset_con_and_sub()
        except Exception as e:
            self.fail(f"reset_con_and_sub() raised an exception: {e}")
    
    def test_convert_to_default_value_ops(self):
        """Test convert_to_default_value_ops method (partial implementation)."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # This should not raise an error (even though it's not fully implemented)
        try:
            alg.convert_to_default_value_ops()
        except Exception as e:
            self.fail(f"convert_to_default_value_ops() raised an exception: {e}")
    
    def test_is_unary(self):
        """Test is_unary method."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # With no operations, it should be unary
        self.assertTrue(alg.is_unary())
    
    def test_is_idempotent(self):
        """Test is_idempotent method."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # With no operations, it should be idempotent
        self.assertTrue(alg.is_idempotent())
    
    def test_is_total(self):
        """Test is_total method."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # With no operations, it should be total
        self.assertTrue(alg.is_total())
    
    def test_monitoring(self):
        """Test monitoring method."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # Initially monitoring should be false
        self.assertFalse(alg.monitoring())
    
    def test_input_size(self):
        """Test input_size method."""

        alg = BasicAlgebra("test", [0, 1, 2, 3, 4] ,[])
        
        # Input size should match cardinality for algebras with no operations
        input_size = alg.input_size()
        self.assertGreaterEqual(input_size, 0)
    
    def test_str_representation(self):
        """Test string representation."""

        alg = BasicAlgebra("test", [0, 1, 2] ,[])
        
        str_repr = str(alg)
        self.assertIsInstance(str_repr, str)
        self.assertGreater(len(str_repr), 0)
    
    def test_repr_representation(self):
        """Test repr representation."""

        alg = BasicAlgebra("test", [0, 1, 2] ,[])
        
        repr_str = repr(alg)
        self.assertIsInstance(repr_str, str)
        self.assertIn("BasicAlgebra", repr_str)
    
    def test_equality(self):
        """Test equality comparison."""

        alg1 = BasicAlgebra("test", [0, 1, 2] ,[])
        alg2 = BasicAlgebra("test", [0, 1, 2] ,[])
        alg3 = BasicAlgebra("different", [0, 1, 2] ,[])
        
        # Same name and cardinality should be equal
        self.assertEqual(alg1, alg2)
        
        # Different name should not be equal
        self.assertNotEqual(alg1, alg3)

    def test_operations(self):
        """Test operations."""

        op = IntOperation.from_int_value_at("add", 2, 3, lambda args: max(args[0], args[1]))
        alg = BasicAlgebra("test", [0, 1, 2] ,[op])
        print(alg.operations())
        alg_op = alg.operations()[0]
        self.assertEqual(alg_op.symbol().name(), "add")
        self.assertEqual(alg_op.arity(), 2)
        self.assertEqual(alg_op.get_set_size(), 3)
        self.assertEqual(alg_op.int_value_at([0, 1]), 1)
        self.assertEqual(alg_op.int_value_at([1, 2]), 2)
        self.assertEqual(alg_op.int_value_at([2, 2]), 2)

    def test_con(self):
        """Test con method."""
        # Four element diamond semilattice
        def meet_int_value_at(args):
            if 0 in args:
                return 0
            elif set(args) == {0, 1}:
                return 0
            elif 1 in args:
                return 1
            else:
                return 2
        op = IntOperation.from_int_value_at("meet", 2, 4, meet_int_value_at)
        alg = BasicAlgebra("test", list(range(4)) ,[op])
        con = alg.con()
        self.assertEqual(con.alg_size(), 4)
        self.assertGreaterEqual(con.con_cardinality(), 2)
    
    def test_sub(self):
        """Test sub method."""
        SubalgebraLattice = uacalc_lib.alg.SubalgebraLattice
        
        # Create a simple algebra with a binary operation
        def join_int_value_at(args):
            return max(args[0], args[1])
        op = IntOperation.from_int_value_at("join", 2, 3, join_int_value_at)
        alg = BasicAlgebra("test", list(range(3)), [op])
        
        # Test sub() method
        sub_lat = alg.sub()
        
        # Verify it returns a SubalgebraLattice
        self.assertIsInstance(sub_lat, SubalgebraLattice)
        
        # Verify basic properties - should have at least 2 subalgebras (zero and one)
        self.assertGreaterEqual(sub_lat.cardinality(), 2)
        
        # Test that we can call sub() multiple times
        sub_lat2 = alg.sub()
        self.assertIsInstance(sub_lat2, SubalgebraLattice)
        self.assertEqual(sub_lat2.cardinality(), sub_lat.cardinality())
    
    def test_from_general_algebra_with_integer_universe(self):
        """Test creating BasicAlgebra from GeneralAlgebra with integer universe."""
        GeneralAlgebra = uacalc_lib.alg.GeneralAlgebra
        
        universe = [0, 1, 2, 3]
        general_alg = GeneralAlgebra("TestInt", universe)
        
        # Convert to BasicAlgebra
        basic_alg = BasicAlgebra.from_general_algebra(general_alg)
        
        # Verify properties
        self.assertEqual(basic_alg.name(), "TestInt")
        self.assertEqual(basic_alg.cardinality(), 4)
        self.assertEqual(basic_alg.algebra_type(), "Basic")
        
        # Check universe
        basic_universe = basic_alg.get_universe()
        self.assertEqual(len(basic_universe), 4)
        self.assertEqual(set(basic_universe), {0, 1, 2, 3})
    
    def test_from_general_algebra_with_string_universe(self):
        """Test creating BasicAlgebra from GeneralAlgebra with string universe."""
        GeneralAlgebra = uacalc_lib.alg.GeneralAlgebra
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        universe = ["red", "green", "blue"]
        general_alg = GeneralAlgebra("TestString", universe)
        
        # Convert to BasicAlgebra
        basic_alg = BasicAlgebra.from_general_algebra(general_alg)
        
        # Verify properties
        self.assertEqual(basic_alg.name(), "TestString")
        self.assertEqual(basic_alg.cardinality(), 3)
        self.assertEqual(basic_alg.algebra_type(), "Basic")
        
        # Check universe - should be integers (indices)
        basic_universe = basic_alg.get_universe()
        self.assertEqual(len(basic_universe), 3)
        self.assertEqual(set(basic_universe), {0, 1, 2})
    
    def test_from_general_algebra_with_operations(self):
        """Test creating BasicAlgebra from GeneralAlgebra with operations."""
        GeneralAlgebra = uacalc_lib.alg.GeneralAlgebra
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        universe = [0, 1, 2]
        
        # Create a binary operation: (a + b) mod 3
        def add_mod3(args):
            return (args[0] + args[1]) % 3
        
        op = AbstractOperation.from_int_value_at_function("add_mod3", 2, 3, add_mod3)
        general_alg = GeneralAlgebra("TestWithOps", universe, [op])
        
        # Convert to BasicAlgebra
        basic_alg = BasicAlgebra.from_general_algebra(general_alg)
        
        # Verify properties
        self.assertEqual(basic_alg.name(), "TestWithOps")
        self.assertEqual(basic_alg.cardinality(), 3)
        self.assertEqual(basic_alg.operations_count(), 1)
        
        # Check operations
        basic_ops = basic_alg.operations()
        self.assertEqual(len(basic_ops), 1)
        self.assertEqual(basic_ops[0].arity(), 2)
        
        # Verify operation works correctly
        self.assertEqual(basic_ops[0].int_value_at([0, 1]), 1)
        self.assertEqual(basic_ops[0].int_value_at([1, 2]), 0)
        self.assertEqual(basic_ops[0].int_value_at([2, 2]), 1)
    
    def test_from_general_algebra_preserves_name(self):
        """Test that from_general_algebra preserves the algebra name."""
        GeneralAlgebra = uacalc_lib.alg.GeneralAlgebra
        
        general_alg = GeneralAlgebra("MyAlgebra", [0, 1, 2])
        basic_alg = BasicAlgebra.from_general_algebra(general_alg)
        
        self.assertEqual(basic_alg.name(), "MyAlgebra")
        self.assertEqual(general_alg.name(), "MyAlgebra")  # Original unchanged


if __name__ == '__main__':
    unittest.main()

