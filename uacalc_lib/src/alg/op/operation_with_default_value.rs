use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyAny;

use super::operation_symbol::PyOperationSymbol;
use super::operation::PyBasicOperation;
use super::int_operation::PyIntOperation;
use uacalc::alg::op::Operation;

/// Python wrapper for OperationWithDefaultValue
#[pyclass]
pub struct PyOperationWithDefaultValue {
    pub(crate) inner: uacalc::alg::op::OperationWithDefaultValue,
}

#[pymethods]
impl PyOperationWithDefaultValue {
    /// Constructor supporting multiple signatures.
    #[new]
    #[pyo3(signature = (name_or_op, arity_or_set_size=None, set_size=None, default_value=-1))]
    fn new(
        name_or_op: &Bound<'_, PyAny>,
        arity_or_set_size: Option<i32>,
        set_size: Option<i32>,
        default_value: i32,
    ) -> PyResult<Self> {
        // From BasicOperation
        if let Ok(basic_op) = name_or_op.extract::<PyRef<PyBasicOperation>>() {
            if let Some(alg_size) = arity_or_set_size {
                match uacalc::alg::op::OperationWithDefaultValue::from_operation_with_size(
                    basic_op.inner.clone(),
                    alg_size,
                ) {
                    Ok(inner) => return Ok(PyOperationWithDefaultValue { inner }),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            } else {
                match uacalc::alg::op::OperationWithDefaultValue::from_operation(basic_op.inner.clone()) {
                    Ok(inner) => return Ok(PyOperationWithDefaultValue { inner }),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            }
        } else if let Ok(op_symbol) = name_or_op.extract::<PyRef<PyOperationSymbol>>() {
            // With symbol and alg size (and optional table not supported yet)
            let alg_size = arity_or_set_size.ok_or_else(|| PyValueError::new_err("alg_size required with symbol"))?;
            match uacalc::alg::op::OperationWithDefaultValue::new_with_symbol_and_default(
                op_symbol.get_inner().clone(),
                alg_size,
                default_value,
            ) {
                Ok(inner) => return Ok(PyOperationWithDefaultValue { inner }),
                Err(e) => return Err(PyValueError::new_err(e)),
            }
        } else if let Ok(name) = name_or_op.extract::<String>() {
            // From name + arity + set_size
            let arity = arity_or_set_size.ok_or_else(|| PyValueError::new_err("arity required when passing name"))?;
            let alg_size = set_size.ok_or_else(|| PyValueError::new_err("set_size required when passing name and arity"))?;
            match uacalc::alg::op::OperationWithDefaultValue::new_with_name(
                &name,
                arity,
                alg_size,
                default_value,
            ) {
                Ok(inner) => return Ok(PyOperationWithDefaultValue { inner }),
                Err(e) => return Err(PyValueError::new_err(e)),
            }
        }

        Err(PyValueError::new_err("Unsupported constructor arguments for OperationWithDefaultValue"))
    }

    /// Alternative constructor: from_operation
    #[staticmethod]
    fn from_operation(op: PyRef<PyBasicOperation>) -> PyResult<Self> {
        match uacalc::alg::op::OperationWithDefaultValue::from_operation(op.inner.clone()) {
            Ok(inner) => Ok(PyOperationWithDefaultValue { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get arity
    fn arity(&self) -> i32 { self.inner.arity() }

    /// Get set size
    fn get_set_size(&self) -> i32 { self.inner.get_set_size() }

    /// Get symbol
    fn symbol(&self) -> PyOperationSymbol { PyOperationSymbol::from_inner(self.inner.symbol().clone()) }

    /// Get default value
    fn get_default_value(&self) -> i32 { self.inner.get_default_value() }

    /// Set default value
    fn set_default_value(&mut self, value: i32) { self.inner.set_default_value(value) }

    /// Whether op is total (no default used)
    fn is_total(&self) -> bool { self.inner.is_total().unwrap_or(false) }

    /// Update random value table
    fn update_random_value_table(&mut self) { self.inner.update_random_value_table() }

    /// Get random value table
    fn get_random_value_table(&mut self) -> Vec<i32> { self.inner.get_random_value_table().to_vec() }

    /// Is idempotent set flag
    fn is_idempotent_set(&self) -> bool { self.inner.is_idempotent_set() }

    /// Set idempotent flag
    fn set_idempotent(&mut self, idempotent: bool) { self.inner.set_idempotent(idempotent) }

    /// Make idempotent (mutating underlying table/defaults as needed)
    fn make_idempotent(&mut self) { self.inner.make_idempotent() }

    /// Is diagonal at position
    fn is_diagonal(&self, i: i32, j: i32) -> bool { self.inner.is_diagonal(i as usize, j as usize) }

    /// Make internal table
    fn make_table(&mut self) { let _ = self.inner.make_table(); }

    /// Get total table if exists
    fn get_total_table(&self) -> Option<Vec<i32>> { self.inner.get_total_table().map(|s| s.to_vec()) }

    /// Make an ordinary IntOperation if possible
    fn make_ordinary_operation(&self) -> Option<PyIntOperation> {
        self.inner.make_ordinary_operation().map(|op| PyIntOperation { inner: op })
    }

    /// Static: convert list to ordinary ops
    #[staticmethod]
    fn make_ordinary(ops: Vec<PyRef<PyOperationWithDefaultValue>>) -> Vec<PyIntOperation> {
        let rust_ops: Vec<_> = ops.into_iter().map(|op| op.inner.clone()).collect();
        uacalc::alg::op::OperationWithDefaultValue::make_ordinary_list(rust_ops)
            .into_iter()
            .map(|op| PyIntOperation { inner: op })
            .collect()
    }

    /// Evaluate int value at args (list)
    fn int_value_at(&self, args: Vec<i32>) -> i32 { self.inner.int_value_at(&args).unwrap_or(self.inner.get_default_value()) }

    /// Evaluate value at args (list)
    fn value_at(&self, args: Vec<i32>) -> i32 { self.inner.value_at(&args).unwrap_or(self.inner.get_default_value()) }

    fn __eq__(&self, other: &PyOperationWithDefaultValue) -> bool { self.inner == other.inner }

    fn __repr__(&self) -> String {
        format!(
            "OperationWithDefaultValue(name='{}', arity={}, set_size={}, default_value={})",
            self.inner.symbol().name(),
            self.inner.arity(),
            self.inner.get_set_size(),
            self.inner.get_default_value()
        )
    }
}


