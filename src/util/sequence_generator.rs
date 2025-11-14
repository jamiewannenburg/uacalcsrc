/*!
 * SequenceGenerator - Utility for generating sequences and array incrementors.
 * 
 * This is a Rust implementation of org.uacalc.util.SequenceGenerator,
 * providing functionality for generating various types of sequences
 * and incrementing arrays in place.
 */

// use std::collections::HashMap;

/// Trait for incrementing arrays in place.
/// 
/// This corresponds to the Java ArrayIncrementor interface.
pub trait ArrayIncrementor {
    /// Modify the array to be the next one; return false if there is no more.
    fn increment(&mut self) -> bool;
    
    /// Get the current state of the array.
    fn get_current(&self) -> Vec<i32>;
}

/// A sequence incrementor that generates all possible tuples
/// with entries between 0 and max.
/// 
/// This increments from the right: [0,0,0], [0,0,1], ...,[max,max,max].
pub struct SequenceIncrementor<'a> {
    array: &'a mut [i32],
    max: i32,
}

impl<'a> SequenceIncrementor<'a> {
    /// Create a new sequence incrementor.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    pub fn new(array: &'a mut [i32], max: i32) -> Self {
        Self { array, max }
    }
}

impl<'a> ArrayIncrementor for SequenceIncrementor<'a> {
    fn increment(&mut self) -> bool {
        let len = self.array.len();
        for i in (0..len).rev() {
            if self.array[i] < self.max {
                self.array[i] += 1;
                for j in (i + 1)..len {
                    self.array[j] = 0;
                }
                return true;
            }
        }
        false
    }
    
    fn get_current(&self) -> Vec<i32> {
        self.array.to_vec()
    }
}

/// A sequence incrementor that generates all possible tuples
/// with entries between 0 and max, subject to the restriction that
/// the last coordinate is at least min.
pub struct SequenceIncrementorWithMin<'a> {
    array: &'a mut [i32],
    max: i32,
    min: i32,
}

impl<'a> SequenceIncrementorWithMin<'a> {
    /// Create a new sequence incrementor with minimum constraint.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    /// * `min` - Minimum value that must appear in the array
    pub fn new(array: &'a mut [i32], max: i32, min: i32) -> Self {
        // Ensure the initial array satisfies the minimum constraint
        let mut has_min = false;
        for i in 0..array.len() {
            if array[i] >= min {
                has_min = true;
                break;
            }
        }
        if !has_min && !array.is_empty() {
            array[array.len() - 1] = min;
        }
        
        Self { array, max, min }
    }
}

impl<'a> ArrayIncrementor for SequenceIncrementorWithMin<'a> {
    fn increment(&mut self) -> bool {
        let len = self.array.len();
        for i in (0..len).rev() {
            if self.array[i] < self.max {
                self.array[i] += 1;
                for j in (i + 1)..len {
                    self.array[j] = 0;
                }
                
                // Check if at least one element is >= min
                let mut ok = false;
                for j in 0..len {
                    if self.array[j] >= self.min {
                        ok = true;
                        break;
                    }
                }
                if !ok {
                    // If no element is >= min, set the last element to min
                    self.array[len - 1] = self.min;
                }
                return true;
            }
        }
        false
    }
    
    fn get_current(&self) -> Vec<i32> {
        self.array.to_vec()
    }
}

/// A sequence incrementor that generates all possible tuples
/// with entries between 0 and max, subject to the restriction that
/// the last coordinate is at least min, with jump support for parallel processing.
pub struct SequenceIncrementorWithJump<'a> {
    array: &'a mut [i32],
    max: i32,
    min: i32,
    jump: usize,
}

impl<'a> SequenceIncrementorWithJump<'a> {
    /// Create a new sequence incrementor with jump support.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    /// * `min` - Minimum value that must appear in the array
    /// * `jump` - Number of times to increment per call
    pub fn new(array: &'a mut [i32], max: i32, min: i32, jump: usize) -> Self {
        Self { array, max, min, jump }
    }
}

impl<'a> ArrayIncrementor for SequenceIncrementorWithJump<'a> {
    fn increment(&mut self) -> bool {
        for _ in 0..self.jump {
            if !self.increment_aux() {
                return false;
            }
        }
        true
    }
    
