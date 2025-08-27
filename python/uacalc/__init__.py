"""
Universal Algebra Calculator - Python Package

This package provides Python bindings for the UACalc Rust core library,
enabling efficient universal algebra computations in Python.
"""

__version__ = "0.2.0"
__author__ = "UACalc Team"
__email__ = "uacalc@example.com"

from typing import Optional, Callable, Dict, Any, Union, List, Tuple
import warnings

# Import the Rust extension module
try:
    from uacalc_rust import (
        PyAlgebra as Algebra,
        PyOperation as Operation,
        PyPartition as Partition,
        PyBinaryRelation as BinaryRelation,
        PyCongruenceLattice as CongruenceLattice,
        PyTerm as Term,
        PyTermArena as TermArena,
        PyProgressReporter as ProgressReporter,
        UACalcError,
        CancellationError,
        create_algebra,
        create_operation,
        create_partition,
        create_partition_from_blocks,
        create_binary_relation,
        create_congruence_lattice,
        create_term_arena,
        create_progress_reporter,
        parse_term,
        eval_term,
    )
except ImportError as e:
    raise ImportError(
        "Failed to import UACalc Rust extension. "
        "Make sure the Rust code has been compiled with 'maturin develop' or 'maturin build'."
    ) from e

# Feature detection (moved to top to avoid circular imports)
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    import warnings
    warnings.warn(
        "NumPy not found. Some advanced features may not be available.",
        UserWarning
    )

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Import pure Python modules
try:
    from . import io
except ImportError:
    # I/O module not available, create fallback stubs
    class _IOStub:
        def load_algebra(self, file_path: str):
            raise NotImplementedError("I/O module not available. Install required dependencies.")
        
        def save_algebra(self, algebra, file_path: str):
            raise NotImplementedError("I/O module not available. Install required dependencies.")
    
    io = _IOStub()

from . import algebra as algebra_utils

# Re-export main classes and functions
__all__ = [
    # Core classes
    "Algebra",
    "Operation", 
    "Partition",
    "BinaryRelation",
    "CongruenceLattice",
    "Term",
    "TermArena",
    "ProgressReporter",
    
    # Error classes
    "UACalcError",
    "CancellationError",
    
    # Factory functions
    "create_algebra",
    "create_operation", 
    "create_partition",
    "create_partition_from_blocks",
    "create_binary_relation",
    "create_congruence_lattice",
    "create_term_arena",
    "create_progress_reporter",
    
    # Utility functions
    "parse_term",
    "eval_term",
    
    # Utility modules
    "io",
    "algebra_utils",
]

# Enhanced convenience functions
def load_algebra(file_path: str) -> "Algebra":
    """Load an algebra from a .ua file.
    
    Args:
        file_path: Path to the .ua file
        
    Returns:
        Algebra object loaded from the file
        
    Raises:
        IOError: If the file cannot be read
        ValueError: If the file format is invalid
    """
    return io.load_algebra(file_path)

def save_algebra(algebra: "Algebra", file_path: str) -> None:
    """Save an algebra to a .ua file.
    
    Args:
        algebra: Algebra object to save
        file_path: Path where to save the file
        
    Raises:
        IOError: If the file cannot be written
    """
    io.save_algebra(algebra, file_path)

def create_group_operation(name: str, size: int, operation_table: list) -> "Operation":
    """Create a group operation from a multiplication table.
    
    Args:
        name: Name of the operation
        size: Size of the algebra universe
        operation_table: NxN matrix representing the operation
        
    Returns:
        Operation object representing the group operation
    """
    return algebra_utils.create_group_operation(name, size, operation_table)

def create_lattice_operations(name: str, size: int, meet_table: list, join_table: list) -> Tuple["Operation", "Operation"]:
    """Create meet and join operations for a lattice.
    
    Args:
        name: Base name for the operations (will be extended with "_meet" and "_join")
        size: Size of the algebra universe
        meet_table: NxN matrix for the meet operation
        join_table: NxN matrix for the join operation
        
    Returns:
        Tuple of (meet_operation, join_operation)
    """
    return algebra_utils.create_lattice_operations(name, size, meet_table, join_table)

def create_congruence_lattice_with_progress(algebra: "Algebra", 
                                          with_progress: Optional[Callable[[float, str], None]] = None) -> "CongruenceLattice":
    """Create a congruence lattice with optional progress reporting.
    
    Args:
        algebra: Algebra to compute the congruence lattice for
        with_progress: Optional callback function(progress: float, message: str) for progress reporting
        
    Returns:
        CongruenceLattice object
        
    Note:
        This function triggers immediate construction of the congruence lattice.
        If you want to defer construction, use create_congruence_lattice() and
        call with_progress_callback() separately.
        
    Example:
        def progress_callback(progress, message):
            print(f"Progress: {progress:.1%} - {message}")
            
        lattice = create_congruence_lattice_with_progress(algebra, progress_callback)
    """
    lattice = create_congruence_lattice(algebra)
    if with_progress is not None:
        lattice.with_progress_callback(with_progress)
    return lattice

def parse_and_eval_term(expr: str, algebra: "Algebra", variables: Dict[int, int]) -> int:
    """Parse and evaluate a term expression in one step.
    
    Args:
        expr: String representation of the term (e.g., "f(x0, g(x1))")
        algebra: Algebra to evaluate the term in
        variables: Dictionary mapping variable indices to values
        
    Returns:
        Result of term evaluation
        
    Example:
        result = parse_and_eval_term("f(x0, x1)", algebra, {0: 1, 1: 2})
    """
    arena = create_term_arena()
    term = parse_term(arena, expr)
    return eval_term(term, algebra, variables)

def create_term_from_string(expr: str, arena: Optional["TermArena"] = None) -> "Term":
    """Create a term from a string expression.
    
    Args:
        expr: String representation of the term
        arena: Optional term arena (will create new one if not provided)
        
    Returns:
        Term object
        
    Example:
        term = create_term_from_string("f(x0, g(x1))")
    """
    if arena is None:
        arena = create_term_arena()
    return parse_term(arena, expr)

# Add convenience functions to __all__
__all__.extend([
    "load_algebra",
    "save_algebra", 
    "create_group_operation",
    "create_lattice_operations",
    "create_congruence_lattice_with_progress",
    "parse_and_eval_term",
    "create_term_from_string",
])

# Version compatibility check
import sys
if sys.version_info < (3, 7):
    warnings.warn(
        "UACalc requires Python 3.7 or higher. Some features may not work correctly.",
        UserWarning
    )

# Export feature flags
__all__.extend([
    "HAS_NUMPY",
    "HAS_NETWORKX", 
    "HAS_MATPLOTLIB"
])

