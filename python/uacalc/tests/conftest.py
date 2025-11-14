"""
Pytest configuration and shared fixtures for UACalc tests.

This module makes fixtures from test_utils available to all test files
in the tests directory and provides algebra loading utilities.
"""

import os
import pytest
import uacalc_lib
from typing import Optional

# Import all fixtures from test_utils to make them available
from test_utils import (
    test_config,
    test_harness, 
    memory_monitor,
    TestConfig,
    TestHarness,
    TestDataGenerator,
    JavaCliOutput,
    MemoryMonitor
)


def load_test_algebra(name: str, skip_if_missing: bool = True):
    """
    Load a test algebra from resources/algebras/
    
    Args:
        name: Algebra filename (with or without .ua extension)
        skip_if_missing: If True, skip test when algebra not found
        
    Returns:
        Loaded algebra object
        
    Raises:
        FileNotFoundError: If algebra not found and skip_if_missing=False
        unittest.SkipTest: If algebra not found and skip_if_missing=True
    """
    if not name.endswith('.ua'):
        name = f"{name}.ua"
    
    algebra_path = f"resources/algebras/{name}"
    
    if not os.path.exists(algebra_path):
        if skip_if_missing:
            import unittest
            raise unittest.SkipTest(f"Algebra file {algebra_path} not found")
        else:
            raise FileNotFoundError(f"Algebra file {algebra_path} not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(algebra_path)
    return reader.read_algebra_file()


@pytest.fixture
def cyclic2_algebra():
    """Fixture providing cyclic2 algebra."""
    if not os.path.exists("resources/algebras/cyclic2.ua"):
        pytest.skip("cyclic2.ua not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file("resources/algebras/cyclic2.ua")
    return reader.read_algebra_file()


@pytest.fixture
def cyclic3_algebra():
    """Fixture providing cyclic3 algebra."""
    if not os.path.exists("resources/algebras/cyclic3.ua"):
        pytest.skip("cyclic3.ua not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
    return reader.read_algebra_file()


@pytest.fixture(params=["cyclic2", "cyclic3", "n5"])
def test_algebra(request):
    """Parameterized fixture for multiple algebras."""
    algebra_name = request.param
    algebra_path = f"resources/algebras/{algebra_name}.ua"
    
    if not os.path.exists(algebra_path):
        pytest.skip(f"{algebra_name}.ua not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(algebra_path)
    return reader.read_algebra_file()


@pytest.fixture
def algebra_loader():
    """Fixture providing algebra loading function."""
    def load_algebra(name: str):
        """Load algebra by name."""
        return load_test_algebra(name, skip_if_missing=False)
    return load_algebra


# Re-export fixtures so they're available to all test files
__all__ = [
    'test_config',
    'test_harness',
    'memory_monitor',
    'TestConfig',
    'TestHarness', 
    'TestDataGenerator',
    'JavaCliOutput',
    'MemoryMonitor',
    'load_test_algebra',
    'cyclic2_algebra',
    'cyclic3_algebra',
    'test_algebra',
    'algebra_loader'
]
