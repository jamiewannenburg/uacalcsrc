//! Abstract Operation implementation for UACalc
//! 
//! Provides a base implementation of the Operation trait with common functionality.

use crate::alg::op::{Operation, OperationSymbol, OperationError, OperationResult, operations_util};
use pyo3::prelude::*;
use std::cmp::Ordering;
use std::fmt;
use std::hash::{Hash, Hasher};

/// Abstract base implementation of the Operation trait
/// 
/// This struct provides default implementations for most Operation methods
/// and serves as a base for concrete operation implementations.
#[derive(Debug, Clone)]
#[pyclass(name = "AbstractOperation")]
pub struct AbstractOperation {
    symbol: OperationSymbol,
    set_size: i32,
    value_table: Option<Vec<i32>>,
}

impl AbstractOperation {
    /// Create a new AbstractOperation with a symbol name and arity
    pub fn new(name: String, arity: i32, set_size: i32) -> Self {
        Self::with_symbol(OperationSymbol::new(name, arity), set_size)
    }
    
    /// Create a new AbstractOperation with an OperationSymbol
    pub fn with_symbol(symbol: OperationSymbol, set_size: i32) -> Self {
        Self {
            symbol,
            set_size,
            value_table: None,
        }
    }
    
    /// Helper method to compute table size for this operation
    fn compute_table_size(&self) -> usize {
        if self.arity() == 0 {
            1
        } else {
            (self.set_size as usize).pow(self.arity() as u32)
        }
    }
    
    /// Helper method to convert arguments to Horner encoding
    #[allow(dead_code)]
    fn args_to_horner(&self, args: &[i32]) -> OperationResult<i32> {
        if args.len() != self.arity() as usize {
            return Err(OperationError::InvalidArguments(
                format!("Expected {} arguments, got {}", self.arity(), args.len())
            ));
        }
        
        let mut result = 0;
        let base = self.set_size;
        
        for &arg in args {
            if arg < 0 || arg >= base {
                return Err(OperationError::InvalidArguments(
                    format!("Argument {} out of range [0, {})", arg, base)
                ));
            }
            result = result * base + arg;
        }
        
        Ok(result)
    }
    
    /// Helper method to convert Horner encoding back to arguments
    fn horner_to_args(&self, horner: i32) -> OperationResult<Vec<i32>> {
        let mut args = Vec::with_capacity(self.arity() as usize);
        let mut remaining = horner;
        let base = self.set_size;
        
        for _ in 0..self.arity() {
            args.push(remaining % base);
            remaining /= base;
        }
        
        args.reverse();
        Ok(args)
    }
}

#[pymethods]
impl AbstractOperation {
    #[new]
    pub fn py_new(name: String, arity: i32, set_size: i32) -> Self {
        Self::new(name, arity, set_size)
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
    
    /// Check if operation has a table
    pub fn has_table(&self) -> bool {
        self.value_table.is_some()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("{}", self)
    }
    
    /// Python representation
    fn __repr__(&self) -> String {
        format!("AbstractOperation('{}', {}, {})", self.symbol.name, self.symbol.arity, self.set_size)
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

impl Operation for AbstractOperation {
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
            "Generic object evaluation not implemented in AbstractOperation".to_string()
        ))
    }
    
    fn value_at_arrays(&self, _args: &[&[i32]]) -> OperationResult<Vec<i32>> {
        Err(OperationError::NotImplemented(
            "Array evaluation not implemented in AbstractOperation".to_string()
        ))
    }
    
    fn int_value_at(&self, _args: &[i32]) -> OperationResult<i32> {
        Err(OperationError::NotImplemented(
            "Integer evaluation not implemented in AbstractOperation".to_string()
        ))
    }
    
    fn int_value_at_horner(&self, arg: i32) -> OperationResult<i32> {
        // If we have a table, use it for fast lookup
        if let Some(ref table) = self.value_table {
            if arg >= 0 && (arg as usize) < table.len() {
                return Ok(table[arg as usize]);
            } else {
                return Err(OperationError::IndexOutOfBounds(
                    format!("Horner index {} out of bounds for table of size {}", arg, table.len())
                ));
            }
        }
        
        // Otherwise, convert to regular arguments and evaluate
        let args = self.horner_to_args(arg)?;
        self.int_value_at(&args)
    }
    
    fn make_table(&mut self) -> OperationResult<()> {
        let table_size = self.compute_table_size();
        let mut table = Vec::with_capacity(table_size);
        
        if self.arity() == 0 {
            // Nullary operation
            let value = self.int_value_at(&[])?;
            table.push(value);
        } else {
            // Generate all possible argument combinations
            for horner_index in 0..table_size {
                let args = self.horner_to_args(horner_index as i32)?;
                let value = self.int_value_at(&args)?;
                table.push(value);
            }
        }
        
        self.value_table = Some(table);
        Ok(())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        self.value_table.as_deref()
    }
    
    fn get_table_force(&mut self, make_table: bool) -> OperationResult<Option<&[i32]>> {
        if self.value_table.is_none() && make_table {
            self.make_table()?;
        }
        Ok(self.value_table.as_deref())
    }
    
    fn is_table_based(&self) -> bool {
        false // AbstractOperation is not inherently table-based
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
            return Ok(true); // Nullary and unary operations are trivially symmetric
        }
        
        // We need to check all permutations of arguments
        // For now, implement a basic check for small arities
        if arity == 2 {
            return self.is_commutative();
        }
        
        // For higher arities, we would need to generate all permutations
        // This is computationally expensive, so for now return a conservative result
        Err(OperationError::NotImplemented(
            format!("Total symmetry check not fully implemented for arity {}", arity)
        ))
    }
    
    fn is_maltsev(&self) -> OperationResult<bool> {
        if self.arity() != 3 {
            return Ok(false);
        }
        
        let set_size = self.get_set_size();
        
        // Check Maltsev identity: f(x,y,y) = x and f(x,x,y) = y
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
        operations_util::is_total_check(self)
    }
}

impl fmt::Display for AbstractOperation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.symbol)
    }
}

impl PartialEq for AbstractOperation {
    fn eq(&self, other: &Self) -> bool {
        self.symbol == other.symbol && self.set_size == other.set_size
    }
}

impl Eq for AbstractOperation {}

impl Hash for AbstractOperation {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.symbol.hash(state);
        self.set_size.hash(state);
    }
}

impl PartialOrd for AbstractOperation {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for AbstractOperation {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.symbol.cmp(&other.symbol) {
            Ordering::Equal => self.set_size.cmp(&other.set_size),
            other => other,
        }
    }
}