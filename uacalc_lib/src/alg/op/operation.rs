//! Python wrapper for BasicOperation

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::op::{Operation, BasicOperation};
use super::operation_symbol::PyOperationSymbol;

/// Python wrapper for BasicOperation
#[pyclass]
pub struct PyBasicOperation {
    inner: BasicOperation,
}

#[pymethods]
impl PyBasicOperation {
    /// Create a new AbstractOperation with the given symbol and set size.
    ///
    /// Args:
    ///     symbol (OperationSymbol): The operation symbol
    ///     set_size (int): The size of the set on which the operation is defined
    ///
    /// Raises:
    ///     ValueError: If set_size is invalid
    #[new]
    #[pyo3(signature = (symbol, set_size, table=None))]
    fn new(symbol: &PyOperationSymbol, set_size: i32, table: Option<Vec<i32>>) -> PyResult<Self> {
        if let Some(table_vec) = table {
            match BasicOperation::new_with_table(symbol.get_inner().clone(), set_size, table_vec) {
                Ok(inner) => Ok(PyBasicOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else {
            match BasicOperation::new_safe(symbol.get_inner().clone(), set_size) {
                Ok(inner) => Ok(PyBasicOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        }
    }

    /// Create a simple binary operation for testing.
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///     set_size (int): The size of the set
    ///
    /// Returns:
    ///     AbstractOperation: A new AbstractOperation instance
    #[staticmethod]
    fn simple_binary_op(name: &str, set_size: i32) -> PyResult<Self> {
        match BasicOperation::simple_binary_op(name, set_size) {
            Ok(inner) => Ok(PyBasicOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a simple unary operation for testing.
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///     set_size (int): The size of the set
    ///
    /// Returns:
    ///     AbstractOperation: A new AbstractOperation instance
    #[staticmethod]
    fn simple_unary_op(name: &str, set_size: i32) -> PyResult<Self> {
        match BasicOperation::simple_unary_op(name, set_size) {
            Ok(inner) => Ok(PyBasicOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a simple nullary operation for testing.
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///     set_size (int): The size of the set
    ///
    /// Returns:
    ///     AbstractOperation: A new AbstractOperation instance
    #[staticmethod]
    fn simple_nullary_op(name: &str, set_size: i32) -> PyResult<Self> {
        match BasicOperation::simple_nullary_op(name, set_size) {
            Ok(inner) => Ok(PyBasicOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the arity of this operation.
    ///
    /// Returns:
    ///     int: The number of arguments this operation takes
    fn arity(&self) -> i32 {
        self.inner.arity()
    }

    /// Get the size of the set upon which the operation is defined.
    ///
    /// Returns:
    ///     int: The size of the underlying set
    fn get_set_size(&self) -> i32 {
        self.inner.get_set_size()
    }

    /// Get the operation symbol for this operation.
    ///
    /// Returns:
    ///     OperationSymbol: The operation symbol
    fn symbol(&self) -> PyOperationSymbol { PyOperationSymbol::from_inner(self.inner.symbol().clone()) }

    /// Evaluate the operation at the given arguments.
    ///
    /// Args:
    ///     args (List[int]): Arguments for the operation
    ///
    /// Returns:
    ///     int: The result of the operation
    ///
    /// Raises:
    ///     ValueError: If arguments are invalid
    fn value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Evaluate the operation on arrays of arguments.
    ///
    /// Args:
    ///     args (List[List[int]]): Arrays of arguments
    ///
    /// Returns:
    ///     List[int]: Array of results
    ///
    /// Raises:
    ///     ValueError: If arguments are invalid
    fn value_at_arrays(&self, args: Vec<Vec<i32>>) -> PyResult<Vec<i32>> {
        let arg_refs: Vec<&[i32]> = args.iter().map(|v| v.as_slice()).collect();
        match self.inner.value_at_arrays(&arg_refs) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Integer version of the operation evaluation.
    ///
    /// Args:
    ///     args (List[int]): Integer arguments
    ///
    /// Returns:
    ///     int: The result of the operation
    ///
    /// Raises:
    ///     ValueError: If arguments are invalid
    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.int_value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Fast table access using Horner encoding.
    ///
    /// Args:
    ///     arg (int): The Horner encoding of the actual args
    ///
    /// Returns:
    ///     int: The result of the operation
    ///
    /// Raises:
    ///     ValueError: If argument is invalid or table doesn't exist
    fn int_value_at_horner(&self, arg: i32) -> PyResult<i32> {
        match self.inner.int_value_at_horner(arg) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a table for faster operation evaluation.
    ///
    /// Raises:
    ///     ValueError: If table creation fails
    fn make_table(&mut self) -> PyResult<()> {
        match self.inner.make_table() {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the table for this operation.
    ///
    /// Returns:
    ///     List[int] or None: The operation table or None if it doesn't exist
    fn get_table(&self) -> Option<Vec<i32>> {
        self.inner.get_table().map(|slice| slice.to_vec())
    }

    /// Get the table, creating it if necessary.
    ///
    /// Args:
    ///     make_table (bool): Whether to create the table if it doesn't exist
    ///
    /// Returns:
    ///     List[int]: The operation table
    ///
    /// Raises:
    ///     ValueError: If table creation fails
    fn get_table_force(&mut self, make_table: bool) -> PyResult<Vec<i32>> {
        match self.inner.get_table_force(make_table) {
            Ok(slice) => Ok(slice.to_vec()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Check if this operation is table-based.
    ///
    /// Returns:
    ///     bool: True if the operation uses a precomputed table
    fn is_table_based(&self) -> bool {
        self.inner.is_table_based()
    }

    /// Check if this operation is idempotent.
    ///
    /// Returns:
    ///     bool: True if f(x,x,...,x) = x for all x
    ///
    /// Raises:
    ///     ValueError: If the check fails
    fn is_idempotent(&self) -> PyResult<bool> {
        match self.inner.is_idempotent() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Check if this operation is binary and associative.
    ///
    /// Returns:
    ///     bool: True if the operation is binary and associative
    ///
    /// Raises:
    ///     ValueError: If the check fails
    fn is_associative(&self) -> PyResult<bool> {
        match self.inner.is_associative() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Check if this operation is binary and commutative.
    ///
    /// Returns:
    ///     bool: True if the operation is binary and commutative
    ///
    /// Raises:
    ///     ValueError: If the check fails
    fn is_commutative(&self) -> PyResult<bool> {
        match self.inner.is_commutative() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Check if this operation is totally symmetric.
    ///
    /// Returns:
    ///     bool: True if the operation is invariant under all variable permutations
    ///
    /// Raises:
    ///     ValueError: If the check fails
    fn is_totally_symmetric(&self) -> PyResult<bool> {
        match self.inner.is_totally_symmetric() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Check if this is a Maltsev operation.
    ///
    /// Returns:
    ///     bool: True if the operation is a Maltsev operation
    ///
    /// Raises:
    ///     ValueError: If the check fails
    fn is_maltsev(&self) -> PyResult<bool> {
        match self.inner.is_maltsev() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Check if this operation is total.
    ///
    /// Returns:
    ///     bool: True if the operation is total
    ///
    /// Raises:
    ///     ValueError: If the check fails
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
        format!("BasicOperation({})", self.inner.to_string())
    }

    /// Python equality comparison.
    fn __eq__(&self, other: &PyBasicOperation) -> bool {
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

    /// Python comparison (less than).
    fn __lt__(&self, other: &PyBasicOperation) -> bool {
        self.inner < other.inner
    }

    /// Python comparison (less than or equal).
    fn __le__(&self, other: &PyBasicOperation) -> bool {
        self.inner <= other.inner
    }

    /// Python comparison (greater than).
    fn __gt__(&self, other: &PyBasicOperation) -> bool {
        self.inner > other.inner
    }

    /// Python comparison (greater than or equal).
    fn __ge__(&self, other: &PyBasicOperation) -> bool {
        self.inner >= other.inner
    }
}