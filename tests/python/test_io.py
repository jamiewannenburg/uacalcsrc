"""
Tests for UACalc I/O functionality.

This module tests the loading and saving of .ua files with comprehensive
validation and error handling.
"""

import pytest
import tempfile
import os
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

from uacalc import (
    load_algebra, save_algebra, validate_ua_file, list_ua_files, 
    get_algebra_info, create_algebra, create_operation
)
from uacalc.errors import (
    BadUAFileError, InvalidOperationTableError, UnsupportedAlgebraTypeError,
    XMLParsingError, FileFormatError
)


class TestBasicFileOperations:
    """Test basic file operations."""
    
    def test_load_valid_ua_file(self):
        """Test loading a valid .ua file."""
        # Create a simple test algebra
        algebra = create_algebra("test", [0, 1])
        op = create_operation("test_op", 1, [[0, 1], [1, 0]])
        algebra.add_operation("test_op", op)
        
        # Save and reload
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            loaded_algebra = load_algebra(temp_path)
            
            assert loaded_algebra.name == "test"
            assert loaded_algebra.cardinality() == 2
            assert len(loaded_algebra.operations()) == 1
            
            loaded_op = loaded_algebra.get_operation("test_op")
            assert loaded_op.arity() == 1
            assert loaded_op.value([0]) == 1
            assert loaded_op.value([1]) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_load_nonexistent_file(self):
        """Test loading a non-existent file."""
        with pytest.raises(BadUAFileError) as exc_info:
            load_algebra("nonexistent.ua")
        
        assert "File not found" in str(exc_info.value)
        assert exc_info.value.file_path == "nonexistent.ua"
    
    def test_load_wrong_extension(self):
        """Test loading a file with wrong extension."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(FileFormatError) as exc_info:
                load_algebra(temp_path)
            
            assert "must have .ua extension" in str(exc_info.value)
            assert exc_info.value.expected_format == ".ua"
            assert exc_info.value.actual_format == ".txt"
            
        finally:
            os.unlink(temp_path)
    
    def test_round_trip_compatibility(self):
        """Test round-trip save and load produces equivalent algebra."""
        # Create a more complex algebra
        algebra = create_algebra("complex_test", [0, 1, 2])
        
        # Add binary operation
        binary_op = create_operation("binary", 2, [
            [0, 0, 0], [0, 1, 1], [0, 2, 2],
            [1, 0, 1], [1, 1, 1], [1, 2, 2],
            [2, 0, 2], [2, 1, 2], [2, 2, 2]
        ])
        algebra.add_operation("binary", binary_op)
        
        # Add unary operation
        unary_op = create_operation("unary", 1, [[0, 2], [1, 1], [2, 0]])
        algebra.add_operation("unary", unary_op)
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            loaded_algebra = load_algebra(temp_path)
            
            # Check basic properties
            assert loaded_algebra.name == algebra.name
            assert loaded_algebra.cardinality() == algebra.cardinality()
            assert len(loaded_algebra.operations()) == len(algebra.operations())
            
            # Check operations
            for op_name in ["binary", "unary"]:
                original_op = algebra.get_operation(op_name)
                loaded_op = loaded_algebra.get_operation(op_name)
                
                assert loaded_op.arity() == original_op.arity()
                
                # Test some values
                if op_name == "binary":
                    assert loaded_op.value([0, 1]) == original_op.value([0, 1])
                    assert loaded_op.value([1, 2]) == original_op.value([1, 2])
                else:  # unary
                    assert loaded_op.value([0]) == original_op.value([0])
                    assert loaded_op.value([2]) == original_op.value([2])
                    
        finally:
            os.unlink(temp_path)


class TestXMLParsing:
    """Test XML parsing functionality."""
    
    def test_parse_basic_algebra_structure(self):
        """Test parsing of basic algebra XML structure."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <desc>Test algebra</desc>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>test_op</opName>
          <arity>1</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">1</row>
            <row r="[1]">0</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            algebra = load_algebra(temp_path)
            
            assert algebra.name == "test"
            assert algebra.cardinality == 2
            
            # Get the first operation
            operations = list(algebra.operations())
            assert len(operations) == 1
            op = operations[0]
            assert op.arity() == 1
            assert op.value([0]) == 1
            assert op.value([1]) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_malformed_xml(self):
        """Test handling of malformed XML."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>test_op</opName>
          <arity>1</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">1</row>
            <row r="[1]">0</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
<!-- Missing closing tag -->'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            with pytest.raises(XMLParsingError) as exc_info:
                load_algebra(temp_path)
            
            assert "XML parsing error" in str(exc_info.value)
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_unsupported_algebra_type(self):
        """Test handling of unsupported algebra types."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <productAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
  </productAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            with pytest.raises(UnsupportedAlgebraTypeError) as exc_info:
                load_algebra(temp_path)
            
            assert "productAlgebra" in str(exc_info.value)
            assert exc_info.value.algebra_type == "productAlgebra"
            assert "basicAlgebra" in exc_info.value.supported_types
            
        finally:
            os.unlink(temp_path)


