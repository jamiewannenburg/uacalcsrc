/*!
 * Java comparison tests for Closer implementation.
 * 
 * These tests verify that Rust Closer implementation produces the same results
 * as the Java implementation for power algebras and free algebras.
 */

use uacalc::alg::{Closer, BigProductAlgebra, FreeAlgebra, Algebra, SmallAlgebra};
use uacalc::alg::conlat::partition::Partition;
use uacalc::util::int_array::{IntArray, IntArrayTrait};
use uacalc::io::algebra_io::read_algebra_file;
use std::collections::{HashSet, HashMap};
use std::sync::Arc;
use std::path::Path;
use serde_json::json;

use uacalc::common::*;
use uacalc::compare_with_java;

/// Helper function to create ba2 algebra
fn create_ba2() -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
    let alg_file = Path::new("resources/algebras/ba2.ua");
    if !alg_file.exists() {
        panic!("ba2.ua not found at {}", alg_file.display());
    }
    
    let base_alg = read_algebra_file(alg_file).expect("Failed to load ba2.ua");
    
    use uacalc::alg::op::ops::make_int_operations;
    use uacalc::alg::BasicAlgebra;
    use uacalc::alg::Algebra;
    
    let card = base_alg.cardinality();
    let ops = base_alg.operations();
    let int_ops = make_int_operations(ops).expect("Failed to create int operations");
    let universe: HashSet<i32> = (0..card).collect();
    
    let mut alg = BasicAlgebra::new(
        base_alg.name().to_string(),
        universe,
        int_ops,
    );
    // Initialize similarity type
    alg.update_similarity_type();
    
    Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>
}

/// Helper function to create F(n) - free algebra with n generators over ba2
fn create_f_n(n: i32) -> FreeAlgebra {
    let ba2 = create_ba2();
    let mut f_n = FreeAlgebra::new_safe(ba2, n).expect(&format!("Failed to create F({})", n));
    f_n.make_operation_tables();
    f_n
}

#[test]
fn test_closer_ba2_power2_java_comparison() {
    let config = TestConfig::default();
    
    let ba2 = create_ba2();
    let ba2_power2 = BigProductAlgebra::<i32>::new_power_safe(ba2, 2).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![0, 1]).unwrap();
    let gens = vec![g0, g1];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_ba2_power", "--power", "2", "--generators", "0,0;0,1"],
        || {
            let mut closer = Closer::new_safe(Arc::new(ba2_power2), gens.clone()).unwrap();
            let closure = closer.sg_close().unwrap();
            
            json!({
                "command": "sg_close_ba2_power",
                "power": 2,
                "base_size": 2,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "status": "success"
            })
        }
    );
}

#[test]
fn test_closer_ba2_power3_java_comparison() {
    let config = TestConfig::default();
    
    let ba2 = create_ba2();
    let ba2_power3 = BigProductAlgebra::<i32>::new_power_safe(ba2, 3).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0, 1]).unwrap();
    let g1 = IntArray::from_array(vec![1, 1, 0]).unwrap();
    let gens = vec![g0, g1];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_ba2_power", "--power", "3", "--generators", "0,0,1;1,1,0"],
        || {
            let mut closer = Closer::new_safe(Arc::new(ba2_power3), gens.clone()).unwrap();
            let closure = closer.sg_close().unwrap();
            
            json!({
                "command": "sg_close_ba2_power",
                "power": 3,
                "base_size": 2,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "status": "success"
            })
        }
    );
}

#[test]
fn test_closer_ba2_power3_single_generator() {
    let config = TestConfig::default();
    
    let ba2 = create_ba2();
    let ba2_power3 = BigProductAlgebra::<i32>::new_power_safe(ba2, 3).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0, 0]).unwrap();
    let gens = vec![g0];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_ba2_power", "--power", "3", "--generators", "0,0,0"],
        || {
            let mut closer = Closer::new_safe(Arc::new(ba2_power3), gens.clone()).unwrap();
            let closure = closer.sg_close().unwrap();
            
            json!({
                "command": "sg_close_ba2_power",
                "power": 3,
                "base_size": 2,
                "generators_count": 1,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "status": "success"
            })
        }
    );
}

