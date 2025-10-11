use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::*;

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

/// Python wrapper for SimilarityType
#[pyclass]
pub struct PySimilarityType {
    inner: uacalc::alg::op::SimilarityType,
}

#[pymethods]
impl PySimilarityType {
    /// Create a new SimilarityType with the given operation symbols.
    /// 
    /// Args:
    ///     operation_symbols (List[OperationSymbol]): List of operation symbols
    ///     sort (bool, optional): Whether to sort the operation symbols. Defaults to False.
    /// 
    /// Returns:
    ///     SimilarityType: A new SimilarityType instance
    #[new]
    #[pyo3(signature = (operation_symbols, sort=false))]
    fn new(operation_symbols: &PyAny, sort: bool) -> PyResult<Self> {
        let ops: Vec<uacalc::alg::op::OperationSymbol> = operation_symbols
            .extract::<Vec<PyRef<PyOperationSymbol>>>()?
            .into_iter()
            .map(|py_op| py_op.inner.clone())
            .collect();
        
        match uacalc::alg::op::SimilarityType::new_safe(ops) {
            Ok(mut inner) => {
                if sort {
                    // Create a new instance with sorted symbols
                    let sorted_ops = inner.get_sorted_operation_symbols();
                    inner = uacalc::alg::op::SimilarityType::new(sorted_ops);
                }
                Ok(PySimilarityType { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the operation symbols in this similarity type.
    /// 
    /// Returns:
    ///     List[OperationSymbol]: List of operation symbols
    fn get_operation_symbols(&self) -> Vec<PyOperationSymbol> {
        self.inner.get_operation_symbols()
            .iter()
            .map(|op| PyOperationSymbol { inner: op.clone() })
            .collect()
    }
    
    /// Get a sorted list of operation symbols.
    /// 
    /// The sorting is by lowest arity first, then by alphabetical order on the name.
    /// 
    /// Returns:
    ///     List[OperationSymbol]: A sorted list of operation symbols
    fn get_sorted_operation_symbols(&self) -> Vec<PyOperationSymbol> {
        self.inner.get_sorted_operation_symbols()
            .into_iter()
            .map(|op| PyOperationSymbol { inner: op })
            .collect()
    }
    
    /// Calculate the computer input size for this similarity type.
    /// 
    /// If the result exceeds the maximum integer value, returns -1.
    /// If there are no operations, returns the algebra size.
    /// 
    /// Args:
    ///     alg_size (int): The algebra size
    /// 
    /// Returns:
    ///     int: The input size if it fits in an i32, or -1 if it exceeds the maximum
    fn input_size(&self, alg_size: i32) -> i32 {
        self.inner.input_size(alg_size)
    }
    
    /// Get a map from arity to the number of operations of that arity.
    /// 
    /// This method caches the result for performance.
    /// 
    /// Returns:
    ///     Dict[int, int]: A dictionary mapping arity to count
    fn get_arities_map(&mut self) -> std::collections::HashMap<i32, i32> {
        self.inner.get_arities_map().clone().into_iter().collect()
    }
    
    /// Get the maximum arity among all operation symbols.
    /// 
    /// This method caches the result for performance.
    /// 
    /// Returns:
    ///     int: The maximum arity, or -1 if there are no operations
    fn get_max_arity(&mut self) -> i32 {
        self.inner.get_max_arity()
    }
    
    /// Get the LATTICE_SIMILARITY_TYPE constant.
    /// 
    /// Returns:
    ///     SimilarityType: The static lattice similarity type
    #[staticmethod]
    fn lattice_similarity_type() -> Self {
        PySimilarityType {
            inner: uacalc::alg::op::SimilarityType::lattice_similarity_type().clone()
        }
    }
    
    /// Get the GROUP_SIMILARITY_TYPE constant.
    /// 
    /// Returns:
    ///     SimilarityType: The static group similarity type
    #[staticmethod]
    fn group_similarity_type() -> Self {
        PySimilarityType {
            inner: uacalc::alg::op::SimilarityType::group_similarity_type().clone()
        }
    }
    
    /// Generate a string representation of the arities.
    /// 
    /// Returns:
    ///     str: A string describing the arities of operations in this similarity type
    fn arities_string(&mut self) -> String {
        self.inner.arities_string()
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("SimilarityType({})", self.inner.to_string())
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PySimilarityType) -> bool {
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

pub fn register_alg_module(py: Python, m: &PyModule) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyOperationSymbol>()?;
    m.add_class::<PySimilarityType>()?;
    
    // Export only clean names (without Py prefix)
    m.add("OperationSymbol", m.getattr("PyOperationSymbol")?)?;
    m.add("SimilarityType", m.getattr("PySimilarityType")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyOperationSymbol")?;
    module_dict.del_item("PySimilarityType")?;
    
    Ok(())
}
