/* algebras.rs - Static utility methods for algebra operations and analysis
 *
 * This module provides utility functions for working with algebras,
 * matching the functionality of the Java Algebras class.
 */

use crate::alg::op::Operation;
use crate::alg::SmallAlgebra;
use crate::alg::op::operations::{commutes_unary, commutes_map};

/// Test if an operation is an endomorphism of an algebra.
///
/// An endomorphism is a unary operation that commutes with all operations
/// of the algebra. This means that for any operation f and endomorphism e,
/// we have: e(f(x1, x2, ..., xn)) = f(e(x1), e(x2), ..., e(xn))
///
/// # Arguments
/// * `endo` - The operation to test (must be unary)
/// * `alg` - The algebra to test against
///
/// # Returns
/// * `Ok(true)` if the operation is an endomorphism
/// * `Ok(false)` if the operation is not an endomorphism
/// * `Err(msg)` if the operation is not unary or there's an error
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, SmallAlgebra, BasicAlgebra};
/// use uacalc::alg::op::{Operation, OperationSymbol, operations};
///
/// // Create a simple algebra and test an endomorphism
/// // (example would go here)
/// ```
pub fn is_endomorphism(
    endo: &dyn Operation,
    alg: &dyn SmallAlgebra<UniverseItem = i32>,
) -> Result<bool, String> {
    // Check if endo is unary
    if endo.arity() != 1 {
        return Err("Endomorphism must be a unary operation".to_string());
    }

    // Get all operations from the algebra
    let ops = alg.get_operations_ref();

    // Check if endo commutes with each operation
    for op in ops {
        match commutes_unary(endo, op) {
            Ok(true) => continue, // This operation commutes, check next
            Ok(false) => return Ok(false), // Found a non-commuting operation
            Err(e) => return Err(format!("Error checking commutation: {}", e)),
        }
    }

    // All operations commute with endo
    Ok(true)
}

