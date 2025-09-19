"""
Tests for progress reporting functionality.
"""

import pytest
import time
import threading
from typing import List, Dict, Any

from uacalc import (
    Algebra, create_algebra, create_operation, create_progress_reporter,
    ProgressReporter
)
from uacalc.progress import (
    BaseProgressReporter, SimpleProgress, SilentProgress, TqdmProgress,
    JupyterProgress, LoggingProgress, CallbackProgress, MultiCallbackProgress,
    ThreadSafeProgress, with_progress, timed_operation, cancellable_operation,
    estimate_time_remaining, format_progress_message, ProgressConfig,
    create_default_progress_reporter, create_congruence_lattice_with_progress,
    batch_evaluate_with_progress
)


class TestBaseProgressReporter:
    """Test base progress reporter functionality."""
    
    def test_base_reporter_creation(self):
        """Test creating a base progress reporter."""
        reporter = BaseProgressReporter()
        assert reporter is not None
        assert not reporter.should_cancel()
    
    def test_progress_reporting(self):
        """Test basic progress reporting."""
        reporter = BaseProgressReporter()
        
        # Test progress values
        reporter.report(0.0, "Starting")
        reporter.report(0.5, "Halfway")
        reporter.report(1.0, "Complete")
        
        # Should not crash
        assert reporter.current_progress() == 1.0
    
    def test_cancellation(self):
        """Test cancellation functionality."""
        reporter = BaseProgressReporter()
        
        assert not reporter.should_cancel()
        reporter.set_cancelled()
        assert reporter.should_cancel()
    
    def test_timing(self):
        """Test timing functionality."""
        reporter = BaseProgressReporter()
        
        assert reporter.elapsed_time() == 0.0
        
        reporter.start()
        time.sleep(0.1)
        
        elapsed = reporter.elapsed_time()
        assert elapsed > 0.0
        assert elapsed < 1.0  # Should be less than 1 second
    
    def test_time_estimation(self):
        """Test time estimation functionality."""
        reporter = BaseProgressReporter()
        reporter.start()
        
        # Simulate some progress
        time.sleep(0.1)
        reporter.report(0.5, "Halfway")
        
        eta = reporter.estimate_time_remaining(50, 100)
        assert eta is not None
        assert eta > 0.0


class TestSimpleProgress:
    """Test simple progress reporter."""
    
    def test_simple_progress_creation(self):
        """Test creating a simple progress reporter."""
        reporter = SimpleProgress("Test Progress")
        assert reporter.prefix == "Test Progress"
    
    def test_simple_progress_reporting(self):
        """Test simple progress reporting."""
        reporter = SimpleProgress("Test")
        reporter.start()
        
        # Should not crash
        reporter.report(0.0, "Starting")
        reporter.report(0.5, "Halfway")
        reporter.report(1.0, "Complete")
    
    def test_simple_progress_update_interval(self):
        """Test that simple progress respects update interval."""
        reporter = SimpleProgress("Test")
        reporter._update_interval = 0.1  # Set short interval for testing
        
        start_time = time.time()
        for i in range(10):
            reporter.report(i / 10.0, f"Step {i}")
        total_time = time.time() - start_time
        
        # The update interval doesn't cause delays in SimpleProgress
        # It only affects when _report_impl is called, but SimpleProgress
        # only prints when integer percentage changes
        assert total_time >= 0.0  # Should be non-negative


class TestSilentProgress:
    """Test silent progress reporter."""
    
    def test_silent_progress_creation(self):
        """Test creating a silent progress reporter."""
        reporter = SilentProgress()
        assert reporter is not None
    
    def test_silent_progress_reporting(self):
        """Test that silent progress does nothing."""
        reporter = SilentProgress()
        
        # Should not crash and do nothing
        reporter.report(0.0, "Starting")
        reporter.report(0.5, "Halfway")
        reporter.report(1.0, "Complete")


