use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::op::{Operation, BasicOperation};
use crate::alg::op::operation_symbol::PyOperationSymbol;
use crate::alg::op::operation_symbol as op_mod_symbol;
use pyo3::types::PyAny;

/// Python wrapper for BasicOperation
#[pyclass]
pub struct PyBasicOperation {
    inner: BasicOperation,
}

#[pymethods]
impl PyBasicOperation {
    /// Create a new BasicOperation with the given symbol and set size.
    /// 
    /// Args:
    ///     symbol (OperationSymbol): The operation symbol
    ///     set_size (int): The size of the set on which the operation is defined
    /// 
    /// Raises:
    ///     ValueError: If set_size is invalid
    #[new]
    #[pyo3(signature = (symbol, set_size, table=None))]
    fn new(symbol: &PyAny, set_size: i32, table: Option<Vec<i32>>) -> PyResult<Self> {
        // Accept either root-level or op module OperationSymbol
        let inner_sym = if let Ok(sym) = symbol.extract::<PyRef<PyOperationSymbol>>() {
            sym.get_inner()
        } else if let Ok(sym2) = symbol.extract::<PyRef<op_mod_symbol::PyOperationSymbol>>() {
            sym2.get_inner()
        } else {
            return Err(PyValueError::new_err("Expected OperationSymbol"));
        };

        if let Some(table_vec) = table {
            match BasicOperation::new_with_table(inner_sym, set_size, table_vec) {
                Ok(inner) => Ok(PyBasicOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else {
            match BasicOperation::new_safe(inner_sym, set_size) {
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
    ///     BasicOperation: A new BasicOperation instance
    #[staticmethod]
    fn simple_binary_op(name: &str, set_size: i32) -> PyResult<Self> {
        match BasicOperation::simple_binary_op(name, set_size) {
            Ok(inner) => Ok(PyBasicOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the operation symbol.
    /// 
    /// Returns:
    ///     OperationSymbol: The operation symbol
    fn symbol(&self) -> PyOperationSymbol { PyOperationSymbol::from_inner(self.inner.symbol().clone()) }
    
    /// Get the arity of the operation.
    /// 
    /// Returns:
    ///     int: The arity
    fn arity(&self) -> i32 { self.inner.arity() }
    
    /// Get the set size.
    /// 
    /// Returns:
    ///     int: The set size
    fn set_size(&self) -> i32 { self.inner.get_set_size() }
    
    /// Apply the operation to the given arguments.
    /// 
    /// Args:
    ///     args (List[int]): The arguments
    /// 
    /// Returns:
    ///     int: The result of the operation
    /// 
    /// Raises:
    ///     ValueError: If the arguments are invalid
    fn apply(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the operation table.
    /// 
    /// Returns:
    ///     List[int]: The operation table
    fn table(&self) -> Vec<i32> { self.inner.get_table().map(|s| s.to_vec()).unwrap_or_default() }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("BasicOperation(symbol={}, arity={}, set_size={})",
                self.inner.symbol().name(),
                self.inner.arity(),
                self.inner.get_set_size())
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
}

impl PyBasicOperation {
    /// Get the inner BasicOperation (for internal use)
    pub(crate) fn get_inner(&self) -> &BasicOperation {
        &self.inner
    }
}
