/*! BasicBinaryRelation implementation.

This module provides a concrete implementation of the BinaryRelation trait
using a BTreeSet to store pairs. This matches the Java implementation
of org.uacalc.alg.conlat.BasicBinaryRelation.
*/

use std::collections::BTreeSet;
use std::fmt;
use std::hash::{Hash, Hasher};
use crate::util::int_array::{IntArray, IntArrayTrait};
use super::binary_relation::{
    BinaryRelation, MutableBinaryRelation, BinaryRelationCompare, 
    BinaryRelationIterator, BinaryRelationFactory
};

/// A basic implementation of a binary relation using a BTreeSet for storage.
/// 
/// This struct provides a concrete implementation of the BinaryRelation trait,
/// storing pairs in a BTreeSet for efficient lookup and iteration. It matches
/// the behavior of the Java BasicBinaryRelation class.
/// 
/// # Examples
/// ```
/// use uacalc::alg::conlat::{BasicBinaryRelation, BinaryRelation, MutableBinaryRelation};
/// 
/// let mut relation = BasicBinaryRelation::new(3).unwrap();
/// relation.add(0, 1).unwrap();
/// relation.add(1, 2).unwrap();
/// 
/// assert!(relation.is_related(0, 1));
/// assert_eq!(relation.get_pairs().len(), 2);
/// ```
#[derive(Debug, Clone)]
pub struct BasicBinaryRelation {
    /// The pairs in the relation, stored as a sorted set
    pairs: BTreeSet<IntArray>,
    /// The size of the universe {0, 1, ..., univ_size-1}
    univ_size: usize,
}

impl BasicBinaryRelation {
    /// Create a new empty binary relation on a universe of given size.
    /// 
    /// # Arguments
    /// * `univ_size` - The size of the universe
    /// 
    /// # Returns
    /// * `Ok(BasicBinaryRelation)` - Successfully created relation
    /// * `Err(String)` - If the universe size is invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::{BasicBinaryRelation, BinaryRelation};
    /// 
    /// let relation = BasicBinaryRelation::new(5).unwrap();
    /// assert_eq!(relation.universe_size(), 5);
    /// assert!(relation.get_pairs().is_empty());
    /// ```
    pub fn new(univ_size: usize) -> Result<Self, String> {
        if univ_size == 0 {
            return Err("Universe size cannot be zero".to_string());
        }
        
        Ok(BasicBinaryRelation {
            pairs: BTreeSet::new(),
            univ_size,
        })
    }
    
    /// Create a new binary relation from a collection of pairs.
    /// 
    /// # Arguments
    /// * `pairs` - A collection of IntArray pairs
    /// * `univ_size` - The size of the universe
    /// 
    /// # Returns
    /// * `Ok(BasicBinaryRelation)` - Successfully created relation
    /// * `Err(String)` - If the universe size is invalid or pairs are out of bounds
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::{BasicBinaryRelation, BinaryRelation};
    /// use uacalc::util::int_array::IntArray;
    /// 
    /// let pairs = vec![
    ///     IntArray::from_array(vec![0, 1]).unwrap(),
    ///     IntArray::from_array(vec![1, 2]).unwrap(),
    /// ];
    /// let relation = BasicBinaryRelation::from_pairs(pairs, 3).unwrap();
    /// assert_eq!(relation.get_pairs().len(), 2);
    /// ```
    pub fn from_pairs(pairs: Vec<IntArray>, univ_size: usize) -> Result<Self, String> {
        if univ_size == 0 {
            return Err("Universe size cannot be zero".to_string());
        }
        
        let mut relation = BasicBinaryRelation {
            pairs: BTreeSet::new(),
            univ_size,
        };
        
        // Validate and add pairs
        for pair in pairs {
            if pair.universe_size() != 2 {
                return Err("Each pair must have exactly 2 elements".to_string());
            }
            
            let i = pair.get(0).unwrap() as usize;
            let j = pair.get(1).unwrap() as usize;
            
            if i >= univ_size || j >= univ_size {
                return Err(format!("Pair ({}, {}) is out of bounds for universe size {}", i, j, univ_size));
            }
            
            relation.pairs.insert(pair);
        }
        
        Ok(relation)
    }
    
