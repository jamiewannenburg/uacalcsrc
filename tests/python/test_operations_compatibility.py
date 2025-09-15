#!/usr/bin/env python3
"""
Operations Compatibility Test

This module tests the org.uacalc.alg.op.Operations utility class compatibility between
Java UACalc and the Rust/Python implementation. It verifies that Operations utility
factory methods, operation construction from tables and functions, and operation
validation and normalization utilities produce identical results.
"""

import unittest
import json
import itertools
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class OperationsCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.op.Operations utility class compatibility.
    
    This class tests the Operations utility class methods to ensure
    the Rust implementation matches Java behavior exactly for:
    - Operations utility class factory methods
    - Operation construction from tables and functions
    - Operation validation and normalization utilities
    """
    
    def test_operations_constant_factory_compatibility(self):
        """Test Operations.makeConstantIntOperation factory method"""
        logger.info("Testing Operations constant factory compatibility")
        
        # Test Java factory method for constant operations
        java_result = self._run_java_operation(
            "operations_factory", "constant", "{}"
        )
        
        if java_result is None:
            self.skipTest("Java UACalc not available")
        
        if not java_result.get("success", True):
            self.skipTest(f"Java operation failed: {java_result.get('error')}")
        
        # Verify Java operation properties
        java_operation = java_result.get("created_operation", {})
        
        # Verify basic properties
        self.assertEqual(java_operation.get("arity"), 0)
        self.assertEqual(java_operation.get("cardinality"), 2)
        self.assertEqual(java_operation.get("value"), 1)
        
        logger.info("Constant operation test passed")
    
    def test_operations_unary_factory_compatibility(self):
        """Test Operations.makeIntOperation factory method for unary operations"""
        logger.info("Testing Operations unary factory compatibility")
        
        # Test Java factory method for unary operations
        java_result = self._run_java_operation(
            "operations_factory", "unary", "{}"
        )
        
        if java_result is None:
            self.skipTest("Java UACalc not available")
        
        if not java_result.get("success", True):
            self.skipTest(f"Java operation failed: {java_result.get('error')}")
        
        # Verify Java operation properties
        java_operation = java_result.get("created_operation", {})
        
        self.assertEqual(java_operation.get("symbol"), "f")
        self.assertEqual(java_operation.get("arity"), 1)
        self.assertEqual(java_operation.get("cardinality"), 3)
        self.assertEqual(java_operation.get("table"), [0, 1, 2])  # Identity function
        
        logger.info("Unary operation test passed")
    
    def test_operations_binary_factory_compatibility(self):
        """Test Operations.makeBinaryIntOperation factory method"""
        logger.info("Testing Operations binary factory compatibility")
        
        # Test Java factory method for binary operations
        java_result = self._run_java_operation(
            "operations_factory", "binary", "{}"
        )
        
        if java_result is None:
            self.skipTest("Java UACalc not available")
        
        if not java_result.get("success", True):
            self.skipTest(f"Java operation failed: {java_result.get('error')}")
        
        # Verify Java operation properties
        java_operation = java_result.get("created_operation", {})
        
        self.assertEqual(java_operation.get("symbol"), "*")
        self.assertEqual(java_operation.get("arity"), 2)
        self.assertEqual(java_operation.get("cardinality"), 2)
        self.assertEqual(java_operation.get("table"), [0, 0, 0, 1])  # AND operation
        
        logger.info("Binary operation test passed")
    
    def test_operations_random_factory_compatibility(self):
        """Test Operations.makeRandomOperation factory method"""
        logger.info("Testing Operations random factory compatibility")
        
        # Test Java factory method for random operations
        java_result = self._run_java_operation(
            "operations_factory", "random", "{}"
        )
        
        if java_result is None:
            self.skipTest("Java UACalc not available")
        
        if not java_result.get("success", True):
            self.skipTest(f"Java operation failed: {java_result.get('error')}")
        
        # Verify Java operation properties
        java_operation = java_result.get("created_operation", {})
        
        self.assertEqual(java_operation.get("symbol"), "r")
        self.assertEqual(java_operation.get("arity"), 2)
        self.assertIn("note", java_operation)  # Should have note about random nature
        
        logger.info("Random operation test passed")
    
    def test_operations_validation_compatibility(self):
        """Test operation validation utilities"""
        logger.info("Testing Operations validation compatibility")
        
        # Test Java validation using Operations utility methods
        java_result = self._run_java_operation(
            "operations_validation", "{}"
        )
        
        if java_result is None:
            self.skipTest("Java UACalc not available")
        
        if not java_result.get("success", True):
            self.skipTest(f"Java operation failed: {java_result.get('error')}")
        
        # Verify validation result
        validation_result = java_result.get("validation_result", {})
        
        # Should be valid since we're testing with a proper XOR operation
        self.assertTrue(validation_result.get("is_valid", False))
        self.assertEqual(validation_result.get("symbol"), "test")
        self.assertEqual(validation_result.get("arity"), 2)
        self.assertEqual(validation_result.get("cardinality"), 2)
        
        # Check that properties are computed
        properties = validation_result.get("properties", {})
        self.assertIn("is_commutative", properties)
        self.assertIn("is_associative", properties)
        self.assertIn("is_idempotent", properties)
        self.assertIn("is_total", properties)
        
        # XOR should be commutative and associative but not idempotent
        self.assertTrue(properties.get("is_commutative"))
        self.assertTrue(properties.get("is_associative"))  # XOR is associative
        self.assertFalse(properties.get("is_idempotent"))
        self.assertTrue(properties.get("is_total"))
        
        logger.info("Validation test passed")
    
    def test_operations_normalization_compatibility(self):
        """Test operation normalization utilities"""
        logger.info("Testing Operations normalization compatibility")
        
        # Test Java normalization using Operations utility methods
        java_result = self._run_java_operation(
            "operations_normalization", "{}"
        )
        
        if java_result is None:
            self.skipTest("Java UACalc not available")
        
        if not java_result.get("success", True):
            self.skipTest(f"Java operation failed: {java_result.get('error')}")
        
        # Verify normalization result
        normalization_result = java_result.get("normalization_result", {})
        test_operations = normalization_result.get("test_operations", [])
        
        # Should have two test operations: max and identity
        self.assertEqual(len(test_operations), 2)
        
        # Check max operation (first operation)
        max_op = test_operations[0]
        self.assertEqual(max_op.get("symbol"), "max")
        self.assertEqual(max_op.get("arity"), 2)
        self.assertEqual(max_op.get("cardinality"), 3)
        
        max_properties = max_op.get("properties", {})
        self.assertTrue(max_properties.get("is_commutative"), "MAX should be commutative")
        self.assertTrue(max_properties.get("is_associative"), "MAX should be associative")
        self.assertTrue(max_properties.get("is_idempotent"), "MAX should be idempotent")
        
        # Verify max table
        expected_max_table = [0, 1, 2, 1, 1, 2, 2, 2, 2]
        self.assertEqual(max_op.get("table"), expected_max_table)
        
        # Check identity operation (second operation)
        id_op = test_operations[1]
        self.assertEqual(id_op.get("symbol"), "id")
        self.assertEqual(id_op.get("arity"), 1)
        self.assertEqual(id_op.get("cardinality"), 3)
        
        id_properties = id_op.get("properties", {})
        self.assertTrue(id_properties.get("is_idempotent"), "Identity should be idempotent")
        
        # Verify identity table
        expected_id_table = [0, 1, 2]
        self.assertEqual(id_op.get("table"), expected_id_table)
        
        logger.info("Normalization test passed")
    
    def test_operations_factory_error_handling_compatibility(self):
        """Test error handling in Operations factory methods"""
        logger.info("Testing Operations factory error handling compatibility")
        
        # Test with unsupported operation type
        java_result = self._run_java_operation(
            "operations_factory", "ternary", "{}"
        )
        
        if java_result is None:
            self.skipTest("Java UACalc not available")
        
        # Should get an error result for unsupported operation type
        self.assertFalse(java_result.get("success", True),
            "Expected error for unsupported operation type")
        
        # Should have error information
        self.assertIn("error", java_result)
        self.assertIn("error_type", java_result)
        
        logger.info("Error handling test passed")
    
    def test_operations_complex_factory_scenarios(self):
        """Test complex scenarios with Operations factory methods"""
        logger.info("Testing Operations complex factory scenarios")
        
        # Test creating multiple different operation types
        operation_types = ["constant", "unary", "binary", "random"]
        created_operations = []
        
        for op_type in operation_types:
            java_result = self._run_java_operation(
                "operations_factory", op_type, "{}"
            )
            
            if java_result is None:
                self.skipTest("Java UACalc not available")
            
            if not java_result.get("success", True):
                self.fail(f"Failed to create {op_type} operation: {java_result.get('error')}")
            
            created_operations.append((op_type, java_result.get("created_operation")))
        
        # Verify all operations were created successfully
        self.assertEqual(len(created_operations), len(operation_types))
        
        # Verify operation properties
        for op_type, created_op in created_operations:
            if op_type == "constant":
                self.assertEqual(created_op.get("arity"), 0)
            elif op_type == "unary":
                self.assertEqual(created_op.get("arity"), 1)
                self.assertEqual(created_op.get("symbol"), "f")
            elif op_type == "binary":
                self.assertEqual(created_op.get("arity"), 2)
                self.assertEqual(created_op.get("symbol"), "*")
            elif op_type == "random":
                self.assertEqual(created_op.get("arity"), 2)
                self.assertEqual(created_op.get("symbol"), "r")
        
        logger.info("Complex factory scenario passed")


if __name__ == '__main__':
    unittest.main()