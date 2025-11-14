"""
Tests for TypeFinder

These tests verify the TypeFinder implementation for Tame Congruence Theory (TCT)
analysis of algebras. Tests compare Python/Rust output with Java wrapper results.
"""

import unittest
import os
import json
import subprocess
import platform
import uacalc_lib
from conftest import load_test_algebra


def run_java_wrapper(command, args):
    """Run the Java TypeFinder wrapper and return parsed JSON output."""
    separator = ";" if platform.system() == "Windows" else ":"
    classpath = f"java_wrapper/build/classes{separator}build/classes{separator}org{separator}jars/*"
    cmd = [
        "java", "-cp", classpath,
        "java_wrapper.src.alg.conlat.TypeFinderWrapper",
        command
    ] + args
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise Exception(f"Java wrapper failed: {result.stderr}")
        
        # Strip out any non-JSON lines (like "universe size: X") before parsing
        stdout_lines = result.stdout.strip().split('\n')
        json_start = -1
        for i, line in enumerate(stdout_lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start == -1:
            raise Exception(f"No JSON output found in: {result.stdout}")
        
        json_output = '\n'.join(stdout_lines[json_start:])
        output = json.loads(json_output)
        
        # Parse the data field again if it's a string
        if "data" in output and isinstance(output["data"], str):
            output["data"] = json.loads(output["data"])
        return output
    except Exception as e:
        raise Exception(f"Failed to run Java wrapper: {e}")


class TestTypeFinder(unittest.TestCase):
    """Test TypeFinder class with comprehensive TCT analysis tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_algebras = [
            "cyclic2", "cyclic3", "n5", "m3", "z3"
        ]
        cls.loaded_algebras = {}
        
        # Load available test algebras
        for name in cls.test_algebras:
            try:
                cls.loaded_algebras[name] = load_test_algebra(name, skip_if_missing=True)
            except unittest.SkipTest:
                pass  # Skip if algebra not found
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            TypeFinder = uacalc_lib.alg.TypeFinder
            self.TypeFinder = TypeFinder
        except (ImportError, AttributeError):
            self.skipTest("TypeFinder not available - requires full build")
    
    def test_basic_functionality(self):
        """Test basic TypeFinder creation and initialization."""
        if not self.loaded_algebras:
            self.skipTest("No test algebras available")
        
        # Test with cyclic3 algebra
        alg = self.loaded_algebras.get("cyclic3")
        if not alg:
            self.skipTest("cyclic3 algebra not available")
        
        tf = self.TypeFinder(alg)
        self.assertIsNotNone(tf)
        self.assertEqual(tf.alg_size(), 3)
        
        # Test initialization
        tf.init()
    
    def test_find_type_set_cyclic2(self):
        """Test find_type_set with cyclic2 algebra."""
        alg = self.loaded_algebras.get("cyclic2")
        if not alg:
            self.skipTest("cyclic2 algebra not available")
        
        # Test Python/Rust implementation
        tf = self.TypeFinder(alg)
        tf.init()
        type_set = tf.find_type_set()
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("find_type_set", ["--algebra", "resources/algebras/cyclic2.ua"])
        java_type_set = set(java_result["data"]["type_set"])
        
        # Convert Python result to set for comparison
        python_type_set = set(type_set) if isinstance(type_set, list) else type_set
        
        self.assertEqual(python_type_set, java_type_set)
        self.assertIsInstance(type_set, set)
        self.assertTrue(all(isinstance(t, int) and 1 <= t <= 5 for t in type_set))
    
    def test_find_type_set_cyclic3(self):
        """Test find_type_set with cyclic3 algebra."""
        alg = self.loaded_algebras.get("cyclic3")
        if not alg:
            self.skipTest("cyclic3 algebra not available")
        
        # Test Python/Rust implementation
        tf = self.TypeFinder(alg)
        tf.init()
        type_set = tf.find_type_set()
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("find_type_set", ["--algebra", "resources/algebras/cyclic3.ua"])
        java_type_set = set(java_result["data"]["type_set"])
        
        self.assertEqual(type_set, java_type_set)
        self.assertIsInstance(type_set, set)
        self.assertTrue(all(isinstance(t, int) and 1 <= t <= 5 for t in type_set))
    
    def test_find_type_set_m3(self):
        """Test find_type_set with m3 lattice."""
        alg = self.loaded_algebras.get("m3")
        if not alg:
            self.skipTest("m3 algebra not available")
        
        # Test Python/Rust implementation
        tf = self.TypeFinder(alg)
        tf.init()
        type_set = tf.find_type_set()
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("find_type_set", ["--algebra", "resources/algebras/m3.ua"])
        java_type_set = set(java_result["data"]["type_set"])
        
        self.assertEqual(type_set, java_type_set)
        self.assertIsInstance(type_set, set)
        self.assertTrue(all(isinstance(t, int) and 1 <= t <= 5 for t in type_set))
    
    def test_find_type_cyclic2(self):
        """Test find_type method with cyclic2 algebra."""
        alg = self.loaded_algebras.get("cyclic2")
        if not alg:
            self.skipTest("cyclic2 algebra not available")
        
        tf = self.TypeFinder(alg)
        tf.init()
        
        # Get join irreducibles
        con = alg.con()
        jis = con.join_irreducibles()
        
        if not jis:
            self.skipTest("No join irreducibles found")
        
        # Test first join irreducible
        ji = jis[0]
        type_result = tf.find_type(ji)
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("find_type", ["--algebra", "resources/algebras/cyclic2.ua", "--ji_index", "0"])
        java_type = java_result["data"]["type"]
        
        self.assertEqual(type_result, java_type)
        self.assertIsInstance(type_result, int)
        self.assertTrue(1 <= type_result <= 5)
    
    def test_find_type_cyclic3(self):
        """Test find_type method with cyclic3 algebra."""
        alg = self.loaded_algebras.get("cyclic3")
        if not alg:
            self.skipTest("cyclic3 algebra not available")
        
        tf = self.TypeFinder(alg)
        tf.init()
        
        # Get join irreducibles
        con = alg.con()
        jis = con.join_irreducibles()
        
        if not jis:
            self.skipTest("No join irreducibles found")
        
        # Test first join irreducible
        ji = jis[0]
        type_result = tf.find_type(ji)
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("find_type", ["--algebra", "resources/algebras/cyclic3.ua", "--ji_index", "0"])
        java_type = java_result["data"]["type"]
        
        self.assertEqual(type_result, java_type)
        self.assertIsInstance(type_result, int)
        self.assertTrue(1 <= type_result <= 5)
    
    def test_find_subtrace_cyclic2(self):
        """Test find_subtrace method with cyclic2 algebra."""
        alg = self.loaded_algebras.get("cyclic2")
        if not alg:
            self.skipTest("cyclic2 algebra not available")
        
        tf = self.TypeFinder(alg)
        tf.init()
        
        # Get join irreducibles
        con = alg.con()
        jis = con.join_irreducibles()
        
        if not jis:
            self.skipTest("No join irreducibles found")
        
        # Test first join irreducible
        ji = jis[0]
        subtrace = tf.find_subtrace(ji)
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("find_subtrace", ["--algebra", "resources/algebras/cyclic2.ua", "--ji_index", "0"])
        java_data = java_result["data"]
        
        self.assertEqual(subtrace.first(), java_data["first"])
        self.assertEqual(subtrace.second(), java_data["second"])
        self.assertEqual(subtrace.has_involution(), java_data["has_involution"])
        self.assertEqual(subtrace.type(), java_data["type"])
    
    def test_find_subtrace_cyclic3(self):
        """Test find_subtrace method with cyclic3 algebra."""
        alg = self.loaded_algebras.get("cyclic3")
        if not alg:
            self.skipTest("cyclic3 algebra not available")
        
        tf = self.TypeFinder(alg)
        tf.init()
        
        # Get join irreducibles
        con = alg.con()
        jis = con.join_irreducibles()
        
        if not jis:
            self.skipTest("No join irreducibles found")
        
        # Test first join irreducible
        ji = jis[0]
        subtrace = tf.find_subtrace(ji)
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("find_subtrace", ["--algebra", "resources/algebras/cyclic3.ua", "--ji_index", "0"])
        java_data = java_result["data"]
        
        self.assertEqual(subtrace.first(), java_data["first"])
        self.assertEqual(subtrace.second(), java_data["second"])
        self.assertEqual(subtrace.has_involution(), java_data["has_involution"])
        self.assertEqual(subtrace.type(), java_data["type"])
    
    def test_is_subtrace_cyclic2(self):
        """Test is_subtrace method with cyclic2 algebra."""
        alg = self.loaded_algebras.get("cyclic2")
        if not alg:
            self.skipTest("cyclic2 algebra not available")
        
        tf = self.TypeFinder(alg)
        tf.init()
        
        # Get join irreducibles
        con = alg.con()
        jis = con.join_irreducibles()
        
        if not jis:
            self.skipTest("No join irreducibles found")
        
        # Test first join irreducible
        ji = jis[0]
        
        # Test pair (0, 1) - need to create IntArray
        IntArray = uacalc_lib.util.IntArray
        pair = IntArray.from_array([0, 1])
        is_subtrace = tf.is_subtrace(pair, ji)
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("is_subtrace", ["--algebra", "resources/algebras/cyclic2.ua", "--ji_index", "0", "--a", "0", "--b", "1"])
        java_is_subtrace = java_result["data"]["is_subtrace"]
        
        self.assertEqual(is_subtrace, java_is_subtrace)
        self.assertIsInstance(is_subtrace, bool)
    
    def test_is_subtrace_cyclic3(self):
        """Test is_subtrace method with cyclic3 algebra."""
        alg = self.loaded_algebras.get("cyclic3")
        if not alg:
            self.skipTest("cyclic3 algebra not available")
        
        tf = self.TypeFinder(alg)
        tf.init()
        
        # Get join irreducibles
        con = alg.con()
        jis = con.join_irreducibles()
        
        if not jis:
            self.skipTest("No join irreducibles found")
        
        # Test first join irreducible
        ji = jis[0]
        
        # Test pair (0, 1) - need to create IntArray
        IntArray = uacalc_lib.util.IntArray
        pair = IntArray.from_array([0, 1])
        is_subtrace = tf.is_subtrace(pair, ji)
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("is_subtrace", ["--algebra", "resources/algebras/cyclic3.ua", "--ji_index", "0", "--a", "0", "--b", "1"])
        java_is_subtrace = java_result["data"]["is_subtrace"]
        
        self.assertEqual(is_subtrace, java_is_subtrace)
        self.assertIsInstance(is_subtrace, bool)
    
    def test_multiple_join_irreducibles(self):
        """Test TypeFinder with algebras that have multiple join irreducibles."""
        for name, alg in self.loaded_algebras.items():
            with self.subTest(algebra=name):
                tf = self.TypeFinder(alg)
                tf.init()
                
                # Get join irreducibles
                con = alg.con()
                jis = con.join_irreducibles()
                
                if len(jis) > 1:
                    # Test multiple join irreducibles
                    for i, ji in enumerate(jis):
                        with self.subTest(ji_index=i):
                            try:
                                # Test find_type - catch ValueError if not join irreducible
                                type_result = tf.find_type(ji)
                                self.assertIsInstance(type_result, int)
                                self.assertTrue(1 <= type_result <= 5)
                                
                                # Test find_subtrace - catch ValueError if not join irreducible
                                subtrace = tf.find_subtrace(ji)
                                self.assertIsNotNone(subtrace)
                                self.assertIsInstance(subtrace.first(), int)
                                self.assertIsInstance(subtrace.second(), int)
                                self.assertIsInstance(subtrace.has_involution(), bool)
                                self.assertIsInstance(subtrace.type(), int)
                            except ValueError as e:
                                if "is not join irreducible" in str(e):
                                    # FAIL the test if join_irreducibles() returns non-join-irreducible partitions
                                    self.fail(f"join_irreducibles() returned a non-join-irreducible partition {ji}: {e}")
                                else:
                                    # Re-raise other ValueError exceptions
                                    raise
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        if not self.loaded_algebras:
            self.skipTest("No test algebras available")
        
        alg = list(self.loaded_algebras.values())[0]
        tf = self.TypeFinder(alg)
        tf.init()
        
        # Test with invalid partition (should handle gracefully)
        try:
            # Create an invalid partition - this should be handled by the implementation
            invalid_partition = None  # This would need to be a proper Partition object
            # The actual test would depend on how Partition validation works
            pass
        except Exception:
            # Expected to fail with invalid input
            pass
    
    def test_string_representations(self):
        """Test string representations."""
        if not self.loaded_algebras:
            self.skipTest("No test algebras available")
        
        alg = list(self.loaded_algebras.values())[0]
        tf = self.TypeFinder(alg)
            
        str_repr = str(tf)
        self.assertIn("TypeFinder", str_repr)
        
        repr_str = repr(tf)
        self.assertIn("TypeFinder", repr_str)


if __name__ == '__main__':
    unittest.main()
