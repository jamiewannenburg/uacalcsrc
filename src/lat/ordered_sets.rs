/// Static algorithms for ordered sets and lattices.
/// 
/// This module provides utility functions for working with partially ordered sets,
/// including finding maximal elements according to a given order relation.

use super::Order;

/// Find all maximal elements in a collection according to the given order relation.
/// 
/// An element is maximal if there is no other element in the collection that is
/// strictly greater than it according to the order relation.
/// 
/// # Arguments
/// * `elems` - The collection of elements to search
/// * `order` - The order relation implementing the `Order` trait
/// 
/// # Returns
/// A vector containing all maximal elements from the input collection
/// 
/// # Examples
/// 
/// ```
/// use uacalc::lat::{ordered_sets, DivisibilityOrder};
/// 
/// let numbers = vec![2, 3, 6, 35, 175];
/// let order = DivisibilityOrder;
/// let maxs = ordered_sets::maximals(&numbers, &order);
/// // Result should contain [6, 175] since they are not divisors of any other element
/// assert!(maxs.contains(&6));
/// assert!(maxs.contains(&175));
/// assert!(!maxs.contains(&2));  // 2 divides 6
/// assert!(!maxs.contains(&35)); // 35 divides 175
/// ```
pub fn maximals<T, O>(elems: &[T], order: &O) -> Vec<T>
where
    T: Clone,
    O: Order<T>,
{
    let mut ans = Vec::new();
    
    for candidate in elems {
        let mut candidate_below = false;
        let mut new_ans = Vec::new();
        
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
    }
    
    ans
}

/// Test the maximals function with integer divisibility order.
/// 
/// This demonstrates the usage of the maximals function with a divisibility
/// order where a ≤ b if b is divisible by a.
pub fn main() {
    let lst = vec![2, 3, 6, 35, 35 * 5];
    
    // Define divisibility order where a ≤ b if b % a == 0
    struct DivOrder;
    impl Order<i32> for DivOrder {
        fn leq(&self, a: &i32, b: &i32) -> bool {
            if *a == 0 { return true; }  // 0 divides everything by convention
            if *b == 0 { return *a == 0; }
            *a != 0 && *b % *a == 0
        }
    }
    
    let order = DivOrder;
    let maxs = maximals(&lst, &order);
    
    println!("max's are {:?}", maxs);
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::lat::DivisibilityOrder;

    #[test]
    fn test_maximals_divisibility() {
        let numbers = vec![2, 3, 6, 35, 175];
        let order = DivisibilityOrder;
        let maxs = maximals(&numbers, &order);
        
        // 6 should be maximal (not a divisor of 35 or 175)
        // 175 should be maximal (not a divisor of anything else)
        // 2, 3, 35 should not be maximal
        assert!(maxs.contains(&6));
        assert!(maxs.contains(&175));
        assert_eq!(maxs.len(), 2);
    }

    #[test]
    fn test_maximals_empty() {
        let empty: Vec<i32> = vec![];
        let order = DivisibilityOrder;
        let maxs = maximals(&empty, &order);
        assert!(maxs.is_empty());
    }

    #[test]
    fn test_maximals_single() {
        let single = vec![42];
        let order = DivisibilityOrder;
        let maxs = maximals(&single, &order);
        assert_eq!(maxs, vec![42]);
    }

    #[test]
    fn test_maximals_all_incomparable() {
        // Prime numbers are incomparable under divisibility
        let primes = vec![2, 3, 5, 7];
        let order = DivisibilityOrder;
        let maxs = maximals(&primes, &order);
        assert_eq!(maxs.len(), 4);
        for prime in &primes {
            assert!(maxs.contains(prime));
        }
    }
}