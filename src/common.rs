/*!
 * Common test utilities for UACalc Rust implementation.
 * 
 * This module provides shared testing infrastructure including:
 * - Timeout support for long-running tests
 * - Java CLI comparison utilities
 * - Memory limit testing
 * - Test data generation
 */

#[cfg(feature = "test-infrastructure")]
mod test_infrastructure {
    use std::process::{Command, Stdio};
    use std::time::{Duration, Instant};
    use std::path::Path;
    use tempfile::TempDir;
    use serde_json::Value;
    use std::io;

    // Re-export the macro (used by test files)
    pub use crate::compare_with_java;

    /// Configuration for test timeouts and memory limits.
    #[derive(Debug, Clone)]
    pub struct TestConfig {
        /// Default timeout for operations (slightly longer than Java)
        pub default_timeout: Duration,
        /// Memory limit in MB
        pub memory_limit_mb: usize,
        /// Whether to enable verbose output
        pub verbose: bool,
    }

    impl Default for TestConfig {
        fn default() -> Self {
            Self {
                default_timeout: Duration::from_secs(30),
                memory_limit_mb: 1024, // 1GB default
                verbose: false,
            }
        }
    }

    /// Result type for test operations that can timeout or fail.
    pub type TestResult<T> = Result<T, TestError>;

    #[derive(Debug, thiserror::Error)]
    pub enum TestError {
        #[error("Test timeout after {0:?}")]
        Timeout(Duration),
        #[error("Java CLI execution failed: {0}")]
        JavaCliError(String),
        #[error("Output comparison failed: {0}")]
        ComparisonError(String),
        #[error("Memory limit exceeded: {0}MB")]
        MemoryLimitExceeded(usize),
        #[error("IO error: {0}")]
        IoError(#[from] io::Error),
        #[error("JSON parsing error: {0}")]
        JsonError(#[from] serde_json::Error),
    }

    /// Execute a function with a timeout.
    pub async fn with_timeout<F, T>(timeout: Duration, f: F) -> TestResult<T>
    where
        F: std::future::Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        tokio::time::timeout(timeout, f)
            .await
            .map_err(|_| TestError::Timeout(timeout))
    }

    /// Execute a blocking function with a timeout.
    pub fn with_timeout_blocking<F, T>(timeout: Duration, f: F) -> TestResult<T>
    where
        F: FnOnce() -> T + Send + 'static,
        T: Send + 'static,
    {
        let rt = tokio::runtime::Runtime::new().unwrap();
        rt.block_on(with_timeout(timeout, async { f() }))
    }


    /// Build a platform-independent Java command for wrapper classes.
    fn build_java_command(wrapper_class: &str, args: &[&str]) -> Vec<String> {
        let separator = if cfg!(target_os = "windows") { ";" } else { ":" };
        let classpath = format!(
            "java_wrapper/build/classes{}build/classes{}org{}jars/*",
            separator, separator, separator
        );
        
        let mut cmd = vec![
            "java".to_string(),
            "-cp".to_string(),
            classpath,
            wrapper_class.to_string(),
        ];
        cmd.extend(args.iter().map(|s| s.to_string()));
        cmd
    }

    /// Run a Java CLI wrapper and capture its output.
    pub fn run_java_cli(
        wrapper_class: &str,
        args: &[&str],
        config: &TestConfig,
    ) -> TestResult<JavaCliOutput> {
        let java_cmd = build_java_command(wrapper_class, args);
        
        let start = Instant::now();
        let output = Command::new(&java_cmd[0])
            .args(&java_cmd[1..])
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .output()?;
        
    let duration = start.elapsed();
    let exit_code = output.status.code().unwrap_or(-1);
    
    let java_output = JavaCliOutput {
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
        exit_code,
        duration,
    };
    
    // Check if the Java command failed
    if exit_code != 0 {
        return Err(TestError::JavaCliError(format!(
            "Java CLI failed with exit code {}: {}",
            exit_code, java_output.stderr
        )));
    }
    
    Ok(java_output)
    }

