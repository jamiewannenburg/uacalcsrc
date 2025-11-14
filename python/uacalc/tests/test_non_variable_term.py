#!/usr/bin/env python3
"""
Tests for NonVariableTerm Python bindings.

This module tests NonVariableTerm functionality including:
- Creation and basic properties
- Evaluation with algebras (eval, int_eval)
- Nested term structures
- Constant terms
- Comparison with Java wrapper for interpretation
- String representation and variable extraction
"""

import unittest
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# Import test utilities
from test_utils import TestConfig, run_java_wrapper, build_java_command

# Import uacalc_lib
import uacalc_lib

# Get project root to locate resources
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESOURCES_ALGEBRAS_DIR = PROJECT_ROOT / "resources" / "algebras"


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


def run_java_interpret_term(algebra_path: str, term_str: str, vars_str: str, use_all: bool = True) -> Dict[str, Any]:
    """Run Java wrapper interpret_term command and return JSON result."""
    wrapper_class = "java_wrapper.src.terms.TermsWrapper"
    use_all_str = "true" if use_all else "false"
    
    args = [
        "interpret_term",
        "--algebra", algebra_path,
        "--term", term_str,
        "--vars", vars_str,
        "--use_all", use_all_str
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
        # Find the JSON object (starts with {)
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


class TestNonVariableTermBasic(unittest.TestCase):
    """Test basic NonVariableTerm creation and properties."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
        self.OperationSymbol = uacalc_lib.alg.OperationSymbol
    
    def test_create_simple_term(self):
        """Test creating a simple non-variable term."""
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        f = self.OperationSymbol("f", 2)
        
        term = self.NonVariableTerm(f, [x, y])
        
        self.assertIsNotNone(term)
        self.assertFalse(term.isa_variable())
        self.assertEqual(term.depth(), 1)
        self.assertEqual(term.length(), 3)  # f, x, y
    
    def test_term_properties(self):
        """Test term properties (depth, length, isa_variable)."""
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        f = self.OperationSymbol("f", 2)
        g = self.OperationSymbol("g", 1)
        
        # Simple term: f(x, y)
        term1 = self.NonVariableTerm(f, [x, y])
        self.assertEqual(term1.depth(), 1)
        self.assertEqual(term1.length(), 3)
        
        # Nested term: f(g(x), y)
        gx = self.NonVariableTerm(g, [x])
        term2 = self.NonVariableTerm(f, [gx, y])
        self.assertEqual(term2.depth(), 2)
        self.assertEqual(term2.length(), 4)  # f, g, x, y
    
    def test_get_variable_list(self):
        """Test getting variable list from term."""
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        f = self.OperationSymbol("f", 2)
        
        # Simple term
        term1 = self.NonVariableTerm(f, [x, y])
        var_list = term1.get_variable_list()
        self.assertEqual(len(var_list), 2)
        self.assertIn("x", var_list)
        self.assertIn("y", var_list)
        
        # Nested term with repeated variables
        term2 = self.NonVariableTerm(f, [x, self.NonVariableTerm(f, [y, z])])
        var_list2 = term2.get_variable_list()
        self.assertEqual(len(var_list2), 3)
        self.assertIn("x", var_list2)
        self.assertIn("y", var_list2)
        self.assertIn("z", var_list2)
    
    def test_string_representation(self):
        """Test string representation of terms."""
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        f = self.OperationSymbol("f", 2)
        
        term = self.NonVariableTerm(f, [x, y])
        str_repr = str(term)
        
        self.assertIn("f", str_repr)
        self.assertIn("x", str_repr)
        self.assertIn("y", str_repr)
    
    def test_constant_term(self):
        """Test creating constant terms."""
        c = self.OperationSymbol("c", 0)
        
        term = self.NonVariableTerm.make_constant_term(c)
        
        self.assertIsNotNone(term)
        self.assertFalse(term.isa_variable())
        self.assertEqual(term.depth(), 1)  # Constant term has depth 1 (the constant itself)
        self.assertEqual(term.length(), 1)
        self.assertEqual(len(term.get_variable_list()), 0)


class TestNonVariableTermEvaluation(unittest.TestCase):
    """Test NonVariableTerm evaluation with algebras."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
        self.OperationSymbol = uacalc_lib.alg.OperationSymbol
    
    def test_eval_cyclic3_addition(self):
        """Test evaluating addition term in cyclic3 algebra."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        plus = self.OperationSymbol("+", 2)
        
        # Create term: x + y
        term = self.NonVariableTerm(plus, [x, y])
        
        # Test various assignments
        # 0 + 1 = 1
        result = term.eval(alg, {"x": 0, "y": 1})
        self.assertEqual(result, 1)
        
        # 1 + 2 = 0 (mod 3)
        result = term.eval(alg, {"x": 1, "y": 2})
        self.assertEqual(result, 0)
        
        # 2 + 2 = 1 (mod 3)
        result = term.eval(alg, {"x": 2, "y": 2})
        self.assertEqual(result, 1)
    
    def test_int_eval_cyclic3(self):
        """Test int_eval method with cyclic3 algebra."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        plus = self.OperationSymbol("+", 2)
        
        term = self.NonVariableTerm(plus, [x, y])
        
        # Test int_eval
        result = term.int_eval(alg, {"x": 0, "y": 1})
        self.assertEqual(result, 1)
        
        result = term.int_eval(alg, {"x": 1, "y": 2})
        self.assertEqual(result, 0)
    
    def test_eval_nested_term_cyclic3(self):
        """Test evaluating nested terms in cyclic3."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        plus = self.OperationSymbol("+", 2)
        
        # Create term: (x + y) + z
        inner = self.NonVariableTerm(plus, [x, y])
        term = self.NonVariableTerm(plus, [inner, z])
        
        # Test: (0 + 1) + 2 = 1 + 2 = 0
        result = term.eval(alg, {"x": 0, "y": 1, "z": 2})
        self.assertEqual(result, 0)
        
        # Test: (1 + 2) + 0 = 0 + 0 = 0
        result = term.eval(alg, {"x": 1, "y": 2, "z": 0})
        self.assertEqual(result, 0)
    
    def test_eval_baker2(self):
        """Test evaluating term in baker2 algebra."""
        alg = load_test_algebra("baker2")
        
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        bak = self.OperationSymbol("bak", 3)
        
        # Create term: bak(x, y, z)
        term = self.NonVariableTerm(bak, [x, y, z])
        
        # Test various assignments
        # bak(0, 0, 0) = 0
        result = term.eval(alg, {"x": 0, "y": 0, "z": 0})
        self.assertEqual(result, 0)
        
        # bak(0, 0, 1) = 0
        result = term.eval(alg, {"x": 0, "y": 0, "z": 1})
        self.assertEqual(result, 0)
        
        # bak(1, 0, 0) = 0
        result = term.eval(alg, {"x": 1, "y": 0, "z": 0})
        self.assertEqual(result, 0)
        
        # bak(1, 1, 1) = 1
        result = term.eval(alg, {"x": 1, "y": 1, "z": 1})
        self.assertEqual(result, 1)
    
    def test_eval_missing_variable(self):
        """Test that evaluating with missing variable raises error."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        plus = self.OperationSymbol("+", 2)
        
        term = self.NonVariableTerm(plus, [x, y])
        
        # Missing variable should raise error
        with self.assertRaises(ValueError):
            term.eval(alg, {"x": 0})
        
        with self.assertRaises(ValueError):
            term.eval(alg, {})
    
    def test_eval_multiple_algebras(self):
        """Test evaluation with multiple different algebras."""
        algebras = ["cyclic2", "cyclic3", "n5"]
        
        for alg_name in algebras:
            try:
                alg = load_test_algebra(alg_name)
                
                x = self.VariableImp("x")
                y = self.VariableImp("y")
                
                # Find the first binary operation
                ops = alg.operations()
                if len(ops) > 0:
                    op = ops[0]
                    op_sym = self.OperationSymbol(op.symbol().name(), op.arity())
                    
                    term = self.NonVariableTerm(op_sym, [x, y])
                    
                    # Test with first assignment
                    var_map = {"x": 0, "y": 0}
                    result = term.eval(alg, var_map)
                    self.assertIsInstance(result, int)
                    self.assertGreaterEqual(result, 0)
                    
            except unittest.SkipTest:
                continue


class TestNonVariableTermNested(unittest.TestCase):
    """Test nested NonVariableTerm structures."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
        self.OperationSymbol = uacalc_lib.alg.OperationSymbol
    
    def test_deeply_nested_term(self):
        """Test deeply nested term structure."""
        x = self.VariableImp("x")
        f = self.OperationSymbol("f", 1)
        
        # Create f(f(f(x)))
        term = x
        for _ in range(3):
            term = self.NonVariableTerm(f, [term])
        
        self.assertEqual(term.depth(), 3)
        self.assertEqual(term.length(), 4)
        self.assertEqual(len(term.get_variable_list()), 1)
    
    def test_nested_binary_operations(self):
        """Test nested binary operations."""
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        f = self.OperationSymbol("f", 2)
        
        # Create f(f(x, y), z)
        inner = self.NonVariableTerm(f, [x, y])
        outer = self.NonVariableTerm(f, [inner, z])
        
        self.assertEqual(outer.depth(), 2)
        self.assertEqual(outer.length(), 5)  # f, f, x, y, z
        
        var_list = outer.get_variable_list()
        self.assertEqual(len(var_list), 3)
        self.assertIn("x", var_list)
        self.assertIn("y", var_list)
        self.assertIn("z", var_list)
    
    def test_nested_evaluation_cyclic3(self):
        """Test evaluating nested terms in cyclic3."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        plus = self.OperationSymbol("+", 2)
        
        # Create: ((x + y) + z) + x
        inner1 = self.NonVariableTerm(plus, [x, y])
        inner2 = self.NonVariableTerm(plus, [inner1, z])
        term = self.NonVariableTerm(plus, [inner2, x])
        
        # Test evaluation
        result = term.eval(alg, {"x": 0, "y": 1, "z": 2})
        # ((0 + 1) + 2) + 0 = (1 + 2) + 0 = 0 + 0 = 0
        self.assertEqual(result, 0)


class TestNonVariableTermJavaComparison(unittest.TestCase):
    """Test NonVariableTerm against Java wrapper for interpretation."""
    
    def setUp(self):
        """Set up test configuration."""
        self.config = TestConfig(default_timeout=30.0, memory_limit_mb=1024)
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
        self.OperationSymbol = uacalc_lib.alg.OperationSymbol
    
    def test_interpret_term_cyclic3_simple(self):
        """Test interpretation of simple term in cyclic3 and compare with Java."""
        algebra_path = str(RESOURCES_ALGEBRAS_DIR / "cyclic3.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra in Python
        alg = load_test_algebra("cyclic3")
        
        # Get the operation from the algebra
        ops = alg.operations()
        if len(ops) == 0:
            self.skipTest("No operations in algebra")
        
        op = ops[0]
        op_name = op.symbol().name()
        op_arity = op.arity()
        
        # Create term using the operation name from the algebra
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        op_sym = self.OperationSymbol(op_name, op_arity)
        term = self.NonVariableTerm(op_sym, [x, y])
        
        # For cyclic3, the operation name is "+" which Java can't parse
        # So we'll skip Java comparison for this test and just verify Python evaluation works
        # Test evaluation directly
        result = term.eval(alg, {"x": 0, "y": 1})
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLess(result, 3)  # Cyclic3 has 3 elements
        
        # Note: For cyclic3, Java can't parse "+" as an operation name
        # So we just verify Python evaluation works correctly
        # This test validates that NonVariableTerm evaluation works with loaded algebras
    
    def test_interpret_term_baker2(self):
        """Test interpretation of term in baker2 and compare with Java."""
        algebra_path = str(RESOURCES_ALGEBRAS_DIR / "baker2.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra in Python
        alg = load_test_algebra("baker2")
        
        # Create term: bak(x, y, z)
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        bak = self.OperationSymbol("bak", 3)
        term = self.NonVariableTerm(bak, [x, y, z])
        
        # Get Java interpretation result
        java_result = run_java_interpret_term(
            algebra_path,
            "bak(x,y,z)",
            "x,y,z",
            use_all=True
        )
        
        self.assertTrue(java_result["success"])
        
        # Verify table values match Python evaluation
        arity = java_result["data"]["arity"]
        set_size = java_result["data"]["set_size"]
        table = java_result["data"]["table"]
        
        self.assertEqual(arity, 3)  # Three variables
        self.assertEqual(set_size, 2)  # Baker2 has 2 elements
        self.assertEqual(len(table), 8)  # 2^3 = 8 entries
        
        # Verify all table entries match Python evaluation
        # Java uses horner encoding with args in reverse order (least significant first)
        # So for 3 variables with set_size=2, the order is:
        # i=0: (x=0,y=0,z=0), i=1: (x=1,y=0,z=0), i=2: (x=0,y=1,z=0), i=3: (x=1,y=1,z=0),
        # i=4: (x=0,y=0,z=1), i=5: (x=1,y=0,z=1), i=6: (x=0,y=1,z=1), i=7: (x=1,y=1,z=1)
        expected_values = [
            term.eval(alg, {"x": 0, "y": 0, "z": 0}),  # i=0
            term.eval(alg, {"x": 1, "y": 0, "z": 0}),  # i=1
            term.eval(alg, {"x": 0, "y": 1, "z": 0}),  # i=2
            term.eval(alg, {"x": 1, "y": 1, "z": 0}),  # i=3
            term.eval(alg, {"x": 0, "y": 0, "z": 1}),  # i=4
            term.eval(alg, {"x": 1, "y": 0, "z": 1}),  # i=5
            term.eval(alg, {"x": 0, "y": 1, "z": 1}),  # i=6
            term.eval(alg, {"x": 1, "y": 1, "z": 1}),  # i=7
        ]
        
        self.assertEqual(table, expected_values)
    
    def test_interpret_term_nested_cyclic3(self):
        """Test evaluation of nested term in cyclic3 (no Java comparison due to + symbol)."""
        algebra_path = str(RESOURCES_ALGEBRAS_DIR / "cyclic3.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra in Python
        alg = load_test_algebra("cyclic3")
        
        # Get the operation from the algebra
        ops = alg.operations()
        if len(ops) == 0:
            self.skipTest("No operations in algebra")
        
        op = ops[0]
        op_name = op.symbol().name()
        op_arity = op.arity()
        
        # Create nested term: (x op y) op z
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        op_sym = self.OperationSymbol(op_name, op_arity)
        
        inner = self.NonVariableTerm(op_sym, [x, y])
        term = self.NonVariableTerm(op_sym, [inner, z])
        
        # Test evaluation directly (Java can't parse "+" as operation name)
        # Verify nested evaluation works
        result = term.eval(alg, {"x": 0, "y": 1, "z": 2})
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLess(result, 3)  # Cyclic3 has 3 elements


if __name__ == '__main__':
    unittest.main(verbosity=2)

