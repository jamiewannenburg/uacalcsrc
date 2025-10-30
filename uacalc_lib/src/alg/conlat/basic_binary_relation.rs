use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use uacalc::alg::conlat::{BasicBinaryRelation, BinaryRelation, MutableBinaryRelation};
use uacalc::util::IntArrayTrait;

/// Python wrapper for BasicBinaryRelation
#[pyclass]
pub struct PyBasicBinaryRelation {
    inner: BasicBinaryRelation,
}

#[pymethods]
impl PyBasicBinaryRelation {
    /// Create a new BasicBinaryRelation with the given universe size.
    ///
    /// Args:
    ///     universe_size (int): The size of the universe {0, 1, ..., n-1}
    ///
    /// Raises:
    ///     ValueError: If universe_size is zero or negative
    #[new]
    fn new(universe_size: usize) -> PyResult<Self> {
        match BasicBinaryRelation::new(universe_size) {
            Ok(inner) => Ok(PyBasicBinaryRelation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Add a pair (i, j) to the relation.
    ///
    /// Args:
    ///     i (int): The first element
    ///     j (int): The second element
    ///
    /// Raises:
    ///     ValueError: If indices are out of bounds
    fn add(&mut self, i: usize, j: usize) -> PyResult<()> {
        match self.inner.add(i, j) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Check if element i is related to element j.
    ///
    /// Args:
    ///     i (int): The first element
    ///     j (int): The second element
    ///
    /// Returns:
    ///     bool: True if i is related to j, False otherwise
    fn is_related(&self, i: usize, j: usize) -> bool {
        self.inner.is_related(i, j)
    }

    /// Get the size of the universe.
    ///
    /// Returns:
    ///     int: The size of the universe
    fn universe_size(&self) -> usize {
        self.inner.universe_size()
    }

    /// Get all pairs in the relation.
    ///
    /// Returns:
    ///     list: List of pairs as [i, j] lists
    fn get_pairs(&self) -> Vec<Vec<i32>> {
        let pairs = self.inner.get_pairs();
        pairs.into_iter()
            .map(|pair| vec![pair.get(0).unwrap(), pair.get(1).unwrap()])
            .collect()
    }

    /// Compose this relation with another relation.
    ///
    /// Args:
    ///     other (BasicBinaryRelation): The other relation to compose with
    ///
    /// Returns:
    ///     BasicBinaryRelation: The composition of the two relations
    ///
    /// Raises:
    ///     ValueError: If relations have incompatible universe sizes
    fn compose(&self, other: &PyBasicBinaryRelation) -> PyResult<PyBasicBinaryRelation> {
        match self.inner.compose(&other.inner) {
            Ok(result) => {
                // Extract the BasicBinaryRelation from the boxed trait object
                // This is a bit of a hack since we can't downcast trait objects easily
                // For now, we'll create a new relation with the same pairs
                let pairs = result.get_pairs();
                let mut new_relation = BasicBinaryRelation::new(result.universe_size())
                    .map_err(|e| PyValueError::new_err(e))?;
                for pair in pairs {
                    let i = pair.get(0).unwrap() as usize;
                    let j = pair.get(1).unwrap() as usize;
                    new_relation.add(i, j).map_err(|e| PyValueError::new_err(e))?;
                }
                Ok(PyBasicBinaryRelation { inner: new_relation })
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Check if the relation is reflexive.
    ///
    /// Returns:
    ///     bool: True if the relation is reflexive, False otherwise
    fn is_reflexive(&self) -> bool {
        self.inner.is_reflexive()
    }

    /// Check if the relation is symmetric.
    ///
    /// Returns:
    ///     bool: True if the relation is symmetric, False otherwise
    fn is_symmetric(&self) -> bool {
        self.inner.is_symmetric()
    }

    /// Check if the relation is transitive.
    ///
    /// Returns:
    ///     bool: True if the relation is transitive, False otherwise
    fn is_transitive(&self) -> bool {
        self.inner.is_transitive()
    }

    /// Check if the relation is an equivalence relation.
    ///
    /// Returns:
    ///     bool: True if the relation is an equivalence relation, False otherwise
    fn is_equivalence(&self) -> bool {
        self.inner.is_equivalence()
    }

    /// Get the number of pairs in the relation.
    ///
    /// Returns:
    ///     int: The number of pairs
    fn size(&self) -> usize {
        self.inner.size()
    }

    /// Check if the relation is empty.
    ///
    /// Returns:
    ///     bool: True if the relation is empty, False otherwise
    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    /// Clear all pairs from the relation.
    fn clear(&mut self) {
        self.inner.clear();
    }

    /// Remove a pair (i, j) from the relation.
    ///
    /// Args:
    ///     i (int): The first element
    ///     j (int): The second element
    ///
    /// Raises:
    ///     ValueError: If indices are out of bounds
    fn remove(&mut self, i: usize, j: usize) -> PyResult<()> {
        match self.inner.remove(i, j) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create the identity relation on a set of given size.
    ///
    /// Args:
    ///     size (int): The size of the universe
    ///
    /// Returns:
    ///     BasicBinaryRelation: The identity relation
    ///
    /// Raises:
    ///     ValueError: If size is zero or negative
    #[staticmethod]
    fn identity(size: usize) -> PyResult<Self> {
        match BasicBinaryRelation::identity(size) {
            Ok(inner) => Ok(PyBasicBinaryRelation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create the universal relation on a set of given size.
    ///
    /// Args:
    ///     size (int): The size of the universe
    ///
    /// Returns:
    ///     BasicBinaryRelation: The universal relation
    ///
    /// Raises:
    ///     ValueError: If size is zero or negative
    #[staticmethod]
    fn universal(size: usize) -> PyResult<Self> {
        match BasicBinaryRelation::universal(size) {
            Ok(inner) => Ok(PyBasicBinaryRelation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create the empty relation on a set of given size.
    ///
    /// Args:
    ///     size (int): The size of the universe
    ///
    /// Returns:
    ///     BasicBinaryRelation: The empty relation
    ///
    /// Raises:
    ///     ValueError: If size is zero or negative
    #[staticmethod]
    fn empty(size: usize) -> PyResult<Self> {
        match BasicBinaryRelation::empty(size) {
            Ok(inner) => Ok(PyBasicBinaryRelation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("BasicBinaryRelation({})", self.inner.to_string())
    }

    /// Python equality comparison
    fn __eq__(&self, other: &PyBasicBinaryRelation) -> bool {
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

    /// Python iterator support
    fn __iter__(&self) -> PyResult<PyObject> {
        let pairs = self.get_pairs();
        Python::with_gil(|py| {
            let list = pyo3::types::PyList::new_bound(py, pairs);
            Ok(list.into())
        })
    }
}

impl PyBasicBinaryRelation {
    /// Get the inner BasicBinaryRelation (for internal use)
    pub(crate) fn get_inner(&self) -> &BasicBinaryRelation {
        &self.inner
    }
    pub(crate) fn from_inner(inner: BasicBinaryRelation) -> Self { PyBasicBinaryRelation { inner } }
}