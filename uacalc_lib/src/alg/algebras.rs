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
    m.add_function(wrap_pyfunction!(is_homomorphism, m)?)?;

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

/// Test if a map is a homomorphism from one algebra to another.
///
/// A homomorphism is a map h: A -> B such that for any operation f in alg0
/// and corresponding operation g in alg1 (with the same symbol), we have:
/// h(f(x1, x2, ..., xn)) = g(h(x1), h(x2), ..., h(xn))
///
/// # Arguments
/// * `map` - A list of integers defining the map from elements of alg0 to elements of alg1
/// * `alg0` - The source algebra (BasicAlgebra)
/// * `alg1` - The target algebra (BasicAlgebra)
///
/// # Returns
/// `True` if the map is a homomorphism, `False` otherwise
///
/// # Raises
/// `ValueError` if there's an error (e.g., map size mismatch, missing operation)
#[pyfunction]
fn is_homomorphism(map: Vec<i32>, alg0: &PyBasicAlgebra, alg1: &PyBasicAlgebra) -> PyResult<bool> {
    match algebras::is_homomorphism(&map, &alg0.inner, &alg1.inner) {
        Ok(result) => Ok(result),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}
