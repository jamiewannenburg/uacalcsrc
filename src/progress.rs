/*!
 * Progress reporting trait for UACalc Rust implementation.
 * 
 * This module provides a minimal, non-UI progress reporting system to replace
 * the UI-dependent `org.uacalc.ui.tm.ProgressReport` from the Java implementation.
 * 
 * The trait allows algorithms to report progress without depending on UI components,
 * making it suitable for both CLI and library usage.
 */

use std::sync::Arc;
use std::time::Instant;

/// Progress reporting trait for long-running operations.
/// 
/// This trait provides a way for algorithms to report their progress without
/// depending on UI components. It's designed to be minimal and flexible,
/// allowing different implementations for different use cases (CLI, logging, etc.).
pub trait ProgressReport: Send + Sync {
    /// Set the current pass number (for multi-pass algorithms).
    fn set_pass(&self, pass: usize);
    
    /// Set the total number of passes.
    fn set_pass_size(&self, pass_size: usize);
    
    /// Set the current size/count being processed.
    fn set_size(&self, size: usize);
    
    /// Set a description of the current operation.
    fn set_description(&self, description: &str);
    
    /// Add a log line with automatic indentation.
    fn add_line(&self, line: &str);
    
    /// Add a start line and increase indentation.
    fn add_start_line(&self, line: &str);
    
    /// Add an end line, decrease indentation, and show elapsed time.
    fn add_end_line(&self, line: &str);
    
    /// Reset the progress state (clear indentation, times, etc.).
    fn reset(&self);
    
    /// Get the current pass number.
    fn get_pass(&self) -> usize;
    
    /// Get the total number of passes.
    fn get_pass_size(&self) -> usize;
    
    /// Get the current size.
    fn get_size(&self) -> usize;
    
    /// Get the current description.
    fn get_description(&self) -> String;
    
    /// Set the estimated time left for the current operation.
    /// 
    /// # Arguments
    /// * `time_str` - A formatted string representing time left (e.g., "1:23:45")
    fn set_time_left(&self, time_str: &str);
    
    /// Set the estimated time for the next pass.
    /// 
    /// # Arguments
    /// * `time_str` - A formatted string representing time for next pass
    fn set_time_next(&self, time_str: &str);
}

/// A no-op implementation that suppresses all progress output.
/// 
/// This is useful when you want to disable progress reporting entirely,
/// similar to the Java `ProgressReport()` constructor with `dontOutput = true`.
#[derive(Debug, Clone)]
pub struct NoOpProgressReport;

impl ProgressReport for NoOpProgressReport {
    fn set_pass(&self, _pass: usize) {}
    fn set_pass_size(&self, _pass_size: usize) {}
    fn set_size(&self, _size: usize) {}
    fn set_description(&self, _description: &str) {}
    fn add_line(&self, _line: &str) {}
    fn add_start_line(&self, _line: &str) {}
    fn add_end_line(&self, _line: &str) {}
    fn reset(&self) {}
    fn get_pass(&self) -> usize { 0 }
    fn get_pass_size(&self) -> usize { 0 }
    fn get_size(&self) -> usize { 0 }
    fn get_description(&self) -> String { String::new() }
    fn set_time_left(&self, _time_str: &str) {}
    fn set_time_next(&self, _time_str: &str) {}
}

/// A simple console-based progress reporter.
/// 
/// This implementation prints progress information to stdout/stderr,
/// making it suitable for CLI applications and debugging.
#[derive(Debug)]
pub struct ConsoleProgressReport {
    pass: std::sync::Mutex<usize>,
    pass_size: std::sync::Mutex<usize>,
    size: std::sync::Mutex<usize>,
    description: std::sync::Mutex<String>,
    indent: std::sync::Mutex<usize>,
    times: std::sync::Mutex<Vec<Instant>>,
    time_left: std::sync::Mutex<String>,
    time_next: std::sync::Mutex<String>,
}

impl ConsoleProgressReport {
    /// Create a new console progress reporter.
    pub fn new() -> Self {
        Self {
            pass: std::sync::Mutex::new(0),
            pass_size: std::sync::Mutex::new(0),
            size: std::sync::Mutex::new(0),
            description: std::sync::Mutex::new(String::new()),
            indent: std::sync::Mutex::new(0),
            times: std::sync::Mutex::new(Vec::new()),
            time_left: std::sync::Mutex::new(String::new()),
            time_next: std::sync::Mutex::new(String::new()),
        }
    }
    
    fn get_indent_string(&self, indent: usize) -> String {
        "  ".repeat(indent)
    }
}

impl Default for ConsoleProgressReport {
    fn default() -> Self {
        Self::new()
    }
}

impl ProgressReport for ConsoleProgressReport {
    fn set_pass(&self, pass: usize) {
        if let Ok(mut p) = self.pass.lock() {
            *p = pass;
        }
    }
    
