"""Tests for ArrayIncrementor Python bindings."""

import pytest
import uacalc_lib
from pathlib import Path
import json
import platform
import subprocess

# Get the project root directory
project_root = Path(__file__).parent.parent.parent.parent

def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    from test_utils import build_java_command
    
    wrapper_class = "java_wrapper.src.util.ArrayIncrementorWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")
        
        # Parse JSON output
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Java wrapper output: {e}")

class TestSimpleArrayIncrementor:
    """Test SimpleArrayIncrementor Python bindings."""
    
    def test_new(self):
        """Test creating a new SimpleArrayIncrementor."""
        # Import through uacalc_lib module (direct imports don't work)
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        incrementor = SimpleArrayIncrementor([0, 1, 2])
        assert incrementor.get_array() == [0, 1, 2]
    
    def test_new_with_max_values(self):
        """Test creating a SimpleArrayIncrementor with custom max values."""
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        incrementor = SimpleArrayIncrementor.new_with_max_values([0, 0, 0], [1, 2, 1])
        assert incrementor.get_array() == [0, 0, 0]
    
    def test_new_with_max_values_invalid_length(self):
        """Test creating a SimpleArrayIncrementor with invalid max values length."""
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        with pytest.raises(Exception):  # PyValueError
            SimpleArrayIncrementor.new_with_max_values([0, 1], [2])
    
    def test_new_with_max_values_invalid_value(self):
        """Test creating a SimpleArrayIncrementor with invalid array values."""
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        with pytest.raises(Exception):  # PyValueError
            SimpleArrayIncrementor.new_with_max_values([0, 3], [2, 2])
    
    def test_increment_basic(self):
        """Test basic incrementing functionality."""
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        incrementor = SimpleArrayIncrementor([0, 0, 0])
        
        # First call should return true (initial state)
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0, 0, 0]
        
        # Second call should increment to [0, 0, 1]
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0, 0, 1]
        
        # Continue incrementing
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0, 0, 2]
        
        # Should wrap around to [0, 1, 0]
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0, 1, 0]
    
    def test_increment_with_custom_max(self):
        """Test incrementing with custom maximum values."""
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        incrementor = SimpleArrayIncrementor.new_with_max_values([0, 0, 0], [1, 2, 1])
        
        # First call should return true (initial state)
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0, 0, 0]
        
        # Increment through all possible combinations
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0, 0, 1]
        
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0, 1, 0]
        
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0, 1, 1]
        
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0, 2, 0]
        
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0, 2, 1]
        
        assert incrementor.increment() == True
        assert incrementor.get_array() == [1, 0, 0]
        
        assert incrementor.increment() == True
        assert incrementor.get_array() == [1, 0, 1]
        
        assert incrementor.increment() == True
        assert incrementor.get_array() == [1, 1, 0]
        
        assert incrementor.increment() == True
        assert incrementor.get_array() == [1, 1, 1]
        
        assert incrementor.increment() == True
        assert incrementor.get_array() == [1, 2, 0]
        
        assert incrementor.increment() == True
        assert incrementor.get_array() == [1, 2, 1]
        
        # Should return false (no more increments)
        assert incrementor.increment() == False
    
    def test_increment_exhaustion(self):
        """Test incrementing when already at maximum."""
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        incrementor = SimpleArrayIncrementor([2, 2, 2])
        
        # First call should return true (initial state)
        assert incrementor.increment() == True
        assert incrementor.get_array() == [2, 2, 2]
        
        # Should return false (no more increments possible)
        assert incrementor.increment() == False
    
    def test_comparison_with_java_array_incrementor(self):
        """Test that Python implementation matches Java array incrementor."""
        ArrayIncrementorImpl = uacalc_lib.util.ArrayIncrementorImpl
        
        # Test with array [0, 1, 2]
        incrementor = ArrayIncrementorImpl([0, 1, 2])
        
        results = []
        results.append(incrementor.get_array().copy())
        
        while incrementor.increment():
            results.append(incrementor.get_array().copy())
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("array_incrementor", ["--array", "0,1,2"])
        
        assert java_result["success"] == True
        assert len(results) == java_result["data"]["total_permutations"]
    
    def test_comparison_with_java_list_incrementor(self):
        """Test that Python implementation matches Java list incrementor."""
        ArrayIncrementorImpl = uacalc_lib.util.ArrayIncrementorImpl
        
        # Test with indices for ["a", "b", "c"]
        incrementor = ArrayIncrementorImpl([0, 1, 2])
        
        results = []
        results.append(incrementor.get_array().copy())
        
        while incrementor.increment():
            results.append(incrementor.get_array().copy())
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("list_incrementor", ["--list", "a,b,c"])
        
        assert java_result["success"] == True
        assert len(results) == java_result["data"]["total_permutations"]
    
    def test_comparison_with_java_test(self):
        """Test that Python implementation matches Java test command."""
        ArrayIncrementorImpl = uacalc_lib.util.ArrayIncrementorImpl
        
        # Test array incrementor
        incrementor = ArrayIncrementorImpl([0, 1, 2])
        
        array_results = []
        array_results.append(incrementor.get_array().copy())
        
        while incrementor.increment():
            array_results.append(incrementor.get_array().copy())
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("test", [])
        
        assert java_result["success"] == True
        assert len(array_results) == java_result["data"]["array_test"]["permutations"]
    
    def test_string_representation(self):
        """Test string representation methods."""
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        incrementor = SimpleArrayIncrementor([0, 1, 2])
        
        str_repr = str(incrementor)
        assert "SimpleArrayIncrementor" in str_repr
        assert "[0, 1, 2]" in str_repr
        
        repr_str = repr(incrementor)
        assert "SimpleArrayIncrementor" in repr_str
        assert "[0, 1, 2]" in repr_str
    
    def test_equality(self):
        """Test equality comparison."""
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        incrementor1 = SimpleArrayIncrementor([0, 1, 2])
        incrementor2 = SimpleArrayIncrementor([0, 1, 2])
        incrementor3 = SimpleArrayIncrementor([0, 1, 3])
        
        assert incrementor1 == incrementor2
        assert incrementor1 != incrementor3
    
    def test_hash(self):
        """Test hash function."""
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        incrementor1 = SimpleArrayIncrementor([0, 1, 2])
        incrementor2 = SimpleArrayIncrementor([0, 1, 2])
        incrementor3 = SimpleArrayIncrementor([0, 1, 3])
        
        assert hash(incrementor1) == hash(incrementor2)
        assert hash(incrementor1) != hash(incrementor3)
    
    def test_edge_cases(self):
        """Test edge cases."""
        SimpleArrayIncrementor = uacalc_lib.util.SimpleArrayIncrementor
        
        # Test single element array
        incrementor = SimpleArrayIncrementor([0])
        
        # First call should return true (initial state)
        assert incrementor.increment() == True
        assert incrementor.get_array() == [0]
        
        # Should return false (no more increments possible)
        assert incrementor.increment() == False