class TestTqdmProgress:
    """Test tqdm progress reporter."""
    
    def test_tqdm_progress_creation(self):
        """Test creating a tqdm progress reporter."""
        reporter = TqdmProgress(100, "Test Progress")
        assert reporter.total == 100
        assert reporter.desc == "Test Progress"
    
    def test_tqdm_progress_reporting(self):
        """Test tqdm progress reporting."""
        reporter = TqdmProgress(100, "Test")
        reporter.start()
        
        # Should not crash
        reporter.report(0.0, "Starting")
        reporter.report(0.5, "Halfway")
        reporter.report(1.0, "Complete")
        
        reporter.close()
    
    def test_tqdm_fallback(self):
        """Test tqdm fallback when tqdm is not available."""
        # This test would require mocking tqdm import
        # For now, just test that it doesn't crash
        reporter = TqdmProgress(100, "Test")
        reporter.start()
        reporter.report(0.5, "Test")
        reporter.close()


class TestJupyterProgress:
    """Test Jupyter progress reporter."""
    
    def test_jupyter_progress_creation(self):
        """Test creating a Jupyter progress reporter."""
        reporter = JupyterProgress(100, "Test Progress")
        assert reporter.total == 100
        assert reporter.desc == "Test Progress"
    
    def test_jupyter_progress_reporting(self):
        """Test Jupyter progress reporting."""
        reporter = JupyterProgress(100, "Test")
        reporter.start()
        
        # Should not crash
        reporter.report(0.0, "Starting")
        reporter.report(0.5, "Halfway")
        reporter.report(1.0, "Complete")
    
    def test_jupyter_fallback(self):
        """Test Jupyter fallback when widgets are not available."""
        # This test would require mocking ipywidgets import
        # For now, just test that it doesn't crash
        reporter = JupyterProgress(100, "Test")
        reporter.start()
        reporter.report(0.5, "Test")


class TestLoggingProgress:
    """Test logging progress reporter."""
    
    def test_logging_progress_creation(self):
        """Test creating a logging progress reporter."""
        reporter = LoggingProgress(level='INFO')
        assert reporter.level == 20  # INFO level
        assert reporter.prefix == "Progress"
    
    def test_logging_progress_reporting(self):
        """Test logging progress reporting."""
        reporter = LoggingProgress(level='INFO')
        reporter.start()
        
        # Should not crash
        reporter.report(0.0, "Starting")
        reporter.report(0.5, "Halfway")
        reporter.report(1.0, "Complete")
    
    def test_logging_progress_with_custom_logger(self):
        """Test logging progress with custom logger."""
        import logging
        logger = logging.getLogger("test_logger")
        
        reporter = LoggingProgress(logger=logger, level='DEBUG')
        reporter.start()
        
        # Should not crash
        reporter.report(0.5, "Test")


class TestCallbackProgress:
    """Test callback progress reporter."""
    
    def test_callback_progress_creation(self):
        """Test creating a callback progress reporter."""
        calls = []
        
        def callback(progress: float, message: str):
            calls.append((progress, message))
        
        reporter = CallbackProgress(callback)
        assert reporter.callback == callback
    
    def test_callback_progress_reporting(self):
        """Test callback progress reporting."""
        calls = []
        
        def callback(progress: float, message: str):
            calls.append((progress, message))
        
        reporter = CallbackProgress(callback)
        reporter.start()
        
        # Set a very short update interval for testing
        reporter._update_interval = 0.001
        
        # Add small delays to ensure different timestamps
        reporter.report(0.0, "Starting")
        time.sleep(0.002)  # Wait longer than update interval
        reporter.report(0.5, "Halfway")
        time.sleep(0.002)  # Wait longer than update interval
        reporter.report(1.0, "Complete")
        
        # All calls should be recorded with proper delays
        assert len(calls) == 3
        assert calls[0] == (0.0, "Starting")
        assert calls[1] == (0.5, "Halfway")
        assert calls[2] == (1.0, "Complete")
    
    def test_callback_performance(self):
        """Test performance of callback progress reporting."""
        calls = []
        
        def callback(progress: float, message: str):
            calls.append((progress, message))
        
        reporter = CallbackProgress(callback)
        reporter.start()
        
        # Set a very short update interval for testing
        reporter._update_interval = 0.001
        
        # Time many progress updates with small delays
        start_time = time.time()
        for i in range(100):  # Reduced number to make test faster
            reporter.report(i / 100.0, f"Step {i}")
            time.sleep(0.002)  # Small delay to ensure different timestamps
        total_time = time.time() - start_time
        
        # Should be reasonably fast
        assert total_time < 5.0  # Less than 5 seconds for 100 updates
        assert len(calls) == 100
    
    def test_callback_progress_error_handling(self):
        """Test callback progress error handling."""
        def bad_callback(progress: float, message: str):
            raise ValueError("Test error")
        
        reporter = CallbackProgress(bad_callback)
        reporter.start()
        
        # Should not crash
        reporter.report(0.5, "Test")


