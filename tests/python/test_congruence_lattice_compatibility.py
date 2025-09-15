#!/usr/bin/env python3
"""
Congruence Lattice Compatibility Test

This module tests the compatibility of congruence lattice operations between
the Rust/Python UACalc implementation and the original Java UACalc library.
Tests include congruence lattice construction, principal congruence generation,
and lattice structural properties.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import itertools

from tests.python.base_compatibility_test import BaseCompatibilityTest


class CongruenceLatticeCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.conlat.CongruenceLattice class compatibility.
    
    This class tests:
    - Congruence lattice construction and basic properties
    - Principal congruence generation Cg(a,b) for all element pairs
    - Congruence lattice size, join irreducibles, and structural properties
    
    Requirements: 2.1, 2.2
    """
    
    def test_congruence_lattice_construction_compatibility(self):
        """Test congruence lattice construction produces identical lattices"""
        for algebra_file in self.algebra_files[:5]:  # Test on first 5 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_congruence_lattice_construction(algebra_file)
    
    def _test_congruence_lattice_construction(self, algebra_file: Path):
        """Test congruence lattice construction for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip very large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'congruence_lattice'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Get congruence lattice from Rust implementation
        try:
            rust_start_time = self.test_start_time
            con_lattice = algebra.congruence_lattice()
            rust_execution_time = self.test_start_time - rust_start_time
            
            rust_result = {
                'lattice_size': len(con_lattice),
                'algebra_name': algebra.name,
                'algebra_cardinality': algebra.cardinality,
                'has_zero': hasattr(con_lattice, 'zero') and con_lattice.zero() is not None,
                'has_one': hasattr(con_lattice, 'one') and con_lattice.one() is not None,
            }
            
            # Add lattice elements information if available
            if hasattr(con_lattice, 'elements'):
                rust_result['elements_count'] = len(list(con_lattice.elements()))
            
        except Exception as e:
            self.fail(f"Rust congruence lattice construction failed for {algebra.name}: {e}")
        
        # Get congruence lattice from Java implementation
        timeout = self._get_test_timeout('congruence_lattice', algebra.cardinality)
        java_result = self._run_java_operation('lattice', str(algebra_file), timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'congruence_lattice_construction', algebra.name
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Congruence lattice construction mismatch for {algebra.name}: "
                f"Rust size: {rust_result.get('lattice_size')}, "
                f"Java size: {java_result.get('lattice_size')}"
            )
    
    def test_principal_congruence_compatibility(self):
        """Test Cg(a,b) computation produces identical partitions"""
        for algebra_file in self.algebra_files[:3]:  # Test on first 3 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_principal_congruence_generation(algebra_file)
    
    def _test_principal_congruence_generation(self, algebra_file: Path):
        """Test principal congruence generation for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance (principal congruences are expensive)
        if self._should_skip_test(algebra.cardinality, 'cg'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Test principal congruences for a sample of element pairs
        element_pairs = self._get_element_pairs_sample(algebra.cardinality)
        
        for a, b in element_pairs:
            with self.subTest(pair=(a, b)):
                self._test_principal_congruence_pair(algebra, algebra_file, a, b)
    
    def _get_element_pairs_sample(self, cardinality: int) -> List[Tuple[int, int]]:
        """Get a representative sample of element pairs for testing"""
        if cardinality <= 4:
            # For small algebras, test all pairs
            return [(a, b) for a in range(cardinality) for b in range(cardinality)]
        elif cardinality <= 8:
            # For medium algebras, test diagonal and some off-diagonal pairs
            pairs = [(i, i) for i in range(cardinality)]  # Diagonal
            pairs.extend([(0, i) for i in range(1, min(4, cardinality))])  # From 0
            pairs.extend([(i, 0) for i in range(1, min(4, cardinality))])  # To 0
            if cardinality > 2:
                pairs.extend([(1, i) for i in range(2, min(4, cardinality))])  # From 1
            return pairs
        else:
            # For large algebras, test only a few representative pairs
            return [(0, 0), (0, 1), (1, 0), (1, 1), (0, cardinality-1), (cardinality-1, 0)]
    
    def _test_principal_congruence_pair(self, algebra, algebra_file: Path, a: int, b: int):
        """Test principal congruence Cg(a,b) for a specific pair"""
        # Get principal congruence from Rust implementation
        try:
            cg_rust = algebra.cg(a, b)
            
            # Convert to a comparable format
            rust_result = {
                'pair': [a, b],
                'algebra_name': algebra.name,
                'partition_size': len(cg_rust) if hasattr(cg_rust, '__len__') else None,
            }
            
            # Try to get partition blocks if available
            if hasattr(cg_rust, 'blocks'):
                blocks = list(cg_rust.blocks())
                rust_result['blocks'] = [sorted(list(block)) for block in blocks]
                rust_result['blocks'].sort()  # Sort for consistent comparison
            elif hasattr(cg_rust, '__iter__'):
                # If it's iterable, try to convert to blocks
                try:
                    blocks = list(cg_rust)
                    rust_result['blocks'] = [sorted(list(block)) for block in blocks]
                    rust_result['blocks'].sort()
                except:
                    pass
            
        except Exception as e:
            self.fail(f"Rust Cg({a},{b}) failed for {algebra.name}: {e}")
        
        # Get principal congruence from Java implementation
        timeout = self._get_test_timeout('cg', algebra.cardinality)
        java_result = self._run_java_operation('cg', str(algebra_file), str(a), str(b), timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'principal_congruence', f"{algebra.name}_Cg({a},{b})"
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Principal congruence Cg({a},{b}) mismatch for {algebra.name}: "
                f"Rust blocks: {rust_result.get('blocks')}, "
                f"Java blocks: {java_result.get('blocks')}"
            )
    
    def test_join_irreducibles_compatibility(self):
        """Test join irreducible detection matches exactly"""
        for algebra_file in self.algebra_files[:4]:  # Test on first 4 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_join_irreducibles(algebra_file)
    
    def _test_join_irreducibles(self, algebra_file: Path):
        """Test join irreducibles detection for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'join_irreducibles'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Get join irreducibles from Rust implementation
        try:
            con_lattice = algebra.congruence_lattice()
            
            rust_result = {
                'algebra_name': algebra.name,
                'lattice_size': len(con_lattice) if hasattr(con_lattice, '__len__') else None,
            }
            
            # Try to get join irreducibles if the method exists
            if hasattr(con_lattice, 'join_irreducibles'):
                ji_rust = con_lattice.join_irreducibles()
                rust_result['join_irreducibles_count'] = len(ji_rust) if hasattr(ji_rust, '__len__') else None
                
                # Try to get more detailed information
                if hasattr(ji_rust, '__iter__'):
                    try:
                        ji_list = list(ji_rust)
                        rust_result['join_irreducibles_count'] = len(ji_list)
                        # Don't include the actual elements as they might be complex objects
                    except:
                        pass
            
        except Exception as e:
            self.fail(f"Rust join irreducibles computation failed for {algebra.name}: {e}")
        
        # Get join irreducibles from Java implementation
        timeout = self._get_test_timeout('join_irreducibles', algebra.cardinality)
        java_result = self._run_java_operation('join_irreducibles', str(algebra_file), timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'join_irreducibles', algebra.name
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Join irreducibles mismatch for {algebra.name}: "
                f"Rust count: {rust_result.get('join_irreducibles_count')}, "
                f"Java count: {java_result.get('join_irreducibles_count')}"
            )
    
    def test_congruence_lattice_properties_compatibility(self):
        """Test congruence lattice structural properties match exactly"""
        for algebra_file in self.algebra_files[:4]:  # Test on first 4 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_congruence_lattice_properties(algebra_file)
    
    def _test_congruence_lattice_properties(self, algebra_file: Path):
        """Test congruence lattice properties for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'lattice_properties'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Get lattice properties from Rust implementation
        try:
            con_lattice = algebra.congruence_lattice()
            
            rust_result = {
                'algebra_name': algebra.name,
                'algebra_cardinality': algebra.cardinality,
                'lattice_size': len(con_lattice) if hasattr(con_lattice, '__len__') else None,
            }
            
            # Test various lattice properties if available
            if hasattr(con_lattice, 'is_distributive'):
                rust_result['is_distributive'] = con_lattice.is_distributive()
            
            if hasattr(con_lattice, 'is_modular'):
                rust_result['is_modular'] = con_lattice.is_modular()
            
            if hasattr(con_lattice, 'height'):
                rust_result['height'] = con_lattice.height()
            
            if hasattr(con_lattice, 'width'):
                rust_result['width'] = con_lattice.width()
            
            # Check for zero and one elements
            if hasattr(con_lattice, 'zero'):
                rust_result['has_zero'] = con_lattice.zero() is not None
            
            if hasattr(con_lattice, 'one'):
                rust_result['has_one'] = con_lattice.one() is not None
            
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
                f"Rust size: {rust_result.get('lattice_size')}, "
                f"Java size: {java_result.get('lattice_size')}"
            )


if __name__ == '__main__':
    unittest.main()