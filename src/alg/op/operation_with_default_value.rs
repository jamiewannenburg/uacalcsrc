use std::fmt::{Debug, Display, Formatter};
use std::hash::{Hash, Hasher};
use std::cmp::Ordering;
use crate::alg::op::{Operation, OperationSymbol, BasicOperation};
use crate::util::horner;

/// A convenience class for the UI that wraps operations with default value handling.
/// 
/// This struct wraps an Operation and provides default value semantics for undefined entries.
/// The default value can be:
/// - `-1`: undefined (operation is partial)
/// - `-2`: random (use random value table)
/// - `>= 0`: specific default value
#[derive(Debug)]
pub struct OperationWithDefaultValue {
    symbol: OperationSymbol,
    alg_size: i32,
    op: BasicOperation,
    value_table: Option<Vec<i32>>,
    default_value: i32,
    idempotent_set: bool,
    random_value_table: Option<Vec<i32>>,
    diag_indices: Option<Vec<usize>>,
    diag_div: usize,
}

impl OperationWithDefaultValue {
    /// Constructor 1: Create from an existing BasicOperation.
    /// 
    /// # Arguments
    /// * `op` - The operation to wrap
    /// 
    /// # Returns
    /// * `Ok(OperationWithDefaultValue)` if successful
    /// * `Err(String)` if operation is invalid
    pub fn from_operation(mut op: BasicOperation) -> Result<Self, String> {
        let symbol = op.symbol().clone();
        let alg_size = op.get_set_size();
        
        // Ensure table is created
        let _ = op.make_table(); // Ignore errors
        let value_table = op.get_table().map(|t| t.to_vec());
        
        let diag_div = Self::calculate_diag_div(symbol.arity(), alg_size);
        
        Ok(OperationWithDefaultValue {
            symbol,
            alg_size,
            op,
            value_table,
            default_value: -1,
            idempotent_set: false,
            random_value_table: None,
            diag_indices: None,
            diag_div,
        })
    }
    
    /// Constructor 2: Create with name, arity, alg_size, and default value.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation
    /// * `arity` - The arity of the operation
    /// * `alg_size` - The algebra size
    /// * `default_value` - The default value
    pub fn new_with_name(name: &str, arity: i32, alg_size: i32, default_value: i32) -> Result<Self, String> {
        if arity < 0 { return Err("Arity must be non-negative".to_string()); }
        let symbol = OperationSymbol::new_safe(name, arity, false)?;
        Self::new_with_symbol(symbol, alg_size, None, default_value)
    }
    
    /// Constructor 3: Create with symbol and alg_size.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `alg_size` - The algebra size
    pub fn new_with_symbol_and_size(symbol: OperationSymbol, alg_size: i32) -> Result<Self, String> {
        Self::new_with_symbol(symbol, alg_size, None, -1)
    }
    
    /// Constructor 4: Create with symbol, alg_size, and default value.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `alg_size` - The algebra size
    /// * `default_value` - The default value
    pub fn new_with_symbol_and_default(symbol: OperationSymbol, alg_size: i32, default_value: i32) -> Result<Self, String> {
        Self::new_with_symbol(symbol, alg_size, None, default_value)
    }
    
    /// Constructor 5: Create from operation with specific alg_size.
    /// 
    /// # Arguments
    /// * `op` - The base operation
    /// * `alg_size` - The algebra size
    pub fn from_operation_with_size(op: BasicOperation, alg_size: i32) -> Result<Self, String> {
        let symbol = op.symbol().clone();
        
        if alg_size <= 0 {
            return Err("Algebra size must be positive".to_string());
        }
        
        // Create initial value table with -1 (undefined)
        let table_size = Self::calculate_table_size(symbol.arity(), alg_size);
        let value_table = vec![-1; table_size];
        
        let diag_div = Self::calculate_diag_div(symbol.arity(), alg_size);
        
        Ok(OperationWithDefaultValue {
            symbol: symbol.clone(),
            alg_size,
            op,
            value_table: Some(value_table.clone()),
            default_value: -1,
            idempotent_set: false,
            random_value_table: None,
            diag_indices: None,
            diag_div,
        })
    }
    
