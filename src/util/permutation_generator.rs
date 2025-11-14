use std::hash::{Hash, Hasher};
use super::array_incrementor::ArrayIncrementor;

/// Permutation generator using the Johnson-Trotter algorithm.
/// 
/// This class is used to help generate permutations of arrays. It has
/// one public method: `next_index()` which returns the index i such that 
/// the next permutation should interchange the i-th and following elements.
/// 
/// Using this one can start with a fixed array or List and modify it in
/// place, generating all permutations of the elements. Note if the two
/// elements to be interchanged are the same, `next_index()` can
/// just be called again.
/// 
/// This class has static methods giving both an Iterator and an
/// (in place) ArrayIncrementor.
/// 
/// This uses the Johnson-Trotter algorithm:
/// start with the identity permutation and with the direction of
/// each integer left. If there is a mobile integer k, 
/// find the largest one, swap it with the neighbor it points to, 
/// and reverse the arrows of all integers larger than k. 
/// Mobile means pointing to a smaller integer.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PermutationGenerator {
    n: usize,
    a: Vec<usize>,
    arrows: Vec<bool>, // false for left, true for right
    largest_mobile_index: Option<usize>, // only used in the iterator
}

impl PermutationGenerator {
    /// Create a new PermutationGenerator for permutations of n elements.
    /// 
    /// # Arguments
    /// * `n` - The number of elements to permute (must be >= 1)
    /// 
    /// # Panics
    /// Panics if n < 1
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::PermutationGenerator;
    /// let generator = PermutationGenerator::new(3);
    /// ```
    pub fn new(n: usize) -> Self {
        if n < 1 {
            panic!("Min 1");
        }
        
        let mut generator = Self {
            n,
            a: vec![0; n],
            arrows: vec![false; n],
            largest_mobile_index: None,
        };
        generator.reset();
        generator
    }
    
    /// Create a new PermutationGenerator for permutations of n elements.
    /// 
    /// # Arguments
    /// * `n` - The number of elements to permute (must be >= 1)
    /// 
    /// # Returns
    /// * `Ok(Self)` - The new PermutationGenerator
    /// * `Err(String)` - If n < 1
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::PermutationGenerator;
    /// let generator = PermutationGenerator::new_safe(3).unwrap();
    /// ```
    pub fn new_safe(n: usize) -> Result<Self, String> {
        if n < 1 {
            return Err("Min 1".to_string());
        }
        
        let mut generator = Self {
            n,
            a: vec![0; n],
            arrows: vec![false; n],
            largest_mobile_index: None,
        };
        generator.reset();
        Ok(generator)
    }
    
    /// Reset the generator to the initial state (identity permutation).
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::PermutationGenerator;
    /// let mut generator = PermutationGenerator::new(3);
    /// generator.reset();
    /// ```
    pub fn reset(&mut self) {
        self.arrows = vec![false; self.n];
        for i in 0..self.n {
            self.a[i] = i;
        }
        self.largest_mobile_index = None;
    }
    
    /// Get the current permutation array.
    /// 
    /// # Returns
    /// A reference to the current permutation array
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::PermutationGenerator;
    /// let generator = PermutationGenerator::new(3);
    /// let perm = generator.get_permutation();
    /// assert_eq!(perm, &[0, 1, 2]);
    /// ```
    pub fn get_permutation(&self) -> &[usize] {
        &self.a
    }
    
    /// Get the current permutation array as a vector.
    /// 
    /// # Returns
    /// A copy of the current permutation array
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::PermutationGenerator;
    /// let generator = PermutationGenerator::new(3);
    /// let perm = generator.get_permutation_vec();
    /// assert_eq!(perm, vec![0, 1, 2]);
    /// ```
    pub fn get_permutation_vec(&self) -> Vec<usize> {
        self.a.clone()
    }
    
    /// Get the size of the permutation.
    /// 
    /// # Returns
    /// The number of elements being permuted
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::PermutationGenerator;
    /// let generator = PermutationGenerator::new(5);
    /// assert_eq!(generator.size(), 5);
    /// ```
    pub fn size(&self) -> usize {
        self.n
    }
    
    /// Get the next index for permutation.
    /// 
    /// Returns the index i such that the next permutation should interchange 
    /// the i-th and following elements. Returns None if no more permutations.
    /// 
    /// # Returns
    /// * `Some(usize)` - The index to swap with the next element
    /// * `None` - If no more permutations are available
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::PermutationGenerator;
    /// let mut generator = PermutationGenerator::new(3);
    /// let index = generator.next_index();
    /// // index will be Some(1) for the first swap
    /// ```
    pub fn next_index(&mut self) -> Option<usize> {
        let k = self.largest_mobile_index.or_else(|| self.find_largest_mobile_index());
        let k = match k {
            Some(k) => k,
            None => return None,
        };
        
        let ans = if self.arrows[self.a[k]] { k } else { k - 1 };
        let largest_mob = self.a[k];
        
        // Reverse arrows for all integers larger than the largest mobile
        for i in (largest_mob + 1)..self.n {
            self.arrows[i] = !self.arrows[i];
        }
        
        // Swap elements
        self.a.swap(ans, ans + 1);
        
        Some(ans)
    }
    
