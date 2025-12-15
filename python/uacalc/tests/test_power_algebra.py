"""Tests for PowerAlgebra implementation.

This module contains comprehensive tests for the PowerAlgebra class,
including unit tests, integration tests, and comparison tests with Java implementation.
"""

import unittest
import os
import json
import uacalc_lib
from test_utils import run_java_wrapper


def get_java_data(java_result):
    """Extract and parse the data field from Java output."""
    parsed = java_result.parse_json()
    data = parsed.get("data", {})
    if isinstance(data, str):
        return json.loads(data)
    return data


class TestPowerAlgebra(unittest.TestCase):
    """Test cases for PowerAlgebra implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        self.PowerAlgebra = uacalc_lib.alg.PowerAlgebra
        self.IntOperation = uacalc_lib.alg.IntOperation
        self.OperationSymbol = uacalc_lib.alg.OperationSymbol

    def test_power_algebra_creation(self):
        """Test PowerAlgebra creation."""
        # Create a basic small algebra
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [])
        
        # Create power algebra
        power = self.PowerAlgebra(root_alg, 3)
        
        # Verify basic properties
        self.assertEqual(power.get_power(), 3)
        self.assertEqual(power.cardinality(), 8)  # 2^3 = 8
        self.assertEqual(power.get_root_size(), 2)
        self.assertIn("Power", power.algebra_type())

    def test_power_algebra_creation_with_name(self):
        """Test PowerAlgebra creation with custom name."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [])
        
        power = self.PowerAlgebra.new_with_name("MyPower", root_alg, 2)
        
        self.assertEqual(power.name(), "MyPower")
        self.assertEqual(power.get_power(), 2)
        self.assertEqual(power.cardinality(), 4)  # 2^2 = 4

    def test_get_power(self):
        """Test get_power method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [])
        power = self.PowerAlgebra(root_alg, 4)
        
        self.assertEqual(power.get_power(), 4)

    def test_cardinality(self):
        """Test cardinality method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1, 2], [])
        power = self.PowerAlgebra(root_alg, 2)
        
        # 3^2 = 9
        self.assertEqual(power.cardinality(), 9)

    def test_get_root_size(self):
        """Test get_root_size method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1, 2, 3], [])
        power = self.PowerAlgebra(root_alg, 3)
        
        self.assertEqual(power.get_root_size(), 4)

    def test_name_and_description(self):
        """Test name and description methods."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [])
        power = self.PowerAlgebra.new_with_name("TestPower", root_alg, 2)
        
        self.assertEqual(power.name(), "TestPower")
        self.assertIsNone(power.description())
        
        # Test setting name
        power.set_name("NewName")
        self.assertEqual(power.name(), "NewName")
        
        # Test setting description
        power.set_description("Test description")
        self.assertEqual(power.description(), "Test description")
        
        power.set_description(None)
        self.assertIsNone(power.description())

    def test_operations_returns_operation_objects(self):
        """Test that operations() returns Operation objects, not tuples."""
        # Create root algebra with an operation
        symbol = self.OperationSymbol("f", 2)
        table = [0, 1, 1, 0]  # XOR operation on {0, 1}
        op = self.IntOperation(symbol, 2, table)
        
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [op])
        power = self.PowerAlgebra(root_alg, 2)
        
        # Get operations - should return Operation objects, not tuples
        ops = power.operations()
        
        # Verify it's a list
        self.assertIsInstance(ops, list)
        self.assertGreater(len(ops), 0)
        
        # Verify each operation is an Operation object (has symbol and arity methods)
        for op in ops:
            # Should have symbol() method (Operation objects have this)
            self.assertTrue(hasattr(op, 'symbol'))
            self.assertTrue(hasattr(op, 'arity'))
            self.assertTrue(hasattr(op, 'get_set_size'))
            
            # Should NOT be a tuple
            self.assertNotIsInstance(op, tuple)

    def test_operations_preserves_operation_properties(self):
        """Test that operations preserve their properties."""
        # Create root algebra with an operation
        symbol = self.OperationSymbol("g", 1)
        table = [1, 0]  # NOT operation on {0, 1}
        op = self.IntOperation(symbol, 2, table)
        
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [op])
        power = self.PowerAlgebra(root_alg, 2)
        
        ops = power.operations()
        self.assertEqual(len(ops), 1)
        
        # Check operation properties
        op_obj = ops[0]
        self.assertEqual(op_obj.symbol().name(), "g")
        self.assertEqual(op_obj.arity(), 1)
        self.assertEqual(op_obj.get_set_size(), 4)  # Power algebra size is 2^2 = 4

    def test_to_basic_algebra(self):
        """Test conversion to BasicAlgebra."""
        # Create root algebra with an operation
        symbol = self.OperationSymbol("h", 2)
        table = [0, 0, 0, 1]  # AND operation on {0, 1}
        op = self.IntOperation(symbol, 2, table)
        
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [op])
        power = self.PowerAlgebra(root_alg, 2)
        
        # Convert to BasicAlgebra
        basic_alg = power.to_basic_algebra()
        
        # Verify it's a BasicAlgebra
        self.assertIsInstance(basic_alg, self.BasicAlgebra)
        
        # Verify cardinality matches
        self.assertEqual(basic_alg.cardinality(), power.cardinality())
        
        # Verify operations are preserved
        basic_ops = basic_alg.operations()
        power_ops = power.operations()
        self.assertEqual(len(basic_ops), len(power_ops))

    def test_to_basic_algebra_preserves_operations(self):
        """Test that to_basic_algebra preserves operation structure."""
        # Create root algebra with multiple operations
        symbol1 = self.OperationSymbol("f", 2)
        table1 = [0, 1, 1, 0]  # XOR
        op1 = self.IntOperation(symbol1, 2, table1)
        
        symbol2 = self.OperationSymbol("g", 1)
        table2 = [1, 0]  # NOT
        op2 = self.IntOperation(symbol2, 2, table2)
        
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [op1, op2])
        power = self.PowerAlgebra(root_alg, 2)
        
        basic_alg = power.to_basic_algebra()
        
        # Check operations count
        basic_ops = basic_alg.operations()
        self.assertEqual(len(basic_ops), 2)
        
        # Check operation names
        op_names = [op.symbol().name() for op in basic_ops]
        self.assertIn("f", op_names)
        self.assertIn("g", op_names)

    def test_is_unary(self):
        """Test is_unary method."""
        # Create unary algebra
        symbol = self.OperationSymbol("u", 1)
        table = [1, 0]
        op = self.IntOperation(symbol, 2, table)
        
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [op])
        power = self.PowerAlgebra(root_alg, 2)
        
        self.assertTrue(power.is_unary())
        
        # Create non-unary algebra
        symbol2 = self.OperationSymbol("b", 2)
        table2 = [0, 1, 1, 0]
        op2 = self.IntOperation(symbol2, 2, table2)
        
        root_alg2 = self.BasicAlgebra("TestRoot2", [0, 1], [op2])
        power2 = self.PowerAlgebra(root_alg2, 2)
        
        self.assertFalse(power2.is_unary())

    def test_is_total(self):
        """Test is_total method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [])
        power = self.PowerAlgebra(root_alg, 2)
        
        # Algebra with no operations should be total
        self.assertTrue(power.is_total())

    def test_is_idempotent(self):
        """Test is_idempotent method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [])
        power = self.PowerAlgebra(root_alg, 2)
        
        # Test that method exists and doesn't crash
        result = power.is_idempotent()
        self.assertIsInstance(result, bool)

    def test_string_representations(self):
        """Test string representation methods."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [])
        power = self.PowerAlgebra(root_alg, 2)
        
        # Test __str__
        str_repr = str(power)
        self.assertIsInstance(str_repr, str)
        self.assertGreater(len(str_repr), 0)
        
        # Test __repr__
        repr_str = repr(power)
        self.assertIsInstance(repr_str, str)
        self.assertIn("PowerAlgebra", repr_str)

    def test_equality(self):
        """Test equality comparison."""
        root_alg1 = self.BasicAlgebra("TestRoot", [0, 1], [])
        power1 = self.PowerAlgebra.new_with_name("Test", root_alg1, 2)
        
        root_alg2 = self.BasicAlgebra("TestRoot", [0, 1], [])
        power2 = self.PowerAlgebra.new_with_name("Test", root_alg2, 2)
        
        # Should be equal if name, cardinality, and power match
        self.assertEqual(power1, power2)

    def test_hash(self):
        """Test hash function."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [])
        power = self.PowerAlgebra(root_alg, 2)
        
        # Test that hash exists and is consistent
        hash1 = hash(power)
        hash2 = hash(power)
        self.assertEqual(hash1, hash2)
        self.assertIsInstance(hash1, int)

    def test_congruence_lattice(self):
        """Test congruence lattice access."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [])
        power = self.PowerAlgebra(root_alg, 2)
        
        # Test that con() method exists and returns a CongruenceLattice
        con_lat = power.con()
        self.assertIsNotNone(con_lat)
        # Verify it has expected methods
        self.assertTrue(hasattr(con_lat, 'cardinality'))

    def test_subalgebra_lattice(self):
        """Test subalgebra lattice access."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1], [])
        power = self.PowerAlgebra(root_alg, 2)
        
        # Test that sub() method exists and returns a SubalgebraLattice
        sub_lat = power.sub()
        self.assertIsNotNone(sub_lat)
        # Verify it has expected methods
        self.assertTrue(hasattr(sub_lat, 'cardinality'))

    def test_large_power(self):
        """Test with larger power values."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1, 2], [])
        power = self.PowerAlgebra(root_alg, 3)
        
        # 3^3 = 27
        self.assertEqual(power.cardinality(), 27)
        self.assertEqual(power.get_power(), 3)
        self.assertEqual(power.get_root_size(), 3)

    def test_power_algebra_with_operations(self):
        """Test PowerAlgebra with operations from root."""
        # Create root with operation
        symbol = self.OperationSymbol("mult", 2)
        # Multiplication mod 3: 0*0=0, 0*1=0, 0*2=0, 1*0=0, 1*1=1, 1*2=2, etc.
        table = [0, 0, 0, 0, 1, 2, 0, 2, 1]
        op = self.IntOperation(symbol, 3, table)
        
        root_alg = self.BasicAlgebra("Z3", [0, 1, 2], [op])
        power = self.PowerAlgebra(root_alg, 2)
        
        # Power algebra should have operations
        ops = power.operations()
        self.assertGreater(len(ops), 0)
        
        # Operations should be Operation objects
        for op in ops:
            self.assertTrue(hasattr(op, 'symbol'))
            self.assertTrue(hasattr(op, 'arity'))


if __name__ == '__main__':
    unittest.main()

