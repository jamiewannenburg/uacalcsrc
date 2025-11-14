/// Array incrementor for in-place incrementing of arrays.
/// 
/// This module provides functionality to modify an array to be the next one
/// in a sequence, returning false if there are no more elements.
/// 
/// This is a translation of the Java interface `org.uacalc.util.ArrayIncrementor`.

use std::hash::{Hash, Hasher};

/// Array incrementor trait for in-place incrementing of arrays.
/// 
/// This trait provides functionality to modify an array to be the next one
/// in a sequence, returning false if there are no more elements.
/// 
/// # Examples
/// ```
/// use uacalc::util::array_incrementor::{ArrayIncrementor, ArrayIncrementorImpl};
/// 
/// let mut arr = vec![0, 1, 2];
/// let mut incrementor = ArrayIncrementorImpl::new(&mut arr);
/// while incrementor.increment() {
///     // println!("{:?}", arr); // Commented out to avoid borrow checker issues in doctest
/// }
/// ```
pub trait ArrayIncrementor {
    /// Modify the array to be the next one; return false if there is no more.
    /// 
    /// # Returns
    /// * `true` - If the array was successfully incremented
    /// * `false` - If there are no more elements in the sequence
    fn increment(&mut self) -> bool;
}

/// Array incrementor implementation that uses PermutationGenerator for permutation generation.
/// 
/// This implementation provides an array incrementor that modifies
/// the array to be the next permutation using the Johnson-Trotter algorithm.
/// 
/// # Examples
/// ```
/// use uacalc::util::array_incrementor::{ArrayIncrementor, ArrayIncrementorImpl};
/// 
/// let mut arr = vec![0, 1, 2];
/// let mut incrementor = ArrayIncrementorImpl::new(&mut arr);
/// while incrementor.increment() {
///     // println!("{:?}", arr); // Commented out to avoid borrow checker issues in doctest
/// }
/// ```
#[derive(Debug, PartialEq, Eq)]
pub struct ArrayIncrementorImpl<'a> {
    generator: crate::util::permutation_generator::PermutationGenerator,
    arr: &'a mut [usize],
}

/// Simple array incrementor that increments arrays in lexicographic order.
/// 
/// This implementation provides a basic array incrementor that modifies
/// the array to be the next one in lexicographic order.
/// 
/// # Examples
/// ```
/// use uacalc::util::array_incrementor::{ArrayIncrementor, SimpleArrayIncrementor};
/// 
/// let mut arr = vec![0, 1, 2];
/// let mut incrementor = SimpleArrayIncrementor::new(&mut arr);
/// while incrementor.increment() {
///     // println!("{:?}", arr); // Commented out to avoid borrow checker issues in doctest
/// }
/// ```
#[derive(Debug, PartialEq, Eq)]
pub struct SimpleArrayIncrementor<'a> {
    arr: &'a mut [usize],
    max_values: Vec<usize>,
    first_call: bool,
}

impl<'a> ArrayIncrementorImpl<'a> {
    /// Create a new ArrayIncrementorImpl for the given array.
    /// 
    /// # Arguments
    /// * `arr` - The array to increment
    /// 
    /// # Returns
    /// A new ArrayIncrementorImpl instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::array_incrementor::ArrayIncrementorImpl;
    /// 
    /// let mut arr = vec![0, 1, 2];
    /// let incrementor = ArrayIncrementorImpl::new(&mut arr);
    /// ```
    pub fn new(arr: &'a mut [usize]) -> Self {
        Self {
            generator: crate::util::permutation_generator::PermutationGenerator::new(arr.len()),
            arr,
        }
    }
    
    /// Get a reference to the current array state.
    /// 
    /// # Returns
    /// A reference to the current array
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::array_incrementor::ArrayIncrementorImpl;
    /// 
    /// let mut arr = vec![0, 1, 2];
    /// let incrementor = ArrayIncrementorImpl::new(&mut arr);
    /// assert_eq!(incrementor.get_array(), &[0, 1, 2]);
    /// ```
    pub fn get_array(&self) -> &[usize] {
        self.arr
    }
    
    fn swap(&mut self, k: usize) {
        self.arr.swap(k, k + 1);
    }
}

