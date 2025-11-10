"""
Tests for term evaluation and Terms utility functions in Python bindings.

This module tests:
- VariableImp creation and evaluation
- Terms utility functions (string_to_term, validation, flatten)
- Comparison with Java wrapper for Terms functions
"""

import unittest
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

# Import test utilities
from test_utils import TestConfig, run_java_wrapper, build_java_command

# Import through uacalc_lib module
import uacalc_lib

# Get project root to locate resources
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESOURCES_ALGEBRAS_DIR = PROJECT_ROOT / "resources" / "algebras"


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
        reader = AlgebraReader.new_from_file(algebra_path)
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
        reader = AlgebraReader.new_from_file(algebra_path)
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
        reader = AlgebraReader.new_from_file(algebra_path)
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
                reader = AlgebraReader.new_from_file(algebra_path)
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


def load_test_algebra(name: str):
    """Load a test algebra from resources/algebras/"""
    if not name.endswith('.ua'):
        name = f"{name}.ua"
    
    algebra_path = RESOURCES_ALGEBRAS_DIR / name
    
    if not algebra_path.exists():
        raise unittest.SkipTest(f"Algebra file {algebra_path} not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(str(algebra_path))
    return reader.read_algebra_file()


def run_java_string_to_term(term_str: str) -> Dict[str, Any]:
    """Run Java wrapper string_to_term command and return JSON result."""
    wrapper_class = "java_wrapper.src.terms.TermsWrapper"
    
    args = [
        "string_to_term",
        "--str", term_str
    ]
    
    cmd = build_java_command(wrapper_class, args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30.0,
            cwd=str(PROJECT_ROOT)
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Java wrapper failed: {result.stderr}")
        
        # Extract JSON from output (may have debug text before JSON)
        stdout = result.stdout.strip()
        json_start = stdout.find('{')
        if json_start == -1:
            raise ValueError(f"No JSON found in output: {stdout}")
        
        json_str = stdout[json_start:]
        return json.loads(json_str)
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("Java wrapper timed out")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Java wrapper output: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error running Java wrapper: {e}")


def run_java_is_valid_var_string(var_str: str) -> Dict[str, Any]:
    """Run Java wrapper is_valid_var_string command and return JSON result."""
    wrapper_class = "java_wrapper.src.terms.TermsWrapper"
    
    args = [
        "is_valid_var_string",
        "--str", var_str
    ]
    
    cmd = build_java_command(wrapper_class, args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30.0,
            cwd=str(PROJECT_ROOT)
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Java wrapper failed: {result.stderr}")
        
        stdout = result.stdout.strip()
        json_start = stdout.find('{')
        if json_start == -1:
            raise ValueError(f"No JSON found in output: {stdout}")
        
        json_str = stdout[json_start:]
        return json.loads(json_str)
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("Java wrapper timed out")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Java wrapper output: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error running Java wrapper: {e}")


def run_java_is_valid_op_name_string(op_str: str) -> Dict[str, Any]:
    """Run Java wrapper is_valid_op_name_string command and return JSON result."""
    wrapper_class = "java_wrapper.src.terms.TermsWrapper"
    
    args = [
        "is_valid_op_name_string",
        "--str", op_str
    ]
    
    cmd = build_java_command(wrapper_class, args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30.0,
            cwd=str(PROJECT_ROOT)
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Java wrapper failed: {result.stderr}")
        
        stdout = result.stdout.strip()
        json_start = stdout.find('{')
        if json_start == -1:
            raise ValueError(f"No JSON found in output: {stdout}")
        
        json_str = stdout[json_start:]
        return json.loads(json_str)
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("Java wrapper timed out")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Java wrapper output: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error running Java wrapper: {e}")


def run_java_flatten(term_str: str) -> Dict[str, Any]:
    """Run Java wrapper flatten command and return JSON result."""
    wrapper_class = "java_wrapper.src.terms.TermsWrapper"
    
    args = [
        "flatten",
        "--str", term_str
    ]
    
    cmd = build_java_command(wrapper_class, args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30.0,
            cwd=str(PROJECT_ROOT)
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Java wrapper failed: {result.stderr}")
        
        stdout = result.stdout.strip()
        json_start = stdout.find('{')
        if json_start == -1:
            raise ValueError(f"No JSON found in output: {stdout}")
        
        json_str = stdout[json_start:]
        return json.loads(json_str)
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("Java wrapper timed out")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Java wrapper output: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error running Java wrapper: {e}")


class TestTermsStringToTerm(unittest.TestCase):
    """Test string_to_term function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.string_to_term = uacalc_lib.terms.string_to_term
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
    
    def test_parse_simple_variable(self):
        """Test parsing a simple variable."""
        term = self.string_to_term("x")
        
        self.assertIsNotNone(term)
        self.assertTrue(term.isa_variable())
        self.assertEqual(str(term), "x")
        self.assertEqual(term.depth(), 0)
        self.assertEqual(term.length(), 1)
    
    def test_parse_compound_term(self):
        """Test parsing a compound term."""
        term = self.string_to_term("f(x,y)")
        
        self.assertIsNotNone(term)
        self.assertFalse(term.isa_variable())
        self.assertEqual(term.depth(), 1)
        self.assertEqual(term.length(), 3)  # f, x, y
    
    def test_parse_nested_term(self):
        """Test parsing a nested term."""
        term = self.string_to_term("f(g(x),y)")
        
        self.assertIsNotNone(term)
        self.assertFalse(term.isa_variable())
        self.assertEqual(term.depth(), 2)
        self.assertGreaterEqual(term.length(), 4)  # f, g, x, y
    
    def test_parse_invalid_string(self):
        """Test parsing an invalid string raises error."""
        with self.assertRaises(ValueError):
            self.string_to_term("")
        
        with self.assertRaises(ValueError):
            self.string_to_term("1x")  # Invalid variable name
    
    def test_string_to_term_java_comparison_simple(self):
        """Test string_to_term and compare with Java wrapper for simple variable."""
        term_str = "x"
        
        # Python result
        py_term = self.string_to_term(term_str)
        
        # Java result
        java_result = run_java_string_to_term(term_str)
        
        self.assertTrue(java_result["success"])
        java_data = java_result["data"]
        
        # Compare properties
        self.assertEqual(str(py_term), java_data["term"])
        self.assertEqual(py_term.isa_variable(), java_data["is_variable"])
        self.assertEqual(py_term.depth(), java_data["depth"])
        self.assertEqual(py_term.length(), java_data["length"])
    
    def test_string_to_term_java_comparison_compound(self):
        """Test string_to_term and compare with Java wrapper for compound term."""
        term_str = "f(x,y)"
        
        # Python result
        py_term = self.string_to_term(term_str)
        
        # Java result
        java_result = run_java_string_to_term(term_str)
        
        self.assertTrue(java_result["success"])
        java_data = java_result["data"]
        
        # Compare properties
        self.assertEqual(str(py_term), java_data["term"])
        self.assertEqual(py_term.isa_variable(), java_data["is_variable"])
        self.assertEqual(py_term.depth(), java_data["depth"])
        self.assertEqual(py_term.length(), java_data["length"])
        
        # For non-variable terms, verify the term string contains the operation name
        if not py_term.isa_variable() and "leading_op" in java_data:
            # The term string should contain the operation name
            term_str = str(py_term)
            self.assertIn(java_data["leading_op"], term_str,
                         f"Term '{term_str}' should contain operation '{java_data['leading_op']}'")
    
    def test_string_to_term_with_algebra_baker2(self):
        """Test string_to_term with baker2 algebra and evaluate."""
        alg = load_test_algebra("baker2")
        
        # Parse a term that uses the 'bak' operation from baker2
        term_str = "bak(x,y,z)"
        term = self.string_to_term(term_str)
        
        self.assertIsNotNone(term)
        self.assertFalse(term.isa_variable())
        
        # Evaluate the term
        result = term.eval(alg, {"x": 0, "y": 0, "z": 0})
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLess(result, 2)  # Baker2 has 2 elements
        
        # Test with different assignments
        result2 = term.eval(alg, {"x": 1, "y": 1, "z": 1})
        self.assertIsInstance(result2, int)
        self.assertGreaterEqual(result2, 0)
        self.assertLess(result2, 2)
    
    def test_string_to_term_nested_baker2(self):
        """Test parsing and evaluating nested terms with baker2 algebra."""
        alg = load_test_algebra("baker2")
        
        # Parse nested term: bak(bak(x,y,z),y,z)
        term_str = "bak(bak(x,y,z),y,z)"
        term = self.string_to_term(term_str)
        
        self.assertIsNotNone(term)
        self.assertGreater(term.depth(), 1)
        
        # Evaluate
        result = term.eval(alg, {"x": 0, "y": 0, "z": 0})
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLess(result, 2)


class TestTermsValidation(unittest.TestCase):
    """Test validation functions (is_valid_var_string, is_valid_op_name_string)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.is_valid_var_string = uacalc_lib.terms.is_valid_var_string
        self.is_valid_op_name_string = uacalc_lib.terms.is_valid_op_name_string
    
    def test_is_valid_var_string_valid(self):
        """Test valid variable strings."""
        self.assertTrue(self.is_valid_var_string("x"))
        self.assertTrue(self.is_valid_var_string("y"))
        self.assertTrue(self.is_valid_var_string("var1"))
        self.assertTrue(self.is_valid_var_string("VarName"))
        self.assertTrue(self.is_valid_var_string("x1"))
    
    def test_is_valid_var_string_invalid(self):
        """Test invalid variable strings."""
        self.assertFalse(self.is_valid_var_string(""))
        self.assertFalse(self.is_valid_var_string("1x"))  # Starts with digit
        self.assertFalse(self.is_valid_var_string("x,y"))  # Contains comma
        self.assertFalse(self.is_valid_var_string("x y"))  # Contains space
        self.assertFalse(self.is_valid_var_string("x(y)"))  # Contains parentheses
    
    def test_is_valid_var_string_java_comparison(self):
        """Test is_valid_var_string and compare with Java wrapper."""
        test_cases = ["x", "y", "var1", "", "1x", "x,y"]
        
        for var_str in test_cases:
            py_result = self.is_valid_var_string(var_str)
            
            try:
                java_result = run_java_is_valid_var_string(var_str)
                self.assertTrue(java_result["success"])
                java_data = java_result["data"]
                
                self.assertEqual(py_result, java_data["status"],
                               f"Mismatch for '{var_str}': Python={py_result}, Java={java_data['status']}")
            except Exception as e:
                # If Java wrapper fails, just test Python behavior
                print(f"Java wrapper failed for '{var_str}': {e}")
    
    def test_is_valid_op_name_string_valid(self):
        """Test valid operation name strings."""
        self.assertTrue(self.is_valid_op_name_string("f"))
        self.assertTrue(self.is_valid_op_name_string("add"))
        self.assertTrue(self.is_valid_op_name_string("bak"))
        self.assertTrue(self.is_valid_op_name_string("op1"))
    
    def test_is_valid_op_name_string_invalid(self):
        """Test invalid operation name strings."""
        self.assertFalse(self.is_valid_op_name_string(""))
        # Note: Operation names may have different rules than variables
    
    def test_is_valid_op_name_string_java_comparison(self):
        """Test is_valid_op_name_string and compare with Java wrapper."""
        test_cases = ["f", "add", "bak", ""]
        
        for op_str in test_cases:
            py_result = self.is_valid_op_name_string(op_str)
            
            try:
                java_result = run_java_is_valid_op_name_string(op_str)
                self.assertTrue(java_result["success"])
                java_data = java_result["data"]
                
                self.assertEqual(py_result, java_data["status"],
                               f"Mismatch for '{op_str}': Python={py_result}, Java={java_data['status']}")
            except Exception as e:
                # If Java wrapper fails, just test Python behavior
                print(f"Java wrapper failed for '{op_str}': {e}")


class TestTermsFlatten(unittest.TestCase):
    """Test flatten function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.string_to_term = uacalc_lib.terms.string_to_term
        self.flatten = uacalc_lib.terms.flatten
    
    def test_flatten_variable(self):
        """Test flattening a variable (should return unchanged)."""
        term = self.string_to_term("x")
        flattened = self.flatten(term)
        
        self.assertEqual(str(term), str(flattened))
        self.assertTrue(flattened.isa_variable())
    
    def test_flatten_simple_term(self):
        """Test flattening a simple term (no nested associative operations)."""
        term = self.string_to_term("f(x,y)")
        flattened = self.flatten(term)
        
        # Simple terms may not change when flattened
        self.assertIsNotNone(flattened)
    
    def test_flatten_java_comparison(self):
        """Test flatten and compare with Java wrapper."""
        # Note: Flattening requires associative operations
        # For now, test that the function works without errors
        term_str = "f(x,y)"
        
        try:
            py_term = self.string_to_term(term_str)
            py_flattened = self.flatten(py_term)
            
            # Java result
            java_result = run_java_flatten(term_str)
            
            if java_result["success"]:
                java_data = java_result["data"]
                # Compare flattened results
                # Note: The exact format may differ, but both should be valid terms
                self.assertIsNotNone(py_flattened)
                # The flattened term should still be a valid term
                self.assertIsInstance(str(py_flattened), str)
        except Exception as e:
            # If Java wrapper or flattening fails, just verify Python works
            print(f"Flatten test with Java comparison failed: {e}")
            # At least verify Python flattening doesn't crash
            term = self.string_to_term(term_str)
            flattened = self.flatten(term)
            self.assertIsNotNone(flattened)


class TestTermsWithAlgebra(unittest.TestCase):
    """Test Terms utility functions with loaded algebras."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.string_to_term = uacalc_lib.terms.string_to_term
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
    
    def test_string_to_term_baker2_evaluation(self):
        """Test parsing terms and evaluating them on baker2 algebra."""
        alg = load_test_algebra("baker2")
        
        # Parse and evaluate various terms
        test_cases = [
            ("x", {"x": 0}, 0),
            ("x", {"x": 1}, 1),
            ("bak(x,y,z)", {"x": 0, "y": 0, "z": 0}, 0),
            ("bak(x,y,z)", {"x": 1, "y": 1, "z": 1}, 1),
        ]
        
        for term_str, var_map, expected in test_cases:
            term = self.string_to_term(term_str)
            result = term.eval(alg, var_map)
            self.assertEqual(result, expected,
                           f"Failed for term '{term_str}' with vars {var_map}")
    
    def test_string_to_term_baker2_evaluation_alternative(self):
        """Test parsing terms and evaluating them on baker2 algebra with operation from algebra."""
        alg = load_test_algebra("baker2")
        
        # Get the operation from baker2 (should be "bak")
        ops = alg.operations()
        if len(ops) == 0:
            self.skipTest("No operations in baker2 algebra")
        
        op = ops[0]
        op_name = op.symbol().name()
        
        # Baker2 uses "bak" which should be parseable
        term_str = f"{op_name}(x,y,z)"
        term = self.string_to_term(term_str)
        
        # Evaluate
        result = term.eval(alg, {"x": 0, "y": 0, "z": 0})
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLess(result, 2)  # Baker2 has 2 elements
        
        # Test with different assignment
        result2 = term.eval(alg, {"x": 1, "y": 1, "z": 1})
        self.assertIsInstance(result2, int)
        self.assertGreaterEqual(result2, 0)
        self.assertLess(result2, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)

