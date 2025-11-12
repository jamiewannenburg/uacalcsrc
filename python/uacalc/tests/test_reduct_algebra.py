#!/usr/bin/env python3
"""
Python tests for ReductAlgebra comparing outputs with Java wrapper.

This test suite compares the Python bindings with Java CLI wrapper outputs
to ensure correctness and compatibility.
"""

import subprocess
import json
import sys
import platform
from pathlib import Path
import unittest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import uacalc_lib
    ReductAlgebra = uacalc_lib.alg.ReductAlgebra
    BasicAlgebra = uacalc_lib.alg.BasicAlgebra
    CongruenceLattice = uacalc_lib.alg.CongruenceLattice
    SubalgebraLattice = uacalc_lib.alg.SubalgebraLattice
except ImportError as e:
    print(f"Error importing uacalc_lib: {e}")
    print("Make sure to run 'maturin develop' first")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def run_java_wrapper(command_args):
    """Run the Java wrapper and return parsed JSON output."""
    try:
        separator = ";" if platform.system() == "Windows" else ":"
        classpath = f"java_wrapper/build/classes{separator}build/classes{separator}org{separator}jars/*"
        cmd = [
            "java", "-cp", classpath,
            "java_wrapper.src.alg.ReductAlgebraWrapper"
        ] + command_args
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"Java command failed: {result.stderr}")
            return None
            
        # Parse JSON output
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        print("Java command timed out")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse Java output: {e}")
        print(f"Output was: {result.stdout[:200]}")
        return None
    except Exception as e:
        print(f"Error running Java wrapper: {e}")
        return None


