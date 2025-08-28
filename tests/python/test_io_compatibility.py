"""
Tests for Java UACalc compatibility.

This module tests round-trip compatibility with Java UACalc .ua files
and specific algebra examples from the resources directory.
"""

import pytest
import tempfile
import os
from pathlib import Path

from uacalc import (
    load_algebra, save_algebra, create_algebra, create_operation
)
from uacalc.errors import (
    BadUAFileError, InvalidOperationTableError, UnsupportedAlgebraTypeError, XMLParsingError
)


class TestRoundTripCompatibility:
    """Test round-trip compatibility with Java UACalc."""
    
    def test_load_sample_ua_files(self):
        """Test loading all sample .ua files from resources directory."""
        resources_dir = Path("resources/algebras")
        
        if not resources_dir.exists():
            pytest.skip("Resources directory not found")
        
        # Test loading each .ua file
        for ua_file in resources_dir.glob("*.ua"):
            try:
                algebra = load_algebra(ua_file)
                
                # Basic validation
                assert algebra.name is not None
                assert algebra.cardinality > 0
                assert len(algebra.universe) == algebra.cardinality
                
                # Check that universe is contiguous
                expected_universe = list(range(algebra.cardinality))
                assert algebra.universe == expected_universe
                
                # Check operations
                for operation in algebra.operations():
                    assert operation.symbol is not None
                    assert operation.arity() >= 0
                    
                    # Test operation evaluation for some inputs
                    if operation.arity() == 0:
                        # Constant operation
                        result = operation.value([])
                        assert 0 <= result < algebra.cardinality
                    elif operation.arity() == 1:
                        # Unary operation
                        for i in range(algebra.cardinality):
                            result = operation.value([i])
                            assert 0 <= result < algebra.cardinality
                    elif operation.arity() == 2:
                        # Binary operation - test a few combinations
                        for i in range(min(3, algebra.cardinality)):
                            for j in range(min(3, algebra.cardinality)):
                                result = operation.value([i, j])
                                assert 0 <= result < algebra.cardinality
                
            except Exception as e:
                pytest.fail(f"Failed to load {ua_file}: {e}")
    
    def test_save_and_reload_equivalence(self):
        """Test that save and reload produces equivalent algebra."""
        resources_dir = Path("resources/algebras")
        
        if not resources_dir.exists():
            pytest.skip("Resources directory not found")
        
        # Test with a few sample files
        test_files = ["m3.ua", "lat2.ua"]
        
        for filename in test_files:
            ua_file = resources_dir / filename
            if not ua_file.exists():
                continue
            
            try:
                # Load original algebra
                original_algebra = load_algebra(ua_file)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
                    temp_path = f.name
                
                try:
                    save_algebra(original_algebra, temp_path)
                    
                    # Load the saved file
                    reloaded_algebra = load_algebra(temp_path)
                    
                    # Compare basic properties
                    assert reloaded_algebra.name == original_algebra.name
                    assert reloaded_algebra.cardinality == original_algebra.cardinality
                    assert len(reloaded_algebra.operations()) == len(original_algebra.operations())
                    
                    # Compare operations
                    for op_name in [op.symbol for op in original_algebra.operations()]:
                        original_op = original_algebra.operation_by_symbol(op_name)
                        reloaded_op = reloaded_algebra.operation_by_symbol(op_name)
                        
                        assert reloaded_op.arity() == original_op.arity()
                        
                        # Test operation values
                        if original_op.arity() == 0:
                            assert reloaded_op.value([]) == original_op.value([])
                        elif original_op.arity() == 1:
                            for i in range(original_algebra.cardinality):
                                assert reloaded_op.value([i]) == original_op.value([i])
                        elif original_op.arity() == 2:
                            for i in range(original_algebra.cardinality):
                                for j in range(original_algebra.cardinality):
                                    assert reloaded_op.value([i, j]) == original_op.value([i, j])
                
                finally:
                    os.unlink(temp_path)
                    
            except Exception as e:
                pytest.fail(f"Round-trip test failed for {filename}: {e}")


