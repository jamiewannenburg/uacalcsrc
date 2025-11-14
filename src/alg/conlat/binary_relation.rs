/*! BinaryRelation trait for binary relations on finite sets.

This module defines the core trait for binary relations, providing a flexible
interface that can be implemented by various concrete types like BasicBinaryRelation
and Partition.

The trait is based on the Java `org.uacalc.alg.conlat.BinaryRelation` interface.
*/

use std::collections::BTreeSet;
use std::cmp::Ordering;
use crate::util::int_array::{IntArray, IntArrayTrait};

/// A binary relation on a finite set {0, 1, ..., n-1}.
/// 
/// This trait defines the core operations for binary relations, including
/// checking if elements are related, getting all pairs, and composing relations.
/// It provides flexibility with types while maintaining the core functionality
/// of the Java interface.
/// 
/// # Type Parameters
/// * `T` - The type used to represent pairs (typically `IntArray`)
/// 
/// # Examples
/// ```
/// use uacalc::alg::conlat::{BinaryRelation, BasicBinaryRelation, MutableBinaryRelation};
/// 
/// let mut relation = BasicBinaryRelation::new(3).unwrap();
/// relation.add(0, 1).unwrap();
/// relation.add(1, 2).unwrap();
/// 
/// assert!(relation.is_related(0, 1));
/// assert!(!relation.is_related(0, 2));
/// assert_eq!(relation.universe_size(), 3);
/// ```
pub trait BinaryRelation<T = IntArray> 
where
    T: IntArrayTrait + Clone + Ord + std::fmt::Debug,
{
    /// Get the size of the universe (the set {0, 1, ..., n-1}).
    /// 
    /// # Returns
    /// The size of the universe
    fn universe_size(&self) -> usize;
    
    /// Check if element `i` is related to element `j`.
    /// 
    /// # Arguments
    /// * `i` - The first element
    /// * `j` - The second element
    /// 
    /// # Returns
    /// `true` if `i` is related to `j`, `false` otherwise
    /// 
    /// # Panics
    /// May panic if `i` or `j` is greater than or equal to `universe_size()`
    fn is_related(&self, i: usize, j: usize) -> bool;
    
    /// Get all pairs in the relation as a sorted set.
    /// 
    /// # Returns
    /// A `BTreeSet` containing all pairs in the relation
    fn get_pairs(&self) -> BTreeSet<T>;
    
    /// Compose this relation with another relation.
    /// 
    /// The composition R ∘ S is defined as:
    /// (a, c) ∈ R ∘ S if and only if there exists b such that (a, b) ∈ R and (b, c) ∈ S
    /// 
    /// # Arguments
    /// * `other` - The other relation to compose with
    /// 
    /// # Returns
    /// A new relation representing the composition
    /// 
    /// # Errors
    /// Returns an error if the relations have incompatible universe sizes
    fn compose(&self, other: &dyn BinaryRelation<T>) -> Result<Box<dyn BinaryRelation<T>>, String>;
    
    /// Check if the relation is reflexive.
    /// 
    /// A relation is reflexive if (a, a) ∈ R for all a in the universe.
    /// 
    /// # Returns
    /// `true` if the relation is reflexive, `false` otherwise
    fn is_reflexive(&self) -> bool {
        for i in 0..self.universe_size() {
            if !self.is_related(i, i) {
                return false;
            }
        }
        true
    }
    
    /// Check if the relation is symmetric.
    /// 
    /// A relation is symmetric if (a, b) ∈ R implies (b, a) ∈ R for all a, b.
    /// 
    /// # Returns
    /// `true` if the relation is symmetric, `false` otherwise
    fn is_symmetric(&self) -> bool {
        for pair in self.get_pairs() {
            let i = pair.get(0).unwrap() as usize;
            let j = pair.get(1).unwrap() as usize;
            if !self.is_related(j, i) {
                return false;
            }
        }
        true
    }
    
    /// Check if the relation is transitive.
    /// 
    /// A relation is transitive if (a, b) ∈ R and (b, c) ∈ R implies (a, c) ∈ R for all a, b, c.
    /// 
    /// # Returns
    /// `true` if the relation is transitive, `false` otherwise
    fn is_transitive(&self) -> bool {
        for pair1 in self.get_pairs() {
            let i = pair1.get(0).unwrap() as usize;
            let j = pair1.get(1).unwrap() as usize;
            
            for pair2 in self.get_pairs() {
                if pair2.get(0).unwrap() as usize == j {
                    let k = pair2.get(1).unwrap() as usize;
                    if !self.is_related(i, k) {
                        return false;
                    }
                }
            }
        }
        true
    }
    
    /// Check if the relation is an equivalence relation.
    /// 
    /// An equivalence relation is reflexive, symmetric, and transitive.
    /// 
    /// # Returns
    /// `true` if the relation is an equivalence relation, `false` otherwise
    fn is_equivalence(&self) -> bool {
        self.is_reflexive() && self.is_symmetric() && self.is_transitive()
    }
}

