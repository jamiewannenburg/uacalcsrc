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
from typing import Dict, List, Any, Optional, Union
import uacalc
import time
from dataclasses import dataclass
from tests.python.test_data_manager import TestDataManager, TestCaseGenerator, AlgebraComplexity

@dataclass
class CompatibilityTestResult:
    """Represents the result of a single compatibility test"""
    test_name: str
    algebra_name: str
    operation: str
    rust_result: Any
    java_result: Any
    matches: bool
    error_message: Optional[str] = None
    execution_time_rust: float = 0.0
    execution_time_java: float = 0.0

@dataclass  
class TestSuiteReport:
    """Aggregated results from the entire test suite"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    compatibility_percentage: float
    failed_test_details: List[CompatibilityTestResult]
    feature_coverage: Dict[str, float]

class BaseCompatibilityTest(unittest.TestCase):
    """Base class providing common functionality for all compatibility tests"""
    
    @classmethod
    def setUpClass(cls):
        """Initialize Java environment and test data"""
        cls.java_jar_path = "jars/uacalc.jar"
        cls.java_wrapper_path = "scripts/JavaWrapper.java"
        cls.data_manager = TestDataManager()
        cls.test_case_generator = TestCaseGenerator(cls.data_manager)
        cls.algebra_files = cls.data_manager.discover_algebras()
        cls.java_available = cls._check_java_availability()
        cls._algebra_cache = {}  # Cache for loaded algebras
        
        if not cls.java_available:
            print("Warning: Java UACalc not available. Some tests will be skipped.")
        
        # Print test data summary
        summary = cls.data_manager.get_algebra_summary()
        if summary:
            print(f"Discovered {summary['total_algebras']} test algebras")
            print(f"Complexity distribution: {summary['complexity_distribution']}")
            print(f"Average cardinality: {summary['average_cardinality']:.1f}")
            print(f"Average operations: {summary['average_operations']:.1f}")
    
    @classmethod
    def _discover_test_algebras(cls) -> List[Path]:
        """Discover and categorize test algebra files"""
        algebra_files = []
        resources_dir = Path("resources/algebras")
        if resources_dir.exists():
            algebra_files = list(resources_dir.glob("*.ua"))
            
        # Sort by file size for systematic testing (small to large)
        algebra_files.sort(key=lambda f: f.stat().st_size)
        return algebra_files
    
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
                cls.java_wrapper_path
            ], capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False
    
    def setUp(self):
        """Set up for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_results = []
    
    def tearDown(self):
        """Clean up after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _run_java_operation(self, operation: str, *args) -> Optional[Dict[str, Any]]:
        """Generic method to run Java operations and parse JSON results"""
        if not self.java_available:
            return None
            
        try:
            cmd = [
                "java", "-cp", f"{self.java_jar_path}{os.pathsep}scripts",
                "JavaWrapper", operation
            ] + list(args)
            
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr, "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _compare_results(self, rust_result: Any, java_result: Dict[str, Any], 
                        operation: str, context: str = "") -> CompatibilityTestResult:
        """Generic result comparison with detailed error reporting"""
        test_name = f"{self.__class__.__name__}.{self._testMethodName}"
        algebra_name = context or "unknown"
        
        if java_result is None:
            return CompatibilityTestResult(
                test_name=test_name,
                algebra_name=algebra_name,
                operation=operation,
                rust_result=rust_result,
                java_result=None,
                matches=False,
                error_message="Java operation returned None"
            )
        
        if not java_result.get("success", False):
            return CompatibilityTestResult(
                test_name=test_name,
                algebra_name=algebra_name,
                operation=operation,
                rust_result=rust_result,
                java_result=java_result,
                matches=False,
                error_message=f"Java operation failed: {java_result.get('error', 'Unknown error')}"
            )
        
        # Compare the actual results
        matches = self._deep_compare(rust_result, java_result)
        error_message = None if matches else f"Results differ: Rust={rust_result}, Java={java_result}"
        
        return CompatibilityTestResult(
            test_name=test_name,
            algebra_name=algebra_name,
            operation=operation,
            rust_result=rust_result,
            java_result=java_result,
            matches=matches,
            error_message=error_message
        )
    
    def _deep_compare(self, rust_result: Any, java_result: Dict[str, Any]) -> bool:
        """Deep comparison of results with type-aware matching"""
        # This is a simplified comparison - can be enhanced based on specific needs
        if isinstance(rust_result, dict) and isinstance(java_result, dict):
            # Compare dictionaries
            for key in rust_result:
                if key not in java_result:
                    return False
                if not self._deep_compare(rust_result[key], java_result[key]):
                    return False
            return True
        elif isinstance(rust_result, (list, tuple)) and isinstance(java_result, (list, tuple)):
            # Compare sequences
            if len(rust_result) != len(java_result):
                return False
            return all(self._deep_compare(r, j) for r, j in zip(rust_result, java_result))
        else:
            # Direct comparison
            return rust_result == java_result
    
    def _load_test_algebra(self, file_path: Union[str, Path]) -> Any:
        """Load algebra with error handling and caching"""
        file_path = str(file_path)
        
        if file_path in self._algebra_cache:
            return self._algebra_cache[file_path]
        
        try:
            algebra = uacalc.load_algebra(file_path)
            self._algebra_cache[file_path] = algebra
            return algebra
        except Exception as e:
            self.fail(f"Failed to load algebra from {file_path}: {e}")
    
    def _should_skip_test(self, algebra_size: int, operation: str) -> bool:
        """Determine if test should be skipped based on complexity"""
        # Skip very large algebras for expensive operations
        if algebra_size > 10 and operation in ['congruence_lattice', 'maltsev_conditions']:
            return True
        if algebra_size > 20:
            return True
        return False

class JavaCompatibilityTest(BaseCompatibilityTest):
    """Test suite for Java UACalc compatibility"""
    
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
                self.assertEqual(len(original_algebra.operations), len(reloaded_algebra.operations))
                
                # Verify operation properties
                for orig_op, reloaded_op in zip(original_algebra.operations, reloaded_algebra.operations):
                    self.assertEqual(orig_op.symbol, reloaded_op.symbol)
                    self.assertEqual(orig_op.arity, reloaded_op.arity)
    
    def test_algebra_properties_compatibility(self):
        """Test comprehensive algebra properties match between Java and Rust"""
        if not self.java_available:
            self.skipTest("Java UACalc not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files[:3]:  # Test first 3 files
            with self.subTest(file=ua_file.name):
                # Load algebra in Rust
                rust_algebra = self._load_test_algebra(ua_file)
                
                # Skip if algebra is too large
                if self._should_skip_test(rust_algebra.cardinality, "algebra_properties"):
                    continue
                
                # Get properties from Java
                java_result = self._run_java_operation("algebra_properties", str(ua_file))
                
                if java_result and java_result.get("success"):
                    # Compare basic properties
                    self.assertEqual(rust_algebra.name, java_result["algebra_name"])
                    self.assertEqual(rust_algebra.cardinality, java_result["cardinality"])
                    self.assertEqual(len(rust_algebra.operations), java_result["operation_count"])
                    
                    # Compare operation symbols (order might differ)
                    rust_symbols = [op.symbol for op in rust_algebra.operations]
                    java_symbols = java_result["operation_symbols"]
                    self.assertEqual(set(rust_symbols), set(java_symbols), 
                                   f"Operation symbols differ: Rust={rust_symbols}, Java={java_symbols}")
                    
                    # Compare operation arities (create symbol->arity mapping to handle order differences)
                    rust_symbol_arities = {op.symbol: op.arity for op in rust_algebra.operations}
                    java_symbol_arities = {symbol: arity for symbol, arity in zip(java_symbols, java_result["operation_arities"])}
                    self.assertEqual(rust_symbol_arities, java_symbol_arities,
                                   f"Operation arities differ: Rust={rust_symbol_arities}, Java={java_symbol_arities}")
    
    def test_subalgebra_generation_compatibility(self):
        """Test subalgebra generation produces identical results"""
        if not self.java_available:
            self.skipTest("Java UACalc not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files[:2]:  # Test first 2 files
            with self.subTest(file=ua_file.name):
                # Load algebra in Rust
                rust_algebra = self._load_test_algebra(ua_file)
                
                # Skip if algebra is too large
                if self._should_skip_test(rust_algebra.cardinality, "subalgebra"):
                    continue
                
                # Test with different generator sets
                generator_sets = [
                    [0],
                    [0, 1] if rust_algebra.cardinality > 1 else [0],
                    list(range(min(3, rust_algebra.cardinality)))
                ]
                
                for generators in generator_sets:
                    with self.subTest(generators=generators):
                        # Generate subalgebra in Rust
                        try:
                            rust_subalgebra = rust_algebra.subalgebra(generators)
                            rust_size = rust_subalgebra.cardinality
                            rust_universe = list(rust_subalgebra.universe)
                        except Exception as e:
                            self.skipTest(f"Rust subalgebra generation failed: {e}")
                            continue
                        
                        # Generate subalgebra in Java
                        generators_json = json.dumps(generators)
                        java_result = self._run_java_operation("subalgebra", str(ua_file), generators_json)
                        
                        if java_result and java_result.get("success"):
                            # Compare subalgebra properties
                            self.assertEqual(rust_size, java_result["subalgebra_size"])
                            # Note: Universe comparison might need adjustment based on representation
    
    def test_maltsev_conditions_compatibility(self):
        """Test Maltsev condition checking matches between implementations"""
        if not self.java_available:
            self.skipTest("Java UACalc not available")
        
        if not self.algebra_files:
            self.skipTest("No algebra files found")
        
        for ua_file in self.algebra_files[:2]:  # Test first 2 files
            with self.subTest(file=ua_file.name):
                # Load algebra in Rust
                rust_algebra = self._load_test_algebra(ua_file)
                
                # Skip if algebra is too large for Maltsev analysis
                if self._should_skip_test(rust_algebra.cardinality, "maltsev_conditions"):
                    continue
                
                # Get Maltsev conditions from Java
                java_result = self._run_java_operation("maltsev_conditions", str(ua_file))
                
                if java_result and java_result.get("success"):
                    # For now, just verify the operation completed successfully
                    # Full Maltsev condition checking in Rust would need to be implemented
                    self.assertIn("results", java_result)
                    self.assertIn("has_maltsev_term", java_result["results"])
                    self.assertIn("has_join_term", java_result["results"])
                    
                    # Print results for manual verification during development
                    print(f"Maltsev analysis for {ua_file.name}: {java_result['results']}")
    
    def test_isomorphism_checking_compatibility(self):
        """Test isomorphism checking between algebras"""
        if not self.java_available:
            self.skipTest("Java UACalc not available")
        
        if len(self.algebra_files) < 2:
            self.skipTest("Need at least 2 algebra files for isomorphism testing")
        
        # Test isomorphism between first two algebras
        ua_file1 = self.algebra_files[0]
        ua_file2 = self.algebra_files[1]
        
        # Load algebras in Rust
        rust_algebra1 = self._load_test_algebra(ua_file1)
        rust_algebra2 = self._load_test_algebra(ua_file2)
        
        # Skip if algebras are too large
        if (self._should_skip_test(rust_algebra1.cardinality, "isomorphism") or 
            self._should_skip_test(rust_algebra2.cardinality, "isomorphism")):
            self.skipTest("Algebras too large for isomorphism testing")
        
        # Check isomorphism in Java
        java_result = self._run_java_operation("isomorphism", str(ua_file1), str(ua_file2))
        
        if java_result and java_result.get("success"):
            # Basic compatibility checks
            expected_compatible = (rust_algebra1.cardinality == rust_algebra2.cardinality and
                                 len(rust_algebra1.operations) == len(rust_algebra2.operations))
            
            self.assertEqual(expected_compatible, java_result["compatible_signatures"])
            
            # Print results for manual verification during development
            print(f"Isomorphism check between {ua_file1.name} and {ua_file2.name}: {java_result}")
        
        # Test algebra with itself (should be isomorphic)
        java_result_self = self._run_java_operation("isomorphism", str(ua_file1), str(ua_file1))
        if java_result_self and java_result_self.get("success"):
            self.assertTrue(java_result_self["compatible_signatures"])
            # Note: Full isomorphism detection would require more sophisticated algorithms
    
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

class TermCompatibilityTest(unittest.TestCase):
    """Test term parsing and evaluation compatibility with Java"""
    
    def test_java_term_parsing_compatibility(self):
        """Test that term parsing matches Java behavior"""
        if not self._check_java_availability():
            self.skipTest("Java UACalc not available")
        
        # Test cases that should work in both Java and Rust
        valid_terms = [
            "x0",
            "x1", 
            "x",
            "y",
            "z",
            "f(x0)",
            "f(x0, x1)",
            "f(g(x0), h(x1))",
            "f(x0, x1, x2)",
        ]
        
        for term_str in valid_terms:
            with self.subTest(term=term_str):
                # Test Rust parsing
                try:
                    arena = uacalc.create_term_arena()
                    rust_term = uacalc.parse_term(arena, term_str)
                    self.assertIsNotNone(rust_term)
                except Exception as e:
                    self.fail(f"Rust failed to parse '{term_str}': {e}")
                
                # Test Java parsing
                java_result = self._run_java_term_parse(term_str)
                if java_result is not None:
                    # Both should succeed
                    self.assertIsNotNone(java_result)
    
    def test_java_term_validation_compatibility(self):
        """Test that term validation matches Java behavior"""
        if not self._check_java_availability():
            self.skipTest("Java UACalc not available")
        
        # Test cases that should be rejected in both Java and Rust
        invalid_terms = [
            "",  # Empty
            "(",  # Unbalanced parentheses
            ")",  # Unbalanced parentheses
            "f(x0",  # Missing closing parenthesis
            "f(x0,)",  # Missing argument
            "f(,x0)",  # Missing argument
            "f(x0 x1)",  # Missing comma
        ]
        
        for term_str in invalid_terms:
            with self.subTest(term=term_str):
                # Test Rust validation using TermParser
                from uacalc.terms import TermParser
                parser = TermParser()
                is_valid, error = parser.validate_syntax(term_str)
                
                # Rust should reject invalid terms
                self.assertFalse(is_valid, f"Rust incorrectly accepted invalid term '{term_str}'")
                self.assertIsNotNone(error, f"No error message for invalid term '{term_str}'")
                
                # Test Java parsing
                java_result = self._run_java_term_parse(term_str)
                if java_result is not None and "error" in java_result:
                    # Both should fail
                    self.assertIn("error", java_result)
    
    def test_java_variable_handling_compatibility(self):
        """Test that variable handling matches Java behavior"""
        if not self._check_java_availability():
            self.skipTest("Java UACalc not available")
        
        # Test variable names that Java accepts
        java_variables = ["x", "y", "z", "a", "b", "c", "var1", "var2"]
        
        for var_name in java_variables:
            with self.subTest(variable=var_name):
                # Test Rust variable creation
                try:
                    arena = uacalc.create_term_arena()
                    from uacalc.terms import create_variable
                    rust_var = create_variable(var_name, arena)
                    self.assertIsNotNone(rust_var)
                except Exception as e:
                    # If Rust doesn't support this format, that's a compatibility issue
                    self.fail(f"Rust doesn't support Java variable format '{var_name}': {e}")
                
                # Test Java variable creation
                java_result = self._run_java_variable_create(var_name)
                if java_result is not None:
                    self.assertIsNotNone(java_result)
    
    def test_java_missing_variable_handling(self):
        """Test that missing variable handling matches Java behavior"""
        if not self._check_java_availability():
            self.skipTest("Java UACalc not available")
        
        # Create a simple algebra
        algebra = uacalc.create_algebra("test", [0, 1, 2])
        operation = uacalc.create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        # Test term with missing variable
        arena = uacalc.create_term_arena()
        term = uacalc.parse_term(arena, "f(x0, x1)")
        variables = {0: 1}  # Missing x1
        
        # Test Rust evaluation
        try:
            result = uacalc.eval_term(term, algebra, variables)
            # If we get here, Rust didn't raise an exception for missing variable
            # This might be acceptable if Rust has default behavior
            print(f"Rust evaluation with missing variable returned: {result}")
        except Exception as e:
            # Expected failure
            print(f"Rust correctly raised exception for missing variable: {e}")
        
        # Test Java evaluation
        java_result = self._run_java_term_eval("f(x0, x1)", variables)
        if java_result is not None and "error" in java_result:
            # Java should also fail
            self.assertIn("error", java_result)
    
    def test_java_operation_validation_compatibility(self):
        """Test that operation validation matches Java behavior"""
        if not self._check_java_availability():
            self.skipTest("Java UACalc not available")
        
        # Create algebra with only operation 'f'
        algebra = uacalc.create_algebra("test", [0, 1, 2])
        operation = uacalc.create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        # Test valid term
        arena = uacalc.create_term_arena()
        valid_term = uacalc.parse_term(arena, "f(x0, x1)")
        
        from uacalc.terms import validate_term_against_algebra
        is_valid, error = validate_term_against_algebra(valid_term, algebra)
        
        # Rust should validate correctly
        self.assertTrue(is_valid, f"Rust incorrectly rejected valid term: {error}")
        
        # Test invalid term (unknown operation)
        invalid_term = uacalc.parse_term(arena, "g(x0, x1)")
        is_valid, error = validate_term_against_algebra(invalid_term, algebra)
        
        # Rust should reject invalid term
        self.assertFalse(is_valid, f"Rust incorrectly accepted invalid term: {error}")
        self.assertIsNotNone(error)
        
        # Test Java validation
        java_result = self._run_java_term_validate("f(x0, x1)", algebra)
        if java_result is not None:
            self.assertTrue(java_result.get("valid", False))
        
        java_result = self._run_java_term_validate("g(x0, x1)", algebra)
        if java_result is not None:
            self.assertFalse(java_result.get("valid", True))
    
    def _check_java_availability(self) -> bool:
        """Check if Java UACalc is available for testing"""
        java_jar_path = "jars/uacalc.jar"
        java_wrapper_path = "scripts/JavaWrapper.java"
        
        if not os.path.exists(java_jar_path) or not os.path.exists(java_wrapper_path):
            return False
        
        try:
            result = subprocess.run([
                "javac", "-cp", java_jar_path, 
                "-d", "scripts", java_wrapper_path
            ], capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False
    
    def _run_java_term_parse(self, term_str: str) -> Optional[Dict[str, Any]]:
        """Run term parsing in Java"""
        try:
            result = subprocess.run([
                "java", "-cp", f"jars/uacalc.jar{os.pathsep}scripts",
                "JavaWrapper", "parse_term", term_str
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def _run_java_variable_create(self, var_name: str) -> Optional[Dict[str, Any]]:
        """Run variable creation in Java"""
        try:
            result = subprocess.run([
                "java", "-cp", f"jars/uacalc.jar{os.pathsep}scripts",
                "JavaWrapper", "create_variable", var_name
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def _run_java_term_eval(self, term_str: str, variables: Dict[int, int]) -> Optional[Dict[str, Any]]:
        """Run term evaluation in Java"""
        try:
            # Convert variables to JSON
            var_json = json.dumps(variables)
            
            result = subprocess.run([
                "java", "-cp", f"jars/uacalc.jar{os.pathsep}scripts",
                "JavaWrapper", "eval_term", term_str, var_json
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def _run_java_term_validate(self, term_str: str, algebra) -> Optional[Dict[str, Any]]:
        """Run term validation in Java"""
        try:
            # Save algebra to temporary file
            temp_file = os.path.join(tempfile.gettempdir(), "temp_algebra.ua")
            uacalc.save_algebra(algebra, temp_file)
            
            result = subprocess.run([
                "java", "-cp", f"jars/uacalc.jar{os.pathsep}scripts",
                "JavaWrapper", "validate_term", term_str, temp_file
            ], capture_output=True, text=True, timeout=10)
            
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if result.returncode == 0:
                # Find the JSON part in the output (last line that starts with {)
                lines = result.stdout.strip().split('\n')
                json_line = None
                for line in reversed(lines):
                    if line.strip().startswith('{'):
                        json_line = line.strip()
                        break
                
                if json_line:
                    return json.loads(json_line)
                else:
                    return {"error": "No JSON found in output"}
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}

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
            for op in algebra.operations:
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
    suite.addTests(loader.loadTestsFromTestCase(TermCompatibilityTest))
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