class TestSpecificAlgebraExamples:
    """Test specific algebra examples from resources."""
    
    def test_m3_ua_diamond_lattice(self):
        """Test m3.ua (diamond lattice) - 5 elements, 2 binary operations."""
        resources_dir = Path("resources/algebras")
        m3_file = resources_dir / "m3.ua"
        
        if not m3_file.exists():
            pytest.skip("m3.ua file not found")
        
        algebra = load_algebra(m3_file)
        
        # Check basic properties
        assert algebra.name == "m3"
        assert algebra.cardinality == 5
        assert len(algebra.operations()) == 2
        
        # Check operations
        meet_op = algebra.operation_by_symbol("meet")
        join_op = algebra.operation_by_symbol("join")
        
        assert meet_op.arity() == 2
        assert join_op.arity() == 2
        
        # Test some meet operation values (diamond lattice)
        assert meet_op.value([0, 0]) == 0  # bottom meet bottom = bottom
        assert meet_op.value([0, 1]) == 0  # bottom meet element = bottom
        assert meet_op.value([1, 2]) == 0  # meet of incomparable elements = bottom
        assert meet_op.value([1, 4]) == 1  # element meet top = element
        assert meet_op.value([4, 4]) == 4  # top meet top = top
        
        # Test some join operation values
        assert join_op.value([0, 0]) == 0  # bottom join bottom = bottom
        assert join_op.value([0, 1]) == 1  # bottom join element = element
        assert join_op.value([1, 2]) == 4  # join of incomparable elements = top
        assert join_op.value([1, 4]) == 4  # element join top = top
        assert join_op.value([4, 4]) == 4  # top join top = top
    
    def test_lat2_ua_two_element_lattice(self):
        """Test lat2.ua (2-element lattice) - 2 elements, 2 binary operations."""
        resources_dir = Path("resources/algebras")
        lat2_file = resources_dir / "lat2.ua"
        
        if not lat2_file.exists():
            pytest.skip("lat2.ua file not found")
        
        algebra = load_algebra(lat2_file)
        
        # Check basic properties
        assert algebra.name == "lat2"
        assert algebra.cardinality == 2
        assert len(algebra.operations()) == 2
        
        # Check operations
        meet_op = algebra.operation_by_symbol("meet")
        join_op = algebra.operation_by_symbol("join")
        
        assert meet_op.arity() == 2
        assert join_op.arity() == 2
        
        # Test meet operation (2-element lattice)
        assert meet_op.value([0, 0]) == 0  # 0 ∧ 0 = 0
        assert meet_op.value([0, 1]) == 0  # 0 ∧ 1 = 0
        assert meet_op.value([1, 0]) == 0  # 1 ∧ 0 = 0
        assert meet_op.value([1, 1]) == 1  # 1 ∧ 1 = 1
        
        # Test join operation
        assert join_op.value([0, 0]) == 0  # 0 ∨ 0 = 0
        assert join_op.value([0, 1]) == 1  # 0 ∨ 1 = 1
        assert join_op.value([1, 0]) == 1  # 1 ∨ 0 = 1
        assert join_op.value([1, 1]) == 1  # 1 ∨ 1 = 1
    
    def test_verify_operation_table_values(self):
        """Verify operation table values match expected results."""
        resources_dir = Path("resources/algebras")
        
        # Test with m3.ua
        m3_file = resources_dir / "m3.ua"
        if m3_file.exists():
            algebra = load_algebra(m3_file)
            meet_op = algebra.operation_by_symbol("meet")
            
            # Verify specific table values from m3.ua
            # Row 0: 0,0,0,0,0
            assert meet_op.value([0, 0]) == 0
            assert meet_op.value([0, 1]) == 0
            assert meet_op.value([0, 2]) == 0
            assert meet_op.value([0, 3]) == 0
            assert meet_op.value([0, 4]) == 0
            
            # Row 1: 0,1,0,0,1
            assert meet_op.value([1, 0]) == 0
            assert meet_op.value([1, 1]) == 1
            assert meet_op.value([1, 2]) == 0
            assert meet_op.value([1, 3]) == 0
            assert meet_op.value([1, 4]) == 1
            
            # Row 4: 0,1,2,3,4 (diagonal)
            assert meet_op.value([4, 0]) == 0
            assert meet_op.value([4, 1]) == 1
            assert meet_op.value([4, 2]) == 2
            assert meet_op.value([4, 3]) == 3
            assert meet_op.value([4, 4]) == 4


