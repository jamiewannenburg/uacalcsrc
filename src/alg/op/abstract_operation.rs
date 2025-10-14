//! AbstractOperation implementation

use crate::error::{Result, UaCalcError};
use super::{Operation, OperationSymbol, Operations};
use std::any::Any;
use std::cmp::Ordering;
use std::fmt::{self, Display};
use std::hash::{Hash, Hasher};
use pyo3::prelude::*;

/// Abstract operation providing default implementations for most Operation methods
/// 
/// This corresponds to the Java AbstractOperation class and provides
/// base functionality that concrete operations can build upon.
#[pyclass(name = "AbstractOperation")]
#[derive(Debug, Clone)]
pub struct AbstractOperation {
    symbol: OperationSymbol,
    alg_size: i32,
    value_table: Option<Vec<i32>>,
}

impl AbstractOperation {
    /// Create a new abstract operation with a name, arity, and algebra size
    pub fn new(name: String, arity: i32, alg_size: i32) -> Result<Self> {
        let symbol = OperationSymbol::new(name, arity)?;
        Self::new_with_symbol(symbol, alg_size)
    }

    /// Create a new abstract operation with an operation symbol and algebra size
    pub fn new_with_symbol(symbol: OperationSymbol, alg_size: i32) -> Result<Self> {
        if alg_size <= 0 {
            return Err(UaCalcError::InvalidSetSize(alg_size));
        }

        Ok(AbstractOperation {
            symbol,
            alg_size,
            value_table: None,
        })
    }

    /// Compute the Horner encoding for a given set of arguments
    pub fn horner_encode(&self, args: &[i32]) -> Result<i32> {
        if args.len() != self.arity() as usize {
            return Err(UaCalcError::InvalidArgumentCount {
                expected: self.arity() as usize,
                actual: args.len(),
            });
        }

        let mut result = 0;
        let base = self.alg_size;
        
        for &arg in args {
            if arg < 0 || arg >= base {
                return Err(UaCalcError::InvalidArgument(format!(
                    "Argument {} out of range [0, {})", arg, base
                )));
            }
            result = result * base + arg;
        }

        Ok(result)
    }

    /// Decode Horner encoding back to arguments
    pub fn horner_decode(&self, encoded: i32) -> Result<Vec<i32>> {
        let arity = self.arity() as usize;
        let mut args = vec![0; arity];
        let mut remaining = encoded;
        let base = self.alg_size;

        for i in (0..arity).rev() {
            args[i] = remaining % base;
            remaining /= base;
        }

        if remaining != 0 {
            return Err(UaCalcError::InvalidArgument(format!(
                "Invalid Horner encoding: {}", encoded
            )));
        }

        Ok(args)
    }
}

impl Operation for AbstractOperation {
    fn arity(&self) -> i32 {
        self.symbol.arity()
    }

