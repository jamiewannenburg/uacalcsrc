/*! Partition data structure and algorithms.

This module implements partition representations and operations for working with
equivalence relations on finite sets {0, 1, ..., n-1}.

The implementation is based on Ralph Freese's partition algorithms as described
in his unpublished notes on partition algorithms.
*/

use std::collections::{BTreeSet, HashMap};
use std::fmt;
use std::hash::{Hash, Hasher};
use crate::util::int_array::{IntArray, IntArrayTrait};
use super::binary_relation::{
    BinaryRelation, MutableBinaryRelation, BinaryRelationCompare, BinaryRelationIterator, BinaryRelationFactory
};
use super::basic_binary_relation::BasicBinaryRelation;

/// Print types for partition string representations.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum PrintType {
    /// Internal representation (array format)
    Internal,
    /// Algebra program representation (comma-separated sequence of ints)
    Ewk,
    /// Block representation (usual way of writing a partition)
    Block,
    /// Block representation with number of blocks at the end
    Human,
    /// Block representation using square brackets
    SqBraceBlock,
}

/// A partition on the set {0, 1, ..., n-1}.
/// 
/// This struct represents an equivalence relation as an array where:
/// - Negative values indicate root elements with the negative of their block size
/// - Non-negative values indicate parent pointers to root elements
/// 
/// The partition is maintained in normalized form where roots are the smallest
/// elements in their blocks.
#[derive(Debug, Clone)]
pub struct Partition {
    /// The underlying array representation
    array: Vec<i32>,
    /// Cached number of blocks (-1 if not computed)
    block_count: i32,
    /// Cached representatives array
    representatives: Option<Vec<usize>>,
}

impl Partition {
    /// Create a new partition from an array representation.
    /// 
    /// The array should be in normalized form where:
    /// - Negative values represent root elements (negative of block size)
    /// - Non-negative values represent parent pointers
    /// 
    /// # Arguments
    /// * `array` - The array representation of the partition
    /// 
    /// # Returns
    /// * `Ok(Partition)` - Successfully created partition
    /// * `Err(String)` - Invalid array representation
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::partition::Partition;
    /// 
    /// let partition = Partition::new(vec![-2, 0, -1]).unwrap();
    /// assert_eq!(partition.universe_size(), 3);
    /// ```
    pub fn new(array: Vec<i32>) -> Result<Self, String> {
        if array.is_empty() {
            return Err("Partition array cannot be empty".to_string());
        }
        
        let mut partition = Partition {
            array,
            block_count: -1,
            representatives: None,
        };
        
        partition.normalize();
        Ok(partition)
    }
    
    /// Create a new partition from a string representation.
    /// 
    /// Supports both bracket notation `[[1 2][3 4 5]]` and bar notation `|1 2|3 4 5|`.
    /// 
    /// # Arguments
    /// * `str` - String representation of the partition
    /// 
    /// # Returns
    /// * `Ok(Partition)` - Successfully created partition
    /// * `Err(String)` - Invalid string format
    pub fn from_string(str: &str) -> Result<Self, String> {
        Self::from_string_with_length(str, -1)
    }
    
    /// Create a new partition from a string representation with specified length.
    /// 
    /// If length is non-negative, converts str into a partition on 0 to length-1,
    /// ignoring any integer in str greater than length-1.
    /// 
    /// # Arguments
    /// * `str` - String representation of the partition
    /// * `length` - Maximum universe size (-1 for auto-detect)
    /// 
    /// # Returns
    /// * `Ok(Partition)` - Successfully created partition
    /// * `Err(String)` - Invalid string format
    pub fn from_string_with_length(str: &str, length: i32) -> Result<Self, String> {
        let array = Self::string_to_partition(str, length)?;
        Self::new(array)
    }
    
    /// Create the zero partition (all elements in separate blocks).
    /// 
    /// # Arguments
    /// * `size` - Size of the universe
    /// 
    /// # Returns
    /// * `Partition` - Zero partition
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::partition::Partition;
    /// 
    /// let zero = Partition::zero(3);
    /// assert_eq!(zero.number_of_blocks(), 3);
    /// ```
    pub fn zero(size: usize) -> Self {
        let array = vec![-1; size];
        Self {
            array,
            block_count: size as i32,
            representatives: None,
        }
    }
    
    /// Create the one partition (all elements in one block).
    /// 
    /// # Arguments
    /// * `size` - Size of the universe
    /// 
    /// # Returns
    /// * `Partition` - One partition
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::partition::Partition;
    /// 
    /// let one = Partition::one(3);
    /// assert_eq!(one.number_of_blocks(), 1);
    /// ```
    pub fn one(size: usize) -> Self {
        if size == 0 {
            return Self::zero(0);
        }
        
        let mut array = vec![0; size];
        array[0] = -(size as i32);
        Self {
            array,
            block_count: 1,
            representatives: None,
        }
    }
    
