use crate::{UACalcError, UACalcResult};
use serde::{Deserialize, Serialize};

use bitvec::prelude::*;

/// Trait for binary relations
pub trait BinaryRelation: Send + Sync {
    /// Get the size of the relation (number of elements)
    fn size(&self) -> usize;

    /// Check if the relation contains a pair
    fn contains(&self, a: usize, b: usize) -> UACalcResult<bool>;

    /// Check if the relation contains a pair (alias for contains to mirror Java)
    fn is_related(&self, a: usize, b: usize) -> UACalcResult<bool> {
        self.contains(a, b)
    }

    /// Add a pair to the relation
    fn add(&mut self, a: usize, b: usize) -> UACalcResult<()>;

    /// Remove a pair from the relation
    fn remove(&mut self, a: usize, b: usize) -> UACalcResult<()>;

    /// Get all pairs in the relation
    fn pairs(&self) -> Vec<(usize, usize)>;

    /// Get all pairs in the relation (mirrors Java getPairs)
    fn get_pairs(&self) -> Vec<(usize, usize)> {
        self.pairs()
    }

    /// Iterate over pairs in the relation
    fn iter_pairs(&self) -> Box<dyn Iterator<Item = (usize, usize)> + '_>;

    /// Get the as_any method for downcasting
    fn as_any(&self) -> &dyn std::any::Any;

    /// Compute the reflexive closure
    fn reflexive_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>>
    where
        Self: Sized;

    /// Compute the symmetric closure
    fn symmetric_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>>
    where
        Self: Sized;

    /// Compute the transitive closure using Warshall's algorithm
    fn transitive_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>>
    where
        Self: Sized;

    /// Compute the equivalence closure
    fn equivalence_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>>
    where
        Self: Sized;

    /// Check if the relation is reflexive
    fn is_reflexive(&self) -> UACalcResult<bool>;

    /// Check if the relation is symmetric
    fn is_symmetric(&self) -> UACalcResult<bool>;

    /// Check if the relation is transitive
    fn is_transitive(&self) -> UACalcResult<bool>;

    /// Check if the relation is an equivalence relation
    fn is_equivalence(&self) -> UACalcResult<bool>;

