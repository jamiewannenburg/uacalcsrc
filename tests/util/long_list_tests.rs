/*!
 * Tests for LongList virtual list implementations.
 * 
 * This module tests the Rust LongList implementations against the Java
 * ground truth using the Java CLI wrapper for validation.
 */

use crate::common::*;
use uacalc::util::virtuallist::*;
use serde_json::json;

// TupleWithMin Tests

#[test]
fn test_tuple_with_min_new() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.virtuallist.TupleWithMinWrapper",
        ["new", "--arrayLen", "3", "--base", "4", "--min", "2"],
        || {
            let tuples = TupleWithMin::new(3, 4, 2);
            json!({
                "command": "new",
                "arrayLen": 3,
                "base": 4,
                "min": 2,
                "status": "created",
                "size": tuples.size()
            })
        }
    );
}

#[test]
fn test_tuple_with_min_size() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.virtuallist.TupleWithMinWrapper",
        ["size", "--arrayLen", "3", "--base", "4", "--min", "2"],
        || {
            let tuples = TupleWithMin::new(3, 4, 2);
            json!({
                "command": "size",
                "arrayLen": 3,
                "base": 4,
                "min": 2,
                "size": tuples.size()
            })
        }
    );
}

#[test]
fn test_tuple_with_min_get_first() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.virtuallist.TupleWithMinWrapper",
        ["get", "--arrayLen", "3", "--base", "4", "--min", "2", "--k", "0"],
        || {
            let tuples = TupleWithMin::new(3, 4, 2);
            let result_vec = tuples.get(0);
            json!({
                "command": "get",
                "arrayLen": 3,
                "base": 4,
                "min": 2,
                "k": 0,
                "value": result_vec
            })
        }
    );
}

#[test]
fn test_tuple_with_min_get_middle() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.virtuallist.TupleWithMinWrapper",
        ["get", "--arrayLen", "3", "--base", "4", "--min", "2", "--k", "28"],
        || {
            let tuples = TupleWithMin::new(3, 4, 2);
            let result_vec = tuples.get(28);
            json!({
                "command": "get",
                "arrayLen": 3,
                "base": 4,
                "min": 2,
                "k": 28,
                "value": result_vec
            })
        }
    );
}

#[test]
fn test_tuple_with_min_get_last() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.virtuallist.TupleWithMinWrapper",
        ["get", "--arrayLen", "3", "--base", "4", "--min", "2", "--k", "55"],
        || {
            let tuples = TupleWithMin::new(3, 4, 2);
            let result_vec = tuples.get(55);
            json!({
                "command": "get",
                "arrayLen": 3,
                "base": 4,
                "min": 2,
                "k": 55,
                "value": result_vec
            })
        }
    );
}

#[test]
fn test_tuple_with_min_different_params() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.virtuallist.TupleWithMinWrapper",
        ["new", "--arrayLen", "4", "--base", "5", "--min", "3"],
        || {
            let tuples = TupleWithMin::new(4, 5, 3);
            json!({
                "command": "new",
                "arrayLen": 4,
                "base": 5,
                "min": 3,
                "status": "created",
                "size": tuples.size()
            })
        }
    );
}

#[test]
fn test_tuple_with_min_sequence() {
    let config = TestConfig::default();
    
    // Test multiple elements in sequence
    let tuples = TupleWithMin::new(3, 4, 2);
    let mut elements = Vec::new();
    for i in 0..10 {
        elements.push(tuples.get(i));
    }
    
    // Compare using the test command which generates the same sequence in Java
    compare_with_java!(
        config,
        "java_wrapper.src.util.virtuallist.TupleWithMinWrapper",
        ["test"],
        || {
            json!({
                "command": "test",
                "arrayLen": 3,
                "base": 4,
                "min": 2,
                "size": tuples.size(),
                "elements": elements,
                "status": "passed"
            })
        }
    );
}

// Existing IntTuples tests

#[test]
fn test_int_tuples_basic() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["int_tuples", "--tuple_length", "3", "--base", "4"],
        || {
            let list = IntTuples::new(3, 4);
            json!({
                "tuple_length": 3,
                "base": 4,
                "size": list.size()
            })
        }
    );
}

#[test]
fn test_int_tuples_get_element() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["int_tuples", "--tuple_length", "3", "--base", "4", "--k", "5"],
        || {
            let list = IntTuples::new(3, 4);
            let result = list.get(5);
            json!({
                "tuple_length": 3,
                "base": 4,
                "k": 5,
                "status": format!("{:?}", result)
            })
        }
    );
}

