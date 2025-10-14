#!/usr/bin/env python3
"""
Test module for lat (lattice and ordered sets) functionality.
Tests the py_maximals function against Java wrapper implementation.
"""

import json
import subprocess
import sys
import unittest
from typing import List, Dict, Any


def run_java_wrapper(command: str, args: List[str]) -> Dict[str, Any]:
    """
    Run the Java wrapper and return parsed JSON result.
    
    Args:
        command: The command to run
        args: List of arguments for the command
        
    Returns:
        Dictionary containing the parsed JSON response
    """
    cmd = [
        "java", "-cp", ".:org:java_wrapper/src",
        "java_wrapper.src.lat.OrderedSetsWrapper",
        command
    ] + args
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"Java wrapper failed: {result.stderr}")
            
        # Parse JSON output
        output = json.loads(result.stdout)
        
        # Parse the data field if it's a string (nested JSON)
        if "data" in output and isinstance(output["data"], str):
            output["data"] = json.loads(output["data"])
            
        return output
        
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse Java wrapper output: {e}\nOutput: {result.stdout}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Java wrapper timed out")
    except Exception as e:
        raise RuntimeError(f"Failed to run Java wrapper: {e}")


class TestLat(unittest.TestCase):
    """Test cases for lat module functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Import the Python module
        try:
            import uacalc_rust
            self.uacalc = uacalc_rust
        except ImportError as e:
            self.skipTest(f"Could not import uacalc_rust module: {e}")
    
    def test_maximals_divisibility_basic(self):
        """Test maximals with divisibility order - basic case."""
        elements = [2, 3, 6, 35, 175]
        order_type = "divisibility"
        
        # Get result from Python bindings
        py_result = self.uacalc.py_maximals(elements, order_type)
        
        # Get result from Java wrapper
        java_result = run_java_wrapper("maximals", [
            "--elements", ",".join(map(str, elements)),
            "--order", order_type
        ])
        
        # Compare results
        java_maximals = java_result["data"]["status"]
        self.assertEqual(sorted(py_result), sorted(java_maximals))
        
        # Expected result based on divisibility order
        expected = [2, 3, 35]  # 6 divides 2&3, 175 divides 35
        self.assertEqual(sorted(py_result), sorted(expected))
    
    def test_maximals_divisibility_java_example(self):
        """Test maximals with the exact Java main method example."""
        elements = [2, 3, 6, 35, 175]  # 35 * 5 = 175
        
        # Get result from Python bindings
        py_result = self.uacalc.py_maximals(elements, "divisibility")
        
        # Get result from Java wrapper test command
        java_result = run_java_wrapper("test", [])
        
        # Compare results
        java_maximals = java_result["data"]["status"]
        self.assertEqual(sorted(py_result), sorted(java_maximals))
    
    def test_maximals_natural_order(self):
        """Test maximals with natural order."""
        elements = [1, 2, 3, 4, 5]
        order_type = "natural"
        
        # Get result from Python bindings
        py_result = self.uacalc.py_maximals(elements, order_type)
        
        # Get result from Java wrapper
        java_result = run_java_wrapper("maximals", [
            "--elements", ",".join(map(str, elements)),
            "--order", order_type
        ])
        
        # Compare results
        java_maximals = java_result["data"]["status"]
        self.assertEqual(sorted(py_result), sorted(java_maximals))
        
        # With natural order, only the maximum element should be maximal
        expected = [5]
        self.assertEqual(py_result, expected)
    
    def test_maximals_empty_list(self):
        """Test maximals with empty list."""
        elements = []
        
        # Get result from Python bindings
        py_result = self.uacalc.py_maximals(elements, "divisibility")
        
        # Should return empty list
        self.assertEqual(py_result, [])
    
    def test_maximals_single_element(self):
        """Test maximals with single element."""
        elements = [42]
        
        # Get result from Python bindings
        py_result = self.uacalc.py_maximals(elements, "divisibility")
        
        # Single element should be maximal
        self.assertEqual(py_result, [42])
    
    def test_maximals_incomparable_elements(self):
        """Test maximals with mutually incomparable elements."""
        elements = [2, 3, 5, 7]  # All primes, none divides another
        
        # Get result from Python bindings
        py_result = self.uacalc.py_maximals(elements, "divisibility")
        
        # Get result from Java wrapper
        java_result = run_java_wrapper("maximals", [
            "--elements", ",".join(map(str, elements)),
            "--order", "divisibility"
        ])
        
        # Compare results
        java_maximals = java_result["data"]["status"]
        self.assertEqual(sorted(py_result), sorted(java_maximals))
        
        # All should be maximal since none divides another
        self.assertEqual(sorted(py_result), sorted(elements))
    
    def test_maximals_invalid_order(self):
        """Test maximals with invalid order type."""
        elements = [1, 2, 3]
        
        with self.assertRaises(Exception):
            self.uacalc.py_maximals(elements, "invalid_order")
    
    def test_maximals_chain(self):
        """Test maximals with chain of divisibility."""
        elements = [1, 2, 4, 8, 16]  # Chain: 1|2|4|8|16
        
        # Get result from Python bindings
        py_result = self.uacalc.py_maximals(elements, "divisibility")
        
        # Get result from Java wrapper
        java_result = run_java_wrapper("maximals", [
            "--elements", ",".join(map(str, elements)),
            "--order", "divisibility"
        ])
        
        # Compare results
        java_maximals = java_result["data"]["status"]
        self.assertEqual(sorted(py_result), sorted(java_maximals))
        
        # With divisibility order a <= b iff a % b == 0:
        # All elements are divisible by 1, so 1 is maximal
        # 2,4,8,16 are all <= 1, so 1 is the only maximal element
        expected = [1]
        self.assertEqual(py_result, expected)
    
    def test_maximals_complex_case(self):
        """Test maximals with more complex divisibility relationships."""
        elements = [2, 3, 4, 6, 12, 18, 36]  # Mixed relationships
        
        # Get result from Python bindings
        py_result = self.uacalc.py_maximals(elements, "divisibility")
        
        # Get result from Java wrapper
        java_result = run_java_wrapper("maximals", [
            "--elements", ",".join(map(str, elements)),
            "--order", "divisibility"
        ])
        
        # Compare results
        java_maximals = java_result["data"]["status"]
        self.assertEqual(sorted(py_result), sorted(java_maximals))
    
    def test_java_wrapper_help(self):
        """Test that Java wrapper help command works."""
        # Help command doesn't return JSON, just runs the Java wrapper directly
        cmd = [
            "java", "-cp", ".:org:java_wrapper/src",
            "java_wrapper.src.lat.OrderedSetsWrapper",
            "help"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            # Should succeed and print usage info
            self.assertEqual(result.returncode, 0)
            self.assertIn("Usage:", result.stdout)
            self.assertIn("OrderedSetsWrapper", result.stdout)
        except Exception as e:
            self.fail(f"Java wrapper help failed: {e}")


if __name__ == '__main__':
    unittest.main()