class TestOperationTableParsing:
    """Test operation table parsing."""
    
    def test_parse_unary_operation(self):
        """Test parsing of unary operation table."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>3</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>unary</opName>
          <arity>1</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">2</row>
            <row r="[1]">1</row>
            <row r="[2]">0</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            algebra = load_algebra(temp_path)
            op = algebra.get_operation("unary")
            
            assert op.arity() == 1
            assert op.value([0]) == 2
            assert op.value([1]) == 1
            assert op.value([2]) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_binary_operation(self):
        """Test parsing of binary operation table."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>binary</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1</row>
            <row r="[1]">1,1</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            algebra = load_algebra(temp_path)
            op = algebra.get_operation("binary")
            
            assert op.arity() == 2
            assert op.value([0, 0]) == 0
            assert op.value([0, 1]) == 1
            assert op.value([1, 0]) == 1
            assert op.value([1, 1]) == 1
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_invalid_table_size(self):
        """Test handling of invalid table size."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>binary</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1</row>
            <row r="[1]">1,1</row>
            <row r="[2]">2,2</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            with pytest.raises(InvalidOperationTableError) as exc_info:
                load_algebra(temp_path)
            
            assert "wrong number of rows" in str(exc_info.value)
            assert exc_info.value.expected_size == 4  # 2^2
            assert exc_info.value.actual_size == 3
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_invalid_values(self):
        """Test handling of invalid values in table."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>unary</opName>
          <arity>1</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">2</row>
            <row r="[1]">0</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            with pytest.raises(InvalidOperationTableError) as exc_info:
                load_algebra(temp_path)
            
            assert "outside universe range" in str(exc_info.value)
            
        finally:
            os.unlink(temp_path)


class TestXMLGeneration:
    """Test XML generation functionality."""
    
    def test_generate_basic_algebra_xml(self):
        """Test generation of basic algebra XML."""
        algebra = create_algebra("test", [0, 1])
        op = create_operation("test_op", 1, [[0, 1], [1, 0]])
        algebra.add_operation("test_op", op)
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            
            # Read the generated XML
            with open(temp_path, 'r') as f:
                content = f.read()
            
            # Check XML structure
            assert '<?xml version="1.0"?>' in content
            assert '<algebra>' in content
            assert '<basicAlgebra>' in content
            assert '<algName>test</algName>' in content
            assert '<cardinality>2</cardinality>' in content
            assert '<operations>' in content
            assert '<op>' in content
            assert '<opSymbol>' in content
            assert '<opName>test_op</opName>' in content
            assert '<arity>1</arity>' in content
            assert '<opTable>' in content
            assert '<intArray>' in content
            assert '<row r="[0]">1</row>' in content
            assert '<row r="[1]">0</row>' in content
            
        finally:
            os.unlink(temp_path)
    
    def test_generate_binary_operation_xml(self):
        """Test generation of binary operation XML."""
        algebra = create_algebra("test", [0, 1])
        op = create_operation("binary", 2, [
            [0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1]
        ])
        algebra.add_operation("binary", op)
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            
            # Read the generated XML
            with open(temp_path, 'r') as f:
                content = f.read()
            
            # Check binary operation structure
            assert '<row r="[0]">0,1</row>' in content
            assert '<row r="[1]">1,1</row>' in content
            
        finally:
            os.unlink(temp_path)
    
    def test_xml_indentation(self):
        """Test XML indentation and formatting."""
        algebra = create_algebra("test", [0, 1])
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            
            # Read the generated XML
            with open(temp_path, 'r') as f:
                lines = f.readlines()
            
            # Check indentation
            assert lines[0].strip() == '<?xml version="1.0"?>'
            assert lines[1].strip() == '<algebra>'
            assert lines[2].strip() == '<basicAlgebra>'
            assert lines[2].startswith('  ')  # Should be indented
            
        finally:
            os.unlink(temp_path)