    /// Get the universe size (number of elements).
    pub fn universe_size(&self) -> usize {
        self.array.len()
    }
    
    /// Get the number of blocks in the partition.
    pub fn number_of_blocks(&self) -> usize {
        if self.block_count < 0 {
            let count = self.array.iter().filter(|&&x| x < 0).count();
            // Note: We can't mutate self here, so we'll compute each time
            // In a real implementation, we might use interior mutability
            count
        } else {
            self.block_count as usize
        }
    }
    
    /// Check if two elements are related (in the same block).
    /// 
    /// # Arguments
    /// * `i` - First element
    /// * `j` - Second element
    /// 
    /// # Returns
    /// * `true` if elements are in the same block
    /// * `false` otherwise
    pub fn is_related(&self, i: usize, j: usize) -> bool {
        if i >= self.array.len() || j >= self.array.len() {
            return false;
        }
        self.representative(i) == self.representative(j)
    }
    
    /// Get the representative (root) of the block containing element i.
    /// 
    /// # Arguments
    /// * `i` - Element index
    /// 
    /// # Returns
    /// * Representative element index
    pub fn representative(&self, i: usize) -> usize {
        if i >= self.array.len() {
            return i;
        }
        
        let mut current = i;
        while self.array[current] >= 0 {
            current = self.array[current] as usize;
        }
        current
    }
    
    /// Check if an element is a representative (root) of its block.
    /// 
    /// # Arguments
    /// * `i` - Element index
    /// 
    /// # Returns
    /// * `true` if element is a representative
    /// * `false` otherwise
    pub fn is_representative(&self, i: usize) -> bool {
        if i >= self.array.len() {
            return true;
        }
        self.array[i] < 0
    }
    
    /// Get all representatives of the partition.
    /// 
    /// # Returns
    /// * Vector of representative indices
    pub fn representatives(&self) -> Vec<usize> {
        if let Some(ref reps) = self.representatives {
            return reps.clone();
        }
        
        let mut reps = Vec::new();
        for i in 0..self.array.len() {
            if self.is_representative(i) {
                reps.push(i);
            }
        }
        reps
    }
    
    /// Get the index of the block containing element i.
    /// 
    /// This will be the index in the quotient structure of i modulo this partition.
    /// 
    /// # Arguments
    /// * `i` - Element index
    /// 
    /// # Returns
    /// * Block index
    pub fn block_index(&self, i: usize) -> Result<usize, String> {
        let rep = self.representative(i);
        let reps = self.representatives();
        reps.binary_search(&rep).map_err(|_| "Element not found in representatives".to_string())
    }
    
    /// Get the blocks of the partition as an array of arrays.
    /// 
    /// # Returns
    /// * Vector of blocks, where each block is a vector of element indices
    pub fn get_blocks(&self) -> Vec<Vec<usize>> {
        let mut blocks: Vec<Vec<usize>> = vec![Vec::new(); self.array.len()];
        
        for i in 0..self.array.len() {
            let rep = self.representative(i);
            blocks[rep].push(i);
        }
        
        blocks.into_iter().filter(|block| !block.is_empty()).collect()
    }
    
    /// Join two blocks by their representatives.
    /// 
    /// # Arguments
    /// * `r` - Representative of first block
    /// * `s` - Representative of second block
    /// 
    /// # Panics
    /// Panics if r or s are not representatives or if r == s
    pub fn join_blocks(&mut self, r: usize, s: usize) {
        if r == s {
            panic!("Cannot join a block with itself");
        }
        if !self.is_representative(r) || !self.is_representative(s) {
            panic!("Both arguments must be representatives");
        }
        
        let size_r = (-self.array[r]) as usize;
        let size_s = (-self.array[s]) as usize;
        
        if size_r < size_s {
            self.array[r] = s as i32;
            self.array[s] = -((size_r + size_s) as i32);
        } else {
            self.array[s] = r as i32;
            self.array[r] = -((size_r + size_s) as i32);
        }
        
        // Invalidate cached values
        self.block_count = -1;
        self.representatives = None;
    }
    