#[test]
fn test_closer_f1_power2_java_comparison() {
    let config = TestConfig::default();
    
    let f1 = create_f_n(1);
    let f1_cardinality = f1.cardinality();
    let f1_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f1) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f1_power2 = BigProductAlgebra::new_power_safe(f1_boxed, 2).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![0, 1]).unwrap();
    let gens = vec![g0, g1];
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_free_algebra", "--num_gens", "1", "--power", "2", "--generators", "0,0;0,1"],
        || {
            let mut closer = Closer::new_safe(Arc::new(f1_power2), gens.clone()).unwrap();
            let closure = closer.sg_close().unwrap();
            
            json!({
                "command": "sg_close_free_algebra",
                "num_gens": 1,
                "power": 2,
                "base_size": f1_cardinality,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "status": "success"
            })
        }
    );
}

#[test]
fn test_closer_f1_power3_java_comparison() {
    let config = TestConfig::default();
    
    let f1 = create_f_n(1);
    let f1_cardinality = f1.cardinality();
    let f1_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f1) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f1_power3 = BigProductAlgebra::new_power_safe(f1_boxed, 3).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0, 1]).unwrap();
    let g1 = IntArray::from_array(vec![1, 1, 0]).unwrap();
    let gens = vec![g0, g1];
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_free_algebra", "--num_gens", "1", "--power", "3", "--generators", "0,0,1;1,1,0"],
        || {
            let mut closer = Closer::new_safe(Arc::new(f1_power3), gens.clone()).unwrap();
            let closure = closer.sg_close().unwrap();
            
            json!({
                "command": "sg_close_free_algebra",
                "num_gens": 1,
                "power": 3,
                "base_size": f1_cardinality,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "status": "success"
            })
        }
    );
}

#[test]
fn test_closer_f2_power2_java_comparison() {
    let config = TestConfig::default();
    
    let f2 = create_f_n(2);
    let f2_cardinality = f2.cardinality();
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_power2 = BigProductAlgebra::new_power_safe(f2_boxed, 2).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![0, 1]).unwrap();
    let gens = vec![g0, g1];
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_free_algebra", "--num_gens", "2", "--power", "2", "--generators", "0,0;0,1"],
        || {
            let mut closer = Closer::new_safe(Arc::new(f2_power2), gens.clone()).unwrap();
            let closure = closer.sg_close().unwrap();
            
            json!({
                "command": "sg_close_free_algebra",
                "num_gens": 2,
                "power": 2,
                "base_size": f2_cardinality,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "status": "success"
            })
        }
    );
}

#[test]
fn test_closer_f2_power3_java_comparison() {
    let config = TestConfig::default();
    
    let f2 = create_f_n(2);
    let f2_cardinality = f2.cardinality();
    let f2_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f2) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f2_power3 = BigProductAlgebra::new_power_safe(f2_boxed, 3).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0, 1]).unwrap();
    let g1 = IntArray::from_array(vec![0, 1, 0]).unwrap();
    let g2 = IntArray::from_array(vec![1, 0, 0]).unwrap();
    let gens = vec![g0, g1, g2];
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_free_algebra", "--num_gens", "2", "--power", "3", "--generators", "0,0,1;0,1,0;1,0,0"],
        || {
            let mut closer = Closer::new_safe(Arc::new(f2_power3), gens.clone()).unwrap();
            let closure = closer.sg_close().unwrap();
            
            json!({
                "command": "sg_close_free_algebra",
                "num_gens": 2,
                "power": 3,
                "base_size": f2_cardinality,
                "generators_count": 3,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "status": "success"
            })
        }
    );
}

