"""Base classes and utilities for parity testing.

This module provides infrastructure for exact behavioral parity tests between
Java/Jython and CPython implementations.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from unittest import TestCase

# Parity test type markers
SMOKE = "smoke"  # Import/basic structure only
SURFACE = "surface"  # Public API surface (dir(), counts)
BEHAVIORAL = "behavioral"  # Exact behavioral parity

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class TestCaseSpec:
    """Specification for a single behavioral test case."""
    
    id: str  # Unique identifier for this test case
    method: str  # Fully qualified method name (e.g., "AlgebraIO.readAlgebraFile")
    args: List[Any] = field(default_factory=list)  # Positional arguments
    kwargs: Dict[str, Any] = field(default_factory=dict)  # Keyword arguments
    description: str = ""  # Human-readable description
    expected_exception: Optional[str] = None  # Expected exception type name
    skip_string_check: bool = False  # Skip string representation comparison
    notes: str = ""  # Additional notes or documentation


@dataclass
class TestResult:
    """Result from running a test case."""
    
    success: bool  # True if method completed without exception
    return_value: Any = None  # Returned value (if success=True)
    return_type: str = ""  # Type name of return value
    string_repr: str = ""  # String representation of return value
    exception_type: str = ""  # Exception type name (if success=False)
    exception_message: str = ""  # Exception message (if success=False)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Extra info


def serialize_for_golden(obj: Any) -> Any:
    """Convert an object to a JSON-serializable form for golden data.
    
    This handles common UACalc types and converts them to comparable dictionaries.
    """
    if obj is None:
        return None
    
    # Handle primitive types
    if isinstance(obj, (bool, int, float, str)):
        return obj
    
    # Handle lists and tuples
    if isinstance(obj, (list, tuple)):
        return [serialize_for_golden(item) for item in obj]
    
    # Handle dictionaries
    if isinstance(obj, dict):
        return {k: serialize_for_golden(v) for k, v in obj.items()}
    
    # Handle UACalc algebra objects - extract semantic fields
    if hasattr(obj, '__class__'):
        class_name = obj.__class__.__name__
        
        # Common algebra types
        if 'Algebra' in class_name:
            result = {'__type__': class_name}
            if hasattr(obj, 'name') or hasattr(obj, 'getName'):
                name = obj.name if hasattr(obj, 'name') else obj.getName()
                result['name'] = name() if callable(name) else name
            if hasattr(obj, 'cardinality') or hasattr(obj, 'cardinality'):
                card = obj.cardinality if hasattr(obj, 'cardinality') else obj.cardinality()
                result['cardinality'] = card() if callable(card) else card
            if hasattr(obj, 'operations'):
                ops = obj.operations if hasattr(obj, 'operations') else obj.operations()
                ops = ops() if callable(ops) else ops
                if ops:
                    result['operation_count'] = len(list(ops))
            return result
        
        # Lattice types
        if 'Lattice' in class_name:
            result = {'__type__': class_name}
            if hasattr(obj, 'cardinality'):
                card = obj.cardinality if hasattr(obj, 'cardinality') else obj.cardinality()
                result['cardinality'] = card() if callable(card) else card
            return result
        
        # Term types
        if 'Term' in class_name:
            result = {'__type__': class_name}
            if hasattr(obj, 'toString'):
                result['string'] = obj.toString()
            elif hasattr(obj, '__str__'):
                result['string'] = str(obj)
            return result
    
    # Fallback: convert to string
    return {'__repr__': repr(obj), '__type__': type(obj).__name__}


def load_golden_data(package: str, filename: str) -> Dict[str, Any]:
    """Load golden data JSON file for a package.
    
    Args:
        package: Package name (e.g., "io", "lat", "terms")
        filename: JSON filename (e.g., "AlgebraIO_jython.json")
    
    Returns:
        Parsed JSON data
    """
    golden_dir = REPO_ROOT / "tests" / "parity" / package / "golden_data"
    filepath = golden_dir / filename
    
    if not filepath.exists():
        raise FileNotFoundError(
            f"Golden data file not found: {filepath}\n"
            f"Generate it with: python3 tools/generate_golden_data.py --package {package}"
        )
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_golden_data(package: str, filename: str, data: Dict[str, Any]) -> None:
    """Save golden data to JSON file.
    
    Args:
        package: Package name (e.g., "io", "lat", "terms")
        filename: JSON filename (e.g., "AlgebraIO_jython.json")
        data: Data to save
    """
    golden_dir = REPO_ROOT / "tests" / "parity" / package / "golden_data"
    golden_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = golden_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write('\n')  # Trailing newline for git-friendliness


class BehavioralParityTest(TestCase):
    """Base class for behavioral parity tests.
    
    Subclasses should set:
        package: str - Package name (e.g., "io")
        golden_file: str - Golden data filename (e.g., "AlgebraIO_jython.json")
    
    Then create test methods that call run_golden_test_case(test_id).
    """
    
    package: str = ""
    golden_file: str = ""
    
    @classmethod
    def setUpClass(cls):
        """Load golden data once for all tests in this class."""
        if not cls.package or not cls.golden_file:
            raise ValueError(
                f"{cls.__name__} must set 'package' and 'golden_file' class attributes"
            )
        cls.golden_data = load_golden_data(cls.package, cls.golden_file)
        cls.test_cases_by_id = {
            tc['id']: tc for tc in cls.golden_data.get('test_cases', [])
        }
    
    def run_golden_test_case(self, test_id: str) -> None:
        """Run a single golden test case and compare to expected output.
        
        Args:
            test_id: ID of test case from golden data
        """
        if test_id not in self.test_cases_by_id:
            self.fail(f"Test case '{test_id}' not found in golden data")
        
        expected = self.test_cases_by_id[test_id]
        method_name = expected['method']
        args = expected.get('args', [])
        kwargs = expected.get('kwargs', {})
        expected_result = expected['result']
        
        # Import and call the method
        actual_result = self._call_method(method_name, args, kwargs)
        
        # Compare results
        if expected_result['success']:
            self.assertTrue(
                actual_result.success,
                f"{test_id}: Expected success but got exception: "
                f"{actual_result.exception_type}: {actual_result.exception_message}"
            )
            
            # Compare return values
            self._compare_values(
                test_id,
                serialize_for_golden(actual_result.return_value),
                expected_result.get('return_value'),
                "return value"
            )
            
            # Compare string representations (unless skipped)
            if not expected.get('skip_string_check', False):
                self.assertEqual(
                    actual_result.string_repr,
                    expected_result.get('string_repr', ''),
                    f"{test_id}: String representation mismatch"
                )
        else:
            self.assertFalse(
                actual_result.success,
                f"{test_id}: Expected exception but method succeeded"
            )
            
            expected_exc_type = expected_result['exception']['type']
            self.assertEqual(
                actual_result.exception_type,
                expected_exc_type,
                f"{test_id}: Exception type mismatch"
            )
            
            # Exception message comparison (may be lenient if documented)
            expected_msg = expected_result['exception'].get('message', '')
            if expected_msg and not self._messages_match(
                actual_result.exception_message, expected_msg
            ):
                self.fail(
                    f"{test_id}: Exception message mismatch\n"
                    f"  Expected: {expected_msg}\n"
                    f"  Actual:   {actual_result.exception_message}"
                )
    
    def _call_method(
        self, method_name: str, args: List[Any], kwargs: Dict[str, Any]
    ) -> TestResult:
        """Call a method and capture the result."""
        # Parse method name (e.g., "AlgebraIO.readAlgebraFile" or "read_algebra_file")
        parts = method_name.split('.')
        
        # Import the package
        package_name = f"org.uacalc.{self.package}"
        try:
            # Ensure python/org is on path
            python_dir = REPO_ROOT / "python"
            if str(python_dir) not in sys.path:
                sys.path.insert(0, str(python_dir))
            
            pkg = __import__(package_name, fromlist=[''])
        except ImportError as e:
            return TestResult(
                success=False,
                exception_type="ImportError",
                exception_message=str(e)
            )
        
        # Navigate to the method
        try:
            obj = pkg
            for part in parts[:-1]:
                obj = getattr(obj, part)
            method = getattr(obj, parts[-1])
        except AttributeError as e:
            return TestResult(
                success=False,
                exception_type="AttributeError",
                exception_message=f"Method not found: {method_name}: {e}"
            )
        
        # Call the method
        try:
            result = method(*args, **kwargs)
            return TestResult(
                success=True,
                return_value=result,
                return_type=type(result).__name__,
                string_repr=str(result) if result is not None else ""
            )
        except Exception as e:
            return TestResult(
                success=False,
                exception_type=type(e).__name__,
                exception_message=str(e)
            )
    
    def _compare_values(
        self, test_id: str, actual: Any, expected: Any, context: str
    ) -> None:
        """Compare two values for exact equality."""
        if actual != expected:
            self.fail(
                f"{test_id}: {context} mismatch\n"
                f"  Expected: {json.dumps(expected, indent=2)}\n"
                f"  Actual:   {json.dumps(actual, indent=2)}"
            )
    
    def _messages_match(self, actual: str, expected: str) -> bool:
        """Check if exception messages match (with some leniency for path differences)."""
        # Exact match is preferred
        if actual == expected:
            return True
        
        # Normalize paths and whitespace
        actual_norm = actual.replace('\\', '/').strip()
        expected_norm = expected.replace('\\', '/').strip()
        
        return actual_norm == expected_norm


def collect_test_coverage(package: str) -> Dict[str, Any]:
    """Analyze test coverage for a package.
    
    Returns a dictionary with:
        - wrapped_methods: List of methods wrapped in Python
        - tested_methods: List of methods with behavioral tests
        - untested_methods: List of wrapped but untested methods
    """
    # This will be implemented in the coverage measurement tool
    raise NotImplementedError("Use tools/jython_contracts_cli.py parity-coverage")