    /// Constructor 6: Create with symbol, alg_size, value_table, and default value.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `alg_size` - The algebra size
    /// * `value_table` - Optional value table (None creates -1 table)
    /// * `default_value` - The default value
    pub fn new_with_symbol(
        symbol: OperationSymbol,
        alg_size: i32,
        value_table: Option<Vec<i32>>,
        default_value: i32
    ) -> Result<Self, String> {
        if alg_size <= 0 {
            return Err("Algebra size must be positive".to_string());
        }
        if symbol.arity() < 0 { return Err("Arity must be non-negative".to_string()); }
        
        let table_size = Self::calculate_table_size(symbol.arity(), alg_size);
        let value_table = if let Some(table) = value_table {
            if table.len() != table_size {
                return Err(format!(
                    "Value table size {} doesn't match expected size {}",
                    table.len(), table_size
                ));
            }
            table
        } else {
            vec![-1; table_size]
        };
        
        // Create a BasicOperation (compute-on-demand), avoid precomputing table
        let op = BasicOperation::new_safe(symbol.clone(), alg_size)?;
        
        let diag_div = Self::calculate_diag_div(symbol.arity(), alg_size);
        
        Ok(OperationWithDefaultValue {
            symbol,
            alg_size,
            op,
            value_table: Some(value_table),
            default_value,
            idempotent_set: false,
            random_value_table: None,
            diag_indices: None,
            diag_div,
        })
    }
    
    /// Calculate the table size for given arity and alg_size.
    fn calculate_table_size(arity: i32, alg_size: i32) -> usize {
        let mut size = 1;
        for _ in 0..arity {
            size *= alg_size as usize;
        }
        size
    }
    
    /// Calculate the diagonal divisor for diagonal checking.
    fn calculate_diag_div(arity: i32, alg_size: i32) -> usize {
        if arity < 3 {
            return 1;
        }
        
        let mut k = 1;
        let mut pow = alg_size as usize;
        for _ in 0..(arity - 2) {
            k += pow;
            pow *= alg_size as usize;
        }
        k
    }
    
    /// Get the default value.
    pub fn get_default_value(&self) -> i32 {
        self.default_value
    }
    
    /// Set the default value.
    pub fn set_default_value(&mut self, v: i32) {
        self.default_value = v;
    }
    
    /// Check if the idempotent flag is set.
    pub fn is_idempotent_set(&self) -> bool {
        self.idempotent_set
    }
    
    /// Set the idempotent flag and make the operation idempotent if true.
    pub fn set_idempotent(&mut self, v: bool) {
        self.idempotent_set = v;
        if v {
            self.make_idempotent();
        }
    }
    
    /// Make the operation idempotent by setting diagonal values.
    pub fn make_idempotent(&mut self) {
        // Lazy initialize diag_indices
        if self.diag_indices.is_none() {
            let arity = self.symbol.arity();
            let mut indices = Vec::with_capacity(self.alg_size as usize);
            
            for i in 0..self.alg_size {
                let diag = vec![i; arity as usize];
                let sizes = vec![self.alg_size; arity as usize];
                let index = horner::horner(&diag, &sizes);
                indices.push(index as usize);
            }
            
            self.diag_indices = Some(indices);
        }
        
        // Set diagonal values
        if let Some(ref mut table) = self.value_table {
            if let Some(ref indices) = self.diag_indices {
                for i in 0..self.alg_size as usize {
                    if i < indices.len() && indices[i] < table.len() {
                        table[indices[i]] = i as i32;
                    }
                }
            }
        }
    }
    
    /// Check if a position is on the diagonal.
    pub fn is_diagonal(&self, row: usize, col: usize) -> bool {
        row % self.diag_div == 0 && col == row / self.diag_div
    }
    
    /// Update the random value table with new random values.
    pub fn update_random_value_table(&mut self) {
        use std::collections::hash_map::RandomState;
        use std::hash::{BuildHasher, Hasher};
        
        let table_size = Self::calculate_table_size(self.symbol.arity(), self.alg_size);
        let mut random_table = Vec::with_capacity(table_size);
        
        // Use hash-based pseudo-random generation
        let random_state = RandomState::new();
        let mut hasher = random_state.build_hasher();
        
        for i in 0..table_size {
            hasher.write_usize(i);
            let hash = hasher.finish();
            let value = (hash % self.alg_size as u64) as i32;
            random_table.push(value);
        }
        
        self.random_value_table = Some(random_table);
    }
    
