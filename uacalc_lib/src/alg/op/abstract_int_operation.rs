use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::op::{Operation, AbstractIntOperation};

/// Python wrapper for AbstractIntOperation
#[pyclass]
pub struct PyAbstractIntOperation {
    inner: AbstractIntOperation,
}

#[pymethods]
impl PyAbstractIntOperation {
    /// Create a new AbstractIntOperation with name, arity, and algebra size.
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///     arity (int): The arity (number of arguments) of the operation
    ///     alg_size (int): The size of the algebra set
    ///
    /// Raises:
    ///     ValueError: If parameters are invalid
    #[new]
    fn new(name: &str, arity: i32, alg_size: i32) -> PyResult<Self> {
        match AbstractIntOperation::new_safe(name, arity, alg_size) {
            Ok(inner) => Ok(PyAbstractIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new AbstractIntOperation with an existing OperationSymbol.
    ///
    /// Args:
    ///     symbol (OperationSymbol): The operation symbol
    ///     alg_size (int): The size of the algebra set
    ///
    /// Raises:
    ///     ValueError: If alg_size is invalid
    #[staticmethod]
    fn with_symbol(symbol: &super::operation_symbol::PyOperationSymbol, alg_size: i32) -> PyResult<Self> {
        match AbstractIntOperation::new_with_symbol_safe(symbol.get_inner().clone(), alg_size) {
            Ok(inner) => Ok(PyAbstractIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the arity of this operation.
    fn arity(&self) -> i32 {
        self.inner.arity()
    }

    /// Get the size of the set upon which the operation is defined.
    fn get_set_size(&self) -> i32 {
        self.inner.get_set_size()
    }

    /// Get the operation symbol for this operation.
    fn symbol(&self) -> super::operation_symbol::PyOperationSymbol { super::operation_symbol::PyOperationSymbol::from_inner(self.inner.symbol().clone()) }

    /// Attempt to evaluate the operation (will fail with UnsupportedOperationException).
    ///
    /// Args:
    ///     args (List[int]): Arguments for the operation
    ///
    /// Raises:
    ///     ValueError: Always raises since this method is not implemented
    fn value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Attempt integer operation evaluation (will fail with UnsupportedOperationException).
    ///
    /// Args:
    ///     args (List[int]): Integer arguments
    ///
    /// Raises:
    ///     ValueError: Always raises since this method is not implemented
    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.int_value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Check if this operation is total.
    fn is_total(&self) -> PyResult<bool> {
        match self.inner.is_total() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("AbstractIntOperation({})", self.inner.to_string())
    }

    /// Python equality comparison.
    fn __eq__(&self, other: &PyAbstractIntOperation) -> bool {
        self.inner == other.inner
    }

    /// Python hash function.
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
}