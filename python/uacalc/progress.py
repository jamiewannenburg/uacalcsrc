"""
Progress Reporting System

This module provides a comprehensive progress reporting system for long-running
operations in universal algebra computations.
"""

from typing import Optional, Callable, Dict, Any, Union, List
from typing_extensions import Protocol
import time
import threading
import warnings
from contextlib import contextmanager

from . import ProgressReporter, create_progress_reporter

class ProgressCallback(Protocol):
    """Protocol for progress callback functions."""
    def __call__(self, progress: float, message: str) -> None: ...

class BaseProgressReporter:
    """Abstract base class for progress reporters."""
    
    def __init__(self):
        self._cancelled = False
        self._start_time = None
        self._last_update_time = 0
        self._update_interval = 0.1  # Minimum seconds between updates
        self._current_progress = 0.0
    
    def report(self, progress: float, message: str = "") -> None:
        """Report progress.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional message describing current operation
        """
        if self._cancelled:
            return
        
        self._current_progress = progress
        
        current_time = time.time()
        if current_time - self._last_update_time >= self._update_interval:
            self._report_impl(progress, message)
            self._last_update_time = current_time
    
    def _report_impl(self, progress: float, message: str) -> None:
        """Implementation of progress reporting. Override in subclasses."""
        pass
    
    def should_cancel(self) -> bool:
        """Check if the operation should be cancelled."""
        return self._cancelled
    
    def set_cancelled(self) -> None:
        """Mark the operation as cancelled."""
        self._cancelled = True
    
    def start(self) -> None:
        """Start timing the operation."""
        self._start_time = time.time()
    
    def elapsed_time(self) -> float:
        """Get elapsed time since start."""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time
    
    def estimate_time_remaining(self, current: int, total: int) -> Optional[float]:
        """Estimate time remaining based on current progress.
        
        Args:
            current: Current progress value
            total: Total progress value
            
        Returns:
            Estimated time remaining in seconds, or None if not enough data
        """
        if self._start_time is None or current <= 0:
            return None
        
        elapsed = self.elapsed_time()
        if elapsed <= 0:
            return None
        
        rate = current / elapsed
        if rate <= 0:
            return None
        
        remaining = (total - current) / rate
        return remaining
    
    def current_progress(self) -> float:
        """Get the current progress value.
        
        Returns:
            Current progress value between 0.0 and 1.0
        """
        return self._current_progress

class SimpleProgress(BaseProgressReporter):
    """Simple progress reporter that prints to stdout."""
    
    def __init__(self, prefix: str = "Progress"):
        super().__init__()
        self.prefix = prefix
        self._last_progress = 0
    
    def _report_impl(self, progress: float, message: str) -> None:
        current = int(progress * 100)
        if current > self._last_progress:
            elapsed = self.elapsed_time()
            eta = self.estimate_time_remaining(current, 100)
            
            status = f"{self.prefix}: {progress:.1%}"
            if message:
                status += f" - {message}"
            if elapsed > 0:
                status += f" (elapsed: {elapsed:.1f}s"
                if eta is not None:
                    status += f", ETA: {eta:.1f}s"
                status += ")"
            
            print(status)
            self._last_progress = current

class SilentProgress(BaseProgressReporter):
    """Silent progress reporter that does nothing."""
    
    def _report_impl(self, progress: float, message: str) -> None:
        pass

class TqdmProgress(BaseProgressReporter):
    """Progress reporter using tqdm library."""
    
    def __init__(self, total: int = 100, desc: str = "Progress", **kwargs):
        super().__init__()
        self.total = total
        self.desc = desc
        self.kwargs = kwargs
        self._tqdm = None
        self._available = False
        
        try:
            from tqdm import tqdm
            self._tqdm_class = tqdm
            self._available = True
        except ImportError:
            warnings.warn("tqdm not available, falling back to SimpleProgress")
            self._fallback = SimpleProgress(desc)
    
    def start(self) -> None:
        super().start()
        if self._available:
            self._tqdm = self._tqdm_class(
                total=self.total,
                desc=self.desc,
                **self.kwargs
            )
        else:
            self._fallback.start()
    
    def _report_impl(self, progress: float, message: str) -> None:
        if self._available and self._tqdm is not None:
            current = int(progress * self.total)
            self._tqdm.n = current
            if message:
                self._tqdm.set_postfix_str(message)
            self._tqdm.refresh()
        elif not self._available:
            self._fallback.report(progress, message)
    
    def close(self) -> None:
        """Close the progress bar."""
        if self._available and self._tqdm is not None:
            self._tqdm.close()
        elif not self._available:
            self._fallback.close()