    /// Get the random value table, creating it if necessary.
    pub fn get_random_value_table(&mut self) -> &[i32] {
        if self.random_value_table.is_none() {
            self.update_random_value_table();
        }
        
        self.random_value_table.as_ref().unwrap()
    }
    
    /// Get value at arguments (int array version).
    /// 
    /// This matches Java's `int intValueAt(int[] args)`.
    pub fn int_value_at_array(&self, args: &[i32]) -> Result<i32, String> {
        if args.len() != self.symbol.arity() as usize {
            return Err(format!(
                "Expected {} arguments, got {}",
                self.symbol.arity(),
                args.len()
            ));
        }
        // If we have a value table, use it to detect undefined (-1) and apply defaults
        if let Some(ref table) = self.value_table {
            let index = if args.is_empty() { 0 } else {
                let sizes = vec![self.alg_size; args.len()];
                horner::horner(args, &sizes) as usize
            };
            let v = table[index];
            if v == -1 {
                if self.default_value != -2 {
                    return Ok(self.default_value);
                }
                // Random: if we have a random table use it, otherwise fall back to default
                if let Some(ref random_table) = self.random_value_table {
                    return Ok(random_table[index]);
                }
                return Ok(self.default_value);
            }
            return Ok(v);
        }
        // Fallback to base operation
        self.op.int_value_at(args)
    }
    
    /// Get value at single argument (int version).
    /// 
    /// This matches Java's `int intValueAt(int arg)`.
    pub fn int_value_at_single(&self, arg: i32) -> Result<i32, String> {
        // If we have a value table and arity is 1, use it directly by index
        if self.symbol.arity() == 1 {
            if let Some(ref table) = self.value_table {
                if arg < 0 || (arg as usize) >= table.len() {
                    return Err(format!("Argument {} is out of bounds [0, {})", arg, table.len()));
                }
                let v = table[arg as usize];
                if v == -1 {
                    if self.default_value != -2 {
                        return Ok(self.default_value);
                    }
                    if let Some(ref random_table) = self.random_value_table {
                        return Ok(random_table[arg as usize]);
                    }
                    return Ok(self.default_value);
                }
                return Ok(v);
            }
        }
        // Fallback to base operation
        self.op.int_value_at_horner(arg)
    }
    
    /// Check if the operation is total (no undefined values).
    pub fn is_total_op(&self) -> bool {
        if self.default_value >= 0 || self.default_value == -2 {
            return true;
        }
        
        if let Some(ref table) = self.value_table {
            for &v in table {
                if v < 0 {
                    return false;
                }
            }
            return true;
        }
        
        false
    }
    
    /// Get the table with default and random values filled in.
    /// 
    /// Returns None if the operation cannot be made total.
    pub fn get_total_table(&self) -> Option<Vec<i32>> {
        let table = self.value_table.as_ref()?;
        let n = table.len();
        let mut vt = Vec::with_capacity(n);
        
        for i in 0..n {
            if table[i] == -1 {
                if self.default_value == -1 {
                    return None;
                }
                if self.default_value == -2 {
                    if let Some(ref random_table) = self.random_value_table {
                        vt.push(random_table[i]);
                    } else {
                        return None;
                    }
                } else {
                    vt.push(self.default_value);
                }
            } else {
                vt.push(table[i]);
            }
        }
        
        Some(vt)
    }
    
    /// Make an ordinary operation with default value filled in.
    /// 
    /// Returns None if the defaultValue is -1 and there is a -1 in the table.
    pub fn make_ordinary_operation(&self) -> Option<crate::alg::op::IntOperation> {
        let total_table = self.get_total_table()?;
        crate::alg::op::IntOperation::new(self.symbol.clone(), self.alg_size, total_table).ok()
    }
    
