use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::path::Path;

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

/// Python wrapper for ExtFileFilter
#[pyclass]
pub struct PyExtFileFilter {
    inner: uacalc::io::ExtFileFilter,
}

#[pymethods]
impl PyExtFileFilter {
    /// Create a new ExtFileFilter with description and list of extensions
    #[new]
    #[pyo3(signature = (description, exts))]
    fn new(description: &str, exts: Vec<String>) -> PyResult<Self> {
        match uacalc::io::ExtFileFilter::new_safe(description, exts) {
            Ok(inner) => Ok(PyExtFileFilter { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    
    /// Determines whether the given file should be accepted by this filter
    fn accept(&self, path: String) -> PyResult<bool> {
        let path_obj = Path::new(&path);
        Ok(self.inner.accept(path_obj))
    }
    
    /// Returns the description of this filter
    fn get_description(&self) -> &str {
        self.inner.get_description()
    }
    
    /// Returns the set of allowed extensions
    fn get_extensions(&self) -> Vec<String> {
        self.inner.get_extensions().iter().cloned().collect()
    }
    
    /// Split the file name into 2 parts: filename and extension
    #[staticmethod]
    fn split_off_extension(path: String) -> PyResult<(Option<String>, Option<String>)> {
        let path_obj = Path::new(&path);
        Ok(uacalc::io::ExtFileFilter::split_off_extension(path_obj))
    }
    
    /// Get the file extension from a file path
    #[staticmethod]
    fn get_extension(path: String) -> PyResult<Option<String>> {
        let path_obj = Path::new(&path);
        Ok(uacalc::io::ExtFileFilter::get_extension(path_obj))
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("ExtFileFilter('{}')", self.inner.get_description())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyExtFileFilter) -> bool {
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

/// Python wrapper for AlgebraReader
#[pyclass]
pub struct PyAlgebraReader {
    inner: uacalc::io::AlgebraReader,
}

#[pymethods]
impl PyAlgebraReader {
    /// Create a new AlgebraReader from a file path
    #[staticmethod]
    #[pyo3(signature = (file_path))]
    fn new_from_file(file_path: String) -> PyResult<Self> {
        let path = Path::new(&file_path);
        match uacalc::io::AlgebraReader::new_from_file(path) {
            Ok(inner) => Ok(PyAlgebraReader { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new AlgebraReader from a path string
    #[staticmethod]
    #[pyo3(signature = (path))]
    fn new_from_path(path: String) -> PyResult<Self> {
        match uacalc::io::AlgebraReader::new_from_path(&path) {
            Ok(inner) => Ok(PyAlgebraReader { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new AlgebraReader from input data
    #[staticmethod]
    #[pyo3(signature = (data))]
    fn new_from_stream(data: Vec<u8>) -> PyResult<Self> {
        match uacalc::io::AlgebraReader::new_from_stream(data) {
            Ok(inner) => Ok(PyAlgebraReader { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Read a single algebra from the file
    fn read_algebra_file(&self) -> PyResult<crate::alg::PyBasicSmallAlgebra> {
        match self.inner.read_algebra_file() {
            Ok(algebra) => Ok(crate::alg::PyBasicSmallAlgebra::from_inner(algebra)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Read a single algebra from the stream
    fn read_algebra_from_stream(&self) -> PyResult<crate::alg::PyBasicSmallAlgebra> {
        match self.inner.read_algebra_from_stream() {
            Ok(algebra) => Ok(crate::alg::PyBasicSmallAlgebra::from_inner(algebra)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Read a list of algebras from the file
    fn read_algebra_list_file(&self) -> PyResult<Vec<crate::alg::PyBasicSmallAlgebra>> {
        match self.inner.read_algebra_list_file() {
            Ok(algebras) => Ok(algebras.into_iter()
                .map(|a| crate::alg::PyBasicSmallAlgebra::from_inner(a))
                .collect()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Read a list of algebras from the stream
    fn read_algebra_list_from_stream(&self) -> PyResult<Vec<crate::alg::PyBasicSmallAlgebra>> {
        match self.inner.read_algebra_list_from_stream() {
            Ok(algebras) => Ok(algebras.into_iter()
                .map(|a| crate::alg::PyBasicSmallAlgebra::from_inner(a))
                .collect()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "AlgebraReader".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "AlgebraReader()".to_string()
    }
}

pub fn register_io_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyBadAlgebraFileException>()?;
    m.add_class::<PyExtFileFilter>()?;
    m.add_class::<PyAlgebraReader>()?;
    
    // Export only clean names (without Py prefix)
    m.add("BadAlgebraFileException", m.getattr("PyBadAlgebraFileException")?)?;
    m.add("ExtFileFilter", m.getattr("PyExtFileFilter")?)?;
    m.add("AlgebraReader", m.getattr("PyAlgebraReader")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyBadAlgebraFileException")?;
    module_dict.del_item("PyExtFileFilter")?;
    module_dict.del_item("PyAlgebraReader")?;
    
    Ok(())
}