    /// Create the identity relation on a set of given size.
    /// 
    /// The identity relation contains all pairs (i, i) for i in {0, 1, ..., n-1}.
    /// 
    /// # Arguments
    /// * `size` - The size of the universe
    /// 
    /// # Returns
    /// * `Ok(BasicBinaryRelation)` - The identity relation
    /// * `Err(String)` - If the size is invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::{BasicBinaryRelation, BinaryRelation};
    /// 
    /// let identity = BasicBinaryRelation::identity(3).unwrap();
    /// assert!(identity.is_related(0, 0));
    /// assert!(identity.is_related(1, 1));
    /// assert!(identity.is_related(2, 2));
    /// assert!(!identity.is_related(0, 1));
    /// assert_eq!(identity.get_pairs().len(), 3);
    /// ```
    pub fn identity(size: usize) -> Result<Self, String> {
        if size == 0 {
            return Err("Size cannot be zero".to_string());
        }
        
        let mut relation = BasicBinaryRelation::new(size)?;
        
        for i in 0..size {
            relation.add(i, i)?;
        }
        
        Ok(relation)
    }
    
    /// Create the universal relation on a set of given size.
    /// 
    /// The universal relation contains all possible pairs (i, j) for i, j in {0, 1, ..., n-1}.
    /// 
    /// # Arguments
    /// * `size` - The size of the universe
    /// 
    /// # Returns
    /// * `Ok(BasicBinaryRelation)` - The universal relation
    /// * `Err(String)` - If the size is invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::{BasicBinaryRelation, BinaryRelation};
    /// 
    /// let universal = BasicBinaryRelation::universal(2).unwrap();
    /// assert!(universal.is_related(0, 0));
    /// assert!(universal.is_related(0, 1));
    /// assert!(universal.is_related(1, 0));
    /// assert!(universal.is_related(1, 1));
    /// assert_eq!(universal.get_pairs().len(), 4);
    /// ```
    pub fn universal(size: usize) -> Result<Self, String> {
        if size == 0 {
            return Err("Size cannot be zero".to_string());
        }
        
        let mut relation = BasicBinaryRelation::new(size)?;
        
        for i in 0..size {
            for j in 0..size {
                relation.add(i, j)?;
            }
        }
        
        Ok(relation)
    }
    
    /// Create the empty relation on a set of given size.
    /// 
    /// The empty relation contains no pairs.
    /// 
    /// # Arguments
    /// * `size` - The size of the universe
    /// 
    /// # Returns
    /// * `Ok(BasicBinaryRelation)` - The empty relation
    /// * `Err(String)` - If the size is invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::{BasicBinaryRelation, BinaryRelation};
    /// 
    /// let empty = BasicBinaryRelation::empty(3).unwrap();
    /// assert!(!empty.is_related(0, 1));
    /// assert!(empty.get_pairs().is_empty());
    /// ```
    pub fn empty(size: usize) -> Result<Self, String> {
        BasicBinaryRelation::new(size)
    }
    
    /// Get the number of pairs in the relation.
    /// 
    /// # Returns
    /// The number of pairs
    pub fn size(&self) -> usize {
        self.pairs.len()
    }
    
    /// Check if the relation is empty (contains no pairs).
    /// 
    /// # Returns
    /// `true` if the relation is empty, `false` otherwise
    pub fn is_empty(&self) -> bool {
        self.pairs.is_empty()
    }
    
    /// Clear all pairs from the relation.
    pub fn clear(&mut self) {
        self.pairs.clear();
    }
    
    /// Get a string representation of the relation.
    /// 
    /// # Returns
    /// A string representation showing all pairs
    pub fn to_string(&self) -> String {
        format!("{:?}", self.pairs)
    }
}

impl BinaryRelation<IntArray> for BasicBinaryRelation {
    fn universe_size(&self) -> usize {
        self.univ_size
    }
    
    fn is_related(&self, i: usize, j: usize) -> bool {
        if i >= self.univ_size || j >= self.univ_size {
            return false;
        }
        
        let pair = IntArray::from_array(vec![i as i32, j as i32]).unwrap();
        self.pairs.contains(&pair)
    }
    
