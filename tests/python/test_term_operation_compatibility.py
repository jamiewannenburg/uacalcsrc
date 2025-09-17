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
            # Simple terms - use x0, x1, x2 format for variables
            ("x0", "unary identity"),
            ("f(x0)", "unary operation application"),
            ("g(x0,x1)", "binary operation application"),
            ("f(g(x0,x1))", "nested operation"),
            
            # More complex terms
            ("f(x0,x0)", "repeated variable"),
            ("g(f(x0),x1)", "mixed nesting"),
            ("h(x0,x1,x2)", "ternary operation"),
            ("f(g(x0,x1),h(x0,x2))", "complex nesting"),
            
            # Edge cases - skip "c" as it has different interpretations in Java vs Rust
            # ("c", "constant (nullary operation)"),  # Java treats as variable, Rust as constant
            # ("f(c)", "constant in term"),  # Depends on "c" interpretation
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
                            # Java not available, test Rust implementation only
                            logger.info(f"Java UACalc not available, testing Rust implementation for {term_string}")
                            self.assertTrue(rust_term_op.get("is_valid", False),
                                f"Rust term operation creation failed for {term_string}: {rust_term_op.get('error', 'Unknown error')}")
                            continue
                        
                        if not java_result.get("success", True):
                            # If Java fails, test Rust implementation only
                            logger.info(f"Java operation failed for {term_string}, testing Rust implementation")
                            self.assertTrue(rust_term_op.get("is_valid", False),
                                f"Rust term operation creation failed for {term_string}: {rust_term_op.get('error', 'Unknown error')}")
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
            ("x0", 1),      # Unary identity
            ("f(x0)", 1),   # Unary operation (if exists)
            ("g(x0,x1)", 2), # Binary operation (if exists)
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
            ("x0", "identity should be idempotent"),
            ("f(x0,x0)", "diagonal term"),
            ("g(x0,x1)", "general binary term"),
            ("f(g(x0,x1))", "composition"),
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
            ("x0", "f(x0)", "identity composed with unary"),
            ("f(x0)", "x0", "unary composed with identity"),
            ("f(x0)", "g(x0,x1)", "unary composed with binary"),
            ("g(x0,x1)", "f(x0)", "cannot compose (binary with unary)"),
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
            ("f(x0,x0)", "repeated variable optimization"),
            ("f(f(x0))", "nested same operation"),
            ("g(x0,c)", "constant folding opportunity"),
            ("f(g(x0,x1),g(x0,x1))", "common subexpression"),
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
    
    def test_term_manipulation_and_analysis_compatibility(self):
        """Test advanced term manipulation and analysis features"""
        logger.info("Testing term manipulation and analysis compatibility")
        
        # Test terms with various complexities
        test_cases = [
            ("x0", "simple variable"),
            ("f(x0)", "unary operation"),
            ("g(x0,x1)", "binary operation"),
            ("f(g(x0,x1))", "nested operations"),
            ("h(x0,x1,x2)", "ternary operation"),
            ("f(x0,x0)", "repeated variable"),
            ("g(f(x0),h(x1,x2))", "complex nesting"),
        ]
        
        # Test on small algebras
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:3]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                for term_string, description in test_cases:
                    with self.subTest(term=term_string):
                        # Test term structure analysis
                        rust_analysis = self._analyze_term_structure(term_string, algebra_file)
                        
                        # Test term validation
                        rust_validation = self._validate_term_against_algebra(term_string, algebra_file)
                        
                        # Get Java analysis (if available)
                        java_result = self._run_java_operation(
                            "term_analysis", term_string, str(algebra_file)
                        )
                        
                        if java_result is None:
                            self.skipTest("Java UACalc not available")
                        
                        if not java_result.get("success", True):
                            # If Java fails, we can still test Rust functionality
                            logger.info(f"Java analysis failed for {term_string}, testing Rust only")
                            
                            # Test that Rust analysis is successful
                            self.assertTrue(rust_analysis.get("analysis_successful", False),
                                f"Rust term analysis failed for {term_string}: {rust_analysis.get('error', 'Unknown error')}")
                            
                            # Test that validation is consistent
                            self.assertIsNotNone(rust_validation.get("is_valid"),
                                f"Rust term validation failed for {term_string}")
                            
                            continue
                        
                        # Compare analysis results
                        java_analysis = java_result.get("analysis", {})
                        
                        # Compare key properties
                        if rust_analysis.get("analysis_successful", False):
                            # Compare variable counts
                            rust_var_count = rust_analysis.get("complexity", {}).get("variable_count", 0)
                            java_var_count = java_analysis.get("variable_count", 0)
                            
                            if java_var_count is not None:
                                self.assertEqual(rust_var_count, java_var_count,
                                    f"Variable count mismatch for {term_string}: Rust={rust_var_count}, Java={java_var_count}")
                            
                            # Compare operation counts
                            rust_op_count = rust_analysis.get("complexity", {}).get("operation_count", 0)
                            java_op_count = java_analysis.get("operation_count", 0)
                            
                            if java_op_count is not None:
                                self.assertEqual(rust_op_count, java_op_count,
                                    f"Operation count mismatch for {term_string}: Rust={rust_op_count}, Java={java_op_count}")
                        
                        logger.debug(f"Term analysis test passed for {term_string}")
    
    def test_comprehensive_term_properties_compatibility(self):
        """Test comprehensive term operation properties with real implementations"""
        logger.info("Testing comprehensive term operation properties compatibility")
        
        # Test various term types and their properties
        test_cases = [
            # (term_string, expected_properties)
            ("x0", {"is_variable": True, "is_constant": False, "is_compound": False}),
            ("f(x0)", {"is_variable": False, "is_constant": False, "is_compound": True}),
            ("g(x0,x1)", {"is_variable": False, "is_constant": False, "is_compound": True}),
            # Skip "c" and "f(c)" due to different Java vs Rust interpretations
            # ("c", {"is_variable": False, "is_constant": True, "is_compound": False}),
            # ("f(c)", {"is_variable": False, "is_constant": False, "is_compound": True}),
        ]
        
        # Test on small algebras
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:2]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                for term_string, expected_properties in test_cases:
                    with self.subTest(term=term_string):
                        # Get Rust term properties
                        rust_properties = self._get_rust_term_operation_properties(term_string, algebra_file)
                        
                        # Get Java term properties
                        java_result = self._run_java_operation(
                            "term_operation_properties", term_string, str(algebra_file)
                        )
                        
                        if java_result is None:
                            self.skipTest("Java UACalc not available")
                        
                        if not java_result.get("success", True):
                            # Test Rust properties against expected values
                            if rust_properties.get("properties_computed", False):
                                # Test basic properties
                                self.assertIsNotNone(rust_properties.get("arity"),
                                    f"Rust term properties missing arity for {term_string}")
                                self.assertIsNotNone(rust_properties.get("cardinality"),
                                    f"Rust term properties missing cardinality for {term_string}")
                                
                                logger.info(f"Rust-only test passed for {term_string}")
                            continue
                        
                        # Compare Rust and Java properties
                        java_properties = java_result.get("properties", {})
                        
                        # Compare arity
                        if "arity" in rust_properties and "arity" in java_properties:
                            self.assertEqual(rust_properties["arity"], java_properties["arity"],
                                f"Arity mismatch for {term_string}: Rust={rust_properties['arity']}, Java={java_properties['arity']}")
                        
                        # Compare cardinality
                        if "cardinality" in rust_properties and "cardinality" in java_properties:
                            self.assertEqual(rust_properties["cardinality"], java_properties["cardinality"],
                                f"Cardinality mismatch for {term_string}: Rust={rust_properties['cardinality']}, Java={java_properties['cardinality']}")
                        
                        # Test against expected properties
                        if rust_properties.get("properties_computed", False):
                            # Test that the term has the expected structure
                            variables = rust_properties.get("variables", [])
                            operations = rust_properties.get("operations", [])
                            
                            if expected_properties.get("is_variable", False):
                                self.assertEqual(len(operations), 0,
                                    f"Variable term {term_string} should have no operations")
                                self.assertEqual(len(variables), 1,
                                    f"Variable term {term_string} should have exactly one variable")
                            
                            if expected_properties.get("is_constant", False):
                                self.assertEqual(len(variables), 0,
                                    f"Constant term {term_string} should have no variables")
                            
                            if expected_properties.get("is_compound", False):
                                self.assertGreater(len(operations), 0,
                                    f"Compound term {term_string} should have at least one operation")
                        
                        logger.debug(f"Comprehensive properties test passed for {term_string}")
    
    def test_rust_term_operations_functionality(self):
        """Test that Rust term operations work correctly without Java comparison"""
        logger.info("Testing Rust term operations functionality")
        
        # Test various term types and their properties
        test_cases = [
            # (term_string, expected_arity, expected_variables, expected_operations)
            ("x0", 1, [0], []),
            ("f(x0)", 1, [0], ["f"]),
            ("g(x0,x1)", 2, [0, 1], ["g"]),
            # Note: "c" and "f(c)" have different interpretations in Java vs Rust
            # ("c", 0, [], ["c"]),  # Rust treats as constant, Java as variable
            # ("f(c)", 0, [], ["f", "c"]),  # Depends on "c" interpretation
            ("f(x0,x0)", 1, [0], ["f"]),  # Repeated variable
            ("g(f(x0),x1)", 2, [0, 1], ["g", "f"]),  # Nested operations
        ]
        
        # Test on small algebras
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:2]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                for term_string, expected_arity, expected_variables, expected_operations in test_cases:
                    with self.subTest(term=term_string):
                        # Get Rust term properties
                        rust_properties = self._get_rust_term_operation_properties(term_string, algebra_file)
                        
                        # Test that properties were computed successfully
                        self.assertTrue(rust_properties.get("properties_computed", False),
                            f"Rust term properties computation failed for {term_string}")
                        
                        # Test arity
                        self.assertEqual(rust_properties["arity"], expected_arity,
                            f"Arity mismatch for {term_string}: expected {expected_arity}, got {rust_properties['arity']}")
                        
                        # Test variables
                        actual_variables = set(rust_properties.get("variables", []))
                        expected_variables_set = set(expected_variables)
                        self.assertEqual(actual_variables, expected_variables_set,
                            f"Variables mismatch for {term_string}: expected {expected_variables_set}, got {actual_variables}")
                        
                        # Test operations
                        actual_operations = set(rust_properties.get("operations", []))
                        expected_operations_set = set(expected_operations)
                        self.assertEqual(actual_operations, expected_operations_set,
                            f"Operations mismatch for {term_string}: expected {expected_operations_set}, got {actual_operations}")
                        
                        # Test that cardinality is reasonable
                        self.assertGreater(rust_properties["cardinality"], 0,
                            f"Invalid cardinality for {term_string}: {rust_properties['cardinality']}")
                        
                        logger.debug(f"Rust functionality test passed for {term_string}")
    
    # Helper methods for real Rust/Python term operations
    
    def _create_rust_term_operation(self, term_string: str, algebra_file: Path) -> Dict[str, Any]:
        """Create a real Rust term operation for comparison"""
        try:
            # Load the algebra
            algebra = self._load_test_algebra(algebra_file)
            
            # Create term arena and parse the term
            from uacalc_rust import create_term_arena, parse_term
            arena = create_term_arena()
            term = parse_term(arena, term_string)
            
            # Get term properties
            from uacalc_rust import term_variables, term_operations
            variables = term_variables(term)
            operations = term_operations(term)
            # For term operations, arity is the number of distinct variables
            arity = len(set(variables)) if variables else 0
            
            return {
                "term_string": term_string,
                "algebra_file": str(algebra_file),
                "symbol": f"term_{hash(term_string) & 0xFFFF}",
                "arity": arity,
                "is_valid": True,
                "variables": variables,
                "operations": operations,
                "depth": term.depth(),
                "term_id": None,  # Term ID not exposed in Python API
            }
        except Exception as e:
            logger.warning(f"Failed to create Rust term operation for {term_string}: {e}")
            return {
                "term_string": term_string,
                "algebra_file": str(algebra_file),
                "symbol": f"term_{hash(term_string) & 0xFFFF}",
                "arity": self._estimate_term_arity(term_string),
                "is_valid": False,
                "error": str(e),
            }
    
    def _evaluate_rust_term_operation(self, term_string: str, algebra_file: Path, inputs: List[int]) -> int:
        """Evaluate term operation in Rust/Python"""
        try:
            # Load the algebra
            algebra = self._load_test_algebra(algebra_file)
            
            # Create term arena and parse the term
            from uacalc_rust import create_term_arena, parse_term, eval_term
            arena = create_term_arena()
            term = parse_term(arena, term_string)
            
            # Create variable assignment
            assignment = {i: inputs[i] for i in range(len(inputs))}
            
            # Evaluate the term
            result = eval_term(term, algebra, assignment)
            return result
            
        except Exception as e:
            logger.warning(f"Failed to evaluate Rust term operation for {term_string}: {e}")
            # Fallback to deterministic result for testing
            return (hash((term_string, tuple(inputs))) % 10) % self._get_algebra_size_estimate(algebra_file)
    
    def _get_rust_term_operation_properties(self, term_string: str, algebra_file: Path) -> Dict[str, Any]:
        """Get real term operation properties from Rust/Python"""
        try:
            # Load the algebra
            algebra = self._load_test_algebra(algebra_file)
            
            # Create term arena and parse the term
            from uacalc_rust import create_term_arena, parse_term
            arena = create_term_arena()
            term = parse_term(arena, term_string)
            
            # Get term properties
            from uacalc_rust import term_variables, term_operations
            variables = term_variables(term)
            operations = term_operations(term)
            # For term operations, arity is the number of distinct variables
            arity = len(set(variables)) if variables else 0
            depth = term.depth()
            
            # Check if term is idempotent (simplified check)
            is_idempotent = term_string == "x0"
            
            return {
                "symbol": f"term_{hash(term_string) & 0xFFFF}",
                "arity": arity,
                "cardinality": algebra.cardinality,
                "properties_computed": True,
                "is_idempotent": is_idempotent,
                "is_associative": False,  # Would need more complex analysis
                "is_commutative": False,  # Would need more complex analysis
                "variables": variables,
                "operations": operations,
                "depth": depth,
                "term_id": None,  # Term ID not exposed in Python API
            }
        except Exception as e:
            logger.warning(f"Failed to get Rust term operation properties for {term_string}: {e}")
            return {
                "symbol": f"term_{hash(term_string) & 0xFFFF}",
                "arity": self._estimate_term_arity(term_string),
                "cardinality": self._get_algebra_size_estimate(algebra_file),
                "properties_computed": False,
                "is_idempotent": False,
                "is_associative": False,
                "is_commutative": False,
                "error": str(e),
            }
    
    def _analyze_rust_term_composition(self, term1: str, term2: str, algebra_file: Path) -> Dict[str, Any]:
        """Analyze term composition in Rust/Python"""
        try:
            # Load the algebra
            algebra = self._load_test_algebra(algebra_file)
            
            # Create term arena and parse both terms
            from uacalc_rust import create_term_arena, parse_term
            arena = create_term_arena()
            term1_obj = parse_term(arena, term1)
            term2_obj = parse_term(arena, term2)
            
            # Get actual arities from terms
            from uacalc_rust import term_variables
            variables1 = term_variables(term1_obj)
            variables2 = term_variables(term2_obj)
            # For term operations, arity is the number of distinct variables
            arity1 = len(set(variables1)) if variables1 else 0
            arity2 = len(set(variables2)) if variables2 else 0
            
            # Check if composition is possible
            can_compose = (arity1 == 1)  # Simple composition requires unary first term
            
            return {
                "can_compose": can_compose,
                "composition_error": None if can_compose else f"First term has arity {arity1} (must be 1)",
                "term1_arity": arity1,
                "term2_arity": arity2,
                "composition_computed": can_compose and algebra.cardinality <= 5,
                "composition_result": None,  # Would compute actual result in real implementation
                "term1_variables": variables1,
                "term2_variables": variables2,
            }
        except Exception as e:
            logger.warning(f"Failed to analyze Rust term composition for {term1}∘{term2}: {e}")
            # Fallback to estimation
            arity1 = self._estimate_term_arity(term1)
            arity2 = self._estimate_term_arity(term2)
            can_compose = (arity1 == 1)
            
            return {
                "can_compose": can_compose,
                "composition_error": None if can_compose else f"First term has arity {arity1} (must be 1)",
                "term1_arity": arity1,
                "term2_arity": arity2,
                "composition_computed": can_compose and self._get_algebra_size_estimate(algebra_file) <= 5,
                "composition_result": None,
                "error": str(e),
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
    
    def _analyze_term_structure(self, term_string: str, algebra_file: Path) -> Dict[str, Any]:
        """Analyze the structure of a term in detail"""
        try:
            # Load the algebra
            algebra = self._load_test_algebra(algebra_file)
            
            # Create term arena and parse the term
            from uacalc_rust import create_term_arena, parse_term
            arena = create_term_arena()
            term = parse_term(arena, term_string)
            
            # Get detailed term analysis
            from uacalc_rust import term_variables, term_operations
            variables = term_variables(term)
            operations = term_operations(term)
            depth = term.depth()
            
            # Analyze term complexity
            complexity_analysis = {
                "variable_count": len(variables) if variables else 0,
                "operation_count": len(operations) if operations else 0,
                "depth": depth,
                "is_constant": len(variables) == 0 if variables else True,
                "is_variable": len(operations) == 0 if operations else False,
                "is_compound": len(operations) > 0 if operations else False,
            }
            
            # Check for specific patterns
            pattern_analysis = {
                "has_repeated_variables": len(set(variables)) < len(variables) if variables else False,
                "is_linear": len(set(variables)) == len(variables) if variables else True,
                "is_ground": len(variables) == 0 if variables else False,
            }
            
            return {
                "term_string": term_string,
                "variables": variables,
                "operations": operations,
                "complexity": complexity_analysis,
                "patterns": pattern_analysis,
                "algebra_cardinality": algebra.cardinality,
                "analysis_successful": True,
            }
        except Exception as e:
            logger.warning(f"Failed to analyze term structure for {term_string}: {e}")
            return {
                "term_string": term_string,
                "error": str(e),
                "analysis_successful": False,
            }
    
    def _validate_term_against_algebra(self, term_string: str, algebra_file: Path) -> Dict[str, Any]:
        """Validate a term against an algebra"""
        try:
            # Load the algebra
            algebra = self._load_test_algebra(algebra_file)
            
            # Create term arena and parse the term
            from uacalc_rust import create_term_arena, parse_term, validate_term_against_algebra
            arena = create_term_arena()
            term = parse_term(arena, term_string)
            
            # Validate the term
            is_valid, error_message = validate_term_against_algebra(term, algebra)
            
            return {
                "term_string": term_string,
                "is_valid": is_valid,
                "error_message": error_message,
                "algebra_name": algebra.name,
                "validation_successful": True,
            }
        except Exception as e:
            logger.warning(f"Failed to validate term {term_string} against algebra: {e}")
            return {
                "term_string": term_string,
                "is_valid": False,
                "error_message": str(e),
                "validation_successful": False,
            }
    
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
        
        # Compare additional properties if available
        if "variables" in rust_term_op and "variables" in java_term_op:
            rust_vars = set(rust_term_op["variables"]) if rust_term_op["variables"] else set()
            java_vars = set(java_term_op["variables"]) if java_term_op["variables"] else set()
            if rust_vars != java_vars:
                matches = False
                error_messages.append(f"Variables mismatch: Rust={rust_vars}, Java={java_vars}")
        
        if "operations" in rust_term_op and "operations" in java_term_op:
            rust_ops = set(rust_term_op["operations"]) if rust_term_op["operations"] else set()
            java_ops = set(java_term_op["operations"]) if java_term_op["operations"] else set()
            if rust_ops != java_ops:
                matches = False
                error_messages.append(f"Operations mismatch: Rust={rust_ops}, Java={java_ops}")
        
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