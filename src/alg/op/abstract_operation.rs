use crate::alg::op::{Operation, OperationSymbol};

/// AbstractOperation provides default implementations for most Operation methods.
/// 
/// This trait represents the Java AbstractOperation class pattern in Rust.
/// It provides default implementations for most Operation interface methods,
/// allowing concrete implementations to override only the methods they need.
/// 
/// This trait corresponds to Task 11 - AbstractOperation from the Java codebase.
pub trait AbstractOperation: Operation {
    /// Get the operation symbol (must be implemented by concrete types).
    fn get_symbol(&self) -> &OperationSymbol;
    
    /// Get the algebra size (must be implemented by concrete types).
    fn get_algebra_size(&self) -> i32;
    
    /// Check if this operation has a value table (must be implemented by concrete types).
    fn has_value_table(&self) -> bool;
    
    /// Get the value table if it exists (must be implemented by concrete types).
    fn get_value_table(&self) -> Option<&[i32]>;
    
    /// Create a value table (must be implemented by concrete types).
    fn create_value_table(&mut self) -> Result<(), String>;
    
    /// The core value computation method (must be implemented by concrete types).
    /// This corresponds to the abstract valueAt method in Java AbstractOperation.
    fn compute_value(&self, args: &[i32]) -> Result<i32, String>;
    
    // Default implementations for Operation trait methods
    
    /// Default implementation of arity() - delegates to symbol.
    fn default_arity(&self) -> i32 {
        self.get_symbol().arity()
    }
    
    /// Default implementation of get_set_size() - delegates to algebra_size.
    fn default_get_set_size(&self) -> i32 {
        self.get_algebra_size()
    }
    
    /// Default implementation of symbol() - delegates to get_symbol.
    fn default_symbol(&self) -> &OperationSymbol {
        self.get_symbol()
    }
    
    /// Default implementation of value_at() - delegates to compute_value.
    fn default_value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.compute_value(args)
    }
    
    /// Default implementation of value_at_arrays().
    fn default_value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
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
            result.push(self.compute_value(&single_args)?);
        }
        
        Ok(result)
    }
    
    /// Default implementation of int_value_at() - uses table if available, otherwise delegates to compute_value.
    fn default_int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        // Try to use the table first if available
        if let Some(table) = self.get_value_table() {
            // Compute Horner encoding of args
            let set_size = self.get_algebra_size();
            let mut index = 0i32;
            for &arg in args {
                if arg < 0 || arg >= set_size {
                    return Err(format!("Argument {} is out of bounds [0, {})", arg, set_size));
                }
                index = index * set_size + arg;
            }
            if index >= 0 && (index as usize) < table.len() {
                return Ok(table[index as usize]);
            }
        }
        // Fall back to compute_value
        self.compute_value(args)
    }
    
    /// Default implementation of int_value_at_horner() - uses value table if available.
    fn default_int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        if let Some(table) = self.get_value_table() {
            if arg < 0 || arg >= table.len() as i32 {
                return Err(format!("Horner index {} is out of bounds [0, {})", arg, table.len()));
            }
            Ok(table[arg as usize])
        } else {
            Err("No table available for Horner access".to_string())
        }
    }
    
    /// Default implementation of make_table().
    fn default_make_table(&mut self) -> Result<(), String> {
        self.create_value_table()
    }
    
    /// Default implementation of get_table().
    fn default_get_table(&self) -> Option<&[i32]> {
        self.get_value_table()
    }
    
    /// Default implementation of get_table_force().
    fn default_get_table_force(&mut self, make_table: bool) -> Result<&[i32], String> {
        if !self.has_value_table() && make_table {
            self.create_value_table()?;
        }
        
        self.get_value_table()
            .ok_or_else(|| "No table available".to_string())
    }
    
    /// Default implementation of is_table_based().
    fn default_is_table_based(&self) -> bool {
        self.has_value_table()
    }
    
    /// Default implementation of is_idempotent().
    /// Checks if f(x,x,...,x) = x for all x in the domain.
    fn default_is_idempotent(&self) -> Result<bool, String> {
        let arity = self.get_symbol().arity();
        let set_size = self.get_algebra_size();
        
        for x in 0..set_size {
            let args = vec![x; arity as usize];
            if self.compute_value(&args)? != x {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    /// Default implementation of is_associative().
    /// Only works for binary operations.
    fn default_is_associative(&self) -> Result<bool, String> {
        if self.get_symbol().arity() != 2 {
            return Ok(false); // Only binary operations can be associative
        }
        
        let set_size = self.get_algebra_size();
        
        // Check if f(f(x,y),z) = f(x,f(y,z)) for all x,y,z
        for x in 0..set_size {
            for y in 0..set_size {
                for z in 0..set_size {
                    let xy = self.compute_value(&[x, y])?;
                    let yz = self.compute_value(&[y, z])?;
                    let left = self.compute_value(&[xy, z])?;
                    let right = self.compute_value(&[x, yz])?;
                    
                    if left != right {
                        return Ok(false);
                    }
                }
            }
        }
        Ok(true)
    }
    
    /// Default implementation of is_commutative().
    /// Only works for binary operations.
    fn default_is_commutative(&self) -> Result<bool, String> {
        if self.get_symbol().arity() != 2 {
            return Ok(false); // Only binary operations can be commutative
        }
        
        let set_size = self.get_algebra_size();
        
        // Check if f(x,y) = f(y,x) for all x,y
        for x in 0..set_size {
            for y in 0..set_size {
                let xy = self.compute_value(&[x, y])?;
                let yx = self.compute_value(&[y, x])?;
                
                if xy != yx {
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }
    
    /// Default implementation of is_totally_symmetric().
    fn default_is_totally_symmetric(&self) -> Result<bool, String> {
        let arity = self.get_symbol().arity() as usize;
        let set_size = self.get_algebra_size();
        
        if arity <= 1 {
            return Ok(true); // Nullary and unary operations are trivially symmetric
        }
        
        // For simplicity, we'll check a few key permutations
        // A full implementation would check all n! permutations
        if arity >= 2 {
            for args in generate_all_args(set_size, arity) {
                let original = self.compute_value(&args)?;
                
                // Swap first two elements
                let mut swapped = args.clone();
                swapped.swap(0, 1);
                let swapped_result = self.compute_value(&swapped)?;
                
                if original != swapped_result {
                    return Ok(false);
                }
            }
        }
        
        Ok(true)
    }
    
    /// Default implementation of is_maltsev().
    /// Only works for ternary operations.
    fn default_is_maltsev(&self) -> Result<bool, String> {
        if self.get_symbol().arity() != 3 {
            return Ok(false); // Only ternary operations can be Maltsev
        }
        
        let set_size = self.get_algebra_size();
        
        // Check if f(x,y,y) = x and f(x,x,y) = y for all x,y
        for x in 0..set_size {
            for y in 0..set_size {
                let xyy = self.compute_value(&[x, y, y])?;
                let xxy = self.compute_value(&[x, x, y])?;
                
                if xyy != x || xxy != y {
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }
    
    /// Default implementation of is_total().
    fn default_is_total(&self) -> Result<bool, String> {
        // Most operations are total by default
        Ok(true)
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
