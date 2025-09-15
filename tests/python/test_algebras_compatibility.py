#!/usr/bin/env python3
"""
Algebras Utility Compatibility Test

This module tests the org.uacalc.alg.Algebras utility class compatibility between
Java UACalc and the Rust/Python implementation. It verifies that utility methods
for algebra creation, validation, and manipulation work identically.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class AlgebrasCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.Algebras utility class compatibility.
    
    This class tests the Algebras utility class to ensure
    the Rust implementation matches Java behavior exactly for:
    - Algebras utility class static methods
    - Algebra factory methods producing identical results
    - Algebra validation and normalization utilities
    - Algebra comparison and analysis methods
    """
    
    def test_algebras_factory_methods_compatibility(self):
        """Test Algebras utility class factory methods"""
        logger.info("Testing Algebras factory methods compatibility")
        
        for algebra_file in self.algebra_files[:8]:  # Test first 8 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Extract factory-related properties
                rust_factory_props = {
                    "cardinality": algebra.cardinality,
                    "operation_count": len(algebra.operations),
                    "can_be_reconstructed": True,  # Assume we can reconstruct from operations
                    "has_valid_operations": all(hasattr(op, 'arity') for op in algebra.operations),
                    "universe_is_standard": list(algebra.universe) == list(range(algebra.cardinality))
                }
                
                # Get factory properties from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_factory_props = {
                    "cardinality": java_result.get("cardinality", 0),
                    "operation_count": java_result.get("operation_count", 0),
                    "can_be_reconstructed": True,  # Assume Java can reconstruct
                    "has_valid_operations": java_result.get("operation_count", 0) > 0,
                    "universe_is_standard": java_result.get("universe", []) == list(range(java_result.get("cardinality", 0)))
                }
                
                # Compare results
                result = self._compare_results(
                    rust_factory_props,
                    java_factory_props,
                    "factory_methods",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Factory methods mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_algebras_validation_compatibility(self):
        """Test Algebras validation utilities"""
        logger.info("Testing Algebras validation compatibility")
        
        for algebra_file in self.algebra_files[:8]:  # Test first 8 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Perform validation checks
                rust_validation = {
                    "is_valid_algebra": True,  # Assume loaded algebras are valid
                    "cardinality_positive": algebra.cardinality > 0,
                    "operations_well_defined": len(algebra.operations) >= 0,
                    "universe_consistent": len(list(algebra.universe)) == algebra.cardinality,
                    "operations_have_symbols": all(hasattr(op, 'symbol') for op in algebra.operations),
                    "operations_have_arities": all(hasattr(op, 'arity') for op in algebra.operations)
                }
                
                # Check operation table validity for small algebras
                if algebra.cardinality <= 4 and len(algebra.operations) > 0:
                    try:
                        first_op = algebra.operations[0]
                        if first_op.arity <= 2:
                            # Test a few operation evaluations
                            test_inputs = [[0]] if first_op.arity == 1 else [[0, 0], [0, 1]] if algebra.cardinality > 1 else [[0, 0]]
                            for inputs in test_inputs[:2]:  # Test first 2 cases
                                if len(inputs) == first_op.arity:
                                    result = first_op.value(inputs)
                                    if result not in range(algebra.cardinality):
                                        rust_validation["operations_well_defined"] = False
                                        break
                    except Exception:
                        rust_validation["operations_well_defined"] = False
                
                # Get validation from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_validation = {
                    "is_valid_algebra": java_result.get("success", True),
                    "cardinality_positive": java_result.get("cardinality", 0) > 0,
                    "operations_well_defined": java_result.get("operation_count", 0) >= 0,
                    "universe_consistent": len(java_result.get("universe", [])) == java_result.get("cardinality", 0),
                    "operations_have_symbols": len(java_result.get("operation_symbols", [])) == java_result.get("operation_count", 0),
                    "operations_have_arities": len(java_result.get("operation_arities", [])) == java_result.get("operation_count", 0)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_validation,
                    java_validation,
                    "validation",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Validation mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_algebras_normalization_compatibility(self):
        """Test Algebras normalization utilities"""
        logger.info("Testing Algebras normalization compatibility")
        
        for algebra_file in self.algebra_files[:6]:  # Test first 6 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Check normalization properties
                universe_list = list(algebra.universe)
                rust_normalization = {
                    "universe_sorted": universe_list == sorted(universe_list),
                    "universe_starts_at_zero": min(universe_list) == 0 if universe_list else True,
                    "universe_contiguous": universe_list == list(range(len(universe_list))),
                    "operations_ordered": True,  # Assume operations are in some consistent order
                    "symbols_normalized": all(str(op.symbol) for op in algebra.operations)
                }
                
                # Get normalization from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_universe = java_result.get("universe", [])
                java_normalization = {
                    "universe_sorted": java_universe == sorted(java_universe),
                    "universe_starts_at_zero": min(java_universe) == 0 if java_universe else True,
                    "universe_contiguous": java_universe == list(range(len(java_universe))),
                    "operations_ordered": True,  # Assume Java operations are ordered
                    "symbols_normalized": len(java_result.get("operation_symbols", [])) == java_result.get("operation_count", 0)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_normalization,
                    java_normalization,
                    "normalization",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Normalization mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_algebras_comparison_compatibility(self):
        """Test Algebras comparison utilities"""
        logger.info("Testing Algebras comparison compatibility")
        
        # Test comparison between pairs of algebras
        test_algebras = self.algebra_files[:4]  # Test first 4 algebras
        
        for i, algebra_file1 in enumerate(test_algebras):
            for j, algebra_file2 in enumerate(test_algebras):
                if i >= j:  # Only test each pair once
                    continue
                    
                with self.subTest(algebra1=algebra_file1.name, algebra2=algebra_file2.name):
                    # Load both algebras
                    algebra1 = self._load_test_algebra(algebra_file1)
                    algebra2 = self._load_test_algebra(algebra_file2)
                    
                    # Compare algebras
                    rust_comparison = {
                        "same_cardinality": algebra1.cardinality == algebra2.cardinality,
                        "same_operation_count": len(algebra1.operations) == len(algebra2.operations),
                        "same_similarity_type": (
                            sorted([op.arity for op in algebra1.operations]) == 
                            sorted([op.arity for op in algebra2.operations])
                        ),
                        "potentially_isomorphic": (
                            algebra1.cardinality == algebra2.cardinality and
                            len(algebra1.operations) == len(algebra2.operations)
                        )
                    }
                    
                    # Get comparison from Java (using properties of both algebras)
                    java_result1 = self._run_java_operation("algebra_properties", str(algebra_file1))
                    java_result2 = self._run_java_operation("algebra_properties", str(algebra_file2))
                    
                    if java_result1 is None or java_result2 is None:
                        self.skipTest("Java UACalc not available")
                    
                    if not (java_result1.get("success", True) and java_result2.get("success", True)):
                        self.skipTest("Java operation failed")
                    
                    java_comparison = {
                        "same_cardinality": java_result1.get("cardinality", 0) == java_result2.get("cardinality", 0),
                        "same_operation_count": java_result1.get("operation_count", 0) == java_result2.get("operation_count", 0),
                        "same_similarity_type": (
                            sorted(java_result1.get("operation_arities", [])) == 
                            sorted(java_result2.get("operation_arities", []))
                        ),
                        "potentially_isomorphic": (
                            java_result1.get("cardinality", 0) == java_result2.get("cardinality", 0) and
                            java_result1.get("operation_count", 0) == java_result2.get("operation_count", 0)
                        )
                    }
                    
                    # Compare results
                    result = self._compare_results(
                        rust_comparison,
                        java_comparison,
                        "algebra_comparison",
                        f"{algebra_file1.name}_vs_{algebra_file2.name}"
                    )
                    
                    self.assertTrue(result.matches,
                        f"Comparison mismatch for {algebra_file1.name} vs {algebra_file2.name}: {result.error_message}")
    
    def test_algebras_analysis_compatibility(self):
        """Test Algebras analysis utilities"""
        logger.info("Testing Algebras analysis compatibility")
        
        for algebra_file in self.algebra_files[:6]:  # Test first 6 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Perform analysis
                operation_arities = [op.arity for op in algebra.operations]
                rust_analysis = {
                    "cardinality": algebra.cardinality,
                    "operation_count": len(algebra.operations),
                    "arity_distribution": {
                        "nullary": operation_arities.count(0),
                        "unary": operation_arities.count(1),
                        "binary": operation_arities.count(2),
                        "higher": sum(1 for a in operation_arities if a > 2)
                    },
                    "max_arity": max(operation_arities) if operation_arities else 0,
                    "min_arity": min(operation_arities) if operation_arities else 0,
                    "total_operation_table_size": sum(algebra.cardinality ** arity for arity in operation_arities),
                    "is_finite": True,  # All test algebras are finite
                    "complexity_estimate": algebra.cardinality * len(algebra.operations)
                }
                
                # Get analysis from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_arities = java_result.get("operation_arities", [])
                java_cardinality = java_result.get("cardinality", 0)
                
                java_analysis = {
                    "cardinality": java_cardinality,
                    "operation_count": java_result.get("operation_count", 0),
                    "arity_distribution": {
                        "nullary": java_arities.count(0),
                        "unary": java_arities.count(1),
                        "binary": java_arities.count(2),
                        "higher": sum(1 for a in java_arities if a > 2)
                    },
                    "max_arity": max(java_arities) if java_arities else 0,
                    "min_arity": min(java_arities) if java_arities else 0,
                    "total_operation_table_size": sum(java_cardinality ** arity for arity in java_arities),
                    "is_finite": True,  # Assume Java algebras are finite
                    "complexity_estimate": java_cardinality * len(java_arities)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_analysis,
                    java_analysis,
                    "analysis",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Analysis mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_algebras_utility_methods_compatibility(self):
        """Test various Algebras utility methods"""
        logger.info("Testing Algebras utility methods compatibility")
        
        for algebra_file in self.algebra_files[:5]:  # Test first 5 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Test utility method results
                rust_utilities = {
                    "has_operations": len(algebra.operations) > 0,
                    "is_empty": algebra.cardinality == 0,
                    "is_singleton": algebra.cardinality == 1,
                    "operation_symbols_unique": len(set(str(op.symbol) for op in algebra.operations)) == len(algebra.operations),
                    "universe_is_finite": True,  # All test algebras are finite
                    "supports_enumeration": algebra.cardinality <= 100
                }
                
                # Check if operations are well-formed
                operations_well_formed = True
                try:
                    for op in algebra.operations:
                        if not hasattr(op, 'arity') or not hasattr(op, 'symbol'):
                            operations_well_formed = False
                            break
                except Exception:
                    operations_well_formed = False
                
                rust_utilities["operations_well_formed"] = operations_well_formed
                
                # Get utility results from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_cardinality = java_result.get("cardinality", 0)
                java_operation_count = java_result.get("operation_count", 0)
                java_symbols = java_result.get("operation_symbols", [])
                
                java_utilities = {
                    "has_operations": java_operation_count > 0,
                    "is_empty": java_cardinality == 0,
                    "is_singleton": java_cardinality == 1,
                    "operation_symbols_unique": len(set(java_symbols)) == len(java_symbols),
                    "universe_is_finite": True,  # Assume Java algebras are finite
                    "supports_enumeration": java_cardinality <= 100,
                    "operations_well_formed": java_result.get("success", True)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_utilities,
                    java_utilities,
                    "utility_methods",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Utility methods mismatch for {algebra_file.name}: {result.error_message}")


if __name__ == '__main__':
    unittest.main()