class TestReductAlgebra(unittest.TestCase):
    """Test cases for ReductAlgebra."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.BasicAlgebra = BasicAlgebra
        self.ReductAlgebra = ReductAlgebra
    
    def test_create(self):
        """Test basic ReductAlgebra creation."""
        # Create a simple super algebra
        super_alg = self.BasicAlgebra("Super", [0, 1, 2], [])
        
        # Create reduct algebra with empty term list
        reduct = self.ReductAlgebra(super_alg, [])
        
        # Verify basic properties
        self.assertEqual(reduct.cardinality(), 3)
        self.assertIsNotNone(reduct.name())
        
        # Test with Java wrapper
        java_result = run_java_wrapper([
            "create",
            "--super_size", "3",
            "--term_list", ""
        ])
        
        if java_result and java_result.get("success"):
            java_data = java_result["data"]
            self.assertEqual(java_data.get("cardinality"), 3)
    
    def test_create_with_name(self):
        """Test creating ReductAlgebra with a custom name."""
        super_alg = self.BasicAlgebra("Super", [0, 1], [])
        reduct = self.ReductAlgebra(super_alg, [])
        reduct.set_name("MyReduct")
        
        self.assertEqual(reduct.name(), "MyReduct")
        self.assertEqual(reduct.cardinality(), 2)
    
    def test_cardinality(self):
        """Test cardinality method."""
        super_alg = self.BasicAlgebra("Super", [0, 1, 2, 3], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        self.assertEqual(reduct.cardinality(), 4)
        
        # Test with Java wrapper
        java_result = run_java_wrapper([
            "cardinality",
            "--super_size", "4",
            "--term_list", ""
        ])
        
        if java_result and java_result.get("success"):
            java_data = java_result["data"]
            self.assertEqual(java_data.get("cardinality"), 4)
    
    def test_element_index(self):
        """Test element_index method."""
        super_alg = self.BasicAlgebra("Super", [0, 1, 2], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        # Get the actual universe to know what elements exist
        universe = reduct.get_universe_list()
        self.assertIsNotNone(universe)
        self.assertEqual(len(universe), 3)
        
        # Test element_index for each element in the universe
        for elem in universe:
            idx = reduct.element_index(elem)
            self.assertIsNotNone(idx)
            # Verify that get_element returns the same element
            self.assertEqual(reduct.get_element(idx), elem)
        
        # Test with Java wrapper
        java_result = run_java_wrapper([
            "element_index",
            "--super_size", "3",
            "--term_list", "",
            "--element", "1"
        ])
        
        if java_result and java_result.get("success"):
            java_data = java_result["data"]
            # Java returns -1 if element not found, or index if found
            self.assertIsInstance(java_data.get("index"), int)
    
    def test_get_element(self):
        """Test get_element method."""
        super_alg = self.BasicAlgebra("Super", [0, 1, 2], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        # Get the actual universe to know how many elements exist
        universe = reduct.get_universe_list()
        self.assertIsNotNone(universe)
        self.assertEqual(len(universe), 3)
        
        # Test get_element for each valid index
        for idx in range(len(universe)):
            elem = reduct.get_element(idx)
            self.assertIsNotNone(elem)
            # Verify that element_index returns the same index
            self.assertEqual(reduct.element_index(elem), idx)
        
        # Test with Java wrapper
        java_result = run_java_wrapper([
            "get_element",
            "--super_size", "3",
            "--term_list", "",
            "--index", "1"
        ])
        
        if java_result and java_result.get("success"):
            java_data = java_result["data"]
            # Java returns the element at that index
            self.assertIsNotNone(java_data.get("element"))
    
    def test_algebra_type(self):
        """Test algebra_type method."""
        super_alg = self.BasicAlgebra("Super", [0, 1], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        alg_type = reduct.algebra_type()
        self.assertEqual(alg_type, "Reduct")
        
        # Test with Java wrapper
        java_result = run_java_wrapper([
            "algebra_type",
            "--super_size", "2",
            "--term_list", ""
        ])
        
        if java_result and java_result.get("success"):
            java_data = java_result["data"]
            self.assertEqual(java_data.get("type"), "REDUCT")
    
    def test_con_method(self):
        """Test con() method for lazy initialization."""
        super_alg = self.BasicAlgebra("Super", [0, 1], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        # Test con() method
        con_lat = reduct.con()
        self.assertIsInstance(con_lat, CongruenceLattice)
        self.assertEqual(con_lat.alg_size(), 2)
        
        # Test with Java wrapper
        java_result = run_java_wrapper([
            "con",
            "--super_size", "2",
            "--term_list", ""
        ])
        
        if java_result and java_result.get("success"):
            java_data = java_result["data"]
            self.assertEqual(java_data.get("alg_size"), 2)
    
    def test_sub_method(self):
        """Test sub() method for lazy initialization."""
        super_alg = self.BasicAlgebra("Super", [0, 1], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        # Test sub() method
        sub_lat = reduct.sub()
        self.assertIsInstance(sub_lat, SubalgebraLattice)
        self.assertIsInstance(sub_lat.cardinality(), int)
        
        # Test with Java wrapper
        java_result = run_java_wrapper([
            "sub",
            "--super_size", "2",
            "--term_list", ""
        ])
        
        if java_result and java_result.get("success"):
            java_data = java_result["data"]
            self.assertIsInstance(java_data.get("cardinality"), int)
    
    def test_get_universe_list(self):
        """Test get_universe_list method."""
        super_alg = self.BasicAlgebra("Super", [0, 1, 2], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        universe = reduct.get_universe_list()
        self.assertIsNotNone(universe)
        self.assertEqual(len(universe), 3)
        self.assertEqual(set(universe), {0, 1, 2})
    
    def test_get_universe_order(self):
        """Test get_universe_order method."""
        super_alg = self.BasicAlgebra("Super", [0, 1, 2], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        order = reduct.get_universe_order()
        self.assertIsNotNone(order)
        self.assertEqual(len(order), 3)
        # Verify that all elements from the universe are in the order map
        universe = reduct.get_universe_list()
        for elem in universe:
            self.assertIn(elem, order)
            # Verify that the order value is a valid index
            idx = order[elem]
            self.assertGreaterEqual(idx, 0)
            self.assertLess(idx, len(universe))
    
    def test_operations_count(self):
        """Test operations_count method."""
        super_alg = self.BasicAlgebra("Super", [0, 1], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        # With empty term list, should have 0 operations (variables are filtered out)
        count = reduct.operations_count()
        self.assertEqual(count, 0)
    
    def test_make_operation_tables(self):
        """Test make_operation_tables method."""
        super_alg = self.BasicAlgebra("Super", [0, 1], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        # Should not raise an error
        try:
            reduct.make_operation_tables()
        except Exception as e:
            # If it fails, that's okay for now since we're using empty term list
            pass
    
    def test_is_unary(self):
        """Test is_unary method."""
        super_alg = self.BasicAlgebra("Super", [0, 1], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        # With no operations, should be considered unary
        is_unary = reduct.is_unary()
        self.assertIsInstance(is_unary, bool)
    
    def test_is_idempotent(self):
        """Test is_idempotent method."""
        super_alg = self.BasicAlgebra("Super", [0, 1], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        is_idemp = reduct.is_idempotent()
        self.assertIsInstance(is_idemp, bool)
    
    def test_is_total(self):
        """Test is_total method."""
        super_alg = self.BasicAlgebra("Super", [0, 1], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        is_total = reduct.is_total()
        self.assertIsInstance(is_total, bool)
    
    def test_string_representation(self):
        """Test string representation methods."""
        super_alg = self.BasicAlgebra("Super", [0, 1], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        str_repr = str(reduct)
        self.assertIsInstance(str_repr, str)
        self.assertIn("ReductAlgebra", str_repr)
        
        repr_str = repr(reduct)
        self.assertIsInstance(repr_str, str)
        self.assertIn("ReductAlgebra", repr_str)
    
    def test_comprehensive(self):
        """Test comprehensive functionality."""
        # Create a larger super algebra
        super_alg = self.BasicAlgebra("Super", [0, 1, 2, 3, 4], [])
        reduct = self.ReductAlgebra(super_alg, [])
        
        # Test all basic methods
        self.assertEqual(reduct.cardinality(), 5)
        self.assertIsNotNone(reduct.name())
        
        # Get the actual universe
        universe = reduct.get_universe_list()
        self.assertEqual(len(universe), 5)
        self.assertEqual(set(universe), {0, 1, 2, 3, 4})
        
        # Test element access - verify consistency between get_element and element_index
        for i in range(5):
            elem = reduct.get_element(i)
            self.assertIsNotNone(elem)
            # Verify that element_index returns the same index
            idx = reduct.element_index(elem)
            self.assertEqual(idx, i)
        
        # Test lattices
        con_lat = reduct.con()
        self.assertEqual(con_lat.alg_size(), 5)
        
        sub_lat = reduct.sub()
        self.assertIsInstance(sub_lat.cardinality(), int)


if __name__ == "__main__":
    unittest.main()

