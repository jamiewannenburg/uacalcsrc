/*! BasicSet tests.

This module provides comprehensive tests for the BasicSet implementation,
including unit tests, integration tests, and cross-language compatibility tests.
*/

use uacalc::alg::sublat::BasicSet;
use uacalc::util::int_array::IntArrayTrait;
use crate::common::{TestConfig, compare_with_java};

#[test]
fn test_basic_set_creation() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["new", "--elements", "1,3,5"],
        || {
            let set = BasicSet::new(vec![1, 3, 5]).unwrap();
            serde_json::json!({
                "elements": set.elements(),
                "size": set.size()
            })
        }
    );
}

#[test]
fn test_basic_set_empty() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["new", "--elements", ""],
        || {
            let set = BasicSet::new(vec![]).unwrap();
            serde_json::json!({
                "elements": set.elements(),
                "size": set.size()
            })
        }
    );
}

#[test]
fn test_basic_set_duplicates() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["new", "--elements", "1,3,1,5,3"],
        || {
            let set = BasicSet::new(vec![1, 3, 1, 5, 3]).unwrap();
            serde_json::json!({
                "elements": set.elements(),
                "size": set.size()
            })
        }
    );
}

#[test]
fn test_basic_set_contains() {
    let config = TestConfig::default();
    
    // Test with element in set
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["contains", "--element", "3"],
        || {
            let set = BasicSet::new(vec![1, 3, 5]).unwrap();
            serde_json::json!({
                "result": set.contains(3)
            })
        }
    );
}

#[test]
fn test_basic_set_contains_not() {
    let config = TestConfig::default();
    
    // Test with element not in set
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["contains", "--element", "2"],
        || {
            let set = BasicSet::new(vec![1, 3, 5]).unwrap();
            serde_json::json!({
                "result": set.contains(2)
            })
        }
    );
}

#[test]
fn test_basic_set_leq() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["leq", "--other", "1,2,3,4,5"],
        || {
            let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
            let set2 = BasicSet::new(vec![1, 2, 3, 4, 5]).unwrap();
            serde_json::json!({
                "result": set1.leq(&set2)
            })
        }
    );
}

#[test]
fn test_basic_set_leq_static() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["leq_static", "--u", "1,3", "--v", "1,2,3,4"],
        || {
            let result = BasicSet::leq_static(&[1, 3], &[1, 2, 3, 4]);
            serde_json::json!({
                "result": result
            })
        }
    );
}

#[test]
fn test_basic_set_intersection() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["intersection", "--other", "2,3,4"],
        || {
            let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
            let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
            let result = set1.intersection(&set2);
            serde_json::json!({
                "result": result.elements()
            })
        }
    );
}

#[test]
fn test_basic_set_intersection_static() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["intersection_static", "--set1", "1,3,5", "--set2", "2,3,4"],
        || {
            let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
            let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
            let result = BasicSet::intersection_static(&set1, &set2);
            serde_json::json!({
                "result": result.elements()
            })
        }
    );
}

#[test]
fn test_basic_set_union() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["union", "--other", "2,3,4"],
        || {
            let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
            let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
            let result = set1.union(&set2);
            serde_json::json!({
                "result": result.elements()
            })
        }
    );
}

#[test]
fn test_basic_set_union_static() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["union_static", "--set1", "1,3,5", "--set2", "2,3,4"],
        || {
            let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
            let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
            let result = BasicSet::union_static(&set1, &set2);
            serde_json::json!({
                "result": result.elements()
            })
        }
    );
}

#[test]
fn test_basic_set_difference() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["set_difference", "--other", "2,3,4"],
        || {
            let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
            let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
            let result = set1.set_difference(&set2);
            serde_json::json!({
                "result": result.elements()
            })
        }
    );
}

#[test]
fn test_basic_set_normalize() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["normalize"],
        || {
            let mut set = BasicSet::new(vec![3, 1, 5, 1, 3]).unwrap();
            set.normalize();
            serde_json::json!({
                "elements": set.elements()
            })
        }
    );
}

#[test]
fn test_basic_set_size() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["size"],
        || {
            let set = BasicSet::new(vec![1, 3, 5]).unwrap();
            serde_json::json!({
                "size": set.size()
            })
        }
    );
}

#[test]
fn test_basic_set_universe_size() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["universe_size"],
        || {
            let set = BasicSet::new(vec![1, 3, 5]).unwrap();
            serde_json::json!({
                "universe_size": set.universe_size()
            })
        }
    );
}

#[test]
fn test_basic_set_elements() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "sublat.BasicSetWrapper",
        ["elements"],
        || {
            let set = BasicSet::new(vec![1, 3, 5]).unwrap();
            serde_json::json!({
                "elements": set.elements()
            })
        }
    );
}

#[test]
fn test_basic_set_comparison() {
    let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
    let set2 = BasicSet::new(vec![1, 3, 5]).unwrap();
    let set3 = BasicSet::new(vec![1, 3, 6]).unwrap();
    
    assert_eq!(set1, set2);
    assert_ne!(set1, set3);
    assert!(set1 <= set2);
    assert!(set1 >= set2);
    assert!(set1 < set3);
}

#[test]
fn test_basic_set_hash() {
    use std::collections::HashSet;
    
    let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
    let set2 = BasicSet::new(vec![1, 3, 5]).unwrap();
    let set3 = BasicSet::new(vec![1, 3, 6]).unwrap();
    
    let mut hash_set = HashSet::new();
    hash_set.insert(set1.clone());
    hash_set.insert(set2.clone());
    hash_set.insert(set3.clone());
    
    // set1 and set2 should be the same, so only 2 unique items
    assert_eq!(hash_set.len(), 2);
}

#[test]
fn test_basic_set_display() {
    let set = BasicSet::new(vec![1, 3, 5]).unwrap();
    let display_str = format!("{}", set);
    assert_eq!(display_str, "{1,3,5}");
}

#[test]
fn test_basic_set_int_array_trait() {
    let mut set = BasicSet::new(vec![1, 3, 5]).unwrap();
    
    // Test IntArrayTrait implementation
    assert_eq!(set.universe_size(), 3);
    assert_eq!(set.get(0), Some(1));
    assert_eq!(set.get(1), Some(3));
    assert_eq!(set.get(2), Some(5));
    assert_eq!(set.get(3), None);
    
    // Test set method
    set.set(0, 2).unwrap();
    assert_eq!(set.get(0), Some(2));
    
    // Test as_slice
    let slice = set.as_slice();
    assert_eq!(slice, &[2, 3, 5]);
}

#[test]
fn test_basic_set_constraints() {
    let set = BasicSet::new(vec![1, 2, 3]).unwrap();
    
    // Test blocks constraint
    let blocks = vec![vec![0, 1], vec![2]];
    assert!(set.satisfies_blocks_constraint(&blocks));
    
    // Test values constraint
    let values = vec![(0, 1), (1, 2)];
    assert!(set.satisfies_values_constraint(&values));
    
    // Test set constraint
    use std::collections::HashSet;
    let possible_values: HashSet<i32> = [1, 2, 3].iter().cloned().collect();
    assert!(set.satisfies_set_constraint(0, &possible_values));
    
    // Test constant check
    let constant_set = BasicSet::new(vec![1, 1, 1]).unwrap();
    assert!(constant_set.is_constant());
    assert!(!set.is_constant());
    
    // Test idempotent check
    let idempotent_set = BasicSet::new(vec![0, 1, 2]).unwrap();
    assert!(idempotent_set.is_idempotent());
    assert!(!set.is_idempotent());
}