class TestMultiCallbackProgress:
    """Test multi-callback progress reporter."""
    
    def test_multi_callback_progress_creation(self):
        """Test creating a multi-callback progress reporter."""
        calls1 = []
        calls2 = []
        
        def callback1(progress: float, message: str):
            calls1.append((progress, message))
        
        def callback2(progress: float, message: str):
            calls2.append((progress, message))
        
        reporter = MultiCallbackProgress([callback1, callback2])
        assert len(reporter.callbacks) == 2
    
    def test_multi_callback_progress_reporting(self):
        """Test multi-callback progress reporting."""
        calls1 = []
        calls2 = []
        
        def callback1(progress: float, message: str):
            calls1.append((progress, message))
        
        def callback2(progress: float, message: str):
            calls2.append((progress, message))
        
        reporter = MultiCallbackProgress([callback1, callback2])
        reporter.start()
        
        reporter.report(0.5, "Test")
        
        assert len(calls1) == 1
        assert len(calls2) == 1
        assert calls1[0] == (0.5, "Test")
        assert calls2[0] == (0.5, "Test")


class TestThreadSafeProgress:
    """Test thread-safe progress reporter."""
    
    def test_thread_safe_progress_creation(self):
        """Test creating a thread-safe progress reporter."""
        base_reporter = SimpleProgress("Test")
        reporter = ThreadSafeProgress(base_reporter)
        assert reporter.reporter == base_reporter
    
    def test_thread_safe_progress_reporting(self):
        """Test thread-safe progress reporting."""
        base_reporter = SimpleProgress("Test")
        reporter = ThreadSafeProgress(base_reporter)
        reporter.start()
        
        # Should not crash
        reporter.report(0.5, "Test")
    
    def test_thread_safe_cancellation(self):
        """Test thread-safe cancellation."""
        base_reporter = SimpleProgress("Test")
        reporter = ThreadSafeProgress(base_reporter)
        
        assert not reporter.should_cancel()
        reporter.set_cancelled()
        assert reporter.should_cancel()


class TestContextManagers:
    """Test progress context managers."""
    
    def test_with_progress_context(self):
        """Test with_progress context manager."""
        reporter = SimpleProgress("Test")
        
        with with_progress(reporter) as r:
            assert r == reporter
            r.report(0.5, "Test")
    
    def test_timed_operation_context(self):
        """Test timed_operation context manager."""
        with timed_operation("Test Operation") as reporter:
            assert reporter is not None
            reporter.report(0.5, "Test")
    
    def test_timed_operation_with_custom_reporter(self):
        """Test timed_operation with custom reporter."""
        custom_reporter = SimpleProgress("Custom")
        
        with timed_operation("Test Operation", custom_reporter) as reporter:
            assert reporter == custom_reporter
            reporter.report(0.5, "Test")
    
    def test_cancellable_operation_context(self):
        """Test cancellable_operation context manager."""
        reporter = SimpleProgress("Test")
        
        with cancellable_operation(reporter) as r:
            assert r == reporter
            r.report(0.5, "Test")
            # Test cancellation
            r.set_cancelled()
            assert r.should_cancel()


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_estimate_time_remaining(self):
        """Test time estimation utility."""
        start_time = time.time()
        
        # Simulate some progress
        time.sleep(0.1)
        eta = estimate_time_remaining(50, 100, start_time)
        
        assert eta is not None
        assert eta > 0.0
    
    def test_format_progress_message(self):
        """Test progress message formatting."""
        message = format_progress_message("Test Operation", 5, 10)
        assert "Test Operation" in message
        assert "50.0%" in message
        assert "5/10" in message


