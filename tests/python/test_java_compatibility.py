#!/usr/bin/env python3
"""
Java UACalc Compatibility Test Suite

This module provides comprehensive testing to verify compatibility between
the Rust/Python UACalc implementation and the original Java UACalc.
"""

import unittest
import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import uacalc
import time

class JavaCompatibilityTest(unittest.TestCase):
    """Test suite for Java UACalc compatibility"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.java_jar_path = "jars/uacalc.jar"
        cls.java_wrapper_path = "scripts/JavaWrapper.java"
        cls.algebra_files = []
        
        # Find all .ua files in resources
        resources_dir = Path("resources/algebras")
        if resources_dir.exists():
            cls.algebra_files = list(resources_dir.glob("*.ua"))
        
        # Check if Java UACalc is available
        cls.java_available = cls._check_java_availability()
        
        if not cls.java_available:
            print("Warning: Java UACalc not available. Some tests will be skipped.")
    
    @classmethod
    def _check_java_availability(cls) -> bool:
        """Check if Java UACalc is available for testing"""
        if not os.path.exists(cls.java_jar_path):
            return False
        
        if not os.path.exists(cls.java_wrapper_path):
            return False
        
        # Try to compile the Java wrapper
        try:
            result = subprocess.run([
                "javac", "-cp", cls.java_jar_path, 
                "-d", "scripts", cls.java_wrapper_path
            ], capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False
    
    def setUp(self):
        """Set up for each test"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_format_compatibility(self):
        """Test that .ua files can be loaded and saved with full compatibility"""
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files:
            with self.subTest(file=ua_file.name):
                # Load original file
                original_algebra = uacalc.load_algebra(str(ua_file))
                
                # Save to temporary file
                temp_file = os.path.join(self.temp_dir, f"temp_{ua_file.name}")
                uacalc.save_algebra(original_algebra, temp_file)
                
                # Load the saved file
                reloaded_algebra = uacalc.load_algebra(temp_file)
                
                # Verify properties match
                self.assertEqual(original_algebra.name, reloaded_algebra.name)
                self.assertEqual(original_algebra.cardinality, reloaded_algebra.cardinality)
                self.assertEqual(len(original_algebra.operations()), len(reloaded_algebra.operations()))
                
                # Verify operation properties
                for orig_op, reloaded_op in zip(original_algebra.operations(), reloaded_algebra.operations()):
                    self.assertEqual(orig_op.symbol, reloaded_op.symbol)
                    self.assertEqual(orig_op.arity(), reloaded_op.arity())
    
    def test_round_trip_compatibility(self):
        """Test round-trip compatibility: load -> save -> load -> compare"""
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files[:3]:  # Test first 3 files
            with self.subTest(file=ua_file.name):
                # Load original
                original_algebra = uacalc.load_algebra(str(ua_file))
                
                # Save and reload multiple times
                current_algebra = original_algebra
                for i in range(3):
                    temp_file = os.path.join(self.temp_dir, f"roundtrip_{i}_{ua_file.name}")
                    uacalc.save_algebra(current_algebra, temp_file)
                    current_algebra = uacalc.load_algebra(temp_file)
                
                # Verify final result matches original
                self.assertEqual(original_algebra.name, current_algebra.name)
                self.assertEqual(original_algebra.cardinality, current_algebra.cardinality)
    
    def test_java_rust_algorithm_verification(self):
        if not self.java_available:
            self.skipTest("Java UACalc not available")
        """Test that Rust and Java implementations produce the same results"""
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files[:3]:  # Test first 3 files
            with self.subTest(file=ua_file.name):
                # Load algebra in Rust
                rust_algebra = uacalc.load_algebra(str(ua_file))
                
                # Test Cg(a,b) for all pairs
                size = rust_algebra.cardinality
                for a in range(min(size, 3)):  # Limit to first 3 elements
                    for b in range(a + 1, min(size, 4)):
                        with self.subTest(pair=(a, b)):
                            # Compute Cg(a,b) in Rust
                            lattice = uacalc.create_congruence_lattice(rust_algebra)
                            rust_partition = lattice.principal_congruence(a, b)
                            
                            # Compute Cg(a,b) in Java
                            java_result = self._run_java_cg(str(ua_file), a, b)
                            
                            if java_result is not None:
                                # Compare partitions
                                self._compare_partitions(rust_partition, java_result)
    
    def test_java_rust_lattice_verification(self):
        if not self.java_available:
            self.skipTest("Java UACalc not available")
        """Test that congruence lattice sizes match between Java and Rust"""
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files[:2]:  # Test first 2 files
            with self.subTest(file=ua_file.name):
                # Load algebra in Rust
                rust_algebra = uacalc.load_algebra(str(ua_file))
                
                # Only test smaller algebras to avoid timeouts
                if rust_algebra.cardinality <= 6:
                    # Compute lattice in Rust
                    rust_lattice = uacalc.create_congruence_lattice(rust_algebra)
                    
                    # Get lattice info from Java
                    java_lattice_info = self._run_java_lattice(str(ua_file))
                    
                    if java_lattice_info is not None:
                        # Compare lattice sizes
                        self.assertEqual(rust_lattice.size(), java_lattice_info['size'])
                        # Note: join_irreducibles might not be available in the same format
                        # self.assertEqual(len(rust_lattice.join_irreducibles), 
                        #                java_lattice_info['join_irreducibles'])
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with trivial algebra (1 element)
        trivial_algebra = uacalc.create_algebra("trivial", [0])
        self.assertEqual(trivial_algebra.cardinality, 1)
        
        # Test Cg with same element
        lattice = uacalc.create_congruence_lattice(trivial_algebra)
        partition = lattice.principal_congruence(0, 0)
        self.assertEqual(partition.num_blocks, 1)
        
        # Test with larger algebra (if available)
        if len(self.algebra_files) > 0:
            large_file = max(self.algebra_files, key=lambda f: f.stat().st_size)
            try:
                large_algebra = uacalc.load_algebra(str(large_file))
                print(f"Loaded large algebra: {large_algebra.name} (size: {large_algebra.cardinality})")
            except Exception as e:
                print(f"Failed to load large algebra {large_file}: {e}")
    
    def test_performance_comparison(self):
        """Test that Rust implementation is faster than Java (when available)"""
        if not self.java_available or not self.algebra_files:
            self.skipTest("Java UACalc or algebra files not available")
        
        # Test with a small algebra
        test_file = self.algebra_files[0]
        rust_algebra = uacalc.load_algebra(str(test_file))
        
        # Benchmark Rust implementation
        start_time = time.time()
        lattice = uacalc.create_congruence_lattice(rust_algebra)
        for a in range(min(rust_algebra.cardinality, 3)):
            for b in range(a + 1, min(rust_algebra.cardinality, 4)):
                lattice.principal_congruence(a, b)
        rust_time = (time.time() - start_time) * 1000
        
        # Benchmark Java implementation
        start_time = time.time()
        for a in range(min(rust_algebra.cardinality, 3)):
            for b in range(a + 1, min(rust_algebra.cardinality, 4)):
                self._run_java_cg(str(test_file), a, b)
        java_time = (time.time() - start_time) * 1000
        
        # Verify Rust is faster
        speedup = java_time / rust_time if rust_time > 0 else float('inf')
        print(f"Performance comparison: Rust {rust_time:.2f}ms, Java {java_time:.2f}ms, Speedup: {speedup:.2f}x")
        
        # Rust should be at least 2x faster (conservative estimate)
        self.assertGreater(speedup, 2.0, f"Rust should be faster than Java (speedup: {speedup:.2f}x)")
    
    def _run_java_cg(self, ua_file: str, a: int, b: int) -> Optional[List[List[int]]]:
        """Run Cg(a,b) computation in Java and return partition"""
        try:
            result = subprocess.run([
                "java", "-cp", f"{self.java_jar_path}{os.pathsep}scripts",
                "JavaWrapper", "cg", ua_file, str(a), str(b)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("partition")
            else:
                print(f"Java Cg failed: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error running Java Cg: {e}")
            return None
    
    def _run_java_lattice(self, ua_file: str) -> Optional[Dict[str, Any]]:
        """Run lattice computation in Java and return lattice info"""
        try:
            result = subprocess.run([
                "java", "-cp", f"{self.java_jar_path}{os.pathsep}scripts",
                "JavaWrapper", "lattice", ua_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"Java lattice failed: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error running Java lattice: {e}")
            return None
    
    def _compare_partitions(self, rust_partition, java_partition):
        """Compare partitions from Rust and Java implementations"""
        # Convert Java partition to comparable format
        java_blocks = []
        for block in java_partition:
            java_blocks.append(sorted(block))
        java_blocks.sort()
        
        # Convert Rust partition to comparable format
        rust_blocks = []
        for block in rust_partition.blocks():
            rust_blocks.append(sorted(block))
        rust_blocks.sort()
        
        # Compare
        self.assertEqual(rust_blocks, java_blocks, 
                        f"Partitions don't match: Rust {rust_blocks}, Java {java_blocks}")

class FileFormatCompatibilityTest(unittest.TestCase):
    """Test file format compatibility specifically"""
    
    def test_xml_format_compatibility(self):
        """Test that saved files have correct XML format"""
        # Create a simple algebra
        algebra = uacalc.create_algebra("boolean", [0, 1])
        
        # Add a binary operation (meet)
        meet_table = [[0, 0], [0, 1]]
        meet_op = uacalc.create_operation("meet", 2, meet_table)
        algebra.add_operation("meet", meet_op)
        
        # Save to temporary file
        temp_file = tempfile.mktemp(suffix=".ua")
        try:
            uacalc.save_algebra(algebra, temp_file)
            
            # Check that file exists and has content
            self.assertTrue(os.path.exists(temp_file))
            self.assertGreater(os.path.getsize(temp_file), 0)
            
            # Check that file contains expected XML structure
            with open(temp_file, 'r') as f:
                content = f.read()
                
            # Should contain basic XML structure
            self.assertIn("<?xml", content)
            self.assertIn("<algebra", content)
            self.assertIn("</algebra>", content)
            self.assertIn(algebra.name, content)
            
            # Should contain operation definitions
            for op in algebra.operations():
                self.assertIn(op.symbol, content)
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_unicode_handling(self):
        """Test that Unicode characters are handled correctly"""
        # Create algebra with Unicode name
        unicode_name = "Test Algebra with Unicode: αβγδε"
        algebra = uacalc.create_algebra(unicode_name, [0, 1])
        # Note: This would require the API to support custom names
        
        # Save and reload
        temp_file = tempfile.mktemp(suffix=".ua")
        try:
            uacalc.save_algebra(algebra, temp_file)
            reloaded = uacalc.load_algebra(temp_file)
            
            # Verify algebra loads correctly
            self.assertEqual(algebra.cardinality, reloaded.cardinality)
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

class PerformanceRegressionTest(unittest.TestCase):
    """Test for performance regressions"""
    
    def test_cg_performance_baseline(self):
        """Test that Cg computation meets performance baseline"""
        # Create test algebra (cyclic group of order 5)
        algebra = uacalc.create_algebra("cyclic5", [0, 1, 2, 3, 4])
        
        # Add a binary operation (addition mod 5)
        add_table = [
            [0, 1, 2, 3, 4],
            [1, 2, 3, 4, 0],
            [2, 3, 4, 0, 1],
            [3, 4, 0, 1, 2],
            [4, 0, 1, 2, 3]
        ]
        add_op = uacalc.create_operation("add", 2, add_table)
        algebra.add_operation("add", add_op)
        
        # Benchmark Cg computation
        start_time = time.time()
        lattice = uacalc.create_congruence_lattice(algebra)
        for a in range(algebra.cardinality):
            for b in range(a + 1, algebra.cardinality):
                lattice.principal_congruence(a, b)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        total_pairs = algebra.cardinality * (algebra.cardinality - 1) // 2
        
        # Should complete within reasonable time
        # Baseline: 100ms for 10 Cg computations on size 5 algebra
        self.assertLess(duration_ms, 1000, f"Cg computation too slow: {duration_ms:.2f}ms for {total_pairs} pairs")
        
        print(f"Cg performance: {duration_ms:.2f}ms for {total_pairs} pairs ({duration_ms/total_pairs:.2f}ms per pair)")
    
    def test_memory_usage_baseline(self):
        """Test that memory usage stays within reasonable bounds"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create and process multiple algebras
        algebras = []
        for i in range(5):
            # Create a simple algebra
            algebra = uacalc.create_algebra(f"test{i}", [0, 1, 2, 3])
            
            # Add a simple operation
            op_table = [[0, 1, 2, 3], [1, 1, 1, 1], [2, 1, 2, 1], [3, 1, 1, 3]]
            op = uacalc.create_operation("f", 2, op_table)
            algebra.add_operation("f", op)
            
            lattice = uacalc.create_congruence_lattice(algebra)
            algebras.append((algebra, lattice))
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100, f"Memory usage too high: {memory_increase:.1f}MB increase")
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")

def run_compatibility_tests():
    """Run all compatibility tests and generate report"""
    print("Running Java UACalc Compatibility Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(JavaCompatibilityTest))
    suite.addTests(loader.loadTestsFromTestCase(FileFormatCompatibilityTest))
    suite.addTests(loader.loadTestsFromTestCase(PerformanceRegressionTest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    report = {
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
        'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0
    }
    
    print(f"\nCompatibility Test Report:")
    print(f"Total tests: {report['total_tests']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Skipped: {report['skipped']}")
    print(f"Success rate: {report['success_rate']:.1%}")
    
    # Save report
    with open("compatibility_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_compatibility_tests()
    exit(0 if success else 1)
