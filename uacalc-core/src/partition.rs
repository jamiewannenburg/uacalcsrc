use crate::utils::validate_partition_elements;
use crate::{UACalcError, UACalcResult};
use serde::{Deserialize, Serialize};
use std::cell::RefCell;
use std::collections::HashMap;

/// Trait for partition data structures
pub trait Partition {
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
    fn blocks(&self) -> UACalcResult<Vec<Vec<usize>>>;

    /// Get all block representatives
    fn representatives(&self) -> Vec<usize>;

    /// Get the block index for an element
    fn block_index(&self, element: usize) -> UACalcResult<usize>;

    /// Join two partitions
    fn join(&self, other: &dyn Partition) -> UACalcResult<BasicPartition>
    where
        Self: Sized;

    /// Meet two partitions
    fn meet(&self, other: &dyn Partition) -> UACalcResult<BasicPartition>
    where
        Self: Sized;

    /// Check if this partition is finer than another
    fn is_finer_than(&self, other: &dyn Partition) -> UACalcResult<bool>
    where
        Self: Sized;

    /// Check if this partition is coarser than another
    fn is_coarser_than(&self, other: &dyn Partition) -> UACalcResult<bool>
    where
        Self: Sized,
    {
        // This method cannot be implemented for trait objects due to the Sized requirement
        // on is_finer_than. In practice, this would need to be implemented differently
        // for each concrete type that implements Partition.
        unimplemented!("is_coarser_than cannot be implemented for trait objects")
    }

    /// Check if this is the finest partition (all elements in separate blocks)
    fn is_zero(&self) -> bool;

    /// Check if this is the coarsest partition (all elements in one block)
    fn is_one(&self) -> bool;

    /// Check if all blocks have the same size
    fn is_uniform(&self) -> bool;

    /// Convert to representative array (mirrors Java's toArray)
    fn to_array(&self) -> Vec<usize>;

    /// Create from representative array
    fn from_array(array: &[usize]) -> UACalcResult<BasicPartition>
    where
        Self: Sized;
}

/// Basic partition implementation using union-find with interior mutability
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BasicPartition {
    size: usize,
    parent: RefCell<Vec<usize>>,
    rank: RefCell<Vec<usize>>,
    num_blocks_cache: RefCell<Option<usize>>,
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
            parent: RefCell::new(parent),
            rank: RefCell::new(rank),
            num_blocks_cache: RefCell::new(None),
        }
    }

    /// Create a new partition with validation
    /// Returns an error if size is 0
    pub fn try_new(size: usize) -> UACalcResult<Self> {
        if size == 0 {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot create partition with size 0".to_string(),
            });
        }
        Ok(Self::new(size))
    }

    /// Create a partition from a list of blocks
    pub fn from_blocks(size: usize, blocks: Vec<Vec<usize>>) -> UACalcResult<Self> {
        let mut partition = Self::new(size);

        for block in blocks {
            if block.is_empty() {
                continue;
            }

            // Validate all elements in the block
            validate_partition_elements(&block, size)?;

            let representative = block[0];
            for &element in &block[1..] {
                partition.union_elements(representative, element)?;
            }
        }

        Ok(partition)
    }

    /// Create a partition from a representative array
    pub fn from_array(array: &[usize]) -> UACalcResult<Self> {
        let size = array.len();
        let mut partition = Self::new(size);

        for (element, &representative) in array.iter().enumerate() {
            if representative >= size {
                return Err(UACalcError::IndexOutOfBounds {
                    index: representative,
                    size,
                });
            }
            partition.union_elements(representative, element)?;
        }

        Ok(partition)
    }

    /// Find the representative of an element (with path compression)
    fn find_mut(&self, x: usize) -> UACalcResult<usize> {
        if x >= self.size {
            return Err(UACalcError::IndexOutOfBounds {
                index: x,
                size: self.size,
            });
        }
        let mut parent = self.parent.borrow_mut();
        let mut v = x;
        // Find root
        while parent[v] != v {
            v = parent[v];
        }
        let root = v;
        // Path compression
        v = x;
        while parent[v] != v {
            let p = parent[v];
            parent[v] = root;
            v = p;
        }
        Ok(root)
    }

    /// Union two elements (with union by rank)
    pub fn union_elements(&self, x: usize, y: usize) -> UACalcResult<bool> {
        let root_x = self.find_mut(x)?;
        let root_y = self.find_mut(y)?;

        if root_x == root_y {
            return Ok(false); // No union occurred
        }

        let mut parent = self.parent.borrow_mut();
        let mut rank = self.rank.borrow_mut();

        if rank[root_x] < rank[root_y] {
            parent[root_x] = root_y;
        } else if rank[root_x] > rank[root_y] {
            parent[root_y] = root_x;
        } else {
            parent[root_y] = root_x;
            rank[root_x] += 1;
        }

        // Invalidate cache
        *self.num_blocks_cache.borrow_mut() = None;

        Ok(true) // Union occurred
    }

    /// Join two blocks by their representatives
    pub fn join_blocks(&self, repr1: usize, repr2: usize) -> UACalcResult<()> {
        self.union_elements(repr1, repr2)?;
        Ok(())
    }

    /// Get the current blocks efficiently
    fn get_blocks(&self) -> UACalcResult<Vec<Vec<usize>>> {
        let mut block_map: HashMap<usize, Vec<usize>> = HashMap::new();

        for element in 0..self.size {
            let representative = self.find_mut(element)?;
            block_map
                .entry(representative)
                .or_insert_with(Vec::new)
                .push(element);
        }

        let mut blocks: Vec<Vec<usize>> = block_map.into_values().collect();
        blocks.sort_by_key(|block| block[0]); // Sort by representative
        Ok(blocks)
    }

    /// Get the number of blocks efficiently
    fn get_num_blocks(&self) -> UACalcResult<usize> {
        // Check cache first
        if let Some(num_blocks) = *self.num_blocks_cache.borrow() {
            return Ok(num_blocks);
        }

        let num_blocks = self.get_blocks()?.len();
        *self.num_blocks_cache.borrow_mut() = Some(num_blocks);
        Ok(num_blocks)
    }

    /// Get all representatives efficiently
    fn get_representatives(&self) -> UACalcResult<Vec<usize>> {
        let mut representatives = Vec::new();
        let mut seen = std::collections::HashSet::new();

        for element in 0..self.size {
            let representative = self.find_mut(element)?;
            if !seen.contains(&representative) {
                seen.insert(representative);
                representatives.push(representative);
            }
        }

        representatives.sort();
        Ok(representatives)
    }

    /// Get block index for an element
    fn get_block_index(&self, element: usize) -> UACalcResult<usize> {
        let representative = self.find_mut(element)?;
        let representatives = self.get_representatives()?;

        representatives
            .binary_search(&representative)
            .map_err(|_| UACalcError::InvalidOperation {
                message: "Representative not found in sorted list".to_string(),
            })
    }

    /// Check if this is the finest partition
    fn is_zero_partition(&self) -> bool {
        for element in 0..self.size {
            if self.find_mut(element).unwrap_or(element) != element {
                return false;
            }
        }
        true
    }

    /// Check if this is the coarsest partition
    fn is_one_partition(&self) -> bool {
        if self.size <= 1 {
            return true;
        }

        let first_representative = self.find_mut(0).unwrap_or(0);
        for element in 1..self.size {
            if self.find_mut(element).unwrap_or(element) != first_representative {
                return false;
            }
        }
        true
    }

    /// Check if all blocks have the same size
    fn is_uniform_partition(&self) -> bool {
        let blocks = self.get_blocks().unwrap_or_default();
        if blocks.len() <= 1 {
            return true;
        }

        let first_size = blocks[0].len();
        blocks.iter().all(|block| block.len() == first_size)
    }

    /// Convert to representative array
    fn to_array_partition(&self) -> Vec<usize> {
        let mut array = Vec::with_capacity(self.size);
        for element in 0..self.size {
            array.push(self.find_mut(element).unwrap_or(element));
        }
        array
    }
}