/// Helper function to create a trivial algebra with no operations (like Java's makeTestAlgebra)
fn create_trivial_algebra(size: i32) -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
    use uacalc::alg::BasicAlgebra;
    use std::collections::HashSet;
    
    let universe: HashSet<i32> = (0..size).collect();
    let ops = Vec::new(); // No operations
    
    Box::new(BasicAlgebra::new(
        "TestAlg".to_string(),
        universe,
        ops,
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>
}

#[test]
fn test_closer_sg_close_power_ba2_power2_java_comparison() {
    let config = TestConfig::default();
    
    // Use trivial algebra (no operations) to match Java's makeTestAlgebra
    let trivial_alg = create_trivial_algebra(2);
    let alg_power2 = BigProductAlgebra::<i32>::new_power_safe(trivial_alg, 2).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![0, 1]).unwrap();
    let gens = vec![g0, g1];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_power", "--base_size", "2", "--power", "2", "--generators", "0,0;0,1"],
        || {
            let mut closer = Closer::new_safe(Arc::new(alg_power2), gens.clone()).unwrap();
            let closure = closer.sg_close_power().unwrap();
            
            json!({
                "command": "sg_close_power",
                "base_size": 2,
                "power": 2,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "status": "success"
            })
        }
    );
}

#[test]
fn test_closer_sg_close_power_ba2_power3_java_comparison() {
    let config = TestConfig::default();
    
    // Use trivial algebra (no operations) to match Java's makeTestAlgebra
    let trivial_alg = create_trivial_algebra(2);
    let alg_power3 = BigProductAlgebra::<i32>::new_power_safe(trivial_alg, 3).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0, 1]).unwrap();
    let g1 = IntArray::from_array(vec![1, 1, 0]).unwrap();
    let gens = vec![g0, g1];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_power", "--base_size", "2", "--power", "3", "--generators", "0,0,1;1,1,0"],
        || {
            let mut closer = Closer::new_safe(Arc::new(alg_power3), gens.clone()).unwrap();
            let closure = closer.sg_close_power().unwrap();
            
            json!({
                "command": "sg_close_power",
                "base_size": 2,
                "power": 3,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "status": "success"
            })
        }
    );
}

#[test]
fn test_closer_sg_close_power_ba2_power3_single_generator() {
    let config = TestConfig::default();
    
    // Use trivial algebra (no operations) to match Java's makeTestAlgebra
    let trivial_alg = create_trivial_algebra(2);
    let alg_power3 = BigProductAlgebra::<i32>::new_power_safe(trivial_alg, 3).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0, 0]).unwrap();
    let gens = vec![g0];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_power", "--base_size", "2", "--power", "3", "--generators", "0,0,0"],
        || {
            let mut closer = Closer::new_safe(Arc::new(alg_power3), gens.clone()).unwrap();
            let closure = closer.sg_close_power().unwrap();
            
            json!({
                "command": "sg_close_power",
                "base_size": 2,
                "power": 3,
                "generators_count": 1,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "status": "success"
            })
        }
    );
}

#[test]
fn test_closer_blocks_constraint_java_comparison() {
    let config = TestConfig::default();
    
    // Use ba2 algebra which has operations
    let ba2 = create_ba2();
    let alg_power2 = BigProductAlgebra::<i32>::new_power_safe(ba2, 2).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![0, 1]).unwrap();
    let gens = vec![g0, g1];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_with_constraints", "--base_size", "2", "--power", "2", "--generators", "0,0;0,1", "--blocks", "0,1"],
        || {
            let mut closer = Closer::new_safe(Arc::new(alg_power2), gens.clone()).unwrap();
            // Set blocks constraint: indices 0 and 1 must have the same value
            closer.set_blocks(Some(vec![vec![0, 1]]));
            let closure = closer.sg_close().unwrap();
            
            let found_element = closer.get_element_to_find().cloned();
            let found_element_value = found_element.as_ref().map(|e| e.as_slice().to_vec());
            
            // Match Java format: only include found_element_value if found_element is true
            let mut result = json!({
                "command": "sg_close_with_constraints",
                "base_size": 2,
                "power": 2,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "found_element": found_element.is_some(),
                "status": "success"
            });
            
            // Only add found_element_value if found_element is true (matching Java behavior)
            if found_element.is_some() {
                result["found_element_value"] = json!(found_element_value.unwrap());
            }
            
            result
        }
    );
}

