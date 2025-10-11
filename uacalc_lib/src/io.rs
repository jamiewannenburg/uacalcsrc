use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::io::*;

/// Python wrapper for BadAlgebraFileException
#[pyclass]
pub struct PyBadAlgebraFileException {
    inner: uacalc::io::BadAlgebraFileException,
}

#[pymethods]
impl PyBadAlgebraFileException {
    /// Create a new BadAlgebraFileException
    #[new]
    #[pyo3(signature = (message))]
    fn new(message: &str) -> PyResult<Self> {
        match uacalc::io::BadAlgebraFileException::new_safe(message) {
            Ok(inner) => Ok(PyBadAlgebraFileException { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the error message
    fn message(&self) -> &str {
        self.inner.message()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("BadAlgebraFileException('{}')", self.inner.message())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyBadAlgebraFileException) -> bool {
        self.inner == other.inner
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
}

pub fn register_io_module(_py: Python, m: &PyModule) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyBadAlgebraFileException>()?;
    
    // Export only clean names (without Py prefix)
    m.add("BadAlgebraFileException", m.getattr("PyBadAlgebraFileException")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyBadAlgebraFileException")?;
    
    Ok(())
}