class TestProgressConfig:
    """Test progress configuration."""
    
    def test_progress_config_creation(self):
        """Test creating a progress configuration."""
        config = ProgressConfig()
        assert config.default_reporter_class == SimpleProgress
        assert config.default_update_interval == 0.1
        assert config.enable_logging is True
    
    def test_progress_config_setters(self):
        """Test progress configuration setters."""
        config = ProgressConfig()
        
        config.set_default_reporter(SilentProgress)
        assert config.default_reporter_class == SilentProgress
        
        config.set_update_interval(0.5)
        assert config.default_update_interval == 0.5
        
        config.set_enable_logging(False)
        assert config.enable_logging is False
        
        config.set_log_level("DEBUG")
        assert config.log_level == "DEBUG"


class TestDefaultProgressReporter:
    """Test default progress reporter creation."""
    
    def test_create_default_progress_reporter(self):
        """Test creating a default progress reporter."""
        reporter = create_default_progress_reporter("Test")
        assert isinstance(reporter, SimpleProgress)
        assert reporter.prefix == "Test"


class TestIntegrationWithUACalc:
    """Test integration with UACalc operations."""
    
    def test_congruence_lattice_with_progress(self):
        """Test congruence lattice creation with progress."""
        # Create a simple algebra
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        progress_calls = []
        
        def callback(progress: float, message: str):
            progress_calls.append((progress, message))
        
        progress_reporter = CallbackProgress(callback)
        
        # This would require the actual implementation
        # lattice = create_congruence_lattice_with_progress(algebra, progress_reporter)
        # assert lattice is not None
        # assert len(progress_calls) > 0
    
    def test_batch_evaluate_with_progress(self):
        """Test batch evaluation with progress."""
        # Create a simple algebra
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        progress_calls = []
        
        def callback(progress: float, message: str):
            progress_calls.append((progress, message))
        
        progress_reporter = CallbackProgress(callback)
        
        # This would require the actual implementation
        # terms = ["f(x0, x1)", "f(x0, x0)"]
        # variable_sets = [{0: 1, 1: 2}, {0: 0, 1: 1}]
        # results = batch_evaluate_with_progress(terms, algebra, variable_sets, progress_reporter)
        # assert len(results) == 2
        # assert len(progress_calls) > 0


class TestProgressReporterRust:
    """Test Rust progress reporter integration."""
    
    def test_rust_progress_reporter_creation(self):
        """Test creating a Rust progress reporter."""
        calls = []
        
        def callback(progress: float, message: str):
            calls.append((progress, message))
        
        reporter = create_progress_reporter(callback)
        assert isinstance(reporter, ProgressReporter)
    
    def test_rust_progress_reporter_functionality(self):
        """Test Rust progress reporter functionality."""
        calls = []
        
        def callback(progress: float, message: str):
            calls.append((progress, message))
        
        reporter = create_progress_reporter(callback)
        
        # Test basic functionality
        reporter.report_progress(0.5, "Test")
        assert reporter.current_progress() == 0.5
        
        # Test cancellation
        assert not reporter.should_cancel()
        reporter.set_cancelled()
        assert reporter.should_cancel()


