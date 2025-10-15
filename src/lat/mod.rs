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

use crate::alg::algebra::Algebra;

/// A lattice is a partially ordered set with join and meet operations.
/// 
/// This trait defines the fundamental operations of lattice theory:
/// - Join (∨): least upper bound of two elements
/// - Meet (∧): greatest lower bound of two elements
/// - Special elements: atoms, coatoms, join/meet irreducibles
/// 
/// The trait extends both `Algebra` and `Order<E>` to provide algebraic structure
/// and ordering operations on the elements.
/// 
/// # Mathematical Properties
/// 
/// A lattice must satisfy the lattice laws:
/// 
/// ## Commutative Laws
/// - `join(a, b) == join(b, a)`
/// - `meet(a, b) == meet(b, a)`
/// 
/// ## Associative Laws
/// - `join(join(a, b), c) == join(a, join(b, c))`
/// - `meet(meet(a, b), c) == meet(a, meet(b, c))`
/// 
/// ## Absorption Laws
/// - `join(a, meet(a, b)) == a`
/// - `meet(a, join(a, b)) == a`
/// 
/// # Examples
/// 
/// ## Boolean lattice (2-element lattice)
/// ```
/// use uacalc::lat::{Lattice, Order};
/// use uacalc::alg::algebra::Algebra;
/// 
/// // Note: Full implementation would require implementing Algebra trait
/// // This is a conceptual example of how the trait would be used
/// ```
pub trait Lattice<E>: Algebra<UniverseItem = E> + Order<E> {
    /// Returns the list of join irreducible elements, if available.
    /// 
    /// A join irreducible element is one that cannot be expressed as the join
    /// of two strictly smaller elements. In finite lattices, every element
    /// can be expressed as a join of join irreducible elements.
    /// 
    /// # Returns
    /// * `Some(vec)` - List of join irreducible elements if computable
    /// * `None` - If join irreducibles are not available or not computable
    fn join_irreducibles(&self) -> Option<Vec<E>>;
    
    /// Returns the list of meet irreducible elements, if available.
    /// 
    /// A meet irreducible element is one that cannot be expressed as the meet
    /// of two strictly larger elements. These are dual to join irreducibles.
    /// 
    /// # Returns
    /// * `Some(vec)` - List of meet irreducible elements if computable
    /// * `None` - If meet irreducibles are not available or not computable
    fn meet_irreducibles(&self) -> Option<Vec<E>>;
    
    /// Returns the list of atoms (minimal non-zero elements).
    /// 
    /// An atom is an element that covers only the bottom element (if it exists).
    /// In a Boolean algebra, atoms are the generators of the algebra.
    /// 
    /// # Returns
    /// * `Some(vec)` - List of atoms if they exist and are computable
    /// * `None` - If atoms don't exist, are infinite, or not computable
    fn atoms(&self) -> Option<Vec<E>>;
    
    /// Returns the list of coatoms (maximal non-one elements).
    /// 
    /// A coatom is an element that is covered only by the top element (if it exists).
    /// Coatoms are dual to atoms.
    /// 
    /// # Returns
    /// * `Some(vec)` - List of coatoms if they exist and are computable
    /// * `None` - If coatoms don't exist, are infinite, or not computable
    fn coatoms(&self) -> Option<Vec<E>>;
    
    /// Returns the join (least upper bound) of two elements.
    /// 
    /// The join operation ∨ finds the smallest element that is greater than
    /// or equal to both input elements according to the lattice order.
    /// 
    /// # Arguments
    /// * `a` - First element
    /// * `b` - Second element
    /// 
    /// # Returns
    /// The join of a and b
    fn join(&self, a: &E, b: &E) -> E;
    
    /// Returns the join of a list of elements.
    /// 
    /// Computes the join (least upper bound) of all elements in the list.
    /// For an empty list, implementations may return the bottom element
    /// if one exists, or handle it as an error condition.
    /// 
    /// # Arguments
    /// * `args` - Slice of elements to join
    /// 
    /// # Returns
    /// The join of all elements in the list
    fn join_list(&self, args: &[E]) -> E;
    
    /// Returns the meet (greatest lower bound) of two elements.
    /// 
    /// The meet operation ∧ finds the largest element that is less than
    /// or equal to both input elements according to the lattice order.
    /// 
    /// # Arguments
    /// * `a` - First element
    /// * `b` - Second element
    /// 
    /// # Returns
    /// The meet of a and b
    fn meet(&self, a: &E, b: &E) -> E;
    
    /// Returns the meet of a list of elements.
    /// 
    /// Computes the meet (greatest lower bound) of all elements in the list.
    /// For an empty list, implementations may return the top element
    /// if one exists, or handle it as an error condition.
    /// 
    /// # Arguments
    /// * `args` - Slice of elements to meet
    /// 
    /// # Returns
    /// The meet of all elements in the list
    fn meet_list(&self, args: &[E]) -> E;
}

/// A small lattice is a finite lattice with indexed elements.
/// 
/// This trait extends the general `Lattice` trait with operations
/// specific to small finite lattices where elements can be indexed.
/// The main addition is the ability to get upper covers by index,
/// which is useful for efficient lattice computations.
/// 
/// # Index-Based Operations
/// 
/// Small lattices allow elements to be accessed by integer indices,
/// typically from 0 to size-1. This enables efficient algorithms
/// that work with array-based representations of the lattice.
/// 
/// # Examples
/// 
/// ## Diamond lattice (4-element lattice)
/// ```
/// use uacalc::lat::{SmallLattice, Lattice, Order};
/// use uacalc::alg::algebra::Algebra;
/// 
/// // Note: Full implementation would require implementing all parent traits
/// // This is a conceptual example showing the upper covers relationship
/// // In a diamond lattice with elements [⊥, a, b, ⊤]:
/// // - upper_covers_indices(0) -> [1, 2] (⊥ is covered by a and b)
/// // - upper_covers_indices(1) -> [3] (a is covered by ⊤)
/// // - upper_covers_indices(2) -> [3] (b is covered by ⊤)
/// // - upper_covers_indices(3) -> [] (⊤ has no upper covers)
/// ```
pub trait SmallLattice<E>: Lattice<E> {
    /// Returns the indices of the upper covers of the element at the given index.
    /// 
    /// An upper cover of an element x is an element y such that:
    /// 1. x < y (y is strictly greater than x)
    /// 2. There is no element z with x < z < y (y immediately covers x)
    /// 
    /// This method returns the indices (positions in the lattice ordering)
    /// of all such elements y for the element at position `index`.
    /// 
    /// # Arguments
    /// * `index` - The index of the element whose upper covers are requested
    /// 
    /// # Returns
    /// A vector of indices representing the upper covers of the element
    /// 
    /// # Panics
    /// May panic if `index` is out of bounds for the lattice
    fn upper_covers_indices(&self, index: usize) -> Vec<usize>;
}

pub struct BasicLattice {
    // TODO: Implement basic lattice
}

pub struct Lattices {
    // TODO: Implement lattices collection
}

pub mod ordered_sets;

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
