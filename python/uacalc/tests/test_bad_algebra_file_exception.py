"""
Tests for BadAlgebraFileException Python bindings.

These tests verify that the Python bindings work correctly and match
the Java implementation behavior.
"""

import pytest
import json
import uacalc_lib
from test_utils import TestHarness, TestConfig


class TestBadAlgebraFileException:
    """Test cases for BadAlgebraFileException Python bindings."""
    
    def setup_method(self):
        """Set up test configuration."""
        self.config = TestConfig()
        self.harness = TestHarness(self.config)
    
    def test_create_simple_message(self):
        """Test creating exception with simple message."""
        # Import clean class names (Py* names are not available)
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        exception = BadAlgebraFileException("Test message")
        java_result = self.harness.run_java_cli("java_wrapper.src.io.BadAlgebraFileExceptionWrapper", 
                                               ["create", "--message", "Test message"])
        
        assert exception.message() == "Test message"
        assert java_result.is_success()
        
        java_data = java_result.parse_json()["data"]
        assert exception.message() == java_data["message"]
        assert "BadAlgebraFileException" in str(exception)
        assert "BadAlgebraFileException" in java_data["class_name"]
    
    def test_create_empty_message(self):
        """Test creating exception with empty message."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        exception = BadAlgebraFileException("")
        java_result = self.harness.run_java_cli("java_wrapper.src.io.BadAlgebraFileExceptionWrapper", 
                                               ["create", "--message", ""])
        
        assert exception.message() == ""
        assert java_result.is_success()
        
        java_data = java_result.parse_json()["data"]
        assert exception.message() == java_data["message"]
        assert "BadAlgebraFileException" in str(exception)
    
    def test_create_special_characters(self):
        """Test creating exception with special characters."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        special_message = "Error: File 'test\\file.txt' not found!\nLine 42: Invalid format"
        exception = BadAlgebraFileException(special_message)
        java_result = self.harness.run_java_cli("java_wrapper.src.io.BadAlgebraFileExceptionWrapper", 
                                               ["create", "--message", special_message])
        
        assert exception.message() == special_message
        assert java_result.is_success()
        
        java_data = java_result.parse_json()["data"]
        assert exception.message() == java_data["message"]
        assert "BadAlgebraFileException" in str(exception)
        assert "\n" in exception.message()
        assert "\\" in exception.message()
    
    def test_string_representation(self):
        """Test string representation methods."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        exception = BadAlgebraFileException("String test")
        java_result = self.harness.run_java_cli("java_wrapper.src.io.BadAlgebraFileExceptionWrapper", 
                                               ["create", "--message", "String test"])
        
        # Test __str__
        str_repr = str(exception)
        assert "BadAlgebraFileException" in str_repr
        assert "String test" in str_repr
        
        # Test __repr__
        repr_str = repr(exception)
        assert "BadAlgebraFileException" in repr_str
        assert "String test" in repr_str
        assert repr_str.startswith("BadAlgebraFileException(")
        assert repr_str.endswith(")")
        
        java_data = java_result.parse_json()["data"]
        assert java_result.is_success()
        assert "BadAlgebraFileException" in java_data["string_representation"]
    
    def test_equality(self):
        """Test equality comparison."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        exception1 = BadAlgebraFileException("Equality test")
        exception2 = BadAlgebraFileException("Equality test")
        exception3 = BadAlgebraFileException("Different message")
        
        assert exception1 == exception2
        assert exception1 != exception3
        assert exception2 != exception3
    
    def test_hash(self):
        """Test hash function."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        exception1 = BadAlgebraFileException("Hash test")
        exception2 = BadAlgebraFileException("Hash test")
        exception3 = BadAlgebraFileException("Different message")
        
        assert hash(exception1) == hash(exception2)
        assert hash(exception1) != hash(exception3)
        
        # Test that hash is consistent
        assert hash(exception1) == hash(exception1)
        assert hash(exception2) == hash(exception2)
    
    def test_comprehensive_functionality(self):
        """Test comprehensive functionality against Java implementation."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        java_result = self.harness.run_java_cli("java_wrapper.src.io.BadAlgebraFileExceptionWrapper", ["test"])
        assert java_result.is_success()
        
        java_data = java_result.parse_json()["data"]
        
        # Test 1: Create exception with simple message
        ex1 = BadAlgebraFileException("Test message")
        test1_java = java_data["test1_create_simple"]
        assert test1_java["success"]
        assert ex1.message() == test1_java["message"]
        
        # Test 2: Create exception with empty message
        ex2 = BadAlgebraFileException("")
        test2_java = java_data["test2_create_empty"]
        assert test2_java["success"]
        assert ex2.message() == test2_java["message"]
        assert ex2.message() == ""
        
        # Test 3: Create exception with special characters
        special_message = "Error: File 'test\\file.txt' not found!\nLine 42: Invalid format"
        ex3 = BadAlgebraFileException(special_message)
        test3_java = java_data["test3_create_special_chars"]
        assert test3_java["success"]
        assert ex3.message() == test3_java["message"]
        assert "\n" in ex3.message()
        assert "\\" in ex3.message()
        
        # Test 4: Test toString method
        ex4 = BadAlgebraFileException("toString test")
        test4_java = java_data["test4_to_string"]
        assert test4_java["success"]
        assert "BadAlgebraFileException" in str(ex4)
        assert "toString test" in str(ex4)
    
    def test_edge_cases(self):
        """Test edge cases."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        # Test with very long message
        long_message = "A" * 1000
        exception = BadAlgebraFileException(long_message)
        assert exception.message() == long_message
        assert "BadAlgebraFileException" in str(exception)
        
        # Test with unicode characters
        unicode_message = "错误：文件 '测试文件.txt' 未找到！\n行 42：格式无效"
        exception = BadAlgebraFileException(unicode_message)
        assert exception.message() == unicode_message
        assert "BadAlgebraFileException" in str(exception)
        
        # Test with null-like string (empty string)
        empty_exception = BadAlgebraFileException("")
        assert empty_exception.message() == ""
        assert "BadAlgebraFileException" in str(empty_exception)
    
    def test_type_consistency(self):
        """Test that the exception maintains type consistency."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        exception = BadAlgebraFileException("Type test")
        
        # Test that it's the right type
        assert isinstance(exception, BadAlgebraFileException)
        
        # Test that message() returns a string
        assert isinstance(exception.message(), str)
        
        # Test that string representations are strings
        assert isinstance(str(exception), str)
        assert isinstance(repr(exception), str)
        
        # Test that hash returns an int
        assert isinstance(hash(exception), int)
    
    def test_immutability(self):
        """Test that the exception is immutable after creation."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        exception = BadAlgebraFileException("Immutability test")
        original_message = exception.message()
        original_str = str(exception)
        original_repr = repr(exception)
        original_hash = hash(exception)
        
        # The exception should be immutable - these should not change
        assert exception.message() == original_message
        assert str(exception) == original_str
        assert repr(exception) == original_repr
        assert hash(exception) == original_hash
    
    def test_serialization_compatibility(self):
        """Test that the exception can be used in serialization contexts."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        exception = BadAlgebraFileException("Serialization test")
        
        # Test that it can be converted to a dictionary-like structure
        data = {
            "message": exception.message(),
            "class_name": "BadAlgebraFileException",
            "string_representation": str(exception)
        }
        
        # Verify the structure is what we expect
        assert isinstance(data["message"], str)
        assert isinstance(data["class_name"], str)
        assert isinstance(data["string_representation"], str)
        assert data["message"] == "Serialization test"
        assert data["class_name"] == "BadAlgebraFileException"
        
        # Test JSON serialization
        json_str = json.dumps(data)
        parsed_data = json.loads(json_str)
        assert parsed_data["message"] == "Serialization test"
        assert parsed_data["class_name"] == "BadAlgebraFileException"
    
    def test_clean_import(self):
        """Test that only clean class names are available for import."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        # Clean import should work
        exception = BadAlgebraFileException("Clean import test")
        assert exception.message() == "Clean import test"
        
        # Py* names should not be available
        with pytest.raises(AttributeError):
            getattr(uacalc_lib.io, 'PyBadAlgebraFileException')
    
    def test_error_handling(self):
        """Test error handling in edge cases."""
        BadAlgebraFileException = uacalc_lib.io.BadAlgebraFileException
        
        # Test with None-like behavior (empty string)
        exception = BadAlgebraFileException("")
        assert exception.message() == ""
        assert "BadAlgebraFileException" in str(exception)
        
        # Test with very long strings
        long_message = "X" * 10000
        exception = BadAlgebraFileException(long_message)
        assert exception.message() == long_message
        assert len(exception.message()) == 10000
