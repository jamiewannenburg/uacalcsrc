use std::fmt::{Debug, Display, Formatter};
use std::hash::{Hash, Hasher};
use std::cmp::Ordering;
use crate::alg::op::{Operation, OperationSymbol};

/// AbstractOperation is a basic implementation of the Operation trait.
/// 
/// This struct provides a foundation for concrete operation implementations
/// that can be extended or used directly for testing purposes.
#[derive(Debug, Clone)]
pub struct AbstractOperation {
    symbol: OperationSymbol,
    set_size: i32,
    table: Option<Vec<i32>>,
}

impl AbstractOperation {
    /// Create a new AbstractOperation with the given symbol and set size.
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
    /// use uacalc::alg::op::{AbstractOperation, OperationSymbol};
    /// 
    /// let symbol = OperationSymbol::new("f", 2, false);
    /// let op = AbstractOperation::new(symbol, 3);
    /// assert_eq!(op.arity(), 2);
    /// assert_eq!(op.get_set_size(), 3);
    /// ```
    pub fn new(symbol: OperationSymbol, set_size: i32) -> Self {
        AbstractOperation {
            symbol,
            set_size,
            table: None,
        }
    }
    
    /// Create a new AbstractOperation with proper error handling.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `set_size` - The size of the set on which the operation is defined
    /// 
    /// # Returns
    /// * `Ok(AbstractOperation)` if successful
    /// * `Err(String)` if set_size is invalid
    pub fn new_safe(symbol: OperationSymbol, set_size: i32) -> Result<Self, String> {
        if set_size <= 0 {
            return Err("Set size must be positive".to_string());
        }
        Ok(AbstractOperation::new(symbol, set_size))
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

impl Operation for AbstractOperation {
    fn arity(&self) -> i32 {
        self.symbol.arity()
    }

    fn get_set_size(&self) -> i32 {
        self.set_size
    }

    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }

    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.int_value_at(args)
    }

    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        if args.is_empty() {
            return Err("No argument arrays provided".to_string());
        }
        
        let length = args[0].len();
        let mut result = Vec::with_capacity(length);
        
        for i in 0..length {
            let mut single_args = Vec::with_capacity(args.len());
            for arg_array in args {
                if arg_array.len() != length {
                    return Err("All argument arrays must have the same length".to_string());
                }
                single_args.push(arg_array[i]);
            }
            result.push(self.int_value_at(&single_args)?);
        }
        
        Ok(result)
    }

    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
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
    
    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        if let Some(table) = &self.table {
            if arg < 0 || arg >= table.len() as i32 {
                return Err(format!("Horner index {} is out of bounds [0, {})", arg, table.len()));
            }
            Ok(table[arg as usize])
        } else {
            Err("No table available for Horner access".to_string())
        }
    }

    fn make_table(&mut self) -> Result<(), String> {
        let table = self.create_table()?;
        self.table = Some(table);
        Ok(())
    }

    fn get_table(&self) -> Option<&[i32]> {
        self.table.as_deref()
    }
    
    fn get_table_force(&mut self, make_table: bool) -> Result<&[i32], String> {
        if self.table.is_none() && make_table {
            self.make_table()?;
        }
        
        self.table
            .as_deref()
            .ok_or_else(|| "No table available".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        self.table.is_some()
    }

    fn is_idempotent(&self) -> Result<bool, String> {
        // Check if f(x,x,...,x) = x for all x in the domain
        for x in 0..self.set_size {
            let args = vec![x; self.arity() as usize];
            if self.int_value_at(&args)? != x {
                return Ok(false);
            }
        }
        Ok(true)
    }

    fn is_associative(&self) -> Result<bool, String> {
        if self.arity() != 2 {
            return Ok(false); // Only binary operations can be associative
        }
        
        // Check if f(f(x,y),z) = f(x,f(y,z)) for all x,y,z
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                for z in 0..self.set_size {
                    let xy = self.int_value_at(&[x, y])?;
                    let yz = self.int_value_at(&[y, z])?;
                    let left = self.int_value_at(&[xy, z])?;
                    let right = self.int_value_at(&[x, yz])?;
                    
                    if left != right {
                        return Ok(false);
                    }
                }
            }
        }
        Ok(true)
    }

    fn is_commutative(&self) -> Result<bool, String> {
        if self.arity() != 2 {
            return Ok(false); // Only binary operations can be commutative
        }
        
        // Check if f(x,y) = f(y,x) for all x,y
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                let xy = self.int_value_at(&[x, y])?;
                let yx = self.int_value_at(&[y, x])?;
                
                if xy != yx {
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }

    fn is_totally_symmetric(&self) -> Result<bool, String> {
        if self.arity() <= 1 {
            return Ok(true); // Nullary and unary operations are trivially symmetric
        }
        
        // For simplicity, we'll check a few key permutations
        // A full implementation would check all n! permutations
        let arity = self.arity() as usize;
        
        // Check if swapping first two arguments gives the same result
        if arity >= 2 {
            for args in generate_all_args(self.set_size, arity) {
                let original = self.int_value_at(&args)?;
                
                // Swap first two elements
                let mut swapped = args.clone();
                swapped.swap(0, 1);
                let swapped_result = self.int_value_at(&swapped)?;
                
                if original != swapped_result {
                    return Ok(false);
                }
            }
        }
        
        Ok(true)
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        if self.arity() != 3 {
            return Ok(false); // Only ternary operations can be Maltsev
        }
        
        // Check if f(x,y,y) = x and f(x,x,y) = y for all x,y
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                let xyy = self.int_value_at(&[x, y, y])?;
                let xxy = self.int_value_at(&[x, x, y])?;
                
                if xyy != x || xxy != y {
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }
    
    fn is_total(&self) -> Result<bool, String> {
        // AbstractOperation is always total
        Ok(true)
    }
}

impl Display for AbstractOperation {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "AbstractOperation({}, size={})", self.symbol, self.set_size)
    }
}

impl PartialEq for AbstractOperation {
    fn eq(&self, other: &Self) -> bool {
        self.symbol == other.symbol && self.set_size == other.set_size
    }
}

impl Eq for AbstractOperation {}

impl PartialOrd for AbstractOperation {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for AbstractOperation {
    fn cmp(&self, other: &Self) -> Ordering {
        // First compare by symbol, then by set size
        match self.symbol.cmp(&other.symbol) {
            Ordering::Equal => self.set_size.cmp(&other.set_size),
            other => other,
        }
    }
}

impl Hash for AbstractOperation {
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