    /// Compute the join of two partitions.
    /// 
    /// # Arguments
    /// * `other` - Other partition to join with
    /// 
    /// # Returns
    /// * `Ok(Partition)` - Join of the two partitions
    /// * `Err(String)` - Partitions have different universe sizes
    pub fn join(&self, other: &Partition) -> Result<Partition, String> {
        if self.universe_size() != other.universe_size() {
            return Err("Partitions must have the same universe size".to_string());
        }
        
        let mut result_array = other.array.clone();
        
        for i in 0..self.array.len() {
            if self.array[i] >= 0 {
                let r = self.root(i);
                let s = other.root(i);
                if r != s {
                    Self::join_blocks_static(r, s, &mut result_array);
                }
            }
        }
        
        let mut result = Partition {
            array: result_array,
            block_count: -1,
            representatives: None,
        };
        result.normalize();
        Ok(result)
    }
    
    /// Compute the meet of two partitions.
    /// 
    /// # Arguments
    /// * `other` - Other partition to meet with
    /// 
    /// # Returns
    /// * `Ok(Partition)` - Meet of the two partitions
    /// * `Err(String)` - Partitions have different universe sizes
    pub fn meet(&self, other: &Partition) -> Result<Partition, String> {
        if self.universe_size() != other.universe_size() {
            return Err("Partitions must have the same universe size".to_string());
        }
        
        let mut ht: HashMap<(usize, usize), usize> = HashMap::new();
        let mut result_array = vec![-1; self.array.len()];
        
        for i in 0..self.array.len() {
            let root_pair = (self.root(i), other.root(i));
            
            if let Some(&root_int) = ht.get(&root_pair) {
                result_array[root_int] -= 1;
                result_array[i] = root_int as i32;
            } else {
                ht.insert(root_pair, i);
                result_array[i] = -1;
            }
        }
        
        Ok(Partition {
            array: result_array,
            block_count: -1,
            representatives: None,
        })
    }
    
    /// Check if this partition is less than or equal to another partition.
    /// 
    /// # Arguments
    /// * `other` - Other partition to compare with
    /// 
    /// # Returns
    /// * `true` if this partition refines the other
    /// * `false` otherwise
    pub fn leq(&self, other: &Partition) -> bool {
        if self.universe_size() != other.universe_size() {
            return false;
        }
        
        for i in 0..self.array.len() {
            if self.array[i] >= 0 && other.root(i) != other.root(self.root(i)) {
                return false;
            }
        }
        true
    }
    
    /// Normalize the partition representation.
    /// 
    /// Ensures that roots are the smallest elements in their blocks
    /// and all elements point directly to their roots (path compression).
    pub fn normalize(&mut self) {
        // Validate the partition before normalizing
        if !self.is_valid_partition() {
            return; // Skip normalization for invalid partitions
        }
        
        Self::normalize_array(&mut self.array);
        
        // Perform path compression: make all elements point directly to their root
        for i in 0..self.array.len() {
            if self.array[i] >= 0 {
                let root = self.representative(i);
                self.array[i] = root as i32;
            }
        }
        
        self.block_count = -1;
        self.representatives = None;
    }
    
    /// Check if this partition is valid (no cycles, proper structure).
    fn is_valid_partition(&self) -> bool {
        if self.array.is_empty() {
            return false;
        }
        
        // Check for cycles by trying to find roots for all elements
        for i in 0..self.array.len() {
            let mut current = i;
            let mut visited = std::collections::HashSet::new();
            
            while self.array[current] >= 0 {
                if !visited.insert(current) {
                    return false; // Cycle detected
                }
                current = self.array[current] as usize;
                if current >= self.array.len() {
                    return false; // Out of bounds
                }
            }
        }
        true
    }
    
    /// Check if this is the zero partition (all elements in separate blocks).
    pub fn is_zero(&self) -> bool {
        self.array.iter().all(|&x| x == -1)
    }
    
    /// Check if this partition is uniform (all blocks have the same size).
    pub fn is_uniform(&self) -> bool {
        if self.array.is_empty() {
            return true;
        }
        
        let first_block_size = self.array[0];  // negative of the size of the first block
        self.array.iter().all(|&x| x >= 0 || x == first_block_size)
    }
    
    /// Check if this partition is in initial lexicographic representative form.
    /// 
    /// This means that when separators are removed, it's just 0 to n-1 in order,
    /// and block sizes are decreasing from left to right.
    pub fn is_initial_lex_representative(&self) -> bool {
        let mut current_root = 0;
        let mut current_block_size = self.array[0];  // negative of the size of the first block
        
        for i in 1..self.array.len() {
            if self.array[i] < 0 {
                if self.array[i] > current_block_size {
                    return false;
                }
                current_block_size = self.array[i];
                current_root = i;
            } else if self.array[i] != current_root as i32 {
                return false;
            }
        }
        true
    }
    
