"""
Test suite for AlgebraIO module functions.

This module tests the AlgebraIO functions for reading and writing algebras
in various formats, including XML and legacy .alg format.
"""

import unittest
import os
import sys
import tempfile
import subprocess
import json

# Import uacalc_lib module
try:
    import uacalc_lib
except ImportError:
    print("Warning: uacalc_lib not found. Run 'maturin develop' to build Python bindings.")
    sys.exit(0)


class TestAlgebraIO(unittest.TestCase):
    """Test suite for AlgebraIO functions."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_resources_dir = "resources/algebras"
        cls.cyclic3_path = os.path.join(cls.test_resources_dir, "cyclic3.ua")
    
    def test_parse_line(self):
        """Test parse_line function."""
        parse_line = uacalc_lib.io.parse_line
        
        # Test parsing a number
        result = parse_line("42")
        self.assertEqual(result, 42)
        
        # Test parsing with whitespace
        result = parse_line("  10  ")
        self.assertEqual(result, 10)
        
        # Test parsing a comment
        result = parse_line("% comment")
        self.assertEqual(result, -1)
        
        # Test parsing another comment
        result = parse_line("  % another comment")
        self.assertEqual(result, -1)
    
    def test_parse_line_invalid(self):
        """Test parse_line with invalid input."""
        parse_line = uacalc_lib.io.parse_line
        
        # Test parsing invalid input
        with self.assertRaises(Exception):
            parse_line("not a number")
    
    def test_read_algebra_file(self):
        """Test read_algebra_file function."""
        if not os.path.exists(self.cyclic3_path):
            self.skipTest(f"Test file {self.cyclic3_path} not found")
        
        read_algebra_file = uacalc_lib.io.read_algebra_file
        
        alg = read_algebra_file(self.cyclic3_path)
        self.assertIsNotNone(alg)
        self.assertEqual(alg.cardinality(), 3)
        self.assertTrue(len(alg.operations()) > 0)
    
    def test_read_algebra_list_file(self):
        """Test read_algebra_list_file function."""
        if not os.path.exists(self.cyclic3_path):
            self.skipTest(f"Test file {self.cyclic3_path} not found")
        
        read_algebra_list_file = uacalc_lib.io.read_algebra_list_file
        
        algebras = read_algebra_list_file(self.cyclic3_path)
        self.assertIsNotNone(algebras)
        self.assertTrue(len(algebras) >= 1)
        self.assertEqual(algebras[0].cardinality(), 3)
    
    def test_read_algebra_from_stream(self):
        """Test read_algebra_from_stream function."""
        if not os.path.exists(self.cyclic3_path):
            self.skipTest(f"Test file {self.cyclic3_path} not found")
        
        read_algebra_from_stream = uacalc_lib.io.read_algebra_from_stream
        
        with open(self.cyclic3_path, 'rb') as f:
            data = f.read()
        
        alg = read_algebra_from_stream(data)
        self.assertIsNotNone(alg)
        self.assertEqual(alg.cardinality(), 3)
    
    def test_write_and_read_algebra_file(self):
        """Test write_algebra_file and read_algebra_file functions."""
        if not os.path.exists(self.cyclic3_path):
            self.skipTest(f"Test file {self.cyclic3_path} not found")
        
        read_algebra_file = uacalc_lib.io.read_algebra_file
        write_algebra_file = uacalc_lib.io.write_algebra_file
        
        # Read an algebra
        alg = read_algebra_file(self.cyclic3_path)
        
        # Write it to a temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            temp_path = f.name
        
        try:
            write_algebra_file(alg, temp_path)
            
            # Verify file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Read it back
            read_alg = read_algebra_file(temp_path)
            self.assertEqual(read_alg.cardinality(), alg.cardinality())
            self.assertEqual(len(read_alg.operations()), len(alg.operations()))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_write_algebra_file_with_style(self):
        """Test write_algebra_file_with_style function."""
        if not os.path.exists(self.cyclic3_path):
            self.skipTest(f"Test file {self.cyclic3_path} not found")
        
        read_algebra_file = uacalc_lib.io.read_algebra_file
        write_algebra_file_with_style = uacalc_lib.io.write_algebra_file_with_style
        
        # Read an algebra
        alg = read_algebra_file(self.cyclic3_path)
        
        # Write it in old style
        with tempfile.NamedTemporaryFile(mode='w', suffix='.alg', delete=False) as f:
            temp_path = f.name
        
        try:
            write_algebra_file_with_style(alg, temp_path, True)
            
            # Verify file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Read it back
            read_alg = read_algebra_file(temp_path)
            self.assertEqual(read_alg.cardinality(), alg.cardinality())
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_convert_to_xml(self):
        """Test convert_to_xml function."""
        convert_to_xml = uacalc_lib.io.convert_to_xml
        
        # Create a temp .alg file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.alg', delete=False) as f:
            temp_alg_path = f.name
            f.write("2\n")  # cardinality
            f.write("2\n")  # arity
            f.write("0\n1\n1\n0\n")  # operation table
        
        try:
            # Convert to XML
            convert_to_xml(temp_alg_path)
            
            # Check if XML file was created
            xml_path = temp_alg_path.replace('.alg', '.xml')
            self.assertTrue(os.path.exists(xml_path))
            
            # Clean up XML file
            if os.path.exists(xml_path):
                os.remove(xml_path)
        finally:
            if os.path.exists(temp_alg_path):
                os.remove(temp_alg_path)
    
    def test_read_projective_plane_error(self):
        """Test read_projective_plane with invalid input."""
        read_projective_plane = uacalc_lib.io.read_projective_plane
        
        # Create a temp file with invalid format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
            f.write("1 2 3\n")  # Invalid: should start with 0
        
        try:
            with self.assertRaises(Exception):
                read_projective_plane(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_read_projective_plane_not_implemented(self):
        """Test read_projective_plane returns not implemented error."""
        read_projective_plane = uacalc_lib.io.read_projective_plane
        
        # Create a temp file with valid first line
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
            f.write("0 1 2\n")  # Valid first line
            f.write("3 4 5\n")
        
        try:
            with self.assertRaises(Exception) as cm:
                read_projective_plane(temp_path)
            
            # Check that error message indicates not implemented
            self.assertIn("not yet implemented", str(cm.exception).lower())
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def run_java_wrapper(self, command, args):
        """Run Java wrapper and return parsed JSON output."""
        import platform
        separator = ";" if platform.system() == "Windows" else ":"
        classpath = f"java_wrapper/build/classes{separator}build/classes{separator}org{separator}jars/*"
        cmd = [
            "java", "-cp", classpath,
            "java_wrapper.src.io.AlgebraIOWrapper",
            command
        ] + args
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Java wrapper failed: {result.stderr}")
        
        output = json.loads(result.stdout)
        # Parse the data field if it's a string
        if "data" in output and isinstance(output["data"], str):
            output["data"] = json.loads(output["data"])
        return output
    
    def test_compare_with_java_parse_line(self):
        """Compare parse_line with Java implementation."""
        parse_line = uacalc_lib.io.parse_line
        
        # Test with a number
        result = parse_line("42")
        java_result = self.run_java_wrapper("parse_line", ["--line", "42"])
        self.assertEqual(result, java_result["data"]["status"])
        
        # Test with a comment
        result = parse_line("% comment")
        java_result = self.run_java_wrapper("parse_line", ["--line", "% comment"])
        self.assertEqual(result, java_result["data"]["status"])
    
    def test_compare_with_java_read_algebra_file(self):
        """Compare read_algebra_file with Java implementation."""
        if not os.path.exists(self.cyclic3_path):
            self.skipTest(f"Test file {self.cyclic3_path} not found")
        
        read_algebra_file = uacalc_lib.io.read_algebra_file
        
        # Read with Python
        alg = read_algebra_file(self.cyclic3_path)
        
        # Read with Java
        java_result = self.run_java_wrapper("read_algebra_file", ["--path", self.cyclic3_path])
        
        # Compare results
        self.assertEqual(alg.cardinality(), java_result["data"]["cardinality"])
        self.assertEqual(len(alg.operations()), java_result["data"]["num_operations"])


def main():
    """Run the tests."""
    unittest.main()


if __name__ == '__main__':
    main()

