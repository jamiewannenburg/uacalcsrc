use pyo3::prelude::*;
use uacalc::example::*;

pub fn register_example_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // TODO: Add Python bindings for example structures
    Ok(())
}
