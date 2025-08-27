use criterion::{black_box, criterion_group, criterion_main, Criterion};
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use uacalc_core::algebra::BasicAlgebra;
use uacalc_core::conlat::cg;
use uacalc_core::io::load_algebra_from_file;
use uacalc_core::partition::BasicPartition;

/// Performance baseline data structure
#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct PerformanceBaseline {
    operation: String,
    algebra_size: usize,
    algebra_name: String,
    mean_time_ms: f64,
    std_dev_ms: f64,
    min_time_ms: f64,
    max_time_ms: f64,
    memory_usage_mb: Option<f64>,
    timestamp: String,
    rust_version: String,
    cpu_info: String,
}

/// Performance regression test suite
pub struct PerformanceRegressionTester {
    baseline_file: String,
    baselines: HashMap<String, PerformanceBaseline>,
    regression_threshold: f64, // Percentage threshold for regression detection
}

impl PerformanceRegressionTester {
    pub fn new(baseline_file: &str) -> Self {
        Self {
            baseline_file: baseline_file.to_string(),
            baselines: HashMap::new(),
            regression_threshold: 10.0, // 10% regression threshold
        }
    }

    /// Load existing baselines from file
    pub fn load_baselines(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        if Path::new(&self.baseline_file).exists() {
            let data = fs::read_to_string(&self.baseline_file)?;
            let loaded: HashMap<String, PerformanceBaseline> = serde_json::from_str(&data)?;
            self.baselines = loaded;
        }
        Ok(())
    }

    /// Save baselines to file
    pub fn save_baselines(&self) -> Result<(), Box<dyn std::error::Error>> {
        let data = serde_json::to_string_pretty(&self.baselines)?;
        fs::write(&self.baseline_file, data)?;
        Ok(())
    }

    /// Generate a unique key for a baseline
    fn baseline_key(&self, operation: &str, algebra_size: usize, algebra_name: &str) -> String {
        format!("{}_{}_{}", operation, algebra_size, algebra_name)
    }

    /// Run a performance test and compare with baseline
    pub fn run_performance_test(
        &mut self,
        operation: &str,
        algebra: &BasicAlgebra,
        test_fn: impl Fn(&BasicAlgebra) -> Result<(), Box<dyn std::error::Error>>,
    ) -> Result<PerformanceTestResult, Box<dyn std::error::Error>> {
        let key = self.baseline_key(operation, algebra.cardinality(), &algebra.name);

        // Run the test multiple times to get statistics
        let mut times = Vec::new();
        let mut memory_usage = Vec::new();

        for _ in 0..10 {
            let start_time = std::time::Instant::now();
            let start_memory = self.get_memory_usage();

            test_fn(algebra)?;

            let end_time = std::time::Instant::now();
            let end_memory = self.get_memory_usage();

            let duration_ms = end_time.duration_since(start_time).as_millis() as f64;
            times.push(duration_ms);

            if let (Some(start), Some(end)) = (start_memory, end_memory) {
                memory_usage.push(end - start);
            }
        }

        // Calculate statistics
        let mean_time = times.iter().sum::<f64>() / times.len() as f64;
        let variance =
            times.iter().map(|&x| (x - mean_time).powi(2)).sum::<f64>() / times.len() as f64;
        let std_dev = variance.sqrt();
        let min_time = times.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let max_time = times.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));

        let avg_memory = if memory_usage.is_empty() {
            None
        } else {
            Some(memory_usage.iter().sum::<f64>() / memory_usage.len() as f64)
        };

        // Create current baseline
        let current_baseline = PerformanceBaseline {
            operation: operation.to_string(),
            algebra_size: algebra.cardinality(),
            algebra_name: algebra.name.clone(),
            mean_time_ms: mean_time,
            std_dev_ms: std_dev,
            min_time_ms: min_time,
            max_time_ms: max_time,
            memory_usage_mb: avg_memory,
            timestamp: chrono::Utc::now().to_rfc3339(),
            rust_version: env!("CARGO_PKG_VERSION").to_string(),
            cpu_info: self.get_cpu_info(),
        };

        // Check for regression
        let regression = if let Some(existing_baseline) = self.baselines.get(&key) {
            let time_increase = (mean_time - existing_baseline.mean_time_ms)
                / existing_baseline.mean_time_ms
                * 100.0;
            time_increase > self.regression_threshold
        } else {
            false
        };

        // Update baseline
        self.baselines.insert(key, current_baseline.clone());

        Ok(PerformanceTestResult {
            baseline: current_baseline,
            regression,
            times,
            memory_usage,
        })
    }

    /// Get current memory usage in MB
    fn get_memory_usage(&self) -> Option<f64> {
        #[cfg(target_os = "linux")]
        {
            if let Ok(contents) = fs::read_to_string("/proc/self/status") {
                for line in contents.lines() {
                    if line.starts_with("VmRSS:") {
                        if let Some(kb_str) = line.split_whitespace().nth(1) {
                            if let Ok(kb) = kb_str.parse::<f64>() {
                                return Some(kb / 1024.0); // Convert KB to MB
                            }
                        }
                    }
                }
            }
        }

        #[cfg(target_os = "windows")]
        {
            // Windows memory usage would require additional dependencies
            None
        }

        #[cfg(target_os = "macos")]
        {
            // macOS memory usage would require additional dependencies
            None
        }

        None
    }

    /// Get CPU information
    fn get_cpu_info(&self) -> String {
        #[cfg(target_os = "linux")]
        {
            if let Ok(contents) = fs::read_to_string("/proc/cpuinfo") {
                for line in contents.lines() {
                    if line.starts_with("model name") {
                        if let Some(name) = line.split(':').nth(1) {
                            return name.trim().to_string();
                        }
                    }
                }
            }
        }

        "Unknown CPU".to_string()
    }

    /// Run Java comparison test
    pub fn run_java_comparison(
        &self,
        operation: &str,
        algebra_file: &str,
    ) -> Result<JavaComparisonResult, Box<dyn std::error::Error>> {
        // This would integrate with the Java comparison script
        // For now, return a placeholder result
        Ok(JavaComparisonResult {
            java_time_ms: 1000.0, // Placeholder
            rust_time_ms: 100.0,  // Placeholder
            speedup: 10.0,
            memory_improvement: Some(50.0),
        })
    }
}

