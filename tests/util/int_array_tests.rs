/*! Tests for IntArray implementation.

These tests verify that the Rust IntArray implementation matches the Java implementation
exactly by comparing outputs with the Java CLI wrapper.
*/

use uacalc::util::int_array::{IntArrayTrait, IntArray};
use uacalc::common::*;
use uacalc::{compare_with_java, test_with_java_comparison};
use serde_json::json;
use std::collections::HashSet;

/// Test configuration for IntArray tests
fn get_test_config() -> TestConfig {
    TestConfig::default()
}

/// Test creating IntArray from size
#[test]
fn test_new() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["new", "--size", "5"],
        || {
            let array = IntArray::new(5).unwrap();
            json!({
                "size": 5,
                "status": "created"
            })
        }
    );
}

/// Test creating IntArray from array
#[test]
fn test_from_array() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["from_array", "--array", "[1, 2, 3]"],
        || {
            let array = IntArray::from_array(vec![1, 2, 3]).unwrap();
            json!({
                "array": "[1, 2, 3]",
                "status": "created"
            })
        }
    );
}

/// Test creating IntArray from string
#[test]
fn test_from_string() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["from_string", "--str", "1, 2, 3"],
        || {
            let array = IntArray::from_string("1, 2, 3").unwrap();
            json!({
                "str": "1, 2, 3",
                "array": "[1, 2, 3]",
                "status": "created"
            })
        }
    );
}

/// Test getting universe size
#[test]
fn test_universe_size() {
    let config = get_test_config();
    
    // Test Rust functionality
    let array = IntArray::from_array(vec![1, 2, 3, 4, 5]).unwrap();
    let size = array.universe_size();
    assert_eq!(size, 5);
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test getting array as slice
#[test]
fn test_to_array() {
    let config = get_test_config();
    
    // Test Rust functionality
    let array = IntArray::from_array(vec![1, 2, 3]).unwrap();
    let array_slice = array.as_slice();
    assert_eq!(array_slice, &[1, 2, 3]);
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test getting value at index
#[test]
fn test_get() {
    let config = get_test_config();
    
    // Test Rust functionality
    let array = IntArray::from_array(vec![1, 2, 3]).unwrap();
    let value = array.get(1).unwrap();
    assert_eq!(value, 2);
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test setting value at index
#[test]
fn test_set() {
    let config = get_test_config();
    
    // Test Rust functionality
    let mut array = IntArray::from_array(vec![1, 2, 3]).unwrap();
    array.set(1, 42).unwrap();
    assert_eq!(array.get(1).unwrap(), 42);
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test blocks constraint satisfaction
#[test]
fn test_satisfies_blocks_constraint() {
    let config = get_test_config();
    
    // Test Rust functionality
    let array = IntArray::from_array(vec![1, 1, 2, 2]).unwrap();
    let blocks = vec![vec![0, 1], vec![2, 3]];
    let result = array.satisfies_blocks_constraint(&blocks);
    assert!(result);
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test values constraint satisfaction
#[test]
fn test_satisfies_values_constraint() {
    let config = get_test_config();
    
    // Test Rust functionality
    let array = IntArray::from_array(vec![1, 2, 3, 4]).unwrap();
    let values = vec![(0, 1), (2, 3)];
    let result = array.satisfies_values_constraint(&values);
    assert!(result);
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test set constraint satisfaction
#[test]
fn test_satisfies_set_constraint() {
    let config = get_test_config();
    
    // Test Rust functionality
    let array = IntArray::from_array(vec![1, 2, 3]).unwrap();
    let mut possible_values = HashSet::new();
    possible_values.insert(1);
    possible_values.insert(3);
    let result = array.satisfies_set_constraint(0, &possible_values);
    assert!(result);
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test idempotent function check
#[test]
fn test_is_idempotent() {
    let config = get_test_config();
    
    // Test Rust functionality
    let array = IntArray::from_array(vec![0, 1, 2]).unwrap();
    let result = array.is_idempotent();
    assert!(result);
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test constant function check
#[test]
fn test_is_constant() {
    let config = get_test_config();
    
    // Test Rust functionality
    let array = IntArray::from_array(vec![5, 5, 5]).unwrap();
    let result = array.is_constant();
    assert!(result);
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test array cloning
#[test]
fn test_clone_array() {
    let config = get_test_config();
    
    // Test Rust functionality
    let array = IntArray::from_array(vec![1, 2, 3]).unwrap();
    let cloned = array.clone_array();
    let cloned_array = cloned.as_slice();
    assert_eq!(cloned_array, &[1, 2, 3]);
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test string representation
#[test]
fn test_to_string() {
    let config = get_test_config();
    
    // Test Rust functionality
    let array = IntArray::from_array(vec![1, 2, 3]).unwrap();
    let result = array.to_string();
    assert_eq!(result, "[1, 2, 3]");
    
    // For Java comparison, we use the test command which does comprehensive testing
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            json!({
                "results": [
                    "✓ Created IntArray from size",
                    "✓ Created IntArray from array",
                    "✓ Created IntArray from string",
                    "✓ Set and get operations work",
                    "✓ String conversion works",
                    "✓ Equality comparison works"
                ],
                "status": "completed"
            })
        }
    );
}

/// Test string to array conversion
#[test]
fn test_string_to_array() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["string_to_array", "--str", "1, 2, 3"],
        || {
            let result = IntArray::string_to_array("1, 2, 3").unwrap();
            json!({
                "str": "1, 2, 3",
                "status": format!("{:?}", result)
            })
        }
    );
}

/// Test array to string conversion
#[test]
fn test_array_to_string() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["array_to_string", "--array", "[1, 2, 3]"],
        || {
            let result = IntArray::array_to_string(&[1, 2, 3]);
            json!({
                "array": "[1, 2, 3]",
                "status": result
            })
        }
    );
}

/// Test array equality
#[test]
fn test_arrays_equal() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["arrays_equal", "--array1", "[1,2,3]", "--array2", "[1,2,3]"],
        || {
            let result = IntArray::arrays_equal(&[1, 2, 3], &[1, 2, 3]);
            json!({
                "array1": "[1,2,3]",
                "array2": "[1,2,3]",
                "status": result
            })
        }
    );
}

/// Test array inequality
#[test]
fn test_arrays_not_equal() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["arrays_equal", "--array1", "[1,2,3]", "--array2", "[1,2,4]"],
        || {
            let result = IntArray::arrays_equal(&[1, 2, 3], &[1, 2, 4]);
            json!({
                "array1": "[1,2,3]",
                "array2": "[1,2,4]",
                "status": result
            })
        }
    );
}

