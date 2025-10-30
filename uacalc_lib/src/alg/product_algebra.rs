use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::*;
use crate::alg::{PyBasicSmallAlgebra, PySubalgebraLattice};
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;

/// Python wrapper for ProductAlgebra
#[pyclass]
pub struct PyProductAlgebra {
    inner: uacalc::alg::ProductAlgebra,
}

#[pymethods]
impl PyProductAlgebra {
    /// Create a new ProductAlgebra from a list of algebras.
    ///
    /// Args:
    ///     name (str): Name of the product algebra
    ///     algebras (list[BasicSmallAlgebra]): List of algebras to form the product
    ///
    /// Raises:
    ///     ValueError: If algebras are incompatible or empty
    #[new]
    fn new(name: String, algebras: Vec<PyRef<PyBasicSmallAlgebra>>) -> PyResult<Self> {
        if algebras.is_empty() {
            return Err(PyValueError::new_err("Cannot create product of empty algebra list"));
        }

        let rust_algebras: Vec<Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>> = algebras
            .iter()
            .map(|alg| Box::new(alg.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>)
            .collect();

        match uacalc::alg::ProductAlgebra::new_safe(name, rust_algebras) {
            Ok(inner) => Ok(PyProductAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Calculate the product cardinality.
    ///
    /// Args:
    ///     sizes (list[int]): The sizes of the algebras
    ///
    /// Returns:
    ///     int: The product cardinality, or -1 if too large, or 0 if any factor is empty
    ///
    /// Raises:
    ///     ValueError: If sizes array is empty
    #[staticmethod]
    fn calc_card(sizes: Vec<i32>) -> PyResult<i32> {
        match uacalc::alg::ProductAlgebra::calc_card_safe(&sizes) {
            Ok(card) => Ok(card),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the number of factor algebras.
    ///
    /// Returns:
    ///     int: The number of algebras in the product
    fn number_of_factors(&self) -> usize {
        self.inner.number_of_factors()
    }

    /// Get the sizes of each factor algebra.
    ///
    /// Returns:
    ///     list[int]: Sizes of the factor algebras
    fn get_sizes(&self) -> Vec<i32> {
        self.inner.get_sizes().to_vec()
    }

    /// Get the cardinality of this product algebra.
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
    ///     str: The algebra type ("Product")
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

    /// Make operation tables for all operations.
    fn make_operation_tables(&mut self) {
        self.inner.make_operation_tables();
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("ProductAlgebra({})", self.inner.to_string())
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