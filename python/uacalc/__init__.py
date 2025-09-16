"""
Universal Algebra Calculator - Python Package

This package provides Python bindings for the UACalc Rust core library,
enabling efficient universal algebra computations in Python.

The package includes comprehensive I/O functionality for .ua files with
full compatibility with Java UACalc, including XML parsing, validation,
and round-trip file operations.
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
        Operations,
        OperationSymbol,
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
        create_operation_with_size,
        create_partition,
        create_partition_from_blocks,
        create_binary_relation,
        create_congruence_lattice,
        create_term_arena,
        create_progress_reporter,
        parse_term,
        eval_term,
        rust_create_product_algebra,
        rust_create_quotient_algebra,
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
    from . import errors
except ImportError:
    # I/O module not available, create fallback stubs
    class _IOStub:
        def load_algebra(self, file_path: str):
            raise NotImplementedError("I/O module not available. Install required dependencies.")
        
        def save_algebra(self, algebra, file_path: str):
            raise NotImplementedError("I/O module not available. Install required dependencies.")
        
        def validate_ua_file(self, file_path: str):
            raise NotImplementedError("I/O module not available. Install required dependencies.")
        
        def list_ua_files(self, directory: str):
            raise NotImplementedError("I/O module not available. Install required dependencies.")
        
        def get_algebra_info(self, file_path: str):
            raise NotImplementedError("I/O module not available. Install required dependencies.")
    
    io = _IOStub()
    errors = None

from . import algebra as algebra_utils
from .algebra import create_product_algebra

# Import I/O functions and error classes
try:
    from .io import (
        load_algebra,
        save_algebra,
        validate_ua_file,
        list_ua_files,
        get_algebra_info,
        convert_format,
        repair_ua_file,
    )
    
    from .errors import (
        BadUAFileError,
        InvalidOperationTableError,
        UnsupportedAlgebraTypeError,
        XMLParsingError,
        FileFormatError,
        map_xml_error,
        map_io_error,
    )
except ImportError:
    # Create fallback functions if I/O module is not available
    def load_algebra(file_path: str):
        raise NotImplementedError("I/O module not available. Install required dependencies.")
    
    def save_algebra(algebra, file_path: str):
        raise NotImplementedError("I/O module not available. Install required dependencies.")
    
    def validate_ua_file(file_path: str):
        raise NotImplementedError("I/O module not available. Install required dependencies.")
    
    def list_ua_files(directory: str):
        raise NotImplementedError("I/O module not available. Install required dependencies.")
    
    def get_algebra_info(file_path: str):
        raise NotImplementedError("I/O module not available. Install required dependencies.")
    
    def convert_format(input_file: str, output_file: str, target_format: str = "ua"):
        raise NotImplementedError("I/O module not available. Install required dependencies.")
    
    def repair_ua_file(file_path: str, backup: bool = True):
        raise NotImplementedError("I/O module not available. Install required dependencies.")
    
    # Create fallback error classes
    class BadUAFileError(Exception):
        pass
    
    class InvalidOperationTableError(Exception):
        pass
    
    class UnsupportedAlgebraTypeError(Exception):
        pass
    
    class XMLParsingError(Exception):
        pass
    
    class FileFormatError(Exception):
        pass
    
    def map_xml_error(xml_error, file_path=None, context=None):
        raise NotImplementedError("I/O module not available. Install required dependencies.")
    
    def map_io_error(io_error, file_path=None, context=None):
        raise NotImplementedError("I/O module not available. Install required dependencies.")

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
    "BadUAFileError",
    "InvalidOperationTableError",
    "UnsupportedAlgebraTypeError",
    "XMLParsingError",
    "FileFormatError",
    
    # Factory functions
    "create_algebra",
    "create_operation", 
    "create_partition",
    "create_partition_from_blocks",
    "create_binary_relation",
    "create_congruence_lattice",
    "create_term_arena",
    "create_progress_reporter",
    "create_product_algebra",
    "rust_create_product_algebra",
    "rust_create_quotient_algebra",
    
    # I/O functions
    "load_algebra",
    "save_algebra",
    "validate_ua_file",
    "list_ua_files",
    "get_algebra_info",
    "convert_format",
    "repair_ua_file",
    
    # Error mapping functions
    "map_xml_error",
    "map_io_error",
    
    # Utility functions
    "parse_term",
    "eval_term",
    
    # Utility modules
    "io",
    "algebra_utils",
]

# Enhanced convenience functions
def load_algebra_safe(file_path: str) -> Tuple[Optional["Algebra"], List[str]]:
    """Load an algebra from a .ua file with error reporting.
    
    Args:
        file_path: Path to the .ua file
        
    Returns:
        Tuple of (algebra, errors) where algebra is None if loading failed
        
    Example:
        algebra, errors = load_algebra_safe("test.ua")
        if algebra is None:
            print(f"Failed to load: {errors}")
        else:
            print(f"Loaded algebra: {algebra.name}")
    """
    try:
        algebra = load_algebra(file_path)
        return algebra, []
    except Exception as e:
        return None, [str(e)]

def save_algebra_validated(algebra: "Algebra", file_path: str) -> Tuple[bool, List[str]]:
    """Save an algebra to a .ua file with validation.
    
    Args:
        algebra: Algebra object to save
        file_path: Path where to save the file
        
    Returns:
        Tuple of (success, errors) where success is True if saving succeeded
        
    Example:
        success, errors = save_algebra_validated(algebra, "output.ua")
        if not success:
            print(f"Failed to save: {errors}")
    """
    try:
        save_algebra(algebra, file_path)
        # Validate the saved file
        is_valid, validation_errors = validate_ua_file(file_path)
        if not is_valid:
            return False, validation_errors
        return True, []
    except Exception as e:
        return False, [str(e)]

def batch_load_algebras(file_paths: List[str]) -> Dict[str, Tuple[Optional["Algebra"], List[str]]]:
    """Load multiple algebras from .ua files.
    
    Args:
        file_paths: List of file paths to load
        
    Returns:
        Dictionary mapping file paths to (algebra, errors) tuples
        
    Example:
        results = batch_load_algebras(["alg1.ua", "alg2.ua", "alg3.ua"])
        for file_path, (algebra, errors) in results.items():
            if algebra is None:
                print(f"Failed to load {file_path}: {errors}")
            else:
                print(f"Loaded {file_path}: {algebra.name}")
    """
    results = {}
    for file_path in file_paths:
        results[file_path] = load_algebra_safe(file_path)
    return results

def quick_algebra_info(file_path: str) -> Dict[str, Any]:
    """Get quick information about an algebra without full parsing.
    
    Args:
        file_path: Path to the .ua file
        
    Returns:
        Dictionary with basic algebra information
        
    Example:
        info = quick_algebra_info("test.ua")
        print(f"Name: {info.get('name', 'Unknown')}")
        print(f"Cardinality: {info.get('cardinality', 'Unknown')}")
        print(f"Valid: {info.get('valid', False)}")
    """
    return get_algebra_info(file_path)

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
    "load_algebra_safe",
    "save_algebra_validated", 
    "batch_load_algebras",
    "quick_algebra_info",
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

# I/O module documentation
def _get_io_documentation():
    """Get I/O module documentation."""
    return """
