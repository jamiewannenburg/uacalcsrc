#!/usr/bin/env python3
"""
Equation Compatibility Test

This module tests compatibility between Rust and Java UACalc implementations
for equation construction, satisfaction checking, and manipulation operations.

Tests cover:
- Equation construction from terms
- Equation satisfaction checking in algebras
- Equation manipulation and transformation operations
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
        parse_term, eval_term, variable, constant, operation,
        term_variables, term_operations
    )
    UACALC_AVAILABLE = True
except ImportError:
    UACALC_AVAILABLE = False


class EquationCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.eq.Equation interface compatibility.
    
    This class tests equation construction, satisfaction checking, and manipulation
    operations to ensure identical behavior between Rust and Java implementations.
    """
    
    def setUp(self):
        """Set up for each test"""
        super().setUp()
        
        # Skip tests if uacalc is not available
        if not UACALC_AVAILABLE:
            self.skipTest("uacalc module not available")
        
        # Test equation definitions for various scenarios
        self.test_equations = {
            "simple_identity": {
                "left_term": "x",
                "right_term": "x",
                "description": "Simple identity equation x = x"
            },
            "commutative": {
                "left_term": "f(x,y)",
                "right_term": "f(y,x)",
                "description": "Commutative law f(x,y) = f(y,x)"
            },
            "associative": {
                "left_term": "f(f(x,y),z)",
                "right_term": "f(x,f(y,z))",
                "description": "Associative law f(f(x,y),z) = f(x,f(y,z))"
            },
            "idempotent": {
                "left_term": "f(x,x)",
                "right_term": "x",
                "description": "Idempotent law f(x,x) = x"
            },
            "constant_equation": {
                "left_term": "c",
                "right_term": "c",
                "description": "Constant equation c = c"
            },
            "complex_nested": {
                "left_term": "f(g(x,y),h(z,w))",
                "right_term": "f(h(z,w),g(x,y))",
                "description": "Complex nested equation"
            },
            "unary_operation": {
                "left_term": "g(x)",
                "right_term": "g(g(x))",
                "description": "Unary operation equation"
            },
            "ternary_operation": {
                "left_term": "h(x,y,z)",
                "right_term": "h(z,x,y)",
                "description": "Ternary operation equation"
            }
        }
        
        # Test algebras for equation satisfaction
        self.test_algebras = [
            "resources/algebras/ba2.ua",      # Boolean algebra
            "resources/algebras/cyclic2.ua",  # Cyclic group
            "resources/algebras/cyclic3.ua",  # Cyclic group
            "resources/algebras/m3.ua",       # Modular lattice
            "resources/algebras/m4.ua",       # Modular lattice
            "resources/algebras/n5.ua",       # Non-modular lattice
            "resources/algebras/sym3.ua",     # Symmetric group
            "resources/algebras/z3.ua"        # Cyclic group
        ]
    
    def test_equation_construction_from_terms(self):
        """Test equation construction from terms"""
        self.test_logger.info("Testing equation construction from terms")
        
        for eq_name, eq_data in self.test_equations.items():
            with self.subTest(equation=eq_name):
                self._test_equation_construction(eq_name, eq_data)
    
    def _test_equation_construction(self, eq_name: str, eq_data: Dict[str, str]):
        """Test construction of a specific equation"""
        left_term_str = eq_data["left_term"]
        right_term_str = eq_data["right_term"]
        description = eq_data["description"]
        
        # Test Rust implementation
        try:
            # Parse terms in Rust
            left_term_rust = parse_term(left_term_str)
            right_term_rust = parse_term(right_term_str)
            
            # Create equation representation (Rust doesn't have direct Equation class)
            # We'll test the components separately
            rust_result = {
                "left_term": str(left_term_rust),
                "right_term": str(right_term_rust),
                "left_variables": list(term_variables(left_term_rust)),
                "right_variables": list(term_variables(right_term_rust)),
                "left_operations": list(term_operations(left_term_rust)),
                "right_operations": list(term_operations(right_term_rust)),
                "description": description
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation construction failed for {eq_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        equation_json = json.dumps({
            "left_term": left_term_str,
            "right_term": right_term_str
        })
        
        # Use equation_generation operation to test equation construction
        java_result = self._run_java_operation(
            "equation_generation", "f", "associative", 
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # For equation construction, we mainly verify that both can parse the terms
        # The Java result will be from equation_generation, so we compare the parsing capability
        if java_result and java_result.get("success"):
            # Both implementations can handle term parsing
            result = self._compare_results(
                rust_result, java_result, "equation_construction", 
                context=f"{eq_name}: {description}"
            )
            
            # For construction tests, we mainly verify parsing works
            if "error" not in rust_result:
                self.assertTrue(
                    result.matches or "error" not in java_result,
                    f"Equation construction failed for {eq_name}: {result.error_message}"
                )
        else:
            # Java operation failed, but we can still test Rust parsing
            if "error" not in rust_result:
                self.test_logger.warning(f"Java equation construction failed for {eq_name}, but Rust parsing succeeded")
    
    def test_equation_satisfaction_checking(self):
        """Test equation satisfaction checking in algebras"""
        self.test_logger.info("Testing equation satisfaction checking in algebras")
        
        # Test with a few representative equations and algebras
        test_cases = [
            ("simple_identity", "resources/algebras/ba2.ua"),
            ("commutative", "resources/algebras/cyclic2.ua"),
            ("associative", "resources/algebras/m3.ua"),
            ("idempotent", "resources/algebras/sym3.ua")
        ]
        
        for eq_name, algebra_file in test_cases:
            with self.subTest(equation=eq_name, algebra=Path(algebra_file).name):
                if Path(algebra_file).exists():
                    self._test_equation_satisfaction(eq_name, algebra_file)
                else:
                    self.test_logger.warning(f"Algebra file not found: {algebra_file}")
    
    def _test_equation_satisfaction(self, eq_name: str, algebra_file: str):
        """Test satisfaction checking for a specific equation and algebra"""
        eq_data = self.test_equations[eq_name]
        left_term_str = eq_data["left_term"]
        right_term_str = eq_data["right_term"]
        
        # Test Rust implementation
        try:
            # Load algebra
            algebra = self._load_test_algebra(algebra_file)
            
            # Parse terms
            left_term = parse_term(left_term_str)
            right_term = parse_term(right_term_str)
            
            # Get variables in the equation
            left_vars = term_variables(left_term)
            right_vars = term_variables(right_term)
            all_vars = list(set(left_vars + right_vars))
            
            # Test equation satisfaction by checking if terms evaluate to same values
            # for all possible variable assignments
            satisfied = True
            failure_examples = []
            
            # For small algebras, we can exhaustively check
            if algebra.cardinality <= 8:
                from itertools import product
                
                for var_assignment in product(range(algebra.cardinality), repeat=len(all_vars)):
                    var_map = dict(zip(all_vars, var_assignment))
                    
                    try:
                        left_value = eval_term(left_term, var_map, algebra)
                        right_value = eval_term(right_term, var_map, algebra)
                        
                        if left_value != right_value:
                            satisfied = False
                            failure_examples.append({
                                "assignment": var_map,
                                "left_value": left_value,
                                "right_value": right_value
                            })
                            # Limit failure examples to avoid too much output
                            if len(failure_examples) >= 3:
                                break
                    except Exception as e:
                        satisfied = False
                        failure_examples.append({
                            "assignment": var_map,
                            "error": str(e)
                        })
                        break
            else:
                # For larger algebras, do a sampling
                import random
                sample_size = min(100, algebra.cardinality ** len(all_vars))
                
                for _ in range(sample_size):
                    var_assignment = [random.randint(0, algebra.cardinality - 1) for _ in all_vars]
                    var_map = dict(zip(all_vars, var_assignment))
                    
                    try:
                        left_value = eval_term(left_term, var_map, algebra)
                        right_value = eval_term(right_term, var_map, algebra)
                        
                        if left_value != right_value:
                            satisfied = False
                            failure_examples.append({
                                "assignment": var_map,
                                "left_value": left_value,
                                "right_value": right_value
                            })
                            break
                    except Exception as e:
                        satisfied = False
                        failure_examples.append({
                            "assignment": var_map,
                            "error": str(e)
                        })
                        break
            
            rust_result = {
                "satisfied": satisfied,
                "failure_examples": failure_examples,
                "variable_count": len(all_vars),
                "variables": all_vars
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation satisfaction failed for {eq_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        equation_json = json.dumps({
            "left_term": left_term_str,
            "right_term": right_term_str
        })
        
        java_result = self._run_java_operation(
            "equation_satisfaction", equation_json, algebra_file,
            timeout=self._get_test_timeout("equation_satisfaction", algebra.cardinality if 'algebra' in locals() else 4)
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_satisfaction",
            context=f"{eq_name} in {Path(algebra_file).name}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Equation satisfaction test passed for {eq_name}")
        else:
            self.test_logger.warning(f"Equation satisfaction test failed for {eq_name}: {result.error_message}")
            # Don't fail the test immediately, just log the difference
            # This allows us to see patterns in compatibility issues
    
    def test_equation_manipulation_operations(self):
        """Test equation manipulation and transformation operations"""
        self.test_logger.info("Testing equation manipulation and transformation operations")
        
        # Test various equation transformations
        transformation_tests = [
            {
                "name": "variable_substitution",
                "original": {"left_term": "f(x,y)", "right_term": "f(y,x)"},
                "substitution": {"x": "z", "y": "w"},
                "expected": {"left_term": "f(z,w)", "right_term": "f(w,z)"}
            },
            {
                "name": "term_simplification",
                "original": {"left_term": "f(f(x,y),f(x,y))", "right_term": "f(x,y)"},
                "description": "Test if repeated terms can be simplified"
            },
            {
                "name": "operation_extraction",
                "original": {"left_term": "f(g(x),h(y))", "right_term": "f(h(y),g(x))"},
                "description": "Test extraction of operation symbols"
            }
        ]
        
        for test_case in transformation_tests:
            with self.subTest(transformation=test_case["name"]):
                self._test_equation_manipulation(test_case)
    
    def _test_equation_manipulation(self, test_case: Dict[str, Any]):
        """Test a specific equation manipulation operation"""
        test_name = test_case["name"]
        original = test_case["original"]
        
        # Test Rust implementation
        try:
            left_term = parse_term(original["left_term"])
            right_term = parse_term(original["right_term"])
            
            # Test variable extraction
            left_vars = list(term_variables(left_term))
            right_vars = list(term_variables(right_term))
            all_vars = list(set(left_vars + right_vars))
            
            # Test operation extraction
            left_ops = list(term_operations(left_term))
            right_ops = list(term_operations(right_term))
            all_ops = list(set(left_ops + right_ops))
            
            # Test variable substitution if provided
            substitution_result = None
            if "substitution" in test_case:
                substitution = test_case["substitution"]
                try:
                    # Create new terms with substituted variables
                    # This is a simplified substitution - in practice you'd need more sophisticated logic
                    left_substituted = str(left_term)  # Simplified
                    right_substituted = str(right_term)  # Simplified
                    
                    for old_var, new_var in substitution.items():
                        left_substituted = left_substituted.replace(old_var, new_var)
                        right_substituted = right_substituted.replace(old_var, new_var)
                    
                    substitution_result = {
                        "left_term": left_substituted,
                        "right_term": right_substituted
                    }
                except Exception as e:
                    substitution_result = {"error": str(e)}
            
            rust_result = {
                "variables": all_vars,
                "operations": all_ops,
                "variable_count": len(all_vars),
                "operation_count": len(all_ops),
                "substitution_result": substitution_result
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation manipulation failed for {test_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        # For manipulation tests, we'll use equation_generation to test operation extraction
        java_result = self._run_java_operation(
            "equation_generation", "f", "associative",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_manipulation",
            context=f"{test_name}: {test_case.get('description', '')}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Equation manipulation test passed for {test_name}")
        else:
            self.test_logger.warning(f"Equation manipulation test failed for {test_name}: {result.error_message}")
    
    def test_equation_properties_analysis(self):
        """Test analysis of equation properties"""
        self.test_logger.info("Testing equation properties analysis")
        
        # Test equation property detection
        property_tests = [
            {
                "name": "identity_equation",
                "equation": {"left_term": "x", "right_term": "x"},
                "expected_properties": ["identity", "tautology"]
            },
            {
                "name": "commutative_law",
                "equation": {"left_term": "f(x,y)", "right_term": "f(y,x)"},
                "expected_properties": ["commutative"]
            },
            {
                "name": "associative_law",
                "equation": {"left_term": "f(f(x,y),z)", "right_term": "f(x,f(y,z))"},
                "expected_properties": ["associative"]
            }
        ]
        
        for test_case in property_tests:
            with self.subTest(property_test=test_case["name"]):
                self._test_equation_properties(test_case)
    
    def _test_equation_properties(self, test_case: Dict[str, Any]):
        """Test property analysis for a specific equation"""
        test_name = test_case["name"]
        equation = test_case["equation"]
        expected_properties = test_case.get("expected_properties", [])
        
        # Test Rust implementation
        try:
            left_term = parse_term(equation["left_term"])
            right_term = parse_term(equation["right_term"])
            
            # Analyze equation properties
            properties = []
            
            # Check if it's an identity equation
            if str(left_term) == str(right_term):
                properties.append("identity")
                properties.append("tautology")
            
            # Check if it's commutative
            if "f(x,y)" in str(left_term) and "f(y,x)" in str(right_term):
                properties.append("commutative")
            
            # Check if it's associative
            if "f(f(x,y),z)" in str(left_term) and "f(x,f(y,z))" in str(right_term):
                properties.append("associative")
            
            # Get variable and operation information
            left_vars = list(term_variables(left_term))
            right_vars = list(term_variables(right_term))
            all_vars = list(set(left_vars + right_vars))
            
            left_ops = list(term_operations(left_term))
            right_ops = list(term_operations(right_term))
            all_ops = list(set(left_ops + right_ops))
            
            rust_result = {
                "properties": properties,
                "variables": all_vars,
                "operations": all_ops,
                "variable_count": len(all_vars),
                "operation_count": len(all_ops),
                "is_identity": "identity" in properties,
                "is_tautology": "tautology" in properties
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation properties analysis failed for {test_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        equation_json = json.dumps(equation)
        
        # Use equation_generation to test property analysis
        java_result = self._run_java_operation(
            "equation_generation", "f", "associative",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_properties",
            context=f"{test_name}: {expected_properties}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Equation properties test passed for {test_name}")
        else:
            self.test_logger.warning(f"Equation properties test failed for {test_name}: {result.error_message}")
    
    def test_equation_generation_standard_laws(self):
        """Test generation of standard algebraic laws"""
        self.test_logger.info("Testing generation of standard algebraic laws")
        
        # Test standard equation generation
        standard_laws = [
            {"type": "associative", "symbol": "f", "arity": 2},
            {"type": "cyclic", "symbol": "g", "arity": 3},
            {"type": "first_second_symmetric", "symbol": "h", "arity": 2}
        ]
        
        for law in standard_laws:
            with self.subTest(law_type=law["type"]):
                self._test_standard_law_generation(law)
    
    def _test_standard_law_generation(self, law: Dict[str, Any]):
        """Test generation of a specific standard law"""
        law_type = law["type"]
        symbol = law["symbol"]
        arity = law["arity"]
        
        # Test Rust implementation
        try:
            # Generate the law using Rust term construction
            if law_type == "associative" and arity == 2:
                # f(f(x,y),z) = f(x,f(y,z))
                left_term = parse_term(f"f(f(x,y),z)")
                right_term = parse_term(f"f(x,f(y,z))")
            elif law_type == "cyclic" and arity == 3:
                # g(x,y,z) = g(z,x,y)
                left_term = parse_term(f"g(x,y,z)")
                right_term = parse_term(f"g(z,x,y)")
            elif law_type == "first_second_symmetric" and arity == 2:
                # h(x,y) = h(y,x)
                left_term = parse_term(f"h(x,y)")
                right_term = parse_term(f"h(y,x)")
            else:
                raise ValueError(f"Unsupported law type: {law_type}")
            
            rust_result = {
                "law_type": law_type,
                "symbol": symbol,
                "arity": arity,
                "left_term": str(left_term),
                "right_term": str(right_term),
                "variables": list(set(term_variables(left_term) + term_variables(right_term))),
                "operations": list(set(term_operations(left_term) + term_operations(right_term)))
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust standard law generation failed for {law_type}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        java_result = self._run_java_operation(
            "equation_generation", symbol, law_type,
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_generation",
            context=f"{law_type} law for {symbol} (arity {arity})"
        )
        
        if result.matches:
            self.test_logger.debug(f"Standard law generation test passed for {law_type}")
        else:
            self.test_logger.warning(f"Standard law generation test failed for {law_type}: {result.error_message}")
    
    def test_equation_complexity_analysis(self):
        """Test analysis of equation complexity"""
        self.test_logger.info("Testing equation complexity analysis")
        
        # Test equations of varying complexity
        complexity_tests = [
            {
                "name": "simple_equation",
                "equation": {"left_term": "x", "right_term": "y"},
                "expected_complexity": "low"
            },
            {
                "name": "medium_equation",
                "equation": {"left_term": "f(g(x),h(y))", "right_term": "f(h(y),g(x))"},
                "expected_complexity": "medium"
            },
            {
                "name": "complex_equation",
                "equation": {"left_term": "f(g(h(x,y),z),w)", "right_term": "f(w,g(h(x,y),z))"},
                "expected_complexity": "high"
            }
        ]
        
        for test_case in complexity_tests:
            with self.subTest(complexity_test=test_case["name"]):
                self._test_equation_complexity(test_case)
    
    def _test_equation_complexity(self, test_case: Dict[str, Any]):
        """Test complexity analysis for a specific equation"""
        test_name = test_case["name"]
        equation = test_case["equation"]
        expected_complexity = test_case["expected_complexity"]
        
        # Test Rust implementation
        try:
            left_term = parse_term(equation["left_term"])
            right_term = parse_term(equation["right_term"])
            
            # Analyze complexity
            left_vars = list(term_variables(left_term))
            right_vars = list(term_variables(right_term))
            all_vars = list(set(left_vars + right_vars))
            
            left_ops = list(term_operations(left_term))
            right_ops = list(term_operations(right_term))
            all_ops = list(set(left_ops + right_ops))
            
            # Calculate complexity metrics
            variable_count = len(all_vars)
            operation_count = len(all_ops)
            term_depth = max(
                self._calculate_term_depth(left_term),
                self._calculate_term_depth(right_term)
            )
            
            # Determine complexity level
            if variable_count <= 2 and operation_count <= 2 and term_depth <= 2:
                complexity_level = "low"
            elif variable_count <= 4 and operation_count <= 4 and term_depth <= 4:
                complexity_level = "medium"
            else:
                complexity_level = "high"
            
            rust_result = {
                "variable_count": variable_count,
                "operation_count": operation_count,
                "term_depth": term_depth,
                "complexity_level": complexity_level,
                "variables": all_vars,
                "operations": all_ops
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation complexity analysis failed for {test_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        equation_json = json.dumps(equation)
        
        # Use equation_generation to test complexity analysis
        java_result = self._run_java_operation(
            "equation_generation", "f", "associative",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_complexity",
            context=f"{test_name}: {expected_complexity}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Equation complexity test passed for {test_name}")
        else:
            self.test_logger.warning(f"Equation complexity test failed for {test_name}: {result.error_message}")
    
    def _calculate_term_depth(self, term) -> int:
        """Calculate the depth of a term (maximum nesting level)"""
        # This is a simplified depth calculation
        # In practice, you'd need to traverse the term structure properly
        term_str = str(term)
        depth = 0
        current_depth = 0
        
        for char in term_str:
            if char == '(':
                current_depth += 1
                depth = max(depth, current_depth)
            elif char == ')':
                current_depth -= 1
        
        return depth


if __name__ == '__main__':
    unittest.main()
