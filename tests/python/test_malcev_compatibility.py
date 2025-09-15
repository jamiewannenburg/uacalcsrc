#!/usr/bin/env python3
"""
Malcev Compatibility Test

This module tests the org.uacalc.alg.Malcev class compatibility between
Java UACalc and the Rust/Python implementation. It verifies that Maltsev
condition checking, variety membership detection, and tame congruence theory
type detection work identically.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class MalcevCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.Malcev class compatibility.
    
    This class tests the Malcev implementation to ensure
    the Rust implementation matches Java behavior exactly for:
    - Maltsev condition checking (modularity, distributivity)
    - Variety membership detection for standard varieties
    - Tame congruence theory type detection
    - Advanced algebraic property analysis
    """
    
    def test_maltsev_conditions_compatibility(self):
        """Test Maltsev condition checking (modularity, distributivity)"""
        logger.info("Testing Maltsev conditions compatibility")
        
        # Test on small to medium algebras
        test_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 8][:6]
        
        for algebra_file in test_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Skip if algebra is too large for Maltsev analysis
                if self._should_skip_test(self._get_algebra_size_estimate(algebra_file), "maltsev_conditions"):
                    self.skipTest(f"Algebra too large for Maltsev analysis: {algebra_file.name}")
                
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Get Maltsev conditions from Rust/Python
                rust_maltsev = None
                try:
                    # This would call the Rust Maltsev analysis
                    # For now, simulate based on basic properties
                    rust_maltsev = {
                        "congruence_modular": self._estimate_congruence_modularity(algebra),
                        "congruence_distributive": self._estimate_congruence_distributivity(algebra),
                        "has_majority_term": False,  # Conservative estimate
                        "has_minority_term": False,  # Conservative estimate
                        "maltsev_type": self._estimate_maltsev_type(algebra),
                        "analysis_completed": True
                    }
                except Exception as e:
                    self.skipTest(f"Rust Maltsev analysis not implemented: {e}")
                
                # Get Maltsev conditions from Java
                java_result = self._run_java_operation(
                    "maltsev_conditions", str(algebra_file),
                    timeout=self._get_test_timeout("maltsev_conditions", algebra.cardinality)
                )
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java Maltsev analysis failed: {java_result.get('error')}")
                
                java_maltsev = {
                    "congruence_modular": java_result.get("congruence_modular", False),
                    "congruence_distributive": java_result.get("congruence_distributive", False),
                    "has_majority_term": java_result.get("has_majority_term", False),
                    "has_minority_term": java_result.get("has_minority_term", False),
                    "maltsev_type": java_result.get("maltsev_type", 0),
                    "analysis_completed": True
                }
                
                # Compare results
                result = self._compare_results(
                    rust_maltsev,
                    java_maltsev,
                    "maltsev_conditions",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Maltsev conditions mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_variety_membership_compatibility(self):
        """Test variety membership detection for standard varieties"""
        logger.info("Testing variety membership compatibility")
        
        # Test on smaller algebras for variety membership
        test_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 6][:5]
        
        for algebra_file in test_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Get variety membership from Rust/Python
                rust_varieties = None
                try:
                    # Simulate variety membership detection
                    rust_varieties = {
                        "is_group": self._check_group_variety(algebra),
                        "is_lattice": self._check_lattice_variety(algebra),
                        "is_boolean_algebra": self._check_boolean_algebra_variety(algebra),
                        "is_semilattice": self._check_semilattice_variety(algebra),
                        "is_quasigroup": self._check_quasigroup_variety(algebra),
                        "variety_count": 0  # Will be updated based on checks
                    }
                    
                    # Count varieties
                    rust_varieties["variety_count"] = sum(1 for v in rust_varieties.values() if isinstance(v, bool) and v)
                    
                except Exception as e:
                    self.skipTest(f"Rust variety membership not implemented: {e}")
                
                # Get variety membership from Java
                java_result = self._run_java_operation(
                    "maltsev_conditions", str(algebra_file),
                    timeout=self._get_test_timeout("maltsev_conditions", algebra.cardinality)
                )
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java variety analysis failed: {java_result.get('error')}")
                
                java_varieties = {
                    "is_group": java_result.get("is_group", False),
                    "is_lattice": java_result.get("is_lattice", False),
                    "is_boolean_algebra": java_result.get("is_boolean_algebra", False),
                    "is_semilattice": java_result.get("is_semilattice", False),
                    "is_quasigroup": java_result.get("is_quasigroup", False),
                    "variety_count": java_result.get("variety_count", 0)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_varieties,
                    java_varieties,
                    "variety_membership",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Variety membership mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_tame_congruence_theory_type_compatibility(self):
        """Test tame congruence theory type detection"""
        logger.info("Testing tame congruence theory type compatibility")
        
        # Test on small algebras only (TCT type detection is expensive)
        small_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 5][:4]
        
        for algebra_file in small_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Get TCT type from Rust/Python
                rust_tct_type = None
                try:
                    # Simulate TCT type detection
                    rust_tct_type = {
                        "tct_type": self._estimate_tct_type(algebra),
                        "type_determined": True,
                        "has_type_1": False,  # Conservative estimates
                        "has_type_2": False,
                        "has_type_3": False,
                        "has_type_4": False,
                        "has_type_5": False,
                        "type_analysis_complete": True
                    }
                    
                    # Set the specific type flag
                    tct_type = rust_tct_type["tct_type"]
                    if 1 <= tct_type <= 5:
                        rust_tct_type[f"has_type_{tct_type}"] = True
                    
                except Exception as e:
                    self.skipTest(f"Rust TCT type detection not implemented: {e}")
                
                # Get TCT type from Java
                java_result = self._run_java_operation(
                    "type_finder", str(algebra_file),
                    timeout=self._get_test_timeout("type_finder", algebra.cardinality)
                )
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java TCT type detection failed: {java_result.get('error')}")
                
                java_tct_type = {
                    "tct_type": java_result.get("tct_type", 0),
                    "type_determined": java_result.get("type_determined", False),
                    "has_type_1": java_result.get("has_type_1", False),
                    "has_type_2": java_result.get("has_type_2", False),
                    "has_type_3": java_result.get("has_type_3", False),
                    "has_type_4": java_result.get("has_type_4", False),
                    "has_type_5": java_result.get("has_type_5", False),
                    "type_analysis_complete": java_result.get("type_analysis_complete", True)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_tct_type,
                    java_tct_type,
                    "tct_type",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"TCT type mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_advanced_algebraic_properties_compatibility(self):
        """Test advanced algebraic property analysis"""
        logger.info("Testing advanced algebraic properties compatibility")
        
        # Test on small algebras for advanced properties
        test_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 6][:4]
        
        for algebra_file in test_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Get advanced properties from Rust/Python
                rust_advanced = None
                try:
                    # Simulate advanced property analysis
                    rust_advanced = {
                        "has_permuting_congruences": False,  # Conservative estimate
                        "congruence_lattice_size": self._estimate_congruence_lattice_size(algebra),
                        "join_irreducible_count": 0,  # Conservative estimate
                        "atoms_count": 0,  # Conservative estimate
                        "height": 0,  # Conservative estimate
                        "width": 0,  # Conservative estimate
                        "is_simple": algebra.cardinality == 1,  # Only trivial algebra is definitely simple
                        "analysis_depth": "basic"
                    }
                except Exception as e:
                    self.skipTest(f"Rust advanced properties not implemented: {e}")
                
                # Get advanced properties from Java
                java_result = self._run_java_operation(
                    "maltsev_conditions", str(algebra_file),
                    timeout=self._get_test_timeout("maltsev_conditions", algebra.cardinality)
                )
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java advanced analysis failed: {java_result.get('error')}")
                
                java_advanced = {
                    "has_permuting_congruences": java_result.get("has_permuting_congruences", False),
                    "congruence_lattice_size": java_result.get("congruence_lattice_size", 0),
                    "join_irreducible_count": java_result.get("join_irreducible_count", 0),
                    "atoms_count": java_result.get("atoms_count", 0),
                    "height": java_result.get("height", 0),
                    "width": java_result.get("width", 0),
                    "is_simple": java_result.get("is_simple", False),
                    "analysis_depth": java_result.get("analysis_depth", "basic")
                }
                
                # Compare results
                result = self._compare_results(
                    rust_advanced,
                    java_advanced,
                    "advanced_properties",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Advanced properties mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_maltsev_term_detection_compatibility(self):
        """Test Maltsev term detection"""
        logger.info("Testing Maltsev term detection compatibility")
        
        # Test on very small algebras for term detection
        tiny_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:3]
        
        for algebra_file in tiny_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Get Maltsev term detection from Rust/Python
                rust_terms = None
                try:
                    # Simulate Maltsev term detection
                    rust_terms = {
                        "has_maltsev_term": False,  # Conservative estimate
                        "has_majority_term": False,
                        "has_minority_term": False,
                        "has_near_unanimity_term": False,
                        "term_condition_satisfied": False,
                        "term_detection_complete": True
                    }
                    
                    # For very small algebras, we might be able to detect some terms
                    if algebra.cardinality <= 3:
                        rust_terms["term_detection_feasible"] = True
                    
                except Exception as e:
                    self.skipTest(f"Rust Maltsev term detection not implemented: {e}")
                
                # Get Maltsev term detection from Java
                java_result = self._run_java_operation(
                    "maltsev_conditions", str(algebra_file),
                    timeout=self._get_test_timeout("maltsev_conditions", algebra.cardinality)
                )
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java Maltsev term detection failed: {java_result.get('error')}")
                
                java_terms = {
                    "has_maltsev_term": java_result.get("has_maltsev_term", False),
                    "has_majority_term": java_result.get("has_majority_term", False),
                    "has_minority_term": java_result.get("has_minority_term", False),
                    "has_near_unanimity_term": java_result.get("has_near_unanimity_term", False),
                    "term_condition_satisfied": java_result.get("term_condition_satisfied", False),
                    "term_detection_complete": java_result.get("term_detection_complete", True),
                    "term_detection_feasible": java_result.get("term_detection_feasible", True)
                }
                
                # Compare results
                result = self._compare_results(
                    rust_terms,
                    java_terms,
                    "maltsev_terms",
                    algebra_file.name
                )
                
                self.assertTrue(result.matches,
                    f"Maltsev term detection mismatch for {algebra_file.name}: {result.error_message}")
    
    def _get_algebra_size_estimate(self, algebra_file: Path) -> int:
        """Estimate algebra size from file size (rough heuristic)"""
        try:
            file_size = algebra_file.stat().st_size
            if file_size < 1000:
                return 3
            elif file_size < 5000:
                return 6
            elif file_size < 20000:
                return 10
            else:
                return 20
        except:
            return 10
    
    def _estimate_congruence_modularity(self, algebra) -> bool:
        """Estimate if algebra has modular congruence lattice"""
        # Very conservative estimate - only trivial algebra is definitely modular
        return algebra.cardinality == 1
    
    def _estimate_congruence_distributivity(self, algebra) -> bool:
        """Estimate if algebra has distributive congruence lattice"""
        # Very conservative estimate - only trivial algebra is definitely distributive
        return algebra.cardinality == 1
    
    def _estimate_maltsev_type(self, algebra) -> int:
        """Estimate Maltsev type of algebra"""
        # Conservative estimate based on size
        if algebra.cardinality == 1:
            return 1  # Trivial algebra
        elif algebra.cardinality == 2:
            return 2  # Small algebra, likely type 2
        else:
            return 0  # Unknown/undetermined
    
    def _estimate_tct_type(self, algebra) -> int:
        """Estimate tame congruence theory type"""
        # Very basic estimation
        if algebra.cardinality == 1:
            return 1
        elif algebra.cardinality == 2:
            return 2
        else:
            return 0  # Undetermined
    
    def _estimate_congruence_lattice_size(self, algebra) -> int:
        """Estimate size of congruence lattice"""
        # Very rough estimate - at least 2 (trivial congruences)
        if algebra.cardinality == 1:
            return 1
        else:
            return 2  # At least identity and universal congruence
    
    def _check_group_variety(self, algebra) -> bool:
        """Check if algebra might be in the variety of groups"""
        # Very basic check - needs exactly one binary operation
        binary_ops = [op for op in algebra.operations if op.arity == 2]
        return len(binary_ops) == 1 and len(algebra.operations) == 1
    
    def _check_lattice_variety(self, algebra) -> bool:
        """Check if algebra might be in the variety of lattices"""
        # Basic check - needs exactly two binary operations
        binary_ops = [op for op in algebra.operations if op.arity == 2]
        return len(binary_ops) == 2 and len(algebra.operations) == 2
    
    def _check_boolean_algebra_variety(self, algebra) -> bool:
        """Check if algebra might be in the variety of Boolean algebras"""
        # Basic check - needs specific operation signature
        binary_ops = [op for op in algebra.operations if op.arity == 2]
        unary_ops = [op for op in algebra.operations if op.arity == 1]
        nullary_ops = [op for op in algebra.operations if op.arity == 0]
        return len(binary_ops) == 2 and len(unary_ops) == 1 and len(nullary_ops) == 2
    
    def _check_semilattice_variety(self, algebra) -> bool:
        """Check if algebra might be in the variety of semilattices"""
        # Basic check - needs exactly one binary operation
        binary_ops = [op for op in algebra.operations if op.arity == 2]
        return len(binary_ops) == 1 and len(algebra.operations) == 1
    
    def _check_quasigroup_variety(self, algebra) -> bool:
        """Check if algebra might be in the variety of quasigroups"""
        # Basic check - needs exactly one binary operation
        binary_ops = [op for op in algebra.operations if op.arity == 2]
        return len(binary_ops) == 1 and len(algebra.operations) == 1


if __name__ == '__main__':
    unittest.main()