    /// Union with another relation
    fn union(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>>
    where
        Self: Sized;

    /// Intersection with another relation
    fn intersection(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>>
    where
        Self: Sized;

    /// Composition with another relation (mirrors Java compose)
    fn compose(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>>
    where
        Self: Sized,
    {
        self.composition(other)
    }

    /// Composition with another relation
    fn composition(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>>
    where
        Self: Sized;

    /// Iterate over rows
    fn rows(&self) -> Box<dyn Iterator<Item = Box<dyn Iterator<Item = bool> + '_>> + '_>;

    /// Iterate over columns
    fn columns(&self) -> Box<dyn Iterator<Item = Box<dyn Iterator<Item = bool> + '_>> + '_>;

    /// Check if relation contains all given pairs
    fn contains_all(&self, pairs: &[(usize, usize)]) -> UACalcResult<bool>;

    /// Add all given pairs to the relation
    fn add_all(&mut self, pairs: &[(usize, usize)]) -> UACalcResult<()>;
}

/// Basic binary relation implementation using bit vectors
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BasicBinaryRelation {
    size: usize,
    matrix: BitVec,
}

impl BasicBinaryRelation {
    /// Create a new empty binary relation
    pub fn new(size: usize) -> Self {
        Self {
            size,
            matrix: bitvec![0; size * size],
        }
    }

    /// Create a binary relation from a list of pairs
    pub fn from_pairs(size: usize, pairs: Vec<(usize, usize)>) -> UACalcResult<Self> {
        let mut relation = Self::new(size);
        for (a, b) in pairs {
            relation.add(a, b)?;
        }
        Ok(relation)
    }

    /// Get the index in the bit vector for pair (a, b)
    fn index(&self, a: usize, b: usize) -> UACalcResult<usize> {
        if a >= self.size || b >= self.size {
            return Err(UACalcError::IndexOutOfBounds {
                index: a.max(b),
                size: self.size,
            });
        }
        Ok(a * self.size + b)
    }

    /// Create the identity relation
    pub fn identity(size: usize) -> Self {
        let mut relation = Self::new(size);
        for i in 0..size {
            relation.matrix.set(i * size + i, true);
        }
        relation
    }

    /// Create the universal relation
    pub fn universal(size: usize) -> Self {
        let mut relation = Self::new(size);
        for i in 0..size * size {
            relation.matrix.set(i, true);
        }
        relation
    }

    /// Create an empty relation
    pub fn empty(size: usize) -> Self {
        Self::new(size)
    }

    /// Matrix multiplication for composition
    pub fn matrix_multiply(
        &self,
        other: &BasicBinaryRelation,
    ) -> UACalcResult<BasicBinaryRelation> {
        if self.size != other.size {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot multiply relations of different sizes".to_string(),
            });
        }

        let mut result = BasicBinaryRelation::new(self.size);

        for i in 0..self.size {
            for j in 0..self.size {
                for k in 0..self.size {
                    if self.contains(i, k)? && other.contains(k, j)? {
                        result.add(i, j)?;
                    }
                }
            }
        }

        Ok(result)
    }

    /// Compute the reflexive closure (owned version)
    pub fn reflexive_closure_owned(&self) -> UACalcResult<Self> {
        let mut closure = self.clone();
        for i in 0..self.size {
            closure.add(i, i)?;
        }
        Ok(closure)
    }

    /// Compute the symmetric closure (owned version)
    pub fn symmetric_closure_owned(&self) -> UACalcResult<Self> {
        let mut closure = self.clone();
        for a in 0..self.size {
            for b in 0..self.size {
                if self.contains(a, b)? {
                    closure.add(b, a)?;
                }
            }
        }
        Ok(closure)
    }

    /// Compute the transitive closure using Warshall's algorithm (owned version)
    pub fn transitive_closure_owned(&self) -> UACalcResult<Self> {
        let mut closure = self.clone();

        // Warshall's algorithm with optimized bit operations
        for k in 0..self.size {
            // Pre-copy row k for efficiency
            let row_k_start = k * self.size;
            let row_k_end = row_k_start + self.size;
            let row_k: Vec<bool> = (row_k_start..row_k_end)
                .map(|i| closure.matrix[i])
                .collect();

            // For each row i with bit (i,k) set, perform row_i |= row_k
            for i in 0..self.size {
                let row_i_start = i * self.size;
                let _row_i_end = row_i_start + self.size;

                if closure.matrix[row_i_start + k] {
                    // Use bitvec slice operations for efficiency
                    for j in 0..self.size {
                        if row_k[j] {
                            closure.matrix.set(row_i_start + j, true);
                        }
                    }
                }
            }
        }

        Ok(closure)
    }

    /// Compute the equivalence closure (owned version)
    pub fn equivalence_closure_owned(&self) -> UACalcResult<Self> {
        let reflexive = self.reflexive_closure_owned()?;
        let symmetric = reflexive.symmetric_closure_owned()?;
        symmetric.transitive_closure_owned()
    }

    /// Efficient union with another BasicBinaryRelation using bitwise operations
    pub fn union_efficient(
        &self,
        other: &BasicBinaryRelation,
    ) -> UACalcResult<BasicBinaryRelation> {
        if self.size != other.size {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot union relations of different sizes".to_string(),
            });
        }

        let mut result = self.clone();
        result.matrix |= &other.matrix;
        Ok(result)
    }

