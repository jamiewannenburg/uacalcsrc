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
        
        # Create equivalent Rust/Python operation
        try:
            import uacalc
            rust_operation = uacalc.Operations.make_constant_int_operation(2, 1)
            
            # Compare properties
            self.assertEqual(rust_operation.arity(), java_operation.get("arity"))
            self.assertEqual(rust_operation.value([]), java_operation.get("value"))
            
            logger.info("Constant operation test passed")
        except ImportError:
            self.skipTest("UACalc Rust extension not available")
    
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
        
        # Create equivalent Rust/Python operation
        try:
            import uacalc
            symbol = uacalc.OperationSymbol("f", 1)
            rust_operation = uacalc.Operations.make_int_operation(symbol, 3, [0, 1, 2])
            
            # Compare properties
            self.assertEqual(rust_operation.symbol, java_operation.get("symbol"))
            self.assertEqual(rust_operation.arity(), java_operation.get("arity"))
            
            # Test operation values
            for i in range(3):
                self.assertEqual(rust_operation.value([i]), java_operation.get("table")[i])
            
            logger.info("Unary operation test passed")
        except ImportError:
            self.skipTest("UACalc Rust extension not available")
    
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
        
        # Create equivalent Rust/Python operation
        try:
            import uacalc
            symbol = uacalc.OperationSymbol("*", 2)
            # AND operation table: [[0, 0], [0, 1]]
            table = [[0, 0], [0, 1]]
            rust_operation = uacalc.Operations.make_binary_int_operation(symbol, 2, table)
            
            # Compare properties
            self.assertEqual(rust_operation.symbol, java_operation.get("symbol"))
            self.assertEqual(rust_operation.arity(), java_operation.get("arity"))
            
            # Test operation values
            java_table = java_operation.get("table", [])
            for i in range(2):
                for j in range(2):
                    expected = java_table[i * 2 + j]
                    actual = rust_operation.value([i, j])
                    self.assertEqual(actual, expected)
            
            logger.info("Binary operation test passed")
        except ImportError:
            self.skipTest("UACalc Rust extension not available")
    
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
        
        # Create equivalent Rust/Python operation
        try:
            import uacalc
            symbol = uacalc.OperationSymbol("r", 2)
            # Use a fixed seed for reproducible results
            rust_operation = uacalc.Operations.make_random_operation_with_seed(3, symbol, 42)
            
            # Compare properties
            self.assertEqual(rust_operation.symbol, java_operation.get("symbol"))
            self.assertEqual(rust_operation.arity(), java_operation.get("arity"))
            
            # Test that the operation is valid (returns values in range)
            for i in range(3):
                for j in range(3):
                    result = rust_operation.value([i, j])
                    self.assertGreaterEqual(result, 0)
                    self.assertLess(result, 3)
            
            logger.info("Random operation test passed")
        except ImportError:
            self.skipTest("UACalc Rust extension not available")
    
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
        
        # Create equivalent Rust/Python operation for validation
        try:
            import uacalc
            symbol = uacalc.OperationSymbol("test", 2)
            # XOR operation table: [[0, 1], [1, 0]]
            table = [[0, 1], [1, 0]]
            rust_operation = uacalc.Operations.make_binary_int_operation(symbol, 2, table)
            
            # Test validation properties
            self.assertTrue(uacalc.Operations.is_commutative(rust_operation))
            self.assertTrue(uacalc.Operations.is_associative(rust_operation))  # XOR is associative
            self.assertFalse(uacalc.Operations.is_idempotent(rust_operation))
            self.assertTrue(uacalc.Operations.is_total(rust_operation))
            
            # Compare with Java results
            properties = validation_result.get("properties", {})
            self.assertEqual(uacalc.Operations.is_commutative(rust_operation), properties.get("is_commutative"))
            self.assertEqual(uacalc.Operations.is_associative(rust_operation), properties.get("is_associative"))
            self.assertEqual(uacalc.Operations.is_idempotent(rust_operation), properties.get("is_idempotent"))
            self.assertEqual(uacalc.Operations.is_total(rust_operation), properties.get("is_total"))
            
            logger.info("Validation test passed")
        except ImportError:
            self.skipTest("UACalc Rust extension not available")
    
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
        
        # Create equivalent Rust/Python operations for normalization testing
        try:
            import uacalc
            
            # Test max operation (first operation)
            max_op_java = test_operations[0]
            max_symbol = uacalc.OperationSymbol("max", 2)
            max_table = [[0, 1, 2], [1, 1, 2], [2, 2, 2]]
            max_operation = uacalc.Operations.make_binary_int_operation(max_symbol, 3, max_table)
            
            # Test max operation properties
            self.assertTrue(uacalc.Operations.is_commutative(max_operation), "MAX should be commutative")
            self.assertTrue(uacalc.Operations.is_associative(max_operation), "MAX should be associative")
            self.assertTrue(uacalc.Operations.is_idempotent(max_operation), "MAX should be idempotent")
            
            # Test identity operation (second operation)
            id_op_java = test_operations[1]
            id_symbol = uacalc.OperationSymbol("id", 1)
            id_operation = uacalc.Operations.make_int_operation(id_symbol, 3, [0, 1, 2])
            
            # Test identity operation properties
            self.assertTrue(uacalc.Operations.is_idempotent(id_operation), "Identity should be idempotent")
            
            # Compare with Java results
            max_properties = max_op_java.get("properties", {})
            self.assertEqual(uacalc.Operations.is_commutative(max_operation), max_properties.get("is_commutative"))
            self.assertEqual(uacalc.Operations.is_associative(max_operation), max_properties.get("is_associative"))
            self.assertEqual(uacalc.Operations.is_idempotent(max_operation), max_properties.get("is_idempotent"))
            
            id_properties = id_op_java.get("properties", {})
            self.assertEqual(uacalc.Operations.is_idempotent(id_operation), id_properties.get("is_idempotent"))
            
            logger.info("Normalization test passed")
        except ImportError:
            self.skipTest("UACalc Rust extension not available")
    
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
        
        # Test Rust/Python error handling
        try:
            import uacalc
            # Test invalid table size
            symbol = uacalc.OperationSymbol("test", 2)
            # This should fail because table size doesn't match expected size
            with self.assertRaises(Exception):
                uacalc.Operations.make_int_operation(symbol, 2, [0, 1])  # Wrong size for binary operation
            
            # Test invalid values in table
            with self.assertRaises(Exception):
                uacalc.Operations.make_int_operation(symbol, 2, [0, 1, 2, 3])  # Value 3 >= cardinality 2
            
            logger.info("Error handling test passed")
        except ImportError:
            self.skipTest("UACalc Rust extension not available")
    
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
        
        # Test equivalent Rust/Python operations
        try:
            import uacalc
            
            # Test constant operation
            constant_op = uacalc.Operations.make_constant_int_operation(2, 1)
            self.assertEqual(constant_op.arity(), 0)
            self.assertEqual(constant_op.value([]), 1)
            
            # Test unary operation
            unary_symbol = uacalc.OperationSymbol("f", 1)
            unary_op = uacalc.Operations.make_int_operation(unary_symbol, 3, [0, 1, 2])
            self.assertEqual(unary_op.arity(), 1)
            self.assertEqual(unary_op.symbol, "f")
            
            # Test binary operation
            binary_symbol = uacalc.OperationSymbol("*", 2)
            binary_table = [[0, 0], [0, 1]]
            binary_op = uacalc.Operations.make_binary_int_operation(binary_symbol, 2, binary_table)
            self.assertEqual(binary_op.arity(), 2)
            self.assertEqual(binary_op.symbol, "*")
            
            # Test random operation
            random_symbol = uacalc.OperationSymbol("r", 2)
            random_op = uacalc.Operations.make_random_operation_with_seed(3, random_symbol, 123)
            self.assertEqual(random_op.arity(), 2)
            self.assertEqual(random_op.symbol, "r")
            
            # Test validation utilities on all operations
            self.assertTrue(uacalc.Operations.is_idempotent(constant_op))
            self.assertTrue(uacalc.Operations.is_idempotent(unary_op))
            self.assertTrue(uacalc.Operations.is_idempotent(binary_op))  # AND is idempotent (a ∧ a = a)
            self.assertTrue(uacalc.Operations.is_commutative(binary_op))  # AND is commutative
            self.assertTrue(uacalc.Operations.is_associative(binary_op))  # AND is associative
            
            logger.info("Complex factory scenario passed")
        except ImportError:
            self.skipTest("UACalc Rust extension not available")


if __name__ == '__main__':
    unittest.main()