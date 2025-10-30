use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

/// Python wrapper for PrintType
#[pyclass]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PyPrintType {
    pub(crate) inner: uacalc::alg::conlat::partition::PrintType,
}

#[pymethods]
impl PyPrintType {
    /// Create a new PrintType from string.
    #[new]
    fn new(print_type: &str) -> PyResult<Self> {
        let inner = match print_type.to_lowercase().as_str() {
            "internal" => uacalc::alg::conlat::partition::PrintType::Internal,
            "ewk" => uacalc::alg::conlat::partition::PrintType::Ewk,
            "block" => uacalc::alg::conlat::partition::PrintType::Block,
            "human" => uacalc::alg::conlat::partition::PrintType::Human,
            "sq_brace_block" => uacalc::alg::conlat::partition::PrintType::SqBraceBlock,
            _ => return Err(PyValueError::new_err(format!("Invalid print type: {}", print_type))),
        };
        Ok(PyPrintType { inner })
    }

    /// Get the string representation of this print type.
    fn to_string(&self) -> String {
        match self.inner {
            uacalc::alg::conlat::partition::PrintType::Internal => "internal".to_string(),
            uacalc::alg::conlat::partition::PrintType::Ewk => "ewk".to_string(),
            uacalc::alg::conlat::partition::PrintType::Block => "block".to_string(),
            uacalc::alg::conlat::partition::PrintType::Human => "human".to_string(),
            uacalc::alg::conlat::partition::PrintType::SqBraceBlock => "sq_brace_block".to_string(),
        }
    }

    fn __str__(&self) -> String { self.to_string() }

    fn __repr__(&self) -> String { format!("PrintType('{}')", self.to_string()) }

    fn __eq__(&self, other: &PyPrintType) -> bool { self.inner == other.inner }
}


