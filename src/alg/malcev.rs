/* malcev.rs
 *
 * This module provides static methods for Mal'cev conditions such as finding
 * Jonsson terms, etc. It also has methods for related things such as
 * finding a near unanimity term of a given arity, finding a near
 * majority term, etc.
 *
 * Based on org.uacalc.alg.Malcev.java
 */

use crate::alg::{SmallAlgebra, BigProductAlgebra, FreeAlgebra, BasicSmallAlgebra, Closer};
use crate::terms::{Term, VariableImp};
use crate::util::int_array::IntArray;
use std::collections::{HashMap, HashSet};
use std::sync::Arc;

/// A module with static functions for Mal'cev conditions and term finding algorithms.
///
/// This module provides functions to:
/// - Find Jonsson terms
/// - Find near unanimity terms
/// - Find majority/minority/Pixley terms
/// - Test for congruence distributivity/modularity
/// - Test various algebraic properties

/// Helper function to convert a generic algebra to i32 algebra for term finding.
/// For now, this is a placeholder - in practice, algebras used with Malcev
/// functions should already be i32-based (BasicSmallAlgebra<i32>).
/// This function will be properly implemented when needed for non-i32 algebras.
fn convert_to_i32_algebra<T>(_alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Box<dyn SmallAlgebra<UniverseItem = i32>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // For now, we assume the input algebra can be cast or converted
    // This is a simplified version - full implementation would need to
    // properly map operations from T to i32
    
    // Try to use the algebra directly if it's already i32-based
    // Otherwise, we'd need a more sophisticated conversion
    Err("Algebra conversion from generic type to i32 not yet fully implemented. Please use i32-based algebras directly.".to_string())
}

/// Check if an algebra has a Malcev term.
///
/// A Malcev term is a ternary term m(x,y,z) satisfying:
/// - m(x,x,y) = y
/// - m(x,y,y) = x
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Term))` - A Malcev term if one exists
/// * `Ok(None)` - No Malcev term exists
/// * `Err(String)` - If there's an error during computation
///
/// # Examples
/// ```
/// use uacalc::alg::malcev;
/// // Example would require an actual algebra
/// // let term = malcev::malcev_term(&alg)?;
/// ```
pub fn malcev_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if alg.cardinality() == 1 {
        return Ok(Some(Box::new(VariableImp::x())));
    }
    
    // Convert the algebra to i32-based for use with FreeAlgebra
    // Extract operations and create a new BasicSmallAlgebra with i32 universe
    let card = alg.cardinality();
    let ops = alg.operations();
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    // Make operation tables (via Algebra trait)
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Create BigProductAlgebra (F(2)^2) - power of the free algebra
    // FreeAlgebra implements SmallAlgebra<UniverseItem = IntArray>
    // We need to box the free algebra to create the power
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_squared = BigProductAlgebra::new_power_safe(f2_boxed, 2)?;
    
    // Create generators: elements of F(2)^2
    // These are IntArrays representing pairs of indices into F(2)
    // (x,x) = first generator, (x,y) = second generator, (y,y) = third generator
    // But we need to map these to actual indices in F(2)
    
    // Actually, in F(2), the generators are at indices 0 and 1 (for x and y)
    // So (x,x) in F(2)^2 would be represented as an IntArray [0, 0]
    let g0 = IntArray::from_array(vec![0, 0])?;
    let g1 = IntArray::from_array(vec![0, 1])?;
    let g2 = IntArray::from_array(vec![1, 1])?;
    let gens = vec![g0.clone(), g1.clone(), g2.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::x()));
    term_map.insert(g1.clone(), Box::new(VariableImp::y()));
    term_map.insert(g2.clone(), Box::new(VariableImp::z()));
    
    // The element we're looking for: (y,x) = [1, 0]
    let yx = IntArray::from_array(vec![1, 0])?;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_squared),
        gens,
        term_map,
    )?;
    closer.set_element_to_find(Some(yx.clone()));
    
    let closure = closer.sg_close_power()?;
    if closure.contains(&yx) {
        if let Some(term) = closer.get_term_map().and_then(|tm| tm.get(&yx).map(|t| t.clone_box())) {
            return Ok(Some(term));
        }
    }
    
    Ok(None)
}

/// Find a majority term for the algebra.
///
/// A majority term is a ternary term m(x,y,z) satisfying:
/// - m(x,x,y) = x
/// - m(x,y,x) = x
/// - m(y,x,x) = x
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Term))` - A majority term if one exists
/// * `Ok(None)` - No majority term exists
/// * `Err(String)` - If there's an error during computation
pub fn majority_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if alg.cardinality() == 1 {
        return Ok(Some(Box::new(VariableImp::x())));
    }
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    
    // Check if operations are empty
    if ops.is_empty() {
        return Err("Algebra has no operations".to_string());
    }
    
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Get F(2) info before moving it
    let f2_cardinality = f2.cardinality();
    
    // Create BigProductAlgebra (F(2)^3)
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_cubed = BigProductAlgebra::new_power_safe(f2_boxed, 3)?;
    
    // Create generators: (x,x,y), (x,y,x), (y,x,x)
    // Use indices 0 and 1 from F(2)'s universe
    let g0 = IntArray::from_array(vec![0, 0, 1])?;  // (x,x,y)
    let g1 = IntArray::from_array(vec![0, 1, 0])?;  // (x,y,x)
    let g2 = IntArray::from_array(vec![1, 0, 0])?;  // (y,x,x)
    let gens = vec![g0.clone(), g1.clone(), g2.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::x()));
    term_map.insert(g1.clone(), Box::new(VariableImp::y()));
    term_map.insert(g2.clone(), Box::new(VariableImp::z()));
    
    // The element we're looking for: (x,x,x) = [0,0,0]
    let xxx = IntArray::from_array(vec![0, 0, 0])?;
    
    // DEBUG: Print information about the closure setup
    use crate::util::int_array::IntArrayTrait;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_cubed.clone()),
        gens.clone(),
        term_map,
    )?;
    closer.set_element_to_find(Some(xxx.clone()));
    
    let closure = closer.sg_close_power()?;
     
    if closure.contains(&xxx) {
        if let Some(term) = closer.get_term_map().and_then(|tm| tm.get(&xxx).map(|t| t.clone_box())) {
            return Ok(Some(term));
        }
    }
    
    Ok(None)
}

/// Find a minority term for the algebra.
///
/// A minority term is a ternary term m(x,y,z) where the output agrees with
/// the minority value among x, y, z.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Term))` - A minority term if one exists
/// * `Ok(None)` - No minority term exists
/// * `Err(String)` - If there's an error during computation
pub fn minority_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if alg.cardinality() == 1 {
        return Ok(Some(Box::new(VariableImp::x())));
    }
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    
    // Check if operations are empty
    if ops.is_empty() {
        return Err("Algebra has no operations".to_string());
    }
    
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Create BigProductAlgebra (F(2)^3)
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_cubed = BigProductAlgebra::new_power_safe(f2_boxed, 3)?;
    
    // Create generators: (x,x,y), (x,y,x), (y,x,x)
    let g0 = IntArray::from_array(vec![0, 0, 1])?;  // (x,x,y)
    let g1 = IntArray::from_array(vec![0, 1, 0])?;  // (x,y,x)
    let g2 = IntArray::from_array(vec![1, 0, 0])?;  // (y,x,x)
    let gens = vec![g0.clone(), g1.clone(), g2.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::x()));
    term_map.insert(g1.clone(), Box::new(VariableImp::y()));
    term_map.insert(g2.clone(), Box::new(VariableImp::z()));
    
    // The element we're looking for: (y,y,y) = [1,1,1]
    let yyy = IntArray::from_array(vec![1, 1, 1])?;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_cubed),
        gens,
        term_map,
    )?;
    closer.set_element_to_find(Some(yyy.clone()));
    
    let closure = closer.sg_close_power()?;
    if closure.contains(&yyy) {
        if let Some(term) = closer.get_term_map().and_then(|tm| tm.get(&yyy).map(|t| t.clone_box())) {
            return Ok(Some(term));
        }
    }
    
    Ok(None)
}

