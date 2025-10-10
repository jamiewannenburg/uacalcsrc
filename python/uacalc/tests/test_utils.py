"""
Test utilities for UACalc Python tests.

This module provides shared testing infrastructure including:
- Timeout support for long-running tests
- Java CLI comparison utilities
- Memory limit testing
- Test data generation
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import threading
import psutil
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from contextlib import contextmanager
import pytest


@dataclass
class TestConfig:
    """Configuration for test timeouts and memory limits."""
    default_timeout: float = 60.0  # seconds
    memory_limit_mb: int = 1024  # MB
    java_wrapper_path: str = "java_wrapper/build/scripts"
    verbose: bool = False


@dataclass
class JavaCliOutput:
    """Output from a Java CLI execution."""
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    
    def parse_json(self) -> Dict[str, Any]:
        """Parse the stdout as JSON."""
        return json.loads(self.stdout)
    
    def is_success(self) -> bool:
        """Check if the execution was successful."""
        return self.exit_code == 0


class MemoryMonitor:
    """Monitor memory usage during tests."""
    
    def __init__(self, limit_mb: int):
        self.limit_mb = limit_mb
        self.process = psutil.Process()
        self.initial_memory = self._get_memory_usage()
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def check_memory(self) -> None:
        """Check if memory usage is within limits."""
        current_memory = self._get_memory_usage()
        used_memory = current_memory - self.initial_memory
        
        if used_memory > self.limit_mb:
            raise MemoryError(
                f"Memory limit exceeded: {used_memory:.1f}MB > {self.limit_mb}MB"
            )


class TestHarness:
    """Test harness for running UACalc operations with full validation."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.temp_dir = tempfile.mkdtemp()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def get_script_extension(self) -> str:
        """Get the appropriate script extension for the current platform."""
        return ".bat" if platform.system() == "Windows" else ""
    
    def get_script_path(self, script_name: str) -> Path:
        """Get the full script path with appropriate extension for the current platform."""
        extension = self.get_script_extension()
        return Path(self.config.java_wrapper_path) / f"{script_name}{extension}"

    def run_java_cli(self, script_name: str, args: List[str]) -> JavaCliOutput:
        """Run a Java CLI wrapper and capture its output."""
        script_path = self.get_script_path(script_name)
        
        if not script_path.exists():
            raise FileNotFoundError(f"Java CLI script not found: {script_path}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [str(script_path)] + args,
                capture_output=True,
                text=True,
                timeout=self.config.default_timeout
            )
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Java CLI timed out after {self.config.default_timeout}s")
        
        duration = time.time() - start_time
        
        return JavaCliOutput(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
            duration=duration
        )
    
    def compare_outputs(
        self,
        python_output: str,
        java_output: JavaCliOutput,
        tolerance: Optional[float] = None
    ) -> None:
        """Compare Python output with Java CLI output."""
        if not java_output.is_success():
            raise AssertionError(
                f"Java CLI failed with exit code {java_output.exit_code}: "
                f"{java_output.stderr}"
            )
        
        # Try to parse both as JSON for structured comparison
        try:
            python_json = json.loads(python_output)
            java_json = java_output.parse_json()
            self._compare_json_outputs(python_json, java_json, tolerance)
        except json.JSONDecodeError:
            # Fall back to string comparison
            self._compare_string_outputs(python_output, java_output.stdout)
    
    def _compare_json_outputs(
        self,
        python_json: Dict[str, Any],
        java_json: Dict[str, Any],
        tolerance: Optional[float]
    ) -> None:
        """Compare JSON outputs with optional numerical tolerance."""
        if python_json == java_json:
            return
        
        # If tolerance is specified, try numerical comparison
        if tolerance is not None:
            if self._compare_numbers_with_tolerance(python_json, java_json, tolerance):
                return
        
        raise AssertionError(
            f"JSON outputs differ:\n"
            f"Python: {json.dumps(python_json, indent=2)}\n"
            f"Java: {json.dumps(java_json, indent=2)}"
        )
    
    def _compare_numbers_with_tolerance(
        self,
        python_val: Any,
        java_val: Any,
        tolerance: float
    ) -> bool:
        """Compare numerical values with tolerance."""
        if isinstance(python_val, (int, float)) and isinstance(java_val, (int, float)):
            return abs(python_val - java_val) <= tolerance
        elif isinstance(python_val, dict) and isinstance(java_val, dict):
            if set(python_val.keys()) != set(java_val.keys()):
                return False
            return all(
                self._compare_numbers_with_tolerance(
                    python_val[k], java_val[k], tolerance
                )
                for k in python_val.keys()
            )
        elif isinstance(python_val, list) and isinstance(java_val, list):
            if len(python_val) != len(java_val):
                return False
            return all(
                self._compare_numbers_with_tolerance(p, j, tolerance)
                for p, j in zip(python_val, java_val)
            )
        else:
            return python_val == java_val
    
    def _compare_string_outputs(self, python_output: str, java_output: str) -> None:
        """Compare string outputs (for non-JSON data)."""
        if python_output.strip() != java_output.strip():
            raise AssertionError(
                f"String outputs differ:\n"
                f"Python: {python_output}\n"
                f"Java: {java_output}"
            )
    
    def run_test_with_monitoring(
        self,
        test_name: str,
        test_func,
        *args,
        **kwargs
    ) -> Any:
        """Run a test with timeout and memory monitoring."""
        memory_monitor = MemoryMonitor(self.config.memory_limit_mb)
        
        if self.config.verbose:
            print(f"Running test: {test_name}")
        
        try:
            result = test_func(*args, **kwargs)
            memory_monitor.check_memory()
            
            if self.config.verbose:
                print(f"Test {test_name} completed")
            
            return result
        except Exception as e:
            if self.config.verbose:
                print(f"Test {test_name} failed: {e}")
            raise