#[test]
fn test_int_tuples_with_min_basic() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["int_tuples_with_min", "--tuple_length", "3", "--base", "4", "--min", "2"],
        || {
            let list = IntTuplesWithMin::new(3, 4, 2);
            json!({
                "tuple_length": 3,
                "base": 4,
                "min": 2,
                "size": list.size()
            })
        }
    );
}

#[test]
fn test_int_tuples_with_min_get_element() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["int_tuples_with_min", "--tuple_length", "3", "--base", "4", "--min", "2", "--k", "5"],
        || {
            let list = IntTuplesWithMin::new(3, 4, 2);
            let result = list.get(5);
            json!({
                "tuple_length": 3,
                "base": 4,
                "min": 2,
                "k": 5,
                "status": format!("{:?}", result)
            })
        }
    );
}

#[test]
fn test_fixed_sized_subsets_basic() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["fixed_sized_subsets", "--subset_size", "3", "--set_size", "6"],
        || {
            let list = FixedSizedSubsets::new(3, 6);
            json!({
                "subset_size": 3,
                "set_size": 6,
                "size": list.size()
            })
        }
    );
}

#[test]
fn test_fixed_sized_subsets_get_element() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["fixed_sized_subsets", "--subset_size", "3", "--set_size", "6", "--k", "5"],
        || {
            let list = FixedSizedSubsets::new(3, 6);
            let result = list.get(5);
            json!({
                "subset_size": 3,
                "set_size": 6,
                "k": 5,
                "status": format!("{:?}", result)
            })
        }
    );
}

#[test]
fn test_subsets_basic() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["subsets", "--set_size", "4"],
        || {
            let list = Subsets::new(4);
            json!({
                "set_size": 4,
                "size": list.size()
            })
        }
    );
}

#[test]
fn test_subsets_get_element() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["subsets", "--set_size", "4", "--k", "5"],
        || {
            let list = Subsets::new(4);
            let result = list.get(5);
            json!({
                "set_size": 4,
                "k": 5,
                "status": format!("{:?}", result)
            })
        }
    );
}

#[test]
fn test_permutations_basic() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["permutations", "--n", "4"],
        || {
            let list = Permutations::new(4);
            json!({
                "n": 4,
                "size": list.size()
            })
        }
    );
}

#[test]
fn test_permutations_get_element() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["permutations", "--n", "4", "--k", "5"],
        || {
            let list = Permutations::new(4);
            let result = list.get(5);
            json!({
                "n": 4,
                "k": 5,
                "status": format!("{:?}", result)
            })
        }
    );
}

#[test]
fn test_factorial() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["factorial", "--n", "5"],
        || {
            let result = LongListUtils::factorial(5);
            json!({
                "n": 5,
                "status": result
            })
        }
    );
}

#[test]
fn test_binomial() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["binomial", "--n", "5", "--r", "2"],
        || {
            let result = LongListUtils::binomial(5, 2);
            json!({
                "n": 5,
                "r": 2,
                "status": result
            })
        }
    );
}

#[test]
fn test_log2() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["log2", "--k", "8"],
        || {
            let result = LongListUtils::log2(8);
            json!({
                "k": 8,
                "status": result
            })
        }
    );
}

#[test]
fn test_pow2() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["pow2", "--r", "3"],
        || {
            let result = LongListUtils::pow2(3);
            json!({
                "r": 3,
                "status": result
            })
        }
    );
}

#[test]
fn test_comprehensive() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.LongListWrapper",
        ["test"],
        || {
            // Test basic functionality
            let tuples = IntTuples::new(3, 4);
            let result1 = tuples.get(0);
            
            let subsets = Subsets::new(4);
            let result2 = subsets.get(0);
            
            let factorial = LongListUtils::factorial(5);
            let binomial = LongListUtils::binomial(5, 2);
            
            json!({
                "int_tuples_size": tuples.size(),
                "int_tuples_first": format!("{:?}", result1),
                "subsets_size": subsets.size(),
                "subsets_first": format!("{:?}", result2),
                "factorial_5": factorial,
                "binomial_5_2": binomial,
                "status": "all_tests_passed"
            })
        }
    );
}

#[test]
fn test_int_tuples_with_min_size() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.TupleWithMinWrapper",
        ["size", "--array_len", "3", "--base", "4", "--min", "2"],
        || {
            let tuples = IntTuplesWithMin::new(3, 4, 2);
            json!({
                "array_len": 3,
                "base": 4,
                "min": 2,
                "status": tuples.size()
            })
        }
    );
}

