use pyo3::prelude::*;
use uacalc::group::*;

pub fn register_group_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // TODO: Add Python bindings for group structures
    Ok(())
}
