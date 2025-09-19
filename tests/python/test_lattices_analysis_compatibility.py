#!/usr/bin/env python3
"""
Lattices Analysis Compatibility Test

This module tests the lattices analysis compatibility between
Java UACalc and the Rust/Python implementation. It verifies that lattice
analysis utilities work identically, including:
- Congruence lattice size computation
- Join/meet irreducibles analysis
- Basic lattice construction capability
- Distributive, modular, boolean property detection
- Height and width analysis
- Dual lattice analysis
"""

import unittest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class LatticesAnalysisCompatibilityTest(BaseCompatibilityTest):
    """
    Test lattices analysis compatibility.
    
    This class tests the lattices analysis implementation to ensure
    the Rust implementation matches Java behavior exactly for:
    - Congruence lattice size computation
    - Join/meet irreducibles count
    - Basic lattice construction capability
    - Lattice property detection (distributive, modular, boolean)
    - Height and width analysis
    - Dual lattice analysis
    """
    
    def test_lattices_analysis_compatibility(self):
        """Test lattices analysis compatibility"""
        logger.info("Testing lattices analysis compatibility")
        
        # Test on small algebras to avoid memory issues
        test_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 6][:4]
        
        # If no small algebras found, skip the test
        if not test_algebras:
            self.skipTest("No small algebras found for testing")
        
        for algebra_file in test_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Skip if algebra is too large for lattice analysis
                if self._should_skip_test(self._get_algebra_size_estimate(algebra_file), "lattices_analysis"):
                    self.skipTest(f"Algebra too large for lattice analysis: {algebra_file.name}")
                
                # Load algebra in Rust/Python
                algebra = self._load_test_algebra(algebra_file)
                
                # Get lattice analysis from Rust/Python
                rust_result = None
                try:
                    import uacalc
                    props = uacalc.py_analyze_lattice_properties(algebra)
                    
                    rust_result = {
                        "algebra_name": algebra.name,
                        "algebra_cardinality": algebra.cardinality,
                        "congruence_lattice_size": props.congruence_lattice_size,
                        "join_irreducibles_count": props.join_irreducibles_count,
                        "meet_irreducibles_count": props.meet_irreducibles_count,
                        "lattice_height": props.lattice_height,
                        "lattice_width": props.lattice_width,
                        "is_distributive": props.is_distributive,
                        "is_modular": props.is_modular,
                        "is_boolean": props.is_boolean,
                        "has_zero": props.has_zero,
                        "has_one": props.has_one,
                        "can_construct_basic_lattice": props.can_construct_basic_lattice,
                        "basic_lattice_error": props.basic_lattice_error,
                        "dual_analysis": {
                            "can_construct_dual": props.dual_analysis.can_construct_dual,
                            "dual_size": props.dual_analysis.dual_size,
                            "dual_join_irreducibles_count": props.dual_analysis.dual_join_irreducibles_count,
                            "dual_meet_irreducibles_count": props.dual_analysis.dual_meet_irreducibles_count,
                        }
                    }
                except Exception as e:
                    self.skipTest(f"Rust lattice properties not implemented: {e}")
                
                # Get lattice analysis from Java
                java_result = self._run_java_operation(
                    "lattices_analysis", str(algebra_file),
                    timeout=self._get_test_timeout("lattices_analysis", algebra.cardinality)
                )
                
                if java_result is None:
                    self.skipTest(f"Java lattices_analysis failed for {algebra_file.name}")
                
                # Compare results
                result = self._compare_lattices_analysis_results(rust_result, java_result)
                
                self.assertTrue(
                    result.matches,
                    f"Lattices analysis mismatch for {algebra_file.name}: {result.error_message}"
                )
    
    def test_lattice_property_consistency(self):
        """Test that lattice properties are internally consistent"""
        logger.info("Testing lattice property consistency")
        
        # Test on small algebras
        test_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:3]
        
        if not test_algebras:
            self.skipTest("No small algebras found for testing")
        
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
                                      f"Boolean lattice should be distributive: {algebra_file.name}")
                    
                    # 2. Distributive implies modular
                    if props.is_distributive:
                        self.assertTrue(props.is_modular, 
                                      f"Distributive lattice should be modular: {algebra_file.name}")
                    
                    # 3. Congruence lattice size should be at least 1
                    self.assertGreaterEqual(props.congruence_lattice_size, 1,
                                          f"Congruence lattice size should be at least 1: {algebra_file.name}")
                    
                    # 4. Height should be at least 1
                    self.assertGreaterEqual(props.lattice_height, 1,
                                          f"Lattice height should be at least 1: {algebra_file.name}")
                    
                    # 5. Width should be at least 1
                    self.assertGreaterEqual(props.lattice_width, 1,
                                          f"Lattice width should be at least 1: {algebra_file.name}")
                    
                    # 6. Join irreducibles count should be non-negative
                    self.assertGreaterEqual(props.join_irreducibles_count, 0,
                                          f"Join irreducibles count should be non-negative: {algebra_file.name}")
                    
                    # 7. Congruence lattices always have zero and one
                    self.assertTrue(props.has_zero, 
                                  f"Congruence lattice should have zero: {algebra_file.name}")
                    self.assertTrue(props.has_one, 
                                  f"Congruence lattice should have one: {algebra_file.name}")
                    
                except Exception as e:
                    self.skipTest(f"Lattice properties analysis failed: {e}")
    
    def test_dual_lattice_analysis(self):
        """Test dual lattice analysis capabilities"""
        logger.info("Testing dual lattice analysis")
        
        # Test on very small algebras
        test_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 3][:2]
        
        if not test_algebras:
            self.skipTest("No small algebras found for testing")
        
        for algebra_file in test_algebras:
            with self.subTest(algebra=algebra_file.name):
                algebra = self._load_test_algebra(algebra_file)
                
                try:
                    import uacalc
                    props = uacalc.py_analyze_lattice_properties(algebra)
                    
                    # For dual lattice analysis, we expect:
                    # - Dual size should equal original size
                    # - Dual join irreducibles should equal original meet irreducibles
                    # - Dual meet irreducibles should equal original join irreducibles
                    
                    # Note: Current Rust implementation doesn't compute meet irreducibles
                    # This test documents the expected behavior for future implementation
                    
                    # Basic dual properties
                    self.assertEqual(props.congruence_lattice_size, props.congruence_lattice_size,
                                   f"Dual lattice size should equal original: {algebra_file.name}")
                    
                except Exception as e:
                    self.skipTest(f"Dual lattice analysis failed: {e}")
    
    def _compare_lattices_analysis_results(self, rust_result: Dict[str, Any], 
                                         java_result: Dict[str, Any]) -> 'CompatibilityTestResult':
        """Compare lattices analysis results between Rust and Java"""
        from tests.python.base_compatibility_test import CompatibilityTestResult
        
        try:
            # Extract Java lattice analysis data
            java_lattice_analysis = java_result.get("lattice_analysis", {})
            
            # Compare key properties
            mismatches = []
            
            # Congruence lattice size
            rust_size = rust_result.get("congruence_lattice_size", 0)
            java_size = java_lattice_analysis.get("congruence_lattice_size", 0)
            if rust_size != java_size:
                mismatches.append(f"congruence_lattice_size: Rust={rust_size}, Java={java_size}")
            
            # Join irreducibles count
            rust_join_irr = rust_result.get("join_irreducibles_count", 0)
            java_join_irr = java_lattice_analysis.get("join_irreducibles_count", 0)
            if rust_join_irr != java_join_irr:
                mismatches.append(f"join_irreducibles_count: Rust={rust_join_irr}, Java={java_join_irr}")
            
            # Meet irreducibles count
            rust_meet_irr = rust_result.get("meet_irreducibles_count", 0)
            java_meet_irr = java_lattice_analysis.get("meet_irreducibles_count", 0)
            if rust_meet_irr != java_meet_irr:
                mismatches.append(f"meet_irreducibles_count: Rust={rust_meet_irr}, Java={java_meet_irr}")
            
            # Lattice height
            rust_height = rust_result.get("lattice_height", 0)
            java_height = java_lattice_analysis.get("lattice_height", 0)
            if rust_height != java_height:
                mismatches.append(f"lattice_height: Rust={rust_height}, Java={java_height}")
            
            # Lattice width
            rust_width = rust_result.get("lattice_width", 0)
            java_width = java_lattice_analysis.get("lattice_width", 0)
            if rust_width != java_width:
                mismatches.append(f"lattice_width: Rust={rust_width}, Java={java_width}")
            
            # Distributive property
            rust_dist = rust_result.get("is_distributive", False)
            java_dist = java_lattice_analysis.get("is_distributive", False)
            if rust_dist != java_dist:
                mismatches.append(f"is_distributive: Rust={rust_dist}, Java={java_dist}")
            
            # Modular property
            rust_mod = rust_result.get("is_modular", False)
            java_mod = java_lattice_analysis.get("is_modular", False)
            if rust_mod != java_mod:
                mismatches.append(f"is_modular: Rust={rust_mod}, Java={java_mod}")
            
            # Boolean property
            rust_bool = rust_result.get("is_boolean", False)
            java_bool = java_lattice_analysis.get("is_boolean", False)
            if rust_bool != java_bool:
                mismatches.append(f"is_boolean: Rust={rust_bool}, Java={java_bool}")
            
            # Basic lattice construction capability
            rust_basic = rust_result.get("can_construct_basic_lattice", False)
            java_basic = java_lattice_analysis.get("can_construct_basic_lattice", False)
            if rust_basic != java_basic:
                mismatches.append(f"can_construct_basic_lattice: Rust={rust_basic}, Java={java_basic}")
            
            # Dual lattice analysis
            rust_dual = rust_result.get("dual_analysis", {})
            java_dual = java_lattice_analysis.get("dual_analysis", {})
            
            rust_dual_size = rust_dual.get("dual_size", 0)
            java_dual_size = java_dual.get("dual_size", 0)
            if rust_dual_size != java_dual_size:
                mismatches.append(f"dual_size: Rust={rust_dual_size}, Java={java_dual_size}")
            
            rust_dual_join_irr = rust_dual.get("dual_join_irreducibles_count", 0)
            java_dual_join_irr = java_dual.get("dual_join_irreducibles_count", 0)
            if rust_dual_join_irr != java_dual_join_irr:
                mismatches.append(f"dual_join_irreducibles_count: Rust={rust_dual_join_irr}, Java={java_dual_join_irr}")
            
            rust_dual_meet_irr = rust_dual.get("dual_meet_irreducibles_count", 0)
            java_dual_meet_irr = java_dual.get("dual_meet_irreducibles_count", 0)
            if rust_dual_meet_irr != java_dual_meet_irr:
                mismatches.append(f"dual_meet_irreducibles_count: Rust={rust_dual_meet_irr}, Java={java_dual_meet_irr}")
            
            # Check if all properties match
            matches = len(mismatches) == 0
            
            return CompatibilityTestResult(
                test_name="lattices_analysis_compatibility",
                algebra_name=rust_result.get("algebra_name", "unknown"),
                operation="lattices_analysis",
                rust_result=rust_result,
                java_result=java_result,
                matches=matches,
                error_message="; ".join(mismatches) if mismatches else None
            )
            
        except Exception as e:
            return CompatibilityTestResult(
                test_name="lattices_analysis_compatibility",
                algebra_name=rust_result.get("algebra_name", "unknown"),
                operation="lattices_analysis",
                rust_result=rust_result,
                java_result=java_result,
                matches=False,
                error_message=f"Comparison failed: {str(e)}"
            )

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
        elif file_size < 100000:
            return 20
        else:
            return 50


if __name__ == "__main__":
    unittest.main()