/// Find a Pixley term for the algebra.
///
/// A Pixley term is a ternary term p(x,y,z) satisfying:
/// - p(x,x,y) = y
/// - p(x,y,x) = y  
/// - p(y,x,x) = y
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Term))` - A Pixley term if one exists
/// * `Ok(None)` - No Pixley term exists
/// * `Err(String)` - If there's an error during computation
pub fn pixley_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if alg.cardinality() == 1 {
        return Ok(Some(Box::new(VariableImp::x())));
    }
    
    // For idempotent algebras, check if congruence distributive first
    // (Pixley terms exist only in arithmetical varieties)
    // TODO: Implement is_congruence_dist_idempotent check when available
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    
    // Check if operations are empty
    if ops.is_empty() {
        return Err("Algebra has no operations".to_string());
    }
    
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Create BigProductAlgebra (F(2)^3)
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_cubed = BigProductAlgebra::new_power_safe(f2_boxed, 3)?;
    
    // Create generators: (x,x,y), (y,y,y), (y,x,x)
    let g0 = IntArray::from_array(vec![0, 0, 1])?;  // (x,x,y)
    let g1 = IntArray::from_array(vec![1, 1, 1])?;  // (y,y,y)
    let g2 = IntArray::from_array(vec![1, 0, 0])?;  // (y,x,x)
    let gens = vec![g0.clone(), g1.clone(), g2.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::x()));
    term_map.insert(g1.clone(), Box::new(VariableImp::y()));
    term_map.insert(g2.clone(), Box::new(VariableImp::z()));
    
    // The element we're looking for: (x,x,x) = [0,0,0]
    let xxx = IntArray::from_array(vec![0, 0, 0])?;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_cubed),
        gens,
        term_map,
    )?;
    closer.set_element_to_find(Some(xxx.clone()));
    
    let closure = closer.sg_close_power()?;
    if closure.contains(&xxx) {
        if let Some(term) = closer.get_term_map().and_then(|tm| tm.get(&xxx).map(|t| t.clone_box())) {
            return Ok(Some(term));
        }
    }
    
    Ok(None)
}

/// Find a near unanimity (NU) term of the given arity.
///
/// An NU term of arity n is a term t(x₀, x₁, ..., xₙ₋₁) such that:
/// - t(y,x,x,...,x) = x
/// - t(x,y,x,...,x) = x
/// - ...
/// - t(x,x,x,...,y) = x
///
/// # Arguments
/// * `alg` - The algebra to check
/// * `arity` - The arity of the NU term to find
///
/// # Returns
/// * `Ok(Some(Term))` - An NU term if one exists
/// * `Ok(None)` - No NU term exists
/// * `Err(String)` - If there's an error during computation
pub fn nu_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>, arity: usize) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if arity < 3 {
        return Err("NU term arity must be at least 3".to_string());
    }
    
    if alg.cardinality() == 1 {
        return Ok(Some(Box::new(VariableImp::new(&format!("x0")))));
    }
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    
    // Check if operations are empty
    if ops.is_empty() {
        return Err("Algebra has no operations".to_string());
    }
    
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Create BigProductAlgebra (F(2)^arity)
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_power = BigProductAlgebra::new_power_safe(f2_boxed, arity)?;
    
    // Create generators: for each position i, set that position to 1 (y) and others to 0 (x)
    let mut gens = Vec::new();
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    
    for i in 0..arity {
        let mut arr = vec![0; arity];
        arr[i] = 1; // Position i is y, others are x
        let gen = IntArray::from_array(arr)?;
        gens.push(gen.clone());
        
        // Map to appropriate variable
        let var = if arity > 3 {
            Box::new(VariableImp::new(&format!("x{}", i))) as Box<dyn Term>
        } else {
            match i {
                0 => Box::new(VariableImp::x()) as Box<dyn Term>,
                1 => Box::new(VariableImp::y()) as Box<dyn Term>,
                _ => Box::new(VariableImp::z()) as Box<dyn Term>,
            }
        };
        term_map.insert(gen, var);
    }
    
    // The element we're looking for: all zeros = (x,x,...,x)
    let zero = IntArray::from_array(vec![0; arity])?;
    
    // Use Closer to find if (x,x,...,x) is in the closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_power),
        gens,
        term_map,
    )?;
    closer.set_element_to_find(Some(zero.clone()));
    
    let closure = closer.sg_close_power()?;
    if closure.contains(&zero) {
        if let Some(term) = closer.get_term_map().and_then(|tm| tm.get(&zero).map(|t| t.clone_box())) {
            return Ok(Some(term));
        }
    }
    
    Ok(None)
}

/// Test if an idempotent algebra has an NU term of the given arity.
///
/// Uses Horowitz's polynomial-time algorithm for idempotent algebras.
///
/// # Arguments
/// * `alg` - The idempotent algebra to check
/// * `arity` - The arity of the NU term to test for
///
/// # Returns
/// * `Ok(true)` - The algebra has an NU term of the given arity
/// * `Ok(false)` - The algebra does not have an NU term
/// * `Err(String)` - If there's an error during computation
pub fn nu_term_idempotent<T>(alg: &dyn SmallAlgebra<UniverseItem = T>, arity: usize) -> Result<bool, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if arity < 3 {
        return Err("NU term arity must be at least 3".to_string());
    }
    
    // TODO: Implement Horowitz's algorithm for testing NU terms
    Err("NU term idempotent test not yet implemented".to_string())
}

/// Find a weak near unanimity term of the given arity.
///
/// A weak NU term satisfies the NU identities except possibly for one position.
///
/// # Arguments
/// * `alg` - The algebra to check
/// * `arity` - The arity of the weak NU term to find
///
/// # Returns
/// * `Ok(Some(Term))` - A weak NU term if one exists
/// * `Ok(None)` - No weak NU term exists
/// * `Err(String)` - If there's an error during computation
pub fn weak_nu_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>, arity: usize) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if arity < 3 {
        return Err("Weak NU term arity must be at least 3".to_string());
    }
    
    // TODO: Implement weak NU term finding algorithm
    Err("Weak NU term finding not yet implemented".to_string())
}

/// Find a weak majority term for the algebra.
///
/// A weak majority term is similar to a majority term but may not satisfy all identities.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Term))` - A weak majority term if one exists
/// * `Ok(None)` - No weak majority term exists
/// * `Err(String)` - If there's an error during computation
pub fn weak_majority_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if alg.cardinality() == 1 {
        return Ok(Some(Box::new(VariableImp::x())));
    }
    
    let is_idempotent = alg.is_idempotent();
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Create generators: (x,x,y), (x,y,x), (y,x,x)
    let g0: IntArray;
    let g1: IntArray;
    let g2: IntArray;
    let power: usize;
    
    if is_idempotent {
        // For idempotent algebras, use F(2)^3
        g0 = IntArray::from_array(vec![0, 0, 1])?;  // (x,x,y)
        g1 = IntArray::from_array(vec![0, 1, 0])?;  // (x,y,x)
        g2 = IntArray::from_array(vec![1, 0, 0])?;  // (y,x,x)
        power = 3;
    } else {
        // For non-idempotent algebras, use F(2)^4
        g0 = IntArray::from_array(vec![0, 0, 1, 0])?;  // (x,x,y,x)
        g1 = IntArray::from_array(vec![0, 1, 0, 0])?;  // (x,y,x,x)
        g2 = IntArray::from_array(vec![1, 0, 0, 0])?;  // (y,x,x,x)
        power = 4;
    }
    
    let gens = vec![g0.clone(), g1.clone(), g2.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::x()));
    term_map.insert(g1.clone(), Box::new(VariableImp::y()));
    term_map.insert(g2.clone(), Box::new(VariableImp::z()));
    
    // Create BigProductAlgebra
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_power = BigProductAlgebra::new_power_safe(f2_boxed, power)?;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_power),
        gens,
        term_map,
    )?;
    
    let closure = closer.sg_close_power()?;
    
    // Look for any element where all coordinates are equal
    // For idempotent: any (a,a,a)
    // For non-idempotent: any (a,a,a,x) where last coord is x (0)
    use crate::util::int_array::IntArrayTrait;
    let term_map_ref = closer.get_term_map();
    for elem in &closure {
        let size = elem.universe_size();
        if size >= 3 {
            // Check if first three coordinates are equal
            if let (Some(v0), Some(v1), Some(v2)) = (elem.get(0), elem.get(1), elem.get(2)) {
                if v0 == v1 && v1 == v2 {
                    if is_idempotent {
                        // For idempotent, any (a,a,a) works
                        if let Some(tm) = term_map_ref {
                            if let Some(term) = tm.get(elem).map(|t| t.clone_box()) {
                                return Ok(Some(term));
                            }
                        }
                    } else {
                        // For non-idempotent, need last coord to be x (0)
                        if size == 4 {
                            if let Some(v3) = elem.get(3) {
                                if v3 == 0 {
                                    if let Some(tm) = term_map_ref {
                                        if let Some(term) = tm.get(elem).map(|t| t.clone_box()) {
                                            return Ok(Some(term));
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    Ok(None)
}

/// Find a semilattice term for the algebra.
///
/// A semilattice term is a binary term that is idempotent, commutative, and associative.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Term))` - A semilattice term if one exists
/// * `Ok(None)` - No semilattice term exists
/// * `Err(String)` - If there's an error during computation
pub fn semilattice_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement semilattice term finding algorithm
    Err("Semilattice term finding not yet implemented".to_string())
}

/// Find a difference term for the algebra.
///
/// A difference term is a ternary term d(x,y,z) such that d(x,y,y) = x.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Term))` - A difference term if one exists
/// * `Ok(None)` - No difference term exists
/// * `Err(String)` - If there's an error during computation
pub fn difference_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement difference term finding algorithm
    Err("Difference term finding not yet implemented".to_string())
}

/// Helper function to convert a path of IntArrays to a list of Terms.
fn path2_term_list(
    path: &[IntArray],
    term_map: &HashMap<IntArray, Box<dyn Term>>,
) -> Vec<Box<dyn Term>> {
    let mut ans = Vec::new();
    for ia in path {
        if let Some(term) = term_map.get(ia) {
            ans.push(term.clone_box());
        }
    }
    ans
}

/// Helper function to find a path from g0 to g2 in middleZero.
/// Two triples are connected by an edge if either their first or third coordinates agree.
/// When alvin_variant is true, it starts with changing the third coordinate; otherwise the first.
fn jonsson_level_path(
    middle_zero: &mut [IntArray],
    g0: &IntArray,
    g2: &IntArray,
    alvin_variant: bool,
) -> Option<Vec<IntArray>> {
    use crate::util::int_array::IntArrayTrait;
    
    // Sort middle_zero for consistent processing
    middle_zero.sort_by(|a, b| {
        for i in 0..a.universe_size().min(b.universe_size()) {
            if let (Some(va), Some(vb)) = (a.get(i), b.get(i)) {
                if va < vb {
                    return std::cmp::Ordering::Less;
                } else if va > vb {
                    return std::cmp::Ordering::Greater;
                }
            }
        }
        std::cmp::Ordering::Equal
    });
    
    // Build equivalence classes: classes0 groups by first coordinate, classes2 by third coordinate
    use std::collections::HashMap as StdHashMap;
    let mut classes0: StdHashMap<i32, Vec<IntArray>> = StdHashMap::new();
    let mut classes2: StdHashMap<i32, Vec<IntArray>> = StdHashMap::new();
    
    for ia in middle_zero.iter() {
        if let Some(v0) = ia.get(0) {
            classes0.entry(v0).or_insert_with(Vec::new).push(ia.clone());
        }
        if let Some(v2) = ia.get(2) {
            classes2.entry(v2).or_insert_with(Vec::new).push(ia.clone());
        }
    }
    
    let mut levels: Vec<Vec<IntArray>> = Vec::new();
    let mut parent_map: StdHashMap<IntArray, IntArray> = StdHashMap::new();
    let mut visited: StdHashMap<IntArray, ()> = StdHashMap::new();
    let mut current_level = vec![g0.clone()];
    visited.insert(g0.clone(), ());
    levels.push(current_level.clone());
    
    let mut even = alvin_variant;
    
    loop {
        even = !even;
        let mut next_level = Vec::new();
        
        for ia in &current_level {
            let eqclass = if even {
                ia.get(0).and_then(|v0| classes0.get(&v0))
            } else {
                ia.get(2).and_then(|v2| classes2.get(&v2))
            };
            
            if let Some(class) = eqclass {
                for ia2 in class {
                    if !visited.contains_key(ia2) {
                        parent_map.insert(ia2.clone(), ia.clone());
                        visited.insert(ia2.clone(), ());
                        next_level.push(ia2.clone());
                    }
                    if ia2 == g2 {
                        // Reconstruct path from g2 back to g0
                        let mut path = vec![g2.clone()];
                        let mut current = parent_map.get(g2).cloned();
                        while let Some(prev) = current {
                            path.push(prev.clone());
                            if prev == *g0 {
                                break;
                            }
                            current = parent_map.get(&prev).cloned();
                        }
                        path.reverse();
                        return Some(path);
                    }
                }
            }
        }
        
        if next_level.is_empty() {
            break;
        }
        levels.push(next_level.clone());
        current_level = next_level;
    }
    
    None
}

/// Find Jonsson terms for the algebra.
///
/// Jonsson terms are a sequence of terms satisfying certain conditions related to
/// congruence meet-semidistributivity.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Vec<Term>))` - Jonsson terms if they exist
/// * `Ok(None)` - No Jonsson terms exist
/// * `Err(String)` - If there's an error during computation
pub fn jonsson_terms<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Vec<Box<dyn Term>>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    let alvin_variant = false; // Use standard Jonsson variant
    
    // Check if idempotent - if so, verify congruence distributivity first
    if alg.is_idempotent() {
        if !is_congruence_dist_idempotent(alg)? {
            return Ok(None);
        }
    }
    
    if alg.cardinality() == 1 {
        let mut ans: Vec<Box<dyn Term>> = Vec::new();
        ans.push(Box::new(VariableImp::x()) as Box<dyn Term>);
        ans.push(Box::new(VariableImp::z()) as Box<dyn Term>);
        return Ok(Some(ans));
    }
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    
    // Check if operations are empty
    if ops.is_empty() {
        return Err("Algebra has no operations".to_string());
    }
    
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Create generators: (x,x,y), (x,y,x), (y,x,x)
    let g0 = IntArray::from_array(vec![0, 0, 1])?;
    let g1 = IntArray::from_array(vec![0, 1, 0])?;
    let g2 = IntArray::from_array(vec![1, 0, 0])?;
    let gens = vec![g0.clone(), g1.clone(), g2.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::x()));
    term_map.insert(g1.clone(), Box::new(VariableImp::y()));
    term_map.insert(g2.clone(), Box::new(VariableImp::z()));
    
    // Create BigProductAlgebra (F(2)^3)
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_cubed = BigProductAlgebra::new_power_safe(f2_boxed, 3)?;
    
    let zero = IntArray::from_array(vec![0, 0, 0])?;
    let pixley = IntArray::from_array(vec![1, 0, 1])?;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_cubed),
        gens,
        term_map,
    )?;
    
    let closure = closer.sg_close_power()?;
    let term_map_ref = closer.get_term_map().ok_or("Term map missing")?;
    
    // Check for Pixley term (for alvin variant)
    if alvin_variant && closure.contains(&pixley) {
        if let Some(term) = term_map_ref.get(&pixley).map(|t| t.clone_box()) {
            let mut ans: Vec<Box<dyn Term>> = Vec::new();
            ans.push(Box::new(VariableImp::x()) as Box<dyn Term>);
            ans.push(term);
            ans.push(Box::new(VariableImp::z()) as Box<dyn Term>);
            return Ok(Some(ans));
        }
    }
    
    // Check for majority term (zero)
    if !alvin_variant && closure.contains(&zero) {
        if let Some(term) = term_map_ref.get(&zero).map(|t| t.clone_box()) {
            let mut ans: Vec<Box<dyn Term>> = Vec::new();
            ans.push(Box::new(VariableImp::x()) as Box<dyn Term>);
            ans.push(term);
            ans.push(Box::new(VariableImp::z()) as Box<dyn Term>);
            return Ok(Some(ans));
        }
    }
    
    // Find middle zero elements (where second coordinate is 0)
    use crate::util::int_array::IntArrayTrait;
    let mut middle_zero: Vec<IntArray> = closure.iter()
        .filter(|ia| (*ia).get(1) == Some(0))
        .cloned()
        .collect();
    
    // Find paths
    let path = jonsson_level_path(&mut middle_zero, &g0, &g2, false);
    let path2 = jonsson_level_path(&mut middle_zero, &g0, &g2, true);
    
    if path.is_none() {
        if let Some(p) = path2 {
            let mut ans = path2_term_list(&p, term_map_ref);
            if !alvin_variant {
                ans.insert(0, ans[0].clone_box());
            }
            return Ok(Some(ans));
        }
        return Ok(None);
    }
    
    if path2.is_none() || path.as_ref().unwrap().len() < path2.as_ref().unwrap().len() {
        if let Some(p) = path {
            let mut ans = path2_term_list(&p, term_map_ref);
            if alvin_variant {
                ans.insert(0, ans[0].clone_box());
            }
            return Ok(Some(ans));
        }
    }
    
    if let Some(p) = path2 {
        let mut ans = path2_term_list(&p, term_map_ref);
        if !alvin_variant {
            ans.insert(0, ans[0].clone_box());
        }
        Ok(Some(ans))
    } else if let Some(p) = path {
        Ok(Some(path2_term_list(&p, term_map_ref)))
    } else {
        Ok(None)
    }
}

/// Find Hagemann-Mitschke terms for the algebra.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Vec<Term>))` - Hagemann-Mitschke terms if they exist
/// * `Ok(None)` - No Hagemann-Mitschke terms exist
/// * `Err(String)` - If there's an error during computation
pub fn hagemann_mitschke_terms<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Vec<Box<dyn Term>>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement Hagemann-Mitschke terms finding algorithm
    Err("Hagemann-Mitschke terms finding not yet implemented".to_string())
}

/// Find Gumm terms for the algebra.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Vec<Term>))` - Gumm terms if they exist
/// * `Ok(None)` - No Gumm terms exist
/// * `Err(String)` - If there's an error during computation
pub fn gumm_terms<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Vec<Box<dyn Term>>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement Gumm terms finding algorithm
    Err("Gumm terms finding not yet implemented".to_string())
}

/// Get a join term (Kearnes-Kiss) for the algebra.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Term))` - A join term if one exists
/// * `Ok(None)` - No join term exists
/// * `Err(String)` - If there's an error during computation
pub fn join_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if alg.cardinality() == 1 {
        return Ok(Some(Box::new(VariableImp::x()) as Box<dyn Term>));
    }
    
    // Get the MMST term
    let taylor = markovic_mckenzie_siggers_taylor_term(alg)?;
    let taylor = match taylor {
        Some(t) => t,
        None => return Ok(None),
    };
    
    // Create substitution maps (using variable names as keys)
    let mut map: HashMap<String, Box<dyn Term>> = HashMap::new();
    
    // t0 = taylor(x, x, y, y)
    map.insert("x0".to_string(), Box::new(VariableImp::x()) as Box<dyn Term>);
    map.insert("x1".to_string(), Box::new(VariableImp::x()) as Box<dyn Term>);
    map.insert("x2".to_string(), Box::new(VariableImp::y()) as Box<dyn Term>);
    map.insert("x3".to_string(), Box::new(VariableImp::y()) as Box<dyn Term>);
    let t0 = taylor.substitute(&map)?;
    
    // t1 = taylor(x, x, y, x)
    map.clear();
    map.insert("x0".to_string(), Box::new(VariableImp::x()) as Box<dyn Term>);
    map.insert("x1".to_string(), Box::new(VariableImp::x()) as Box<dyn Term>);
    map.insert("x2".to_string(), Box::new(VariableImp::y()) as Box<dyn Term>);
    map.insert("x3".to_string(), Box::new(VariableImp::x()) as Box<dyn Term>);
    let t1 = taylor.substitute(&map)?;
    
    // t2 = taylor(y, x, x, x)
    map.clear();
    map.insert("x0".to_string(), Box::new(VariableImp::y()) as Box<dyn Term>);
    map.insert("x1".to_string(), Box::new(VariableImp::x()) as Box<dyn Term>);
    map.insert("x2".to_string(), Box::new(VariableImp::x()) as Box<dyn Term>);
    map.insert("x3".to_string(), Box::new(VariableImp::x()) as Box<dyn Term>);
    let t2 = taylor.substitute(&map)?;
    
    // t3 = t2
    let t3 = t2.clone_box();
    
    // Final substitution: taylor(t0, t1, t2, t3)
    map.clear();
    map.insert("x0".to_string(), t0);
    map.insert("x1".to_string(), t1);
    map.insert("x2".to_string(), t2);
    map.insert("x3".to_string(), t3);
    
    let result = taylor.substitute(&map)?;
    Ok(Some(result))
}

