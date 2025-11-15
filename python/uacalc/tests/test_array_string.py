"""
Tests for ArrayString Python bindings.

This module provides comprehensive tests for the ArrayString class,
including unit tests and integration tests.
"""

import json
import pytest
import uacalc_lib as lib
from test_utils import TestConfig, TestHarness

class TestArrayString:
    """Test cases for ArrayString Python bindings."""
    
    @property
    def ArrayString(self):
        """Get the ArrayString class."""
        return lib.util.ArrayString
    
    def test_to_string_int(self):
        """Test converting integer array to string."""
        result = self.ArrayString.to_string_int([1, 2, 3])
        assert result == "[1,2,3]"
    
    def test_to_string_empty(self):
        """Test converting empty array to string."""
        result = self.ArrayString.to_string_int([])
        assert result == "[]"
    
    def test_to_string_single(self):
        """Test converting single element array to string."""
        result = self.ArrayString.to_string_int([42])
        assert result == "[42]"
    
    def test_to_string_2d_int(self):
        """Test converting 2D integer array to string."""
        result = self.ArrayString.to_string_2d_int([[1, 2], [3, 4]])
        assert result == "[[1,2],[3,4]]"
    
    def test_to_string_2d_empty(self):
        """Test converting empty 2D array to string."""
        result = self.ArrayString.to_string_2d_int([])
        assert result == "[]"
    
    def test_to_string_2d_mixed(self):
        """Test converting mixed 2D array to string."""
        result = self.ArrayString.to_string_2d_int([[1], [2, 3], []])
        assert result == "[[1],[2,3],[]]"
    
    def test_to_string_str(self):
        """Test converting string array to string."""
        result = self.ArrayString.to_string_str(["hello", "world"])
        assert result == "[hello,world]"
    
    def test_to_string_2d_str(self):
        """Test converting 2D string array to string."""
        result = self.ArrayString.to_string_2d_str([["a", "b"], ["c", "d"]])
        assert result == "[[a,b],[c,d]]"
    
    def test_value_of_str(self):
        """Test value_of with string."""
        result = self.ArrayString.value_of("hello")
        assert result == "hello"
    
    def test_value_of_int(self):
        """Test value_of with integer."""
        result = self.ArrayString.value_of(42)
        assert result == "42"
    
    def test_to_string_generic(self):
        """Test generic to_string with Python objects."""
        result = self.ArrayString.to_string([1, 2, 3])
        assert result == "[1,2,3]"
    
    def test_to_string_2d_generic(self):
        """Test generic to_string_2d with Python objects."""
        result = self.ArrayString.to_string_2d([[1, 2], [3, 4]])
        assert result == "[[1,2],[3,4]]"
    
    def test_nested_conversion(self):
        """Test nested array conversion."""
        result = self.ArrayString.to_string_2d_int([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        assert result == "[[1,2,3],[4,5,6],[7,8,9]]"
    
    def test_large_array(self):
        """Test large array conversion."""
        result = self.ArrayString.to_string_int([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        assert result == "[1,2,3,4,5,6,7,8,9,10]"
    
    def test_array_string_instance(self):
        """Test creating ArrayString instance."""
        # ArrayString is a static utility class, but we should be able to create instances
        instance = self.ArrayString()
        assert instance is not None
        assert str(instance) == "ArrayString"
        assert repr(instance) == "ArrayString()"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])