/*! BasicSet implementation.

This module provides a set data structure for working with sets of integers,
primarily representing subsets of {0, 1, ..., n-1}.

The implementation is based on the Java `org.uacalc.alg.sublat.BasicSet` class.
*/

use std::cmp::Ordering;
use std::fmt;
use std::hash::{Hash, Hasher};
use once_cell::sync::Lazy;

/// A set of integers with basic set operations.
/// 
/// BasicSet represents a subset of {0, 1, ..., n-1} and provides
/// efficient set operations like union, intersection, difference, and
/// membership testing. Elements are always kept in sorted order.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BasicSet {
    /// The elements of the set, always sorted in ascending order
    pub elements: Vec<i32>,
}

/// Empty set constant
pub static EMPTY_SET: Lazy<BasicSet> = Lazy::new(|| BasicSet {
    elements: Vec::new(),
});

impl BasicSet {
    /// Create a new BasicSet from a vector of elements.
    /// 
    /// The elements will be automatically sorted and normalized.
    /// 
    /// # Arguments
    /// * `elements` - Vector of integers to include in the set
    /// 
    /// # Returns
    /// * `BasicSet` - A new set with sorted elements
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set = BasicSet::new(vec![3, 1, 2]);
    /// assert_eq!(set.elements, vec![1, 2, 3]);
    /// ```
    pub fn new(mut elements: Vec<i32>) -> Self {
        elements.sort_unstable();
        BasicSet { elements }
    }
    
    /// Create an empty set.
    /// 
    /// # Returns
    /// * `BasicSet` - An empty set
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set = BasicSet::empty();
    /// assert_eq!(set.universe_size(), 0);
    /// ```
    pub fn empty() -> Self {
        BasicSet {
            elements: Vec::new(),
        }
    }
    
    /// Normalize the set by sorting elements in ascending order.
    /// 
    /// This modifies the internal array to ensure elements are sorted.
    /// Note: In the normal constructor, normalization happens automatically.
    pub fn normalize(&mut self) {
        self.elements.sort_unstable();
    }
    
    /// Get the size of the set (number of elements).
    /// 
    /// # Returns
    /// * `usize` - The number of elements in the set
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set = BasicSet::new(vec![1, 2, 3]);
    /// assert_eq!(set.universe_size(), 3);
    /// ```
    pub fn universe_size(&self) -> usize {
        self.elements.len()
    }
    
    /// Get an element at the specified index.
    /// 
    /// # Arguments
    /// * `index` - The index to access
    /// 
    /// # Returns
    /// * `i32` - The element at the index
    /// 
    /// # Panics
    /// Panics if the index is out of bounds.
    pub fn get(&self, index: usize) -> i32 {
        self.elements[index]
    }
    
    /// Get the underlying array as a slice.
    /// 
    /// # Returns
    /// * `&[i32]` - Slice of the internal array
    pub fn to_array(&self) -> &[i32] {
        &self.elements
    }
    
    /// Check if this set is a subset of another set.
    /// 
    /// Both sets are assumed to be sorted.
    /// 
    /// # Arguments
    /// * `set2` - The set to check against
    /// 
    /// # Returns
    /// * `bool` - true if this is a subset of set2
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set1 = BasicSet::new(vec![1, 2]);
    /// let set2 = BasicSet::new(vec![1, 2, 3]);
    /// assert!(set1.leq(&set2));
    /// assert!(!set2.leq(&set1));
    /// ```
    pub fn leq(&self, set2: &BasicSet) -> bool {
        Self::leq_arrays(&self.elements, &set2.elements)
    }
    
    /// Static method to check if array u is a subset of array v.
    /// 
    /// Both arrays are assumed to be sorted.
    /// 
    /// # Arguments
    /// * `u` - First sorted array
    /// * `v` - Second sorted array
    /// 
    /// # Returns
    /// * `bool` - true if u is a subset of v
    pub fn leq_arrays(u: &[i32], v: &[i32]) -> bool {
        let n = u.len();
        let m = v.len();
        
        if m < n {
            return false;
        }
        
        let mut j = 0;
        for i in 0..n {
            let mut found = false;
            while j < m {
                if u[i] < v[j] {
                    return false;
                }
                if u[i] == v[j] {
                    found = true;
                    break;
                }
                j += 1;
            }
            if !found {
                return false;
            }
        }
        true
    }
    
    /// Check if the set contains a specific element.
    /// 
    /// Uses binary search for O(log n) performance.
    /// 
    /// # Arguments
    /// * `i` - The element to search for
    /// 
    /// # Returns
    /// * `bool` - true if the element is in the set
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set = BasicSet::new(vec![1, 2, 3]);
    /// assert!(set.contains(2));
    /// assert!(!set.contains(4));
    /// ```
    pub fn contains(&self, i: i32) -> bool {
        self.elements.binary_search(&i).is_ok()
    }
    
