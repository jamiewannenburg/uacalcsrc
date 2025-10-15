"""
Tests for LongList virtual list implementations.

This module tests the Python bindings for LongList against the Java
ground truth using the Java CLI wrapper for validation.
"""

import pytest
import uacalc_lib
import json
import subprocess
from test_utils import build_java_command


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    wrapper_class = "java_wrapper.src.util.LongListWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")
        
        output = json.loads(result.stdout)
        # The data field contains a JSON string, so we need to parse it again
        if "data" in output and isinstance(output["data"], str):
            output["data"] = json.loads(output["data"])
        return output
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Java wrapper output: {e}")


def run_tuple_with_min_wrapper(command, args):
    """Run TupleWithMin Java wrapper and return JSON output."""
    wrapper_class = "java_wrapper.src.util.virtuallist.TupleWithMinWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")
        
        output = json.loads(result.stdout)
        # The data field contains a JSON string, so we need to parse it again
        if "data" in output and isinstance(output["data"], str):
            output["data"] = json.loads(output["data"])
        return output
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Java wrapper output: {e}")


class TestTupleWithMin:
    """Test TupleWithMin LongList implementation."""
    
    def test_basic_creation(self):
        """Test basic TupleWithMin creation."""
        TupleWithMin = uacalc_lib.util.TupleWithMin
        
        # Test basic creation
        tuples = TupleWithMin(3, 4, 2)
        assert tuples.size() == 56  # Expected size for (3, 4, 2)
        
        # Test with Java comparison
        java_result = run_tuple_with_min_wrapper("new", ["--arrayLen", "3", "--base", "4", "--min", "2"])
        assert tuples.size() == java_result["data"]["size"]
    
    def test_size(self):
        """Test TupleWithMin size method."""
        TupleWithMin = uacalc_lib.util.TupleWithMin
        
        tuples = TupleWithMin(3, 4, 2)
        result = tuples.size()
        
        # Test with Java comparison
        java_result = run_tuple_with_min_wrapper("size", ["--arrayLen", "3", "--base", "4", "--min", "2"])
        assert result == java_result["data"]["size"]
    
    def test_get_first_element(self):
        """Test getting the first element from TupleWithMin."""
        TupleWithMin = uacalc_lib.util.TupleWithMin
        
        tuples = TupleWithMin(3, 4, 2)
        result = tuples.get(0)
        
        # Test with Java comparison
        java_result = run_tuple_with_min_wrapper("get", ["--arrayLen", "3", "--base", "4", "--min", "2", "--k", "0"])
        assert result == java_result["data"]["value"]
    
    def test_get_middle_element(self):
        """Test getting a middle element from TupleWithMin."""
        TupleWithMin = uacalc_lib.util.TupleWithMin
        
        tuples = TupleWithMin(3, 4, 2)
        result = tuples.get(28)
        
        # Test with Java comparison
        java_result = run_tuple_with_min_wrapper("get", ["--arrayLen", "3", "--base", "4", "--min", "2", "--k", "28"])
        assert result == java_result["data"]["value"]
    
    def test_get_last_element(self):
        """Test getting the last element from TupleWithMin."""
        TupleWithMin = uacalc_lib.util.TupleWithMin
        
        tuples = TupleWithMin(3, 4, 2)
        result = tuples.get(55)
        
        # Test with Java comparison
        java_result = run_tuple_with_min_wrapper("get", ["--arrayLen", "3", "--base", "4", "--min", "2", "--k", "55"])
        assert result == java_result["data"]["value"]
    
    def test_different_parameters(self):
        """Test TupleWithMin with different parameters."""
        TupleWithMin = uacalc_lib.util.TupleWithMin
        
        tuples = TupleWithMin(4, 5, 3)
        result = tuples.size()
        
        # Test with Java comparison
        java_result = run_tuple_with_min_wrapper("new", ["--arrayLen", "4", "--base", "5", "--min", "3"])
        assert result == java_result["data"]["size"]
    
    def test_sequence_of_elements(self):
        """Test getting a sequence of elements."""
        TupleWithMin = uacalc_lib.util.TupleWithMin
        
        tuples = TupleWithMin(3, 4, 2)
        elements = [tuples.get(i) for i in range(10)]
        
        # Test with Java comparison
        java_result = run_tuple_with_min_wrapper("test", [])
        assert elements == java_result["data"]["elements"]
    
    def test_error_handling(self):
        """Test error handling for invalid parameters."""
        TupleWithMin = uacalc_lib.util.TupleWithMin
        
        # Test with invalid parameters - base <= min should raise error
        with pytest.raises(Exception):
            TupleWithMin(3, 2, 2)
        
        # Test with base < min
        with pytest.raises(Exception):
            TupleWithMin(3, 2, 3)
    
    def test_string_representation(self):
        """Test string representation methods."""
        TupleWithMin = uacalc_lib.util.TupleWithMin
        
        tuples = TupleWithMin(3, 4, 2)
        
        # Test __str__
        str_repr = str(tuples)
        assert "TupleWithMin" in str_repr
        assert "3" in str_repr
        assert "4" in str_repr
        assert "2" in str_repr
        
        # Test __repr__
        repr_str = repr(tuples)
        assert "TupleWithMin" in repr_str


