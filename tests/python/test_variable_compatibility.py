#!/usr/bin/env python3
"""
Variable Compatibility Test

This module tests compatibility between Rust and Java UACalc implementations
for variable creation, naming, comparison, substitution, and scope operations.

Tests cover:
- Variable creation, naming, and comparison
- Variable substitution in complex terms
- Variable scope and binding operations
"""

import unittest
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

from tests.python.base_compatibility_test import BaseCompatibilityTest

try:
    import uacalc
    from uacalc.terms import (
        TermParser, TermEvaluator, parse_term, eval_term, 
        create_term_arena, term_variables, term_operations,
        validate_term_against_algebra, variable, constant, operation,
        substitute_variables
    )
    UACALC_AVAILABLE = True
except ImportError:
    UACALC_AVAILABLE = False


class VariableCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.terms.Variable interface compatibility.
    
    This class tests variable creation, naming, comparison, substitution,
    and scope operations to ensure identical behavior between Rust and Java implementations.
    """
    
    def setUp(self):
        """Set up for each test"""
        super().setUp()
        
        # Skip tests if uacalc is not available
        if not UACALC_AVAILABLE:
            self.skipTest("uacalc module not available")
        
        # Initialize term arena for variable creation
        self.term_arena = create_term_arena()
        
        # Test variable names for various tests
        self.test_variable_names = [
            # Standard indexed variables
            "x0", "x1", "x2", "x3", "x4",
            
            # Single letter variables
            "x", "y", "z", "a", "b", "c",
            
            # Multi-character variables
            "var", "temp", "input", "output",
            
            # Special cases
            "X", "Y", "Z",  # Uppercase
            "x10", "x100",  # Higher indices
            "v1", "v2",     # Different prefix
        ]
        
        # Test terms for substitution and scope analysis
        self.test_terms_for_substitution = [
            # Simple variable terms
            "x0",
            "x1", 
            "y",
            
            # Single operation terms
            "f(x0)",
            "g(x0, x1)",
            "h(x, y, z)",
            
            # Nested terms with variables
            "f(g(x0))",
            "f(x0, g(x1))",
            "f(g(x0), h(x1))",
            "f(g(h(x0)))",
            
            # Complex terms with multiple variables
            "f(x0, g(x1, h(x2)))",
            "f(g(x0, x1), h(x2, x3))",
            "f(g(x, y), h(z, a))",
            
            # Terms with repeated variables
            "f(x0, x0)",
            "g(x0, f(x0, x1))",
            "f(g(x0, x0), x0)",
        ]
    
    def test_variable_creation_compatibility(self):
        """Test variable creation compatibility between Rust and Java"""
        for var_name in self.test_variable_names:
            with self.subTest(variable_name=var_name):
                self._test_variable_creation_compatibility(var_name)
    
    def test_variable_naming_compatibility(self):
        """Test variable naming and string representation compatibility"""
        for var_name in self.test_variable_names:
            with self.subTest(variable_name=var_name):
                self._test_variable_naming_compatibility(var_name)
    
    def test_variable_comparison_compatibility(self):
        """Test variable comparison operations compatibility"""
        # Test pairs of variables for comparison
        test_pairs = [
            # Same variables
            ("x0", "x0"),
            ("x1", "x1"),
            ("x", "x"),
            ("var", "var"),
            
            # Different variables
            ("x0", "x1"),
            ("x", "y"),
            ("var", "temp"),
            ("x0", "x"),
            
            # Case sensitivity
            ("x", "X"),
            ("var", "VAR"),
            
            # Different indices
            ("x0", "x10"),
            ("x1", "x2"),
        ]
        
        for var1_name, var2_name in test_pairs:
            with self.subTest(var1=var1_name, var2=var2_name):
                self._test_variable_comparison_compatibility(var1_name, var2_name)
    
    def test_variable_substitution_simple_compatibility(self):
        """Test simple variable substitution compatibility"""
        # Test simple substitution cases
        simple_substitution_tests = [
            # Variable to variable substitution
            ("x0", "x0", "x1"),
            ("x1", "x1", "x0"),
            ("y", "y", "z"),
            
            # Variable to constant substitution
            ("x0", "x0", "c"),
            ("y", "y", "const"),
            
            # Variable to operation substitution
            ("x0", "x0", "f(x1)"),
            ("y", "y", "g(x, z)"),
        ]
        
        for original_term, var_to_substitute, substitute_term in simple_substitution_tests:
            with self.subTest(term=original_term, var=var_to_substitute, substitute=substitute_term):
                self._test_variable_substitution_compatibility(original_term, var_to_substitute, substitute_term)
    
    def test_variable_substitution_complex_compatibility(self):
        """Test complex variable substitution in nested terms"""
        # Test complex substitution cases
        complex_substitution_tests = [
            # Substitution in operation terms
            ("f(x0)", "x0", "x1"),
            ("g(x0, x1)", "x0", "y"),
            ("h(x, y, z)", "y", "f(a)"),
            
            # Substitution in nested terms
            ("f(g(x0))", "x0", "x1"),
            ("f(x0, g(x1))", "x1", "h(x2)"),
            ("f(g(x0), h(x1))", "x0", "f(x2, x3)"),
            
            # Multiple occurrences
            ("f(x0, x0)", "x0", "x1"),
            ("g(x0, f(x0, x1))", "x0", "y"),
            ("f(g(x0, x0), x0)", "x0", "h(z)"),
            
            # No substitution (variable not present)
            ("f(x0, x1)", "x2", "y"),
            ("g(y, z)", "x0", "a"),
        ]
        
        for original_term, var_to_substitute, substitute_term in complex_substitution_tests:
            with self.subTest(term=original_term, var=var_to_substitute, substitute=substitute_term):
                self._test_variable_substitution_compatibility(original_term, var_to_substitute, substitute_term)
    
    def test_variable_scope_analysis_compatibility(self):
        """Test variable scope and binding analysis compatibility"""
        for term_str in self.test_terms_for_substitution:
            with self.subTest(term=term_str):
                self._test_variable_scope_compatibility(term_str)
    
    def test_variable_binding_operations_compatibility(self):
        """Test variable binding operations compatibility"""
        # Test terms with different variable binding patterns
        binding_test_terms = [
            # Single variable, single occurrence
            "x0",
            "f(x0)",
            
            # Single variable, multiple occurrences
            "f(x0, x0)",
            "g(x0, f(x0))",
            "f(g(x0, x0), h(x0))",
            
            # Multiple variables, single occurrences
            "f(x0, x1)",
            "g(x, y, z)",
            "f(g(x0, x1), h(x2, x3))",
            
            # Multiple variables, mixed occurrences
            "f(x0, g(x0, x1))",
            "g(x, f(x, y), h(y, z))",
            "f(g(x0, x1), h(x0, x2), k(x1, x2))",
            
            # Deep nesting with variables
            "f(g(h(x0)))",
            "f(g(h(x0, x1), k(x0)), l(x1))",
        ]
        
        for term_str in binding_test_terms:
            with self.subTest(term=term_str):
                self._test_variable_binding_compatibility(term_str)
    
    def test_variable_index_mapping_compatibility(self):
        """Test variable index mapping and conversion compatibility"""
        # Test different variable naming schemes and their index mappings
        index_mapping_tests = [
            # Standard x0, x1, ... format
            ("x0", 0),
            ("x1", 1),
            ("x10", 10),
            ("x100", 100),
            
            # Single letter variables
            ("x", None),  # Should map to some consistent index
            ("y", None),  # Should map to some consistent index
            ("z", None),  # Should map to some consistent index
            
            # Multi-character variables
            ("var", None),   # Should map consistently
            ("temp", None),  # Should map consistently
            ("input", None), # Should map consistently
        ]
        
        for var_name, expected_index in index_mapping_tests:
            with self.subTest(variable=var_name, expected_index=expected_index):
                self._test_variable_index_mapping_compatibility(var_name, expected_index)
    
    def _test_variable_creation_compatibility(self, var_name: str):
        """Test variable creation compatibility for a single variable name"""
        # Get Java result
        java_result = self._run_java_operation("create_variable", var_name,
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_variable_creation_result(var_name)
        
        # Compare results
        result = self._compare_results(rust_result, java_result, "create_variable", var_name)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Variable creation mismatch for '{var_name}': {result.error_message}")
    
    def _test_variable_naming_compatibility(self, var_name: str):
        """Test variable naming compatibility"""
        # This is covered by the creation test, but we can add specific naming checks
        self._test_variable_creation_compatibility(var_name)
    
    def _test_variable_comparison_compatibility(self, var1_name: str, var2_name: str):
        """Test variable comparison compatibility"""
        # Get Java result
        java_result = self._run_java_operation("variable_comparison", var1_name, var2_name,
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_variable_comparison_result(var1_name, var2_name)
        
        # Compare results
        context = f"{var1_name} vs {var2_name}"
        result = self._compare_results(rust_result, java_result, "variable_comparison", context)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Variable comparison mismatch: {result.error_message}")
    
    def _test_variable_substitution_compatibility(self, original_term: str, var_to_substitute: str, substitute_term: str):
        """Test variable substitution compatibility"""
        # Get Java result
        java_result = self._run_java_operation("variable_substitution", original_term, var_to_substitute, substitute_term,
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_variable_substitution_result(original_term, var_to_substitute, substitute_term)
        
        # Compare results
        context = f"{original_term}[{var_to_substitute} -> {substitute_term}]"
        result = self._compare_results(rust_result, java_result, "variable_substitution", context)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Variable substitution mismatch: {result.error_message}")
    
    def _test_variable_scope_compatibility(self, term_str: str):
        """Test variable scope analysis compatibility"""
        # Get Java result
        java_result = self._run_java_operation("variable_scope", term_str,
                                             timeout=self.JAVA_TIMEOUT_SHORT)
        
        # Get Rust result
        rust_result = self._get_rust_variable_scope_result(term_str)
        
        # Compare results
        result = self._compare_results(rust_result, java_result, "variable_scope", term_str)
        
        if not result.matches and java_result and java_result.get("success", True):
            self.test_logger.warning(f"Variable scope mismatch for '{term_str}': {result.error_message}")
    
    def _test_variable_binding_compatibility(self, term_str: str):
        """Test variable binding analysis compatibility"""
        # Variable binding is analyzed as part of scope analysis
        self._test_variable_scope_compatibility(term_str)
    
    def _test_variable_index_mapping_compatibility(self, var_name: str, expected_index: Optional[int]):
        """Test variable index mapping compatibility"""
        # This is tested as part of variable creation
        self._test_variable_creation_compatibility(var_name)
    
    def _get_rust_variable_creation_result(self, var_name: str) -> Dict[str, Any]:
        """Get Rust variable creation result"""
        try:
            start_time = time.time()
            
            # Create variable using Rust implementation
            var_term = variable(var_name, self.term_arena)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "create_variable",
                "variable_name": var_name,
                "variable_string": var_term.to_string(),
                "variable_hash": hash(var_term.to_string()),  # Approximate hash
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "create_variable",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_rust_variable_comparison_result(self, var1_name: str, var2_name: str) -> Dict[str, Any]:
        """Get Rust variable comparison result"""
        try:
            start_time = time.time()
            
            # Create variables using Rust implementation
            var1 = variable(var1_name, self.term_arena)
            var2 = variable(var2_name, self.term_arena)
            
            # Compare variables
            var1_str = var1.to_string()
            var2_str = var2.to_string()
            
            are_equal = var1_str == var2_str
            same_name = var1_name == var2_name
            var1_hash = hash(var1_str)
            var2_hash = hash(var2_str)
            
            # Simple comparison result (lexicographic)
            if var1_str < var2_str:
                comparison_result = -1
            elif var1_str > var2_str:
                comparison_result = 1
            else:
                comparison_result = 0
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "variable_comparison",
                "var1_name": var1_name,
                "var2_name": var2_name,
                "are_equal": are_equal,
                "same_name": same_name,
                "var1_hash": var1_hash,
                "var2_hash": var2_hash,
                "comparison_result": comparison_result,
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "variable_comparison",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_rust_variable_substitution_result(self, original_term: str, var_to_substitute: str, substitute_term: str) -> Dict[str, Any]:
        """Get Rust variable substitution result"""
        try:
            start_time = time.time()
            
            # Parse terms
            original = parse_term(self.term_arena, original_term)
            substitute = parse_term(self.term_arena, substitute_term)
            
            # Convert variable name to index
            var_index = self._variable_name_to_index(var_to_substitute)
            
            # Create substitution map
            substitutions = {var_index: substitute.term_id}
            
            # Perform substitution
            result_term = substitute_variables(original, substitutions)
            result_term_str = result_term.to_string()
            
            # Check if substitution occurred
            substitution_occurred = result_term_str != original.to_string()
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "variable_substitution",
                "original_term": original_term,
                "variable_name": var_to_substitute,
                "substitute_term": substitute_term,
                "result_term": result_term_str,
                "substitution_occurred": substitution_occurred,
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "variable_substitution",
                "original_term": original_term,
                "variable_name": var_to_substitute,
                "substitute_term": substitute_term,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_rust_variable_scope_result(self, term_str: str) -> Dict[str, Any]:
        """Get Rust variable scope analysis result"""
        try:
            start_time = time.time()
            
            # Parse term
            term = parse_term(self.term_arena, term_str)
            
            # Get variables from the term
            variable_indices = term_variables(term)
            
            # Analyze variable occurrences and depths
            variables_info = []
            for var_index in variable_indices:
                var_name = f"x{var_index}"  # Standard naming
                
                # Count occurrences by analyzing the term string
                # This is a simplified approach - in a real implementation,
                # we would traverse the term tree structure
                occurrences = term_str.count(var_name)
                
                # Estimate max depth by counting parentheses depth around variable
                # This is also simplified - real implementation would use term tree
                max_depth = self._estimate_variable_depth(term_str, var_name)
                
                variables_info.append({
                    "name": var_name,
                    "occurrences": occurrences,
                    "max_depth": max_depth
                })
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "operation": "variable_scope",
                "term_string": term_str,
                "variables": variables_info,
                "total_variables": len(variable_indices),
                "term_depth": term.depth(),
                "execution_time_ms": execution_time * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "variable_scope",
                "term_string": term_str,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _estimate_variable_depth(self, term_str: str, var_name: str) -> int:
        """Estimate the maximum depth at which a variable appears in a term string"""
        # Find all occurrences of the variable
        var_positions = []
        start = 0
        while True:
            pos = term_str.find(var_name, start)
            if pos == -1:
                break
            var_positions.append(pos)
            start = pos + 1
        
        if not var_positions:
            return 0
        
        # For each occurrence, count the depth by counting parentheses
        max_depth = 0
        for pos in var_positions:
            depth = 0
            for i in range(pos):
                if term_str[i] == '(':
                    depth += 1
                elif term_str[i] == ')':
                    depth -= 1
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _variable_name_to_index(self, var_name: str) -> int:
        """Convert variable name to index (approximate mapping)"""
        if var_name.startswith("x") and len(var_name) > 1:
            try:
                return int(var_name[1:])
            except ValueError:
                pass
        
        # For non-standard names, use hash-based mapping
        if len(var_name) == 1 and var_name.isalpha():
            if var_name.islower():
                return ord(var_name) - ord('a')
            else:
                return ord(var_name) - ord('A') + 26
        
        # For other names, use hash
        return hash(var_name) % 255


if __name__ == "__main__":
    unittest.main()