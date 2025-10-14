use pyo3::prelude::*;
use uacalc::terms::*;

pub fn register_terms_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // TODO: Add Python bindings for terms structures
    Ok(())
}
