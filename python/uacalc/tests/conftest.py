"""
Pytest configuration and shared fixtures for UACalc tests.

This module makes fixtures from test_utils available to all test files
in the tests directory, and provides algebra loading fixtures.
"""

import os
import pytest
import uacalc_lib

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


# Algebra loading helper function
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
        pytest.skip: If algebra not found and skip_if_missing=True
    """
    if not name.endswith('.ua'):
        name = f"{name}.ua"
    
    algebra_path = f"resources/algebras/{name}"
    
    if not os.path.exists(algebra_path):
        if skip_if_missing:
            pytest.skip(f"Algebra file {algebra_path} not found")
        else:
            raise FileNotFoundError(f"Algebra file {algebra_path} not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(algebra_path)
    return reader.read_algebra_file()


# Algebra fixtures for common test algebras
@pytest.fixture
def cyclic2_algebra():
    """Fixture providing cyclic2 algebra (2-element cyclic group)."""
    return load_test_algebra("cyclic2")


@pytest.fixture
def cyclic3_algebra():
    """Fixture providing cyclic3 algebra (3-element cyclic group)."""
    return load_test_algebra("cyclic3")


@pytest.fixture
def n5_algebra():
    """Fixture providing n5 algebra (5-element pentagon lattice)."""
    return load_test_algebra("n5")


@pytest.fixture
def m3_algebra():
    """Fixture providing m3 algebra (3-element diamond lattice)."""
    return load_test_algebra("m3")


@pytest.fixture(params=["cyclic2", "cyclic3", "n5"])
def test_algebra(request):
    """
    Parameterized fixture for multiple algebras.
    
    Usage:
        def test_with_various_algebras(test_algebra):
            # test_algebra will be cyclic2, cyclic3, and n5 in turn
            result = some_operation(test_algebra)
            assert result is not None
    """
    return load_test_algebra(request.param)


@pytest.fixture
def algebra_loader():
    """
    Fixture that returns the load_test_algebra function.
    
    Usage:
        def test_custom_algebra(algebra_loader):
            alg = algebra_loader("custom_algebra")
            # Use alg for testing
    """
    return load_test_algebra


# Re-export fixtures and utilities so they're available to all test files
__all__ = [
    # Test utilities
    'test_config',
    'test_harness',
    'memory_monitor',
    'TestConfig',
    'TestHarness', 
    'TestDataGenerator',
    'JavaCliOutput',
    'MemoryMonitor',
    
    # Algebra loading
    'load_test_algebra',
    'cyclic2_algebra',
    'cyclic3_algebra',
    'n5_algebra',
    'm3_algebra',
    'test_algebra',
    'algebra_loader',
]
