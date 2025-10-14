use std::fmt::{Debug, Display, Formatter};
use std::hash::{Hash, Hasher};
use std::cmp::Ordering;
use crate::alg::op::{Operation, OperationSymbol, AbstractOperation};

/// AbstractIntOperation is a minimal concrete operation for Jython/Groovy compatibility.
/// 
/// This class corresponds to Task 13 - AbstractIntOperation from the Java codebase.
/// Despite its name containing "Abstract", this is actually a concrete class that can be
/// instantiated. It's designed for Jython/Groovy compatibility and most methods throw
/// UnsupportedOperationException to indicate they must be overridden by subclasses.
/// 
/// # Examples
/// ```
/// use uacalc::alg::op::{AbstractIntOperation, OperationSymbol, Operation, AbstractOperation};
/// 
/// let symbol = OperationSymbol::new("test", 2, false);
/// let op = AbstractIntOperation::new_with_symbol(symbol, 3);
/// assert_eq!(op.arity(), 2);
/// assert_eq!(op.get_set_size(), 3);
/// 
/// // This will return an error since it's not implemented
/// let result = op.compute_value(&[0, 1]);
/// assert!(result.is_err());
/// ```
#[derive(Debug, Clone)]
pub struct AbstractIntOperation {
    symbol: OperationSymbol,
    alg_size: i32,
}

impl AbstractIntOperation {
    /// Create a new AbstractIntOperation with a name, arity, and algebra size.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// * `arity` - The arity (number of arguments) of the operation
    /// * `alg_size` - The size of the algebra set
    /// 
    /// # Returns
    /// A new AbstractIntOperation instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::op::{AbstractIntOperation, Operation};
    /// 
    /// let op = AbstractIntOperation::new("add", 2, 5);
    /// assert_eq!(op.arity(), 2);
    /// assert_eq!(op.get_set_size(), 5);
    /// ```
    pub fn new(name: &str, arity: i32, alg_size: i32) -> Self {
        let symbol = OperationSymbol::new(name, arity, false);
        AbstractIntOperation {
            symbol,
            alg_size,
        }
    }
    
    /// Create a new AbstractIntOperation with proper error handling.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// * `arity` - The arity (number of arguments) of the operation
    /// * `alg_size` - The size of the algebra set
    /// 
    /// # Returns
    /// * `Ok(AbstractIntOperation)` if successful
    /// * `Err(String)` if parameters are invalid
    pub fn new_safe(name: &str, arity: i32, alg_size: i32) -> Result<Self, String> {
        if alg_size <= 0 {
            return Err("Algebra size must be positive".to_string());
        }
        
        if arity < 0 {
            return Err("Arity must be non-negative".to_string());
        }
        
        let symbol = OperationSymbol::new_safe(name, arity, false)?;
        Ok(AbstractIntOperation {
            symbol,
            alg_size,
        })
    }
    
    /// Create a new AbstractIntOperation with an existing OperationSymbol.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `alg_size` - The size of the algebra set
    /// 
    /// # Returns
    /// A new AbstractIntOperation instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::op::{AbstractIntOperation, OperationSymbol, Operation};
    /// 
    /// let symbol = OperationSymbol::new("mult", 2, false);
    /// let op = AbstractIntOperation::new_with_symbol(symbol, 3);
    /// assert_eq!(op.arity(), 2);
    /// assert_eq!(op.get_set_size(), 3);
    /// ```
    pub fn new_with_symbol(symbol: OperationSymbol, alg_size: i32) -> Self {
        AbstractIntOperation {
            symbol,
            alg_size,
        }
    }
    
    /// Create a new AbstractIntOperation with an existing OperationSymbol and error handling.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `alg_size` - The size of the algebra set
    /// 
    /// # Returns
    /// * `Ok(AbstractIntOperation)` if successful
    /// * `Err(String)` if alg_size is invalid
    pub fn new_with_symbol_safe(symbol: OperationSymbol, alg_size: i32) -> Result<Self, String> {
        if alg_size <= 0 {
            return Err("Algebra size must be positive".to_string());
        }
        
        Ok(AbstractIntOperation {
            symbol,
            alg_size,
        })
    }
}

impl Operation for AbstractIntOperation {
    fn arity(&self) -> i32 {
        self.default_arity()
    }

    fn get_set_size(&self) -> i32 {
        self.default_get_set_size()
    }

    fn symbol(&self) -> &OperationSymbol {
        self.default_symbol()
    }

    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.default_value_at(args)
    }

    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        self.default_value_at_arrays(args)
    }

    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.default_int_value_at(args)
    }
    
    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        self.default_int_value_at_horner(arg)
    }

    fn make_table(&mut self) -> Result<(), String> {
        self.default_make_table()
    }

    fn get_table(&self) -> Option<&[i32]> {
        self.default_get_table()
    }
    
    fn get_table_force(&mut self, make_table: bool) -> Result<&[i32], String> {
        self.default_get_table_force(make_table)
    }
    
    fn is_table_based(&self) -> bool {
        self.default_is_table_based()
    }

    fn is_idempotent(&self) -> Result<bool, String> {
        self.default_is_idempotent()
    }

    fn is_associative(&self) -> Result<bool, String> {
        self.default_is_associative()
    }

    fn is_commutative(&self) -> Result<bool, String> {
        self.default_is_commutative()
    }

    fn is_totally_symmetric(&self) -> Result<bool, String> {
        self.default_is_totally_symmetric()
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        self.default_is_maltsev()
    }
    
    fn is_total(&self) -> Result<bool, String> {
        self.default_is_total()
    }
}

impl AbstractOperation for AbstractIntOperation {
    fn get_symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn get_algebra_size(&self) -> i32 {
        self.alg_size
    }
    
    fn has_value_table(&self) -> bool {
        false // No table by default
    }
    
    fn get_value_table(&self) -> Option<&[i32]> {
        None // No table by default
    }
    
    fn create_value_table(&mut self) -> Result<(), String> {
        Err("UnsupportedOperationException: Table creation not supported".to_string())
    }
    
    /// The core compute_value method throws UnsupportedOperationException.
    /// This matches the Java behavior where valueAt() throws UnsupportedOperationException.
    /// Subclasses are expected to override this method with actual computation logic.
    fn compute_value(&self, _args: &[i32]) -> Result<i32, String> {
        Err("UnsupportedOperationException: compute_value must be implemented by subclasses".to_string())
    }
}

impl Display for AbstractIntOperation {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "AbstractIntOperation({}, size={})", self.symbol, self.alg_size)
    }
}

impl PartialEq for AbstractIntOperation {
    fn eq(&self, other: &Self) -> bool {
        self.symbol == other.symbol && self.alg_size == other.alg_size
    }
}

impl Eq for AbstractIntOperation {}

impl PartialOrd for AbstractIntOperation {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for AbstractIntOperation {
    fn cmp(&self, other: &Self) -> Ordering {
        // First compare by symbol, then by algebra size
        match self.symbol.cmp(&other.symbol) {
            Ordering::Equal => self.alg_size.cmp(&other.alg_size),
            other => other,
        }
    }
}

impl Hash for AbstractIntOperation {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.symbol.hash(state);
        self.alg_size.hash(state);
    }
}