/// Find SD-meet terms for the algebra.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Vec<Term>))` - SD-meet terms if they exist
/// * `Ok(None)` - No SD-meet terms exist
/// * `Err(String)` - If there's an error during computation
pub fn sd_meet_terms<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Vec<Box<dyn Term>>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement SD-meet terms finding algorithm
    Err("SD-meet terms finding not yet implemented".to_string())
}

/// Helper function to find a path from g0 to g2 in subalg (for SD terms).
/// Similar to jonsson_level_path but with different edge connectivity.
fn sd_path(
    subalg: &mut [IntArray],
    g0: &IntArray,
    g2: &IntArray,
) -> Option<Vec<IntArray>> {
    use crate::util::int_array::IntArrayTrait;
    use std::collections::HashMap as StdHashMap;
    
    // Sort subalg lexicographically
    subalg.sort();
    
    // Build equivalence classes: classes01 groups by (first, second) coordinates, classes2 by third coordinate
    let mut classes01: StdHashMap<(i32, i32), Vec<IntArray>> = StdHashMap::new();
    let mut classes2: StdHashMap<i32, Vec<IntArray>> = StdHashMap::new();
    
    for ia in subalg.iter() {
        if let (Some(v0), Some(v1)) = (ia.get(0), ia.get(1)) {
            classes01.entry((v0, v1)).or_insert_with(Vec::new).push(ia.clone());
        }
        if let Some(v2) = ia.get(2) {
            classes2.entry(v2).or_insert_with(Vec::new).push(ia.clone());
        }
    }
    
    let mut levels: Vec<Vec<IntArray>> = Vec::new();
    let mut parent_map: StdHashMap<IntArray, IntArray> = StdHashMap::new();
    let mut visited: StdHashMap<IntArray, ()> = StdHashMap::new();
    let mut current_level = vec![g0.clone()];
    visited.insert(g0.clone(), ());
    levels.push(current_level.clone());
    
    let mut even = false;
    let mut first = true;
    
    loop {
        even = !even;
        let mut next_level = Vec::new();
        
        for ia in &current_level {
            let eqclass = if even {
                ia.get(0).and_then(|v0| {
                    ia.get(1).and_then(|v1| classes01.get(&(v0, v1)))
                })
            } else {
                ia.get(2).and_then(|v2| classes2.get(&v2))
            };
            
            if let Some(class) = eqclass {
                for ia2 in class {
                    if !visited.contains_key(ia2) {
                        parent_map.insert(ia2.clone(), ia.clone());
                        visited.insert(ia2.clone(), ());
                        next_level.push(ia2.clone());
                    }
                    if ia2 == g2 {
                        // Reconstruct path
                        let mut path = vec![g2.clone()];
                        let mut current = parent_map.get(g2).cloned();
                        while let Some(prev) = current {
                            path.push(prev.clone());
                            if prev == *g0 {
                                break;
                            }
                            current = parent_map.get(&prev).cloned();
                        }
                        path.reverse();
                        return Some(path);
                    }
                }
            }
        }
        
        if next_level.is_empty() {
            if !first {
                break;
            } else {
                first = false;
                continue;
            }
        }
        first = false;
        levels.push(next_level.clone());
        current_level = next_level;
    }
    
    None
}

