//! IntOperation implementation for table-based operations

use crate::error::{Result, UaCalcError};
use super::{AbstractOperation, Operation, OperationSymbol, Operations};
use std::any::Any;
use std::cmp::Ordering;
use std::fmt::{self, Display};
use std::hash::{Hash, Hasher};
use pyo3::prelude::*;

/// Table-based integer operation implementation
/// 
/// This provides a concrete implementation of Operation that stores
/// operation results in a table for fast lookup.
#[pyclass(name = "IntOperation")]
#[derive(Debug, Clone)]
pub struct IntOperation {
    base: AbstractOperation,
    operation_table: Vec<i32>,
}

impl IntOperation {
    /// Create a new integer operation with a table
    pub fn new(symbol: OperationSymbol, table: Vec<i32>, set_size: i32) -> Result<Self> {
        if set_size <= 0 {
            return Err(UaCalcError::InvalidSetSize(set_size));
        }

        let arity = symbol.arity();
        let expected_size = Self::calculate_table_size(arity, set_size)?;
        
        if table.len() != expected_size {
            return Err(UaCalcError::InvalidArgument(format!(
                "Table size mismatch: expected {}, got {}", expected_size, table.len()
            )));
        }

        // Validate table values are in range
        for &value in &table {
            if value < 0 || value >= set_size {
                return Err(UaCalcError::InvalidArgument(format!(
                    "Table value {} out of range [0, {})", value, set_size
                )));
            }
        }

        let base = AbstractOperation::new_with_symbol(symbol, set_size)?;

        Ok(IntOperation {
            base,
            operation_table: table,
        })
    }

    /// Create a new integer operation with name, arity, table, and set size
    pub fn new_with_name(name: String, arity: i32, table: Vec<i32>, set_size: i32) -> Result<Self> {
        let symbol = OperationSymbol::new(name, arity)?;
        Self::new(symbol, table, set_size)
    }

    /// Calculate the expected table size for given arity and set size
    fn calculate_table_size(arity: i32, set_size: i32) -> Result<usize> {
        if arity < 0 {
            return Err(UaCalcError::InvalidArity(arity));
        }
        if set_size <= 0 {
            return Err(UaCalcError::InvalidSetSize(set_size));
        }

        let mut size = 1usize;
        for _ in 0..arity {
            size = size.checked_mul(set_size as usize)
                .ok_or_else(|| UaCalcError::InvalidArgument("Table size overflow".to_string()))?;
        }

        Ok(size)
    }

    /// Get the operation table
    pub fn table(&self) -> &[i32] {
        &self.operation_table
    }

    /// Create a binary operation table for testing
    pub fn create_binary_operation(name: String, set_size: i32, f: impl Fn(i32, i32) -> i32) -> Result<Self> {
        let table_size = (set_size * set_size) as usize;
        let mut table = Vec::with_capacity(table_size);

        for a in 0..set_size {
            for b in 0..set_size {
                let result = f(a, b);
                if result < 0 || result >= set_size {
                    return Err(UaCalcError::InvalidArgument(format!(
                        "Function result {} out of range [0, {})", result, set_size
                    )));
                }
                table.push(result);
            }
        }

        Self::new_with_name(name, 2, table, set_size)
    }

    /// Create a unary operation table for testing
    pub fn create_unary_operation(name: String, set_size: i32, f: impl Fn(i32) -> i32) -> Result<Self> {
        let mut table = Vec::with_capacity(set_size as usize);

        for a in 0..set_size {
            let result = f(a);
            if result < 0 || result >= set_size {
                return Err(UaCalcError::InvalidArgument(format!(
                    "Function result {} out of range [0, {})", result, set_size
                )));
            }
            table.push(result);
        }

        Self::new_with_name(name, 1, table, set_size)
    }
}

impl Operation for IntOperation {
    fn arity(&self) -> i32 {
        self.base.arity()
    }

    fn get_set_size(&self) -> i32 {
        self.base.get_set_size()
    }

    fn symbol(&self) -> &OperationSymbol {
        self.base.symbol()
    }

