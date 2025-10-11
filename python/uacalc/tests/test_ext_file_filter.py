#!/usr/bin/env python3
"""
Tests for ExtFileFilter Python bindings.

This module tests the ExtFileFilter functionality through Python bindings,
ensuring that the Rust implementation works correctly from Python.
"""

import pytest
import tempfile
import os
import uacalc_lib


class TestExtFileFilter:
    """Test cases for ExtFileFilter Python bindings."""
    
    def setup_method(self):
        """Set up test configuration."""
        self.ExtFileFilter = uacalc_lib.io.ExtFileFilter

    def test_new_with_multiple_extensions(self):
        """Test creating ExtFileFilter with multiple extensions."""
        filter_obj = self.ExtFileFilter("UA Files", ["ua", "xml"])
        assert filter_obj.get_description() == "UA Files"
        extensions = filter_obj.get_extensions()
        assert "ua" in extensions
        assert "xml" in extensions
        assert len(extensions) == 2

    def test_new_with_single_extension(self):
        """Test creating ExtFileFilter with single extension."""
        filter_obj = self.ExtFileFilter("Text Files", ["txt"])
        assert filter_obj.get_description() == "Text Files"
        extensions = filter_obj.get_extensions()
        assert extensions == ["txt"]

    def test_new_validation_empty_description(self):
        """Test that empty description raises ValueError."""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.ExtFileFilter("", ["txt"])

    def test_new_validation_empty_extensions(self):
        """Test that empty extensions list raises ValueError."""
        with pytest.raises(ValueError, match="Extensions list cannot be empty"):
            self.ExtFileFilter("Test", [])

    def test_accept_file_with_extension(self):
        """Test accepting files with matching extensions."""
        filter_obj = self.ExtFileFilter("UA Files", ["ua", "xml"])
        
        # Test with .ua file
        assert filter_obj.accept("example.ua") is True
        
        # Test with .xml file
        assert filter_obj.accept("example.xml") is True
        
        # Test with .txt file (should be rejected)
        assert filter_obj.accept("example.txt") is False

    def test_accept_directory(self):
        """Test that directories are always accepted."""
        filter_obj = self.ExtFileFilter("UA Files", ["ua"])
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            assert filter_obj.accept(temp_dir) is True

    def test_accept_file_without_extension(self):
        """Test accepting files without extensions."""
        filter_obj = self.ExtFileFilter("UA Files", ["ua"])
        
        # File without extension should be rejected
        assert filter_obj.accept("noextension") is False

    def test_get_extension_with_extension(self):
        """Test getting extension from files with extensions."""
        # Test with .ua file
        ext = self.ExtFileFilter.get_extension("example.ua")
        assert ext == "ua"
        
        # Test with .xml file
        ext = self.ExtFileFilter.get_extension("example.xml")
        assert ext == "xml"
        
        # Test with multiple dots
        ext = self.ExtFileFilter.get_extension("example.backup.ua")
        assert ext == "ua"

    def test_get_extension_without_extension(self):
        """Test getting extension from files without extensions."""
        ext = self.ExtFileFilter.get_extension("noextension")
        assert ext is None
        
        # Test with file starting with dot
        ext = self.ExtFileFilter.get_extension(".hidden")
        assert ext is None
        
        # Test with file ending with dot
        ext = self.ExtFileFilter.get_extension("file.")
        assert ext is None

    def test_split_off_extension_with_extension(self):
        """Test splitting filename and extension."""
        name, ext = self.ExtFileFilter.split_off_extension("example.ua")
        assert name == "example"
        assert ext == "ua"
        
        # Test with multiple dots
        name, ext = self.ExtFileFilter.split_off_extension("example.backup.ua")
        assert name == "example.backup"
        assert ext == "ua"

    def test_split_off_extension_without_extension(self):
        """Test splitting filename without extension."""
        name, ext = self.ExtFileFilter.split_off_extension("noextension")
        assert name is None
        assert ext is None
        
        # Test with file starting with dot
        name, ext = self.ExtFileFilter.split_off_extension(".hidden")
        assert name is None
        assert ext is None
        
        # Test with file ending with dot
        name, ext = self.ExtFileFilter.split_off_extension("file.")
        assert name is None
        assert ext is None

    def test_string_representation(self):
        """Test string representation of ExtFileFilter."""
        filter_obj = self.ExtFileFilter("UA Files", ["ua"])
        assert str(filter_obj) == "ExtFileFilter(UA Files)"
        assert repr(filter_obj) == "ExtFileFilter('UA Files')"

    def test_equality(self):
        """Test equality comparison between ExtFileFilter instances."""
        filter1 = self.ExtFileFilter("UA Files", ["ua", "xml"])
        filter2 = self.ExtFileFilter("UA Files", ["ua", "xml"])
        filter3 = self.ExtFileFilter("UA Files", ["ua"])
        filter4 = self.ExtFileFilter("Text Files", ["ua", "xml"])
        
        assert filter1 == filter2
        assert filter1 != filter3
        assert filter1 != filter4

    def test_hash(self):
        """Test hash function for ExtFileFilter instances."""
        filter1 = self.ExtFileFilter("UA Files", ["ua", "xml"])
        filter2 = self.ExtFileFilter("UA Files", ["ua", "xml"])
        filter3 = self.ExtFileFilter("UA Files", ["ua"])
        
        # Equal objects should have equal hashes
        assert hash(filter1) == hash(filter2)
        
        # Different objects should have different hashes (likely)
        assert hash(filter1) != hash(filter3)

    def test_case_sensitivity(self):
        """Test that extension matching is case sensitive."""
        filter_obj = self.ExtFileFilter("UA Files", ["ua"])
        
        # Should accept exact case
        assert filter_obj.accept("example.ua") is True
        
        # Should reject different case
        assert filter_obj.accept("example.UA") is False
        assert filter_obj.accept("example.Ua") is False

    def test_multiple_extensions_in_filter(self):
        """Test filter with many extensions."""
        extensions = ["ua", "xml", "alg", "uac", "csv", "txt"]
        filter_obj = self.ExtFileFilter("All Files", extensions)
        
        for ext in extensions:
            assert filter_obj.accept(f"example.{ext}") is True
        
        # Test rejection
        assert filter_obj.accept("example.unknown") is False

    def test_path_with_directories(self):
        """Test that path components don't affect extension detection."""
        filter_obj = self.ExtFileFilter("UA Files", ["ua"])
        
        # Should work with paths containing directories
        assert filter_obj.accept("/path/to/example.ua") is True
        assert filter_obj.accept("subdir/example.ua") is True
        assert filter_obj.accept("example.ua") is True
        
        # Should reject non-matching extensions even in paths
        assert filter_obj.accept("/path/to/example.txt") is False


if __name__ == "__main__":
    pytest.main([__file__])
