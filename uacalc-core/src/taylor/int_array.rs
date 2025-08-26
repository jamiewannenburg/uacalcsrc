//! Efficient integer array representation for Taylor terms
//! 
//! This module provides memory-efficient integer array representation
//! for Taylor term canonicalization and search.

use crate::{UACalcError, UACalcResult};
use std::fmt;
use std::hash::{Hash, Hasher};
use std::cmp::Ordering;

/// Efficient integer array representation using Box<[u8]>
#[derive(Debug, Clone)]
pub struct IntArray {
    /// Array data (most values are 0 or 1, so u8 is sufficient)
    data: Box<[u8]>,
    /// Length of the array
    length: usize,
}

impl IntArray {
    /// Create a new integer array with given length
    pub fn new(length: usize) -> Self {
        Self {
            data: vec![0; length].into_boxed_slice(),
            length,
        }
    }
    
    /// Create an integer array from a vector
    pub fn from_vec(data: Vec<usize>) -> Self {
        let length = data.len();
        let mut array = Self::new(length);
        for (i, &value) in data.iter().enumerate() {
            array.set(i, value);
        }
        array
    }
    
    /// Create an integer array from a slice
    pub fn from_slice(data: &[usize]) -> Self {
        Self::from_vec(data.to_vec())
    }
    
    /// Get the length of the array
    pub fn len(&self) -> usize {
        self.length
    }
    
    /// Check if the array is empty
    pub fn is_empty(&self) -> bool {
        self.length == 0
    }
    
    /// Get a value at the given index
    pub fn get(&self, index: usize) -> UACalcResult<usize> {
        if index >= self.length {
            return Err(UACalcError::InvalidOperation {
                message: format!("Index {} out of bounds for array of length {}", index, self.length),
            });
        }
        Ok(self.data[index] as usize)
    }
    
    /// Set a value at the given index
    pub fn set(&mut self, index: usize, value: usize) -> UACalcResult<()> {
        if index >= self.length {
            return Err(UACalcError::InvalidOperation {
                message: format!("Index {} out of bounds for array of length {}", index, self.length),
            });
        }
        if value > u8::MAX as usize {
            return Err(UACalcError::InvalidOperation {
                message: format!("Value {} too large for u8 storage", value),
            });
        }
        self.data[index] = value as u8;
        Ok(())
    }
    
    /// Get the array as a vector
    pub fn to_vec(&self) -> Vec<usize> {
        self.data.iter().map(|&x| x as usize).collect()
    }
    
    /// Get the array as a slice
    pub fn as_slice(&self) -> &[u8] {
        &self.data
    }
    
    /// Get a mutable slice to the array
    pub fn as_mut_slice(&mut self) -> &mut [u8] {
        &mut self.data
    }
    
    /// Create a complement array (1 - each element)
    pub fn complement(&self) -> Self {
        let mut result = self.clone();
        for i in 0..self.length {
            result.data[i] = if result.data[i] == 0 { 1 } else { 0 };
        }
        result
    }
    
    /// Check if this array is the complement of another
    pub fn is_complement_of(&self, other: &IntArray) -> bool {
        if self.length != other.length {
            return false;
        }
        for i in 0..self.length {
            if self.data[i] + other.data[i] != 1 {
                return false;
            }
        }
        true
    }
    
    /// Create an array filled with a constant value
    pub fn constant(length: usize, value: usize) -> UACalcResult<Self> {
        if value > u8::MAX as usize {
            return Err(UACalcError::InvalidOperation {
                message: format!("Value {} too large for u8 storage", value),
            });
        }
        Ok(Self {
            data: vec![value as u8; length].into_boxed_slice(),
            length,
        })
    }
    
    /// Create an array with a single 1 at the given position
    pub fn unit_vector(length: usize, position: usize) -> UACalcResult<Self> {
        if position >= length {
            return Err(UACalcError::InvalidOperation {
                message: format!("Position {} out of bounds for array of length {}", position, length),
            });
        }
        let mut array = Self::new(length);
        array.set(position, 1)?;
        Ok(array)
    }
    
    /// Count the number of 1s in the array
    pub fn count_ones(&self) -> usize {
        self.data.iter().filter(|&&x| x == 1).count()
    }
    
    /// Count the number of 0s in the array
    pub fn count_zeros(&self) -> usize {
        self.data.iter().filter(|&&x| x == 0).count()
    }
    
    /// Check if the array contains only zeros
    pub fn is_zero(&self) -> bool {
        self.data.iter().all(|&x| x == 0)
    }
    
    /// Check if the array contains only ones
    pub fn is_one(&self) -> bool {
        self.data.iter().all(|&x| x == 1)
    }
    
    /// Get the first position of a 1, or None if no 1s
    pub fn first_one(&self) -> Option<usize> {
        self.data.iter().position(|&x| x == 1)
    }
    
    /// Get the last position of a 1, or None if no 1s
    pub fn last_one(&self) -> Option<usize> {
        self.data.iter().rposition(|&x| x == 1)
    }
    
    /// Get the first position of a 0, or None if no 0s
    pub fn first_zero(&self) -> Option<usize> {
        self.data.iter().position(|&x| x == 0)
    }
    
    /// Get the last position of a 0, or None if no 0s
    pub fn last_zero(&self) -> Option<usize> {
        self.data.iter().rposition(|&x| x == 0)
    }
}

impl PartialEq for IntArray {
    fn eq(&self, other: &Self) -> bool {
        self.length == other.length && self.data == other.data
    }
}

impl Eq for IntArray {}

impl Hash for IntArray {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.length.hash(state);
        self.data.hash(state);
    }
}

