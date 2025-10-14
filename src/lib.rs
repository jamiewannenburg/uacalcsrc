//! Universal Algebra Calculator - Rust Implementation
//! 
//! This crate provides Rust implementations of the core universal algebra
//! concepts from the Java UACalc library, with Python bindings via PyO3.

use pyo3::prelude::*;

pub mod alg;
pub mod error;

/// Python module definition
#[pymodule]
fn uacalc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add operation types
    m.add_class::<alg::op::PyOperationSymbol>()?;
    m.add_class::<alg::op::PyAbstractOperation>()?;
    m.add_class::<alg::op::PyIntOperation>()?;
    
    Ok(())
}