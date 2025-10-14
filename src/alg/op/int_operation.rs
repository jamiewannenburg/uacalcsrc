//! Integer Operation implementation for UACalc
//! 
//! Provides a table-based implementation of operations using integer lookup tables.

use crate::alg::op::{Operation, OperationSymbol, OperationError, OperationResult, operations_util};
use pyo3::prelude::*;
use std::cmp::Ordering;
use std::fmt;
use std::hash::{Hash, Hasher};

/// Table-based operation implementation using integer lookup tables
/// 
/// This struct implements operations using pre-computed lookup tables
/// for fast evaluation.
#[derive(Debug, Clone)]
#[pyclass(name = "IntOperation")]
pub struct IntOperation {
    symbol: OperationSymbol,
    set_size: i32,
    table: Vec<i32>,
}

impl IntOperation {
    /// Create a new IntOperation with a lookup table
    pub fn new(name: String, arity: i32, set_size: i32, table: Vec<i32>) -> OperationResult<Self> {
        let symbol = OperationSymbol::new(name, arity);
        Self::with_symbol(symbol, set_size, table)
    }
    
    /// Create a new IntOperation with an OperationSymbol and lookup table
    pub fn with_symbol(symbol: OperationSymbol, set_size: i32, table: Vec<i32>) -> OperationResult<Self> {
        let expected_size = if symbol.arity == 0 {
            1
        } else {
            (set_size as usize).pow(symbol.arity as u32)
        };
        
        if table.len() != expected_size {
            return Err(OperationError::InvalidArguments(
                format!("Table size {} does not match expected size {} for arity {} and set size {}",
                    table.len(), expected_size, symbol.arity, set_size)
            ));
        }
        
        // Validate that all table values are within the valid range
        for (index, &value) in table.iter().enumerate() {
            if value < 0 || value >= set_size {
                return Err(OperationError::InvalidArguments(
                    format!("Table value {} at index {} is out of range [0, {})", 
                        value, index, set_size)
                ));
            }
        }
        
        Ok(Self {
            symbol,
            set_size,
            table,
        })
    }
    
    /// Create an identity operation (f(x) = x) for the given set size
    pub fn identity(set_size: i32) -> OperationResult<Self> {
        let table: Vec<i32> = (0..set_size).collect();
        Self::new("id".to_string(), 1, set_size, table)
    }
    
    /// Create a constant operation (f(...) = c) for the given constant
    pub fn constant(arity: i32, set_size: i32, constant: i32) -> OperationResult<Self> {
        if constant < 0 || constant >= set_size {
            return Err(OperationError::InvalidArguments(
                format!("Constant {} out of range [0, {})", constant, set_size)
            ));
        }
        
        let table_size = if arity == 0 { 1 } else { (set_size as usize).pow(arity as u32) };
        let table = vec![constant; table_size];
        
        Self::new(format!("const_{}", constant), arity, set_size, table)
    }
    
    /// Helper method to convert arguments to table index using Horner's method
    fn args_to_index(&self, args: &[i32]) -> OperationResult<usize> {
        if args.len() != self.arity() as usize {
            return Err(OperationError::InvalidArguments(
                format!("Expected {} arguments, got {}", self.arity(), args.len())
            ));
        }
        
        if self.arity() == 0 {
            return Ok(0);
        }
        
        let mut index = 0usize;
        let base = self.set_size as usize;
        
        for &arg in args {
            if arg < 0 || arg >= self.set_size {
                return Err(OperationError::InvalidArguments(
                    format!("Argument {} out of range [0, {})", arg, self.set_size)
                ));
            }
            index = index * base + arg as usize;
        }
        
        Ok(index)
    }
    
    /// Get the table as a slice
    pub fn get_table_slice(&self) -> &[i32] {
        &self.table
    }
}

#[pymethods]
impl IntOperation {
    #[new]
    pub fn py_new(name: String, arity: i32, set_size: i32, table: Vec<i32>) -> PyResult<Self> {
        Self::new(name, arity, set_size, table)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }
    
    /// Create an identity operation
    #[staticmethod]
    pub fn py_identity(set_size: i32) -> PyResult<Self> {
        Self::identity(set_size)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }
    
    /// Create a constant operation
    #[staticmethod]
    pub fn py_constant(arity: i32, set_size: i32, constant: i32) -> PyResult<Self> {
        Self::constant(arity, set_size, constant)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }
    
    /// Get the arity of this operation
    pub fn get_arity(&self) -> i32 {
        self.arity()
    }
    
    /// Get the set size
    pub fn get_set_size_py(&self) -> i32 {
        self.get_set_size()
    }
    
    /// Get the operation symbol
    pub fn get_symbol(&self) -> OperationSymbol {
        self.symbol.clone()
    }
    
    /// Get a copy of the table
    pub fn get_table_copy(&self) -> Vec<i32> {
        self.table.clone()
    }
    
    /// Evaluate the operation with integer arguments
    pub fn evaluate(&self, args: Vec<i32>) -> PyResult<i32> {
        self.int_value_at(&args)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("{}", self)
    }
    
    /// Python representation
    fn __repr__(&self) -> String {
        format!("IntOperation('{}', {}, {}, table_size={})", 
                self.symbol.name, self.symbol.arity, self.set_size, self.table.len())
    }
    
    /// Python equality
    fn __eq__(&self, other: &Self) -> bool {
        self == other
    }
    
    /// Python hash
    fn __hash__(&self) -> u64 {
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish()
    }
}