    /// Get the array representation of the partition.
    pub fn to_array(&self) -> Vec<i32> {
        self.array.clone()
    }
    
    /// Get the rank of the partition (universe size - number of blocks).
    pub fn rank(&self) -> usize {
        self.universe_size() - self.number_of_blocks()
    }
    
    // Private helper methods
    
    /// Find the root of element i, with path compression.
    fn root(&self, i: usize) -> usize {
        if i >= self.array.len() {
            return i;
        }
        
        let mut current = i;
        while self.array[current] >= 0 {
            current = self.array[current] as usize;
        }
        current
    }
    
    /// Static version of root finding for use with mutable arrays.
    fn root_static(i: usize, part: &[i32]) -> usize {
        if i >= part.len() {
            return i;
        }
        
        let mut current = i;
        let mut visited = std::collections::HashSet::new();
        
        while part[current] >= 0 {
            // Check for infinite loop
            if !visited.insert(current) {
                // We've seen this index before, indicating a cycle
                return current; // Return the current index to break the cycle
            }
            
            current = part[current] as usize;
            
            // Safety check to prevent infinite loops
            if current >= part.len() {
                return i; // Return original index if we go out of bounds
            }
        }
        current
    }
    
    /// Static version of join_blocks for use with mutable arrays.
    fn join_blocks_static(r: usize, s: usize, part: &mut [i32]) {
        let size_r = (-part[r]) as usize;
        let size_s = (-part[s]) as usize;
        
        if size_r < size_s {
            part[r] = s as i32;
            part[s] = -((size_r + size_s) as i32);
        } else {
            part[s] = r as i32;
            part[r] = -((size_r + size_s) as i32);
        }
    }
    
    /// Normalize an array representation.
    fn normalize_array(part: &mut [i32]) {
        let size = part.len();
        
        // First pass: make roots the smallest elements in their blocks
        for i in 0..size {
            let r = Self::root_static(i, part);
            if r > i {
                part[i] = part[r];
                part[r] = i as i32;
            }
        }
        
        // Second pass: path compression
        for i in 0..size {
            Self::root_static(i, part);
        }
    }
    
    /// Convert string to partition array representation.
    fn string_to_partition(str: &str, length: i32) -> Result<Vec<i32>, String> {
        let str = str.trim();
        let mut blocks: Option<Vec<BTreeSet<i32>>> = None;
        let mut strings: Option<Vec<String>> = None;
        let mut blk_count = -1;
        
        // Parse bar notation: |1 2|3 4 5|
        if str.starts_with('|') && str.ends_with('|') {
            let content = &str[1..str.len()-1];
            strings = Some(content.split('|').map(|s| s.to_string()).collect());
            blk_count = strings.as_ref().unwrap().len() as i32;
            blocks = Some(Vec::new());
        }
        // Parse bracket notation: [[1 2][3 4 5]]
        else if str.starts_with("[[") && str.ends_with("]]") {
            let content = &str[2..str.len()-2].trim();
            if !content.starts_with('[') {
                return Err("Not a valid partition string".to_string());
            }
            strings = Some(content[1..].split("][").map(|s| s.to_string()).collect());
            blk_count = strings.as_ref().unwrap().len() as i32;
            blocks = Some(Vec::new());
        }
        
        if let (Some(mut blocks), Some(strings)) = (blocks, strings) {
            for i in 0..blk_count as usize {
                blocks.push(Self::block_string_to_set(&strings[i])?);
            }
            
            let size = if length < 0 {
                blocks.iter().map(|block| block.len()).sum()
            } else {
                length as usize
            };
            
            let mut ans = vec![-1; size];
            for block in &blocks {
                for &i in block {
                    if i < size as i32 {
                        if i == *block.iter().next().unwrap() {
                            ans[i as usize] = -(block.len() as i32);
                        } else {
                            ans[i as usize] = *block.iter().next().unwrap();
                        }
                    }
                }
            }
            return Ok(ans);
        }
        
        Err("Invalid partition string format".to_string())
    }
    
    /// Convert a block string to a set of integers.
    fn block_string_to_set(blk_str: &str) -> Result<BTreeSet<i32>, String> {
        let blk_str = blk_str.trim();
        let mut blk_str = blk_str.to_string();
        
        // Remove trailing brackets
        if let Some(idx) = blk_str.find(']') {
            blk_str = blk_str[..idx].to_string();
            if let Some(idx) = blk_str.find(']') {
                blk_str = blk_str[..idx].to_string();
            }
        }
        
        let mut ans = BTreeSet::new();
        let elts: Vec<&str> = blk_str.split(|c: char| c.is_whitespace() || c == ',').collect();
        
        for elt in elts {
            if !elt.is_empty() {
                let num = elt.parse::<i32>()
                    .map_err(|_| format!("Invalid number: {}", elt))?;
                ans.insert(num);
            }
        }
        
        Ok(ans)
    }
}

