"""Test cases for lat.ordered_sets module."""

import json
import subprocess
import sys
import unittest
import uacalc_lib


def run_java_wrapper(command, args):
    """Run Java wrapper and return parsed JSON output."""
    cmd = [
        "java", "-cp", "java_wrapper/build/classes:build/classes:org:jars/*",
        "java_wrapper.src.lat.OrderedSetsWrapper", command
    ] + args
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)
        
        # Parse the data field again if it's a string
        if "data" in output and isinstance(output["data"], str):
            output["data"] = json.loads(output["data"])
            
        return output
    except subprocess.CalledProcessError as e:
        print(f"Java command failed: {e}", file=sys.stderr)
        print(f"stdout: {e.stdout}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        raise
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON output: {e}", file=sys.stderr)
        print(f"Raw output: {result.stdout}", file=sys.stderr)
        raise


class TestOrderedSets(unittest.TestCase):
    """Test ordered sets functionality."""

    def test_maximals_divisibility_basic(self):
        """Test maximals with divisibility order - basic case."""
        import uacalc_lib
        maximals_divisibility = uacalc_lib.lat.maximals_divisibility
        
        elements = [2, 3, 6, 35, 175]
        result = maximals_divisibility(elements)
        
        java_result = run_java_wrapper("maximals", 
            ["--elements", "2,3,6,35,175", "--order", "divisibility"])
        
        self.assertEqual(sorted(result), sorted(java_result["data"]["status"]))

    def test_maximals_divisibility_empty(self):
        """Test maximals with divisibility order - empty list."""
        import uacalc_lib
        maximals_divisibility = uacalc_lib.lat.maximals_divisibility
        
        elements = []
        result = maximals_divisibility(elements)
        
        java_result = run_java_wrapper("maximals", 
            ["--elements", "", "--order", "divisibility"])
        
        self.assertEqual(result, java_result["data"]["status"])

    def test_maximals_divisibility_single(self):
        """Test maximals with divisibility order - single element."""
        import uacalc_lib
        maximals_divisibility = uacalc_lib.lat.maximals_divisibility
        
        elements = [42]
        result = maximals_divisibility(elements)
        
        java_result = run_java_wrapper("maximals", 
            ["--elements", "42", "--order", "divisibility"])
        
        self.assertEqual(result, java_result["data"]["status"])

    def test_maximals_natural_order(self):
        """Test maximals with natural order."""
        import uacalc_lib
        maximals_natural_i32 = uacalc_lib.lat.maximals_natural_i32
        
        elements = [1, 2, 3, 4, 5]
        result = maximals_natural_i32(elements)
        
        java_result = run_java_wrapper("maximals", 
            ["--elements", "1,2,3,4,5", "--order", "natural"])
        
        self.assertEqual(result, java_result["data"]["status"])

    def test_maximals_primes(self):
        """Test maximals with prime numbers (all should be maximal)."""
        import uacalc_lib
        maximals_divisibility = uacalc_lib.lat.maximals_divisibility
        
        elements = [2, 3, 5, 7, 11]
        result = maximals_divisibility(elements)
        
        java_result = run_java_wrapper("maximals", 
            ["--elements", "2,3,5,7,11", "--order", "divisibility"])
        
        # All primes should be maximal, order doesn't matter
        self.assertEqual(sorted(result), sorted(java_result["data"]["status"]))
        self.assertEqual(len(result), 5)

    def test_main_method(self):
        """Test the main method functionality."""
        import uacalc_lib
        ordered_sets_main = uacalc_lib.lat.ordered_sets_main
        
        result = ordered_sets_main()
        
        java_result = run_java_wrapper("main", [])
        
        # Compare the message content
        self.assertEqual(result, java_result["data"]["message"])

    def test_maximals_complex_divisibility(self):
        """Test maximals with complex divisibility relationships."""
        import uacalc_lib
        maximals_divisibility = uacalc_lib.lat.maximals_divisibility
        
        elements = [1, 2, 4, 8, 3, 6, 12, 5, 10, 20]
        result = maximals_divisibility(elements)
        
        java_result = run_java_wrapper("maximals", 
            ["--elements", "1,2,4,8,3,6,12,5,10,20", "--order", "divisibility"])
        
        self.assertEqual(sorted(result), sorted(java_result["data"]["status"]))

    def test_maximals_prefix_order(self):
        """Test maximals with prefix order for strings."""
        import uacalc_lib
        maximals_prefix = uacalc_lib.lat.maximals_prefix
        
        elements = ["a", "ab", "abc", "b", "bc"]
        result = maximals_prefix(elements)
        
        # "abc" and "bc" should be maximal (no other string is a suffix of them)
        expected_maximal = ["abc", "bc"]
        self.assertEqual(sorted(result), sorted(expected_maximal))

    def test_maximals_natural_strings(self):
        """Test maximals with natural order for strings."""
        import uacalc_lib
        maximals_natural_string = uacalc_lib.lat.maximals_natural_string
        
        elements = ["apple", "banana", "cherry", "date"]
        result = maximals_natural_string(elements)
        
        # In lexicographic order, "date" should be the only maximal element
        expected_maximal = ["date"]
        self.assertEqual(result, expected_maximal)

    def test_order_classes(self):
        """Test that order classes can be instantiated."""
        import uacalc_lib
        
        # Test DivisibilityOrder
        div_order = uacalc_lib.lat.DivisibilityOrder()
        self.assertTrue(div_order.leq(2, 6))  # 2 divides 6
        self.assertFalse(div_order.leq(6, 2))  # 6 does not divide 2
        
        # Test PrefixOrder  
        prefix_order = uacalc_lib.lat.PrefixOrder()
        self.assertTrue(prefix_order.leq("ab", "abcd"))  # "ab" is prefix of "abcd"
        self.assertFalse(prefix_order.leq("abcd", "ab"))  # "abcd" is not prefix of "ab"
        
        # Test NaturalOrder
        natural_order = uacalc_lib.lat.NaturalOrder()
        self.assertTrue(natural_order.leq_i32(1, 2))  # 1 <= 2
        self.assertFalse(natural_order.leq_i32(2, 1))  # 2 > 1


if __name__ == '__main__':
    unittest.main()
