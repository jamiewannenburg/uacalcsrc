use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

use uacalc::alg::op::SimilarityType;

use super::operation_symbol as op_mod_symbol;
use crate::alg as root_alg;
use crate::alg::op::operation_symbol::PyOperationSymbol;

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
        // Accept either root-level or local OperationSymbol wrappers
        let ops: Vec<uacalc::alg::op::OperationSymbol> = if let Ok(v) = operation_symbols.extract::<Vec<PyRef<root_alg::PyOperationSymbol>>>() {
            v.into_iter().map(|py_op| py_op.get_inner()).collect()
        } else if let Ok(v) = operation_symbols.extract::<Vec<PyRef<op_mod_symbol::PyOperationSymbol>>>() {
            v.into_iter().map(|py_op| py_op.get_inner()).collect()
        } else {
            return Err(PyValueError::new_err("Expected list of OperationSymbol"));
        };

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
            .map(|op| PyOperationSymbol::from_inner(op.clone()))
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
            .map(|op| PyOperationSymbol::from_inner(op))
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

// Internal accessor for other bindings modules
impl PySimilarityType {
    pub(crate) fn get_inner(&self) -> SimilarityType {
        self.inner.clone()
    }
}