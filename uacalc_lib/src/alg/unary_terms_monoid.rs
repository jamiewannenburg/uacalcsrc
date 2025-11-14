use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::*;
use crate::alg::PyBasicAlgebra;
use crate::util::PyIntArray;

/// Python wrapper for UnaryTermsMonoid
#[pyclass]
pub struct PyUnaryTermsMonoid {
    inner: uacalc::alg::UnaryTermsMonoid,
}

#[pymethods]
impl PyUnaryTermsMonoid {
    /// Create a new UnaryTermsMonoid from a generating algebra.
    ///
    /// Args:
    ///     algebra (BasicAlgebra): The generating algebra
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[new]
    fn new(algebra: &PyBasicAlgebra) -> PyResult<Self> {
        let rust_alg = Box::new(algebra.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::UnaryTermsMonoid::new_safe(rust_alg) {
            Ok(inner) => Ok(PyUnaryTermsMonoid { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new UnaryTermsMonoid with optional identity inclusion.
    ///
    /// Args:
    ///     algebra (BasicAlgebra): The generating algebra
    ///     include_id (bool): Whether to include the identity term
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[staticmethod]
    fn new_with_id(algebra: &PyBasicAlgebra, include_id: bool) -> PyResult<Self> {
        let rust_alg = Box::new(algebra.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::UnaryTermsMonoid::new_with_id_safe(rust_alg, include_id) {
            Ok(inner) => Ok(PyUnaryTermsMonoid { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the algebra type.
    ///
    /// Returns:
    ///     str: The algebra type
    fn algebra_type(&self) -> String {
        match self.inner.algebra_type() {
            uacalc::alg::AlgebraType::UnaryTermsMonoid => "UNARY_TERMS_MONOID".to_string(),
            _ => "UNKNOWN".to_string(),
        }
    }

    /// Get the cardinality of the algebra.
    ///
    /// Returns:
    ///     int: The cardinality
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    /// Get the name of the algebra.
    ///
    /// Returns:
    ///     str: The name
    fn name(&self) -> String {
        self.inner.name().to_string()
    }

    /// Set the name of the algebra.
    ///
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }

    /// Check if this algebra is unary.
    ///
    /// Returns:
    ///     bool: True if the algebra is unary
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }

    /// Check if this algebra is idempotent.
    ///
    /// Returns:
    ///     bool: True if the algebra is idempotent
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }

    /// Check if this algebra is total.
    ///
    /// Returns:
    ///     bool: True if the algebra is total
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }

    /// Get the number of operations.
    ///
    /// Returns:
    ///     int: The number of operations (1 for the product operation)
    fn operations_count(&self) -> usize {
        self.inner.get_operations_ref().len()
    }

    /// Get the universe as a list.
    ///
    /// Returns:
    ///     List[IntArray]: The universe elements
    fn get_universe_list(&self) -> Vec<PyIntArray> {
        self.inner.get_universe_list()
            .unwrap_or_default()
            .into_iter()
            .map(|item| PyIntArray { inner: item })
            .collect()
    }

    /// Get an element by its index.
    ///
    /// Args:
    ///     index (int): The index of the element
    ///
    /// Returns:
    ///     IntArray: The element at the given index (optional)
    fn get_element(&self, index: usize) -> Option<PyIntArray> {
        self.inner.get_element(index).map(|item| PyIntArray { inner: item })
    }

    /// Get the index of an element.
    ///
    /// Args:
    ///     element (IntArray): The element to find the index for
    ///
    /// Returns:
    ///     int: The index of the element (optional)
    fn element_index(&self, element: &PyIntArray) -> Option<usize> {
        self.inner.element_index(&element.inner)
    }

    /// String representation of the algebra.
    ///
    /// Returns:
    ///     str: String representation
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }

    /// String representation for debugging.
    ///
    /// Returns:
    ///     str: Debug string representation
    fn __repr__(&self) -> String {
        format!("UnaryTermsMonoid(name='{}', cardinality={})", self.name(), self.cardinality())
    }

    /// Length function for use with len().
    ///
    /// Returns:
    ///     int: Cardinality of the algebra
    fn __len__(&self) -> usize {
        self.inner.cardinality() as usize
    }
}