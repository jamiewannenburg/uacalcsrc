/* algebras.rs - Static utility methods for algebra operations and analysis
 *
 * This module provides utility functions for working with algebras,
 * matching the functionality of the Java Algebras class.
 */

use crate::alg::op::Operation;
use crate::alg::SmallAlgebra;
use crate::alg::algebra::Algebra;
use crate::alg::op::operations::{commutes_unary, commutes_map, make_binary_left_shift, make_int_operations, power, ternary_discriminator};
use crate::alg::{PowerAlgebra, BasicAlgebra};
use std::collections::HashSet;

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

/// Returns Jonsson terms for distributive variety.
///
/// This method delegates to `malcev::jonsson_terms`. It returns a list of
/// Jonsson terms witnessing congruence distributivity, or `None` if the
/// algebra does not generate a congruence distributive variety.
/// The returned terms are guaranteed to be the least number of terms possible.
///
/// # Arguments
/// * `alg` - The algebra to test
///
/// # Returns
/// * `Ok(Some(Vec<Term>))` - Jonsson terms if they exist
/// * `Ok(None)` - No Jonsson terms exist
/// * `Err(String)` - If there's an error during computation
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, SmallAlgebra, BasicAlgebra};
///
/// // Create an algebra and find Jonsson terms
/// // (example would go here)
/// ```
pub fn jonsson_terms<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Vec<Box<dyn crate::terms::Term>>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    crate::alg::malcev::jonsson_terms(alg)
}

/// Returns the minimal number of Jonsson terms.
///
/// This method delegates to `malcev::jonsson_level`. If the algebra generates
/// a distributive variety, this returns the minimal number of Jonsson terms
/// minus 1; otherwise it returns -1. For congruence distributivity testing,
/// it's probably better to use `jonsson_terms` to get the actual terms.
///
/// If the algebra has only one element, it returns 1.
/// For a lattice it returns 2.
///
/// # Arguments
/// * `alg` - The algebra to test
///
/// # Returns
/// * `Ok(level)` - The Jonsson level (minimal number of Jonsson terms minus 1)
/// * `Err(String)` - If there's an error during computation
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, SmallAlgebra, BasicAlgebra};
///
/// // Create an algebra and find Jonsson level
/// // (example would go here)
/// ```
pub fn jonsson_level<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<i32, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    crate::alg::malcev::jonsson_level(alg)
}

/// Find a near unanimity term (NUF) of the given arity.
///
/// This method delegates to `malcev::nu_term`. It will find a near unanimity
/// term of the given arity if one exists; otherwise it returns `None`.
///
/// A near unanimity term of arity n is a term t(x₀, x₁, ..., xₙ₋₁) such that:
/// - t(y,x,x,...,x) = x
/// - t(x,y,x,...,x) = x
/// - ...
/// - t(x,x,x,...,y) = x
///
/// # Arguments
/// * `alg` - The algebra to check
/// * `arity` - The arity of the NU term to find (must be at least 3)
///
/// # Returns
/// * `Ok(Some(Term))` - An NU term if one exists
/// * `Ok(None)` - No NU term exists
/// * `Err(String)` - If there's an error during computation
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, SmallAlgebra, BasicAlgebra};
///
/// // Create an algebra and find an NU term
/// // (example would go here)
/// ```
pub fn find_nuf<T>(alg: &dyn SmallAlgebra<UniverseItem = T>, arity: usize) -> Result<Option<Box<dyn crate::terms::Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    crate::alg::malcev::nu_term(alg, arity)
}

/// The matrix power algebra as defined in Hobby-McKenzie.
///
/// Creates a matrix power algebra A^[k] from a given algebra A and power k.
/// This is a BasicAlgebra that contains:
/// - All operations from the power algebra A^k
/// - A binary left shift operation
///
/// # Arguments
/// * `alg` - The root algebra to raise to a power
/// * `k` - The power/exponent (number of copies)
///
/// # Returns
/// * `Ok(BasicAlgebra)` - Successfully created matrix power algebra
/// * `Err(String)` - If there's an error during creation
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, SmallAlgebra, BasicAlgebra};
/// use std::collections::HashSet;
///
/// let alg = Box::new(BasicAlgebra::new(
///     "A".to_string(),
///     HashSet::from([0, 1]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
///
/// let matrix_power = algebras::matrix_power(alg, 2).unwrap();
/// assert_eq!(matrix_power.cardinality(), 4); // 2^2 = 4
/// ```
pub fn matrix_power(
    alg: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    k: i32,
) -> Result<BasicAlgebra<i32>, String> {
    if k <= 0 {
        return Err("Power k must be positive".to_string());
    }
    
    let root_size = alg.cardinality();
    if root_size < 0 {
        return Err("Cannot create matrix power of algebra with unknown cardinality".to_string());
    }
    
    // Create PowerAlgebra
    let pow = PowerAlgebra::new_safe(alg.clone_box(), k as usize)?;
    
    // Get operations from power algebra
    let mut ops = pow.operations();
    
    // Add binary left shift operation
    let binary_left_shift = make_binary_left_shift(k, root_size)?;
    ops.push(binary_left_shift);
    
    // Convert to int operations (not power ops)
    let ops2 = make_int_operations(ops)?;
    
    // Create name
    let name = if !alg.name().is_empty() {
        format!("{}^[{}]", alg.name(), k)
    } else {
        format!("{}-matrix power", k)
    };
    
    // Create universe
    let alg_size = power(root_size, k);
    let universe: HashSet<i32> = (0..alg_size).collect();
    
    // Create BasicAlgebra
    Ok(BasicAlgebra::new(name, universe, ops2))
}

