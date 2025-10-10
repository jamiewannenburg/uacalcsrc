"""
Pytest configuration and shared fixtures for UACalc tests.

This module makes fixtures from test_utils available to all test files
in the tests directory.
"""

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

# Re-export fixtures so they're available to all test files
__all__ = [
    'test_config',
    'test_harness',
    'memory_monitor',
    'TestConfig',
    'TestHarness', 
    'TestDataGenerator',
    'JavaCliOutput',
    'MemoryMonitor'
]
