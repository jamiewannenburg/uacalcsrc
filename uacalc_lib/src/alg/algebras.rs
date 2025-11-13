/* algebras.rs - Python bindings for Algebras functions
 *
 * This module provides Python bindings for all the Algebras static functions.
 */

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use crate::alg::PyBasicAlgebra;
use crate::alg::op::int_operation::PyIntOperation;
use uacalc::alg::op::Operation;
use uacalc::alg::algebras;

/// Python module for Algebras functions.
///
/// Since all Algebras methods are static functions in Java, we expose them
/// as module-level functions in Python.
pub fn register_algebras_functions(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_endomorphism, m)?)?;

    Ok(())
}

/// Test if an operation is an endomorphism of an algebra.
///
/// An endomorphism is a unary operation that commutes with all operations
/// of the algebra.
///
/// # Arguments
/// * `endo` - The operation to test (must be unary, IntOperation)
/// * `alg` - The algebra to test against (BasicAlgebra)
///
/// # Returns
/// `True` if the operation is an endomorphism, `False` otherwise
///
/// # Raises
/// `ValueError` if the operation is not unary or there's an error
#[pyfunction]
fn is_endomorphism(endo: &PyIntOperation, alg: &PyBasicAlgebra) -> PyResult<bool> {
    match algebras::is_endomorphism(&endo.inner as &dyn Operation, &alg.inner) {
        Ok(result) => Ok(result),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}
