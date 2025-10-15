use std::collections::HashMap;
use std::sync::Arc;
use crate::alg::op::{Operation, OperationSymbol, IntOperation, SimilarityType};
use crate::util::horner;
use crate::util::array_string as ArrayString;

/// Operations is a factory module with static methods to make and test Operations.
/// 
/// This module provides factory methods for creating various types of operations,
/// as well as testing methods for checking properties of operations (commutativity,
/// associativity, idempotence, etc.).

// =============================================================================
// Testing Methods
// =============================================================================

/// Test if a unary operation commutes with another operation.
/// This can be used to test if an operation is an endomorphism (or automorphism).
///
/// # Arguments
/// * `unary_op` - The unary operation to test
/// * `op` - The operation to test against
///
/// # Returns
/// `true` if the operations commute, `false` otherwise
pub fn commutes_unary(unary_op: &dyn Operation, op: &dyn Operation) -> Result<bool, String> {
    if unary_op.arity() != 1 {
        return Err("First operation must be unary".to_string());
    }
    
    let set_size = op.get_set_size();
    if unary_op.get_set_size() != set_size {
        return Err("Operations must have the same set size".to_string());
    }
    
    let arity = op.arity() as usize;
    let total = (set_size as usize).pow(arity as u32);
    
    for idx in 0..total {
        let arr = horner::horner_inv_same_size(idx as i32, set_size, arity);
        let result = op.int_value_at(&arr)?;
        let v = unary_op.int_value_at(&[result])?;
        
        let mut image_arr = vec![0i32; arity];
        for i in 0..arity {
            image_arr[i] = unary_op.int_value_at(&[arr[i]])?;
        }
        
        if op.int_value_at(&image_arr)? != v {
            return Ok(false);
        }
    }
    
    Ok(true)
}

/// Test if a map defines a homomorphism with respect to these operations.
/// The operations must have the same arity.
///
/// # Arguments
/// * `map` - An array defining the map
/// * `op0` - The first operation
/// * `op1` - The second operation
///
/// # Returns
/// `true` if the map is a homomorphism, `false` otherwise
pub fn commutes_map(map: &[i32], op0: &dyn Operation, op1: &dyn Operation) -> Result<bool, String> {
    if op0.arity() != op1.arity() {
        return Err("Operations must have the same arity".to_string());
    }
    
    let set_size = op0.get_set_size();
    let arity = op0.arity() as usize;
    let total = (set_size as usize).pow(arity as u32);
    
    for idx in 0..total {
        let arr = horner::horner_inv_same_size(idx as i32, set_size, arity);
        let result = op0.int_value_at(&arr)?;
        let v = map[result as usize];
        
        let mut image_arr = vec![0i32; arity];
        for i in 0..arity {
            image_arr[i] = map[arr[i] as usize];
        }
        
        if op1.int_value_at(&image_arr)? != v {
            return Ok(false);
        }
    }
    
    Ok(true)
}

/// Test if an operation is total.
pub fn is_total(op: &dyn Operation) -> Result<bool, String> {
    op.is_total()
}

/// Test if an operation is idempotent: f(x,x,...,x) = x for all x.
pub fn is_idempotent(op: &dyn Operation) -> Result<bool, String> {
    op.is_idempotent()
}

/// Test if an operation is binary and commutative.
pub fn is_commutative(op: &dyn Operation) -> Result<bool, String> {
    if op.arity() != 2 {
        return Ok(false);
    }
    is_totally_symmetric(op)
}

/// Test if an operation is totally symmetric (invariant under all permutations of variables).
pub fn is_totally_symmetric(op: &dyn Operation) -> Result<bool, String> {
    op.is_totally_symmetric()
}

/// Test if an operation is binary and associative.
pub fn is_associative(op: &dyn Operation) -> Result<bool, String> {
    op.is_associative()
}

/// Check if a ternary operation is a Maltsev operation.
/// A Maltsev operation satisfies: f(x,y,y) = x and f(x,x,y) = y for all x,y.
pub fn is_maltsev(op: &dyn Operation) -> Result<bool, String> {
    op.is_maltsev()
}

