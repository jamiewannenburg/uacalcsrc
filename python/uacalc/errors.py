"""
Error Handling System

This module provides comprehensive error handling for UACalc operations
with custom exception classes and error mapping utilities.
"""

from typing import Optional, Dict, Any, Union, Type, Callable, List
import traceback
import logging
import warnings
from functools import wraps
from contextlib import contextmanager

from . import UACalcError, CancellationError

class AlgebraError(UACalcError):
    """Base exception for algebra-specific errors."""
    
    def __init__(self, message: str, algebra_name: Optional[str] = None, **kwargs):
        super().__init__(message)
        self.algebra_name = algebra_name
        self.details = kwargs
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.algebra_name:
            base += f" (algebra: {self.algebra_name})"
        return base

class TermError(UACalcError):
    """Base exception for term-related errors."""
    
    def __init__(self, message: str, term_expr: Optional[str] = None, **kwargs):
        super().__init__(message)
        self.term_expr = term_expr
        self.details = kwargs
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.term_expr:
            base += f" (term: {self.term_expr})"
        return base

class CongruenceError(UACalcError):
    """Base exception for congruence lattice errors."""
    
    def __init__(self, message: str, algebra_name: Optional[str] = None, **kwargs):
        super().__init__(message)
        self.algebra_name = algebra_name
        self.details = kwargs
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.algebra_name:
            base += f" (algebra: {self.algebra_name})"
        return base

class IndexOutOfBoundsError(UACalcError, IndexError):
    """Exception for index out of bounds errors."""
    
    def __init__(self, message: str, index: Optional[int] = None, size: Optional[int] = None):
        super().__init__(message)
        self.index = index
        self.size = size
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.index is not None and self.size is not None:
            base += f" (index: {self.index}, size: {self.size})"
        return base

class InvalidArityError(UACalcError, ValueError):
    """Exception for arity mismatch errors."""
    
    def __init__(self, message: str, expected: Optional[int] = None, actual: Optional[int] = None):
        super().__init__(message)
        self.expected = expected
        self.actual = actual
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.expected is not None and self.actual is not None:
            base += f" (expected: {self.expected}, actual: {self.actual})"
        return base

class ParseError(TermError, ValueError):
    """Exception for term parsing errors."""
    
    def __init__(self, message: str, term_expr: Optional[str] = None, position: Optional[int] = None):
        super().__init__(message, term_expr)
        self.position = position
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.position is not None:
            base += f" (position: {self.position})"
        return base

class EvaluationError(TermError):
    """Exception for term evaluation errors."""
    
    def __init__(self, message: str, term_expr: Optional[str] = None, variables: Optional[Dict] = None):
        super().__init__(message, term_expr)
        self.variables = variables or {}
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.variables:
            base += f" (variables: {self.variables})"
        return base

class OperationNotFoundError(AlgebraError, KeyError):
    """Exception for missing operation errors."""
    
    def __init__(self, message: str, operation_name: Optional[str] = None, algebra_name: Optional[str] = None):
        super().__init__(message, algebra_name)
        self.operation_name = operation_name
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.operation_name:
            base += f" (operation: {self.operation_name})"
        return base

class ValidationError(UACalcError, ValueError):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        super().__init__(message)
        self.field = field
        self.value = value
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.field is not None:
            base += f" (field: {self.field})"
        if self.value is not None:
            base += f" (value: {self.value})"
        return base

class ConfigurationError(UACalcError, ValueError):
    """Exception for configuration errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message)
        self.config_key = config_key
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.config_key:
            base += f" (config: {self.config_key})"
        return base

# I/O Error Classes for .ua file handling

class BadUAFileError(UACalcError, ValueError):
    """Exception for malformed .ua files.
    
    Maps to Java's BadAlgebraFileException.
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 line_number: Optional[int] = None, column_number: Optional[int] = None, **kwargs):
        super().__init__(message)
        self.file_path = file_path
        self.line_number = line_number
        self.column_number = column_number
        self.details = kwargs
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.file_path:
            base += f" (file: {self.file_path})"
        if self.line_number is not None:
            base += f" (line: {self.line_number})"
        if self.column_number is not None:
            base += f" (column: {self.column_number})"
        return base

