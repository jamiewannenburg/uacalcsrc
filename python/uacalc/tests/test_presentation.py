#!/usr/bin/env python3
"""
Tests for Presentation class.

This module tests the Presentation functionality including creation,
getters, and basic operations.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import uacalc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uacalc_lib
# Import from the correct module structure
Presentation = uacalc_lib.eq.Presentation
Equation = uacalc_lib.eq.Equation
VariableImp = uacalc_lib.terms.VariableImp
NonVariableTerm = uacalc_lib.terms.NonVariableTerm
OperationSymbol = uacalc_lib.alg.OperationSymbol


class TestPresentation(unittest.TestCase):
    """Test cases for Presentation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.variables = ["x", "y", "z"]
        self.empty_relations = []
        
        # Create some test equations
        x = VariableImp("x")
        y = VariableImp("y")
        z = VariableImp("z")
        
        # Create operation symbol for testing
        f = OperationSymbol("f", 2)
        
        # Create some test equations
        self.eq1 = Equation(x, y)
        self.eq2 = Equation(y, z)
        self.test_relations = [self.eq1, self.eq2]
    
    def test_presentation_creation_empty(self):
        """Test creating a presentation with no relations."""
        pres = Presentation(self.variables, self.empty_relations)
        
        self.assertEqual(len(pres.get_variables()), 3)
        self.assertEqual(len(pres.get_relations()), 0)
        self.assertEqual(pres.get_variables(), ["x", "y", "z"])
    
    def test_presentation_creation_with_relations(self):
        """Test creating a presentation with relations."""
        pres = Presentation(self.variables, self.test_relations)
        
        self.assertEqual(len(pres.get_variables()), 3)
        self.assertEqual(len(pres.get_relations()), 2)
        self.assertEqual(pres.get_variables(), ["x", "y", "z"])
    
    def test_presentation_getters(self):
        """Test getter methods."""
        pres = Presentation(self.variables, self.test_relations)
        
        # Test get_variables
        variables = pres.get_variables()
        self.assertIsInstance(variables, list)
        self.assertEqual(variables, ["x", "y", "z"])
        
        # Test get_relations
        relations = pres.get_relations()
        self.assertIsInstance(relations, list)
        self.assertEqual(len(relations), 2)
        # Relations should be string representations of equations
        self.assertIsInstance(relations[0], str)
        self.assertIsInstance(relations[1], str)
    
    def test_presentation_str(self):
        """Test string representation."""
        pres = Presentation(self.variables, self.empty_relations)
        str_repr = str(pres)
        
        self.assertIn("Presentation", str_repr)
        self.assertIn("variables=[x, y, z]", str_repr)
        self.assertIn("relations=[]", str_repr)
    
    def test_presentation_repr(self):
        """Test detailed string representation."""
        pres = Presentation(self.variables, self.test_relations)
        repr_str = repr(pres)
        
        self.assertIn("Presentation", repr_str)
        self.assertIn("variables=[x, y, z]", repr_str)
        self.assertIn("relations=", repr_str)
    
    def test_presentation_with_single_variable(self):
        """Test presentation with single variable."""
        single_var = ["x"]
        pres = Presentation(single_var, self.empty_relations)
        
        self.assertEqual(len(pres.get_variables()), 1)
        self.assertEqual(pres.get_variables(), ["x"])
    
    def test_presentation_with_single_relation(self):
        """Test presentation with single relation."""
        single_rel = [self.eq1]
        pres = Presentation(self.variables, single_rel)
        
        self.assertEqual(len(pres.get_variables()), 3)
        self.assertEqual(len(pres.get_relations()), 1)
    
    def test_presentation_empty_variables(self):
        """Test presentation with empty variables list."""
        pres = Presentation([], self.empty_relations)
        
        self.assertEqual(len(pres.get_variables()), 0)
        self.assertEqual(len(pres.get_relations()), 0)
        self.assertEqual(pres.get_variables(), [])
    
    def test_presentation_complex_relations(self):
        """Test presentation with complex relations."""
        # Create more complex equations
        x = VariableImp("x")
        y = VariableImp("y")
        f = OperationSymbol("f", 2)
        
        # Create f(x,y) term
        fxy = NonVariableTerm(f, [x, y])
        
        # Create equation f(x,y) = x
        complex_eq = Equation(fxy, x)
        
        pres = Presentation(self.variables, [complex_eq])
        
        self.assertEqual(len(pres.get_variables()), 3)
        self.assertEqual(len(pres.get_relations()), 1)
        
        relations = pres.get_relations()
        self.assertIsInstance(relations[0], str)
        # Should contain the equation representation
        self.assertIn("=", relations[0])
    
    def test_presentation_immutability(self):
        """Test that presentation data is immutable from outside."""
        pres = Presentation(self.variables, self.test_relations)
        
        # Get references to internal data
        variables = pres.get_variables()
        relations = pres.get_relations()
        
        # These should be copies, not references to internal data
        # Modifying them shouldn't affect the original
        original_var_count = len(variables)
        original_rel_count = len(relations)
        
        # Try to modify (this should not affect the original)
        variables.append("w")
        relations.append("new_relation")
        
        # Original should be unchanged
        self.assertEqual(len(pres.get_variables()), original_var_count)
        self.assertEqual(len(pres.get_relations()), original_rel_count)


class TestPresentationIntegration(unittest.TestCase):
    """Integration tests for Presentation with other components."""
    
    def test_presentation_with_equations_module(self):
        """Test presentation with equations from equations module."""
        try:
            associative_law = uacalc_lib.eq.associative_law
            
            # Create operation symbol
            f = OperationSymbol("multiply", 2)
            
            # Create associative law equation
            assoc_eq = associative_law(f)
            self.assertIsNotNone(assoc_eq)
            
            # Create presentation with this equation
            variables = ["x", "y", "z"]
            pres = Presentation(variables, [assoc_eq])
            
            self.assertEqual(len(pres.get_variables()), 3)
            self.assertEqual(len(pres.get_relations()), 1)
            
        except ImportError:
            self.skipTest("equations module not available")
    
    def test_presentation_serialization(self):
        """Test that presentation can be serialized/deserialized."""
        pres = Presentation(["x", "y"], [])
        
        # Test that we can get string representations
        str_repr = str(pres)
        repr_str = repr(pres)
        
        self.assertIsInstance(str_repr, str)
        self.assertIsInstance(repr_str, str)
        self.assertGreater(len(str_repr), 0)
        self.assertGreater(len(repr_str), 0)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)