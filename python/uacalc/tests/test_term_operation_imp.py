#!/usr/bin/env python3
"""
Tests for TermOperationImp functionality using term interpretation.

This module tests term interpretation functionality by:
1. Creating terms in Python
2. Using interpretation() to get operations
3. Comparing results with Java TermOperationImp for validation
"""

import unittest
import os
from pathlib import Path

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


class TestTermInterpretationBasic(unittest.TestCase):
    """Test basic term interpretation functionality."""
    
    def setUp(self):
        """Set up test configuration."""
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
        self.OperationSymbol = uacalc_lib.alg.OperationSymbol
    
    def test_interpretation_simple_variable(self):
        """Test interpretation of a simple variable term."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        
        # Interpret variable x with variable list [x]
        op = x.interpretation(alg, ["x"], True)
        
        self.assertIsNotNone(op)
        self.assertEqual(op.arity(), 1)
        self.assertEqual(op.get_set_size(), 3)  # Cyclic3 has 3 elements
        
        # Test evaluation - variable x should project to first argument
        self.assertEqual(op.int_value_at([0]), 0)
        self.assertEqual(op.int_value_at([1]), 1)
        self.assertEqual(op.int_value_at([2]), 2)
    
    def test_interpretation_variable_with_multiple_vars(self):
        """Test interpretation of variable with multiple variables in list."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        
        # Interpret variable x with variable list [x, y, z]
        # x should project to the first argument
        op = x.interpretation(alg, ["x", "y", "z"], True)
        
        self.assertEqual(op.arity(), 3)
        self.assertEqual(op.get_set_size(), 3)
        
        # Test evaluation - x should return first argument
        self.assertEqual(op.int_value_at([0, 1, 2]), 0)
        self.assertEqual(op.int_value_at([1, 0, 2]), 1)
        self.assertEqual(op.int_value_at([2, 1, 0]), 2)
    
    def test_interpretation_get_table(self):
        """Test getting operation table from interpretation."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        op = x.interpretation(alg, ["x"], True)
        
        table = op.get_table()
        self.assertIsNotNone(table)
        self.assertEqual(len(table), 3)  # 3^1 = 3 entries
        # For variable x, table should be [0, 1, 2] (identity projection)
        self.assertEqual(table, [0, 1, 2])


class TestTermInterpretationNonVariableTerm(unittest.TestCase):
    """Test interpretation of NonVariableTerm (compound terms)."""
    
    def setUp(self):
        """Set up test configuration."""
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
        self.OperationSymbol = uacalc_lib.alg.OperationSymbol
    
    def test_interpretation_baker2_term(self):
        """Test interpretation of a NonVariableTerm in baker2."""
        alg = load_test_algebra("baker2")
        
        # Create term: bak(x, y, z)
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        bak = self.OperationSymbol("bak", 3)
        term = self.NonVariableTerm(bak, [x, y, z])
        
        # Interpret the term
        op = term.interpretation(alg, ["x", "y", "z"], True)
        
        self.assertIsNotNone(op)
        self.assertEqual(op.arity(), 3)
        self.assertEqual(op.get_set_size(), 2)  # Baker2 has 2 elements
        
        # Test evaluation matches term evaluation
        self.assertEqual(op.int_value_at([0, 0, 0]), term.eval(alg, {"x": 0, "y": 0, "z": 0}))
        self.assertEqual(op.int_value_at([0, 0, 1]), term.eval(alg, {"x": 0, "y": 0, "z": 1}))
        self.assertEqual(op.int_value_at([1, 1, 1]), term.eval(alg, {"x": 1, "y": 1, "z": 1}))
    
    def test_interpretation_get_table_baker2(self):
        """Test getting full operation table from interpretation."""
        alg = load_test_algebra("baker2")
        
        # Create term: bak(x, y, z)
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        bak = self.OperationSymbol("bak", 3)
        term = self.NonVariableTerm(bak, [x, y, z])
        
        # Interpret the term
        op = term.interpretation(alg, ["x", "y", "z"], True)
        
        # Get the table
        table = op.get_table()
        self.assertIsNotNone(table)
        self.assertEqual(len(table), 8)  # 2^3 = 8 entries
        
        # Verify all table entries match term evaluation
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
    
    def test_interpretation_nested_term(self):
        """Test interpretation of nested terms."""
        alg = load_test_algebra("baker2")
        
        # Create nested term: bak(bak(x, y, z), x, y)
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        bak = self.OperationSymbol("bak", 3)
        
        inner = self.NonVariableTerm(bak, [x, y, z])
        term = self.NonVariableTerm(bak, [inner, x, y])
        
        # Interpret the term
        op = term.interpretation(alg, ["x", "y", "z"], True)
        
        self.assertIsNotNone(op)
        self.assertEqual(op.arity(), 3)
        self.assertEqual(op.get_set_size(), 2)
        
        # Test evaluation
        result = op.int_value_at([0, 0, 0])
        expected = term.eval(alg, {"x": 0, "y": 0, "z": 0})
        self.assertEqual(result, expected)
    
    def test_interpretation_use_all_flag(self):
        """Test interpretation with use_all flag."""
        alg = load_test_algebra("baker2")
        
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        bak = self.OperationSymbol("bak", 3)
        z = self.VariableImp("z")
        
        # Create term: bak(x, y, z)
        term = self.NonVariableTerm(bak, [x, y, z])
        
        # With use_all=True, all variables in varlist are used
        op1 = term.interpretation(alg, ["x", "y", "z", "w"], True)
        self.assertEqual(op1.arity(), 4)  # Includes w even though term doesn't use it
        
        # With use_all=False, only variables in term are used
        op2 = term.interpretation(alg, ["x", "y", "z", "w"], False)
        self.assertEqual(op2.arity(), 3)  # Only x, y, z from the term


class TestTermInterpretationComparison(unittest.TestCase):
    """Test term interpretation by comparing with Java TermOperationImp."""
    
    def setUp(self):
        """Set up test configuration."""
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
        self.OperationSymbol = uacalc_lib.alg.OperationSymbol
    
    def test_baker2_full_table_comparison(self):
        """Compare full operation table between Python interpretation and term evaluation."""
        alg = load_test_algebra("baker2")
        
        # Create term: bak(x, y, z)
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        bak = self.OperationSymbol("bak", 3)
        term = self.NonVariableTerm(bak, [x, y, z])
        
        # Get interpretation
        op = term.interpretation(alg, ["x", "y", "z"], True)
        python_table = op.get_table()
        
        # Generate expected table using term evaluation
        expected_table = []
        set_size = 2
        arity = 3
        for i in range(set_size ** arity):
            # Convert i to arguments using horner encoding (least significant first)
            args = []
            temp = i
            for j in range(arity):
                args.append(temp % set_size)
                temp //= set_size
            
            # Create variable map
            var_map = {"x": args[0], "y": args[1], "z": args[2]}
            value = term.eval(alg, var_map)
            expected_table.append(value)
        
        # Compare tables
        self.assertEqual(len(python_table), len(expected_table))
        self.assertEqual(python_table, expected_table,
                        "Python interpretation table doesn't match term evaluation")


class TestTermOperationImpBasic(unittest.TestCase):
    """Test basic TermOperationImp functionality."""
    
    def setUp(self):
        """Set up test configuration."""
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
        self.OperationSymbol = uacalc_lib.alg.OperationSymbol
        self.TermOperationImp = uacalc_lib.terms.TermOperationImp
    
    def test_create_from_variable(self):
        """Test creating TermOperationImp from a variable."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        term_op = self.TermOperationImp(x, [x], alg)
        
        self.assertIsNotNone(term_op)
        self.assertEqual(term_op.arity(), 1)
        self.assertEqual(term_op.get_set_size(), 3)
        self.assertEqual(term_op.get_term(), "x")
        self.assertEqual(term_op.get_ordered_variables(), ["x"])
    
    def test_create_with_name(self):
        """Test creating TermOperationImp with a custom name."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        term_op = self.TermOperationImp(x, [x], alg, name="projection_x")
        
        self.assertIsNotNone(term_op)
        self.assertEqual(term_op.arity(), 1)
    
    def test_create_from_string_term(self):
        """Test creating TermOperationImp from a string term."""
        alg = load_test_algebra("lat2-01")
        
        # Create term using string_to_term
        term = uacalc_lib.terms.string_to_term("join(x, meet(y, z))")
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        z = self.VariableImp("z")
        
        term_op = self.TermOperationImp(term, [x, y, z], alg, name="meet")
        
        self.assertIsNotNone(term_op)
        self.assertEqual(term_op.arity(), 3)
        self.assertEqual(term_op.get_set_size(), 2)
        self.assertEqual(term_op.get_ordered_variables(), ["x", "y", "z"])
    
    def test_create_with_variable_strings(self):
        """Test creating TermOperationImp with variable names as strings."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        term_op = self.TermOperationImp(x, ["x"], alg)
        
        self.assertIsNotNone(term_op)
        self.assertEqual(term_op.arity(), 1)
    
    def test_evaluation(self):
        """Test evaluating TermOperationImp."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        term_op = self.TermOperationImp(x, [x], alg)
        
        # Variable x should project to first argument
        self.assertEqual(term_op.int_value_at([0]), 0)
        self.assertEqual(term_op.int_value_at([1]), 1)
        self.assertEqual(term_op.int_value_at([2]), 2)
    
    def test_get_table(self):
        """Test getting operation table from TermOperationImp."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        term_op = self.TermOperationImp(x, [x], alg)
        
        table = term_op.get_table()
        self.assertIsNotNone(table)
        self.assertEqual(len(table), 3)
        self.assertEqual(table, [0, 1, 2])


