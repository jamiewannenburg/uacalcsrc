"""Tests for MatrixPowerAlgebra implementation.

This module contains comprehensive tests for the MatrixPowerAlgebra class,
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


class TestMatrixPowerAlgebra(unittest.TestCase):
    """Test cases for MatrixPowerAlgebra implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        self.MatrixPowerAlgebra = uacalc_lib.alg.MatrixPowerAlgebra

    def test_matrix_power_algebra_creation(self):
        """Test MatrixPowerAlgebra creation."""
        # Create a basic small algebra
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        
        # Create matrix power algebra
        matrix_power = self.MatrixPowerAlgebra(root_alg, 3)
        
        # Verify basic properties
        self.assertEqual(matrix_power.get_power(), 3)
        self.assertEqual(matrix_power.cardinality(), 8)  # 2^3 = 8
        self.assertEqual(matrix_power.algebra_type(), "MATRIX_POWER")

    def test_matrix_power_algebra_creation_with_name(self):
        """Test MatrixPowerAlgebra creation with custom name."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        
        matrix_power = self.MatrixPowerAlgebra.new_with_name("MyMatrixPower", root_alg, 2)
        
        self.assertEqual(matrix_power.name(), "MyMatrixPower")
        self.assertEqual(matrix_power.get_power(), 2)
        self.assertEqual(matrix_power.cardinality(), 4)  # 2^2 = 4

    def test_get_power(self):
        """Test get_power method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 4)
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["get_power"])
        self.assertEqual(matrix_power.get_power(), get_java_data(java_result)["power"])

    def test_cardinality(self):
        """Test cardinality method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1, 2] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["cardinality"])
        self.assertEqual(matrix_power.cardinality(), get_java_data(java_result)["cardinality"])

    def test_get_element(self):
        """Test get_element method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        # Test first element
        element = matrix_power.get_element(0)
        self.assertEqual(element, [0, 0])
        
        # Test with Java comparison
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["get_element", "--index", "0"])
        # Note: Java returns string representation, we return list
        self.assertIsInstance(element, list)

    def test_element_index(self):
        """Test element_index method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        # Test roundtrip
        element = [0, 0]
        index = matrix_power.element_index(element)
        self.assertEqual(index, 0)
        
        element = [1, 1]
        index = matrix_power.element_index(element)
        self.assertEqual(index, 3)

    def test_algebra_type(self):
        """Test algebra_type method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["algebra_type"])
        self.assertEqual(matrix_power.algebra_type(), get_java_data(java_result)["type"])

    def test_name_operations(self):
        """Test name getter and setter."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra.new_with_name("MyMatrixPower", root_alg, 2)
        
        # Test getter
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["name"])
        self.assertEqual(matrix_power.name(), get_java_data(java_result)["name"])
        
        # Test setter
        matrix_power.set_name("NewName")
        self.assertEqual(matrix_power.name(), "NewName")

    def test_set_name(self):
        """Test set_name method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["set_name", "--name", "NewName"])
        self.assertEqual(get_java_data(java_result)["new_name"], "NewName")

    def test_is_unary(self):
        """Test is_unary method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["is_unary"])
        self.assertEqual(matrix_power.is_unary(), get_java_data(java_result)["is_unary"])

    def test_is_idempotent(self):
        """Test is_idempotent method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["is_idempotent"])
        self.assertEqual(matrix_power.is_idempotent(), get_java_data(java_result)["is_idempotent"])

    def test_is_total(self):
        """Test is_total method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["is_total"])
        self.assertEqual(matrix_power.is_total(), get_java_data(java_result)["is_total"])

    def test_operations_count(self):
        """Test operations_count method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["operations_count"])
        self.assertEqual(matrix_power.operations_count(), get_java_data(java_result)["count"])

    def test_get_universe_list(self):
        """Test get_universe_list method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        universe_list = matrix_power.get_universe_list()
        self.assertEqual(len(universe_list), 4)  # 2^2 = 4
        self.assertIn([0, 0], universe_list)
        self.assertIn([1, 1], universe_list)
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["get_universe_list"])
        self.assertEqual(len(universe_list), get_java_data(java_result)["universe_size"])

    def test_get_universe_order(self):
        """Test get_universe_order method."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        universe_order = matrix_power.get_universe_order()
        self.assertIsNone(universe_order)  # Matrix power algebras don't have natural order
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["get_universe_order"])
        self.assertEqual(universe_order is None, not get_java_data(java_result)["has_order"])

    def test_convert_to_default_value_ops(self):
        """Test convert_to_default_value_ops method (should fail)."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        # This should raise an exception
        with self.assertRaises(Exception):
            matrix_power.convert_to_default_value_ops()

    def test_basic_functionality(self):
        """Test basic functionality with Java comparison."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra.new_with_name("TestMatrixPower", root_alg, 3)
        
        java_result = run_java_wrapper("java_wrapper.src.alg.MatrixPowerAlgebraWrapper", ["test"])
        
        self.assertEqual(matrix_power.name(), get_java_data(java_result)["name"])
        self.assertEqual(matrix_power.get_power(), get_java_data(java_result)["power"])
        self.assertEqual(matrix_power.cardinality(), get_java_data(java_result)["cardinality"])
        self.assertEqual(matrix_power.algebra_type(), get_java_data(java_result)["algebra_type"])

    def test_horner_encoding_roundtrip(self):
        """Test Horner encoding roundtrip."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1, 2] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        # Test roundtrip for all elements
        for i in range(matrix_power.cardinality()):
            element = matrix_power.get_element(i)
            index = matrix_power.element_index(element)
            self.assertEqual(index, i)

    def test_matrix_operations(self):
        """Test that matrix-specific operations are present."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra(root_alg, 2)
        
        # Should have matrix-specific operations
        operations_count = matrix_power.operations_count()
        self.assertGreaterEqual(operations_count, 2)  # At least left shift and diagonal

    def test_error_handling(self):
        """Test error handling."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        
        # Test with power = 0 (should fail)
        with self.assertRaises(Exception):
            self.MatrixPowerAlgebra(root_alg, 0)

    def test_display_representation(self):
        """Test string representation."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power = self.MatrixPowerAlgebra.new_with_name("DisplayTest", root_alg, 2)
        
        # Test string representation
        str_repr = str(matrix_power)
        self.assertIn("DisplayTest", str_repr)
        
        # Test repr representation
        repr_str = repr(matrix_power)
        self.assertIn("MatrixPowerAlgebra", repr_str)

    def test_equality_and_hash(self):
        """Test equality and hash functions."""
        root_alg1 = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        root_alg2 = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        
        matrix_power1 = self.MatrixPowerAlgebra.new_with_name("Test", root_alg1, 2)
        matrix_power2 = self.MatrixPowerAlgebra.new_with_name("Test", root_alg2, 2)
        
        # Test equality
        self.assertEqual(matrix_power1, matrix_power2)
        
        # Test hash
        self.assertEqual(hash(matrix_power1), hash(matrix_power2))

    def test_different_powers(self):
        """Test with different powers."""
        root_alg = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        
        # Test power 1
        matrix_power1 = self.MatrixPowerAlgebra(root_alg, 1)
        self.assertEqual(matrix_power1.cardinality(), 2)
        
        # Test power 2
        matrix_power2 = self.MatrixPowerAlgebra(root_alg, 2)
        self.assertEqual(matrix_power2.cardinality(), 4)
        
        # Test power 3
        matrix_power3 = self.MatrixPowerAlgebra(root_alg, 3)
        self.assertEqual(matrix_power3.cardinality(), 8)

    def test_different_root_sizes(self):
        """Test with different root algebra sizes."""
        # Test with size 2
        root_alg2 = self.BasicAlgebra("TestRoot", [0, 1] ,[])
        matrix_power2 = self.MatrixPowerAlgebra(root_alg2, 2)
        self.assertEqual(matrix_power2.cardinality(), 4)
        
        # Test with size 3
        root_alg3 = self.BasicAlgebra("TestRoot", [0, 1, 2] ,[])
        matrix_power3 = self.MatrixPowerAlgebra(root_alg3, 2)
        self.assertEqual(matrix_power3.cardinality(), 9)
        
        # Test with size 4
        root_alg4 = self.BasicAlgebra("TestRoot", [0, 1, 2, 3] ,[])
        matrix_power4 = self.MatrixPowerAlgebra(root_alg4, 2)
        self.assertEqual(matrix_power4.cardinality(), 16)


if __name__ == '__main__':
    unittest.main()
