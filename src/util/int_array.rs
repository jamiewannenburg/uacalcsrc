/*! IntArray trait and implementation.

This module provides a trait and concrete implementation for working with arrays of integers,
primarily for use in constraint satisfaction and binary relation operations.

The implementation is based on the Java `org.uacalc.util.IntArray` class.
*/

use std::collections::HashSet;
use std::fmt;
use std::hash::Hash;
use crate::alg::conlat::partition::Partition;

/// Trait for integer array operations.
/// 
/// This trait defines the interface for working with arrays of integers,
/// providing methods for constraint checking, equality, and basic operations.
pub trait IntArrayTrait {
    /// Get the size of the universe (array length).
    fn universe_size(&self) -> usize;
    
    /// Get the underlying array as a slice.
    fn as_slice(&self) -> &[i32];
    
    /// Get a value at the specified index.
    /// 
    /// # Arguments
    /// * `index` - The index to access
    /// 
    /// # Returns
    /// * `Some(i32)` - The value at the index
    /// * `None` - If the index is out of bounds
    fn get(&self, index: usize) -> Option<i32>;
    
    /// Set a value at the specified index.
    /// 
    /// # Arguments
    /// * `index` - The index to set
    /// * `value` - The value to set
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully set the value
    /// * `Err(String)` - If the index is out of bounds
    fn set(&mut self, index: usize, value: i32) -> Result<(), String>;
    
    /// Test if the array is constant on each block of the partition.
    /// 
    /// # Arguments
    /// * `blocks` - The blocks of a partition on the index set
    /// 
    /// # Returns
    /// * `true` if the condition is satisfied
    fn satisfies_blocks_constraint(&self, blocks: &[Vec<usize>]) -> bool;
    
    /// Test if this satisfies array[i] = v for each [i,v] in values.
    /// 
    /// # Arguments
    /// * `values` - An array of pairs [i,v] specifying array[i] = v
    /// 
    /// # Returns
    /// * `true` if the condition is satisfied
    fn satisfies_values_constraint(&self, values: &[(usize, i32)]) -> bool;
    
    /// Test if this IntArray value at index is in a set of possible values.
    /// 
    /// # Arguments
    /// * `index` - The index to test
    /// * `possible_values` - A set of possible values
    /// 
    /// # Returns
    /// * `true` if the value at index is in the set
    fn satisfies_set_constraint(&self, index: usize, possible_values: &HashSet<i32>) -> bool;
    
    /// Test if this IntArray's value at index is congruent mod alpha to the element with index elem_index.
    /// 
    /// # Arguments
    /// * `index` - The index to test
    /// * `alpha` - The partition defining the congruence
    /// * `elem_index` - The element index to compare with
    /// 
    /// # Returns
    /// * `true` if the condition is satisfied
    fn satisfies_congruence_constraint(&self, index: usize, alpha: &Partition, elem_index: usize) -> bool;
    
    /// Test if this represents an idempotent function.
    /// 
    /// A function f is idempotent if f(f(x)) = f(x) for all x.
    /// 
    /// # Returns
    /// * `true` if the function is idempotent
    fn is_idempotent(&self) -> bool;
    
    /// Test if this array is constant (all elements are the same).
    /// 
    /// # Returns
    /// * `true` if all elements are the same
    fn is_constant(&self) -> bool;
    
    /// Clone the array into a new instance.
    fn clone_array(&self) -> Box<dyn IntArrayTrait>;
}

/// Concrete implementation of IntArrayTrait using Vec<i32>.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct IntArray {
    /// The underlying array
    array: Vec<i32>,
    /// The size of the universe
    size: usize,
}

impl IntArray {
    /// Create a new IntArray with the given size, initialized to 0.
    /// 
    /// # Arguments
    /// * `size` - The size of the array
    /// 
    /// # Returns
    /// * `Ok(IntArray)` - Successfully created array
    /// * `Err(String)` - If size is invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::int_array::{IntArray, IntArrayTrait};
    /// 
    /// let array = IntArray::new(5).unwrap();
    /// assert_eq!(array.universe_size(), 5);
    /// ```
    pub fn new(size: usize) -> Result<Self, String> {
        if size == 0 {
            return Err("Array size cannot be zero".to_string());
        }
        
        Ok(IntArray {
            array: vec![0; size],
            size,
        })
    }
    