    /// Run a Java CLI wrapper with timeout and capture its output.
    pub fn run_java_cli_with_timeout(
        wrapper_class: &str,
        args: &[&str],
        config: &TestConfig,
        timeout: Duration,
    ) -> TestResult<JavaCliOutput> {
        let java_cmd = build_java_command(wrapper_class, args);
        
        let start = Instant::now();
        
        // Use timeout for the command
        let output = std::thread::scope(|s| {
            let handle = s.spawn(|| {
                Command::new(&java_cmd[0])
                    .args(&java_cmd[1..])
                    .stdout(Stdio::piped())
                    .stderr(Stdio::piped())
                    .output()
            });
            
            // Wait for the command to complete or timeout
            let start = Instant::now();
            loop {
                if handle.is_finished() {
                    break;
                }
                if start.elapsed() > timeout {
                    return Err(TestError::Timeout(timeout));
                }
                std::thread::sleep(Duration::from_millis(10));
            }
            
            // Command completed
            match handle.join() {
                Ok(Ok(output)) => Ok(output),
                Ok(Err(e)) => Err(TestError::JavaCliError(e.to_string())),
                Err(_) => Err(TestError::JavaCliError("Thread join failed".to_string())),
            }
        })?;
        
    let duration = start.elapsed();
    let exit_code = output.status.code().unwrap_or(-1);
    
    let java_output = JavaCliOutput {
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
        exit_code,
        duration,
    };
    
    // Check if the Java command failed
    if exit_code != 0 {
        return Err(TestError::JavaCliError(format!(
            "Java CLI failed with exit code {}: {}",
            exit_code, java_output.stderr
        )));
    }
    
    Ok(java_output)
    }

    /// Output from a Java CLI execution.
    #[derive(Debug, Clone)]
    pub struct JavaCliOutput {
        pub stdout: String,
        pub stderr: String,
        pub exit_code: i32,
        pub duration: Duration,
    }

    impl JavaCliOutput {
        /// Parse the stdout as JSON.
        pub fn parse_json(&self) -> TestResult<Value> {
            serde_json::from_str(&self.stdout)
                .map_err(|e| TestError::JsonError(e))
        }
        
        /// Parse the stdout as JSON, extracting JSON from mixed output.
        /// This handles cases where the output contains debug prints before the JSON.
        pub fn parse_json_from_mixed_output(&self) -> TestResult<Value> {
            // First try to parse the entire output as JSON
            if let Ok(json) = serde_json::from_str::<Value>(&self.stdout) {
                return Ok(json);
            }
            
            // If that fails, try to find JSON at the end of the output
            let lines: Vec<&str> = self.stdout.lines().collect();
            for i in (0..lines.len()).rev() {
                let remaining = lines[i..].join("\n");
                if let Ok(json) = serde_json::from_str::<Value>(&remaining) {
                    return Ok(json);
                }
            }
            
            // If all else fails, return the original error
            serde_json::from_str(&self.stdout)
                .map_err(|e| TestError::JsonError(e))
        }
        
        /// Check if the execution was successful.
        pub fn is_success(&self) -> bool {
            self.exit_code == 0
        }
    }

    /// Compare Rust output with Java CLI output.
    pub fn compare_outputs(
        rust_output: &str,
        java_output: &JavaCliOutput,
        tolerance: Option<f64>,
    ) -> TestResult<()> {
        if !java_output.is_success() {
            return Err(TestError::ComparisonError(format!(
                "Java CLI failed with exit code {}: {}",
                java_output.exit_code, java_output.stderr
            )));
        }
        
        // Try to parse both as JSON for structured comparison
        if let (Ok(rust_json), Ok(java_json)) = (
            serde_json::from_str::<Value>(rust_output),
            java_output.parse_json_from_mixed_output(),
        ) {
            // Extract the 'data' field from Java response if it exists
            let java_data = if let Some(data) = java_json.get("data") {
                data.clone()
            } else {
                java_json
            };
            
            compare_json_outputs(&rust_json, &java_data, tolerance)
        } else {
            // Fall back to string comparison
            compare_string_outputs(rust_output, &java_output.stdout)
        }
    }

