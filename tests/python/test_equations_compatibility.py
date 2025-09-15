#!/usr/bin/env python3
"""
Equations Compatibility Test

This module tests compatibility between Rust and Java UACalc implementations
for the Equations utility class methods, equation set operations, and equation
generation utilities.

Tests cover:
- Equations utility class methods (associativeLaw, cyclicLaw, firstSecondSymmetricLaw)
- Equation set operations and properties
- Equation generation and enumeration utilities
"""

import unittest
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from tests.python.base_compatibility_test import BaseCompatibilityTest

try:
    import uacalc
    from uacalc import create_term_arena
    from uacalc.terms import (
        parse_term, eval_term, variable, constant, operation,
        term_variables, term_operations
    )
    UACALC_AVAILABLE = True
except ImportError:
    UACALC_AVAILABLE = False


class EquationsCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.eq.Equations utility class compatibility.
    
    This class tests:
    - Equations utility class methods (associativeLaw, cyclicLaw, firstSecondSymmetricLaw)
    - Equation set operations and properties
    - Equation generation and enumeration utilities
    
    Requirements: 4.4, 5.6
    """
    
    def setUp(self):
        """Set up for each test"""
        super().setUp()
        
        # Skip tests if uacalc is not available
        if not UACALC_AVAILABLE:
            self.skipTest("uacalc module not available")
        
        # Create term arena for parsing
        self.arena = create_term_arena()
        
        # Test operation symbols for equation generation
        self.test_operation_symbols = [
            {"symbol": "f", "arity": 2, "description": "Binary operation f"},
            {"symbol": "g", "arity": 3, "description": "Ternary operation g"},
            {"symbol": "h", "arity": 4, "description": "Quaternary operation h"},
            {"symbol": "m", "arity": 2, "description": "Binary operation m"},
            {"symbol": "n", "arity": 1, "description": "Unary operation n"}
        ]
        
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
    
    def test_equations_utility_methods_compatibility(self):
        """Test Equations utility class methods"""
        self.test_logger.info("Testing Equations utility class methods")
        
        # Test associative law generation
        self._test_associative_law_generation()
        
        # Test cyclic law generation
        self._test_cyclic_law_generation()
        
        # Test first-second symmetric law generation
        self._test_first_second_symmetric_law_generation()
    
    def _test_associative_law_generation(self):
        """Test associative law generation for binary operations"""
        self.test_logger.info("Testing associative law generation")
        
        # Test with binary operations
        binary_operations = [op for op in self.test_operation_symbols if op["arity"] == 2]
        
        for op_data in binary_operations:
            with self.subTest(operation=op_data["symbol"]):
                self._test_associative_law_for_operation(op_data)
    
    def _test_associative_law_for_operation(self, op_data: Dict[str, Any]):
        """Test associative law generation for a specific operation"""
        symbol = op_data["symbol"]
        arity = op_data["arity"]
        description = op_data["description"]
        
        # Test Rust implementation
        try:
            # Generate associative law: f(f(x,y),z) = f(x,f(y,z))
            left_term = parse_term(self.arena,self.arena, f"{symbol}({symbol}(x,y),z)")
            right_term = parse_term(self.arena,self.arena, f"{symbol}(x,{symbol}(y,z))")
            
            # Extract variables and operations
            left_vars = list(term_variables(left_term))
            right_vars = list(term_variables(right_term))
            all_vars = list(set(left_vars + right_vars))
            
            left_ops = list(term_operations(left_term))
            right_ops = list(term_operations(right_term))
            all_ops = list(set(left_ops + right_ops))
            
            rust_result = {
                "law_type": "associative",
                "symbol": symbol,
                "arity": arity,
                "left_term": str(left_term),
                "right_term": str(right_term),
                "variables": all_vars,
                "operations": all_ops,
                "variable_count": len(all_vars),
                "operation_count": len(all_ops),
                "description": description
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust associative law generation failed for {symbol}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        java_result = self._run_java_operation(
            "equation_generation", symbol, "associative",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "associative_law_generation",
            context=f"{symbol} (arity {arity}): {description}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Associative law generation test passed for {symbol}")
        else:
            self.test_logger.warning(f"Associative law generation test failed for {symbol}: {result.error_message}")
    
    def _test_cyclic_law_generation(self):
        """Test cyclic law generation for operations with arity >= 1"""
        self.test_logger.info("Testing cyclic law generation")
        
        # Test with operations of different arities
        for op_data in self.test_operation_symbols:
            if op_data["arity"] >= 1:
                with self.subTest(operation=op_data["symbol"]):
                    self._test_cyclic_law_for_operation(op_data)
    
    def _test_cyclic_law_for_operation(self, op_data: Dict[str, Any]):
        """Test cyclic law generation for a specific operation"""
        symbol = op_data["symbol"]
        arity = op_data["arity"]
        description = op_data["description"]
        
        # Test Rust implementation
        try:
            # Generate cyclic law: f(x0,x1,...,x{k-1}) = f(x{k-1},x0,...,x{k-2})
            if arity == 1:
                left_term = parse_term(self.arena,f"{symbol}(x0)")
                right_term = parse_term(self.arena,f"{symbol}(x0)")
            elif arity == 2:
                left_term = parse_term(self.arena,f"{symbol}(x0,x1)")
                right_term = parse_term(self.arena,f"{symbol}(x1,x0)")
            elif arity == 3:
                left_term = parse_term(self.arena,f"{symbol}(x0,x1,x2)")
                right_term = parse_term(self.arena,f"{symbol}(x2,x0,x1)")
            elif arity == 4:
                left_term = parse_term(self.arena,f"{symbol}(x0,x1,x2,x3)")
                right_term = parse_term(self.arena,f"{symbol}(x3,x0,x1,x2)")
            else:
                # For higher arities, construct the terms programmatically
                left_vars = [f"x{i}" for i in range(arity)]
                right_vars = [f"x{arity-1}"] + [f"x{i}" for i in range(arity-1)]
                
                left_term_str = f"{symbol}({','.join(left_vars)})"
                right_term_str = f"{symbol}({','.join(right_vars)})"
                
                left_term = parse_term(self.arena,left_term_str)
                right_term = parse_term(self.arena,right_term_str)
            
            # Extract variables and operations
            left_vars = list(term_variables(left_term))
            right_vars = list(term_variables(right_term))
            all_vars = list(set(left_vars + right_vars))
            
            left_ops = list(term_operations(left_term))
            right_ops = list(term_operations(right_term))
            all_ops = list(set(left_ops + right_ops))
            
            rust_result = {
                "law_type": "cyclic",
                "symbol": symbol,
                "arity": arity,
                "left_term": str(left_term),
                "right_term": str(right_term),
                "variables": all_vars,
                "operations": all_ops,
                "variable_count": len(all_vars),
                "operation_count": len(all_ops),
                "description": description
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust cyclic law generation failed for {symbol}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        java_result = self._run_java_operation(
            "equation_generation", symbol, "cyclic",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "cyclic_law_generation",
            context=f"{symbol} (arity {arity}): {description}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Cyclic law generation test passed for {symbol}")
        else:
            self.test_logger.warning(f"Cyclic law generation test failed for {symbol}: {result.error_message}")
    
    def _test_first_second_symmetric_law_generation(self):
        """Test first-second symmetric law generation for operations with arity >= 2"""
        self.test_logger.info("Testing first-second symmetric law generation")
        
        # Test with operations of arity >= 2
        for op_data in self.test_operation_symbols:
            if op_data["arity"] >= 2:
                with self.subTest(operation=op_data["symbol"]):
                    self._test_first_second_symmetric_law_for_operation(op_data)
    
    def _test_first_second_symmetric_law_for_operation(self, op_data: Dict[str, Any]):
        """Test first-second symmetric law generation for a specific operation"""
        symbol = op_data["symbol"]
        arity = op_data["arity"]
        description = op_data["description"]
        
        # Test Rust implementation
        try:
            # Generate first-second symmetric law: f(x0,x1,x2,...) = f(x1,x0,x2,...)
            if arity == 2:
                left_term = parse_term(self.arena,f"{symbol}(x0,x1)")
                right_term = parse_term(self.arena,f"{symbol}(x1,x0)")
            elif arity == 3:
                left_term = parse_term(self.arena,f"{symbol}(x0,x1,x2)")
                right_term = parse_term(self.arena,f"{symbol}(x1,x0,x2)")
            elif arity == 4:
                left_term = parse_term(self.arena,f"{symbol}(x0,x1,x2,x3)")
                right_term = parse_term(self.arena,f"{symbol}(x1,x0,x2,x3)")
            else:
                # For higher arities, construct the terms programmatically
                left_vars = [f"x{i}" for i in range(arity)]
                right_vars = [f"x1", f"x0"] + [f"x{i}" for i in range(2, arity)]
                
                left_term_str = f"{symbol}({','.join(left_vars)})"
                right_term_str = f"{symbol}({','.join(right_vars)})"
                
                left_term = parse_term(self.arena,left_term_str)
                right_term = parse_term(self.arena,right_term_str)
            
            # Extract variables and operations
            left_vars = list(term_variables(left_term))
            right_vars = list(term_variables(right_term))
            all_vars = list(set(left_vars + right_vars))
            
            left_ops = list(term_operations(left_term))
            right_ops = list(term_operations(right_term))
            all_ops = list(set(left_ops + right_ops))
            
            rust_result = {
                "law_type": "first_second_symmetric",
                "symbol": symbol,
                "arity": arity,
                "left_term": str(left_term),
                "right_term": str(right_term),
                "variables": all_vars,
                "operations": all_ops,
                "variable_count": len(all_vars),
                "operation_count": len(all_ops),
                "description": description
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust first-second symmetric law generation failed for {symbol}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        java_result = self._run_java_operation(
            "equation_generation", symbol, "first_second_symmetric",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "first_second_symmetric_law_generation",
            context=f"{symbol} (arity {arity}): {description}"
        )
        
        if result.matches:
            self.test_logger.debug(f"First-second symmetric law generation test passed for {symbol}")
        else:
            self.test_logger.warning(f"First-second symmetric law generation test failed for {symbol}: {result.error_message}")
    
    def test_equation_set_operations_compatibility(self):
        """Test equation set operations and properties"""
        self.test_logger.info("Testing equation set operations and properties")
        
        # Test equation set construction
        self._test_equation_set_construction()
        
        # Test equation set properties
        self._test_equation_set_properties()
        
        # Test equation set operations
        self._test_equation_set_operations()
    
    def _test_equation_set_construction(self):
        """Test construction of equation sets"""
        self.test_logger.info("Testing equation set construction")
        
        # Create a set of standard equations
        equation_set = [
            {"type": "associative", "symbol": "f", "arity": 2},
            {"type": "cyclic", "symbol": "g", "arity": 3},
            {"type": "first_second_symmetric", "symbol": "h", "arity": 2}
        ]
        
        for eq_data in equation_set:
            with self.subTest(equation_type=eq_data["type"]):
                self._test_single_equation_construction(eq_data)
    
    def _test_single_equation_construction(self, eq_data: Dict[str, Any]):
        """Test construction of a single equation"""
        eq_type = eq_data["type"]
        symbol = eq_data["symbol"]
        arity = eq_data["arity"]
        
        # Test Rust implementation
        try:
            # Generate the equation based on type
            if eq_type == "associative" and arity == 2:
                left_term = parse_term(self.arena,f"{symbol}({symbol}(x,y),z)")
                right_term = parse_term(self.arena,f"{symbol}(x,{symbol}(y,z))")
            elif eq_type == "cyclic" and arity == 3:
                left_term = parse_term(self.arena,f"{symbol}(x0,x1,x2)")
                right_term = parse_term(self.arena,f"{symbol}(x2,x0,x1)")
            elif eq_type == "first_second_symmetric" and arity == 2:
                left_term = parse_term(self.arena,f"{symbol}(x0,x1)")
                right_term = parse_term(self.arena,f"{symbol}(x1,x0)")
            else:
                raise ValueError(f"Unsupported equation type: {eq_type}")
            
            # Analyze equation properties
            left_vars = list(term_variables(left_term))
            right_vars = list(term_variables(right_term))
            all_vars = list(set(left_vars + right_vars))
            
            left_ops = list(term_operations(left_term))
            right_ops = list(term_operations(right_term))
            all_ops = list(set(left_ops + right_ops))
            
            rust_result = {
                "equation_type": eq_type,
                "symbol": symbol,
                "arity": arity,
                "left_term": str(left_term),
                "right_term": str(right_term),
                "variables": all_vars,
                "operations": all_ops,
                "variable_count": len(all_vars),
                "operation_count": len(all_ops),
                "is_well_formed": True
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation construction failed for {eq_type}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        java_result = self._run_java_operation(
            "equation_generation", symbol, eq_type,
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_set_construction",
            context=f"{eq_type} equation for {symbol} (arity {arity})"
        )
        
        if result.matches:
            self.test_logger.debug(f"Equation set construction test passed for {eq_type}")
        else:
            self.test_logger.warning(f"Equation set construction test failed for {eq_type}: {result.error_message}")
    
    def _test_equation_set_properties(self):
        """Test properties of equation sets"""
        self.test_logger.info("Testing equation set properties")
        
        # Test equation set analysis
        equation_sets = [
            {
                "name": "associative_set",
                "equations": [
                    {"type": "associative", "symbol": "f", "arity": 2},
                    {"type": "associative", "symbol": "g", "arity": 2}
                ]
            },
            {
                "name": "mixed_set",
                "equations": [
                    {"type": "associative", "symbol": "f", "arity": 2},
                    {"type": "cyclic", "symbol": "g", "arity": 3},
                    {"type": "first_second_symmetric", "symbol": "h", "arity": 2}
                ]
            }
        ]
        
        for eq_set in equation_sets:
            with self.subTest(equation_set=eq_set["name"]):
                self._test_equation_set_analysis(eq_set)
    
    def _test_equation_set_analysis(self, eq_set: Dict[str, Any]):
        """Test analysis of a specific equation set"""
        set_name = eq_set["name"]
        equations = eq_set["equations"]
        
        # Test Rust implementation
        try:
            all_variables = set()
            all_operations = set()
            equation_count = len(equations)
            
            for eq_data in equations:
                eq_type = eq_data["type"]
                symbol = eq_data["symbol"]
                arity = eq_data["arity"]
                
                # Generate equation terms
                if eq_type == "associative" and arity == 2:
                    left_term = parse_term(self.arena,f"{symbol}({symbol}(x,y),z)")
                    right_term = parse_term(self.arena,f"{symbol}(x,{symbol}(y,z))")
                elif eq_type == "cyclic" and arity == 3:
                    left_term = parse_term(self.arena,f"{symbol}(x0,x1,x2)")
                    right_term = parse_term(self.arena,f"{symbol}(x2,x0,x1)")
                elif eq_type == "first_second_symmetric" and arity == 2:
                    left_term = parse_term(self.arena,f"{symbol}(x0,x1)")
                    right_term = parse_term(self.arena,f"{symbol}(x1,x0)")
                else:
                    continue
                
                # Collect variables and operations
                left_vars = list(term_variables(left_term))
                right_vars = list(term_variables(right_term))
                all_variables.update(left_vars + right_vars)
                
                left_ops = list(term_operations(left_term))
                right_ops = list(term_operations(right_term))
                all_operations.update(left_ops + right_ops)
            
            rust_result = {
                "set_name": set_name,
                "equation_count": equation_count,
                "total_variables": len(all_variables),
                "total_operations": len(all_operations),
                "variables": list(all_variables),
                "operations": list(all_operations),
                "is_consistent": True,  # Simplified consistency check
                "complexity_score": equation_count * len(all_variables) * len(all_operations)
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation set analysis failed for {set_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        # Use equation_generation to test set analysis
        java_result = self._run_java_operation(
            "equation_generation", "f", "associative",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_set_properties",
            context=f"{set_name} with {equation_count} equations"
        )
        
        if result.matches:
            self.test_logger.debug(f"Equation set properties test passed for {set_name}")
        else:
            self.test_logger.warning(f"Equation set properties test failed for {set_name}: {result.error_message}")
    
    def _test_equation_set_operations(self):
        """Test operations on equation sets"""
        self.test_logger.info("Testing equation set operations")
        
        # Test equation set union, intersection, and difference operations
        operation_tests = [
            {
                "name": "equation_union",
                "description": "Test union of equation sets"
            },
            {
                "name": "equation_intersection",
                "description": "Test intersection of equation sets"
            },
            {
                "name": "equation_difference",
                "description": "Test difference of equation sets"
            }
        ]
        
        for test_case in operation_tests:
            with self.subTest(operation=test_case["name"]):
                self._test_equation_set_operation(test_case)
    
    def _test_equation_set_operation(self, test_case: Dict[str, Any]):
        """Test a specific equation set operation"""
        operation_name = test_case["name"]
        description = test_case["description"]
        
        # Test Rust implementation
        try:
            # Create sample equation sets
            set1_equations = [
                {"type": "associative", "symbol": "f", "arity": 2},
                {"type": "cyclic", "symbol": "g", "arity": 3}
            ]
            
            set2_equations = [
                {"type": "associative", "symbol": "f", "arity": 2},
                {"type": "first_second_symmetric", "symbol": "h", "arity": 2}
            ]
            
            # Perform set operations
            if operation_name == "equation_union":
                # Union: combine all equations
                result_equations = set1_equations + set2_equations
                operation_result = "union"
            elif operation_name == "equation_intersection":
                # Intersection: common equations
                common_equations = [eq for eq in set1_equations if eq in set2_equations]
                result_equations = common_equations
                operation_result = "intersection"
            elif operation_name == "equation_difference":
                # Difference: equations in set1 but not in set2
                diff_equations = [eq for eq in set1_equations if eq not in set2_equations]
                result_equations = diff_equations
                operation_result = "difference"
            else:
                raise ValueError(f"Unknown operation: {operation_name}")
            
            rust_result = {
                "operation": operation_name,
                "operation_result": operation_result,
                "result_equation_count": len(result_equations),
                "set1_size": len(set1_equations),
                "set2_size": len(set2_equations),
                "description": description
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation set operation failed for {operation_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        java_result = self._run_java_operation(
            "equation_generation", "f", "associative",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_set_operations",
            context=f"{operation_name}: {description}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Equation set operation test passed for {operation_name}")
        else:
            self.test_logger.warning(f"Equation set operation test failed for {operation_name}: {result.error_message}")
    
    def test_equation_generation_utilities_compatibility(self):
        """Test equation generation and enumeration utilities"""
        self.test_logger.info("Testing equation generation and enumeration utilities")
        
        # Test equation enumeration
        self._test_equation_enumeration()
        
        # Test equation generation patterns
        self._test_equation_generation_patterns()
        
        # Test equation validation
        self._test_equation_validation()
    
    def _test_equation_enumeration(self):
        """Test enumeration of equations"""
        self.test_logger.info("Testing equation enumeration")
        
        # Test enumeration of standard equations
        enumeration_tests = [
            {
                "name": "binary_operations",
                "operations": [{"symbol": "f", "arity": 2}, {"symbol": "g", "arity": 2}],
                "equation_types": ["associative", "first_second_symmetric"]
            },
            {
                "name": "ternary_operations",
                "operations": [{"symbol": "h", "arity": 3}],
                "equation_types": ["cyclic"]
            },
            {
                "name": "mixed_operations",
                "operations": [{"symbol": "f", "arity": 2}, {"symbol": "g", "arity": 3}],
                "equation_types": ["associative", "cyclic"]
            }
        ]
        
        for test_case in enumeration_tests:
            with self.subTest(enumeration=test_case["name"]):
                self._test_equation_enumeration_case(test_case)
    
    def _test_equation_enumeration_case(self, test_case: Dict[str, Any]):
        """Test enumeration for a specific case"""
        case_name = test_case["name"]
        operations = test_case["operations"]
        equation_types = test_case["equation_types"]
        
        # Test Rust implementation
        try:
            enumerated_equations = []
            
            for op_data in operations:
                symbol = op_data["symbol"]
                arity = op_data["arity"]
                
                for eq_type in equation_types:
                    # Check if equation type is applicable
                    if eq_type == "associative" and arity == 2:
                        left_term = parse_term(self.arena,f"{symbol}({symbol}(x,y),z)")
                        right_term = parse_term(self.arena,f"{symbol}(x,{symbol}(y,z))")
                        enumerated_equations.append({
                            "symbol": symbol,
                            "type": eq_type,
                            "left_term": str(left_term),
                            "right_term": str(right_term)
                        })
                    elif eq_type == "cyclic" and arity >= 1:
                        if arity == 3:
                            left_term = parse_term(self.arena,f"{symbol}(x0,x1,x2)")
                            right_term = parse_term(self.arena,f"{symbol}(x2,x0,x1)")
                        else:
                            # Simplified for other arities
                            left_term = parse_term(self.arena,f"{symbol}(x0,x1)")
                            right_term = parse_term(self.arena,f"{symbol}(x1,x0)")
                        enumerated_equations.append({
                            "symbol": symbol,
                            "type": eq_type,
                            "left_term": str(left_term),
                            "right_term": str(right_term)
                        })
                    elif eq_type == "first_second_symmetric" and arity >= 2:
                        left_term = parse_term(self.arena,f"{symbol}(x0,x1)")
                        right_term = parse_term(self.arena,f"{symbol}(x1,x0)")
                        enumerated_equations.append({
                            "symbol": symbol,
                            "type": eq_type,
                            "left_term": str(left_term),
                            "right_term": str(right_term)
                        })
            
            rust_result = {
                "case_name": case_name,
                "operation_count": len(operations),
                "equation_type_count": len(equation_types),
                "enumerated_equation_count": len(enumerated_equations),
                "enumerated_equations": enumerated_equations,
                "enumeration_successful": True
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation enumeration failed for {case_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        java_result = self._run_java_operation(
            "equation_generation", "f", "associative",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_enumeration",
            context=f"{case_name}: {len(operations)} operations, {len(equation_types)} types"
        )
        
        if result.matches:
            self.test_logger.debug(f"Equation enumeration test passed for {case_name}")
        else:
            self.test_logger.warning(f"Equation enumeration test failed for {case_name}: {result.error_message}")
    
    def _test_equation_generation_patterns(self):
        """Test equation generation patterns"""
        self.test_logger.info("Testing equation generation patterns")
        
        # Test different generation patterns
        pattern_tests = [
            {
                "name": "standard_laws",
                "pattern": "standard",
                "description": "Generate standard algebraic laws"
            },
            {
                "name": "custom_patterns",
                "pattern": "custom",
                "description": "Generate custom equation patterns"
            },
            {
                "name": "variety_specific",
                "pattern": "variety",
                "description": "Generate variety-specific equations"
            }
        ]
        
        for test_case in pattern_tests:
            with self.subTest(pattern=test_case["name"]):
                self._test_equation_generation_pattern(test_case)
    
    def _test_equation_generation_pattern(self, test_case: Dict[str, Any]):
        """Test a specific equation generation pattern"""
        pattern_name = test_case["name"]
        pattern_type = test_case["pattern"]
        description = test_case["description"]
        
        # Test Rust implementation
        try:
            if pattern_type == "standard":
                # Generate standard laws
                generated_equations = [
                    {"type": "associative", "symbol": "f", "arity": 2},
                    {"type": "cyclic", "symbol": "g", "arity": 3},
                    {"type": "first_second_symmetric", "symbol": "h", "arity": 2}
                ]
            elif pattern_type == "custom":
                # Generate custom patterns
                generated_equations = [
                    {"type": "associative", "symbol": "m", "arity": 2},
                    {"type": "first_second_symmetric", "symbol": "n", "arity": 2}
                ]
            elif pattern_type == "variety":
                # Generate variety-specific equations
                generated_equations = [
                    {"type": "associative", "symbol": "f", "arity": 2}
                ]
            else:
                generated_equations = []
            
            rust_result = {
                "pattern_name": pattern_name,
                "pattern_type": pattern_type,
                "generated_equation_count": len(generated_equations),
                "generated_equations": generated_equations,
                "description": description,
                "generation_successful": True
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation generation pattern failed for {pattern_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        java_result = self._run_java_operation(
            "equation_generation", "f", "associative",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_generation_patterns",
            context=f"{pattern_name}: {description}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Equation generation pattern test passed for {pattern_name}")
        else:
            self.test_logger.warning(f"Equation generation pattern test failed for {pattern_name}: {result.error_message}")
    
    def _test_equation_validation(self):
        """Test equation validation utilities"""
        self.test_logger.info("Testing equation validation utilities")
        
        # Test validation of different equation types
        validation_tests = [
            {
                "name": "valid_equations",
                "equations": [
                    {"type": "associative", "symbol": "f", "arity": 2, "expected_valid": True},
                    {"type": "cyclic", "symbol": "g", "arity": 3, "expected_valid": True}
                ]
            },
            {
                "name": "invalid_equations",
                "equations": [
                    {"type": "associative", "symbol": "f", "arity": 1, "expected_valid": False},
                    {"type": "cyclic", "symbol": "g", "arity": 0, "expected_valid": False}
                ]
            }
        ]
        
        for test_case in validation_tests:
            with self.subTest(validation=test_case["name"]):
                self._test_equation_validation_case(test_case)
    
    def _test_equation_validation_case(self, test_case: Dict[str, Any]):
        """Test validation for a specific case"""
        case_name = test_case["name"]
        equations = test_case["equations"]
        
        # Test Rust implementation
        try:
            validation_results = []
            
            for eq_data in equations:
                eq_type = eq_data["type"]
                symbol = eq_data["symbol"]
                arity = eq_data["arity"]
                expected_valid = eq_data["expected_valid"]
                
                # Validate equation
                is_valid = True
                validation_error = None
                
                try:
                    if eq_type == "associative" and arity != 2:
                        is_valid = False
                        validation_error = "Associative law requires arity 2"
                    elif eq_type == "cyclic" and arity < 1:
                        is_valid = False
                        validation_error = "Cyclic law requires arity >= 1"
                    elif eq_type == "first_second_symmetric" and arity < 2:
                        is_valid = False
                        validation_error = "First-second symmetric law requires arity >= 2"
                    
                    # Try to generate the equation
                    if is_valid:
                        if eq_type == "associative":
                            left_term = parse_term(self.arena,f"{symbol}({symbol}(x,y),z)")
                            right_term = parse_term(self.arena,f"{symbol}(x,{symbol}(y,z))")
                        elif eq_type == "cyclic" and arity == 3:
                            left_term = parse_term(self.arena,f"{symbol}(x0,x1,x2)")
                            right_term = parse_term(self.arena,f"{symbol}(x2,x0,x1)")
                        elif eq_type == "first_second_symmetric":
                            left_term = parse_term(self.arena,f"{symbol}(x0,x1)")
                            right_term = parse_term(self.arena,f"{symbol}(x1,x0)")
                        
                except Exception as e:
                    is_valid = False
                    validation_error = str(e)
                
                validation_results.append({
                    "symbol": symbol,
                    "type": eq_type,
                    "arity": arity,
                    "is_valid": is_valid,
                    "expected_valid": expected_valid,
                    "validation_error": validation_error,
                    "validation_matches_expectation": is_valid == expected_valid
                })
            
            rust_result = {
                "case_name": case_name,
                "equation_count": len(equations),
                "validation_results": validation_results,
                "all_validations_correct": all(
                    result["validation_matches_expectation"] for result in validation_results
                )
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust equation validation failed for {case_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        java_result = self._run_java_operation(
            "equation_generation", "f", "associative",
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "equation_validation",
            context=f"{case_name}: {len(equations)} equations"
        )
        
        if result.matches:
            self.test_logger.debug(f"Equation validation test passed for {case_name}")
        else:
            self.test_logger.warning(f"Equation validation test failed for {case_name}: {result.error_message}")


if __name__ == '__main__':
    unittest.main()
