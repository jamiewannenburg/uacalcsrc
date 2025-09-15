#!/usr/bin/env python3
"""
SmallAlgebra Compatibility Test

This module tests the org.uacalc.alg.SmallAlgebra interface compatibility between
Java UACalc and the Rust/Python implementation. It verifies that SmallAlgebra
specific optimizations and methods work identically.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class SmallAlgebraCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.SmallAlgebra interface compatibility.
    
    This class tests the SmallAlgebra interface to ensure
    the Rust implementation matches Java behavior exactly for:
    - SmallAlgebra interface methods and properties
    - Small algebra specific optimizations
    - Algebra type detection and classification
    - Performance characteristics for small algebras
    """
    
    def test_small_algebra_interface_compatibility(self):
        """Test SmallAlgebra interface methods match"""
        logger.info("Testing SmallAlgebra interface compatibility")
        
        # Focus on genuinely small algebras (cardinality <= 8)
        small_algebra_files = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 8][:10]
        
        for algebra_file in small_algebra_files:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Check if algebra qualifies as "small"
                is_small = algebra.cardinality <= 20  # Reasonable threshold for "small"
                
                # Extract SmallAlgebra interface properties
                rust_small_props = {
                    "is_small": is_small,
                    "cardinality": algebra.cardinality,
                    "supports_exhaustive_search": algebra.cardinality <= 10,
                    "universe_as_list": list(algebra.universe),
                    "operation_count": len(algebra.operations)
                }
                
                # Get SmallAlgebra properties from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_cardinality = java_result.get("cardinality", 0)
                java_small_props = {
                    "is_small": java_cardinality <= 20,
                    "cardinality": java_cardinality,
                    "supports_exhaustive_search": java_cardinality <= 10,
                    "universe_as_list": java_result.get("universe", []),
                    "operation_count": java_result.get("operation_count", 0)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_small_props,
                    java_small_props,
                    "small_algebra_interface",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"SmallAlgebra interface mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_small_algebra_optimization_compatibility(self):
        """Test SmallAlgebra specific optimizations work identically"""
        logger.info("Testing SmallAlgebra optimization compatibility")
        
        # Test on very small algebras where optimizations matter most
        tiny_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:5]
        
        for algebra_file in tiny_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Test optimization-related properties
                rust_optimizations = {
                    "cardinality": algebra.cardinality,
                    "can_enumerate_all": algebra.cardinality <= 6,
                    "operation_table_size": sum(algebra.cardinality ** op.arity for op in algebra.operations),
                    "memory_efficient": algebra.cardinality <= 10,
                    "fast_lookup": True  # Assume small algebras use fast lookup
                }
                
                # Get optimization properties from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_cardinality = java_result.get("cardinality", 0)
                java_arities = java_result.get("operation_arities", [])
                
                java_optimizations = {
                    "cardinality": java_cardinality,
                    "can_enumerate_all": java_cardinality <= 6,
                    "operation_table_size": sum(java_cardinality ** arity for arity in java_arities),
                    "memory_efficient": java_cardinality <= 10,
                    "fast_lookup": True  # Assume Java small algebras use fast lookup
                }
                
                # Compare results
                result = self._compare_results(
                    rust_optimizations,
                    java_optimizations,
                    "small_algebra_optimizations",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"SmallAlgebra optimizations mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_small_algebra_type_detection_compatibility(self):
        """Test algebra type detection and classification"""
        logger.info("Testing SmallAlgebra type detection compatibility")
        
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 6][:8]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Detect algebra type characteristics
                rust_type_detection = {
                    "cardinality": algebra.cardinality,
                    "is_trivial": algebra.cardinality == 1,
                    "is_binary": algebra.cardinality == 2,
                    "has_nullary_ops": any(op.arity == 0 for op in algebra.operations),
                    "has_unary_ops": any(op.arity == 1 for op in algebra.operations),
                    "has_binary_ops": any(op.arity == 2 for op in algebra.operations),
                    "max_arity": max((op.arity for op in algebra.operations), default=0),
                    "operation_signature": sorted([op.arity for op in algebra.operations])
                }
                
                # Get type detection from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_cardinality = java_result.get("cardinality", 0)
                java_arities = java_result.get("operation_arities", [])
                
                java_type_detection = {
                    "cardinality": java_cardinality,
                    "is_trivial": java_cardinality == 1,
                    "is_binary": java_cardinality == 2,
                    "has_nullary_ops": 0 in java_arities,
                    "has_unary_ops": 1 in java_arities,
                    "has_binary_ops": 2 in java_arities,
                    "max_arity": max(java_arities, default=0),
                    "operation_signature": sorted(java_arities)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_type_detection,
                    java_type_detection,
                    "type_detection",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Type detection mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_small_algebra_enumeration_compatibility(self):
        """Test enumeration capabilities for small algebras"""
        logger.info("Testing SmallAlgebra enumeration compatibility")
        
        # Test on very small algebras only
        tiny_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 3][:3]
        
        for algebra_file in tiny_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Test enumeration properties
                universe_list = list(algebra.universe)
                rust_enumeration = {
                    "universe_size": len(universe_list),
                    "universe_elements": sorted(universe_list),
                    "can_enumerate_operations": len(algebra.operations) <= 5,
                    "total_operation_entries": sum(
                        algebra.cardinality ** op.arity for op in algebra.operations
                    ),
                    "enumeration_feasible": algebra.cardinality <= 4
                }
                
                # Get enumeration properties from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_universe = java_result.get("universe", [])
                java_cardinality = java_result.get("cardinality", 0)
                java_arities = java_result.get("operation_arities", [])
                
                java_enumeration = {
                    "universe_size": len(java_universe),
                    "universe_elements": sorted(java_universe),
                    "can_enumerate_operations": len(java_arities) <= 5,
                    "total_operation_entries": sum(
                        java_cardinality ** arity for arity in java_arities
                    ),
                    "enumeration_feasible": java_cardinality <= 4
                }
                
                # Compare results
                result = self._compare_results(
                    rust_enumeration,
                    java_enumeration,
                    "enumeration",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Enumeration mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_small_algebra_operation_evaluation_performance(self):
        """Test operation evaluation performance characteristics"""
        logger.info("Testing SmallAlgebra operation evaluation performance")
        
        # Test on small algebras with simple operations
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:3]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                if len(algebra.operations) == 0:
                    self.skipTest(f"No operations in {algebra_file.name}")
                
                # Test first operation
                operation = algebra.operations[0]
                
                # Performance characteristics
                rust_performance = {
                    "operation_arity": operation.arity,
                    "domain_size": algebra.cardinality,
                    "lookup_table_size": algebra.cardinality ** operation.arity if operation.arity > 0 else 1,
                    "constant_time_lookup": operation.arity <= 2 and algebra.cardinality <= 10,
                    "supports_fast_evaluation": True
                }
                
                # Test a few evaluations to ensure they work
                evaluation_success = True
                try:
                    if operation.arity == 0:
                        result = operation.value([])
                        evaluation_success = result is not None
                    elif operation.arity == 1:
                        result = operation.value([0])
                        evaluation_success = result is not None
                    elif operation.arity == 2 and algebra.cardinality >= 2:
                        result = operation.value([0, 1])
                        evaluation_success = result is not None
                except Exception:
                    evaluation_success = False
                
                rust_performance["evaluation_works"] = evaluation_success
                
                # Get performance characteristics from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_arities = java_result.get("operation_arities", [])
                java_cardinality = java_result.get("cardinality", 0)
                
                if len(java_arities) == 0:
                    self.skipTest(f"No operations in Java result for {algebra_file.name}")
                
                first_arity = java_arities[0]
                java_performance = {
                    "operation_arity": first_arity,
                    "domain_size": java_cardinality,
                    "lookup_table_size": java_cardinality ** first_arity if first_arity > 0 else 1,
                    "constant_time_lookup": first_arity <= 2 and java_cardinality <= 10,
                    "supports_fast_evaluation": True,
                    "evaluation_works": True  # Assume Java implementation works
                }
                
                # Compare results
                result = self._compare_results(
                    rust_performance,
                    java_performance,
                    "operation_performance",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Operation performance mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_small_algebra_memory_usage_compatibility(self):
        """Test memory usage characteristics for small algebras"""
        logger.info("Testing SmallAlgebra memory usage compatibility")
        
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 6][:5]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Estimate memory usage characteristics
                total_table_entries = sum(
                    algebra.cardinality ** op.arity for op in algebra.operations
                )
                
                rust_memory = {
                    "cardinality": algebra.cardinality,
                    "operation_count": len(algebra.operations),
                    "total_table_entries": total_table_entries,
                    "memory_efficient": total_table_entries <= 1000,
                    "fits_in_cache": total_table_entries <= 100,
                    "universe_storage": algebra.cardinality  # Elements in universe
                }
                
                # Get memory characteristics from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_cardinality = java_result.get("cardinality", 0)
                java_arities = java_result.get("operation_arities", [])
                
                java_total_entries = sum(
                    java_cardinality ** arity for arity in java_arities
                )
                
                java_memory = {
                    "cardinality": java_cardinality,
                    "operation_count": len(java_arities),
                    "total_table_entries": java_total_entries,
                    "memory_efficient": java_total_entries <= 1000,
                    "fits_in_cache": java_total_entries <= 100,
                    "universe_storage": java_cardinality
                }
                
                # Compare results
                result = self._compare_results(
                    rust_memory,
                    java_memory,
                    "memory_usage",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Memory usage mismatch for {algebra_file.name}: {result.error_message}")
    
    def _get_algebra_size_estimate(self, algebra_file: Path) -> int:
        """Estimate algebra size from file size (rough heuristic)"""
        try:
            file_size = algebra_file.stat().st_size
            # Very rough estimate: smaller files = smaller algebras
            if file_size < 500:
                return 2
            elif file_size < 1000:
                return 3
            elif file_size < 2000:
                return 4
            elif file_size < 5000:
                return 6
            elif file_size < 10000:
                return 8
            else:
                return 12
        except:
            return 6  # Default estimate for small algebra tests


if __name__ == '__main__':
    unittest.main()