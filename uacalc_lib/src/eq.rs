use pyo3::prelude::*;
use uacalc::eq::*;

pub fn register_eq_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // TODO: Add Python bindings for equation structures
    Ok(())
}
