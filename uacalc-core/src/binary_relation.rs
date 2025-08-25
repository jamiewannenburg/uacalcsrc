use crate::{UACalcError, UACalcResult};
use serde::{Deserialize, Serialize};
use bitvec::prelude::*;

/// Trait for binary relation data structures
pub trait BinaryRelation: Clone + Send + Sync {
    /// Get the size of the relation (number of elements)
    fn size(&self) -> usize;
    
    /// Check if (a, b) is in the relation
    fn contains(&self, a: usize, b: usize) -> UACalcResult<bool>;
    
    /// Add (a, b) to the relation
    fn add(&mut self, a: usize, b: usize) -> UACalcResult<()>;
    
    /// Remove (a, b) from the relation
    fn remove(&mut self, a: usize, b: usize) -> UACalcResult<()>;
    
    /// Get all pairs in the relation
    fn pairs(&self) -> Vec<(usize, usize)>;
    
    /// Get the reflexive closure of the relation
    fn reflexive_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>>;
    
    /// Get the symmetric closure of the relation
    fn symmetric_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>>;
    
    /// Get the transitive closure of the relation
    fn transitive_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>>;
    
    /// Get the reflexive, symmetric, and transitive closure (equivalence relation)
    fn equivalence_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>> {
        let reflexive = self.reflexive_closure()?;
        let symmetric = reflexive.symmetric_closure()?;
        symmetric.transitive_closure()
    }
    
    /// Check if the relation is reflexive
    fn is_reflexive(&self) -> UACalcResult<bool>;
    
    /// Check if the relation is symmetric
    fn is_symmetric(&self) -> UACalcResult<bool>;
    
    /// Check if the relation is transitive
    fn is_transitive(&self) -> UACalcResult<bool>;
    
    /// Check if the relation is an equivalence relation
    fn is_equivalence(&self) -> UACalcResult<bool> {
        Ok(self.is_reflexive()? && self.is_symmetric()? && self.is_transitive()?)
    }
    
    /// Union with another relation
    fn union(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>>;
    
    /// Intersection with another relation
    fn intersection(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>>;
    
    /// Composition with another relation
    fn composition(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>>;
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
    
    fn reflexive_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>> {
        let mut closure = self.clone();
        for i in 0..self.size {
            closure.add(i, i)?;
        }
        Ok(Box::new(closure))
    }
    
    fn symmetric_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>> {
        let mut closure = self.clone();
        for a in 0..self.size {
            for b in 0..self.size {
                if self.contains(a, b)? {
                    closure.add(b, a)?;
                }
            }
        }
        Ok(Box::new(closure))
    }
    
    fn transitive_closure(&self) -> UACalcResult<Box<dyn BinaryRelation>> {
        // Use Floyd-Warshall algorithm for transitive closure
        let mut closure = self.clone();
        
        for k in 0..self.size {
            for i in 0..self.size {
                for j in 0..self.size {
                    if closure.contains(i, k)? && closure.contains(k, j)? {
                        closure.add(i, j)?;
                    }
                }
            }
        }
        
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
    
    fn union(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>> {
        if self.size() != other.size() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot union relations of different sizes".to_string(),
            });
        }
        
        let mut result = self.clone();
        for (a, b) in other.pairs() {
            result.add(a, b)?;
        }
        
        Ok(Box::new(result))
    }
    
    fn intersection(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>> {
        if self.size() != other.size() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot intersect relations of different sizes".to_string(),
            });
        }
        
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
    
    fn composition(&self, other: &dyn BinaryRelation) -> UACalcResult<Box<dyn BinaryRelation>> {
        if self.size() != other.size() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot compose relations of different sizes".to_string(),
            });
        }
        
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

/// Create the identity relation
pub fn identity_relation(size: usize) -> BasicBinaryRelation {
    BasicBinaryRelation::identity(size)
}

/// Create the universal relation
pub fn universal_relation(size: usize) -> BasicBinaryRelation {
    BasicBinaryRelation::universal(size)
}

/// Create an equivalence relation from a partition
pub fn equivalence_from_partition(partition: &dyn crate::partition::Partition) -> UACalcResult<BasicBinaryRelation> {
    let size = partition.size();
    let mut relation = BasicBinaryRelation::new(size);
    
    for block in partition.blocks() {
        for &a in &block {
            for &b in &block {
                relation.add(a, b)?;
            }
        }
    }
    
    Ok(relation)
}

