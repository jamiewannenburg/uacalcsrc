//! Operation trait definition

use crate::error::{Result, UaCalcError};
use super::OperationSymbol;
use std::fmt::Display;
use std::hash::Hash;

/// The core Operation trait defining operations in universal algebra
/// 
/// This trait corresponds to the Java Operation interface and defines
/// all methods for working with algebraic operations.
pub trait Operation: Ord + PartialOrd + Eq + PartialEq + Hash + Display + Send + Sync {
    /// Returns the arity (number of operands) of the operation
    fn arity(&self) -> i32;

    /// Returns the size of the set the operation acts on
    fn get_set_size(&self) -> i32;

    /// Returns the operation symbol
    fn symbol(&self) -> &OperationSymbol;

    /// Element version of operation evaluation
    /// 
    /// This corresponds to `valueAt(List args)` in Java.
    /// For Rust, we use a generic approach that can handle different element types.
    fn value_at_elements(&self, args: &[Box<dyn std::any::Any>]) -> Result<Box<dyn std::any::Any>>;

    /// Fast product operation evaluation
    /// 
    /// This corresponds to `valueAt(int[][] args)` in Java.
    /// Each inner array represents one element from the product algebra.
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>>;

    /// Integer version of operation evaluation
    /// 
    /// This corresponds to `intValueAt(int[] args)` in Java.
    fn int_value_at(&self, args: &[i32]) -> Result<i32>;

    /// Fast table access using Horner encoding
    /// 
    /// This corresponds to `intValueAt(int arg)` in Java.
    /// The arg parameter is the Horner encoding of the actual arguments.
    fn int_value_at_horner(&self, arg: i32) -> Result<i32>;

    /// Creates operation table for faster evaluation
    /// 
    /// This will make a table and so make the operation faster but
    /// requires more space.
    fn make_table(&mut self) -> Result<()>;

    /// Gets the operation table or None if it doesn't exist
    fn get_table(&self) -> Option<&[i32]>;

    /// Gets the table for this operation, creating it if requested
    /// 
    /// If the table doesn't exist and make_table is true, it will be created.
    fn get_table_force(&mut self, make_table: bool) -> Result<&[i32]>;

    /// Checks if operation is table-based
    fn is_table_based(&self) -> bool;

    /// Checks if operation is idempotent in the sense f(x,x,...,x) = x
    fn is_idempotent(&self) -> Result<bool>;

    /// Checks if operation is binary and associative
    fn is_associative(&self) -> Result<bool>;

    /// Checks if operation is binary and commutative
    fn is_commutative(&self) -> Result<bool>;

    /// Checks if operation is totally symmetric (invariant under all variable permutations)
    fn is_totally_symmetric(&self) -> Result<bool>;

    /// Checks if a ternary operation is a Maltsev operation
    fn is_maltsev(&self) -> Result<bool>;

    /// Checks if operation is total (only operations with default values can fail this)
    fn is_total(&self) -> Result<bool>;
}

/// Utility functions for operations
pub struct Operations;

impl Operations {
    /// Check if an operation is totally symmetric
    pub fn is_totally_symmetric<T: Operation + ?Sized>(op: &T) -> Result<bool> {
        let arity = op.arity();
        if arity <= 1 {
            return Ok(true);
        }

        let set_size = op.get_set_size();
        if set_size <= 0 {
            return Err(UaCalcError::InvalidSetSize(set_size));
        }

        // For small arities, we can check all permutations
        // For larger arities, this becomes computationally expensive
        if arity > 4 {
            // For now, return false for large arities
            // TODO: Implement more efficient algorithm
            return Ok(false);
        }

        // Generate all possible argument vectors
        let mut args = vec![0; arity as usize];
        Self::check_all_permutations(op, &mut args, 0, set_size)
    }

