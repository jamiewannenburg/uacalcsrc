"""
Tests for the Equations module Python bindings.

This module tests the equation generation functions (associative_law, cyclic_law,
first_second_symmetric_law) and verifies they match the Java implementation.
"""

import unittest
import json
import subprocess
import sys
import os
from typing import Dict, Any, Optional

# Import test utilities
from test_utils import TestConfig, run_java_wrapper


class TestEquations(unittest.TestCase):
    """Test the Equations module Python bindings."""
    
    def setUp(self):
        """Set up test configuration."""
        self.config = TestConfig(default_timeout=30.0, memory_limit_mb=1024)
    
    def test_associative_law_binary_operation(self):
        """Test associative law with binary operation."""
        import uacalc_lib
        
        # Create binary operation symbol
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        op = OperationSymbol("multiply", 2, False)
        
        # Generate equation using Python
        equation = uacalc_lib.eq.associative_law(op)
        
        # Verify equation structure
        self.assertIsNotNone(equation)
        self.assertIn("multiply", str(equation))
        self.assertIn("x", str(equation))
        self.assertIn("y", str(equation))
        self.assertIn("z", str(equation))
        
        # Compare with Java implementation
        java_result = run_java_wrapper(
            "eq.EquationsWrapper",
            ["associative-law", "--op-name", "multiply", "--op-arity", "2"],
            self.config
        )
        
        # Parse Java output to extract equation
        java_equation = None
        for line in java_result.stdout.split('\n'):
            if line.startswith("Equation:"):
                java_equation = line.split(":", 1)[1].strip()
                break
        
        self.assertIsNotNone(java_equation, "Java wrapper should return equation")
        self.assertEqual(str(equation), java_equation, "Python and Java should produce identical equations")
    
    def test_associative_law_wrong_arity(self):
        """Test associative law with wrong arity (should raise error)."""
        import uacalc_lib
        
        # Create unary operation symbol (wrong arity for associative law)
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        op = OperationSymbol("unary_op", 1, False)
        
        # Should raise ValueError
        with self.assertRaises(Exception) as context:
            uacalc_lib.eq.associative_law(op)
        
        # Verify error message
        self.assertIn("arity must be 2", str(context.exception))
        
        # Compare with Java implementation
        java_result = run_java_wrapper(
            "eq.EquationsWrapper",
            ["associative-law", "--op-name", "unary_op", "--op-arity", "1"],
            self.config
        )
        
        # Java should also fail
        self.assertNotEqual(java_result.exit_code, 0, "Java wrapper should fail for wrong arity")
        self.assertIn("arity must be 2", java_result.stderr)
    
    def test_cyclic_law_ternary_operation(self):
        """Test cyclic law with ternary operation."""
        import uacalc_lib
        
        # Create ternary operation symbol
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        op = OperationSymbol("ternary_op", 3, False)
        
        # Generate equation using Python
        equation = uacalc_lib.eq.cyclic_law(op)
        
        # Verify equation structure
        self.assertIsNotNone(equation)
        self.assertIn("ternary_op", str(equation))
        self.assertIn("x0", str(equation))
        self.assertIn("x1", str(equation))
        self.assertIn("x2", str(equation))
        
        # Compare with Java implementation
        java_result = run_java_wrapper(
            "eq.EquationsWrapper",
            ["cyclic-law", "--op-name", "ternary_op", "--op-arity", "3"],
            self.config
        )
        
        # Parse Java output to extract equation
        java_equation = None
        for line in java_result.stdout.split('\n'):
            if line.startswith("Equation:"):
                java_equation = line.split(":", 1)[1].strip()
                break
        
        self.assertIsNotNone(java_equation, "Java wrapper should return equation")
        self.assertEqual(str(equation), java_equation, "Python and Java should produce identical equations")
    
    def test_cyclic_law_unary_operation(self):
        """Test cyclic law with unary operation (should work)."""
        import uacalc_lib
        
        # Create unary operation symbol
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        op = OperationSymbol("unary_op", 1, False)
        
        # Generate equation using Python
        equation = uacalc_lib.eq.cyclic_law(op)
        
        # Verify equation structure (should be f(x0) = f(x0))
        self.assertIsNotNone(equation)
        self.assertIn("unary_op", str(equation))
        self.assertIn("x0", str(equation))
        
        # Compare with Java implementation
        java_result = run_java_wrapper(
            "eq.EquationsWrapper",
            ["cyclic-law", "--op-name", "unary_op", "--op-arity", "1"],
            self.config
        )
        
        # Parse Java output to extract equation
        java_equation = None
        for line in java_result.stdout.split('\n'):
            if line.startswith("Equation:"):
                java_equation = line.split(":", 1)[1].strip()
                break
        
        self.assertIsNotNone(java_equation, "Java wrapper should return equation")
        self.assertEqual(str(equation), java_equation, "Python and Java should produce identical equations")
    
    def test_cyclic_law_zero_arity(self):
        """Test cyclic law with zero arity (should raise error)."""
        import uacalc_lib
        
        # Create constant operation symbol (zero arity)
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        op = OperationSymbol("constant", 0, False)
        
        # Should raise ValueError
        with self.assertRaises(Exception) as context:
            uacalc_lib.eq.cyclic_law(op)
        
        # Verify error message
        self.assertIn("arity must be at least 1", str(context.exception))
        
        # Compare with Java implementation
        java_result = run_java_wrapper(
            "eq.EquationsWrapper",
            ["cyclic-law", "--op-name", "constant", "--op-arity", "0"],
            self.config
        )
        
        # Java should also fail
        self.assertNotEqual(java_result.exit_code, 0, "Java wrapper should fail for zero arity")
        self.assertIn("arity must be at least 1", java_result.stderr)
    
    def test_first_second_symmetric_law_binary_operation(self):
        """Test first-second symmetric law with binary operation."""
        import uacalc_lib
        
        # Create binary operation symbol
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        op = OperationSymbol("binary_op", 2, False)
        
        # Generate equation using Python
        equation = uacalc_lib.eq.first_second_symmetric_law(op)
        
        # Verify equation structure
        self.assertIsNotNone(equation)
        self.assertIn("binary_op", str(equation))
        self.assertIn("x0", str(equation))
        self.assertIn("x1", str(equation))
        
        # Compare with Java implementation
        java_result = run_java_wrapper(
            "eq.EquationsWrapper",
            ["first-second-symmetric-law", "--op-name", "binary_op", "--op-arity", "2"],
            self.config
        )
        
        # Parse Java output to extract equation
        java_equation = None
        for line in java_result.stdout.split('\n'):
            if line.startswith("Equation:"):
                java_equation = line.split(":", 1)[1].strip()
                break
        
        self.assertIsNotNone(java_equation, "Java wrapper should return equation")
        self.assertEqual(str(equation), java_equation, "Python and Java should produce identical equations")
    
    def test_first_second_symmetric_law_ternary_operation(self):
        """Test first-second symmetric law with ternary operation."""
        import uacalc_lib
        
        # Create ternary operation symbol
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        op = OperationSymbol("ternary_op", 3, False)
        
        # Generate equation using Python
        equation = uacalc_lib.eq.first_second_symmetric_law(op)
        
        # Verify equation structure
        self.assertIsNotNone(equation)
        self.assertIn("ternary_op", str(equation))
        self.assertIn("x0", str(equation))
        self.assertIn("x1", str(equation))
        self.assertIn("x2", str(equation))
        
        # Compare with Java implementation
        java_result = run_java_wrapper(
            "eq.EquationsWrapper",
            ["first-second-symmetric-law", "--op-name", "ternary_op", "--op-arity", "3"],
            self.config
        )
        
        # Parse Java output to extract equation
        java_equation = None
        for line in java_result.stdout.split('\n'):
            if line.startswith("Equation:"):
                java_equation = line.split(":", 1)[1].strip()
                break
        
        self.assertIsNotNone(java_equation, "Java wrapper should return equation")
        self.assertEqual(str(equation), java_equation, "Python and Java should produce identical equations")
    
    def test_first_second_symmetric_law_wrong_arity(self):
        """Test first-second symmetric law with wrong arity (should raise error)."""
        import uacalc_lib
        
        # Create unary operation symbol (wrong arity for first-second symmetric law)
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        op = OperationSymbol("unary_op", 1, False)
        
        # Should raise ValueError
        with self.assertRaises(Exception) as context:
            uacalc_lib.eq.first_second_symmetric_law(op)
        
        # Verify error message
        self.assertIn("arity must be at least 2", str(context.exception))
        
        # Compare with Java implementation
        java_result = run_java_wrapper(
            "eq.EquationsWrapper",
            ["first-second-symmetric-law", "--op-name", "unary_op", "--op-arity", "1"],
            self.config
        )
        
        # Java should also fail
        self.assertNotEqual(java_result.exit_code, 0, "Java wrapper should fail for wrong arity")
        self.assertIn("arity must be at least 2", java_result.stderr)
    
    def test_equation_properties(self):
        """Test that generated equations have correct properties."""
        import uacalc_lib
        
        # Test associative law equation properties
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        op = OperationSymbol("multiply", 2, False)
        equation = uacalc_lib.eq.associative_law(op)
        
        # Test equation methods
        left_side = equation.left_side()
        right_side = equation.right_side()
        variables = equation.get_variable_list()
        
        self.assertIsInstance(left_side, str)
        self.assertIsInstance(right_side, str)
        self.assertIsInstance(variables, list)
        
        # Verify variables
        self.assertIn("x", variables)
        self.assertIn("y", variables)
        self.assertIn("z", variables)
        self.assertEqual(len(variables), 3)
        
        # Verify equation string representation
        equation_str = str(equation)
        self.assertIn("=", equation_str)
        self.assertIn(left_side, equation_str)
        self.assertIn(right_side, equation_str)
    
    def test_java_wrapper_test_command(self):
        """Test the Java wrapper test command to verify all functions work."""
        java_result = run_java_wrapper(
            "eq.EquationsWrapper",
            ["test"],
            self.config
        )
        
        # Java test command should succeed
        self.assertEqual(java_result.exit_code, 0, "Java test command should succeed")
        
        # Verify output contains expected test results
        output = java_result.stdout
        self.assertIn("Associative law generated", output)
        self.assertIn("Cyclic law generated", output)
        self.assertIn("First-second symmetric law generated", output)
        self.assertIn("All tests completed", output)
    
    def test_equation_variable_extraction(self):
        """Test that equations correctly extract variables from both sides."""
        import uacalc_lib
        
        # Test with different operation symbols
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        
        # Test associative law (should have x, y, z)
        op1 = OperationSymbol("multiply", 2, False)
        eq1 = uacalc_lib.eq.associative_law(op1)
        vars1 = eq1.get_variable_list()
        self.assertEqual(set(vars1), {"x", "y", "z"})
        
        # Test cyclic law with ternary operation (should have x0, x1, x2)
        op2 = OperationSymbol("ternary_op", 3, False)
        eq2 = uacalc_lib.eq.cyclic_law(op2)
        vars2 = eq2.get_variable_list()
        self.assertEqual(set(vars2), {"x0", "x1", "x2"})
        
        # Test first-second symmetric law with binary operation (should have x0, x1)
        op3 = OperationSymbol("binary_op", 2, False)
        eq3 = uacalc_lib.eq.first_second_symmetric_law(op3)
        vars3 = eq3.get_variable_list()
        self.assertEqual(set(vars3), {"x0", "x1"})


if __name__ == '__main__':
    unittest.main()
