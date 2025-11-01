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
fn convert_to_i32_algebra<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<Box<dyn SmallAlgebra<UniverseItem = i32>>, String>
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
    let universe_set: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        alg.name().to_string(),
        universe_set,
        ops,
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
    
    let closure = closer.sg_close()?;
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
    
    // The element we're looking for: (x,x,x) = [0,0,0]
    let xxx = IntArray::from_array(vec![0, 0, 0])?;
    
    // Use Closer for term tracking during closure
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_cubed),
        gens,
        term_map,
    )?;
    closer.set_element_to_find(Some(xxx.clone()));
    
    let closure = closer.sg_close()?;
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
    
    let closure = closer.sg_close()?;
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
    
    let closure = closer.sg_close()?;
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
    
    let closure = closer.sg_close()?;
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
    
    let closure = closer.sg_close()?;
    
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
    // TODO: Implement Jonsson terms finding algorithm
    Err("Jonsson terms finding not yet implemented".to_string())
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
    // TODO: Implement join term finding algorithm
    Err("Join term finding not yet implemented".to_string())
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
    // TODO: Implement SD terms finding algorithm
    Err("SD terms finding not yet implemented".to_string())
}

/// Find the Markovic-McKenzie-Siggers-Taylor term for the algebra.
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
    // TODO: Implement MMST term finding algorithm
    Err("Markovic-McKenzie-Siggers-Taylor term finding not yet implemented".to_string())
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
                    
                    // Debug: Check closure size before creating subalgebra
                    let closure_before = sq.sg_close(gens.clone())?;
                    eprintln!("DEBUG: Closure size for ({},{},{},{}) = {}", x0, x1, y0, y1, closure_before.len());
                    
                    // Create SubProductAlgebra
                    // Note: Java doesn't call makeOperationTables() before computing congruences
                    let mut sub = crate::alg::SubProductAlgebra::new_safe(
                        "SubSquare".to_string(),
                        sq.clone(),
                        gens,
                        false,
                    )?;
                    
                    eprintln!("DEBUG: SubProductAlgebra size after creation = {}", sub.cardinality());
                    
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
                    // Debug output (remove after fixing)
                    eprintln!("DEBUG: x0={}, x1={}, y0={}, y1={}, a_idx={}, b_idx={}, c_idx={}, d_idx={}, is_related={}, sub_size={}", 
                             x0, x1, y0, y1, a_index, b_index, c_index, d_index, is_related, sub.cardinality());
                    
                    if !is_related {
                        // Found a Day quadruple
                        eprintln!("DEBUG: Found Day quadruple at ({},{},{},{})", x0, x1, y0, y1);
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

/// Compute the Jonsson level of an algebra.
///
/// # Arguments
/// * `alg` - The algebra
///
/// # Returns
/// * `Ok(level)` - The Jonsson level
/// * `Err(String)` - If there's an error during computation
pub fn jonsson_level<T>(alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<i32, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement Jonsson level computation
    Err("Jonsson level computation not yet implemented".to_string())
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::{BasicSmallAlgebra, Algebra};
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

