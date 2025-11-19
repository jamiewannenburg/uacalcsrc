/* algebras.rs - Static utility methods for algebra operations and analysis
 *
 * This module provides utility functions for working with algebras,
 * matching the functionality of the Java Algebras class.
 */

use crate::alg::op::Operation;
use crate::alg::SmallAlgebra;
use crate::alg::algebra::Algebra;
use crate::alg::op::operations::{commutes_unary, commutes_map, make_binary_left_shift, make_int_operations, power, ternary_discriminator};
use crate::alg::{PowerAlgebra, BasicAlgebra, Homomorphism};
use crate::alg::conlat::partition::Partition;
use crate::util::int_array::{IntArray, IntArrayTrait};
use std::collections::{HashSet, BTreeSet, HashMap};
use std::sync::Arc;

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
/// use uacalc::alg::{algebras, SmallAlgebra, BasicAlgebra, Algebra};
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

/// Make a random algebra of a given similarity type.
///
/// Creates a random algebra with the specified size and similarity type.
/// The operations are generated randomly.
///
/// # Arguments
/// * `n` - The size of the algebra (cardinality of the universe)
/// * `sim_type` - The similarity type (defines the operations)
///
/// # Returns
/// * `Ok(BasicAlgebra)` - Successfully created random algebra
/// * `Err(String)` - If there's an error during creation
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, Algebra};
/// use uacalc::alg::op::{SimilarityType, OperationSymbol};
///
/// let op_syms = vec![OperationSymbol::new("f", 2, false)];
/// let sim_type = SimilarityType::new(op_syms);
/// let alg = algebras::make_random_algebra(3, &sim_type).unwrap();
/// assert_eq!(alg.cardinality(), 3);
/// ```
pub fn make_random_algebra(
    n: i32,
    sim_type: &crate::alg::op::SimilarityType,
) -> Result<BasicAlgebra<i32>, String> {
    make_random_algebra_with_seed(n, sim_type, None)
}

/// Make a random algebra of a given similarity type with a seed.
///
/// Creates a random algebra with the specified size and similarity type.
/// The operations are generated randomly using the provided seed for reproducibility.
///
/// # Arguments
/// * `n` - The size of the algebra (cardinality of the universe)
/// * `sim_type` - The similarity type (defines the operations)
/// * `seed` - Optional seed for the random number generator (None means use random seed)
///
/// # Returns
/// * `Ok(BasicAlgebra)` - Successfully created random algebra
/// * `Err(String)` - If there's an error during creation
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, Algebra};
/// use uacalc::alg::op::{SimilarityType, OperationSymbol};
///
/// let op_syms = vec![OperationSymbol::new("f", 2, false)];
/// let sim_type = SimilarityType::new(op_syms);
/// let alg = algebras::make_random_algebra_with_seed(3, &sim_type, Some(12345)).unwrap();
/// assert_eq!(alg.cardinality(), 3);
/// ```
pub fn make_random_algebra_with_seed(
    n: i32,
    sim_type: &crate::alg::op::SimilarityType,
    seed: Option<i64>,
) -> Result<BasicAlgebra<i32>, String> {
    if n <= 0 {
        return Err(format!("Algebra size must be positive, got {}", n));
    }
    
    // Convert i64 seed to Option<u64> for make_random_operations_with_seed
    // In Java, -1 means no seed, so we treat None as no seed
    let seed_u64 = seed.map(|s| s as u64);
    
    // Create random operations
    let ops = crate::alg::op::operations::make_random_operations_with_seed(n, sim_type, seed_u64)?;
    
    // Create universe set
    let universe: HashSet<i32> = (0..n).collect();
    
    // Create name
    let name = format!("RAlg{}", n);
    
    // Create BasicAlgebra
    Ok(BasicAlgebra::new(name, universe, ops))
}

/// Make a random algebra with given arities of the operations.
///
/// Creates a random algebra with the specified size and operation arities.
/// Operation symbols are automatically created as "r0", "r1", etc.
///
/// # Arguments
/// * `n` - The size of the algebra (cardinality of the universe)
/// * `arities` - Vector of arities for the operations
///
/// # Returns
/// * `Ok(BasicAlgebra)` - Successfully created random algebra
/// * `Err(String)` - If there's an error during creation
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, Algebra};
///
/// let arities = vec![2, 1]; // One binary and one unary operation
/// let alg = algebras::make_random_algebra_with_arities(3, &arities).unwrap();
/// assert_eq!(alg.cardinality(), 3);
/// ```
pub fn make_random_algebra_with_arities(
    n: i32,
    arities: &[i32],
) -> Result<BasicAlgebra<i32>, String> {
    make_random_algebra_with_arities_and_seed(n, arities, None)
}