impl fmt::Display for Partition {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.to_string_with_type(PrintType::Block, -1).fmt(f)
    }
}

impl Partition {
    /// Convert to string with specified print type and maximum length.
    pub fn to_string_with_type(&self, kind: PrintType, max_len: i32) -> String {
        match kind {
            PrintType::Internal => Self::int_array_to_string(&self.array),
            PrintType::Ewk => Self::part_to_kiss_string(&self.array),
            PrintType::Block => Self::part_to_block_string(&self.array, max_len),
            PrintType::SqBraceBlock => Self::part_to_block_string_with_brackets(&self.array, max_len),
            PrintType::Human => {
                let block_str = Self::part_to_block_string(&self.array, max_len);
                format!("{} ({} block(s))", block_str, self.number_of_blocks())
            }
        }
    }
    
    /// Convert to string with specified print type.
    pub fn to_string_with_print_type(&self, kind: PrintType) -> String {
        self.to_string_with_type(kind, -1)
    }
    
    /// Convert to string with maximum length.
    pub fn to_string_with_max_len(&self, max_len: i32) -> String {
        self.to_string_with_type(PrintType::Block, max_len)
    }
    
    /// Convert int array to string representation.
    fn int_array_to_string(array: &[i32]) -> String {
        if array.is_empty() {
            return "[]".to_string();
        }
        
        let mut result = String::from("[");
        for (i, &val) in array.iter().enumerate() {
            if i > 0 {
                result.push_str(", ");
            }
            result.push_str(&val.to_string());
        }
        result.push(']');
        result
    }
    
    /// Convert partition to KISS string format.
    fn part_to_kiss_string(part: &[i32]) -> String {
        let mut result = String::from(",");
        for i in 0..part.len() {
            result.push_str(&Self::root_static(i, part).to_string());
            result.push(',');
        }
        if result.len() > 1 {
            result.pop(); // Remove trailing comma
        }
        result
    }
    
    /// Convert partition to block string format.
    fn part_to_block_string(part: &[i32], max_len: i32) -> String {
        Self::part_to_block_string_with_delimiters(part, "|", "|", "|", max_len)
    }
    
    /// Convert partition to block string format with custom brackets.
    fn part_to_block_string_with_brackets(part: &[i32], max_len: i32) -> String {
        Self::part_to_block_string_with_delimiters(part, "[[", "],[", "]]", max_len)
    }
    
    /// Convert partition to block string format with custom delimiters.
    fn part_to_block_string_with_delimiters(
        part: &[i32],
        left: &str,
        middle: &str,
        end: &str,
        max_len: i32,
    ) -> String {
        let mut blocks: Vec<Vec<usize>> = vec![Vec::new(); part.len()];
        
        for i in 0..part.len() {
            let r = Self::root_static(i, part);
            blocks[r].push(i);
        }
        
        let mut result = String::from(left);
        let mut first = true;
        
        for i in 0..part.len() {
            if blocks[i].is_empty() {
                continue;
            }
            
            let mut block_first = true;
            for &elem in &blocks[i] {
                if max_len > 0 && result.len() > max_len as usize {
                    return format!("{} ...", result);
                }
                
                if !first && !block_first {
                    result.push(',');
                } else if first {
                    first = false;
                }
                block_first = false;
                
                result.push_str(&elem.to_string());
            }
            
            result.push_str(middle);
        }
        
        // Replace the last middle with end
        if result.ends_with(middle) {
            let end_pos = result.len() - middle.len();
            result.truncate(end_pos);
            result.push_str(end);
        }
        
        result
    }
    
