"""
Tests for UACalc I/O validation functionality.

This module tests comprehensive validation of .ua files including
XML structure, algebra metadata, operations, and operation tables.
"""

import pytest
import tempfile
import os
from pathlib import Path

from uacalc import (
    validate_ua_file, get_algebra_info, create_algebra, create_operation, save_algebra
)
from uacalc.errors import (
    BadUAFileError, InvalidOperationTableError, XMLParsingError
)


class TestXMLStructureValidation:
    """Test XML structure validation."""
    
    def test_valid_xml_structure(self):
        """Test validation of valid XML structure."""
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_missing_required_elements(self):
        """Test validation of files with missing required elements."""
        # Missing basicAlgebra
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <algName>test</algName>
  <cardinality>2</cardinality>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            assert any("No algebra type found" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_incorrect_element_nesting(self):
        """Test validation of files with incorrect element nesting."""
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
            <row>1,0</row>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            # This should be valid
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_unknown_elements(self):
        """Test validation of files with unknown elements."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <unknownElement>value</unknownElement>
    <operations>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            is_valid, errors = validate_ua_file(temp_path)
            
            # Unknown elements should not cause validation failure
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_malformed_xml_syntax(self):
        """Test validation of files with malformed XML syntax."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
    </operations>
  </basicAlgebra>
<!-- Missing closing tag -->
'''
        
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
    
    def test_incorrect_xml_encoding(self):
        """Test validation of files with incorrect XML encoding."""
        # Create file with non-UTF-8 encoding
        xml_content = '''<?xml version="1.0" encoding="ISO-8859-1"?>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            # Should still be valid
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)