#[test]
fn test_closer_values_constraint_java_comparison() {
    let config = TestConfig::default();
    
    // Use ba2 algebra which has operations
    let ba2 = create_ba2();
    let alg_power2 = BigProductAlgebra::<i32>::new_power_safe(ba2, 2).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![0, 1]).unwrap();
    let gens = vec![g0, g1];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_with_constraints", "--base_size", "2", "--power", "2", "--generators", "0,0;0,1", "--values", "0:1"],
        || {
            let mut closer = Closer::new_safe(Arc::new(alg_power2), gens.clone()).unwrap();
            // Set values constraint: index 0 must equal 1
            closer.set_values(Some(vec![(0, 1)]));
            let closure = closer.sg_close().unwrap();
            
            let found_element = closer.get_element_to_find().cloned();
            let found_element_value = found_element.as_ref().map(|e| e.as_slice().to_vec());
            
            // Match Java format: only include found_element_value if found_element is true
            let mut result = json!({
                "command": "sg_close_with_constraints",
                "base_size": 2,
                "power": 2,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "found_element": found_element.is_some(),
                "status": "success"
            });
            
            // Only add found_element_value if found_element is true (matching Java behavior)
            if found_element.is_some() {
                result["found_element_value"] = json!(found_element_value.unwrap());
            }
            
            result
        }
    );
}

#[test]
fn test_closer_congruence_constraint_java_comparison() {
    let config = TestConfig::default();
    
    // Use ba2 algebra which has operations
    let ba2 = create_ba2();
    let alg_power2 = BigProductAlgebra::<i32>::new_power_safe(ba2, 2).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![0, 1]).unwrap();
    let gens = vec![g0, g1];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_with_constraints", "--base_size", "2", "--power", "2", "--generators", "0,0;0,1", "--congruence", "|0 1|", "--congruence_index", "0", "--congruence_elem_index", "0"],
        || {
            let mut closer = Closer::new_safe(Arc::new(alg_power2), gens.clone()).unwrap();
            // Set congruence constraint: partition where 0 and 1 are in the same block
            // This means index 0's value must be congruent to element 0 under this partition
            // Use bar notation which is more compatible
            let partition = Partition::from_string("|0 1|").unwrap();
            closer.setup_congruence_constraint(partition, 0, 0);
            let closure = closer.sg_close().unwrap();
            
            let found_element = closer.get_element_to_find().cloned();
            let found_element_value = found_element.as_ref().map(|e| e.as_slice().to_vec());
            
            // Match Java format: only include found_element_value if found_element is true
            let mut result = json!({
                "command": "sg_close_with_constraints",
                "base_size": 2,
                "power": 2,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "found_element": found_element.is_some(),
                "status": "success"
            });
            
            // Only add found_element_value if found_element is true (matching Java behavior)
            if found_element.is_some() {
                result["found_element_value"] = json!(found_element_value.unwrap());
            }
            
            result
        }
    );
}


