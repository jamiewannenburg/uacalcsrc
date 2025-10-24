/*! Tests for Taylor implementation.

These tests verify that the Rust Taylor implementation matches the Java implementation
exactly by comparing outputs with the Java CLI wrapper.
*/

use uacalc::terms::{Taylor, VariableImp, NonVariableTerm, Term};
use uacalc::alg::op::OperationSymbol;
use uacalc::util::int_array::IntArray;
use uacalc::common::*;
use uacalc::{compare_with_java, test_with_java_comparison};
use serde_json::json;

/// Test configuration for Taylor tests
fn get_test_config() -> TestConfig {
    TestConfig::default()
}

/// Test creating the Markovic-McKenzie term
#[test]
fn test_markovic_mckenzie_term() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.terms.TaylorWrapper",
        ["markovic_mckenzie_term"],
        || {
            let taylor = Taylor::markovic_mckenzie_term();
            json!({
                "command": "markovic_mckenzie_term",
                "arity": taylor.arity(),
                "inteqs_count": taylor.inteqs().len()
            })
        }
    );
}

/// Test creating the Siggers term
#[test]
fn test_siggers_term() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.terms.TaylorWrapper",
        ["siggers_term"],
        || {
            let taylor = Taylor::siggers_term();
            json!({
                "command": "siggers_term",
                "arity": taylor.arity(),
                "inteqs_count": taylor.inteqs().len()
            })
        }
    );
}

/// Test creating a Taylor with arity and equations
#[test]
fn test_new_with_arity() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.terms.TaylorWrapper",
        ["new_with_arity", "--arity", "4", "--eqs", "[[1,0,0,0],[0,0,1,1]]:[[0,0,1,0],[0,1,0,0]]"],
        || {
            let mut eqs = Vec::new();
            
            let mut eq = Vec::new();
            eq.push(IntArray::from_array(vec![1, 0, 0, 0]).unwrap());
            eq.push(IntArray::from_array(vec![0, 0, 1, 1]).unwrap());
            eqs.push(eq);
            
            let mut eq = Vec::new();
            eq.push(IntArray::from_array(vec![0, 0, 1, 0]).unwrap());
            eq.push(IntArray::from_array(vec![0, 1, 0, 0]).unwrap());
            eqs.push(eq);
            
            let taylor = Taylor::new_with_arity(4, eqs);
            json!({
                "command": "new_with_arity",
                "arity": taylor.arity(),
                "inteqs_count": taylor.inteqs().len()
            })
        }
    );
}

/// Test term_from_array
#[test]
fn test_term_from_array() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.terms.TaylorWrapper",
        ["term_from_array", "--arr", "0,1,1,0", "--arity", "2", "--eqs", "[[1,0],[0,1]]"],
        || {
            let mut eqs = Vec::new();
            let mut eq = Vec::new();
            eq.push(IntArray::from_array(vec![1, 0]).unwrap());
            eq.push(IntArray::from_array(vec![0, 1]).unwrap());
            eqs.push(eq);
            
            let taylor = Taylor::new_with_arity(2, eqs);
            let term = taylor.term_from_array(&[0, 1, 1, 0]);
            
            json!({
                "command": "term_from_array",
                "status": format!("{}", term)
            })
        }
    );
}

/// Test lexicographically_compare_arrays
#[test]
fn test_lexicographically_compare_arrays() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.terms.TaylorWrapper",
        ["lexicographically_compare_arrays", "--a", "1,2,3", "--b", "1,2,4"],
        || {
            let result = Taylor::lexicographically_compare_arrays(&[1, 2, 3], &[1, 2, 4]);
            json!({
                "command": "lexicographically_compare_arrays",
                "status": result
            })
        }
    );
}

/// Test lexicographically_compare_arrays with equal arrays
#[test]
fn test_lexicographically_compare_arrays_equal() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.terms.TaylorWrapper",
        ["lexicographically_compare_arrays", "--a", "1,2,3", "--b", "1,2,3"],
        || {
            let result = Taylor::lexicographically_compare_arrays(&[1, 2, 3], &[1, 2, 3]);
            json!({
                "command": "lexicographically_compare_arrays",
                "status": result
            })
        }
    );
}

/// Test lexicographically_compare_arrays with first array greater
#[test]
fn test_lexicographically_compare_arrays_greater() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.terms.TaylorWrapper",
        ["lexicographically_compare_arrays", "--a", "1,3,3", "--b", "1,2,3"],
        || {
            let result = Taylor::lexicographically_compare_arrays(&[1, 3, 3], &[1, 2, 3]);
            json!({
                "command": "lexicographically_compare_arrays",
                "status": result
            })
        }
    );
}

