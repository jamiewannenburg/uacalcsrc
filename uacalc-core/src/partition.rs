use crate::{UACalcError, UACalcResult};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Trait for partition data structures
pub trait Partition: Clone + Send + Sync {
    /// Get the number of elements in the partition
    fn size(&self) -> usize;
    
    /// Get the number of blocks in the partition
    fn num_blocks(&self) -> usize;
    
    /// Get the block containing a given element
    fn block(&self, element: usize) -> UACalcResult<Vec<usize>>;
    
    /// Get the representative of the block containing a given element
    fn representative(&self, element: usize) -> UACalcResult<usize>;
    
    /// Check if two elements are in the same block
    fn same_block(&self, a: usize, b: usize) -> UACalcResult<bool>;
    
    /// Get all blocks of the partition
    fn blocks(&self) -> Vec<Vec<usize>>;
    
    /// Join two partitions
    fn join(&self, other: &dyn Partition) -> UACalcResult<Box<dyn Partition>>;
    
    /// Meet two partitions
    fn meet(&self, other: &dyn Partition) -> UACalcResult<Box<dyn Partition>>;
    
    /// Check if this partition is finer than another
    fn is_finer_than(&self, other: &dyn Partition) -> UACalcResult<bool>;
    
    /// Check if this partition is coarser than another
    fn is_coarser_than(&self, other: &dyn Partition) -> UACalcResult<bool> {
        other.is_finer_than(self)
    }
}

/// Basic partition implementation using union-find
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BasicPartition {
    size: usize,
    parent: Vec<usize>,
    rank: Vec<usize>,
    block_cache: Option<Vec<Vec<usize>>>,
}

impl BasicPartition {
    /// Create a new partition with all elements in separate blocks
    pub fn new(size: usize) -> Self {
        let mut parent = Vec::with_capacity(size);
        let mut rank = Vec::with_capacity(size);
        
        for i in 0..size {
            parent.push(i);
            rank.push(0);
        }
        
        Self {
            size,
            parent,
            rank,
            block_cache: None,
        }
    }
    
    /// Create a partition from a list of blocks
    pub fn from_blocks(size: usize, blocks: Vec<Vec<usize>>) -> UACalcResult<Self> {
        let mut partition = Self::new(size);
        
        for block in blocks {
            if block.is_empty() {
                continue;
            }
            
            let representative = block[0];
            for &element in &block[1..] {
                partition.union(representative, element)?;
            }
        }
        
        Ok(partition)
    }
    
    /// Find the representative of an element (with path compression)
    fn find(&mut self, mut x: usize) -> UACalcResult<usize> {
        if x >= self.size {
            return Err(UACalcError::IndexOutOfBounds {
                index: x,
                size: self.size,
            });
        }
        
        if self.parent[x] != x {
            self.parent[x] = self.find(self.parent[x])?;
        }
        
        Ok(self.parent[x])
    }
    
    /// Union two elements (with union by rank)
    pub fn union(&mut self, x: usize, y: usize) -> UACalcResult<()> {
        let root_x = self.find(x)?;
        let root_y = self.find(y)?;
        
        if root_x == root_y {
            return Ok(());
        }
        
        if self.rank[root_x] < self.rank[root_y] {
            self.parent[root_x] = root_y;
        } else if self.rank[root_x] > self.rank[root_y] {
            self.parent[root_y] = root_x;
        } else {
            self.parent[root_y] = root_x;
            self.rank[root_x] += 1;
        }
        
        // Invalidate cache
        self.block_cache = None;
        
        Ok(())
    }
    
    /// Get the current blocks (with caching)
    fn get_blocks(&mut self) -> UACalcResult<Vec<Vec<usize>>> {
        if let Some(ref blocks) = self.block_cache {
            return Ok(blocks.clone());
        }
        
        let mut block_map: HashMap<usize, Vec<usize>> = HashMap::new();
        
        for element in 0..self.size {
            let representative = self.find(element)?;
            block_map.entry(representative).or_insert_with(Vec::new).push(element);
        }
        
        let blocks: Vec<Vec<usize>> = block_map.into_values().collect();
        self.block_cache = Some(blocks.clone());
        
        Ok(blocks)
    }
    