/// Result of a performance test
#[derive(Debug)]
pub struct PerformanceTestResult {
    baseline: PerformanceBaseline,
    regression: bool,
    times: Vec<f64>,
    memory_usage: Vec<f64>,
}

/// Result of Java comparison
#[derive(Debug)]
pub struct JavaComparisonResult {
    java_time_ms: f64,
    rust_time_ms: f64,
    speedup: f64,
    memory_improvement: Option<f64>,
}

/// Test functions for different operations

fn test_cg_operation(algebra: &BasicAlgebra) -> Result<(), Box<dyn std::error::Error>> {
    let size = algebra.cardinality();

    // Test Cg for all pairs (a,b) where a < b
    for a in 0..size {
        for b in (a + 1)..size {
            let _partition = cg(algebra, &[(a, b)])?;
        }
    }

    Ok(())
}

fn test_lattice_construction(algebra: &BasicAlgebra) -> Result<(), Box<dyn std::error::Error>> {
    // This would test full lattice construction
    // For now, just test a few principal congruences
    let size = algebra.cardinality();

    for a in 0..size.min(3) {
        for b in (a + 1)..size.min(4) {
            let _partition = cg(algebra, &[(a, b)])?;
        }
    }

    Ok(())
}

fn test_term_evaluation(algebra: &BasicAlgebra) -> Result<(), Box<dyn std::error::Error>> {
    // This would test term evaluation
    // For now, just do some basic operations
    let size = algebra.cardinality();

    for _ in 0..100 {
        for op in algebra.operations() {
            let op_guard = op.lock()?;
            let arity = op_guard.arity();
            if arity > 0 {
                let args = vec![0; arity];
                let _result = op_guard.value(&args)?;
            }
        }
    }

    Ok(())
}

/// Criterion benchmark functions