class JupyterProgress(BaseProgressReporter):
    """Progress reporter for Jupyter notebooks using IPython widgets."""
    
    def __init__(self, total: int = 100, desc: str = "Progress"):
        super().__init__()
        self.total = total
        self.desc = desc
        self._widget = None
        self._available = False
        
        try:
            import ipywidgets as widgets
            from IPython.display import display
            self._widgets = widgets
            self._display = display
            self._available = True
        except ImportError:
            warnings.warn("IPython widgets not available, falling back to SimpleProgress")
            self._fallback = SimpleProgress(desc)
    
    def start(self) -> None:
        super().start()
        if self._available:
            self._widget = self._widgets.HTML(
                value=f"<div>{self.desc}: 0%</div>",
                layout=self._widgets.Layout(width='100%')
            )
            self._display(self._widget)
        else:
            self._fallback.start()
    
    def _report_impl(self, progress: float, message: str) -> None:
        if self._available and self._widget is not None:
            current = int(progress * 100)
            status = f"{self.desc}: {progress:.1%}"
            if message:
                status += f" - {message}"
            
            elapsed = self.elapsed_time()
            if elapsed > 0:
                eta = self.estimate_time_remaining(current, 100)
                status += f" (elapsed: {elapsed:.1f}s"
                if eta is not None:
                    status += f", ETA: {eta:.1f}s"
                status += ")"
            
            self._widget.value = f"<div>{status}</div>"
        elif not self._available:
            self._fallback.report(progress, message)

class LoggingProgress(BaseProgressReporter):
    """Progress reporter that logs to Python logging system."""
    
    def __init__(self, logger=None, level='INFO', prefix: str = "Progress"):
        super().__init__()
        import logging
        self.logger = logger or logging.getLogger(__name__)
        self.level = getattr(logging, level.upper())
        self.prefix = prefix
        self._last_progress = 0
    
    def _report_impl(self, progress: float, message: str) -> None:
        current = int(progress * 100)
        if current > self._last_progress:
            status = f"{self.prefix}: {progress:.1%}"
            if message:
                status += f" - {message}"
            
            elapsed = self.elapsed_time()
            if elapsed > 0:
                eta = self.estimate_time_remaining(current, 100)
                status += f" (elapsed: {elapsed:.1f}s"
                if eta is not None:
                    status += f", ETA: {eta:.1f}s"
                status += ")"
            
            self.logger.log(self.level, status)
            self._last_progress = current

class CallbackProgress(BaseProgressReporter):
    """Progress reporter that calls a custom callback function."""
    
    def __init__(self, callback: ProgressCallback):
        super().__init__()
        self.callback = callback
    
    def _report_impl(self, progress: float, message: str) -> None:
        try:
            self.callback(progress, message)
        except Exception as e:
            warnings.warn(f"Progress callback failed: {e}")

class MultiCallbackProgress(BaseProgressReporter):
    """Progress reporter that calls multiple callbacks."""
    
    def __init__(self, callbacks: List[ProgressCallback]):
        super().__init__()
        self.callbacks = callbacks
    
    def _report_impl(self, progress: float, message: str) -> None:
        for callback in self.callbacks:
            try:
                callback(progress, message)
            except Exception as e:
                warnings.warn(f"Progress callback failed: {e}")

class ThreadSafeProgress(BaseProgressReporter):
    """Thread-safe progress reporter."""
    
    def __init__(self, reporter: BaseProgressReporter):
        super().__init__()
        self.reporter = reporter
        self._lock = threading.Lock()
    
    def _report_impl(self, progress: float, message: str) -> None:
        with self._lock:
            self.reporter.report(progress, message)
    
    def should_cancel(self) -> bool:
        with self._lock:
            return self.reporter.should_cancel() or super().should_cancel()
    
    def set_cancelled(self) -> None:
        with self._lock:
            self.reporter.set_cancelled()
            super().set_cancelled()

# Context managers
@contextmanager
def with_progress(reporter: BaseProgressReporter):
    """Context manager for automatic progress setup and cleanup.
    
    Args:
        reporter: Progress reporter to use
        
    Example:
        with with_progress(TqdmProgress(100, "Computing")):
            # Do work here
            pass
    """
    try:
        reporter.start()
        yield reporter
    finally:
        if hasattr(reporter, 'close'):
            reporter.close()

@contextmanager
def timed_operation(name: str, reporter: Optional[BaseProgressReporter] = None):
    """Context manager for timed operations with progress reporting.
    
    Args:
        name: Name of the operation
        reporter: Optional progress reporter
        
    Example:
        with timed_operation("Lattice construction", TqdmProgress()):
            # Do work here
            pass
    """
    if reporter is None:
        reporter = SimpleProgress(name)
    
    start_time = time.time()
    try:
        with with_progress(reporter):
            yield reporter
    finally:
        elapsed = time.time() - start_time
        print(f"{name} completed in {elapsed:.2f} seconds")

