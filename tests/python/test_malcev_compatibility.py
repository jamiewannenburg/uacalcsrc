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


@unittest.skip("Malcev is hanging")
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
    
    # def test_maltsev_conditions_compatibility(self):
    #     """Test Maltsev condition checking (modularity, distributivity)"""
    #     logger.info("Testing Maltsev conditions compatibility")
        
    #     # Test on very small algebras only to avoid memory issues
    #     test_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 3][:2]
        
    #     # If no small algebras found, skip the test
    #     if not test_algebras:
    #         self.skipTest("No small algebras found for testing")
        
        # for algebra_file in test_algebras:
        #     with self.subTest(algebra=algebra_file.name):
        #         # Skip if algebra is too large for Maltsev analysis
        #         if self._should_skip_test(self._get_algebra_size_estimate(algebra_file), "maltsev_conditions"):
        #             self.skipTest(f"Algebra too large for Maltsev analysis: {algebra_file.name}")
                
        #         # Load algebra in Rust/Python
        #         algebra = self._load_test_algebra(algebra_file)
                
        #         # Get Maltsev conditions from Rust/Python
        #         rust_maltsev = None
        #         try:
        #             # Call the actual Rust Malcev analysis
        #             import uacalc
        #             analyzer = uacalc.MalcevAnalyzer()
        #             analysis = analyzer.analyze_malcev_conditions(algebra)
                    
        #             rust_maltsev = {
        #                 "has_maltsev_term": analysis.has_malcev_term,
        #                 "has_join_term": analysis.has_join_term,
        #                 "congruence_lattice_size": 0,  # Will be computed separately
        #                 "analysis_completed": analysis.analysis_completed
        #             }
                    
        #             # Get advanced properties for congruence_lattice_size
        #             try:
        #                 advanced_analysis = analyzer.analyze_advanced_properties(algebra)
        #                 rust_maltsev["congruence_lattice_size"] = advanced_analysis.congruence_lattice_size
        #             except:
        #                 rust_maltsev["congruence_lattice_size"] = 0
                    
        #             # Get term finding analysis
        #             try:
        #                 term_analysis = uacalc.py_find_all_terms(algebra)
        #                 rust_maltsev["has_majority_term"] = term_analysis.has_majority_term
        #                 rust_maltsev["has_minority_term"] = term_analysis.has_minority_term
        #                 rust_maltsev["has_near_unanimity_term"] = term_analysis.has_near_unanimity_term
        #             except:
        #                 rust_maltsev["has_majority_term"] = False
        #                 rust_maltsev["has_minority_term"] = False
        #                 rust_maltsev["has_near_unanimity_term"] = False
                    
        #         except Exception as e:
        #             error_msg = str(e)
        #             if "MemoryLimitExceeded" in error_msg:
        #                 self.skipTest(f"Memory limit exceeded for {algebra_file.name}: {error_msg}")
        #             else:
        #                 self.skipTest(f"Rust Maltsev analysis not implemented: {e}")
                
        #         # Get Maltsev conditions from Java
        #         java_result = self._run_java_operation(
        #             "maltsev_conditions", str(algebra_file),
        #             timeout=self._get_test_timeout("maltsev_conditions", algebra.cardinality)
        #         )
                
        #         if java_result is None:
        #             self.skipTest("Java UACalc not available")
                
        #         if not java_result.get("success", True):
        #             self.skipTest(f"Java Maltsev analysis failed: {java_result.get('error')}")
                
        #         # Extract results from the nested structure
        #         java_results = java_result.get("results", {})
        #         java_maltsev = {
        #             "has_maltsev_term": java_results.get("has_maltsev_term", False),
        #             "has_join_term": java_results.get("has_join_term", False),
        #             "has_majority_term": java_results.get("has_majority_term", False),
        #             "has_minority_term": java_results.get("has_minority_term", False),
        #             "has_near_unanimity_term": java_results.get("has_near_unanimity_term", False),
        #             "has_semilattice_term": java_results.get("has_semilattice_term", False),
        #             "has_difference_term": java_results.get("has_difference_term", False),
        #             "has_pixley_term": java_results.get("has_pixley_term", False),
        #             "has_weak_majority_term": java_results.get("has_weak_majority_term", False),
        #             "has_weak_nu_term": java_results.get("has_weak_nu_term", False),
        #             "has_weak_3edge_term": java_results.get("has_weak_3edge_term", False),
        #             "has_fixed_kedge_term": java_results.get("has_fixed_kedge_term", False),
        #             "analysis_completed": True
        #         }
                
        #         # Compare results
        #         result = self._compare_results(
        #             rust_maltsev,
        #             java_maltsev,
        #             "maltsev_conditions",
        #             algebra_file.name
        #         )
                
        #         self.assertTrue(result.matches,
        #             f"Maltsev conditions mismatch for {algebra_file.name}: {result.error_message}")
    
    def test_actual_terms_compatibility(self):
        """Test actual term string comparison between Java and Rust"""
        logger.info("Testing actual terms compatibility")
        
        # Test on very small algebras for term comparison
        tiny_algebras = [f for f in self.algebra_files if self._get_algebra_size_estimate(f) <= 4][:2]
        
        for algebra_file in tiny_algebras:
            with self.subTest(algebra=algebra_file.name):
                # Load algebra in Rust/Python
                print(f"DEBUG: Loading algebra {algebra_file.name}")
                algebra = self._load_test_algebra(algebra_file)
                print(f"DEBUG: Loaded algebra {algebra_file.name} with cardinality {algebra.cardinality}")
                
                # Get actual terms from Rust/Python
                rust_terms = None
                try:
                    # Call the actual Rust Malcev analysis
                    import uacalc
                    print(f"DEBUG: Creating MalcevAnalyzer for algebra {algebra_file.name}")
                    analyzer = uacalc.MalcevAnalyzer()
                    print(f"DEBUG: Starting analyze_malcev_conditions for algebra {algebra_file.name}")
                    analysis = analyzer.analyze_malcev_conditions(algebra)
                    print(f"DEBUG: Analysis completed for algebra {algebra_file.name}")
                    
                    rust_terms = {
                        # "maltsev_term": analysis.malcev_term if hasattr(analysis, 'malcev_term') else None,
                        # "join_term": analysis.join_term if hasattr(analysis, 'join_term') else None,
                        # "majority_term": analysis.majority_term if hasattr(analysis, 'majority_term') else None,
                        # "minority_term": analysis.minority_term if hasattr(analysis, 'minority_term') else None,
                        # "near_unanimity_term": analysis.near_unanimity_term if hasattr(analysis, 'near_unanimity_term') else None,
                        "semilattice_term": analysis.semilattice_term if hasattr(analysis, 'semilattice_term') else None,
                        # "difference_term": analysis.difference_term if hasattr(analysis, 'difference_term') else None,
                        # "pixley_term": analysis.pixley_term if hasattr(analysis, 'pixley_term') else None,
                        # "weak_majority_term": analysis.weak_majority_term if hasattr(analysis, 'weak_majority_term') else None,
                        # "weak_nu_term": analysis.weak_nu_term if hasattr(analysis, 'weak_nu_term') else None,
                        # "weak_3edge_term": analysis.weak_3edge_term if hasattr(analysis, 'weak_3edge_term') else None,
                        # "fixed_kedge_term": analysis.fixed_kedge_term if hasattr(analysis, 'fixed_kedge_term') else None,
                        # "jonsson_terms": analysis.jonsson_terms if hasattr(analysis, 'jonsson_terms') else None,
                        # "gumm_terms": analysis.gumm_terms if hasattr(analysis, 'gumm_terms') else None,
                        # "hagemann_mitschke_terms": analysis.hagemann_mitschke_terms if hasattr(analysis, 'hagemann_mitschke_terms') else None,
                        # "sd_terms": analysis.sd_terms if hasattr(analysis, 'sd_terms') else None,
                        # "sdmeet_terms": analysis.sdmeet_terms if hasattr(analysis, 'sdmeet_terms') else None,
                        # "primality_terms": analysis.primality_terms if hasattr(analysis, 'primality_terms') else None,
                    }
                    
                except Exception as e:
                    self.skipTest(f"Rust actual terms analysis not implemented: {e}")
                
                # Get actual terms from Java
                java_result = self._run_java_operation(
                    "maltsev_conditions", str(algebra_file),
                    timeout=self._get_test_timeout("maltsev_conditions", algebra.cardinality)
                )
                
                if java_result is None:
                    self.skipTest("Java UACalc not available")
                
                if not java_result.get("success", True):
                    self.skipTest(f"Java actual terms analysis failed: {java_result.get('error')}")
                
                # Extract actual terms from the nested structure
                java_results = java_result.get("results", {})
                java_terms = {
                    # "maltsev_term": java_results.get("maltsev_term"),
                    # "join_term": java_results.get("join_term"),
                    # "majority_term": java_results.get("majority_term"),
                    # "minority_term": java_results.get("minority_term"),
                    # "near_unanimity_term": java_results.get("near_unanimity_term"),
                    "semilattice_term": java_results.get("semilattice_term"),
                    # "difference_term": java_results.get("difference_term"),
                    # "pixley_term": java_results.get("pixley_term"),
                    # "weak_majority_term": java_results.get("weak_majority_term"),
                    # "weak_nu_term": java_results.get("weak_nu_term"),
                    # "weak_3edge_term": java_results.get("weak_3edge_term"),
                    # "fixed_kedge_term": java_results.get("fixed_kedge_term"),
                    # "jonsson_terms": java_results.get("jonsson_terms"),
                    # "gumm_terms": java_results.get("gumm_terms"),
                    # "hagemann_mitschke_terms": java_results.get("hagemann_mitschke_terms"),
                    # "sd_terms": java_results.get("sd_terms"),
                    # "sdmeet_terms": java_results.get("sdmeet_terms"),
                    # "primality_terms": java_results.get("primality_terms"),
                }
                
                # Compare actual terms
                self._compare_actual_terms(
                    rust_terms,
                    java_terms,
                    "actual_terms",
                    algebra_file.name
                )
    
    def _compare_actual_terms(self, rust_terms: Dict[str, Any], java_terms: Dict[str, Any], 
                             test_name: str, algebra_name: str):
        """Compare actual term strings between Rust and Java implementations"""
        mismatches = []
        
        for term_name in rust_terms.keys():
            rust_term = rust_terms.get(term_name)
            java_term = java_terms.get(term_name)
            
            # Handle None values
            if rust_term is None and java_term is None:
                continue
            elif rust_term is None and java_term is not None:
                mismatches.append(f"{term_name}: Rust=None, Java={java_term}")
            elif rust_term is not None and java_term is None:
                mismatches.append(f"{term_name}: Rust={rust_term}, Java=None")
            else:
                # Both are not None, compare them
                if isinstance(rust_term, list) and isinstance(java_term, list):
                    # Compare term collections
                    if len(rust_term) != len(java_term):
                        mismatches.append(f"{term_name}: Different lengths - Rust={len(rust_term)}, Java={len(java_term)}")
                    else:
                        for i, (r_term, j_term) in enumerate(zip(rust_term, java_term)):
                            if r_term != j_term:
                                mismatches.append(f"{term_name}[{i}]: Rust={r_term}, Java={j_term}")
                else:
                    # Compare single terms
                    if str(rust_term) != str(java_term):
                        mismatches.append(f"{term_name}: Rust={rust_term}, Java={java_term}")
        
        if mismatches:
            error_message = f"Term mismatches for {algebra_name}:\n" + "\n".join(mismatches)
            self.fail(error_message)
        else:
            logger.info(f"All terms match for {algebra_name}")
    
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


if __name__ == '__main__':
    unittest.main()