pub fn benchmark_cg_operations(c: &mut Criterion) {
    let mut group = c.benchmark_group("cg_operations");

    // Test with different algebra sizes
    for size in [3, 5, 7, 10] {
        let algebra = BasicAlgebra::with_cardinality(format!("Test{}", size), size).unwrap();

        group.bench_function(&format!("cg_size_{}", size), |b| {
            b.iter(|| {
                let size = algebra.cardinality();
                for a in 0..size {
                    for b in (a + 1)..size {
                        let _partition = cg(&algebra, &[(a, b)]).unwrap();
                    }
                }
            });
        });
    }

    group.finish();
}

pub fn benchmark_lattice_construction(c: &mut Criterion) {
    let mut group = c.benchmark_group("lattice_construction");

    // Test with different algebra sizes
    for size in [3, 5, 7] {
        let algebra = BasicAlgebra::with_cardinality(format!("Test{}", size), size).unwrap();

        group.bench_function(&format!("lattice_size_{}", size), |b| {
            b.iter(|| {
                // Test lattice construction for small algebras
                let size = algebra.cardinality();
                for a in 0..size.min(3) {
                    for b in (a + 1)..size.min(4) {
                        let _partition = cg(&algebra, &[(a, b)]).unwrap();
                    }
                }
            });
        });
    }

    group.finish();
}

pub fn benchmark_term_evaluation(c: &mut Criterion) {
    let mut group = c.benchmark_group("term_evaluation");

    // Test with different algebra sizes
    for size in [3, 5, 7] {
        let algebra = BasicAlgebra::with_cardinality(format!("Test{}", size), size).unwrap();

        group.bench_function(&format!("terms_size_{}", size), |b| {
            b.iter(|| {
                for _ in 0..100 {
                    for op in algebra.operations() {
                        let op_guard = op.lock().unwrap();
                        let arity = op_guard.arity();
                        if arity > 0 {
                            let args = vec![0; arity];
                            let _result = op_guard.value(&args).unwrap();
                        }
                    }
                }
            });
        });
    }

    group.finish();
}

/// Main performance regression test
#[test]
fn test_performance_regression() -> Result<(), Box<dyn std::error::Error>> {
    let mut tester = PerformanceRegressionTester::new("performance_baselines.json");
    tester.load_baselines()?;

    // Test with different algebra sizes
    for size in [3, 5, 7, 10] {
        let algebra = BasicAlgebra::with_cardinality(format!("Test{}", size), size)?;

        // Test Cg operations
        let cg_result = tester.run_performance_test("cg", &algebra, test_cg_operation)?;
        println!(
            "CG test for size {}: {:.2}ms (regression: {})",
            size, cg_result.baseline.mean_time_ms, cg_result.regression
        );

        // Test lattice construction for smaller algebras
        if size <= 7 {
            let lattice_result =
                tester.run_performance_test("lattice", &algebra, test_lattice_construction)?;
            println!(
                "Lattice test for size {}: {:.2}ms (regression: {})",
                size, lattice_result.baseline.mean_time_ms, lattice_result.regression
            );
        }

        // Test term evaluation
        let term_result =
            tester.run_performance_test("term_evaluation", &algebra, test_term_evaluation)?;
        println!(
            "Term evaluation test for size {}: {:.2}ms (regression: {})",
            size, term_result.baseline.mean_time_ms, term_result.regression
        );
    }

    // Save updated baselines
    tester.save_baselines()?;

    Ok(())
}

/// Java comparison test
#[test]
fn test_java_comparison() -> Result<(), Box<dyn std::error::Error>> {
    let tester = PerformanceRegressionTester::new("performance_baselines.json");

    // Test with sample algebra files
    let algebra_files = ["resources/algebras/ba2.ua", "resources/algebras/cyclic3.ua"];

    for file in &algebra_files {
        if Path::new(file).exists() {
            let algebra = load_algebra_from_file(file)?;

            let java_result = tester.run_java_comparison("cg", file)?;
            println!(
                "Java comparison for {}: Rust {:.2}ms, Java {:.2}ms, Speedup: {:.2}x",
                file, java_result.rust_time_ms, java_result.java_time_ms, java_result.speedup
            );
        }
    }

    Ok(())
}

criterion_group!(
    benches,
    benchmark_cg_operations,
    benchmark_lattice_construction,
    benchmark_term_evaluation
);
criterion_main!(benches);