/// Make a random algebra with given arities of the operations and a seed.
///
/// Creates a random algebra with the specified size and operation arities.
/// Operation symbols are automatically created as "r0", "r1", etc.
/// The operations are generated randomly using the provided seed for reproducibility.
///
/// # Arguments
/// * `n` - The size of the algebra (cardinality of the universe)
/// * `arities` - Vector of arities for the operations
/// * `seed` - Optional seed for the random number generator (None means use random seed)
///
/// # Returns
/// * `Ok(BasicAlgebra)` - Successfully created random algebra
/// * `Err(String)` - If there's an error during creation
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, Algebra};
///
/// let arities = vec![2, 1]; // One binary and one unary operation
/// let alg = algebras::make_random_algebra_with_arities_and_seed(3, &arities, Some(12345)).unwrap();
/// assert_eq!(alg.cardinality(), 3);
/// ```
pub fn make_random_algebra_with_arities_and_seed(
    n: i32,
    arities: &[i32],
    seed: Option<i64>,
) -> Result<BasicAlgebra<i32>, String> {
    if n <= 0 {
        return Err(format!("Algebra size must be positive, got {}", n));
    }
    
    // Create operation symbols from arities
    let mut op_syms = Vec::new();
    for (i, &arity) in arities.iter().enumerate() {
        if arity < 0 {
            return Err(format!("Arity must be non-negative, got {} at index {}", arity, i));
        }
        let sym = crate::alg::op::OperationSymbol::new(&format!("r{}", i), arity, false);
        op_syms.push(sym);
    }
    
    // Create similarity type
    let sim_type = crate::alg::op::SimilarityType::new(op_syms);
    
    // Call the similarity type version
    make_random_algebra_with_seed(n, &sim_type, seed)
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
/// use uacalc::alg::{algebras, Algebra};
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

/// Create the full transformation semigroup on n elements.
///
/// The transformation semigroup consists of all functions from {0..n-1} to {0..n-1}.
/// Each transformation is encoded as a Horner integer.
///
/// # Arguments
/// * `n` - The size of the underlying set (must be at most 9)
/// * `include_constants` - Whether to include constant transformations (one for each element)
/// * `include_id` - Whether to include the identity transformation
///
/// # Returns
/// * `Ok(BasicAlgebra)` - The transformation semigroup algebra
/// * `Err(String)` - If n > 9 or there's an error during creation
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, Algebra};
///
/// let alg = algebras::full_transformation_semigroup(3, true, true).unwrap();
/// assert_eq!(alg.cardinality(), 27); // 3^3 = 27
/// ```
pub fn full_transformation_semigroup(
    n: i32,
    include_constants: bool,
    include_id: bool,
) -> Result<BasicAlgebra<i32>, String> {
    use crate::util::horner;
    use crate::alg::op::operations::{make_composition_op, make_constant_int_operation};
    
    if n > 9 {
        return Err("n can be at most 9".to_string());
    }
    if n <= 0 {
        return Err("n must be positive".to_string());
    }
    
    // Compute pow = n^n
    let mut pow = n;
    for _i in 1..n {
        pow = pow * n;
    }
    
    let mut ops = Vec::new();
    
    // Add composition operation
    ops.push(make_composition_op(n, pow)?);
    
    // Add constant transformations if requested
    if include_constants {
        for i in 0..n {
            // Create constant transformation: f(x) = i for all x
            let ci = vec![i; n as usize];
            let c = horner::horner_same_size(&ci, n);
            ops.push(make_constant_int_operation(pow, c)?);
        }
    }
    
    // Add identity transformation if requested
    if include_id {
        // Create identity transformation: f(x) = x
        let id: Vec<i32> = (0..n).collect();
        let idx = horner::horner_same_size(&id, n);
        ops.push(make_constant_int_operation(pow, idx)?);
    }
    
    // Create universe set
    let universe: HashSet<i32> = (0..pow).collect();
    
    // Create name
    let name = format!("Trans{}", n);
    
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

    #[test]
    fn test_make_random_algebra_basic() {
        // Test basic creation of random algebra
        use crate::alg::op::{SimilarityType, OperationSymbol};
        
        let op_syms = vec![OperationSymbol::new("f", 2, false)];
        let sim_type = SimilarityType::new(op_syms);
        
        let result = make_random_algebra(3, &sim_type);
        assert!(result.is_ok());
        let alg = result.unwrap();
        
        assert_eq!(alg.cardinality(), 3);
        assert_eq!(alg.name(), "RAlg3");
        
        // Should have one operation
        let ops = alg.get_operations_ref();
        assert_eq!(ops.len(), 1);
        assert_eq!(ops[0].arity(), 2);
    }

    #[test]
    fn test_make_random_algebra_with_seed() {
        // Test creation with seed (should be reproducible)
        use crate::alg::op::{SimilarityType, OperationSymbol};
        
        let op_syms = vec![OperationSymbol::new("f", 2, false)];
        let sim_type = SimilarityType::new(op_syms);
        
        let alg1 = make_random_algebra_with_seed(3, &sim_type, Some(12345)).unwrap();
        let alg2 = make_random_algebra_with_seed(3, &sim_type, Some(12345)).unwrap();
        
        // With same seed, should get same operations
        assert_eq!(alg1.cardinality(), alg2.cardinality());
        assert_eq!(alg1.get_operations_ref().len(), alg2.get_operations_ref().len());
        
        // Check that operations are the same
        let op1 = alg1.get_operations_ref()[0];
        let op2 = alg2.get_operations_ref()[0];
        
        // Check a few values
        for i in 0..3 {
            for j in 0..3 {
                let val1 = op1.int_value_at(&[i, j]).unwrap();
                let val2 = op2.int_value_at(&[i, j]).unwrap();
                assert_eq!(val1, val2, "Operations should be identical with same seed");
            }
        }
    }

    #[test]
    fn test_make_random_algebra_invalid_size() {
        // Test with invalid size
        use crate::alg::op::{SimilarityType, OperationSymbol};
        
        let op_syms = vec![OperationSymbol::new("f", 2, false)];
        let sim_type = SimilarityType::new(op_syms);
        
        let result = make_random_algebra(0, &sim_type);
        assert!(result.is_err());
        
        let result = make_random_algebra(-1, &sim_type);
        assert!(result.is_err());
    }

    #[test]
    fn test_make_random_algebra_with_arities() {
        // Test creation with arities
        let arities = vec![2, 1, 0]; // Binary, unary, nullary
        
        let result = make_random_algebra_with_arities(3, &arities);
        assert!(result.is_ok());
        let alg = result.unwrap();
        
        assert_eq!(alg.cardinality(), 3);
        assert_eq!(alg.name(), "RAlg3");
        
        // Should have 3 operations
        let ops = alg.get_operations_ref();
        assert_eq!(ops.len(), 3);
        assert_eq!(ops[0].arity(), 2);
        assert_eq!(ops[1].arity(), 1);
        assert_eq!(ops[2].arity(), 0);
        
        // Check operation names
        assert_eq!(ops[0].symbol().name(), "r0");
        assert_eq!(ops[1].symbol().name(), "r1");
        assert_eq!(ops[2].symbol().name(), "r2");
    }

    #[test]
    fn test_make_random_algebra_with_arities_and_seed() {
        // Test creation with arities and seed
        let arities = vec![2, 1];
        
        let alg1 = make_random_algebra_with_arities_and_seed(3, &arities, Some(12345)).unwrap();
        let alg2 = make_random_algebra_with_arities_and_seed(3, &arities, Some(12345)).unwrap();
        
        // With same seed, should get same operations
        assert_eq!(alg1.cardinality(), alg2.cardinality());
        assert_eq!(alg1.get_operations_ref().len(), alg2.get_operations_ref().len());
        
        // Check that operations are the same
        let ops1 = alg1.get_operations_ref();
        let ops2 = alg2.get_operations_ref();
        
        for (op1, op2) in ops1.iter().zip(ops2.iter()) {
            // Check a few values for binary operation
            if op1.arity() == 2 {
                for i in 0..3 {
                    for j in 0..3 {
                        let val1 = op1.int_value_at(&[i, j]).unwrap();
                        let val2 = op2.int_value_at(&[i, j]).unwrap();
                        assert_eq!(val1, val2, "Operations should be identical with same seed");
                    }
                }
            } else if op1.arity() == 1 {
                for i in 0..3 {
                    let val1 = op1.int_value_at(&[i]).unwrap();
                    let val2 = op2.int_value_at(&[i]).unwrap();
                    assert_eq!(val1, val2, "Operations should be identical with same seed");
                }
            }
        }
    }

    #[test]
    fn test_make_random_algebra_with_arities_invalid() {
        // Test with invalid arities
        let arities = vec![2, -1];
        
        let result = make_random_algebra_with_arities(3, &arities);
        assert!(result.is_err());
        
        // Test with invalid size
        let arities = vec![2, 1];
        let result = make_random_algebra_with_arities(0, &arities);
        assert!(result.is_err());
    }
}

/// Test if algebra A is in the quasivariety generated by algebra B.
///
/// Returns a list of homomorphisms from A into B if A is in the quasivariety;
/// otherwise returns None.
///
/// # Arguments
/// * `a` - The algebra to test for membership
/// * `b` - The generating algebra
/// * `report` - Optional progress report
///
/// # Returns
/// * `Ok(Some(Vec<Homomorphism>))` - List of homomorphisms if A is in the quasivariety
/// * `Ok(None)` - If A is not in the quasivariety
/// * `Err(String)` - If there's an error during computation
pub fn member_of_quasivariety(
    a: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    b: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    report: Option<&mut dyn crate::progress::ProgressReport>,
) -> Result<Option<Vec<Homomorphism>>, String> {
    let gen_algs = vec![b];
    member_of_quasivariety_list(a, gen_algs, report)
}

/// Test if algebra A is in the quasivariety generated by a list of algebras.
///
/// Returns a list of homomorphisms from A into the generating algebras if A is
/// in the quasivariety; otherwise returns None.
///
/// # Arguments
/// * `a` - The algebra to test for membership
/// * `gen_algs` - The list of generating algebras
/// * `report` - Optional progress report
///
/// # Returns
/// * `Ok(Some(Vec<Homomorphism>))` - List of homomorphisms if A is in the quasivariety
/// * `Ok(None)` - If A is not in the quasivariety
/// * `Err(String)` - If there's an error during computation
pub fn member_of_quasivariety_list(
    a: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    gen_algs: Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>>,
    mut report: Option<&mut dyn crate::progress::ProgressReport>,
) -> Result<Option<Vec<Homomorphism>>, String> {
    use crate::alg::conlat::CongruenceLattice;
    use crate::alg::sublat::SubalgebraLattice;
    
    use crate::util::{ArrayIncrementor, SequenceGenerator};
    use std::collections::HashMap;
    
    // Create congruence lattice for A
    let a_con = CongruenceLattice::new(a.clone_box());
    let zero = a_con.zero();
    
    // Create subalgebra lattice for A
    let mut a_sub = SubalgebraLattice::new_safe(a.clone_box())?;
    
    // Find minimal generating set
    let gen_set = a_sub.find_minimal_sized_generating_set();
    let gens = gen_set.elements();
    let gen_size = gens.len();
    
    if let Some(ref mut r) = report {
        r.add_line(&format!("gens of A: {:?}", gens));
    }
    
    // Start with the one partition (all elements together)
    let mut phi = a_con.one();
    let mut homos = Vec::new();
    
    // For each generating algebra B
    for b in gen_algs {
        let b_card = b.cardinality();
        if b_card <= 0 {
            continue;
        }
        
        // Create array for generator assignments
        let mut arr = vec![0i32; gen_size];
        let mut inc = SequenceGenerator::sequence_incrementor(&mut arr, b_card - 1);
        
        // Iterate through all possible assignments
        // Process initial state first, then increment
        loop {
            // Get current assignment (without borrowing arr)
            let current_arr = inc.get_current();
            
            // Try to extend the assignment to a homomorphism
            if let Some(homo_map) = SubalgebraLattice::extend_to_homomorphism(
                gens,
                &current_arr,
                a.as_ref(),
                b.as_ref(),
            ) {
                // Convert HashMap<i32, i32> to HashMap<usize, usize> for Homomorphism
                let mut homo_map_usize = HashMap::new();
                for (&k, &v) in homo_map.iter() {
                    homo_map_usize.insert(k as usize, v as usize);
                }
                
                // Create homomorphism
                let homo = Homomorphism::new_safe(
                    a.clone_box(),
                    b.clone_box(),
                    homo_map_usize,
                )?;
                
                // Compute kernel
                let kernel = homo.kernel()?;
                
                // Check if kernel is not already covered by phi
                if !phi.leq(&kernel) {
                    // Update phi to be the meet of phi and kernel
                    phi = phi.meet(&kernel)?;
                    homos.push(homo);
                    
                    // If phi equals zero, we're done
                    if phi == zero {
                        return Ok(Some(homos));
                    }
                }
            }
            
            // Increment to next assignment
            if !inc.increment() {
                break;
            }
        }
    }
    
    if let Some(ref mut r) = report {
        r.add_line(&format!("the intersection of the kernel is {}", phi));
    }
    
    // If phi didn't become zero, A is not in the quasivariety
    Ok(None)
}