    /// Create a new IntArray from an existing array.
    /// 
    /// # Arguments
    /// * `array` - The array to wrap
    /// 
    /// # Returns
    /// * `Ok(IntArray)` - Successfully created array
    /// * `Err(String)` - If array is empty
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::int_array::{IntArray, IntArrayTrait};
    /// 
    /// let array = IntArray::from_array(vec![1, 2, 3]).unwrap();
    /// assert_eq!(array.universe_size(), 3);
    /// ```
    pub fn from_array(array: Vec<i32>) -> Result<Self, String> {
        if array.is_empty() {
            return Err("Array cannot be empty".to_string());
        }
        
        let size = array.len();
        Ok(IntArray { array, size })
    }
    
    /// Create a new IntArray from a string representation.
    /// 
    /// The string should contain integers separated by commas or spaces.
    /// 
    /// # Arguments
    /// * `str` - String representation of the array
    /// 
    /// # Returns
    /// * `Ok(IntArray)` - Successfully created array
    /// * `Err(String)` - If string format is invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::int_array::{IntArray, IntArrayTrait};
    /// 
    /// let array = IntArray::from_string("1, 2, 3").unwrap();
    /// assert_eq!(array.universe_size(), 3);
    /// ```
    pub fn from_string(str: &str) -> Result<Self, String> {
        let array = Self::string_to_array(str)?;
        Self::from_array(array)
    }
    
    /// Convert a string to an array of integers.
    /// 
    /// # Arguments
    /// * `str` - String containing integers separated by commas or spaces
    /// 
    /// # Returns
    /// * `Ok(Vec<i32>)` - Array of integers
    /// * `Err(String)` - If parsing fails
    pub fn string_to_array(str: &str) -> Result<Vec<i32>, String> {
        let trimmed = str.trim();
        if trimmed.is_empty() {
            return Err("Empty string".to_string());
        }
        
        let parts: Vec<&str> = trimmed.split(|c: char| c == ',' || c.is_whitespace())
            .filter(|s| !s.is_empty())
            .collect();
        
        if parts.is_empty() {
            return Err("No valid integers found".to_string());
        }
        
        let mut result = Vec::with_capacity(parts.len());
        for part in parts {
            match part.trim().parse::<i32>() {
                Ok(value) => result.push(value),
                Err(_) => return Err(format!("Invalid integer: {}", part)),
            }
        }
        
        Ok(result)
    }
    
    /// Convert the array to a string representation.
    /// 
    /// # Returns
    /// * `String` - String representation in format "[1, 2, 3]"
    pub fn to_string(&self) -> String {
        Self::array_to_string(&self.array)
    }
    
    /// Convert an array to a string representation.
    /// 
    /// # Arguments
    /// * `array` - The array to convert
    /// 
    /// # Returns
    /// * `String` - String representation in format "[1, 2, 3]"
    pub fn array_to_string(array: &[i32]) -> String {
        if array.is_empty() {
            return "[]".to_string();
        }
        
        let mut result = String::from("[");
        for (i, &value) in array.iter().enumerate() {
            if i > 0 {
                result.push_str(", ");
            }
            result.push_str(&value.to_string());
        }
        result.push(']');
        result
    }
    
    /// Check if two arrays are equal.
    /// 
    /// # Arguments
    /// * `a` - First array
    /// * `b` - Second array
    /// 
    /// # Returns
    /// * `true` if arrays are equal
    pub fn arrays_equal(a: &[i32], b: &[i32]) -> bool {
        a.len() == b.len() && a.iter().zip(b.iter()).all(|(x, y)| x == y)
    }
    
    /// Get a lexicographic comparator for IntArray instances.
    /// 
    /// # Returns
    /// * `fn(&IntArray, &IntArray) -> std::cmp::Ordering` - Comparator function
    pub fn lexicographic_comparator() -> fn(&IntArray, &IntArray) -> std::cmp::Ordering {
        |a, b| {
            let min_size = a.universe_size().min(b.universe_size());
            
            // Compare elements up to the minimum size
            for i in 0..min_size {
                match a.get(i).unwrap().cmp(&b.get(i).unwrap()) {
                    std::cmp::Ordering::Equal => continue,
                    other => return other,
                }
            }
            
            // If all elements up to min_size are equal, compare sizes
            a.universe_size().cmp(&b.universe_size())
        }
    }
}

