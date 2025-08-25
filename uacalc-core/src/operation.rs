use crate::{UACalcError, UACalcResult};
use serde::{Deserialize, Serialize};
use std::fmt;

/// Symbol for an operation
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct OperationSymbol {
    pub name: String,
    pub arity: usize,
}

impl OperationSymbol {
    pub fn new(name: String, arity: usize) -> Self {
        Self { name, arity }
    }
}

/// Type of operation
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum OperationType {
    Constant,
    Unary,
    Binary,
    Ternary,
    Nary(usize),
}

/// Trait for operations in universal algebras
pub trait Operation: fmt::Debug + Send + Sync {
    /// Get the arity of the operation
    fn arity(&self) -> usize;
    
    /// Get the symbol of the operation
    fn symbol(&self) -> &OperationSymbol;
    
    /// Compute the value of the operation on given arguments
    fn value(&self, args: &[usize]) -> UACalcResult<usize>;
    
    /// Get the operation type
    fn operation_type(&self) -> OperationType {
        match self.arity() {
            0 => OperationType::Constant,
            1 => OperationType::Unary,
            2 => OperationType::Binary,
            3 => OperationType::Ternary,
            n => OperationType::Nary(n),
        }
    }
    
    /// Check if the operation is idempotent
    fn is_idempotent(&self) -> UACalcResult<bool> {
        if self.arity() != 1 {
            return Ok(false);
        }
        // This would need access to the algebra's universe
        // For now, return false as a placeholder
        Ok(false)
    }
    
    /// Check if the operation is associative (for binary operations)
    fn is_associative(&self) -> UACalcResult<bool> {
        if self.arity() != 2 {
            return Ok(false);
        }
        // This would need access to the algebra's universe
        // For now, return false as a placeholder
        Ok(false)
    }
    
    /// Check if the operation is commutative (for binary operations)
    fn is_commutative(&self) -> UACalcResult<bool> {
        if self.arity() != 2 {
            return Ok(false);
        }
        // This would need access to the algebra's universe
        // For now, return false as a placeholder
        Ok(false)
    }
}

/// Table-based operation implementation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TableOperation {
    symbol: OperationSymbol,
    table: Vec<Vec<usize>>,
}

impl TableOperation {
    /// Create a new table-based operation
    pub fn new(symbol: OperationSymbol, table: Vec<Vec<usize>>) -> UACalcResult<Self> {
        // Validate table dimensions
        let expected_size = symbol.arity();
        for row in &table {
            if row.len() != expected_size {
                return Err(UACalcError::InvalidArity {
                    expected: expected_size,
                    actual: row.len(),
                });
            }
        }
        
        Ok(Self { symbol, table })
    }
    
    /// Create a constant operation
    pub fn constant(name: String, value: usize) -> Self {
        Self {
            symbol: OperationSymbol::new(name, 0),
            table: vec![vec![value]],
        }
    }
    
    /// Create a unary operation from a function
    pub fn unary<F>(name: String, size: usize, f: F) -> Self 
    where
        F: Fn(usize) -> usize,
    {
        let mut table = Vec::with_capacity(size);
        for i in 0..size {
            table.push(vec![f(i)]);
        }
        
        Self {
            symbol: OperationSymbol::new(name, 1),
            table,
        }
    }
    
    /// Create a binary operation from a function
    pub fn binary<F>(name: String, size: usize, f: F) -> Self 
    where
        F: Fn(usize, usize) -> usize,
    {
        let mut table = Vec::with_capacity(size * size);
        for i in 0..size {
            for j in 0..size {
                table.push(vec![i, j, f(i, j)]);
            }
        }
        
        Self {
            symbol: OperationSymbol::new(name, 2),
            table,
        }
    }
}

impl Operation for TableOperation {
    fn arity(&self) -> usize {
        self.symbol.arity
    }
    
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn value(&self, args: &[usize]) -> UACalcResult<usize> {
        if args.len() != self.arity() {
            return Err(UACalcError::InvalidArity {
                expected: self.arity(),
                actual: args.len(),
            });
        }
        
        // For table-based operations, we need to find the row that matches the arguments
        // This is a simplified implementation - in practice, you'd want a more efficient lookup
        for row in &self.table {
            if row[..args.len()] == args {
                return Ok(row[args.len()]);
            }
        }
        
        Err(UACalcError::InvalidOperation {
            message: format!("No table entry found for arguments: {:?}", args),
        })
    }
}

/// Function-based operation implementation
#[derive(Debug)]
pub struct FunctionOperation<F> {
    symbol: OperationSymbol,
    function: F,
}

impl<F> FunctionOperation<F>
where
    F: Fn(&[usize]) -> UACalcResult<usize> + Send + Sync,
{
    pub fn new(symbol: OperationSymbol, function: F) -> Self {
        Self { symbol, function }
    }
}

impl<F> Operation for FunctionOperation<F>
where
    F: Fn(&[usize]) -> UACalcResult<usize> + Send + Sync,
{
    fn arity(&self) -> usize {
        self.symbol.arity
    }
    
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn value(&self, args: &[usize]) -> UACalcResult<usize> {
        if args.len() != self.arity() {
            return Err(UACalcError::InvalidArity {
                expected: self.arity(),
                actual: args.len(),
            });
        }
        
        (self.function)(args)
    }
}

impl<F> Clone for FunctionOperation<F>
where
    F: Clone + Fn(&[usize]) -> UACalcResult<usize> + Send + Sync,
{
    fn clone(&self) -> Self {
        Self {
            symbol: self.symbol.clone(),
            function: self.function.clone(),
        }
    }
}

impl<F> Serialize for FunctionOperation<F>
where
    F: Clone + Fn(&[usize]) -> UACalcResult<usize> + Send + Sync,
{
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        self.symbol.serialize(serializer)
    }
}

impl<F> Deserialize for FunctionOperation<F>
where
    F: Clone + Fn(&[usize]) -> UACalcResult<usize> + Send + Sync,
{
    fn deserialize<D>(_deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        // This is a placeholder - function operations can't be fully deserialized
        unimplemented!("Function operations cannot be deserialized")
    }
}

