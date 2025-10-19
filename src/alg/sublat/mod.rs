use std::cmp::Ordering;
use std::collections::HashSet;
use std::fmt;
use std::hash::{Hash, Hasher};
use crate::util::int_array::IntArrayTrait;
use crate::util::array_string;
use crate::alg::small_algebra::SmallAlgebra;

/// A basic set implementation for representing sets of integers {0, 1, ..., n-1}.
/// 
/// This struct provides basic set operations including union, intersection, difference,
/// and membership testing. It extends the functionality of IntArray with set-specific
/// operations and maintains elements in sorted order for efficient operations.
/// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::BasicSet;
/// 
/// let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
/// let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
/// 
/// let intersection = set1.intersection(&set2);
/// assert_eq!(intersection.elements(), &vec![3]);
/// ```
#[derive(Debug, Clone)]
pub struct BasicSet {
    /// The elements of the set, stored in sorted order
    pub elements: Vec<i32>,
}

impl BasicSet {
    /// Empty set constant
    pub const EMPTY_SET: BasicSet = BasicSet { elements: vec![] };
    
    /// Create a new BasicSet from a vector of elements.
    /// 
    /// The elements will be automatically sorted and deduplicated.
    /// 
    /// # Arguments
    /// * `elements` - Vector of integers to include in the set
    /// 
    /// # Returns
    /// * `Ok(BasicSet)` - Successfully created set
    /// * `Err(String)` - If elements contain invalid values
    /// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::BasicSet;
/// 
/// let set = BasicSet::new(vec![3, 1, 2]).unwrap();
/// assert_eq!(set.elements(), &vec![1, 2, 3]);
/// ```
    pub fn new(elements: Vec<i32>) -> Result<Self, String> {
        let mut set = BasicSet { elements };
        set.normalize();
        Ok(set)
    }
    
    /// Create a new BasicSet with proper error handling.
    /// 
    /// # Arguments
    /// * `elements` - Vector of integers to include in the set
    /// 
    /// # Returns
    /// * `Ok(BasicSet)` - Successfully created set
    /// * `Err(String)` - If elements contain invalid values
    pub fn new_safe(elements: Vec<i32>) -> Result<Self, String> {
        Self::new(elements)
    }
    
    /// Get the elements of the set.
    /// 
    /// # Returns
    /// A reference to the sorted elements vector
    pub fn elements(&self) -> &Vec<i32> {
        &self.elements
    }
    
    /// Get the size of the set (number of elements).
    /// 
    /// # Returns
    /// The number of elements in the set
    pub fn size(&self) -> usize {
        self.elements.len()
    }
    
    /// Get the universe size (same as size for BasicSet).
    /// 
    /// # Returns
    /// The number of elements in the set
    pub fn universe_size(&self) -> usize {
        self.elements.len()
    }
    
    /// Normalize the set by sorting elements and removing duplicates.
    /// 
    /// This method modifies the internal elements vector to ensure
    /// they are in ascending order with no duplicates.
    pub fn normalize(&mut self) {
        // Remove duplicates using HashSet
        let unique_elements: HashSet<i32> = self.elements.drain(..).collect();
        
        // Convert back to sorted vector
        self.elements = unique_elements.into_iter().collect();
        self.elements.sort();
    }
    
    /// Check if this set is a subset of another set.
    /// 
    /// # Arguments
    /// * `other` - The set to compare against
    /// 
    /// # Returns
    /// * `true` if this set is a subset of other
    /// * `false` otherwise
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set1 = BasicSet::new(vec![1, 2]).unwrap();
    /// let set2 = BasicSet::new(vec![1, 2, 3, 4]).unwrap();
    /// assert!(set1.leq(&set2));
    /// ```
    pub fn leq(&self, other: &BasicSet) -> bool {
        Self::leq_static(&self.elements, &other.elements)
    }
    