class TestIntTuples:
    """Test IntTuples LongList implementation."""
    
    def test_basic_creation(self):
        """Test basic IntTuples creation."""
        IntTuples = uacalc_lib.util.IntTuples
        
        # Test basic creation
        list_obj = IntTuples(3, 4)
        assert list_obj.size() == 64  # 4^3
        
        # Test with Java comparison
        java_result = run_java_wrapper("int_tuples", ["--tuple_length", "3", "--base", "4"])
        assert list_obj.size() == java_result["data"]["size"]
    
    def test_get_element(self):
        """Test getting elements from IntTuples."""
        IntTuples = uacalc_lib.util.IntTuples
        
        list_obj = IntTuples(3, 4)
        result = list_obj.get(5)
        
        # Test with Java comparison
        java_result = run_java_wrapper("int_tuples", ["--tuple_length", "3", "--base", "4", "--k", "5"])
        assert str(result) == java_result["data"]["status"]
    
    def test_error_handling(self):
        """Test error handling for invalid parameters."""
        IntTuples = uacalc_lib.util.IntTuples
        
        # Test with invalid parameters that should raise errors
        with pytest.raises(Exception):
            IntTuples(0, 0)  # Both parameters 0


class TestIntTuplesWithMin:
    """Test IntTuplesWithMin LongList implementation."""
    
    def test_basic_creation(self):
        """Test basic IntTuplesWithMin creation."""
        IntTuplesWithMin = uacalc_lib.util.IntTuplesWithMin
        
        # Test basic creation
        list_obj = IntTuplesWithMin(3, 4, 2)
        assert list_obj.size() > 0
        
        # Test with Java comparison
        java_result = run_java_wrapper("int_tuples_with_min", ["--tuple_length", "3", "--base", "4", "--min", "2"])
        assert list_obj.size() == java_result["data"]["size"]
    
    def test_get_element(self):
        """Test getting elements from IntTuplesWithMin."""
        IntTuplesWithMin = uacalc_lib.util.IntTuplesWithMin
        
        list_obj = IntTuplesWithMin(3, 4, 2)
        result = list_obj.get(5)
        
        # Test with Java comparison
        java_result = run_java_wrapper("int_tuples_with_min", ["--tuple_length", "3", "--base", "4", "--min", "2", "--k", "5"])
        assert str(result) == java_result["data"]["status"]
    
    def test_error_handling(self):
        """Test error handling for invalid parameters."""
        IntTuplesWithMin = uacalc_lib.util.IntTuplesWithMin
        
        # Test with invalid parameters that should raise errors
        with pytest.raises(Exception):
            IntTuplesWithMin(3, 2, 2)  # base <= min