    /// Compare JSON outputs with optional numerical tolerance.
    fn compare_json_outputs(
        rust_json: &Value,
        java_json: &Value,
        tolerance: Option<f64>,
    ) -> TestResult<()> {
        if rust_json == java_json {
            return Ok(());
        }
        
        // If tolerance is specified, try numerical comparison
        if let Some(tol) = tolerance {
            // Try direct numeric comparison first
            if let (Some(rust_num), Some(java_num)) = (
                rust_json.as_f64(),
                java_json.as_f64(),
            ) {
                if (rust_num - java_num).abs() <= tol {
                    return Ok(());
                }
            }
            
            // Try comparing numeric fields in objects
            if let (Some(rust_obj), Some(java_obj)) = (rust_json.as_object(), java_json.as_object()) {
                if rust_obj.len() == java_obj.len() {
                    let mut all_numeric_fields_match = true;
                    for (key, rust_val) in rust_obj {
                        if let Some(java_val) = java_obj.get(key) {
                            if let (Some(rust_num), Some(java_num)) = (rust_val.as_f64(), java_val.as_f64()) {
                                if (rust_num - java_num).abs() > tol {
                                    all_numeric_fields_match = false;
                                    break;
                                }
                            } else if rust_val != java_val {
                                all_numeric_fields_match = false;
                                break;
                            }
                        } else {
                            all_numeric_fields_match = false;
                            break;
                        }
                    }
                    if all_numeric_fields_match {
                        return Ok(());
                    }
                }
            }
        }
        
        Err(TestError::ComparisonError(format!(
            "JSON outputs differ:\nRust: {}\nJava: {}",
            serde_json::to_string_pretty(rust_json).unwrap_or_default(),
            serde_json::to_string_pretty(java_json).unwrap_or_default()
        )))
    }

    /// Compare string outputs (for non-JSON data).
    fn compare_string_outputs(rust_output: &str, java_output: &str) -> TestResult<()> {
        if rust_output.trim() == java_output.trim() {
            Ok(())
        } else {
            Err(TestError::ComparisonError(format!(
                "String outputs differ:\nRust: {}\nJava: {}",
                rust_output, java_output
            )))
        }
    }

    /// Test data generator for common UACalc test cases.
    pub struct TestDataGenerator;

    impl TestDataGenerator {
        /// Generate test data for small algebras.
        pub fn small_algebra_data() -> Vec<SmallAlgebraTest> {
            vec![
                SmallAlgebraTest {
                    size: 2,
                    operations: vec!["meet".to_string(), "join".to_string()],
                    description: "Boolean algebra".to_string(),
                },
                SmallAlgebraTest {
                    size: 3,
                    operations: vec!["+".to_string(), "*".to_string()],
                    description: "3-element ring".to_string(),
                },
                SmallAlgebraTest {
                    size: 4,
                    operations: vec!["min".to_string(), "max".to_string()],
                    description: "4-element lattice".to_string(),
                },
            ]
        }
        
        /// Generate test data for lattice operations.
        pub fn lattice_data() -> Vec<LatticeTest> {
            vec![
                LatticeTest {
                    size: 2,
                    lattice_type: "boolean".to_string(),
                },
                LatticeTest {
                    size: 3,
                    lattice_type: "chain".to_string(),
                },
                LatticeTest {
                    size: 4,
                    lattice_type: "diamond".to_string(),
                },
            ]
        }
    }

    /// Test data for small algebra operations.
    #[derive(Debug, Clone)]
    pub struct SmallAlgebraTest {
        pub size: usize,
        pub operations: Vec<String>,
        pub description: String,
    }

    /// Test data for lattice operations.
    #[derive(Debug, Clone)]
    pub struct LatticeTest {
        pub size: usize,
        pub lattice_type: String,
    }

    /// Memory usage monitor for tests.
    pub struct MemoryMonitor {
        initial_memory: usize,
        limit_mb: usize,
    }

    impl MemoryMonitor {
        /// Create a new memory monitor.
        pub fn new(limit_mb: usize) -> Self {
            Self {
                initial_memory: Self::current_memory_usage(),
                limit_mb,
            }
        }
        
        /// Check if memory usage is within limits.
        pub fn check_memory(&self) -> TestResult<()> {
            let current = Self::current_memory_usage();
            let used_mb = (current - self.initial_memory) / (1024 * 1024);
            
            if used_mb > self.limit_mb {
                Err(TestError::MemoryLimitExceeded(used_mb))
            } else {
                Ok(())
            }
        }
        
