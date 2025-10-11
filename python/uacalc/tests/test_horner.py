"""
Tests for Horner Python bindings.

These tests verify that the Python bindings work correctly
and provide the expected interface to the Rust implementation.
"""

import pytest
import subprocess
import json
import os
import sys
import platform
from pathlib import Path

# Add the project root to the path to import uacalc_lib
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import uacalc_lib
    Horner = uacalc_lib.util.Horner
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    from test_utils import build_java_command
    
    wrapper_class = "java_wrapper.src.util.HornerWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=project_root
        )
        
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")
        
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Java wrapper output: {e}")


class TestHorner:
    """Test Horner Python bindings."""
    
    def test_horner_encoding(self):
        """Test basic Horner encoding."""
        args = [1, 2, 3]
        sizes = [4, 5, 6]
        
        # Test Python implementation
        python_result = Horner.horner(args, sizes)
        
        # Test Java implementation
        java_result = run_java_wrapper("horner", ["--args", "1,2,3", "--sizes", "4,5,6"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_horner_inv(self):
        """Test Horner inverse decoding."""
        k = 123
        sizes = [4, 5, 6]
        
        # Test Python implementation
        python_result = Horner.horner_inv(k, sizes)
        
        # Test Java implementation
        java_result = run_java_wrapper("hornerInv", ["--k", "123", "--sizes", "4,5,6"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_horner_same_size(self):
        """Test Horner encoding with same size algebras."""
        args = [1, 2, 3]
        size = 10
        
        # Test Python implementation
        python_result = Horner.horner_same_size(args, size)
        
        # Test Java implementation
        java_result = run_java_wrapper("hornerSameSize", ["--args", "1,2,3", "--size", "10"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_horner_inv_same_size(self):
        """Test Horner inverse with same size algebras."""
        k = 321
        size = 10
        length = 3
        
        # Test Python implementation
        python_result = Horner.horner_inv_same_size(k, size, length)
        
        # Test Java implementation
        java_result = run_java_wrapper("hornerInvSameSize", ["--k", "321", "--size", "10", "--length", "3"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_horner_integer(self):
        """Test Horner encoding with Integer arrays."""
        args = [2, 1, 0]
        size = 5
        
        # Test Python implementation
        python_result = Horner.horner_integer(args, size)
        
        # Test Java implementation
        java_result = run_java_wrapper("hornerInteger", ["--args", "2,1,0", "--size", "5"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_reverse_array(self):
        """Test array reversal."""
        arr = [1, 2, 3, 4]
        
        # Test Python implementation
        python_result = Horner.reverse_array(arr)
        
        # Test Java implementation
        java_result = run_java_wrapper("reverseArray", ["--arr", "1,2,3,4"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_left_right_reverse(self):
        """Test left-right reverse transformation."""
        values = [0, 1, 2, 3]
        alg_size = 2
        arity = 2
        
        # Test Python implementation
        python_result = Horner.left_right_reverse(values, alg_size, arity)
        
        # Test Java implementation
        java_result = run_java_wrapper("leftRightReverse", ["--values", "0,1,2,3", "--algSize", "2", "--arity", "2"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_horner_round_trip(self):
        """Test round-trip encoding/decoding."""
        args = [2, 3, 1]
        sizes = [4, 5, 6]
        
        # Encode
        encoded = Horner.horner(args, sizes)
        
        # Decode
        decoded = Horner.horner_inv(encoded, sizes)
        
        # Verify round trip
        assert decoded == args
    
    def test_horner_same_size_round_trip(self):
        """Test round-trip encoding/decoding with same size."""
        args = [1, 2, 3]
        size = 10
        length = 3
        
        # Encode
        encoded = Horner.horner_same_size(args, size)
        
        # Decode
        decoded = Horner.horner_inv_same_size(encoded, size, length)
        
        # Verify round trip
        assert decoded == args
    
    def test_horner_integer_round_trip(self):
        """Test round-trip encoding/decoding with Integer arrays."""
        args = [2, 1, 0]
        size = 5
        length = 3
        
        # Encode
        encoded = Horner.horner_integer(args, size)
        
        # Decode
        decoded = Horner.horner_inv_same_size(encoded, size, length)
        
        # Verify round trip
        assert decoded == args
    
    def test_error_handling_mismatched_arrays(self):
        """Test error handling for mismatched array lengths."""
        args = [1, 2, 3]
        sizes = [4, 5]  # Different length
        
        with pytest.raises(Exception):  # Should raise PyValueError
            Horner.horner(args, sizes)
    
    def test_error_handling_empty_sizes(self):
        """Test error handling for empty sizes array."""
        k = 123
        sizes = []
        
        with pytest.raises(Exception):  # Should raise PyValueError
            Horner.horner_inv(k, sizes)
    
    def test_error_handling_negative_size(self):
        """Test error handling for negative size."""
        args = [1, 2, 3]
        size = -1
        
        with pytest.raises(Exception):  # Should raise PyValueError
            Horner.horner_same_size(args, size)
    
    def test_error_handling_zero_length(self):
        """Test error handling for zero length."""
        k = 123
        size = 10
        length = 0
        
        with pytest.raises(Exception):  # Should raise PyValueError
            Horner.horner_inv_same_size(k, size, length)
    
    def test_error_handling_negative_alg_size(self):
        """Test error handling for negative alg_size."""
        values = [0, 1, 2, 3]
        alg_size = -1
        arity = 2
        
        with pytest.raises(Exception):  # Should raise PyValueError
            Horner.left_right_reverse(values, alg_size, arity)
    
    def test_error_handling_zero_arity(self):
        """Test error handling for zero arity."""
        values = [0, 1, 2, 3]
        alg_size = 2
        arity = 0
        
        with pytest.raises(Exception):  # Should raise PyValueError
            Horner.left_right_reverse(values, alg_size, arity)
    
    def test_edge_cases_single_element(self):
        """Test edge cases with single element arrays."""
        args = [5]
        sizes = [10]
        
        # Test Python implementation
        python_result = Horner.horner(args, sizes)
        
        # Test Java implementation
        java_result = run_java_wrapper("horner", ["--args", "5", "--sizes", "10"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_edge_cases_large_arrays(self):
        """Test edge cases with larger arrays."""
        args = [1, 2, 3, 4, 5]
        sizes = [6, 7, 8, 9, 10]
        
        # Test Python implementation
        python_result = Horner.horner(args, sizes)
        
        # Test Java implementation
        java_result = run_java_wrapper("horner", ["--args", "1,2,3,4,5", "--sizes", "6,7,8,9,10"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_edge_cases_zero_values(self):
        """Test edge cases with zero values."""
        args = [0, 0, 0]
        sizes = [2, 3, 4]
        
        # Test Python implementation
        python_result = Horner.horner(args, sizes)
        
        # Test Java implementation
        java_result = run_java_wrapper("horner", ["--args", "0,0,0", "--sizes", "2,3,4"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_edge_cases_maximum_values(self):
        """Test edge cases with maximum values."""
        args = [1, 2, 3]
        sizes = [2, 3, 4]
        
        # Test Python implementation
        python_result = Horner.horner(args, sizes)
        
        # Test Java implementation
        java_result = run_java_wrapper("horner", ["--args", "1,2,3", "--sizes", "2,3,4"])
        
        assert python_result == java_result["data"]["result"]
    
    def test_performance_large_arrays(self):
        """Test performance with large arrays."""
        import time
        
        args = list(range(1, 11))  # [1, 2, ..., 10]
        sizes = list(range(11, 21))  # [11, 12, ..., 20]
        
        # Time Python implementation
        start_time = time.time()
        python_result = Horner.horner(args, sizes)
        python_time = time.time() - start_time
        
        # Time Java implementation
        start_time = time.time()
        java_result = run_java_wrapper("horner", ["--args", ",".join(map(str, args)), "--sizes", ",".join(map(str, sizes))])
        java_time = time.time() - start_time
        
        # Verify results match
        assert python_result == java_result["data"]["result"]
        
        # Python should be reasonably fast (less than 1 second for this size)
        assert python_time < 1.0
    
    def test_string_representation(self):
        """Test string representation of Horner class."""
        horner = Horner()
        assert str(horner) == "Horner"
        assert repr(horner) == "Horner()"
    
    def test_original_main_functionality(self):
        """Test the original main method functionality."""
        # This test runs the original main method test
        java_result = run_java_wrapper("test", [])
        
        # Just verify it completed successfully
        assert "message" in java_result["data"]
        assert java_result["data"]["message"] == "Test completed successfully"