    fn set_pass_size(&self, pass_size: usize) {
        if let Ok(mut ps) = self.pass_size.lock() {
            *ps = pass_size;
        }
    }
    
    fn set_size(&self, size: usize) {
        if let Ok(mut s) = self.size.lock() {
            *s = size;
        }
    }
    
    fn set_description(&self, description: &str) {
        if let Ok(mut desc) = self.description.lock() {
            *desc = description.to_string();
        }
    }
    
    fn add_line(&self, line: &str) {
        if let Ok(indent) = self.indent.lock() {
            let indent_str = self.get_indent_string(*indent);
            eprintln!("{}{}", indent_str, line);
        }
    }
    
    fn add_start_line(&self, line: &str) {
        if let Ok(mut indent) = self.indent.lock() {
            let indent_str = self.get_indent_string(*indent);
            eprintln!("{}{}", indent_str, line);
            *indent += 1;
        }
        if let Ok(mut times) = self.times.lock() {
            times.push(Instant::now());
        }
    }
    
    fn add_end_line(&self, line: &str) {
        let elapsed_ms = if let Ok(mut times) = self.times.lock() {
            if let Some(start) = times.pop() {
                start.elapsed().as_millis()
            } else {
                0
            }
        } else {
            0
        };
        
        if let Ok(mut indent) = self.indent.lock() {
            if *indent > 0 {
                *indent -= 1;
            }
            let indent_str = self.get_indent_string(*indent);
            eprintln!("{}{}  ({} ms)", indent_str, line, elapsed_ms);
        }
    }
    
    fn reset(&self) {
        if let Ok(mut indent) = self.indent.lock() {
            *indent = 0;
        }
        if let Ok(mut times) = self.times.lock() {
            times.clear();
        }
    }
    
    fn get_pass(&self) -> usize {
        self.pass.lock().map(|v| *v).unwrap_or(0)
    }
    
    fn get_pass_size(&self) -> usize {
        self.pass_size.lock().map(|v| *v).unwrap_or(0)
    }
    
    fn get_size(&self) -> usize {
        self.size.lock().map(|v| *v).unwrap_or(0)
    }
    
    fn get_description(&self) -> String {
        self.description.lock().map(|v| v.clone()).unwrap_or_else(|_| String::new())
    }
    
    fn set_time_left(&self, time_str: &str) {
        if let Ok(mut time) = self.time_left.lock() {
            *time = time_str.to_string();
            eprintln!("Time left: {}", time_str);
        }
    }
    
    fn set_time_next(&self, time_str: &str) {
        if let Ok(mut time) = self.time_next.lock() {
            *time = time_str.to_string();
            eprintln!("Time for next pass: {}", time_str);
        }
    }
}

/// A type alias for a shared progress reporter.
pub type SharedProgressReport = Arc<dyn ProgressReport>;

/// Helper functions for creating common progress reporters.
pub mod factory {
    use super::*;
    
    /// Create a no-op progress reporter that suppresses all output.
    pub fn no_op() -> SharedProgressReport {
        Arc::new(NoOpProgressReport)
    }
    
    /// Create a console progress reporter that prints to stderr.
    pub fn console() -> SharedProgressReport {
        Arc::new(ConsoleProgressReport::new())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    use std::time::Duration;
    
    #[test]
    fn test_no_op_progress_report() {
        let reporter = NoOpProgressReport;
        
        // All operations should be no-ops
        reporter.set_pass(5);
        reporter.set_pass_size(10);
        reporter.set_size(100);
        reporter.set_description("test");
        reporter.add_line("test line");
        reporter.add_start_line("start");
        reporter.add_end_line("end");
        reporter.reset();
        
        // Getters should return default values
        assert_eq!(reporter.get_pass(), 0);
        assert_eq!(reporter.get_pass_size(), 0);
        assert_eq!(reporter.get_size(), 0);
        assert_eq!(reporter.get_description(), "");
    }
    
    #[test]
    fn test_console_progress_report() {
        let reporter = ConsoleProgressReport::new();
        
        reporter.set_pass(1);
        reporter.set_pass_size(3);
        reporter.set_size(50);
        reporter.set_description("Testing");
        
        assert_eq!(reporter.get_pass(), 1);
        assert_eq!(reporter.get_pass_size(), 3);
        assert_eq!(reporter.get_size(), 50);
        assert_eq!(reporter.get_description(), "Testing");
        
        // Test timing functionality
        reporter.add_start_line("Starting operation");
        thread::sleep(Duration::from_millis(10));
        reporter.add_end_line("Operation complete");
        
        reporter.reset();
        assert_eq!(reporter.get_pass(), 1); // Should still have the value
    }
    
    #[test]
    fn test_factory_functions() {
        let no_op = factory::no_op();
        let console = factory::console();
        
        // Both should implement the trait
        no_op.set_description("test");
        console.set_description("test");
        
        assert_eq!(no_op.get_description(), "");
        assert_eq!(console.get_description(), "test");
    }
}