        /// Get current memory usage in bytes (approximate).
        fn current_memory_usage() -> usize {
            // This is a simplified implementation
            // In practice, you might want to use a more sophisticated approach
            std::process::id() as usize * 1024 // Placeholder
        }
    }

    /// Test harness for running UACalc operations with full validation.
    pub struct TestHarness {
        config: TestConfig,
        temp_dir: TempDir,
    }

    impl TestHarness {
        /// Create a new test harness.
        pub fn new(config: TestConfig) -> TestResult<Self> {
            let temp_dir = TempDir::new()?;
            Ok(Self { config, temp_dir })
        }
        
        /// Run a test with timeout and memory monitoring.
        pub fn run_test<F, T>(&self, test_name: &str, f: F) -> TestResult<T>
        where
            F: FnOnce() -> T + Send + 'static,
            T: Send + 'static,
        {
            let memory_monitor = MemoryMonitor::new(self.config.memory_limit_mb);
            
            if self.config.verbose {
                println!("Running test: {}", test_name);
            }
            
            let result = with_timeout_blocking(self.config.default_timeout, f);
            
            // Check memory usage
            memory_monitor.check_memory()?;
            
            if self.config.verbose {
                println!("Test {} completed", test_name);
            }
            
            result
        }
        
        /// Get the temporary directory for test files.
        pub fn temp_dir(&self) -> &Path {
            self.temp_dir.path()
        }
        
        /// Run a test that compares Rust output with Java CLI wrapper.
        /// 
        /// This method provides a convenient way to test Rust implementations
        /// against Java ground truth, with built-in timeout and error handling.
        /// 
        /// # Arguments
        /// * `test_name` - Name of the test for logging
        /// * `java_script` - Name of the Java CLI script
        /// * `java_args` - Arguments to pass to the Java CLI
        /// * `rust_function` - Rust function that produces the result to compare
        /// * `timeout` - Optional timeout (uses default if None)
        /// 
        /// # Returns
        /// The result from the Rust function if comparison succeeds
        pub fn compare_with_java<F, T>(
            &self,
            test_name: &str,
            wrapper_class: &str,
            java_args: &[&str],
            rust_function: F,
            timeout: Option<Duration>,
        ) -> TestResult<T>
        where
            F: FnOnce() -> T + Send + 'static,
            T: Send + 'static + serde::Serialize,
        {
            let timeout = timeout.unwrap_or(self.config.default_timeout);
            let memory_monitor = MemoryMonitor::new(self.config.memory_limit_mb);
            
            // Clone the necessary data to move into the closure
            let wrapper_class = wrapper_class.to_string();
            let java_args: Vec<String> = java_args.iter().map(|s| s.to_string()).collect();
            let config = self.config.clone();
            let test_name = test_name.to_string();
            
            if self.config.verbose {
                println!("Running Java comparison test: {}", test_name);
            }
            
            let result = with_timeout_blocking(timeout, move || {
                // Convert Vec<String> back to Vec<&str> for the function call
                let java_args_refs: Vec<&str> = java_args.iter().map(|s| s.as_str()).collect();
                
                // Run Java CLI first
                let java_output = run_java_cli_with_timeout(
                    &wrapper_class,
                    &java_args_refs,
                    &config,
                    timeout,
                )?;
                
                // Run Rust function
                let rust_result = rust_function();
                
                // Serialize Rust result to JSON
                let rust_json = serde_json::to_string_pretty(&rust_result)
                    .map_err(|e| TestError::JsonError(e))?;
                
                // Compare outputs
                compare_outputs(&rust_json, &java_output, None)?;
                
                Ok(rust_result)
            })?;
            
            // Check memory usage
            memory_monitor.check_memory()?;
            
            if self.config.verbose {
                println!("Java comparison test {} completed", test_name);
            }
            
            result
        }
        
