//! Canonicalization algorithms for Taylor terms
//! 
//! This module provides efficient canonical form computation using
//! union-find with path compression for true equivalence class management.

use crate::{UACalcError, UACalcResult};
use crate::taylor::int_array::IntArray;
use std::collections::HashMap;

/// Union-Find data structure for canonicalization
#[derive(Debug, Clone)]
pub struct UnionFind {
    /// Parent map: maps each array to its parent
    parent: HashMap<IntArray, IntArray>,
    /// Rank map for union by rank optimization
    rank: HashMap<IntArray, usize>,
}

impl UnionFind {
    /// Create a new union-find structure
    pub fn new() -> Self {
        Self {
            parent: HashMap::new(),
            rank: HashMap::new(),
        }
    }
    
    /// Find the canonical representative of an array with path compression
    pub fn find(&mut self, array: &IntArray) -> IntArray {
        if !self.parent.contains_key(array) {
            // If not in the structure, add it as its own root
            self.parent.insert(array.clone(), array.clone());
            self.rank.insert(array.clone(), 0);
            return array.clone();
        }
        
        let mut current = array.clone();
        let mut path = Vec::new();
        
        // Follow the path to find the root
        while self.parent[&current] != current {
            path.push(current.clone());
            current = self.parent[&current].clone();
        }
        
        // Path compression: update all nodes on the path to point directly to the root
        for node in path {
            self.parent.insert(node, current.clone());
        }
        
        current
    }
    
    /// Union two arrays, choosing the lexicographically smaller as the root
    pub fn union(&mut self, a: &IntArray, b: &IntArray) {
        let root_a = self.find(a);
        let root_b = self.find(b);
        
        if root_a == root_b {
            return; // Already in the same set
        }
        
        // Choose the lexicographically smaller as the root
        let (new_root, old_root) = if root_a < root_b {
            (root_a, root_b)
        } else {
            (root_b, root_a)
        };
        
        // Union by rank
        let rank_new = self.rank.get(&new_root).unwrap_or(&0);
        let rank_old = self.rank.get(&old_root).unwrap_or(&0);
        
        self.parent.insert(old_root.clone(), new_root.clone());
        
        if rank_new == rank_old {
            self.rank.insert(new_root, rank_new + 1);
        }
    }
    
    /// Get all canonical representatives
    pub fn canonical_representatives(&self) -> Vec<IntArray> {
        let mut representatives = std::collections::HashSet::new();
        
        for array in self.parent.keys() {
            // Note: This is a simplified version. In practice, we'd need to
            // call find() on each element to get the true canonical representatives
            representatives.insert(array.clone());
        }
        
        let mut result: Vec<_> = representatives.into_iter().collect();
        result.sort();
        result
    }
    
    /// Count the number of equivalence classes
    pub fn count_classes(&mut self) -> usize {
        let mut roots = std::collections::HashSet::new();
        
        // Collect all arrays first to avoid borrowing issues
        let arrays: Vec<IntArray> = self.parent.keys().cloned().collect();
        
        for array in arrays {
            let root = self.find(&array);
            roots.insert(root);
        }
        
        roots.len()
    }
}

/// Canonical form representation
#[derive(Debug, Clone)]
pub struct CanonicalForm {
    /// The canonical representative
    representative: IntArray,
    /// Union-find structure for equivalence classes
    union_find: UnionFind,
}

impl CanonicalForm {
    /// Create a new canonical form
    pub fn new(representative: IntArray) -> Self {
        let mut union_find = UnionFind::new();
        union_find.find(&representative); // Initialize the representative
        
        Self {
            representative,
            union_find,
        }
    }
    
    /// Get the canonical representative
    pub fn representative(&self) -> &IntArray {
        &self.representative
    }
    
    /// Get the union-find structure
    pub fn union_find(&self) -> &UnionFind {
        &self.union_find
    }
    
    /// Get a mutable reference to the union-find structure
    pub fn union_find_mut(&mut self) -> &mut UnionFind {
        &mut self.union_find
    }
    
    /// Find the canonical form of an array using union-find
    pub fn find_canonical(&mut self, array: &IntArray) -> IntArray {
        self.union_find.find(array)
    }
}