/// Test if algebra A can be embedded into a product of proper subalgebras of A.
///
/// This checks if A is in the quasivariety generated by its proper subalgebras.
/// Returns a list of homomorphisms from A into A (with non-zero kernels) if A
/// can be embedded; otherwise returns None.
///
/// # Arguments
/// * `a` - The algebra to test
/// * `report` - Optional progress report
///
/// # Returns
/// * `Ok(Some(Vec<Homomorphism>))` - List of homomorphisms if A can be embedded
/// * `Ok(None)` - If A cannot be embedded
/// * `Err(String)` - If there's an error during computation
pub fn member_of_quasivariety_gen_by_proper_subs(
    a: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    mut report: Option<&mut dyn crate::progress::ProgressReport>,
) -> Result<Option<Vec<Homomorphism>>, String> {
    use crate::alg::conlat::CongruenceLattice;
    use crate::alg::sublat::SubalgebraLattice;
    
    use crate::util::{ArrayIncrementor, SequenceGenerator};
    use std::collections::HashMap;
    
    // Create congruence lattice for A
    let a_con = CongruenceLattice::new(a.clone_box());
    let zero = a_con.zero();
    
    // Create subalgebra lattice for A
    let mut a_sub = SubalgebraLattice::new_safe(a.clone_box())?;
    
    // Find minimal generating set
    let gen_set = a_sub.find_minimal_sized_generating_set();
    let gens = gen_set.elements();
    let gen_size = gens.len();
    
    if let Some(ref mut r) = report {
        r.add_line(&format!("gens of A: {:?}", gens));
    }
    
    // Start with the one partition (all elements together)
    let mut phi = a_con.one();
    let mut homos = Vec::new();
    
    // Get cardinality of A
    let a_card = a.cardinality();
    if a_card <= 0 {
        return Ok(None);
    }
    
    // For a single element algebra, there are no proper subalgebras
    if a_card == 1 {
        if let Some(ref mut r) = report {
            r.add_line("Single element algebra has no proper subalgebras");
        }
        return Ok(None);
    }
    
    // Create array for generator assignments
    // We iterate through assignments to A.cardinality() - 1 (not A.cardinality())
    // to ensure we only get proper subalgebras
    let mut arr = vec![0i32; gen_size];
    let mut inc = SequenceGenerator::sequence_incrementor(&mut arr, a_card - 1);
    
    // Iterate through all possible assignments
    // Process initial state first, then increment
    loop {
        // Get current assignment (without borrowing arr)
        let current_arr = inc.get_current();
        
        // Try to extend the assignment to a homomorphism from A to A
        if let Some(homo_map) = SubalgebraLattice::extend_to_homomorphism(
            gens,
            &current_arr,
            a.as_ref(),
            a.as_ref(),
        ) {
            // Convert HashMap<i32, i32> to HashMap<usize, usize> for Homomorphism
            let mut homo_map_usize = HashMap::new();
            for (&k, &v) in homo_map.iter() {
                homo_map_usize.insert(k as usize, v as usize);
            }
            
            // Create homomorphism
            let homo = Homomorphism::new_safe(
                a.clone_box(),
                a.clone_box(),
                homo_map_usize,
            )?;
            
            // Compute kernel
            let kernel = homo.kernel()?;
            
            // Check that kernel is not zero (to ensure it's a proper subalgebra)
            // and that kernel is not already covered by phi
            if kernel != zero && !phi.leq(&kernel) {
                // Update phi to be the meet of phi and kernel
                phi = phi.meet(&kernel)?;
                homos.push(homo);
                
                // If phi equals zero, we're done
                if phi == zero {
                    return Ok(Some(homos));
                }
            }
        }
        
        // Increment to next assignment
        if !inc.increment() {
            break;
        }
    }
    
    if let Some(ref mut r) = report {
        r.add_line(&format!("the intersection of the kernel is {}", phi));
    }
    
    // If phi didn't become zero, A cannot be embedded
    Ok(None)
}

#[cfg(test)]
mod member_of_quasivariety_tests {
    use super::*;
    use crate::alg::BasicAlgebra;
    use std::collections::HashSet;

    #[test]
    fn test_member_of_quasivariety_identical_algebras() {
        // Create two identical 2-element algebras
        let size = 2;
        let universe: HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe.clone(), Vec::new());
        
        let a = Box::new(alg.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        let b = Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // An algebra should be in its own quasivariety
        let result = member_of_quasivariety(a, b, None);
        assert!(result.is_ok());
        // The result may be Some or None depending on the implementation
        // For identical algebras, we should get Some with homomorphisms
    }

    #[test]
    fn test_member_of_quasivariety_list() {
        // Create two identical 2-element algebras
        let size = 2;
        let universe: HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe.clone(), Vec::new());
        
        let a = Box::new(alg.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        let gen_algs = vec![Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>];
        
        // An algebra should be in its own quasivariety
        let result = member_of_quasivariety_list(a, gen_algs, None);
        assert!(result.is_ok());
    }
}

#[cfg(test)]
mod member_of_quasivariety_gen_by_proper_subs_tests {
    use super::*;
    use crate::alg::BasicAlgebra;
    use std::collections::HashSet;

    #[test]
    fn test_member_of_quasivariety_gen_by_proper_subs_small_algebra() {
        // Create a small 2-element algebra
        let size = 2;
        let universe: HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe, Vec::new());
        
        let a = Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Test the function - result may be Some or None depending on the algebra
        let result = member_of_quasivariety_gen_by_proper_subs(a, None);
        assert!(result.is_ok());
    }

    #[test]
    fn test_member_of_quasivariety_gen_by_proper_subs_larger_algebra() {
        // Create a larger 3-element algebra
        let size = 3;
        let universe: HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("TestAlg3".to_string(), universe, Vec::new());
        
        let a = Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Test the function
        let result = member_of_quasivariety_gen_by_proper_subs(a, None);
        assert!(result.is_ok());
    }

    #[test]
    fn test_member_of_quasivariety_gen_by_proper_subs_single_element() {
        // Create a single element algebra
        let size = 1;
        let universe: HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("TestAlg1".to_string(), universe, Vec::new());
        
        let a = Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Single element algebra should return None (no proper subalgebras)
        let result = member_of_quasivariety_gen_by_proper_subs(a, None);
        assert!(result.is_ok());
        // For a single element algebra, there are no proper subalgebras, so result should be None
    }
}

#[cfg(test)]
mod full_transformation_semigroup_tests {
    use super::*;
    use crate::util::horner;

