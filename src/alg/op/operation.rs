//! Operation trait definition for UACalc
//! 
//! Provides the core Operation trait that defines the interface for universal algebra operations.

use crate::alg::op::OperationSymbol;
use std::fmt;
use std::hash::Hash;
use thiserror::Error;

/// Errors that can occur during operation evaluation
#[derive(Error, Debug)]
pub enum OperationError {
    #[error("Invalid arguments: {0}")]
    InvalidArguments(String),
    #[error("Operation not implemented: {0}")]
    NotImplemented(String),
    #[error("Table creation failed: {0}")]
    TableCreationFailed(String),
    #[error("Index out of bounds: {0}")]
    IndexOutOfBounds(String),
    #[error("Operation evaluation failed: {0}")]
    EvaluationFailed(String),
}

/// Result type for operation methods
pub type OperationResult<T> = Result<T, OperationError>;

/// The core Operation trait defining universal algebra operations
/// 
/// This trait corresponds to the Java Operation interface and defines
/// all the methods needed for operation evaluation and property checking.
pub trait Operation: Ord + PartialOrd + Eq + PartialEq + Hash + fmt::Display + fmt::Debug {
    
    // ===== CORE PROPERTIES =====
    
    /// Returns the arity (number of operands) of this operation
    fn arity(&self) -> i32;
    
    /// Returns the size of the set this operation acts on
    fn get_set_size(&self) -> i32;
    
    /// Returns the operation symbol for this operation
    fn symbol(&self) -> &OperationSymbol;
    
    // ===== OPERATION EVALUATION =====
    
    /// Element version of operation evaluation using generic objects
    /// This is primarily for compatibility with the Java interface
    fn value_at_objects(&self, args: &[Box<dyn std::any::Any>]) -> OperationResult<Box<dyn std::any::Any>>;
    
    /// Fast product operation evaluation for arrays of integer arrays
    fn value_at_arrays(&self, args: &[&[i32]]) -> OperationResult<Vec<i32>>;
    
    /// Integer version of operation evaluation
    fn int_value_at(&self, args: &[i32]) -> OperationResult<i32>;
    
    /// Fast table access using Horner encoding
    fn int_value_at_horner(&self, arg: i32) -> OperationResult<i32>;
    
    // ===== TABLE MANAGEMENT =====
    
    /// Creates an operation table for faster evaluation
    fn make_table(&mut self) -> OperationResult<()>;
    
    /// Gets the operation table or None if it doesn't exist
    fn get_table(&self) -> Option<&[i32]>;
    
    /// Gets the operation table, creating it if requested and it doesn't exist
    fn get_table_force(&mut self, make_table: bool) -> OperationResult<Option<&[i32]>>;
    
    /// Checks if this operation is table-based
    fn is_table_based(&self) -> bool;
    
    // ===== PROPERTY CHECKS =====
    
    /// Checks if this operation is idempotent: f(x,x,...,x) = x
    fn is_idempotent(&self) -> OperationResult<bool>;
    
    /// Checks if this operation is binary and associative
    fn is_associative(&self) -> OperationResult<bool>;
    
    /// Checks if this operation is binary and commutative  
    fn is_commutative(&self) -> OperationResult<bool>;
    
    /// Checks if this operation is totally symmetric (invariant under all variable permutations)
    fn is_totally_symmetric(&self) -> OperationResult<bool>;
    
    /// Checks if this ternary operation is a Maltsev operation
    fn is_maltsev(&self) -> OperationResult<bool>;
    
    /// Checks if this operation is total (only OperationWithDefaultValue can fail this)
    fn is_total(&self) -> OperationResult<bool>;
}

/// Utility functions for operations
pub mod operations_util {
    use super::*;
    
    /// Check if an operation is total by attempting to evaluate it on all possible inputs
    pub fn is_total_check<T: Operation>(op: &T) -> OperationResult<bool> {
        let set_size = op.get_set_size();
        let arity = op.arity();
        
        if arity == 0 {
            // Nullary operation - always total if it can be evaluated
            return match op.int_value_at(&[]) {
                Ok(_) => Ok(true),
                Err(_) => Ok(false),
            };
        }
        
        // Generate all possible argument combinations
        let mut args = vec![0; arity as usize];
        
        // Use lexicographic enumeration of all possible argument tuples
        loop {
            match op.int_value_at(&args) {
                Ok(_) => {},
                Err(_) => return Ok(false),
            }
            
            // Generate next combination
            let mut i = (arity - 1) as usize;
            loop {
                args[i] += 1;
                if args[i] < set_size {
                    break;
                }
                args[i] = 0;
                if i == 0 {
                    return Ok(true); // All combinations checked successfully
                }
                i -= 1;
            }
        }
    }
    
    /// Check if a binary operation is associative
    pub fn is_associative_check<T: Operation>(op: &T) -> OperationResult<bool> {
        if op.arity() != 2 {
            return Ok(false);
        }
        
        let set_size = op.get_set_size();
        
        for a in 0..set_size {
            for b in 0..set_size {
                for c in 0..set_size {
                    let ab = op.int_value_at(&[a, b])?;
                    let bc = op.int_value_at(&[b, c])?;
                    let ab_c = op.int_value_at(&[ab, c])?;
                    let a_bc = op.int_value_at(&[a, bc])?;
                    
                    if ab_c != a_bc {
                        return Ok(false);
                    }
                }
            }
        }
        
        Ok(true)
    }
    
    /// Check if a binary operation is commutative  
    pub fn is_commutative_check<T: Operation>(op: &T) -> OperationResult<bool> {
        if op.arity() != 2 {
            return Ok(false);
        }
        
        let set_size = op.get_set_size();
        
        for a in 0..set_size {
            for b in 0..set_size {
                let ab = op.int_value_at(&[a, b])?;
                let ba = op.int_value_at(&[b, a])?;
                
                if ab != ba {
                    return Ok(false);
                }
            }
        }
        
        Ok(true)
    }
    
    /// Check if an operation is idempotent
    pub fn is_idempotent_check<T: Operation>(op: &T) -> OperationResult<bool> {
        let set_size = op.get_set_size();
        let arity = op.arity();
        let mut args = vec![0; arity as usize];
        
        for i in 0..set_size {
            // Set all arguments to the same value
            for j in 0..arity as usize {
                args[j] = i;
            }
            
            let result = op.int_value_at(&args)?;
            if result != i {
                return Ok(false);
            }
        }
        
        Ok(true)
    }
}

/// Trait for objects that can be converted to/from Any for generic operation evaluation
pub trait AnyConvertible {
    fn to_any(self) -> Box<dyn std::any::Any>;
    fn from_any(any: Box<dyn std::any::Any>) -> Option<Self> where Self: Sized;
}