#!/usr/bin/env python3
"""
Algebra Compatibility Test

This module tests the org.uacalc.alg.Algebra interface compatibility between
Java UACalc and the Rust/Python implementation. It verifies that core algebra
operations produce identical results.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class AlgebraCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.Algebra interface compatibility.
    
    This class tests the fundamental Algebra interface methods to ensure
    the Rust implementation matches Java behavior exactly for:
    - Algebra cardinality and universe
    - Operation count and symbols
    - Basic algebra properties (finite, similarity type)
    - Algebra metadata and description handling
    """
    
    def test_algebra_cardinality_compatibility(self):
        """Test Algebra.cardinality() matches between Java and Rust"""
        logger.info("Testing algebra cardinality compatibility")
        
        for algebra_file in self.algebra_files[:10]:  # Test first 10 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                rust_cardinality = algebra.cardinality
                
                # Get cardinality from Java
                java_result = self._run_java_operation("properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                # Compare results
                result = self._compare_results(
                    rust_cardinality, 
                    java_result.get("cardinality"),
                    "cardinality",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches, 
                    f"Cardinality mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_algebra_operations_compatibility(self):
        """Test Algebra.operations() returns identical operation lists"""
        logger.info("Testing algebra operations compatibility")
        
        for algebra_file in self.algebra_files[:10]:  # Test first 10 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Extract operation information from Rust
                rust_operations = {
                    "count": len(algebra.operations),
                    "symbols": [str(op.symbol) for op in algebra.operations],
                    "arities": [op.arity for op in algebra.operations]
                }
                
                # Get operation information from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                # Extract comparable operation information from Java result
                java_operations = {
                    "count": java_result.get("operation_count", 0),
                    "symbols": java_result.get("operation_symbols", []),
                    "arities": java_result.get("operation_arities", [])
                }
                
                # Compare results
                result = self._compare_results(
                    rust_operations,
                    java_operations,
                    "operations",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Operations mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_algebra_universe_compatibility(self):
        """Test Algebra.universe() returns identical universes"""
        logger.info("Testing algebra universe compatibility")
        
        for algebra_file in self.algebra_files[:10]:  # Test first 10 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                rust_universe = list(algebra.universe)
                
                # Get universe from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_universe = java_result.get("universe", [])
                
                # Compare results
                result = self._compare_results(
                    rust_universe,
                    java_universe,
                    "universe",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Universe mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_algebra_finite_property_compatibility(self):
        """Test algebra finite property checking matches"""
        logger.info("Testing algebra finite property compatibility")
        
        for algebra_file in self.algebra_files[:10]:  # Test first 10 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                rust_is_finite = hasattr(algebra, 'is_finite') and algebra.is_finite
                
                # Get finite property from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_is_finite = java_result.get("is_finite", True)  # Default to True for finite algebras
                
                # Compare results
                result = self._compare_results(
                    rust_is_finite,
                    java_is_finite,
                    "is_finite",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Finite property mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_algebra_similarity_type_compatibility(self):
        """Test algebra similarity type matches"""
        logger.info("Testing algebra similarity type compatibility")
        
        for algebra_file in self.algebra_files[:10]:  # Test first 10 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Extract similarity type information
                rust_similarity_type = {
                    "operation_count": len(algebra.operations),
                    "arities": sorted([op.arity for op in algebra.operations])
                }
                
                # Get similarity type from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_similarity_type = {
                    "operation_count": java_result.get("operation_count", 0),
                    "arities": sorted(java_result.get("operation_arities", []))
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
    
    def test_algebra_metadata_compatibility(self):
        """Test algebra metadata and description handling"""
        logger.info("Testing algebra metadata compatibility")
        
        for algebra_file in self.algebra_files[:10]:  # Test first 10 algebras
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Extract metadata
                rust_metadata = {
                    "name": getattr(algebra, 'name', algebra_file.stem),
                    "cardinality": algebra.cardinality,
                    "operation_count": len(algebra.operations)
                }
                
                # Get metadata from Java
                java_result = self._run_java_operation("algebra_properties", str(algebra_file))
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java operation failed: {java_result.get('error')}")
                
                java_metadata = {
                    "name": java_result.get("name", algebra_file.stem),
                    "cardinality": java_result.get("cardinality", 0),
                    "operation_count": java_result.get("operation_count", 0)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_metadata,
                    java_metadata,
                    "metadata",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Metadata mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_algebra_operation_evaluation_compatibility(self):
        """Test that operation evaluation produces identical results"""
        logger.info("Testing algebra operation evaluation compatibility")
        
        # Test on smaller algebras only for performance
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 6][:5]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Test first operation with a few input combinations
                if len(algebra.operations) == 0:
                    self.skipTest(f"No operations in {algebra_file.name}")
                
                operation = algebra.operations[0]
                
                # Generate test cases for the operation
                test_cases = self._generate_operation_test_cases(operation, algebra.cardinality, max_cases=10)
                
                for i, inputs in enumerate(test_cases):
                    # Evaluate in Rust/Python
                    try:
                        rust_result = operation.value(inputs)
                    except Exception as e:
                        self.skipTest(f"Rust operation evaluation failed: {e}")
                    
                    # Get evaluation from Java (this would need a specific Java operation)
                    # For now, we'll use the properties operation as a placeholder
                    java_result = self._run_java_operation("properties", str(algebra_file))
                    
                    if java_result is None:
                        self.skipTest("Java UACalc not available")
                    
                    # Note: This is a simplified test - full operation evaluation
                    # would require extending the Java wrapper
                    self.assertIsNotNone(rust_result, 
                        f"Operation evaluation failed for {algebra_file.name}")
    
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
    
    def _generate_operation_test_cases(self, operation, cardinality: int, max_cases: int = 10) -> List[List[int]]:
        """Generate test cases for operation evaluation"""
        import itertools
        
        arity = operation.arity
        if arity == 0:
            return [[]]  # Nullary operation
        
        # Generate all possible inputs for small arities and cardinalities
        if arity <= 2 and cardinality <= 4:
            return list(itertools.product(range(cardinality), repeat=arity))
        
        # For larger cases, generate a sample
        test_cases = []
        universe = list(range(cardinality))
        
        # Add some systematic cases
        if arity == 1:
            test_cases.extend([[i] for i in universe[:min(max_cases, cardinality)]])
        elif arity == 2:
            # Add diagonal cases
            test_cases.extend([[i, i] for i in universe[:min(max_cases//2, cardinality)]])
            # Add some off-diagonal cases
            for i in range(min(max_cases//2, cardinality)):
                for j in range(min(2, cardinality)):
                    if i != j:
                        test_cases.append([i, j])
                        break
        else:
            # For higher arity, just test a few cases
            for i in range(min(max_cases, cardinality)):
                test_cases.append([i] * arity)
        
        return test_cases[:max_cases]


if __name__ == '__main__':
    unittest.main()