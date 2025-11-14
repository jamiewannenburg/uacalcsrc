"""
Test suite for CentralityData class.

Tests the Rust implementation of CentralityData against expected behavior.
"""

import unittest
import sys
import os
import json

# Add parent directory to path to import uacalc_lib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    import uacalc_lib
    UACALC_AVAILABLE = True
except ImportError:
    UACALC_AVAILABLE = False

# Import test utilities
try:
    from test_utils import run_java_wrapper, TestConfig
    JAVA_COMPARISON_AVAILABLE = True
except ImportError:
    JAVA_COMPARISON_AVAILABLE = False


@unittest.skipUnless(UACALC_AVAILABLE, "uacalc_lib not available")
class TestCentralityData(unittest.TestCase):
    """Test CentralityData implementation."""
    
    def test_creation(self):
        """Test creating a CentralityData object."""
        # Import classes through uacalc_lib module
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create binary relations
        left = BasicBinaryRelation(3)
        left.add(0, 1)
        
        right = BasicBinaryRelation(3)
        right.add(1, 2)
        
        # Create partition
        delta = Partition.zero(3)
        
        # Create CentralityData
        data = CentralityData(left, right, delta)
        
        self.assertIsNotNone(data)
        self.assertEqual(data.universe_size(), 3)
        self.assertEqual(data.delta_blocks(), 3)
    
    def test_getters(self):
        """Test getter methods."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        left = BasicBinaryRelation(3)
        right = BasicBinaryRelation(3)
        delta = Partition.zero(3)
        
        data = CentralityData(left, right, delta)
        
        self.assertEqual(data.universe_size(), 3)
        self.assertEqual(data.delta_blocks(), 3)
    
    def test_validation(self):
        """Test validation of universe sizes."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create relations with mismatched sizes
        left = BasicBinaryRelation(3)
        right = BasicBinaryRelation(4)
        delta = Partition.zero(3)
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            data = CentralityData(left, right, delta)
    
    def test_comparison(self):
        """Test comparison methods."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        left1 = BasicBinaryRelation(3)
        right1 = BasicBinaryRelation(3)
        delta1 = Partition.zero(3)
        data1 = CentralityData(left1, right1, delta1)
        
        left2 = BasicBinaryRelation(3)
        right2 = BasicBinaryRelation(3)
        delta2 = Partition.one(3)
        data2 = CentralityData(left2, right2, delta2)
        
        # Test compare_to
        cmp = data1.compare_to(data2)
        self.assertIsInstance(cmp, int)
        
        # Test comparison operators
        self.assertNotEqual(data1, data2)
    
    def test_string_representation(self):
        """Test string representation."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        left = BasicBinaryRelation(2)
        left.add(0, 1)
        right = BasicBinaryRelation(2)
        right.add(1, 0)
        delta = Partition.zero(2)
        
        data = CentralityData(left, right, delta)
        
        # Test __str__
        str_rep = str(data)
        self.assertIsInstance(str_rep, str)
        self.assertIn("left:", str_rep)
        self.assertIn("right:", str_rep)
        self.assertIn("delta:", str_rep)
        
        # Test __repr__
        repr_rep = repr(data)
        self.assertIsInstance(repr_rep, str)
        self.assertIn("CentralityData", repr_rep)