    fn check_all_permutations<T: Operation + ?Sized>(
        op: &T,
        args: &mut [i32],
        pos: usize,
        set_size: i32,
    ) -> Result<bool> {
        if pos == args.len() {
            // Check all permutations of current args
            return Self::check_permutations_equal(op, args);
        }

        for i in 0..set_size {
            args[pos] = i;
            if !Self::check_all_permutations(op, args, pos + 1, set_size)? {
                return Ok(false);
            }
        }

        Ok(true)
    }

    fn check_permutations_equal<T: Operation + ?Sized>(op: &T, args: &[i32]) -> Result<bool> {
        let base_result = op.int_value_at(args)?;
        
        // Generate all permutations and check if they give the same result
        let mut perm = args.to_vec();
        loop {
            if op.int_value_at(&perm)? != base_result {
                return Ok(false);
            }
            if !Self::next_permutation(&mut perm) {
                break;
            }
        }

        Ok(true)
    }

    fn next_permutation(data: &mut [i32]) -> bool {
        if data.len() <= 1 {
            return false;
        }

        // Find the largest index k such that data[k] < data[k + 1]
        let mut k = None;
        for i in 0..data.len() - 1 {
            if data[i] < data[i + 1] {
                k = Some(i);
            }
        }

        if k.is_none() {
            return false;
        }
        let k = k.unwrap();

        // Find the largest index l greater than k such that data[k] < data[l]
        let mut l = k + 1;
        for i in k + 2..data.len() {
            if data[k] < data[i] {
                l = i;
            }
        }

        // Swap data[k] and data[l]
        data.swap(k, l);

        // Reverse the suffix starting at data[k + 1]
        data[k + 1..].reverse();

        true
    }

    /// Check if an operation is associative
    pub fn is_associative<T: Operation + ?Sized>(op: &T) -> Result<bool> {
        if op.arity() != 2 {
            return Ok(false);
        }

        let set_size = op.get_set_size();
        if set_size <= 0 {
            return Err(UaCalcError::InvalidSetSize(set_size));
        }

        for a in 0..set_size {
            for b in 0..set_size {
                for c in 0..set_size {
                    let ab_c = op.int_value_at(&[op.int_value_at(&[a, b])?, c])?;
                    let a_bc = op.int_value_at(&[a, op.int_value_at(&[b, c])?])?;
                    if ab_c != a_bc {
                        return Ok(false);
                    }
                }
            }
        }

        Ok(true)
    }

    /// Check if an operation is commutative
    pub fn is_commutative<T: Operation + ?Sized>(op: &T) -> Result<bool> {
        if op.arity() != 2 {
            return Ok(false);
        }

        let set_size = op.get_set_size();
        if set_size <= 0 {
            return Err(UaCalcError::InvalidSetSize(set_size));
        }

        for a in 0..set_size {
            for b in 0..set_size {
                if op.int_value_at(&[a, b])? != op.int_value_at(&[b, a])? {
                    return Ok(false);
                }
            }
        }

        Ok(true)
    }

    /// Check if a ternary operation is Maltsev
    pub fn is_maltsev<T: Operation + ?Sized>(op: &T) -> Result<bool> {
        if op.arity() != 3 {
            return Ok(false);
        }

        let set_size = op.get_set_size();
        if set_size <= 0 {
            return Err(UaCalcError::InvalidSetSize(set_size));
        }

        // Check if f(x,y,y) = x and f(x,x,y) = y for all x,y
        for x in 0..set_size {
            for y in 0..set_size {
                if op.int_value_at(&[x, y, y])? != x {
                    return Ok(false);
                }
                if op.int_value_at(&[x, x, y])? != y {
                    return Ok(false);
                }
            }
        }

        Ok(true)
    }

    /// Check if an operation is total
    pub fn is_total<T: Operation + ?Sized>(_op: &T) -> Result<bool> {
        // By default, operations are total
        // Only OperationWithDefaultValue can be non-total
        Ok(true)
    }

    /// Create an integer operation from a table
    pub fn make_int_operation(symbol: OperationSymbol, table: Vec<i32>, set_size: i32) -> Result<super::IntOperation> {
        use super::IntOperation;
        IntOperation::new(symbol, table, set_size)
    }
}