class InvalidOperationTableError(BadUAFileError):
    """Exception for invalid operation tables in .ua files."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 operation_name: Optional[str] = None, expected_size: Optional[int] = None,
                 actual_size: Optional[int] = None, row_index: Optional[int] = None, **kwargs):
        super().__init__(message, file_path, **kwargs)
        self.operation_name = operation_name
        self.expected_size = expected_size
        self.actual_size = actual_size
        self.row_index = row_index
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.operation_name:
            base += f" (operation: {self.operation_name})"
        if self.expected_size is not None and self.actual_size is not None:
            base += f" (expected: {self.expected_size}, actual: {self.actual_size})"
        if self.row_index is not None:
            base += f" (row: {self.row_index})"
        return base

class UnsupportedAlgebraTypeError(BadUAFileError):
    """Exception for unsupported algebra types in .ua files."""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 algebra_type: Optional[str] = None, supported_types: Optional[List[str]] = None, **kwargs):
        super().__init__(message, file_path, **kwargs)
        self.algebra_type = algebra_type
        self.supported_types = supported_types or []
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.algebra_type:
            base += f" (type: {self.algebra_type})"
        if self.supported_types:
            base += f" (supported: {', '.join(self.supported_types)})"
        return base

class XMLParsingError(BadUAFileError):
    """Exception for XML parsing errors in .ua files."""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 xml_error: Optional[str] = None, **kwargs):
        super().__init__(message, file_path, **kwargs)
        self.xml_error = xml_error
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.xml_error:
            base += f" (XML error: {self.xml_error})"
        return base

class FileFormatError(BadUAFileError):
    """Exception for file format errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 expected_format: Optional[str] = None, actual_format: Optional[str] = None, **kwargs):
        super().__init__(message, file_path, **kwargs)
        self.expected_format = expected_format
        self.actual_format = actual_format
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.expected_format and self.actual_format:
            base += f" (expected: {self.expected_format}, actual: {self.actual_format})"
        return base