impl IntArrayTrait for IntArray {
    fn universe_size(&self) -> usize {
        self.size
    }
    
    fn as_slice(&self) -> &[i32] {
        &self.array
    }
    
    fn get(&self, index: usize) -> Option<i32> {
        self.array.get(index).copied()
    }
    
    fn set(&mut self, index: usize, value: i32) -> Result<(), String> {
        if index >= self.size {
            return Err(format!("Index {} out of bounds for array of size {}", index, self.size));
        }
        self.array[index] = value;
        Ok(())
    }
    
    fn satisfies_blocks_constraint(&self, blocks: &[Vec<usize>]) -> bool {
        for block in blocks {
            if block.is_empty() {
                continue;
            }
            
            let first_index = block[0];
            if first_index >= self.size {
                return false;
            }
            
            let first_value = self.array[first_index];
            for &index in &block[1..] {
                if index >= self.size || self.array[index] != first_value {
                    return false;
                }
            }
        }
        true
    }
    
    fn satisfies_values_constraint(&self, values: &[(usize, i32)]) -> bool {
        for &(index, expected_value) in values {
            if index >= self.size || self.array[index] != expected_value {
                return false;
            }
        }
        true
    }
    
    fn satisfies_set_constraint(&self, index: usize, possible_values: &HashSet<i32>) -> bool {
        if index >= self.size {
            return false;
        }
        possible_values.contains(&self.array[index])
    }
    
    fn satisfies_congruence_constraint(&self, index: usize, alpha: &Partition, elem_index: usize) -> bool {
        if index >= self.size {
            return false;
        }
        alpha.is_related(elem_index, self.array[index] as usize)
    }
    
    fn is_idempotent(&self) -> bool {
        for i in 0..self.size {
            let j = self.array[i];
            if j < 0 || j as usize >= self.size {
                return false;
            }
            if self.array[j as usize] != j {
                return false;
            }
        }
        true
    }
    
    fn is_constant(&self) -> bool {
        if self.size == 0 {
            return true;
        }
        let first_value = self.array[0];
        self.array.iter().all(|&value| value == first_value)
    }
    
    fn clone_array(&self) -> Box<dyn IntArrayTrait> {
        Box::new(self.clone())
    }
}

// PartialEq, Eq, Hash, PartialOrd, and Ord are now derived

impl fmt::Display for IntArray {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;
    
    #[test]
    fn test_new() {
        let array = IntArray::new(5).unwrap();
        assert_eq!(array.universe_size(), 5);
        assert_eq!(array.as_slice(), &[0, 0, 0, 0, 0]);
    }
    