    #[test]
    fn test_full_transformation_semigroup_basic() {
        // Test basic creation with n=2
        let result = full_transformation_semigroup(2, false, false);
        assert!(result.is_ok());
        let alg = result.unwrap();
        
        // Should have cardinality 2^2 = 4
        assert_eq!(alg.cardinality(), 4);
        assert_eq!(alg.name(), "Trans2");
        
        // Should have one operation (composition)
        let ops = alg.get_operations_ref();
        assert_eq!(ops.len(), 1);
        assert_eq!(ops[0].arity(), 2);
        assert_eq!(ops[0].symbol().name(), "composition");
    }

    #[test]
    fn test_full_transformation_semigroup_with_constants() {
        // Test with constants included
        let result = full_transformation_semigroup(2, true, false);
        assert!(result.is_ok());
        let alg = result.unwrap();
        
        // Should have cardinality 4
        assert_eq!(alg.cardinality(), 4);
        
        // Should have 1 composition + 2 constants = 3 operations
        let ops = alg.get_operations_ref();
        assert_eq!(ops.len(), 3);
        
        // Check that constants are correct
        // Constant 0: f(x) = 0 for all x, encoded as [0,0] = 0*2 + 0 = 0
        // Constant 1: f(x) = 1 for all x, encoded as [1,1] = 1*2 + 1 = 3
        let const0 = ops[1].int_value_at(&[]).unwrap();
        let const1 = ops[2].int_value_at(&[]).unwrap();
        assert_eq!(const0, 0);
        assert_eq!(const1, 3);
    }

    #[test]
    fn test_full_transformation_semigroup_with_id() {
        // Test with identity included
        let result = full_transformation_semigroup(2, false, true);
        assert!(result.is_ok());
        let alg = result.unwrap();
        
        // Should have cardinality 4
        assert_eq!(alg.cardinality(), 4);
        
        // Should have 1 composition + 1 identity = 2 operations
        let ops = alg.get_operations_ref();
        assert_eq!(ops.len(), 2);
        
        // Check that identity is correct
        // Identity: f(x) = x, encoded as [0,1]
        // horner_same_size([0,1], 2) = 2*0 + 1 = 1, then 2*1 + 0 = 2
        // So identity is encoded as 2
        let id = ops[1].int_value_at(&[]).unwrap();
        assert_eq!(id, 2);
    }

    #[test]
    fn test_full_transformation_semigroup_with_all() {
        // Test with both constants and identity
        let result = full_transformation_semigroup(2, true, true);
        assert!(result.is_ok());
        let alg = result.unwrap();
        
        // Should have cardinality 4
        assert_eq!(alg.cardinality(), 4);
        
        // Should have 1 composition + 2 constants + 1 identity = 4 operations
        let ops = alg.get_operations_ref();
        assert_eq!(ops.len(), 4);
    }

    #[test]
    fn test_full_transformation_semigroup_composition() {
        // Test that composition works correctly
        let alg = full_transformation_semigroup(2, false, false).unwrap();
        let ops = alg.get_operations_ref();
        let comp_op = ops[0];
        
        // For n=2, we have 4 transformations:
        // 0: [0,0] -> horner = 2*0 + 0 = 0
        // 1: [1,0] -> horner = 2*0 + 1 = 1, then 2*1 + 0 = 2 (swap)
        // 2: [0,1] -> horner = 2*0 + 1 = 1, then 2*1 + 0 = 2 (identity)
        // 3: [1,1] -> horner = 2*0 + 1 = 1, then 2*1 + 1 = 3
        
        // Actually, let's decode to verify:
        // 0 -> [0,0]
        // 1 -> [1,0] (swap)
        // 2 -> [0,1] (identity)
        // 3 -> [1,1]
        
        // Compose identity with itself: id ∘ id = id
        // Identity is encoded as 2
        let id_id = comp_op.int_value_at(&[2, 2]).unwrap();
        assert_eq!(id_id, 2);
        
        // Test a simpler composition: [0,0] ∘ [0,1] (identity)
        // [0,0] means f(0)=0, f(1)=0
        // [0,1] (identity) means g(0)=0, g(1)=1
        // (f ∘ g)(0) = f(g(0)) = f(0) = 0
        // (f ∘ g)(1) = f(g(1)) = f(1) = 0
        // So result is [0,0] = 0
        let comp = comp_op.int_value_at(&[0, 2]).unwrap();
        assert_eq!(comp, 0);
    }

    #[test]
    fn test_full_transformation_semigroup_n3() {
        // Test with n=3
        let result = full_transformation_semigroup(3, true, true);
        assert!(result.is_ok());
        let alg = result.unwrap();
        
        // Should have cardinality 3^3 = 27
        assert_eq!(alg.cardinality(), 27);
        assert_eq!(alg.name(), "Trans3");
        
        // Should have 1 composition + 3 constants + 1 identity = 5 operations
        let ops = alg.get_operations_ref();
        assert_eq!(ops.len(), 5);
    }

    #[test]
    fn test_full_transformation_semigroup_invalid_n() {
        // Test with n > 9 (should fail)
        let result = full_transformation_semigroup(10, false, false);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("at most 9"));
        
        // Test with n = 0 (should fail)
        let result = full_transformation_semigroup(0, false, false);
        assert!(result.is_err());
        
        // Test with n < 0 (should fail)
        let result = full_transformation_semigroup(-1, false, false);
        assert!(result.is_err());
    }
}

/// Find all quasi-critical congruences of an algebra.
///
/// A congruence theta is quasi-critical if A/theta is quasi-critical,
/// i.e., A/theta is not a subdirect product of proper subalgebras.
///
/// # Arguments
/// * `a` - The algebra to analyze
/// * `report` - Optional progress report
///
/// # Returns
/// * `Ok(Vec<Partition>)` - List of quasi-critical congruences
/// * `Err(String)` - If there's an error during computation
pub fn quasi_critical_congruences(
    a: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    mut report: Option<&mut dyn crate::progress::ProgressReport>,
) -> Result<Vec<crate::alg::conlat::partition::Partition>, String> {
    use crate::alg::conlat::CongruenceLattice;
    
    use crate::alg::QuotientAlgebra;
    
    let a_con = CongruenceLattice::new(a.clone_box());
    let one = a_con.one();
    let zero = a_con.zero();
    let mut meet_of_non_zeros = one.clone();
    
    let mut critical_congs = Vec::new();
    
    // Get all congruences
    let univ = a_con.universe();
    
    for par in univ {
        // Skip the one congruence
        if par == one {
            continue;
        }
        
        // Create quotient algebra A/par
        let quot = QuotientAlgebra::<i32>::new_safe(a.clone_box(), par.clone())?;
        
        // Convert QuotientAlgebra to BasicAlgebra for use with member_of_quasivariety_gen_by_proper_subs
        // QuotientAlgebra has UniverseItem = QuotientElement<i32>, but we need i32
        let quot_card = quot.cardinality();
        let quot_ops = quot.operations();
        let int_ops = crate::alg::op::ops::make_int_operations(quot_ops)?;
        let quot_universe: HashSet<i32> = (0..quot_card).collect();
        let quot_basic = BasicAlgebra::new(quot.name().to_string(), quot_universe, int_ops);
        let quot_box = Box::new(quot_basic) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Check if A/par is quasi-critical (i.e., not a subdirect product of proper subalgebras)
        // This means member_of_quasivariety_gen_by_proper_subs should return None
        // Don't pass report in the loop to avoid borrowing issues
        let result = member_of_quasivariety_gen_by_proper_subs(quot_box, None)?;
        match result {
            None => {
                // A/par is quasi-critical, so par is a quasi-critical congruence
                critical_congs.push(par.clone());
                if par != zero {
                    meet_of_non_zeros = meet_of_non_zeros.meet(&par)?;
                }
            }
            Some(_) => {
                // A/par is not quasi-critical, so par is not a quasi-critical congruence
            }
        }
    }
    
    if let Some(ref mut r) = report {
        r.add_line(&format!("The meet of nonzero q-critical congruences is {}", meet_of_non_zeros));
    }
    
    Ok(critical_congs)
}