/// Find the first argument combination where two operations differ.
///
/// # Arguments
/// * `op0` - The first operation
/// * `op1` - The second operation
///
/// # Returns
/// * `Some(args)` - The first argument combination where the operations differ
/// * `None` - If the operations are equal
pub fn find_difference(op0: &dyn Operation, op1: &dyn Operation) -> Result<Option<Vec<i32>>, String> {
    if op0.arity() != op1.arity() {
        return Err("Operations must have the same arity".to_string());
    }
    if op0.get_set_size() != op1.get_set_size() {
        return Err("Operations must have the same set size".to_string());
    }
    
    let set_size = op0.get_set_size();
    let arity = op0.arity() as usize;
    let total = (set_size as usize).pow(arity as u32);
    
    for idx in 0..total {
        let arr = horner::horner_inv_same_size(idx as i32, set_size, arity);
        if op0.int_value_at(&arr)? != op1.int_value_at(&arr)? {
            return Ok(Some(arr));
        }
    }
    
    Ok(None)
}

/// Test if two operations have the same int values on the common sized set.
/// They may have different symbols.
pub fn equal_values(op0: &dyn Operation, op1: &dyn Operation) -> Result<bool, String> {
    Ok(find_difference(op0, op1)?.is_none())
}

// =============================================================================
// Additional Constructors (matching Java public API)
// =============================================================================

/// Make Jónsson operations from a near-unanimity function (placeholder).
/// Returns an empty list for now until full algorithm is implemented.
pub fn make_jonsson_operations_from_nuf(_nuf: &dyn Operation) -> Result<Vec<Box<dyn Operation>>, String> {
    Ok(Vec::new())
}

/// Make a left shift unary operation on vectors of given size (deterministic placeholder).
pub fn make_left_shift(vec_size: i32, _root_size: i32) -> Result<Box<dyn Operation>, String> {
    let sym = OperationSymbol::new_safe("leftShift", 1, false)?;
    let mut table = Vec::with_capacity(vec_size as usize);
    for i in 0..vec_size { table.push((i + 1) % vec_size); }
    make_int_operation(sym, vec_size, table)
}

/// Make a binary left shift operation (deterministic placeholder).
pub fn make_binary_left_shift(vec_size: i32, _root_size: i32) -> Result<Box<dyn Operation>, String> {
    let sym = OperationSymbol::new_safe("binaryLeftShift", 2, false)?;
    let mut table = Vec::with_capacity((vec_size * vec_size) as usize);
    for i in 0..vec_size { for j in 0..vec_size { table.push((i + j) % vec_size); } }
    make_int_operation(sym, vec_size, table)
}

/// Make a matrix diagonal operation (deterministic placeholder; arity 2).
pub fn make_matrix_diagonal_op(vec_size: i32, _root_size: i32) -> Result<Box<dyn Operation>, String> {
    let sym = OperationSymbol::new_safe("matrixDiagonal", 2, false)?;
    let mut table = Vec::with_capacity((vec_size * vec_size) as usize);
    for i in 0..vec_size { for j in 0..vec_size { table.push(if i == j { i } else { 0 }); } }
    make_int_operation(sym, vec_size, table)
}

/// Make a module operation with the given modulus and coefficients: f(x1,...,xk) = sum c_i x_i (mod m).
pub fn make_module_operation(modulus: i32, coeffs: &[i32]) -> Result<Box<dyn Operation>, String> {
    if modulus <= 0 { return Err("Modulus must be positive".to_string()); }
    let arity = coeffs.len() as i32;
    let sym = OperationSymbol::new_safe("module", arity, false)?;
    let table_size = (modulus as usize).pow(arity as u32);
    let mut table = Vec::with_capacity(table_size);
    for k in 0..table_size {
        let args = horner::horner_inv_same_size(k as i32, modulus, arity as usize);
        let mut acc = 0i32;
        for i in 0..arity as usize {
            acc = (acc + coeffs[i] * args[i]) % modulus;
        }
        table.push((acc + modulus) % modulus);
    }
    make_int_operation(sym, modulus, table)
}

/// Make a composition operation (placeholder): unary op f(x) = (x + pow) mod n.
pub fn make_composition_op(n: i32, pow: i32) -> Result<Box<dyn Operation>, String> {
    if n <= 0 { return Err("Set size must be positive".to_string()); }
    let sym = OperationSymbol::new_safe("composition", 1, false)?;
    let mut table = Vec::with_capacity(n as usize);
    for i in 0..n { table.push((i + pow).rem_euclid(n)); }
    make_int_operation(sym, n, table)
}

// =============================================================================
// Factory Methods - Basic Operations
// =============================================================================

/// Construct an Operation from a value table.
///
/// # Arguments
/// * `symbol` - The operation symbol (name and arity)
/// * `alg_size` - The algebra size
/// * `value_table` - A Horner-encoded table of the values of the operation
///
/// # Returns
/// A new IntOperation with the given table
pub fn make_int_operation(
    symbol: OperationSymbol,
    alg_size: i32,
    value_table: Vec<i32>,
) -> Result<Box<dyn Operation>, String> {
    let op = IntOperation::new(symbol, alg_size, value_table)?;
    Ok(Box::new(op))
}