# Error mapping utilities
def handle_rust_error(rust_error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Map Rust errors to appropriate Python exceptions and raise them.
    
    Args:
        rust_error: The Rust error to map
        context: Optional context information
        
    Raises:
        Mapped Python exception
    """
    error_str = str(rust_error)
    context = context or {}
    
    # Check if this is a UACalcError with a specific error type
    if isinstance(rust_error, UACalcError):
        # Try to extract error type from the string representation
        # The format appears to be ('message', 'ErrorType')
        import re
        match = re.search(r"\('([^']+)', '([^']+)'\)", error_str)
        if match:
            message, error_type = match.group(1), match.group(2)
            
            if error_type == "AlgebraError":
                raise AlgebraError(message, context.get('algebra_name'))
            elif error_type == "TermError":
                raise TermError(message, context.get('term_expr'))
            elif error_type == "CongruenceError":
                raise CongruenceError(message, context.get('algebra_name'))
            elif error_type == "IndexOutOfBoundsError":
                # Try to extract index and size from message
                index_match = re.search(r'index (\d+), size (\d+)', message)
                if index_match:
                    index, size = int(index_match.group(1)), int(index_match.group(2))
                    raise IndexOutOfBoundsError(message, index, size)
                raise IndexOutOfBoundsError(message)
            elif error_type == "InvalidArityError":
                # Try to extract expected and actual from message
                arity_match = re.search(r'expected (\d+), got (\d+)', message)
                if arity_match:
                    expected, actual = int(arity_match.group(1)), int(arity_match.group(2))
                    raise InvalidArityError(message, expected, actual)
                raise InvalidArityError(message)
            elif error_type == "ParseError":
                raise ParseError(message, context.get('term_expr'))
            elif error_type == "OperationNotFoundError":
                # Try to extract operation name from message
                op_match = re.search(r"'([^']+)'", message)
                if op_match:
                    op_name = op_match.group(1)
                    raise OperationNotFoundError(message, op_name, context.get('algebra_name'))
                raise OperationNotFoundError(message)
            else:
                # Unknown error type, raise as generic UACalcError
                raise UACalcError(message)
    
    # Map common error patterns from string content
    if "Index out of bounds" in error_str:
        # Extract index and size if possible
        import re
        match = re.search(r'index (\d+), size (\d+)', error_str)
        if match:
            index, size = int(match.group(1)), int(match.group(2))
            raise IndexOutOfBoundsError(error_str, index, size)
        raise IndexOutOfBoundsError(error_str)
    
    elif "Invalid arity" in error_str:
        # Extract expected and actual arity if possible
        import re
        match = re.search(r'expected (\d+), got (\d+)', error_str)
        if match:
            expected, actual = int(match.group(1)), int(match.group(2))
            raise InvalidArityError(error_str, expected, actual)
        raise InvalidArityError(error_str)
    
    elif "Operation not found" in error_str:
        # Extract operation name if possible
        import re
        match = re.search(r"'([^']+)'", error_str)
        if match:
            op_name = match.group(1)
            raise OperationNotFoundError(error_str, op_name, context.get('algebra_name'))
        raise OperationNotFoundError(error_str)
    
    elif "Parse error" in error_str:
        raise ParseError(error_str, context.get('term_expr'))
    
    elif "Operation cancelled" in error_str:
        raise CancellationError(error_str)
    
    elif "Algebra not found" in error_str:
        # Extract algebra name if possible
        import re
        match = re.search(r"'([^']+)'", error_str)
        if match:
            algebra_name = match.group(1)
            raise AlgebraError(error_str, algebra_name)
        raise AlgebraError(error_str)
    
    else:
        # Default mapping
        raise UACalcError(error_str)

def map_xml_error(xml_error: Exception, file_path: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> XMLParsingError:
    """Map XML parsing errors to UACalc XMLParsingError.
    
    Args:
        xml_error: The XML parsing error to map
        file_path: Optional file path for context
        context: Optional additional context
        
    Returns:
        XMLParsingError with mapped information
    """
    context = context or {}
    context['file_path'] = file_path
    
    if hasattr(xml_error, 'position'):
        line, column = xml_error.position
        return XMLParsingError(
            f"XML parsing error: {xml_error}",
            file_path=file_path,
            xml_error=str(xml_error),
            line_number=line,
            column_number=column
        )
    else:
        return XMLParsingError(
            f"XML parsing error: {xml_error}",
            file_path=file_path,
            xml_error=str(xml_error)
        )

def map_io_error(io_error: Exception, file_path: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> BadUAFileError:
    """Map I/O errors to UACalc BadUAFileError.
    
    Args:
        io_error: The I/O error to map
        file_path: Optional file path for context
        context: Optional additional context
        
    Returns:
        BadUAFileError with mapped information
    """
    context = context or {}
    context['file_path'] = file_path
    
    if isinstance(io_error, FileNotFoundError):
        return BadUAFileError(
            f"File not found: {file_path}",
            file_path=file_path,
            **context
        )
    elif isinstance(io_error, PermissionError):
        return BadUAFileError(
            f"Permission denied accessing file: {file_path}",
            file_path=file_path,
            **context
        )
    elif isinstance(io_error, UnicodeDecodeError):
        return BadUAFileError(
            f"Unicode decode error in file: {file_path}",
            file_path=file_path,
            line_number=getattr(io_error, 'start', None),
            **context
        )
    else:
        return BadUAFileError(
            f"I/O error: {io_error}",
            file_path=file_path,
            **context
        )

def validate_inputs(*validators: Callable) -> Callable:
    """Decorator for input validation.
    
    Args:
        *validators: Validation functions to apply
        
    Returns:
        Decorated function with validation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for validator in validators:
                try:
                    validator(*args, **kwargs)
                except Exception as e:
                    raise ValidationError(f"Input validation failed: {e}", 
                                        value=f"function: {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@contextmanager
def with_error_context(context: Dict[str, Any]):
    """Context manager for adding error context.
    
    Args:
        context: Context information to add to errors
        
    Example:
        with with_error_context({'algebra_name': 'my_algebra'}):
            # Operations that might raise errors
            pass
    """
    try:
        yield context
    except Exception as e:
        # Add context to the error if it's a UACalcError
        if isinstance(e, UACalcError):
            e.details.update(context)
        raise

@contextmanager
def safe_operation(operation_name: str, default_value: Any = None):
    """Context manager for safe operation execution with error handling.
    
    Args:
        operation_name: Name of the operation for error reporting
        default_value: Default value to return if operation fails
        
    Yields:
        Context manager for the operation
        
    Example:
        with safe_operation("Test operation", default_value=42) as result:
            # Perform operation
            result.value = some_function()
    """
    class OperationResult:
        def __init__(self):
            self.value = None
            self.success = False
    
    result = OperationResult()
    
    try:
        yield result
        result.success = True
    except Exception as e:
        if isinstance(e, UACalcError):
            raise
        else:
            if default_value is not None:
                result.value = default_value
                result.success = False
            else:
                raise UACalcError(f"Operation failed: {e}")

# Logging integration
class UACalcLogger:
    """Logger for UACalc operations with error tracking."""
    
    def __init__(self, name: str = "uacalc", level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Add handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an error with context.
        
        Args:
            error: The error to log
            context: Optional context information
        """
        context = context or {}
        
        if isinstance(error, UACalcError):
            self.logger.error(f"{error.error_type}: {error.message}", 
                            extra={'context': context, 'error_details': error.details})
        else:
            self.logger.error(f"Unexpected error: {error}", 
                            extra={'context': context, 'traceback': traceback.format_exc()})
    
    def log_operation(self, operation: str, **kwargs):
        """Log an operation.
        
        Args:
            operation: Name of the operation
            **kwargs: Operation parameters
        """
        self.logger.info(f"Operation: {operation}", extra={'params': kwargs})
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance information.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            **kwargs: Additional performance metrics
        """
        self.logger.info(f"Performance: {operation} took {duration:.3f}s", 
                        extra={'duration': duration, 'metrics': kwargs})
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def operation_start(self, operation: str, **kwargs):
        """Log operation start."""
        self.logger.info(f"Operation started: {operation}", extra=kwargs)
    
    def operation_end(self, operation: str, **kwargs):
        """Log operation end."""
        self.logger.info(f"Operation completed: {operation}", extra=kwargs)
    
    def performance_start(self, operation: str, **kwargs):
        """Log performance measurement start."""
        self.logger.debug(f"Performance measurement started: {operation}", extra=kwargs)
    
    def performance_end(self, operation: str, duration: float, **kwargs):
        """Log performance measurement end."""
        self.logger.info(f"Performance measurement completed: {operation} took {duration:.3f}s", 
                        extra={'duration': duration, **kwargs})

# Global logger instance
_logger = UACalcLogger()

def get_logger() -> UACalcLogger:
    """Get the global UACalc logger.
    
    Returns:
        Logger instance
    """
    return _logger

def set_log_level(level: str) -> None:
    """Set the global log level.
    
    Args:
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    _logger.logger.setLevel(getattr(logging, level.upper()))

# Error reporting utilities
class ErrorReporter:
    """Error reporter for collecting and reporting errors."""
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.max_errors = 100
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
    
    def report_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Report an error.
        
        Args:
            error: The error to report
            context: Optional context information
        """
        if len(self.errors) >= self.max_errors:
            warnings.warn("Maximum number of errors reached, dropping oldest")
            self.errors.pop(0)
        
        error_info = {
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'timestamp': time.time(),
            'traceback': traceback.format_exc()
        }
        
        if isinstance(error, UACalcError):
            error_info['details'] = error.details
        
        self.errors.append(error_info)
        self.failed_operations += 1
        _logger.log_error(error, context)
    
    def add_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Add an error to the reporter."""
        self.report_error(error, context)
        self.total_operations += 1
    
    def add_success(self, operation: str, context: Optional[Dict[str, Any]] = None):
        """Add a successful operation."""
        self.successful_operations += 1
        self.total_operations += 1
    
    def add_operation(self, operation: str, success: bool, context: Optional[Dict[str, Any]] = None):
        """Add an operation result."""
        if success:
            self.add_success(operation, context)
        else:
            self.total_operations += 1
    
    def success_rate(self) -> float:
        """Get the success rate."""
        if self.total_operations == 0:
            return 1.0
        return self.successful_operations / self.total_operations
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all reported errors.
        
        Returns:
            List of error information dictionaries
        """
        return self.errors.copy()
    
    def clear_errors(self):
        """Clear all reported errors."""
        self.errors.clear()
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get a summary of error types.
        
        Returns:
            Dictionary mapping error types to counts
        """
        summary = {}
        for error in self.errors:
            error_type = error['error_type']
            summary[error_type] = summary.get(error_type, 0) + 1
        return summary
    
    def error_summary(self) -> Dict[str, Any]:
        """Get a comprehensive error summary."""
        return {
            'total_operations': self.total_operations,
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations,
            'success_rate': self.success_rate(),
            'error_types': self.get_error_summary(),
            'total_errors': len(self.errors)
        }
    
    def operation_summary(self) -> Dict[str, Any]:
        """Get an operation summary."""
        return {
            'total_operations': self.total_operations,
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations,
            'success_rate': self.success_rate()
        }
    
    def clear(self):
        """Clear all data."""
        self.errors.clear()
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
    
    def get_errors_by_operation(self, operation: str) -> List[Dict[str, Any]]:
        """Get errors for a specific operation."""
        return [error for error in self.errors 
                if error.get('context', {}).get('operation') == operation]
    
    def get_errors_by_type(self, error_type: str) -> List[Dict[str, Any]]:
        """Get errors of a specific type."""
        return [error for error in self.errors 
                if error.get('error_type') == error_type]

# Global error reporter instance
_error_reporter = ErrorReporter()

def get_error_reporter() -> ErrorReporter:
    """Get the global error reporter.
    
    Returns:
        ErrorReporter instance
    """
    return _error_reporter

# Backward compatibility
def report_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Report an error using the global error reporter.
    
    Args:
        error: The error to report
        context: Optional context information
    """
    _error_reporter.report_error(error, context)

# Error handling best practices
def handle_errors_gracefully(func: Callable) -> Callable:
    """Decorator for graceful error handling.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UACalcError:
            # Re-raise UACalc errors
            raise
        except Exception as e:
            # Map other errors to UACalcError and report them
            try:
                handle_rust_error(e, {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                })
            except Exception as mapped_error:
                report_error(mapped_error, {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                })
                raise mapped_error
    return wrapper

# Import time for context manager
import time
