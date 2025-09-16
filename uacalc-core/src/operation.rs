use crate::utils::{horner_decode, horner_encode, horner_table_size, validate_operation_args};
use crate::{UACalcError, UACalcResult};
use serde::{Deserialize, Serialize};
use std::fmt;
use std::collections::BTreeMap;

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

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn arity(&self) -> usize {
        self.arity
    }

    pub fn set_arity(&mut self, arity: usize) {
        self.arity = arity;
    }

    /// Create a string representation with optional arity display
    pub fn to_string_with_arity(&self, show_arity: bool) -> String {
        if show_arity {
            format!("{}({})", self.name, self.arity)
        } else {
            self.name.clone()
        }
    }

    /// Get hash code similar to Java implementation
    pub fn hash_code(&self) -> i32 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.name.hash(&mut hasher);
        let name_hash = hasher.finish() as i32;
        (name_hash + self.arity as i32) & 0x7FFFFFFF
    }
}

impl std::fmt::Display for OperationSymbol {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.name)
    }
}

impl std::cmp::Ord for OperationSymbol {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        // Java compareTo: high arity operations first, then by name
        match other.arity.cmp(&self.arity) {
            std::cmp::Ordering::Equal => self.name.cmp(&other.name),
            other => other,
        }
    }
}

impl std::cmp::PartialOrd for OperationSymbol {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
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
        if value >= self.set_size {
            return Err(UACalcError::IndexOutOfBounds {
                index: value,
                size: self.set_size,
            });
        }
        let index =
            horner_encode(args, self.set_size).ok_or_else(|| UACalcError::InvalidOperation {
                message: "Failed to encode arguments".to_string(),
            })?;
        self.set(index, value)
    }

    /// Get the value at the given arguments (alias for get_value)
    pub fn value_at(&self, args: &[usize]) -> UACalcResult<usize> {
        self.get_value(args)
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
pub trait Operation: fmt::Debug + Send + Sync + std::any::Any {
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
        let k = self.arity();
        if k == 0 {
            return Ok(true); // Conventionally true for constants
        }

        for a in 0..set_size {
            let args = vec![a; k];
            if self.int_value_at(&args)? != a {
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

        // Compute expected table size and validate completeness
        let expected_rows = horner_table_size(symbol.arity, set_size).ok_or_else(|| {
            UACalcError::InvalidOperation {
                message: "Table size would overflow".to_string(),
            }
        })?;

        let mut visited = vec![false; expected_rows];

        let mut operation = Self {
            symbol,
            table: None,
            set_size,
        };

        // Build the flat table from the row-based table
        operation.make_table(set_size)?;

        // Populate the flat table and track visited entries
        if let Some(ref mut flat_table) = operation.table {
            for row in table {
                let args = &row[..row.len() - 1];
                let result = row[row.len() - 1];

                // Validate arguments and result
                for &arg in args {
                    if arg >= set_size {
                        return Err(UACalcError::IndexOutOfBounds {
                            index: arg,
                            size: set_size,
                        });
                    }
                }
                if result >= set_size {
                    return Err(UACalcError::IndexOutOfBounds {
                        index: result,
                        size: set_size,
                    });
                }

                // Encode arguments to index and mark as visited
                let index =
                    horner_encode(args, set_size).ok_or_else(|| UACalcError::InvalidOperation {
                        message: "Failed to encode arguments".to_string(),
                    })?;

                if visited[index] {
                    return Err(UACalcError::InvalidOperation {
                        message: format!("Duplicate entry for arguments {:?}", args),
                    });
                }

                visited[index] = true;
                flat_table.set_value(args, result)?;
            }
        }

        // Check that all entries are covered
        if !visited.iter().all(|&v| v) {
            return Err(UACalcError::InvalidOperation {
                message: format!(
                    "Table is incomplete: {} of {} entries provided",
                    visited.iter().filter(|&&v| v).count(),
                    expected_rows
                ),
            });
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
    pub fn unary<F>(name: String, set_size: usize, f: F) -> UACalcResult<Self>
    where
        F: Fn(usize) -> usize,
    {
        let mut operation = Self {
            symbol: OperationSymbol::new(name, 1),
            table: None,
            set_size,
        };

        // Build flat table
        operation.make_table(set_size)?;

        // Populate the table
        if let Some(ref mut flat_table) = operation.table {
            for i in 0..set_size {
                flat_table.set_value(&[i], f(i))?;
            }
        }

        Ok(operation)
    }

    /// Create a binary operation from a function
    pub fn binary<F>(name: String, set_size: usize, f: F) -> UACalcResult<Self>
    where
        F: Fn(usize, usize) -> usize,
    {
        let mut operation = Self {
            symbol: OperationSymbol::new(name, 2),
            table: None,
            set_size,
        };

        // Build flat table
        operation.make_table(set_size)?;

        // Populate the table
        if let Some(ref mut flat_table) = operation.table {
            for i in 0..set_size {
                for j in 0..set_size {
                    flat_table.set_value(&[i, j], f(i, j))?;
                }
            }
        }

        Ok(operation)
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
    pub fn identity(set_size: usize) -> UACalcResult<Self> {
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
        if set_size != self.set_size {
            return Err(UACalcError::InvalidOperation {
                message: format!("set_size mismatch: {} != {}", set_size, self.set_size),
            });
        }
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
    F: Fn(&[usize]) -> UACalcResult<usize> + Send + Sync + std::fmt::Debug + 'static,
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
        if set_size != self.set_size {
            return Err(UACalcError::InvalidOperation {
                message: format!("set_size mismatch: {} != {}", set_size, self.set_size),
            });
        }

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

/// Serializable operation enum that can hold different types of operations
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SerializableOperation {
    Table(TableOperation),
    // Add other operation types here as needed
}

impl SerializableOperation {
    /// Create a new table operation
    pub fn new_table(
        symbol: OperationSymbol,
        table: Vec<Vec<usize>>,
        set_size: usize,
    ) -> UACalcResult<Self> {
        Ok(Self::Table(TableOperation::new(symbol, table, set_size)?))
    }

    /// Create a constant operation
    pub fn constant(name: String, value: usize, set_size: usize) -> UACalcResult<Self> {
        Ok(Self::Table(TableOperation::constant(
            name, value, set_size,
        )?))
    }

    /// Create a unary operation from a function
    pub fn unary<F>(name: String, set_size: usize, f: F) -> UACalcResult<Self>
    where
        F: Fn(usize) -> usize,
    {
        Ok(Self::Table(TableOperation::unary(name, set_size, f)?))
    }

    /// Create a binary operation from a function
    pub fn binary<F>(name: String, set_size: usize, f: F) -> UACalcResult<Self>
    where
        F: Fn(usize, usize) -> usize,
    {
        Ok(Self::Table(TableOperation::binary(name, set_size, f)?))
    }

    /// Create an operation from a function with arbitrary arity
    pub fn from_function<F>(symbol: OperationSymbol, set_size: usize, f: F) -> UACalcResult<Self>
    where
        F: Fn(&[usize]) -> UACalcResult<usize>,
    {
        Ok(Self::Table(TableOperation::from_function(
            symbol, set_size, f,
        )?))
    }

    /// Create the identity operation
    pub fn identity(set_size: usize) -> UACalcResult<Self> {
        Ok(Self::Table(TableOperation::identity(set_size)?))
    }
}

impl Operation for SerializableOperation {
    fn arity(&self) -> usize {
        match self {
            Self::Table(op) => op.arity(),
        }
    }

    fn symbol(&self) -> &OperationSymbol {
        match self {
            Self::Table(op) => op.symbol(),
        }
    }

    fn value(&self, args: &[usize]) -> UACalcResult<usize> {
        match self {
            Self::Table(op) => op.value(args),
        }
    }

    fn int_value_at(&self, args: &[usize]) -> UACalcResult<usize> {
        match self {
            Self::Table(op) => op.int_value_at(args),
        }
    }

    fn int_value_at_index(&self, horner_index: usize) -> UACalcResult<usize> {
        match self {
            Self::Table(op) => op.int_value_at_index(horner_index),
        }
    }

    fn set_size(&self) -> usize {
        match self {
            Self::Table(op) => op.set_size(),
        }
    }

    fn make_table(&mut self, set_size: usize) -> UACalcResult<()> {
        match self {
            Self::Table(op) => op.make_table(set_size),
        }
    }

    fn get_table(&self) -> Option<&FlatOperationTable> {
        match self {
            Self::Table(op) => op.get_table(),
        }
    }

    fn operation_type(&self) -> OperationType {
        match self {
            Self::Table(op) => op.operation_type(),
        }
    }

    fn is_idempotent_on_set(&self, set_size: usize) -> UACalcResult<bool> {
        match self {
            Self::Table(op) => op.is_idempotent_on_set(set_size),
        }
    }

    fn is_associative_on_set(&self, set_size: usize) -> UACalcResult<bool> {
        match self {
            Self::Table(op) => op.is_associative_on_set(set_size),
        }
    }

    fn is_commutative_on_set(&self, set_size: usize) -> UACalcResult<bool> {
        match self {
            Self::Table(op) => op.is_commutative_on_set(set_size),
        }
    }
}

/// Similarity type - a set of operation symbols
#[derive(Debug, Clone, Hash, Serialize, Deserialize)]
pub struct SimilarityType {
    operation_symbols: Vec<OperationSymbol>,
    arities_map: Option<BTreeMap<usize, usize>>,
    max_arity: Option<usize>,
}

impl SimilarityType {
    /// Create a new similarity type from a list of operation symbols
    pub fn new(operation_symbols: Vec<OperationSymbol>) -> Self {
        Self {
            operation_symbols,
            arities_map: None,
            max_arity: None,
        }
    }

    /// Create a new similarity type with optional sorting
    pub fn new_sorted(operation_symbols: Vec<OperationSymbol>, sort: bool) -> Self {
        let mut symbols = operation_symbols;
        if sort {
            symbols.sort();
        }
        Self {
            operation_symbols: symbols,
            arities_map: None,
            max_arity: None,
        }
    }

    /// Get the operation symbols
    pub fn get_operation_symbols(&self) -> &[OperationSymbol] {
        &self.operation_symbols
    }

    /// Get sorted operation symbols (by arity descending, then by name)
    pub fn get_sorted_operation_symbols(&self) -> Vec<OperationSymbol> {
        let mut symbols = self.operation_symbols.clone();
        symbols.sort();
        symbols
    }

    /// Calculate input size for a given algebra size
    pub fn input_size(&self, alg_size: usize) -> Option<usize> {
        if self.operation_symbols.is_empty() {
            return Some(alg_size);
        }

        let mut input_size = 0u64;
        let algebra_size = alg_size as u64;
        let max_int = i32::MAX as u64;

        for symbol in &self.operation_symbols {
            let term_size = algebra_size.pow(symbol.arity() as u32);
            input_size = input_size.saturating_add(term_size);
            if input_size > max_int {
                return None; // Would overflow
            }
        }

        Some(input_size as usize)
    }

    /// Get a map from arity to number of operations of that arity
    pub fn get_arities_map(&mut self) -> &BTreeMap<usize, usize> {
        if self.arities_map.is_none() {
            let mut map = BTreeMap::new();
            let mut max_arity = 0usize;

            for symbol in &self.operation_symbols {
                let arity = symbol.arity();
                max_arity = max_arity.max(arity);
                *map.entry(arity).or_insert(0) += 1;
            }

            self.arities_map = Some(map);
            self.max_arity = Some(max_arity);
        }

        self.arities_map.as_ref().unwrap()
    }

    /// Get the maximum arity
    pub fn get_max_arity(&mut self) -> i32 {
        if self.max_arity.is_none() {
            self.get_arities_map(); // This will set max_arity
        }
        if self.operation_symbols.is_empty() {
            -1  // Match Java behavior for empty similarity types
        } else {
            self.max_arity.unwrap_or(0) as i32
        }
    }

    /// Get arities string representation
    pub fn arities_string(&mut self) -> String {
        let max_arity = self.get_max_arity();
        if max_arity == -1 {
            return String::new(); // Empty similarity type
        }
        
        let arities_map = self.get_arities_map();
        let max_arity_usize = max_arity as usize;
        
        let mut parts = Vec::new();
        for arity in (0..=max_arity_usize).rev() {
            if let Some(&count) = arities_map.get(&arity) {
                let arity_string = match arity {
                    1 => format!("unary ({})", count),
                    2 => format!("binary: ({})", count),
                    n => format!("{}-ary ({})", n, count),
                };
                parts.push(arity_string);
            }
        }
        
        parts.join(", ")
    }

    /// Get hash code
    pub fn hash_code(&self) -> i32 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.operation_symbols.hash(&mut hasher);
        (hasher.finish() as i32) & 0x7FFFFFFF
    }
}

impl PartialEq for SimilarityType {
    fn eq(&self, other: &Self) -> bool {
        if self.operation_symbols.len() != other.operation_symbols.len() {
            return false;
        }
        
        // Check if each symbol in self is contained in other
        for symbol in &self.operation_symbols {
            if !other.operation_symbols.contains(symbol) {
                return false;
            }
        }
        true
    }
}

impl Eq for SimilarityType {}

impl std::fmt::Display for SimilarityType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "(")?;
        for (i, symbol) in self.operation_symbols.iter().enumerate() {
            if i > 0 {
                write!(f, ", ")?;
            }
            write!(f, "{}", symbol)?;
        }
        write!(f, ")")
    }
}

/// Operations utility class with static factory methods
/// 
/// This class provides factory methods for creating operations, similar to the Java
/// org.uacalc.alg.op.Operations class. It includes methods for creating constant,
/// unary, binary, and random operations, as well as validation utilities.
pub struct Operations;

impl Operations {
    /// Create a constant operation that always returns the same value
    /// 
    /// # Arguments
    /// * `alg_size` - The size of the algebra (universe size)
    /// * `elt` - The constant value to return
    /// 
    /// # Returns
    /// A `TableOperation` that always returns `elt`
    pub fn make_constant_int_operation(alg_size: usize, elt: usize) -> UACalcResult<TableOperation> {
        TableOperation::constant(format!("c{}", elt), elt, alg_size)
    }

    /// Create a constant operation with a custom symbol prefix
    /// 
    /// # Arguments
    /// * `symbol_prefix` - The prefix for the operation symbol
    /// * `alg_size` - The size of the algebra (universe size)
    /// * `elt` - The constant value to return
    /// 
    /// # Returns
    /// A `TableOperation` that always returns `elt`
    pub fn make_constant_int_operation_with_prefix(
        symbol_prefix: &str,
        alg_size: usize,
        elt: usize,
    ) -> UACalcResult<TableOperation> {
        TableOperation::constant(format!("{}{}", symbol_prefix, elt), elt, alg_size)
    }

    /// Create a unary operation from a table
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `alg_size` - The size of the algebra (universe size)
    /// * `table` - The operation table as a flat array
    /// 
    /// # Returns
    /// A `TableOperation` implementing the unary operation
    pub fn make_int_operation(
        symbol: OperationSymbol,
        alg_size: usize,
        table: Vec<usize>,
    ) -> UACalcResult<TableOperation> {
        // Validate table size
        let expected_size = alg_size.pow(symbol.arity() as u32);
        if table.len() != expected_size {
            return Err(UACalcError::InvalidOperation {
                message: format!(
                    "Table size mismatch: expected {}, got {}",
                    expected_size,
                    table.len()
                ),
            });
        }

        // Validate all values are within bounds
        for &value in &table {
            if value >= alg_size {
                return Err(UACalcError::IndexOutOfBounds {
                    index: value,
                    size: alg_size,
                });
            }
        }

        let mut operation = TableOperation {
            symbol,
            table: None,
            set_size: alg_size,
        };

        // Build flat table
        operation.make_table(alg_size)?;

        // Populate the table
        if let Some(ref mut flat_table) = operation.table {
            for (i, &value) in table.iter().enumerate() {
                flat_table.set(i, value)?;
            }
        }

        Ok(operation)
    }

    /// Create a binary operation from a 2D table
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `alg_size` - The size of the algebra (universe size)
    /// * `table` - The operation table as a 2D array
    /// 
    /// # Returns
    /// A `TableOperation` implementing the binary operation
    pub fn make_binary_int_operation(
        symbol: OperationSymbol,
        alg_size: usize,
        table: Vec<Vec<usize>>,
    ) -> UACalcResult<TableOperation> {
        if symbol.arity() != 2 {
            return Err(UACalcError::InvalidOperation {
                message: format!("Expected binary operation, got arity {}", symbol.arity()),
            });
        }

        // Validate table dimensions
        if table.len() != alg_size {
            return Err(UACalcError::InvalidOperation {
                message: format!(
                    "Table height mismatch: expected {}, got {}",
                    alg_size,
                    table.len()
                ),
            });
        }

        // Flatten the 2D table
        let mut flat_table = Vec::new();
        for row in table {
            if row.len() != alg_size {
                return Err(UACalcError::InvalidOperation {
                    message: format!(
                        "Table width mismatch: expected {}, got {}",
                        alg_size,
                        row.len()
                    ),
                });
            }
            flat_table.extend(row);
        }

        Self::make_int_operation(symbol, alg_size, flat_table)
    }

    /// Create a random operation with the given symbol and set size
    /// 
    /// # Arguments
    /// * `n` - The set size
    /// * `op_sym` - The operation symbol
    /// 
    /// # Returns
    /// A `TableOperation` with random values
    pub fn make_random_operation(
        n: usize,
        op_sym: OperationSymbol,
    ) -> UACalcResult<TableOperation> {
        Self::make_random_operation_with_seed(n, op_sym, None)
    }

    /// Create a random operation with the given symbol, set size, and seed
    /// 
    /// # Arguments
    /// * `n` - The set size
    /// * `op_sym` - The operation symbol
    /// * `seed` - Optional seed for reproducible randomness
    /// 
    /// # Returns
    /// A `TableOperation` with random values
    pub fn make_random_operation_with_seed(
        n: usize,
        op_sym: OperationSymbol,
        seed: Option<u64>,
    ) -> UACalcResult<TableOperation> {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let arity = op_sym.arity();
        let table_size = n.pow(arity as u32);
        let mut values = Vec::with_capacity(table_size);

        // Create a simple pseudo-random number generator
        let mut rng_state = if let Some(s) = seed {
            s
        } else {
            // Use current time as seed
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_nanos() as u64
        };

        for _ in 0..table_size {
            // Simple linear congruential generator
            rng_state = rng_state.wrapping_mul(1103515245).wrapping_add(12345);
            values.push((rng_state % n as u64) as usize);
        }

        Self::make_int_operation(op_sym, n, values)
    }

    /// Test if an operation is idempotent
    /// 
    /// # Arguments
    /// * `op` - The operation to test
    /// 
    /// # Returns
    /// `true` if the operation is idempotent, `false` otherwise
    pub fn is_idempotent(op: &dyn Operation) -> UACalcResult<bool> {
        let set_size = op.set_size();
        let arity = op.arity();
        
        if arity == 0 {
            return Ok(true); // Constant operations are idempotent
        }

        // For each element, check if f(x, x, ..., x) = x
        for i in 0..set_size {
            let args = vec![i; arity];
            if op.value(&args)? != i {
                return Ok(false);
            }
        }
        Ok(true)
    }

    /// Test if an operation is commutative (binary operations only)
    /// 
    /// # Arguments
    /// * `op` - The operation to test
    /// 
    /// # Returns
    /// `true` if the operation is commutative, `false` otherwise
    pub fn is_commutative(op: &dyn Operation) -> UACalcResult<bool> {
        if op.arity() != 2 {
            return Ok(false); // Only binary operations can be commutative
        }

        let set_size = op.set_size();
        for i in 0..set_size {
            for j in 0..set_size {
                if op.value(&[i, j])? != op.value(&[j, i])? {
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }

    /// Test if an operation is associative (binary operations only)
    /// 
    /// # Arguments
    /// * `op` - The operation to test
    /// 
    /// # Returns
    /// `true` if the operation is associative, `false` otherwise
    pub fn is_associative(op: &dyn Operation) -> UACalcResult<bool> {
        if op.arity() != 2 {
            return Ok(false); // Only binary operations can be associative
        }

        let set_size = op.set_size();
        for i in 0..set_size {
            for j in 0..set_size {
                for k in 0..set_size {
                    let left = op.value(&[op.value(&[i, j])?, k])?;
                    let right = op.value(&[i, op.value(&[j, k])?])?;
                    if left != right {
                        return Ok(false);
                    }
                }
            }
        }
        Ok(true)
    }

    /// Test if an operation is total (always defined)
    /// 
    /// # Arguments
    /// * `op` - The operation to test
    /// 
    /// # Returns
    /// `true` if the operation is total, `false` otherwise
    pub fn is_total(op: &dyn Operation) -> bool {
        // For table-based operations, they are always total
        // This method exists for compatibility with Java interface
        true
    }

    /// Test if an operation is totally symmetric (invariant under all permutations)
    /// 
    /// # Arguments
    /// * `op` - The operation to test
    /// 
    /// # Returns
    /// `true` if the operation is totally symmetric, `false` otherwise
    pub fn is_totally_symmetric(op: &dyn Operation) -> UACalcResult<bool> {
        let arity = op.arity();
        if arity <= 1 {
            return Ok(true); // Unary and constant operations are symmetric
        }

        let set_size = op.set_size();
        
        // Generate all non-decreasing sequences of length arity
        let mut args = vec![0; arity];
        loop {
            // Check if this sequence is symmetric under all permutations
            let value = op.value(&args)?;
            
            // Generate all permutations of args and check they give the same result
            if !Self::check_permutations_symmetric(op, &args, value)? {
                return Ok(false);
            }
            
            // Move to next non-decreasing sequence
            if !Self::increment_non_decreasing(&mut args, set_size - 1) {
                break;
            }
        }
        
        Ok(true)
    }

    /// Helper function to check if all permutations of args give the same result
    fn check_permutations_symmetric(
        op: &dyn Operation,
        args: &[usize],
        expected_value: usize,
    ) -> UACalcResult<bool> {
        let mut perm_args = args.to_vec();
        
        // Generate all permutations using Heap's algorithm
        if !Self::heap_permute(op, &mut perm_args, args.len(), expected_value)? {
            return Ok(false);
        }
        
        Ok(true)
    }

    /// Heap's algorithm for generating permutations
    fn heap_permute(
        op: &dyn Operation,
        arr: &mut [usize],
        size: usize,
        expected_value: usize,
    ) -> UACalcResult<bool> {
        if size == 1 {
            return Ok(op.value(arr)? == expected_value);
        }

        for i in 0..size {
            if !Self::heap_permute(op, arr, size - 1, expected_value)? {
                return Ok(false);
            }

            if size % 2 == 1 {
                arr.swap(0, size - 1);
            } else {
                arr.swap(i, size - 1);
            }
        }
        Ok(true)
    }

    /// Helper function to increment a non-decreasing sequence
    fn increment_non_decreasing(seq: &mut [usize], max_val: usize) -> bool {
        for i in (0..seq.len()).rev() {
            if seq[i] < max_val {
                seq[i] += 1;
                // Reset all following elements to the same value
                for j in i + 1..seq.len() {
                    seq[j] = seq[i];
                }
                return true;
            }
        }
        false
    }

    /// Create a list of constant operations for all elements in the algebra
    /// 
    /// # Arguments
    /// * `alg_size` - The size of the algebra
    /// 
    /// # Returns
    /// A vector of constant operations, one for each element
    pub fn make_constant_int_operations(alg_size: usize) -> UACalcResult<Vec<TableOperation>> {
        let mut operations = Vec::with_capacity(alg_size);
        for i in 0..alg_size {
            operations.push(Self::make_constant_int_operation(alg_size, i)?);
        }
        Ok(operations)
    }
}