    /// Efficient intersection with another BasicBinaryRelation using bitwise operations
    pub fn intersection_efficient(
        &self,
        other: &BasicBinaryRelation,
    ) -> UACalcResult<BasicBinaryRelation> {
        if self.size != other.size {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot intersect relations of different sizes".to_string(),
            });
        }

        let mut result = self.clone();
        result.matrix &= &other.matrix;
        Ok(result)
    }

    /// Efficient composition with another BasicBinaryRelation using bit matrix multiplication
    pub fn composition_efficient(
        &self,
        other: &BasicBinaryRelation,
    ) -> UACalcResult<BasicBinaryRelation> {
        self.matrix_multiply(other)
    }

    /// Convert to partition (for equivalence relations)
    pub fn to_partition(&self) -> UACalcResult<crate::partition::BasicPartition> {
        if !self.is_equivalence()? {
            return Err(UACalcError::InvalidOperation {
                message: "Relation is not an equivalence relation".to_string(),
            });
        }

        let partition = crate::partition::BasicPartition::new(self.size);

        // Use the relation to build the partition
        for i in 0..self.size {
            for j in 0..self.size {
                if self.contains(i, j)? {
                    partition.union_elements(i, j)?;
                }
            }
        }

        Ok(partition)
    }

    /// Create from partition
    pub fn from_partition(partition: &dyn crate::partition::Partition) -> UACalcResult<Self> {
        let size = partition.size();
        let mut relation = Self::new(size);

        for block in partition.blocks()? {
            for &a in &block {
                for &b in &block {
                    relation.add(a, b)?;
                }
            }
        }

        Ok(relation)
    }
}

impl BinaryRelation for BasicBinaryRelation {
    fn size(&self) -> usize {
        self.size
    }

    fn contains(&self, a: usize, b: usize) -> UACalcResult<bool> {
        let index = self.index(a, b)?;
        Ok(self.matrix[index])
    }

    fn add(&mut self, a: usize, b: usize) -> UACalcResult<()> {
        let index = self.index(a, b)?;
        self.matrix.set(index, true);
        Ok(())
    }

    fn remove(&mut self, a: usize, b: usize) -> UACalcResult<()> {
        let index = self.index(a, b)?;
        self.matrix.set(index, false);
        Ok(())
    }

    fn pairs(&self) -> Vec<(usize, usize)> {
        let mut pairs = Vec::new();
        for a in 0..self.size {
            for b in 0..self.size {
                let index = a * self.size + b;
                if self.matrix[index] {
                    pairs.push((a, b));
                }
            }
        }
        pairs
    }