@contextmanager
def cancellable_operation(reporter: BaseProgressReporter):
    """Context manager for operations that can be cancelled.
    
    Args:
        reporter: Progress reporter with cancellation support
        
    Example:
        with cancellable_operation(TqdmProgress()) as progress:
            if progress.should_cancel():
                break
    """
    try:
        with with_progress(reporter):
            yield reporter
    except KeyboardInterrupt:
        reporter.set_cancelled()
        print("\nOperation cancelled by user")
        raise

# Utility functions
def estimate_time_remaining(current: int, total: int, start_time: float) -> Optional[float]:
    """Estimate time remaining based on current progress.
    
    Args:
        current: Current progress value
        total: Total progress value
        start_time: Start time from time.time()
        
    Returns:
        Estimated time remaining in seconds, or None if not enough data
    """
    if current <= 0:
        return None
    
    elapsed = time.time() - start_time
    if elapsed <= 0:
        return None
    
    rate = current / elapsed
    if rate <= 0:
        return None
    
    remaining = (total - current) / rate
    return remaining

def format_progress_message(operation: str, current: int, total: int) -> str:
    """Format a standard progress message.
    
    Args:
        operation: Name of the operation
        current: Current progress value
        total: Total progress value
        
    Returns:
        Formatted progress message
    """
    progress = current / total if total > 0 else 0.0
    return f"{operation}: {progress:.1%} ({current}/{total})"

class ProgressConfig:
    """Global configuration for progress reporting."""
    
    def __init__(self):
        self.default_reporter_class = SimpleProgress
        self.default_update_interval = 0.1
        self.enable_logging = True
        self.log_level = 'INFO'
        self.show_eta = True
        self.show_elapsed = True
    
    def set_default_reporter(self, reporter_class: type) -> None:
        """Set the default progress reporter class."""
        self.default_reporter_class = reporter_class
    
    def set_update_interval(self, interval: float) -> None:
        """Set the default update interval for progress reporters."""
        self.default_update_interval = interval
    
    def enable_logging(self, enabled: bool) -> None:
        """Enable or disable progress logging."""
        self.enable_logging = enabled
    
    def set_log_level(self, level: str) -> None:
        """Set the log level for progress messages."""
        self.log_level = level

# Global configuration instance
config = ProgressConfig()

def create_default_progress_reporter(desc: str = "Progress") -> BaseProgressReporter:
    """Create a default progress reporter based on global configuration.
    
    Args:
        desc: Description for the progress reporter
        
    Returns:
        Progress reporter instance
    """
    reporter = config.default_reporter_class(desc)
    reporter._update_interval = config.default_update_interval
    return reporter

# Integration with UACalc operations
def create_congruence_lattice_with_progress(algebra, progress_reporter: Optional[BaseProgressReporter] = None):
    """Create a congruence lattice with progress reporting.
    
    Args:
        algebra: Algebra to compute lattice for
        progress_reporter: Optional progress reporter
        
    Returns:
        CongruenceLattice object
    """
    from . import create_congruence_lattice
    
    if progress_reporter is None:
        progress_reporter = create_default_progress_reporter("Building congruence lattice")
    
    def progress_callback(progress: float, message: str):
        progress_reporter.report(progress, message)
        if progress_reporter.should_cancel():
            raise RuntimeError("Operation cancelled")
    
    lattice = create_congruence_lattice(algebra)
    lattice.with_progress_callback(progress_callback)
    
    return lattice

def batch_evaluate_with_progress(terms, algebra, variable_sets, 
                                progress_reporter: Optional[BaseProgressReporter] = None):
    """Evaluate multiple terms with progress reporting.
    
    Args:
        terms: List of terms to evaluate
        algebra: Algebra to evaluate in
        variable_sets: List of variable assignments
        progress_reporter: Optional progress reporter
        
    Returns:
        List of evaluation results
    """
    from . import eval_term
    
    if progress_reporter is None:
        progress_reporter = create_default_progress_reporter("Evaluating terms")
    
    total = len(terms)
    results = []
    
    with with_progress(progress_reporter):
        for i, (term, variables) in enumerate(zip(terms, variable_sets)):
            if progress_reporter.should_cancel():
                break
            
            result = eval_term(term, variables)
            results.append(result)
            
            progress = (i + 1) / total
            progress_reporter.report(progress, f"Evaluated term {i+1}/{total}")
    
    return results
