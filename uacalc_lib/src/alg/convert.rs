//! Shared conversion helpers for Jython-facing Python bindings.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::conversion::IntoPyObjectExt;
use uacalc::resource::UaError;

fn ua_err(e: UaError) -> PyErr {
    Python::attach(|py| crate::resource::ua_to_py(e, py))
}
use pyo3::types::{PyAny, PyDict};
use std::collections::HashMap;
use uacalc::alg::op::{IntOperation, Operation};
use uacalc::alg::AlgebraType;
use uacalc::terms::{NonVariableTerm, Term, VariableImp};
use uacalc::util::horner;
use uacalc::util::int_array::IntArray;

use crate::alg::basic_algebra::PyBasicAlgebra;
use crate::alg::op::int_operation::PyIntOperation;
use crate::terms::{PyNonVariableTerm, PyVariableImp};
use crate::util::PyIntArray;

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

/// Java `Map<Variable,IntArray>` as a Python dict of VariableImp → IntArray.
pub fn vars_map_to_py(py: Python<'_>, map: &HashMap<VariableImp, IntArray>) -> PyResult<Py<PyAny>> {
    let dict = PyDict::new(py);
    for (var, ia) in map {
        let key = Py::new(py, PyVariableImp { inner: var.clone() })?;
        let val = Py::new(py, PyIntArray { inner: ia.clone() })?;
        dict.set_item(key, val)?;
    }
    Ok(dict.into_py_any(py)?)
}

/// Wrap a Rust term as a Python VariableImp or NonVariableTerm.
pub fn term_to_py(py: Python<'_>, term: &dyn Term) -> PyResult<Py<PyAny>> {
    if term.isa_variable() {
        let var = PyVariableImp {
            inner: VariableImp::new(&term.to_string()),
        };
        return Ok(Py::new(py, var)?.into_any());
    }
    let sym = term
        .leading_operation_symbol()
        .ok_or_else(|| PyValueError::new_err("non-variable term is missing an operation symbol"))?
        .clone();
    let children = term.get_children().unwrap_or_default();
    let nvt = PyNonVariableTerm {
        inner: NonVariableTerm::new(sym, children),
    };
    Ok(Py::new(py, nvt)?.into_any())
}

/// Reconstruct a table-backed IntOperation so Jython scripts can call intValueAt.
pub fn operation_to_py(py: Python<'_>, op: &dyn Operation) -> PyResult<Py<PyAny>> {
    let symbol = op.symbol().clone();
    let set_size = op.get_set_size();
    if let Some(table) = op.get_table() {
        if let Ok(int_op) = IntOperation::new(symbol.clone(), set_size, table.to_vec()) {
            return Ok(Py::new(py, PyIntOperation { inner: int_op })?.into_any());
        }
    }
    if set_size < 0 {
        return Err(PyValueError::new_err(format!(
            "cannot expose operation {} with unknown set size",
            symbol.name()
        )));
    }
    let arity = op.arity();
    let table_vec = uacalc::resource::build_i32_table_horner(set_size, arity as usize, |args| {
        op.int_value_at(args)
    })
    .map_err(|e| crate::resource::ua_to_py(e, py))?;
    let int_op = IntOperation::new(symbol, set_size, table_vec).map_err(PyValueError::new_err)?;
    Ok(Py::new(py, PyIntOperation { inner: int_op })?.into_any())
}

pub fn operations_to_py(
    py: Python<'_>,
    ops: impl IntoIterator<Item = Box<dyn Operation>>,
) -> PyResult<Vec<Py<PyAny>>> {
    ops.into_iter()
        .map(|op| operation_to_py(py, op.as_ref()))
        .collect()
}

/// Look up an operation by Java `OperationSymbol` (or a name string).
pub fn get_operation_by_symbol(
    py: Python<'_>,
    ops: impl IntoIterator<Item = Box<dyn Operation>>,
    sym: &Bound<'_, PyAny>,
) -> PyResult<Option<Py<PyAny>>> {
    let name = if let Ok(s) = sym.extract::<String>() {
        s
    } else if let Ok(n) = sym.call_method0("name") {
        n.extract::<String>()?
    } else {
        return Ok(None);
    };
    let arity = if let Ok(a) = sym.call_method0("arity") {
        a.extract::<i32>().ok()
    } else {
        None
    };
    for op in ops {
        if op.symbol().name() == name && arity.map(|a| op.arity() == a).unwrap_or(true) {
            return Ok(Some(operation_to_py(py, op.as_ref())?));
        }
    }
    Ok(None)
}

/// Materialize operations as a table-backed BasicAlgebra (Java write/read shape).
pub fn ops_to_basic_algebra(
    name: String,
    cardinality: i32,
    ops: impl IntoIterator<Item = Box<dyn Operation>>,
) -> PyResult<PyBasicAlgebra> {
    use std::collections::HashSet;
    if cardinality < 0 {
        return Err(PyValueError::new_err(
            "Cannot convert algebra with unknown cardinality to BasicAlgebra",
        ));
    }
    let universe: HashSet<i32> = (0..cardinality).collect();
    let mut rust_ops: Vec<Box<dyn Operation>> = Vec::new();
    for op in ops {
        uacalc::resource::checkpoint().map_err(ua_err)?;
        let symbol = op.symbol().clone();
        let arity = op.arity();
        let table_vec =
            uacalc::resource::build_i32_table_horner(cardinality, arity as usize, |args| {
                op.int_value_at(args)
            })
            .map_err(ua_err)?;
        let int_op =
            IntOperation::new(symbol, cardinality, table_vec).map_err(PyValueError::new_err)?;
        rust_ops.push(Box::new(int_op));
    }
    Ok(PyBasicAlgebra::from_inner(uacalc::alg::BasicAlgebra::new(
        name, universe, rust_ops,
    )))
}

/// Java `Arrays.binarySearch` encoding: index, or `-(insertion point) - 1`.
pub fn binary_search_i32(sorted: &[i32], key: i32) -> i32 {
    match sorted.binary_search(&key) {
        Ok(i) => i as i32,
        Err(i) => -(i as i32) - 1,
    }
}

pub fn binary_search_usize(sorted: &[usize], key: usize) -> i32 {
    match sorted.binary_search(&key) {
        Ok(i) => i as i32,
        Err(i) => -(i as i32) - 1,
    }
}