/// Find SD terms for the algebra.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Vec<Term>))` - SD terms if they exist
/// * `Ok(None)` - No SD terms exist
/// * `Err(String)` - If there's an error during computation
pub fn sd_terms<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Vec<Box<dyn Term>>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // For idempotent algebras, check SD-meet first
    if alg.is_idempotent() {
        // Note: Java checks sdIdempotent which checks SD-join, not SD-meet
        // We'll skip this check for now and proceed directly
    }
    
    if alg.cardinality() == 1 {
        let mut ans: Vec<Box<dyn Term>> = Vec::new();
        ans.push(Box::new(VariableImp::x()) as Box<dyn Term>);
        ans.push(Box::new(VariableImp::z()) as Box<dyn Term>);
        return Ok(Some(ans));
    }
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    
    // Check if operations are empty
    if ops.is_empty() {
        return Err("Algebra has no operations".to_string());
    }
    
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Create generators: (x,x,y), (x,y,x), (y,x,x)
    let g0 = IntArray::from_array(vec![0, 0, 1])?;
    let g1 = IntArray::from_array(vec![0, 1, 0])?;
    let g2 = IntArray::from_array(vec![1, 0, 0])?;
    let gens = vec![g0.clone(), g1.clone(), g2.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::x()));
    term_map.insert(g1.clone(), Box::new(VariableImp::y()));
    term_map.insert(g2.clone(), Box::new(VariableImp::z()));
    
    // Create BigProductAlgebra (F(2)^3)
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_cubed = BigProductAlgebra::new_power_safe(f2_boxed, 3)?;
    
    let zero = IntArray::from_array(vec![0, 0, 0])?;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_cubed),
        gens,
        term_map,
    )?;
    
    let closure = closer.sg_close_power()?;
    let term_map_ref = closer.get_term_map().ok_or("Term map missing")?;
    
    // Check for majority term (zero)
    if closure.contains(&zero) {
        if let Some(term) = term_map_ref.get(&zero).map(|t| t.clone_box()) {
            let mut ans: Vec<Box<dyn Term>> = Vec::new();
            ans.push(Box::new(VariableImp::x()) as Box<dyn Term>);
            ans.push(term);
            ans.push(Box::new(VariableImp::z()) as Box<dyn Term>);
            return Ok(Some(ans));
        }
    }
    
    // Try to find Jonsson terms (congruence distributive case)
    use crate::util::int_array::IntArrayTrait;
    let mut middle_zero: Vec<IntArray> = closure.iter()
        .filter(|ia| (**ia).get(1) == Some(0))
        .cloned()
        .collect();
    
    let path = jonsson_level_path(&mut middle_zero, &g0, &g2, false);
    let path2 = jonsson_level_path(&mut middle_zero, &g0, &g2, true);
    
    if path.is_some() || path2.is_some() {
        // Found Jonsson terms - return them
        if let Some(p) = path2 {
            let mut ans = path2_term_list(&p, term_map_ref);
            ans.insert(0, ans[0].clone_box());
            return Ok(Some(ans));
        } else if let Some(p) = path {
            Ok(Some(path2_term_list(&p, term_map_ref)))
        } else {
            Ok(None)
        }
    } else {
        // Try SD path
        let mut sorted_subalg: Vec<IntArray> = closure.iter().cloned().collect();
        let path3 = sd_path(&mut sorted_subalg, &g0, &g2);
        if let Some(p) = path3 {
            Ok(Some(path2_term_list(&p, term_map_ref)))
        } else {
            Ok(None)
        }
    }
}

/// Find the Markovic-McKenzie-Siggers-Taylor term for the algebra.
///
/// A MMST term is a 4-ary term t(x,y,z,u) satisfying:
/// - t(y,x,x,x) = t(x,x,y,y)
/// - t(x,x,y,x) = t(x,y,x,x)
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Term))` - A MMST term if one exists
/// * `Ok(None)` - No MMST term exists
/// * `Err(String)` - If there's an error during computation
pub fn markovic_mckenzie_siggers_taylor_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if alg.cardinality() == 1 {
        return Ok(Some(Box::new(VariableImp::x()) as Box<dyn Term>));
    }
    
    let is_idempotent = alg.is_idempotent();
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    
    // Check if operations are empty
    if ops.is_empty() {
        return Err("Algebra has no operations".to_string());
    }
    
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Create generators based on idempotency
    let (g0, g1, g2, g3): (IntArray, IntArray, IntArray, IntArray);
    let power: usize;
    
    if is_idempotent {
        g0 = IntArray::from_array(vec![1, 0, 0, 0])?;
        g1 = IntArray::from_array(vec![0, 0, 0, 1])?;
        g2 = IntArray::from_array(vec![0, 1, 1, 0])?;
        g3 = IntArray::from_array(vec![0, 1, 0, 0])?;
        power = 4;
    } else {
        g0 = IntArray::from_array(vec![1, 0, 0, 0, 0])?;
        g1 = IntArray::from_array(vec![0, 0, 0, 1, 0])?;
        g2 = IntArray::from_array(vec![0, 1, 1, 0, 0])?;
        g3 = IntArray::from_array(vec![0, 1, 0, 0, 0])?;
        power = 5;
    }
    
    let gens = vec![g0.clone(), g1.clone(), g2.clone(), g3.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::new("x0")) as Box<dyn Term>);
    term_map.insert(g1.clone(), Box::new(VariableImp::new("x1")) as Box<dyn Term>);
    term_map.insert(g2.clone(), Box::new(VariableImp::new("x2")) as Box<dyn Term>);
    term_map.insert(g3.clone(), Box::new(VariableImp::new("x3")) as Box<dyn Term>);
    
    // Create BigProductAlgebra (F(2)^power)
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_power = BigProductAlgebra::new_power_safe(f2_boxed, power)?;
    
    // Use Closer for closure (note: blocks/values not yet implemented, so we check manually)
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_power),
        gens,
        term_map,
    )?;
    
    // Use sg_close_power for power algebras (matches Java's sgClosePower)
    let closure = closer.sg_close_power()?;
    let term_map_ref = closer.get_term_map().ok_or("Term map missing")?;
    
    use crate::util::int_array::IntArrayTrait;
    
    // Look for element satisfying MMST constraints:
    // For idempotent: ia.get(0) == ia.get(1) && ia.get(2) == ia.get(3)
    // For non-idempotent: same plus ia.get(4) == 0
    for ia in &closure {
        if let (Some(v0), Some(v1), Some(v2), Some(v3)) = (ia.get(0), ia.get(1), ia.get(2), ia.get(3)) {
            if v0 == v1 && v2 == v3 {
                if is_idempotent {
                    if let Some(term) = term_map_ref.get(ia).map(|t| t.clone_box()) {
                        return Ok(Some(term));
                    }
                } else {
                    if let Some(v4) = ia.get(4) {
                        if v4 == 0 {
                            if let Some(term) = term_map_ref.get(ia).map(|t| t.clone_box()) {
                                return Ok(Some(term));
                            }
                        }
                    }
                }
            }
        }
    }
    
    Ok(None)
}

/// Find a weak 3-edge term for the algebra.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Term))` - A weak 3-edge term if one exists
/// * `Ok(None)` - No weak 3-edge term exists
/// * `Err(String)` - If there's an error during computation
pub fn weak_3_edge_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement weak 3-edge term finding algorithm
    Err("Weak 3-edge term finding not yet implemented".to_string())
}