    /// Get the number of blocks (with caching)
    fn get_num_blocks(&mut self) -> UACalcResult<usize> {
        Ok(self.get_blocks()?.len())
    }
}

impl Partition for BasicPartition {
    fn size(&self) -> usize {
        self.size
    }
    
    fn num_blocks(&self) -> usize {
        // This is a bit awkward due to the need for mutable access
        // In practice, you might want to cache this or use a different approach
        let mut this = self.clone();
        this.get_num_blocks().unwrap_or(0)
    }
    
    fn block(&self, element: usize) -> UACalcResult<Vec<usize>> {
        let mut this = self.clone();
        let blocks = this.get_blocks()?;
        
        for block in blocks {
            if block.contains(&element) {
                return Ok(block);
            }
        }
        
        Err(UACalcError::IndexOutOfBounds {
            index: element,
            size: self.size,
        })
    }
    
    fn representative(&self, element: usize) -> UACalcResult<usize> {
        let mut this = self.clone();
        this.find(element)
    }
    
    fn same_block(&self, a: usize, b: usize) -> UACalcResult<bool> {
        let mut this = self.clone();
        let rep_a = this.find(a)?;
        let rep_b = this.find(b)?;
        Ok(rep_a == rep_b)
    }
    
    fn blocks(&self) -> Vec<Vec<usize>> {
        let mut this = self.clone();
        this.get_blocks().unwrap_or_default()
    }
    
    fn join(&self, other: &dyn Partition) -> UACalcResult<Box<dyn Partition>> {
        if self.size() != other.size() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot join partitions of different sizes".to_string(),
            });
        }
        
        let mut result = self.clone();
        
        // For each pair of elements that are in the same block in other,
        // union them in result
        for block in other.blocks() {
            if block.len() > 1 {
                let representative = block[0];
                for &element in &block[1..] {
                    result.union(representative, element)?;
                }
            }
        }
        
        Ok(Box::new(result))
    }
    
    fn meet(&self, other: &dyn Partition) -> UACalcResult<Box<dyn Partition>> {
        if self.size() != other.size() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot meet partitions of different sizes".to_string(),
            });
        }
        
        // The meet is more complex - we need to find the finest partition
        // that is coarser than both self and other
        // This is a simplified implementation
        let mut result = BasicPartition::new(self.size());
        
        // For each element, find the intersection of its blocks in both partitions
        for element in 0..self.size() {
            let block_self = self.block(element)?;
            let block_other = other.block(element)?;
            
            // Find intersection
            let intersection: Vec<usize> = block_self
                .into_iter()
                .filter(|&x| block_other.contains(&x))
                .collect();
            
            // Union all elements in the intersection
            if intersection.len() > 1 {
                let representative = intersection[0];
                for &x in &intersection[1..] {
                    result.union(representative, x)?;
                }
            }
        }
        
        Ok(Box::new(result))
    }
    
    fn is_finer_than(&self, other: &dyn Partition) -> UACalcResult<bool> {
        if self.size() != other.size() {
            return Ok(false);
        }
        
        // Check if every block of self is contained in some block of other
        for block_self in self.blocks() {
            if block_self.is_empty() {
                continue;
            }
            
            let representative = block_self[0];
            let block_other = other.block(representative)?;
            
            // Check if all elements in block_self are in block_other
            for &element in &block_self {
                if !block_other.contains(&element) {
                    return Ok(false);
                }
            }
        }
        
        Ok(true)
    }
}

/// Create the finest partition (all elements in separate blocks)
pub fn finest_partition(size: usize) -> BasicPartition {
    BasicPartition::new(size)
}

/// Create the coarsest partition (all elements in one block)
pub fn coarsest_partition(size: usize) -> UACalcResult<BasicPartition> {
    let mut partition = BasicPartition::new(size);
    if size > 1 {
        for i in 1..size {
            partition.union(0, i)?;
        }
    }
    Ok(partition)
}