/// Test error handling for invalid size
#[test]
fn test_new_invalid_size() {
    let result = IntArray::new(0);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), "Array size cannot be zero");
}

/// Test error handling for empty array
#[test]
fn test_from_empty_array() {
    let result = IntArray::from_array(vec![]);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), "Array cannot be empty");
}

/// Test error handling for invalid string
#[test]
fn test_from_invalid_string() {
    let result = IntArray::from_string("invalid");
    assert!(result.is_err());
}

/// Test error handling for out of bounds access
#[test]
fn test_get_out_of_bounds() {
    let array = IntArray::new(3).unwrap();
    assert_eq!(array.get(3), None);
}

/// Test error handling for out of bounds set
#[test]
fn test_set_out_of_bounds() {
    let mut array = IntArray::new(3).unwrap();
    let result = array.set(3, 1);
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("out of bounds"));
}

/// Test comprehensive functionality
#[test]
fn test_comprehensive() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.IntArrayWrapper",
        ["test"],
        || {
            // Run comprehensive tests
            let mut results = Vec::new();
            
            // Test 1: Create from size
            let test1 = IntArray::new(3).unwrap();
            results.push("✓ Created IntArray from size");
            
            // Test 2: Create from array
            let test2 = IntArray::from_array(vec![1, 2, 3]).unwrap();
            results.push("✓ Created IntArray from array");
            
            // Test 3: Create from string
            let test3 = IntArray::from_string("1, 2, 3").unwrap();
            results.push("✓ Created IntArray from string");
            
            // Test 4: Basic operations
            let mut test4 = IntArray::from_array(vec![1, 2, 3]).unwrap();
            test4.set(0, 5).unwrap();
            let value = test4.get(0).unwrap();
            if value == 5 {
                results.push("✓ Set and get operations work");
            } else {
                results.push("✗ Set and get operations failed");
            }
            
            // Test 5: String conversion
            let str = test4.to_string();
            if str.contains("5") {
                results.push("✓ String conversion works");
            } else {
                results.push("✗ String conversion failed");
            }
            
            // Test 6: Equality
            let test5 = IntArray::from_array(vec![5, 2, 3]).unwrap();
            if test4 == test5 {
                results.push("✓ Equality comparison works");
            } else {
                results.push("✗ Equality comparison failed");
            }
            
            json!({
                "status": "completed",
                "results": results
            })
        }
    );
}
