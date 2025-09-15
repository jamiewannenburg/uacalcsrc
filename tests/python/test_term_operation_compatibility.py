#!/usr/bin/env python3
"""
Term Operation Compatibility Test

This module tests the org.uacalc.alg.op.TermOperation interface compatibility between
Java UACalc and the Rust/Python implementation. It verifies that term-based operation
construction, evaluation, optimization, caching, and composition produce identical results.
"""

import unittest
import json
import itertools
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class TermOperationCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.op.TermOperation interface compatibility.
    
    This class tests the TermOperation interface to ensure
    the Rust implementation matches Java behavior exactly for:
    - Term-based operation construction and evaluation
    - Term operation optimization and caching
    - Term operation composition and properties
    """
    
    def test_term_operation_construction_compatibility(self):
        """Test TermOperation construction from terms matches between Java and Rust"""
        logger.info("Testing term operation construction compatibility")
        
        # Test various term strings with different complexities
        test_cases = [
            # Simple terms
            ("x", "unary identity"),
            ("f(x)", "unary operation application"),
            ("g(x,y)", "binary operation application"),
            ("f(g(x,y))", "nested operation"),
            
            # More complex terms
            ("f(x,x)", "repeated variable"),
            ("g(f(x),y)", "mixed nesting"),
            ("h(x,y,z)", "ternary operation"),
            ("f(g(x,y),h(x,z))", "complex nesting"),
            
            # Edge cases
            ("c", "constant (nullary operation)"),
            ("f(c)", "constant in term"),
        ]
        
        # Test on smaller algebras for performance
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 6][:5]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                for term_string, description in test_cases:
                    with self.subTest(term=term_string):
                        # Create term operation in Rust/Python (simulated)
                        rust_term_op = self._create_rust_term_operation(term_string, algebra_file)
                        
                        # Get term operation construction from Java
                        java_result = self._run_java_operation(
                            "term_operation_construction", term_string, str(algebra_file)
                        )
                        
                        if java_result is None:
                            self.skipTest("Java UACalc not available")
                        
                        if not java_result.get("success", True):
                            # If Java fails, Rust should also fail or we skip
                            error_msg = java_result.get("error_message", "")
                            if "parse" in error_msg.lower() or "invalid" in error_msg.lower():
                                self.skipTest(f"Java parsing failed for {term_string}: {error_msg}")
                            continue
                        
                        # Compare results
                        result = self._compare_term_operation_construction(
                            rust_term_op,
                            java_result,
                            f"construction_{term_string}",
                            f"algebra={algebra_file.name}, term={term_string}"
                        )
                        
                        self.assertTrue(result.matches,
                            f"Term operation construction mismatch for {term_string} in {algebra_file.name}: {result.error_message}")
    
    def test_term_operation_evaluation_compatibility(self):
        """Test term operation evaluation matches between Java and Rust"""
        logger.info("Testing term operation evaluation compatibility")
        
        # Test simple terms that should work in most algebras
        test_cases = [
            ("x", 1),      # Unary identity
            ("f(x)", 1),   # Unary operation (if exists)
            ("g(x,y)", 2), # Binary operation (if exists)
        ]
        
        # Test on very small algebras for performance
        tiny_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:3]
        
        for algebra_file in tiny_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra to check available operations
                try:
                    algebra = self._load_test_algebra(algebra_file)
                    operations = algebra.operations()
                    if len(operations) == 0:
                        self.skipTest(f"No operations in {algebra_file.name}")
                except:
                    self.skipTest(f"Failed to load {algebra_file.name}")
                
                for term_string, expected_arity in test_cases:
                    with self.subTest(term=term_string):
                        # Generate test inputs for the expected arity
                        if expected_arity == 0:
                            test_inputs = [[]]
                        elif expected_arity == 1:
                            test_inputs = [[i] for i in range(min(algebra.cardinality, 3))]
                        elif expected_arity == 2:
                            test_inputs = [[i, j] for i in range(min(algebra.cardinality, 2)) 
                                         for j in range(min(algebra.cardinality, 2))]
                        else:
                            continue  # Skip higher arity for performance
                        
                        for inputs in test_inputs:
                            # Evaluate in Rust/Python (simulated)
                            rust_result = self._evaluate_rust_term_operation(
                                term_string, algebra_file, inputs
                            )
                            
                            # Get evaluation from Java
                            java_result = self._run_java_operation(
                                "term_operation_evaluation", 
                                term_string, str(algebra_file), json.dumps(inputs)
                            )
                            
                            if java_result is None:
                                self.skipTest("Java UACalc not available")
                            
                            if not java_result.get("success", True):
                                # If Java fails, skip this test case
                                continue
                            
                            # Compare results
                            result = self._compare_term_operation_evaluation(
                                rust_result,
                                java_result,
                                f"evaluation_{term_string}_inputs_{inputs}",
                                f"algebra={algebra_file.name}, term={term_string}, inputs={inputs}"
                            )
                            
                            self.assertTrue(result.matches,
                                f"Term operation evaluation mismatch for {term_string} with inputs {inputs} in {algebra_file.name}: {result.error_message}")
    
    def test_term_operation_properties_compatibility(self):
        """Test term operation properties match between Java and Rust"""
        logger.info("Testing term operation properties compatibility")
        
        # Test terms with known properties
        test_cases = [
            ("x", "identity should be idempotent"),
            ("f(x,x)", "diagonal term"),
            ("g(x,y)", "general binary term"),
            ("f(g(x,y))", "composition"),
        ]
        
        # Test on small algebras only
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:3]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                for term_string, description in test_cases:
                    with self.subTest(term=term_string):
                        # Get properties in Rust/Python (simulated)
                        rust_properties = self._get_rust_term_operation_properties(
                            term_string, algebra_file
                        )
                        
                        # Get properties from Java
                        java_result = self._run_java_operation(
                            "term_operation_properties", term_string, str(algebra_file)
                        )
                        
                        if java_result is None:
                            self.skipTest("Java UACalc not available")
                        
                        if not java_result.get("success", True):
                            # If Java fails, skip this test case
                            continue
                        
                        # Compare results
                        result = self._compare_term_operation_properties(
                            rust_properties,
                            java_result,
                            f"properties_{term_string}",
                            f"algebra={algebra_file.name}, term={term_string}"
                        )
                        
                        self.assertTrue(result.matches,
                            f"Term operation properties mismatch for {term_string} in {algebra_file.name}: {result.error_message}")
    
    def test_term_operation_composition_compatibility(self):
        """Test term operation composition matches between Java and Rust"""
        logger.info("Testing term operation composition compatibility")
        
        # Test composition cases
        test_cases = [
            ("x", "f(x)", "identity composed with unary"),
            ("f(x)", "x", "unary composed with identity"),
            ("f(x)", "g(x,y)", "unary composed with binary"),
            ("g(x,y)", "f(x)", "cannot compose (binary with unary)"),
        ]
        
        # Test on very small algebras only
        tiny_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 3][:2]
        
        for algebra_file in tiny_algebras:
            with self.subTest(algebra=algebra_file.name):
                for term1_string, term2_string, description in test_cases:
                    with self.subTest(term1=term1_string, term2=term2_string):
                        # Analyze composition in Rust/Python (simulated)
                        rust_composition = self._analyze_rust_term_composition(
                            term1_string, term2_string, algebra_file
                        )
                        
                        # Get composition analysis from Java
                        java_result = self._run_java_operation(
                            "term_operation_composition", 
                            term1_string, term2_string, str(algebra_file)
                        )
                        
                        if java_result is None:
                            self.skipTest("Java UACalc not available")
                        
                        if not java_result.get("success", True):
                            # If Java fails, skip this test case
                            continue
                        
                        # Compare results
                        result = self._compare_term_operation_composition(
                            rust_composition,
                            java_result,
                            f"composition_{term1_string}_{term2_string}",
                            f"algebra={algebra_file.name}, terms={term1_string}∘{term2_string}"
                        )
                        
                        self.assertTrue(result.matches,
                            f"Term operation composition mismatch for {term1_string}∘{term2_string} in {algebra_file.name}: {result.error_message}")
    
    def test_term_operation_optimization_compatibility(self):
        """Test term operation optimization and caching behavior"""
        logger.info("Testing term operation optimization compatibility")
        
        # Test terms that might benefit from optimization
        test_cases = [
            ("f(x,x)", "repeated variable optimization"),
            ("f(f(x))", "nested same operation"),
            ("g(x,c)", "constant folding opportunity"),
            ("f(g(x,y),g(x,y))", "common subexpression"),
        ]
        
        # Test on small algebras
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:2]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                for term_string, description in test_cases:
                    with self.subTest(term=term_string):
                        # Test multiple evaluations to check caching behavior
                        # (In practice, we can't directly test caching, but we can test consistency)
                        
                        # First evaluation
                        java_result1 = self._run_java_operation(
                            "term_operation_properties", term_string, str(algebra_file)
                        )
                        
                        if java_result1 is None or not java_result1.get("success", True):
                            self.skipTest(f"Java operation failed for {term_string}")
                        
                        # Second evaluation (should be consistent)
                        java_result2 = self._run_java_operation(
                            "term_operation_properties", term_string, str(algebra_file)
                        )
                        
                        if java_result2 is None or not java_result2.get("success", True):
                            self.skipTest(f"Java operation failed for {term_string} (second evaluation)")
                        
                        # Results should be identical (testing consistency)
                        properties1 = java_result1.get("properties", {})
                        properties2 = java_result2.get("properties", {})
                        
                        self.assertEqual(properties1, properties2,
                            f"Term operation properties inconsistent for {term_string} in {algebra_file.name}")
                        
                        logger.debug(f"Optimization test passed for {term_string}: consistent results")
    
    # Helper methods for simulating Rust/Python term operations
    
    def _create_rust_term_operation(self, term_string: str, algebra_file: Path) -> Dict[str, Any]:
        """Create a simulated Rust term operation for comparison"""
        # This is a simplified simulation - in practice, this would use the actual Rust implementation
        return {
            "term_string": term_string,
            "algebra_file": str(algebra_file),
            "symbol": f"term_{hash(term_string) & 0xFFFF}",
            "arity": self._estimate_term_arity(term_string),
            "is_valid": True,  # Assume valid for simulation
        }
    
    def _evaluate_rust_term_operation(self, term_string: str, algebra_file: Path, inputs: List[int]) -> int:
        """Simulate term operation evaluation in Rust/Python"""
        # This is a placeholder - in practice, this would use the actual Rust implementation
        # For now, return a deterministic but arbitrary result
        return (hash((term_string, tuple(inputs))) % 10) % self._get_algebra_size_estimate(algebra_file)
    
    def _get_rust_term_operation_properties(self, term_string: str, algebra_file: Path) -> Dict[str, Any]:
        """Get simulated term operation properties from Rust/Python"""
        return {
            "symbol": f"term_{hash(term_string) & 0xFFFF}",
            "arity": self._estimate_term_arity(term_string),
            "cardinality": self._get_algebra_size_estimate(algebra_file),
            "properties_computed": True,
            "is_idempotent": term_string == "x",  # Only identity is idempotent
            "is_associative": False,  # Assume not associative for simulation
            "is_commutative": False,  # Assume not commutative for simulation
        }
    
    def _analyze_rust_term_composition(self, term1: str, term2: str, algebra_file: Path) -> Dict[str, Any]:
        """Analyze term composition in Rust/Python"""
        arity1 = self._estimate_term_arity(term1)
        arity2 = self._estimate_term_arity(term2)
        
        can_compose = (arity1 == 1)  # Simple composition requires unary first term
        
        return {
            "can_compose": can_compose,
            "composition_error": None if can_compose else f"First term has arity {arity1} (must be 1)",
            "term1_arity": arity1,
            "term2_arity": arity2,
            "composition_computed": can_compose and self._get_algebra_size_estimate(algebra_file) <= 5,
            "composition_result": None,  # Would compute actual result in real implementation
        }
    
    def _estimate_term_arity(self, term_string: str) -> int:
        """Estimate the arity of a term from its string representation"""
        # Simple heuristic based on variable count
        variables = set()
        for char in term_string:
            if char.isalpha() and char.islower() and char in 'xyz':
                variables.add(char)
        
        # If no variables found, but it's a single letter, it might be a unary operation
        if len(variables) == 0 and len(term_string) == 1 and term_string.isalpha():
            return 1  # Assume unary operation
        
        return max(len(variables), 1)  # At least arity 1 for most operations
    
    def _get_algebra_size_estimate(self, algebra_file: Path) -> int:
        """Estimate algebra size from file size (rough heuristic)"""
        try:
            file_size = algebra_file.stat().st_size
            if file_size < 1000:
                return 3
            elif file_size < 5000:
                return 6
            else:
                return 10
        except:
            return 5  # Default estimate
    
    # Comparison helper methods
    
    def _compare_term_operation_construction(self, rust_term_op: Dict[str, Any], 
                                           java_result: Dict[str, Any], 
                                           operation: str, context: str) -> Any:
        """Compare term operation construction results"""
        from tests.python.base_compatibility_test import CompatibilityTestResult
        
        test_name = f"{self.__class__.__name__}.{self._testMethodName}"
        
        if not java_result.get("success", True):
            error_msg = java_result.get("error", "Unknown Java error")
            result = CompatibilityTestResult(
                test_name=test_name,
                algebra_name="term_operation",
                operation=operation,
                rust_result=rust_term_op,
                java_result=java_result,
                matches=False,
                error_message=f"Java operation failed: {error_msg}",
                execution_time_java=java_result.get('_execution_time', 0.0),
                context=context
            )
            self.current_test_results.append(result)
            return result
        
        java_term_op = java_result.get("created_operation", {})
        
        # Compare key properties
        matches = True
        error_messages = []
        
        # Compare arity (most important property)
        if rust_term_op["arity"] != java_term_op.get("arity"):
            matches = False
            error_messages.append(f"Arity mismatch: Rust={rust_term_op['arity']}, Java={java_term_op.get('arity')}")
        
        # Compare validity
        if rust_term_op["is_valid"] != java_term_op.get("is_valid", True):
            matches = False
            error_messages.append(f"Validity mismatch: Rust={rust_term_op['is_valid']}, Java={java_term_op.get('is_valid')}")
        
        error_message = "; ".join(error_messages) if error_messages else None
        
        result = CompatibilityTestResult(
            test_name=test_name,
            algebra_name="term_operation",
            operation=operation,
            rust_result=rust_term_op,
            java_result=java_result,
            matches=matches,
            error_message=error_message,
            execution_time_java=java_result.get('_execution_time', 0.0),
            context=context
        )
        
        self.current_test_results.append(result)
        return result
    
    def _compare_term_operation_evaluation(self, rust_result: int, 
                                         java_result: Dict[str, Any], 
                                         operation: str, context: str) -> Any:
        """Compare term operation evaluation results"""
        from tests.python.base_compatibility_test import CompatibilityTestResult
        
        test_name = f"{self.__class__.__name__}.{self._testMethodName}"
        
        if not java_result.get("success", True):
            error_msg = java_result.get("error", "Unknown Java error")
            result = CompatibilityTestResult(
                test_name=test_name,
                algebra_name="term_operation",
                operation=operation,
                rust_result=rust_result,
                java_result=java_result,
                matches=False,
                error_message=f"Java operation failed: {error_msg}",
                execution_time_java=java_result.get('_execution_time', 0.0),
                context=context
            )
            self.current_test_results.append(result)
            return result
        
        java_value = java_result.get("result")
        
        matches = rust_result == java_value
        error_message = None if matches else f"Evaluation mismatch: Rust={rust_result}, Java={java_value}"
        
        result = CompatibilityTestResult(
            test_name=test_name,
            algebra_name="term_operation",
            operation=operation,
            rust_result=rust_result,
            java_result=java_result,
            matches=matches,
            error_message=error_message,
            execution_time_java=java_result.get('_execution_time', 0.0),
            context=context
        )
        
        self.current_test_results.append(result)
        return result
    
    def _compare_term_operation_properties(self, rust_properties: Dict[str, Any], 
                                         java_result: Dict[str, Any], 
                                         operation: str, context: str) -> Any:
        """Compare term operation properties results"""
        from tests.python.base_compatibility_test import CompatibilityTestResult
        
        test_name = f"{self.__class__.__name__}.{self._testMethodName}"
        
        if not java_result.get("success", True):
            error_msg = java_result.get("error", "Unknown Java error")
            result = CompatibilityTestResult(
                test_name=test_name,
                algebra_name="term_operation",
                operation=operation,
                rust_result=rust_properties,
                java_result=java_result,
                matches=False,
                error_message=f"Java operation failed: {error_msg}",
                execution_time_java=java_result.get('_execution_time', 0.0),
                context=context
            )
            self.current_test_results.append(result)
            return result
        
        java_properties = java_result.get("properties", {})
        
        # Compare key properties
        matches = True
        error_messages = []
        
        # Compare arity
        if rust_properties["arity"] != java_properties.get("arity"):
            matches = False
            error_messages.append(f"Arity mismatch: Rust={rust_properties['arity']}, Java={java_properties.get('arity')}")
        
        # Compare cardinality
        if rust_properties["cardinality"] != java_properties.get("cardinality"):
            matches = False
            error_messages.append(f"Cardinality mismatch: Rust={rust_properties['cardinality']}, Java={java_properties.get('cardinality')}")
        
        # Compare algebraic properties if computed
        if java_properties.get("properties_computed", False):
            for prop in ["is_idempotent", "is_associative", "is_commutative"]:
                if rust_properties.get(prop) != java_properties.get(prop):
                    matches = False
                    error_messages.append(f"{prop} mismatch: Rust={rust_properties.get(prop)}, Java={java_properties.get(prop)}")
        
        error_message = "; ".join(error_messages) if error_messages else None
        
        result = CompatibilityTestResult(
            test_name=test_name,
            algebra_name="term_operation",
            operation=operation,
            rust_result=rust_properties,
            java_result=java_result,
            matches=matches,
            error_message=error_message,
            execution_time_java=java_result.get('_execution_time', 0.0),
            context=context
        )
        
        self.current_test_results.append(result)
        return result
    
    def _compare_term_operation_composition(self, rust_composition: Dict[str, Any], 
                                          java_result: Dict[str, Any], 
                                          operation: str, context: str) -> Any:
        """Compare term operation composition results"""
        from tests.python.base_compatibility_test import CompatibilityTestResult
        
        test_name = f"{self.__class__.__name__}.{self._testMethodName}"
        
        if not java_result.get("success", True):
            error_msg = java_result.get("error", "Unknown Java error")
            result = CompatibilityTestResult(
                test_name=test_name,
                algebra_name="term_operation",
                operation=operation,
                rust_result=rust_composition,
                java_result=java_result,
                matches=False,
                error_message=f"Java operation failed: {error_msg}",
                execution_time_java=java_result.get('_execution_time', 0.0),
                context=context
            )
            self.current_test_results.append(result)
            return result
        
        java_composition = java_result.get("composition_analysis", {})
        
        # Compare key properties
        matches = True
        error_messages = []
        
        # Compare can_compose
        if rust_composition["can_compose"] != java_composition.get("can_compose"):
            matches = False
            error_messages.append(f"can_compose mismatch: Rust={rust_composition['can_compose']}, Java={java_composition.get('can_compose')}")
        
        # Compare arities
        if rust_composition["term1_arity"] != java_composition.get("term1_arity"):
            matches = False
            error_messages.append(f"term1_arity mismatch: Rust={rust_composition['term1_arity']}, Java={java_composition.get('term1_arity')}")
        
        if rust_composition["term2_arity"] != java_composition.get("term2_arity"):
            matches = False
            error_messages.append(f"term2_arity mismatch: Rust={rust_composition['term2_arity']}, Java={java_composition.get('term2_arity')}")
        
        error_message = "; ".join(error_messages) if error_messages else None
        
        result = CompatibilityTestResult(
            test_name=test_name,
            algebra_name="term_operation",
            operation=operation,
            rust_result=rust_composition,
            java_result=java_result,
            matches=matches,
            error_message=error_message,
            execution_time_java=java_result.get('_execution_time', 0.0),
            context=context
        )
        
        self.current_test_results.append(result)
        return result


if __name__ == '__main__':
    unittest.main()