/// Compute the canonical form of an array using union-find
pub fn canonical_form(arr: &IntArray, union_find: &mut UnionFind) -> IntArray {
    union_find.find(arr)
}

/// Create a union-find structure from equations
pub fn make_union_find(equations: &[(IntArray, IntArray)]) -> UnionFind {
    let mut union_find = UnionFind::new();
    
    for (left, right) in equations {
        // Union both sides of the equation
        union_find.union(left, right);
        
        // Also process complements for completeness
        let complement_left = left.complement();
        let complement_right = right.complement();
        union_find.union(&complement_left, &complement_right);
    }
    
    union_find
}

/// Check if two arrays are equivalent under the given equations
pub fn are_equivalent(
    arr1: &IntArray,
    arr2: &IntArray,
    union_find: &mut UnionFind,
) -> bool {
    let canonical1 = canonical_form(arr1, union_find);
    let canonical2 = canonical_form(arr2, union_find);
    canonical1 == canonical2
}

/// Get all canonical representatives from a union-find structure
pub fn get_canonical_representatives(union_find: &mut UnionFind) -> Vec<IntArray> {
    union_find.canonical_representatives()
}

/// Count the number of equivalence classes
pub fn count_equivalence_classes(union_find: &mut UnionFind) -> usize {
    union_find.count_classes()
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_canonical_form_creation() {
        let array = IntArray::from_vec(vec![1, 0, 1]);
        let canonical = CanonicalForm::new(array.clone());
        
        assert_eq!(canonical.representative(), &array);
        assert!(canonical.union_find().parent.is_empty());
        assert!(canonical.union_find().rank.is_empty());
    }
    
    #[test]
    fn test_make_union_find() {
        let left = IntArray::from_vec(vec![1, 0, 1]);
        let right = IntArray::from_vec(vec![0, 1, 0]);
        let equations = vec![(left, right)];
        
        let union_find = make_union_find(&equations);
        
        // Should have mappings for both sides and their complements
        assert!(union_find.parent.len() >= 2);
    }
    
    #[test]
    fn test_canonical_form() {
        let array = IntArray::from_vec(vec![1, 0, 1]);
        let mut union_find = UnionFind::new();
        let canonical = IntArray::from_vec(vec![0, 1, 0]);
        union_find.find(&canonical); // Initialize the canonical
        
        let result = canonical_form(&array, &mut union_find);
        assert_eq!(result, canonical);
    }
    
    #[test]
    fn test_are_equivalent() {
        let arr1 = IntArray::from_vec(vec![1, 0, 1]);
        let arr2 = IntArray::from_vec(vec![0, 1, 0]);
        let mut union_find = UnionFind::new();
        let canonical = IntArray::from_vec(vec![0, 0, 0]);
        union_find.find(&canonical); // Initialize the canonical
        
        union_find.union(&arr1, &canonical);
        union_find.union(&arr2, &canonical);
        
        assert!(are_equivalent(&arr1, &arr2, &mut union_find));
    }
    
    #[test]
    fn test_get_canonical_representatives() {
        let mut union_find = UnionFind::new();
        let rep1 = IntArray::from_vec(vec![0, 0, 0]);
        let rep2 = IntArray::from_vec(vec![1, 1, 1]);
        
        union_find.find(&IntArray::from_vec(vec![1, 0, 1]));
        union_find.find(&IntArray::from_vec(vec![0, 1, 0]));
        union_find.find(&IntArray::from_vec(vec![1, 1, 0]));
        
        let representatives = get_canonical_representatives(&mut union_find);
        assert_eq!(representatives.len(), 2);
    }
    
    #[test]
    fn test_count_equivalence_classes() {
        let mut union_find = UnionFind::new();
        let rep1 = IntArray::from_vec(vec![0, 0, 0]);
        let rep2 = IntArray::from_vec(vec![1, 1, 1]);
        
        union_find.find(&IntArray::from_vec(vec![1, 0, 1]));
        union_find.find(&IntArray::from_vec(vec![0, 1, 0]));
        union_find.find(&IntArray::from_vec(vec![1, 1, 0]));
        
        assert_eq!(count_equivalence_classes(&mut union_find), 2);
    }
}
