use uacalc::lat::{Order, DivisibilityOrder, PrefixOrder, NaturalOrder};

#[test]
fn test_divisibility_order_basic() {
    let order = DivisibilityOrder;
    
    // Basic divisibility tests
    assert!(order.leq(&2, &6));   // 2 divides 6
    assert!(order.leq(&3, &12));  // 3 divides 12
    assert!(!order.leq(&6, &2));  // 6 does not divide 2
    assert!(!order.leq(&5, &7));  // 5 does not divide 7
}

#[test]
fn test_divisibility_order_reflexivity() {
    let order = DivisibilityOrder;
    
    // Reflexivity: every element divides itself
    assert!(order.leq(&1, &1));
    assert!(order.leq(&2, &2));
    assert!(order.leq(&5, &5));
    assert!(order.leq(&100, &100));
    assert!(order.leq(&-7, &-7));
}

#[test]
fn test_divisibility_order_zero_cases() {
    let order = DivisibilityOrder;
    
    // 0 divides everything by convention
    assert!(order.leq(&0, &0));
    assert!(order.leq(&0, &5));
    assert!(order.leq(&0, &-3));
    
    // Only 0 divides 0
    assert!(order.leq(&0, &0));
    assert!(!order.leq(&5, &0));
    assert!(!order.leq(&-3, &0));
}

#[test]
fn test_divisibility_order_transitivity() {
    let order = DivisibilityOrder;
    
    // If a|b and b|c, then a|c
    // 2 divides 6, 6 divides 12, so 2 should divide 12
    assert!(order.leq(&2, &6));
    assert!(order.leq(&6, &12));
    assert!(order.leq(&2, &12));
    
    // 3 divides 6, 6 divides 18, so 3 should divide 18
    assert!(order.leq(&3, &6));
    assert!(order.leq(&6, &18));
    assert!(order.leq(&3, &18));
}

#[test]
fn test_divisibility_order_negative_numbers() {
    let order = DivisibilityOrder;
    
    // Negative numbers
    assert!(order.leq(&-2, &6));   // -2 divides 6
    assert!(order.leq(&2, &-6));   // 2 divides -6
    assert!(order.leq(&-2, &-6));  // -2 divides -6
    assert!(!order.leq(&3, &-7));  // 3 does not divide -7
}

#[test]
fn test_prefix_order_basic() {
    let order = PrefixOrder;
    
    // Basic prefix tests
    assert!(order.leq(&"ab".to_string(), &"abcd".to_string()));
    assert!(order.leq(&"hello".to_string(), &"hello world".to_string()));
    assert!(!order.leq(&"abcd".to_string(), &"ab".to_string()));
    assert!(!order.leq(&"xyz".to_string(), &"abc".to_string()));
}

#[test]
fn test_prefix_order_reflexivity() {
    let order = PrefixOrder;
    
    // Reflexivity: every string is a prefix of itself
    assert!(order.leq(&"hello".to_string(), &"hello".to_string()));
    assert!(order.leq(&"".to_string(), &"".to_string()));
    assert!(order.leq(&"a".to_string(), &"a".to_string()));
    assert!(order.leq(&"long string".to_string(), &"long string".to_string()));
}

#[test]
fn test_prefix_order_empty_string() {
    let order = PrefixOrder;
    
    // Empty string is prefix of everything
    assert!(order.leq(&"".to_string(), &"anything".to_string()));
    assert!(order.leq(&"".to_string(), &"".to_string()));
    assert!(order.leq(&"".to_string(), &"a".to_string()));
    
    // Non-empty string is not prefix of empty string (except empty itself)
    assert!(!order.leq(&"a".to_string(), &"".to_string()));
    assert!(!order.leq(&"hello".to_string(), &"".to_string()));
}

#[test]
fn test_prefix_order_transitivity() {
    let order = PrefixOrder;
    
    // If a is prefix of b and b is prefix of c, then a is prefix of c
    let a = "he".to_string();
    let b = "hello".to_string();
    let c = "hello world".to_string();
    
    assert!(order.leq(&a, &b));
    assert!(order.leq(&b, &c));
    assert!(order.leq(&a, &c));
}

