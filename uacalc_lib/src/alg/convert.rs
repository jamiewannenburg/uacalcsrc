//! Shared conversion helpers for Jython-facing Python bindings.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyAny;
use uacalc::alg::op::{IntOperation, Operation};
use uacalc::alg::AlgebraType;
use uacalc::terms::{NonVariableTerm, Term, VariableImp};
use uacalc::util::horner;

use crate::alg::op::int_operation::PyIntOperation;
use crate::terms::{PyNonVariableTerm, PyVariableImp};

/// Java `SmallAlgebra.AlgebraType` enum names (e.g. `FREE`, `REDUCT`).
pub fn algebra_type_java_name(t: AlgebraType) -> String {
    match t {
        AlgebraType::Basic => "BASIC".to_string(),
        AlgebraType::BasicLattice => "BASIC_LATTICE".to_string(),
        AlgebraType::Quotient => "QUOTIENT".to_string(),
        AlgebraType::Subalgebra => "SUBALGEBRA".to_string(),
        AlgebraType::Product => "PRODUCT".to_string(),
        AlgebraType::Power => "POWER".to_string(),
        AlgebraType::MatrixPower => "MATRIX_POWER".to_string(),
        AlgebraType::Reduct => "REDUCT".to_string(),
        AlgebraType::Subproduct => "SUBPRODUCT".to_string(),
        AlgebraType::Free => "FREE".to_string(),
        AlgebraType::PolinLike => "POLIN_LIKE".to_string(),
        AlgebraType::UnaryTermsMonoid => "UNARY_TERMS_MONOID".to_string(),
        AlgebraType::FiniteField => "FINITE_FIELD".to_string(),
    }
}

/// Extract a Rust `Term` from a Python VariableImp, NonVariableTerm, or str.
pub fn py_to_term(item: &Bound<'_, PyAny>) -> PyResult<Box<dyn Term>> {
    if let Ok(var) = item.extract::<PyRef<PyVariableImp>>() {
        return Ok(Box::new(var.inner.clone()));
    }
    if let Ok(nvt) = item.extract::<PyRef<PyNonVariableTerm>>() {
        return Ok(nvt.inner.clone_box());
    }
    if let Ok(name) = item.extract::<String>() {
        return Ok(Box::new(VariableImp::new(&name)));
    }
    Err(PyValueError::new_err(
        "term list items must be VariableImp, NonVariableTerm, or str",
    ))
}

/// Wrap a Rust term as a Python VariableImp or NonVariableTerm.
pub fn term_to_py(py: Python<'_>, term: &dyn Term) -> PyResult<PyObject> {
    if term.isa_variable() {
        let var = PyVariableImp {
            inner: VariableImp::new(&term.to_string()),
        };
        return Ok(Py::new(py, var)?.to_object(py));
    }
    let sym = term
        .leading_operation_symbol()
        .ok_or_else(|| {
            PyValueError::new_err("non-variable term is missing an operation symbol")
        })?
        .clone();
    let children = term.get_children().unwrap_or_default();
    let nvt = PyNonVariableTerm {
        inner: NonVariableTerm::new(sym, children),
    };
    Ok(Py::new(py, nvt)?.to_object(py))
}

/// Reconstruct a table-backed IntOperation so Jython scripts can call intValueAt.
pub fn operation_to_py(py: Python<'_>, op: &dyn Operation) -> PyResult<PyObject> {
    let symbol = op.symbol().clone();
    let set_size = op.get_set_size();
    if let Some(table) = op.get_table() {
        if let Ok(int_op) = IntOperation::new(symbol.clone(), set_size, table.to_vec()) {
            return Ok(Py::new(py, PyIntOperation { inner: int_op })?.to_object(py));
        }
    }
    if set_size < 0 {
        return Err(PyValueError::new_err(format!(
            "cannot expose operation {} with unknown set size",
            symbol.name()
        )));
    }
    let arity = op.arity();
    let table_size = if arity == 0 {
        1usize
    } else {
        (set_size as usize)
            .checked_pow(arity as u32)
            .ok_or_else(|| {
                PyValueError::new_err(format!(
                    "operation {} table is too large to materialize",
                    symbol.name()
                ))
            })?
    };
    let mut table_vec = Vec::with_capacity(table_size);
    for i in 0..table_size {
        let args = if arity == 0 {
            Vec::new()
        } else {
            horner::horner_inv_same_size_safe(i as i32, set_size, arity as usize)
                .map_err(PyValueError::new_err)?
        };
        table_vec.push(
            op.int_value_at(&args)
                .map_err(|e| PyValueError::new_err(e))?,
        );
    }
    let int_op = IntOperation::new(symbol, set_size, table_vec).map_err(PyValueError::new_err)?;
    Ok(Py::new(py, PyIntOperation { inner: int_op })?.to_object(py))
}

pub fn operations_to_py(
    py: Python<'_>,
    ops: impl IntoIterator<Item = Box<dyn Operation>>,
) -> PyResult<Vec<PyObject>> {
    ops.into_iter()
        .map(|op| operation_to_py(py, op.as_ref()))
        .collect()
}