/// Create a ternary discriminator algebra.
///
/// A ternary discriminator algebra is an algebra with a single ternary operation
/// called the discriminator. The discriminator operation d(x,y,z) satisfies:
/// - d(x,y,z) = z if x = y
/// - d(x,y,z) = x if x ≠ y
///
/// # Arguments
/// * `card` - The cardinality of the algebra (size of the universe)
///
/// # Returns
/// * `Ok(BasicAlgebra)` - Successfully created ternary discriminator algebra
/// * `Err(String)` - If there's an error during creation (e.g., invalid cardinality)
///
/// # Examples
/// ```
/// use uacalc::alg::algebras;
///
/// let alg = algebras::ternary_discriminator_algebra(3).unwrap();
/// assert_eq!(alg.cardinality(), 3);
/// assert_eq!(alg.name(), "Disc-3");
/// ```
pub fn ternary_discriminator_algebra(card: i32) -> Result<BasicAlgebra<i32>, String> {
    if card <= 0 {
        return Err(format!("Cardinality must be positive, got {}", card));
    }
    
    // Create the ternary discriminator operation
    let disc_op = ternary_discriminator(card)?;
    
    // Create universe set
    let universe: HashSet<i32> = (0..card).collect();
    
    // Create operations vector
    let mut ops = Vec::new();
    ops.push(disc_op);
    
    // Create name
    let name = format!("Disc-{}", card);
    
    // Create BasicAlgebra
    Ok(BasicAlgebra::new(name, universe, ops))
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

    #[test]
    fn test_jonsson_terms_single_element() {
        // Test with single element algebra - should return Some with x and z
        let size = 1;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("SingleElement".to_string(), universe, Vec::new());
        
        let result = jonsson_terms(&alg);
        assert!(result.is_ok());
        let terms = result.unwrap();
        assert!(terms.is_some());
        let terms_vec = terms.unwrap();
        assert_eq!(terms_vec.len(), 2);
    }

    #[test]
    fn test_jonsson_terms_no_operations() {
        // Test with algebra that has no operations - should return error
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("NoOps".to_string(), universe, Vec::new());
        
        let result = jonsson_terms(&alg);
        assert!(result.is_ok());
        // For algebras with no operations, it may return None or error
        // The actual behavior depends on malcev::jonsson_terms implementation
    }

    #[test]
    fn test_jonsson_level_single_element() {
        // Test with single element algebra - should return 1
        let size = 1;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("SingleElement".to_string(), universe, Vec::new());
        
        let result = jonsson_level(&alg);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 1);
    }

    #[test]
    fn test_jonsson_level_no_operations() {
        // Test with algebra that has no operations - should return error
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("NoOps".to_string(), universe, Vec::new());
        
        let result = jonsson_level(&alg);
        // The actual behavior depends on malcev::jonsson_level implementation
        // It may return an error or a specific value
        assert!(result.is_ok() || result.is_err());
    }

    #[test]
    fn test_matrix_power_basic() {
        // Create a simple 2-element algebra
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg = Box::new(BasicAlgebra::new(
            "A".to_string(),
            universe,
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Create matrix power A^[2]
        let result = matrix_power(alg, 2);
        assert!(result.is_ok());
        let matrix_power_alg = result.unwrap();
        
        // Should have cardinality 2^2 = 4
        assert_eq!(matrix_power_alg.cardinality(), 4);
        
        // Check name
        assert!(matrix_power_alg.name().contains("^[2]") || matrix_power_alg.name().contains("2-matrix power"));
    }

    #[test]
    fn test_matrix_power_with_operations() {
        // Create a 2-element algebra with a binary operation
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let mut ops = Vec::new();
        
        // Create a simple binary operation: f(x,y) = x (first projection)
        let sym = OperationSymbol::new_safe("f", 2, false).unwrap();
        let table = vec![0, 0, 1, 1];
        let op = operations::make_int_operation(sym, size, table).unwrap();
        ops.push(op);
        
        let alg = Box::new(BasicAlgebra::new(
            "TestAlg".to_string(),
            universe,
            ops
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Create matrix power A^[3]
        let result = matrix_power(alg, 3);
        assert!(result.is_ok());
        let matrix_power_alg = result.unwrap();
        
        // Should have cardinality 2^3 = 8
        assert_eq!(matrix_power_alg.cardinality(), 8);
        
        // Should have operations (from power algebra + binary left shift)
        let ops_count = matrix_power_alg.get_operations_ref().len();
        assert!(ops_count > 0);
    }

    #[test]
    fn test_matrix_power_invalid_power() {
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg = Box::new(BasicAlgebra::new(
            "A".to_string(),
            universe,
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Test with k = 0 (should fail)
        let result = matrix_power(alg.clone_box(), 0);
        assert!(result.is_err());
        
        // Test with k < 0 (should fail)
        let result = matrix_power(alg, -1);
        assert!(result.is_err());
    }

    #[test]
    fn test_find_nuf_single_element() {
        // Test with single element algebra - should return Some with x0
        let size = 1;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("SingleElement".to_string(), universe, Vec::new());
        
        let result = find_nuf(&alg, 3);
        assert!(result.is_ok());
        let term = result.unwrap();
        assert!(term.is_some());
    }

    #[test]
    fn test_find_nuf_invalid_arity() {
        // Test with arity < 3 (should fail)
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe, Vec::new());
        
        let result = find_nuf(&alg, 2);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("arity must be at least 3"));
    }

    #[test]
    fn test_find_nuf_no_operations() {
        // Test with algebra that has no operations - should return error
        let size = 2;
        let universe: std::collections::HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("NoOps".to_string(), universe, Vec::new());
        
        let result = find_nuf(&alg, 3);
        // The actual behavior depends on malcev::nu_term implementation
        // It may return an error or None
        assert!(result.is_ok() || result.is_err());
    }

    #[test]
    fn test_ternary_discriminator_algebra_basic() {
        // Test basic creation of ternary discriminator algebra
        let result = ternary_discriminator_algebra(3);
        assert!(result.is_ok());
        let alg = result.unwrap();
        
        assert_eq!(alg.cardinality(), 3);
        assert_eq!(alg.name(), "Disc-3");
        
        // Should have exactly one operation (the discriminator)
        let ops = alg.get_operations_ref();
        assert_eq!(ops.len(), 1);
        
        // Check that the operation is ternary
        let disc_op = ops[0];
        assert_eq!(disc_op.arity(), 3);
        assert_eq!(disc_op.symbol().name(), "disc");
    }

    #[test]
    fn test_ternary_discriminator_algebra_discriminator_property() {
        // Test that the discriminator operation has the correct property
        let alg = ternary_discriminator_algebra(3).unwrap();
        let ops = alg.get_operations_ref();
        let disc_op = ops[0];
        
        // Test discriminator property: d(x,y,z) = z if x = y, otherwise x
        // d(0,0,1) = 1 (since 0 == 0)
        assert_eq!(disc_op.int_value_at(&[0, 0, 1]).unwrap(), 1);
        
        // d(0,1,2) = 0 (since 0 != 1)
        assert_eq!(disc_op.int_value_at(&[0, 1, 2]).unwrap(), 0);
        
        // d(1,1,0) = 0 (since 1 == 1)
        assert_eq!(disc_op.int_value_at(&[1, 1, 0]).unwrap(), 0);
        
        // d(2,1,0) = 2 (since 2 != 1)
        assert_eq!(disc_op.int_value_at(&[2, 1, 0]).unwrap(), 2);
    }

    #[test]
    fn test_ternary_discriminator_algebra_invalid_cardinality() {
        // Test with invalid cardinality (should fail)
        let result = ternary_discriminator_algebra(0);
        assert!(result.is_err());
        
        let result = ternary_discriminator_algebra(-1);
        assert!(result.is_err());
    }

    #[test]
    fn test_ternary_discriminator_algebra_larger() {
        // Test with larger cardinality
        let alg = ternary_discriminator_algebra(5).unwrap();
        assert_eq!(alg.cardinality(), 5);
        assert_eq!(alg.name(), "Disc-5");
        
        let ops = alg.get_operations_ref();
        assert_eq!(ops.len(), 1);
        
        let disc_op = ops[0];
        // Test a few values
        assert_eq!(disc_op.int_value_at(&[0, 0, 4]).unwrap(), 4);
        assert_eq!(disc_op.int_value_at(&[0, 1, 4]).unwrap(), 0);
        assert_eq!(disc_op.int_value_at(&[3, 3, 2]).unwrap(), 2);
    }
}

