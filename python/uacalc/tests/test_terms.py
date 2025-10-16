"""
Tests for term evaluation in Python bindings.
"""

import unittest
import os
import sys

# Import through uacalc_lib module
import uacalc_lib


class TestTermEvaluation(unittest.TestCase):
    """Test term evaluation with loaded algebras."""
    
    def test_variable_creation(self):
        """Test creating variables."""
        VariableImp = uacalc_lib.terms.VariableImp
        
        x = VariableImp("x")
        self.assertEqual(x.get_name(), "x")
        self.assertTrue(x.isa_variable())
        self.assertEqual(x.depth(), 0)
        self.assertEqual(x.length(), 1)
    
    def test_predefined_variables(self):
        """Test predefined variables x, y, z."""
        VariableImp = uacalc_lib.terms.VariableImp
        
        x = VariableImp.x()
        y = VariableImp.y()
        z = VariableImp.z()
        
        self.assertEqual(x.get_name(), "x")
        self.assertEqual(y.get_name(), "y")
        self.assertEqual(z.get_name(), "z")
    
    def test_variable_properties(self):
        """Test variable properties."""
        VariableImp = uacalc_lib.terms.VariableImp
        
        x = VariableImp("x")
        self.assertTrue(x.isa_variable())
        self.assertEqual(x.depth(), 0)
        self.assertEqual(x.length(), 1)
        
        var_list = x.get_variable_list()
        self.assertEqual(len(var_list), 1)
        self.assertEqual(var_list[0], "x")
    
    def test_variable_string_representation(self):
        """Test variable string representation."""
        VariableImp = uacalc_lib.terms.VariableImp
        
        x = VariableImp("x")
        self.assertEqual(str(x), "x")
        self.assertEqual(repr(x), 'VariableImp("x")')
    
    def test_variable_equality(self):
        """Test variable equality."""
        VariableImp = uacalc_lib.terms.VariableImp
        
        x1 = VariableImp("x")
        x2 = VariableImp("x")
        y = VariableImp("y")
        
        self.assertEqual(x1, x2)
        self.assertNotEqual(x1, y)
    
    def test_variable_hash(self):
        """Test variable hashing."""
        VariableImp = uacalc_lib.terms.VariableImp
        
        x1 = VariableImp("x")
        x2 = VariableImp("x")
        y = VariableImp("y")
        
        # Same name should have same hash
        self.assertEqual(hash(x1), hash(x2))
        # Different names should have different hash (usually)
        self.assertNotEqual(hash(x1), hash(y))
    
    def test_variable_eval_with_simple_algebra(self):
        """Test variable evaluation with a simple algebra."""
        VariableImp = uacalc_lib.terms.VariableImp
        AlgebraReader = uacalc_lib.io.AlgebraReader
        
        # Try to load an algebra file
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        reader = AlgebraReader.from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Create a variable term
        x = VariableImp("x")
        
        # Evaluate: x = 0
        var_map = {"x": 0}
        result = x.eval(alg, var_map)
        self.assertEqual(result, 0)
        
        # Evaluate: x = 1
        var_map = {"x": 1}
        result = x.eval(alg, var_map)
        self.assertEqual(result, 1)
        
        # Evaluate: x = 2
        var_map = {"x": 2}
        result = x.eval(alg, var_map)
        self.assertEqual(result, 2)
    
    def test_variable_int_eval(self):
        """Test variable int_eval method."""
        VariableImp = uacalc_lib.terms.VariableImp
        AlgebraReader = uacalc_lib.io.AlgebraReader
        
        # Try to load an algebra file
        algebra_path = "resources/algebras/cyclic2.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        reader = AlgebraReader.from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Create a variable term
        x = VariableImp("x")
        
        # Evaluate using int_eval
        var_map = {"x": 1}
        result = x.int_eval(alg, var_map)
        self.assertEqual(result, 1)
    
    def test_variable_eval_missing_variable(self):
        """Test that evaluating with missing variable raises error."""
        VariableImp = uacalc_lib.terms.VariableImp
        AlgebraReader = uacalc_lib.io.AlgebraReader
        
        # Try to load an algebra file
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        reader = AlgebraReader.from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Create a variable term
        x = VariableImp("x")
        
        # Try to evaluate without providing value for x
        var_map = {}
        with self.assertRaises(ValueError):
            x.eval(alg, var_map)
    
    def test_variable_eval_with_different_algebras(self):
        """Test variable evaluation with different algebra files."""
        VariableImp = uacalc_lib.terms.VariableImp
        AlgebraReader = uacalc_lib.io.AlgebraReader
        
        # List of algebra files to test
        algebra_files = [
            "resources/algebras/cyclic2.ua",
            "resources/algebras/cyclic3.ua",
            "resources/algebras/n5.ua",
        ]
        
        for algebra_path in algebra_files:
            if not os.path.exists(algebra_path):
                print(f"Skipping {algebra_path} - not found")
                continue
            
            try:
                # Load algebra
                reader = AlgebraReader.from_file(algebra_path)
                alg = reader.read_algebra_file()
                
                # Create a variable term
                x = VariableImp("x")
                
                # Evaluate: x = 0
                var_map = {"x": 0}
                result = x.eval(alg, var_map)
                self.assertEqual(result, 0, f"Failed for {algebra_path}")
                
                print(f"✓ Successfully evaluated variable in {algebra_path}")
            except Exception as e:
                print(f"✗ Failed for {algebra_path}: {e}")


if __name__ == '__main__':
    unittest.main()