    /// Static method to check if one array is a subset of another.
    /// 
    /// # Arguments
    /// * `u` - First array (sorted)
    /// * `v` - Second array (sorted)
    /// 
    /// # Returns
    /// * `true` if u is a subset of v
    /// * `false` otherwise
    pub fn leq_static(u: &[i32], v: &[i32]) -> bool {
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
                    j += 1;
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
    /// # Arguments
    /// * `element` - The element to search for
    /// 
    /// # Returns
    /// * `true` if the element is in the set
    /// * `false` otherwise
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set = BasicSet::new(vec![1, 3, 5]).unwrap();
    /// assert!(set.contains(3));
    /// assert!(!set.contains(2));
    /// ```
    pub fn contains(&self, element: i32) -> bool {
        self.elements.binary_search(&element).is_ok()
    }
    
    /// Compute the set difference (this - other).
    /// 
    /// # Arguments
    /// * `other` - The set to subtract
    /// 
    /// # Returns
    /// A new BasicSet containing elements in this set but not in other
    /// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::BasicSet;
/// 
/// let set1 = BasicSet::new(vec![1, 2, 3, 4]).unwrap();
/// let set2 = BasicSet::new(vec![2, 4]).unwrap();
/// let diff = set1.set_difference(&set2);
/// assert_eq!(diff.elements(), &vec![1, 3]);
/// ```
    pub fn set_difference(&self, other: &BasicSet) -> BasicSet {
        let mut result = Vec::new();
        for &element in &self.elements {
            if !other.contains(element) {
                result.push(element);
            }
        }
        BasicSet { elements: result }
    }
    
    /// Compute the intersection of this set with another.
    /// 
    /// # Arguments
    /// * `other` - The set to intersect with
    /// 
    /// # Returns
    /// A new BasicSet containing elements in both sets
    /// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::BasicSet;
/// 
/// let set1 = BasicSet::new(vec![1, 2, 3]).unwrap();
/// let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
/// let intersection = set1.intersection(&set2);
/// assert_eq!(intersection.elements(), &vec![2, 3]);
/// ```
    pub fn intersection(&self, other: &BasicSet) -> BasicSet {
        Self::intersection_static(self, other)
    }
    
    /// Static method to compute the intersection of two sets.
    /// 
    /// # Arguments
    /// * `set1` - First set
    /// * `set2` - Second set
    /// 
    /// # Returns
    /// A new BasicSet containing elements in both sets
    pub fn intersection_static(set1: &BasicSet, set2: &BasicSet) -> BasicSet {
        let mut result = Vec::new();
        for &element in &set1.elements {
            if set2.contains(element) {
                result.push(element);
            }
        }
        BasicSet { elements: result }
    }
    
    /// Compute the union of this set with another.
    /// 
    /// # Arguments
    /// * `other` - The set to union with
    /// 
    /// # Returns
    /// A new BasicSet containing elements from both sets
    /// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::BasicSet;
/// 
/// let set1 = BasicSet::new(vec![1, 2]).unwrap();
/// let set2 = BasicSet::new(vec![2, 3]).unwrap();
/// let union = set1.union(&set2);
/// assert_eq!(union.elements(), &vec![1, 2, 3]);
/// ```
    pub fn union(&self, other: &BasicSet) -> BasicSet {
        Self::union_static(self, other)
    }
    
    /// Static method to compute the union of two sets.
    /// 
    /// # Arguments
    /// * `set1` - First set
    /// * `set2` - Second set
    /// 
    /// # Returns
    /// A new BasicSet containing elements from both sets
    pub fn union_static(set1: &BasicSet, set2: &BasicSet) -> BasicSet {
        let mut result = Vec::new();
        
        // Add all elements from set1
        for &element in &set1.elements {
            result.push(element);
        }
        
        // Add elements from set2 that are not already in result
        for &element in &set2.elements {
            if !result.contains(&element) {
                result.push(element);
            }
        }
        
        // Sort the result
        result.sort();
        BasicSet { elements: result }
    }
    
    /// Convert the set to a string representation using algebra elements.
    /// 
    /// # Arguments
    /// * `alg` - The algebra to use for element representation
    /// 
    /// # Returns
    /// A string representation of the set using algebra elements
    pub fn to_string_with_algebra<T>(&self, alg: &dyn SmallAlgebra<UniverseItem = T>) -> String 
    where 
        T: std::fmt::Display + Clone + PartialEq + Eq + Hash + std::fmt::Debug
    {
        let mut result = String::from("{");
        for (i, &element) in self.elements.iter().enumerate() {
            if i > 0 {
                result.push(',');
            }
            if let Some(elem) = alg.get_element(element as usize) {
                result.push_str(&array_string::to_string(&[elem]));
            } else {
                result.push_str(&element.to_string());
            }
        }
        result.push('}');
        result
    }
}

impl PartialEq for BasicSet {
    fn eq(&self, other: &Self) -> bool {
        self.elements == other.elements
    }
}

impl Eq for BasicSet {}

impl PartialOrd for BasicSet {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for BasicSet {
    fn cmp(&self, other: &Self) -> Ordering {
        // First compare by size
        match self.size().cmp(&other.size()) {
            Ordering::Equal => {
                // Then compare lexicographically
                self.elements.cmp(&other.elements)
            }
            other => other,
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
        for (i, &element) in self.elements.iter().enumerate() {
            if i > 0 {
                write!(f, ",")?;
            }
            write!(f, "{}", element)?;
        }
        write!(f, "}}")
    }
}

impl IntArrayTrait for BasicSet {
    fn universe_size(&self) -> usize {
        self.universe_size()
    }
    
