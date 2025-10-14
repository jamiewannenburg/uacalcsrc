use std::fmt::{Debug, Display, Formatter};
use std::hash::{Hash, Hasher};
use std::cmp::Ordering;
use crate::alg::op::{Operation, OperationSymbol, AbstractOperation};

/// BasicOperation is a concrete implementation of the Operation trait.
/// 
/// This struct provides a foundation for concrete operation implementations
/// that can be extended or used directly for testing purposes.
#[derive(Debug, Clone)]
pub struct BasicOperation {
    symbol: OperationSymbol,
    set_size: i32,
    table: Option<Vec<i32>>,
}

impl BasicOperation {
    /// Create a new BasicOperation with the given symbol and set size.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `set_size` - The size of the set on which the operation is defined
    /// 
    /// # Returns
    /// A new AbstractOperation instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::op::{BasicOperation, OperationSymbol};
    /// 
    /// let symbol = OperationSymbol::new("f", 2, false);
    /// let op = BasicOperation::new(symbol, 3);
    /// assert_eq!(op.arity(), 2);
    /// assert_eq!(op.get_set_size(), 3);
    /// ```
    pub fn new(symbol: OperationSymbol, set_size: i32) -> Self {
        BasicOperation {
            symbol,
            set_size,
            table: None,
        }
    }
    
    /// Create a new BasicOperation with proper error handling.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `set_size` - The size of the set on which the operation is defined
    /// 
    /// # Returns
    /// * `Ok(BasicOperation)` if successful
    /// * `Err(String)` if set_size is invalid
    pub fn new_safe(symbol: OperationSymbol, set_size: i32) -> Result<Self, String> {
        if set_size <= 0 {
            return Err("Set size must be positive".to_string());
        }
        Ok(BasicOperation::new(symbol, set_size))
    }

    /// Create a simple binary operation for testing.
    /// 
    /// This creates a simple binary operation that returns (a + b) % set_size.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// * `set_size` - The size of the set
    /// 
    /// # Returns
    /// A new AbstractOperation instance
    pub fn simple_binary_op(name: &str, set_size: i32) -> Result<Self, String> {
        let symbol = OperationSymbol::new_safe(name, 2, false)?;
        Self::new_safe(symbol, set_size)
    }

    /// Create a simple unary operation for testing.
    /// 
    /// This creates a simple unary operation that returns (a + 1) % set_size.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// * `set_size` - The size of the set
    /// 
    /// # Returns
    /// A new AbstractOperation instance
    pub fn simple_unary_op(name: &str, set_size: i32) -> Result<Self, String> {
        let symbol = OperationSymbol::new_safe(name, 1, false)?;
        Self::new_safe(symbol, set_size)
    }

    /// Create a simple nullary operation for testing.
    /// 
    /// This creates a nullary operation that returns 0.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// * `set_size` - The size of the set
    /// 
    /// # Returns
    /// A new AbstractOperation instance
    pub fn simple_nullary_op(name: &str, set_size: i32) -> Result<Self, String> {
        let symbol = OperationSymbol::new_safe(name, 0, false)?;
        Self::new_safe(symbol, set_size)
    }

    /// Create table based on the current operation's behavior.
    fn create_table(&self) -> Result<Vec<i32>, String> {
        let arity = self.arity();
        let set_size = self.set_size;
        
        if arity == 0 {
            return Ok(vec![0]); // Nullary operation always returns 0
        }
        
        let table_size = (set_size as usize).pow(arity as u32);
        let mut table = Vec::with_capacity(table_size);
        
        // Generate all possible argument combinations and compute results
        let mut args = vec![0; arity as usize];
        
        for _ in 0..table_size {
            let result = match arity {
                1 => (args[0] + 1) % set_size, // Simple unary operation
                2 => (args[0] + args[1]) % set_size, // Simple binary operation
                _ => args.iter().sum::<i32>() % set_size, // Sum for higher arity
            };
            table.push(result);
            
            // Generate next argument combination (like counting in base set_size)
            let mut carry = 1;
            for i in 0..arity as usize {
                args[i] += carry;
                if args[i] >= set_size {
                    args[i] = 0;
                } else {
                    carry = 0;
                    break;
                }
            }
        }
        
        Ok(table)
    }

    /// Compute Horner encoding for arguments.
    fn horner_encode(&self, args: &[i32]) -> i32 {
        let mut result = 0;
        let base = self.set_size;
        
        for &arg in args {
            result = result * base + arg;
        }
        
        result
    }
}

impl AbstractOperation for BasicOperation {
    fn get_symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn get_algebra_size(&self) -> i32 {
        self.set_size
    }
    
    fn has_value_table(&self) -> bool {
        self.table.is_some()
    }
    
    fn get_value_table(&self) -> Option<&[i32]> {
        self.table.as_deref()
    }
    
    fn create_value_table(&mut self) -> Result<(), String> {
        let table = self.create_table()?;
        self.table = Some(table);
        Ok(())
    }
    
    fn compute_value(&self, args: &[i32]) -> Result<i32, String> {
        if args.len() != self.arity() as usize {
            return Err(format!(
                "Expected {} arguments, got {}", 
                self.arity(), 
                args.len()
            ));
        }
        
        // Check bounds
        for &arg in args {
            if arg < 0 || arg >= self.set_size {
                return Err(format!("Argument {} is out of bounds [0, {})", arg, self.set_size));
            }
        }
        
        // Simple computation based on arity
        let result = match self.arity() {
            0 => 0, // Nullary operation returns 0
            1 => (args[0] + 1) % self.set_size, // Simple unary operation  
            2 => (args[0] + args[1]) % self.set_size, // Simple binary operation
            _ => args.iter().sum::<i32>() % self.set_size, // Sum for higher arity
        };
        
        Ok(result)
    }
}

impl Operation for BasicOperation {
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

impl Display for BasicOperation {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "BasicOperation({}, size={})", self.symbol, self.set_size)
    }
}

impl PartialEq for BasicOperation {
    fn eq(&self, other: &Self) -> bool {
        self.symbol == other.symbol && self.set_size == other.set_size
    }
}

impl Eq for BasicOperation {}

impl PartialOrd for BasicOperation {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for BasicOperation {
    fn cmp(&self, other: &Self) -> Ordering {
        // First compare by symbol, then by set size
        match self.symbol.cmp(&other.symbol) {
            Ordering::Equal => self.set_size.cmp(&other.set_size),
            other => other,
        }
    }
}

impl Hash for BasicOperation {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.symbol.hash(state);
        self.set_size.hash(state);
    }
}

/// Generate all possible argument combinations for testing.
fn generate_all_args(set_size: i32, arity: usize) -> Vec<Vec<i32>> {
    let mut result = Vec::new();
    let total_combinations = (set_size as usize).pow(arity as u32);
    
    for i in 0..total_combinations {
        let mut args = Vec::with_capacity(arity);
        let mut temp = i;
        
        for _ in 0..arity {
            args.push((temp % set_size as usize) as i32);
            temp /= set_size as usize;
        }
        
        result.push(args);
    }
    
    result
}