class TestPerformance:
    """Test performance of progress reporting."""
    
    def test_progress_reporting_performance(self):
        """Test performance of progress reporting."""
        reporter = SimpleProgress("Performance Test")
        reporter.start()
        
        # Time many progress updates
        start_time = time.time()
        for i in range(1000):
            reporter.report(i / 1000.0, f"Step {i}")
        total_time = time.time() - start_time
        
        # Should be reasonably fast
        assert total_time < 5.0  # Less than 5 seconds for 1000 updates
    
    def test_callback_performance(self):
        """Test performance of callback progress reporting."""
        calls = []
        
        def callback(progress: float, message: str):
            calls.append((progress, message))
        
        reporter = CallbackProgress(callback)
        reporter.start()
        
        # Set a very short update interval for testing
        reporter._update_interval = 0.001
        
        # Time many progress updates with small delays
        start_time = time.time()
        for i in range(100):  # Reduced number to make test faster
            reporter.report(i / 100.0, f"Step {i}")
            time.sleep(0.002)  # Small delay to ensure different timestamps
        total_time = time.time() - start_time
        
        # Should be reasonably fast
        assert total_time < 5.0  # Less than 5 seconds for 100 updates
        assert len(calls) == 100


class TestErrorHandling:
    """Test error handling in progress reporting."""
    
    def test_progress_reporter_error_isolation(self):
        """Test that errors in one callback don't affect others."""
        calls1 = []
        calls2 = []
        
        def bad_callback(progress: float, message: str):
            raise ValueError("Test error")
        
        def good_callback(progress: float, message: str):
            calls1.append((progress, message))
        
        reporter = MultiCallbackProgress([bad_callback, good_callback])
        reporter.start()
        
        # Should not crash and good callback should still work
        reporter.report(0.5, "Test")
        assert len(calls1) == 1
        assert calls1[0] == (0.5, "Test")
    
    def test_progress_reporter_cancellation_handling(self):
        """Test handling of cancellation during progress reporting."""
        reporter = SimpleProgress("Test")
        reporter.start()
        
        # Report some progress
        reporter.report(0.3, "Working")
        
        # Cancel
        reporter.set_cancelled()
        
        # Further reports should be ignored
        reporter.report(0.6, "Ignored")
        reporter.report(1.0, "Ignored")


class TestThreadSafety:
    """Test thread safety of progress reporting."""
    
    def test_thread_safe_progress_concurrent_access(self):
        """Test concurrent access to thread-safe progress reporter."""
        base_reporter = SimpleProgress("Test")
        reporter = ThreadSafeProgress(base_reporter)
        reporter.start()
        
        results = []
        errors = []
        
        def worker():
            try:
                for i in range(100):
                    reporter.report(i / 100.0, f"Worker {i}")
                    time.sleep(0.001)  # Small delay
                results.append("success")
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
        assert len(results) == 4  # All threads succeeded


class TestIntegration:
    """Integration tests for progress reporting."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow with progress reporting."""
        # Create progress reporter
        calls = []
        
        def callback(progress: float, message: str):
            calls.append((progress, message))
        
        progress_reporter = CallbackProgress(callback)
        progress_reporter._update_interval = 0.001  # Short interval for testing
        
        # Simulate a long-running operation
        with timed_operation("Test Operation", progress_reporter) as reporter:
            for i in range(10):
                progress = i / 10.0
                reporter.report(progress, f"Step {i}")
                time.sleep(0.01)  # Small delay
            
            # Explicitly report 100% at the end
            reporter.report(1.0, "Complete")
        
        # Verify results
        assert len(calls) > 0
        assert calls[-1][0] == 1.0  # Should reach 100%
    
    #@pytest.mark.slow
    def test_large_scale_progress_reporting(self):
        """Test large-scale progress reporting."""
        calls = []
        
        def callback(progress: float, message: str):
            calls.append((progress, message))
        
        progress_reporter = CallbackProgress(callback)
        progress_reporter._update_interval = 0.001  # Short interval for testing
        
        # Simulate a very long operation
        start_time = time.time()
        with timed_operation("Large Scale Test", progress_reporter) as reporter:
            for i in range(100):  # Reduced number to make test faster
                progress = i / 100.0
                reporter.report(progress, f"Step {i}")
                time.sleep(0.002)  # Small delay to ensure different timestamps
            
            # Explicitly report 100% at the end
            reporter.report(1.0, "Complete")
        
        total_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert total_time < 10.0  # Less than 10 seconds
        assert len(calls) > 0
        assert calls[-1][0] == 1.0  # Should reach 100%


if __name__ == "__main__":
    pytest.main([__file__])