@unittest.skipUnless(UACALC_AVAILABLE and JAVA_COMPARISON_AVAILABLE, "uacalc_lib or Java comparison not available")
class TestCentralityDataJavaComparison(unittest.TestCase):
    """Test CentralityData implementation against Java wrapper."""
    
    def test_new_command_comparison(self):
        """Test new command comparison with Java."""
        # Import classes through uacalc_lib module
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create Python implementation
        left = BasicBinaryRelation(3)
        left.add(0, 1)
        right = BasicBinaryRelation(3)
        right.add(1, 2)
        delta = Partition.zero(3)
        data = CentralityData(left, right, delta)
        
        # Run Java wrapper
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.conlat.CentralityDataWrapper",
            ["new", "--size", "3"]
        )
        
        # Compare results
        self.assertTrue(java_result.is_success(), f"Java wrapper failed: {java_result.stderr}")
        java_data = java_result.parse_json()["data"]
        
        self.assertEqual(data.universe_size(), java_data["left_universe_size"])
        self.assertEqual(data.universe_size(), java_data["right_universe_size"])
        self.assertEqual(data.universe_size(), java_data["delta_universe_size"])
        self.assertEqual(data.delta_blocks(), java_data["delta_blocks"])
    
    def test_get_left_command_comparison(self):
        """Test get_left command comparison with Java."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create Python implementation
        left = BasicBinaryRelation(3)
        left.add(0, 1)
        right = BasicBinaryRelation(3)
        delta = Partition.zero(3)
        data = CentralityData(left, right, delta)
        
        # Run Java wrapper
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.conlat.CentralityDataWrapper",
            ["get_left", "--size", "3"]
        )
        
        # Compare results
        self.assertTrue(java_result.is_success(), f"Java wrapper failed: {java_result.stderr}")
        java_data = java_result.parse_json()["data"]
        
        self.assertEqual(data.universe_size(), java_data["universe_size"])
        self.assertTrue(data.left().is_related(0, 1))
        self.assertEqual(java_data["is_related_0_1"], True)
    
    def test_get_right_command_comparison(self):
        """Test get_right command comparison with Java."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create Python implementation
        left = BasicBinaryRelation(3)
        right = BasicBinaryRelation(3)
        right.add(1, 2)
        delta = Partition.zero(3)
        data = CentralityData(left, right, delta)
        
        # Run Java wrapper
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.conlat.CentralityDataWrapper",
            ["get_right", "--size", "3"]
        )
        
        # Compare results
        self.assertTrue(java_result.is_success(), f"Java wrapper failed: {java_result.stderr}")
        java_data = java_result.parse_json()["data"]
        
        self.assertEqual(data.universe_size(), java_data["universe_size"])
        self.assertTrue(data.right().is_related(1, 2))
        self.assertEqual(java_data["is_related_1_2"], True)
    
    def test_get_delta_command_comparison(self):
        """Test get_delta command comparison with Java."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create Python implementation
        left = BasicBinaryRelation(3)
        right = BasicBinaryRelation(3)
        delta = Partition.zero(3)
        data = CentralityData(left, right, delta)
        
        # Run Java wrapper
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.conlat.CentralityDataWrapper",
            ["get_delta", "--size", "3"]
        )
        
        # Compare results
        self.assertTrue(java_result.is_success(), f"Java wrapper failed: {java_result.stderr}")
        java_data = java_result.parse_json()["data"]
        
        self.assertEqual(data.universe_size(), java_data["universe_size"])
        self.assertEqual(data.delta_blocks(), java_data["num_blocks"])
    
    def test_get_delta_one_command_comparison(self):
        """Test get_delta command with is_one=true comparison with Java."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create Python implementation
        left = BasicBinaryRelation(3)
        right = BasicBinaryRelation(3)
        delta = Partition.one(3)  # All elements in one block
        data = CentralityData(left, right, delta)
        
        # Run Java wrapper
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.conlat.CentralityDataWrapper",
            ["get_delta", "--size", "3", "--is_one", "true"]
        )
        
        # Compare results
        self.assertTrue(java_result.is_success(), f"Java wrapper failed: {java_result.stderr}")
        java_data = java_result.parse_json()["data"]
        
        self.assertEqual(data.universe_size(), java_data["universe_size"])
        self.assertEqual(data.delta_blocks(), java_data["num_blocks"])
        self.assertEqual(data.delta_blocks(), 1)  # Should be 1 block for one partition
    
    def test_compare_to_command_comparison(self):
        """Test compare_to command comparison with Java."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create Python implementation
        left1 = BasicBinaryRelation(3)
        right1 = BasicBinaryRelation(3)
        delta1 = Partition.zero(3)
        data1 = CentralityData(left1, right1, delta1)
        
        left2 = BasicBinaryRelation(3)
        right2 = BasicBinaryRelation(3)
        delta2 = Partition.one(3)
        data2 = CentralityData(left2, right2, delta2)
        
        python_cmp = data1.compare_to(data2)
        
        # Run Java wrapper
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.conlat.CentralityDataWrapper",
            ["compare_to", "--size", "3"]
        )
        
        # Compare results
        self.assertTrue(java_result.is_success(), f"Java wrapper failed: {java_result.stderr}")
        java_data = java_result.parse_json()["data"]
        
        self.assertEqual(python_cmp, java_data["comparison"])
        self.assertEqual(data1.delta_blocks(), java_data["delta1_blocks"])
        self.assertEqual(data2.delta_blocks(), java_data["delta2_blocks"])
    
    def test_to_string_command_comparison(self):
        """Test to_string command comparison with Java."""
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        Partition = uacalc_lib.alg.Partition
        CentralityData = uacalc_lib.alg.CentralityData
        
        # Create Python implementation
        left = BasicBinaryRelation(2)
        left.add(0, 1)
        right = BasicBinaryRelation(2)
        right.add(1, 0)
        delta = Partition.zero(2)
        data = CentralityData(left, right, delta)
        
        python_str = str(data)
        
        # Run Java wrapper
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.conlat.CentralityDataWrapper",
            ["to_string", "--size", "2"]
        )
        
        # Compare results
        self.assertTrue(java_result.is_success(), f"Java wrapper failed: {java_result.stderr}")
        java_data = java_result.parse_json()["data"]
        
        # Check that both contain expected substrings
        self.assertIn("left:", python_str)
        self.assertIn("right:", python_str)
        self.assertIn("delta:", python_str)
        
        self.assertEqual(java_data["contains_left"], True)
        self.assertEqual(java_data["contains_right"], True)
        self.assertEqual(java_data["contains_delta"], True)
    
    def test_test_command_comparison(self):
        """Test test command comparison with Java."""
        # Run Java wrapper test command
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.conlat.CentralityDataWrapper",
            ["test"]
        )
        
        # Verify Java wrapper runs successfully
        self.assertTrue(java_result.is_success(), f"Java wrapper failed: {java_result.stderr}")
        java_data = java_result.parse_json()["data"]
        
        # Check that test results are present
        self.assertIn("results", java_data)
        self.assertIsInstance(java_data["results"], list)
        self.assertGreater(len(java_data["results"]), 0)
        
        # Check that all tests passed
        for result in java_data["results"]:
            self.assertTrue(result.startswith("PASS:"), f"Test failed: {result}")


if __name__ == '__main__':
    unittest.main()