    /// Static method: Convert a list of operations with default values to ordinary operations.
    /// 
    /// This replaces OperationWithDefaultValue instances with ordinary operations.
    pub fn make_ordinary_list(ops: Vec<OperationWithDefaultValue>) -> Vec<crate::alg::op::IntOperation> {
        let mut ans = Vec::with_capacity(ops.len());
        
        for op in ops {
            if let Some(ordinary_op) = op.make_ordinary_operation() {
                ans.push(ordinary_op);
            }
        }
        
        ans
    }
}

impl Operation for OperationWithDefaultValue {
    fn arity(&self) -> i32 {
        self.symbol.arity()
    }

    fn get_set_size(&self) -> i32 {
        self.alg_size
    }

    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }

    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.int_value_at_array(args)
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
            result.push(self.int_value_at_array(&single_args)?);
        }
        
        Ok(result)
    }

    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.int_value_at_array(args)
    }
    
    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        self.int_value_at_single(arg)
    }

    fn make_table(&mut self) -> Result<(), String> {
        // Try to make the operation total and update the table
        if let Some(total_table) = self.get_total_table() {
            self.value_table = Some(total_table);
            self.op.make_table()?;
            Ok(())
        } else {
            Err("Cannot create table: operation is not total".to_string())
        }
    }

    fn get_table(&self) -> Option<&[i32]> {
        self.value_table.as_deref()
    }
    
    fn get_table_force(&mut self, make_table: bool) -> Result<&[i32], String> {
        if make_table && self.value_table.is_none() {
            self.make_table()?;
        }
        self.value_table.as_deref()
            .ok_or_else(|| "No table available".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        self.value_table.is_some()
    }

    fn is_idempotent(&self) -> Result<bool, String> {
        // Check if f(x,x,...,x) = x for all x in the domain
        for x in 0..self.alg_size {
            let args = vec![x; self.arity() as usize];
            if self.int_value_at_array(&args)? != x {
                return Ok(false);
            }
        }
        Ok(true)
    }

    fn is_associative(&self) -> Result<bool, String> {
        if self.arity() != 2 {
            return Ok(false);
        }
        
        for x in 0..self.alg_size {
            for y in 0..self.alg_size {
                for z in 0..self.alg_size {
                    let xy = self.int_value_at_array(&[x, y])?;
                    let yz = self.int_value_at_array(&[y, z])?;
                    let left = self.int_value_at_array(&[xy, z])?;
                    let right = self.int_value_at_array(&[x, yz])?;
                    
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
            return Ok(false);
        }
        
        for x in 0..self.alg_size {
            for y in 0..self.alg_size {
                let xy = self.int_value_at_array(&[x, y])?;
                let yx = self.int_value_at_array(&[y, x])?;
                
                if xy != yx {
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }

    fn is_totally_symmetric(&self) -> Result<bool, String> {
        self.op.is_totally_symmetric()
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        self.op.is_maltsev()
    }
    
    fn is_total(&self) -> Result<bool, String> {
        Ok(self.is_total_op())
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        Box::new(self.clone())
    }
}

impl Display for OperationWithDefaultValue {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "OperationWithDefaultValue({}, size={}, default={})", 
               self.symbol, self.alg_size, self.default_value)
    }
}

impl PartialEq for OperationWithDefaultValue {
    fn eq(&self, other: &Self) -> bool {
        self.symbol == other.symbol && 
        self.alg_size == other.alg_size &&
        self.default_value == other.default_value &&
        self.value_table == other.value_table
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
        match self.symbol.cmp(&other.symbol) {
            Ordering::Equal => match self.alg_size.cmp(&other.alg_size) {
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
        self.alg_size.hash(state);
        self.default_value.hash(state);
    }
}

impl Clone for OperationWithDefaultValue {
    fn clone(&self) -> Self {
        OperationWithDefaultValue {
            symbol: self.symbol.clone(),
            alg_size: self.alg_size,
            op: self.op.clone(),
            value_table: self.value_table.clone(),
            default_value: self.default_value,
            idempotent_set: self.idempotent_set,
            random_value_table: self.random_value_table.clone(),
            diag_indices: self.diag_indices.clone(),
            diag_div: self.diag_div,
        }
    }
}