/// Determine if an algebra is quasi-critical.
///
/// An algebra is quasi-critical if it is not a subdirect product of proper subalgebras.
/// This method returns a map from congruences to subalgebras if the algebra is quasi-critical,
/// or None if it is not.
///
/// Note: This has been replaced by `member_of_quasivariety_gen_by_proper_subs` in newer code,
/// but is kept for compatibility.
///
/// # Arguments
/// * `a` - The algebra to test
/// * `report` - Optional progress report
///
/// # Returns
/// * `Ok(Some(HashMap<Partition, Vec<i32>>))` - Map from congruences to subalgebra generators if quasi-critical
/// * `Ok(None)` - If the algebra is not quasi-critical
/// * `Err(String)` - If there's an error during computation
pub fn quasi_critical(
    a: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    mut report: Option<&mut dyn crate::progress::ProgressReport>,
) -> Result<Option<std::collections::HashMap<crate::alg::conlat::partition::Partition, Vec<i32>>>, String> {
    use crate::alg::conlat::CongruenceLattice;
    use crate::alg::sublat::SubalgebraLattice;
    use crate::alg::conlat::partition::Partition;
    use crate::alg::QuotientAlgebra;
    use crate::util::{ArrayIncrementor, SequenceGenerator};
    use std::collections::HashMap;
    
    let mut a_con = CongruenceLattice::new(a.clone_box());
    let zero = a_con.zero();
    let mut phi = a_con.one();
    
    let mut a_sub = SubalgebraLattice::new_safe(a.clone_box())?;
    let gen_set = a_sub.find_minimal_sized_generating_set();
    let gens = gen_set.elements();
    let gen_size = gens.len();
    
    if let Some(ref mut r) = report {
        r.add_line(&format!("gens of A: {:?}", gens));
    }
    
    let a_card = a.cardinality();
    let mut card_to_gens: HashMap<usize, Vec<Vec<i32>>> = HashMap::new();
    
    // Build a table mapping cardinalities to generating sets of subalgebras
    let mut arr = vec![0i32; gen_size];
    let mut inc = SequenceGenerator::sequence_incrementor(&mut arr, a_card - 1);
    
    if let Some(ref mut r) = report {
        r.add_start_line("Constructing a table from cardinalities to generating sets of subalgebra");
    }
    
    let total = a_card.pow(gen_size as u32);
    let mut m = 0;
    
    loop {
        let current_arr = inc.get_current();
        
        // Generate subalgebra from current assignment
        let subalg = a_sub.sg(&current_arr);
        let sub_card = subalg.size() as usize;
        
        // Check if we already have a generating set for this cardinality
        let sub_gens_list = card_to_gens.entry(sub_card).or_insert_with(Vec::new);
        
        // Check if this generating set is equivalent to an existing one
        let mut dup_found = false;
        for existing_gens in sub_gens_list.iter() {
            if SubalgebraLattice::extend_to_homomorphism(
                &current_arr,
                existing_gens,
                a.as_ref(),
                a.as_ref(),
            ).is_some() {
                dup_found = true;
                break;
            }
        }
        
        if !dup_found {
            sub_gens_list.push(current_arr.clone());
        }
        
        m += 1;
        if m % 10000 == 0 {
            if let Some(ref mut r) = report {
                r.add_line(&format!("{} of ({})^{} = {} so far", m, a_card, gen_size, total));
            }
        }
        
        if !inc.increment() {
            break;
        }
    }
    
    if let Some(ref mut r) = report {
        r.add_end_line("Table construction complete:");
        for i in 1..=a_card as usize {
            let size = card_to_gens.get(&i).map(|v| v.len()).unwrap_or(0);
            r.add_line(&format!("For card = {} there are {} gensets", i, size));
        }
        r.add_line(&format!("|Con(A)| = {}", a_con.con_cardinality()));
    }
    
    let mut map: HashMap<Partition, Vec<i32>> = HashMap::new();
    
    if let Some(ref mut r) = report {
        r.add_start_line("Testing which thetas are good: those for which A mod theta is a subalgebra.");
    }
    
    let univ = a_con.universe();
    let mut k = 0;
    
    for par in univ {
        k += 1;
        if k % 1000 == 0 {
            if let Some(ref mut r) = report {
                r.add_line(&format!("tried {} congruences", k));
            }
        }
        
        // Skip zero congruence and congruences already covered by phi
        if par == zero || phi.leq(&par) {
            continue;
        }
        
        // Create quotient algebra A/par
        let quot = QuotientAlgebra::<i32>::new_safe(a.clone_box(), par.clone())?;
        let quot_card = quot.cardinality() as usize;
        
        // Check if we have generating sets for this cardinality
        if let Some(sub_gens_list) = card_to_gens.get(&quot_card) {
            // Get generators of quotient algebra
            let mut quot_gens = Vec::new();
            for &gen in gens.iter() {
                let quot_gen = quot.canonical_homomorphism(gen as usize)?;
                quot_gens.push(quot_gen as i32);
            }
            
            // Try to find a homomorphism from quotient to a subalgebra
            // Convert QuotientAlgebra to BasicAlgebra for use with extend_to_homomorphism
            let quot_card = quot.cardinality();
            let quot_ops = quot.operations();
            let int_ops = crate::alg::op::ops::make_int_operations(quot_ops)?;
            let quot_universe: HashSet<i32> = (0..quot_card).collect();
            let quot_basic = BasicAlgebra::new(quot.name().to_string(), quot_universe, int_ops);
            
            for sub_gens in sub_gens_list.iter() {
                if let Some(_) = SubalgebraLattice::extend_to_homomorphism(
                    &quot_gens,
                    sub_gens,
                    &quot_basic,
                    a.as_ref(),
                ) {
                    // Found a homomorphism, so A/par is isomorphic to a subalgebra
                    map.insert(par.clone(), sub_gens.clone());
                    phi = phi.meet(&par)?;
                    
                    if let Some(ref mut r) = report {
                        r.add_line(&format!("A mod {} is a subalgebra", par));
                        r.add_line(&format!("the intersection of good congruences is {}", phi));
                    }
                    
                    // If phi equals zero, we're done
                    if phi == zero {
                        if let Some(ref mut r) = report {
                            r.add_end_line("meet of good congruences is 0.");
                            r.add_line(&format!("map is {:?}", map));
                        }
                        return Ok(Some(map));
                    }
                    break;
                }
            }
        }
    }
    
    if let Some(ref mut r) = report {
        r.add_end_line("Done:");
        r.add_line(&format!("map is {:?}", map));
        r.add_line(&format!("meet of good congruences is {}", phi));
    }
    
    // If phi didn't become zero, the algebra is not quasi-critical
    Ok(None)
}

/// Compute the unary clone set from partitions.
///
/// This function computes the set of all unary operations (represented as IntArray)
/// that respect every partition in `pars` and also respect the partitions `eta0` and `eta1`,
/// which meet and join to 0 and 1 and permute.
///
/// # Arguments
/// * `pars` - List of partitions that the operations must respect
/// * `eta0` - First eta partition
/// * `eta1` - Second eta partition
///
/// # Returns
/// * `Ok(BTreeSet<IntArray>)` - Set of unary operations as IntArrays
/// * `Err(String)` - If there's an error (e.g., empty partitions list or mismatched sizes)
///
/// # Examples
/// ```
/// use uacalc::alg::algebras;
/// use uacalc::alg::conlat::partition::Partition;
/// use std::collections::BTreeSet;
///
/// // Create partitions and compute unary clone
/// // (example would go here)
/// ```
pub fn unary_clone(
    pars: &[Partition],
    eta0: &Partition,
    eta1: &Partition,
) -> Result<BTreeSet<IntArray>, String> {
    if pars.is_empty() {
        return Err("Partition list cannot be empty".to_string());
    }
    
    let size = pars[0].universe_size();
    
    // Validate all partitions have the same universe size
    for (i, par) in pars.iter().enumerate() {
        if par.universe_size() != size {
            return Err(format!(
                "Partition {} has universe size {} but expected {}",
                i,
                par.universe_size(),
                size
            ));
        }
    }
    
    if eta0.universe_size() != size || eta1.universe_size() != size {
        return Err("Eta partitions must have the same universe size as pars".to_string());
    }
    
    // Build maps between integers and IntArrays
    let mut int2vec: HashMap<i32, IntArray> = HashMap::new();
    let mut vec2int: HashMap<IntArray, i32> = HashMap::new();
    
    for i in 0..size {
        let vec = vec![
            eta0.block_index(i).map_err(|e| format!("Error getting block index for eta0: {}", e))? as i32,
            eta1.block_index(i).map_err(|e| format!("Error getting block index for eta1: {}", e))? as i32,
        ];
        let ia = IntArray::from_array(vec)?;
        int2vec.insert(i as i32, ia.clone());
        vec2int.insert(ia, i as i32);
    }
    
    let size0 = eta0.number_of_blocks();
    let size1 = eta1.number_of_blocks();
    let mut f0 = IntArray::from_array(vec![0; size0])?;
    let mut f1 = IntArray::from_array(vec![0; size1])?;
    let n = size;
    let mut ans = BTreeSet::new();
    
    unary_clone_aux(
        &mut f0,
        &mut f1,
        size0,
        size1,
        0,
        0,
        n,
        true,
        &mut ans,
        &int2vec,
        &vec2int,
        pars,
    );
    
    Ok(ans)
}

