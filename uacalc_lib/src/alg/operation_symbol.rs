use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

/// Python wrapper for OperationSymbol
#[pyclass]
pub struct PyOperationSymbol {
    inner: uacalc::alg::op::OperationSymbol,
}

#[pymethods]
impl PyOperationSymbol {
    /// Create a new OperationSymbol with the given name and arity.
    /// 
    /// Args:
    ///     name (str): The name of the operation symbol
    ///     arity (int): The arity (number of operands) of the operation
    ///     associative (bool, optional): Whether the operation is associative (only valid for binary operations). Defaults to False.
    /// 
    /// Raises:
    ///     ValueError: If associative is True but arity is not 2.
    #[new]
    #[pyo3(signature = (name, arity, associative=false))]
    fn new(name: &str, arity: i32, associative: bool) -> PyResult<Self> {
        match uacalc::alg::op::OperationSymbol::new_safe(name, arity, associative) {
            Ok(inner) => Ok(PyOperationSymbol { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the arity of this operation symbol.
    /// 
    /// Returns:
    ///     int: The arity of the operation symbol
    fn arity(&self) -> i32 {
        self.inner.arity()
    }
    
    /// Get the name of this operation symbol.
    /// 
    /// Returns:
    ///     str: The name of the operation symbol
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Check if this operation symbol is marked as associative.
    /// 
    /// Only binary operations (arity 2) can be associative.
    /// 
    /// Returns:
    ///     bool: True if the operation is associative, False otherwise
    fn is_associative(&self) -> bool {
        self.inner.is_associative()
    }
    
    /// Set whether this operation symbol is associative.
    /// 
    /// Args:
    ///     assoc (bool): Whether the operation should be associative
    /// 
    /// Raises:
    ///     ValueError: If assoc is True but the arity is not 2.
    fn set_associative(&mut self, assoc: bool) -> PyResult<()> {
        match self.inner.set_associative(assoc) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Convert this operation symbol to a string representation.
    /// 
    /// Args:
    ///     show_arity (bool, optional): Whether to include the arity in the string. Defaults to False.
    /// 
    /// Returns:
    ///     str: String representation of the operation symbol
    fn to_string_with_arity(&self, show_arity: Option<bool>) -> String {
        self.inner.to_string_with_arity(show_arity.unwrap_or(false))
    }
    
    /// Get an OperationSymbol in a uniform manner for consistent naming.
    /// 
    /// This method generates operation symbols with standardized names
    /// based on arity, ensuring that similar algebras will have consistent
    /// operation symbol naming.
    /// 
    /// Args:
    ///     arity (int): The arity of the operation symbol to generate
    /// 
    /// Returns:
    ///     OperationSymbol: A new OperationSymbol with a generated name based on the arity
    #[staticmethod]
    fn get_operation_symbol(arity: i32) -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::get_operation_symbol(arity)
        }
    }
    
    /// Get the JOIN constant (binary operation).
    #[staticmethod]
    fn join() -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::join().clone()
        }
    }
    
    /// Get the MEET constant (binary operation).
    #[staticmethod]
    fn meet() -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::meet().clone()
        }
    }
    
    /// Get the PRODUCT constant (binary operation).
    #[staticmethod]
    fn product() -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::product().clone()
        }
    }
    
    /// Get the INVERSE constant (unary operation).
    #[staticmethod]
    fn inverse() -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::inverse().clone()
        }
    }
    
    /// Get the IDENTITY constant (nullary operation).
    #[staticmethod]
    fn identity() -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::identity().clone()
        }
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("OperationSymbol(name='{}', arity={}, associative={})", 
                self.inner.name(), self.inner.arity(), self.inner.is_associative())
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PyOperationSymbol) -> bool {
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
    fn __lt__(&self, other: &PyOperationSymbol) -> bool {
        self.inner < other.inner
    }
    
    /// Python comparison (less than or equal).
    fn __le__(&self, other: &PyOperationSymbol) -> bool {
        self.inner <= other.inner
    }
    
    /// Python comparison (greater than).
    fn __gt__(&self, other: &PyOperationSymbol) -> bool {
        self.inner > other.inner
    }
    
    /// Python comparison (greater than or equal).
    fn __ge__(&self, other: &PyOperationSymbol) -> bool {
        self.inner >= other.inner
    }
}

impl PyOperationSymbol {
    /// Get the inner OperationSymbol (for internal use)
    pub(crate) fn get_inner(&self) -> uacalc::alg::op::OperationSymbol {
        self.inner.clone()
    }

    pub(crate) fn from_inner(inner: uacalc::alg::op::OperationSymbol) -> Self {
        PyOperationSymbol { inner }
    }
}
