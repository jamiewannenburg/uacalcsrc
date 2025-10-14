//! Order trait definition.
//!
//! This module defines the Order trait which represents a binary relation
//! that can be used to compare elements of a type.

/// A trait representing an order relation on elements of type `T`.
/// 
/// This trait corresponds to the Java `Order<E>` interface and provides
/// a way to define order relations for use with ordered set algorithms.
/// 
/// # Examples
/// 
/// ```
/// use uacalc_core::lat::Order;
/// 
/// struct DivisibilityOrder;
/// 
/// impl Order<i32> for DivisibilityOrder {
///     fn leq(&self, a: &i32, b: &i32) -> bool {
///         a % b == 0
///     }
/// }
/// 
/// let order = DivisibilityOrder;
/// assert!(order.leq(&6, &2)); // 6 is divisible by 2
/// assert!(!order.leq(&2, &6)); // 2 is not divisible by 6
/// ```
pub trait Order<T> {
    /// Returns true if `a` is less than or equal to `b` according to this order.
    /// 
    /// # Arguments
    /// * `a` - The first element to compare
    /// * `b` - The second element to compare
    /// 
    /// # Returns
    /// `true` if `a ≤ b` according to this order relation, `false` otherwise
    fn leq(&self, a: &T, b: &T) -> bool;
}

/// Implementation of Order for function types to allow closures
impl<T, F> Order<T> for F
where
    F: Fn(&T, &T) -> bool,
{
    fn leq(&self, a: &T, b: &T) -> bool {
        self(a, b)
    }
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
    fn test_divisibility_order() {
        let order = DivisibilityOrder;
        assert!(order.leq(&6, &2));
        assert!(order.leq(&35, &5));
        assert!(!order.leq(&2, &6));
        assert!(!order.leq(&5, &35));
    }

    #[test]
    fn test_order_with_closure() {
        let divisibility_order = |a: &i32, b: &i32| a % b == 0;
        assert!(divisibility_order.leq(&6, &2));
        assert!(!divisibility_order.leq(&2, &6));
    }
}