/// Find a witness for SD-meet failure in an idempotent algebra.
///
/// Uses Theorem 4.3 of Freese-Valeriote to test if the variety is congruence SD-meet.
/// Returns coordinates [x, y] witnessing the failure, or None if SD-meet holds.
///
/// # Arguments
/// * `alg` - The idempotent algebra to check
///
/// # Returns
/// * `Ok(Some([x, y]))` - Found witness for SD-meet failure
/// * `Ok(None)` - No failure found (SD-meet holds)
/// * `Err(String)` - If there's an error during computation
pub fn sd_meet_idempotent<T>(
    alg: &dyn SmallAlgebra<UniverseItem = T>,
) -> Result<Option<Vec<usize>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static,
{
    let n = alg.cardinality() as usize;
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        ops,
    );
    
    // Create BigProductAlgebra A^2
    let alg_boxed: Box<dyn SmallAlgebra<UniverseItem = i32>> = Box::new(i32_alg);
    let sq = BigProductAlgebra::new_power_safe(alg_boxed, 2)?;
    
    // Loop through all pairs (x, y) with x ≠ y
    for x in 0..n {
        for y in 0..n {
            if x == y {
                continue;
            }
            
            // Create generators:
            // a = (x, x)
            // b = (x, y)
            // c = (y, x)
            let a_arr = IntArray::from_array(vec![x as i32, x as i32])?;
            let b_arr = IntArray::from_array(vec![x as i32, y as i32])?;
            let c_arr = IntArray::from_array(vec![y as i32, x as i32])?;
            
            let gens = vec![a_arr.clone(), b_arr.clone(), c_arr.clone()];
            
            // Create SubProductAlgebra
            let mut sub = crate::alg::SubProductAlgebra::new_safe(
                "SDMeetSub".to_string(),
                sq.clone(),
                gens,
                false,
            )?;
            
            sub.make_operation_tables();
            
            // Get element indices
            let a_index = sub.element_index(&a_arr).ok_or_else(|| {
                format!("Element a = [{}, {}] not found in subalgebra", x, x)
            })?;
            let b_index = sub.element_index(&b_arr).ok_or_else(|| {
                format!("Element b = [{}, {}] not found in subalgebra", x, y)
            })?;
            let c_index = sub.element_index(&c_arr).ok_or_else(|| {
                format!("Element c = [{}, {}] not found in subalgebra", y, x)
            })?;
            
            // Create congruence lattice
            use crate::alg::SmallAlgebraWrapper;
            let alg_box = Box::new(sub.clone()) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
            let wrapper = Box::new(SmallAlgebraWrapper::<IntArray>::new(alg_box));
            let mut con_lat = crate::alg::conlat::CongruenceLattice::<IntArray>::new(wrapper);
            
            // Compute congruences:
            // alpha = Cg(a, c)
            let alpha = con_lat.cg(a_index, c_index);
            
            // beta = Cg(a, b)
            let beta = con_lat.cg(a_index, b_index);
            
            // gamma = Cg(b, c)
            let gamma = con_lat.cg(b_index, c_index);
            
            // Check if !((((alpha ∧ beta) ∨ gamma) ∧ alpha) ∨ beta).isRelated(a, c)
            // This is: !((alpha ∧ beta).join(gamma).meet(alpha).join(beta)).isRelated(a, c)
            let alpha_meet_beta = alpha.meet(&beta)?;
            let alpha_beta_join_gamma = alpha_meet_beta.join(&gamma)?;
            let join_meet_alpha = alpha_beta_join_gamma.meet(&alpha)?;
            let final_join = join_meet_alpha.join(&beta)?;
            
            if !final_join.is_related(a_index, c_index) {
                // Found a witness for SD-meet failure
                return Ok(Some(vec![x, y]));
            }
        }
    }
    
    Ok(None)
}

/// Test if an idempotent algebra is congruence distributive.
///
/// Uses the polynomial-time algorithm from Freese-Valeriote:
/// 1. Check for a Day quadruple (non-modularity witness)
/// 2. Check for SD-meet failure
/// Returns true only if both checks pass (no Day quadruple AND SD-meet holds).
///
/// # Arguments
/// * `alg` - The idempotent algebra to check
///
/// # Returns
/// * `Ok(true)` - The algebra is congruence distributive
/// * `Ok(false)` - The algebra is not congruence distributive
/// * `Err(String)` - If there's an error during computation
pub fn is_congruence_dist_idempotent<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<bool, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // First check for Day quadruple (non-modularity)
    match find_day_quadruple_in_square(alg) {
        Ok(Some(_)) => {
            // Day quadruple found = not modular = not distributive
            return Ok(false);
        }
        Err(e) => return Err(e),
        Ok(None) => {
            // No Day quadruple, continue to SD-meet check
        }
    }
    
    // Check for SD-meet failure
    match sd_meet_idempotent(alg) {
        Ok(Some(_)) => {
            // SD-meet failure found = not distributive
            Ok(false)
        }
        Ok(None) => {
            // No Day quadruple and SD-meet holds = distributive
            Ok(true)
        }
        Err(e) => Err(e),
    }
}

/// Find a Day quadruple in the square of the algebra.
///
/// Searches for a Day quadruple in all subalgebras of A^2.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some([x0, x1, y0, y1]))` - A Day quadruple found with these coordinates
/// * `Ok(None)` - No Day quadruple exists
/// * `Err(String)` - If there's an error during computation
pub fn find_day_quadruple_in_square<T>(
    alg: &dyn SmallAlgebra<UniverseItem = T>,
) -> Result<Option<Vec<usize>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static,
{
    let n = alg.cardinality() as usize;
    
    // Convert to i32 algebra
    // Note: We need to ensure operations work with i32 universe
    // Java uses the algebra directly without conversion, but Rust needs i32 for BigProductAlgebra
    let card = alg.cardinality();
    let ops = alg.operations();
    // Convert operations to use integer tables to ensure they work correctly
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create BigProductAlgebra A^2
    let alg_boxed: Box<dyn SmallAlgebra<UniverseItem = i32>> = Box::new(i32_alg);
    let sq = BigProductAlgebra::new_power_safe(alg_boxed, 2)?;
    
    // Loop through all combinations
    for x0 in 0..n {
        for x1 in 0..n {
            for y0 in 0..n {
                for y1 in (x1 + 1)..n {
                    // Create the four generators for this combination
                    let a_arr = IntArray::from_array(vec![x0 as i32, x1 as i32])?;
                    let b_arr = IntArray::from_array(vec![x0 as i32, y1 as i32])?;
                    let c_arr = IntArray::from_array(vec![y0 as i32, x1 as i32])?;
                    let d_arr = IntArray::from_array(vec![y0 as i32, y1 as i32])?;
                    
                    let gens = vec![a_arr.clone(), b_arr.clone(), c_arr.clone(), d_arr.clone()];
                    
                    // Create SubProductAlgebra
                    // Note: Java doesn't call makeOperationTables() before computing congruences
                    let mut sub = crate::alg::SubProductAlgebra::new_safe(
                        "SubSquare".to_string(),
                        sq.clone(),
                        gens,
                        false,
                    )?;
                    
                    // Get element indices and check for Day quadruple
                    let a_index = sub.element_index(&a_arr).ok_or_else(|| {
                        format!("Element a = [{}, {}] not found in subalgebra", x0, x1)
                    })?;
                    let b_index = sub.element_index(&b_arr).ok_or_else(|| {
                        format!("Element b = [{}, {}] not found in subalgebra", x0, y1)
                    })?;
                    let c_index = sub.element_index(&c_arr).ok_or_else(|| {
                        format!("Element c = [{}, {}] not found in subalgebra", y0, x1)
                    })?;
                    let d_index = sub.element_index(&d_arr).ok_or_else(|| {
                        format!("Element d = [{}, {}] not found in subalgebra", y0, y1)
                    })?;
                    
                    // Note: Java's SubProductAlgebra constructor doesn't call makeOperationTables(),
                    // but we may need it for proper congruence computation in Rust
                    // sub.make_operation_tables();
                    
                    // Use sub.con() to get the cached congruence lattice (matches Java pattern exactly)
                    // Java: alg.con().Cg(...) - con() returns a reference that can be used for Cg()
                    let con_lat = sub.con();
                    
                    // Compute the congruences (Java: alg.con().Cg(...))
                    // cgcd = Cg(c, d)
                    let cgcd = con_lat.cg(c_index, d_index);
                    
                    // cgab = Cg(a, b)
                    let cgab = con_lat.cg(a_index, b_index);
                    
                    // cgac = Cg(a, c)
                    let cgac = con_lat.cg(a_index, c_index);
                    
                    // cgbd = Cg(b, d)
                    let cgbd = con_lat.cg(b_index, d_index);
                    
                    // cgab_cd = Cg(a,b) ∨ Cg(c,d)  (Java: alg.con().Cg(a,b).join(cgcd))
                    let cgab_cd = cgab.join(&cgcd)?;
                    
                    // cgac_bd = Cg(a,c) ∨ Cg(b,d)  (Java: alg.con().Cg(a,c).join(alg.con().Cg(b,d)))
                    let cgac_bd = cgac.join(&cgbd)?;
                    
                    // Check Day quadruple condition: !cgcd.join(cgab_cd.meet(cgac_bd)).isRelated(a,b)
                    // Java: return !cgcd.join(cgab_cd.meet(cgac_bd)).isRelated(a,b);
                    let meet_result = cgab_cd.meet(&cgac_bd)?;
                    let join_result = cgcd.join(&meet_result)?;
                    
                    let is_related = join_result.is_related(a_index, b_index);
                    
                    if !is_related {
                        // Found a Day quadruple
                        return Ok(Some(vec![x0, x1, y0, y1]));
                    }
                }
            }
        }
    }
    
    Ok(None)
}