    fn value_at_elements(&self, _args: &[Box<dyn Any>]) -> Result<Box<dyn Any>> {
        Err(UaCalcError::UnsupportedOperation(
            "value_at_elements not implemented for IntOperation".to_string()
        ))
    }

    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>> {
        if args.is_empty() {
            return Ok(Vec::new());
        }

        let result_len = args[0].len();
        let mut result = Vec::with_capacity(result_len);

        for i in 0..result_len {
            let mut op_args = Vec::with_capacity(args.len());
            for arg_array in args {
                if i >= arg_array.len() {
                    return Err(UaCalcError::InvalidArgument(
                        "Inconsistent array lengths".to_string()
                    ));
                }
                op_args.push(arg_array[i]);
            }
            result.push(self.int_value_at(&op_args)?);
        }

        Ok(result)
    }

    fn int_value_at(&self, args: &[i32]) -> Result<i32> {
        if args.len() != self.arity() as usize {
            return Err(UaCalcError::InvalidArgumentCount {
                expected: self.arity() as usize,
                actual: args.len(),
            });
        }

        let set_size = self.get_set_size();
        
        // Validate arguments are in range
        for &arg in args {
            if arg < 0 || arg >= set_size {
                return Err(UaCalcError::InvalidArgument(format!(
                    "Argument {} out of range [0, {})", arg, set_size
                )));
            }
        }

        // Compute table index using Horner's method
        let index = self.base.horner_encode(args)?;
        
        if index < 0 || index as usize >= self.operation_table.len() {
            return Err(UaCalcError::InvalidArgument(format!(
                "Table index {} out of range [0, {})", index, self.operation_table.len()
            )));
        }

        Ok(self.operation_table[index as usize])
    }

    fn int_value_at_horner(&self, arg: i32) -> Result<i32> {
        if arg < 0 || arg as usize >= self.operation_table.len() {
            return Err(UaCalcError::InvalidArgument(format!(
                "Horner index {} out of range [0, {})", arg, self.operation_table.len()
            )));
        }

        Ok(self.operation_table[arg as usize])
    }

    fn make_table(&mut self) -> Result<()> {
        // Table already exists, nothing to do
        Ok(())
    }

    fn get_table(&self) -> Option<&[i32]> {
        Some(&self.operation_table)
    }

    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32]> {
        Ok(&self.operation_table)
    }

    fn is_table_based(&self) -> bool {
        true
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

impl Display for IntOperation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.base)
    }
}

impl PartialEq for IntOperation {
    fn eq(&self, other: &Self) -> bool {
        self.base == other.base && self.operation_table == other.operation_table
    }
}

impl Eq for IntOperation {}

impl Hash for IntOperation {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.base.hash(state);
        self.operation_table.hash(state);
    }
}

impl PartialOrd for IntOperation {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for IntOperation {
    fn cmp(&self, other: &Self) -> Ordering {
        self.base.cmp(&other.base)
    }
}

/// Python wrapper methods for IntOperation
#[pymethods]
impl IntOperation {
    #[new]
    fn py_new(name: String, arity: i32, table: Vec<i32>, set_size: i32) -> PyResult<Self> {
        Self::new_with_name(name, arity, table, set_size).map_err(|e| e.into())
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

    #[getter]
    fn get_table(&self) -> Vec<i32> {
        self.operation_table.clone()
    }

    fn int_value_at_py(&self, args: Vec<i32>) -> PyResult<i32> {
        self.int_value_at(&args).map_err(|e| e.into())
    }

    fn int_value_at_horner_py(&self, arg: i32) -> PyResult<i32> {
        self.int_value_at_horner(arg).map_err(|e| e.into())
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

    #[staticmethod]
    fn create_binary_operation_py(name: String, set_size: i32, table: Vec<i32>) -> PyResult<Self> {
        if table.len() != (set_size * set_size) as usize {
            return Err(UaCalcError::InvalidArgument(format!(
                "Binary operation table must have {} elements, got {}", 
                set_size * set_size, table.len()
            )).into());
        }
        Self::new_with_name(name, 2, table, set_size).map_err(|e| e.into())
    }

    #[staticmethod]
    fn create_unary_operation_py(name: String, set_size: i32, table: Vec<i32>) -> PyResult<Self> {
        if table.len() != set_size as usize {
            return Err(UaCalcError::InvalidArgument(format!(
                "Unary operation table must have {} elements, got {}", 
                set_size, table.len()
            )).into());
        }
        Self::new_with_name(name, 1, table, set_size).map_err(|e| e.into())
    }

    fn __str__(&self) -> String {
        self.to_string()
    }

    fn __repr__(&self) -> String {
        format!("IntOperation('{}', arity={}, set_size={}, table_size={})", 
                self.symbol().name(), self.arity(), self.get_set_size(), self.operation_table.len())
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
pub type PyIntOperation = IntOperation;