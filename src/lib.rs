//! UACalc Rust Implementation
//! 
//! This crate provides Rust implementations of UACalc (Universal Algebra Calculator) 
//! classes with Python bindings using PyO3.

pub mod alg;

use pyo3::prelude::*;

/// Python module for UACalc Rust implementation
#[pymodule]
fn uacalc_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    // Export operation-related classes
    m.add_class::<alg::op::OperationSymbol>()?;
    m.add_class::<alg::op::AbstractOperation>()?;
    m.add_class::<alg::op::IntOperation>()?;
    
    Ok(())
}