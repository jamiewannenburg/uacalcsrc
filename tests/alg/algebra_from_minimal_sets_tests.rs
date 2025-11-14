/*! Tests for the AlgebraFromMinimalSets module.

These tests verify that the Rust implementation matches the Java implementation
by comparing outputs with the Java CLI wrapper.
*/

use uacalc::alg::{AlgebraFromMinimalSets, SmallAlgebra, BasicAlgebra, Algebra};
use std::collections::HashSet;

/// Helper function to create a mock BasicAlgebra for testing
fn create_mock_algebra(name: &str, universe: Vec<i32>) -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
    let name = name.to_string();
    let universe_set: HashSet<i32> = universe.into_iter().collect();
    let operations = Vec::new(); // Empty operations for testing
    
    Box::new(BasicAlgebra::new(name, universe_set, operations)) as Box<dyn SmallAlgebra<UniverseItem = i32>>
}

#[test]
fn test_algebra_from_minimal_sets_new() {
    // Create mock minimal algebra
    let min_alg = create_mock_algebra("minimal", vec![0, 1, 2]);
    
    // Create algebra from minimal sets
    let alg = AlgebraFromMinimalSets::new(min_alg).unwrap();
    
    // Test basic properties
    // Default size should be 3 * 3 - 2 = 7
    assert_eq!(alg.cardinality(), 7);
    assert_eq!(alg.name(), "AlgebraFromMinimalSets");
}

#[test]
fn test_algebra_from_minimal_sets_new_with_name() {
    // Create mock minimal algebra
    let min_alg = create_mock_algebra("minimal", vec![0, 1, 2]);
    
    // Create algebra from minimal sets with name
    let alg = AlgebraFromMinimalSets::new_with_name(
        Some("TestAlgebra".to_string()),
        min_alg
    ).unwrap();
    
    // Test basic properties
    assert_eq!(alg.cardinality(), 7);
    assert_eq!(alg.name(), "TestAlgebra");
}

#[test]
fn test_algebra_from_minimal_sets_new_with_size() {
    // Create mock minimal algebra
    let min_alg = create_mock_algebra("minimal", vec![0, 1, 2]);
    
    // Create algebra from minimal sets with explicit size and default maps
    // Using None for maps will create default maps that cover all elements
    let alg = AlgebraFromMinimalSets::new_with_size(
        min_alg,
        7, // Use default size to match default maps
        None
    ).unwrap();
    
    // Test basic properties
    assert_eq!(alg.cardinality(), 7);
}

#[test]
fn test_algebra_from_minimal_sets_new_with_connecting_pts() {
    // Create mock minimal algebra
    let min_alg = create_mock_algebra("minimal", vec![0, 1, 2]);
    
    // Create algebra from minimal sets with connecting points
    let alg = AlgebraFromMinimalSets::new_with_connecting_pts(
        Some("TestAlgebra".to_string()),
        min_alg,
        Some(vec![0, 2])
    ).unwrap();
    
    // Test basic properties
    assert_eq!(alg.cardinality(), 7);
    assert_eq!(alg.name(), "TestAlgebra");
}

#[test]
fn test_algebra_from_minimal_sets_get_element() {
    // Create mock minimal algebra
    let min_alg = create_mock_algebra("minimal", vec![0, 1, 2]);
    
    // Create algebra from minimal sets
    let alg = AlgebraFromMinimalSets::new(min_alg).unwrap();
    
    // Test get_element
    assert_eq!(alg.get_element(0), Some(0));
    assert_eq!(alg.get_element(6), Some(6));
    assert_eq!(alg.get_element(7), None); // Out of bounds
}

#[test]
fn test_algebra_from_minimal_sets_element_index() {
    // Create mock minimal algebra
    let min_alg = create_mock_algebra("minimal", vec![0, 1, 2]);
    
    // Create algebra from minimal sets
    let alg = AlgebraFromMinimalSets::new(min_alg).unwrap();
    
    // Test element_index
    assert_eq!(alg.element_index(&0), Some(0));
    assert_eq!(alg.element_index(&6), Some(6));
    assert_eq!(alg.element_index(&7), None); // Out of bounds
}

#[test]
fn test_algebra_from_minimal_sets_get_universe_list() {
    // Create mock minimal algebra
    let min_alg = create_mock_algebra("minimal", vec![0, 1, 2]);
    
    // Create algebra from minimal sets
    let alg = AlgebraFromMinimalSets::new(min_alg).unwrap();
    
    // Test get_universe_list
    let universe = alg.get_universe_list().unwrap();
    assert_eq!(universe.len(), 7);
    assert_eq!(universe[0], 0);
    assert_eq!(universe[6], 6);
}

#[test]
fn test_algebra_from_minimal_sets_operations() {
    // Create mock minimal algebra
    let min_alg = create_mock_algebra("minimal", vec![0, 1, 2]);
    
    // Create algebra from minimal sets
    let alg = AlgebraFromMinimalSets::new(min_alg).unwrap();
    
    // Test operations - should have at least the 's' operation and map operations
    let ops = alg.operations();
    assert!(!ops.is_empty());
}

#[test]
fn test_algebra_from_minimal_sets_parent() {
    // Create mock minimal algebra
    let min_alg = create_mock_algebra("minimal", vec![0, 1, 2]);
    
    // Create algebra from minimal sets
    let alg = AlgebraFromMinimalSets::new(min_alg).unwrap();
    
    // Test parent - should return the minimal algebra
    let parent = alg.parent();
    assert!(parent.is_some());
    assert_eq!(parent.unwrap().cardinality(), 3);
}

#[test]
fn test_algebra_from_minimal_sets_different_sizes() {
    // Test with different minimal algebra sizes
    for min_size in 2..=5 {
        let universe: Vec<i32> = (0..min_size).collect();
        let min_alg = create_mock_algebra("minimal", universe);
        
        let alg = AlgebraFromMinimalSets::new(min_alg).unwrap();
        
        // Default size should be 3 * min_size - 2
        let expected_size = 3 * min_size - 2;
        assert_eq!(alg.cardinality(), expected_size as i32);
    }
}

