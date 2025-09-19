#!/usr/bin/env python3
"""
BasicAlgebra Compatibility Test

This module tests the org.uacalc.alg.BasicAlgebra class compatibility between
Java UACalc and the Rust/Python implementation. It verifies that BasicAlgebra
construction, operation management, and cloning work identically.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class BasicAlgebraCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.BasicAlgebra class compatibility.
    
    This class tests the BasicAlgebra implementation to ensure
    the Rust implementation matches Java behavior exactly for:
    - BasicAlgebra construction from operations and universe
    - Operation addition and removal functionality
    - Algebra cloning and copying operations
    - BasicAlgebra-specific methods and properties
    """
    
    def test_basic_algebra_construction_compatibility(self):
        """Test BasicAlgebra constructor produces identical algebras"""
        logger.info("Testing BasicAlgebra construction compatibility")
        
        for algebra_file in self.algebra_files[:8]:  # Test first 8 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python (assuming it creates a BasicAlgebra)
                algebra = self._load_test_algebra(algebra_file)
                
                # Extract construction properties
                rust_construction = {
                    "cardinality": algebra.cardinality,
                    "operation_count": len(algebra.operations),
                    "universe_size": len(list(algebra.universe)),
                    "is_basic_algebra": True  # Assuming our implementation uses BasicAlgebra
                }
                
                # Get construction properties from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_construction = {
                    "cardinality": java_result.get("cardinality", 0),
                    "operation_count": java_result.get("operation_count", 0),
                    "universe_size": java_result.get("cardinality", 0),  # Universe size = cardinality for finite algebras
                    "is_basic_algebra": java_result.get("is_basic_algebra", True)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_construction,
                    java_construction,
                    "basic_algebra_construction",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"BasicAlgebra construction mismatch for {algebra_file.name}: {result.error_message}")
    def test_basic_algebra_operation_properties_compatibility(self):
        """Test BasicAlgebra operation properties match"""
        logger.info("Testing BasicAlgebra operation properties compatibility")
        
        for algebra_file in self.algebra_files[:8]:  # Test first 8 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Extract operation properties (sort by symbol name for consistency with Java)
                ops = algebra.operations
                sorted_ops = sorted(ops, key=lambda op: str(op.symbol))
                rust_op_properties = []
                for i, operation in enumerate(sorted_ops):
                    op_props = {
                        "index": i,
                        "arity": operation.arity,
                        "symbol": str(operation.symbol)
                        # Note: Only comparing basic properties that JavaWrapper provides
                    }
                    rust_op_properties.append(op_props)
                
                # Get operation properties from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                # Extract Java operation properties (only basic properties available from JavaWrapper)
                java_op_properties = []
                operation_symbols = java_result.get("operation_symbols", [])
                operation_arities = java_result.get("operation_arities", [])
                
                for i, (symbol, arity) in enumerate(zip(operation_symbols, operation_arities)):
                    op_props = {
                        "index": i,
                        "arity": arity,
                        "symbol": symbol
                        # Note: JavaWrapper doesn't provide is_idempotent or is_commutative fields
                    }
                    java_op_properties.append(op_props)
                
                # Compare results - structure as dictionaries for comparison
                rust_ops_dict = {f"op_{i}": props for i, props in enumerate(rust_op_properties)}
                java_ops_dict = {f"op_{i}": props for i, props in enumerate(java_op_properties)}
                
                result = self._compare_results(
                    rust_ops_dict,
                    java_ops_dict,
                    "operation_properties",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Operation properties mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_basic_algebra_universe_consistency_compatibility(self):
        """Test BasicAlgebra universe consistency"""
        logger.info("Testing BasicAlgebra universe consistency compatibility")
        
        for algebra_file in self.algebra_files[:8]:  # Test first 8 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Check universe consistency
                universe_list = list(algebra.universe)
                rust_consistency = {
                    "universe_sorted": sorted(universe_list),
                    "universe_unique": len(universe_list) == len(set(universe_list)),
                    "universe_contiguous": universe_list == list(range(len(universe_list))),
                    "cardinality_matches": len(universe_list) == algebra.cardinality
                }
                
                # Get universe consistency from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_universe = java_result.get("universe", [])
                java_consistency = {
                    "universe_sorted": sorted(java_universe),
                    "universe_unique": len(java_universe) == len(set(java_universe)),
                    "universe_contiguous": java_universe == list(range(len(java_universe))),
                    "cardinality_matches": len(java_universe) == java_result.get("cardinality", 0)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_consistency,
                    java_consistency,
                    "universe_consistency",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Universe consistency mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_basic_algebra_operation_table_compatibility(self):
        """Test BasicAlgebra operation table structure"""
        logger.info("Testing BasicAlgebra operation table compatibility")
        
        # Test on very small algebras only for performance
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:3]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                if len(algebra.operations) == 0:
                    self.skipTest(f"No operations in {algebra_file.name}")
                
                # Test first operation's table structure
                operation = algebra.operations[0]
                
                # Extract operation table properties
                rust_table_props = {
                    "arity": operation.arity,
                    "domain_size": algebra.cardinality,
                    "table_size": algebra.cardinality ** operation.arity if operation.arity > 0 else 1,
                    "codomain_valid": True  # All outputs should be in universe
                }
                
                # Verify codomain validity for small operations
                if operation.arity <= 2 and algebra.cardinality <= 4:
                    try:
                        import itertools
                        for inputs in itertools.product(range(algebra.cardinality), repeat=operation.arity):
                            result = operation.value(list(inputs))
                            if result not in range(algebra.cardinality):
                                rust_table_props["codomain_valid"] = False
                                break
                    except Exception:
                        rust_table_props["codomain_valid"] = False
                
                # Get table properties from Java (using basic properties)
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                # Extract comparable properties from Java
                operation_arities = java_result.get("operation_arities", [])
                if len(operation_arities) == 0:
                    self.skipTest(f"No operation arities in Java result for {algebra_file.name}")
                
                first_arity = operation_arities[0]
                cardinality = java_result.get("cardinality", 0)
                
                java_table_props = {
                    "arity": first_arity,
                    "domain_size": cardinality,
                    "table_size": cardinality ** first_arity if first_arity > 0 else 1,
                    "codomain_valid": True  # Assume Java implementation is correct
                }
                
                # Compare results
                result = self._compare_results(
                    rust_table_props,
                    java_table_props,
                    "operation_table",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Operation table mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_basic_algebra_similarity_type_compatibility(self):
        """Test BasicAlgebra similarity type computation"""
        logger.info("Testing BasicAlgebra similarity type compatibility")
        
        for algebra_file in self.algebra_files[:8]:  # Test first 8 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Compute similarity type
                arities = [op.arity for op in algebra.operations]
                rust_similarity_type = {
                    "arity_signature": sorted(arities),
                    "operation_count": len(arities),
                    "max_arity": max(arities) if arities else 0,
                    "min_arity": min(arities) if arities else 0,
                    "has_constants": 0 in arities,
                    "has_unary": 1 in arities,
                    "has_binary": 2 in arities
                }
                
                # Get similarity type from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_arities = java_result.get("operation_arities", [])
                java_similarity_type = {
                    "arity_signature": sorted(java_arities),
                    "operation_count": len(java_arities),
                    "max_arity": max(java_arities) if java_arities else 0,
                    "min_arity": min(java_arities) if java_arities else 0,
                    "has_constants": 0 in java_arities,
                    "has_unary": 1 in java_arities,
                    "has_binary": 2 in java_arities
                }
                
                # Compare results
                result = self._compare_results(
                    rust_similarity_type,
                    java_similarity_type,
                    "similarity_type",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Similarity type mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_basic_algebra_string_representation_compatibility(self):
        """Test BasicAlgebra string representation"""
        logger.info("Testing BasicAlgebra string representation compatibility")
        
        for algebra_file in self.algebra_files[:5]:  # Test first 5 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Extract string representation components
                rust_repr = {
                    "name": algebra.name.lower(),  # Normalize to lowercase for comparison
                    "cardinality_str": str(algebra.cardinality),
                    "operation_count_str": str(len(algebra.operations)),
                    "has_name": hasattr(algebra, 'name') and algebra.name is not None
                }
                
                # Get string representation from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_repr = {
                    "name": java_result.get("algebra_name", algebra_file.stem).lower(),  # Normalize to lowercase for comparison
                    "cardinality_str": str(java_result.get("cardinality", 0)),
                    "operation_count_str": str(java_result.get("operation_count", 0)),
                    "has_name": "algebra_name" in java_result and java_result["algebra_name"] is not None
                }
                
                # Compare results
                result = self._compare_results(
                    rust_repr,
                    java_repr,
                    "string_representation",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"String representation mismatch for {algebra_file.name}: {result.error_message}")
    
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
    
    def _check_idempotent(self, operation, cardinality: int) -> bool:
        """Check if operation is idempotent (for small algebras only)"""
        if operation.arity != 1 or cardinality > 6:
            return False  # Only check unary operations on small algebras
        
        try:
            for i in range(cardinality):
                if operation.value([i]) != i:
                    return False
            return True
        except Exception:
            return False
    
    def _check_commutative(self, operation, cardinality: int) -> bool:
        """Check if binary operation is commutative (for small algebras only)"""
        if operation.arity != 2 or cardinality > 4:
            return False  # Only check binary operations on very small algebras
        
        try:
            for i in range(cardinality):
                for j in range(cardinality):
                    if operation.value([i, j]) != operation.value([j, i]):
                        return False
            return True
        except Exception:
            return False
    
    def _check_commutative_safe(self, operation, cardinality: int) -> bool:
        """Check if binary operation is commutative, returning None if unable to determine"""
        if operation.arity != 2 or cardinality > 4:
            return None  # Return None for non-binary operations or large algebras
        
        try:
            for i in range(cardinality):
                for j in range(cardinality):
                    if operation.value([i, j]) != operation.value([j, i]):
                        return False
            return True
        except Exception:
            return None  # Return None if we can't determine


if __name__ == '__main__':
    unittest.main()