
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::util::{IntArray, IntArrayTrait};
use crate::alg::big_product_algebra::PyBigProductAlgebra;

/// Python wrapper for IntArray
#[pyclass(name = "IntArray")]
#[derive(Clone)]
pub struct PyIntArray {
    inner: IntArray,
}

#[pymethods]
impl PyIntArray {
    /// Create a new IntArray.
    /// 
    /// # Arguments
    /// * `size` - The size of the array
    /// 
    /// # Returns
    /// A new IntArray instance
    #[new]
    fn new(size: usize) -> PyResult<Self> {
        match IntArray::new(size) {
            Ok(ia) => Ok(PyIntArray { inner: ia }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create an IntArray from a list.
    /// 
    /// # Arguments
    /// * `values` - The values
    /// 
    /// # Returns
    /// A new IntArray instance
    #[staticmethod]
    fn from_list(values: Vec<i32>) -> PyResult<Self> {
        match IntArray::from_array(values) {
            Ok(ia) => Ok(PyIntArray { inner: ia }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the size.
    fn size(&self) -> usize {
        self.inner.universe_size()
    }
    
    /// Get a value at an index.
    fn get(&self, index: usize) -> PyResult<i32> {
        match self.inner.get(index) {
            Some(val) => Ok(val),
            None => Err(PyValueError::new_err(format!("Index {} out of bounds", index))),
        }
    }
    
    /// Set a value at an index.
    fn set(&mut self, index: usize, value: i32) -> PyResult<()> {
        match self.inner.set(index, value) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Convert to a list.
    fn to_list(&self) -> Vec<i32> {
        let mut result = Vec::new();
        for i in 0..self.inner.universe_size() {
            if let Some(val) = self.inner.get(i) {
                result.push(val);
            }
        }
        result
    }
    
    fn __str__(&self) -> String {
        format!("{:?}", self.to_list())
    }
    
    fn __repr__(&self) -> String {
        format!("IntArray({:?})", self.to_list())
    }
    
    fn __eq__(&self, other: &PyIntArray) -> bool {
        self.inner == other.inner
    }
    
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
}

pub fn register_alg_bindings(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyBigProductAlgebra>()?;
    crate::alg::small_algebra::register_small_algebra(_py, m)?;
    m.add_class::<PyIntArray>()?;

    // Don't try to create aliases or delete - PyO3 already handles the name from #[pyclass(name = "...")]

    // Register Malcev functions
    crate::alg::malcev::register_malcev_functions(_py, m)?;

    // Register Closer
    crate::alg::closer::register_closer(_py, m)?;

    // Register GeneralAlgebra
    crate::alg::general_algebra::register_general_algebra_module(_py, m)?;

    Ok(())
}

