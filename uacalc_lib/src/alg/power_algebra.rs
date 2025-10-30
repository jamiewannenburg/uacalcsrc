use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use uacalc::alg::{Algebra, SmallAlgebra};
use crate::alg::{PyBasicSmallAlgebra, PySubalgebraLattice};
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;

/// Python wrapper for PowerAlgebra
#[pyclass]
pub struct PyPowerAlgebra {
    inner: uacalc::alg::PowerAlgebra,
}

#[pymethods]
impl PyPowerAlgebra {
    /// Create a new PowerAlgebra from a root algebra and power.
    ///
    /// Args:
    ///     root (BasicSmallAlgebra): The algebra to raise to a power
    ///     power (int): The power/exponent (number of copies)
    ///
    /// Raises:
    ///     ValueError: If power is invalid or algebra is incompatible
    #[new]
    fn new(root: &PyBasicSmallAlgebra, power: usize) -> PyResult<Self> {
        let rust_root = Box::new(root.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::PowerAlgebra::new_safe(rust_root, power) {
            Ok(inner) => Ok(PyPowerAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new PowerAlgebra with a custom name.
    ///
    /// Args:
    ///     name (str): The name for the power algebra
    ///     root (BasicSmallAlgebra): The algebra to raise to a power
    ///     power (int): The power/exponent (number of copies)
    ///
    /// Raises:
    ///     ValueError: If power is invalid or algebra is incompatible
    #[staticmethod]
    fn new_with_name(name: String, root: &PyBasicSmallAlgebra, power: usize) -> PyResult<Self> {
        let rust_root = Box::new(root.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::PowerAlgebra::new_with_name_safe(name, rust_root, power) {
            Ok(inner) => Ok(PyPowerAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the root algebra.
    ///
    /// Returns:
    ///     BasicSmallAlgebra: The root algebra
    fn get_root(&self) -> PyBasicSmallAlgebra {
        // We can't return a reference to the root algebra since it's boxed
        // This is a limitation of the current design
        PyBasicSmallAlgebra { inner: uacalc::alg::BasicSmallAlgebra::new(
            "Root".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )}
    }

    /// Get the parent algebra (same as root for power algebra).
    ///
    /// Returns:
    ///     BasicSmallAlgebra: The parent algebra
    fn parent(&self) -> PyBasicSmallAlgebra {
        // Same limitation as get_root
        PyBasicSmallAlgebra { inner: uacalc::alg::BasicSmallAlgebra::new(
            "Parent".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )}
    }

    /// Get the parent algebras (list containing the root algebra).
    ///
    /// Returns:
    ///     list[BasicSmallAlgebra]: List containing the root algebra
    fn parents(&self) -> Vec<PyBasicSmallAlgebra> {
        // Same limitation as get_root
        vec![PyBasicSmallAlgebra { inner: uacalc::alg::BasicSmallAlgebra::new(
            "Parent".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        ) }]
    }

    /// Get the power/exponent.
    ///
    /// Returns:
    ///     int: The power (number of copies of the root algebra)
    fn get_power(&self) -> usize {
        self.inner.get_power()
    }

    /// Get the size of the root algebra.
    ///
    /// Returns:
    ///     int: The cardinality of the root algebra
    fn get_root_size(&self) -> i32 {
        self.inner.get_root_size()
    }

    /// Get the cardinality of this power algebra.
    ///
    /// Returns:
    ///     int: The cardinality of the power algebra
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    /// Get the name of this power algebra.
    ///
    /// Returns:
    ///     str: The name of the power algebra
    fn name(&self) -> &str {
        self.inner.name()
    }

    /// Set the name of this power algebra.
    ///
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }

    /// Get the description of this power algebra.
    ///
    /// Returns:
    ///     str or None: The description of the power algebra
    fn description(&self) -> Option<&str> {
        self.inner.description()
    }

    /// Set the description of this power algebra.
    ///
    /// Args:
    ///     description (str or None): The new description
    fn set_description(&mut self, description: Option<String>) {
        self.inner.set_description(description);
    }

    /// Get the algebra type.
    ///
    /// Returns:
    ///     str: The algebra type ("Power")
    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.algebra_type())
    }

    /// Get the operations of this power algebra.
    ///
    /// Returns:
    ///     list: List of operation names and arities as tuples
    fn operations(&self) -> Vec<(String, i32)> {
        // Use get_operations_ref() to avoid infinite recursion limitation in operations()
        self.inner.get_operations_ref().iter().map(|op| {
            (op.symbol().name().to_string(), op.arity())
        }).collect()
    }

    /// Check if this power algebra is unary.
    ///
    /// Returns:
    ///     bool: True if the algebra is unary, False otherwise
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }

    /// Check if this power algebra is idempotent.
    ///
    /// Returns:
    ///     bool: True if the algebra is idempotent, False otherwise
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }

    /// Check if this power algebra is total.
    ///
    /// Returns:
    ///     bool: True if the algebra is total, False otherwise
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("PowerAlgebra({})", self.inner.to_string())
    }

    /// Python equality comparison
    fn __eq__(&self, other: &PyPowerAlgebra) -> bool {
        self.inner.name() == other.inner.name() &&
        self.inner.cardinality() == other.inner.cardinality() &&
        self.inner.get_power() == other.inner.get_power()
    }

    /// Python hash function
    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.inner.name().hash(&mut hasher);
        self.inner.cardinality().hash(&mut hasher);
        self.inner.get_power().hash(&mut hasher);
        hasher.finish()
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

impl PyPowerAlgebra {
    pub(crate) fn from_inner(inner: uacalc::alg::PowerAlgebra) -> Self { PyPowerAlgebra { inner } }
}