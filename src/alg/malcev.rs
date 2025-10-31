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
    // TODO: Implement weak majority term finding algorithm
    Err("Weak majority term finding not yet implemented".to_string())
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

/// Test if an idempotent algebra is congruence distributive.
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
    // TODO: Implement congruence distributivity test for idempotent algebras
    Err("Congruence distributivity test not yet implemented".to_string())
}

/// Test if an idempotent algebra is congruence modular.
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
    // TODO: Implement congruence modularity test for idempotent algebras
    Err("Congruence modularity test not yet implemented".to_string())
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

/// Test if a Day quadruple exists in the square of the algebra.
///
/// # Arguments
/// * `a`, `b`, `c`, `d` - Four element indices
/// * `alg` - The algebra
///
/// # Returns
/// * `Ok(true)` - A Day quadruple exists
/// * `Ok(false)` - No Day quadruple exists
/// * `Err(String)` - If there's an error during computation
pub fn day_quadruple<T>(a: usize, b: usize, c: usize, d: usize, alg: &dyn SmallAlgebra<UniverseItem = T>) -> Result<bool, String>
where
    T: Clone + std::fmt::Debug + std::fmt::Display + std::hash::Hash + Eq + Send + Sync + 'static
{
    // TODO: Implement Day quadruple test
    Err("Day quadruple test not yet implemented".to_string())
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
}

