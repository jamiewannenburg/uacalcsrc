# Java CLI Comparison Testing

This document explains how to use the enhanced Rust test infrastructure to compare Rust implementations directly with Java CLI wrappers, avoiding potential deadlocks in Python bindings.

## Overview

The enhanced test infrastructure provides several ways to test Rust implementations against Java ground truth:

1. **Macros** - Quick and easy comparison with `compare_with_java!` and `test_with_java_comparison!`
2. **TestHarness** - More control with `TestHarness::compare_with_java()` and `TestHarness::compare_with_java_tolerance()`
3. **Direct functions** - Low-level control with `run_java_cli_with_timeout()` and `compare_outputs()`

## Why Java CLI Comparison?

- **Avoids deadlocks**: Python bindings can hang due to GIL issues or other threading problems
- **Direct comparison**: Tests Rust code directly against Java implementation
- **Timeout control**: Built-in timeout support prevents hanging tests
- **Memory monitoring**: Tracks memory usage during tests
- **Performance testing**: Can compare execution times between Rust and Java

## Quick Start

### Using Macros

The simplest way to compare Rust and Java implementations:

```rust
use crate::common::*;

#[test]
fn test_horner_encoding() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "horner", // Java CLI script name
        ["horner", "--args", "1,2,3", "--sizes", "4,5,6"], // CLI args
        || {
            // Rust implementation
            let args = vec![1, 2, 3];
            let sizes = vec![4, 5, 6];
            let result = horner_encoding(&args, &sizes);
            serde_json::json!({
                "result": result,
                "args": args,
                "sizes": sizes
            })
        }
    );
}
```

### Using TestHarness

For more control over the testing process:

```rust
use crate::common::*;
use std::time::Duration;

#[test]
fn test_complex_algorithm() {
    let config = TestConfig {
        verbose: true,
        default_timeout: Duration::from_secs(30),
        memory_limit_mb: 512,
        ..Default::default()
    };
    
    let harness = TestHarness::new(config).expect("Failed to create test harness");
    
    let result = harness.compare_with_java(
        "complex_algorithm_test",
        "complex-alg",
        &["compute", "--input", "large_data"],
        || {
            // Rust implementation
            complex_algorithm("large_data")
        },
        Some(Duration::from_secs(60)), // Custom timeout
    ).expect("Java comparison test failed");
    
    // Verify the result
    assert!(result["success"]);
}
```

## Advanced Features

### Numerical Tolerance

For floating-point comparisons where exact equality might not be achievable:

```rust
#[test]
fn test_floating_point_algorithm() {
    let config = TestConfig::default();
    let harness = TestHarness::new(config).expect("Failed to create test harness");
    
    let result = harness.compare_with_java_tolerance(
        "floating_point_test",
        "floating-alg",
        &["compute", "--precision", "high"],
        || {
            let result = floating_point_algorithm();
            serde_json::json!({
                "result": result,
                "precision": "high"
            })
        },
        1e-10, // tolerance for floating-point comparison
        Some(Duration::from_secs(5)),
    ).expect("Java comparison test with tolerance failed");
}
```

### Timeout Testing

Test that operations complete within expected time limits:

```rust
#[test]
fn test_performance_requirements() {
    let config = TestConfig::default();
    
    test_with_java_comparison!(
        config,
        Duration::from_secs(10), // Must complete within 10 seconds
        "performance-alg",
        ["benchmark", "--iterations", "1000"],
        || {
            performance_critical_algorithm(1000)
        }
    );
}
```

### Memory Monitoring

Ensure tests don't exceed memory limits:

```rust
#[test]
fn test_memory_efficient_algorithm() {
    let config = TestConfig {
        memory_limit_mb: 100, // 100MB limit
        ..Default::default()
    };
    
    let harness = TestHarness::new(config).expect("Failed to create test harness");
    
    let result = harness.compare_with_java(
        "memory_efficient_test",
        "memory-alg",
        &["process", "--large_dataset"],
        || {
            memory_efficient_algorithm()
        },
        None,
    ).expect("Memory test failed");
}
```

## Error Handling

The test infrastructure provides detailed error information:

```rust
#[test]
fn test_error_handling() {
    let config = TestConfig::default();
    
    // Test with invalid input
    let result = run_java_cli("invalid-script", &[], &config);
    assert!(result.is_err());
    
    match result.unwrap_err() {
        TestError::JavaCliError(msg) => {
            assert!(msg.contains("Java CLI script not found"));
        }
        TestError::Timeout(duration) => {
            println!("Operation timed out after {:?}", duration);
        }
        TestError::MemoryLimitExceeded(used_mb) => {
            println!("Memory limit exceeded: {}MB used", used_mb);
        }
        _ => panic!("Unexpected error type"),
    }
}
```