impl<'a> ArrayIncrementor for ArrayIncrementorImpl<'a> {
    fn increment(&mut self) -> bool {
        loop {
            match self.generator.next_index() {
                Some(k) => {
                    if self.arr[k] != self.arr[k + 1] {
                        self.swap(k);
                        return true;
                    }
                    // If elements are equal, continue to next permutation
                }
                None => {
                    // Reset to original state if array has more than 1 element
                    if self.arr.len() > 1 {
                        self.swap(0);
                    }
                    return false;
                }
            }
        }
    }
}

impl<'a> Hash for ArrayIncrementorImpl<'a> {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.arr.hash(state);
        self.generator.hash(state);
    }
}

impl<'a> std::fmt::Display for ArrayIncrementorImpl<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "ArrayIncrementorImpl(arr={:?})", self.arr)
    }
}

impl<'a> SimpleArrayIncrementor<'a> {
    /// Create a new SimpleArrayIncrementor for the given array.
    /// 
    /// # Arguments
    /// * `arr` - The array to increment
    /// 
    /// # Returns
    /// A new SimpleArrayIncrementor instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::array_incrementor::SimpleArrayIncrementor;
    /// 
    /// let mut arr = vec![0, 1, 2];
    /// let incrementor = SimpleArrayIncrementor::new(&mut arr);
    /// ```
    pub fn new(arr: &'a mut [usize]) -> Self {
        let max_values = vec![arr.len() - 1; arr.len()];
        Self {
            arr,
            max_values,
            first_call: true,
        }
    }
    
    /// Create a new SimpleArrayIncrementor with custom maximum values.
    /// 
    /// # Arguments
    /// * `arr` - The array to increment
    /// * `max_values` - Maximum value for each position (must have same length as arr)
    /// 
    /// # Returns
    /// * `Ok(Self)` - The new SimpleArrayIncrementor
    /// * `Err(String)` - If max_values length doesn't match arr length
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::array_incrementor::SimpleArrayIncrementor;
    /// 
    /// let mut arr = vec![0, 1, 2];
    /// let max_vals = vec![2, 3, 4];
    /// let incrementor = SimpleArrayIncrementor::new_with_max_values(&mut arr, max_vals).unwrap();
    /// ```
    pub fn new_with_max_values(arr: &'a mut [usize], max_values: Vec<usize>) -> Result<Self, String> {
        if arr.len() != max_values.len() {
            return Err("Array and max_values must have the same length".to_string());
        }
        
        // Validate that all array values are within their max bounds
        for (i, &val) in arr.iter().enumerate() {
            if val > max_values[i] {
                return Err(format!("Array value {} at position {} exceeds maximum {}", val, i, max_values[i]));
            }
        }
        
        Ok(Self {
            arr,
            max_values,
            first_call: true,
        })
    }
    
    /// Create a new SimpleArrayIncrementor with custom maximum values (panic version).
    /// 
    /// # Arguments
    /// * `arr` - The array to increment
    /// * `max_values` - Maximum value for each position (must have same length as arr)
    /// 
    /// # Panics
    /// Panics if max_values length doesn't match arr length or if array values exceed max bounds
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::array_incrementor::SimpleArrayIncrementor;
    /// 
    /// let mut arr = vec![0, 1, 2];
    /// let max_vals = vec![2, 3, 4];
    /// let incrementor = SimpleArrayIncrementor::new_with_max_values_panic(&mut arr, max_vals);
    /// ```
    pub fn new_with_max_values_panic(arr: &'a mut [usize], max_values: Vec<usize>) -> Self {
        Self::new_with_max_values(arr, max_values).unwrap()
    }
    
    /// Get a reference to the current array state.
    /// 
    /// # Returns
    /// A reference to the current array
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::array_incrementor::SimpleArrayIncrementor;
    /// 
    /// let mut arr = vec![0, 1, 2];
    /// let incrementor = SimpleArrayIncrementor::new(&mut arr);
    /// assert_eq!(incrementor.get_array(), &[0, 1, 2]);
    /// ```
    pub fn get_array(&self) -> &[usize] {
        self.arr
    }
}

impl<'a> ArrayIncrementor for SimpleArrayIncrementor<'a> {
    fn increment(&mut self) -> bool {
        if self.first_call {
            self.first_call = false;
            return true; // Return the initial state
        }
        
        // Find the rightmost position that can be incremented
        for i in (0..self.arr.len()).rev() {
            if self.arr[i] < self.max_values[i] {
                self.arr[i] += 1;
                // Reset all positions to the right to 0
                for j in (i + 1)..self.arr.len() {
                    self.arr[j] = 0;
                }
                return true;
            }
        }
        
        false // No more increments possible
    }
}