class TestValidation:
    """Test validation functionality."""
    
    def test_validate_valid_file(self):
        """Test validation of valid file."""
        algebra = create_algebra("test", [0, 1])
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            is_valid, errors = validate_ua_file(temp_path)
            
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_validate_invalid_file(self):
        """Test validation of invalid file."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <!-- Missing cardinality -->
    <operations>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            assert any("Missing <cardinality> element" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_validate_malformed_xml(self):
        """Test validation of malformed XML."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <!-- Missing closing tag -->
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            assert any("XML parsing error" in error for error in errors)
            
        finally:
            os.unlink(temp_path)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_list_ua_files(self):
        """Test listing .ua files in directory."""
        # Create temporary directory with some .ua files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create some .ua files
            (temp_path / "test1.ua").write_text("test content")
            (temp_path / "test2.ua").write_text("test content")
            (temp_path / "test.txt").write_text("test content")  # Should be ignored
            
            files = list_ua_files(temp_path)
            
            assert len(files) == 2
            assert any(f.name == "test1.ua" for f in files)
            assert any(f.name == "test2.ua" for f in files)
            assert not any(f.name == "test.txt" for f in files)
    
    def test_get_algebra_info(self):
        """Test getting algebra information."""
        algebra = create_algebra("test", [0, 1])
        op = create_operation("test_op", 1, [[0, 1], [1, 0]])
        algebra.add_operation("test_op", op)
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            info = get_algebra_info(temp_path)
            
            assert info['file_path'] == temp_path
            assert info['valid'] == True
            assert info['name'] == "test"
            assert info['cardinality'] == 2
            assert info['operation_count'] == 1
            assert info['file_size'] > 0
            
        finally:
            os.unlink(temp_path)
    
    def test_get_algebra_info_invalid_file(self):
        """Test getting info for invalid file."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <!-- Missing cardinality -->
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            info = get_algebra_info(temp_path)
            
            assert info['file_path'] == temp_path
            assert info['valid'] == False
            assert info['name'] == "test"
            assert len(info['errors']) > 0
            
        finally:
            os.unlink(temp_path)


class TestErrorHandling:
    """Test error handling."""
    
    def test_specific_error_types(self):
        """Test specific error types for different failure modes."""
        # Test file not found
        with pytest.raises(BadUAFileError) as exc_info:
            load_algebra("nonexistent.ua")
        assert exc_info.value.file_path == "nonexistent.ua"
        
        # Test wrong extension
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(FileFormatError) as exc_info:
                load_algebra(temp_path)
            assert exc_info.value.expected_format == ".ua"
            assert exc_info.value.actual_format == ".txt"
        finally:
            os.unlink(temp_path)
    
    def test_error_message_quality(self):
        """Test error message quality and helpfulness."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>test_op</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1,2</row>
            <row r="[1]">1,1</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            with pytest.raises(InvalidOperationTableError) as exc_info:
                load_algebra(temp_path)
            
            error_msg = str(exc_info.value)
            assert "test_op" in error_msg
            assert "wrong size" in error_msg
            assert exc_info.value.operation_name == "test_op"
            assert exc_info.value.row_index == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_graceful_edge_cases(self):
        """Test graceful handling of edge cases."""
        # Test empty operations
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            algebra = load_algebra(temp_path)
            assert algebra.name == "test"
            assert algebra.cardinality() == 2
            assert len(algebra.operations()) == 0
            
        finally:
            os.unlink(temp_path)
