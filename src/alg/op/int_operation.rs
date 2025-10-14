use std::fmt::{Debug, Display, Formatter};
use std::hash::{Hash, Hasher};
use std::cmp::Ordering;
use crate::alg::op::{Operation, OperationSymbol};

/// IntOperation is a table-based implementation of the Operation trait.
/// 
/// This struct stores the operation results in a precomputed table for fast access.
/// It's particularly useful for small operations where table lookup is more efficient
/// than computation.
#[derive(Debug, Clone)]
pub struct IntOperation {
    symbol: OperationSymbol,
    set_size: i32,
    table: Vec<i32>,
}

impl IntOperation {
    /// Create a new IntOperation with the given symbol, set size, and table.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `set_size` - The size of the set on which the operation is defined
    /// * `table` - The precomputed table of operation results
    /// 
    /// # Returns
    /// * `Ok(IntOperation)` if successful
    /// * `Err(String)` if parameters are invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::op::{IntOperation, OperationSymbol, Operation};
    /// 
    /// let symbol = OperationSymbol::new("f", 2, false);
    /// // Binary operation on {0,1} where f(0,0)=0, f(0,1)=1, f(1,0)=1, f(1,1)=0 (XOR)
    /// let table = vec![0, 1, 1, 0];
    /// let op = IntOperation::new(symbol, 2, table).unwrap();
    /// assert_eq!(op.arity(), 2);
    /// assert_eq!(op.get_set_size(), 2);
    /// ```
    pub fn new(symbol: OperationSymbol, set_size: i32, table: Vec<i32>) -> Result<Self, String> {
        if set_size <= 0 {
            return Err("Set size must be positive".to_string());
        }
        
        let expected_size = if symbol.arity() == 0 {
            1
        } else {
            (set_size as usize).pow(symbol.arity() as u32)
        };
        
        if table.len() != expected_size {
            return Err(format!(
                "Table size {} doesn't match expected size {} for arity {} and set size {}",
                table.len(), expected_size, symbol.arity(), set_size
            ));
        }
        
        // Validate table values are in range
        for (i, &value) in table.iter().enumerate() {
            if value < 0 || value >= set_size {
                return Err(format!(
                    "Table value {} at index {} is out of range [0, {})",
                    value, i, set_size
                ));
            }
        }
        
        Ok(IntOperation {
            symbol,
            set_size,
            table,
        })
    }
    
    /// Create a simple binary XOR operation for testing.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// 
    /// # Returns
    /// A new IntOperation implementing XOR on {0, 1}
    pub fn binary_xor(name: &str) -> Result<Self, String> {
        let symbol = OperationSymbol::new_safe(name, 2, false)?;
        let table = vec![0, 1, 1, 0]; // XOR truth table
        Self::new(symbol, 2, table)
    }
    
    /// Create a simple binary AND operation for testing.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// 
    /// # Returns
    /// A new IntOperation implementing AND on {0, 1}
    pub fn binary_and(name: &str) -> Result<Self, String> {
        let symbol = OperationSymbol::new_safe(name, 2, false)?;
        let table = vec![0, 0, 0, 1]; // AND truth table
        Self::new(symbol, 2, table)
    }
    
    /// Create a simple binary OR operation for testing.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// 
    /// # Returns
    /// A new IntOperation implementing OR on {0, 1}
    pub fn binary_or(name: &str) -> Result<Self, String> {
        let symbol = OperationSymbol::new_safe(name, 2, false)?;
        let table = vec![0, 1, 1, 1]; // OR truth table
        Self::new(symbol, 2, table)
    }
    
    /// Create a unary NOT operation for testing.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// 
    /// # Returns
    /// A new IntOperation implementing NOT on {0, 1}
    pub fn unary_not(name: &str) -> Result<Self, String> {
        let symbol = OperationSymbol::new_safe(name, 1, false)?;
        let table = vec![1, 0]; // NOT truth table
        Self::new(symbol, 2, table)
    }

    /// Create a nullary constant operation for testing.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// * `constant_value` - The constant value to return
    /// 
    /// # Returns
    /// A new IntOperation returning the constant value
    pub fn nullary_constant(name: &str, constant_value: i32) -> Result<Self, String> {
        let symbol = OperationSymbol::new_safe(name, 0, false)?;
        let table = vec![constant_value];
        // Set size is constant_value + 1 to ensure the constant is in range
        Self::new(symbol, constant_value + 1, table)
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

impl Operation for IntOperation {
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
        
        // Use table lookup
        let index = self.horner_encode(args);
        if index < 0 || index >= self.table.len() as i32 {
            return Err(format!("Computed index {} is out of table bounds", index));
        }
        
        Ok(self.table[index as usize])
    }
    
    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        if arg < 0 || arg >= self.table.len() as i32 {
            return Err(format!("Horner index {} is out of bounds [0, {})", arg, self.table.len()));
        }
        Ok(self.table[arg as usize])
    }

    fn make_table(&mut self) -> Result<(), String> {
        // Table already exists, no need to create
        Ok(())
    }

    fn get_table(&self) -> Option<&[i32]> {
        Some(&self.table)
    }
    
    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32], String> {
        // Table always exists for IntOperation
        Ok(&self.table)
    }
    
    fn is_table_based(&self) -> bool {
        true // IntOperation is always table-based
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
        // IntOperation is always total
        Ok(true)
    }
}

impl Display for IntOperation {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "IntOperation({}, size={}, table_size={})", 
               self.symbol, self.set_size, self.table.len())
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

impl PartialOrd for IntOperation {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for IntOperation {
    fn cmp(&self, other: &Self) -> Ordering {
        // First compare by symbol, then by set size, then by table
        match self.symbol.cmp(&other.symbol) {
            Ordering::Equal => match self.set_size.cmp(&other.set_size) {
                Ordering::Equal => self.table.cmp(&other.table),
                other => other,
            },
            other => other,
        }
    }
}

impl Hash for IntOperation {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.symbol.hash(state);
        self.set_size.hash(state);
        self.table.hash(state);
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