    /// Get the next index for permutation with error handling.
    /// 
    /// Returns the index i such that the next permutation should interchange 
    /// the i-th and following elements. Returns an error if no more permutations.
    /// 
    /// # Returns
    /// * `Ok(usize)` - The index to swap with the next element
    /// * `Err(String)` - If no more permutations are available
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::PermutationGenerator;
    /// let mut generator = PermutationGenerator::new(3);
    /// let index = generator.next_index_safe().unwrap();
    /// // index will be 1 for the first swap
    /// ```
    pub fn next_index_safe(&mut self) -> Result<usize, String> {
        match self.next_index() {
            Some(index) => Ok(index),
            None => Err("No more permutations".to_string()),
        }
    }
    
    /// Finds the index of the largest mobile element (not the largest index).
    /// 
    /// # Returns
    /// * `Some(usize)` - The index of the largest mobile element
    /// * `None` - If no mobile element exists
    fn find_largest_mobile_index(&self) -> Option<usize> {
        let mut largest_mob = 0;
        let mut largest_mobile_ind = None;
        
        for i in 0..self.n {
            if self.a[i] > largest_mob {
                let is_mobile = if self.arrows[self.a[i]] {
                    // Arrow points right
                    i != self.n - 1 && self.a[i] > self.a[i + 1]
                } else {
                    // Arrow points left
                    i != 0 && self.a[i] > self.a[i - 1]
                };
                
                if is_mobile {
                    largest_mobile_ind = Some(i);
                    largest_mob = self.a[i];
                }
            }
        }
        
        largest_mobile_ind
    }
    
    /// Create an iterator over all permutations.
    /// 
    /// This iterator iterates all permutations on the set 0, ..., n-1.
    /// The iteration is on a fixed array so one needs to be careful to
    /// copy any permutation that needs to be saved.
    /// 
    /// # Arguments
    /// * `n` - The number of elements to permute
    /// 
    /// # Returns
    /// An iterator that yields permutation arrays
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::PermutationGenerator;
    /// let mut count = 0;
    /// for perm in PermutationGenerator::iterator(3) {
    ///     count += 1;
    /// }
    /// assert_eq!(count, 6); // 3! = 6
    /// ```
    pub fn iterator(n: usize) -> PermutationIterator {
        PermutationIterator::new(n)
    }
    
    /// Create an array incrementor for the given array.
    /// 
    /// This increments arr, applying the next transposition that results
    /// in a different array.
    /// The iteration is on a fixed array so one needs to be careful to
    /// copy any result that needs to be saved.
    /// 
    /// # Arguments
    /// * `arr` - The array to increment
    /// 
    /// # Returns
    /// An ArrayIncrementor that modifies the array in place
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::{PermutationGenerator, ArrayIncrementor};
    /// let mut arr = vec![0, 1, 2];
    /// let mut incrementor = PermutationGenerator::array_incrementor(&mut arr);
    /// while incrementor.increment() {
    ///     // println!("{:?}", arr); // Commented out to avoid borrow checker issues in doctest
    /// }
    /// ```
    pub fn array_incrementor(arr: &mut [usize]) -> super::array_incrementor::ArrayIncrementorImpl<'_> {
        super::array_incrementor::ArrayIncrementorImpl::new(arr)
    }
    
    /// Create a list incrementor for the given list.
    /// 
    /// This increments lst, applying the next transposition that results
    /// in a different list.
    /// The iteration is on a fixed list so one needs to be careful to
    /// copy any result that needs to be saved.
    /// 
    /// # Arguments
    /// * `lst` - The list to increment
    /// 
    /// # Returns
    /// An ArrayIncrementor that modifies the list in place
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::{PermutationGenerator, ArrayIncrementor};
    /// let mut lst = vec![0, 1, 2];
    /// let mut incrementor = PermutationGenerator::list_incrementor(&mut lst);
    /// while incrementor.increment() {
    ///     // println!("{:?}", lst); // Commented out to avoid borrow checker issues in doctest
    /// }
    /// ```
    pub fn list_incrementor<T: Clone + PartialEq>(lst: &mut Vec<T>) -> ListIncrementorImpl<'_, T> {
        ListIncrementorImpl::new(lst)
    }
}

impl Hash for PermutationGenerator {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.n.hash(state);
        self.a.hash(state);
        self.arrows.hash(state);
    }
}

impl std::fmt::Display for PermutationGenerator {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "PermutationGenerator(n={}, perm={:?})", self.n, self.a)
    }
}