impl Partition for BasicPartition {
    fn size(&self) -> usize {
        self.size
    }

    fn num_blocks(&self) -> usize {
        self.get_num_blocks().unwrap_or(0)
    }

    fn block(&self, element: usize) -> UACalcResult<Vec<usize>> {
        let representative = self.find_mut(element)?;
        let blocks = self.get_blocks()?;

        for block in blocks {
            if block.contains(&representative) {
                return Ok(block);
            }
        }

        Err(UACalcError::IndexOutOfBounds {
            index: element,
            size: self.size,
        })
    }

    fn representative(&self, element: usize) -> UACalcResult<usize> {
        self.find_mut(element)
    }

    fn same_block(&self, a: usize, b: usize) -> UACalcResult<bool> {
        let rep_a = self.find_mut(a)?;
        let rep_b = self.find_mut(b)?;
        Ok(rep_a == rep_b)
    }

    fn blocks(&self) -> UACalcResult<Vec<Vec<usize>>> {
        self.get_blocks()
    }

    fn representatives(&self) -> Vec<usize> {
        self.get_representatives().unwrap_or_default()
    }

    fn block_index(&self, element: usize) -> UACalcResult<usize> {
        self.get_block_index(element)
    }

    fn join(&self, other: &dyn Partition) -> UACalcResult<BasicPartition> {
        if self.size() != other.size() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot join partitions of different sizes".to_string(),
            });
        }

        let mut result = self.clone();

        // For each pair of elements that are in the same block in other,
        // union them in result
        for block in other.blocks()? {
            if block.len() > 1 {
                let representative = block[0];
                for &element in &block[1..] {
                    result.union_elements(representative, element)?;
                }
            }
        }

        Ok(result)
    }

    fn meet(&self, other: &dyn Partition) -> UACalcResult<BasicPartition> {
        if self.size() != other.size() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot meet partitions of different sizes".to_string(),
            });
        }

        // The meet is more complex - we need to find the finest partition
        // that is coarser than both self and other
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
                    result.union_elements(representative, x)?;
                }
            }
        }

        Ok(result)
    }

    fn is_finer_than(&self, other: &dyn Partition) -> UACalcResult<bool> {
        if self.size() != other.size() {
            return Ok(false);
        }

        // Check if every block of self is contained in some block of other
        for block_self in self.blocks()? {
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

    fn is_zero(&self) -> bool {
        self.is_zero_partition()
    }

    fn is_one(&self) -> bool {
        self.is_one_partition()
    }

    fn is_uniform(&self) -> bool {
        self.is_uniform_partition()
    }

    fn to_array(&self) -> Vec<usize> {
        self.to_array_partition()
    }

    fn from_array(array: &[usize]) -> UACalcResult<BasicPartition> {
        Self::from_array(array)
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
            partition.union_elements(0, i)?;
        }
    }
    Ok(partition)
}
