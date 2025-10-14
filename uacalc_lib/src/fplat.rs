use pyo3::prelude::*;
use uacalc::fplat::*;

pub fn register_fplat_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // TODO: Add Python bindings for fplat structures
    Ok(())
}
