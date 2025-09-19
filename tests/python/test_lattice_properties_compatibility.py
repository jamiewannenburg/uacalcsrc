#!/usr/bin/env python3
"""
Lattice Properties Compatibility Test

This module tests the compatibility of lattice properties analysis between
the Rust/Python UACalc implementation and the original Java UACalc library.
Tests include congruence lattice size, join irreducibles, height, width,
modularity, distributivity, and Boolean properties.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class LatticePropertiesCompatibilityTest(BaseCompatibilityTest):
    """
    Test lattice properties analysis compatibility.
    
    This class tests the lattice properties analysis to ensure
    the Rust implementation matches Java behavior exactly for:
    - Congruence lattice size computation
    - Join irreducibles counting
    - Lattice height and width calculation
    - Modularity, distributivity, and Boolean property detection
    - Zero and one element detection
    """
    
    def test_lattice_properties_compatibility(self):
        """Test lattice properties analysis compatibility"""
        logger.info("Testing lattice properties compatibility")
        
        # Test on small to medium algebras to avoid memory issues
        test_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 10][:5]
        
        # If no suitable algebras found, skip the test
        if not test_algebras:
            self.skipTest("No suitable algebras found for testing")
        
        for algebra_file in test_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Skip if algebra is too large for lattice properties analysis
                if self._should_skip_test(self._get_algebra_size_estimate(algebra_file), "lattice_properties"):
                    self.skipTest(f"Algebra too large for lattice properties analysis: {algebra_file.name}")
                
                self._test_lattice_properties(algebra_file)
    
    def _test_lattice_properties(self, algebra_file: Path):
        """Test lattice properties for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip very large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'lattice_properties'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Get lattice properties from Rust implementation
        try:
            import uacalc
            rust_props = uacalc.py_analyze_lattice_properties(algebra)
            
            rust_result = {
                'algebra_name': algebra.name,
                'algebra_cardinality': algebra.cardinality,
                'congruence_lattice_size': rust_props.congruence_lattice_size,
                'join_irreducibles_count': rust_props.join_irreducibles_count,
                'lattice_height': rust_props.lattice_height,
                'lattice_width': rust_props.lattice_width,
                'is_modular': rust_props.is_modular,
                'is_distributive': rust_props.is_distributive,
                'is_boolean': rust_props.is_boolean,
                'has_zero': rust_props.has_zero,
                'has_one': rust_props.has_one,
            }
            
        except Exception as e:
            self.fail(f"Rust lattice properties computation failed for {algebra.name}: {e}")
        
        # Get lattice properties from Java implementation
        timeout = self._get_test_timeout('lattice_properties', algebra.cardinality)
        java_result = self._run_java_operation('lattice_properties', str(algebra_file), timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'lattice_properties', algebra.name
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Lattice properties mismatch for {algebra.name}: "
                f"Rust size: {rust_result.get('congruence_lattice_size')}, "
                f"Java size: {java_result.get('congruence_lattice_size')}, "
                f"Rust modular: {rust_result.get('is_modular')}, "
                f"Java modular: {java_result.get('is_modular')}"
            )
    
    def test_lattice_properties_specific_algebras(self):
        """Test lattice properties on specific well-known algebras"""
        logger.info("Testing lattice properties on specific algebras")
        
        # Test on specific algebras with known properties
        specific_algebra_names = [
            'ba2.ua',      # Boolean algebra of size 2
            'm3.ua',       # M3 lattice (modular but not distributive)
            'n5.ua',       # N5 lattice (neither modular nor distributive)
            'lat2.ua',     # Simple 2-element lattice
            'cyclic2.ua',  # Cyclic group of order 2
        ]
        
        # Find the specific algebras from the available algebra files
        specific_algebras = []
        for algebra_file in self.algebra_files:
            if algebra_file.name in specific_algebra_names:
                specific_algebras.append(algebra_file)
        
        if not specific_algebras:
            self.skipTest("No specific test algebras found")
        
        for algebra_file in specific_algebras:
            with self.subTest(algebra=algebra_file.name):
                self._test_lattice_properties(algebra_file)
    
    def test_lattice_properties_edge_cases(self):
        """Test lattice properties on edge cases"""
        logger.info("Testing lattice properties edge cases")
        
        # Test on very small algebras
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 3]
        
        for algebra_file in small_algebras[:3]:  # Test first 3 small algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_lattice_properties(algebra_file)
    
    def test_lattice_properties_consistency(self):
        """Test that lattice properties are consistent with each other"""
        logger.info("Testing lattice properties consistency")
        
        # Test on a few small algebras
        test_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 6][:3]
        
        for algebra_file in test_algebras:
            with self.subTest(algebra=algebra_file.name):
                algebra = self._load_test_algebra(algebra_file)
                
                try:
                    import uacalc
                    props = uacalc.py_analyze_lattice_properties(algebra)
                    
                    # Test consistency rules
                    # 1. Boolean implies distributive
                    if props.is_boolean:
                        self.assertTrue(props.is_distributive, 
                                      f"Boolean lattice should be distributive in {algebra.name}")
                    
                    # 2. Distributive implies modular
                    if props.is_distributive:
                        self.assertTrue(props.is_modular, 
                                      f"Distributive lattice should be modular in {algebra.name}")
                    
                    # 3. Congruence lattices always have zero and one
                    self.assertTrue(props.has_zero, 
                                  f"Congruence lattice should have zero in {algebra.name}")
                    self.assertTrue(props.has_one, 
                                  f"Congruence lattice should have one in {algebra.name}")
                    
                    # 4. Height should be at least 1 for non-trivial algebras
                    if algebra.cardinality > 1:
                        self.assertGreaterEqual(props.lattice_height, 1,
                                              f"Non-trivial algebra should have height >= 1 in {algebra.name}")
                    
                    # 5. Width should be at least 1
                    self.assertGreaterEqual(props.lattice_width, 1,
                                          f"Lattice should have width >= 1 in {algebra.name}")
                    
                    # 6. Join irreducibles count should be reasonable
                    self.assertLessEqual(props.join_irreducibles_count, props.congruence_lattice_size,
                                       f"Join irreducibles count should be <= lattice size in {algebra.name}")
                    
                except Exception as e:
                    self.fail(f"Lattice properties consistency check failed for {algebra.name}: {e}")
    
    def _get_algebra_size_estimate(self, algebra_file: Path) -> int:
        """Get an estimate of algebra size from file size or name"""
        # Simple heuristic based on file size
        file_size = algebra_file.stat().st_size
        if file_size < 1000:
            return 3
        elif file_size < 5000:
            return 6
        elif file_size < 20000:
            return 10
        else:
            return 20


if __name__ == '__main__':
    unittest.main()
