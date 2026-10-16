use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyAny;
use std::collections::HashMap;
use uacalc::alg::*;
use crate::alg::convert::{
    algebra_type_java_name, get_operation_by_symbol, operations_to_py, ops_to_basic_algebra,
};
use crate::alg::PyBasicAlgebra;
use crate::alg::power_algebra::PyPowerAlgebra;

/// Python wrapper for MatrixPowerAlgebra
#[pyclass]
pub struct PyMatrixPowerAlgebra {
    inner: uacalc::alg::MatrixPowerAlgebra,
    root: uacalc::alg::BasicAlgebra<i32>,
}

#[pymethods]
impl PyMatrixPowerAlgebra {
    /// Create a new MatrixPowerAlgebra from a root algebra and power.
    ///
    /// Args:
    ///     root (BasicAlgebra): The algebra to raise to a power
    ///     power (int): The power/exponent (number of copies)
    ///
    /// Raises:
    ///     ValueError: If power is invalid or algebra is incompatible
    #[new]
    fn new(root: &PyBasicAlgebra, power: usize) -> PyResult<Self> {
        let rust_root = Box::new(root.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::MatrixPowerAlgebra::new_safe(rust_root, power) {
            Ok(inner) => Ok(PyMatrixPowerAlgebra {
                inner,
                root: root.inner.clone(),
            }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new MatrixPowerAlgebra with a custom name.
    ///
    /// Args:
    ///     name (str): The name for the matrix power algebra
    ///     root (BasicAlgebra): The algebra to raise to a power
    ///     power (int): The power/exponent (number of copies)
    ///
    /// Raises:
    ///     ValueError: If power is invalid or algebra is incompatible
    #[staticmethod]
    fn new_with_name(name: String, root: &PyBasicAlgebra, power: usize) -> PyResult<Self> {
        let rust_root = Box::new(root.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::MatrixPowerAlgebra::new_with_name_safe(name, rust_root, power) {
            Ok(inner) => Ok(PyMatrixPowerAlgebra {
                inner,
                root: root.inner.clone(),
            }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the root algebra.
    ///
    /// Returns:
    ///     BasicAlgebra: The root algebra
    fn get_root(&self) -> PyBasicAlgebra {
        PyBasicAlgebra::from_inner(self.root.clone())
    }

    /// Get the parent algebra (same as root for matrix power algebra).
    ///
    /// Returns:
    ///     BasicAlgebra: The parent algebra
    fn parent(&self) -> PyBasicAlgebra {
        self.get_root()
    }

    /// Get the parent algebras (list containing the root algebra).
    ///
    /// Returns:
    ///     list[BasicAlgebra]: List containing the root algebra
    fn parents(&self) -> Vec<PyBasicAlgebra> {
        vec![self.get_root()]
    }

    /// Get the underlying power algebra.
    ///
    /// Returns:
    ///     PowerAlgebra: The underlying power algebra
    fn get_power_algebra(&self) -> PyResult<PyPowerAlgebra> {
        let rust_root = Box::new(self.root.clone())
            as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        match uacalc::alg::PowerAlgebra::new_safe(rust_root, self.inner.get_power()) {
            Ok(inner) => Ok(PyPowerAlgebra::from_inner(inner)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the power/exponent.
    ///
    /// Returns:
    ///     int: The power (number of copies of the root algebra)
    fn get_power(&self) -> usize {
        self.inner.get_power()
    }

    /// Get an element by its index using Horner encoding.
    ///
    /// Args:
    ///     index (int): The index of the element
    ///
    /// Returns:
    ///     list[int]: The element as a list of integers
    fn get_element(&self, index: usize) -> Vec<i32> {
        self.inner.get_element(index)
    }

    /// Get the index of an element using the power algebra.
    ///
    /// Args:
    ///     obj (list[int]): The element (as a list of integers)
    ///
    /// Returns:
    ///     int: The index of the element
    fn element_index(&self, obj: Vec<i32>) -> usize {
        self.inner.element_index(&obj)
    }

    /// Get the universe as a list of integer arrays.
    ///
    /// Returns:
    ///     list[list[int]]: A list of lists representing the universe elements
    fn get_universe_list(&self) -> Vec<Vec<i32>> {
        self.inner.get_universe_list()
    }

    /// Get the universe order (not implemented for matrix power algebras).
    ///
    /// Returns:
    ///     None: Matrix power algebras don't have a natural order
    fn get_universe_order(&self) -> Option<HashMap<Vec<i32>, usize>> {
        self.inner.get_universe_order()
    }

    /// Convert to default value operations (not supported for matrix power algebras).
    ///
    /// Raises:
    ///     RuntimeError: Always raises "Only for basic algebras"
    fn convert_to_default_value_ops(&mut self) -> PyResult<()> {
        Err(PyValueError::new_err("Only for basic algebras"))
    }

    /// Get the algebra type.
    ///
    /// Returns:
    ///     str: The algebra type ("MATRIX_POWER")
    fn algebra_type(&self) -> String {
        algebra_type_java_name(self.inner.algebra_type())
    }

    fn operations(&self, py: Python<'_>) -> PyResult<Vec<PyObject>> {
        operations_to_py(py, Algebra::operations(&self.inner))
    }

    fn get_operation(&self, py: Python<'_>, sym: &Bound<'_, PyAny>) -> PyResult<Option<PyObject>> {
        get_operation_by_symbol(py, Algebra::operations(&self.inner), sym)
    }

    fn to_basic_algebra(&self) -> PyResult<PyBasicAlgebra> {
        ops_to_basic_algebra(
            self.inner.name().to_string(),
            self.inner.cardinality(),
            Algebra::operations(&self.inner),
        )
    }

    /// Get the cardinality of this algebra.
    ///
    /// Returns:
    ///     int: The number of elements in the algebra
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
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

    /// Get the description of this algebra.
    ///
    /// Returns:
    ///     str or None: The description of the algebra
    fn description(&self) -> Option<&str> {
        self.inner.description()
    }

    /// Set the description of this algebra.
    ///
    /// Args:
    ///     desc (str or None): The new description
    fn set_description(&mut self, desc: Option<String>) {
        self.inner.set_description(desc);
    }

    /// Check if this algebra is unary (all operations have arity 1).
    ///
    /// Returns:
    ///     bool: True if all operations are unary
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

    /// Get the number of operations in this algebra.
    ///
    /// Returns:
    ///     int: The number of operations
    fn operations_count(&self) -> usize {
        self.inner.get_operations_ref().len()
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("MatrixPowerAlgebra({})", self.inner.to_string())
    }

    /// Python equality comparison
    fn __eq__(&self, other: &PyMatrixPowerAlgebra) -> bool {
        self.inner.name() == other.inner.name() &&
        self.inner.get_power() == other.inner.get_power() &&
        self.inner.cardinality() == other.inner.cardinality()
    }

    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.inner.name().hash(&mut hasher);
        self.inner.get_power().hash(&mut hasher);
        self.inner.cardinality().hash(&mut hasher);
        hasher.finish()
    }
}