    /// Compute the set difference (this - set2).
    /// 
    /// Returns a new set containing elements that are in this set
    /// but not in set2.
    /// 
    /// # Arguments
    /// * `set2` - The set to subtract
    /// 
    /// # Returns
    /// * `BasicSet` - A new set with the difference
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set1 = BasicSet::new(vec![1, 2, 3]);
    /// let set2 = BasicSet::new(vec![2, 3, 4]);
    /// let diff = set1.set_difference(&set2);
    /// assert_eq!(diff.elements, vec![1]);
    /// ```
    pub fn set_difference(&self, set2: &BasicSet) -> BasicSet {
        let mut result = Vec::new();
        for &elem in &self.elements {
            if !set2.contains(elem) {
                result.push(elem);
            }
        }
        BasicSet::new(result)
    }
    
    /// Compute the intersection of this set with another.
    /// 
    /// Returns a new set containing elements that are in both sets.
    /// 
    /// # Arguments
    /// * `set2` - The set to intersect with
    /// 
    /// # Returns
    /// * `BasicSet` - A new set with the intersection
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set1 = BasicSet::new(vec![1, 2, 3]);
    /// let set2 = BasicSet::new(vec![2, 3, 4]);
    /// let inter = set1.intersection(&set2);
    /// assert_eq!(inter.elements, vec![2, 3]);
    /// ```
    pub fn intersection(&self, set2: &BasicSet) -> BasicSet {
        Self::intersection_static(self, set2)
    }
    
    /// Static method to compute the intersection of two sets.
    /// 
    /// # Arguments
    /// * `set1` - First set
    /// * `set2` - Second set
    /// 
    /// # Returns
    /// * `BasicSet` - A new set with the intersection
    pub fn intersection_static(set1: &BasicSet, set2: &BasicSet) -> BasicSet {
        let mut result = Vec::new();
        for &elem in &set1.elements {
            if set2.contains(elem) {
                result.push(elem);
            }
        }
        BasicSet::new(result)
    }
    
    /// Compute the union of this set with another.
    /// 
    /// Returns a new set containing elements that are in either set.
    /// 
    /// # Arguments
    /// * `set2` - The set to union with
    /// 
    /// # Returns
    /// * `BasicSet` - A new set with the union
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set1 = BasicSet::new(vec![1, 2]);
    /// let set2 = BasicSet::new(vec![2, 3]);
    /// let u = set1.union(&set2);
    /// assert_eq!(u.elements, vec![1, 2, 3]);
    /// ```
    pub fn union(&self, set2: &BasicSet) -> BasicSet {
        Self::union_static(self, set2)
    }
    
    /// Static method to compute the union of two sets.
    /// 
    /// # Arguments
    /// * `set1` - First set
    /// * `set2` - Second set
    /// 
    /// # Returns
    /// * `BasicSet` - A new set with the union
    pub fn union_static(set1: &BasicSet, set2: &BasicSet) -> BasicSet {
        let mut result = Vec::new();
        
        // Add all elements from set1
        result.extend_from_slice(&set1.elements);
        
        // Add elements from set2 that are not already in the result
        for &elem in &set2.elements {
            if !result.contains(&elem) {
                result.push(elem);
            }
        }
        
        BasicSet::new(result)
    }
    
    /// Convert the set to a string representation using algebra elements.
    /// 
    /// This is a placeholder for compatibility with the Java API.
    /// The actual implementation would require SmallAlgebra integration.
    /// 
    /// # Arguments
    /// * `_alg` - The algebra (currently unused)
    /// 
    /// # Returns
    /// * `String` - String representation of the set
    pub fn to_string_with_algebra(&self, _alg: Option<&str>) -> String {
        // Placeholder implementation
        // In the full implementation, this would use SmallAlgebra to
        // format elements according to the algebra's element representation
        self.to_string()
    }
}

impl PartialOrd for BasicSet {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for BasicSet {
    /// Compare two sets using size first, then lexicographic order.
    /// 
    /// This implements the Comparable interface from Java.
    fn cmp(&self, other: &Self) -> Ordering {
        let n = self.universe_size();
        let m = other.universe_size();
        
        // First compare by size
        match n.cmp(&m) {
            Ordering::Equal => {
                // If sizes are equal, compare lexicographically
                for i in 0..n {
                    match self.get(i).cmp(&other.get(i)) {
                        Ordering::Equal => continue,
                        other_order => return other_order,
                    }
                }
                Ordering::Equal
            }
            other_order => other_order,
        }
    }
}

impl Hash for BasicSet {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.elements.hash(state);
    }
}

impl fmt::Display for BasicSet {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{{")?;
        for (i, &elem) in self.elements.iter().enumerate() {
            if i > 0 {
                write!(f, ",")?;
            }
            write!(f, "{}", elem)?;
        }
        write!(f, "}}")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_new() {
        let set = BasicSet::new(vec![3, 1, 2]);
        assert_eq!(set.elements, vec![1, 2, 3]);
    }
    
    #[test]
    fn test_empty() {
        let set = BasicSet::empty();
        assert_eq!(set.universe_size(), 0);
        assert_eq!(set.elements.len(), 0);
    }
    