/// Construct an Operation from a value table with a string symbol name.
pub fn make_int_operation_str(
    symbol: &str,
    arity: i32,
    alg_size: i32,
    value_table: Vec<i32>,
) -> Result<Box<dyn Operation>, String> {
    let sym = OperationSymbol::new_safe(symbol, arity, false)?;
    make_int_operation(sym, alg_size, value_table)
}

/// Construct a binary operation from a 2D table.
///
/// # Arguments
/// * `symbol` - The operation symbol
/// * `alg_size` - The algebra size
/// * `table` - A 2D table where table[i][j] = f(i,j)
pub fn make_binary_int_operation(
    symbol: OperationSymbol,
    alg_size: i32,
    table: Vec<Vec<i32>>,
) -> Result<Box<dyn Operation>, String> {
    if symbol.arity() != 2 {
        return Err("Symbol must have arity 2 for binary operation".to_string());
    }
    
    let mut value_table = Vec::with_capacity((alg_size * alg_size) as usize);
    for i in 0..alg_size {
        if table[i as usize].len() != alg_size as usize {
            return Err(format!("Row {} has incorrect length", i));
        }
        for j in 0..alg_size {
            value_table.push(table[i as usize][j as usize]);
        }
    }
    
    make_int_operation(symbol, alg_size, value_table)
}

/// Make a constant (nullary) integer operation.
///
/// # Arguments
/// * `alg_size` - The algebra size
/// * `elt` - The constant element to return
pub fn make_constant_int_operation(alg_size: i32, elt: i32) -> Result<Box<dyn Operation>, String> {
    make_constant_int_operation_with_prefix("c", alg_size, elt)
}

/// Make a constant (nullary) integer operation with a custom symbol prefix.
pub fn make_constant_int_operation_with_prefix(
    symbol_prefix: &str,
    alg_size: i32,
    elt: i32,
) -> Result<Box<dyn Operation>, String> {
    if elt < 0 || elt >= alg_size {
        return Err(format!("Element {} out of range [0, {})", elt, alg_size));
    }
    
    let sym = OperationSymbol::new_safe(&format!("{}{}", symbol_prefix, elt), 0, false)?;
    let value_table = vec![elt];
    make_int_operation(sym, alg_size, value_table)
}

/// Make all constant (nullary) operations for the given algebra size.
pub fn make_constant_int_operations(alg_size: i32) -> Result<Vec<Box<dyn Operation>>, String> {
    let mut ops = Vec::with_capacity(alg_size as usize);
    for i in 0..alg_size {
        ops.push(make_constant_int_operation(alg_size, i)?);
    }
    Ok(ops)
}

/// Make a unary operation that transposes (swaps) two elements.
///
/// # Arguments
/// * `alg_size` - The algebra size
/// * `a0` - The first element to swap
/// * `a1` - The second element to swap
pub fn make_transposition(alg_size: i32, a0: i32, a1: i32) -> Result<Box<dyn Operation>, String> {
    if a0 < 0 || a0 >= alg_size || a1 < 0 || a1 >= alg_size {
        return Err("Elements out of range".to_string());
    }
    
    let sym = OperationSymbol::new_safe(&format!("transposition{}-{}", a0, a1), 1, false)?;
    let mut value_table = Vec::with_capacity(alg_size as usize);
    
    for i in 0..alg_size {
        if i == a0 {
            value_table.push(a1);
        } else if i == a1 {
            value_table.push(a0);
        } else {
            value_table.push(i);
        }
    }
    
    make_int_operation(sym, alg_size, value_table)
}

/// Make a unary operation that is a full cycle: f(x) = (x + 1) mod alg_size.
pub fn make_full_cycle(alg_size: i32) -> Result<Box<dyn Operation>, String> {
    let sym = OperationSymbol::new_safe(&format!("cycle{}", alg_size), 1, false)?;
    let mut value_table = Vec::with_capacity(alg_size as usize);
    
    for i in 0..alg_size {
        value_table.push((i + 1) % alg_size);
    }
    
    make_int_operation(sym, alg_size, value_table)
}

// =============================================================================
// Factory Methods - Random Operations
// =============================================================================

