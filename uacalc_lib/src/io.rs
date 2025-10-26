use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::fs::File;
use std::path::Path;

/// Python wrapper for Mace4Reader
#[pyclass]
pub struct PyMace4Reader {
    // We don't store the reader directly to avoid Send issues
    // Instead, we'll create it fresh for each operation
}

#[pymethods]
impl PyMace4Reader {
    /// Create a new Mace4Reader from a file path
    #[staticmethod]
    fn new_from_file(file_path: String) -> PyResult<Self> {
        // Just return an empty instance - we'll create the reader when needed
        Ok(PyMace4Reader {})
    }
    
    /// Create a new Mace4Reader from input data
    #[staticmethod]
    fn new_from_stream(data: Vec<u8>) -> PyResult<Self> {
        // Just return an empty instance - we'll create the reader when needed
        Ok(PyMace4Reader {})
    }
    
    /// Parse a single algebra from a file path
    #[staticmethod]
    fn parse_algebra_from_file(file_path: String) -> PyResult<Option<crate::alg::PyBasicSmallAlgebra>> {
        let file = File::open(&file_path)
            .map_err(|e| PyValueError::new_err(format!("Failed to open file {}: {}", file_path, e)))?;
        
        match uacalc::io::Mace4Reader::new_safe(Box::new(file)) {
            Ok(mut reader) => {
                match reader.parse_algebra() {
                    Ok(Some(algebra)) => {
                        let name = algebra.name().to_string();
                        let cardinality = algebra.cardinality();
                        let operations = algebra.operations();
                        
                        let universe: std::collections::HashSet<i32> = (0..cardinality).collect();
                        let basic_alg = uacalc::alg::small_algebra::BasicSmallAlgebra::new(name, universe, operations);
                        Ok(Some(crate::alg::PyBasicSmallAlgebra::from_inner(basic_alg)))
                    }
                    Ok(None) => Ok(None),
                    Err(e) => Err(PyValueError::new_err(e.message().to_string())),
                }
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Parse a single algebra from input data
    fn parse_algebra_from_stream(&self, data: Vec<u8>) -> PyResult<Option<crate::alg::PyBasicSmallAlgebra>> {
        let cursor = std::io::Cursor::new(data);
        match uacalc::io::Mace4Reader::new_safe(Box::new(cursor)) {
            Ok(mut reader) => {
                match reader.parse_algebra() {
                    Ok(Some(algebra)) => {
                        let name = algebra.name().to_string();
                        let cardinality = algebra.cardinality();
                        let operations = algebra.operations();
                        
                        let universe: std::collections::HashSet<i32> = (0..cardinality).collect();
                        let basic_alg = uacalc::alg::small_algebra::BasicSmallAlgebra::new(name, universe, operations);
                        Ok(Some(crate::alg::PyBasicSmallAlgebra::from_inner(basic_alg)))
                    }
                    Ok(None) => Ok(None),
                    Err(e) => Err(PyValueError::new_err(e.message().to_string())),
                }
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Parse a list of algebras from a file path
    fn parse_algebra_list_from_file(&self, file_path: String) -> PyResult<Vec<crate::alg::PyBasicSmallAlgebra>> {
        let file = File::open(&file_path)
            .map_err(|e| PyValueError::new_err(format!("Failed to open file {}: {}", file_path, e)))?;
        
        match uacalc::io::Mace4Reader::new_safe(Box::new(file)) {
            Ok(mut reader) => {
                match reader.parse_algebra_list() {
                    Ok(algebras) => {
                        let mut result = Vec::new();
                        for algebra in algebras {
                            let name = algebra.name().to_string();
                            let cardinality = algebra.cardinality();
                            let operations = algebra.operations();
                            
                            let universe: std::collections::HashSet<i32> = (0..cardinality).collect();
                            let basic_alg = uacalc::alg::small_algebra::BasicSmallAlgebra::new(name, universe, operations);
                            result.push(crate::alg::PyBasicSmallAlgebra::from_inner(basic_alg));
                        }
                        Ok(result)
                    }
                    Err(e) => Err(PyValueError::new_err(e.message().to_string())),
                }
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Parse a list of algebras from input data
    fn parse_algebra_list_from_stream(&self, data: Vec<u8>) -> PyResult<Vec<crate::alg::PyBasicSmallAlgebra>> {
        let cursor = std::io::Cursor::new(data);
        match uacalc::io::Mace4Reader::new_safe(Box::new(cursor)) {
            Ok(mut reader) => {
                match reader.parse_algebra_list() {
                    Ok(algebras) => {
                        let mut result = Vec::new();
                        for algebra in algebras {
                            let name = algebra.name().to_string();
                            let cardinality = algebra.cardinality();
                            let operations = algebra.operations();
                            
                            let universe: std::collections::HashSet<i32> = (0..cardinality).collect();
                            let basic_alg = uacalc::alg::small_algebra::BasicSmallAlgebra::new(name, universe, operations);
                            result.push(crate::alg::PyBasicSmallAlgebra::from_inner(basic_alg));
                        }
                        Ok(result)
                    }
                    Err(e) => Err(PyValueError::new_err(e.message().to_string())),
                }
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if a character is ordinary (can start a symbol)
    #[staticmethod]
    fn is_ordinary_character(c: char) -> bool {
        uacalc::io::Mace4Reader::is_ordinary_character(c)
    }
    
    /// Check if a character is special (operator character)
    #[staticmethod]
    fn is_special_character(c: char) -> bool {
        uacalc::io::Mace4Reader::is_special_character(c)
    }
    
    /// String representation
    fn __str__(&self) -> String {
        "Mace4Reader()".to_string()
    }
    
    /// Debug representation
    fn __repr__(&self) -> String {
        "Mace4Reader()".to_string()
    }
}

/// Python wrapper for AlgebraReader
#[pyclass]
pub struct PyAlgebraReader {
    file_path: Option<String>,
}

#[pymethods]
impl PyAlgebraReader {
    /// Create a new AlgebraReader from a file path
    #[staticmethod]
    fn new_from_file(file_path: String) -> PyResult<Self> {
        Ok(PyAlgebraReader {
            file_path: Some(file_path),
        })
    }
    
    /// Create a new AlgebraReader from input data
    #[staticmethod]
    fn new_from_stream(data: Vec<u8>) -> PyResult<Self> {
        // For stream-based readers, we don't store a file path
        Ok(PyAlgebraReader {
            file_path: None,
        })
    }
    
    /// Read a single algebra from the file path stored in this reader
    fn read_algebra_file(&self) -> PyResult<Option<crate::alg::PyBasicSmallAlgebra>> {
        if let Some(ref file_path) = self.file_path {
            Self::read_algebra_from_file(file_path.clone())
        } else {
            Err(PyValueError::new_err("No file path stored in reader"))
        }
    }
    
    /// Read a single algebra from a file path
    #[staticmethod]
    fn read_algebra_from_file(file_path: String) -> PyResult<Option<crate::alg::PyBasicSmallAlgebra>> {
        let path = Path::new(&file_path);
        match uacalc::io::AlgebraReader::new_from_file(path) {
            Ok(reader) => {
                match reader.read_algebra_file() {
                    Ok(algebra) => Ok(Some(crate::alg::PyBasicSmallAlgebra::from_inner(algebra))),
                    Err(e) => Err(PyValueError::new_err(e)),
                }
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Read a single algebra from input data
    fn read_algebra_from_stream(&self, data: Vec<u8>) -> PyResult<Option<crate::alg::PyBasicSmallAlgebra>> {
        match uacalc::io::AlgebraReader::new_from_stream(data) {
            Ok(reader) => {
                match reader.read_algebra_from_stream() {
                    Ok(algebra) => Ok(Some(crate::alg::PyBasicSmallAlgebra::from_inner(algebra))),
                    Err(e) => Err(PyValueError::new_err(e)),
                }
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Read a list of algebras from a file path
    fn read_algebra_list_from_file(&self, file_path: String) -> PyResult<Vec<crate::alg::PyBasicSmallAlgebra>> {
        let path = Path::new(&file_path);
        match uacalc::io::AlgebraReader::new_from_file(path) {
            Ok(reader) => {
                match reader.read_algebra_list_file() {
                    Ok(algebras) => {
                        let result = algebras.into_iter()
                            .map(|alg| crate::alg::PyBasicSmallAlgebra::from_inner(alg))
                            .collect();
                        Ok(result)
                    }
                    Err(e) => Err(PyValueError::new_err(e)),
                }
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Read a list of algebras from input data
    fn read_algebra_list_from_stream(&self, data: Vec<u8>) -> PyResult<Vec<crate::alg::PyBasicSmallAlgebra>> {
        match uacalc::io::AlgebraReader::new_from_stream(data) {
            Ok(reader) => {
                match reader.read_algebra_list_from_stream() {
                    Ok(algebras) => {
                        let result = algebras.into_iter()
                            .map(|alg| crate::alg::PyBasicSmallAlgebra::from_inner(alg))
                            .collect();
                        Ok(result)
                    }
                    Err(e) => Err(PyValueError::new_err(e)),
                }
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// String representation
    fn __str__(&self) -> String {
        "AlgebraReader()".to_string()
    }
    
    /// Debug representation
    fn __repr__(&self) -> String {
        "AlgebraReader()".to_string()
    }
}

/// Python wrapper for BadAlgebraFileException
#[pyclass]
pub struct PyBadAlgebraFileException {
    inner: uacalc::io::BadAlgebraFileException,
}

#[pymethods]
impl PyBadAlgebraFileException {
    /// Create a new BadAlgebraFileException with the given message
    #[new]
    fn new(message: String) -> Self {
        Self {
            inner: uacalc::io::BadAlgebraFileException::new(&message),
        }
    }
    
    /// Create a new BadAlgebraFileException with the given message (safe version)
    #[staticmethod]
    fn new_safe(message: String) -> PyResult<Self> {
        match uacalc::io::BadAlgebraFileException::new_safe(&message) {
            Ok(inner) => Ok(Self { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the error message
    fn message(&self) -> String {
        self.inner.message().to_string()
    }
    
    /// String representation
    fn __str__(&self) -> String {
        format!("org.uacalc.io.BadAlgebraFileException: {}", self.inner.message())
    }
    
    /// Debug representation
    fn __repr__(&self) -> String {
        format!("BadAlgebraFileException('{}')", self.inner.message())
    }
    
    /// Equality comparison
    fn __eq__(&self, other: &Self) -> bool {
        self.inner == other.inner
    }
    
    /// Hash function
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
    /// Create a new ExtFileFilter with the given description and extensions
    #[new]
    fn new(description: String, exts: Vec<String>) -> PyResult<Self> {
        if description.is_empty() {
            return Err(PyValueError::new_err("Description cannot be empty"));
        }
        if exts.is_empty() {
            return Err(PyValueError::new_err("Extensions list cannot be empty"));
        }
        Ok(Self {
            inner: uacalc::io::ExtFileFilter::new(&description, exts),
        })
    }
    
    /// Create a new ExtFileFilter with the given description and single extension
    #[staticmethod]
    fn new_single(description: String, ext: String) -> Self {
        Self {
            inner: uacalc::io::ExtFileFilter::new_single(&description, &ext),
        }
    }
    
    /// Create a new ExtFileFilter with the given description and extensions (safe version)
    #[staticmethod]
    fn new_safe(description: String, exts: Vec<String>) -> PyResult<Self> {
        if description.is_empty() {
            return Err(PyValueError::new_err("Description cannot be empty"));
        }
        if exts.is_empty() {
            return Err(PyValueError::new_err("Extensions list cannot be empty"));
        }
        match uacalc::io::ExtFileFilter::new_safe(&description, exts) {
            Ok(inner) => Ok(Self { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new ExtFileFilter with the given description and single extension (safe version)
    #[staticmethod]
    fn new_single_safe(description: String, ext: String) -> PyResult<Self> {
        if description.is_empty() {
            return Err(PyValueError::new_err("Description cannot be empty"));
        }
        if ext.is_empty() {
            return Err(PyValueError::new_err("Extension cannot be empty"));
        }
        match uacalc::io::ExtFileFilter::new_single_safe(&description, &ext) {
            Ok(inner) => Ok(Self { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if a file should be accepted by this filter
    fn accept(&self, path: String) -> bool {
        use std::path::Path;
        self.inner.accept(Path::new(&path))
    }
    
    /// Get the description of this filter
    fn get_description(&self) -> String {
        self.inner.get_description().to_string()
    }
    
    /// Get the list of allowed extensions
    fn get_extensions(&self) -> Vec<String> {
        self.inner.get_extensions().clone()
    }
    
    /// Split the file name into name and extension
    #[staticmethod]
    fn split_off_extension(path: String) -> (Option<String>, Option<String>) {
        use std::path::Path;
        uacalc::io::ExtFileFilter::split_off_extension(Path::new(&path))
    }
    
    /// Get the file extension from a file path
    #[staticmethod]
    fn get_extension(path: String) -> Option<String> {
        use std::path::Path;
        uacalc::io::ExtFileFilter::get_extension(Path::new(&path))
    }
    
    /// String representation
    fn __str__(&self) -> String {
        format!("ExtFileFilter({})", self.inner.get_description())
    }
    
    /// Debug representation
    fn __repr__(&self) -> String {
        format!("ExtFileFilter('{}')", self.inner.get_description())
    }
    
    /// Equality comparison
    fn __eq__(&self, other: &Self) -> bool {
        self.inner == other.inner
    }
    
    /// Hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
}

/// Register the io module
pub fn register_io_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyMace4Reader>()?;
    m.add("Mace4Reader", m.getattr("PyMace4Reader")?)?;
    
    m.add_class::<PyAlgebraReader>()?;
    m.add("AlgebraReader", m.getattr("PyAlgebraReader")?)?;
    
    m.add_class::<PyBadAlgebraFileException>()?;
    m.add("BadAlgebraFileException", m.getattr("PyBadAlgebraFileException")?)?;
    
    m.add_class::<PyExtFileFilter>()?;
    m.add("ExtFileFilter", m.getattr("PyExtFileFilter")?)?;
    
    let module_dict = m.dict();
    module_dict.del_item("PyMace4Reader")?;
    module_dict.del_item("PyAlgebraReader")?;
    module_dict.del_item("PyBadAlgebraFileException")?;
    module_dict.del_item("PyExtFileFilter")?;
    
    Ok(())
}