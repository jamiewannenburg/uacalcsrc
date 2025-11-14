"""
Tests for PermutationGenerator functionality.

This module tests the Python bindings for PermutationGenerator against
the Java implementation using the test infrastructure.
"""

import pytest
import uacalc_lib
from pathlib import Path
import json
import platform


class TestPermutationGenerator:
    """Test cases for PermutationGenerator Python bindings."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.java_wrapper_path = self.project_root / "java_wrapper" / "build" / "scripts"
        
    def get_script_extension(self) -> str:
        """Get the appropriate script extension for the current platform."""
        return ".bat" if platform.system() == "Windows" else ""
    
    def run_java_wrapper(self, command, args):
        """Run Java wrapper and return JSON output."""
        from test_utils import build_java_command
        
        wrapper_class = "java_wrapper.src.util.PermutationGeneratorWrapper"
        cmd = build_java_command(wrapper_class, [command] + args)
        
        import subprocess
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                pytest.fail(f"Java wrapper failed: {result.stderr}")
            
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            pytest.fail("Java wrapper timed out")
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to parse Java wrapper output: {e}")
    
    def test_new(self):
        """Test creating a new PermutationGenerator."""
        # Import through uacalc_lib module (direct imports don't work)
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        generator = PermutationGenerator(3)
        assert generator.size() == 3
        
        # Test against Java implementation
        java_result = self.run_java_wrapper("new", ["--n", "3"])
        assert java_result["success"] is True
        assert java_result["data"]["n"] == 3
        assert java_result["data"]["status"] == "created"
    
    def test_new_invalid(self):
        """Test creating PermutationGenerator with invalid input."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        with pytest.raises(Exception):  # Should raise an error for n < 1
            PermutationGenerator(0)
    
    def test_reset(self):
        """Test resetting the generator."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        generator = PermutationGenerator(3)
        generator.reset()
        # After reset, should be back to identity permutation
        assert generator.get_permutation() == [0, 1, 2]
    
    def test_get_permutation(self):
        """Test getting the current permutation."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        generator = PermutationGenerator(3)
        perm = generator.get_permutation()
        assert perm == [0, 1, 2]  # Should start with identity permutation
    
    def test_size(self):
        """Test getting the size of the permutation."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        generator = PermutationGenerator(3)
        assert generator.size() == 3
    
    def test_next_index(self):
        """Test getting the next index for permutation."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        generator = PermutationGenerator(3)
        next_index = generator.next_index()
        assert next_index == 1  # First swap should be at index 1
    
    def test_next_index_safe(self):
        """Test getting the next index with error handling."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        generator = PermutationGenerator(3)
        next_index = generator.next_index_safe()
        assert next_index == 1  # First swap should be at index 1
        
        # Test with generator that has no more permutations
        gen1 = PermutationGenerator(1)
        with pytest.raises(Exception):  # Should raise an error for no more permutations
            gen1.next_index_safe()
    
    def test_iterator(self):
        """Test the iterator over all permutations."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        iterator = PermutationGenerator.iterator(3)
        permutations = list(iterator)
        assert len(permutations) == 6  # 3! = 6
        assert permutations[0] == [0, 1, 2]  # First should be identity
        
        # Test against Java implementation
        java_result = self.run_java_wrapper("iterator", ["--n", "3"])
        assert java_result["success"] is True
        assert java_result["data"]["n"] == 3
        assert java_result["data"]["count"] == 6
        assert java_result["data"]["status"] == "success"
    
    def test_array_incrementor(self):
        """Test the array incrementor."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        arr = [0, 1, 2]
        incrementor = PermutationGenerator.array_incrementor(arr)
        
        count = 0
        while incrementor.increment():
            count += 1
        
        assert count == 5  # 6 permutations - 1 initial = 5 increments
        assert incrementor.get_array() == [0, 1, 2]  # Should be back to original
        
        # Test against Java implementation
        java_result = self.run_java_wrapper("array_incrementor", ["--array", "[0,1,2]"])
        assert java_result["success"] is True
        assert java_result["data"]["original_array"] == "[0,1,2]"
        assert java_result["data"]["increment_count"] == 5
        assert java_result["data"]["status"] == "success"
    
    def test_list_incrementor(self):
        """Test the list incrementor."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        lst = ["a", "b", "c"]
        incrementor = PermutationGenerator.list_incrementor(lst)
        
        count = 0
        while incrementor.increment():
            count += 1
        
        assert count == 5  # 6 permutations - 1 initial = 5 increments
        assert incrementor.get_list() == ["a", "b", "c"]  # Should be back to original
        
        # Test against Java implementation
        java_result = self.run_java_wrapper("list_incrementor", ["--list", '["a","b","c"]'])
        assert java_result["success"] is True
        assert java_result["data"]["original_list"] == '["a","b","c"]'
        assert java_result["data"]["increment_count"] == 5
        assert java_result["data"]["status"] == "success"
    
    def test_basic_functionality(self):
        """Test basic functionality against Java implementation."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test Python implementation
        generator = PermutationGenerator(3)
        assert generator.size() == 3
        assert generator.get_permutation() == [0, 1, 2]
        
        next_index = generator.next_index()
        assert next_index == 1
        
        # Test iterator
        iterator = PermutationGenerator.iterator(3)
        count = sum(1 for _ in iterator)
        assert count == 6
        
        # Test against Java implementation
        java_result = self.run_java_wrapper("test", [])
        assert java_result["success"] is True
        assert java_result["data"]["status"] == "completed"
        assert len(java_result["data"]["test_results"]) > 0
    
    def test_permutation_sequence(self):
        """Test that we get the correct sequence of permutations."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        generator = PermutationGenerator(3)
        permutations = []
        
        # Get initial permutation
        permutations.append(generator.get_permutation())
        
        # Get next few permutations
        for _ in range(5):
            if generator.next_index() is not None:
                permutations.append(generator.get_permutation())
        
        # Verify we have the expected permutations
        assert permutations[0] == [0, 1, 2]  # Initial identity
        assert permutations[1] == [0, 2, 1]  # After first swap
    
    def test_edge_cases(self):
        """Test edge cases."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test with n=1
        gen1 = PermutationGenerator(1)
        assert gen1.get_permutation() == [0]
        assert gen1.next_index() is None  # No more permutations
        
        # Test with n=2
        gen2 = PermutationGenerator(2)
        assert gen2.get_permutation() == [0, 1]
        assert gen2.next_index() == 0  # Swap 0 and 1
        assert gen2.get_permutation() == [1, 0]
        assert gen2.next_index() is None  # No more permutations
        
        # Test iterator with n=1
        iterator1 = PermutationGenerator.iterator(1)
        count = sum(1 for _ in iterator1)
        assert count == 1  # Only one permutation for n=1
        
        # Test iterator with n=2
        iterator2 = PermutationGenerator.iterator(2)
        count = sum(1 for _ in iterator2)
        assert count == 2  # Two permutations for n=2
    
    def test_reset_functionality(self):
        """Test reset functionality."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        generator = PermutationGenerator(3)
        
        # Advance the generator
        generator.next_index()
        perm_after_first = generator.get_permutation()
        assert perm_after_first != [0, 1, 2]  # Should be different from initial
        
        # Reset and verify we're back to initial state
        generator.reset()
        perm_after_reset = generator.get_permutation()
        assert perm_after_reset == [0, 1, 2]  # Should be back to identity
    
    def test_display_and_equality(self):
        """Test display and equality functionality."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        gen1 = PermutationGenerator(3)
        gen2 = PermutationGenerator(3)
        
        # Test string representation
        str_repr = str(gen1)
        assert "PermutationGenerator" in str_repr
        assert "n=3" in str_repr
        
        # Test equality
        assert gen1 == gen2
        
        # Test hash (should be equal for equal objects)
        assert hash(gen1) == hash(gen2)
    
    def test_array_incrementor_with_different_types(self):
        """Test array incrementor with different data types."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test with integers
        arr_int = [1, 2, 3]
        incrementor_int = PermutationGenerator.array_incrementor(arr_int)
        count_int = 0
        while incrementor_int.increment():
            count_int += 1
        assert count_int == 5
        
        # Note: array_incrementor only works with integers, not strings
        # For string permutations, use list_incrementor instead
    
    def test_list_incrementor_with_different_types(self):
        """Test list incrementor with different data types."""
        PermutationGenerator = uacalc_lib.util.PermutationGenerator
        
        # Test with strings
        lst_str = ["alpha", "beta", "gamma"]
        incrementor_str = PermutationGenerator.list_incrementor(lst_str)
        count_str = 0
        while incrementor_str.increment():
            count_str += 1
        assert count_str == 5
        
        # Test with mixed types
        lst_mixed = [1, "two", 3.0]
        incrementor_mixed = PermutationGenerator.list_incrementor(lst_mixed)
        count_mixed = 0
        while incrementor_mixed.increment():
            count_mixed += 1
        assert count_mixed == 5