class TestAlgebraMetadataValidation:
    """Test algebra metadata validation."""
    
    def test_valid_algebra_metadata(self):
        """Test validation of valid algebra metadata."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <desc>Test algebra description</desc>
    <cardinality>5</cardinality>
    <operations>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            is_valid, errors = validate_ua_file(temp_path)
            
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_missing_algebra_name(self):
        """Test validation of files with missing algebra name."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <cardinality>2</cardinality>
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
            assert any("Missing <algName> element" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_invalid_cardinality_values(self):
        """Test validation of files with invalid cardinality values."""
        test_cases = [
            ("0", "Cardinality must be positive"),
            ("-1", "Cardinality must be positive"),
            ("abc", "Invalid cardinality value"),
            ("", "Invalid cardinality value"),
        ]
        
        for cardinality_value, expected_error in test_cases:
            xml_content = f'''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>{cardinality_value}</cardinality>
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
                assert any(expected_error in error for error in errors)
                
            finally:
                os.unlink(temp_path)
    
    def test_extremely_large_cardinality(self):
        """Test validation of files with extremely large cardinality."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>1000000</cardinality>
    <operations>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            is_valid, errors = validate_ua_file(temp_path)
            
            # Should be valid but might be slow
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)


class TestOperationValidation:
    """Test operation validation."""
    
    def test_valid_operations(self):
        """Test validation of valid operations."""
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
            <row>1,0</row>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_missing_operation_names(self):
        """Test validation of operations with missing names."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            assert any("Missing <opName> element" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_missing_operation_arities(self):
        """Test validation of operations with missing arities."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>test_op</opName>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            assert any("Missing <arity> element" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_invalid_arity_values(self):
        """Test validation of operations with invalid arity values."""
        test_cases = [
            ("-1", "Arity must be non-negative"),
            ("abc", "Invalid arity value"),
            ("", "Invalid arity value"),
        ]
        
        for arity_value, expected_error in test_cases:
            xml_content = f'''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>test_op</opName>
          <arity>{arity_value}</arity>
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
                is_valid, errors = validate_ua_file(temp_path)
                
                assert not is_valid
                assert len(errors) > 0
                assert any(expected_error in error for error in errors)
                
            finally:
                os.unlink(temp_path)


class TestOperationTableValidation:
    """Test operation table validation."""
    
    def test_valid_operation_tables(self):
        """Test validation of valid operation tables."""
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_missing_int_array_element(self):
        """Test validation of tables with missing intArray element."""
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
        </opTable>
      </op>
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
            assert any("Missing <intArray> element" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_wrong_number_of_rows(self):
        """Test validation of tables with wrong number of rows."""
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
            <row r="[2]">2</row>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            assert any("wrong number of rows" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_wrong_number_of_columns(self):
        """Test validation of tables with wrong number of columns."""
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            assert any("invalid values" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_non_integer_values(self):
        """Test validation of tables with non-integer values."""
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
            <row>abc,0</row>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            assert any("contains invalid values" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_missing_comma_separators(self):
        """Test validation of tables with missing comma separators."""
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
            <row r="[0]">0 1</row>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            assert any("contains invalid values" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_extra_whitespace(self):
        """Test validation of tables with extra whitespace."""
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
            <row r="[0]"> 0 , 1 </row>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            # Should be valid - whitespace should be handled
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)


class TestRowAttributeValidation:
    """Test row attribute validation."""
    
    def test_valid_row_attributes(self):
        """Test validation of valid row attributes."""
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_malformed_row_attributes(self):
        """Test validation of malformed row attributes."""
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
            <row r="0">0,1</row>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            # Should still be valid - malformed attributes are not critical
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_incorrect_argument_counts(self):
        """Test validation of row attributes with incorrect argument counts."""
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
            <row r="[0,1]">0,1</row>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            # Should still be valid - attribute errors are not critical
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)


class TestUniverseValidation:
    """Test universe validation."""
    
    def test_contiguous_universe(self):
        """Test validation of algebras with contiguous universes."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>3</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>test_op</opName>
          <arity>1</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row>1,2,0</row>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert is_valid
            assert len(errors) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_values_outside_universe(self):
        """Test validation of operation values outside universe range."""
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
            <row>2,0</row>
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            assert any("contains invalid values" in error for error in errors)
            
        finally:
            os.unlink(temp_path)


class TestValidationErrorReporting:
    """Test validation error reporting."""
    
    def test_multiple_errors_reported(self):
        """Test that multiple validation errors are reported together."""
        xml_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <!-- Missing algName -->
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <!-- Missing opName -->
          <arity>1</arity>
        </opSymbol>
        <opTable>
          <!-- Missing intArray -->
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>'''
        
        with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) >= 3  # Should have multiple errors
            assert any("Missing <algName> element" in error for error in errors)
            assert any("Missing <opName> element" in error for error in errors)
            assert any("Missing <intArray> element" in error for error in errors)
            
        finally:
            os.unlink(temp_path)
    
    def test_error_message_clarity(self):
        """Test that error messages are clear and actionable."""
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
            is_valid, errors = validate_ua_file(temp_path)
            
            assert not is_valid
            assert len(errors) > 0
            
            # Check for specific error details
            for error in errors:
                assert "test_op" in error or "wrong number of rows" in error
                
        finally:
            os.unlink(temp_path)


class TestValidationPerformance:
    """Test validation performance."""
    
    def test_validation_speed(self):
        """Test validation speed on large files."""
        # Create a large algebra
        algebra = create_algebra("large_test", list(range(10)))
        
        # Add multiple operations
        for i in range(5):
            op = create_operation(f"op_{i}", 2, [
                [i, j, (i + j) % 10] for i in range(10) for j in range(10)
            ])
            algebra.add_operation(f"op_{i}", op)
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            
            # Time validation
            import time
            start_time = time.time()
            is_valid, errors = validate_ua_file(temp_path)
            end_time = time.time()
            
            assert is_valid
            assert len(errors) == 0
            assert end_time - start_time < 1.0  # Should complete within 1 second
            
        finally:
            os.unlink(temp_path)
    
    def test_validation_many_files(self):
        """Test validation of many files in batch."""
        # Create multiple test files
        temp_files = []
        
        try:
            for i in range(5):
                algebra = create_algebra(f"test_{i}", list(range(3)))
                op = create_operation("test_op", 1, [[0, 1], [1, 2], [2, 0]])
                algebra.add_operation("test_op", op)
                
                with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
                    temp_path = f.name
                    temp_files.append(temp_path)
                
                save_algebra(algebra, temp_path)
            
            # Validate all files
            import time
            start_time = time.time()
            
            for temp_path in temp_files:
                is_valid, errors = validate_ua_file(temp_path)
                assert is_valid
                assert len(errors) == 0
            
            end_time = time.time()
            assert end_time - start_time < 2.0  # Should complete within 2 seconds
            
        finally:
            for temp_path in temp_files:
                os.unlink(temp_path)


class TestValidationUtilityFunctions:
    """Test validation utility functions."""
    
    def test_get_algebra_info_valid_file(self):
        """Test get_algebra_info with valid file."""
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
            assert len(info['errors']) == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_get_algebra_info_invalid_file(self):
        """Test get_algebra_info with invalid file."""
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
            info = get_algebra_info(temp_path)
            
            assert info['file_path'] == temp_path
            assert info['valid'] == False
            assert info['name'] == "test"
            assert len(info['errors']) > 0
            assert any("Missing <cardinality> element" in error for error in info['errors'])
            
        finally:
            os.unlink(temp_path)
    
    def test_validation_integration(self):
        """Test validation integration with file listing."""
        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create valid file
            algebra = create_algebra("valid", [0, 1])
            valid_file = temp_path / "valid.ua"
            save_algebra(algebra, valid_file)
            
            # Create invalid file
            invalid_content = '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>invalid</algName>
    <!-- Missing cardinality -->
  </basicAlgebra>
</algebra>'''
            invalid_file = temp_path / "invalid.ua"
            invalid_file.write_text(invalid_content)
            
            # Test validation of all files
            from uacalc import list_ua_files
            ua_files = list_ua_files(temp_path)
            
            assert len(ua_files) == 2
            
            valid_count = 0
            invalid_count = 0
            
            for ua_file in ua_files:
                is_valid, errors = validate_ua_file(ua_file)
                if is_valid:
                    valid_count += 1
                else:
                    invalid_count += 1
            
            assert valid_count == 1
            assert invalid_count == 1
