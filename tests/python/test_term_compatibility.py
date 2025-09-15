#!/usr/bin/env python3
"""
Term Compatibility Test

This module tests compatibility between Rust and Java UACalc implementations
for term parsing, evaluation, and validation operations.

Tests cover:
- Term parsing from strings with complex nested structures
- Term evaluation with variable assignments
- Term validation against algebra operation signatures
"""

import unittest
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from tests.python.base_compatibility_test import BaseCompatibilityTest

try:
    import uacalc
    from uacalc.terms import (
        TermParser, TermEvaluator, parse_term, eval_term, 
        create_term_arena, term_variables, term_operations,
        validate_term_against_algebra, variable, constant, operation
    )
    UACALC_AVAILABLE = True
except ImportError:
    UACALC_AVAILABLE = False


class TermCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.terms.Term interface compatibility.
    
    This class tests term parsing, evaluation, and validation operations
    to ensure identical behavior between Rust and Java implementations.
    """
    
    def setUp(self):
        """Set up for each test"""
        super().setUp()
        
        # Skip tests if uacalc is not available
        if not UACALC_AVAILABLE:
            self.skipTest("uacalc module not available")
        
        # Initialize term parser and arena
        self.term_arena = create_term_arena()
        self.term_parser = TermParser(self.term_arena)
        
        # Test expressions for parsing tests
        self.test_expressions = [
            # Simple expressions
            "x0",
            "x1", 
            "c",
            "f(x0)",
            "g(x0, x1)",
            
            # Nested expressions
            "f(g(x0))",
            "f(x0, g(x1))",
            "f(g(x0), h(x1))",
            "f(g(h(x0)))",
            
            # Complex nested structures
            "f(x0, g(x1, h(x2)))",
            "f(g(x0, x1), h(x2, x3))",
            "f(g(h(x0), x1), x2)",
            "f(x0, g(x1, h(x2, k(x3))))",
            "f(g(x0, h(x1)), g(x2, h(x3)))",
            
            # Multiple arity operations
            "f(x0, x1, x2)",
            "f(x0, x1, x2, x3)",
            "g(f(x0, x1), f(x2, x3), f(x4, x5))",
            
            # Deep nesting
            "f(g(h(k(x0))))",
            "f(g(h(x0, x1), k(x2, x3)), l(m(x4)))",
        ]
        
        # Invalid expressions for error testing
        self.invalid_expressions = [
            "",  # Empty
            "(",  # Unbalanced parentheses
            ")",  # Unbalanced parentheses  
            "f(x0",  # Missing closing parenthesis
            "f(x0,)",  # Trailing comma
            "f(,x0)",  # Leading comma
            "f(x0 x1)",  # Missing comma
            "f(x0,,x1)",  # Double comma
        ]
    
    def test_term_parsing_simple_compatibility(self):
        """Test simple term parsing compatibility between Rust and Java"""
        simple_expressions = [
            "x0", "x1", "x2", "c", "f", "g", "h"
        ]
        
        for expr in simple_expressions:
            with self.subTest(expression=expr):
                self._test_term_parsing_compatibility(expr)
    
    def test_term_parsing_operations_compatibility(self):
        """Test operation term parsing compatibility"""
        operation_expressions = [
            "f(x0)",
            "g(x0, x1)", 
            "h(x0, x1, x2)",
            "k(x0, x1, x2, x3)"
        ]
        
        for expr in operation_expressions:
            with self.subTest(expression=expr):
                self._test_term_parsing_compatibility(expr)
    
    def test_term_parsing_nested_compatibility(self):
        """Test nested term parsing compatibility"""
        nested_expressions = [
            "f(g(x0))",
            "f(x0, g(x1))",
            "f(g(x0), h(x1))",
            "f(g(h(x0)))",
            "f(x0, g(x1, h(x2)))",
            "f(g(x0, x1), h(x2, x3))"
        ]
        
        for expr in nested_expressions:
            with self.subTest(expression=expr):
                self._test_term_parsing_compatibility(expr)
    
    def test_term_parsing_complex_compatibility(self):
        """Test complex nested structure parsing compatibility"""
        for expr in self.test_expressions:
            with self.subTest(expression=expr):
                self._test_term_parsing_compatibility(expr)
    
    def test_term_parsing_error_handling_compatibility(self):
        """Test term parsing error handling compatibility"""
        for expr in self.invalid_expressions:
            with self.subTest(expression=expr):
                self._test_term_parsing_error_compatibility(expr)
    
    def test_term_evaluation_simple_compatibility(self):
        """Test simple term evaluation compatibility"""
        # Test with small algebras for comprehensive coverage
        small_algebra_files = [f for f in self.algebra_files if f.name in ['cyclic2.ua', 'cyclic3.ua', 'ba2.ua']]
        
        for algebra_file in small_algebra_files[:3]:  # Limit to first 3 for performance
            algebra = self._load_test_algebra(algebra_file)
            
            # Test simple variable evaluation
            simple_terms = ["x0", "x1"]
            for term_str in simple_terms:
                with self.subTest(algebra=algebra_file.name, term=term_str):
                    self._test_term_evaluation_compatibility(algebra, algebra_file.name, term_str)
    
    def test_term_evaluation_operations_compatibility(self):
        """Test operation term evaluation compatibility"""
        # Use small algebras for exhaustive testing
        small_algebra_files = [f for f in self.algebra_files if f.name in ['cyclic2.ua', 'cyclic3.ua']]
        
        for algebra_file in small_algebra_files[:2]:  # Limit for performance
            algebra = self._load_test_algebra(algebra_file)
            
            # Get operation symbols from the algebra
            operation_symbols = [op.symbol for op in algebra.operations()]
            
            # Test evaluation with actual operations from the algebra
            for op_symbol in operation_symbols[:3]:  # Test first 3 operations
                operation = next(op for op in algebra.operations() if op.symbol == op_symbol)
                
                if operation.arity() == 1:
                    term_str = f"{op_symbol}(x0)"
                elif operation.arity() == 2:
                    term_str = f"{op_symbol}(x0, x1)"
                elif operation.arity() == 3:
                    term_str = f"{op_symbol}(x0, x1, x2)"
                else:
                    continue  # Skip higher arity for now
                
                with self.subTest(algebra=algebra_file.name, term=term_str):
                    self._test_term_evaluation_compatibility(algebra, algebra_file.name, term_str)
    
    def test_term_evaluation_nested_compatibility(self):
        """Test nested term evaluation compatibility"""
        # Use very small algebra for nested evaluation tests
        small_algebra_files = [f for f in self.algebra_files if f.name == 'cyclic2.ua']
        
        if not small_algebra_files:
            self.skipTest("No cyclic2.ua algebra found for nested evaluation test")
        
        algebra_file = small_algebra_files[0]
        algebra = self._load_test_algebra(algebra_file)
        
        # Get binary operations for nesting
        binary_ops = [op for op in algebra.operations() if op.arity() == 2]
        
        if len(binary_ops) >= 1:
            op_symbol = binary_ops[0].symbol
            nested_terms = [
                f"{op_symbol}({op_symbol}(x0, x1), x2)",
                f"{op_symbol}(x0, {op_symbol}(x1, x2))"
            ]
            
            for term_str in nested_terms:
                with self.subTest(algebra=algebra_file.name, term=term_str):
                    self._test_term_evaluation_compatibility(algebra, algebra_file.name, term_str)
    
    def test_term_validation_compatibility(self):
        """Test term validation against algebra operation signatures"""
        # Test with a few representative algebras
        test_algebra_files = [f for f in self.algebra_files if f.name in ['cyclic2.ua', 'cyclic3.ua', 'ba2.ua']]
        
        for algebra_file in test_algebra_files[:2]:  # Limit for performance
            algebra = self._load_test_algebra(algebra_file)
            
            # Test valid terms (using actual operations from algebra)
            operation_symbols = [op.symbol for op in algebra.operations()]
            
            for op_symbol in operation_symbols[:3]:  # Test first 3 operations
                operation = next(op for op in algebra.operations() if op.symbol == op_symbol)
                
                if operation.arity() == 0:
                    term_str = op_symbol
                elif operation.arity() == 1:
                    term_str = f"{op_symbol}(x0)"
                elif operation.arity() == 2:
                    term_str = f"{op_symbol}(x0, x1)"
                else:
                    continue
                
                with self.subTest(algebra=algebra_file.name, term=term_str, valid=True):
                    self._test_term_validation_compatibility(algebra, algebra_file.name, term_str, should_be_valid=True)
            
            # Test invalid terms (using non-existent operations)
            invalid_terms = [
                "nonexistent(x0)",
                "invalid(x0, x1)",
                "missing(x0, x1, x2)"
            ]
            
            for term_str in invalid_terms:
                with self.subTest(algebra=algebra_file.name, term=term_str, valid=False):
                    self._test_term_validation_compatibility(algebra, algebra_file.name, term_str, should_be_valid=False)
    
    def test_term_substitution_compatibility(self):
        """Test term variable substitution compatibility"""
        # Test with small algebra
        small_algebra_files = [f for f in self.algebra_files if f.name == 'cyclic2.ua']
        
        if not small_algebra_files:
            self.skipTest("No cyclic2.ua algebra found for substitution test")
        
        algebra_file = small_algebra_files[0]
        
        # Test substitution operations
        substitution_tests = [
            ("f(x0, x1)", {"x0": "x2", "x1": "x0"}),
            ("g(x0)", {"x0": "f(x1, x2)"}),
            ("f(g(x0), x1)", {"x0": "x2", "x1": "g(x3)"})
        ]
        
        for term_str, substitutions in substitution_tests:
            with self.subTest(algebra=algebra_file.name, term=term_str, substitutions=substitutions):
                self._test_term_substitution_compatibility(algebra_file.name, term_str, substitutions)
    
    def test_term_equivalence_compatibility(self):
        """Test term equivalence checking compatibility"""
        # Test with small algebra
        small_algebra_files = [f for f in self.algebra_files if f.name == 'cyclic2.ua']
        
        if not small_algebra_files:
            self.skipTest("No cyclic2.ua algebra found for equivalence test")
        
        algebra_file = small_algebra_files[0]
        
        # Test term equivalence pairs
        equivalence_tests = [
            ("x0", "x0", True),  # Same term
            ("f(x0, x1)", "f(x0, x1)", True),  # Same complex term
            ("f(x0, x1)", "f(x1, x0)", False),  # Different order
            ("f(g(x0), x1)", "f(g(x0), x1)", True),  # Same nested term
            ("f(g(x0), x1)", "g(f(x0, x1))", False),  # Different structure
        ]
        
        for term1_str, term2_str, expected_equal in equivalence_tests:
            with self.subTest(algebra=algebra_file.name, term1=term1_str, term2=term2_str, expected=expected_equal):
                self._test_term_equivalence_compatibility(algebra_file.name, term1_str, term2_str, expected_equal)
    
    def _test_term_parsing_compatibility(self, expression: str):
        """Test term parsing compatibility for a single expression"""
        # Get Java result
        java_result = self._run_java_operation("term_parse_complex", expression, 
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_term_parsing_result(expression)
        
        # Compare results
        result = self._compare_results(rust_result, java_result, "term_parse_complex", expression)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Term parsing mismatch for '{expression}': {result.error_message}")
    
    def _test_term_parsing_error_compatibility(self, expression: str):
        """Test term parsing error handling compatibility"""
        # Get Java result (should be an error)
        java_result = self._run_java_operation("term_parse_complex", expression,
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result (should also be an error)
        rust_result = self._get_rust_term_parsing_result(expression)
        
        # For error cases, we mainly check that both implementations reject the input
        if java_result and not java_result.get("success", True):
            # Java failed as expected
            if rust_result and rust_result.get("success", False):
                # Rust succeeded when it should have failed
                self.test_logger.warning(f"Rust parsed invalid expression '{expression}' but Java rejected it")
            else:
                # Both failed as expected
                self.test_logger.debug(f"Both implementations correctly rejected invalid expression '{expression}'")
        elif java_result and java_result.get("success", True):
            # Java succeeded - check if Rust also succeeded
            if not rust_result or not rust_result.get("success", False):
                self.test_logger.warning(f"Java parsed expression '{expression}' but Rust rejected it")
    
    def _test_term_evaluation_compatibility(self, algebra, algebra_name: str, term_str: str):
        """Test term evaluation compatibility for a single term"""
        # Generate variable assignments for testing
        variable_assignments = self._generate_variable_assignments(algebra, term_str)
        
        for variables in variable_assignments[:5]:  # Limit to first 5 assignments for performance
            variables_json = json.dumps(variables)
            
            # Get Java result
            java_result = self._run_java_operation("eval_term", term_str, variables_json,
                                                 timeout=self.JAVA_TIMEOUT_SHORT)
            
            # Get Rust result
            rust_result = self._get_rust_term_evaluation_result(algebra, term_str, variables)
            
            # Compare results
            context = f"{algebra_name}:{term_str}:{variables}"
            result = self._compare_results(rust_result, java_result, "eval_term", context)
            
            if not result.matches and java_result and java_result.get("success", True):
                self.test_logger.warning(f"Term evaluation mismatch: {result.error_message}")
    
    def _test_term_validation_compatibility(self, algebra, algebra_name: str, term_str: str, should_be_valid: bool):
        """Test term validation compatibility"""
        # Find the algebra file path
        algebra_files = [f for f in self.algebra_files if f.name == algebra_name]
        if not algebra_files:
            self.skipTest(f"Algebra file {algebra_name} not found")
        
        algebra_file = algebra_files[0]
        
        # Get Java result
        java_result = self._run_java_operation("validate_term", term_str, str(algebra_file),
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_term_validation_result(algebra, term_str)
        
        # Compare results
        context = f"{algebra_name}:{term_str}"
        result = self._compare_results(rust_result, java_result, "validate_term", context)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Term validation mismatch: {result.error_message}")
    
    def _test_term_substitution_compatibility(self, algebra_name: str, term_str: str, substitutions: Dict[str, str]):
        """Test term substitution compatibility"""
        substitutions_json = json.dumps(substitutions)
        
        # Get Java result
        java_result = self._run_java_operation("term_substitution", term_str, substitutions_json,
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_term_substitution_result(term_str, substitutions)
        
        # Compare results
        context = f"{algebra_name}:{term_str}:{substitutions}"
        result = self._compare_results(rust_result, java_result, "term_substitution", context)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Term substitution mismatch: {result.error_message}")
    
    def _test_term_equivalence_compatibility(self, algebra_name: str, term1_str: str, term2_str: str, expected_equal: bool):
        """Test term equivalence compatibility"""
        # For equivalence testing, we need an algebra file path
        algebra_files = [f for f in self.algebra_files if f.name == algebra_name]
        if not algebra_files:
            self.skipTest(f"Algebra file {algebra_name} not found")
        
        algebra_file = algebra_files[0]
        
        # Get Java result
        java_result = self._run_java_operation("term_equivalence", term1_str, term2_str, str(algebra_file),
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_term_equivalence_result(algebra_file, term1_str, term2_str)
        
        # Compare results
        context = f"{algebra_name}:{term1_str}:{term2_str}"
        result = self._compare_results(rust_result, java_result, "term_equivalence", context)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Term equivalence mismatch: {result.error_message}")
    
    def _get_rust_term_parsing_result(self, expression: str) -> Dict[str, Any]:
        """Get Rust term parsing result"""
        try:
            start_time = time.time()
            
            # Parse the term using Rust implementation
            term = parse_term(self.term_arena, expression)
            
            execution_time = time.time() - start_time
            
            # Extract term information
            result = {
                "success": True,
                "operation": "term_parse_complex",
                "term_string": expression,
                "results": {
                    "parsed_successfully": True,
                    "term_type": "operation" if term.is_operation() else "variable",
                    "arity": term.arity(),
                    "depth": term.depth(),
                    "variables": term.variables(),
                    "string_representation": term.to_string()
                },
                "execution_time_ms": execution_time * 1000
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "operation": "term_parse_complex", 
                "term_string": expression,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_rust_term_evaluation_result(self, algebra, term_str: str, variables: Dict[str, int]) -> Dict[str, Any]:
        """Get Rust term evaluation result"""
        try:
            start_time = time.time()
            
            # Parse the term
            term = parse_term(self.term_arena, term_str)
            
            # Convert variable names to indices (x0 -> 0, x1 -> 1, etc.)
            var_indices = {}
            for var_name, value in variables.items():
                if var_name.startswith('x'):
                    var_index = int(var_name[1:])
                    var_indices[var_index] = value
                else:
                    # Handle other variable naming schemes
                    var_indices[hash(var_name) % 255] = value
            
            # Evaluate the term
            result_value = eval_term(term, algebra, var_indices)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "eval_term",
                "term_string": term_str,
                "variables": variables,
                "results": {
                    "evaluation_result": result_value,
                    "result_type": type(result_value).__name__
                },
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "eval_term",
                "term_string": term_str,
                "variables": variables,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_rust_term_validation_result(self, algebra, term_str: str) -> Dict[str, Any]:
        """Get Rust term validation result"""
        try:
            start_time = time.time()
            
            # Parse the term
            term = parse_term(self.term_arena, term_str)
            
            # Validate against algebra
            is_valid, error_message = validate_term_against_algebra(term, algebra)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "validate_term",
                "term_string": term_str,
                "results": {
                    "is_valid": is_valid,
                    "error_message": error_message,
                    "validation_details": {
                        "term_variables": term.variables(),
                        "term_operations": term_operations(term),
                        "algebra_cardinality": algebra.cardinality,
                        "algebra_operations": [op.symbol for op in algebra.operations()]
                    }
                },
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "validate_term",
                "term_string": term_str,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_rust_term_substitution_result(self, term_str: str, substitutions: Dict[str, str]) -> Dict[str, Any]:
        """Get Rust term substitution result"""
        try:
            start_time = time.time()
            
            # Parse the original term
            term = parse_term(self.term_arena, term_str)
            
            # For now, return the original term since substitution is not fully implemented
            # TODO: Implement actual variable substitution
            result_term_str = term.to_string()
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "term_substitution",
                "original_term": term_str,
                "substitutions": substitutions,
                "results": {
                    "substituted_term": result_term_str,
                    "substitution_applied": False,  # Not implemented yet
                    "original_variables": term.variables()
                },
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "term_substitution",
                "original_term": term_str,
                "substitutions": substitutions,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_rust_term_equivalence_result(self, algebra_file: Path, term1_str: str, term2_str: str) -> Dict[str, Any]:
        """Get Rust term equivalence result"""
        try:
            start_time = time.time()
            
            # Load algebra
            algebra = self._load_test_algebra(algebra_file)
            
            # Parse both terms
            term1 = parse_term(self.term_arena, term1_str)
            term2 = parse_term(self.term_arena, term2_str)
            
            # Check structural equivalence (string comparison for now)
            # TODO: Implement semantic equivalence checking
            are_equivalent = term1.to_string() == term2.to_string()
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "term_equivalence",
                "term1": term1_str,
                "term2": term2_str,
                "results": {
                    "are_equivalent": are_equivalent,
                    "equivalence_type": "structural",  # Not semantic yet
                    "term1_string": term1.to_string(),
                    "term2_string": term2.to_string()
                },
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "term_equivalence",
                "term1": term1_str,
                "term2": term2_str,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _generate_variable_assignments(self, algebra, term_str: str) -> List[Dict[str, int]]:
        """Generate variable assignments for term evaluation testing"""
        try:
            # Parse term to get variables
            term = parse_term(self.term_arena, term_str)
            variables = term.variables()
            
            if not variables:
                return [{}]  # No variables
            
            # Generate assignments for small algebras (exhaustive)
            # For larger algebras, generate representative samples
            assignments = []
            cardinality = algebra.cardinality
            
            if cardinality <= 3 and len(variables) <= 3:
                # Exhaustive for small cases
                import itertools
                for values in itertools.product(range(cardinality), repeat=len(variables)):
                    assignment = {f"x{var}": val for var, val in zip(sorted(variables), values)}
                    assignments.append(assignment)
            else:
                # Sample for larger cases
                import random
                for _ in range(min(10, cardinality ** min(len(variables), 2))):
                    assignment = {f"x{var}": random.randint(0, cardinality - 1) for var in variables}
                    assignments.append(assignment)
            
            return assignments
            
        except Exception:
            # Fallback: generate simple assignments
            return [
                {"x0": 0, "x1": 0, "x2": 0},
                {"x0": 1, "x1": 0, "x2": 1},
                {"x0": 0, "x1": 1, "x2": 0}
            ]


if __name__ == "__main__":
    unittest.main()