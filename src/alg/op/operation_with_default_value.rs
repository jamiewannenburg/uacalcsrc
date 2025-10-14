use std::fmt::{Debug, Display, Formatter};
use std::hash::{Hash, Hasher};
use std::cmp::Ordering;
use crate::alg::op::{Operation, OperationSymbol, AbstractOperation};

/// OperationWithDefaultValue is an operation that may not be total.
/// 
/// This struct wraps an AbstractOperation and provides a default value
/// for arguments that are outside the domain of the wrapped operation.
/// This is useful for partial operations where some argument combinations
/// may not be defined.
#[derive(Debug, Clone)]
pub struct OperationWithDefaultValue {
    symbol: OperationSymbol,
    set_size: i32,
    base_operation: AbstractOperation,
    default_value: i32,
    undefined_args: std::collections::HashSet<Vec<i32>>,
}

impl OperationWithDefaultValue {
    /// Create a new OperationWithDefaultValue with the given parameters.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `set_size` - The size of the set on which the operation is defined
    /// * `base_operation` - The underlying AbstractOperation to wrap
    /// * `default_value` - The value to return for undefined arguments
    /// * `undefined_args` - Set of argument combinations that are undefined
    /// 
    /// # Returns
    /// * `Ok(OperationWithDefaultValue)` if successful
    /// * `Err(String)` if parameters are invalid
    pub fn new(
        symbol: OperationSymbol,
        set_size: i32,
        base_operation: AbstractOperation,
        default_value: i32,
        undefined_args: std::collections::HashSet<Vec<i32>>,
    ) -> Result<Self, String> {
        if set_size <= 0 {
            return Err("Set size must be positive".to_string());
        }
        
        if default_value < 0 || default_value >= set_size {
            return Err(format!(
                "Default value {} is out of range [0, {})", 
                default_value, set_size
            ));
        }
        
        if base_operation.arity() != symbol.arity() {
            return Err("Base operation arity must match symbol arity".to_string());
        }
        
        if base_operation.get_set_size() != set_size {
            return Err("Base operation set size must match".to_string());
        }
        
        Ok(OperationWithDefaultValue {
            symbol,
            set_size,
            base_operation,
            default_value,
            undefined_args,
        })
    }
    
    /// Create a partial binary operation for testing.
    /// 
    /// This creates a binary operation that is undefined for some argument pairs.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// * `set_size` - The size of the set
    /// * `default_value` - The default value for undefined cases
    /// * `undefined_pairs` - Pairs of arguments that are undefined
    /// 
    /// # Returns
    /// A new OperationWithDefaultValue instance
    pub fn partial_binary_op(
        name: &str, 
        set_size: i32, 
        default_value: i32,
        undefined_pairs: Vec<(i32, i32)>
    ) -> Result<Self, String> {
        let symbol = OperationSymbol::new_safe(name, 2, false)?;
        let base_op = AbstractOperation::simple_binary_op(name, set_size)?;
        
        let mut undefined_args = std::collections::HashSet::new();
        for (x, y) in undefined_pairs {
            undefined_args.insert(vec![x, y]);
        }
        
        Self::new(
            symbol,
            set_size,
            base_op,
            default_value,
            undefined_args,
        )
    }
    
    /// Create a partial unary operation for testing.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// * `set_size` - The size of the set
    /// * `default_value` - The default value for undefined cases
    /// * `undefined_values` - Values that are undefined
    /// 
    /// # Returns
    /// A new OperationWithDefaultValue instance
    pub fn partial_unary_op(
        name: &str,
        set_size: i32,
        default_value: i32,
        undefined_values: Vec<i32>
    ) -> Result<Self, String> {
        let symbol = OperationSymbol::new_safe(name, 1, false)?;
        let base_op = AbstractOperation::simple_unary_op(name, set_size)?;
        
        let mut undefined_args = std::collections::HashSet::new();
        for x in undefined_values {
            undefined_args.insert(vec![x]);
        }
        
        Self::new(
            symbol,
            set_size,
            base_op,
            default_value,
            undefined_args,
        )
    }

    /// Check if the given arguments are defined for this operation.
    fn is_defined(&self, args: &[i32]) -> bool {
        !self.undefined_args.contains(&args.to_vec())
    }
}

impl Operation for OperationWithDefaultValue {
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
        
        // Check if arguments are defined
        if !self.is_defined(args) {
            return Ok(self.default_value);
        }
        
        // Use base operation
        self.base_operation.int_value_at(args)
    }
    
    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        self.base_operation.int_value_at_horner(arg)
    }

    fn make_table(&mut self) -> Result<(), String> {
        // Can't make table for the base operation since we don't own it mutably
        // through the trait object
        Err("Cannot create table for OperationWithDefaultValue".to_string())
    }

    fn get_table(&self) -> Option<&[i32]> {
        self.base_operation.get_table()
    }
    
    fn get_table_force(&mut self, make_table: bool) -> Result<&[i32], String> {
        if make_table {
            return Err("Cannot create table for OperationWithDefaultValue".to_string());
        }
        self.base_operation.get_table()
            .ok_or_else(|| "No table available".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        self.base_operation.is_table_based()
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
        // This operation is not total if there are undefined arguments
        Ok(self.undefined_args.is_empty())
    }
}

impl Display for OperationWithDefaultValue {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "OperationWithDefaultValue({}, size={}, default={}, undefined={})", 
               self.symbol, self.set_size, self.default_value, self.undefined_args.len())
    }
}

impl PartialEq for OperationWithDefaultValue {
    fn eq(&self, other: &Self) -> bool {
        self.symbol == other.symbol && 
        self.set_size == other.set_size &&
        self.default_value == other.default_value &&
        self.undefined_args == other.undefined_args
        // Note: We can't compare base_operations directly since they're trait objects
    }
}

impl Eq for OperationWithDefaultValue {}

impl PartialOrd for OperationWithDefaultValue {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for OperationWithDefaultValue {
    fn cmp(&self, other: &Self) -> Ordering {
        // First compare by symbol, then by set size, then by default value
        match self.symbol.cmp(&other.symbol) {
            Ordering::Equal => match self.set_size.cmp(&other.set_size) {
                Ordering::Equal => self.default_value.cmp(&other.default_value),
                other => other,
            },
            other => other,
        }
    }
}

impl Hash for OperationWithDefaultValue {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.symbol.hash(state);
        self.set_size.hash(state);
        self.default_value.hash(state);
        // Note: We can't hash the base operation or undefined_args easily
        // This is a limitation of the current design
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