    fn iter_pairs(&self) -> Box<dyn Iterator<Item = (usize, usize)> + '_> {
        let size = self.size;
        let matrix = &self.matrix;
        Box::new((0..size).flat_map(move |a| {
            (0..size).filter_map(move |b| {
                let index = a * size + b;
                if matrix[index] {
                    Some((a, b))
                } else {
                    None
                }
            })
        }))
    }

    fn reflexive_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>> {
        let closure = self.reflexive_closure_owned()?;
        Ok(Box::new(closure))
    }

    fn symmetric_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>> {
        let closure = self.symmetric_closure_owned()?;
        Ok(Box::new(closure))
    }

    fn transitive_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>> {
        let closure = self.transitive_closure_owned()?;
        Ok(Box::new(closure))
    }

    fn equivalence_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>> {
        let closure = self.equivalence_closure_owned()?;
        Ok(Box::new(closure))
    }

    fn is_reflexive(&self) -> UACalcResult<bool> {
        for i in 0..self.size {
            if !self.contains(i, i)? {
                return Ok(false);
            }
        }
        Ok(true)
    }

    fn is_symmetric(&self) -> UACalcResult<bool> {
        for a in 0..self.size {
            for b in 0..self.size {
                if self.contains(a, b)? != self.contains(b, a)? {
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }

    fn is_transitive(&self) -> UACalcResult<bool> {
        for a in 0..self.size {
            for b in 0..self.size {
                for c in 0..self.size {
                    if self.contains(a, b)? && self.contains(b, c)? && !self.contains(a, c)? {
                        return Ok(false);
                    }
                }
            }
        }
        Ok(true)
    }

    fn is_equivalence(&self) -> UACalcResult<bool> {
        Ok(self.is_reflexive()? && self.is_symmetric()? && self.is_transitive()?)
    }

    fn union(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>> {
        if self.size() != other.size() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot union relations of different sizes".to_string(),
            });
        }

        // Try to use efficient union if both are BasicBinaryRelation
        if let Some(other_basic) = other.as_any().downcast_ref::<BasicBinaryRelation>() {
            let result = self.union_efficient(other_basic)?;
            Ok(Box::new(result))
        } else {
            // Fall back to generic implementation
            let mut result = self.clone();
            for (a, b) in other.pairs() {
                result.add(a, b)?;
            }
            Ok(Box::new(result))
        }
    }

    fn intersection(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>> {
        if self.size() != other.size() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot intersect relations of different sizes".to_string(),
            });
        }

        // Try to use efficient intersection if both are BasicBinaryRelation
        if let Some(other_basic) = other.as_any().downcast_ref::<BasicBinaryRelation>() {
            let result = self.intersection_efficient(other_basic)?;
            Ok(Box::new(result))
        } else {
            // Fall back to generic implementation
            let mut result = BasicBinaryRelation::new(self.size());
            for a in 0..self.size {
                for b in 0..self.size {
                    if self.contains(a, b)? && other.contains(a, b)? {
                        result.add(a, b)?;
                    }
                }
            }
            Ok(Box::new(result))
        }
    }

    fn composition(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>> {
        if self.size() != other.size() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot compose relations of different sizes".to_string(),
            });
        }

        // Try to use efficient composition if both are BasicBinaryRelation
        if let Some(other_basic) = other.as_any().downcast_ref::<BasicBinaryRelation>() {
            let result = self.composition_efficient(other_basic)?;
            Ok(Box::new(result))
        } else {
            // Fall back to generic implementation
            let mut result = BasicBinaryRelation::new(self.size());
            for a in 0..self.size {
                for b in 0..self.size {
                    for c in 0..self.size {
                        if self.contains(a, b)? && other.contains(b, c)? {
                            result.add(a, c)?;
                        }
                    }
                }
            }
            Ok(Box::new(result))
        }
    }

    fn rows(&self) -> Box<dyn Iterator<Item = Box<dyn Iterator<Item = bool> + '_>> + '_> {
        let size = self.size;
        let matrix = &self.matrix;
        Box::new((0..size).map(move |row| {
            let start = row * size;
            let end = start + size;
            Box::new((start..end).map(move |i| matrix[i])) as Box<dyn Iterator<Item = bool> + '_>
        }))
    }

    fn columns(&self) -> Box<dyn Iterator<Item = Box<dyn Iterator<Item = bool> + '_>> + '_> {
        let size = self.size;
        let matrix = &self.matrix;
        Box::new((0..size).map(move |col| {
            Box::new((0..size).map(move |row| {
                let index = row * size + col;
                matrix[index]
            })) as Box<dyn Iterator<Item = bool> + '_>
        }))
    }

    fn contains_all(&self, pairs: &[(usize, usize)]) -> UACalcResult<bool> {
        for &(a, b) in pairs {
            if !self.contains(a, b)? {
                return Ok(false);
            }
        }
        Ok(true)
    }

    fn add_all(&mut self, pairs: &[(usize, usize)]) -> UACalcResult<()> {
        for &(a, b) in pairs {
            self.add(a, b)?;
        }
        Ok(())
    }

    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
}

/// Create the identity relation
pub fn identity_relation(size: usize) -> BasicBinaryRelation {
    BasicBinaryRelation::identity(size)
}

/// Create the universal relation
pub fn universal_relation(size: usize) -> BasicBinaryRelation {
    BasicBinaryRelation::universal(size)
}

/// Create an empty relation
pub fn empty_relation(size: usize) -> BasicBinaryRelation {
    BasicBinaryRelation::empty(size)
}

/// Create an equivalence relation from a partition
pub fn equivalence_from_partition(
    partition: &dyn crate::partition::Partition,
) -> UACalcResult<BasicBinaryRelation> {
    BasicBinaryRelation::from_partition(partition)
}