impl<'a> Hash for SimpleArrayIncrementor<'a> {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.arr.hash(state);
        self.max_values.hash(state);
        self.first_call.hash(state);
    }
}

impl<'a> std::fmt::Display for SimpleArrayIncrementor<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "SimpleArrayIncrementor(arr={:?}, max_values={:?})", self.arr, self.max_values)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::hash_map::DefaultHasher;
    
    #[test]
    fn test_new() {
        let mut arr = vec![0, 1, 2];
        let incrementor = SimpleArrayIncrementor::new(&mut arr);
        assert_eq!(incrementor.max_values, vec![2, 2, 2]);
        assert!(incrementor.first_call);
    }
    
    #[test]
    fn test_new_with_max_values() {
        let mut arr = vec![0, 1, 2];
        let max_vals = vec![2, 3, 4];
        let incrementor = SimpleArrayIncrementor::new_with_max_values(&mut arr, max_vals).unwrap();
        assert_eq!(incrementor.max_values, vec![2, 3, 4]);
    }
    
    #[test]
    fn test_new_with_max_values_invalid_length() {
        let mut arr = vec![0, 1, 2];
        let max_vals = vec![2, 3]; // Wrong length
        let result = SimpleArrayIncrementor::new_with_max_values(&mut arr, max_vals);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_new_with_max_values_invalid_value() {
        let mut arr = vec![0, 1, 5]; // 5 > 2 (max for position 2)
        let max_vals = vec![2, 3, 4];
        let result = SimpleArrayIncrementor::new_with_max_values(&mut arr, max_vals);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_increment_basic() {
        let mut arr = vec![0, 0, 0];
        let mut incrementor = SimpleArrayIncrementor::new(&mut arr);
        
        // First call should return true (initial state)
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[0, 0, 0]);
        
        // Second call should increment to [0, 0, 1]
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[0, 0, 1]);
        
        // Continue incrementing
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[0, 0, 2]);
        
        // Should wrap around to [0, 1, 0]
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[0, 1, 0]);
    }
    
    #[test]
    fn test_increment_with_custom_max() {
        let mut arr = vec![0, 0, 0];
        let max_vals = vec![1, 2, 1];
        let mut incrementor = SimpleArrayIncrementor::new_with_max_values(&mut arr, max_vals).unwrap();
        
        // First call should return true (initial state)
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[0, 0, 0]);
        
        // Increment through all possible combinations
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[0, 0, 1]);
        
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[0, 1, 0]);
        
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[0, 1, 1]);
        
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[0, 2, 0]);
        
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[0, 2, 1]);
        
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[1, 0, 0]);
        
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[1, 0, 1]);
        
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[1, 1, 0]);
        
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[1, 1, 1]);
        
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[1, 2, 0]);
        
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[1, 2, 1]);
        
        // Should return false (no more increments)
        assert!(!incrementor.increment());
    }
    
    #[test]
    fn test_increment_exhaustion() {
        let mut arr = vec![2, 2, 2]; // Already at maximum
        let mut incrementor = SimpleArrayIncrementor::new(&mut arr);
        
        // First call should return true (initial state)
        assert!(incrementor.increment());
        assert_eq!(incrementor.get_array(), &[2, 2, 2]);
        
        // Should return false (no more increments possible)
        assert!(!incrementor.increment());
    }
    
    #[test]
    fn test_display() {
        let mut arr = vec![0, 1, 2];
        let incrementor = SimpleArrayIncrementor::new(&mut arr);
        let display = format!("{}", incrementor);
        assert!(display.contains("SimpleArrayIncrementor"));
        assert!(display.contains("[0, 1, 2]"));
    }
    
    #[test]
    fn test_hash() {
        let mut arr1 = vec![0, 1, 2];
        let mut arr2 = vec![0, 1, 2];
        let incrementor1 = SimpleArrayIncrementor::new(&mut arr1);
        let incrementor2 = SimpleArrayIncrementor::new(&mut arr2);
        
        let mut hasher1 = DefaultHasher::new();
        let mut hasher2 = DefaultHasher::new();
        
        incrementor1.hash(&mut hasher1);
        incrementor2.hash(&mut hasher2);
        
        assert_eq!(hasher1.finish(), hasher2.finish());
    }
}