#[test]
fn test_closer_homomorphism_java_comparison() {
    let config = TestConfig::default();
    
    // Create separate ba2 instances for power algebra and image algebra
    let ba2_for_power = create_ba2();
    let ba2_for_image = create_ba2();
    // Use identity homomorphism: generators map to themselves
    // This ensures all elements in closure will have predictable images
    let ba2_power2 = BigProductAlgebra::<i32>::new_power_safe(ba2_for_power, 2).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![1, 1]).unwrap();
    let gens = vec![g0, g1];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_with_homomorphism", "--base_size", "2", "--power", "2", "--generators", "0,0;1,1", "--image_generators", "0,1"],
        || {
            let mut closer = Closer::new_safe(Arc::new(ba2_power2.clone()), gens.clone()).unwrap();
            
            // Enable term map (required for homomorphism checking)
            let mut term_map = HashMap::new();
            use uacalc::terms::VariableImp;
            for (i, gen) in gens.iter().enumerate() {
                let var_name = format!("x{}", i);
                let var = Box::new(VariableImp::new(&var_name)) as Box<dyn uacalc::terms::Term>;
                term_map.insert(gen.clone(), var);
            }
            closer.set_term_map(Some(term_map));
            
            // Set image algebra - use a fresh instance
            let image_alg = ba2_for_image.clone_box();
            closer.set_image_algebra(Some(Arc::from(image_alg))).unwrap();
            
            // Set homomorphism from generators - identity: 0->0, 1->1
            let image_gens = vec![0, 1];
            closer.set_homomorphism_from_gens(image_gens).unwrap();
            
            let closure = closer.sg_close().unwrap();
            
            let failing_eq = closer.get_failing_equation();
            let has_failing = failing_eq.is_some();
            
            // Build JSON matching Java format (Java omits failing_equation field when null)
            let mut result = json!({
                "command": "sg_close_with_homomorphism",
                "base_size": 2,
                "power": 2,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "has_failing_equation": has_failing,
                "status": "success"
            });
            
            // Only add failing_equation if it exists (matching Java behavior)
            if has_failing {
                if let Some(eq) = failing_eq {
                    result["failing_equation"] = json!(format!("{}", eq));
                }
            }
            
            result
        }
    );
}

#[test]
fn test_closer_homomorphism_ba2_square_to_base_java_comparison() {
    let config = TestConfig::default();
    
    // Test projection homomorphism from ba2^2 to ba2
    // Note: We can't test ba2^2 to itself directly because BigProductAlgebra 
    // doesn't implement SmallAlgebra. This test uses a projection to ba2 instead.
    
    // Create ba2^2 (square of ba2) - power algebra with power 2
    let ba2_for_power = create_ba2();
    let ba2_for_image = create_ba2();
    let ba2_power2 = BigProductAlgebra::<i32>::new_power_safe(ba2_for_power, 2).unwrap();
    
    // Use generators that create a simple closure
    // The identity case [0,0] and [1,1] works because closure is just these two elements
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![1, 1]).unwrap();
    let gens = vec![g0, g1];
    
    // Test projection homomorphism from ba2^2 to ba2
    // Map [0,0] -> 0 and [1,1] -> 1 (projection to first coordinate)
    // This is a projection homomorphism that preserves the homomorphism property
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_with_homomorphism", "--base_size", "2", "--power", "2", "--generators", "0,0;1,1", "--image_generators", "0,1"],
        || {
            let mut closer = Closer::new_safe(Arc::new(ba2_power2.clone()), gens.clone()).unwrap();
            
            // Enable term map (required for homomorphism checking)
            let mut term_map = HashMap::new();
            use uacalc::terms::VariableImp;
            for (i, gen) in gens.iter().enumerate() {
                let var_name = format!("x{}", i);
                let var = Box::new(VariableImp::new(&var_name)) as Box<dyn uacalc::terms::Term>;
                term_map.insert(gen.clone(), var);
            }
            closer.set_term_map(Some(term_map));
            
            // Set image algebra - use ba2 (base algebra) as the image
            let image_alg = Arc::from(ba2_for_image.clone_box());
            closer.set_image_algebra(Some(image_alg)).unwrap();
            
            // Set homomorphism from generators
            // Map [0,0] -> 0 and [1,1] -> 1 (projection to first coordinate)
            let image_gens = vec![0, 1];
            closer.set_homomorphism_from_gens(image_gens).unwrap();
            
            let closure = closer.sg_close().unwrap();
            
            let failing_eq = closer.get_failing_equation();
            let has_failing = failing_eq.is_some();
            
            // Build JSON matching Java format
            let mut result = json!({
                "command": "sg_close_with_homomorphism",
                "base_size": 2,
                "power": 2,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "has_failing_equation": has_failing,
                "status": "success"
            });
            
            // Only add failing_equation if it exists (matching Java behavior)
            if has_failing {
                if let Some(eq) = failing_eq {
                    result["failing_equation"] = json!(format!("{}", eq));
                }
            }
            
            result
        }
    );
}