/// Iterator over all permutations using PermutationGenerator.
pub struct PermutationIterator {
    generator: PermutationGenerator,
    first: bool,
}

impl PermutationIterator {
    fn new(n: usize) -> Self {
        Self {
            generator: PermutationGenerator::new(n),
            first: true,
        }
    }
}

impl Iterator for PermutationIterator {
    type Item = Vec<usize>;
    
    fn next(&mut self) -> Option<Self::Item> {
        if self.first {
            self.first = false;
            return Some(self.generator.get_permutation_vec());
        }
        
        match self.generator.next_index() {
            Some(_) => Some(self.generator.get_permutation_vec()),
            None => None,
        }
    }
}


/// List incrementor implementation for generic lists.
pub struct ListIncrementorImpl<'a, T: Clone + PartialEq> {
    generator: PermutationGenerator,
    lst: &'a mut Vec<T>,
}

impl<'a, T: Clone + PartialEq> ListIncrementorImpl<'a, T> {
    fn new(lst: &'a mut Vec<T>) -> Self {
        Self {
            generator: PermutationGenerator::new(lst.len()),
            lst,
        }
    }
    
    fn swap(&mut self, k: usize) {
        self.lst.swap(k, k + 1);
    }
}

impl<'a, T: Clone + PartialEq> ArrayIncrementor for ListIncrementorImpl<'a, T> {
    fn increment(&mut self) -> bool {
        loop {
            match self.generator.next_index() {
                Some(k) => {
                    if self.lst[k] != self.lst[k + 1] {
                        self.swap(k);
                        return true;
                    }
                    // If elements are equal, continue to next permutation
                }
                None => {
                    // Reset to original state if list has more than 1 element
                    if self.lst.len() > 1 {
                        self.swap(0);
                    }
                    return false;
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::hash_map::DefaultHasher;
    
    #[test]
    fn test_new() {
        let gen = PermutationGenerator::new(3);
        assert_eq!(gen.size(), 3);
        assert_eq!(gen.get_permutation(), &[0, 1, 2]);
    }
    
    #[test]
    fn test_new_safe() {
        let gen = PermutationGenerator::new_safe(3).unwrap();
        assert_eq!(gen.size(), 3);
        assert_eq!(gen.get_permutation(), &[0, 1, 2]);
    }
    
    #[test]
    fn test_new_safe_invalid() {
        let result = PermutationGenerator::new_safe(0);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_reset() {
        let mut gen = PermutationGenerator::new(3);
        gen.next_index();
        gen.reset();
        assert_eq!(gen.get_permutation(), &[0, 1, 2]);
    }
    
    #[test]
    fn test_next_index() {
        let mut gen = PermutationGenerator::new(3);
        // First permutation: [0, 1, 2], next swap at index 1 -> [0, 2, 1]
        let index = gen.next_index();
        assert_eq!(index, Some(1));
        assert_eq!(gen.get_permutation(), &[0, 2, 1]);
    }
    
    #[test]
    fn test_iterator() {
        let mut count = 0;
        for _perm in PermutationGenerator::iterator(3) {
            count += 1;
        }
        assert_eq!(count, 6); // 3! = 6
    }
    
    #[test]
    fn test_array_incrementor() {
        let mut arr = vec![0, 1, 2];
        let mut incrementor = PermutationGenerator::array_incrementor(&mut arr);
        
        let mut count = 0;
        while incrementor.increment() {
            count += 1;
        }
        assert_eq!(count, 5); // 6 permutations - 1 initial = 5 increments
        assert_eq!(arr, vec![0, 1, 2]); // Should be back to original
    }
    
    #[test]
    fn test_list_incrementor() {
        let mut lst = vec!["a", "b", "c"];
        let mut incrementor = PermutationGenerator::list_incrementor(&mut lst);
        
        let mut count = 0;
        while incrementor.increment() {
            count += 1;
        }
        assert_eq!(count, 5); // 6 permutations - 1 initial = 5 increments
        assert_eq!(lst, vec!["a", "b", "c"]); // Should be back to original
    }
    
    #[test]
    fn test_display() {
        let gen = PermutationGenerator::new(3);
        let display = format!("{}", gen);
        assert!(display.contains("PermutationGenerator"));
        assert!(display.contains("n=3"));
        assert!(display.contains("[0, 1, 2]"));
    }
    
    #[test]
    fn test_hash() {
        let gen1 = PermutationGenerator::new(3);
        let gen2 = PermutationGenerator::new(3);
        
        let mut hasher1 = DefaultHasher::new();
        let mut hasher2 = DefaultHasher::new();
        
        gen1.hash(&mut hasher1);
        gen2.hash(&mut hasher2);
        
        assert_eq!(hasher1.finish(), hasher2.finish());
    }
}