class TestMetadataPreservation:
    """Test metadata preservation through round-trip."""
    
    def test_algebra_name_preservation(self):
        """Test that algebra names are preserved exactly."""
        resources_dir = Path("resources/algebras")
        
        if not resources_dir.exists():
            pytest.skip("Resources directory not found")
        
        for ua_file in resources_dir.glob("*.ua"):
            try:
                original_algebra = load_algebra(ua_file)
                original_name = original_algebra.name
                
                # Save and reload
                with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
                    temp_path = f.name
                
                try:
                    save_algebra(original_algebra, temp_path)
                    reloaded_algebra = load_algebra(temp_path)
                    
                    assert reloaded_algebra.name == original_name
                    
                finally:
                    os.unlink(temp_path)
                    
            except Exception as e:
                pytest.fail(f"Name preservation test failed for {ua_file.name}: {e}")
    
    def test_operation_symbol_preservation(self):
        """Test that operation symbols are preserved exactly."""
        resources_dir = Path("resources/algebras")
        
        if not resources_dir.exists():
            pytest.skip("Resources directory not found")
        
        for ua_file in resources_dir.glob("*.ua"):
            try:
                original_algebra = load_algebra(ua_file)
                original_symbols = [op.symbol for op in original_algebra.operations()]
                
                # Save and reload
                with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
                    temp_path = f.name
                
                try:
                    save_algebra(original_algebra, temp_path)
                    reloaded_algebra = load_algebra(temp_path)
                    reloaded_symbols = [op.symbol for op in reloaded_algebra.operations()]
                    
                    assert reloaded_symbols == original_symbols
                    
                finally:
                    os.unlink(temp_path)
                    
            except Exception as e:
                pytest.fail(f"Symbol preservation test failed for {ua_file.name}: {e}")


class TestXMLFormatCompliance:
    """Test XML format compliance with Java UACalc."""
    
    def test_xml_declaration_presence(self):
        """Test that generated XML has proper declaration."""
        algebra = create_algebra("test", [0, 1])
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            
            with open(temp_path, 'r') as f:
                content = f.read()
            
            assert content.startswith('<?xml version="1.0"?>')
            
        finally:
            os.unlink(temp_path)
    
    def test_element_ordering(self):
        """Test that element ordering matches Java convention."""
        algebra = create_algebra("test", [0, 1])
        op = create_operation("test_op", 1, [[0, 1], [1, 0]])
        algebra.add_operation("test_op", op)
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            
            with open(temp_path, 'r') as f:
                content = f.read()
            
            # Check element order: algName, desc, cardinality, operations
            alg_name_pos = content.find('<algName>')
            cardinality_pos = content.find('<cardinality>')
            operations_pos = content.find('<operations>')
            
            assert alg_name_pos < cardinality_pos
            assert cardinality_pos < operations_pos
            
        finally:
            os.unlink(temp_path)
    
    def test_row_attribute_formatting(self):
        """Test that row attributes are formatted correctly."""
        algebra = create_algebra("test", [0, 1])
        op = create_operation("binary", 2, [
            [0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1]
        ])
        algebra.add_operation("binary", op)
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            
            with open(temp_path, 'r') as f:
                content = f.read()
            
            # Check row attribute format
            assert 'r="[0]"' in content
            assert 'r="[1]"' in content
            
        finally:
            os.unlink(temp_path)
    
    def test_whitespace_and_indentation(self):
        """Test whitespace and indentation formatting."""
        algebra = create_algebra("test", [0, 1])
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            
            with open(temp_path, 'r') as f:
                lines = f.readlines()
            
            # Check indentation
            assert lines[0].strip() == '<?xml version="1.0"?>'
            assert lines[1].strip() == '<algebra>'
            assert lines[2].strip() == '<basicAlgebra>'
            assert lines[2].startswith('  ')  # Should be indented
            
            # Check no excessive whitespace
            for line in lines:
                if line.strip():
                    assert not line.startswith('      ')  # No excessive indentation (more than 4 spaces)
                    
        finally:
            os.unlink(temp_path)