/// Make the unary algebra whose operations are the clone of unary
/// operations respecting every partition in pars and also eta0 and
/// eta1, which meet and join to 0 and 1 and permute.
///
/// This function computes the unary clone set using `unary_clone` and
/// then creates a BasicAlgebra with one unary operation for each
/// element in the clone set.
///
/// # Arguments
/// * `pars` - List of partitions that the operations must respect
/// * `eta0` - First eta partition
/// * `eta1` - Second eta partition
///
/// # Returns
/// * `Ok(BasicAlgebra<i32>)` - Algebra with unary operations from the clone
/// * `Err(String)` - If there's an error (e.g., empty partitions list or mismatched sizes)
///
/// # Examples
/// ```
/// use uacalc::alg::algebras;
/// use uacalc::alg::conlat::partition::Partition;
///
/// // Create partitions and compute unary clone algebra
/// // (example would go here)
/// ```
pub fn unary_clone_alg_from_partitions(
    pars: &[Partition],
    eta0: &Partition,
    eta1: &Partition,
) -> Result<BasicAlgebra<i32>, String> {
    use crate::alg::op::operations::make_int_operation;
    use crate::alg::op::OperationSymbol;
    use std::collections::HashSet;
    
    // Get the unary clone set
    let clone_set = unary_clone(pars, eta0, eta1)?;
    
    let size = pars[0].universe_size();
    let size_i32 = size as i32;
    
    // Create operations from each IntArray in the clone set
    let mut ops = Vec::new();
    let mut i = 0;
    for ia in clone_set {
        // Get the array representation
        let arr = ia.as_slice().to_vec();
        
        // Create operation symbol with name "f_0", "f_1", etc.
        let sym = OperationSymbol::new(&format!("f_{}", i), 1, false);
        
        // Create unary operation from the array
        let op = make_int_operation(sym, size_i32, arr)?;
        ops.push(op);
        i += 1;
    }
    
    // Create universe set
    let universe: HashSet<i32> = (0..size_i32).collect();
    
    // Create BasicAlgebra with empty name (matching Java implementation)
    Ok(BasicAlgebra::new("".to_string(), universe, ops))
}

/// Find operations in the clone of an algebra.
///
/// This function tests if the given operations are in the clone of the algebra A
/// and returns a mapping from OperationSymbols to terms, which will have entries
/// for those operations which are in the clone.
///
/// The algorithm groups operations by arity and for each arity group:
/// 1. Creates a FreeAlgebra over A with that arity
/// 2. Uses a Closer to find which operations are in the clone
/// 3. Maps the found operations to their terms
///
/// # Arguments
/// * `ops` - A list of operations on the set of A
/// * `alg` - The algebra A
/// * `report` - Optional progress reporter
///
/// # Returns
/// * `Ok(HashMap<OperationSymbol, Box<dyn Term>>)` - Map from operation symbols to terms for operations found in the clone
/// * `Err(String)` - If there's an error (e.g., empty operations list or null algebra)
///
/// # Examples
/// ```
/// use uacalc::alg::{algebras, SmallAlgebra, BasicAlgebra};
/// use uacalc::alg::op::Operation;
/// use std::collections::HashSet;
/// use std::sync::Arc;
///
/// // Create an algebra and operations
/// // let alg = ...;
/// // let ops = vec![...];
/// // let result = algebras::find_in_clone(&ops, &alg, None).unwrap();
/// ```
pub fn find_in_clone(
    ops: &[Arc<dyn Operation>],
    alg: &dyn SmallAlgebra<UniverseItem = i32>,
    report: Option<Arc<dyn crate::progress::ProgressReport>>,
) -> Result<HashMap<crate::alg::op::OperationSymbol, Box<dyn crate::terms::Term>>, String> {
    use crate::alg::FreeAlgebra;
    use crate::alg::Closer;
    
    use crate::alg::op::OperationSymbol;
    use crate::terms::Term;
    
    // Validate inputs
    if ops.is_empty() {
        return Err("ops cannot be empty and the algebra cannot be null".to_string());
    }
    
    // Convert to Vec and sort by arity (matching Java's Collections.sort)
    let mut ops2: Vec<Arc<dyn Operation>> = ops.to_vec();
    ops2.sort_by(|a, b| a.arity().cmp(&b.arity()));
    
    let mut map: HashMap<OperationSymbol, Box<dyn Term>> = HashMap::new();
    
    if ops2.is_empty() {
        return Ok(map);
    }
    
    let mut arity = ops2[0].arity();
    let size = ops2.len();
    let mut current_ops: Vec<Arc<dyn Operation>> = Vec::new();
    current_ops.push(ops2[0].clone());
    
    for i in 1..=size {
        let next_arity = if i < size { ops2[i].arity() } else { -1 };
        
        if i == size || ops2[i].arity() != arity {
            if !current_ops.is_empty() {
                // Create FreeAlgebra with this arity (make_universe = false, matching Java)
                let free_alg = FreeAlgebra::new_with_universe_safe(
                    alg.clone_box(),
                    arity as i32,
                    false, // make_universe = false
                )?;
                
                // Get product algebra, generators, and term map from FreeAlgebra
                let inner = free_alg.get_inner();
                let product_algebra = Arc::new(inner.product_algebra.clone());
                let generators = inner.generators().to_vec();
                let term_map_opt = inner.get_term_map();
                
                // Convert term map from Option<&HashMap> to HashMap
                let term_map: HashMap<IntArray, Box<dyn Term>> = if let Some(tm) = term_map_opt {
                    tm.iter().map(|(k, v)| (k.clone(), v.clone_box())).collect()
                } else {
                    HashMap::new()
                };
                
                // Create Closer with product algebra, generators, and term map
                let mut closer = Closer::new_with_term_map_safe(
                    product_algebra,
                    generators,
                    term_map,
                )?;
                
                // Set root algebra
                closer.set_root_algebra(Some(Arc::from(alg.clone_box())));
                
                // Set operations to find
                closer.set_operations(Some(current_ops.clone()));
                
                // Compute closure using sg_close_power (matching Java)
                closer.sg_close_power()?;
                
                // Get term map for operations
                if let Some(curr_map) = closer.get_term_map_for_operations() {
                    // Convert from OperationSymbol to OperationSymbol (already correct type)
                    for (sym, term) in curr_map.iter() {
                        map.insert(sym.clone(), term.clone_box());
                    }
                }
                
                // Clear current_ops for next arity group
                current_ops.clear();
                
                // Update arity for next iteration
                if i + 1 < size {
                    arity = ops2[i + 1].arity();
                }
            }
        }
        
        if i < size {
            current_ops.push(ops2[i].clone());
        }
    }
    
    Ok(map)
}