class TestFixedSizedSubsets:
    """Test FixedSizedSubsets LongList implementation."""
    
    def test_basic_creation(self):
        """Test basic FixedSizedSubsets creation."""
        FixedSizedSubsets = uacalc_lib.util.FixedSizedSubsets
        
        # Test basic creation
        list_obj = FixedSizedSubsets(3, 6)
        assert list_obj.size() > 0
        
        # Test with Java comparison
        java_result = run_java_wrapper("fixed_sized_subsets", ["--subset_size", "3", "--set_size", "6"])
        assert list_obj.size() == java_result["data"]["size"]
    
    def test_get_element(self):
        """Test getting elements from FixedSizedSubsets."""
        FixedSizedSubsets = uacalc_lib.util.FixedSizedSubsets
        
        list_obj = FixedSizedSubsets(3, 6)
        result = list_obj.get(5)
        
        # Test with Java comparison
        java_result = run_java_wrapper("fixed_sized_subsets", ["--subset_size", "3", "--set_size", "6", "--k", "5"])
        assert str(result) == java_result["data"]["status"]
    
    def test_error_handling(self):
        """Test error handling for invalid parameters."""
        FixedSizedSubsets = uacalc_lib.util.FixedSizedSubsets
        
        # Test with invalid parameters that should raise errors
        with pytest.raises(Exception):
            FixedSizedSubsets(5, 3)  # subset_size > set_size


class TestSubsets:
    """Test Subsets LongList implementation."""
    
    def test_basic_creation(self):
        """Test basic Subsets creation."""
        Subsets = uacalc_lib.util.Subsets
        
        # Test basic creation
        list_obj = Subsets(4)
        assert list_obj.size() == 16  # 2^4
        
        # Test with Java comparison
        java_result = run_java_wrapper("subsets", ["--set_size", "4"])
        assert list_obj.size() == java_result["data"]["size"]
    
    def test_get_element(self):
        """Test getting elements from Subsets."""
        Subsets = uacalc_lib.util.Subsets
        
        list_obj = Subsets(4)
        result = list_obj.get(5)
        
        # Test with Java comparison
        java_result = run_java_wrapper("subsets", ["--set_size", "4", "--k", "5"])
        assert str(result) == java_result["data"]["status"]
    
    def test_error_handling(self):
        """Test error handling for invalid parameters."""
        Subsets = uacalc_lib.util.Subsets
        
        # Test with invalid parameters that should raise errors
        with pytest.raises(Exception):
            Subsets(63)  # too large


class TestPermutations:
    """Test Permutations LongList implementation."""
    
    def test_basic_creation(self):
        """Test basic Permutations creation."""
        Permutations = uacalc_lib.util.Permutations
        
        # Test basic creation
        list_obj = Permutations(4)
        assert list_obj.size() == 24  # 4!
        
        # Test with Java comparison
        java_result = run_java_wrapper("permutations", ["--n", "4"])
        assert list_obj.size() == java_result["data"]["size"]
    
    def test_get_element(self):
        """Test getting elements from Permutations."""
        Permutations = uacalc_lib.util.Permutations
        
        list_obj = Permutations(4)
        result = list_obj.get(5)
        
        # Test with Java comparison
        java_result = run_java_wrapper("permutations", ["--n", "4", "--k", "5"])
        assert str(result) == java_result["data"]["status"]
    
    def test_error_handling(self):
        """Test error handling for invalid parameters."""
        Permutations = uacalc_lib.util.Permutations
        
        # Test with invalid parameters that should raise errors
        with pytest.raises(Exception):
            Permutations(21)  # too large


class TestLongListUtils:
    """Test LongListUtils utility functions."""
    
    def test_factorial(self):
        """Test factorial function."""
        LongListUtils = uacalc_lib.util.LongListUtils
        
        result = LongListUtils.factorial(5)
        assert result == 120
        
        # Test with Java comparison
        java_result = run_java_wrapper("factorial", ["--n", "5"])
        assert result == java_result["data"]["status"]
    
    def test_binomial(self):
        """Test binomial coefficient function."""
        LongListUtils = uacalc_lib.util.LongListUtils
        
        result = LongListUtils.binomial(5, 2)
        assert result == 10
        
        # Test with Java comparison
        java_result = run_java_wrapper("binomial", ["--n", "5", "--r", "2"])
        assert result == java_result["data"]["status"]
    
    def test_log2(self):
        """Test log2 function."""
        LongListUtils = uacalc_lib.util.LongListUtils
        
        result = LongListUtils.log2(8)
        assert result == 3
        
        # Test with Java comparison
        java_result = run_java_wrapper("log2", ["--k", "8"])
        assert result == java_result["data"]["status"]
    
    def test_pow2(self):
        """Test pow2 function."""
        LongListUtils = uacalc_lib.util.LongListUtils
        
        result = LongListUtils.pow2(3)
        assert result == 8
        
        # Test with Java comparison
        java_result = run_java_wrapper("pow2", ["--r", "3"])
        assert result == java_result["data"]["status"]