/// Test arity getter
#[test]
fn test_arity() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.terms.TaylorWrapper",
        ["arity", "--arity", "4", "--eqs", "[[1,0,0,0],[0,0,1,1]]"],
        || {
            let mut eqs = Vec::new();
            let mut eq = Vec::new();
            eq.push(IntArray::from_array(vec![1, 0, 0, 0]).unwrap());
            eq.push(IntArray::from_array(vec![0, 0, 1, 1]).unwrap());
            eqs.push(eq);
            
            let taylor = Taylor::new_with_arity(4, eqs);
            json!({
                "command": "arity",
                "status": taylor.arity()
            })
        }
    );
}

/// Test comprehensive functionality
#[test]
fn test_taylor_comprehensive() {
    let config = get_test_config();
    
    compare_with_java!(
        config,
        "java_wrapper.src.terms.TaylorWrapper",
        ["test"],
        || {
            // Run comprehensive tests in Rust
            let mm = Taylor::markovic_mckenzie_term();
            assert_eq!(mm.arity(), 4, "Markovic-McKenzie arity should be 4");
            
            let siggers = Taylor::siggers_term();
            assert_eq!(siggers.arity(), 6, "Siggers arity should be 6");
            
            let result = Taylor::lexicographically_compare_arrays(&[1, 2, 3], &[1, 2, 4]);
            assert!(result < 0, "a should be less than b");
            
            json!({
                "command": "test",
                "status": "All tests passed"
            })
        }
    );
}

// Unit tests without Java comparison

/// Test that Markovic-McKenzie term has correct properties
#[test]
fn test_mm_properties() {
    let taylor = Taylor::markovic_mckenzie_term();
    assert_eq!(taylor.arity(), 4);
    assert_eq!(taylor.inteqs().len(), 2);
}

/// Test that Siggers term has correct properties
#[test]
fn test_siggers_properties() {
    let taylor = Taylor::siggers_term();
    assert_eq!(taylor.arity(), 6);
    assert_eq!(taylor.inteqs().len(), 2);
}

/// Test lexicographic comparison properties
#[test]
fn test_lexicographic_comparison_properties() {
    // Equal arrays
    assert_eq!(Taylor::lexicographically_compare_arrays(&[1, 2, 3], &[1, 2, 3]), 0);
    
    // First less than second
    assert!(Taylor::lexicographically_compare_arrays(&[1, 2, 3], &[1, 2, 4]) < 0);
    assert!(Taylor::lexicographically_compare_arrays(&[1, 2, 3], &[2, 2, 3]) < 0);
    
    // First greater than second
    assert!(Taylor::lexicographically_compare_arrays(&[1, 2, 4], &[1, 2, 3]) > 0);
    assert!(Taylor::lexicographically_compare_arrays(&[2, 2, 3], &[1, 2, 3]) > 0);
    
    // Empty arrays
    assert_eq!(Taylor::lexicographically_compare_arrays(&[], &[]), 0);
    
    // Single element
    assert!(Taylor::lexicographically_compare_arrays(&[1], &[2]) < 0);
    assert!(Taylor::lexicographically_compare_arrays(&[2], &[1]) > 0);
}

/// Test term_from_array creates correct structure
#[test]
fn test_term_from_array_structure() {
    let mut eqs = Vec::new();
    let mut eq = Vec::new();
    eq.push(IntArray::from_array(vec![1, 0]).unwrap());
    eq.push(IntArray::from_array(vec![0, 1]).unwrap());
    eqs.push(eq);
    
    let taylor = Taylor::new_with_arity(2, eqs);
    
    // Create a term from array [0, 1]
    let term = taylor.term_from_array(&[0, 1]);
    assert!(!term.isa_variable());
    
    // Create a term from array [0]
    let term = taylor.term_from_array(&[0]);
    assert!(term.isa_variable());
}

/// Test that creating Taylor with different arities works
#[test]
fn test_taylor_different_arities() {
    for arity in 2..=6 {
        let mut eqs = Vec::new();
        let mut eq = Vec::new();
        let mut left = vec![0; arity as usize];
        left[0] = 1;
        let mut right = vec![0; arity as usize];
        right[1] = 1;
        eq.push(IntArray::from_array(left).unwrap());
        eq.push(IntArray::from_array(right).unwrap());
        eqs.push(eq);
        
        let taylor = Taylor::new_with_arity(arity, eqs);
        assert_eq!(taylor.arity(), arity);
    }
}
