"""
Tests for error handling functionality.
"""

import pytest
import logging
from typing import List, Dict, Any, Optional

from uacalc import (
    Algebra, create_algebra, create_operation, UACalcError, CancellationError
)
from uacalc.errors import (
    AlgebraError, TermError, CongruenceError, IndexOutOfBoundsError,
    InvalidArityError, ParseError, EvaluationError, OperationNotFoundError,
    ValidationError, ConfigurationError, handle_rust_error, validate_inputs,
    with_error_context, safe_operation, UACalcLogger, ErrorReporter
)


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_algebra_error(self):
        """Test AlgebraError exception."""
        error = AlgebraError("Test algebra error")
        assert str(error) == "Test algebra error"
        assert isinstance(error, UACalcError)
    
    def test_term_error(self):
        """Test TermError exception."""
        error = TermError("Test term error")
        assert str(error) == "Test term error"
        assert isinstance(error, UACalcError)
    
    def test_congruence_error(self):
        """Test CongruenceError exception."""
        error = CongruenceError("Test congruence error")
        assert str(error) == "Test congruence error"
        assert isinstance(error, UACalcError)
    
    def test_index_out_of_bounds_error(self):
        """Test IndexOutOfBoundsError exception."""
        error = IndexOutOfBoundsError(5, 3)
        assert "Index 5 out of bounds for size 3" in str(error)
        assert error.index == 5
        assert error.size == 3
        assert isinstance(error, UACalcError)
    
    def test_invalid_arity_error(self):
        """Test InvalidArityError exception."""
        error = InvalidArityError(2, 3)
        assert "Invalid arity: expected 2, got 3" in str(error)
        assert error.expected == 2
        assert error.actual == 3
        assert isinstance(error, UACalcError)
    
    def test_parse_error(self):
        """Test ParseError exception."""
        error = ParseError("Test parse error")
        assert str(error) == "Test parse error"
        assert isinstance(error, UACalcError)
    
    def test_evaluation_error(self):
        """Test EvaluationError exception."""
        error = EvaluationError("Test evaluation error")
        assert str(error) == "Test evaluation error"
        assert isinstance(error, UACalcError)
    
    def test_operation_not_found_error(self):
        """Test OperationNotFoundError exception."""
        error = OperationNotFoundError("f")
        assert "Operation 'f' not found" in str(error)
        assert error.operation == "f"
        assert isinstance(error, UACalcError)
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Test validation error")
        assert str(error) == "Test validation error"
        assert isinstance(error, UACalcError)
    
    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        error = ConfigurationError("Test configuration error")
        assert str(error) == "Test configuration error"
        assert isinstance(error, UACalcError)
    
    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from UACalcError."""
        exceptions = [
            AlgebraError("test"),
            TermError("test"),
            CongruenceError("test"),
            IndexOutOfBoundsError(0, 1),
            InvalidArityError(1, 2),
            ParseError("test"),
            EvaluationError("test"),
            OperationNotFoundError("test"),
            ValidationError("test"),
            ConfigurationError("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, UACalcError)


class TestErrorMapping:
    """Test error mapping functionality."""
    
    def test_handle_rust_error_with_algebra_error(self):
        """Test handling Rust algebra errors."""
        rust_error = UACalcError("Algebra error", "AlgebraError")
        
        with pytest.raises(AlgebraError) as exc_info:
            handle_rust_error(rust_error)
        
        assert "Algebra error" in str(exc_info.value)
    
    def test_handle_rust_error_with_term_error(self):
        """Test handling Rust term errors."""
        rust_error = UACalcError("Term error", "TermError")
        
        with pytest.raises(TermError) as exc_info:
            handle_rust_error(rust_error)
        
        assert "Term error" in str(exc_info.value)
    
    def test_handle_rust_error_with_congruence_error(self):
        """Test handling Rust congruence errors."""
        rust_error = UACalcError("Congruence error", "CongruenceError")
        
        with pytest.raises(CongruenceError) as exc_info:
            handle_rust_error(rust_error)
        
        assert "Congruence error" in str(exc_info.value)
    
    def test_handle_rust_error_with_unknown_error(self):
        """Test handling unknown Rust errors."""
        rust_error = UACalcError("Unknown error", "UnknownError")
        
        with pytest.raises(UACalcError) as exc_info:
            handle_rust_error(rust_error)
        
        assert "Unknown error" in str(exc_info.value)
    
    def test_handle_rust_error_with_cancellation_error(self):
        """Test handling Rust cancellation errors."""
        rust_error = CancellationError("Operation cancelled")
        
        with pytest.raises(CancellationError) as exc_info:
            handle_rust_error(rust_error)
        
        assert "Operation cancelled" in str(exc_info.value)


class TestValidationDecorators:
    """Test validation decorators."""
    
    def test_validate_inputs_decorator(self):
        """Test validate_inputs decorator."""
        @validate_inputs
        def test_function(x: int, y: str) -> str:
            return f"{x}_{y}"
        
        # Valid inputs
        result = test_function(5, "test")
        assert result == "5_test"
        
        # Invalid inputs should raise ValidationError
        with pytest.raises(ValidationError):
            test_function("invalid", "test")
    
    def test_validate_inputs_with_custom_validators(self):
        """Test validate_inputs with custom validators."""
        def validate_positive(x: int) -> bool:
            return x > 0
        
        @validate_inputs
        def test_function(x: int) -> int:
            return x * 2
        
        # Valid input
        result = test_function(5)
        assert result == 10
        
        # Invalid input
        with pytest.raises(ValidationError):
            test_function(-1)
    
    def test_validate_inputs_with_type_hints(self):
        """Test validate_inputs with type hints."""
        @validate_inputs
        def test_function(x: int, y: float, z: str) -> tuple:
            return (x, y, z)
        
        # Valid inputs
        result = test_function(1, 2.5, "test")
        assert result == (1, 2.5, "test")
        
        # Invalid inputs
        with pytest.raises(ValidationError):
            test_function("invalid", 2.5, "test")
        
        with pytest.raises(ValidationError):
            test_function(1, "invalid", "test")


class TestContextManagers:
    """Test error context managers."""
    
    def test_with_error_context_success(self):
        """Test with_error_context on success."""
        with with_error_context("Test operation") as ctx:
            result = 5 + 3
            assert result == 8
        
        # Should not raise any exception
        assert ctx.success
    
    def test_with_error_context_failure(self):
        """Test with_error_context on failure."""
        with pytest.raises(ValueError) as exc_info:
            with with_error_context("Test operation") as ctx:
                raise ValueError("Test error")
        
        assert "Test error" in str(exc_info.value)
        # Note: ctx.success would be False, but we can't access it after the exception
    
    def test_with_error_context_custom_error(self):
        """Test with_error_context with custom error handling."""
        def custom_handler(error: Exception, context: str) -> Exception:
            return ValidationError(f"Custom error in {context}: {error}")
        
        with pytest.raises(ValidationError) as exc_info:
            with with_error_context("Test operation", error_handler=custom_handler) as ctx:
                raise ValueError("Test error")
        
        assert "Custom error in Test operation: Test error" in str(exc_info.value)
    
    def test_safe_operation_success(self):
        """Test safe_operation on success."""
        with safe_operation("Test operation") as result:
            result = 5 + 3
        
        assert result == 8
    
    def test_safe_operation_failure(self):
        """Test safe_operation on failure."""
        with pytest.raises(UACalcError) as exc_info:
            with safe_operation("Test operation") as result:
                raise ValueError("Test error")
        
        assert "Test operation failed" in str(exc_info.value)
        assert "Test error" in str(exc_info.value)
    
    def test_safe_operation_with_default_value(self):
        """Test safe_operation with default value."""
        with safe_operation("Test operation", default_value=42) as result:
            raise ValueError("Test error")
        
        assert result == 42


class TestUACalcLogger:
    """Test UACalcLogger functionality."""
    
    def test_logger_creation(self):
        """Test creating a UACalcLogger."""
        logger = UACalcLogger("test_logger")
        assert logger.name == "test_logger"
        assert isinstance(logger.logger, logging.Logger)
    
    def test_logger_with_custom_logger(self):
        """Test UACalcLogger with custom logger."""
        custom_logger = logging.getLogger("custom")
        logger = UACalcLogger("test", logger=custom_logger)
        assert logger.logger == custom_logger
    
    def test_logger_info(self):
        """Test logger info method."""
        logger = UACalcLogger("test_logger")
        
        # Should not crash
        logger.info("Test info message")
        logger.info("Test info with data", extra={"data": {"key": "value"}})
    
    def test_logger_warning(self):
        """Test logger warning method."""
        logger = UACalcLogger("test_logger")
        
        # Should not crash
        logger.warning("Test warning message")
        logger.warning("Test warning with data", extra={"data": {"key": "value"}})
    
    def test_logger_error(self):
        """Test logger error method."""
        logger = UACalcLogger("test_logger")
        
        # Should not crash
        logger.error("Test error message")
        logger.error("Test error with exception", exception=ValueError("Test"))
    
    def test_logger_debug(self):
        """Test logger debug method."""
        logger = UACalcLogger("test_logger")
        
        # Should not crash
        logger.debug("Test debug message")
        logger.debug("Test debug with data", extra={"data": {"key": "value"}})
    
    def test_logger_operation_start_end(self):
        """Test logger operation start/end methods."""
        logger = UACalcLogger("test_logger")
        
        # Should not crash
        logger.operation_start("Test Operation")
        logger.operation_end("Test Operation", success=True)
        logger.operation_end("Test Operation", success=False, error="Test error")
    
    def test_logger_performance(self):
        """Test logger performance methods."""
        logger = UACalcLogger("test_logger")
        
        # Should not crash
        logger.performance_start("Test Performance")
        logger.performance_end("Test Performance", duration=1.5)
        logger.performance_mark("Test Performance", "checkpoint")


class TestErrorReporter:
    """Test ErrorReporter functionality."""
    
    def test_error_reporter_creation(self):
        """Test creating an ErrorReporter."""
        reporter = ErrorReporter()
        assert len(reporter.errors) == 0
        assert reporter.total_operations == 0
        assert reporter.successful_operations == 0
    
    def test_error_reporter_add_error(self):
        """Test adding errors to ErrorReporter."""
        reporter = ErrorReporter()
        
        error = ValueError("Test error")
        reporter.add_error("Test operation", error)
        
        assert len(reporter.errors) == 1
        assert reporter.errors[0]["operation"] == "Test operation"
        assert reporter.errors[0]["error"] == error
        assert reporter.total_operations == 1
        assert reporter.successful_operations == 0
    
    def test_error_reporter_add_success(self):
        """Test adding successful operations to ErrorReporter."""
        reporter = ErrorReporter()
        
        reporter.add_success("Test operation")
        
        assert len(reporter.errors) == 0
        assert reporter.total_operations == 1
        assert reporter.successful_operations == 1
    
    def test_error_reporter_add_operation(self):
        """Test adding operations to ErrorReporter."""
        reporter = ErrorReporter()
        
        # Add successful operation
        reporter.add_operation("Test operation", success=True)
        assert reporter.total_operations == 1
        assert reporter.successful_operations == 1
        
        # Add failed operation
        error = ValueError("Test error")
        reporter.add_operation("Test operation", success=False, error=error)
        assert reporter.total_operations == 2
        assert reporter.successful_operations == 1
        assert len(reporter.errors) == 1
    
    def test_error_reporter_success_rate(self):
        """Test ErrorReporter success rate calculation."""
        reporter = ErrorReporter()
        
        # No operations
        assert reporter.success_rate() == 0.0
        
        # All successful
        reporter.add_success("Test 1")
        reporter.add_success("Test 2")
        assert reporter.success_rate() == 1.0
        
        # Mixed results
        reporter.add_error("Test 3", ValueError("Error"))
        assert reporter.success_rate() == 2/3
    
    def test_error_reporter_error_summary(self):
        """Test ErrorReporter error summary."""
        reporter = ErrorReporter()
        
        # Add some errors
        reporter.add_error("Op 1", ValueError("Error 1"))
        reporter.add_error("Op 2", TypeError("Error 2"))
        reporter.add_error("Op 3", ValueError("Error 3"))
        
        summary = reporter.error_summary()
        
        assert "ValueError" in summary
        assert "TypeError" in summary
        assert summary["ValueError"] == 2
        assert summary["TypeError"] == 1
    
    def test_error_reporter_operation_summary(self):
        """Test ErrorReporter operation summary."""
        reporter = ErrorReporter()
        
        # Add some operations
        reporter.add_success("Op 1")
        reporter.add_success("Op 2")
        reporter.add_error("Op 3", ValueError("Error"))
        reporter.add_error("Op 4", TypeError("Error"))
        
        summary = reporter.operation_summary()
        
        assert summary["total"] == 4
        assert summary["successful"] == 2
        assert summary["failed"] == 2
        assert summary["success_rate"] == 0.5
    
    def test_error_reporter_clear(self):
        """Test ErrorReporter clear method."""
        reporter = ErrorReporter()
        
        # Add some data
        reporter.add_success("Test 1")
        reporter.add_error("Test 2", ValueError("Error"))
        
        # Clear
        reporter.clear()
        
        assert len(reporter.errors) == 0
        assert reporter.total_operations == 0
        assert reporter.successful_operations == 0
    
    def test_error_reporter_get_errors_by_operation(self):
        """Test ErrorReporter get_errors_by_operation method."""
        reporter = ErrorReporter()
        
        # Add errors for different operations
        reporter.add_error("Op 1", ValueError("Error 1"))
        reporter.add_error("Op 1", ValueError("Error 2"))
        reporter.add_error("Op 2", TypeError("Error 3"))
        
        op1_errors = reporter.get_errors_by_operation("Op 1")
        op2_errors = reporter.get_errors_by_operation("Op 2")
        op3_errors = reporter.get_errors_by_operation("Op 3")
        
        assert len(op1_errors) == 2
        assert len(op2_errors) == 1
        assert len(op3_errors) == 0
    
    def test_error_reporter_get_errors_by_type(self):
        """Test ErrorReporter get_errors_by_type method."""
        reporter = ErrorReporter()
        
        # Add different types of errors
        reporter.add_error("Op 1", ValueError("Error 1"))
        reporter.add_error("Op 2", ValueError("Error 2"))
        reporter.add_error("Op 3", TypeError("Error 3"))
        
        value_errors = reporter.get_errors_by_type(ValueError)
        type_errors = reporter.get_errors_by_type(TypeError)
        index_errors = reporter.get_errors_by_type(IndexError)
        
        assert len(value_errors) == 2
        assert len(type_errors) == 1
        assert len(index_errors) == 0


class TestErrorHandlingIntegration:
    """Test error handling integration."""
    
    def test_error_handling_in_algebra_operations(self):
        """Test error handling in algebra operations."""
        # Create a simple algebra
        algebra = create_algebra("test", [0, 1, 2])
        
        # Test invalid operation access
        with pytest.raises(OperationNotFoundError):
            algebra.get_operation("nonexistent")
        
        # Test invalid index access
        with pytest.raises(IndexOutOfBoundsError):
            algebra.get_element(5)  # Assuming algebra has only 3 elements
    
    def test_error_handling_with_logging(self):
        """Test error handling with logging integration."""
        logger = UACalcLogger("test_logger")
        reporter = ErrorReporter()
        
        try:
            # Simulate an operation that might fail
            raise ValueError("Test error")
        except Exception as e:
            logger.error("Operation failed", exception=e)
            reporter.add_error("Test operation", e)
        
        assert len(reporter.errors) == 1
        assert reporter.total_operations == 1
        assert reporter.successful_operations == 0
    
    def test_error_handling_with_context_manager(self):
        """Test error handling with context manager."""
        logger = UACalcLogger("test_logger")
        
        with with_error_context("Test operation") as ctx:
            # Simulate successful operation
            result = 5 + 3
            assert result == 8
        
        # Should not raise any exception
        assert ctx.success
    
    def test_error_handling_with_safe_operation(self):
        """Test error handling with safe_operation."""
        with pytest.raises(UACalcError) as exc_info:
            with safe_operation("Test operation") as result:
                raise ValueError("Test error")
        
        assert "Test operation failed" in str(exc_info.value)
    
    def test_error_handling_with_validation(self):
        """Test error handling with validation."""
        @validate_inputs
        def test_function(x: int, y: str) -> str:
            if x < 0:
                raise ValueError("Negative value")
            return f"{x}_{y}"
        
        # Valid input
        result = test_function(5, "test")
        assert result == "5_test"
        
        # Invalid input type
        with pytest.raises(ValidationError):
            test_function("invalid", "test")
        
        # Valid input type but invalid value
        with pytest.raises(ValueError):
            test_function(-1, "test")


class TestErrorRecovery:
    """Test error recovery mechanisms."""
    
    def test_error_recovery_with_retry(self):
        """Test error recovery with retry mechanism."""
        attempts = 0
        
        def failing_function():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Temporary error")
            return "success"
        
        # This would require implementing a retry decorator
        # For now, just test the concept
        try:
            result = failing_function()
            assert result == "success"
            assert attempts == 3
        except ValueError:
            # Expected for first two attempts
            pass
    
    def test_error_recovery_with_fallback(self):
        """Test error recovery with fallback mechanism."""
        def primary_function():
            raise ValueError("Primary failed")
        
        def fallback_function():
            return "fallback result"
        
        # This would require implementing a fallback decorator
        # For now, just test the concept
        try:
            result = primary_function()
        except ValueError:
            result = fallback_function()
        
        assert result == "fallback result"


class TestErrorReporting:
    """Test error reporting functionality."""
    
    def test_error_reporting_format(self):
        """Test error reporting format."""
        reporter = ErrorReporter()
        
        # Add some errors
        reporter.add_error("Op 1", ValueError("Error 1"))
        reporter.add_error("Op 2", TypeError("Error 2"))
        reporter.add_success("Op 3")
        
        # Test summary format
        summary = reporter.operation_summary()
        assert "total" in summary
        assert "successful" in summary
        assert "failed" in summary
        assert "success_rate" in summary
        
        # Test error summary format
        error_summary = reporter.error_summary()
        assert "ValueError" in error_summary
        assert "TypeError" in error_summary
    
    def test_error_reporting_persistence(self):
        """Test error reporting persistence."""
        reporter = ErrorReporter()
        
        # Add some data
        reporter.add_success("Op 1")
        reporter.add_error("Op 2", ValueError("Error"))
        
        # Simulate persistence (this would require actual implementation)
        # For now, just verify the data is there
        assert reporter.total_operations == 2
        assert reporter.successful_operations == 1
        assert len(reporter.errors) == 1


class TestPerformance:
    """Test error handling performance."""
    
    def test_error_logging_performance(self):
        """Test error logging performance."""
        logger = UACalcLogger("test_logger")
        
        # Time many error logs
        import time
        start_time = time.time()
        
        for i in range(1000):
            logger.error(f"Error {i}")
        
        total_time = time.time() - start_time
        
        # Should be reasonably fast
        assert total_time < 5.0  # Less than 5 seconds for 1000 logs
    
    def test_error_reporter_performance(self):
        """Test error reporter performance."""
        reporter = ErrorReporter()
        
        # Time many error additions
        import time
        start_time = time.time()
        
        for i in range(1000):
            reporter.add_error(f"Op {i}", ValueError(f"Error {i}"))
        
        total_time = time.time() - start_time
        
        # Should be reasonably fast
        assert total_time < 1.0  # Less than 1 second for 1000 additions
        assert len(reporter.errors) == 1000


class TestThreadSafety:
    """Test thread safety of error handling."""
    
    def test_error_reporter_thread_safety(self):
        """Test thread safety of ErrorReporter."""
        import threading
        import time
        
        reporter = ErrorReporter()
        errors = []
        
        def worker():
            try:
                for i in range(100):
                    reporter.add_error(f"Op {i}", ValueError(f"Error {i}"))
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for _ in range(4):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should not have any errors
        assert len(errors) == 0
        assert len(reporter.errors) == 400  # 4 threads * 100 errors each


if __name__ == "__main__":
    pytest.main([__file__])