class TestComprehensive:
    """Test comprehensive functionality."""
    
    def test_comprehensive_functionality(self):
        """Test comprehensive functionality against Java."""
        IntTuples = uacalc_lib.util.IntTuples
        Subsets = uacalc_lib.util.Subsets
        LongListUtils = uacalc_lib.util.LongListUtils
        
        # Test basic functionality
        tuples = IntTuples(3, 4)
        result1 = tuples.get(0)
        
        subsets = Subsets(4)
        result2 = subsets.get(0)
        
        factorial = LongListUtils.factorial(5)
        binomial = LongListUtils.binomial(5, 2)
        
        # Test with Java comparison
        java_result = run_java_wrapper("test", [])
        
        assert tuples.size() == java_result["data"]["int_tuples_size"]
        assert str(result1) == java_result["data"]["int_tuples_first"]
        assert subsets.size() == java_result["data"]["subsets_size"]
        assert str(result2) == java_result["data"]["subsets_first"]
        assert factorial == java_result["data"]["factorial_5"]
        assert binomial == java_result["data"]["binomial_5_2"]
        assert java_result["data"]["status"] == "all_tests_passed"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_edge_cases(self):
        """Test edge cases."""
        IntTuples = uacalc_lib.util.IntTuples
        Subsets = uacalc_lib.util.Subsets
        Permutations = uacalc_lib.util.Permutations
        
        # Test edge cases
        list1 = IntTuples(0, 1)
        assert list1.size() == 1
        assert list1.get(0) == []
        
        list2 = Subsets(0)
        assert list2.size() == 1
        assert list2.get(0) == []
        
        list3 = Permutations(0)
        assert list3.size() == 1
        assert list3.get(0) == []
    
    def test_consistency(self):
        """Test that multiple calls return the same result."""
        IntTuples = uacalc_lib.util.IntTuples
        Permutations = uacalc_lib.util.Permutations
        
        # Test consistency
        list1 = IntTuples(3, 4)
        result1 = list1.get(5)
        result2 = list1.get(5)
        assert result1 == result2
        
        list2 = Permutations(4)
        result1 = list2.get(10)
        result2 = list2.get(10)
        assert result1 == result2
    
    def test_bounds(self):
        """Test bounds checking."""
        IntTuples = uacalc_lib.util.IntTuples
        
        # Test bounds
        list_obj = IntTuples(3, 4)
        size = list_obj.size()
        
        # Test first and last elements
        first = list_obj.get(0)
        last = list_obj.get(size - 1)
        
        # Test that we can access all elements without errors
        for i in range(min(size, 100)):  # Limit to avoid too long tests
            _ = list_obj.get(i)
    
    def test_utility_functions_edge_cases(self):
        """Test utility functions with edge cases."""
        LongListUtils = uacalc_lib.util.LongListUtils
        
        # Test edge cases
        assert LongListUtils.factorial(0) == 1
        assert LongListUtils.factorial(1) == 1
        assert LongListUtils.factorial(5) == 120
        
        assert LongListUtils.binomial(5, 0) == 1
        assert LongListUtils.binomial(5, 5) == 1
        assert LongListUtils.binomial(5, 2) == 10
        
        assert LongListUtils.log2(1) == 0
        assert LongListUtils.log2(2) == 1
        assert LongListUtils.log2(8) == 3
        
        assert LongListUtils.pow2(0) == 1
        assert LongListUtils.pow2(1) == 2
        assert LongListUtils.pow2(3) == 8
