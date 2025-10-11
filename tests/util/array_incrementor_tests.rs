use uacalc::util::array_incrementor::{ArrayIncrementor, SimpleArrayIncrementor};
use uacalc::common::*;
use uacalc::compare_with_java;
use serde_json::json;

#[test]
fn test_new() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.ArrayIncrementorWrapper",
        ["test"],
        || {
            let mut arr = vec![0, 1, 2];
            let incrementor = SimpleArrayIncrementor::new(&mut arr);
            json!({
                "command": "test",
                "status": "created"
            })
        }
    );
}

#[test]
fn test_new_with_max_values() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.ArrayIncrementorWrapper",
        ["test"],
        || {
            let mut arr = vec![0, 0, 0];
            let max_vals = vec![1, 2, 1];
            let incrementor = SimpleArrayIncrementor::new_with_max_values(&mut arr, max_vals).unwrap();
            json!({
                "command": "test",
                "status": "created_with_max_values"
            })
        }
    );
}

#[test]
fn test_increment_basic() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.ArrayIncrementorWrapper",
        ["array_incrementor", "--array", "0,1,2"],
        || {
            let mut arr = vec![0, 1, 2];
            let mut incrementor = SimpleArrayIncrementor::new(&mut arr);
            
            let mut results = Vec::new();
            results.push(incrementor.get_array().to_vec());
            
            while incrementor.increment() {
                results.push(incrementor.get_array().to_vec());
            }
            
            json!({
                "command": "array_incrementor",
                "input_array": "[0, 1, 2]",
                "total_permutations": results.len(),
                "results": results
            })
        }
    );
}

#[test]
fn test_increment_with_custom_max() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.ArrayIncrementorWrapper",
        ["test"],
        || {
            let mut arr = vec![0, 0, 0];
            let max_vals = vec![1, 2, 1];
            let mut incrementor = SimpleArrayIncrementor::new_with_max_values(&mut arr, max_vals).unwrap();
            
            let mut results = Vec::new();
            results.push(incrementor.get_array().to_vec());
            
            while incrementor.increment() {
                results.push(incrementor.get_array().to_vec());
            }
            
            json!({
                "command": "test",
                "status": format!("Generated {} combinations", results.len())
            })
        }
    );
}

#[test]
fn test_increment_exhaustion() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.ArrayIncrementorWrapper",
        ["array_incrementor", "--array", "2,2,2"],
        || {
            let mut arr = vec![2, 2, 2];
            let mut incrementor = SimpleArrayIncrementor::new(&mut arr);
            
            let mut results = Vec::new();
            results.push(incrementor.get_array().to_vec());
            
            let mut count = 0;
            while incrementor.increment() {
                results.push(incrementor.get_array().to_vec());
                count += 1;
            }
            
            json!({
                "command": "array_incrementor",
                "input_array": "[2, 2, 2]",
                "total_permutations": results.len(),
                "increment_count": count
            })
        }
    );
}

#[test]
fn test_list_incrementor_comparison() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.util.ArrayIncrementorWrapper",
        ["list_incrementor", "--list", "a,b,c"],
        || {
            // Since we don't have a direct list incrementor in our SimpleArrayIncrementor,
            // we'll simulate it by using indices
            let mut arr = vec![0, 1, 2]; // indices for ["a", "b", "c"]
            let mut incrementor = SimpleArrayIncrementor::new(&mut arr);
            
            let mut results = Vec::new();
            results.push(incrementor.get_array().to_vec());
            
            while incrementor.increment() {
                results.push(incrementor.get_array().to_vec());
            }
            
            json!({
                "command": "list_incrementor",
                "input_list": ["a", "b", "c"],
                "total_permutations": results.len(),
                "results": results
            })
        }
    );
}

#[test]
fn test_error_handling() {
    let config = TestConfig::default();
    
    // Test invalid max values length
    let result = SimpleArrayIncrementor::new_with_max_values(&mut vec![0, 1], vec![2]);
    assert!(result.is_err());
    
    // Test invalid array values
    let result = SimpleArrayIncrementor::new_with_max_values(&mut vec![0, 3], vec![2, 2]);
    assert!(result.is_err());
    
    // Test valid case
    let result = SimpleArrayIncrementor::new_with_max_values(&mut vec![0, 1], vec![2, 2]);
    assert!(result.is_ok());
}

#[test]
fn test_edge_cases() {
    let config = TestConfig::default();
    
    // Test single element array
    let mut arr = vec![0];
    let mut incrementor = SimpleArrayIncrementor::new(&mut arr);
    
    let mut count = 0;
    while incrementor.increment() {
        count += 1;
    }
    
    assert_eq!(count, 0); // Single element should have no increments
    
    // Test empty array (should panic in constructor)
    // This is expected behavior - empty arrays don't make sense for incrementor
}

#[test]
fn test_display_and_hash() {
    let mut arr = vec![0, 1, 2];
    let incrementor1 = SimpleArrayIncrementor::new(&mut arr);
    let mut arr2 = vec![0, 1, 2];
    let incrementor2 = SimpleArrayIncrementor::new(&mut arr2);
    
    // Test display
    let display_str = format!("{}", incrementor1);
    assert!(display_str.contains("SimpleArrayIncrementor"));
    assert!(display_str.contains("[0, 1, 2]"));
    
    // Test hash consistency
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    
    let mut hasher1 = DefaultHasher::new();
    let mut hasher2 = DefaultHasher::new();
    
    incrementor1.hash(&mut hasher1);
    incrementor2.hash(&mut hasher2);
    
    assert_eq!(hasher1.finish(), hasher2.finish());
}