class TestDataGenerator:
    """Generate test data for common UACalc test cases."""
    
    @staticmethod
    def small_algebra_data() -> List[Dict[str, Any]]:
        """Generate test data for small algebras."""
        return [
            {
                "size": 2,
                "operations": ["meet", "join"],
                "description": "Boolean algebra"
            },
            {
                "size": 3,
                "operations": ["+", "*"],
                "description": "3-element ring"
            },
            {
                "size": 4,
                "operations": ["min", "max"],
                "description": "4-element lattice"
            }
        ]
    
    @staticmethod
    def lattice_data() -> List[Dict[str, Any]]:
        """Generate test data for lattice operations."""
        return [
            {"size": 2, "lattice_type": "boolean"},
            {"size": 3, "lattice_type": "chain"},
            {"size": 4, "lattice_type": "diamond"}
        ]


# Pytest fixtures
@pytest.fixture
def test_config() -> TestConfig:
    """Provide default test configuration."""
    return TestConfig()


@pytest.fixture
def test_harness(test_config: TestConfig) -> TestHarness:
    """Provide test harness with cleanup."""
    with TestHarness(test_config) as harness:
        yield harness


@pytest.fixture
def memory_monitor(test_config: TestConfig) -> MemoryMonitor:
    """Provide memory monitor for tests."""
    return MemoryMonitor(test_config.memory_limit_mb)


# Pytest markers for timeout control
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "timeout_30: marks tests with 30 second timeout"
    )
    config.addinivalue_line(
        "markers", "timeout_60: marks tests with 60 second timeout"
    )
    config.addinivalue_line(
        "markers", "timeout_120: marks tests with 120 second timeout"
    )
    config.addinivalue_line(
        "markers", "memory_limit: marks tests with memory limit monitoring"
    )


# Context managers for test utilities
@contextmanager
def timeout_context(seconds: float):
    """Context manager for timeout control."""
    def timeout_handler():
        time.sleep(seconds)
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    timer = threading.Timer(seconds, timeout_handler)
    timer.start()
    
    try:
        yield
    finally:
        timer.cancel()


@contextmanager
def memory_limit_context(limit_mb: int):
    """Context manager for memory limit monitoring."""
    monitor = MemoryMonitor(limit_mb)
    
    try:
        yield monitor
    finally:
        monitor.check_memory()


# Utility functions
def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent


def get_java_wrapper_path() -> Path:
    """Get the path to Java wrapper scripts."""
    return get_project_root() / "java_wrapper" / "build" / "scripts"


def is_java_wrapper_available() -> bool:
    """Check if Java wrapper scripts are available."""
    return get_java_wrapper_path().exists()


# Test decorators
def timeout(seconds: float):
    """Decorator to add timeout to test functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with timeout_context(seconds):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def memory_limit(limit_mb: int):
    """Decorator to add memory limit monitoring to test functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with memory_limit_context(limit_mb):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Example usage and tests
if __name__ == "__main__":
    # Example usage
    config = TestConfig(verbose=True)
    
    with TestHarness(config) as harness:
        print("Test harness created successfully")
        
        # Generate test data
        algebra_data = TestDataGenerator.small_algebra_data()
        print(f"Generated {len(algebra_data)} algebra test cases")
        
        # Test memory monitoring
        monitor = MemoryMonitor(100)
        monitor.check_memory()
        print("Memory monitoring working")