impl PartialOrd for IntArray {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for IntArray {
    fn cmp(&self, other: &Self) -> Ordering {
        // Lexicographic comparison
        for i in 0..self.length.min(other.length) {
            match self.data[i].cmp(&other.data[i]) {
                Ordering::Equal => continue,
                other => return other,
            }
        }
        self.length.cmp(&other.length)
    }
}

impl fmt::Display for IntArray {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[")?;
        for (i, &value) in self.data.iter().enumerate() {
            if i > 0 {
                write!(f, ", ")?;
            }
            write!(f, "{}", value)?;
        }
        write!(f, "]")
    }
}

impl From<Vec<usize>> for IntArray {
    fn from(data: Vec<usize>) -> Self {
        Self::from_vec(data)
    }
}

impl From<&[usize]> for IntArray {
    fn from(data: &[usize]) -> Self {
        Self::from_slice(data)
    }
}

impl Into<Vec<usize>> for IntArray {
    fn into(self) -> Vec<usize> {
        self.to_vec()
    }
}

/// Iterator over array elements
pub struct IntArrayIter<'a> {
    array: &'a IntArray,
    index: usize,
}

impl<'a> Iterator for IntArrayIter<'a> {
    type Item = usize;
    
    fn next(&mut self) -> Option<Self::Item> {
        if self.index < self.array.length {
            let value = self.array.data[self.index] as usize;
            self.index += 1;
            Some(value)
        } else {
            None
        }
    }
}

impl<'a> IntoIterator for &'a IntArray {
    type Item = usize;
    type IntoIter = IntArrayIter<'a>;
    
    fn into_iter(self) -> Self::IntoIter {
        IntArrayIter {
            array: self,
            index: 0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_int_array_creation() {
        let array = IntArray::new(5);
        assert_eq!(array.len(), 5);
        assert!(!array.is_empty());
        
        for i in 0..5 {
            assert_eq!(array.get(i).unwrap(), 0);
        }
    }
    
    #[test]
    fn test_int_array_from_vec() {
        let data = vec![1, 0, 1, 0, 1];
        let array = IntArray::from_vec(data);
        
        assert_eq!(array.len(), 5);
        assert_eq!(array.get(0).unwrap(), 1);
        assert_eq!(array.get(1).unwrap(), 0);
        assert_eq!(array.get(2).unwrap(), 1);
    }
    
    #[test]
    fn test_int_array_set_get() {
        let mut array = IntArray::new(3);
        array.set(0, 1).unwrap();
        array.set(1, 0).unwrap();
        array.set(2, 1).unwrap();
        
        assert_eq!(array.get(0).unwrap(), 1);
        assert_eq!(array.get(1).unwrap(), 0);
        assert_eq!(array.get(2).unwrap(), 1);
    }
    
    #[test]
    fn test_int_array_bounds_checking() {
        let array = IntArray::new(3);
        assert!(array.get(3).is_err());
        
        let mut array = IntArray::new(3);
        assert!(array.set(3, 1).is_err());
    }
    
    #[test]
    fn test_int_array_complement() {
        let array = IntArray::from_vec(vec![1, 0, 1, 0]);
        let complement = array.complement();
        
        assert_eq!(complement.get(0).unwrap(), 0);
        assert_eq!(complement.get(1).unwrap(), 1);
        assert_eq!(complement.get(2).unwrap(), 0);
        assert_eq!(complement.get(3).unwrap(), 1);
    }
    
    #[test]
    fn test_int_array_equality() {
        let array1 = IntArray::from_vec(vec![1, 0, 1]);
        let array2 = IntArray::from_vec(vec![1, 0, 1]);
        let array3 = IntArray::from_vec(vec![1, 1, 0]);
        
        assert_eq!(array1, array2);
        assert_ne!(array1, array3);
    }
    
    #[test]
    fn test_int_array_ordering() {
        let array1 = IntArray::from_vec(vec![0, 0, 1]);
        let array2 = IntArray::from_vec(vec![0, 1, 0]);
        let array3 = IntArray::from_vec(vec![1, 0, 0]);
        
        assert!(array1 < array2);
        assert!(array2 < array3);
        assert!(array1 < array3);
    }
    
    #[test]
    fn test_int_array_counting() {
        let array = IntArray::from_vec(vec![1, 0, 1, 0, 1]);
        assert_eq!(array.count_ones(), 3);
        assert_eq!(array.count_zeros(), 2);
        assert!(!array.is_zero());
        assert!(!array.is_one());
    }
    
    #[test]
    fn test_int_array_positions() {
        let array = IntArray::from_vec(vec![0, 1, 0, 1, 0]);
        assert_eq!(array.first_one(), Some(1));
        assert_eq!(array.last_one(), Some(3));
        assert_eq!(array.first_zero(), Some(0));
        assert_eq!(array.last_zero(), Some(4));
    }
    
    #[test]
    fn test_int_array_iteration() {
        let array = IntArray::from_vec(vec![1, 0, 1]);
        let values: Vec<usize> = array.into_iter().collect();
        assert_eq!(values, vec![1, 0, 1]);
    }
    
    #[test]
    fn test_int_array_constant() {
        let array = IntArray::constant(4, 1).unwrap();
        assert_eq!(array.len(), 4);
        assert!(array.is_one());
        
        let array = IntArray::constant(3, 0).unwrap();
        assert_eq!(array.len(), 3);
        assert!(array.is_zero());
    }
    
    #[test]
    fn test_int_array_unit_vector() {
        let array = IntArray::unit_vector(4, 2).unwrap();
        assert_eq!(array.len(), 4);
        assert_eq!(array.get(0).unwrap(), 0);
        assert_eq!(array.get(1).unwrap(), 0);
        assert_eq!(array.get(2).unwrap(), 1);
        assert_eq!(array.get(3).unwrap(), 0);
    }
}
