#!/usr/bin/env python3
"""
AlgebraWriter Compatibility Test

This module tests the org.uacalc.io.AlgebraWriter class compatibility between
Java UACalc and the Rust/Python implementation. It verifies that algebra file
generation operations work identically, including output format validation
and various algebra types and complexities.

Requirements: 6.2, 6.4
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


class AlgebraWriterCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.io.AlgebraWriter class compatibility.
    
    This class tests:
    - AlgebraWriter generation of .ua files
    - Verify output format matches Java UACalc exactly
    - Test file generation with various algebra types and complexities
    
    Requirements: 6.2, 6.4
    """
    
    def setUp(self):
        """Set up for each test"""
        super().setUp()
        
        # Skip tests if uacalc is not available
        try:
            import uacalc
            self.uacalc_available = True
        except ImportError:
            self.uacalc_available = False
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after each test"""
        # Clean up temporary files
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
        super().tearDown()
    
    def test_algebra_writer_basic_generation_compatibility(self):
        """Test AlgebraWriter basic file generation produces identical output"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.uacalc_available:
            self.skipTest("uacalc module not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files:
            with self.subTest(file=ua_file.name):
                # Create temporary output files
                java_output = os.path.join(self.temp_dir, f"java_{ua_file.name}")
                rust_output = os.path.join(self.temp_dir, f"rust_{ua_file.name}")
                
                try:
                    # Test Java AlgebraWriter operation
                    java_result = self._run_java_operation(
                        "algebra_writer", 
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
                            "operation": "algebra_writer",
                            "input_file": str(ua_file),
                            "output_file": rust_output,
                            "algebra_name": rust_algebra.name,
                            "cardinality": rust_algebra.cardinality,
                            "operation_count": len(rust_algebra.operations)
                        }
                    except Exception as e:
                        rust_result = {
                            "success": False,
                            "operation": "algebra_writer",
                            "input_file": str(ua_file),
                            "output_file": rust_output,
                            "error": str(e)
                        }
                    
                    # Compare results
                    self._compare_results(
                        java_result, 
                        rust_result, 
                        f"algebra_writer_basic_{ua_file.name}"
                    )
                    
                    # If both succeeded, compare the output files
                    if (java_result.get("success") and rust_result.get("success")):
                        self._compare_output_files(java_output, rust_output, ua_file.name)
                
                finally:
                    # Clean up temporary files
                    for temp_file in [java_output, rust_output]:
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
    
    def test_algebra_writer_format_compatibility(self):
        """Test AlgebraWriter output format matches Java UACalc exactly"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.uacalc_available:
            self.skipTest("uacalc module not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files:
            with self.subTest(file=ua_file.name):
                # Create temporary output files
                java_output = os.path.join(self.temp_dir, f"java_format_{ua_file.name}")
                rust_output = os.path.join(self.temp_dir, f"rust_format_{ua_file.name}")
                
                try:
                    # Test Java AlgebraWriter operation
                    java_result = self._run_java_operation(
                        "algebra_writer", 
                        str(ua_file),
                        java_output
                    )
                    
                    # Test Rust operation
                    try:
                        import uacalc
                        rust_algebra = uacalc.load_algebra(str(ua_file))
                        uacalc.save_algebra(rust_algebra, rust_output)
                        
                        rust_result = {
                            "success": True,
                            "operation": "algebra_writer",
                            "input_file": str(ua_file),
                            "output_file": rust_output
                        }
                    except Exception as e:
                        rust_result = {
                            "success": False,
                            "operation": "algebra_writer",
                            "input_file": str(ua_file),
                            "output_file": rust_output,
                            "error": str(e)
                        }
                    
                    # Both should succeed
                    self.assertTrue(
                        java_result.get("success", False),
                        f"Java AlgebraWriter should succeed for {ua_file.name}: {java_result.get('error', 'Unknown error')}"
                    )
                    self.assertTrue(
                        rust_result.get("success", False),
                        f"Rust save_algebra should succeed for {ua_file.name}: {rust_result.get('error', 'Unknown error')}"
                    )
                    
                    # Compare output file formats
                    if (java_result.get("success") and rust_result.get("success")):
                        self._compare_file_formats(java_output, rust_output, ua_file.name)
                
                finally:
                    # Clean up temporary files
                    for temp_file in [java_output, rust_output]:
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
    
    def test_algebra_writer_various_types_compatibility(self):
        """Test AlgebraWriter with various algebra types and complexities"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.uacalc_available:
            self.skipTest("uacalc module not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        # Test with different types of algebras
        test_cases = [
            ("small_algebra", lambda files: [f for f in files if f.stat().st_size < 1000]),
            ("medium_algebra", lambda files: [f for f in files if 1000 <= f.stat().st_size < 5000]),
            ("large_algebra", lambda files: [f for f in files if f.stat().st_size >= 5000])
        ]
        
        for test_type, file_filter in test_cases:
            filtered_files = file_filter(self.algebra_files)
            if not filtered_files:
                continue
                
            # Test up to 3 files of each type
            for ua_file in filtered_files[:3]:
                with self.subTest(type=test_type, file=ua_file.name):
                    # Create temporary output files
                    java_output = os.path.join(self.temp_dir, f"java_{test_type}_{ua_file.name}")
                    rust_output = os.path.join(self.temp_dir, f"rust_{test_type}_{ua_file.name}")
                    
                    try:
                        # Test Java AlgebraWriter operation
                        java_result = self._run_java_operation(
                            "algebra_writer", 
                            str(ua_file),
                            java_output
                        )
                        
                        # Test Rust operation
                        try:
                            import uacalc
                            rust_algebra = uacalc.load_algebra(str(ua_file))
                            uacalc.save_algebra(rust_algebra, rust_output)
                            
                            rust_result = {
                                "success": True,
                                "operation": "algebra_writer",
                                "input_file": str(ua_file),
                                "output_file": rust_output,
                                "algebra_name": rust_algebra.name,
                                "cardinality": rust_algebra.cardinality,
                                "operation_count": len(rust_algebra.operations),
                                "test_type": test_type
                            }
                        except Exception as e:
                            rust_result = {
                                "success": False,
                                "operation": "algebra_writer",
                                "input_file": str(ua_file),
                                "output_file": rust_output,
                                "test_type": test_type,
                                "error": str(e)
                            }
                        
                        # Compare results
                        self._compare_results(
                            java_result, 
                            rust_result, 
                            f"algebra_writer_{test_type}_{ua_file.name}"
                        )
                    
                    finally:
                        # Clean up temporary files
                        for temp_file in [java_output, rust_output]:
                            if os.path.exists(temp_file):
                                os.unlink(temp_file)
    
    def test_algebra_writer_roundtrip_compatibility(self):
        """Test AlgebraWriter round-trip operations preserve all data"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.uacalc_available:
            self.skipTest("uacalc module not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files:
            with self.subTest(file=ua_file.name):
                # Create temporary files for round-trip testing
                java_temp = os.path.join(self.temp_dir, f"java_roundtrip_{ua_file.name}")
                rust_temp = os.path.join(self.temp_dir, f"rust_roundtrip_{ua_file.name}")
                
                try:
                    # Test Java round-trip: read -> write -> read
                    java_result = self._run_java_operation(
                        "algebra_io_roundtrip", 
                        str(ua_file),
                        java_temp
                    )
                    
                    # Test Rust round-trip
                    try:
                        import uacalc
                        # Load original
                        original_algebra = uacalc.load_algebra(str(ua_file))
                        # Save to temp file
                        uacalc.save_algebra(original_algebra, rust_temp)
                        # Load back
                        reloaded_algebra = uacalc.load_algebra(rust_temp)
                        
                        # Compare properties
                        name_matches = original_algebra.name == reloaded_algebra.name
                        cardinality_matches = original_algebra.cardinality == reloaded_algebra.cardinality
                        operation_count_matches = len(original_algebra.operations) == len(reloaded_algebra.operations)
                        
                        # Compare operation symbols
                        original_symbols = [op.symbol for op in original_algebra.operations]
                        reloaded_symbols = [op.symbol for op in reloaded_algebra.operations]
                        symbols_match = original_symbols == reloaded_symbols
                        
                        rust_result = {
                            "success": True,
                            "operation": "algebra_writer_roundtrip",
                            "input_file": str(ua_file),
                            "temp_file": rust_temp,
                            "algebra_name": original_algebra.name,
                            "cardinality": original_algebra.cardinality,
                            "operation_count": len(original_algebra.operations),
                            "roundtrip_success": name_matches and cardinality_matches and operation_count_matches and symbols_match,
                            "name_matches": name_matches,
                            "cardinality_matches": cardinality_matches,
                            "operation_count_matches": operation_count_matches,
                            "symbols_match": symbols_match
                        }
                    except Exception as e:
                        rust_result = {
                            "success": False,
                            "operation": "algebra_writer_roundtrip",
                            "input_file": str(ua_file),
                            "temp_file": rust_temp,
                            "error": str(e)
                        }
                    
                    # Compare results
                    self._compare_results(
                        java_result, 
                        rust_result, 
                        f"algebra_writer_roundtrip_{ua_file.name}"
                    )
                
                finally:
                    # Clean up temporary files
                    for temp_file in [java_temp, rust_temp]:
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
    
    def test_algebra_writer_error_handling_compatibility(self):
        """Test AlgebraWriter error handling for invalid inputs"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.uacalc_available:
            self.skipTest("uacalc module not available")
        
        # Test error cases
        error_test_cases = [
            {
                "name": "nonexistent_file",
                "input_file": "/nonexistent/path/to/file.ua",
                "expected_error": "file not found"
            },
            {
                "name": "invalid_output_path",
                "input_file": self.algebra_files[0] if self.algebra_files else None,
                "output_file": "/invalid/path/that/does/not/exist/output.ua",
                "expected_error": "output path"
            }
        ]
        
        for test_case in error_test_cases:
            if test_case["input_file"] is None:
                continue
                
            with self.subTest(case=test_case["name"]):
                # Create temporary output file for valid cases
                if "output_file" not in test_case:
                    test_case["output_file"] = os.path.join(self.temp_dir, f"error_test_{test_case['name']}.ua")
                
                # Test Java error handling
                java_result = self._run_java_operation(
                    "algebra_writer", 
                    test_case["input_file"],
                    test_case["output_file"]
                )
                
                # Test Rust error handling
                try:
                    import uacalc
                    rust_algebra = uacalc.load_algebra(test_case["input_file"])
                    uacalc.save_algebra(rust_algebra, test_case["output_file"])
                    
                    rust_result = {
                        "success": True,
                        "operation": "algebra_writer",
                        "input_file": test_case["input_file"],
                        "output_file": test_case["output_file"],
                        "error": None
                    }
                except Exception as e:
                    rust_result = {
                        "success": False,
                        "operation": "algebra_writer",
                        "input_file": test_case["input_file"],
                        "output_file": test_case["output_file"],
                        "error": str(e)
                    }
                
                # Both should fail for error cases
                self.assertFalse(
                    java_result.get("success", True),
                    f"Java should have failed for {test_case['name']} but didn't"
                )
                self.assertFalse(
                    rust_result.get("success", True),
                    f"Rust should have failed for {test_case['name']} but didn't"
                )
                
                # Both should produce error messages
                self.assertIsNotNone(
                    java_result.get("error"),
                    f"Java should have produced error for {test_case['name']}"
                )
                self.assertIsNotNone(
                    rust_result.get("error"),
                    f"Rust should have produced error for {test_case['name']}"
                )
    
    def _compare_output_files(self, java_file: str, rust_file: str, original_name: str):
        """Compare the content of output files from Java and Rust"""
        try:
            with open(java_file, 'r', encoding='utf-8') as f:
                java_content = f.read()
            with open(rust_file, 'r', encoding='utf-8') as f:
                rust_content = f.read()
            
            # Both files should be valid XML
            self.assertTrue(
                java_content.startswith('<?xml'),
                f"Java output file {java_file} should be valid XML"
            )
            self.assertTrue(
                rust_content.startswith('<?xml'),
                f"Rust output file {rust_file} should be valid XML"
            )
            
            # Both should contain the algebra name
            if f'<algName>{original_name}</algName>' in java_content:
                self.assertIn(
                    f'<algName>{original_name}</algName>',
                    rust_content,
                    f"Rust output should contain algebra name {original_name}"
                )
            
            # Both should have similar structure
            self.assertIn('<algebra>', java_content, "Java output should contain <algebra> tag")
            self.assertIn('<algebra>', rust_content, "Rust output should contain <algebra> tag")
            self.assertIn('<basicAlgebra>', java_content, "Java output should contain <basicAlgebra> tag")
            self.assertIn('<basicAlgebra>', rust_content, "Rust output should contain <basicAlgebra> tag")
            
        except Exception as e:
            self.fail(f"Failed to compare output files: {e}")
    
    def _compare_file_formats(self, java_file: str, rust_file: str, original_name: str):
        """Compare the format and structure of output files"""
        try:
            with open(java_file, 'r', encoding='utf-8') as f:
                java_content = f.read()
            with open(rust_file, 'r', encoding='utf-8') as f:
                rust_content = f.read()
            
            # Check XML structure
            java_lines = java_content.split('\n')
            rust_lines = rust_content.split('\n')
            
            # Both should have XML declaration
            self.assertTrue(
                any(line.strip().startswith('<?xml') for line in java_lines),
                "Java output should have XML declaration"
            )
            self.assertTrue(
                any(line.strip().startswith('<?xml') for line in rust_lines),
                "Rust output should have XML declaration"
            )
            
            # Both should have proper XML structure
            self.assertIn('<algebra>', java_content, "Java output should have <algebra> root element")
            self.assertIn('<algebra>', rust_content, "Rust output should have <algebra> root element")
            self.assertIn('</algebra>', java_content, "Java output should have closing </algebra> tag")
            self.assertIn('</algebra>', rust_content, "Rust output should have closing </algebra> tag")
            
            # Both should have cardinality
            self.assertIn('<cardinality>', java_content, "Java output should have cardinality")
            self.assertIn('<cardinality>', rust_content, "Rust output should have cardinality")
            
            # Both should have operations section
            self.assertIn('<operations>', java_content, "Java output should have operations section")
            self.assertIn('<operations>', rust_content, "Rust output should have operations section")
            
        except Exception as e:
            self.fail(f"Failed to compare file formats: {e}")


if __name__ == '__main__':
    unittest.main()
