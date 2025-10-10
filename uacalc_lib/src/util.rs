use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::util::horner;

/// Python wrapper for Horner encoding/decoding operations
#[pyclass]
pub struct PyHorner;

#[pymethods]
impl PyHorner {
    /// Create a new Horner instance (static methods, so this is just a placeholder)
    #[new]
    fn new() -> Self {
        PyHorner
    }
    
    /// Returns the Horner encoding of an int array representing an element
    /// from a direct product of algebras with various sizes.
    #[staticmethod]
    fn horner(args: Vec<i32>, sizes: Vec<i32>) -> PyResult<i32> {
        match horner::horner_safe(&args, &sizes) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Returns the int array corresponding to this Horner encoding
    /// for a direct product of algebras with various sizes.
    #[staticmethod]
    fn horner_inv(k: i32, sizes: Vec<i32>) -> PyResult<Vec<i32>> {
        match horner::horner_inv_safe(k, &sizes) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Returns the Horner encoding of an int array representing an element
    /// from a direct product of algebras all with the same size.
    #[staticmethod]
    fn horner_same_size(args: Vec<i32>, size: i32) -> PyResult<i32> {
        match horner::horner_same_size_safe(&args, size) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Returns the int array corresponding to this Horner encoding
    /// for a direct product of algebras with the same size.
    #[staticmethod]
    fn horner_inv_same_size(k: i32, size: i32, length: usize) -> PyResult<Vec<i32>> {
        match horner::horner_inv_same_size_safe(k, size, length) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Returns the Horner encoding of an int array representing an element
    /// from a direct product of algebras with the same size (Integer version).
    #[staticmethod]
    fn horner_integer(args: Vec<i32>, size: i32) -> PyResult<i32> {
        match horner::horner_integer_safe(&args, size) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// A convenience method for generating a new array with the reverse
    /// order of the given array.
    #[staticmethod]
    fn reverse_array(arr: Vec<i32>) -> Vec<i32> {
        horner::reverse_array(&arr)
    }
    
    /// If values are the values of a function at [0,0, ...,0], [1,0,...,0],
    /// this gives the values in the order [0,0, ...,0], [0,0,...,1], ...  .
    #[staticmethod]
    fn left_right_reverse(values: Vec<i32>, alg_size: i32, arity: usize) -> PyResult<Vec<i32>> {
        match horner::left_right_reverse_safe(&values, alg_size, arity) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "Horner".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "Horner()".to_string()
    }
}

pub fn register_util_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyHorner>()?;
    Ok(())
}
