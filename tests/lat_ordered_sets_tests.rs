use serde_json::json;
use uacalc::lat::ordered_sets;
use uacalc::lat::DivisibilityOrder;
use uacalc::common::{TestConfig, compare_outputs, run_java_cli_with_timeout};
use uacalc::compare_with_java;

#[test]
fn test_maximals_divisibility_basic() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.lat.OrderedSetsWrapper",
        ["maximals", "--elements", "2,3,6,35,175", "--order", "divisibility"],
        || {
            let elements = vec![2, 3, 6, 35, 175];
            let order = DivisibilityOrder;
            let result = ordered_sets::maximals(&elements, &order);
            json!({
                "command": "maximals",
                "elements": elements,
                "order": "divisibility",
                "status": result
            })
        }
    );
}

#[test]
fn test_maximals_divisibility_empty() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.lat.OrderedSetsWrapper",
        ["maximals", "--elements", "", "--order", "divisibility"],
        || {
            let elements: Vec<i32> = vec![];
            let order = DivisibilityOrder;
            let result = ordered_sets::maximals(&elements, &order);
            json!({
                "command": "maximals",
                "elements": elements,
                "order": "divisibility",
                "status": result
            })
        }
    );
}

#[test]
fn test_maximals_divisibility_single() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.lat.OrderedSetsWrapper",
        ["maximals", "--elements", "42", "--order", "divisibility"],
        || {
            let elements = vec![42];
            let order = DivisibilityOrder;
            let result = ordered_sets::maximals(&elements, &order);
            json!({
                "command": "maximals",
                "elements": elements,
                "order": "divisibility",
                "status": result
            })
        }
    );
}

#[test]
fn test_maximals_natural_order() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.lat.OrderedSetsWrapper",
        ["maximals", "--elements", "1,2,3,4,5", "--order", "natural"],
        || {
            let elements = vec![1, 2, 3, 4, 5];
            
            // Natural order implementation
            struct NaturalOrder;
            impl uacalc::lat::Order<i32> for NaturalOrder {
                fn leq(&self, a: &i32, b: &i32) -> bool {
                    a <= b
                }
            }
            
            let order = NaturalOrder;
            let result = ordered_sets::maximals(&elements, &order);
            json!({
                "command": "maximals",
                "elements": elements,
                "order": "natural",
                "status": result
            })
        }
    );
}

#[test]
fn test_maximals_primes() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.lat.OrderedSetsWrapper",
        ["maximals", "--elements", "2,3,5,7,11", "--order", "divisibility"],
        || {
            let elements = vec![2, 3, 5, 7, 11];
            let order = DivisibilityOrder;
            let result = ordered_sets::maximals(&elements, &order);
            json!({
                "command": "maximals",
                "elements": elements,
                "order": "divisibility",
                "status": result
            })
        }
    );
}

#[test]
fn test_main_method() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.lat.OrderedSetsWrapper",
        ["main"],
        || {
            let lst = vec![2, 3, 6, 35, 35 * 5];
            
            // Replicate the main method divisibility order
            struct DivOrder;
            impl uacalc::lat::Order<i32> for DivOrder {
                fn leq(&self, a: &i32, b: &i32) -> bool {
                    if *a == 0 { return true; }  // 0 divides everything by convention
                    if *b == 0 { return *a == 0; }
                    *a != 0 && *b % *a == 0
                }
            }
            
            let order = DivOrder;
            let maxs = ordered_sets::maximals(&lst, &order);
            
            json!({
                "command": "main",
                "input": lst,
                "status": maxs,
                "message": format!("max's are {:?}", maxs)
            })
        }
    );
}

#[test]
fn test_maximals_complex_divisibility() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.lat.OrderedSetsWrapper",
        ["maximals", "--elements", "1,2,4,8,3,6,12,5,10,20", "--order", "divisibility"],
        || {
            let elements = vec![1, 2, 4, 8, 3, 6, 12, 5, 10, 20];
            let order = DivisibilityOrder;
            let result = ordered_sets::maximals(&elements, &order);
            json!({
                "command": "maximals",
                "elements": elements,
                "order": "divisibility",
                "status": result
            })
        }
    );
}