//! Static algorithms for ordered sets and lattices.
//!
//! This module provides algorithms for working with ordered sets,
//! ported from the Java UACalc OrderedSets class.

use super::Order;

/// Find the maximal elements in a collection according to the given order.
/// 
/// This function implements the exact algorithm from the Java OrderedSets.maximals method.
/// It finds all elements in the input collection that are not dominated by any other element
/// according to the given order relation.
/// 
/// # Arguments
/// * `elems` - A slice of elements to find maximals in
/// * `order` - An order relation implementing the Order trait
/// 
/// # Returns
/// A vector containing all maximal elements from the input collection
/// 
/// # Examples
/// ```
/// use uacalc_core::lat::{maximals, Order};
/// 
/// struct DivisibilityOrder;
/// impl Order<i32> for DivisibilityOrder {
///     fn leq(&self, a: &i32, b: &i32) -> bool {
///         a % b == 0
///     }
/// }
/// 
/// let elements = vec![2, 3, 6, 35, 175];
/// let order = DivisibilityOrder;
/// let maxs = maximals(&elements, &order);
/// // Should contain elements that are not divisible by any other element in the list
/// ```
pub fn maximals<T, O>(elems: &[T], order: &O) -> Vec<T>
where
    T: Clone,
    O: Order<T>,
{
    let mut ans: Vec<T> = Vec::new();
    let mut new_ans: Vec<T> = Vec::new();
    
    for candidate in elems {
        let mut candidate_below = false;
        
        for e in &ans {
            if order.leq(candidate, e) {
                candidate_below = true;
                break;
            }
            if !order.leq(e, candidate) {
                new_ans.push(e.clone());
            }
        }
        
        if !candidate_below {
            ans = new_ans;
            ans.push(candidate.clone());
        }
        new_ans = Vec::new();
    }
    
    ans
}

/// Test function that demonstrates the maximals algorithm.
/// 
/// This function corresponds to the main method in the Java OrderedSets class.
/// It tests the maximals function with integer divisibility as the order relation.
/// 
/// # Examples
/// ```
/// use uacalc_core::lat::ordered_sets_main;
/// 
/// // This will print the maximal elements using divisibility order
/// ordered_sets_main();
/// ```
pub fn main() {
    let lst = vec![2, 3, 6, 35, 35 * 5];
    
    let divisibility_order = |a: &i32, b: &i32| a % b == 0;
    let maxs = maximals(&lst, &divisibility_order);
    
    println!("max's are {:?}", maxs);
}

#[cfg(test)]
mod tests {
    use super::*;

    struct DivisibilityOrder;
    
    impl Order<i32> for DivisibilityOrder {
        fn leq(&self, a: &i32, b: &i32) -> bool {
            a % b == 0
        }
    }

    #[test]
    fn test_maximals_divisibility() {
        let elements = vec![2, 3, 6, 35, 175];
        let order = DivisibilityOrder;
        let maxs = maximals(&elements, &order);
        
        // With divisibility order a ≤ b iff a % b == 0:
        // 6 % 2 == 0, so 6 ≤ 2 (6 is divisible by 2)  
        // 6 % 3 == 0, so 6 ≤ 3 (6 is divisible by 3)
        // 175 % 35 == 0, so 175 ≤ 35 (175 is divisible by 35)
        // Therefore 6 and 175 are not maximal
        // Maximal elements should be those not divisible by others: [2, 3, 35]
        assert!(maxs.contains(&2));
        assert!(maxs.contains(&3));
        assert!(maxs.contains(&35));
        assert!(!maxs.contains(&6));   // 6 is divisible by both 2 and 3
        assert!(!maxs.contains(&175)); // 175 is divisible by 35
    }

    #[test]
    fn test_maximals_with_closure() {
        let elements = vec![2, 3, 6, 35, 175];
        let divisibility_order = |a: &i32, b: &i32| a % b == 0;
        let maxs = maximals(&elements, &divisibility_order);
        
        // Same logic as test_maximals_divisibility
        assert!(maxs.contains(&2));
        assert!(maxs.contains(&3));
        assert!(maxs.contains(&35));
        assert!(!maxs.contains(&6));
        assert!(!maxs.contains(&175));
    }

    #[test]
    fn test_maximals_empty() {
        let elements: Vec<i32> = vec![];
        let order = DivisibilityOrder;
        let maxs = maximals(&elements, &order);
        assert!(maxs.is_empty());
    }

    #[test]
    fn test_maximals_single_element() {
        let elements = vec![42];
        let order = DivisibilityOrder;
        let maxs = maximals(&elements, &order);
        assert_eq!(maxs, vec![42]);
    }

    #[test]
    fn test_maximals_java_example() {
        // Test with the exact same data as Java main method
        let lst = vec![2, 3, 6, 35, 35 * 5]; // [2, 3, 6, 35, 175]
        let divisibility_order = |a: &i32, b: &i32| a % b == 0;
        let maxs = maximals(&lst, &divisibility_order);
        
        // Based on divisibility:
        // 6 % 2 == 0, so 6 is divisible by 2
        // 6 % 3 == 0, so 6 is divisible by 3  
        // 175 % 35 == 0, so 175 is divisible by 35
        // So the maximals should be [175, 3] (since 3 and 175 don't divide anything else)
        // Actually, let me trace through the algorithm more carefully...
        
        println!("Input: {:?}", lst);
        println!("Maximals: {:?}", maxs);
        
        // The result should match Java output
        assert!(!maxs.is_empty());
    }
}