/// Make a random operation with the given operation symbol and set size.
///
/// # Arguments
/// * `n` - The set size
/// * `op_sym` - The operation symbol
///
/// # Returns
/// A new random operation
///
/// Note: This function is not deterministic as it uses a random seed.
/// For reproducible results, use make_random_operations_with_seed.
pub fn make_random_operation(n: i32, op_sym: OperationSymbol) -> Result<Box<dyn Operation>, String> {
    // Simple deterministic "random" based on operation name hash for now
    // In Java this uses Random without a seed, which is non-deterministic
    let seed = op_sym.name().bytes().fold(0u64, |acc, b| acc.wrapping_mul(31).wrapping_add(b as u64));
    make_random_operation_with_seed(n, op_sym, seed)
}

/// Make a random operation with a specific seed.
pub fn make_random_operation_with_seed(
    n: i32,
    op_sym: OperationSymbol,
    seed: u64,
) -> Result<Box<dyn Operation>, String> {
    let arity = op_sym.arity();
    let table_size = (n as usize).pow(arity as u32);
    
    // Simple LCG (Linear Congruential Generator) for deterministic randomness
    let mut rng_state = seed;
    let mut values = Vec::with_capacity(table_size);
    for _ in 0..table_size {
        rng_state = rng_state.wrapping_mul(1103515245).wrapping_add(12345);
        values.push(((rng_state / 65536) % (n as u64)) as i32);
    }
    
    make_int_operation(op_sym, n, values)
}

/// Make a list of random operations corresponding to a similarity type and set size.
///
/// # Arguments
/// * `n` - The set size
/// * `sim_type` - The similarity type
///
/// # Returns
/// A list of random operations
pub fn make_random_operations(
    n: i32,
    sim_type: &SimilarityType,
) -> Result<Vec<Box<dyn Operation>>, String> {
    make_random_operations_with_seed(n, sim_type, None)
}

/// Make a list of random operations with an optional seed.
pub fn make_random_operations_with_seed(
    n: i32,
    sim_type: &SimilarityType,
    seed: Option<u64>,
) -> Result<Vec<Box<dyn Operation>>, String> {
    let base_seed = seed.unwrap_or(12345);
    
    let op_syms = sim_type.get_operation_symbols();
    let mut ops = Vec::with_capacity(op_syms.len());
    
    for (i, op_sym) in op_syms.iter().enumerate() {
        let op_seed = base_seed.wrapping_add(i as u64);
        ops.push(make_random_operation_with_seed(n, op_sym.clone(), op_seed)?);
    }
    
    Ok(ops)
}

// =============================================================================
// Factory Methods - Derived and Special Operations
// =============================================================================

/// Create an operation derived by equating variables.
///
/// If f(x,y,z) is an operation and [1, 0, 1] is the reduction_array,
/// then the derived operation is g(x,y) = f(y,x,y).
///
/// # Arguments
/// * `op` - The base operation
/// * `reduction_array` - Maps indices of the new operation to indices of the old operation
/// * `new_arity` - The arity of the derived operation
pub fn make_derived_operation(
    op: Arc<dyn Operation>,
    reduction_array: Vec<i32>,
    new_arity: i32,
) -> Result<Box<dyn Operation>, String> {
    let big_arity = op.arity();
    let alg_size = op.get_set_size();
    
    // Validate reduction_array bounds
    for &idx in &reduction_array {
        if idx < 0 || idx >= new_arity {
            return Err(format!("reduction_array contains invalid index {} (must be 0 <= index < {})", idx, new_arity));
        }
    }
    
    // Calculate table for the derived operation
    let table_size = (alg_size as usize).pow(new_arity as u32);
    let mut value_table = Vec::with_capacity(table_size);
    
    // Use Horner utility for robust argument enumeration
    for k in 0..table_size {
        let new_args = horner::horner_inv_same_size(k as i32, alg_size, new_arity as usize);
        let mut big_args = vec![0i32; big_arity as usize];
        
        // Map new arguments to old arguments using reduction_array
        for i in 0..big_arity as usize {
            big_args[i] = new_args[reduction_array[i] as usize];
        }
        
        value_table.push(op.int_value_at(&big_args)?);
    }
    
    let name = format!("{}_derived{}", op.symbol().name(), ArrayString::to_string(&reduction_array));
    let sym = OperationSymbol::new_safe(&name, new_arity, false)?;
    make_int_operation(sym, alg_size, value_table)
}

/// Create a ternary discriminator operation.
/// The discriminator satisfies: d(x,y,z) = z if x = y, otherwise x.
pub fn ternary_discriminator(size: i32) -> Result<Box<dyn Operation>, String> {
    let sym = OperationSymbol::new_safe("disc", 3, false)?;
    let table_size = (size as usize).pow(3);
    let mut value_table = Vec::with_capacity(table_size);
    
    for x in 0..size {
        for y in 0..size {
            for z in 0..size {
                if x == y {
                    value_table.push(z);
                } else {
                    value_table.push(x);
                }
            }
        }
    }
    
    make_int_operation(sym, size, value_table)
}