    fn get_pairs(&self) -> BTreeSet<IntArray> {
        self.pairs.clone()
    }
    
    fn compose(&self, other: &dyn BinaryRelation<IntArray>) -> Result<Box<dyn BinaryRelation<IntArray>>, String> {
        if self.universe_size() != other.universe_size() {
            return Err(format!(
                "Cannot compose relations with different universe sizes: {} and {}",
                self.universe_size(),
                other.universe_size()
            ));
        }
        
        let mut result = BasicBinaryRelation::new(self.universe_size())?;
        
        // For each pair (i, j) in this relation
        for pair in self.get_pairs() {
            let i = pair.get(0).unwrap() as usize;
            let j = pair.get(1).unwrap() as usize;
            
            // For each k in the universe
            for k in 0..self.universe_size() {
                // If (j, k) is in the other relation, add (i, k) to the result
                if other.is_related(j, k) {
                    result.add(i, k)?;
                }
            }
        }
        
        Ok(Box::new(result))
    }
}

impl MutableBinaryRelation<IntArray> for BasicBinaryRelation {
    fn add(&mut self, i: usize, j: usize) -> Result<(), String> {
        if i >= self.univ_size {
            return Err(format!("Index {} out of bounds for universe size {}", i, self.univ_size));
        }
        if j >= self.univ_size {
            return Err(format!("Index {} out of bounds for universe size {}", j, self.univ_size));
        }
        
        let pair = IntArray::from_array(vec![i as i32, j as i32])?;
        self.pairs.insert(pair);
        Ok(())
    }
    
    fn remove(&mut self, i: usize, j: usize) -> Result<(), String> {
        if i >= self.univ_size {
            return Err(format!("Index {} out of bounds for universe size {}", i, self.univ_size));
        }
        if j >= self.univ_size {
            return Err(format!("Index {} out of bounds for universe size {}", j, self.univ_size));
        }
        
        let pair = IntArray::from_array(vec![i as i32, j as i32])?;
        self.pairs.remove(&pair);
        Ok(())
    }
}

impl BinaryRelationCompare<IntArray> for BasicBinaryRelation {}

impl BinaryRelationIterator<IntArray> for BasicBinaryRelation {
    fn pairs(&self) -> std::collections::btree_set::IntoIter<IntArray> {
        self.pairs.clone().into_iter()
    }
}

impl BinaryRelationFactory<IntArray> for BasicBinaryRelation {
    fn identity(size: usize) -> Result<Box<dyn BinaryRelation<IntArray>>, String> {
        Ok(Box::new(Self::identity(size)?))
    }
    
    fn universal(size: usize) -> Result<Box<dyn BinaryRelation<IntArray>>, String> {
        Ok(Box::new(Self::universal(size)?))
    }
    
    fn empty(size: usize) -> Result<Box<dyn BinaryRelation<IntArray>>, String> {
        Ok(Box::new(Self::empty(size)?))
    }
}

impl PartialEq for BasicBinaryRelation {
    fn eq(&self, other: &Self) -> bool {
        self.univ_size == other.univ_size && self.pairs == other.pairs
    }
}

impl Eq for BasicBinaryRelation {}

impl Hash for BasicBinaryRelation {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.univ_size.hash(state);
        // Hash pairs in a consistent order
        for pair in &self.pairs {
            pair.hash(state);
        }
    }
}

impl fmt::Display for BasicBinaryRelation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.to_string())
    }
}

impl PartialOrd for BasicBinaryRelation {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for BasicBinaryRelation {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        // First compare by universe size
        match self.univ_size.cmp(&other.univ_size) {
            std::cmp::Ordering::Equal => {
                // Then compare by number of pairs
                self.pairs.len().cmp(&other.pairs.len())
            }
            other => other,
        }
    }
}

// Iterator implementation for BasicBinaryRelation
impl<'a> IntoIterator for &'a BasicBinaryRelation {
    type Item = &'a IntArray;
    type IntoIter = std::collections::btree_set::Iter<'a, IntArray>;
    