#[test]
fn test_closer_operations_finding_java_comparison() {
    let config = TestConfig::default();
    
    // Create ba2^2 (square of ba2) - power algebra with power 2
    let ba2_for_power = create_ba2();
    let ba2_for_root = create_ba2();
    let ba2_power2 = BigProductAlgebra::<i32>::new_power_safe(ba2_for_power, 2).unwrap();
    
    // Use generators that create a closure containing the operations we're looking for
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![0, 1]).unwrap();
    let gens = vec![g0, g1];
    
    // Create an operation to find - use meet operation from ba2
    // For ba2, meet is binary: 0,0->0, 0,1->0, 1,0->0, 1,1->1
    // Table: [0, 0, 0, 1]
    use uacalc::alg::op::{OperationSymbol, Operation};
    use uacalc::alg::op::ops::make_int_operation;
    use std::sync::Arc;
    
    let meet_symbol = OperationSymbol::new("meet", 2, false);
    let meet_table = vec![0, 0, 0, 1];
    let meet_op = make_int_operation(meet_symbol, 2, meet_table).unwrap();
    
    let operations_to_find = vec![Arc::from(meet_op) as Arc<dyn Operation>];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_with_operations_finding", "--base_size", "2", "--power", "2", "--generators", "0,0;0,1", "--operations", "2:0,0,0,1"],
        || {
            let mut closer = Closer::new_safe(Arc::new(ba2_power2.clone()), gens.clone()).unwrap();
            
            // Enable term map (required for operations finding)
            let mut term_map = HashMap::new();
            use uacalc::terms::VariableImp;
            for (i, gen) in gens.iter().enumerate() {
                let var_name = format!("x{}", i);
                let var = Box::new(VariableImp::new(&var_name)) as Box<dyn uacalc::terms::Term>;
                term_map.insert(gen.clone(), var);
            }
            closer.set_term_map(Some(term_map));
            
            // Set root algebra and operations
            let root_alg = ba2_for_root.clone_box();
            closer.set_root_algebra(Some(Arc::from(root_alg)));
            closer.set_operations(Some(operations_to_find.clone()));
            
            let closure = closer.sg_close().unwrap();
            
            // Get term map for operations
            let term_map_for_ops = closer.get_term_map_for_operations();
            let mut operations_found = HashMap::new();
            if let Some(ref map) = term_map_for_ops {
                for (sym, term) in map.iter() {
                    operations_found.insert(sym.name().to_string(), format!("{}", term));
                }
            }
            
            json!({
                "command": "sg_close_with_operations_finding",
                "base_size": 2,
                "power": 2,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "operations_found_count": operations_found.len(),
                "operations_found": operations_found,
                "status": "success"
            })
        }
    );
}

#[test]
fn test_closer_multiple_elements_finding_java_comparison() {
    let config = TestConfig::default();
    
    let ba2 = create_ba2();
    let ba2_power2 = BigProductAlgebra::<i32>::new_power_safe(ba2, 2).unwrap();
    
    let g0 = IntArray::from_array(vec![0, 0]).unwrap();
    let g1 = IntArray::from_array(vec![0, 1]).unwrap();
    let gens = vec![g0, g1];
    
    // Elements to find: [1,1] and [1,0]
    let e1 = IntArray::from_array(vec![1, 1]).unwrap();
    let e2 = IntArray::from_array(vec![1, 0]).unwrap();
    let elements_to_find = vec![e1, e2];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.CloserWrapper",
        ["sg_close_with_multiple_elements", "--power", "2", "--generators", "0,0;0,1", "--elements_to_find", "1,1;1,0"],
        || {
            let mut closer = Closer::new_safe(Arc::new(ba2_power2), gens.clone()).unwrap();
            closer.set_elements_to_find(elements_to_find.clone(), &gens);
            let closure = closer.sg_close_power().unwrap();
            
            json!({
                "command": "sg_close_with_multiple_elements",
                "power": 2,
                "base_size": 2,
                "generators_count": 2,
                "closure_size": closure.len(),
                "closure": closure.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "elements_to_find": elements_to_find.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>(),
                "all_elements_found": closer.all_elements_found(),
                "status": "success"
            })
        }
    );
}