// =============================================================================
// Utility Methods
// =============================================================================

/// Create a hash map from operation symbols to operations.
pub fn make_map(ops: &[Box<dyn Operation>]) -> HashMap<OperationSymbol, usize> {
    let mut map = HashMap::with_capacity(ops.len());
    for (i, op) in ops.iter().enumerate() {
        map.insert(op.symbol().clone(), i);
    }
    map
}

/// Compute base^pow using integer exponentiation.
pub fn power(base: i32, pow: i32) -> i32 {
    let mut ans = 1;
    for _ in 0..pow {
        ans *= base;
    }
    ans
}

/// Convert a list of operations to use IntOperation internally.
pub fn make_int_operations(ops: Vec<Box<dyn Operation>>) -> Result<Vec<Box<dyn Operation>>, String> {
    let mut result = Vec::with_capacity(ops.len());
    
    for op in ops {
        // If it already has a table, use it directly
        if let Some(table) = op.get_table() {
            let new_op = make_int_operation(op.symbol().clone(), op.get_set_size(), table.to_vec())?;
            result.push(new_op);
        } else {
            // Generate the table
            let arity = op.arity();
            let set_size = op.get_set_size();
            let table_size = (set_size as usize).pow(arity as u32);
            let mut table = Vec::with_capacity(table_size);
            
            for i in 0..table_size {
                let args = horner::horner_inv_same_size(i as i32, set_size, arity as usize);
                table.push(op.int_value_at(&args)?);
            }
            
            let new_op = make_int_operation(op.symbol().clone(), set_size, table)?;
            result.push(new_op);
        }
    }
    
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_idempotent() {
        // Create a projection operation (idempotent)
        let sym = OperationSymbol::new("proj", 2, false);
        let table = vec![0, 0, 1, 1]; // f(x,y) = x
        let op = IntOperation::new(sym, 2, table).unwrap();
        assert!(is_idempotent(&op).unwrap());
    }

    #[test]
    fn test_is_commutative() {
        // Create an XOR operation (commutative)
        let op = IntOperation::binary_xor("xor").unwrap();
        assert!(is_commutative(&op).unwrap());
    }

    #[test]
    fn test_make_constant() {
        let op = make_constant_int_operation(5, 2).unwrap();
        assert_eq!(op.arity(), 0);
        assert_eq!(op.int_value_at(&[]).unwrap(), 2);
    }

    #[test]
    fn test_make_transposition() {
        let op = make_transposition(5, 1, 3).unwrap();
        assert_eq!(op.int_value_at(&[0]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[1]).unwrap(), 3);
        assert_eq!(op.int_value_at(&[2]).unwrap(), 2);
        assert_eq!(op.int_value_at(&[3]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[4]).unwrap(), 4);
    }

    #[test]
    fn test_make_full_cycle() {
        let op = make_full_cycle(5).unwrap();
        assert_eq!(op.int_value_at(&[0]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1]).unwrap(), 2);
        assert_eq!(op.int_value_at(&[2]).unwrap(), 3);
        assert_eq!(op.int_value_at(&[3]).unwrap(), 4);
        assert_eq!(op.int_value_at(&[4]).unwrap(), 0);
    }

    #[test]
    fn test_ternary_discriminator() {
        let op = ternary_discriminator(3).unwrap();
        // d(x,x,z) = z
        assert_eq!(op.int_value_at(&[0, 0, 2]).unwrap(), 2);
        assert_eq!(op.int_value_at(&[1, 1, 0]).unwrap(), 0);
        // d(x,y,z) = x when x != y
        assert_eq!(op.int_value_at(&[0, 1, 2]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[2, 1, 0]).unwrap(), 2);
    }

    #[test]
    fn test_find_difference() {
        let op1 = IntOperation::binary_xor("xor").unwrap();
        let op2 = IntOperation::binary_and("and").unwrap();
        
        let diff = find_difference(&op1, &op2).unwrap();
        assert!(diff.is_some());
    }

    #[test]
    fn test_equal_values() {
        let op1 = IntOperation::binary_xor("xor1").unwrap();
        let op2 = IntOperation::binary_xor("xor2").unwrap(); // Same values, different name
        
        assert!(equal_values(&op1, &op2).unwrap());
    }
}
