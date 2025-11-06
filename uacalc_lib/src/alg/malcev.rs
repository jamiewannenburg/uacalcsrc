/* malcev.rs - Python bindings for Malcev functions
 *
 * This module provides Python bindings for all the Malcev static functions.
 */

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use crate::alg::PyBasicAlgebra;
use uacalc::alg::malcev;

/// Python module for Malcev functions.
///
/// Since all Malcev methods are static functions in Java, we expose them
/// as module-level functions in Python.
pub fn register_malcev_functions(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Note: All functions return NotImplementedError for now
    // They will be implemented as the Rust implementation is completed

    m.add_function(wrap_pyfunction!(malcev_term, m)?)?;
    m.add_function(wrap_pyfunction!(majority_term, m)?)?;
    m.add_function(wrap_pyfunction!(minority_term, m)?)?;
    m.add_function(wrap_pyfunction!(pixley_term, m)?)?;
    m.add_function(wrap_pyfunction!(nu_term, m)?)?;
    m.add_function(wrap_pyfunction!(nu_term_idempotent, m)?)?;
    m.add_function(wrap_pyfunction!(weak_nu_term, m)?)?;
    m.add_function(wrap_pyfunction!(weak_majority_term, m)?)?;
    m.add_function(wrap_pyfunction!(semilattice_term, m)?)?;
    m.add_function(wrap_pyfunction!(difference_term, m)?)?;
    m.add_function(wrap_pyfunction!(jonsson_terms, m)?)?;
    m.add_function(wrap_pyfunction!(hagemann_mitschke_terms, m)?)?;
    m.add_function(wrap_pyfunction!(gumm_terms, m)?)?;
    m.add_function(wrap_pyfunction!(join_term, m)?)?;
    m.add_function(wrap_pyfunction!(sd_meet_terms, m)?)?;
    m.add_function(wrap_pyfunction!(sd_terms, m)?)?;
    m.add_function(wrap_pyfunction!(markovic_mckenzie_siggers_taylor_term, m)?)?;
    m.add_function(wrap_pyfunction!(weak_3_edge_term, m)?)?;
    m.add_function(wrap_pyfunction!(is_congruence_dist_idempotent, m)?)?;
    m.add_function(wrap_pyfunction!(is_congruence_modular_idempotent, m)?)?;
    m.add_function(wrap_pyfunction!(congruence_modular_variety, m)?)?;
    m.add_function(wrap_pyfunction!(jonsson_level, m)?)?;
    m.add_function(wrap_pyfunction!(local_distributivity_level, m)?)?;
    m.add_function(wrap_pyfunction!(day_quadruple, m)?)?;
    m.add_function(wrap_pyfunction!(find_day_quadruple_in_square, m)?)?;
    m.add_function(wrap_pyfunction!(sd_meet_idempotent, m)?)?;
    m.add_function(wrap_pyfunction!(cyclic_term_idempotent, m)?)?;
    m.add_function(wrap_pyfunction!(primality_terms, m)?)?;
    m.add_function(wrap_pyfunction!(fixed_k_edge_term, m)?)?;
    m.add_function(wrap_pyfunction!(fixed_k_qwnu, m)?)?;

    Ok(())
}