## Best Practices

### 1. Use Appropriate Timeouts

Set timeouts based on the complexity of the operation:

```rust
// Simple operations
let config = TestConfig {
    default_timeout: Duration::from_secs(5),
    ..Default::default()
};

// Complex algorithms
let config = TestConfig {
    default_timeout: Duration::from_secs(60),
    ..Default::default()
};
```

### 2. Test Edge Cases

Always test edge cases that might cause issues:

```rust
#[test]
fn test_edge_cases() {
    let config = TestConfig::default();
    let harness = TestHarness::new(config).expect("Failed to create test harness");
    
    let edge_cases = vec![
        ("empty_input", vec![]),
        ("single_element", vec![42]),
        ("large_input", (0..10000).collect()),
        ("negative_values", vec![-1, -2, -3]),
    ];
    
    for (case_name, input_data) in edge_cases {
        let result = harness.compare_with_java(
            &format!("edge_case_{}", case_name),
            "edge-case-handler",
            &["handle", "--input", case_name],
            || handle_edge_case(input_data),
            None,
        ).expect(&format!("Edge case test failed for {}", case_name));
        
        assert!(result["handled"], "Edge case {} not handled correctly", case_name);
    }
}
```

### 3. Batch Testing

For multiple related operations, use batch testing:

```rust
#[test]
fn test_batch_operations() {
    let config = TestConfig::default();
    let harness = TestHarness::new(config).expect("Failed to create test harness");
    
    let test_data = TestDataGenerator::small_algebra_data();
    
    for (i, data) in test_data.iter().enumerate() {
        let result = harness.compare_with_java(
            &format!("batch_test_{}", i),
            "small-algebra",
            &["create", "--size", &data.size.to_string(), "--operations", &data.operations.join(",")],
            || create_small_algebra(data.size, data.operations.clone()),
            None,
        ).expect(&format!("Batch test {} failed", i));
        
        assert_eq!(result["size"], data.size);
    }
}
```

### 4. Performance Testing

Compare performance between Rust and Java implementations:

```rust
#[test]
fn test_performance_comparison() {
    let config = TestConfig::default();
    let harness = TestHarness::new(config).expect("Failed to create test harness");
    
    let start = std::time::Instant::now();
    
    let result = harness.compare_with_java(
        "performance_test",
        "perf-alg",
        &["benchmark", "--iterations", "1000"],
        || performance_critical_algorithm(1000),
        Some(Duration::from_secs(60)),
    ).expect("Performance test failed");
    
    let duration = start.elapsed();
    
    // Verify performance (Rust should be faster or comparable)
    assert!(duration.as_secs() < 30, "Rust implementation too slow: {:?}", duration);
    assert_eq!(result["iterations"], 1000);
}
```

## Configuration Options

The `TestConfig` struct provides several configuration options:

```rust
let config = TestConfig {
    default_timeout: Duration::from_secs(30),    // Default timeout for operations
    memory_limit_mb: 1024,                       // Memory limit in MB
    java_wrapper_path: "java_wrapper/build/scripts".to_string(), // Path to Java CLI scripts
    verbose: true,                               // Enable verbose output
};
```

## Troubleshooting

### Common Issues

1. **Java CLI script not found**
   - Ensure the Java wrapper has been compiled: `ant compile-wrappers`
   - Check that the script exists in `java_wrapper/build/scripts/`

2. **Timeout errors**
   - Increase the timeout for complex operations
   - Check if the Java implementation is hanging

3. **Memory limit exceeded**
   - Increase the memory limit in `TestConfig`
   - Optimize the Rust implementation to use less memory

4. **JSON parsing errors**
   - Ensure the Rust function returns valid JSON
   - Check that the Java CLI outputs valid JSON

### Debug Mode

Enable verbose output for debugging:

```rust
let config = TestConfig {
    verbose: true,
    ..Default::default()
};
```

This will print detailed information about test execution, including:
- Test start/completion messages
- Java CLI execution details
- Memory usage information
- Timing information

## Examples

See `tests/java_comparison_examples.rs` for comprehensive examples of all the features described in this document.

## Integration with Translation Tasks

When implementing translation tasks from `TRANSLATION_TASKS.md`, use these patterns:

1. **For simple utility functions**: Use `compare_with_java!` macro
2. **For complex algorithms**: Use `TestHarness::compare_with_java()`
3. **For floating-point operations**: Use `TestHarness::compare_with_java_tolerance()`
4. **For performance-critical code**: Use `test_with_java_comparison!` macro

This ensures that every Rust implementation is thoroughly tested against the Java ground truth, providing confidence in the correctness of the translation.
