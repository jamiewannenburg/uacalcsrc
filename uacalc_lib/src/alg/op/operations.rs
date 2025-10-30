//! Python wrapper for Operations utility class

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyAny;

use super::operation_symbol::PyOperationSymbol;
use super::operation::PyBasicOperation;
use super::int_operation::PyIntOperation;

/// Python wrapper for Operations utility class
#[pyclass]
pub struct PyOperations;

#[pymethods]
impl PyOperations {
    /// Check if a unary operation commutes with another operation.
    #[staticmethod]
    fn commutes(unary_op: &PyAny, op: &PyAny) -> PyResult<bool> {
        if let Ok(u) = unary_op.extract::<PyRef<PyBasicOperation>>() {
            if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
                return uacalc::alg::op::ops::commutes_unary(&u.inner, &o.inner).map_err(PyValueError::new_err);
            } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
                return uacalc::alg::op::ops::commutes_unary(&u.inner, &o.inner).map_err(PyValueError::new_err);
            }
        } else if let Ok(u) = unary_op.extract::<PyRef<PyIntOperation>>() {
            if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
                return uacalc::alg::op::ops::commutes_unary(&u.inner, &o.inner).map_err(PyValueError::new_err);
            } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
                return uacalc::alg::op::ops::commutes_unary(&u.inner, &o.inner).map_err(PyValueError::new_err);
            }
        }
        Err(PyValueError::new_err("Unsupported operation types for commutes"))
    }

    /// Check if an operation is total.
    #[staticmethod]
    fn is_total(op: &PyAny) -> PyResult<bool> {
        if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
            return uacalc::alg::op::ops::is_total(&o.inner).map_err(PyValueError::new_err);
        } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
            return uacalc::alg::op::ops::is_total(&o.inner).map_err(PyValueError::new_err);
        }
        Err(PyValueError::new_err("Unsupported operation type"))
    }

    /// Check if an operation is idempotent.
    #[staticmethod]
    fn is_idempotent(operation: &PyAny) -> PyResult<bool> {
        if let Ok(basic_op) = operation.extract::<PyRef<PyBasicOperation>>() {
            return uacalc::alg::op::ops::is_idempotent(&basic_op.inner).map_err(PyValueError::new_err);
        } else if let Ok(int_op) = operation.extract::<PyRef<PyIntOperation>>() {
            return uacalc::alg::op::ops::is_idempotent(&int_op.inner).map_err(PyValueError::new_err);
        }
        Err(PyValueError::new_err("Unsupported operation type"))
    }

    /// Check if an operation is commutative.
    #[staticmethod]
    fn is_commutative(operation: &PyAny) -> PyResult<bool> {
        if let Ok(basic_op) = operation.extract::<PyRef<PyBasicOperation>>() {
            return uacalc::alg::op::ops::is_commutative(&basic_op.inner).map_err(PyValueError::new_err);
        } else if let Ok(int_op) = operation.extract::<PyRef<PyIntOperation>>() {
            return uacalc::alg::op::ops::is_commutative(&int_op.inner).map_err(PyValueError::new_err);
        }
        Err(PyValueError::new_err("Unsupported operation type"))
    }

    /// Check if an operation is totally symmetric.
    #[staticmethod]
    fn is_totally_symmetric(op: &PyAny) -> PyResult<bool> {
        if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
            return uacalc::alg::op::ops::is_totally_symmetric(&o.inner).map_err(PyValueError::new_err);
        } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
            return uacalc::alg::op::ops::is_totally_symmetric(&o.inner).map_err(PyValueError::new_err);
        }
        Err(PyValueError::new_err("Unsupported operation type"))
    }

    /// Check if an operation is associative.
    #[staticmethod]
    fn is_associative(op: &PyAny) -> PyResult<bool> {
        if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
            return uacalc::alg::op::ops::is_associative(&o.inner).map_err(PyValueError::new_err);
        } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
            return uacalc::alg::op::ops::is_associative(&o.inner).map_err(PyValueError::new_err);
        }
        Err(PyValueError::new_err("Unsupported operation type"))
    }

    /// Check if an operation is a Maltsev operation.
    #[staticmethod]
    fn is_maltsev(op: &PyAny) -> PyResult<bool> {
        if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
            return uacalc::alg::op::ops::is_maltsev(&o.inner).map_err(PyValueError::new_err);
        } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
            return uacalc::alg::op::ops::is_maltsev(&o.inner).map_err(PyValueError::new_err);
        }
        Err(PyValueError::new_err("Unsupported operation type"))
    }

    /// Find the first difference between two operations.
    #[staticmethod]
    fn find_difference(op1: &PyAny, op2: &PyAny) -> PyResult<Option<Vec<i32>>> {
        if let Ok(basic_op1) = op1.extract::<PyRef<PyBasicOperation>>() {
            if let Ok(basic_op2) = op2.extract::<PyRef<PyBasicOperation>>() {
                return uacalc::alg::op::ops::find_difference(&basic_op1.inner, &basic_op2.inner)
                    .map_err(PyValueError::new_err);
            } else if let Ok(int_op2) = op2.extract::<PyRef<PyIntOperation>>() {
                return uacalc::alg::op::ops::find_difference(&basic_op1.inner, &int_op2.inner)
                    .map_err(PyValueError::new_err);
            }
        } else if let Ok(int_op1) = op1.extract::<PyRef<PyIntOperation>>() {
            if let Ok(basic_op2) = op2.extract::<PyRef<PyBasicOperation>>() {
                return uacalc::alg::op::ops::find_difference(&int_op1.inner, &basic_op2.inner)
                    .map_err(PyValueError::new_err);
            } else if let Ok(int_op2) = op2.extract::<PyRef<PyIntOperation>>() {
                return uacalc::alg::op::ops::find_difference(&int_op1.inner, &int_op2.inner)
                    .map_err(PyValueError::new_err);
            }
        }
        Err(PyValueError::new_err("Unsupported operation type combination"))
    }

    /// Check if two operations have equal values.
    #[staticmethod]
    fn equal_values(op1: &PyAny, op2: &PyAny) -> PyResult<bool> {
        if let Ok(basic_op1) = op1.extract::<PyRef<PyBasicOperation>>() {
            if let Ok(basic_op2) = op2.extract::<PyRef<PyBasicOperation>>() {
                return uacalc::alg::op::ops::equal_values(&basic_op1.inner, &basic_op2.inner)
                    .map_err(PyValueError::new_err);
            } else if let Ok(int_op2) = op2.extract::<PyRef<PyIntOperation>>() {
                return uacalc::alg::op::ops::equal_values(&basic_op1.inner, &int_op2.inner)
                    .map_err(PyValueError::new_err);
            }
        } else if let Ok(int_op1) = op1.extract::<PyRef<PyIntOperation>>() {
            if let Ok(basic_op2) = op2.extract::<PyRef<PyBasicOperation>>() {
                return uacalc::alg::op::ops::equal_values(&int_op1.inner, &basic_op2.inner)
                    .map_err(PyValueError::new_err);
            } else if let Ok(int_op2) = op2.extract::<PyRef<PyIntOperation>>() {
                return uacalc::alg::op::ops::equal_values(&int_op1.inner, &int_op2.inner)
                    .map_err(PyValueError::new_err);
            }
        }
        Err(PyValueError::new_err("Unsupported operation type combination"))
    }

    // -------------------- Factory methods --------------------

    /// Overloaded constructor for IntOperation from symbol or name.
    #[staticmethod]
    #[pyo3(signature = (a, b, c, d=None))]
    fn make_int_operation(a: &PyAny, b: i32, c: &PyAny, d: Option<&PyAny>) -> PyResult<PyIntOperation> {
        // Case 1: (symbol, set_size, table)
        if let Ok(sym) = a.extract::<PyRef<PyOperationSymbol>>() {
            let set_size = b;
            let table: Vec<i32> = c.extract().map_err(PyValueError::new_err)?;
            match uacalc::alg::op::ops::make_int_operation(sym.get_inner().clone(), set_size, table) {
                Ok(op) => {
                    let sy = op.symbol().clone();
                    let ss = op.get_set_size();
                    let tb = op.get_table().unwrap().to_vec();
                    let inner = uacalc::alg::op::IntOperation::new(sy, ss, tb).map_err(PyValueError::new_err)?;
                    return Ok(PyIntOperation { inner })
                },
                Err(e) => return Err(PyValueError::new_err(e)),
            }
        }
        // Case 2: (name: str, arity, set_size, table)
        if let Ok(name) = a.extract::<String>() {
            let arity = b;
            let set_size: i32 = c.extract().map_err(PyValueError::new_err)?;
            let table_any = d.ok_or_else(|| PyValueError::new_err("table required"))?;
            let table: Vec<i32> = table_any.extract().map_err(PyValueError::new_err)?;
            match uacalc::alg::op::ops::make_int_operation_str(&name, arity, set_size, table) {
                Ok(op) => {
                    let sy = op.symbol().clone();
                    let ss = op.get_set_size();
                    let tb = op.get_table().unwrap().to_vec();
                    let inner = uacalc::alg::op::IntOperation::new(sy, ss, tb).map_err(PyValueError::new_err)?;
                    return Ok(PyIntOperation { inner })
                },
                Err(e) => return Err(PyValueError::new_err(e)),
            }
        }
        Err(PyValueError::new_err("Expected OperationSymbol or name string"))
    }

    /// Construct an operation from a string symbol and table.
    #[staticmethod]
    fn make_int_operation_str(name: &str, arity: i32, set_size: i32, table: Vec<i32>) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_int_operation_str(name, arity, set_size, table) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Make a binary IntOperation from a flattened 1D table.
    #[staticmethod]
    fn make_binary_int_operation(symbol: &PyOperationSymbol, set_size: i32, table_1d: Vec<i32>) -> PyResult<PyIntOperation> {
        // Convert flattened 1D into 2D for Rust API
        let mut table2d: Vec<Vec<i32>> = Vec::with_capacity(set_size as usize);
        let mut k = 0usize;
        for _ in 0..set_size {
            let mut row = Vec::with_capacity(set_size as usize);
            for _ in 0..set_size { row.push(if k < table_1d.len() { table_1d[k] } else { 0 }); k += 1; }
            table2d.push(row);
        }
        match uacalc::alg::op::ops::make_binary_int_operation(symbol.get_inner().clone(), set_size, table2d) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Make a constant IntOperation with implicit symbol.
    #[staticmethod]
    fn make_constant_int_operation(set_size: i32, elt: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_constant_int_operation(set_size, elt) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Make a constant IntOperation with a prefix and value.
    #[staticmethod]
    fn make_constant_int_operation_with_prefix(prefix: &str, set_size: i32, elt: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_constant_int_operation_with_prefix(prefix, set_size, elt) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Make all constant IntOperations for a set size.
    #[staticmethod]
    fn make_constant_int_operations(set_size: i32) -> Vec<PyIntOperation> {
        // Build via repeated make_constant_int_operation to avoid crate visibility issues
        let mut out = Vec::new();
        for v in 0..set_size {
            if let Ok(op) = Self::make_constant_int_operation(set_size, v) { out.push(op); }
        }
        out
    }

    /// Make a transposition IntOperation.
    #[staticmethod]
    fn make_transposition(alg_size: i32, i: i32, j: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_transposition(alg_size, i, j) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().map(|t| t.to_vec()).unwrap_or_else(|| {
                    let arity = op.arity() as usize;
                    let total = (set_size as usize).pow(arity as u32);
                    let mut vt = Vec::with_capacity(total);
                    for k in 0..total { let args = uacalc::util::horner::horner_inv_same_size(k as i32, set_size, arity); vt.push(op.int_value_at(&args).unwrap()); }
                    vt
                });
                let int_op = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner: int_op })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Make a full cycle IntOperation.
    #[staticmethod]
    fn make_full_cycle(alg_size: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_full_cycle(alg_size) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().map(|t| t.to_vec()).unwrap_or_else(|| {
                    let arity = op.arity() as usize;
                    let total = (set_size as usize).pow(arity as u32);
                    let mut vt = Vec::with_capacity(total);
                    for k in 0..total { let args = uacalc::util::horner::horner_inv_same_size(k as i32, set_size, arity); vt.push(op.int_value_at(&args).unwrap()); }
                    vt
                });
                let int_op = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner: int_op })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
}