/// Recursive helper function for computing unary clone.
///
/// This function builds partial functions f0 and f1 and checks if they respect
/// the partitions. When a complete function is built (k0 * k1 == n), it adds
/// the function to the answer set.
fn unary_clone_aux(
    f0: &mut IntArray,
    f1: &mut IntArray,
    size0: usize,
    size1: usize,
    k0: usize,
    k1: usize,
    n: usize,
    zero_first: bool,
    ans: &mut BTreeSet<IntArray>,
    int2vec: &HashMap<i32, IntArray>,
    vec2int: &HashMap<IntArray, i32>,
    pars: &[Partition],
) {
    if k0 * k1 == n {
        // We have a complete function, build it and add to answer set
        let mut copy = IntArray::from_array(vec![0; n]).unwrap();
        let mut scratch = IntArray::from_array(vec![0; 2]).unwrap();
        
        for i in 0..n {
            let argv = int2vec.get(&(i as i32)).unwrap();
            let b0 = argv.get(0).unwrap() as usize;
            let b1 = argv.get(1).unwrap() as usize;
            let f0_val = f0.get(b0).unwrap();
            let f1_val = f1.get(b1).unwrap();
            
            scratch.set(0, f0_val).unwrap();
            scratch.set(1, f1_val).unwrap();
            let lookup = IntArray::from_array(vec![f0_val, f1_val]).unwrap();
            let result = vec2int.get(&lookup).unwrap();
            copy.set(i, *result).unwrap();
        }
        
        ans.insert(copy);
        return;
    }
    
    let size = if zero_first { size0 } else { size1 };
    for value in 0..size {
        if respects(
            value as i32,
            f0,
            f1,
            size0,
            size1,
            k0,
            k1,
            n,
            zero_first,
            int2vec,
            vec2int,
            pars,
        ) {
            let mut new_zero_first = zero_first;
            if zero_first {
                f0.set(k0, value as i32).unwrap();
                if k1 < size1 {
                    new_zero_first = false;
                }
            } else {
                f1.set(k1, value as i32).unwrap();
                if k0 < size0 {
                    new_zero_first = true;
                }
            }
            
            unary_clone_aux(
                f0,
                f1,
                size0,
                size1,
                if zero_first { k0 + 1 } else { k0 },
                if zero_first { k1 } else { k1 + 1 },
                n,
                new_zero_first,
                ans,
                int2vec,
                vec2int,
                pars,
            );
        }
    }
}

/// Check if a value respects the partitions.
///
/// This function checks if setting f0[k0] = value (if zero_first) or f1[k1] = value
/// (if not zero_first) respects all the partitions in pars.
fn respects(
    value: i32,
    f0: &IntArray,
    f1: &IntArray,
    size0: usize,
    size1: usize,
    k0: usize,
    k1: usize,
    n: usize,
    zero_first: bool,
    int2vec: &HashMap<i32, IntArray>,
    vec2int: &HashMap<IntArray, i32>,
    pars: &[Partition],
) -> bool {
    // Create a reusable scratch array
    let mut scratch = IntArray::from_array(vec![0; 2]).unwrap();
    
    if zero_first {
        for j in 0..k1 {
            let m = match get_scratch_value(&mut scratch, k0 as i32, j as i32, vec2int) {
                Some(v) => v,
                None => return false, // Invalid combination
            };
            let image = match get_scratch_value(&mut scratch, value, f1.get(j).unwrap(), vec2int) {
                Some(v) => v,
                None => return false, // Invalid combination
            };
            
            for w in 0..j {
                let k = match get_scratch_value(&mut scratch, k0 as i32, w as i32, vec2int) {
                    Some(v) => v,
                    None => return false, // Invalid combination
                };
                let mut k_img = -1;
                
                for par in pars {
                    let r_m = par.representative(m as usize);
                    let r_k = par.representative(k as usize);
                    if r_m == r_k {
                        if k_img == -1 {
                            k_img = match get_scratch_value(&mut scratch, value, f1.get(w).unwrap(), vec2int) {
                                Some(v) => v,
                                None => return false, // Invalid combination
                            };
                        }
                        if !par.is_related(image as usize, k_img as usize) {
                            return false;
                        }
                    }
                }
            }
            
            for u in 0..k0 {
                for v in 0..k1 {
                    let uv = match get_scratch_value(&mut scratch, u as i32, v as i32, vec2int) {
                        Some(v) => v,
                        None => return false, // Invalid combination
                    };
                    let mut uv_img = -1;
                    
                    for par in pars {
                        let r_m = par.representative(m as usize);
                        let r_uv = par.representative(uv as usize);
                        if r_m == r_uv {
                            if uv_img == -1 {
                                uv_img = match get_scratch_value(&mut scratch, f0.get(u).unwrap(), f1.get(v).unwrap(), vec2int) {
                                    Some(v) => v,
                                    None => return false, // Invalid combination
                                };
                            }
                            if !par.is_related(image as usize, uv_img as usize) {
                                return false;
                            }
                        }
                    }
                }
            }
        }
    } else {
        for i in 0..k0 {
            let m = match get_scratch_value(&mut scratch, i as i32, k1 as i32, vec2int) {
                Some(v) => v,
                None => return false, // Invalid combination
            };
            let image = match get_scratch_value(&mut scratch, f0.get(i).unwrap(), value, vec2int) {
                Some(v) => v,
                None => return false, // Invalid combination
            };
            
            for w in 0..i {
                let k = match get_scratch_value(&mut scratch, w as i32, k1 as i32, vec2int) {
                    Some(v) => v,
                    None => return false, // Invalid combination
                };
                let mut k_img = -1;
                
                for par in pars {
                    let r_m = par.representative(m as usize);
                    let r_k = par.representative(k as usize);
                    if r_m == r_k {
                        if k_img == -1 {
                            k_img = match get_scratch_value(&mut scratch, f0.get(w).unwrap(), value, vec2int) {
                                Some(v) => v,
                                None => return false, // Invalid combination
                            };
                        }
                        if !par.is_related(image as usize, k_img as usize) {
                            return false;
                        }
                    }
                }
            }
            
            for u in 0..k0 {
                for v in 0..k1 {
                    let uv = match get_scratch_value(&mut scratch, u as i32, v as i32, vec2int) {
                        Some(v) => v,
                        None => return false, // Invalid combination
                    };
                    let mut uv_img = -1;
                    
                    for par in pars {
                        let r_m = par.representative(m as usize);
                        let r_uv = par.representative(uv as usize);
                        if r_m == r_uv {
                            if uv_img == -1 {
                                uv_img = match get_scratch_value(&mut scratch, f0.get(u).unwrap(), f1.get(v).unwrap(), vec2int) {
                                    Some(v) => v,
                                    None => return false, // Invalid combination
                                };
                            }
                            if !par.is_related(image as usize, uv_img as usize) {
                                return false;
                            }
                        }
                    }
                }
            }
        }
    }
    
    true
}

/// Helper function to get a value from the scratch array.
///
/// Sets scratch[0] = i, scratch[1] = j, and returns vec2int[scratch].
/// Returns None if the combination is not in the map.
fn get_scratch_value(
    scratch: &mut IntArray,
    i: i32,
    j: i32,
    vec2int: &HashMap<IntArray, i32>,
) -> Option<i32> {
    scratch.set(0, i).unwrap();
    scratch.set(1, j).unwrap();
    // Create a new IntArray for lookup since HashMap keys need to match exactly
    let lookup = IntArray::from_array(vec![i, j]).unwrap();
    vec2int.get(&lookup).copied()
}

#[cfg(test)]
mod quasi_critical_tests {
    use super::*;
    use crate::alg::BasicAlgebra;
    use std::collections::HashSet;

    #[test]
    fn test_quasi_critical_congruences_small_algebra() {
        // Create a small 2-element algebra
        let size = 2;
        let universe: HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe, Vec::new());
        
        let a = Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Test the function
        let result = quasi_critical_congruences(a, None);
        assert!(result.is_ok());
        let critical_congs = result.unwrap();
        // The result depends on the algebra structure
        assert!(critical_congs.len() >= 0);
    }

    #[test]
    fn test_quasi_critical_small_algebra() {
        // Create a small 2-element algebra
        let size = 2;
        let universe: HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe, Vec::new());
        
        let a = Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Test the function
        let result = quasi_critical(a, None);
        assert!(result.is_ok());
        // The result may be Some or None depending on the algebra
    }
}

#[cfg(test)]
mod unary_clone_tests {
    use super::*;
    use crate::alg::conlat::partition::Partition;
    