    /// Calculate unary polymorphisms of a collection of partitions.
    /// 
    /// A unary polymorphism is a function f: {0,...,n-1} -> {0,...,n-1} that
    /// preserves all partitions in the collection, meaning if elements a and b
    /// are related in a partition, then f(a) and f(b) are also related.
    /// 
    /// # Arguments
    /// * `pars` - Collection of partitions to respect
    /// 
    /// # Returns
    /// * `Ok(BTreeSet<IntArray>)` - Set of all unary polymorphisms
    /// * `Err(String)` - Error if partitions are empty or have different sizes
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::partition::Partition;
    /// 
    /// let pars = vec![Partition::zero(3), Partition::one(3)];
    /// let polys = Partition::unary_polymorphisms(&pars).unwrap();
    /// assert!(polys.len() > 0);
    /// ```
    pub fn unary_polymorphisms(pars: &[Partition]) -> Result<BTreeSet<IntArray>, String> {
        if pars.is_empty() {
            return Err("Partition list cannot be empty".to_string());
        }
        
        let n = pars[0].universe_size();
        
        // Validate all partitions have the same universe size
        for (i, par) in pars.iter().enumerate() {
            if par.universe_size() != n {
                return Err(format!(
                    "Partition {} has universe size {} but expected {}",
                    i,
                    par.universe_size(),
                    n
                ));
            }
        }
        
        let mut set = BTreeSet::new();
        let mut ia = IntArray::from_array(vec![0; n]).unwrap();
        Self::unary_polymorphisms_aux(&mut ia, 0, n, &mut set, pars);
        
        Ok(set)
    }
    
    /// Recursive helper for calculating unary polymorphisms.
    /// 
    /// Find all functions respecting the partitions and extending the partial
    /// function arr and add them to the answer set.
    /// 
    /// # Arguments
    /// * `arr` - Vector representing the partial function f defined for i < k
    /// * `k` - The first place the function is not defined
    /// * `n` - The size of the underlying set for the partitions
    /// * `ans` - The answer set
    /// * `pars` - The list of partitions
    fn unary_polymorphisms_aux(
        arr: &mut IntArray,
        k: usize,
        n: usize,
        ans: &mut BTreeSet<IntArray>,
        pars: &[Partition],
    ) {
        if k == n {
            // We have a complete function, add it to the answer set
            ans.insert(arr.clone());
            return;
        }
        
        // Try each possible value for position k
        for value in 0..n {
            if Self::respects_unary(arr, k, value as i32, pars) {
                let _ = arr.set(k, value as i32);
                Self::unary_polymorphisms_aux(arr, k + 1, n, ans, pars);
            }
        }
    }
    
    /// Check if a partial function respects the partitions.
    /// 
    /// # Arguments
    /// * `partial_function` - The partial function being built
    /// * `k` - The position being considered
    /// * `value` - The value to try for position k
    /// * `pars` - The list of partitions to respect
    /// 
    /// # Returns
    /// `true` if setting partial_function[k] = value respects all partitions
    fn respects_unary(
        partial_function: &IntArray,
        k: usize,
        value: i32,
        pars: &[Partition],
    ) -> bool {
        for par in pars {
            let r = par.representative(k);
            for i in 0..k {
                if r == par.representative(i) {
                    // k and i are in the same block, so their images must be related
                    let img = partial_function.get(i).unwrap_or(0) as usize;
                    if !par.is_related(value as usize, img) {
                        return false;
                    }
                }
            }
        }
        true
    }
    
    /// Calculate binary polymorphisms of a collection of partitions.
    /// 
    /// A binary polymorphism is a binary operation that preserves all partitions
    /// in the collection. The operation is represented as a function table of size n*n.
    /// 
    /// # Arguments
    /// * `pars` - Collection of partitions to respect
    /// * `unary_clone` - Optional precomputed set of unary polymorphisms (for efficiency)
    /// 
    /// # Returns
    /// * `Ok(BTreeSet<IntArray>)` - Set of all binary polymorphisms
    /// * `Err(String)` - Error if partitions are empty or have different sizes
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::partition::Partition;
    /// 
    /// let pars = vec![Partition::zero(3), Partition::one(3)];
    /// let polys = Partition::binary_polymorphisms(&pars, None).unwrap();
    /// assert!(polys.len() > 0);
    /// ```
    pub fn binary_polymorphisms(
        pars: &[Partition],
        unary_clone: Option<BTreeSet<IntArray>>,
    ) -> Result<BTreeSet<IntArray>, String> {
        if pars.is_empty() {
            return Err("Partition list cannot be empty".to_string());
        }
        
        let n = pars[0].universe_size();
        
        // Validate all partitions have the same universe size
        for (i, par) in pars.iter().enumerate() {
            if par.universe_size() != n {
                return Err(format!(
                    "Partition {} has universe size {} but expected {}",
                    i,
                    par.universe_size(),
                    n
                ));
            }
        }
        
        // Compute unary clone if not provided
        let unary_clone = match unary_clone {
            Some(uc) => uc,
            None => Self::unary_polymorphisms(pars)?,
        };
        
        let mut set = BTreeSet::new();
        let mut partial_op: Vec<Option<IntArray>> = vec![None; n];
        
        Self::binary_polymorphisms_aux(&mut partial_op, 0, n, &unary_clone, &mut set);
        
        Ok(set)
    }
    
