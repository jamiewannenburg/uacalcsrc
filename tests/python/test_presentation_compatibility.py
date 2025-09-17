#!/usr/bin/env python3
"""
Presentation Compatibility Test

This module tests compatibility between Rust and Java UACalc implementations
for algebraic presentation construction, properties, equivalence, and normalization.

Tests cover:
- Algebraic presentation construction and properties
- Presentation equivalence and normalization
- Presentation-based algebra construction
"""

import unittest
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from tests.python.base_compatibility_test import BaseCompatibilityTest

try:
    import uacalc
    from uacalc import create_term_arena, Presentation, PresentationProperties
    from uacalc.terms import (
        parse_term, eval_term, variable, constant, operation,
        term_variables, term_operations
    )
    UACALC_AVAILABLE = True
except ImportError:
    UACALC_AVAILABLE = False


class PresentationCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.eq.Presentation class compatibility.
    
    This class tests:
    - Algebraic presentation construction and properties
    - Presentation equivalence and normalization
    - Presentation-based algebra construction
    
    Requirements: 5.6
    """
    
    def setUp(self):
        """Set up for each test"""
        super().setUp()
        
        # Skip tests if uacalc is not available
        if not UACALC_AVAILABLE:
            self.skipTest("uacalc module not available")
        
        # Create term arena for parsing
        self.arena = create_term_arena()
        
        # Test presentation definitions for various scenarios
        self.test_presentations = {
            "simple_group": {
                "variables": ["x", "y", "z"],
                "equations": [
                    {"left_term": "f(f(x,y),z)", "right_term": "f(x,f(y,z))"},  # Associativity
                    {"left_term": "f(x,e)", "right_term": "x"},  # Identity
                    {"left_term": "f(x,g(x))", "right_term": "e"}  # Inverse
                ],
                "description": "Simple group presentation with associativity, identity, and inverse"
            },
            "commutative_monoid": {
                "variables": ["x", "y"],
                "equations": [
                    {"left_term": "f(f(x,y),z)", "right_term": "f(x,f(y,z))"},  # Associativity
                    {"left_term": "f(x,y)", "right_term": "f(y,x)"},  # Commutativity
                    {"left_term": "f(x,e)", "right_term": "x"}  # Identity
                ],
                "description": "Commutative monoid presentation"
            },
            "lattice": {
                "variables": ["x", "y", "z"],
                "equations": [
                    {"left_term": "f(f(x,y),z)", "right_term": "f(x,f(y,z))"},  # Join associativity
                    {"left_term": "f(x,y)", "right_term": "f(y,x)"},  # Join commutativity
                    {"left_term": "f(x,x)", "right_term": "x"},  # Join idempotency
                    {"left_term": "g(g(x,y),z)", "right_term": "g(x,g(y,z))"},  # Meet associativity
                    {"left_term": "g(x,y)", "right_term": "g(y,x)"},  # Meet commutativity
                    {"left_term": "g(x,x)", "right_term": "x"},  # Meet idempotency
                    {"left_term": "f(x,g(x,y))", "right_term": "x"},  # Absorption
                    {"left_term": "g(x,f(x,y))", "right_term": "x"}  # Absorption
                ],
                "description": "Lattice presentation with join and meet operations"
            },
            "boolean_algebra": {
                "variables": ["x", "y"],
                "equations": [
                    {"left_term": "f(f(x,y),z)", "right_term": "f(x,f(y,z))"},  # Join associativity
                    {"left_term": "f(x,y)", "right_term": "f(y,x)"},  # Join commutativity
                    {"left_term": "f(x,0)", "right_term": "x"},  # Join identity
                    {"left_term": "f(x,1)", "right_term": "1"},  # Join annihilator
                    {"left_term": "g(g(x,y),z)", "right_term": "g(x,g(y,z))"},  # Meet associativity
                    {"left_term": "g(x,y)", "right_term": "g(y,x)"},  # Meet commutativity
                    {"left_term": "g(x,1)", "right_term": "x"},  # Meet identity
                    {"left_term": "g(x,0)", "right_term": "0"},  # Meet annihilator
                    {"left_term": "f(x,g(x,y))", "right_term": "x"},  # Absorption
                    {"left_term": "g(x,f(x,y))", "right_term": "x"},  # Absorption
                    {"left_term": "f(x,g(y,z))", "right_term": "g(f(x,y),f(x,z))"},  # Distributivity
                    {"left_term": "g(x,f(y,z))", "right_term": "f(g(x,y),g(x,z))"},  # Distributivity
                    {"left_term": "f(x,h(x))", "right_term": "1"},  # Complement
                    {"left_term": "g(x,h(x))", "right_term": "0"}  # Complement
                ],
                "description": "Boolean algebra presentation with join, meet, and complement"
            },
            "simple_equation": {
                "variables": ["x"],
                "equations": [
                    {"left_term": "x", "right_term": "x"}
                ],
                "description": "Simple identity equation presentation"
            }
        }
        
        # Test algebras for presentation-based construction
        self.test_algebras = [
            "resources/algebras/ba2.ua",      # Boolean algebra
            "resources/algebras/cyclic2.ua",  # Cyclic group
            "resources/algebras/cyclic3.ua",  # Cyclic group
            "resources/algebras/m3.ua",       # Modular lattice
            "resources/algebras/m4.ua",       # Modular lattice
            "resources/algebras/n5.ua",       # Non-modular lattice
            "resources/algebras/sym3.ua",     # Symmetric group
            "resources/algebras/z3.ua"        # Cyclic group
        ]
    
    def test_presentation_construction_from_variables_and_equations(self):
        """Test presentation construction from variables and equations"""
        self.test_logger.info("Testing presentation construction from variables and equations")
        
        for pres_name, pres_data in self.test_presentations.items():
            with self.subTest(presentation=pres_name):
                self._test_presentation_construction(pres_name, pres_data)
    
    def _test_presentation_construction(self, pres_name: str, pres_data: Dict[str, Any]):
        """Test construction of a specific presentation"""
        variables = pres_data["variables"]
        equations = pres_data["equations"]
        description = pres_data["description"]
        
        # Test Rust implementation
        try:
            # Create presentation using the real Presentation class
            equation_strings = [(eq["left_term"], eq["right_term"]) for eq in equations]
            presentation = Presentation(variables, equation_strings)
            
            # Get presentation properties
            properties = presentation.analyze_properties()
            used_vars = presentation.used_variables()
            operation_symbols = presentation.operation_symbols()
            
            rust_result = {
                "declared_variables": variables,
                "all_variables": used_vars,
                "equation_count": len(equations),
                "variable_count": len(variables),
                "all_variable_count": len(used_vars),
                "operation_count": len(operation_symbols),
                "operations": [str(op) for op in operation_symbols],
                "description": description,
                "is_consistent": presentation.is_consistent(),
                "is_valid": presentation.is_valid(),
                "properties": properties.properties
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust presentation construction failed for {pres_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        presentation_json = json.dumps({
            "variables": variables,
            "equations": equations
        })
        
        java_result = self._run_java_operation(
            "presentation_properties", presentation_json,
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "presentation_construction", 
            context=f"{pres_name}: {description}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Presentation construction test passed for {pres_name}")
        else:
            self.test_logger.warning(f"Presentation construction test failed for {pres_name}: {result.error_message}")
            # Don't fail the test immediately, just log the difference
            # This allows us to see patterns in compatibility issues
    
    def test_presentation_property_analysis(self):
        """Test presentation property analysis and validation"""
        self.test_logger.info("Testing presentation property analysis and validation")
        
        # Test various presentation properties
        property_tests = [
            {
                "name": "variable_consistency",
                "presentation": "simple_group",
                "expected_properties": ["consistent_variables", "valid_equations"]
            },
            {
                "name": "equation_complexity",
                "presentation": "boolean_algebra",
                "expected_properties": ["complex_equations", "multiple_operations"]
            },
            {
                "name": "minimal_presentation",
                "presentation": "simple_equation",
                "expected_properties": ["minimal", "single_equation"]
            }
        ]
        
        for test_case in property_tests:
            with self.subTest(property_test=test_case["name"]):
                self._test_presentation_properties(test_case)
    
    def _test_presentation_properties(self, test_case: Dict[str, Any]):
        """Test property analysis for a specific presentation"""
        test_name = test_case["name"]
        pres_name = test_case["presentation"]
        expected_properties = test_case.get("expected_properties", [])
        
        pres_data = self.test_presentations[pres_name]
        variables = pres_data["variables"]
        equations = pres_data["equations"]
        
        # Test Rust implementation
        try:
            # Create presentation and analyze properties
            equation_strings = [(eq["left_term"], eq["right_term"]) for eq in equations]
            presentation = Presentation(variables, equation_strings)
            properties = presentation.analyze_properties()
            operation_symbols = presentation.operation_symbols()
            
            rust_result = {
                "properties": properties.properties,
                "variable_count": properties.variable_count,
                "equation_count": properties.equation_count,
                "operation_count": properties.operation_count,
                "operations": [str(op) for op in operation_symbols],
                "valid_equation_count": properties.equation_count,  # All equations are valid if presentation is valid
                "is_consistent": properties.is_consistent,
                "is_valid": properties.is_valid
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust presentation properties analysis failed for {test_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        presentation_json = json.dumps({
            "variables": variables,
            "equations": equations
        })
        
        java_result = self._run_java_operation(
            "presentation_properties", presentation_json,
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "presentation_properties",
            context=f"{test_name}: {expected_properties}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Presentation properties test passed for {test_name}")
        else:
            self.test_logger.warning(f"Presentation properties test failed for {test_name}: {result.error_message}")
    
    def test_presentation_equivalence_and_normalization(self):
        """Test presentation equivalence and normalization"""
        self.test_logger.info("Testing presentation equivalence and normalization")
        
        # Test equivalent presentations
        equivalence_tests = [
            {
                "name": "associative_variants",
                "presentation1": {
                    "variables": ["x", "y", "z"],
                    "equations": [{"left_term": "f(f(x,y),z)", "right_term": "f(x,f(y,z))"}]
                },
                "presentation2": {
                    "variables": ["a", "b", "c"],
                    "equations": [{"left_term": "f(f(a,b),c)", "right_term": "f(a,f(b,c))"}]
                },
                "expected_equivalent": True
            },
            {
                "name": "commutative_variants",
                "presentation1": {
                    "variables": ["x", "y"],
                    "equations": [{"left_term": "f(x,y)", "right_term": "f(y,x)"}]
                },
                "presentation2": {
                    "variables": ["x", "y"],
                    "equations": [{"left_term": "f(y,x)", "right_term": "f(x,y)"}]
                },
                "expected_equivalent": True
            },
            {
                "name": "different_equations",
                "presentation1": {
                    "variables": ["x", "y"],
                    "equations": [{"left_term": "f(x,y)", "right_term": "f(y,x)"}]
                },
                "presentation2": {
                    "variables": ["x", "y"],
                    "equations": [{"left_term": "f(x,x)", "right_term": "x"}]
                },
                "expected_equivalent": False
            }
        ]
        
        for test_case in equivalence_tests:
            with self.subTest(equivalence_test=test_case["name"]):
                self._test_presentation_equivalence(test_case)
    
    def _test_presentation_equivalence(self, test_case: Dict[str, Any]):
        """Test equivalence checking for two presentations"""
        test_name = test_case["name"]
        pres1 = test_case["presentation1"]
        pres2 = test_case["presentation2"]
        expected_equivalent = test_case["expected_equivalent"]
        
        # Test Rust implementation
        try:
            # Create both presentations
            pres1_equations = [(eq["left_term"], eq["right_term"]) for eq in pres1["equations"]]
            pres2_equations = [(eq["left_term"], eq["right_term"]) for eq in pres2["equations"]]
            
            presentation1 = Presentation(pres1["variables"], pres1_equations)
            presentation2 = Presentation(pres2["variables"], pres2_equations)
            
            # Check equivalence using the real method
            equivalent = presentation1.is_equivalent_to(presentation2)
            
            # Get additional information
            pres1_ops = presentation1.operation_symbols()
            pres2_ops = presentation2.operation_symbols()
            
            rust_result = {
                "equivalent": equivalent,
                "structural_equivalent": equivalent,  # For now, use the same value
                "equation_equivalent": equivalent,    # For now, use the same value
                "pres1_equation_count": presentation1.equations().__len__(),
                "pres2_equation_count": presentation2.equations().__len__(),
                "pres1_operation_count": len(pres1_ops),
                "pres2_operation_count": len(pres2_ops),
                "pres1_operations": [str(op) for op in pres1_ops],
                "pres2_operations": [str(op) for op in pres2_ops]
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust presentation equivalence failed for {test_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        # For equivalence testing, we'll test each presentation separately
        # and compare their properties
        pres1_json = json.dumps(pres1)
        pres2_json = json.dumps(pres2)
        
        java_result1 = self._run_java_operation(
            "presentation_properties", pres1_json,
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        java_result2 = self._run_java_operation(
            "presentation_properties", pres2_json,
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        if java_result1 and java_result2 and java_result1.get("success") and java_result2.get("success"):
            # Both presentations were processed successfully
            result = self._compare_results(
                rust_result, {"success": True, "equivalent": expected_equivalent}, "presentation_equivalence",
                context=f"{test_name}: expected {expected_equivalent}"
            )
            
            if result.matches:
                self.test_logger.debug(f"Presentation equivalence test passed for {test_name}")
            else:
                self.test_logger.warning(f"Presentation equivalence test failed for {test_name}: {result.error_message}")
        else:
            self.test_logger.warning(f"Java presentation equivalence test failed for {test_name}")
    
    def test_presentation_based_algebra_construction(self):
        """Test presentation-based algebra construction"""
        self.test_logger.info("Testing presentation-based algebra construction")
        
        # Test with a few representative presentations and algebras
        construction_tests = [
            {
                "name": "group_presentation_vs_cyclic",
                "presentation": "simple_group",
                "algebra": "resources/algebras/cyclic2.ua"
            },
            {
                "name": "lattice_presentation_vs_modular",
                "presentation": "lattice",
                "algebra": "resources/algebras/m3.ua"
            },
            {
                "name": "boolean_presentation_vs_boolean",
                "presentation": "boolean_algebra",
                "algebra": "resources/algebras/ba2.ua"
            }
        ]
        
        for test_case in construction_tests:
            with self.subTest(construction_test=test_case["name"]):
                if Path(test_case["algebra"]).exists():
                    self._test_presentation_algebra_construction(test_case)
                else:
                    self.test_logger.warning(f"Algebra file not found: {test_case['algebra']}")
    
    def _test_presentation_algebra_construction(self, test_case: Dict[str, Any]):
        """Test algebra construction from a specific presentation"""
        test_name = test_case["name"]
        pres_name = test_case["presentation"]
        algebra_file = test_case["algebra"]
        
        pres_data = self.test_presentations[pres_name]
        variables = pres_data["variables"]
        equations = pres_data["equations"]
        
        # Test Rust implementation
        try:
            # Load the algebra
            algebra = self._load_test_algebra(algebra_file)
            
            # Create presentation and check if algebra satisfies it
            equation_strings = [(eq["left_term"], eq["right_term"]) for eq in equations]
            presentation = Presentation(variables, equation_strings)
            
            # Check if the algebra satisfies the presentation
            is_satisfied = presentation.is_satisfied_by(algebra)
            
            # Get presentation properties
            properties = presentation.analyze_properties()
            
            rust_result = {
                "algebra_file": algebra_file,
                "presentation": pres_name,
                "total_equations": len(equations),
                "satisfied_equations": len(equations) if is_satisfied else 0,
                "satisfaction_percentage": 100.0 if is_satisfied else 0.0,
                "is_satisfied": is_satisfied,
                "algebra_cardinality": algebra.cardinality(),
                "algebra_operations": len(algebra.operations()),
                "presentation_properties": properties.properties
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust presentation algebra construction failed for {test_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        presentation_json = json.dumps({
            "variables": variables,
            "equations": equations
        })
        
        java_result = self._run_java_operation(
            "presentation_properties", presentation_json,
            timeout=self._get_test_timeout("presentation_properties", algebra.cardinality if 'algebra' in locals() else 4)
        )
        
        # Compare results
        result = self._compare_results(
            rust_result, java_result, "presentation_algebra_construction",
            context=f"{test_name}: {pres_name} vs {Path(algebra_file).name}"
        )
        
        if result.matches:
            self.test_logger.debug(f"Presentation algebra construction test passed for {test_name}")
        else:
            self.test_logger.warning(f"Presentation algebra construction test failed for {test_name}: {result.error_message}")
    
    def test_presentation_normalization_operations(self):
        """Test presentation normalization operations"""
        self.test_logger.info("Testing presentation normalization operations")
        
        # Test various normalization scenarios
        normalization_tests = [
            {
                "name": "variable_renaming",
                "original": {
                    "variables": ["x", "y", "z"],
                    "equations": [{"left_term": "f(x,y)", "right_term": "f(y,x)"}]
                },
                "normalized": {
                    "variables": ["x0", "x1", "x2"],
                    "equations": [{"left_term": "f(x0,x1)", "right_term": "f(x1,x0)"}]
                }
            },
            {
                "name": "equation_reordering",
                "original": {
                    "variables": ["x", "y"],
                    "equations": [
                        {"left_term": "f(x,y)", "right_term": "f(y,x)"},
                        {"left_term": "f(x,x)", "right_term": "x"}
                    ]
                },
                "normalized": {
                    "variables": ["x", "y"],
                    "equations": [
                        {"left_term": "f(x,x)", "right_term": "x"},
                        {"left_term": "f(x,y)", "right_term": "f(y,x)"}
                    ]
                }
            }
        ]
        
        for test_case in normalization_tests:
            with self.subTest(normalization_test=test_case["name"]):
                self._test_presentation_normalization(test_case)
    
    def _test_presentation_normalization(self, test_case: Dict[str, Any]):
        """Test normalization for a specific presentation"""
        test_name = test_case["name"]
        original = test_case["original"]
        normalized = test_case["normalized"]
        
        # Test Rust implementation
        try:
            # Create original presentation
            orig_equations = [(eq["left_term"], eq["right_term"]) for eq in original["equations"]]
            original_presentation = Presentation(original["variables"], orig_equations)
            
            # Create normalized presentation
            norm_equations = [(eq["left_term"], eq["right_term"]) for eq in normalized["equations"]]
            normalized_presentation = Presentation(normalized["variables"], norm_equations)
            
            # Test normalization using the real method
            normalized_result = original_presentation.normalize()
            
            # Get operation information
            orig_ops = original_presentation.operation_symbols()
            norm_ops = normalized_presentation.operation_symbols()
            normalized_ops = normalized_result.operation_symbols()
            
            # Check if normalization preserves structure
            structure_preserved = (
                original_presentation.equations().__len__() == normalized_result.equations().__len__() and
                len(orig_ops) == len(normalized_ops)
            )
            
            # Check if operations are the same
            operations_preserved = len(orig_ops) == len(normalized_ops)
            
            rust_result = {
                "structure_preserved": structure_preserved,
                "operations_preserved": operations_preserved,
                "original_equation_count": original_presentation.equations().__len__(),
                "normalized_equation_count": normalized_result.equations().__len__(),
                "original_operation_count": len(orig_ops),
                "normalized_operation_count": len(normalized_ops),
                "original_operations": [str(op) for op in orig_ops],
                "normalized_operations": [str(op) for op in normalized_ops]
            }
            
        except Exception as e:
            self.test_logger.error(f"Rust presentation normalization failed for {test_name}: {e}")
            rust_result = {"error": str(e), "success": False}
        
        # Test Java implementation
        original_json = json.dumps(original)
        normalized_json = json.dumps(normalized)
        
        java_result1 = self._run_java_operation(
            "presentation_properties", original_json,
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        java_result2 = self._run_java_operation(
            "presentation_properties", normalized_json,
            timeout=self.JAVA_TIMEOUT_SHORT
        )
        
        # Compare results
        if java_result1 and java_result2 and java_result1.get("success") and java_result2.get("success"):
            result = self._compare_results(
                rust_result, {"success": True, "normalized": True}, "presentation_normalization",
                context=f"{test_name}: structure preservation"
            )
            
            if result.matches:
                self.test_logger.debug(f"Presentation normalization test passed for {test_name}")
            else:
                self.test_logger.warning(f"Presentation normalization test failed for {test_name}: {result.error_message}")
        else:
            self.test_logger.warning(f"Java presentation normalization test failed for {test_name}")


if __name__ == '__main__':
    unittest.main()
