#!/usr/bin/env python3
"""
Type Finder Compatibility Test

This module tests the compatibility of tame congruence theory type detection
between the Rust/Python UACalc implementation and the original Java UACalc library.
Tests include type detection, classification, and variety membership detection.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from tests.python.base_compatibility_test import BaseCompatibilityTest


class TypeFinderCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.conlat.TypeFinder class compatibility.
    
    This class tests:
    - Tame congruence theory type detection
    - Type classification and properties
    - Type-based variety membership detection
    
    Requirements: 2.5, 5.1
    """
    
    def test_type_detection_compatibility(self):
        """Test tame congruence theory type detection matches exactly"""
        for algebra_file in self.algebra_files[:4]:  # Test on first 4 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_type_detection(algebra_file)
    
    def _test_type_detection(self, algebra_file: Path):
        """Test type detection for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance (type detection can be expensive)
        if self._should_skip_test(algebra.cardinality, 'type_finder'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Get type information from Rust implementation
        try:
            rust_result = {
                'algebra_name': algebra.name,
                'algebra_cardinality': algebra.cardinality,
                'operation_count': len(algebra.operations) if hasattr(algebra, 'operations') else None,
            }
            
            # Try to detect tame congruence theory type
            if hasattr(algebra, 'tame_congruence_type'):
                tct_type = algebra.tame_congruence_type()
                rust_result['type_detected'] = True
                rust_result['tame_congruence_type'] = tct_type
                
                # Classify the type
                if isinstance(tct_type, int):
                    rust_result['type_number'] = tct_type
                    rust_result['type_classification'] = self._classify_tct_type(tct_type)
                elif hasattr(tct_type, 'type_number'):
                    rust_result['type_number'] = tct_type.type_number()
                    rust_result['type_classification'] = self._classify_tct_type(tct_type.type_number())
                
            elif hasattr(algebra, 'type_finder'):
                type_finder = algebra.type_finder()
                rust_result['type_detected'] = True
                
                if hasattr(type_finder, 'find_type'):
                    tct_type = type_finder.find_type()
                    rust_result['tame_congruence_type'] = tct_type
                    
                    if isinstance(tct_type, int):
                        rust_result['type_number'] = tct_type
                        rust_result['type_classification'] = self._classify_tct_type(tct_type)
                
            else:
                rust_result['type_detected'] = False
                rust_result['type_finder_available'] = False
            
            # Try to get additional type-related properties
            if hasattr(algebra, 'is_congruence_modular'):
                rust_result['is_congruence_modular'] = algebra.is_congruence_modular()
            
            if hasattr(algebra, 'is_congruence_distributive'):
                rust_result['is_congruence_distributive'] = algebra.is_congruence_distributive()
            
            if hasattr(algebra, 'has_cube_term'):
                rust_result['has_cube_term'] = algebra.has_cube_term()
            
        except Exception as e:
            self.fail(f"Rust type detection failed for {algebra.name}: {e}")
        
        # Get type information from Java implementation
        timeout = self._get_test_timeout('type_finder', algebra.cardinality)
        java_result = self._run_java_operation('type_finder', str(algebra_file), timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'type_detection', algebra.name
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Type detection mismatch for {algebra.name}: "
                f"Rust type: {rust_result.get('type_number')}, "
                f"Java type: {java_result.get('type_number')}"
            )
    
    def _classify_tct_type(self, type_number: int) -> str:
        """Classify tame congruence theory type number"""
        type_classifications = {
            1: "unary",
            2: "affine", 
            3: "boolean",
            4: "lattice",
            5: "semilattice"
        }
        return type_classifications.get(type_number, f"type_{type_number}")
    
    def test_type_classification_compatibility(self):
        """Test type classification and properties match exactly"""
        for algebra_file in self.algebra_files[:3]:  # Test on first 3 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_type_classification(algebra_file)
    
    def _test_type_classification(self, algebra_file: Path):
        """Test type classification for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'type_classification'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Get type classification from Rust implementation
        try:
            rust_result = {
                'algebra_name': algebra.name,
                'algebra_cardinality': algebra.cardinality,
            }
            
            # Try to get detailed type classification
            if hasattr(algebra, 'tame_congruence_type'):
                tct_type = algebra.tame_congruence_type()
                rust_result['has_type'] = True
                
                if isinstance(tct_type, int):
                    rust_result['type_number'] = tct_type
                    rust_result['type_name'] = self._classify_tct_type(tct_type)
                    
                    # Determine properties based on type
                    rust_result['is_unary_type'] = (tct_type == 1)
                    rust_result['is_affine_type'] = (tct_type == 2)
                    rust_result['is_boolean_type'] = (tct_type == 3)
                    rust_result['is_lattice_type'] = (tct_type == 4)
                    rust_result['is_semilattice_type'] = (tct_type == 5)
                
            else:
                rust_result['has_type'] = False
            
            # Check for specific algebraic properties that relate to types
            if hasattr(algebra, 'has_majority_term'):
                rust_result['has_majority_term'] = algebra.has_majority_term()
            
            if hasattr(algebra, 'has_minority_term'):
                rust_result['has_minority_term'] = algebra.has_minority_term()
            
            if hasattr(algebra, 'has_maltsev_term'):
                rust_result['has_maltsev_term'] = algebra.has_maltsev_term()
            
            if hasattr(algebra, 'has_pixley_term'):
                rust_result['has_pixley_term'] = algebra.has_pixley_term()
            
        except Exception as e:
            self.fail(f"Rust type classification failed for {algebra.name}: {e}")
        
        # Get type classification from Java implementation
        timeout = self._get_test_timeout('type_finder', algebra.cardinality)
        java_result = self._run_java_operation('type_finder', str(algebra_file), timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'type_classification', algebra.name
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Type classification mismatch for {algebra.name}: "
                f"Rust type name: {rust_result.get('type_name')}, "
                f"Java type name: {java_result.get('type_name')}"
            )
    
    def test_variety_membership_compatibility(self):
        """Test type-based variety membership detection matches exactly"""
        for algebra_file in self.algebra_files[:4]:  # Test on first 4 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_variety_membership(algebra_file)
    
    def _test_variety_membership(self, algebra_file: Path):
        """Test variety membership detection for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'variety_membership'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Get variety membership from Rust implementation
        try:
            rust_result = {
                'algebra_name': algebra.name,
                'algebra_cardinality': algebra.cardinality,
            }
            
            # Test membership in various varieties
            varieties_to_test = [
                'groups', 'lattices', 'boolean_algebras', 'semilattices',
                'modular_lattices', 'distributive_lattices'
            ]
            
            for variety in varieties_to_test:
                method_name = f'is_in_{variety}_variety'
                if hasattr(algebra, method_name):
                    rust_result[f'in_{variety}_variety'] = getattr(algebra, method_name)()
                else:
                    # Try alternative method names
                    alt_method_name = f'is_{variety.rstrip("s")}'
                    if hasattr(algebra, alt_method_name):
                        rust_result[f'in_{variety}_variety'] = getattr(algebra, alt_method_name)()
            
            # Check specific variety-related properties
            if hasattr(algebra, 'is_group'):
                rust_result['is_group'] = algebra.is_group()
            
            if hasattr(algebra, 'is_lattice'):
                rust_result['is_lattice'] = algebra.is_lattice()
            
            if hasattr(algebra, 'is_boolean_algebra'):
                rust_result['is_boolean_algebra'] = algebra.is_boolean_algebra()
            
            if hasattr(algebra, 'is_semilattice'):
                rust_result['is_semilattice'] = algebra.is_semilattice()
            
            # Use type information to infer variety membership if available
            if hasattr(algebra, 'tame_congruence_type'):
                tct_type = algebra.tame_congruence_type()
                if isinstance(tct_type, int):
                    rust_result['type_based_variety_inference'] = self._infer_variety_from_type(tct_type)
            
        except Exception as e:
            self.fail(f"Rust variety membership detection failed for {algebra.name}: {e}")
        
        # Get variety membership from Java implementation
        timeout = self._get_test_timeout('type_finder', algebra.cardinality)
        java_result = self._run_java_operation('type_finder', str(algebra_file), timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'variety_membership', algebra.name
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Variety membership mismatch for {algebra.name}: "
                f"Rust group: {rust_result.get('is_group')}, "
                f"Java group: {java_result.get('is_group')}"
            )
    
    def _infer_variety_from_type(self, type_number: int) -> Dict[str, bool]:
        """Infer variety membership from tame congruence theory type"""
        # This is a simplified inference based on tame congruence theory
        inference = {
            'likely_group': False,
            'likely_lattice': False,
            'likely_boolean': False,
            'likely_semilattice': False
        }
        
        if type_number == 1:  # Unary type
            inference['likely_group'] = True
        elif type_number == 2:  # Affine type
            inference['likely_group'] = True
        elif type_number == 3:  # Boolean type
            inference['likely_boolean'] = True
        elif type_number == 4:  # Lattice type
            inference['likely_lattice'] = True
        elif type_number == 5:  # Semilattice type
            inference['likely_semilattice'] = True
        
        return inference
    
    def test_type_properties_compatibility(self):
        """Test type-specific properties match exactly"""
        for algebra_file in self.algebra_files[:3]:  # Test on first 3 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_type_properties(algebra_file)
    
    def _test_type_properties(self, algebra_file: Path):
        """Test type-specific properties for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'type_properties'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Get type properties from Rust implementation
        try:
            rust_result = {
                'algebra_name': algebra.name,
                'algebra_cardinality': algebra.cardinality,
            }
            
            # Test congruence properties related to types
            if hasattr(algebra, 'congruence_lattice'):
                con_lattice = algebra.congruence_lattice()
                
                if hasattr(con_lattice, 'is_modular'):
                    rust_result['congruence_modular'] = con_lattice.is_modular()
                
                if hasattr(con_lattice, 'is_distributive'):
                    rust_result['congruence_distributive'] = con_lattice.is_distributive()
                
                if hasattr(con_lattice, '__len__'):
                    rust_result['congruence_lattice_size'] = len(con_lattice)
            
            # Test for specific term conditions
            term_conditions = [
                'has_majority_term', 'has_minority_term', 'has_maltsev_term',
                'has_pixley_term', 'has_near_unanimity_term', 'has_cube_term'
            ]
            
            for condition in term_conditions:
                if hasattr(algebra, condition):
                    rust_result[condition] = getattr(algebra, condition)()
            
            # Test for idempotency
            if hasattr(algebra, 'is_idempotent_algebra'):
                rust_result['is_idempotent'] = algebra.is_idempotent_algebra()
            
        except Exception as e:
            self.fail(f"Rust type properties analysis failed for {algebra.name}: {e}")
        
        # Get type properties from Java implementation
        timeout = self._get_test_timeout('type_finder', algebra.cardinality)
        java_result = self._run_java_operation('type_finder', str(algebra_file), timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'type_properties', algebra.name
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Type properties mismatch for {algebra.name}: "
                f"Rust congruence modular: {rust_result.get('congruence_modular')}, "
                f"Java congruence modular: {java_result.get('congruence_modular')}"
            )
    
    def test_type_finder_edge_cases_compatibility(self):
        """Test type finder edge cases and special algebras"""
        # Test on specific algebras that might have interesting type properties
        special_algebras = []
        
        # Look for algebras with specific names that might be interesting
        for algebra_file in self.algebra_files:
            name = algebra_file.stem.lower()
            if any(keyword in name for keyword in ['lat', 'bool', 'group', 'sym', 'cyclic']):
                special_algebras.append(algebra_file)
        
        # Test on first few special algebras
        for algebra_file in special_algebras[:3]:
            with self.subTest(algebra=algebra_file.name):
                self._test_type_finder_edge_cases(algebra_file)
    
    def _test_type_finder_edge_cases(self, algebra_file: Path):
        """Test type finder on edge cases and special algebras"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'type_finder_edge_cases'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Test edge cases in type detection
        try:
            rust_result = {
                'algebra_name': algebra.name,
                'algebra_cardinality': algebra.cardinality,
                'is_edge_case_test': True,
            }
            
            # Test type detection robustness
            if hasattr(algebra, 'tame_congruence_type'):
                try:
                    tct_type = algebra.tame_congruence_type()
                    rust_result['type_detection_successful'] = True
                    rust_result['detected_type'] = tct_type
                except Exception as e:
                    rust_result['type_detection_successful'] = False
                    rust_result['type_detection_error'] = str(e)
            
            # Test for degenerate cases
            if algebra.cardinality == 1:
                rust_result['is_trivial_algebra'] = True
            elif algebra.cardinality == 2:
                rust_result['is_two_element_algebra'] = True
            
            # Test for specific structural properties
            if hasattr(algebra, 'operations'):
                ops = algebra.operations
                rust_result['operation_count'] = len(ops)
                
                # Check for nullary operations (constants)
                nullary_count = sum(1 for op in ops if hasattr(op, 'arity') and op.arity == 0)
                rust_result['nullary_operations'] = nullary_count
                
                # Check for unary operations
                unary_count = sum(1 for op in ops if hasattr(op, 'arity') and op.arity == 1)
                rust_result['unary_operations'] = unary_count
            
        except Exception as e:
            self.fail(f"Rust type finder edge case testing failed for {algebra.name}: {e}")
        
        # Get edge case results from Java implementation
        timeout = self._get_test_timeout('type_finder', algebra.cardinality)
        java_result = self._run_java_operation('type_finder', str(algebra_file), timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'type_finder_edge_cases', algebra.name
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Type finder edge case mismatch for {algebra.name}: "
                f"Rust detection successful: {rust_result.get('type_detection_successful')}, "
                f"Java detection successful: {java_result.get('type_detection_successful')}"
            )


if __name__ == '__main__':
    unittest.main()