    fn get_current(&self) -> Vec<i32> {
        self.array.to_vec()
    }
}

impl<'a> SequenceIncrementorWithJump<'a> {
    fn increment_aux(&mut self) -> bool {
        let len = self.array.len();
        for i in (0..len).rev() {
            if self.array[i] < self.max {
                self.array[i] += 1;
                for j in (i + 1)..len {
                    self.array[j] = 0;
                }
                
                // Check if at least one element is >= min
                let mut ok = false;
                for j in 0..=i {
                    if self.array[j] >= self.min {
                        ok = true;
                        break;
                    }
                }
                if !ok {
                    self.array[len - 1] = self.min;
                }
                return true;
            }
        }
        false
    }
}

/// A nondecreasing sequence incrementor that generates sequences
/// where each element is >= the previous element.
pub struct NondecreasingSequenceIncrementor<'a> {
    array: &'a mut [i32],
    max: i32,
}

impl<'a> NondecreasingSequenceIncrementor<'a> {
    /// Create a new nondecreasing sequence incrementor.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    pub fn new(array: &'a mut [i32], max: i32) -> Self {
        Self { array, max }
    }
}

impl<'a> ArrayIncrementor for NondecreasingSequenceIncrementor<'a> {
    fn increment(&mut self) -> bool {
        let len = self.array.len();
        for i in (0..len).rev() {
            if self.array[i] < self.max {
                self.array[i] += 1;
                // Reset all elements to the right to maintain nondecreasing property
                for j in (i + 1)..len {
                    self.array[j] = self.array[i];
                }
                return true;
            }
        }
        false
    }
    
    fn get_current(&self) -> Vec<i32> {
        self.array.to_vec()
    }
}

/// An increasing sequence incrementor that generates sequences
/// where each element is > the previous element.
pub struct IncreasingSequenceIncrementor<'a> {
    array: &'a mut [i32],
    max: i32,
}

impl<'a> IncreasingSequenceIncrementor<'a> {
    /// Create a new increasing sequence incrementor.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    pub fn new(array: &'a mut [i32], max: i32) -> Self {
        Self { array, max }
    }
}

impl<'a> ArrayIncrementor for IncreasingSequenceIncrementor<'a> {
    fn increment(&mut self) -> bool {
        let len = self.array.len();
        for i in (0..len).rev() {
            if self.array[i] < self.max - (len - 1 - i) as i32 {
                self.array[i] += 1;
                // Reset all elements to the right to maintain increasing property
                for j in (i + 1)..len {
                    self.array[j] = self.array[i] + (j - i) as i32;
                }
                return true;
            }
        }
        false
    }
    
    fn get_current(&self) -> Vec<i32> {
        self.array.to_vec()
    }
}

/// A left sequence incrementor that generates sequences
/// incrementing from the left.
pub struct LeftSequenceIncrementor<'a> {
    array: &'a mut [i32],
    max: i32,
}

impl<'a> LeftSequenceIncrementor<'a> {
    /// Create a new left sequence incrementor.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    pub fn new(array: &'a mut [i32], max: i32) -> Self {
        Self { array, max }
    }
}

impl<'a> ArrayIncrementor for LeftSequenceIncrementor<'a> {
    fn increment(&mut self) -> bool {
        let len = self.array.len();
        for i in 0..len {
            if self.array[i] < self.max {
                self.array[i] += 1;
                // Reset all elements to the left
                for j in 0..i {
                    self.array[j] = 0;
                }
                return true;
            }
        }
        false
    }
    
    fn get_current(&self) -> Vec<i32> {
        self.array.to_vec()
    }
}

/// A partition array incrementor for generating partitions.
pub struct PartitionArrayIncrementor<'a> {
    array: &'a mut [i32],
    max: i32,
}

impl<'a> PartitionArrayIncrementor<'a> {
    /// Create a new partition array incrementor.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    pub fn new(array: &'a mut [i32], max: i32) -> Self {
        Self { array, max }
    }
}