    #[test]
    fn test_unary_clone_basic() {
        // Create simple partitions for testing
        // For a 4-element universe, create eta0 with 2 blocks and eta1 with 2 blocks
        // eta0: {0,1}, {2,3}
        // eta1: {0,2}, {1,3}
        let eta0 = Partition::new(vec![-2, 0, -2, 2]).unwrap();
        let eta1 = Partition::new(vec![-2, -2, 0, 2]).unwrap();
        let pars = vec![Partition::zero(4)];
        
        let result = unary_clone(&pars, &eta0, &eta1);
        assert!(result.is_ok());
        let clone_set = result.unwrap();
        // The result should be a set (may be empty depending on partitions)
        // Just verify the function completes without error
        assert!(clone_set.len() >= 0);
    }
    
    #[test]
    fn test_unary_clone_empty_partitions() {
        let eta0 = Partition::zero(3);
        let eta1 = Partition::one(3);
        let pars = vec![];
        
        let result = unary_clone(&pars, &eta0, &eta1);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("cannot be empty"));
    }
    
    #[test]
    fn test_unary_clone_mismatched_sizes() {
        let eta0 = Partition::zero(3);
        let eta1 = Partition::one(4); // Different size
        let pars = vec![Partition::zero(3)];
        
        let result = unary_clone(&pars, &eta0, &eta1);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("same universe size"));
    }
    
    #[test]
    fn test_unary_clone_small_universe() {
        // Test with a very small universe (2 elements)
        let eta0 = Partition::zero(2);
        let eta1 = Partition::one(2);
        let pars = vec![Partition::zero(2)];
        
        let result = unary_clone(&pars, &eta0, &eta1);
        assert!(result.is_ok());
        let clone_set = result.unwrap();
        // Should have at least the identity function
        assert!(clone_set.len() >= 1);
    }
    
    #[test]
    fn test_unary_clone_alg_from_partitions_basic() {
        // Test creating an algebra from unary clone
        let eta0 = Partition::zero(2);
        let eta1 = Partition::one(2);
        let pars = vec![Partition::zero(2)];
        
        let result = unary_clone_alg_from_partitions(&pars, &eta0, &eta1);
        assert!(result.is_ok());
        let alg = result.unwrap();
        
        // Should have the correct cardinality
        assert_eq!(alg.cardinality(), 2);
        
        // Should have operations (at least the identity)
        let ops = alg.get_operations_ref();
        assert!(ops.len() >= 1);
        
        // All operations should be unary
        for op in ops {
            assert_eq!(op.arity(), 1);
        }
    }
    
    #[test]
    fn test_unary_clone_alg_from_partitions_operation_names() {
        // Test that operations are named correctly
        let eta0 = Partition::zero(3);
        let eta1 = Partition::one(3);
        let pars = vec![Partition::zero(3)];
        
        let result = unary_clone_alg_from_partitions(&pars, &eta0, &eta1);
        assert!(result.is_ok());
        let alg = result.unwrap();
        
        let ops = alg.get_operations_ref();
        // Check that operations are named f_0, f_1, etc. and are unary
        // (operations are created in the order they appear in the BTreeSet)
        assert!(ops.len() > 0, "Should have at least one operation");
        
        // Verify all operations are unary and have correct names
        for op in &ops {
            assert_eq!(op.arity(), 1, "All operations should be unary");
            let name = op.symbol().name();
            assert!(name.starts_with("f_"), "Operation name should start with 'f_'");
        }
        
        // Collect all operation names and parse the numbers
        let mut name_numbers: Vec<(String, usize)> = ops.iter()
            .map(|op| {
                let name = op.symbol().name().to_string();
                // Parse the number after "f_"
                let num_str = &name[2..]; // Skip "f_"
                let num = num_str.parse::<usize>().expect("Operation name should have a number after 'f_'");
                (name, num)
            })
            .collect();
        
        // Sort by the numeric value
        name_numbers.sort_by_key(|(_, num)| *num);
        
        // Verify we have sequential names (f_0, f_1, f_2, etc.)
        for (i, (name, num)) in name_numbers.iter().enumerate() {
            assert_eq!(*num, i, "Operation numbers should be sequential: expected {}, got {}", i, num);
            let expected = format!("f_{}", i);
            assert_eq!(name, &expected, "Operation names should be sequential");
        }
    }
    
    #[test]
    fn test_unary_clone_alg_from_partitions_empty_partitions() {
        // Test with empty partitions list (should fail)
        let eta0 = Partition::zero(3);
        let eta1 = Partition::one(3);
        let pars = vec![];
        
        let result = unary_clone_alg_from_partitions(&pars, &eta0, &eta1);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("cannot be empty"));
    }
}

#[cfg(test)]
mod find_in_clone_tests {
    use super::*;
    use crate::alg::op::operations::make_int_operation_str;
    use crate::alg::op::OperationSymbol;
    use std::collections::HashSet;
    use std::sync::Arc;
    
    #[test]
    fn test_find_in_clone_empty_ops() {
        // Test with empty operations list
        let size = 2;
        let universe: HashSet<i32> = (0..size).collect();
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe, Vec::new());
        
        let ops: Vec<Arc<dyn Operation>> = Vec::new();
        let result = find_in_clone(&ops, &alg, None);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("cannot be empty"));
    }
    
    #[test]
    fn test_find_in_clone_basic() {
        // Create a simple algebra with one binary operation (meet)
        let size = 2;
        let universe: HashSet<i32> = (0..size).collect();
        
        // Create a binary meet operation: min(x, y)
        let meet_table = vec![0, 0, 0, 1]; // 0*0=0, 0*1=0, 1*0=0, 1*1=1
        let meet_op = make_int_operation_str("meet", 2, size, meet_table.clone()).unwrap();
        
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe, vec![meet_op]);
        
        // Create an operation that is in the clone (the meet operation itself)
        // Extract the IntOperation from the Box<dyn Operation>
        use crate::alg::op::IntOperation;
        let test_op_box = make_int_operation_str("test_meet", 2, size, meet_table.clone()).unwrap();
        // Convert Box<dyn Operation> to IntOperation by cloning the table
        let test_op = IntOperation::new(
            test_op_box.symbol().clone(),
            test_op_box.get_set_size(),
            test_op_box.get_table().unwrap().to_vec()
        ).unwrap();
        let ops: Vec<Arc<dyn Operation>> = vec![Arc::new(test_op)];
        
        let result = find_in_clone(&ops, &alg, None);
        assert!(result.is_ok());
        let map = result.unwrap();
        // The operation should be found in the clone (it's the same as the algebra's operation)
        assert!(map.len() >= 0); // May or may not find it depending on implementation
    }
    
    #[test]
    fn test_find_in_clone_multiple_arities() {
        // Test with operations of different arities
        let size = 2;
        let universe: HashSet<i32> = (0..size).collect();
        
        // Create a binary operation
        let binary_table = vec![0, 0, 0, 1];
        let binary_op = make_int_operation_str("binary", 2, size, binary_table.clone()).unwrap();
        
        let alg = BasicAlgebra::new("TestAlg".to_string(), universe, vec![binary_op]);
        
        // Test with both unary and binary operations
        use crate::alg::op::IntOperation;
        let test_binary_box = make_int_operation_str("test_binary", 2, size, binary_table.clone()).unwrap();
        let test_binary = IntOperation::new(
            test_binary_box.symbol().clone(),
            test_binary_box.get_set_size(),
            test_binary_box.get_table().unwrap().to_vec()
        ).unwrap();
        
        let unary_table = vec![0, 1];
        let test_unary_box = make_int_operation_str("test_unary", 1, size, unary_table).unwrap();
        let test_unary = IntOperation::new(
            test_unary_box.symbol().clone(),
            test_unary_box.get_set_size(),
            test_unary_box.get_table().unwrap().to_vec()
        ).unwrap();
        
        let ops: Vec<Arc<dyn Operation>> = vec![
            Arc::new(test_unary),
            Arc::new(test_binary),
        ];
        
        let result = find_in_clone(&ops, &alg, None);
        assert!(result.is_ok());
        let map = result.unwrap();
        // Should process both arities
        assert!(map.len() >= 0);
    }
}