/// Test if an idempotent algebra is congruence modular.
///
/// Uses the polynomial-time algorithm from Freese-Valeriote that searches
/// for a Day quadruple in the square of the algebra.
///
/// # Arguments
/// * `alg` - The idempotent algebra to check
///
/// # Returns
/// * `Ok(true)` - The algebra is congruence modular
/// * `Ok(false)` - The algebra is not congruence modular
/// * `Err(String)` - If there's an error during computation
pub fn is_congruence_modular_idempotent<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<bool, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    match find_day_quadruple_in_square(alg) {
        Ok(Some(_)) => Ok(false),  // Day quadruple found = not CM
        Ok(None) => Ok(true),       // No Day quadruple = CM
        Err(e) => Err(e),
    }
}

/// Test if the variety generated by the algebra is congruence modular.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(true)` - The variety is congruence modular
/// * `Ok(false)` - The variety is not congruence modular
/// * `Err(String)` - If there's an error during computation
pub fn congruence_modular_variety<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<bool, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement variety congruence modularity test
    Err("Variety congruence modularity test not yet implemented".to_string())
}

/// Helper function to compute Jonsson level (auxiliary function).
fn jonsson_level_aux(
    middle_zero: &[IntArray],
    g0: &IntArray,
    g2: &IntArray,
) -> i32 {
    use crate::util::int_array::IntArrayTrait;
    use std::collections::HashMap as StdHashMap;
    use std::collections::HashSet as StdHashSet;
    
    let mut levels: Vec<Vec<IntArray>> = Vec::new();
    let mut visited: StdHashSet<IntArray> = StdHashSet::new();
    let mut current_level: Vec<(IntArray, Option<IntArray>)> = vec![(g0.clone(), None)];
    visited.insert(g0.clone());
    levels.push(vec![g0.clone()]);
    
    // Build equivalence classes
    let mut classes0: StdHashMap<i32, Vec<IntArray>> = StdHashMap::new();
    let mut classes2: StdHashMap<i32, Vec<IntArray>> = StdHashMap::new();
    
    for ia in middle_zero.iter() {
        if let Some(v0) = ia.get(0) {
            classes0.entry(v0).or_insert_with(Vec::new).push(ia.clone());
        }
        if let Some(v2) = ia.get(2) {
            classes2.entry(v2).or_insert_with(Vec::new).push(ia.clone());
        }
    }
    
    let mut even = false;
    
    loop {
        even = !even;
        let mut next_level_items: Vec<(IntArray, Option<IntArray>)> = Vec::new();
        let mut next_level: Vec<IntArray> = Vec::new();
        
        for (ia, _parent) in &current_level {
            let eqclass = if even {
                ia.get(0).and_then(|v0| classes0.get(&v0))
            } else {
                ia.get(2).and_then(|v2| classes2.get(&v2))
            };
            
            if let Some(class) = eqclass {
                for ia2 in class {
                    if ia2 == g2 {
                        return (levels.len()) as i32;
                    }
                    if !visited.contains(ia2) {
                        visited.insert(ia2.clone());
                        next_level_items.push((ia2.clone(), Some(ia.clone())));
                        next_level.push(ia2.clone());
                    }
                }
            }
        }
        
        if next_level.is_empty() {
            break;
        }
        levels.push(next_level.clone());
        current_level = next_level_items;
    }
    
    -1
}

/// Compute the Jonsson level of an algebra.
///
/// # Arguments
/// * `alg` - The algebra
///
/// # Returns
/// * `Ok(level)` - The Jonsson level (minimal number of Jonsson terms minus 1)
/// * `Err(String)` - If there's an error during computation
pub fn jonsson_level<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<i32, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if alg.cardinality() == 1 {
        return Ok(1);
    }
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    
    // Check if operations are empty
    if ops.is_empty() {
        return Err("Algebra has no operations".to_string());
    }
    
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Create generators: (x,x,y), (x,y,x), (y,x,x)
    let g0 = IntArray::from_array(vec![0, 0, 1])?;
    let g1 = IntArray::from_array(vec![0, 1, 0])?;
    let g2 = IntArray::from_array(vec![1, 0, 0])?;
    let gens = vec![g0.clone(), g1.clone(), g2.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::x()));
    term_map.insert(g1.clone(), Box::new(VariableImp::y()));
    term_map.insert(g2.clone(), Box::new(VariableImp::z()));
    
    // Create BigProductAlgebra (F(2)^3)
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_cubed = BigProductAlgebra::new_power_safe(f2_boxed, 3)?;
    
    // Use Closer for closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_cubed),
        gens,
        term_map,
    )?;
    
    let closure = closer.sg_close_power()?;
    
    let zero = IntArray::from_array(vec![0, 0, 0])?;
    if closure.contains(&zero) {
        // Found majority term - level is 2
        return Ok(2);
    }
    
    // Find middle zero elements (where second coordinate is 0)
    use crate::util::int_array::IntArrayTrait;
    let mut middle_zero: Vec<IntArray> = closure.iter()
        .filter(|ia| (**ia).get(1) == Some(0))
        .cloned()
        .collect();
    
    // Sort middle_zero
    middle_zero.sort_by(|a, b| {
        let size_a = a.universe_size();
        let size_b = b.universe_size();
        for i in 0..size_a.min(size_b) {
            if let (Some(va), Some(vb)) = (a.get(i), b.get(i)) {
                if va < vb {
                    return std::cmp::Ordering::Less;
                } else if va > vb {
                    return std::cmp::Ordering::Greater;
                }
            }
        }
        std::cmp::Ordering::Equal
    });
    
    Ok(jonsson_level_aux(&middle_zero, &g0, &g2))
}

/// Compute the local distributivity level for three elements.
///
/// # Arguments
/// * `a` - First element index
/// * `b` - Second element index
/// * `c` - Third element index
/// * `alg` - The algebra
///
/// # Returns
/// * `Ok(level)` - The local distributivity level
/// * `Err(String)` - If there's an error during computation
pub fn local_distributivity_level<T>(a: usize, b: usize, c: usize, alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<i32, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement local distributivity level computation
    Err("Local distributivity level computation not yet implemented".to_string())
}

/// Check if a, b, c, d form a Day quadruple in the algebra.
///
/// A Day quadruple exists if the congruences Cg(c,d), Cg(a,b)∨Cg(c,d), and Cg(a,c)∨Cg(b,d)
/// generate a nonmodular lattice.
///
/// This is a helper function that can be used with a congruence lattice.
/// For most purposes, use `find_day_quadruple_in_square` instead.
///
/// # Arguments
/// * `a`, `b`, `c`, `d` - Four element indices
/// * `con_lat` - The congruence lattice of the algebra (mutable for caching)
///
/// # Returns
/// * `Ok(true)` - A Day quadruple exists
/// * `Ok(false)` - No Day quadruple exists
/// * `Err(String)` - If there's an error during computation
pub fn day_quadruple(
    a: usize,
    b: usize,
    c: usize,
    d: usize,
    con_lat: &mut crate::alg::conlat::CongruenceLattice<IntArray>,
) -> Result<bool, String>
{
    // Compute the congruences:
    // cgcd = Cg(c, d)
    let cgcd = con_lat.cg(c, d);
    
    // cgab = Cg(a, b)
    let cgab = con_lat.cg(a, b);
    
    // cgac = Cg(a, c)
    let cgac = con_lat.cg(a, c);
    
    // cgbd = Cg(b, d)
    let cgbd = con_lat.cg(b, d);
    
    // cgab_cd = Cg(a,b) ∨ Cg(c,d)
    let cgab_cd = cgab.join(&cgcd)?;
    
    // cgac_bd = Cg(a,c) ∨ Cg(b,d)
    let cgac_bd = cgac.join(&cgbd)?;
    
    // Check if Cg(c,d) ∨ (Cg(a,b)∨Cg(c,d)) ∧ (Cg(a,c)∨Cg(b,d)) does NOT relate a and b
    // This means: !(cgcd ∨ (cgab_cd ∧ cgac_bd)).isRelated(a, b)
    let meet_result = cgab_cd.meet(&cgac_bd)?;
    let join_result = cgcd.join(&meet_result)?;
    
    // A Day quadruple exists if a and b are NOT related in join_result
    Ok(!join_result.is_related(a, b))
}

/// Test if the algebra admits a cyclic term of the given arity.
///
/// # Arguments
/// * `alg` - The algebra
/// * `arity` - The arity of the cyclic term
///
/// # Returns
/// * `Ok(true)` - A cyclic term exists
/// * `Ok(false)` - No cyclic term exists
/// * `Err(String)` - If there's an error during computation
pub fn cyclic_term_idempotent<T>(alg: &dyn SmallAlgebra<UniverseItem = T>, arity: usize) -> Result<bool, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement cyclic term test for idempotent algebras
    Err("Cyclic term test not yet implemented".to_string())
}

/// Helper function to create unit vectors for dimension n.
/// 
/// Creates n vectors where the i-th vector has 1 at position i and 0 elsewhere.
fn unit_vectors(n: usize) -> Result<Vec<IntArray>, String> {
    let mut ans = Vec::with_capacity(n);
    for i in 0..n {
        let mut arr = vec![0; n];
        arr[i] = 1;
        ans.push(IntArray::from_array(arr)?);
    }
    Ok(ans)
}

/// Find a binary term of alg that is a semilattice meet on {0,1} or None if there is none.
/// Used in testing primality.
fn semilat_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create BigProductAlgebra (A^4)
    let alg_boxed: Box<dyn SmallAlgebra<UniverseItem = i32>> = Box::new(i32_alg);
    let alg4 = BigProductAlgebra::new_power_safe(alg_boxed, 4)?;
    
    // Create generators: [0,0,1,1] and [0,1,0,1]
    let g0 = IntArray::from_array(vec![0, 0, 1, 1])?;
    let g1 = IntArray::from_array(vec![0, 1, 0, 1])?;
    let gens = vec![g0.clone(), g1.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::x()));
    term_map.insert(g1.clone(), Box::new(VariableImp::y()));
    
    // The element we're looking for: [0,0,0,1] (the meet operation)
    let meet = IntArray::from_array(vec![0, 0, 0, 1])?;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(alg4),
        gens,
        term_map,
    )?;
    closer.set_element_to_find(Some(meet.clone()));
    
    let _closure = closer.sg_close_power()?;
    
    // Check if meet was found
    if let Some(term_map) = closer.get_term_map() {
        if let Some(term) = term_map.get(&meet) {
            return Ok(Some(term.clone_box()));
        }
    }
    
    Ok(None)
}

