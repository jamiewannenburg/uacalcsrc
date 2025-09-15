#!/usr/bin/env python3
"""
Operation Compatibility Test

This module tests the org.uacalc.alg.op.Operation interface compatibility between
Java UACalc and the Rust/Python implementation. It verifies that operation
interface methods, evaluation, and properties produce identical results.
"""

import unittest
import json
import itertools
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class OperationCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.op.Operation interface compatibility.
    
    This class tests the Operation interface methods to ensure
    the Rust implementation matches Java behavior exactly for:
    - Operation arity, symbol, and value computation
    - Operation evaluation for all possible input combinations
    - Operation properties (idempotent, associative, commutative)
    """
    
    def test_operation_arity_compatibility(self):
        """Test Operation.arity() matches between Java and Rust"""
        logger.info("Testing operation arity compatibility")
        
        for algebra_file in self.algebra_files[:8]:  # Test first 8 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                operations = algebra.operations()
                if len(operations) == 0:
                    self.skipTest(f"No operations in {algebra_file.name}")
                
                # Test each operation's arity
                for op_index, operation in enumerate(operations):
                    rust_arity = operation.arity()
                    
                    # Get arity from Java
                    java_result = self._run_java_operation(
                        "operation_properties", str(algebra_file), op_index
                    )
                    
                    if java_result is None:
                        self.skipTest("Java UACalc not available")
                    
                    if not java_result.get("success", True):
                        self.skipTest(f"Java operation failed: {java_result.get('error')}")
                    
                    java_arity = java_result.get("arity")
                    
                    # Compare results
                    result = self._compare_operation_property(
                        rust_arity,
                        java_result,
                        "arity",
                        f"arity_op_{op_index}",
                        algebra_file.name
                    )
                    
                    self.assertTrue(result.matches,
                        f"Arity mismatch for operation {op_index} in {algebra_file.name}: {result.error_message}")
    
    def test_operation_symbol_compatibility(self):
        """Test Operation.symbol() matches between Java and Rust"""
        logger.info("Testing operation symbol compatibility")
        
        for algebra_file in self.algebra_files[:8]:  # Test first 8 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                operations = algebra.operations()
                if len(operations) == 0:
                    self.skipTest(f"No operations in {algebra_file.name}")
                
                # Test each operation's symbol
                for op_index, operation in enumerate(operations):
                    rust_symbol = str(operation.symbol)
                    
                    # Get symbol from Java
                    java_result = self._run_java_operation(
                        "operation_properties", str(algebra_file), op_index
                    )
                    
                    if java_result is None:
                        self.skipTest("Java UACalc not available")
                    
                    if not java_result.get("success", True):
                        self.skipTest(f"Java operation failed: {java_result.get('error')}")
                    
                    java_symbol = java_result.get("operation_symbol")
                    
                    # Compare results
                    result = self._compare_operation_property(
                        rust_symbol,
                        java_result,
                        "operation_symbol",
                        f"symbol_op_{op_index}",
                        algebra_file.name
                    )
                    
                    self.assertTrue(result.matches,
                        f"Symbol mismatch for operation {op_index} in {algebra_file.name}: {result.error_message}")
    
    def test_operation_evaluation_compatibility(self):
        """Test operation evaluation for all possible input combinations"""
        logger.info("Testing operation evaluation compatibility")
        
        # Test on smaller algebras only for performance
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 5][:5]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                operations = algebra.operations()
                if len(operations) == 0:
                    self.skipTest(f"No operations in {algebra_file.name}")
                
                # Test each operation
                for op_index, operation in enumerate(operations):
                    # Skip operations with too many input combinations
                    if self._should_skip_operation_test(operation.arity(), algebra.cardinality):
                        continue
                    
                    # Generate all possible input combinations for small operations
                    test_cases = self._generate_all_operation_inputs(operation.arity(), algebra.cardinality)
                    
                    for inputs in test_cases:
                        # Evaluate in Rust/Python
                        try:
                            rust_result = operation.value(inputs)
                        except Exception as e:
                            self.fail(f"Rust operation evaluation failed for {algebra_file.name} op {op_index} inputs {inputs}: {e}")
                        
                        # Get evaluation from Java
                        java_result = self._run_java_operation(
                            "operation_evaluation", str(algebra_file), op_index, json.dumps(inputs)
                        )
                        
                        if java_result is None:
                            self.skipTest("Java UACalc not available")
                        
                        if not java_result.get("success", True):
                            self.fail(f"Java operation evaluation failed: {java_result.get('error')}")
                        
                        java_value = java_result.get("result")
                        
                        # Compare results
                        result = self._compare_operation_property(
                            rust_result,
                            java_result,
                            "result",
                            f"evaluation_op_{op_index}_inputs_{inputs}",
                            algebra_file.name
                        )
                        
                        self.assertTrue(result.matches,
                            f"Evaluation mismatch for operation {op_index} in {algebra_file.name} with inputs {inputs}: {result.error_message}")
    
    def test_operation_idempotent_property_compatibility(self):
        """Test operation idempotent property checking"""
        logger.info("Testing operation idempotent property compatibility")
        
        for algebra_file in self.algebra_files[:8]:  # Test first 8 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                operations = algebra.operations()
                if len(operations) == 0:
                    self.skipTest(f"No operations in {algebra_file.name}")
                
                # Test each unary operation for idempotency
                for op_index, operation in enumerate(operations):
                    if operation.arity() != 1:
                        continue  # Only test unary operations for idempotency
                    
                    # Check idempotency in Rust/Python
                    rust_is_idempotent = self._check_idempotent_rust(operation, algebra.cardinality)
                    
                    # Get idempotency from Java
                    java_result = self._run_java_operation(
                        "operation_properties", str(algebra_file), op_index
                    )
                    
                    if java_result is None:
                        self.skipTest("Java UACalc not available")
                    
                    if not java_result.get("success", True):
                        self.skipTest(f"Java operation failed: {java_result.get('error')}")
                    
                    java_is_idempotent = java_result.get("is_idempotent", False)
                    
                    # Compare results
                    result = self._compare_operation_property(
                        rust_is_idempotent,
                        java_result,
                        "is_idempotent",
                        f"idempotent_op_{op_index}",
                        algebra_file.name
                    )
                    
                    self.assertTrue(result.matches,
                        f"Idempotent property mismatch for operation {op_index} in {algebra_file.name}: {result.error_message}")
    
    def test_operation_associative_property_compatibility(self):
        """Test operation associative property checking"""
        logger.info("Testing operation associative property compatibility")
        
        # Test on smaller algebras only for performance
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:5]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                operations = algebra.operations()
                if len(operations) == 0:
                    self.skipTest(f"No operations in {algebra_file.name}")
                
                # Test each binary operation for associativity
                for op_index, operation in enumerate(operations):
                    if operation.arity() != 2:
                        continue  # Only test binary operations for associativity
                    
                    # Check associativity in Rust/Python
                    rust_is_associative = self._check_associative_rust(operation, algebra.cardinality)
                    
                    # Get associativity from Java
                    java_result = self._run_java_operation(
                        "operation_properties", str(algebra_file), op_index
                    )
                    
                    if java_result is None:
                        self.skipTest("Java UACalc not available")
                    
                    if not java_result.get("success", True):
                        self.skipTest(f"Java operation failed: {java_result.get('error')}")
                    
                    java_is_associative = java_result.get("is_associative", False)
                    
                    # Compare results
                    result = self._compare_operation_property(
                        rust_is_associative,
                        java_result,
                        "is_associative",
                        f"associative_op_{op_index}",
                        algebra_file.name
                    )
                    
                    self.assertTrue(result.matches,
                        f"Associative property mismatch for operation {op_index} in {algebra_file.name}: {result.error_message}")
    
    def test_operation_commutative_property_compatibility(self):
        """Test operation commutative property checking"""
        logger.info("Testing operation commutative property compatibility")
        
        # Test on smaller algebras only for performance
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:5]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                operations = algebra.operations()
                if len(operations) == 0:
                    self.skipTest(f"No operations in {algebra_file.name}")
                
                # Test each binary operation for commutativity
                for op_index, operation in enumerate(operations):
                    if operation.arity() != 2:
                        continue  # Only test binary operations for commutativity
                    
                    # Check commutativity in Rust/Python
                    rust_is_commutative = self._check_commutative_rust(operation, algebra.cardinality)
                    
                    # Get commutativity from Java
                    java_result = self._run_java_operation(
                        "operation_properties", str(algebra_file), op_index
                    )
                    
                    if java_result is None:
                        self.skipTest("Java UACalc not available")
                    
                    if not java_result.get("success", True):
                        self.skipTest(f"Java operation failed: {java_result.get('error')}")
                    
                    java_is_commutative = java_result.get("is_commutative", False)
                    
                    # Compare results
                    result = self._compare_operation_property(
                        rust_is_commutative,
                        java_result,
                        "is_commutative",
                        f"commutative_op_{op_index}",
                        algebra_file.name
                    )
                    
                    self.assertTrue(result.matches,
                        f"Commutative property mismatch for operation {op_index} in {algebra_file.name}: {result.error_message}")
    
    def test_operation_table_compatibility(self):
        """Test complete operation table matches between Java and Rust"""
        logger.info("Testing operation table compatibility")
        
        # Test on very small algebras only for performance
        tiny_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 3][:3]
        
        for algebra_file in tiny_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                operations = algebra.operations()
                if len(operations) == 0:
                    self.skipTest(f"No operations in {algebra_file.name}")
                
                # Test first operation only (for performance)
                operation = operations[0]
                op_index = 0
                
                # Skip operations with too many entries
                if self._should_skip_operation_test(operation.arity(), algebra.cardinality):
                    self.skipTest(f"Operation table too large for {algebra_file.name}")
                
                # Generate complete operation table in Rust/Python
                rust_table = self._generate_operation_table_rust(operation, algebra.cardinality)
                
                # Get operation table from Java
                java_result = self._run_java_operation(
                    "operation_table", str(algebra_file), op_index
                )
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_table = java_result.get("table", [])
                
                # Convert Java table to comparable format
                java_table_dict = {}
                for entry in java_table:
                    inputs_key = tuple(entry["inputs"])
                    java_table_dict[inputs_key] = entry["output"]
                
                # Compare tables
                result = self._compare_results(
                    rust_table,
                    java_table_dict,
                    f"table_op_{op_index}",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Operation table mismatch for operation {op_index} in {algebra_file.name}: {result.error_message}")
    
    # Helper methods
    
    def _compare_operation_property(self, rust_value: Any, java_result: Dict[str, Any], 
                                  property_name: str, operation: str, context: str) -> Any:
        """Compare a specific property from Java operation result"""
        from tests.python.base_compatibility_test import CompatibilityTestResult
        
        test_name = f"{self.__class__.__name__}.{self._testMethodName}"
        algebra_name = context or "unknown"
        
        if java_result is None:
            result = CompatibilityTestResult(
                test_name=test_name,
                algebra_name=algebra_name,
                operation=operation,
                rust_result=rust_value,
                java_result=None,
                matches=False,
                error_message="Java operation returned None (Java unavailable)",
                context=context
            )
            self.current_test_results.append(result)
            return result
        
        if not java_result.get("success", True):
            error_msg = java_result.get("error", "Unknown Java error")
            result = CompatibilityTestResult(
                test_name=test_name,
                algebra_name=algebra_name,
                operation=operation,
                rust_result=rust_value,
                java_result=java_result,
                matches=False,
                error_message=f"Java operation failed: {error_msg}",
                execution_time_java=java_result.get('_execution_time', 0.0),
                context=context
            )
            self.current_test_results.append(result)
            return result
        
        java_value = java_result.get(property_name)
        
        # Perform comparison
        matches = rust_value == java_value
        error_message = None if matches else f"Values differ: Rust={rust_value}, Java={java_value}"
        
        result = CompatibilityTestResult(
            test_name=test_name,
            algebra_name=algebra_name,
            operation=operation,
            rust_result=rust_value,
            java_result=java_result,
            matches=matches,
            error_message=error_message,
            execution_time_java=java_result.get('_execution_time', 0.0),
            context=context
        )
        
        self.current_test_results.append(result)
        return result
    
    def _get_algebra_size_estimate(self, algebra_file: Path) -> int:
        """Estimate algebra size from file size (rough heuristic)"""
        try:
            file_size = algebra_file.stat().st_size
            # Very rough estimate: smaller files = smaller algebras
            if file_size < 1000:
                return 3
            elif file_size < 5000:
                return 6
            elif file_size < 20000:
                return 10
            else:
                return 20
        except:
            return 10  # Default estimate
    
    def _should_skip_operation_test(self, arity: int, cardinality: int) -> bool:
        """Determine if operation test should be skipped based on complexity"""
        # Skip if too many input combinations
        total_combinations = cardinality ** arity
        return total_combinations > 1000
    
    def _generate_all_operation_inputs(self, arity: int, cardinality: int) -> List[List[int]]:
        """Generate all possible input combinations for an operation"""
        if arity == 0:
            return [[]]  # Nullary operation
        
        return list(itertools.product(range(cardinality), repeat=arity))
    
    def _check_idempotent_rust(self, operation, cardinality: int) -> bool:
        """Check if a unary operation is idempotent in Rust/Python"""
        if operation.arity() != 1:
            return False
        
        for i in range(cardinality):
            if operation.value([i]) != i:
                return False
        return True
    
    def _check_associative_rust(self, operation, cardinality: int) -> bool:
        """Check if a binary operation is associative in Rust/Python"""
        if operation.arity() != 2:
            return False
        
        for a in range(cardinality):
            for b in range(cardinality):
                for c in range(cardinality):
                    left = operation.value([operation.value([a, b]), c])
                    right = operation.value([a, operation.value([b, c])])
                    if left != right:
                        return False
        return True
    
    def _check_commutative_rust(self, operation, cardinality: int) -> bool:
        """Check if a binary operation is commutative in Rust/Python"""
        if operation.arity() != 2:
            return False
        
        for a in range(cardinality):
            for b in range(cardinality):
                left = operation.value([a, b])
                right = operation.value([b, a])
                if left != right:
                    return False
        return True
    
    def _generate_operation_table_rust(self, operation, cardinality: int) -> Dict[Tuple[int, ...], int]:
        """Generate complete operation table in Rust/Python"""
        table = {}
        
        if operation.arity() == 0:
            # Nullary operation
            table[()] = operation.value([])
        else:
            # Generate all input combinations
            for inputs in itertools.product(range(cardinality), repeat=operation.arity()):
                inputs_list = list(inputs)
                output = operation.value(inputs_list)
                table[inputs] = output
        
        return table


if __name__ == '__main__':
    unittest.main()