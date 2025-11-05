/*!
 * Java comparison tests for Closer implementation.
 * 
 * These tests verify that Rust Closer implementation produces the same results
 * as the Java implementation for power algebras and free algebras.
 */

use uacalc::alg::{Closer, BigProductAlgebra, FreeAlgebra, Algebra, SmallAlgebra};
use uacalc::util::int_array::{IntArray, IntArrayTrait};
use uacalc::io::algebra_io::read_algebra_file;
use std::collections::HashSet;
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
    use uacalc::alg::BasicSmallAlgebra;
    
    let card = base_alg.cardinality();
    let ops = base_alg.operations();
    let int_ops = make_int_operations(ops).expect("Failed to create int operations");
    let universe: HashSet<i32> = (0..card).collect();
    
    Box::new(BasicSmallAlgebra::new(
        base_alg.name().to_string(),
        universe,
        int_ops,
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>
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