I/O Module Features:

1. .ua File Format Support:
   - Full compatibility with Java UACalc .ua files
   - XML-based format with nested structure
   - Support for basic algebras (product, quotient algebras planned)

2. File Operations:
   - load_algebra(): Load algebra from .ua file
   - save_algebra(): Save algebra to .ua file
   - validate_ua_file(): Validate .ua file without loading
   - list_ua_files(): List .ua files in directory
   - get_algebra_info(): Get basic info without full parsing

3. Error Handling:
   - BadUAFileError: General .ua file errors
   - InvalidOperationTableError: Operation table validation errors
   - UnsupportedAlgebraTypeError: Unsupported algebra types
   - XMLParsingError: XML parsing errors
   - FileFormatError: File format errors

4. Convenience Functions:
   - load_algebra_safe(): Load with error reporting
   - save_algebra_validated(): Save with validation
   - batch_load_algebras(): Load multiple files
   - quick_algebra_info(): Fast metadata extraction

5. Validation Features:
   - XML structure validation
   - Algebra metadata validation
   - Operation table validation
   - Universe constraint validation
   - Comprehensive error reporting

Example Usage:
    # Load and save algebras
    algebra = load_algebra("test.ua")
    save_algebra(algebra, "output.ua")
    
    # Validate files
    is_valid, errors = validate_ua_file("test.ua")
    if not is_valid:
        print(f"Validation errors: {errors}")
    
    # Batch operations
    results = batch_load_algebras(["alg1.ua", "alg2.ua"])
    for file_path, (algebra, errors) in results.items():
        if algebra is None:
            print(f"Failed to load {file_path}: {errors}")
        else:
            print(f"Loaded {file_path}: {algebra.name}")
"""