impl<'a> ArrayIncrementor for PartitionArrayIncrementor<'a> {
    fn increment(&mut self) -> bool {
        let len = self.array.len();
        for i in (0..len).rev() {
            if self.array[i] < self.max {
                self.array[i] += 1;
                // Reset all elements to the right to 0
                for j in (i + 1)..len {
                    self.array[j] = 0;
                }
                return true;
            }
        }
        false
    }
    
    fn get_current(&self) -> Vec<i32> {
        self.array.to_vec()
    }
}

/// Utility functions for sequence generation.
pub struct SequenceGenerator;

impl SequenceGenerator {
    /// Create a sequence incrementor for all possible tuples
    /// with entries between 0 and max.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    /// 
    /// # Returns
    /// A boxed ArrayIncrementor
    pub fn sequence_incrementor(array: &mut [i32], max: i32) -> Box<dyn ArrayIncrementor + '_> {
        Box::new(SequenceIncrementor::new(array, max))
    }
    
    /// Create a sequence incrementor for all possible tuples
    /// with entries between 0 and max, subject to the restriction that
    /// the last coordinate is at least min.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    /// * `min` - Minimum value that must appear in the array
    /// 
    /// # Returns
    /// A boxed ArrayIncrementor
    pub fn sequence_incrementor_with_min(
        array: &mut [i32], 
        max: i32, 
        min: i32
    ) -> Box<dyn ArrayIncrementor + '_> {
        Box::new(SequenceIncrementorWithMin::new(array, max, min))
    }
    
    /// Create a sequence incrementor for all possible tuples
    /// with entries between 0 and max, subject to the restriction that
    /// the last coordinate is at least min, with jump support.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    /// * `min` - Minimum value that must appear in the array
    /// * `jump` - Number of times to increment per call
    /// 
    /// # Returns
    /// A boxed ArrayIncrementor
    pub fn sequence_incrementor_with_jump(
        array: &mut [i32], 
        max: i32, 
        min: i32, 
        jump: usize
    ) -> Box<dyn ArrayIncrementor + '_> {
        Box::new(SequenceIncrementorWithJump::new(array, max, min, jump))
    }
    
    /// Create a nondecreasing sequence incrementor.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    /// 
    /// # Returns
    /// A boxed ArrayIncrementor
    pub fn nondecreasing_sequence_incrementor(
        array: &mut [i32], 
        max: i32
    ) -> Box<dyn ArrayIncrementor + '_> {
        Box::new(NondecreasingSequenceIncrementor::new(array, max))
    }
    
    /// Create an increasing sequence incrementor.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    /// 
    /// # Returns
    /// A boxed ArrayIncrementor
    pub fn increasing_sequence_incrementor(
        array: &mut [i32], 
        max: i32
    ) -> Box<dyn ArrayIncrementor + '_> {
        Box::new(IncreasingSequenceIncrementor::new(array, max))
    }
    
    /// Create a left sequence incrementor.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    /// 
    /// # Returns
    /// A boxed ArrayIncrementor
    pub fn left_sequence_incrementor(
        array: &mut [i32], 
        max: i32
    ) -> Box<dyn ArrayIncrementor + '_> {
        Box::new(LeftSequenceIncrementor::new(array, max))
    }
    
    /// Create a partition array incrementor.
    /// 
    /// # Arguments
    /// * `array` - The array to increment
    /// * `max` - Maximum value for each element
    /// 
    /// # Returns
    /// A boxed ArrayIncrementor
    pub fn partition_array_incrementor(
        array: &mut [i32], 
        max: i32
    ) -> Box<dyn ArrayIncrementor + '_> {
        Box::new(PartitionArrayIncrementor::new(array, max))
    }
    
    /// Generate all possible tuples with entries between 0 and max.
    /// 
    /// # Arguments
    /// * `length` - Length of each tuple
    /// * `max` - Maximum value for each element
    /// 
    /// # Returns
    /// A vector of all possible tuples
    pub fn generate_all_sequences(length: usize, max: i32) -> Vec<Vec<i32>> {
        let mut result = Vec::new();
        let mut array = vec![0; length];
        
        // Add the initial sequence
        result.push(array.clone());
        
        // Generate all remaining sequences
        loop {
            // Create a temporary copy for the incrementor
            let mut temp_array = array.clone();
            let mut incrementor = Self::sequence_incrementor(&mut temp_array, max);
            if !incrementor.increment() {
                break;
            }
            // Get the updated array from the incrementor
            array = incrementor.get_current();
            result.push(array.clone());
        }
        
        result
    }
    
    /// Generate all possible tuples with entries between 0 and max,
    /// subject to the restriction that the last coordinate is at least min.
    /// 
    /// # Arguments
    /// * `length` - Length of each tuple
    /// * `max` - Maximum value for each element
    /// * `min` - Minimum value that must appear in the array
    /// 
    /// # Returns
    /// A vector of all possible tuples
    pub fn generate_all_sequences_with_min(length: usize, max: i32, min: i32) -> Vec<Vec<i32>> {
        let mut result = Vec::new();
        let mut array = vec![0; length];
        
        // Add the initial sequence
        result.push(array.clone());
        
        // Generate all remaining sequences
        loop {
            // Create a temporary copy for the incrementor
            let mut temp_array = array.clone();
            let mut incrementor = Self::sequence_incrementor_with_min(&mut temp_array, max, min);
            if !incrementor.increment() {
                break;
            }
            // Get the updated array from the incrementor
            array = incrementor.get_current();
            result.push(array.clone());
        }
        
        result
    }
    
    /// Get the initial partition on size with num_blocks blocks in JB form.
    /// This creates a partition where the first num_blocks elements are 0, 1, 2, ..., num_blocks-1
    /// and the remaining elements are num_blocks-1.
    pub fn initial_partition(size: usize, num_blocks: usize) -> Vec<i32> {
        let mut partition = vec![0; size];
        for i in 0..size {
            if i < num_blocks {
                partition[i] = i as i32;
            } else {
                partition[i] = (num_blocks - 1) as i32;
            }
        }
        partition
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sequence_incrementor() {
        let mut array = [0, 0, 0];
        let mut incrementor = SequenceGenerator::sequence_incrementor(&mut array, 2);
        
        let mut sequences = Vec::new();
        sequences.push(incrementor.get_current());
        
        while incrementor.increment() {
            sequences.push(incrementor.get_current());
        }
        
        let expected = vec![
            vec![0, 0, 0],
            vec![0, 0, 1],
            vec![0, 0, 2],
            vec![0, 1, 0],
            vec![0, 1, 1],
            vec![0, 1, 2],
            vec![0, 2, 0],
            vec![0, 2, 1],
            vec![0, 2, 2],
            vec![1, 0, 0],
            vec![1, 0, 1],
            vec![1, 0, 2],
            vec![1, 1, 0],
            vec![1, 1, 1],
            vec![1, 1, 2],
            vec![1, 2, 0],
            vec![1, 2, 1],
            vec![1, 2, 2],
            vec![2, 0, 0],
            vec![2, 0, 1],
            vec![2, 0, 2],
            vec![2, 1, 0],
            vec![2, 1, 1],
            vec![2, 1, 2],
            vec![2, 2, 0],
            vec![2, 2, 1],
            vec![2, 2, 2],
        ];
        
        assert_eq!(sequences, expected);
    }

    #[test]
    fn test_sequence_incrementor_with_min() {
        let mut array = [0, 0, 0];
        let mut incrementor = SequenceGenerator::sequence_incrementor_with_min(&mut array, 2, 1);
        
        let mut sequences = Vec::new();
        sequences.push(incrementor.get_current());
        
        while incrementor.increment() {
            sequences.push(incrementor.get_current());
        }
        
        // All sequences should have at least one element >= 1
        for seq in &sequences {
            assert!(seq.iter().any(|&x| x >= 1));
        }
        
        // Should have fewer sequences than without the min constraint
        assert!(sequences.len() < 27);
    }

    #[test]
    fn test_generate_all_sequences() {
        let sequences = SequenceGenerator::generate_all_sequences(2, 1);
        let expected = vec![
            vec![0, 0],
            vec![0, 1],
            vec![1, 0],
            vec![1, 1],
        ];
        
        assert_eq!(sequences, expected);
    }
}