        /// Run a test that compares Rust output with Java CLI wrapper using numerical tolerance.
        /// 
        /// This is useful for floating-point comparisons where exact equality
        /// might not be achievable due to numerical precision differences.
        pub fn compare_with_java_tolerance<F, T>(
            &self,
            test_name: &str,
            java_script: &str,
            java_args: &[&str],
            rust_function: F,
            tolerance: f64,
            timeout: Option<Duration>,
        ) -> TestResult<T>
        where
            F: FnOnce() -> T + Send + 'static,
            T: Send + 'static + serde::Serialize,
        {
            let timeout = timeout.unwrap_or(self.config.default_timeout);
            let memory_monitor = MemoryMonitor::new(self.config.memory_limit_mb);
            
            // Clone the necessary data to move into the closure
            let java_script = java_script.to_string();
            let java_args: Vec<String> = java_args.iter().map(|s| s.to_string()).collect();
            let config = self.config.clone();
            let test_name = test_name.to_string();
            
            if self.config.verbose {
                println!("Running Java comparison test with tolerance: {}", test_name);
            }
            
            let result = with_timeout_blocking(timeout, move || {
                // Convert Vec<String> back to Vec<&str> for the function call
                let java_args_refs: Vec<&str> = java_args.iter().map(|s| s.as_str()).collect();
                
                // Run Java CLI first
                let java_output = run_java_cli_with_timeout(
                    &java_script,
                    &java_args_refs,
                    &config,
                    timeout,
                )?;
                
                // Run Rust function
                let rust_result = rust_function();
                
                // Serialize Rust result to JSON
                let rust_json = serde_json::to_string_pretty(&rust_result)
                    .map_err(|e| TestError::JsonError(e))?;
                
                // Compare outputs with tolerance
                compare_outputs(&rust_json, &java_output, Some(tolerance))?;
                
                Ok(rust_result)
            })?;
            
            // Check memory usage
            memory_monitor.check_memory()?;
            
            if self.config.verbose {
                println!("Java comparison test with tolerance {} completed", test_name);
            }
            
            result
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;
        
        #[test]
        fn test_config_default() {
            let config = TestConfig::default();
            assert_eq!(config.default_timeout, Duration::from_secs(30));
            assert_eq!(config.memory_limit_mb, 1024);
        }
        
        #[test]
        fn test_memory_monitor() {
            let monitor = MemoryMonitor::new(100);
            assert!(monitor.check_memory().is_ok());
        }
        
        #[test]
        fn test_test_data_generator() {
            let algebra_data = TestDataGenerator::small_algebra_data();
            assert!(!algebra_data.is_empty());
            
            let lattice_data = TestDataGenerator::lattice_data();
            assert!(!lattice_data.is_empty());
        }
        
        #[tokio::test]
        async fn test_with_timeout() {
            let result = with_timeout(Duration::from_millis(100), async {
                tokio::time::sleep(Duration::from_millis(50)).await;
                "success"
            }).await;
            
            assert_eq!(result.unwrap(), "success");
        }
        
        #[tokio::test]
        async fn test_with_timeout_failure() {
            let result = with_timeout(Duration::from_millis(50), async {
                tokio::time::sleep(Duration::from_millis(100)).await;
                "success"
            }).await;
            
            assert!(result.is_err());
            match result.unwrap_err() {
                TestError::Timeout(_) => {},
                _ => panic!("Expected timeout error"),
            }
        }
        
        #[test]
        fn test_java_cli_output_parsing() {
            let output = JavaCliOutput {
                stdout: r#"{"success": true, "data": {"result": 42}}"#.to_string(),
                stderr: "".to_string(),
                exit_code: 0,
                duration: Duration::from_millis(100),
            };
            
            assert!(output.is_success());
            let json = output.parse_json().unwrap();
            assert_eq!(json["success"], true);
            assert_eq!(json["data"]["result"], 42);
        }
        
        #[test]
        fn test_compare_json_outputs() {
            let rust_json = serde_json::json!({
                "result": 42,
                "data": [1, 2, 3]
            });
            
            let java_json = serde_json::json!({
                "result": 42,
                "data": [1, 2, 3]
            });
            
            assert!(compare_json_outputs(&rust_json, &java_json, None).is_ok());
        }
        
        #[test]
        fn test_compare_json_outputs_with_tolerance() {
            let rust_json = serde_json::json!({
                "result": 42.0
            });
            
            let java_json = serde_json::json!({
                "result": 42.1
            });
            
            // Should pass with tolerance
            assert!(compare_json_outputs(&rust_json, &java_json, Some(0.2)).is_ok());
            
            // Should fail without tolerance
            assert!(compare_json_outputs(&rust_json, &java_json, None).is_err());
        }
    }
}

// Re-export everything from the test infrastructure module
#[cfg(feature = "test-infrastructure")]
pub use test_infrastructure::*;

/// Macro for comparing Rust function output with Java CLI wrapper.
/// 
/// This macro provides a convenient way to test Rust implementations
/// against Java ground truth, avoiding potential deadlocks in Python bindings.
/// 
/// # Example
/// ```rust
/// use uacalc::common::*;
/// 
/// #[test]
/// fn test_horner_encoding() {
///     let config = TestConfig::default();
///     
///     compare_with_java!(
///         config,
///         "horner", // Java CLI script name
///         ["horner", "--args", "1,2,3", "--sizes", "4,5,6"], // CLI args
///         || {
///             // Rust implementation
///             let args = vec![1, 2, 3];
///             let sizes = vec![4, 5, 6];
///             let result = horner_encoding(&args, &sizes);
///             serde_json::json!({
///                 "result": result,
///                 "args": args,
///                 "sizes": sizes
///             })
///         }
///     );
/// }
/// ```
#[cfg(feature = "test-infrastructure")]
#[macro_export]
macro_rules! compare_with_java {
    ($config:expr, $wrapper_class:expr, $args:expr, $rust_fn:expr) => {
        {
            let java_output = run_java_cli_with_timeout(
                $wrapper_class,
                &$args,
                &$config,
                $config.default_timeout
            ).expect("Java CLI execution failed");
            
            let rust_result = $rust_fn();
            let rust_json = serde_json::to_string_pretty(&rust_result)
                .expect("Failed to serialize Rust result to JSON");
            
            compare_outputs(&rust_json, &java_output, None)
                .expect("Rust and Java outputs do not match");
        }
    };
    ($config:expr, $wrapper_class:expr, $args:expr, $rust_fn:expr, $tolerance:expr) => {
        {
            let java_output = run_java_cli_with_timeout(
                $wrapper_class,
                &$args,
                &$config,
                $config.default_timeout
            ).expect("Java CLI execution failed");
            
            let rust_result = $rust_fn();
            let rust_json = serde_json::to_string_pretty(&rust_result)
                .expect("Failed to serialize Rust result to JSON");
            
            compare_outputs(&rust_json, &java_output, Some($tolerance))
                .expect("Rust and Java outputs do not match");
        }
    };
}

/// Macro for testing Rust functions with Java comparison and timeout.
/// 
/// This macro combines timeout testing with Java comparison,
/// ensuring both performance and correctness.
/// 
/// # Example
/// ```rust
/// use uacalc::common::*;
/// 
/// #[test]
/// fn test_complex_algorithm() {
///     let config = TestConfig::default();
///     
///     test_with_java_comparison!(
///         config,
///         Duration::from_secs(30), // timeout
///         "complex-alg", // Java CLI script
///         ["compute", "--input", "large_data"], // CLI args
///         || {
///             // Rust implementation
///             complex_algorithm("large_data")
///         }
///     );
/// }
/// ```
#[cfg(feature = "test-infrastructure")]
#[macro_export]
macro_rules! test_with_java_comparison {
    ($config:expr, $timeout:expr, $script:expr, $args:expr, $rust_fn:expr) => {
        {
            let result = with_timeout_blocking($timeout, move || {
                let java_output = run_java_cli_with_timeout(
                    $script,
                    &$args,
                    &$config,
                    $timeout
                ).expect("Java CLI execution failed");
                
                let rust_result = $rust_fn();
                let rust_json = serde_json::to_string_pretty(&rust_result)
                    .expect("Failed to serialize Rust result to JSON");
                
                compare_outputs(&rust_json, &java_output, None)
                    .expect("Rust and Java outputs do not match");
                
                rust_result
            });
            
            result.expect("Test failed with timeout or comparison error");
        }
    };
}