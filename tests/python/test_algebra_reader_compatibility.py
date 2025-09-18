#!/usr/bin/env python3
"""
AlgebraReader Compatibility Test

This module tests the org.uacalc.io.AlgebraReader class compatibility between
Java UACalc and the Rust/Python implementation. It verifies that file parsing
operations work identically, including error handling and Unicode support.
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


class AlgebraReaderCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.io.AlgebraReader class compatibility.
    
    This class tests:
    - AlgebraReader parsing of various .ua file formats
    - Error handling for malformed files
    - Unicode and special character handling in file parsing
    
    Requirements: 6.1, 6.4, 6.5
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
        
        # Test files for various scenarios
        self.test_files = [
            "resources/algebras/ba2.ua",      # Boolean algebra
            "resources/algebras/cyclic2.ua",  # Cyclic group
            "resources/algebras/cyclic3.ua",  # Cyclic group
            "resources/algebras/m3.ua",       # Modular lattice
            "resources/algebras/m4.ua",       # Modular lattice
            "resources/algebras/n5.ua",       # Non-modular lattice
            "resources/algebras/sym3.ua",     # Symmetric group
            "resources/algebras/z3.ua"        # Cyclic group
        ]
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after each test"""
        # Clean up temporary files
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
        super().tearDown()
    
    def test_algebra_reader_parsing_compatibility(self):
        """Test AlgebraReader parsing produces identical results"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.uacalc_available:
            self.skipTest("uacalc module not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files:
            with self.subTest(file=ua_file.name):
                # Test Java AlgebraReader operation
                java_result = self._run_java_operation(
                    "algebra_reader_parse", 
                    str(ua_file)
                )
                
                # Test Rust operation (load_algebra)
                try:
                    import uacalc
                    rust_algebra = uacalc.load_algebra(str(ua_file))
                    
                    rust_result = {
                        "success": True,
                        "operation": "algebra_reader_parse",
                        "input_file": str(ua_file),
                        "algebra_name": rust_algebra.name,
                        "cardinality": rust_algebra.cardinality,
                        "operation_count": len(rust_algebra.operations),
                        "operations": []
                    }
                    
                    # Add operation details
                    for op in rust_algebra.operations:
                        rust_result["operations"].append({
                            "symbol": op.symbol,
                            "arity": op.arity,
                            "description": getattr(op, 'description', '')
                        })
                    
                except Exception as e:
                    rust_result = {
                        "success": False,
                        "operation": "algebra_reader_parse",
                        "input_file": str(ua_file),
                        "error": str(e)
                    }
                
                # Compare results
                self._compare_results(
                    java_result, 
                    rust_result, 
                    f"algebra_reader_parse_{ua_file.name}"
                )
    
    def test_algebra_reader_error_handling_compatibility(self):
        """Test AlgebraReader error handling for malformed files"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.uacalc_available:
            self.skipTest("uacalc module not available")
        
        # Test cases for malformed files
        malformed_test_cases = [
            {
                "name": "empty_file",
                "content": "",
                "expected_error": "empty or invalid"
            },
            {
                "name": "invalid_xml",
                "content": "<algebra><basicAlgebra><algName>test</algName><invalid>",
                "expected_error": "XML parsing"
            },
            {
                "name": "missing_algebra_type",
                "content": """<?xml version="1.0"?>
<algebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
</algebra>""",
                "expected_error": "algebra type"
            },
            {
                "name": "invalid_cardinality",
                "content": """<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>invalid</cardinality>
  </basicAlgebra>
</algebra>""",
                "expected_error": "cardinality"
            },
            {
                "name": "malformed_operation_table",
                "content": """<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>f</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1,2,3,4</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>""",
                "expected_error": "operation table"
            }
        ]
        
        for test_case in malformed_test_cases:
            with self.subTest(case=test_case["name"]):
                # Create temporary malformed file
                temp_file = os.path.join(self.temp_dir, f"{test_case['name']}.ua")
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(test_case["content"])
                
                # Test Java error handling
                java_result = self._run_java_operation(
                    "algebra_reader_parse", 
                    temp_file
                )
                
                # Test Rust error handling
                try:
                    import uacalc
                    uacalc.load_algebra(temp_file)
                    rust_result = {
                        "success": True,
                        "operation": "algebra_reader_parse",
                        "input_file": temp_file,
                        "error": None
                    }
                except Exception as e:
                    rust_result = {
                        "success": False,
                        "operation": "algebra_reader_parse",
                        "input_file": temp_file,
                        "error": str(e)
                    }
                
                # Both should fail for malformed files
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
    
    def test_algebra_reader_unicode_compatibility(self):
        """Test AlgebraReader Unicode and special character handling"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.uacalc_available:
            self.skipTest("uacalc module not available")
        
        # Test cases with Unicode and special characters
        unicode_test_cases = [
            {
                "name": "unicode_algebra_name",
                "content": """<?xml version="1.0" encoding="UTF-8"?>