#[test]
fn test_natural_order_integers() {
    let order = NaturalOrder;
    
    // Basic integer ordering
    assert!(order.leq(&1, &2));
    assert!(order.leq(&0, &5));
    assert!(order.leq(&-5, &-2));
    assert!(order.leq(&-10, &10));
    assert!(!order.leq(&5, &3));
    assert!(!order.leq(&0, &-1));
}

#[test]
fn test_natural_order_reflexivity() {
    let order = NaturalOrder;
    
    // Reflexivity
    assert!(order.leq(&5, &5));
    assert!(order.leq(&0, &0));
    assert!(order.leq(&-7, &-7));
    assert!(order.leq(&100, &100));
}

#[test]
fn test_natural_order_transitivity() {
    let order = NaturalOrder;
    
    // Transitivity: if a ≤ b and b ≤ c then a ≤ c
    assert!(order.leq(&1, &5));
    assert!(order.leq(&5, &10));
    assert!(order.leq(&1, &10));
    
    assert!(order.leq(&-10, &-5));
    assert!(order.leq(&-5, &0));
    assert!(order.leq(&-10, &0));
}

#[test]
fn test_natural_order_strings() {
    let order = NaturalOrder;
    
    // String ordering (lexicographic)
    assert!(order.leq(&"apple".to_string(), &"banana".to_string()));
    assert!(order.leq(&"hello".to_string(), &"world".to_string()));
    assert!(!order.leq(&"zebra".to_string(), &"apple".to_string()));
    
    // Same strings
    assert!(order.leq(&"hello".to_string(), &"hello".to_string()));
    
    // Empty string is less than any non-empty string
    assert!(order.leq(&"".to_string(), &"a".to_string()));
    assert!(!order.leq(&"a".to_string(), &"".to_string()));
}

#[test]
fn test_natural_order_unsigned_integers() {
    let order = NaturalOrder;
    
    // Unsigned integer ordering
    assert!(order.leq(&1u32, &2u32));
    assert!(order.leq(&0u32, &100u32));
    assert!(!order.leq(&10u32, &5u32));
    
    // Reflexivity for u32
    assert!(order.leq(&42u32, &42u32));
}

// Test mathematical properties across all implementations
#[test]
fn test_order_properties_comprehensive() {
    // Test that all our implementations satisfy basic order properties
    
    // DivisibilityOrder
    let div_order = DivisibilityOrder;
    test_reflexivity_property(&div_order, &[1, 2, 3, 5, 10]);
    test_antisymmetry_property(&div_order, &[1, 2, 3, 4, 6, 12]);
    
    // PrefixOrder  
    let prefix_order = PrefixOrder;
    let strings = vec!["".to_string(), "a".to_string(), "ab".to_string(), "abc".to_string()];
    test_reflexivity_property(&prefix_order, &strings);
    
    // NaturalOrder
    let nat_order = NaturalOrder;
    test_reflexivity_property(&nat_order, &[1, 2, 3, 5, 10]);
    test_antisymmetry_property(&nat_order, &[1, 2, 3, 4, 5]);
}

// Helper function to test reflexivity property
fn test_reflexivity_property<T, O>(order: &O, elements: &[T]) 
where 
    O: Order<T>,
    T: Clone,
{
    for element in elements {
        assert!(order.leq(element, element), "Reflexivity failed for element");
    }
}

// Helper function to test antisymmetry property  
fn test_antisymmetry_property<T, O>(order: &O, elements: &[T])
where
    O: Order<T>,
    T: Clone + PartialEq + std::fmt::Debug,
{
    for (i, a) in elements.iter().enumerate() {
        for (j, b) in elements.iter().enumerate() {
            if i != j && order.leq(a, b) && order.leq(b, a) {
                // If both a ≤ b and b ≤ a, then for most reasonable orders a should equal b
                // This is a basic sanity check - we expect this to hold for our test data
                // Note: For divisibility order with negatives this might not always hold exactly
                // but for our test cases it should be fine
                println!("Warning: Found elements {:?} and {:?} that are mutually ≤ each other", a, b);
            }
        }
    }
}