/// Find the identity function on A in the subalgebra of A^n generated by the unit vectors.
/// Used in testing primality.
fn id_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    let n = alg.cardinality() as usize;
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create BigProductAlgebra (A^n)
    let alg_boxed: Box<dyn SmallAlgebra<UniverseItem = i32>> = Box::new(i32_alg);
    let prod = BigProductAlgebra::new_power_safe(alg_boxed, n)?;
    
    // Create unit vectors as generators
    let units = unit_vectors(n)?;
    let mut gens = Vec::with_capacity(n);
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    
    for (i, unit) in units.iter().enumerate() {
        gens.push(unit.clone());
        term_map.insert(unit.clone(), Box::new(VariableImp::new(&format!("x_{}", i))));
    }
    
    // The identity element: [0, 1, 2, ..., n-1]
    let id_arr: Vec<i32> = (0..n as i32).collect();
    let id = IntArray::from_array(id_arr)?;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(prod),
        gens,
        term_map,
    )?;
    closer.set_element_to_find(Some(id.clone()));
    
    let _closure = closer.sg_close_power()?;
    
    // Check if id was found
    if let Some(term_map) = closer.get_term_map() {
        if let Some(term) = term_map.get(&id) {
            return Ok(Some(term.clone_box()));
        }
    }
    
    Ok(None)
}

/// Find unary terms giving the n unit vectors in F(1).
/// Used in testing primality.
fn unit_terms<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Vec<Box<dyn Term>>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    let n = alg.cardinality() as usize;
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 1 generator (F(1))
    let mut f1 = FreeAlgebra::new_with_name_progress_safe(
        "F(1)".to_string(),
        Box::new(i32_alg),
        1,
        true, // make_universe
        false, // thin_gens
        false, // decompose
        None, // relations
        None, // report
    )?;
    
    use crate::alg::Algebra;
    f1.make_operation_tables();
    
    // Get unit vectors
    let units = unit_vectors(n)?;
    
    // Get product algebra, generators, and term map from FreeAlgebra
    let inner = f1.get_inner();
    let product_algebra_ref = inner.get_product_algebra();
    let product_algebra = Arc::new(product_algebra_ref.clone());
    let generators = inner.generators().to_vec();
    let term_map_opt = inner.get_term_map();
    
    let term_map: HashMap<IntArray, Box<dyn Term>> = if let Some(tm) = term_map_opt {
        tm.iter().map(|(k, v)| (k.clone(), v.clone_box())).collect()
    } else {
        // Create term map from generators if not available
        let mut tm = HashMap::new();
        for (i, gen) in generators.iter().enumerate() {
            tm.insert(gen.clone(), Box::new(VariableImp::new(&format!("x_{}", i))) as Box<dyn Term>);
        }
        tm
    };
    
    // Use Closer with multiple element finding
    let mut closer = Closer::new_with_term_map_safe(
        product_algebra,
        generators.clone(),
        term_map,
    )?;
    closer.set_elements_to_find(units.clone(), &generators);
    
    let _closure = closer.sg_close_power()?;
    
    // Check if all elements were found
    if !closer.all_elements_found() {
        return Ok(None);
    }
    
    // Extract terms for each unit vector
    let mut ans = Vec::with_capacity(n);
    if let Some(tm) = closer.get_term_map() {
        for unit in &units {
            if let Some(term) = tm.get(unit) {
                ans.push(term.clone_box());
            } else {
                return Ok(None);
            }
        }
    } else {
        return Ok(None);
    }
    
    Ok(Some(ans))
}

/// Find primality terms for an algebra.
///
/// This gives unary terms evaluating to the characteristic functions of the one element
/// subsets of alg; a term which applied to these unit vectors gives the identity function;
/// and a binary term giving a semilattice operation on {0, 1}. It is based on
/// D. M. Clark, B. A. Davey, J. G. Pitkethly and D. L. Rifqui, 
/// "Flat unars: the primal, the semi-primal, and the dualizable",
/// Algebra Universalis, 63(2010), 303-329.
///
/// # Arguments
/// * `alg` - The algebra to check
///
/// # Returns
/// * `Ok(Some(Vec<Term>))` - List of primality terms if found:
///   - First term: semilattice meet term
///   - Second term: identity term
///   - Remaining terms: unit vector terms
/// * `Ok(None)` - No primality terms exist (algebra is not primal)
/// * `Err(String)` - If there's an error during computation
pub fn primality_terms<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Option<Vec<Box<dyn Term>>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // Find semilattice term
    let semilat_term = semilat_term(alg)?;
    if semilat_term.is_none() {
        return Ok(None);
    }
    let semilat_term = semilat_term.unwrap();
    
    // Find identity term
    let id_term = id_term(alg)?;
    if id_term.is_none() {
        return Ok(None);
    }
    let id_term = id_term.unwrap();
    
    // Find unit terms
    let unit_terms = unit_terms(alg)?;
    if unit_terms.is_none() {
        return Ok(None);
    }
    let unit_terms = unit_terms.unwrap();
    
    // Combine all terms
    let mut ans = Vec::with_capacity(alg.cardinality() as usize + 2);
    ans.push(semilat_term);
    ans.push(id_term);
    ans.extend(unit_terms);
    
    Ok(Some(ans))
}

/// Find a k-edge term for the algebra.
///
/// A k-edge term is a term of arity k+1 that satisfies certain edge conditions.
/// This is used to test for certain Mal'cev conditions related to edge terms.
///
/// # Arguments
/// * `alg` - The algebra to check
/// * `k` - The parameter k (edge term will have arity k+1)
///
/// # Returns
/// * `Ok(Some(Term))` - A k-edge term if one exists
/// * `Ok(None)` - No k-edge term exists
/// * `Err(String)` - If there's an error during computation
pub fn fixed_k_edge_term<T>(alg: &dyn SmallAlgebra<UniverseItem = T>, k: usize) -> Result<Option<Box<dyn Term>>, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    let arity = k + 1;
    
    if alg.cardinality() == 1 {
        return Ok(Some(Box::new(VariableImp::new("x0"))));
    }
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    
    // Check if operations are empty
    if ops.is_empty() {
        return Err("Algebra has no operations".to_string());
    }
    
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2)?;
    use crate::alg::Algebra;
    f2.make_operation_tables();
    
    // Create generators
    let mut gens = Vec::with_capacity(arity);
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    
    for i in 0..arity {
        let mut arr = vec![0; k];
        if i == 0 {
            arr[0] = 1;
            if k > 1 {
                arr[1] = 1;
            }
        } else {
            if i - 1 < k {
                arr[i - 1] = 1;
            }
        }
        let ia = IntArray::from_array(arr)?;
        gens.push(ia.clone());
        
        // Map to appropriate variable
        let var: Box<dyn Term> = if arity > 3 {
            Box::new(VariableImp::new(&format!("x{}", i)))
        } else {
            match i {
                0 => Box::new(VariableImp::x()),
                1 => Box::new(VariableImp::y()),
                _ => Box::new(VariableImp::z()),
            }
        };
        term_map.insert(ia, var);
    }
    
    // Create BigProductAlgebra (F(2)^k)
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_power = BigProductAlgebra::new_power_safe(f2_boxed, k)?;
    
    // The element we're looking for: zero vector (x,x,...,x) = [0,0,...,0]
    let zero = IntArray::from_array(vec![0; k])?;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_power),
        gens,
        term_map,
    )?;
    closer.set_element_to_find(Some(zero.clone()));
    
    let closure = closer.sg_close_power()?;
    if closure.contains(&zero) {
        if let Some(term) = closer.get_term_map().and_then(|tm| tm.get(&zero).map(|t| t.clone_box())) {
            return Ok(Some(term));
        }
    }
    
    Ok(None)
}

