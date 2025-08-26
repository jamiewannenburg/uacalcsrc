use crate::utils::{horner_decode, horner_encode, horner_table_size, validate_operation_args};
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

/// Flat operation table using Horner encoding for efficient lookup
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlatOperationTable {
    arity: usize,
    set_size: usize,
    table: Vec<usize>,
}

impl FlatOperationTable {
    /// Create a new flat operation table
    pub fn new(arity: usize, set_size: usize) -> UACalcResult<Self> {
        let table_size =
            horner_table_size(arity, set_size).ok_or_else(|| UACalcError::InvalidOperation {
                message: "Table size would overflow".to_string(),
            })?;

        Ok(Self {
            arity,
            set_size,
            table: vec![0; table_size],
        })
    }

    /// Get the value at the given index
    pub fn get(&self, index: usize) -> UACalcResult<usize> {
        self.table
            .get(index)
            .copied()
            .ok_or_else(|| UACalcError::IndexOutOfBounds {
                index,
                size: self.table.len(),
            })
    }

    /// Set the value at the given index
    pub fn set(&mut self, index: usize, value: usize) -> UACalcResult<()> {
        if index >= self.table.len() {
            return Err(UACalcError::IndexOutOfBounds {
                index,
                size: self.table.len(),
            });
        }
        self.table[index] = value;
        Ok(())
    }

    /// Get the value for given arguments using Horner encoding
    pub fn get_value(&self, args: &[usize]) -> UACalcResult<usize> {
        validate_operation_args(args, self.arity, self.set_size)?;
        let index =
            horner_encode(args, self.set_size).ok_or_else(|| UACalcError::InvalidOperation {
                message: "Failed to encode arguments".to_string(),
            })?;
        self.get(index)
    }

    /// Set the value for given arguments using Horner encoding
    pub fn set_value(&mut self, args: &[usize], value: usize) -> UACalcResult<()> {
        validate_operation_args(args, self.arity, self.set_size)?;
        let index =
            horner_encode(args, self.set_size).ok_or_else(|| UACalcError::InvalidOperation {
                message: "Failed to encode arguments".to_string(),
            })?;
        self.set(index, value)
    }

    /// Get the arity of the operation
    pub fn arity(&self) -> usize {
        self.arity
    }

    /// Get the set size
    pub fn set_size(&self) -> usize {
        self.set_size
    }

    /// Get the table size
    pub fn table_size(&self) -> usize {
        self.table.len()
    }

    /// Get the underlying table as a slice
    pub fn as_slice(&self) -> &[usize] {
        &self.table
    }

    /// Get the underlying table as a mutable slice
    pub fn as_mut_slice(&mut self) -> &mut [usize] {
        &mut self.table
    }

    /// Decode an index back to arguments
    pub fn decode_index(&self, index: usize) -> Vec<usize> {
        horner_decode(index, self.arity, self.set_size)
    }
}

/// Trait for operations in universal algebras
pub trait Operation: fmt::Debug + Send + Sync {
    /// Get the arity of the operation
    fn arity(&self) -> usize;

    /// Get the symbol of the operation
    fn symbol(&self) -> &OperationSymbol;

    /// Compute the value of the operation on given arguments
    fn value(&self, args: &[usize]) -> UACalcResult<usize>;

    /// Integer-optimized value computation (mirrors Java's intValueAt)
    fn int_value_at(&self, args: &[usize]) -> UACalcResult<usize> {
        self.value(args)
    }

    /// Get value by Horner-encoded index for flat table lookup
    fn int_value_at_index(&self, horner_index: usize) -> UACalcResult<usize> {
        // Default implementation decodes and calls value
        // Override in implementations with flat tables
        let args = self.decode_index(horner_index)?;
        self.value(&args)
    }

    /// Get the set size (universe size) for this operation
    fn set_size(&self) -> usize;

    /// Generate operation tables for efficient lookup
    fn make_table(&mut self, set_size: usize) -> UACalcResult<()>;

    /// Get the flat operation table if available
    fn get_table(&self) -> Option<&FlatOperationTable>;

    /// Decode a Horner index to arguments
    fn decode_index(&self, horner_index: usize) -> UACalcResult<Vec<usize>> {
        let set_size = self.set_size();
        let arity = self.arity();
        Ok(horner_decode(horner_index, arity, set_size))
    }

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

    /// Check if the operation is idempotent on the given set size
    fn is_idempotent_on_set(&self, set_size: usize) -> UACalcResult<bool> {
        if self.arity() != 1 {
            return Ok(false);
        }

        for element in 0..set_size {
            if self.int_value_at(&[element])? != element {
                return Ok(false);
            }
        }
        Ok(true)
    }

