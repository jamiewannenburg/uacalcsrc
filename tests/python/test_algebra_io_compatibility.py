#!/usr/bin/env python3
"""
AlgebraIO Compatibility Test

This module tests the org.uacalc.io.AlgebraIO class compatibility between
Java UACalc and the Rust/Python implementation. It verifies that I/O operations
for file reading, writing, and validation work identically.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from tests.python.base_compatibility_test import BaseCompatibilityTest

logger = logging.getLogger(__name__)


class AlgebraIOCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.io.AlgebraIO class compatibility.
    
    This class tests the AlgebraIO implementation to ensure
    the Rust implementation matches Java behavior exactly for:
    - AlgebraIO static methods for file operations
    - Round-trip file operations preserve all data
    - File format validation and error detection
    """
    
    def test_algebra_io_read_compatibility(self):
        """Test AlgebraIO.readAlgebraFile produces identical results"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files:
            with self.subTest(file=ua_file.name):
                # I/O operations are not computationally expensive, so don't skip based on file size
                # if self._should_skip_test(ua_file.stat().st_size, "algebra_io_read"):
                #     self.skipTest(f"Skipping large file {ua_file.name}")
                
                # Test Java operation
                java_result = self._run_java_operation(
                    "algebra_io_read", 
                    str(ua_file)
                )
                
                # Test Rust operation (load_algebra)
                try:
                    import uacalc
                    rust_algebra = uacalc.load_algebra(str(ua_file))
                    
                    rust_result = {
                        "success": True,
                        "operation": "algebra_io_read",
                        "input_file": str(ua_file),
                        "algebra_name": rust_algebra.name,
                        "cardinality": rust_algebra.cardinality,
                        "operation_count": len(rust_algebra.operations())
                    }
                except Exception as e:
                    rust_result = {
                        "success": False,
                        "operation": "algebra_io_read",
                        "input_file": str(ua_file),
                        "error": str(e)
                    }
                
                # Compare results
                self._compare_results(
                    java_result, 
                    rust_result, 
                    f"algebra_io_read_{ua_file.name}"
                )
    
    def test_algebra_io_write_compatibility(self):
        """Test AlgebraIO.writeAlgebraFile produces identical output"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files:
            with self.subTest(file=ua_file.name):
                # I/O operations are not computationally expensive, so don't skip based on file size
                # if self._should_skip_test(ua_file.stat().st_size, "algebra_io_write"):
                #     self.skipTest(f"Skipping large file {ua_file.name}")
                
                # Create temporary output files
                with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as java_temp:
                    java_output = java_temp.name
                with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as rust_temp:
                    rust_output = rust_temp.name
                
                try:
                    # Test Java operation
                    java_result = self._run_java_operation(
                        "algebra_io_write", 
                        str(ua_file),
                        java_output
                    )
                    
                    # Test Rust operation (save_algebra)
                    try:
                        import uacalc
                        rust_algebra = uacalc.load_algebra(str(ua_file))
                        uacalc.save_algebra(rust_algebra, rust_output)
                        
                        rust_result = {
                            "success": True,
                            "operation": "algebra_io_write",
                            "input_file": str(ua_file),
                            "output_file": rust_output,
                            "algebra_name": rust_algebra.name,
                            "cardinality": rust_algebra.cardinality,
                            "operation_count": len(rust_algebra.operations())
                        }
                    except Exception as e:
                        rust_result = {
                            "success": False,
                            "operation": "algebra_io_write",
                            "input_file": str(ua_file),
                            "output_file": rust_output,
                            "error": str(e)
                        }
                    
                    # Compare results
                    self._compare_results(
                        java_result, 
                        rust_result, 
                        f"algebra_io_write_{ua_file.name}"
                    )
                    
                    # If both succeeded, compare the output files
                    if (java_result.get("success") and rust_result.get("success")):
                        self._compare_output_files(java_output, rust_output, ua_file.name)
                
                finally:
                    # Clean up temporary files
                    for temp_file in [java_output, rust_output]:
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
    
    def test_algebra_io_roundtrip_compatibility(self):
        """Test round-trip file operations preserve all data"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files:
            with self.subTest(file=ua_file.name):
                # I/O operations are not computationally expensive, so don't skip based on file size
                # if self._should_skip_test(ua_file.stat().st_size, "algebra_io_roundtrip"):
                #     self.skipTest(f"Skipping large file {ua_file.name}")
                
                # Create temporary files
                with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as java_temp:
                    java_temp_file = java_temp.name
                with tempfile.NamedTemporaryFile(suffix='.ua', delete=False) as rust_temp:
                    rust_temp_file = rust_temp.name
                
                try:
                    # Test Java round-trip
                    java_result = self._run_java_operation(
                        "algebra_io_roundtrip", 
                        str(ua_file),
                        java_temp_file
                    )
                    
                    # Test Rust round-trip
                    try:
                        import uacalc
                        # Load original
                        original_algebra = uacalc.load_algebra(str(ua_file))
                        # Save to temp file
                        uacalc.save_algebra(original_algebra, rust_temp_file)
                        # Load back
                        reloaded_algebra = uacalc.load_algebra(rust_temp_file)
                        
                        # Compare properties
                        name_matches = original_algebra.name == reloaded_algebra.name
                        cardinality_matches = original_algebra.cardinality == reloaded_algebra.cardinality
                        operation_count_matches = len(original_algebra.operations()) == len(reloaded_algebra.operations())
                        
                        # Compare operation symbols
                        original_symbols = [op.symbol for op in original_algebra.operations()]
                        reloaded_symbols = [op.symbol for op in reloaded_algebra.operations()]
                        symbols_match = original_symbols == reloaded_symbols
                        
                        rust_result = {
                            "success": True,
                            "operation": "algebra_io_roundtrip",
                            "input_file": str(ua_file),
                            "temp_file": rust_temp_file,
                            "algebra_name": original_algebra.name,
                            "cardinality": original_algebra.cardinality,
                            "operation_count": len(original_algebra.operations()),
                            "roundtrip_success": name_matches and cardinality_matches and operation_count_matches and symbols_match,
                            "name_matches": name_matches,
                            "cardinality_matches": cardinality_matches,
                            "operation_count_matches": operation_count_matches,
                            "symbols_match": symbols_match
                        }
                    except Exception as e:
                        rust_result = {
                            "success": False,
                            "operation": "algebra_io_roundtrip",
                            "input_file": str(ua_file),
                            "temp_file": rust_temp_file,
                            "error": str(e)
                        }
                    
                    # Compare results
                    self._compare_results(
                        java_result, 
                        rust_result, 
                        f"algebra_io_roundtrip_{ua_file.name}"
                    )
                
                finally:
                    # Clean up temporary files
                    for temp_file in [java_temp_file, rust_temp_file]:
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
    
    def test_algebra_io_validation_compatibility(self):
        """Test file format validation and error detection"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files:
            with self.subTest(file=ua_file.name):
                # I/O operations are not computationally expensive, so don't skip based on file size
                # if self._should_skip_test(ua_file.stat().st_size, "algebra_io_validation"):
                #     self.skipTest(f"Skipping large file {ua_file.name}")
                
                # Test Java validation
                java_result = self._run_java_operation(
                    "algebra_io_validation", 
                    str(ua_file)
                )
                
                # Test Rust validation
                try:
                    import uacalc
                    algebra = uacalc.load_algebra(str(ua_file))
                    
                    # Basic validation checks
                    has_valid_name = algebra.name is not None and algebra.name.strip() != ""
                    has_valid_cardinality = algebra.cardinality > 0
                    has_valid_operations = algebra.operations() is not None and len(algebra.operations()) > 0
                    
                    # Check operation validity
                    all_operations_valid = True
                    for op in algebra.operations():
                        if op.symbol is None:
                            all_operations_valid = False
                            break
                        if op.arity() < 0:
                            all_operations_valid = False
                            break
                    
                    rust_result = {
                        "success": True,
                        "operation": "algebra_io_validation",
                        "input_file": str(ua_file),
                        "algebra_name": algebra.name,
                        "cardinality": algebra.cardinality,
                        "operation_count": len(algebra.operations()),
                        "validation_passed": has_valid_name and has_valid_cardinality and has_valid_operations and all_operations_valid,
                        "has_valid_name": has_valid_name,
                        "has_valid_cardinality": has_valid_cardinality,
                        "has_valid_operations": has_valid_operations,
                        "all_operations_valid": all_operations_valid
                    }
                except Exception as e:
                    rust_result = {
                        "success": False,
                        "operation": "algebra_io_validation",
                        "input_file": str(ua_file),
                        "validation_passed": False,
                        "error": str(e)
                    }
                
                # Compare results
                self._compare_results(
                    java_result, 
                    rust_result, 
                    f"algebra_io_validation_{ua_file.name}"
                )
    
    def test_malformed_file_error_handling_compatibility(self):
        """Test error handling for malformed files"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        # Create malformed test files
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
            with self.subTest(malformed_file=i):
                with tempfile.NamedTemporaryFile(suffix='.ua', mode='w', delete=False) as f:
                    f.write(content)
                    temp_path = f.name
                
                try:
                    # Test Java error handling
                    java_result = self._run_java_operation(
                        "algebra_io_validation", 
                        temp_path
                    )
                    
                    # Test Rust error handling
                    try:
                        import uacalc
                        uacalc.load_algebra(temp_path)
                        rust_result = {
                            "success": True,
                            "operation": "algebra_io_validation",
                            "input_file": temp_path,
                            "validation_passed": True
                        }
                    except Exception as e:
                        rust_result = {
                            "success": False,
                            "operation": "algebra_io_validation",
                            "input_file": temp_path,
                            "validation_passed": False,
                            "error": str(e)
                        }
                    
                    # Both should fail for malformed files
                    self.assertFalse(
                        java_result.get("success", True) and java_result.get("validation_passed", True),
                        f"Java should have failed for malformed file {i}"
                    )
                    self.assertFalse(
                        rust_result.get("success", True) and rust_result.get("validation_passed", True),
                        f"Rust should have failed for malformed file {i}"
                    )
                
                finally:
                    os.unlink(temp_path)
    
    def _compare_output_files(self, java_file: str, rust_file: str, original_name: str):
        """Compare the content of output files from Java and Rust"""
        try:
            with open(java_file, 'r') as f:
                java_content = f.read()
            with open(rust_file, 'r') as f:
                rust_content = f.read()
            
            # For now, just check that both files are valid XML and have similar structure
            # More detailed comparison could be added here
            self.assertTrue(
                java_content.startswith('<?xml'),
                f"Java output file {java_file} should be valid XML"
            )
            self.assertTrue(
                rust_content.startswith('<?xml'),
                f"Rust output file {rust_file} should be valid XML"
            )
            
            # Check that both contain the algebra name
            if f'<algName>{original_name}</algName>' in java_content:
                self.assertIn(
                    f'<algName>{original_name}</algName>',
                    rust_content,
                    f"Rust output should contain algebra name {original_name}"
                )
            
        except Exception as e:
            self.fail(f"Failed to compare output files: {e}")


if __name__ == '__main__':
    unittest.main()