#[test]
fn test_tuple_with_min_get() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.TupleWithMinWrapper",
        ["get", "--array_len", "3", "--base", "4", "--min", "2", "--k", "5"],
        || {
            let tuples = IntTuplesWithMin::new(3, 4, 2);
            let result = tuples.get(5);
            json!({
                "array_len": 3,
                "base": 4,
                "min": 2,
                "k": 5,
                "status": format!("{:?}", result)
            })
        }
    );
}

#[test]
fn test_tuple_with_min_create() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.TupleWithMinWrapper",
        ["create", "--array_len", "3", "--base", "4", "--min", "2"],
        || {
            let tuples = IntTuplesWithMin::new(3, 4, 2);
            json!({
                "array_len": 3,
                "base": 4,
                "min": 2,
                "status": tuples.size()
            })
        }
    );
}

#[test]
fn test_tuple_with_min_test() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.TupleWithMinWrapper",
        ["test"],
        || {
            let tuples = IntTuplesWithMin::new(3, 4, 2);
            let size = tuples.size();
            let first = tuples.get(0);
            let last = tuples.get(size - 1);
            json!({
                "array_len": 3,
                "base": 4,
                "min": 2,
                "size": size,
                "first": format!("{:?}", first),
                "last": format!("{:?}", last),
                "status": "all_tests_passed"
            })
        }
    );
}

#[test]
fn test_error_handling() {
    // Test error cases that should be handled gracefully
    let result = IntTuples::new_safe(0, 0);
    assert!(result.is_err());
    
    let result = IntTuplesWithMin::new_safe(3, 2, 2); // base <= min
    assert!(result.is_err());
    
    let result = IntTuplesWithMin::new_safe(3, 2, 2); // base <= min
    assert!(result.is_err());
    
    let result = FixedSizedSubsets::new_safe(5, 3); // subset_size > set_size
    assert!(result.is_err());
    
    let result = Subsets::new_safe(63); // too large
    assert!(result.is_err());
    
    let result = Permutations::new_safe(21); // too large
    assert!(result.is_err());
}

#[test]
fn test_edge_cases() {
    // Test edge cases
    let list = IntTuples::new(0, 1);
    assert_eq!(list.size(), 1);
    assert_eq!(list.get(0), vec![] as Vec<i32>);
    
    let list = IntTuples::new(1, 0);
    assert_eq!(list.size(), 0);
    
    let list = Subsets::new(0);
    assert_eq!(list.size(), 1);
    assert_eq!(list.get(0), vec![] as Vec<i32>);
    
    let list = Permutations::new(0);
    assert_eq!(list.size(), 1);
    assert_eq!(list.get(0), vec![] as Vec<i32>);
}

#[test]
fn test_large_values() {
    // Test with larger values to ensure no overflow
    let list = IntTuples::new(10, 2);
    assert!(list.size() > 0);
    
    let list = Subsets::new(20);
    assert!(list.size() > 0);
    
    let list = Permutations::new(10);
    assert!(list.size() > 0);
}

#[test]
fn test_consistency() {
    // Test that multiple calls to get() return the same result
    let list = IntTuples::new(3, 4);
    let result1 = list.get(5);
    let result2 = list.get(5);
    assert_eq!(result1, result2);
    
    let list = Permutations::new(4);
    let result1 = list.get(10);
    let result2 = list.get(10);
    assert_eq!(result1, result2);
}

#[test]
fn test_bounds() {
    // Test bounds checking
    let list = IntTuples::new(3, 4);
    let size = list.size();
    
    // Test first and last elements
    let _first = list.get(0);
    let _last = list.get(size - 1);
    
    // Test that we can access all elements without panicking
    for i in 0..size.min(100) { // Limit to avoid too long tests
        let _ = list.get(i);
    }
}

#[test]
fn test_utility_functions() {
    // Test utility functions with various inputs
    assert_eq!(LongListUtils::factorial(0), 1);
    assert_eq!(LongListUtils::factorial(1), 1);
    assert_eq!(LongListUtils::factorial(5), 120);
    
    assert_eq!(LongListUtils::binomial(5, 0), 1);
    assert_eq!(LongListUtils::binomial(5, 5), 1);
    assert_eq!(LongListUtils::binomial(5, 2), 10);
    
    assert_eq!(LongListUtils::log2(1), 0);
    assert_eq!(LongListUtils::log2(2), 1);
    assert_eq!(LongListUtils::log2(8), 3);
    
    assert_eq!(LongListUtils::pow2(0), 1);
    assert_eq!(LongListUtils::pow2(1), 2);
    assert_eq!(LongListUtils::pow2(3), 8);
}