    /// Check if the operation is associative on the given set size
    fn is_associative_on_set(&self, set_size: usize) -> UACalcResult<bool> {
        if self.arity() != 2 {
            return Ok(false);
        }

        for a in 0..set_size {
            for b in 0..set_size {
                for c in 0..set_size {
                    let left = self.int_value_at(&[self.int_value_at(&[a, b])?, c])?;
                    let right = self.int_value_at(&[a, self.int_value_at(&[b, c])?])?;
                    if left != right {
                        return Ok(false);
                    }
                }
            }
        }
        Ok(true)
    }

    /// Check if the operation is commutative on the given set size
    fn is_commutative_on_set(&self, set_size: usize) -> UACalcResult<bool> {
        if self.arity() != 2 {
            return Ok(false);
        }

        for a in 0..set_size {
            for b in 0..set_size {
                let left = self.int_value_at(&[a, b])?;
                let right = self.int_value_at(&[b, a])?;
                if left != right {
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }

    /// Check if the operation is idempotent (deprecated, use is_idempotent_on_set)
    fn is_idempotent(&self) -> UACalcResult<bool> {
        self.is_idempotent_on_set(self.set_size())
    }

    /// Check if the operation is associative (deprecated, use is_associative_on_set)
    fn is_associative(&self) -> UACalcResult<bool> {
        self.is_associative_on_set(self.set_size())
    }

    /// Check if the operation is commutative (deprecated, use is_commutative_on_set)
    fn is_commutative(&self) -> UACalcResult<bool> {
        self.is_commutative_on_set(self.set_size())
    }
}

/// Table-based operation implementation with flat table optimization
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TableOperation {
    symbol: OperationSymbol,
    table: Option<FlatOperationTable>,
    set_size: usize,
}

impl TableOperation {
    /// Create a new table-based operation
    ///
    /// The table should contain rows where each row has the format [args..., result].
    /// For example, a binary operation should have rows like [a, b, result].
    ///
    /// # Arguments
    /// * `symbol` - The operation symbol with name and arity
    /// * `table` - Vector of rows, where each row is [args..., result]
    /// * `set_size` - The size of the universe
    pub fn new(
        symbol: OperationSymbol,
        table: Vec<Vec<usize>>,
        set_size: usize,
    ) -> UACalcResult<Self> {
        // Validate table dimensions - each row should have arity + 1 elements (args + result)
        let expected = symbol.arity + 1;
        for row in &table {
            if row.len() != expected {
                return Err(UACalcError::InvalidArity {
                    expected,
                    actual: row.len(),
                });
            }
        }

        let mut operation = Self {
            symbol,
            table: None,
            set_size,
        };

        // Build the flat table from the row-based table
        operation.make_table(set_size)?;

        // Populate the flat table
        if let Some(ref mut flat_table) = operation.table {
            for row in table {
                let args = &row[..row.len() - 1];
                let result = row[row.len() - 1];
                flat_table.set_value(args, result)?;
            }
        }

        Ok(operation)
    }

    /// Create a constant operation
    pub fn constant(name: String, value: usize, set_size: usize) -> UACalcResult<Self> {
        let mut operation = Self {
            symbol: OperationSymbol::new(name, 0),
            table: None,
            set_size,
        };

        // Build flat table for constant operation
        operation.make_table(set_size)?;

        if value >= set_size {
            return Err(UACalcError::IndexOutOfBounds {
                index: value,
                size: set_size,
            });
        }
        if let Some(ref mut ft) = operation.table {
            ft.set(0, value)?;
        }

        Ok(operation)
    }

    /// Create a unary operation from a function
    pub fn unary<F>(name: String, set_size: usize, f: F) -> Self
    where
        F: Fn(usize) -> usize,
    {
        let mut operation = Self {
            symbol: OperationSymbol::new(name, 1),
            table: None,
            set_size,
        };

        // Build flat table
        operation.make_table(set_size).unwrap();

        // Populate the table
        if let Some(ref mut flat_table) = operation.table {
            for i in 0..set_size {
                flat_table.set_value(&[i], f(i)).unwrap();
            }
        }

        operation
    }

    /// Create a binary operation from a function
    pub fn binary<F>(name: String, set_size: usize, f: F) -> Self
    where
        F: Fn(usize, usize) -> usize,
    {
        let mut operation = Self {
            symbol: OperationSymbol::new(name, 2),
            table: None,
            set_size,
        };

        // Build flat table
        operation.make_table(set_size).unwrap();

        // Populate the table
        if let Some(ref mut flat_table) = operation.table {
            for i in 0..set_size {
                for j in 0..set_size {
                    flat_table.set_value(&[i, j], f(i, j)).unwrap();
                }
            }
        }

        operation
    }

    /// Create an operation from a function with arbitrary arity
    pub fn from_function<F>(symbol: OperationSymbol, set_size: usize, f: F) -> UACalcResult<Self>
    where
        F: Fn(&[usize]) -> UACalcResult<usize>,
    {
        let arity = symbol.arity;
        let mut operation = Self {
            symbol,
            table: None,
            set_size,
        };

        // Build flat table
        operation.make_table(set_size)?;

        // Populate the table using Horner encoding
        if let Some(ref mut flat_table) = operation.table {
            let table_len =
                horner_table_size(arity, set_size).ok_or(UACalcError::InvalidOperation {
                    message: "Table size would overflow".to_string(),
                })?;
            for idx in 0..table_len {
                let args = horner_decode(idx, arity, set_size);
                let result = f(&args)?;
                if result >= set_size {
                    return Err(UACalcError::IndexOutOfBounds {
                        index: result,
                        size: set_size,
                    });
                }
                flat_table.set(idx, result)?;
            }
        }

        Ok(operation)
    }

    /// Create the identity operation
    pub fn identity(set_size: usize) -> Self {
        Self::unary("id".to_string(), set_size, |x| x)
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
        if let Some(ref table) = self.table {
            table.get_value(args)
        } else {
            Err(UACalcError::InvalidOperation {
                message: "Operation table not built".to_string(),
            })
        }
    }

    fn int_value_at(&self, args: &[usize]) -> UACalcResult<usize> {
        self.value(args)
    }

    fn int_value_at_index(&self, horner_index: usize) -> UACalcResult<usize> {
        if let Some(ref table) = self.table {
            table.get(horner_index)
        } else {
            Err(UACalcError::InvalidOperation {
                message: "Operation table not built".to_string(),
            })
        }
    }

    fn set_size(&self) -> usize {
        self.set_size
    }

    fn make_table(&mut self, set_size: usize) -> UACalcResult<()> {
        self.table = Some(FlatOperationTable::new(self.arity(), set_size)?);
        Ok(())
    }

    fn get_table(&self) -> Option<&FlatOperationTable> {
        self.table.as_ref()
    }
}

/// Function-based operation implementation
#[derive(Debug)]
pub struct FunctionOperation<F> {
    symbol: OperationSymbol,
    function: F,
    set_size: usize,
    table: Option<FlatOperationTable>,
}

impl<F> FunctionOperation<F>
where
    F: Fn(&[usize]) -> UACalcResult<usize> + Send + Sync + std::fmt::Debug,
{
    pub fn new(symbol: OperationSymbol, function: F, set_size: usize) -> Self {
        Self {
            symbol,
            function,
            set_size,
            table: None,
        }
    }
}

impl<F> Operation for FunctionOperation<F>
where
    F: Fn(&[usize]) -> UACalcResult<usize> + Send + Sync + std::fmt::Debug,
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

    fn set_size(&self) -> usize {
        self.set_size
    }

    fn make_table(&mut self, set_size: usize) -> UACalcResult<()> {
        let mut flat_table = FlatOperationTable::new(self.arity(), set_size)?;

        // Populate the table using Horner encoding
        let arity = self.arity();
        let table_len =
            horner_table_size(arity, set_size).ok_or(UACalcError::InvalidOperation {
                message: "Table size would overflow".to_string(),
            })?;
        for idx in 0..table_len {
            let args = horner_decode(idx, arity, set_size);
            let result = (self.function)(&args)?;
            if result >= set_size {
                return Err(UACalcError::IndexOutOfBounds {
                    index: result,
                    size: set_size,
                });
            }
            flat_table.set(idx, result)?;
        }

        self.table = Some(flat_table);
        Ok(())
    }

    fn get_table(&self) -> Option<&FlatOperationTable> {
        self.table.as_ref()
    }
}

impl<F> Clone for FunctionOperation<F>
where
    F: Clone + Fn(&[usize]) -> UACalcResult<usize> + Send + Sync + std::fmt::Debug,
{
    fn clone(&self) -> Self {
        Self {
            symbol: self.symbol.clone(),
            function: self.function.clone(),
            set_size: self.set_size,
            table: self.table.clone(),
        }
    }
}

impl<F> Serialize for FunctionOperation<F>
where
    F: Clone + Fn(&[usize]) -> UACalcResult<usize> + Send + Sync + std::fmt::Debug,
{
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        self.symbol.serialize(serializer)
    }
}

// Note: FunctionOperation cannot implement Deserialize because function types
// cannot be reconstructed from serialized data. If deserialization is needed,
// consider using TableOperation or implementing a custom deserialization strategy.