class TestTermOperationImpComplex(unittest.TestCase):
    """Test TermOperationImp with complex terms."""
    
    def setUp(self):
        """Set up test configuration."""
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.NonVariableTerm = uacalc_lib.terms.NonVariableTerm
        self.OperationSymbol = uacalc_lib.alg.OperationSymbol
        self.TermOperationImp = uacalc_lib.terms.TermOperationImp
    
    def test_arrow_operation(self):
        """Test creating arrow operation using TermOperationImp."""
        alg = load_test_algebra("ba2")
        
        # Create term: comp(meet(x, comp(y)))
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        comp_sym = self.OperationSymbol("comp", 1)
        meet_sym = self.OperationSymbol("meet", 2)
        
        comp_y = self.NonVariableTerm(comp_sym, [y])
        meet_term = self.NonVariableTerm(meet_sym, [x, comp_y])
        arrow_term = self.NonVariableTerm(comp_sym, [meet_term])
        
        arrow_op = self.TermOperationImp(arrow_term, [x, y], alg, name="arrow")
        
        self.assertIsNotNone(arrow_op)
        self.assertEqual(arrow_op.arity(), 2)
        self.assertEqual(arrow_op.get_set_size(), 2)


class TestTermOperationImpComparison(unittest.TestCase):
    """Test TermOperationImp compared to interpretation method."""
    
    def setUp(self):
        """Set up test configuration."""
        self.VariableImp = uacalc_lib.terms.VariableImp
        self.TermOperationImp = uacalc_lib.terms.TermOperationImp
    
    def test_same_as_interpretation(self):
        """Test that TermOperationImp produces same results as interpretation()."""
        alg = load_test_algebra("cyclic3")
        
        x = self.VariableImp("x")
        y = self.VariableImp("y")
        
        # Get operation via interpretation
        op1 = x.interpretation(alg, ["x", "y"], True)
        
        # Get operation via TermOperationImp
        term_op = self.TermOperationImp(x, [x, y], alg)
        
        # Both should have same arity and set size
        self.assertEqual(op1.arity(), term_op.arity())
        self.assertEqual(op1.get_set_size(), term_op.get_set_size())
        
        # Both should produce same results
        for i in range(3):
            for j in range(3):
                args = [i, j]
                val1 = op1.int_value_at(args)
                val2 = term_op.int_value_at(args)
                self.assertEqual(val1, val2, f"Values differ at args {args}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