    fn get_set_size(&self) -> i32 {
        self.alg_size
    }

    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }

    fn value_at_elements(&self, _args: &[Box<dyn Any>]) -> Result<Box<dyn Any>> {
        Err(UaCalcError::UnsupportedOperation(
            "value_at_elements not implemented for AbstractOperation".to_string()
        ))
    }

    fn value_at_arrays(&self, _args: &[&[i32]]) -> Result<Vec<i32>> {
        Err(UaCalcError::UnsupportedOperation(
            "value_at_arrays not implemented for AbstractOperation".to_string()
        ))
    }

    fn int_value_at(&self, _args: &[i32]) -> Result<i32> {
        Err(UaCalcError::UnsupportedOperation(
            "int_value_at not implemented for AbstractOperation".to_string()
        ))
    }

    fn int_value_at_horner(&self, arg: i32) -> Result<i32> {
        let args = self.horner_decode(arg)?;
        self.int_value_at(&args)
    }

    fn make_table(&mut self) -> Result<()> {
        // Default implementation does nothing
        // Subclasses can override this
        Ok(())
    }

    fn get_table(&self) -> Option<&[i32]> {
        self.value_table.as_deref()
    }

    fn get_table_force(&mut self, make_table: bool) -> Result<&[i32]> {
        if make_table && self.value_table.is_none() {
            self.make_table()?;
        }
        
        match &self.value_table {
            Some(table) => Ok(table),
            None => Err(UaCalcError::TableNotAvailable),
        }
    }

    fn is_table_based(&self) -> bool {
        false
    }

    fn is_idempotent(&self) -> Result<bool> {
        let n = self.get_set_size();
        let arity = self.arity() as usize;
        let mut args = vec![0; arity];

        for i in 0..n {
            // Set all arguments to the same value
            for j in 0..arity {
                args[j] = i;
            }
            if self.int_value_at(&args)? != i {
                return Ok(false);
            }
        }

        Ok(true)
    }

    fn is_associative(&self) -> Result<bool> {
        Operations::is_associative(self)
    }

    fn is_commutative(&self) -> Result<bool> {
        Operations::is_commutative(self)
    }

    fn is_totally_symmetric(&self) -> Result<bool> {
        Operations::is_totally_symmetric(self)
    }

    fn is_maltsev(&self) -> Result<bool> {
        Operations::is_maltsev(self)
    }

    fn is_total(&self) -> Result<bool> {
        Operations::is_total(self)
    }
}

impl Display for AbstractOperation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.symbol)
    }
}

impl PartialEq for AbstractOperation {
    fn eq(&self, other: &Self) -> bool {
        self.symbol == other.symbol && self.alg_size == other.alg_size
    }
}

impl Eq for AbstractOperation {}

impl Hash for AbstractOperation {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.symbol.hash(state);
        self.alg_size.hash(state);
    }
}

impl PartialOrd for AbstractOperation {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for AbstractOperation {
    fn cmp(&self, other: &Self) -> Ordering {
        self.symbol.cmp(&other.symbol)
    }
}

/// Python wrapper methods for AbstractOperation
#[pymethods]
impl AbstractOperation {
    #[new]
    fn py_new(name: String, arity: i32, alg_size: i32) -> PyResult<Self> {
        Self::new(name, arity, alg_size).map_err(|e| e.into())
    }

    #[getter]
    fn get_arity(&self) -> i32 {
        self.arity()
    }

    #[getter]
    fn get_set_size_py(&self) -> i32 {
        self.get_set_size()
    }

    #[getter]
    fn get_symbol(&self) -> OperationSymbol {
        self.symbol().clone()
    }

    fn is_table_based_py(&self) -> bool {
        self.is_table_based()
    }

    fn is_idempotent_py(&self) -> PyResult<bool> {
        self.is_idempotent().map_err(|e| e.into())
    }

    fn is_associative_py(&self) -> PyResult<bool> {
        self.is_associative().map_err(|e| e.into())
    }

    fn is_commutative_py(&self) -> PyResult<bool> {
        self.is_commutative().map_err(|e| e.into())
    }

    fn is_totally_symmetric_py(&self) -> PyResult<bool> {
        self.is_totally_symmetric().map_err(|e| e.into())
    }

    fn is_maltsev_py(&self) -> PyResult<bool> {
        self.is_maltsev().map_err(|e| e.into())
    }

    fn is_total_py(&self) -> PyResult<bool> {
        self.is_total().map_err(|e| e.into())
    }

    fn __str__(&self) -> String {
        self.to_string()
    }

    fn __repr__(&self) -> String {
        format!("AbstractOperation('{}', arity={}, set_size={})", 
                self.symbol.name(), self.arity(), self.get_set_size())
    }

    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        let mut hasher = DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish()
    }

    fn __eq__(&self, other: &Self) -> bool {
        self == other
    }

    fn __lt__(&self, other: &Self) -> bool {
        self < other
    }

    fn __le__(&self, other: &Self) -> bool {
        self <= other
    }

    fn __gt__(&self, other: &Self) -> bool {
        self > other
    }

    fn __ge__(&self, other: &Self) -> bool {
        self >= other
    }
}

// Create a type alias for the Python class
pub type PyAbstractOperation = AbstractOperation;