    fn as_slice(&self) -> &[i32] {
        &self.elements
    }
    
    fn get(&self, index: usize) -> Option<i32> {
        self.elements.get(index).copied()
    }
    
    fn set(&mut self, index: usize, value: i32) -> Result<(), String> {
        if index >= self.elements.len() {
            return Err("Index out of bounds".to_string());
        }
        self.elements[index] = value;
        self.normalize();
        Ok(())
    }
    
    fn satisfies_blocks_constraint(&self, blocks: &[Vec<usize>]) -> bool {
        // For BasicSet, we check if all elements in each block are the same
        for block in blocks {
            if block.is_empty() {
                continue;
            }
            let first_element = self.elements[block[0]];
            for &index in block.iter().skip(1) {
                if index < self.elements.len() && self.elements[index] != first_element {
                    return false;
                }
            }
        }
        true
    }
    
    fn satisfies_values_constraint(&self, values: &[(usize, i32)]) -> bool {
        for &(index, expected_value) in values {
            if index >= self.elements.len() || self.elements[index] != expected_value {
                return false;
            }
        }
        true
    }
    
    fn satisfies_set_constraint(&self, index: usize, possible_values: &HashSet<i32>) -> bool {
        if index >= self.elements.len() {
            return false;
        }
        possible_values.contains(&self.elements[index])
    }
    
    fn satisfies_congruence_constraint(&self, index: usize, alpha: &crate::alg::conlat::partition::Partition, elem_index: usize) -> bool {
        if index >= self.elements.len() || elem_index >= self.elements.len() {
            return false;
        }
        // Check if elements are in the same block of the partition
        alpha.is_related(index, elem_index)
    }
    
    fn is_idempotent(&self) -> bool {
        // For BasicSet, check if all elements are their own indices
        for (i, &element) in self.elements.iter().enumerate() {
            if element != i as i32 {
                return false;
            }
        }
        true
    }
    
    fn is_constant(&self) -> bool {
        if self.elements.is_empty() {
            return true;
        }
        let first = self.elements[0];
        self.elements.iter().all(|&x| x == first)
    }
    
    fn clone_array(&self) -> Box<dyn IntArrayTrait> {
        Box::new(self.clone())
    }
}

pub struct SubalgebraLattice {
    // TODO: Implement subalgebra lattice
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn test_basic_set_creation() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        assert_eq!(set.elements(), &[1, 3, 5]);
        assert_eq!(set.size(), 3);
    }

    #[test]
    fn test_basic_set_empty() {
        let set = BasicSet::new(vec![]).unwrap();
        assert_eq!(set.elements(), &[] as &[i32]);
        assert_eq!(set.size(), 0);
    }

    #[test]
    fn test_basic_set_duplicates() {
        let set = BasicSet::new(vec![1, 3, 1, 5, 3]).unwrap();
        // Should be normalized (sorted and deduplicated)
        assert_eq!(set.elements(), &[1, 3, 5]);
        assert_eq!(set.size(), 3);
    }

    #[test]
    fn test_basic_set_contains() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        assert!(set.contains(3));
        assert!(!set.contains(2));
    }

