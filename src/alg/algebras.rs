/* algebras.rs - Static utility methods for algebra operations and analysis
 *
 * This module provides utility functions for working with algebras,
 * matching the functionality of the Java Algebras class.
 */

use crate::alg::op::Operation;
use crate::alg::SmallAlgebra;
use crate::alg::op::operations::commutes_unary;

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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::{BasicAlgebra, SmallAlgebra};
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
}

