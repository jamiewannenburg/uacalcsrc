#!/usr/bin/env python3
"""
Base Compatibility Test Infrastructure

This module provides the foundational infrastructure for comprehensive Java UACalc
compatibility testing, including Java environment setup, generic operation execution,
result comparison, and error reporting.
"""

import unittest
import os
import json
import subprocess
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

# Configure logging for detailed test reporting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    context: Optional[str] = None

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
    execution_time_total: float
    resource_statistics: Optional[Dict[str, Any]] = None

class JavaEnvironmentError(Exception):
    """Raised when Java environment is not properly configured"""
    pass

class ResultComparisonError(Exception):
    """Raised when result comparison fails"""
    pass

class BaseCompatibilityTest(unittest.TestCase):
    """
    Base class providing common functionality for all compatibility tests.
    
    This class provides:
    - Java environment setup and validation
    - Generic Java operation execution with timeout and error handling
    - Comprehensive result comparison with detailed diff reporting
    - Test algebra loading with caching and error handling
    - Structured error reporting and logging
    """
    
    # Class-level configuration
    JAVA_TIMEOUT_DEFAULT = 60  # seconds
    JAVA_TIMEOUT_LONG = 300    # seconds for complex operations
    JAVA_TIMEOUT_SHORT = 30    # seconds for simple operations
    
    @classmethod
    def setUpClass(cls):
        """Initialize Java environment and test infrastructure"""
        cls.java_jar_path = "jars/uacalc.jar"
        cls.java_wrapper_path = "scripts/JavaWrapper.java"
        cls.java_wrapper_class = "scripts/JavaWrapper.class"
        
        # Initialize test data management
        try:
            from tests.python.test_data_manager import TestDataManager, TestCaseGenerator
            cls.data_manager = TestDataManager()
            cls.test_case_generator = TestCaseGenerator(cls.data_manager)
            cls.algebra_files = cls.data_manager.discover_algebras()
        except ImportError:
            # Fallback if test data manager is not available
            cls.data_manager = None
            cls.test_case_generator = None
            cls.algebra_files = cls._discover_test_algebras_fallback()
        
        # Initialize caches and state
        cls._algebra_cache = {}  # Cache for loaded algebras
        cls._java_compilation_cache = {}  # Cache for Java compilation status
        cls.test_results_history = []  # History of all test results
        
        # Validate Java environment
        cls.java_available = cls._setup_java_environment()
        
        if not cls.java_available:
            logger.warning("Java UACalc not available. Some tests will be skipped.")
        else:
            logger.info("Java UACalc environment successfully initialized")
        
        # Print test data summary
        if cls.data_manager:
            summary = cls.data_manager.get_algebra_summary()
            if summary:
                logger.info(f"Discovered {summary['total_algebras']} test algebras")
                logger.info(f"Complexity distribution: {summary['complexity_distribution']}")
                logger.info(f"Average cardinality: {summary['average_cardinality']:.1f}")
                logger.info(f"Average operations: {summary['average_operations']:.1f}")
        else:
            logger.info(f"Discovered {len(cls.algebra_files)} test algebras (fallback mode)")
    
    @classmethod
    def _setup_java_environment(cls) -> bool:
        """Set up and validate Java environment for testing"""
        try:
            # Check if Java is available
            if not cls._check_java_installation():
                logger.error("Java installation not found")
                return False
            
            # Check if UACalc jar exists
            if not os.path.exists(cls.java_jar_path):
                logger.error(f"UACalc jar not found at {cls.java_jar_path}")
                return False
            
            # Check if JavaWrapper source exists
            if not os.path.exists(cls.java_wrapper_path):
                logger.error(f"JavaWrapper source not found at {cls.java_wrapper_path}")
                return False
            
            # Compile JavaWrapper if needed
            if not cls._ensure_java_wrapper_compiled():
                logger.error("Failed to compile JavaWrapper")
                return False
            
            # Test basic Java operation
            if not cls._test_basic_java_operation():
                logger.error("Basic Java operation test failed")
                return False
            
            logger.info("Java environment setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Java environment setup failed: {e}")
            return False
    
    @classmethod
    def _check_java_installation(cls) -> bool:
        """Check if Java is properly installed and accessible"""
        try:
            result = subprocess.run(
                ["java", "-version"], 
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.debug(f"Java version: {result.stderr.split()[2]}")
                return True
            return False
        except Exception as e:
            logger.debug(f"Java check failed: {e}")
            return False
    
    @classmethod
    def _ensure_java_wrapper_compiled(cls) -> bool:
        """Ensure JavaWrapper is compiled and up to date"""
        try:
            # Check if compilation is needed
            source_path = Path(cls.java_wrapper_path)
            class_path = Path(cls.java_wrapper_class)
            
            needs_compilation = (
                not class_path.exists() or
                source_path.stat().st_mtime > class_path.stat().st_mtime
            )
            
            if not needs_compilation:
                logger.debug("JavaWrapper already compiled and up to date")
                return True
            
            # Compile JavaWrapper
            logger.info("Compiling JavaWrapper...")
            result = subprocess.run([
                "javac", "-cp", cls.java_jar_path, 
                cls.java_wrapper_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("JavaWrapper compiled successfully")
                return True
            else:
                logger.error(f"JavaWrapper compilation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"JavaWrapper compilation error: {e}")
            return False
    
    @classmethod
    def _test_basic_java_operation(cls) -> bool:
        """Test that basic Java operations work"""
        try:
            # Find a test algebra file
            test_files = list(Path("resources/algebras").glob("*.ua"))
            if not test_files:
                logger.warning("No test algebra files found for Java validation")
                return True  # Skip validation if no test files
            
            test_file = test_files[0]
            
            # Test basic properties operation
            result = subprocess.run([
                "java", "-cp", f"{cls.java_jar_path}{os.pathsep}scripts",
                "JavaWrapper", "properties", str(test_file)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if "name" in data and "cardinality" in data:
                    logger.debug(f"Basic Java operation test passed with {test_file.name}")
                    return True
            
            logger.error(f"Basic Java operation test failed: {result.stderr}")
            return False
            
        except Exception as e:
            logger.error(f"Basic Java operation test error: {e}")
            return False
    
    @classmethod
    def _discover_test_algebras_fallback(cls) -> List[Path]:
        """Fallback method to discover test algebra files"""
        algebra_files = []
        resources_dir = Path("resources/algebras")
        if resources_dir.exists():
            algebra_files = list(resources_dir.glob("*.ua"))
            
        # Sort by file size for systematic testing (small to large)
        algebra_files.sort(key=lambda f: f.stat().st_size)
        return algebra_files
    
    def setUp(self):
        """Set up for each individual test"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_start_time = time.time()
        self.current_test_results = []
        
        # Set up test-specific logging
        self.test_logger = logging.getLogger(f"{self.__class__.__name__}.{self._testMethodName}")
        
    def tearDown(self):
        """Clean up after each test"""
        # Calculate test execution time
        test_duration = time.time() - self.test_start_time
        
        # Log test completion
        self.test_logger.info(f"Test completed in {test_duration:.2f}s")
        
        # Add results to class history
        self.__class__.test_results_history.extend(self.current_test_results)
        
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _run_java_operation(self, operation: str, *args, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Generic method to run Java operations and parse JSON results.
        
        Args:
            operation: The operation name to execute
            *args: Arguments to pass to the Java operation
            timeout: Timeout in seconds (uses default if None)
            
        Returns:
            Dictionary containing the JSON result, or None if Java unavailable
            
        Raises:
            JavaEnvironmentError: If Java environment is not properly set up
        """
        if not self.java_available:
            return None
        
        if timeout is None:
            timeout = self.JAVA_TIMEOUT_DEFAULT
            
        try:
            cmd = [
                "java", "-cp", f"{self.java_jar_path}{os.pathsep}scripts",
                "JavaWrapper", operation
            ] + [str(arg) for arg in args]
            
            self.test_logger.debug(f"Executing Java command: {' '.join(cmd)}")
            
            start_time = time.time()
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                try:
                    json_result = json.loads(result.stdout)
                    json_result['_execution_time'] = execution_time
                    self.test_logger.debug(f"Java operation '{operation}' completed in {execution_time:.3f}s")
                    return json_result
                except json.JSONDecodeError as e:
                    self.test_logger.error(f"Failed to parse Java JSON output: {e}")
                    self.test_logger.debug(f"Raw output: {result.stdout}")
                    return {"error": f"JSON parse error: {e}", "success": False, "raw_output": result.stdout}
            else:
                self.test_logger.warning(f"Java operation '{operation}' failed with return code {result.returncode}")
                return {"error": result.stderr, "success": False, "return_code": result.returncode}
                
        except subprocess.TimeoutExpired:
            self.test_logger.error(f"Java operation '{operation}' timed out after {timeout}s")
            return {"error": f"Operation timed out after {timeout}s", "success": False, "timeout": True}
        except Exception as e:
            self.test_logger.error(f"Java operation '{operation}' failed with exception: {e}")
            return {"error": str(e), "success": False, "exception": str(type(e).__name__)}
    
    def _compare_results(self, rust_result: Any, java_result: Dict[str, Any], 
                        operation: str, context: str = "", tolerance: float = 1e-10) -> CompatibilityTestResult:
        """
        Generic result comparison with detailed error reporting.
        
        Args:
            rust_result: Result from Rust implementation
            java_result: Result from Java implementation (JSON dict)
            operation: Name of the operation being tested
            context: Additional context information (e.g., algebra name)
            tolerance: Tolerance for floating-point comparisons
            
        Returns:
            CompatibilityTestResult with detailed comparison information
        """
        test_name = f"{self.__class__.__name__}.{self._testMethodName}"
        algebra_name = context or "unknown"
        
        # Handle case where Java operation was not available
        if java_result is None:
            result = CompatibilityTestResult(
                test_name=test_name,
                algebra_name=algebra_name,
                operation=operation,
                rust_result=rust_result,
                java_result=None,
                matches=False,
                error_message="Java operation returned None (Java unavailable)",
                context=context
            )
            self.current_test_results.append(result)
            return result
        
        # Handle case where Java operation failed
        if isinstance(java_result, dict) and not java_result.get("success", True):  # Default to True for backward compatibility
            error_msg = java_result.get("error", "Unknown Java error")
            result = CompatibilityTestResult(
                test_name=test_name,
                algebra_name=algebra_name,
                operation=operation,
                rust_result=rust_result,
                java_result=java_result,
                matches=False,
                error_message=f"Java operation failed: {error_msg}",
                execution_time_java=java_result.get('_execution_time', 0.0),
                context=context
            )
            self.current_test_results.append(result)
            return result
        
        # Perform detailed comparison
        try:
            matches, diff_details = self._deep_compare_with_details(rust_result, java_result, tolerance)
            error_message = None if matches else f"Results differ: {diff_details}"
            
            result = CompatibilityTestResult(
                test_name=test_name,
                algebra_name=algebra_name,
                operation=operation,
                rust_result=rust_result,
                java_result=java_result,
                matches=matches,
                error_message=error_message,
                execution_time_java=java_result.get('_execution_time', 0.0) if isinstance(java_result, dict) else 0.0,
                context=context
            )
            
            self.current_test_results.append(result)
            
            if matches:
                self.test_logger.debug(f"Results match for operation '{operation}' on '{algebra_name}'")
            else:
                self.test_logger.warning(f"Results differ for operation '{operation}' on '{algebra_name}': {diff_details}")
            
            return result
            
        except Exception as e:
            error_msg = f"Comparison failed with exception: {e}"
            result = CompatibilityTestResult(
                test_name=test_name,
                algebra_name=algebra_name,
                operation=operation,
                rust_result=rust_result,
                java_result=java_result,
                matches=False,
                error_message=error_msg,
                execution_time_java=java_result.get('_execution_time', 0.0) if isinstance(java_result, dict) else 0.0,
                context=context
            )
            self.current_test_results.append(result)
            self.test_logger.error(f"Result comparison failed: {e}")
            return result
    
    def _deep_compare_with_details(self, rust_result: Any, java_result: Dict[str, Any], 
                                  tolerance: float = 1e-10) -> Tuple[bool, str]:
        """
        Deep comparison of results with detailed diff reporting.
        
        Args:
            rust_result: Result from Rust implementation
            java_result: Result from Java implementation
            tolerance: Tolerance for floating-point comparisons
            
        Returns:
            Tuple of (matches: bool, diff_details: str)
        """
        try:
            return self._compare_values(rust_result, java_result, tolerance, path="root")
        except Exception as e:
            return False, f"Comparison exception: {e}"
    
    def _compare_values(self, rust_val: Any, java_val: Any, tolerance: float, path: str) -> Tuple[bool, str]:
        """
        Recursively compare values with type-aware matching.
        
        Args:
            rust_val: Value from Rust
            java_val: Value from Java (could be nested in dict)
            tolerance: Tolerance for floating-point comparisons
            path: Current path in the data structure for error reporting
            
        Returns:
            Tuple of (matches: bool, diff_details: str)
        """
        # Handle None values
        if rust_val is None and java_val is None:
            return True, ""
        if rust_val is None or java_val is None:
            return False, f"at {path}: None mismatch (Rust: {rust_val}, Java: {java_val})"
        
        # Handle numeric types with tolerance
        if isinstance(rust_val, (int, float)) and isinstance(java_val, (int, float)):
            if abs(rust_val - java_val) <= tolerance:
                return True, ""
            else:
                return False, f"at {path}: numeric mismatch (Rust: {rust_val}, Java: {java_val}, diff: {abs(rust_val - java_val)})"
        
        # Handle string types
        if isinstance(rust_val, str) and isinstance(java_val, str):
            if rust_val == java_val:
                return True, ""
            else:
                return False, f"at {path}: string mismatch (Rust: '{rust_val}', Java: '{java_val}')"
        
        # Handle boolean types
        if isinstance(rust_val, bool) and isinstance(java_val, bool):
            if rust_val == java_val:
                return True, ""
            else:
                return False, f"at {path}: boolean mismatch (Rust: {rust_val}, Java: {java_val})"
        
        # Handle list/tuple types
        if isinstance(rust_val, (list, tuple)) and isinstance(java_val, (list, tuple)):
            if len(rust_val) != len(java_val):
                return False, f"at {path}: length mismatch (Rust: {len(rust_val)}, Java: {len(java_val)})"
            
            for i, (r_item, j_item) in enumerate(zip(rust_val, java_val)):
                matches, details = self._compare_values(r_item, j_item, tolerance, f"{path}[{i}]")
                if not matches:
                    return False, details
            return True, ""
        
        # Handle dictionary types
        if isinstance(rust_val, dict) and isinstance(java_val, dict):
            # Check for missing keys
            rust_keys = set(rust_val.keys())
            java_keys = set(java_val.keys())
            
            if rust_keys != java_keys:
                missing_in_java = rust_keys - java_keys
                missing_in_rust = java_keys - rust_keys
                details = f"at {path}: key mismatch"
                if missing_in_java:
                    details += f" (missing in Java: {missing_in_java})"
                if missing_in_rust:
                    details += f" (missing in Rust: {missing_in_rust})"
                return False, details
            
            # Compare values for each key
            for key in rust_keys:
                matches, details = self._compare_values(rust_val[key], java_val[key], tolerance, f"{path}.{key}")
                if not matches:
                    return False, details
            return True, ""
        
        # Handle mixed types or direct comparison
        if rust_val == java_val:
            return True, ""
        else:
            return False, f"at {path}: type/value mismatch (Rust: {rust_val} ({type(rust_val)}), Java: {java_val} ({type(java_val)}))"
    
    def _load_test_algebra(self, file_path: Union[str, Path]) -> Any:
        """
        Load algebra with error handling and caching.
        
        Args:
            file_path: Path to the algebra file
            
        Returns:
            Loaded algebra object
            
        Raises:
            AssertionError: If algebra loading fails
        """
        file_path = str(file_path)
        
        # Check cache first
        if file_path in self._algebra_cache:
            self.test_logger.debug(f"Loading algebra from cache: {file_path}")
            return self._algebra_cache[file_path]
        
        try:
            # Import uacalc here to avoid import issues if not available
            import uacalc
            
            self.test_logger.debug(f"Loading algebra from file: {file_path}")
            start_time = time.time()
            algebra = uacalc.load_algebra(file_path)
            load_time = time.time() - start_time
            
            # Cache the loaded algebra
            self._algebra_cache[file_path] = algebra
            
            self.test_logger.debug(f"Algebra loaded in {load_time:.3f}s: {algebra.name} (size: {algebra.cardinality})")
            return algebra
            
        except Exception as e:
            self.test_logger.error(f"Failed to load algebra from {file_path}: {e}")
            self.fail(f"Failed to load algebra from {file_path}: {e}")
    
    def _should_skip_test(self, algebra_size: int, operation: str) -> bool:
        """
        Determine if test should be skipped based on complexity.
        
        Args:
            algebra_size: Size of the algebra
            operation: Name of the operation
            
        Returns:
            True if test should be skipped
        """
        # Skip very large algebras for expensive operations
        expensive_operations = {
            'congruence_lattice': 8,
            'maltsev_conditions': 6,
            'isomorphism': 10,
            'automorphism_group': 6,
            'free_algebra': 5
        }
        
        max_size = expensive_operations.get(operation, 20)
        
        if algebra_size > max_size:
            self.test_logger.info(f"Skipping {operation} for algebra size {algebra_size} (max: {max_size})")
            return True
        
        return False
    
    def _get_test_timeout(self, operation: str, algebra_size: int) -> int:
        """
        Get appropriate timeout for an operation based on complexity.
        
        Args:
            operation: Name of the operation
            algebra_size: Size of the algebra
            
        Returns:
            Timeout in seconds
        """
        base_timeouts = {
            'properties': self.JAVA_TIMEOUT_SHORT,
            'cg': self.JAVA_TIMEOUT_DEFAULT,
            'lattice': self.JAVA_TIMEOUT_LONG,
            'congruence_lattice': self.JAVA_TIMEOUT_LONG,
            'maltsev_conditions': self.JAVA_TIMEOUT_LONG,
            'isomorphism': self.JAVA_TIMEOUT_LONG,
            'automorphism_group': self.JAVA_TIMEOUT_LONG,
        }
        
        base_timeout = base_timeouts.get(operation, self.JAVA_TIMEOUT_DEFAULT)
        
        # Scale timeout based on algebra size
        if algebra_size > 10:
            base_timeout *= 2
        if algebra_size > 20:
            base_timeout *= 3
        
        return base_timeout
    
    @classmethod
    def generate_test_suite_report(cls) -> TestSuiteReport:
        """
        Generate a comprehensive test suite report.
        
        Returns:
            TestSuiteReport with aggregated results
        """
        if not cls.test_results_history:
            return TestSuiteReport(
                total_tests=0, passed_tests=0, failed_tests=0, skipped_tests=0,
                compatibility_percentage=0.0, failed_test_details=[], feature_coverage={}
            )
        
        total_tests = len(cls.test_results_history)
        passed_tests = sum(1 for r in cls.test_results_history if r.matches)
        failed_tests = total_tests - passed_tests
        
        compatibility_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
        
        failed_test_details = [r for r in cls.test_results_history if not r.matches]
        
        # Calculate feature coverage
        feature_coverage = {}
        operations = set(r.operation for r in cls.test_results_history)
        for operation in operations:
            op_results = [r for r in cls.test_results_history if r.operation == operation]
            op_passed = sum(1 for r in op_results if r.matches)
            feature_coverage[operation] = (op_passed / len(op_results) * 100) if op_results else 0.0
        
        total_execution_time = sum(r.execution_time_java for r in cls.test_results_history)
        
        return TestSuiteReport(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=0,  # TODO: Track skipped tests
            compatibility_percentage=compatibility_percentage,
            failed_test_details=failed_test_details,
            feature_coverage=feature_coverage,
            execution_time_total=total_execution_time
        )