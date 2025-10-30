use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

/// Python wrapper for BasicSet
#[pyclass]
pub struct PyBasicSet {
    inner: uacalc::alg::sublat::BasicSet,
}

#[pymethods]
impl PyBasicSet {
    /// Create a new BasicSet from a list of elements.
    ///
    /// Args:
    ///     elements (List[int]): List of integers to include in the set
    ///
    /// Returns:
    ///     BasicSet: A new BasicSet instance
    ///
    /// Raises:
    ///     ValueError: If elements contain invalid values
    #[new]
    fn new(elements: Vec<i32>) -> PyResult<Self> {
        match uacalc::alg::sublat::BasicSet::new_safe(elements) {
            Ok(inner) => Ok(PyBasicSet { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the elements of the set.
    ///
    /// Returns:
    ///     List[int]: The sorted elements of the set
    fn elements(&self) -> Vec<i32> {
        self.inner.elements().clone()
    }

    /// Get the size of the set (number of elements).
    ///
    /// Returns:
    ///     int: The number of elements in the set
    fn size(&self) -> usize {
        self.inner.size()
    }

    /// Get the universe size (same as size for BasicSet).
    ///
    /// Returns:
    ///     int: The number of elements in the set
    fn universe_size(&self) -> usize {
        self.inner.universe_size()
    }

    /// Normalize the set by sorting elements and removing duplicates.
    fn normalize(&mut self) {
        self.inner.normalize();
    }

    /// Check if this set is a subset of another set.
    ///
    /// Args:
    ///     other (BasicSet): The set to compare against
    ///
    /// Returns:
    ///     bool: True if this set is a subset of other
    fn leq(&self, other: &PyBasicSet) -> bool {
        self.inner.leq(&other.inner)
    }

    /// Static method to check if one array is a subset of another.
    ///
    /// Args:
    ///     u (List[int]): First array (sorted)
    ///     v (List[int]): Second array (sorted)
    ///
    /// Returns:
    ///     bool: True if u is a subset of v
    #[staticmethod]
    fn leq_static(u: Vec<i32>, v: Vec<i32>) -> bool {
        uacalc::alg::sublat::BasicSet::leq_static(&u, &v)
    }

    /// Check if the set contains a specific element.
    ///
    /// Args:
    ///     element (int): The element to search for
    ///
    /// Returns:
    ///     bool: True if the element is in the set
    fn contains(&self, element: i32) -> bool {
        self.inner.contains(element)
    }

    /// Compute the set difference (this - other).
    ///
    /// Args:
    ///     other (BasicSet): The set to subtract
    ///
    /// Returns:
    ///     BasicSet: A new BasicSet containing elements in this set but not in other
    fn set_difference(&self, other: &PyBasicSet) -> PyBasicSet {
        PyBasicSet { inner: self.inner.set_difference(&other.inner) }
    }

    /// Compute the intersection of this set with another.
    ///
    /// Args:
    ///     other (BasicSet): The set to intersect with
    ///
    /// Returns:
    ///     BasicSet: A new BasicSet containing elements in both sets
    fn intersection(&self, other: &PyBasicSet) -> PyBasicSet {
        PyBasicSet { inner: self.inner.intersection(&other.inner) }
    }

    /// Static method to compute the intersection of two sets.
    ///
    /// Args:
    ///     set1 (BasicSet): First set
    ///     set2 (BasicSet): Second set
    ///
    /// Returns:
    ///     BasicSet: A new BasicSet containing elements in both sets
    #[staticmethod]
    fn intersection_static(set1: &PyBasicSet, set2: &PyBasicSet) -> PyBasicSet {
        PyBasicSet { inner: uacalc::alg::sublat::BasicSet::intersection_static(&set1.inner, &set2.inner) }
    }

    /// Compute the union of this set with another.
    ///
    /// Args:
    ///     other (BasicSet): The set to union with
    ///
    /// Returns:
    ///     BasicSet: A new BasicSet containing elements from both sets
    fn union(&self, other: &PyBasicSet) -> PyBasicSet {
        PyBasicSet { inner: self.inner.union(&other.inner) }
    }

    /// Static method to compute the union of two sets.
    ///
    /// Args:
    ///     set1 (BasicSet): First set
    ///     set2 (BasicSet): Second set
    ///
    /// Returns:
    ///     BasicSet: A new BasicSet containing elements from both sets
    #[staticmethod]
    fn union_static(set1: &PyBasicSet, set2: &PyBasicSet) -> PyBasicSet {
        PyBasicSet { inner: uacalc::alg::sublat::BasicSet::union_static(&set1.inner, &set2.inner) }
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

    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
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
}

impl PyBasicSet {
    pub(crate) fn get_inner(&self) -> &uacalc::alg::sublat::BasicSet { &self.inner }
    pub(crate) fn from_inner(inner: uacalc::alg::sublat::BasicSet) -> Self { PyBasicSet { inner } }
}