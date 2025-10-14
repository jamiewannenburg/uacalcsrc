use pyo3::prelude::*;
use uacalc::element::*;

pub fn register_element_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // TODO: Add Python bindings for element structures
    Ok(())
}