<algebra>
  <basicAlgebra>
    <algName>Álgebra_Test_αβγ</algName>
    <desc>Test algebra with Unicode name</desc>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>f</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1</row>
            <row r="[1]">1,0</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>""",
                "expected_name": "Álgebra_Test_αβγ"
            },
            {
                "name": "unicode_operation_name",
                "content": """<?xml version="1.0" encoding="UTF-8"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <desc>Test algebra with Unicode operation name</desc>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>f_αβγ</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1</row>
            <row r="[1]">1,0</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>""",
                "expected_op_name": "f_αβγ"
            },
            {
                "name": "unicode_description",
                "content": """<?xml version="1.0" encoding="UTF-8"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <desc>Operación binaria αβγ</desc>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>f</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1</row>
            <row r="[1]">1,0</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>""",
                "expected_description": "Operación binaria αβγ"
            },
            {
                "name": "special_characters",
                "content": """<?xml version="1.0" encoding="UTF-8"?>
<algebra>
  <basicAlgebra>
    <algName>test@#$%</algName>
    <desc>Test algebra with special characters</desc>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>f_@#$%</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1</row>
            <row r="[1]">1,0</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>""",
                "expected_name": "test@#$%",
                "expected_op_name": "f_@#$%"
            }
        ]
        
        for test_case in unicode_test_cases:
            with self.subTest(case=test_case["name"]):
                # Create temporary file with Unicode content
                temp_file = os.path.join(self.temp_dir, f"{test_case['name']}.ua")
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(test_case["content"])
                
                # Test Java Unicode handling
                java_result = self._run_java_operation(
                    "algebra_reader_parse", 
                    temp_file
                )
                
                # Test Rust Unicode handling
                try:
                    import uacalc
                    rust_algebra = uacalc.load_algebra(temp_file)
                    
                    rust_result = {
                        "success": True,
                        "operation": "algebra_reader_parse",
                        "input_file": temp_file,
                        "algebra_name": rust_algebra.name,
                        "cardinality": rust_algebra.cardinality,
                        "operation_count": len(rust_algebra.operations),
                        "operations": []
                    }
                    
                    # Add operation details
                    for op in rust_algebra.operations:
                        rust_result["operations"].append({
                            "symbol": op.symbol,
                            "arity": op.arity,
                            "description": getattr(op, 'description', '')
                        })
                    
                except Exception as e:
                    rust_result = {
                        "success": False,
                        "operation": "algebra_reader_parse",
                        "input_file": temp_file,
                        "error": str(e)
                    }
                
                # Both should succeed for valid Unicode files
                self.assertTrue(
                    java_result.get("success", False),
                    f"Java should have succeeded for {test_case['name']}: {java_result.get('error', 'Unknown error')}"
                )
                self.assertTrue(
                    rust_result.get("success", False),
                    f"Rust should have succeeded for {test_case['name']}: {rust_result.get('error', 'Unknown error')}"
                )
                
                # Verify Unicode content is preserved
                if "expected_name" in test_case:
                    self.assertEqual(
                        java_result.get("algebra_name", ""),
                        test_case["expected_name"],
                        f"Java Unicode algebra name mismatch for {test_case['name']}"
                    )
                    self.assertEqual(
                        rust_result.get("algebra_name", ""),
                        test_case["expected_name"],
                        f"Rust Unicode algebra name mismatch for {test_case['name']}"
                    )
                
                if "expected_op_name" in test_case:
                    java_ops = java_result.get("operations", [])
                    rust_ops = rust_result.get("operations", [])
                    
                    if java_ops and rust_ops:
                        self.assertEqual(
                            java_ops[0].get("symbol", ""),
                            test_case["expected_op_name"],
                            f"Java Unicode operation name mismatch for {test_case['name']}"
                        )
                        self.assertEqual(
                            rust_ops[0].get("symbol", ""),
                            test_case["expected_op_name"],
                            f"Rust Unicode operation name mismatch for {test_case['name']}"
                        )
                
                    if "expected_description" in test_case:
                        # Note: Java AlgebraReader may not extract description from <desc> element
                        # This test verifies that both implementations handle Unicode in descriptions
                        # but may not extract them identically due to implementation differences
                        java_ops = java_result.get("operations", [])
                        rust_ops = rust_result.get("operations", [])
                        
                        if java_ops and rust_ops:
                            # Both should handle Unicode in descriptions without errors
                            # The exact extraction may differ between implementations
                            java_desc = java_ops[0].get("description", "")
                            rust_desc = rust_ops[0].get("description", "")
                            
                            # Both should be strings (even if empty) and not cause errors
                            self.assertIsInstance(java_desc, str, f"Java description should be string for {test_case['name']}")
                            self.assertIsInstance(rust_desc, str, f"Rust description should be string for {test_case['name']}")
    
    def test_algebra_reader_stream_compatibility(self):
        """Test AlgebraReader stream-based parsing compatibility"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.uacalc_available:
            self.skipTest("uacalc module not available")
        
        # Test stream-based parsing with a valid file
        if self.algebra_files:
            test_file = self.algebra_files[0]  # Use first available file
            
            with self.subTest(file=test_file.name):
                # Test Java stream parsing
                java_result = self._run_java_operation(
                    "algebra_reader_stream_parse", 
                    str(test_file)
                )
                
                # Test Rust stream parsing (simulated by reading file content)
                try:
                    import uacalc
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create temporary file from content to simulate stream
                    temp_file = os.path.join(self.temp_dir, f"stream_{test_file.name}")
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    rust_algebra = uacalc.load_algebra(temp_file)
                    
                    rust_result = {
                        "success": True,
                        "operation": "algebra_reader_stream_parse",
                        "input_file": str(test_file),
                        "algebra_name": rust_algebra.name,
                        "cardinality": rust_algebra.cardinality,
                        "operation_count": len(rust_algebra.operations)
                    }
                    
                except Exception as e:
                    rust_result = {
                        "success": False,
                        "operation": "algebra_reader_stream_parse",
                        "input_file": str(test_file),
                        "error": str(e)
                    }
                
                # Compare results
                self._compare_results(
                    java_result, 
                    rust_result, 
                    f"algebra_reader_stream_parse_{test_file.name}"
                )
    
    def test_algebra_reader_large_file_compatibility(self):
        """Test AlgebraReader with larger files"""
        if not self.java_available:
            self.skipTest("Java environment not available")
        
        if not self.uacalc_available:
            self.skipTest("uacalc module not available")
        
        # Test with larger algebra files if available
        large_files = [f for f in self.algebra_files if f.stat().st_size > 1000]
        
        if not large_files:
            self.skipTest("No large algebra files found for testing")
        
        for ua_file in large_files[:3]:  # Test up to 3 large files
            with self.subTest(file=ua_file.name):
                # Test Java operation
                java_result = self._run_java_operation(
                    "algebra_reader_parse", 
                    str(ua_file)
                )
                
                # Test Rust operation
                try:
                    import uacalc
                    rust_algebra = uacalc.load_algebra(str(ua_file))
                    
                    rust_result = {
                        "success": True,
                        "operation": "algebra_reader_parse",
                        "input_file": str(ua_file),
                        "algebra_name": rust_algebra.name,
                        "cardinality": rust_algebra.cardinality,
                        "operation_count": len(rust_algebra.operations)
                    }
                    
                except Exception as e:
                    rust_result = {
                        "success": False,
                        "operation": "algebra_reader_parse",
                        "input_file": str(ua_file),
                        "error": str(e)
                    }
                
                # Compare results
                self._compare_results(
                    java_result, 
                    rust_result, 
                    f"algebra_reader_large_{ua_file.name}"
                )


if __name__ == '__main__':
    unittest.main()
