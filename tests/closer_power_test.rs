/*!
 * Test for specialized power algebra closure computation.
 * 
 * This test verifies that sg_close_power_impl correctly finds elements
 * like [0,0,0] in power algebras, matching Java's sgClosePower behavior.
 */

use uacalc::alg::{Closer, BigProductAlgebra, FreeAlgebra, Algebra, SmallAlgebra};
use uacalc::util::int_array::{IntArray, IntArrayTrait};
use uacalc::terms::{Term, VariableImp};
use uacalc::io::algebra_io::read_algebra_file;
use std::collections::HashMap;
use std::sync::Arc;
use std::path::Path;

#[test]
fn test_power_algebra_finds_000() {
    // Load ba2.ua algebra
    let alg_file = Path::new("resources/algebras/ba2.ua");
    if !alg_file.exists() {
        eprintln!("Skipping test: {} not found", alg_file.display());
        return;
    }
    
    let base_alg = read_algebra_file(alg_file).expect("Failed to load ba2.ua");
    
    // Convert to BasicSmallAlgebra if needed, or use make_int_operations
    use uacalc::alg::op::ops::make_int_operations;
    use uacalc::alg::BasicSmallAlgebra;
    use std::collections::HashSet;
    
    let card = base_alg.cardinality();
    let ops = base_alg.operations();
    let int_ops = make_int_operations(ops).expect("Failed to create int operations");
    let universe: HashSet<i32> = (0..card).collect();
    let i32_alg = BasicSmallAlgebra::new(
        base_alg.name().to_string(),
        universe,
        int_ops,
    );
    
    // Create free algebra with 2 generators (F(2))
    let mut f2 = FreeAlgebra::new_safe(Box::new(i32_alg), 2).expect("Failed to create FreeAlgebra");
    f2.make_operation_tables();
    
    // Create power algebra F(2)^3
    let f2_boxed: Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = IntArray>>;
    let f2_cubed = BigProductAlgebra::new_power_safe(f2_boxed, 3).unwrap();
    
    // Create generators: (x,x,y), (x,y,x), (y,x,x)
    let g0 = IntArray::from_array(vec![0, 0, 1]).unwrap();  // (x,x,y)
    let g1 = IntArray::from_array(vec![0, 1, 0]).unwrap();  // (x,y,x)
    let g2 = IntArray::from_array(vec![1, 0, 0]).unwrap();  // (y,x,x)
    let gens = vec![g0.clone(), g1.clone(), g2.clone()];
    
    // Create term map
    let mut term_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    term_map.insert(g0.clone(), Box::new(VariableImp::x()));
    term_map.insert(g1.clone(), Box::new(VariableImp::y()));
    term_map.insert(g2.clone(), Box::new(VariableImp::z()));
    
    // The element we're looking for: (x,x,x) = [0,0,0]
    let xxx = IntArray::from_array(vec![0, 0, 0]).unwrap();
    
    // Use Closer with specialized power algebra path
    let mut closer = Closer::new_with_term_map_safe(
        Arc::new(f2_cubed),
        gens,
        term_map,
    ).unwrap();
    closer.set_element_to_find(Some(xxx.clone()));
    
    let closure = closer.sg_close().unwrap();
    
    // Verify [0,0,0] is in the closure
    assert!(closure.contains(&xxx), "Expected [0,0,0] to be found in closure, but it wasn't. Closure size: {}, elements: {:?}", 
            closure.len(), 
            closure.iter().take(10).map(|e| e.as_slice().to_vec()).collect::<Vec<_>>());
    
    // Verify we can get the term for [0,0,0]
    let term_map_ref = closer.get_term_map().unwrap();
    assert!(term_map_ref.contains_key(&xxx), "Expected term map to contain [0,0,0]");
}

