use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::*;
use uacalc::alg::conlat::BasicBinaryRelation;
use uacalc::alg::sublat::BasicSet;
use uacalc::lat::{Lattice, Order};
use crate::alg::PyBasicSmallAlgebra;
use crate::alg::PyPartition;
use crate::alg::PySubalgebraLattice;
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;

/// Python wrapper for Subalgebra
#[pyclass]
pub struct PySubalgebra {
    inner: uacalc::alg::Subalgebra<i32>,
}

#[pymethods]
impl PySubalgebra {
    /// Create a new Subalgebra with the given super algebra and subuniverse.
    ///
    /// Args:
    ///     name (str): Name of the subalgebra
    ///     super_algebra (BasicSmallAlgebra): The super algebra
    ///     univ (list[int]): Array of indices in the super algebra forming the subuniverse
    ///
    /// Raises:
    ///     ValueError: If the subuniverse is empty or contains invalid indices
    #[new]
    fn new(name: String, super_algebra: &PyBasicSmallAlgebra, univ: Vec<i32>) -> PyResult<Self> {
        let super_box = Box::new(super_algebra.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        match uacalc::alg::Subalgebra::new_safe(name, super_box, univ) {
            Ok(inner) => Ok(PySubalgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find the index in this subalgebra of the element with index k in the super algebra.
    ///
    /// Uses binary search since the universe array is sorted.
    ///
    /// Args:
    ///     k (int): Index in the super algebra
    ///
    /// Returns:
    ///     int: Index in the subalgebra, or -1 if not found
    fn index(&self, k: i32) -> i32 {
        match self.inner.index(k) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }

    /// Restrict a partition (or congruence) on the parent algebra to this subalgebra.
    ///
    /// Args:
    ///     par (Partition): Partition on the super algebra
    ///
    /// Returns:
    ///     Partition: Restricted partition on this subalgebra
    ///
    /// Raises:
    ///     ValueError: If restriction fails
    fn restrict_partition(&self, par: &PyPartition) -> PyResult<PyPartition> {
        match self.inner.restrict_partition(par.get_inner()) {
            Ok(restricted) => Ok(PyPartition::from_inner(restricted)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the super algebra name.
    ///
    /// Returns:
    ///     str: Name of the super algebra
    fn super_algebra_name(&self) -> String {
        self.inner.super_algebra().name().to_string()
    }

    /// Get the subuniverse array.
    ///
    /// Returns:
    ///     list[int]: Array of indices forming the subuniverse
    fn get_subuniverse_array(&self) -> Vec<i32> {
        self.inner.get_subuniverse_array().to_vec()
    }

    /// Get the cardinality of this subalgebra.
    ///
    /// Returns:
    ///     int: The cardinality (size of the universe)
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    /// Get the element at the given index.
    ///
    /// Args:
    ///     k (int): Index of the element
    ///
    /// Returns:
    ///     int: The element at index k, or -1 if out of bounds
    fn get_element(&self, k: usize) -> i32 {
        self.inner.get_element(k).unwrap_or(-1)
    }

    /// Get the index of an element in the universe.
    ///
    /// Args:
    ///     elem (int): The element to find
    ///
    /// Returns:
    ///     int: The index of the element, or -1 if not found
    fn element_index(&self, elem: i32) -> i32 {
        match self.inner.element_index(&elem) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }

    /// Get the algebra type.
    ///
    /// Returns:
    ///     str: The algebra type ("Subalgebra")
    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.algebra_type())
    }

    /// Get the name of this algebra.
    ///
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> &str {
        self.inner.name()
    }

    /// Set the name of this algebra.
    ///
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("Subalgebra({})", self.inner.to_string())
    }

    /// Get the congruence lattice (lazy initialization).
    ///
    /// Returns:
    ///     CongruenceLattice: The congruence lattice
    fn con(&mut self) -> PyCongruenceLattice {
        let con_lat = self.inner.con();
        PyCongruenceLattice { inner: con_lat.clone() }
    }

    /// Get the subalgebra lattice (lazy initialization).
    ///
    /// Returns:
    ///     SubalgebraLattice: The subalgebra lattice
    fn sub(&mut self) -> PySubalgebraLattice {
        let sub_lat = self.inner.sub();
        PySubalgebraLattice::from_inner(sub_lat.clone())
    }
}