/// Test if a map is a homomorphism from one algebra to another.
///
/// A homomorphism is a map h: A -> B such that for any operation f in alg0
/// and corresponding operation g in alg1 (with the same symbol), we have:
/// h(f(x1, x2, ..., xn)) = g(h(x1), h(x2), ..., h(xn))
///
/// # Arguments
/// * `map` - An array defining the map from elements of alg0 to elements of alg1
/// * `alg0` - The source algebra
/// * `alg1` - The target algebra
///
/// # Returns
/// * `Ok(true)` if the map is a homomorphism
/// * `Ok(false)` if the map is not a homomorphism
/// * `Err(msg)` if there's an error (e.g., missing operation in alg1)
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, SmallAlgebra, BasicAlgebra};
/// use uacalc::alg::op::{OperationSymbol, operations};
///
/// // Create two algebras and test a homomorphism
/// // (example would go here)
/// ```
pub fn is_homomorphism(
    map: &[i32],
    alg0: &dyn SmallAlgebra<UniverseItem = i32>,
    alg1: &dyn SmallAlgebra<UniverseItem = i32>,
) -> Result<bool, String> {
    // Validate map size matches alg0 cardinality
    if map.len() != alg0.cardinality() as usize {
        return Err(format!(
            "Map size {} does not match algebra cardinality {}",
            map.len(),
            alg0.cardinality()
        ));
    }

    // Validate map values are within alg1 cardinality
    let alg1_card = alg1.cardinality();
    for (i, &val) in map.iter().enumerate() {
        if val < 0 || val >= alg1_card {
            return Err(format!(
                "Map value {} at index {} is out of range [0, {})",
                val, i, alg1_card
            ));
        }
    }

    // Get all operations from alg0
    let ops0 = alg0.get_operations_ref();

    // Check if each operation in alg0 has a corresponding operation in alg1
    for op0 in ops0 {
        let sym = op0.symbol();
        
        // Get corresponding operation from alg1
        let op1 = match alg1.get_operation_ref(sym) {
            Some(op) => op,
            None => {
                return Err(format!(
                    "Operation {} not found in target algebra",
                    sym.name()
                ));
            }
        };

        // Check if the map commutes with these operations
        match commutes_map(map, op0, op1) {
            Ok(true) => continue, // This operation commutes, check next
            Ok(false) => return Ok(false), // Found a non-commuting operation
            Err(e) => return Err(format!("Error checking commutation: {}", e)),
        }
    }

    // All operations commute with the map
    Ok(true)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::BasicAlgebra;
    use crate::alg::op::{OperationSymbol, operations};

    #[test]
    fn test_is_endomorphism_identity() {
        // Create a simple 2-element algebra with a binary operation
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let mut ops = Vec::new();
        
        // Create a simple binary operation: f(x,y) = x (first projection)
        let sym = OperationSymbol::new_safe("f", 2, false).unwrap();
        let table = vec![0, 0, 1, 1]; // f(0,0)=0, f(0,1)=0, f(1,0)=1, f(1,1)=1
        let op = operations::make_int_operation(sym, size, table).unwrap();
        ops.push(op);
        
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe, ops);
        
        // Create identity endomorphism: e(x) = x
        let id_sym = OperationSymbol::new_safe("id", 1, false).unwrap();
        let id_table = vec![0, 1]; // id(0)=0, id(1)=1
        let id_op = operations::make_int_operation(id_sym, size, id_table).unwrap();
        
        // Identity should be an endomorphism
        let result = is_endomorphism(id_op.as_ref(), &alg);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), true);
    }

    #[test]
    fn test_is_endomorphism_non_unary() {
        // Create a simple algebra
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe, Vec::new());
        
        // Create a binary operation (not unary)
        let sym = OperationSymbol::new_safe("f", 2, false).unwrap();
        let table = vec![0, 0, 1, 1];
        let op = operations::make_int_operation(sym, size, table).unwrap();
        
        // Should return error for non-unary operation
        let result = is_endomorphism(op.as_ref(), &alg);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("unary"));
    }

    #[test]
    fn test_is_endomorphism_non_endomorphism() {
        // Create a simple 2-element algebra with a binary operation
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let mut ops = Vec::new();
        
        // Create a binary operation: f(x,y) = x (first projection)
        let sym = OperationSymbol::new_safe("f", 2, false).unwrap();
        let table = vec![0, 0, 1, 1];
        let op = operations::make_int_operation(sym, size, table).unwrap();
        ops.push(op);
        
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe.clone(), ops);
        
        // Create a non-endomorphism: e(x) = 1-x (swaps 0 and 1)
        let endo_sym = OperationSymbol::new_safe("swap", 1, false).unwrap();
        let endo_table = vec![1, 0]; // swap(0)=1, swap(1)=0
        let endo_op = operations::make_int_operation(endo_sym, size, endo_table).unwrap();
        
        // Use constant operation: f(x,y) = 0
        let const_sym = OperationSymbol::new_safe("const", 2, false).unwrap();
        let const_table = vec![0, 0, 0, 0]; // always returns 0
        let const_op = operations::make_int_operation(const_sym, size, const_table).unwrap();
        
        let mut ops2 = Vec::new();
        ops2.push(const_op);
        let alg2 = BasicAlgebra::new("TestAlg2".to_string(), universe, ops2);
        
        // swap(const(0,1)) = swap(0) = 1
        // const(swap(0), swap(1)) = const(1, 0) = 0
        // 1 != 0, so swap is not an endomorphism
        let result = is_endomorphism(endo_op.as_ref(), &alg2);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), false);
    }

    #[test]
    fn test_is_homomorphism_identity() {
        // Create two identical 2-element algebras with a binary operation
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        
        // Create a simple binary operation: f(x,y) = x (first projection)
        let sym = OperationSymbol::new_safe("f", 2, false).unwrap();
        let table = vec![0, 0, 1, 1]; // f(0,0)=0, f(0,1)=0, f(1,0)=1, f(1,1)=1
        
        // Create separate operations for each algebra
        let op0 = operations::make_int_operation(sym.clone(), size, table.clone()).unwrap();
        let op1 = operations::make_int_operation(sym, size, table).unwrap();
        
        let mut ops0 = Vec::new();
        ops0.push(op0);
        let mut ops1 = Vec::new();
        ops1.push(op1);
        
        let alg0 = BasicAlgebra::new("Alg0".to_string(), universe.clone(), ops0);
        let alg1 = BasicAlgebra::new("Alg1".to_string(), universe, ops1);
        
        // Identity map: 0 -> 0, 1 -> 1
        let map = vec![0, 1];
        
        // Identity should be a homomorphism
        let result = is_homomorphism(&map, &alg0, &alg1);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), true);
    }

    #[test]
    fn test_is_homomorphism_constant() {
        // Create two 2-element algebras with constant operation
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        
        // Create constant operation: f(x,y) = 0
        let sym = OperationSymbol::new_safe("const", 2, false).unwrap();
        let table = vec![0, 0, 0, 0]; // always returns 0
        
        // Create separate operations for each algebra
        let op0 = operations::make_int_operation(sym.clone(), size, table.clone()).unwrap();
        let op1 = operations::make_int_operation(sym, size, table).unwrap();
        
        let mut ops0 = Vec::new();
        ops0.push(op0);
        let mut ops1 = Vec::new();
        ops1.push(op1);
        
        let alg0 = BasicAlgebra::new("Alg0".to_string(), universe.clone(), ops0);
        let alg1 = BasicAlgebra::new("Alg1".to_string(), universe, ops1);
        
        // Constant map: 0 -> 0, 1 -> 0
        let map = vec![0, 0];
        
        // Constant map should be a homomorphism for constant operation
        let result = is_homomorphism(&map, &alg0, &alg1);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), true);
    }

    #[test]
    fn test_is_homomorphism_non_homomorphism() {
        // Create two 2-element algebras with first projection
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let mut ops0 = Vec::new();
        let mut ops1 = Vec::new();
        
        // Alg0: f(x,y) = x (first projection)
        let sym0 = OperationSymbol::new_safe("f", 2, false).unwrap();
        let table0 = vec![0, 0, 1, 1]; // f(0,0)=0, f(0,1)=0, f(1,0)=1, f(1,1)=1
        let op0 = operations::make_int_operation(sym0, size, table0).unwrap();
        ops0.push(op0);
        
        // Alg1: f(x,y) = y (second projection)
        let sym1 = OperationSymbol::new_safe("f", 2, false).unwrap();
        let table1 = vec![0, 1, 0, 1]; // f(0,0)=0, f(0,1)=1, f(1,0)=0, f(1,1)=1
        let op1 = operations::make_int_operation(sym1, size, table1).unwrap();
        ops1.push(op1);
        
        let alg0 = BasicAlgebra::new("Alg0".to_string(), universe.clone(), ops0);
        let alg1 = BasicAlgebra::new("Alg1".to_string(), universe, ops1);
        
        // Identity map: 0 -> 0, 1 -> 1
        let map = vec![0, 1];
        
        // Identity map is NOT a homomorphism from first projection to second projection
        // f(0,1) = 0 in alg0, so h(f(0,1)) = h(0) = 0
        // f(h(0), h(1)) = f(0, 1) = 1 in alg1
        // 0 != 1, so not a homomorphism
        let result = is_homomorphism(&map, &alg0, &alg1);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), false);
    }

    #[test]
    fn test_is_homomorphism_wrong_map_size() {
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg0 = BasicAlgebra::new("Alg0".to_string(), universe.clone(), Vec::new());
        let alg1 = BasicAlgebra::new("Alg1".to_string(), universe, Vec::new());
        
        // Map with wrong size
        let map = vec![0]; // Should be size 2
        
        let result = is_homomorphism(&map, &alg0, &alg1);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Map size"));
    }

    #[test]
    fn test_is_homomorphism_missing_operation() {
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let mut ops0 = Vec::new();
        
        // Alg0 has operation f
        let sym = OperationSymbol::new_safe("f", 2, false).unwrap();
        let table = vec![0, 0, 1, 1];
        let op = operations::make_int_operation(sym, size, table).unwrap();
        ops0.push(op);
        
        let alg0 = BasicAlgebra::new("Alg0".to_string(), universe.clone(), ops0);
        let alg1 = BasicAlgebra::new("Alg1".to_string(), universe, Vec::new()); // No operations
        
        let map = vec![0, 1];
        
        // Should return error because alg1 doesn't have operation f
        let result = is_homomorphism(&map, &alg0, &alg1);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("not found in target algebra"));
    }
}

