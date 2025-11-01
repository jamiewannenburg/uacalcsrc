"""Tests for Pool implementation."""

import unittest
import os
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_utils import run_java_wrapper


class TestPool(unittest.TestCase):
    """Test cases for Pool class."""

    def test_pool_initialization(self):
        """Test that pool can be initialized."""
        import uacalc_lib
        Pool = uacalc_lib.alg.Pool
        
        # Access the pool
        result = Pool.fj_pool()
        self.assertEqual(result, "initialized")

    def test_pool_is_initialized(self):
        """Test is_initialized method."""
        import uacalc_lib
        Pool = uacalc_lib.alg.Pool
        
        # Check if pool is initialized
        result = Pool.is_initialized()
        self.assertTrue(result)

    def test_pool_java_comparison(self):
        """Test pool initialization against Java implementation."""
        import uacalc_lib
        Pool = uacalc_lib.alg.Pool
        
        # Test with Java wrapper
        java_result = run_java_wrapper("get_pool", [])
        
        # Parse the nested JSON if needed
        if "data" in java_result and isinstance(java_result["data"], str):
            java_result["data"] = json.loads(java_result["data"])
        
        # Verify pool is initialized
        self.assertTrue(java_result.get("success", False))
        
        # Access pool from Python
        result = Pool.fj_pool()
        self.assertEqual(result, "initialized")

    def test_pool_is_initialized_java_comparison(self):
        """Test is_initialized against Java implementation."""
        import uacalc_lib
        Pool = uacalc_lib.alg.Pool
        
        # Test with Java wrapper
        java_result = run_java_wrapper("is_initialized", [])
        
        # Parse the nested JSON if needed
        if "data" in java_result and isinstance(java_result["data"], str):
            java_result["data"] = json.loads(java_result["data"])
        
        # Verify pool is initialized
        self.assertTrue(java_result.get("success", False))
        
        # Check from Python
        result = Pool.is_initialized()
        self.assertTrue(result)

    def test_pool_comprehensive(self):
        """Test comprehensive pool functionality against Java."""
        import uacalc_lib
        Pool = uacalc_lib.alg.Pool
        
        # Test with Java wrapper
        java_result = run_java_wrapper("test", [])
        
        # Parse the nested JSON if needed
        if "data" in java_result and isinstance(java_result["data"], str):
            java_result["data"] = json.loads(java_result["data"])
        
        # Verify Java results
        self.assertTrue(java_result.get("success", False))
        data = java_result.get("data", {})
        if isinstance(data, str):
            data = json.loads(data)
        
        # Verify pool is initialized
        self.assertTrue(data.get("initialized", False))
        
        # Verify same instance behavior
        # In Python, we can't directly check Arc pointer equality,
        # but we can verify the pool can be accessed multiple times
        result1 = Pool.fj_pool()
        result2 = Pool.fj_pool()
        self.assertEqual(result1, result2)
        self.assertEqual(result1, "initialized")


if __name__ == '__main__':
    unittest.main()