/// Find a Malcev term for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// The Malcev term as a string if one exists, None otherwise
#[pyfunction]
fn malcev_term(algebra: &PyBasicAlgebra) -> PyResult<Option<String>> {
    match malcev::malcev_term(&algebra.inner) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a majority term for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// The majority term as a string if one exists, None otherwise
#[pyfunction]
fn majority_term(algebra: &PyBasicAlgebra) -> PyResult<Option<String>> {
    match malcev::majority_term(&algebra.inner) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a minority term for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// The minority term as a string if one exists, None otherwise
#[pyfunction]
fn minority_term(algebra: &PyBasicAlgebra) -> PyResult<Option<String>> {
    match malcev::minority_term(&algebra.inner) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a Pixley term for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// The Pixley term as a string if one exists, None otherwise
#[pyfunction]
fn pixley_term(algebra: &PyBasicAlgebra) -> PyResult<Option<String>> {
    match malcev::pixley_term(&algebra.inner) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a near unanimity term of the given arity.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
/// * `arity` - The arity of the NU term
///
/// # Returns
/// The NU term as a string if one exists, None otherwise
#[pyfunction]
fn nu_term(algebra: &PyBasicAlgebra, arity: usize) -> PyResult<Option<String>> {
    match malcev::nu_term(&algebra.inner, arity) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Test if an idempotent algebra has an NU term of the given arity.
///
/// # Arguments
/// * `algebra` - The idempotent algebra to check
/// * `arity` - The arity of the NU term
///
/// # Returns
/// True if the algebra has an NU term, False otherwise
#[pyfunction]
fn nu_term_idempotent(algebra: &PyBasicAlgebra, arity: usize) -> PyResult<bool> {
    match malcev::nu_term_idempotent(&algebra.inner, arity) {
        Ok(result) => Ok(result),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a weak near unanimity term of the given arity.
///
/// # Arguments
/// * `algebra` - The algebra to check
/// * `arity` - The arity of the weak NU term
///
/// # Returns
/// The weak NU term if one exists, None otherwise
#[pyfunction]
fn weak_nu_term(algebra: &PyBasicAlgebra, arity: usize) -> PyResult<Option<String>> {
    match malcev::weak_nu_term(&algebra.inner, arity) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a weak majority term for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// The weak majority term as a string if one exists, None otherwise
#[pyfunction]
fn weak_majority_term(algebra: &PyBasicAlgebra) -> PyResult<Option<String>> {
    match malcev::weak_majority_term(&algebra.inner) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a semilattice term for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// The semilattice term as a string if one exists, None otherwise
#[pyfunction]
fn semilattice_term(algebra: &PyBasicAlgebra) -> PyResult<Option<String>> {
    match malcev::semilattice_term(&algebra.inner) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a difference term for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check
///
/// # Returns
/// The difference term if one exists, None otherwise
#[pyfunction]
fn difference_term(algebra: &PyBasicAlgebra) -> PyResult<Option<String>> {
    match malcev::difference_term(&algebra.inner) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find Jonsson terms for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// List of Jonsson terms as strings if they exist, None otherwise
#[pyfunction]
fn jonsson_terms(algebra: &PyBasicAlgebra) -> PyResult<Option<Vec<String>>> {
    match malcev::jonsson_terms(&algebra.inner) {
        Ok(Some(terms)) => {
            let term_strings: Vec<String> = terms.iter().map(|t| format!("{}", t)).collect();
            Ok(Some(term_strings))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find Hagemann-Mitschke terms for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// List of Hagemann-Mitschke terms as strings if they exist, None otherwise
#[pyfunction]
fn hagemann_mitschke_terms(algebra: &PyBasicAlgebra) -> PyResult<Option<Vec<String>>> {
    match malcev::hagemann_mitschke_terms(&algebra.inner) {
        Ok(Some(terms)) => {
            let term_strings: Vec<String> = terms.iter().map(|t| format!("{}", t)).collect();
            Ok(Some(term_strings))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find Gumm terms for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check
///
/// # Returns
/// List of Gumm terms if they exist, None otherwise
#[pyfunction]
fn gumm_terms(algebra: &PyBasicAlgebra) -> PyResult<Option<Vec<String>>> {
    match malcev::gumm_terms(&algebra.inner) {
        Ok(Some(terms)) => {
            let term_strings: Vec<String> = terms.iter().map(|t| format!("{}", t)).collect();
            Ok(Some(term_strings))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Get a join term (Kearnes-Kiss) for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// The join term as a string if one exists, None otherwise
#[pyfunction]
fn join_term(algebra: &PyBasicAlgebra) -> PyResult<Option<String>> {
    match malcev::join_term(&algebra.inner) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find SD-meet terms for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check
///
/// # Returns
/// List of SD-meet terms if they exist, None otherwise
#[pyfunction]
fn sd_meet_terms(algebra: &PyBasicAlgebra) -> PyResult<Option<Vec<String>>> {
    match malcev::sd_meet_terms(&algebra.inner) {
        Ok(Some(terms)) => {
            let term_strings: Vec<String> = terms.iter().map(|t| format!("{}", t)).collect();
            Ok(Some(term_strings))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find SD terms for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// List of SD terms as strings if they exist, None otherwise
#[pyfunction]
fn sd_terms(algebra: &PyBasicAlgebra) -> PyResult<Option<Vec<String>>> {
    match malcev::sd_terms(&algebra.inner) {
        Ok(Some(terms)) => {
            let term_strings: Vec<String> = terms.iter().map(|t| format!("{}", t)).collect();
            Ok(Some(term_strings))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find the Markovic-McKenzie-Siggers-Taylor term for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// The MMST term as a string if one exists, None otherwise
#[pyfunction]
fn markovic_mckenzie_siggers_taylor_term(algebra: &PyBasicAlgebra) -> PyResult<Option<String>> {
    match malcev::markovic_mckenzie_siggers_taylor_term(&algebra.inner) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a weak 3-edge term for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check
///
/// # Returns
/// The weak 3-edge term if one exists, None otherwise
#[pyfunction]
fn weak_3_edge_term(algebra: &PyBasicAlgebra) -> PyResult<Option<String>> {
    match malcev::weak_3_edge_term(&algebra.inner) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Test if an idempotent algebra is congruence distributive.
///
/// # Arguments
/// * `algebra` - The idempotent algebra to check
///
/// # Returns
/// True if the algebra is congruence distributive, False otherwise
#[pyfunction]
fn is_congruence_dist_idempotent(algebra: &PyBasicAlgebra) -> PyResult<bool> {
    match malcev::is_congruence_dist_idempotent(&algebra.inner) {
        Ok(result) => Ok(result),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Test if an idempotent algebra is congruence modular.
///
/// # Arguments
/// * `algebra` - The idempotent algebra to check
///
/// # Returns
/// True if the algebra is congruence modular, False otherwise
#[pyfunction]
fn is_congruence_modular_idempotent(algebra: &PyBasicAlgebra) -> PyResult<bool> {
    match malcev::is_congruence_modular_idempotent(&algebra.inner) {
        Ok(result) => Ok(result),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Test if the variety generated by the algebra is congruence modular.
///
/// # Arguments
/// * `algebra` - The algebra to check
///
/// # Returns
/// True if the variety is congruence modular, False otherwise
#[pyfunction]
fn congruence_modular_variety(algebra: &PyBasicAlgebra) -> PyResult<bool> {
    match malcev::congruence_modular_variety(&algebra.inner) {
        Ok(result) => Ok(result),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Compute the Jonsson level of an algebra.
///
/// # Arguments
/// * `algebra` - The algebra (BasicAlgebra)
///
/// # Returns
/// The Jonsson level
#[pyfunction]
fn jonsson_level(algebra: &PyBasicAlgebra) -> PyResult<i32> {
    match malcev::jonsson_level(&algebra.inner) {
        Ok(level) => Ok(level),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Compute the local distributivity level for three elements.
///
/// # Arguments
/// * `a` - First element index
/// * `b` - Second element index
/// * `c` - Third element index
/// * `algebra` - The algebra
///
/// # Returns
/// The local distributivity level, or -1 if (a,c) is not in the join
#[pyfunction]
fn local_distributivity_level(a: usize, b: usize, c: usize, algebra: &PyBasicAlgebra) -> PyResult<i32> {
    match malcev::local_distributivity_level(a, b, c, &algebra.inner) {
        Ok(level) => Ok(level),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a Day quadruple in the square of the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check
///
/// # Returns
/// A tuple (x0, x1, y0, y1) if a Day quadruple is found, None otherwise
#[pyfunction]
fn find_day_quadruple_in_square(algebra: &PyBasicAlgebra) -> PyResult<Option<Vec<usize>>> {
    match malcev::find_day_quadruple_in_square(&algebra.inner) {
        Ok(Some(coords)) => Ok(Some(coords)),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a witness for SD-meet failure in an idempotent algebra.
///
/// # Arguments
/// * `algebra` - The idempotent algebra to check
///
/// # Returns
/// A tuple [x, y] if a witness is found, None otherwise
#[pyfunction]
fn sd_meet_idempotent(algebra: &PyBasicAlgebra) -> PyResult<Option<Vec<usize>>> {
    match malcev::sd_meet_idempotent(&algebra.inner) {
        Ok(Some(coords)) => Ok(Some(coords)),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Check if a, b, c, d form a Day quadruple in the algebra.
///
/// Note: This is a lower-level function that requires working with congruence lattices.
/// Most users should use `find_day_quadruple_in_square` or `is_congruence_modular_idempotent` instead.
///
/// # Arguments
/// * `_a`, `_b`, `_c`, `_d` - Four element indices
/// * `_algebra` - The algebra
///
/// # Returns
/// True if a Day quadruple exists, False otherwise
#[pyfunction]
fn day_quadruple(_a: usize, _b: usize, _c: usize, _d: usize, _algebra: PyObject) -> PyResult<bool> {
    Err(PyValueError::new_err("Day quadruple test requires congruence lattice; use find_day_quadruple_in_square instead"))
}

/// Test if the algebra admits a cyclic term of the given arity.
///
/// This implements an algorithm of Valeriote and Willard for testing if
/// the idempotent algebra has a cyclic term of a given arity.
///
/// # Arguments
/// * `algebra` - The algebra (must be idempotent)
/// * `arity` - The arity of the cyclic term (must be at least 2)
///
/// # Returns
/// True if a cyclic term exists, False otherwise
#[pyfunction]
fn cyclic_term_idempotent(algebra: &PyBasicAlgebra, arity: usize) -> PyResult<bool> {
    match malcev::cyclic_term_idempotent(&algebra.inner, arity) {
        Ok(result) => Ok(result),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find primality terms for the algebra.
///
/// This gives unary terms evaluating to the characteristic functions of the one element
/// subsets of alg; a term which applied to these unit vectors gives the identity function;
/// and a binary term giving a semilattice operation on {0, 1}.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// List of primality terms as strings if they exist, None otherwise
#[pyfunction]
fn primality_terms(algebra: &PyBasicAlgebra) -> PyResult<Option<Vec<String>>> {
    match malcev::primality_terms(&algebra.inner) {
        Ok(Some(terms)) => {
            let term_strings: Vec<String> = terms.iter().map(|t| format!("{}", t)).collect();
            Ok(Some(term_strings))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a k-edge term for the algebra.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
/// * `k` - The parameter k (edge term will have arity k+1)
///
/// # Returns
/// The k-edge term as a string if one exists, None otherwise
#[pyfunction]
fn fixed_k_edge_term(algebra: &PyBasicAlgebra, k: usize) -> PyResult<Option<String>> {
    match malcev::fixed_k_edge_term(&algebra.inner, k) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Test if an algebra has a quasi weak near unanimity (QWNU) term of the given arity.
///
/// # Arguments
/// * `algebra` - The algebra to test (BasicAlgebra)
/// * `arity` - The arity of the QWNU term (must be at least 2)
///
/// # Returns
/// True if the algebra has a QWNU term of the given arity, False otherwise
#[pyfunction]
fn fixed_k_qwnu(algebra: &PyBasicAlgebra, arity: usize) -> PyResult<bool> {
    match malcev::fixed_k_qwnu(&algebra.inner, arity) {
        Ok(result) => Ok(result),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}






