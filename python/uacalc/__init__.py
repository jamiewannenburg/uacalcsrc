"""
Universal Algebra Calculator - Python Package

This package provides Python bindings for the UACalc Rust core library,
enabling efficient universal algebra computations in Python.
"""

__version__ = "0.1.0"
__author__ = "UACalc Team"
__email__ = "uacalc@example.com"

# Import the Rust extension module
try:
    from ._core import (
        PyAlgebra as Algebra,
        PyOperation as Operation,
        PyPartition as Partition,
        PyBinaryRelation as BinaryRelation,
        create_algebra,
        create_operation,
        create_partition,
        create_binary_relation,
    )
except ImportError as e:
    raise ImportError(
        "Failed to import UACalc Rust extension. "
        "Make sure the Rust code has been compiled with 'maturin develop' or 'maturin build'."
    ) from e

# Import pure Python modules
from . import io
from . import algebra as algebra_utils

# Re-export main classes and functions
__all__ = [
    # Core classes
    "Algebra",
    "Operation", 
    "Partition",
    "BinaryRelation",
    
    # Factory functions
    "create_algebra",
    "create_operation", 
    "create_partition",
    "create_binary_relation",
    
    # Utility modules
    "io",
    "algebra_utils",
]

# Convenience imports for common operations
def load_algebra(file_path: str) -> "Algebra":
    """Load an algebra from a .ua file."""
    return io.load_algebra(file_path)

def save_algebra(algebra: "Algebra", file_path: str) -> None:
    """Save an algebra to a .ua file."""
    io.save_algebra(algebra, file_path)

def create_group_operation(name: str, size: int, operation_table: list) -> "Operation":
    """Create a group operation from a multiplication table."""
    return algebra_utils.create_group_operation(name, size, operation_table)

def create_lattice_operations(name: str, size: int, meet_table: list, join_table: list) -> tuple["Operation", "Operation"]:
    """Create meet and join operations for a lattice."""
    return algebra_utils.create_lattice_operations(name, size, meet_table, join_table)

# Add convenience functions to __all__
__all__.extend([
    "load_algebra",
    "save_algebra", 
    "create_group_operation",
    "create_lattice_operations",
])

