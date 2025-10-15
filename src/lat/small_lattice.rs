use crate::lat::Lattice;

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