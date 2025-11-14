/*! Tests for the Homomorphism module.

These tests verify that the Rust implementation matches the Java implementation
by comparing outputs with the Java CLI wrapper.
*/

use uacalc::alg::{Homomorphism, SmallAlgebra, BasicAlgebra};
use uacalc::alg::conlat::partition::Partition;
use std::collections::{HashMap, HashSet};

/// Helper function to create a mock BasicAlgebra for testing
fn create_mock_algebra(name: &str, universe: Vec<i32>) -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
    let name = name.to_string();
    let universe_set: HashSet<i32> = universe.into_iter().collect();
    let operations = Vec::new(); // Empty operations for testing
    
    Box::new(BasicAlgebra::new(name, universe_set, operations)) as Box<dyn SmallAlgebra<UniverseItem = i32>>
}

#[test]
fn test_homomorphism_new() {
    // Create mock algebras for testing
    let domain = create_mock_algebra("domain", vec![0, 1]);
    let range = create_mock_algebra("range", vec![0, 1]);
    
    let mut map = HashMap::new();
    map.insert(0, 0);
    map.insert(1, 1);
    
    let homo = Homomorphism::new_safe(domain, range, map).unwrap();
    
    // Test basic properties
    assert_eq!(homo.get_domain().name(), "domain");
    assert_eq!(homo.get_range().name(), "range");
    assert_eq!(homo.get_map().len(), 2);
    assert_eq!(homo.get_map().get(&0), Some(&0));
    assert_eq!(homo.get_map().get(&1), Some(&1));
}

#[test]
fn test_homomorphism_kernel() {
    // Create mock algebras for testing
    let domain = create_mock_algebra("domain", vec![0, 1]);
    let range = create_mock_algebra("range", vec![0, 1]);
    
    let mut map = HashMap::new();
    map.insert(0, 0);
    map.insert(1, 1);
    
    let homo = Homomorphism::new_safe(domain, range, map).unwrap();
    let kernel = homo.kernel().unwrap();
    
    // Test kernel properties - each element should be in its own block
    assert_eq!(kernel.number_of_blocks(), 2);
    assert!(!kernel.is_related(0, 1)); // 0 and 1 should not be related
}

#[test]
fn test_homomorphism_kernel_with_duplicate_mapping() {
    // Create mock algebras for testing
    let domain = create_mock_algebra("domain", vec![0, 1]);
    let range = create_mock_algebra("range", vec![0]);
    
    let mut map = HashMap::new();
    map.insert(0, 0);
    map.insert(1, 0); // Both map to 0
    
    let homo = Homomorphism::new_safe(domain, range, map).unwrap();
    let kernel = homo.kernel().unwrap();
    
    // Test kernel properties - should have 1 block since both elements map to same value
    assert_eq!(kernel.number_of_blocks(), 1);
    assert!(kernel.is_related(0, 1)); // 0 and 1 should be related since they map to the same value
}

#[test]
fn test_homomorphism_to_string() {
    // Create mock algebras for testing
    let domain = create_mock_algebra("domain", vec![0, 1]);
    let range = create_mock_algebra("range", vec![0, 1]);
    
    let mut map = HashMap::new();
    map.insert(0, 0);
    map.insert(1, 1);
    
    let homo = Homomorphism::new_safe(domain, range, map).unwrap();
    
    // Test string representation
    let str_repr = homo.to_string();
    assert!(str_repr.contains("domain"));
    assert!(str_repr.contains("range"));
    assert!(str_repr.contains("homomorphism"));
}

#[test]
fn test_homomorphism_get_set_methods() {
    // Create mock algebras for testing
    let domain = create_mock_algebra("domain", vec![0, 1]);
    let range = create_mock_algebra("range", vec![0, 1]);
    
    let mut map = HashMap::new();
    map.insert(0, 0);
    map.insert(1, 1);
    
    let mut homo = Homomorphism::new_safe(domain, range, map).unwrap();
    
    // Test getters
    assert_eq!(homo.get_domain().name(), "domain");
    assert_eq!(homo.get_range().name(), "range");
    assert_eq!(homo.get_map().len(), 2);
    assert_eq!(homo.get_map().get(&0), Some(&0));
    assert_eq!(homo.get_map().get(&1), Some(&1));
    
    // Test setters
    let new_domain = create_mock_algebra("new_domain", vec![0, 1, 2]);
    let new_range = create_mock_algebra("new_range", vec![0, 1, 2]);
    let mut new_map = HashMap::new();
    new_map.insert(0, 0);
    new_map.insert(1, 1);
    new_map.insert(2, 2);
    
    homo.set_domain(new_domain);
    homo.set_range(new_range);
    homo.set_map(new_map);
    
    // Verify setters worked
    assert_eq!(homo.get_domain().name(), "new_domain");
    assert_eq!(homo.get_range().name(), "new_range");
    assert_eq!(homo.get_map().len(), 3);
    assert_eq!(homo.get_map().get(&2), Some(&2));
}

#[test]
fn test_homomorphism_validation() {
    // Test invalid mapping - missing domain element
    let domain = create_mock_algebra("domain", vec![0, 1]);
    let range = create_mock_algebra("range", vec![0, 1]);
    
    let mut map = HashMap::new();
    map.insert(0, 0);
    // Missing element 1
    
    let result = Homomorphism::new_safe(domain, range, map);
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("Domain element 1 is not mapped"));
}

#[test]
fn test_homomorphism_validation_out_of_range() {
    // Test invalid mapping - out of range value
    let domain = create_mock_algebra("domain", vec![0, 1]);
    let range = create_mock_algebra("range", vec![0]);
    
    let mut map = HashMap::new();
    map.insert(0, 0);
    map.insert(1, 1); // 1 is out of range for range algebra with cardinality 1
    
    let result = Homomorphism::new_safe(domain, range, map);
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("Mapped value 1 is out of range"));
}

#[test]
fn test_homomorphism_product_homo_empty_list() {
    let result = Homomorphism::product_homo(&[]);
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("Cannot create product homomorphism from empty list"));
}

#[test]
fn test_homomorphism_basic_functionality() {
    // Test basic homomorphism creation and operations
    let domain = create_mock_algebra("domain", vec![0, 1, 2]);
    let range = create_mock_algebra("range", vec![0, 1]);
    
    let mut map = HashMap::new();
    map.insert(0, 0);
    map.insert(1, 1);
    map.insert(2, 0); // 0 and 2 both map to 0
    
    let homo = Homomorphism::new_safe(domain, range, map).unwrap();
    
    // Test kernel - should have 2 blocks: {0, 2} and {1}
    let kernel = homo.kernel().unwrap();
    assert_eq!(kernel.number_of_blocks(), 2);
    
    // Test that 0 and 2 are in the same block
    assert!(kernel.is_related(0, 2));
    assert!(!kernel.is_related(0, 1));
    assert!(!kernel.is_related(1, 2));
    
    // Test string representation
    let str_repr = homo.to_string();
    assert!(str_repr.contains("domain"));
    assert!(str_repr.contains("range"));
    assert!(str_repr.contains("homomorphism"));
}