class TestEdgeCases:
    """Test edge cases and unusual but valid .ua files."""
    
    def test_single_element_algebra(self):
        """Test algebra with 1 element (trivial algebra)."""
        algebra = create_algebra("trivial", [0])
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            loaded_algebra = load_algebra(temp_path)
            
            assert loaded_algebra.cardinality == 1
            assert loaded_algebra.universe == [0]
            
        finally:
            os.unlink(temp_path)
    
    def test_algebra_with_many_operations(self):
        """Test algebra with many operations."""
        algebra = create_algebra("many_ops", [0, 1])
        
        # Add multiple operations
        for i in range(5):
            op = create_operation(f"op_{i}", 1, [[0, 1], [1, 0]])
            algebra.add_operation(f"op_{i}", op)
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            loaded_algebra = load_algebra(temp_path)
            
            assert len(loaded_algebra.operations()) == 5
            for i in range(5):
                assert loaded_algebra.operation_by_symbol(f"op_{i}") is not None
                
        finally:
            os.unlink(temp_path)
    
    def test_constant_operations(self):
        """Test operations with arity 0 (constants)."""
        algebra = create_algebra("with_constants", [0, 1])
        
        # Add constant operation
        const_op = create_operation("constant", 0, [[1]])  # Always returns 1
        algebra.add_operation("constant", const_op)
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            loaded_algebra = load_algebra(temp_path)
            
            const_op = loaded_algebra.operation_by_symbol("constant")
            assert const_op.arity() == 0
            assert const_op.value([]) == 1
            
        finally:
            os.unlink(temp_path)
    
    def test_high_arity_operations(self):
        """Test operations with high arity (ternary, quaternary)."""
        algebra = create_algebra("high_arity", [0, 1])
        
        # Add ternary operation
        ternary_op = create_operation("ternary", 3, [
            [0, 0, 0, 0], [0, 0, 1, 1], [0, 1, 0, 1], [0, 1, 1, 0],
            [1, 0, 0, 1], [1, 0, 1, 0], [1, 1, 0, 0], [1, 1, 1, 1]
        ])
        algebra.add_operation("ternary", ternary_op)
        
        with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as f:
            temp_path = f.name
        
        try:
            save_algebra(algebra, temp_path)
            loaded_algebra = load_algebra(temp_path)
            
            ternary_op = loaded_algebra.operation_by_symbol("ternary")
            assert ternary_op.arity() == 3
            assert ternary_op.value([0, 0, 0]) == 0
            assert ternary_op.value([0, 0, 1]) == 1
            assert ternary_op.value([1, 1, 1]) == 1
            
        finally:
            os.unlink(temp_path)


class TestErrorCompatibility:
    """Test error handling compatibility."""
    
    def test_malformed_ua_files(self):
        """Test handling of malformed .ua files."""
        malformed_files = [
            # Missing closing tag
            '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
''',
            # Missing required element
            '''<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <!-- Missing cardinality -->
    <operations>
    </operations>
  </basicAlgebra>
</algebra>''',
            # Invalid table size
            '''<?xml version="1.0"?>
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
        ]
        
        for i, content in enumerate(malformed_files):
            with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
                f.write(content)
                temp_path = f.name
            
            try:
                with pytest.raises((BadUAFileError, InvalidOperationTableError, XMLParsingError)):
                    load_algebra(temp_path)
            finally:
                os.unlink(temp_path)
    
    def test_error_message_helpfulness(self):
        """Test that error messages are helpful and specific."""
        # Test missing cardinality
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
            with pytest.raises(BadUAFileError) as exc_info:
                load_algebra(temp_path)
            
            error_msg = str(exc_info.value)
            assert "Missing <cardinality> element" in error_msg
            assert temp_path in error_msg
            
        finally:
            os.unlink(temp_path)