    fn into_iter(self) -> Self::IntoIter {
        self.pairs.iter()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_new() {
        let relation = BasicBinaryRelation::new(5).unwrap();
        assert_eq!(relation.universe_size(), 5);
        assert!(relation.get_pairs().is_empty());
        assert!(relation.is_empty());
    }
    
    #[test]
    fn test_new_zero_size() {
        let result = BasicBinaryRelation::new(0);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_add_and_is_related() {
        let mut relation = BasicBinaryRelation::new(3).unwrap();
        
        relation.add(0, 1).unwrap();
        relation.add(1, 2).unwrap();
        
        assert!(relation.is_related(0, 1));
        assert!(relation.is_related(1, 2));
        assert!(!relation.is_related(0, 2));
        assert!(!relation.is_related(2, 0));
        assert_eq!(relation.size(), 2);
    }
    
    #[test]
    fn test_add_out_of_bounds() {
        let mut relation = BasicBinaryRelation::new(3).unwrap();
        
        assert!(relation.add(3, 1).is_err());
        assert!(relation.add(1, 3).is_err());
    }
    
    #[test]
    fn test_remove() {
        let mut relation = BasicBinaryRelation::new(3).unwrap();
        
        relation.add(0, 1).unwrap();
        relation.add(1, 2).unwrap();
        
        assert!(relation.is_related(0, 1));
        relation.remove(0, 1).unwrap();
        assert!(!relation.is_related(0, 1));
        assert!(relation.is_related(1, 2));
        assert_eq!(relation.size(), 1);
    }
    
    #[test]
    fn test_identity() {
        let identity = BasicBinaryRelation::identity(3).unwrap();
        
        assert!(identity.is_related(0, 0));
        assert!(identity.is_related(1, 1));
        assert!(identity.is_related(2, 2));
        assert!(!identity.is_related(0, 1));
        assert!(!identity.is_related(1, 0));
        assert_eq!(identity.size(), 3);
        assert!(identity.is_reflexive());
    }
    
    #[test]
    fn test_universal() {
        let universal = BasicBinaryRelation::universal(2).unwrap();
        
        assert!(universal.is_related(0, 0));
        assert!(universal.is_related(0, 1));
        assert!(universal.is_related(1, 0));
        assert!(universal.is_related(1, 1));
        assert_eq!(universal.size(), 4);
    }
    
    #[test]
    fn test_empty() {
        let empty = BasicBinaryRelation::empty(3).unwrap();
        
        assert!(!empty.is_related(0, 1));
        assert!(empty.is_empty());
        assert_eq!(empty.size(), 0);
    }
    
    #[test]
    fn test_compose() {
        let mut alpha = BasicBinaryRelation::new(3).unwrap();
        alpha.add(0, 1).unwrap();
        alpha.add(1, 2).unwrap();
        
        let mut beta = BasicBinaryRelation::new(3).unwrap();
        beta.add(1, 0).unwrap();
        beta.add(2, 1).unwrap();
        
        let composition = alpha.compose(&beta).unwrap();
        
        // (0,1) in alpha, (1,0) in beta -> (0,0) in composition
        assert!(composition.is_related(0, 0));
        // (1,2) in alpha, (2,1) in beta -> (1,1) in composition
        assert!(composition.is_related(1, 1));
        // No other pairs should be in the composition
        assert!(!composition.is_related(0, 1));
        assert!(!composition.is_related(1, 0));
    }
    
    #[test]
    fn test_compose_different_sizes() {
        let alpha = BasicBinaryRelation::new(3).unwrap();
        let beta = BasicBinaryRelation::new(2).unwrap();
        
        let result = alpha.compose(&beta);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_is_reflexive() {
        let mut relation = BasicBinaryRelation::new(3).unwrap();
        
        // Not reflexive initially
        assert!(!relation.is_reflexive());
        
        // Add diagonal pairs
        relation.add(0, 0).unwrap();
        relation.add(1, 1).unwrap();
        relation.add(2, 2).unwrap();
        
        assert!(relation.is_reflexive());
    }
    
    #[test]
    fn test_is_symmetric() {
        let mut relation = BasicBinaryRelation::new(3).unwrap();
        
        // Not symmetric initially
        assert!(relation.is_symmetric());
        
        // Add symmetric pairs
        relation.add(0, 1).unwrap();
        relation.add(1, 0).unwrap();
        
        assert!(relation.is_symmetric());
        
        // Add asymmetric pair
        relation.add(1, 2).unwrap();
        
        assert!(!relation.is_symmetric());
    }
    
    #[test]
    fn test_is_transitive() {
        let mut relation = BasicBinaryRelation::new(3).unwrap();
        
        // Empty relation is transitive
        assert!(relation.is_transitive());
        
        // Add transitive pairs: (0,1), (1,2), (0,2)
        relation.add(0, 1).unwrap();
        relation.add(1, 2).unwrap();
        relation.add(0, 2).unwrap();
        
        assert!(relation.is_transitive());
        
        // Remove (0,2) to make it non-transitive
        relation.remove(0, 2).unwrap();
        
        assert!(!relation.is_transitive());
    }
    
    #[test]
    fn test_is_equivalence() {
        let identity = BasicBinaryRelation::identity(3).unwrap();
        assert!(identity.is_equivalence());
        
        let mut relation = BasicBinaryRelation::new(3).unwrap();
        relation.add(0, 0).unwrap();
        relation.add(1, 1).unwrap();
        relation.add(2, 2).unwrap();
        relation.add(0, 1).unwrap();
        relation.add(1, 0).unwrap();
        relation.add(1, 2).unwrap();
        relation.add(2, 1).unwrap();
        relation.add(0, 2).unwrap();
        relation.add(2, 0).unwrap();
        
        assert!(relation.is_equivalence());
    }
    
    #[test]
    fn test_from_pairs() {
        let pairs = vec![
            IntArray::from_array(vec![0, 1]).unwrap(),
            IntArray::from_array(vec![1, 2]).unwrap(),
        ];
        
        let relation = BasicBinaryRelation::from_pairs(pairs, 3).unwrap();
        
        assert_eq!(relation.universe_size(), 3);
        assert_eq!(relation.size(), 2);
        assert!(relation.is_related(0, 1));
        assert!(relation.is_related(1, 2));
    }
    
    #[test]
    fn test_from_pairs_invalid() {
        let pairs = vec![
            IntArray::from_array(vec![0, 1]).unwrap(),
            IntArray::from_array(vec![1, 2]).unwrap(),
        ];
        
        // Universe size too small
        let result = BasicBinaryRelation::from_pairs(pairs, 2);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_equality() {
        let mut relation1 = BasicBinaryRelation::new(3).unwrap();
        relation1.add(0, 1).unwrap();
        relation1.add(1, 2).unwrap();
        
        let mut relation2 = BasicBinaryRelation::new(3).unwrap();
        relation2.add(0, 1).unwrap();
        relation2.add(1, 2).unwrap();
        
        let mut relation3 = BasicBinaryRelation::new(3).unwrap();
        relation3.add(0, 1).unwrap();
        relation3.add(1, 0).unwrap();
        
        assert_eq!(relation1, relation2);
        assert_ne!(relation1, relation3);
    }
    
    #[test]
    fn test_ordering() {
        let small = BasicBinaryRelation::new(2).unwrap();
        let large = BasicBinaryRelation::new(3).unwrap();
        
        assert!(small < large);
        
        let mut small_with_pairs = BasicBinaryRelation::new(2).unwrap();
        small_with_pairs.add(0, 1).unwrap();
        
        assert!(small < small_with_pairs);
    }
    
    #[test]
    fn test_iterator() {
        let mut relation = BasicBinaryRelation::new(3).unwrap();
        relation.add(0, 1).unwrap();
        relation.add(1, 2).unwrap();
        
        let pairs: Vec<_> = relation.into_iter().collect();
        assert_eq!(pairs.len(), 2);
    }
    
    #[test]
    fn test_clear() {
        let mut relation = BasicBinaryRelation::new(3).unwrap();
        relation.add(0, 1).unwrap();
        relation.add(1, 2).unwrap();
        
        assert_eq!(relation.size(), 2);
        relation.clear();
        assert_eq!(relation.size(), 0);
        assert!(relation.is_empty());
    }
}