    #[test]
    fn test_new_zero_size() {
        let result = IntArray::new(0);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_from_array() {
        let array = IntArray::from_array(vec![1, 2, 3]).unwrap();
        assert_eq!(array.universe_size(), 3);
        assert_eq!(array.as_slice(), &[1, 2, 3]);
    }
    
    #[test]
    fn test_from_empty_array() {
        let result = IntArray::from_array(vec![]);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_from_string() {
        let array = IntArray::from_string("1, 2, 3").unwrap();
        assert_eq!(array.universe_size(), 3);
        assert_eq!(array.as_slice(), &[1, 2, 3]);
    }
    
    #[test]
    fn test_from_string_spaces() {
        let array = IntArray::from_string("1 2 3").unwrap();
        assert_eq!(array.universe_size(), 3);
        assert_eq!(array.as_slice(), &[1, 2, 3]);
    }
    
    #[test]
    fn test_get_set() {
        let mut array = IntArray::new(3).unwrap();
        assert_eq!(array.get(0), Some(0));
        assert_eq!(array.get(3), None);
        
        array.set(1, 42).unwrap();
        assert_eq!(array.get(1), Some(42));
        
        let result = array.set(3, 1);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_blocks_constraint() {
        let array = IntArray::from_array(vec![1, 1, 2, 2]).unwrap();
        let blocks = vec![vec![0, 1], vec![2, 3]];
        assert!(array.satisfies_blocks_constraint(&blocks));
        
        let blocks2 = vec![vec![0, 2], vec![1, 3]];
        assert!(!array.satisfies_blocks_constraint(&blocks2));
    }
    
    #[test]
    fn test_values_constraint() {
        let array = IntArray::from_array(vec![1, 2, 3, 4]).unwrap();
        let values = vec![(0, 1), (2, 3)];
        assert!(array.satisfies_values_constraint(&values));
        
        let values2 = vec![(0, 2), (2, 3)];
        assert!(!array.satisfies_values_constraint(&values2));
    }
    
    #[test]
    fn test_set_constraint() {
        let array = IntArray::from_array(vec![1, 2, 3]).unwrap();
        let mut possible_values = HashSet::new();
        possible_values.insert(1);
        possible_values.insert(3);
        
        assert!(array.satisfies_set_constraint(0, &possible_values));
        assert!(!array.satisfies_set_constraint(1, &possible_values));
        assert!(array.satisfies_set_constraint(2, &possible_values));
    }
    
    #[test]
    fn test_is_idempotent() {
        // f(0) = 0, f(1) = 1, f(2) = 2 - idempotent
        let array = IntArray::from_array(vec![0, 1, 2]).unwrap();
        assert!(array.is_idempotent());
        
        // f(0) = 1, f(1) = 0 - not idempotent (f(f(0)) = f(1) = 0 != 1 = f(0))
        let array2 = IntArray::from_array(vec![1, 0]).unwrap();
        assert!(!array2.is_idempotent());
    }
    
    #[test]
    fn test_is_constant() {
        let array = IntArray::from_array(vec![5, 5, 5]).unwrap();
        assert!(array.is_constant());
        
        let array2 = IntArray::from_array(vec![5, 5, 6]).unwrap();
        assert!(!array2.is_constant());
    }
    
    #[test]
    fn test_equality() {
        let array1 = IntArray::from_array(vec![1, 2, 3]).unwrap();
        let array2 = IntArray::from_array(vec![1, 2, 3]).unwrap();
        let array3 = IntArray::from_array(vec![1, 2, 4]).unwrap();
        
        assert_eq!(array1, array2);
        assert_ne!(array1, array3);
    }
    
    #[test]
    fn test_hash() {
        let array1 = IntArray::from_array(vec![1, 2, 3]).unwrap();
        let array2 = IntArray::from_array(vec![1, 2, 3]).unwrap();
        let array3 = IntArray::from_array(vec![1, 2, 4]).unwrap();
        
        let mut hasher1 = std::collections::hash_map::DefaultHasher::new();
        let mut hasher2 = std::collections::hash_map::DefaultHasher::new();
        let mut hasher3 = std::collections::hash_map::DefaultHasher::new();
        
        array1.hash(&mut hasher1);
        array2.hash(&mut hasher2);
        array3.hash(&mut hasher3);
        
        assert_eq!(hasher1.finish(), hasher2.finish());
        assert_ne!(hasher1.finish(), hasher3.finish());
    }
    
    #[test]
    fn test_to_string() {
        let array = IntArray::from_array(vec![1, 2, 3]).unwrap();
        assert_eq!(array.to_string(), "[1, 2, 3]");
        
        let _empty_array = IntArray::from_array(vec![]).unwrap_err();
        // This should fail since we don't allow empty arrays
    }
    
    #[test]
    fn test_lexicographic_comparator() {
        let array1 = IntArray::from_array(vec![1, 2, 3]).unwrap();
        let array2 = IntArray::from_array(vec![1, 2, 4]).unwrap();
        let array3 = IntArray::from_array(vec![1, 2]).unwrap();
        
        let comparator = IntArray::lexicographic_comparator();
        
        assert_eq!(comparator(&array1, &array1), std::cmp::Ordering::Equal);
        assert_eq!(comparator(&array1, &array2), std::cmp::Ordering::Less);
        assert_eq!(comparator(&array2, &array1), std::cmp::Ordering::Greater);
        assert_eq!(comparator(&array3, &array1), std::cmp::Ordering::Less);
        assert_eq!(comparator(&array1, &array3), std::cmp::Ordering::Greater);
    }
}
