//! Python wrapper for MaltsevDecompositionIterator

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use crate::alg::PyBasicAlgebra;

/// Python wrapper for MaltsevDecompositionIterator
#[pyclass]
pub struct PyMaltsevDecompositionIterator {
    inner: std::cell::RefCell<uacalc::alg::MaltsevDecompositionIterator>,
}

#[pymethods]
impl PyMaltsevDecompositionIterator {
    /// Create a new MaltsevDecompositionIterator for an idempotent algebra.
    ///
    /// Args:
    ///     algebra (BasicAlgebra): An idempotent algebra to decompose
    ///
    /// Raises:
    ///     ValueError: If the algebra is not idempotent
    #[new]
    fn new(algebra: &PyBasicAlgebra) -> PyResult<Self> {
        // Convert Python algebra to Rust algebra
        let alg_box = Box::new(algebra.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        
        match uacalc::alg::MaltsevDecompositionIterator::new_safe(alg_box) {
            Ok(inner) => Ok(PyMaltsevDecompositionIterator {
                inner: std::cell::RefCell::new(inner),
            }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if there are more elements in the iterator.
    ///
    /// Returns:
    ///     bool: True if there are more elements, False otherwise
    fn has_next(&self) -> bool {
        self.inner.borrow().has_next()
    }
    
    /// Python iterator protocol - returns self
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }
    
    /// Python iterator protocol - get next element
    /// 
    /// Returns a dictionary with the algebra's cardinality (matching Java behavior)
    fn __next__(&self, py: Python) -> PyResult<Option<PyObject>> {
        let mut iter = self.inner.borrow_mut();
        
        match iter.next() {
            Some(alg) => {
                // Return cardinality as a dictionary (matching Java main method output)
                let cardinality = alg.cardinality();
                let dict = pyo3::types::PyDict::new_bound(py);
                dict.set_item("cardinality", cardinality)?;
                Ok(Some(dict.into()))
            }
            None => Ok(None),
        }
    }
    
    /// Remove the last element (not supported).
    ///
    /// Raises:
    ///     UnsupportedOperationException: Always raises this exception
    fn remove(&mut self) -> PyResult<()> {
        Err(PyValueError::new_err("UnsupportedOperationException: remove() not supported"))
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("MaltsevDecompositionIterator(has_next={})", self.has_next())
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("MaltsevDecompositionIterator(has_next={})", self.has_next())
    }
}

