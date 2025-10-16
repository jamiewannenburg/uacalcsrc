/*! Python bindings for sublat module.

This module provides Python bindings for subalgebra lattice operations.
*/

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::sublat::BasicSet;

/// Python wrapper for BasicSet
#[pyclass]
pub struct PyBasicSet {
    inner: BasicSet,
}

#[pymethods]
impl PyBasicSet {
    /// Create a new BasicSet from a list of elements.
    /// 
    /// The elements will be automatically sorted.
    /// 
    /// # Arguments
    /// * `elements` - List of integers to include in the set
    /// 
    /// # Returns
    /// * `PyBasicSet` - A new set with sorted elements
    #[new]
    fn new(elements: Vec<i32>) -> Self {
        PyBasicSet {
            inner: BasicSet::new(elements),
        }
    }
    
    /// Create an empty set.
    /// 
    /// # Returns
    /// * `PyBasicSet` - An empty set
    #[staticmethod]
    fn empty() -> Self {
        PyBasicSet {
            inner: BasicSet::empty(),
        }
    }
    
    /// Normalize the set by sorting elements in ascending order.
    fn normalize(&mut self) {
        self.inner.normalize();
    }
    
    /// Get the size of the set (number of elements).
    /// 
    /// # Returns
    /// * `usize` - The number of elements in the set
    fn universe_size(&self) -> usize {
        self.inner.universe_size()
    }
    
    /// Get an element at the specified index.
    /// 
    /// # Arguments
    /// * `index` - The index to access
    /// 
    /// # Returns
    /// * `i32` - The element at the index
    /// 
    /// # Raises
    /// * `IndexError` - If the index is out of bounds
    fn get(&self, index: usize) -> PyResult<i32> {
        if index >= self.inner.universe_size() {
            return Err(PyValueError::new_err(format!(
                "Index {} out of bounds for set of size {}",
                index,
                self.inner.universe_size()
            )));
        }
        Ok(self.inner.get(index))
    }
    
    /// Get the underlying array as a list.
    /// 
    /// # Returns
    /// * `Vec<i32>` - List of elements in the set
    fn to_array(&self) -> Vec<i32> {
        self.inner.to_array().to_vec()
    }
    
    /// Check if this set is a subset of another set.
    /// 
    /// # Arguments
    /// * `set2` - The set to check against
    /// 
    /// # Returns
    /// * `bool` - true if this is a subset of set2
    fn leq(&self, set2: &PyBasicSet) -> bool {
        self.inner.leq(&set2.inner)
    }
    
    /// Static method to check if array u is a subset of array v.
    /// 
    /// # Arguments
    /// * `u` - First sorted array
    /// * `v` - Second sorted array
    /// 
    /// # Returns
    /// * `bool` - true if u is a subset of v
    #[staticmethod]
    fn leq_arrays(u: Vec<i32>, v: Vec<i32>) -> bool {
        BasicSet::leq_arrays(&u, &v)
    }
    
    /// Check if the set contains a specific element.
    /// 
    /// # Arguments
    /// * `i` - The element to search for
    /// 
    /// # Returns
    /// * `bool` - true if the element is in the set
    fn contains(&self, i: i32) -> bool {
        self.inner.contains(i)
    }
    
    /// Compute the set difference (this - set2).
    /// 
    /// # Arguments
    /// * `set2` - The set to subtract
    /// 
    /// # Returns
    /// * `PyBasicSet` - A new set with the difference
    fn set_difference(&self, set2: &PyBasicSet) -> PyBasicSet {
        PyBasicSet {
            inner: self.inner.set_difference(&set2.inner),
        }
    }
    
    /// Compute the intersection of this set with another.
    /// 
    /// # Arguments
    /// * `set2` - The set to intersect with
    /// 
    /// # Returns
    /// * `PyBasicSet` - A new set with the intersection
    fn intersection(&self, set2: &PyBasicSet) -> PyBasicSet {
        PyBasicSet {
            inner: self.inner.intersection(&set2.inner),
        }
    }
    
    /// Static method to compute the intersection of two sets.
    /// 
    /// # Arguments
    /// * `set1` - First set
    /// * `set2` - Second set
    /// 
    /// # Returns
    /// * `PyBasicSet` - A new set with the intersection
    #[staticmethod]
    fn intersection_static(set1: &PyBasicSet, set2: &PyBasicSet) -> PyBasicSet {
        PyBasicSet {
            inner: BasicSet::intersection_static(&set1.inner, &set2.inner),
        }
    }
    
    /// Compute the union of this set with another.
    /// 
    /// # Arguments
    /// * `set2` - The set to union with
    /// 
    /// # Returns
    /// * `PyBasicSet` - A new set with the union
    fn union(&self, set2: &PyBasicSet) -> PyBasicSet {
        PyBasicSet {
            inner: self.inner.union(&set2.inner),
        }
    }
    
    /// Static method to compute the union of two sets.
    /// 
    /// # Arguments
    /// * `set1` - First set
    /// * `set2` - Second set
    /// 
    /// # Returns
    /// * `PyBasicSet` - A new set with the union
    #[staticmethod]
    fn union_static(set1: &PyBasicSet, set2: &PyBasicSet) -> PyBasicSet {
        PyBasicSet {
            inner: BasicSet::union_static(&set1.inner, &set2.inner),
        }
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("BasicSet({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyBasicSet) -> bool {
        self.inner == other.inner
    }
    
    /// Python less than comparison
    fn __lt__(&self, other: &PyBasicSet) -> bool {
        self.inner < other.inner
    }
    
    /// Python less than or equal comparison
    fn __le__(&self, other: &PyBasicSet) -> bool {
        self.inner <= other.inner
    }
    
    /// Python greater than comparison
    fn __gt__(&self, other: &PyBasicSet) -> bool {
        self.inner > other.inner
    }
    
    /// Python greater than or equal comparison
    fn __ge__(&self, other: &PyBasicSet) -> bool {
        self.inner >= other.inner
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
}

pub fn register_sublat_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyBasicSet>()?;
    
    // Export only clean names (without Py prefix)
    m.add("BasicSet", m.getattr("PyBasicSet")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyBasicSet")?;
    
    Ok(())
}
