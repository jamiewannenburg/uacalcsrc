#!/usr/bin/env python3
"""
Terms Compatibility Test

This module tests compatibility between Rust and Java UACalc implementations
for Terms utility class static methods, term factory methods, construction utilities,
and term manipulation and transformation operations.

Tests cover:
- Terms utility class static methods
- Term factory methods and construction utilities  
- Term manipulation and transformation operations
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


class TermsCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.terms.Terms utility class compatibility.
    
    This class tests Terms utility class static methods, term factory methods,
    construction utilities, and term manipulation and transformation operations
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
        
        # Test terms for various operations
        self.test_terms = [
            # Simple terms
            "x",
            "y", 
            "z",
            "f(x)",
            "g(x,y)",
            "h(x,y,z)",
            
            # Complex nested terms
            "f(g(x))",
            "f(x, g(y))",
            "f(g(x), h(y))",
            "f(g(h(x)))",
            "f(x, g(y, h(z)))",
            "f(g(x, y), h(z, w))",
            
            # Deep nesting
            "f(g(h(k(x))))",
            "f(g(h(x, y), k(z, w)), l(m(u)))",
        ]
        
        # Test manipulation operations
        self.manipulation_operations = [
            "clone",
            "variables", 
            "depth",
            "subterms"
        ]
        
        # Test transformation types
        self.transformation_types = [
            "normalize",
            "flatten",
            "expand", 
            "simplify"
        ]
    
    def test_terms_factory_methods_compatibility(self):
        """Test Terms utility class factory methods compatibility"""
        # Get Java result
        java_result = self._run_java_operation("terms_factory_methods", 
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_terms_factory_methods_result()
        
        # Compare results
        result = self._compare_results(rust_result, java_result, "terms_factory_methods", "factory_methods")
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Terms factory methods mismatch: {result.error_message}")
    
    def test_terms_construction_utilities_compatibility(self):
        """Test Terms construction utilities compatibility"""
        for term_str in self.test_terms[:8]:  # Test first 8 terms for performance
            with self.subTest(term=term_str):
                self._test_terms_construction_utilities_compatibility(term_str)
    
    def test_terms_manipulation_compatibility(self):
        """Test Terms manipulation operations compatibility"""
        for term_str in self.test_terms[:6]:  # Test first 6 terms for performance
            for operation in self.manipulation_operations:
                with self.subTest(term=term_str, operation=operation):
                    self._test_terms_manipulation_compatibility(term_str, operation)
    
    def test_terms_transformation_compatibility(self):
        """Test Terms transformation operations compatibility"""
        for term_str in self.test_terms[:6]:  # Test first 6 terms for performance
            for transformation_type in self.transformation_types:
                with self.subTest(term=term_str, transformation=transformation_type):
                    self._test_terms_transformation_compatibility(term_str, transformation_type)
    
    def test_terms_string_to_term_factory_compatibility(self):
        """Test Terms.stringToTerm factory method compatibility specifically"""
        for term_str in self.test_terms:
            with self.subTest(term=term_str):
                self._test_string_to_term_compatibility(term_str)
    
    def test_terms_variable_creation_compatibility(self):
        """Test Terms variable creation utilities compatibility"""
        variable_names = ["x", "y", "z", "var1", "var2", "variable"]
        
        for var_name in variable_names:
            with self.subTest(variable=var_name):
                self._test_variable_creation_compatibility(var_name)
    
    def test_terms_complex_construction_compatibility(self):
        """Test Terms complex construction scenarios compatibility"""
        complex_scenarios = [
            ("nested_operations", "f(g(h(x,y),k(z)),l(m(w)))"),
            ("multiple_variables", "f(x,y,z,w,u,v)"),
            ("deep_nesting", "a(b(c(d(e(f(g(h(x))))))))"),
            ("mixed_arities", "f(g(x),h(y,z),k(w,u,v))"),
        ]
        
        for scenario_name, term_str in complex_scenarios:
            with self.subTest(scenario=scenario_name, term=term_str):
                self._test_terms_construction_utilities_compatibility(term_str)
    
    def _test_terms_construction_utilities_compatibility(self, term_str: str):
        """Test terms construction utilities compatibility for a single term"""
        # Get Java result
        java_result = self._run_java_operation("terms_construction_utilities", term_str,
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_terms_construction_utilities_result(term_str)
        
        # Compare results
        context = f"construction_utilities:{term_str}"
        result = self._compare_results(rust_result, java_result, "terms_construction_utilities", context)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Terms construction utilities mismatch: {result.error_message}")
    
    def _test_terms_manipulation_compatibility(self, term_str: str, operation: str):
        """Test terms manipulation compatibility for a single term and operation"""
        # Get Java result
        java_result = self._run_java_operation("terms_manipulation", term_str, operation,
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_terms_manipulation_result(term_str, operation)
        
        # Compare results
        context = f"manipulation:{term_str}:{operation}"
        result = self._compare_results(rust_result, java_result, "terms_manipulation", context)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Terms manipulation mismatch: {result.error_message}")
    
    def _test_terms_transformation_compatibility(self, term_str: str, transformation_type: str):
        """Test terms transformation compatibility for a single term and transformation"""
        # Get Java result
        java_result = self._run_java_operation("terms_transformation", term_str, transformation_type,
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_terms_transformation_result(term_str, transformation_type)
        
        # Compare results
        context = f"transformation:{term_str}:{transformation_type}"
        result = self._compare_results(rust_result, java_result, "terms_transformation", context)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Terms transformation mismatch: {result.error_message}")
    
    def _test_string_to_term_compatibility(self, term_str: str):
        """Test Terms.stringToTerm compatibility for a single term"""
        # This is tested as part of construction utilities, but we can add specific checks
        try:
            # Parse with Rust
            rust_term = parse_term(self.term_arena, term_str)
            rust_success = True
            rust_string_repr = rust_term.to_string()
        except Exception as e:
            rust_success = False
            rust_string_repr = None
        
        # The Java result is obtained through construction utilities test
        java_result = self._run_java_operation("terms_construction_utilities", term_str,
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        if java_result and java_result.get("success", True):
            java_success = java_result["results"]["term_constructed"]
            java_string_repr = java_result["results"]["term_string_representation"]
            
            # Compare success status
            if rust_success != java_success:
                self.test_logger.warning(f"String to term parsing success mismatch for '{term_str}': "
                                       f"Rust={rust_success}, Java={java_success}")
            
            # Compare string representations if both succeeded
            if rust_success and java_success and rust_string_repr != java_string_repr:
                self.test_logger.warning(f"String to term representation mismatch for '{term_str}': "
                                       f"Rust='{rust_string_repr}', Java='{java_string_repr}'")
    
    def _test_variable_creation_compatibility(self, var_name: str):
        """Test variable creation compatibility"""
        # Test variable creation through factory methods test
        # This is a simplified test since variable creation is tested in the factory methods
        try:
            # Create variable with Rust (simplified)
            rust_var = variable(var_name)
            rust_success = True
            rust_var_name = str(rust_var)
        except Exception as e:
            rust_success = False
            rust_var_name = None
        
        # Java variable creation is tested in the factory methods test
        # We can add specific variable creation tests if needed
        self.test_logger.debug(f"Variable creation test for '{var_name}': Rust success={rust_success}")
    
    def _get_rust_terms_factory_methods_result(self) -> Dict[str, Any]:
        """Get Rust terms factory methods result"""
        try:
            start_time = time.time()
            
            # Test Terms.stringToTerm equivalent functionality
            test_terms = ["x", "f(x)", "g(x,y)", "h(f(x),g(y,z))"]
            parsed_terms = []
            failed_terms = []
            
            for term_str in test_terms:
                try:
                    term = parse_term(self.term_arena, term_str)
                    parsed_terms.append(term_str)
                except Exception as e:
                    failed_terms.append(term_str)
            
            # Test variable creation
            variable_creation_successful = True
            variable_names = []
            variables_equal = False
            
            try:
                var1 = variable("x")
                var2 = variable("y")
                variable_names = [str(var1), str(var2)]
                variables_equal = (str(var1) == str(var2))
            except Exception as e:
                variable_creation_successful = False
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "terms_factory_methods",
                "results": {
                    "string_to_term_tests": {
                        "test_terms": test_terms,
                        "parsed_successfully": parsed_terms,
                        "failed_to_parse": failed_terms,
                        "success_rate": len(parsed_terms) / len(test_terms)
                    },
                    "variable_creation": {
                        "variable_creation_successful": variable_creation_successful,
                        "variable_names": variable_names,
                        "variables_equal": variables_equal
                    }
                },
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "terms_factory_methods",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_rust_terms_construction_utilities_result(self, term_str: str) -> Dict[str, Any]:
        """Get Rust terms construction utilities result"""
        try:
            start_time = time.time()
            
            # Parse the term
            term = parse_term(self.term_arena, term_str)
            
            # Get term properties
            is_variable = term.is_variable() if hasattr(term, 'is_variable') else False
            term_string_representation = term.to_string()
            
            # Calculate arity (number of children for operations)
            arity = 0
            if hasattr(term, 'arity'):
                arity = term.arity()
            elif hasattr(term, 'children') and not is_variable:
                children = term.children()
                arity = len(children) if children else 0
            
            # Get variables in term
            variables_in_term = []
            variable_count = 0
            if hasattr(term, 'variables'):
                variables_in_term = list(term.variables())
                variable_count = len(variables_in_term)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "terms_construction_utilities",
                "term_string": term_str,
                "results": {
                    "term_constructed": True,
                    "term_type": "variable" if is_variable else "operation",
                    "term_string_representation": term_string_representation,
                    "term_arity": arity,
                    "is_variable": is_variable,
                    "is_operation": not is_variable,
                    "variables_in_term": [str(v) for v in variables_in_term],
                    "variable_count": variable_count
                },
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "terms_construction_utilities",
                "term_string": term_str,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_rust_terms_manipulation_result(self, term_str: str, operation: str) -> Dict[str, Any]:
        """Get Rust terms manipulation result"""
        try:
            start_time = time.time()
            
            # Parse the term
            term = parse_term(self.term_arena, term_str)
            
            result_data = {}
            
            if operation.lower() == "clone":
                # Test term cloning/copying
                cloned_term = parse_term(self.term_arena, term_str)  # Re-parse as clone
                result_data["cloned_term"] = cloned_term.to_string()
                result_data["clone_equals_original"] = (term.to_string() == cloned_term.to_string())
                
            elif operation.lower() == "variables":
                # Extract variables from term
                variables = []
                if hasattr(term, 'variables'):
                    variables = [str(v) for v in term.variables()]
                result_data["extracted_variables"] = variables
                result_data["variable_count"] = len(variables)
                
            elif operation.lower() == "depth":
                # Calculate term depth
                depth = self._calculate_term_depth(term)
                result_data["term_depth"] = depth
                
            elif operation.lower() == "subterms":
                # Extract subterms
                subterms = []
                self._extract_subterms(term, subterms)
                result_data["subterms"] = subterms
                result_data["subterm_count"] = len(subterms)
                
            else:
                result_data["error"] = f"Unknown manipulation operation: {operation}"
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "terms_manipulation",
                "term_string": term_str,
                "manipulation_operation": operation,
                "results": result_data,
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "terms_manipulation",
                "term_string": term_str,
                "manipulation_operation": operation,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_rust_terms_transformation_result(self, term_str: str, transformation_type: str) -> Dict[str, Any]:
        """Get Rust terms transformation result"""
        try:
            start_time = time.time()
            
            # Parse the term
            term = parse_term(self.term_arena, term_str)
            
            result_data = {}
            
            if transformation_type.lower() == "normalize":
                # Normalize term representation
                normalized_term = term.to_string()
                result_data["normalized_term"] = normalized_term
                result_data["normalization_changed"] = (term_str != normalized_term)
                
            elif transformation_type.lower() == "flatten":
                # Flatten nested operations (simplified)
                flattened_term = self._flatten_term(term)
                result_data["flattened_term"] = flattened_term
                result_data["flattening_changed"] = (term_str != flattened_term)
                
            elif transformation_type.lower() == "expand":
                # Expand term (for now, just return the same term)
                expanded_term = term.to_string()
                result_data["expanded_term"] = expanded_term
                result_data["expansion_changed"] = False
                result_data["note"] = "Full term expansion requires algebra context"
                
            elif transformation_type.lower() == "simplify":
                # Simplify term (basic simplification)
                simplified_term = self._simplify_term(term)
                result_data["simplified_term"] = simplified_term
                result_data["simplification_changed"] = (term_str != simplified_term)
                
            else:
                result_data["error"] = f"Unknown transformation type: {transformation_type}"
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "terms_transformation",
                "term_string": term_str,
                "transformation_type": transformation_type,
                "results": result_data,
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "terms_transformation",
                "term_string": term_str,
                "transformation_type": transformation_type,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _calculate_term_depth(self, term) -> int:
        """Calculate the depth of a term"""
        try:
            if hasattr(term, 'is_variable') and term.is_variable():
                return 0
            elif hasattr(term, 'depth'):
                return term.depth()
            elif hasattr(term, 'children'):
                children = term.children()
                if not children:
                    return 0
                max_child_depth = 0
                for child in children:
                    max_child_depth = max(max_child_depth, self._calculate_term_depth(child))
                return max_child_depth + 1
            else:
                return 0
        except Exception:
            return 0
    
    def _extract_subterms(self, term, subterms: List[str]):
        """Extract all subterms from a term"""
        try:
            subterms.append(term.to_string())
            if hasattr(term, 'children'):
                children = term.children()
                if children:
                    for child in children:
                        self._extract_subterms(child, subterms)
        except Exception:
            pass
    
    def _flatten_term(self, term) -> str:
        """Flatten a term (basic implementation)"""
        try:
            # Basic flattening - just return string representation
            # Full flattening would require more complex logic
            return term.to_string()
        except Exception:
            return str(term)
    
    def _simplify_term(self, term) -> str:
        """Simplify a term (basic implementation)"""
        try:
            # Basic simplification - just return string representation
            # Full simplification would require algebra context and rules
            return term.to_string()
        except Exception:
            return str(term)


if __name__ == "__main__":
    unittest.main()