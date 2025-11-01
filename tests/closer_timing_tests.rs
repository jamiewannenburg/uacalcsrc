/*!
 * Tests for CloserTiming that verify compatibility with Java implementation.
 */

use uacalc::alg::CloserTiming;

#[test]
fn test_ms_to_string_compatibility() {
    // Test various time values - these match the Java implementation
    let test_cases = vec![
        (5000u64, "5"),
        (65000u64, "1:05"),
        (3665000u64, "1:01:05"),
        (125000u64, "2:05"),
        (0u64, "0"),
        (59999u64, "59"),
        (60000u64, "1:00"),
        (3600000u64, "1:00:00"),
    ];
    
    for (ms, expected) in test_cases {
        let rust_result = CloserTiming::ms_to_string(ms);
        assert_eq!(rust_result, expected, "ms_to_string({}) should be '{}' but got '{}'", ms, expected, rust_result);
    }
}

#[test]
fn test_update_pass_compatibility() {
    use uacalc::alg::{CloserTiming, BigProductAlgebra, BasicSmallAlgebra};
    use std::collections::HashSet;
    
    // Create a simple product algebra for testing
    let alg1 = Box::new(BasicSmallAlgebra::new(
        "A1".to_string(),
        HashSet::from([0, 1]),
        Vec::new()
    )) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    
    let alg2 = Box::new(BasicSmallAlgebra::new(
        "A2".to_string(),
        HashSet::from([0, 1]),
        Vec::new()
    )) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    
    let product = BigProductAlgebra::<i32>::new_safe(vec![alg1, alg2]).unwrap();
    let mut timing = CloserTiming::new_from_algebra(&product, None);
    
    timing.update_pass(10);
    assert_eq!(timing.get_pass(), 1);
    
    timing.update_pass(20);
    assert_eq!(timing.get_pass(), 2);
}

#[test]
fn test_increment_next_pass_size_compatibility() {
    use uacalc::alg::{CloserTiming, BigProductAlgebra, BasicSmallAlgebra};
    use std::collections::HashSet;
    let alg1 = Box::new(BasicSmallAlgebra::new(
        "A1".to_string(),
        HashSet::from([0, 1]),
        Vec::new()
    )) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    
    let product = BigProductAlgebra::<i32>::new_safe(vec![alg1]).unwrap();
    let timing = CloserTiming::new_from_algebra(&product, None);
    
    // Test incrementing - we can't access private field directly, so just verify it doesn't panic
    timing.increment_next_pass_size();
    timing.increment_next_pass_size();
    // If we get here without panic, the increments worked
}