    #[test]
    fn test_basic_set_leq() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![1, 2, 3, 4, 5]).unwrap();
        assert!(set1.leq(&set2));
        assert!(!set2.leq(&set1));
    }

    #[test]
    fn test_basic_set_leq_static() {
        assert!(BasicSet::leq_static(&[1, 3], &[1, 2, 3, 4]));
        assert!(!BasicSet::leq_static(&[1, 2, 3, 4], &[1, 3]));
    }

    #[test]
    fn test_basic_set_intersection() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
        let intersection = set1.intersection(&set2);
        assert_eq!(intersection.elements(), &[3]);
    }

    #[test]
    fn test_basic_set_intersection_static() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
        let intersection = BasicSet::intersection_static(&set1, &set2);
        assert_eq!(intersection.elements(), &[3]);
    }

    #[test]
    fn test_basic_set_union() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
        let union = set1.union(&set2);
        assert_eq!(sorted(union.elements().clone()), vec![1, 2, 3, 4, 5]);
    }

    #[test]
    fn test_basic_set_union_static() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
        let union = BasicSet::union_static(&set1, &set2);
        assert_eq!(sorted(union.elements().clone()), vec![1, 2, 3, 4, 5]);
    }

    #[test]
    fn test_basic_set_difference() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
        let difference = set1.set_difference(&set2);
        assert_eq!(sorted(difference.elements().clone()), vec![1, 5]);
    }

    #[test]
    fn test_basic_set_normalize() {
        let mut set = BasicSet::new(vec![3, 1, 5, 1, 3]).unwrap();
        set.normalize();
        assert_eq!(set.elements(), &[1, 3, 5]);
    }

    #[test]
    fn test_basic_set_size() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        assert_eq!(set.size(), 3);
    }

    #[test]
    fn test_basic_set_universe_size() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        assert_eq!(set.universe_size(), 3);
    }

    #[test]
    fn test_basic_set_elements() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        assert_eq!(set.elements(), &[1, 3, 5]);
    }

    #[test]
    fn test_basic_set_comparison() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set3 = BasicSet::new(vec![1, 3, 6]).unwrap();
        
        assert_eq!(set1, set2);
        assert_ne!(set1, set3);
        assert!(set1 <= set2);
        assert!(set1 >= set2);
        assert!(set1 < set3);
    }

    #[test]
    fn test_basic_set_hash() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set3 = BasicSet::new(vec![1, 3, 6]).unwrap();
        
        let mut hash_set = HashSet::new();
        hash_set.insert(set1.clone());
        hash_set.insert(set2.clone());
        hash_set.insert(set3.clone());
        
        // set1 and set2 should be the same, so only 2 unique items
        assert_eq!(hash_set.len(), 2);
    }

    #[test]
    fn test_basic_set_display() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        let display_str = format!("{}", set);
        assert_eq!(display_str, "{1,3,5}");
    }

    #[test]
    fn test_basic_set_int_array_trait() {
        let mut set = BasicSet::new(vec![1, 3, 5]).unwrap();
        
        // Test IntArrayTrait implementation
        assert_eq!(set.universe_size(), 3);
        assert_eq!(set.get(0), Some(1));
        assert_eq!(set.get(1), Some(3));
        assert_eq!(set.get(2), Some(5));
        assert_eq!(set.get(3), None);
        
        // Test set method
        set.set(0, 2).unwrap();
        assert_eq!(set.get(0), Some(2));
        
        // Test as_slice
        let slice = set.as_slice();
        assert_eq!(slice, &[2, 3, 5]);
    }

    #[test]
    fn test_basic_set_constraints() {
        let set = BasicSet::new(vec![1, 2, 3]).unwrap();
        
        // Test values constraint
        let values = vec![(0, 1), (1, 2)];
        assert!(set.satisfies_values_constraint(&values));
        
        // Test set constraint
        let possible_values: HashSet<i32> = [1, 2, 3].iter().cloned().collect();
        assert!(set.satisfies_set_constraint(0, &possible_values));
        
        // Test constant check
        let constant_set = BasicSet::new(vec![1, 1, 1]).unwrap();
        assert!(constant_set.is_constant());
        assert!(!set.is_constant());
        
        // Test idempotent check
        let idempotent_set = BasicSet::new(vec![0, 1, 2]).unwrap();
        assert!(idempotent_set.is_idempotent());
        assert!(!set.is_idempotent());
    }

    fn sorted(mut vec: Vec<i32>) -> Vec<i32> {
        vec.sort();
        vec
    }
}