    /// Recursive helper for calculating binary polymorphisms.
    /// 
    /// # Arguments
    /// * `partial_op` - List of rows (each is a unary function)
    /// * `index` - Current row index being filled
    /// * `n` - Size of the universe
    /// * `unary_clone` - Set of valid unary polymorphisms
    /// * `set` - Result set to populate
    fn binary_polymorphisms_aux(
        partial_op: &mut Vec<Option<IntArray>>,
        index: usize,
        n: usize,
        unary_clone: &BTreeSet<IntArray>,
        set: &mut BTreeSet<IntArray>,
    ) {
        if index == n {
            // We have a complete binary operation, convert to flat array
            let mut op = vec![0; n * n];
            for i in 0..n {
                if let Some(ref row) = partial_op[i] {
                    for j in 0..n {
                        op[i * n + j] = row.get(j).unwrap_or(0);
                    }
                }
            }
            set.insert(IntArray::from_array(op).unwrap());
            return;
        }
        
        // Try each unary function as the next row
        for unary_fn in unary_clone.iter() {
            if Self::respects_binary(partial_op, index, n, unary_fn, unary_clone) {
                partial_op[index] = Some(unary_fn.clone());
                Self::binary_polymorphisms_aux(partial_op, index + 1, n, unary_clone, set);
            }
        }
    }
    
    /// Check if adding a unary function as a row respects the binary operation constraints.
    /// 
    /// # Arguments
    /// * `partial_binary_op` - List of index-many rows
    /// * `index` - Current row being considered
    /// * `n` - Size of the universe
    /// * `unary_op` - Possible row to add
    /// * `unary_clone` - Set of valid unary polymorphisms
    /// 
    /// # Returns
    /// `true` if adding unary_op at index is consistent
    fn respects_binary(
        partial_binary_op: &[Option<IntArray>],
        index: usize,
        n: usize,
        unary_op: &IntArray,
        unary_clone: &BTreeSet<IntArray>,
    ) -> bool {
        let mut ia = IntArray::from_array(vec![0; n]).unwrap();
        
        // For each column
        for col in 0..n {
            // Build the column vector up to and including index
            for i in 0..index {
                if let Some(ref row) = partial_binary_op[i] {
                    let _ = ia.set(i, row.get(col).unwrap_or(0));
                }
            }
            let _ = ia.set(index, unary_op.get(col).unwrap_or(0));
            
            // Check if this initial segment is in unary_clone
            if !Self::is_initial_member(&ia, index, unary_clone) {
                return false;
            }
        }
        
        true
    }
    
    /// Check if an initial segment of an array is a member of unary_clone.
    /// 
    /// # Arguments
    /// * `ia` - The array to check
    /// * `index` - The length of the initial segment (0..=index)
    /// * `unary_clone` - Set of unary polymorphisms
    /// 
    /// # Returns
    /// `true` if there exists an element in unary_clone that matches ia on positions 0..=index
    fn is_initial_member(
        ia: &IntArray,
        index: usize,
        unary_clone: &BTreeSet<IntArray>,
    ) -> bool {
        // Find the ceiling (smallest element >= ia in lexicographic order)
        // BTreeSet doesn't have ceiling directly, so we use range
        for candidate in unary_clone.range(ia..) {
            // Check if it matches on the initial segment
            for i in 0..=index {
                if candidate.get(i) != ia.get(i) {
                    return false;
                }
            }
            return true;
        }
        false
    }
}

impl PartialEq for Partition {
    fn eq(&self, other: &Self) -> bool {
        self.array == other.array
    }
}

impl Eq for Partition {}

impl Hash for Partition {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.array.hash(state);
    }
}

impl PartialOrd for Partition {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Partition {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        // Compare by number of blocks first, then by array values
        let block_diff = other.number_of_blocks() as i32 - self.number_of_blocks() as i32;
        if block_diff != 0 {
            return block_diff.cmp(&0);
        }
        
        for (a, b) in self.array.iter().zip(other.array.iter()) {
            let diff = a - b;
            if diff != 0 {
                return diff.cmp(&0);
            }
        }
        
        std::cmp::Ordering::Equal
    }
}

// BinaryRelation trait implementation for Partition
impl BinaryRelation<IntArray> for Partition {
    fn universe_size(&self) -> usize {
        self.universe_size()
    }
    
    fn is_related(&self, i: usize, j: usize) -> bool {
        self.is_related(i, j)
    }
    