/// Trait for binary relations that can be modified by adding pairs.
/// 
/// This trait extends `BinaryRelation` with the ability to add new pairs
/// to the relation.
/// 
/// # Type Parameters
/// * `T` - The type used to represent pairs (typically `IntArray`)
pub trait MutableBinaryRelation<T = IntArray>: BinaryRelation<T>
where
    T: IntArrayTrait + Clone + Ord + std::fmt::Debug,
{
    /// Add a pair (i, j) to the relation.
    /// 
    /// # Arguments
    /// * `i` - The first element
    /// * `j` - The second element
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully added the pair
    /// * `Err(String)` - If the indices are out of bounds
    fn add(&mut self, i: usize, j: usize) -> Result<(), String>;
    
    /// Remove a pair (i, j) from the relation.
    /// 
    /// # Arguments
    /// * `i` - The first element
    /// * `j` - The second element
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully removed the pair (or pair was not present)
    /// * `Err(String)` - If the indices are out of bounds
    fn remove(&mut self, i: usize, j: usize) -> Result<(), String>;
}

/// Comparison trait for binary relations.
/// 
/// This trait provides a way to compare binary relations, typically by
/// the number of pairs they contain.
/// 
/// # Type Parameters
/// * `T` - The type used to represent pairs (typically `IntArray`)
pub trait BinaryRelationCompare<T = IntArray>: BinaryRelation<T>
where
    T: IntArrayTrait + Clone + Ord + std::fmt::Debug,
{
    /// Compare this relation with another relation.
    /// 
    /// The default implementation compares by the number of pairs.
    /// 
    /// # Arguments
    /// * `other` - The other relation to compare with
    /// 
    /// # Returns
    /// * `Ordering::Less` - If this relation has fewer pairs
    /// * `Ordering::Equal` - If both relations have the same number of pairs
    /// * `Ordering::Greater` - If this relation has more pairs
    fn compare(&self, other: &dyn BinaryRelation<T>) -> Ordering {
        self.get_pairs().len().cmp(&other.get_pairs().len())
    }
}

/// Iterator trait for binary relations.
/// 
/// This trait provides iteration over the pairs in a binary relation,
/// equivalent to Java's `Iterable<IntArray>`.
/// 
/// # Type Parameters
/// * `T` - The type used to represent pairs (typically `IntArray`)
pub trait BinaryRelationIterator<T = IntArray>
where
    T: IntArrayTrait + Clone + Ord + std::fmt::Debug,
{
    /// Get an iterator over the pairs in the relation.
    /// 
    /// # Returns
    /// An iterator over the pairs
    fn pairs(&self) -> std::collections::btree_set::IntoIter<T>;
}

/// Factory trait for creating binary relations.
/// 
/// This trait provides static methods for creating common binary relations.
pub trait BinaryRelationFactory<T = IntArray>
where
    T: IntArrayTrait + Clone + Ord + std::fmt::Debug,
{
    /// Create the identity relation on a set of given size.
    /// 
    /// The identity relation contains all pairs (i, i) for i in {0, 1, ..., n-1}.
    /// 
    /// # Arguments
    /// * `size` - The size of the universe
    /// 
    /// # Returns
    /// * `Ok(Box<dyn BinaryRelation<T>>)` - The identity relation
    /// * `Err(String)` - If the size is invalid
    fn identity(size: usize) -> Result<Box<dyn BinaryRelation<T>>, String>;
    
    /// Create the universal relation on a set of given size.
    /// 
    /// The universal relation contains all possible pairs (i, j) for i, j in {0, 1, ..., n-1}.
    /// 
    /// # Arguments
    /// * `size` - The size of the universe
    /// 
    /// # Returns
    /// * `Ok(Box<dyn BinaryRelation<T>>)` - The universal relation
    /// * `Err(String)` - If the size is invalid
    fn universal(size: usize) -> Result<Box<dyn BinaryRelation<T>>, String>;
    
    /// Create the empty relation on a set of given size.
    /// 
    /// The empty relation contains no pairs.
    /// 
    /// # Arguments
    /// * `size` - The size of the universe
    /// 
    /// # Returns
    /// * `Ok(Box<dyn BinaryRelation<T>>)` - The empty relation
    /// * `Err(String)` - If the size is invalid
    fn empty(size: usize) -> Result<Box<dyn BinaryRelation<T>>, String>;
}
