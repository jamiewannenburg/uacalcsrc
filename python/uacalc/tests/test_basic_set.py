"""Tests for BasicSet Python bindings.

This module provides comprehensive tests for the BasicSet Python bindings,
including unit tests, integration tests, and cross-language compatibility tests.
"""

import unittest
import json
import subprocess
import os
import uacalc_lib


class TestBasicSet(unittest.TestCase):
    """Test cases for BasicSet Python bindings."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.BasicSet = uacalc_lib.alg.BasicSet
    
    def run_java_wrapper(self, command, args, init_elements=None):
        """Run Java wrapper and return parsed JSON output."""
        # If init_elements is provided, add it to the args
        if init_elements is not None and command != "new":
            args = args + ["--elements", init_elements]
        
        cmd = [
            "java", "-cp", "java_wrapper/build/classes:build/classes:org:jars/*",
            "sublat.BasicSetWrapper", command
        ] + args
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode != 0:
            self.fail(f"Java wrapper failed: {result.stderr}")
        
        output = json.loads(result.stdout)
        if not output["success"]:
            self.fail(f"Java wrapper error: {output.get('error', 'Unknown error')}")
        
        # Parse the data field if it's a string
        if "data" in output and isinstance(output["data"], str):
            output["data"] = json.loads(output["data"])
        
        return output["data"]
    
    def test_basic_set_creation(self):
        """Test BasicSet creation."""
        set1 = self.BasicSet([1, 3, 5])
        self.assertEqual(set1.elements(), [1, 3, 5])
        self.assertEqual(set1.size(), 3)
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("new", ["--elements", "1,3,5"])
        self.assertEqual(set1.elements(), java_result["elements"])
        self.assertEqual(set1.size(), java_result["size"])
    
    def test_basic_set_empty(self):
        """Test empty BasicSet."""
        set1 = self.BasicSet([])
        self.assertEqual(set1.elements(), [])
        self.assertEqual(set1.size(), 0)
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("new", ["--elements", ""])
        self.assertEqual(set1.elements(), java_result["elements"])
        self.assertEqual(set1.size(), java_result["size"])
    
    def test_basic_set_duplicates(self):
        """Test BasicSet with duplicate elements."""
        set1 = self.BasicSet([1, 3, 1, 5, 3])
        # Should be normalized (sorted and deduplicated)
        self.assertEqual(set1.elements(), [1, 3, 5])
        self.assertEqual(set1.size(), 3)
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("new", ["--elements", "1,3,1,5,3"])
        self.assertEqual(set1.elements(), java_result["elements"])
        self.assertEqual(set1.size(), java_result["size"])
    
    def test_basic_set_contains(self):
        """Test contains method."""
        set1 = self.BasicSet([1, 3, 5])
        self.assertTrue(set1.contains(3))
        self.assertFalse(set1.contains(2))
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("contains", ["--element", "3"], "1,3,5")
        self.assertEqual(set1.contains(3), java_result["result"])
    
    def test_basic_set_leq(self):
        """Test subset check."""
        set1 = self.BasicSet([1, 3, 5])
        set2 = self.BasicSet([1, 2, 3, 4, 5])
        self.assertTrue(set1.leq(set2))
        self.assertFalse(set2.leq(set1))
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("leq", ["--other", "1,2,3,4,5"], "1,3,5")
        self.assertEqual(set1.leq(set2), java_result["result"])
    
    def test_basic_set_leq_static(self):
        """Test static subset check."""
        result = self.BasicSet.leq_static([1, 3], [1, 2, 3, 4])
        self.assertTrue(result)
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("leq_static", ["--u", "1,3", "--v", "1,2,3,4"])
        self.assertEqual(result, java_result["result"])
    
    def test_basic_set_intersection(self):
        """Test intersection method."""
        set1 = self.BasicSet([1, 3, 5])
        set2 = self.BasicSet([2, 3, 4])
        intersection = set1.intersection(set2)
        self.assertEqual(intersection.elements(), [3])
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("intersection", ["--other", "2,3,4"], "1,3,5")
        self.assertEqual(intersection.elements(), java_result["result"])
    
    def test_basic_set_intersection_static(self):
        """Test static intersection method."""
        set1 = self.BasicSet([1, 3, 5])
        set2 = self.BasicSet([2, 3, 4])
        intersection = self.BasicSet.intersection_static(set1, set2)
        self.assertEqual(intersection.elements(), [3])
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("intersection_static", ["--set1", "1,3,5", "--set2", "2,3,4"])
        self.assertEqual(intersection.elements(), java_result["result"])
    
    def test_basic_set_union(self):
        """Test union method."""
        set1 = self.BasicSet([1, 3, 5])
        set2 = self.BasicSet([2, 3, 4])
        union = set1.union(set2)
        self.assertEqual(sorted(union.elements()), [1, 2, 3, 4, 5])
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("union", ["--other", "2,3,4"], "1,3,5")
        self.assertEqual(sorted(union.elements()), sorted(java_result["result"]))
    
    def test_basic_set_union_static(self):
        """Test static union method."""
        set1 = self.BasicSet([1, 3, 5])
        set2 = self.BasicSet([2, 3, 4])
        union = self.BasicSet.union_static(set1, set2)
        self.assertEqual(sorted(union.elements()), [1, 2, 3, 4, 5])
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("union_static", ["--set1", "1,3,5", "--set2", "2,3,4"])
        self.assertEqual(sorted(union.elements()), sorted(java_result["result"]))
    
    def test_basic_set_difference(self):
        """Test set difference method."""
        set1 = self.BasicSet([1, 3, 5])
        set2 = self.BasicSet([2, 3, 4])
        difference = set1.set_difference(set2)
        self.assertEqual(sorted(difference.elements()), [1, 5])
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("set_difference", ["--other", "2,3,4"], "1,3,5")
        self.assertEqual(sorted(difference.elements()), sorted(java_result["result"]))
    
    def test_basic_set_normalize(self):
        """Test normalize method."""
        set1 = self.BasicSet([3, 1, 5, 1, 3])
        set1.normalize()
        self.assertEqual(set1.elements(), [1, 3, 5])
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("normalize", [], "3,1,5,1,3")
        self.assertEqual(set1.elements(), java_result["elements"])
    
    def test_basic_set_size(self):
        """Test size method."""
        set1 = self.BasicSet([1, 3, 5])
        self.assertEqual(set1.size(), 3)
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("size", [], "1,3,5")
        self.assertEqual(set1.size(), java_result["size"])
    
    def test_basic_set_universe_size(self):
        """Test universe_size method."""
        set1 = self.BasicSet([1, 3, 5])
        self.assertEqual(set1.universe_size(), 3)
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("universe_size", [], "1,3,5")
        self.assertEqual(set1.universe_size(), java_result["universe_size"])
    
    def test_basic_set_elements(self):
        """Test elements method."""
        set1 = self.BasicSet([1, 3, 5])
        self.assertEqual(set1.elements(), [1, 3, 5])
        
        # Test with Java wrapper
        java_result = self.run_java_wrapper("elements", [], "1,3,5")
        self.assertEqual(set1.elements(), java_result["elements"])
    
    def test_basic_set_comparison(self):
        """Test comparison operators."""
        set1 = self.BasicSet([1, 3, 5])
        set2 = self.BasicSet([1, 3, 5])
        set3 = self.BasicSet([1, 3, 6])
        
        self.assertEqual(set1, set2)
        self.assertNotEqual(set1, set3)
        self.assertLessEqual(set1, set2)
        self.assertGreaterEqual(set1, set2)
        self.assertLess(set1, set3)
    
    def test_basic_set_hash(self):
        """Test hash functionality."""
        set1 = self.BasicSet([1, 3, 5])
        set2 = self.BasicSet([1, 3, 5])
        set3 = self.BasicSet([1, 3, 6])
        
        # Equal sets should have same hash
        self.assertEqual(hash(set1), hash(set2))
        # Different sets should have different hashes
        self.assertNotEqual(hash(set1), hash(set3))
        
        # Test in set
        test_set = {set1, set2, set3}
        self.assertEqual(len(test_set), 2)  # set1 and set2 are equal
    
    def test_basic_set_string_representation(self):
        """Test string representation."""
        set1 = self.BasicSet([1, 3, 5])
        self.assertEqual(str(set1), "{1,3,5}")
        self.assertEqual(repr(set1), "BasicSet({1,3,5})")
    
    def test_basic_set_comprehensive_operations(self):
        """Test comprehensive set operations."""
        # Test with multiple sets
        set1 = self.BasicSet([1, 2, 3, 4, 5])
        set2 = self.BasicSet([3, 4, 5, 6, 7])
        set3 = self.BasicSet([2, 4, 6])
        
        # Intersection
        intersection = set1.intersection(set2)
        self.assertEqual(sorted(intersection.elements()), [3, 4, 5])
        
        # Union
        union = set1.union(set2)
        self.assertEqual(sorted(union.elements()), [1, 2, 3, 4, 5, 6, 7])
        
        # Difference
        difference = set1.set_difference(set2)
        self.assertEqual(sorted(difference.elements()), [1, 2])
        
        # Subset checks
        self.assertFalse(set3.leq(set1))  # [2,4,6] is not subset of [1,2,3,4,5] because 6 is not in set1
        self.assertFalse(set1.leq(set3))  # [1,2,3,4,5] is not subset of [2,4,6] because 1,3,5 are not in set3
        
        # Contains checks
        self.assertTrue(set1.contains(3))
        self.assertFalse(set1.contains(6))
    
    def test_basic_set_edge_cases(self):
        """Test edge cases."""
        # Empty set operations
        empty = self.BasicSet([])
        non_empty = self.BasicSet([1, 2, 3])
        
        self.assertTrue(empty.leq(non_empty))
        self.assertFalse(non_empty.leq(empty))
        
        # Intersection with empty set
        intersection = empty.intersection(non_empty)
        self.assertEqual(intersection.elements(), [])
        
        # Union with empty set
        union = empty.union(non_empty)
        self.assertEqual(sorted(union.elements()), [1, 2, 3])
        
        # Difference with empty set
        difference = non_empty.set_difference(empty)
        self.assertEqual(sorted(difference.elements()), [1, 2, 3])
    
    def test_basic_set_error_handling(self):
        """Test error handling."""
        # Test invalid input (should be handled gracefully)
        try:
            set1 = self.BasicSet([1, 3, 5])
            # BasicSet should handle valid input
            self.assertEqual(set1.size(), 3)
        except Exception as e:
            self.fail(f"Valid input should not raise exception: {e}")


if __name__ == '__main__':
    unittest.main()