    #[test]
    fn test_empty_set_constant() {
        let empty = &*EMPTY_SET;
        assert_eq!(empty.universe_size(), 0);
    }
    
    #[test]
    fn test_normalize() {
        let mut set = BasicSet {
            elements: vec![3, 1, 2],
        };
        set.normalize();
        assert_eq!(set.elements, vec![1, 2, 3]);
    }
    
    #[test]
    fn test_universe_size() {
        let set = BasicSet::new(vec![1, 2, 3]);
        assert_eq!(set.universe_size(), 3);
    }
    
    #[test]
    fn test_get() {
        let set = BasicSet::new(vec![1, 2, 3]);
        assert_eq!(set.get(0), 1);
        assert_eq!(set.get(1), 2);
        assert_eq!(set.get(2), 3);
    }
    
    #[test]
    fn test_contains() {
        let set = BasicSet::new(vec![1, 3, 5]);
        assert!(set.contains(1));
        assert!(set.contains(3));
        assert!(set.contains(5));
        assert!(!set.contains(2));
        assert!(!set.contains(4));
    }
    
    #[test]
    fn test_leq() {
        let set1 = BasicSet::new(vec![1, 2]);
        let set2 = BasicSet::new(vec![1, 2, 3]);
        let set3 = BasicSet::new(vec![1, 3]);
        
        assert!(set1.leq(&set2));
        assert!(!set2.leq(&set1));
        assert!(!set1.leq(&set3));
    }
    
    #[test]
    fn test_set_difference() {
        let set1 = BasicSet::new(vec![1, 2, 3]);
        let set2 = BasicSet::new(vec![2, 3, 4]);
        let diff = set1.set_difference(&set2);
        assert_eq!(diff.elements, vec![1]);
    }
    
    #[test]
    fn test_intersection() {
        let set1 = BasicSet::new(vec![1, 2, 3]);
        let set2 = BasicSet::new(vec![2, 3, 4]);
        let inter = set1.intersection(&set2);
        assert_eq!(inter.elements, vec![2, 3]);
    }
    
    #[test]
    fn test_intersection_static() {
        let set1 = BasicSet::new(vec![1, 2, 3]);
        let set2 = BasicSet::new(vec![2, 3, 4]);
        let inter = BasicSet::intersection_static(&set1, &set2);
        assert_eq!(inter.elements, vec![2, 3]);
    }
    
    #[test]
    fn test_union() {
        let set1 = BasicSet::new(vec![1, 2]);
        let set2 = BasicSet::new(vec![2, 3]);
        let u = set1.union(&set2);
        assert_eq!(u.elements, vec![1, 2, 3]);
    }
    
    #[test]
    fn test_union_static() {
        let set1 = BasicSet::new(vec![1, 2]);
        let set2 = BasicSet::new(vec![2, 3]);
        let u = BasicSet::union_static(&set1, &set2);
        assert_eq!(u.elements, vec![1, 2, 3]);
    }
    
    #[test]
    fn test_compare_to() {
        let set1 = BasicSet::new(vec![1, 2]);
        let set2 = BasicSet::new(vec![1, 2, 3]);
        let set3 = BasicSet::new(vec![1, 3]);
        let set4 = BasicSet::new(vec![1, 2]);
        
        // Compare by size first
        assert_eq!(set1.cmp(&set2), Ordering::Less);
        assert_eq!(set2.cmp(&set1), Ordering::Greater);
        
        // Compare lexicographically if sizes are equal
        assert_eq!(set1.cmp(&set3), Ordering::Less);
        assert_eq!(set3.cmp(&set1), Ordering::Greater);
        assert_eq!(set1.cmp(&set4), Ordering::Equal);
    }
    
    #[test]
    fn test_equality() {
        let set1 = BasicSet::new(vec![1, 2, 3]);
        let set2 = BasicSet::new(vec![1, 2, 3]);
        let set3 = BasicSet::new(vec![1, 2, 4]);
        
        assert_eq!(set1, set2);
        assert_ne!(set1, set3);
    }
    
    #[test]
    fn test_hash() {
        use std::collections::hash_map::DefaultHasher;
        
        let set1 = BasicSet::new(vec![1, 2, 3]);
        let set2 = BasicSet::new(vec![1, 2, 3]);
        let set3 = BasicSet::new(vec![1, 2, 4]);
        
        let mut hasher1 = DefaultHasher::new();
        let mut hasher2 = DefaultHasher::new();
        let mut hasher3 = DefaultHasher::new();
        
        set1.hash(&mut hasher1);
        set2.hash(&mut hasher2);
        set3.hash(&mut hasher3);
        
        assert_eq!(hasher1.finish(), hasher2.finish());
        assert_ne!(hasher1.finish(), hasher3.finish());
    }
    
    #[test]
    fn test_to_string() {
        let set = BasicSet::new(vec![1, 2, 3]);
        assert_eq!(set.to_string(), "{1,2,3}");
        
        let empty = BasicSet::empty();
        assert_eq!(empty.to_string(), "{}");
    }
}
