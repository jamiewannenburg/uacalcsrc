/// A partial order relation on elements of type E.
/// 
/// This trait defines the "less than or equal to" relation (≤) for elements.
/// Implementations must satisfy the mathematical properties of a partial order:
/// 
/// - **Reflexivity**: `leq(a, a) == true` for all a
/// - **Antisymmetry**: if `leq(a, b) && leq(b, a)` then `a == b`
/// - **Transitivity**: if `leq(a, b) && leq(b, c)` then `leq(a, c)`
/// 
/// # Examples
/// 
/// ## Integer divisibility order
/// ```
/// use uacalc::lat::Order;
/// 
/// struct DivisibilityOrder;
/// 
/// impl Order<i32> for DivisibilityOrder {
///     fn leq(&self, a: &i32, b: &i32) -> bool {
///         if *a == 0 { return true; }  // 0 divides everything by convention
///         if *b == 0 { return *a == 0; }
///         b % a == 0
///     }
/// }
/// 
/// let order = DivisibilityOrder;
/// assert!(order.leq(&2, &6));   // 2 divides 6
/// assert!(!order.leq(&6, &2));  // 6 does not divide 2
/// assert!(order.leq(&3, &3));   // 3 divides itself (reflexivity)
/// ```
/// 
/// ## String prefix order
/// ```
/// use uacalc::lat::Order;
/// 
/// struct PrefixOrder;
/// 
/// impl Order<String> for PrefixOrder {
///     fn leq(&self, a: &String, b: &String) -> bool {
///         b.starts_with(a)
///     }
/// }
/// 
/// let order = PrefixOrder;
/// assert!(order.leq(&"ab".to_string(), &"abcd".to_string()));
/// assert!(!order.leq(&"abcd".to_string(), &"ab".to_string()));
/// ```
pub trait Order<E> {
    /// Returns true if a ≤ b in this order relation.
    /// 
    /// # Arguments
    /// * `a` - The first element
    /// * `b` - The second element
    /// 
    /// # Returns
    /// `true` if a ≤ b according to this order relation, `false` otherwise
    fn leq(&self, a: &E, b: &E) -> bool;
}

pub struct BasicLattice {
    // TODO: Implement basic lattice
}

pub struct Lattice {
    // TODO: Implement lattice
}

pub struct Lattices {
    // TODO: Implement lattices collection
}

pub mod ordered_sets;

pub struct SmallLattice {
    // TODO: Implement small lattice
}

// Example implementations for testing
#[derive(Debug, Clone)]
pub struct DivisibilityOrder;

impl Order<i32> for DivisibilityOrder {
    fn leq(&self, a: &i32, b: &i32) -> bool {
        if *a == 0 { return true; }  // 0 divides everything by convention
        if *b == 0 { return *a == 0; }
        *a != 0 && *b % *a == 0
    }
}

#[derive(Debug, Clone)]
pub struct PrefixOrder;

impl Order<String> for PrefixOrder {
    fn leq(&self, a: &String, b: &String) -> bool {
        b.starts_with(a)
    }
}

#[derive(Debug, Clone)]
pub struct NaturalOrder;

impl Order<i32> for NaturalOrder {
    fn leq(&self, a: &i32, b: &i32) -> bool {
        a <= b
    }
}

impl Order<u32> for NaturalOrder {
    fn leq(&self, a: &u32, b: &u32) -> bool {
        a <= b
    }
}

impl Order<String> for NaturalOrder {
    fn leq(&self, a: &String, b: &String) -> bool {
        a <= b
    }
}