    fn get_pairs(&self) -> BTreeSet<IntArray> {
        let mut pairs = BTreeSet::new();
        
        // Generate all pairs (i, j) where i and j are in the same block
        for i in 0..self.universe_size() {
            for j in 0..self.universe_size() {
                if self.is_related(i, j) {
                    let pair = IntArray::from_array(vec![i as i32, j as i32]).unwrap();
                    pairs.insert(pair);
                }
            }
        }
        
        pairs
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
        
        // For each pair (i, j) in this partition
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

impl BinaryRelationCompare<IntArray> for Partition {}

impl BinaryRelationIterator<IntArray> for Partition {
    fn pairs(&self) -> std::collections::btree_set::IntoIter<IntArray> {
        self.get_pairs().into_iter()
    }
}

impl BinaryRelationFactory<IntArray> for Partition {
    fn identity(size: usize) -> Result<Box<dyn BinaryRelation<IntArray>>, String> {
        Ok(Box::new(Self::zero(size)))
    }
    
    fn universal(size: usize) -> Result<Box<dyn BinaryRelation<IntArray>>, String> {
        Ok(Box::new(Self::one(size)))
    }
    
    fn empty(size: usize) -> Result<Box<dyn BinaryRelation<IntArray>>, String> {
        Ok(Box::new(Self::zero(size)))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_zero_partition() {
        let zero = Partition::zero(3);
        assert_eq!(zero.universe_size(), 3);
        assert_eq!(zero.number_of_blocks(), 3);
        assert!(zero.is_zero());
        assert!(!zero.is_related(0, 1));
        assert!(!zero.is_related(0, 2));
        assert!(!zero.is_related(1, 2));
    }
    
    #[test]
    fn test_one_partition() {
        let one = Partition::one(3);
        assert_eq!(one.universe_size(), 3);
        assert_eq!(one.number_of_blocks(), 1);
        assert!(one.is_related(0, 1));
        assert!(one.is_related(0, 2));
        assert!(one.is_related(1, 2));
    }
    
    #[test]
    fn test_join_blocks() {
        let mut partition = Partition::zero(4);
        partition.join_blocks(0, 1);
        assert_eq!(partition.number_of_blocks(), 3);
        assert!(partition.is_related(0, 1));
        assert!(!partition.is_related(0, 2));
    }
    
    #[test]
    fn test_join_partitions() {
        let p1 = Partition::new(vec![-2, 0, -1, -1]).unwrap();
        let p2 = Partition::new(vec![-1, -1, -2, 2]).unwrap();
        let join = p1.join(&p2).unwrap();
        assert_eq!(join.number_of_blocks(), 2);
        assert!(join.is_related(0, 1));
        assert!(join.is_related(2, 3));
    }
    
    #[test]
    fn test_meet_partitions() {
        let p1 = Partition::new(vec![-2, 0, -1, -1]).unwrap();
        let p2 = Partition::new(vec![-1, -1, -2, 2]).unwrap();
        let meet = p1.meet(&p2).unwrap();
        assert_eq!(meet.number_of_blocks(), 4);
        assert!(!meet.is_related(0, 1));
        assert!(!meet.is_related(2, 3));
    }
    
    #[test]
    fn test_leq() {
        let p1 = Partition::new(vec![-2, 0, -1, -1]).unwrap(); // {0,1}, {2}, {3}
        let p2 = Partition::one(4); // {0,1,2,3}
        assert!(p1.leq(&p2));
        assert!(!p2.leq(&p1));
    }
    
    #[test]
    fn test_from_string() {
        let partition = Partition::from_string("|0 1|2 3|").unwrap();
        assert_eq!(partition.universe_size(), 4);
        assert_eq!(partition.number_of_blocks(), 2);
        assert!(partition.is_related(0, 1));
        assert!(partition.is_related(2, 3));
        assert!(!partition.is_related(0, 2));
    }
    
    #[test]
    fn test_representatives() {
        let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
        let reps = partition.representatives();
        assert_eq!(reps.len(), 3);
        assert!(reps.contains(&0));
        assert!(reps.contains(&2));
        assert!(reps.contains(&3));
    }
    
    #[test]
    fn test_get_blocks() {
        let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
        let blocks = partition.get_blocks();
        assert_eq!(blocks.len(), 3);
        assert!(blocks.iter().any(|block| block == &vec![0, 1]));
        assert!(blocks.iter().any(|block| block == &vec![2]));
        assert!(blocks.iter().any(|block| block == &vec![3]));
    }
    
    #[test]
    fn test_to_string() {
        let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
        let s = partition.to_string();
        assert!(s.contains("0,1"));
        assert!(s.contains("2"));
        assert!(s.contains("3"));
    }
}