/// Test if an algebra has a quasi weak near unanimity (QWNU) term of the given arity.
///
/// This uses Alexandr Kazda's local to global test for quasi weak near unanimity operations.
/// See the paper A. Kazda "Deciding the existence of quasi weak near unanimity terms
/// in finite algebras", 2020.
///
/// # Arguments
/// * `alg` - The algebra to test
/// * `arity` - The arity of the QWNU term (must be at least 2)
///
/// # Returns
/// * `Ok(true)` - The algebra has a QWNU term of the given arity
/// * `Ok(false)` - The algebra does not have a QWNU term
/// * `Err(String)` - If there's an error during computation
pub fn fixed_k_qwnu<T>(alg: &dyn SmallAlgebra<UniverseItem = T>, arity: usize) -> Result<bool, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    if arity < 2 {
        return Err("arity must be at least 2".to_string());
    }
    
    // Convert to i32 algebra
    let card = alg.cardinality();
    let ops = alg.operations();
    
    // Check if operations are empty
    if ops.is_empty() {
        return Err("Algebra has no operations".to_string());
    }
    
    let int_ops = crate::alg::op::ops::make_int_operations(ops)?;
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        int_ops,
    );
    
    // Create BigProductAlgebra (A^arity)
    let alg_boxed: Box<dyn SmallAlgebra<UniverseItem = i32>> = Box::new(i32_alg);
    let prod = BigProductAlgebra::new_power_safe(alg_boxed, arity)?;
    
    let size = card as usize;
    
    // For each pair (a, b) with a != b
    for a in 0..size {
        // Create generating matrix filled with a's (will be reset for each b)
        let mut generating_matrix = vec![vec![a as i32; arity]; arity];
        
        for b in 0..size {
            if a == b {
                continue;
            }
            
            // Reset generating matrix to all a's (since we modify it below)
            for i in 0..arity {
                for j in 0..arity {
                    generating_matrix[i][j] = a as i32;
                }
            }
            
            // Set diagonal of generating matrix to b
            for i in 0..arity {
                generating_matrix[i][i] = b as i32;
            }
            
            // Create generators from generating matrix rows
            let mut gens = Vec::with_capacity(arity);
            for i in 0..arity {
                let arr = IntArray::from_array(generating_matrix[i].clone())?;
                gens.push(arr);
            }
            
            // Use Closer for closure computation
            let mut closer = Closer::new_safe(
                Arc::new(prod.clone()),
                gens,
            )?;
            
            let closure = closer.sg_close_power()?;
            
            // Look for an element of the form (q,q,...,q) in the closure
            use crate::util::int_array::IntArrayTrait;
            let mut found = false;
            for elem in &closure {
                if elem.is_constant() {
                    found = true;
                    break;
                }
            }
            
            if !found {
                // No diagonal element found - no QWNU term exists
                return Ok(false);
            }
        }
    }
    
    // All pairs passed - QWNU term exists
    Ok(true)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::BasicSmallAlgebra;
    use crate::io::AlgebraReader;
    use std::path::Path;
    use std::collections::HashSet;

    /// Helper to load an algebra from a test file (skip if not found)
    fn load_test_algebra(name: &str) -> Option<BasicSmallAlgebra<i32>> {
        let path_str = format!("resources/algebras/{}.ua", name);
        let path = Path::new(&path_str);
        if !path.exists() {
            return None;
        }
        
        let reader = AlgebraReader::new_from_path(&path_str).ok()?;
        reader.read_algebra_file().ok()
    }

    #[test]
    fn test_malcev_term_with_trivial_algebra() {
        // Test with cardinality 1 algebra (should return x)
        let alg = BasicSmallAlgebra::new(
            "TestAlgebra".to_string(),
            HashSet::from([0]),
            Vec::new()
        );
        
        let result = malcev_term(&alg);
        assert!(result.is_ok());
        if let Ok(Some(term)) = result {
            // Should be variable x
            assert!(term.isa_variable());
        }
    }

    #[test]
    fn test_malcev_term_with_cyclic2() {
        // Test with cyclic2 algebra
        if let Some(alg) = load_test_algebra("cyclic2") {
            let result = malcev_term(&alg);
            // Should either find a term or return None (not an error)
            assert!(result.is_ok(), "malcev_term should not error on cyclic2");
            // cyclic2 (2-element cyclic group) should have a Malcev term
            if let Ok(Some(term)) = result {
                println!("Found Malcev term for cyclic2: {}", term);
            }
        } else {
            println!("Skipping test - cyclic2.ua not found");
        }
    }

    #[test]
    fn test_malcev_term_with_cyclic3() {
        // Test with cyclic3 algebra
        if let Some(alg) = load_test_algebra("cyclic3") {
            let result = malcev_term(&alg);
            assert!(result.is_ok(), "malcev_term should not error on cyclic3");
            // cyclic3 should have a Malcev term (all groups do)
            if let Ok(Some(term)) = result {
                println!("Found Malcev term for cyclic3: {}", term);
            }
        } else {
            println!("Skipping test - cyclic3.ua not found");
        }
    }

    #[test]
    fn test_nu_term_arity_validation() {
        let alg = BasicSmallAlgebra::new(
            "TestAlgebra".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        );
        
        // Should reject arity < 3
        assert!(nu_term(&alg, 2).is_err());
        assert!(nu_term(&alg, 1).is_err());
    }

    #[test]
    fn test_nu_term_with_trivial_algebra() {
        // Test with cardinality 1 algebra
        let alg = BasicSmallAlgebra::new(
            "TestAlgebra".to_string(),
            HashSet::from([0]),
            Vec::new()
        );
        
        let result = nu_term(&alg, 3);
        assert!(result.is_ok());
        if let Ok(Some(term)) = result {
            assert!(term.isa_variable());
        }
    }

    #[test]
    fn test_nu_term_with_cyclic2() {
        // Test NU term finding with cyclic2
        if let Some(alg) = load_test_algebra("cyclic2") {
            let result = nu_term(&alg, 3);
            assert!(result.is_ok(), "nu_term should not error on cyclic2");
            // Result can be Some or None depending on whether NU term exists
            if let Ok(Some(term)) = result {
                println!("Found NU term for cyclic2: {}", term);
            } else {
                println!("No NU term found for cyclic2 (this is valid)");
            }
        } else {
            println!("Skipping test - cyclic2.ua not found");
        }
    }

    #[test]
    fn test_nu_term_with_cyclic3() {
        // Test NU term finding with cyclic3
        if let Some(alg) = load_test_algebra("cyclic3") {
            let result = nu_term(&alg, 3);
            assert!(result.is_ok(), "nu_term should not error on cyclic3");
            if let Ok(Some(term)) = result {
                println!("Found NU term for cyclic3: {}", term);
            }
        } else {
            println!("Skipping test - cyclic3.ua not found");
        }
    }

    #[test]
    fn test_majority_term_with_trivial_algebra() {
        // Test with cardinality 1 algebra (should return x)
        let alg = BasicSmallAlgebra::new(
            "TestAlgebra".to_string(),
            HashSet::from([0]),
            Vec::new()
        );
        
        let result = majority_term(&alg);
        assert!(result.is_ok());
        if let Ok(Some(term)) = result {
            assert!(term.isa_variable());
        }
    }

    #[test]
    fn test_majority_term_with_cyclic3() {
        // Test majority term finding with cyclic3
        if let Some(alg) = load_test_algebra("cyclic3") {
            let result = majority_term(&alg);
            assert!(result.is_ok(), "majority_term should not error on cyclic3");
            if let Ok(Some(term)) = result {
                println!("Found majority term for cyclic3: {}", term);
            } else {
                println!("No majority term found for cyclic3 (this is valid)");
            }
        } else {
            println!("Skipping test - cyclic3.ua not found");
        }
    }

    #[test]
    fn test_minority_term_with_trivial_algebra() {
        // Test with cardinality 1 algebra (should return x)
        let alg = BasicSmallAlgebra::new(
            "TestAlgebra".to_string(),
            HashSet::from([0]),
            Vec::new()
        );
        
        let result = minority_term(&alg);
        assert!(result.is_ok());
        if let Ok(Some(term)) = result {
            assert!(term.isa_variable());
        }
    }

    #[test]
    fn test_minority_term_with_cyclic3() {
        // Test minority term finding with cyclic3
        if let Some(alg) = load_test_algebra("cyclic3") {
            let result = minority_term(&alg);
            assert!(result.is_ok(), "minority_term should not error on cyclic3");
            if let Ok(Some(term)) = result {
                println!("Found minority term for cyclic3: {}", term);
            } else {
                println!("No minority term found for cyclic3 (this is valid)");
            }
        } else {
            println!("Skipping test - cyclic3.ua not found");
        }
    }

    #[test]
    fn test_pixley_term_with_trivial_algebra() {
        // Test with cardinality 1 algebra (should return x)
        let alg = BasicSmallAlgebra::new(
            "TestAlgebra".to_string(),
            HashSet::from([0]),
            Vec::new()
        );
        
        let result = pixley_term(&alg);
        assert!(result.is_ok());
        if let Ok(Some(term)) = result {
            assert!(term.isa_variable());
        }
    }

    #[test]
    fn test_pixley_term_with_cyclic3() {
        // Test Pixley term finding with cyclic3
        if let Some(alg) = load_test_algebra("cyclic3") {
            let result = pixley_term(&alg);
            assert!(result.is_ok(), "pixley_term should not error on cyclic3");
            if let Ok(Some(term)) = result {
                println!("Found Pixley term for cyclic3: {}", term);
            } else {
                println!("No Pixley term found for cyclic3 (this is valid)");
            }
        } else {
            println!("Skipping test - cyclic3.ua not found");
        }
    }

    #[test]
    fn test_is_congruence_modular_idempotent_with_trivial_algebra() {
        // Test with cardinality 1 algebra (should be CM)
        let alg = BasicSmallAlgebra::new(
            "TestAlgebra".to_string(),
            HashSet::from([0]),
            Vec::new()
        );
        
        let result = is_congruence_modular_idempotent(&alg);
        assert!(result.is_ok(), "is_congruence_modular_idempotent should not error");
        if let Ok(is_cm) = result {
            // Trivial algebra should be CM
            assert!(is_cm, "Trivial algebra should be congruence modular");
        }
    }

    #[test]
    fn test_find_day_quadruple_in_square_with_trivial_algebra() {
        // Test with cardinality 1 algebra (should not find Day quadruple)
        let alg = BasicSmallAlgebra::new(
            "TestAlgebra".to_string(),
            HashSet::from([0]),
            Vec::new()
        );
        
        let result = find_day_quadruple_in_square(&alg);
        assert!(result.is_ok(), "find_day_quadruple_in_square should not error");
        if let Ok(quad) = result {
            // Trivial algebra should not have a Day quadruple
            assert!(quad.is_none(), "Trivial algebra should not have a Day quadruple");
        }
    }

    #[test]
    fn test_sd_meet_idempotent_with_trivial_algebra() {
        // Test with cardinality 1 algebra (should not find SD-meet failure)
        let alg = BasicSmallAlgebra::new(
            "TestAlgebra".to_string(),
            HashSet::from([0]),
            Vec::new()
        );
        
        let result = sd_meet_idempotent(&alg);
        assert!(result.is_ok(), "sd_meet_idempotent should not error");
        if let Ok(witness) = result {
            // Trivial algebra should not have SD-meet failure
            assert!(witness.is_none(), "Trivial algebra should not have SD-meet failure");
        }
    }

    #[test]
    fn test_is_congruence_dist_idempotent_with_trivial_algebra() {
        // Test with cardinality 1 algebra (should be CD)
        let alg = BasicSmallAlgebra::new(
            "TestAlgebra".to_string(),
            HashSet::from([0]),
            Vec::new()
        );
        
        let result = is_congruence_dist_idempotent(&alg);
        assert!(result.is_ok(), "is_congruence_dist_idempotent should not error");
        if let Ok(is_cd) = result {
            // Trivial algebra should be congruence distributive
            assert!(is_cd, "Trivial algebra should be congruence distributive");
        }
    }
}