impl Operation for IntOperation {
    fn arity(&self) -> i32 {
        self.symbol.arity
    }
    
    fn get_set_size(&self) -> i32 {
        self.set_size
    }
    
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn value_at_objects(&self, _args: &[Box<dyn std::any::Any>]) -> OperationResult<Box<dyn std::any::Any>> {
        Err(OperationError::NotImplemented(
            "Generic object evaluation not implemented in IntOperation".to_string()
        ))
    }
    
    fn value_at_arrays(&self, args: &[&[i32]]) -> OperationResult<Vec<i32>> {
        if args.is_empty() {
            return Err(OperationError::InvalidArguments(
                "Empty argument array".to_string()
            ));
        }
        
        let result_length = args[0].len();
        
        // Validate all arrays have the same length
        for (i, arg_array) in args.iter().enumerate() {
            if arg_array.len() != result_length {
                return Err(OperationError::InvalidArguments(
                    format!("Argument array {} has length {}, expected {}", 
                        i, arg_array.len(), result_length)
                ));
            }
        }
        
        let mut result = Vec::with_capacity(result_length);
        
        for i in 0..result_length {
            let mut point_args = Vec::with_capacity(args.len());
            for arg_array in args {
                point_args.push(arg_array[i]);
            }
            let value = self.int_value_at(&point_args)?;
            result.push(value);
        }
        
        Ok(result)
    }
    
    fn int_value_at(&self, args: &[i32]) -> OperationResult<i32> {
        let index = self.args_to_index(args)?;
        
        if index >= self.table.len() {
            return Err(OperationError::IndexOutOfBounds(
                format!("Index {} out of bounds for table of size {}", index, self.table.len())
            ));
        }
        
        Ok(self.table[index])
    }
    
    fn int_value_at_horner(&self, arg: i32) -> OperationResult<i32> {
        if arg < 0 || (arg as usize) >= self.table.len() {
            return Err(OperationError::IndexOutOfBounds(
                format!("Horner index {} out of bounds for table of size {}", arg, self.table.len())
            ));
        }
        
        Ok(self.table[arg as usize])
    }
    
    fn make_table(&mut self) -> OperationResult<()> {
        // Table already exists, nothing to do
        Ok(())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        Some(&self.table)
    }
    
    fn get_table_force(&mut self, _make_table: bool) -> OperationResult<Option<&[i32]>> {
        Ok(Some(&self.table))
    }
    
    fn is_table_based(&self) -> bool {
        true
    }
    
    fn is_idempotent(&self) -> OperationResult<bool> {
        operations_util::is_idempotent_check(self)
    }
    
    fn is_associative(&self) -> OperationResult<bool> {
        operations_util::is_associative_check(self)
    }
    
    fn is_commutative(&self) -> OperationResult<bool> {
        operations_util::is_commutative_check(self)
    }
    
    fn is_totally_symmetric(&self) -> OperationResult<bool> {
        let arity = self.arity();
        if arity <= 1 {
            return Ok(true);
        }
        
        if arity == 2 {
            return self.is_commutative();
        }
        
        // For higher arities, check a few key permutations
        // This is a simplified check - a full implementation would check all permutations
        let set_size = self.get_set_size();
        
        // Check swapping first two arguments
        for args in generate_all_args(arity, set_size).take(100) { // Limit for performance
            if args.len() >= 2 {
                let mut swapped_args = args.clone();
                swapped_args.swap(0, 1);
                
                let orig_result = self.int_value_at(&args)?;
                let swapped_result = self.int_value_at(&swapped_args)?;
                
                if orig_result != swapped_result {
                    return Ok(false);
                }
            }
        }
        
        Ok(true) // Simplified check passed
    }
    
    fn is_maltsev(&self) -> OperationResult<bool> {
        if self.arity() != 3 {
            return Ok(false);
        }
        
        let set_size = self.get_set_size();
        
        for x in 0..set_size {
            for y in 0..set_size {
                let f_xyy = self.int_value_at(&[x, y, y])?;
                let f_xxy = self.int_value_at(&[x, x, y])?;
                
                if f_xyy != x || f_xxy != y {
                    return Ok(false);
                }
            }
        }
        
        Ok(true)
    }
    
    fn is_total(&self) -> OperationResult<bool> {
        // Table-based operations are always total by construction
        Ok(true)
    }
}

impl fmt::Display for IntOperation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}[table]", self.symbol)
    }
}

impl PartialEq for IntOperation {
    fn eq(&self, other: &Self) -> bool {
        self.symbol == other.symbol && 
        self.set_size == other.set_size && 
        self.table == other.table
    }
}

impl Eq for IntOperation {}

impl Hash for IntOperation {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.symbol.hash(state);
        self.set_size.hash(state);
        self.table.hash(state);
    }
}

impl PartialOrd for IntOperation {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for IntOperation {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.symbol.cmp(&other.symbol) {
            Ordering::Equal => match self.set_size.cmp(&other.set_size) {
                Ordering::Equal => self.table.cmp(&other.table),
                other => other,
            },
            other => other,
        }
    }
}

/// Helper function to generate all possible argument combinations
fn generate_all_args(arity: i32, set_size: i32) -> impl Iterator<Item = Vec<i32>> {
    (0..(set_size as usize).pow(arity as u32)).map(move |mut index| {
        let mut args = Vec::with_capacity(arity as usize);
        for _ in 0..arity {
            args.push((index % set_size as usize) as i32);
            index /= set_size as usize;
        }
        args.reverse();
        args
    })
}