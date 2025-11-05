/*!
 * Java comparison tests for SubProductAlgebra implementation.
 * 
 * These tests verify that Rust SubProductAlgebra implementation produces the same results
 * as the Java implementation.
 */

use uacalc::alg::{SubProductAlgebra, BigProductAlgebra, SmallAlgebra, BasicSmallAlgebra};
use uacalc::util::int_array::{IntArray, IntArrayTrait};
use std::collections::HashSet;
use serde_json::json;

use uacalc::common::*;
use uacalc::compare_with_java;

/// Helper function to create a simple algebra with given size
fn create_simple_algebra(name: &str, size: usize) -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
    use uacalc::alg::op::{OperationSymbol, Operation};
    use uacalc::alg::op::operations;
    
    let universe: HashSet<i32> = (0..size as i32).collect();
    
    // Add a constant operation to make the algebra valid for closure computation
    let mut ops: Vec<Box<dyn Operation>> = Vec::new();
    let const_sym = OperationSymbol::new("c", 0, false);
    let const_op = operations::make_int_operation(const_sym, size as i32, vec![0])
        .expect("Failed to create constant operation");
    ops.push(const_op);
    
    Box::new(BasicSmallAlgebra::new(
        name.to_string(),
        universe,
        ops
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>
}

#[test]
fn test_sub_product_algebra_create_java_comparison() {
    let config = TestConfig::default();
    
    let alg1 = create_simple_algebra("A1", 2);
    let alg2 = create_simple_algebra("A2", 3);
    
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
    
    let gens = vec![
        IntArray::from_array(vec![0, 0]).unwrap(),
        IntArray::from_array(vec![1, 0]).unwrap(),
        IntArray::from_array(vec![0, 1]).unwrap(),
    ];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.SubProductAlgebraWrapper",
        ["create", "--name", "TestSubProd", "--factors", "2", "--factor_sizes", "2,3", "--generators", "0,0|1,0|0,1", "--find_terms", "false"],
        || {
            let sub_prod = SubProductAlgebra::new_safe(
                "TestSubProd".to_string(),
                product,
                gens.clone(),
                false
            ).unwrap();
            
            json!({
                "command": "create",
                "name": "TestSubProd",
                "cardinality": sub_prod.cardinality(),
                "number_of_generators": gens.len(),
                "status": "created"
            })
        }
    );
}

#[test]
fn test_sub_product_algebra_cardinality_java_comparison() {
    let config = TestConfig::default();
    
    let alg1 = create_simple_algebra("A1", 2);
    let alg2 = create_simple_algebra("A2", 3);
    
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
    
    let gens = vec![
        IntArray::from_array(vec![0, 0]).unwrap(),
        IntArray::from_array(vec![1, 0]).unwrap(),
        IntArray::from_array(vec![0, 1]).unwrap(),
    ];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.SubProductAlgebraWrapper",
        ["cardinality", "--factors", "2", "--factor_sizes", "2,3", "--generators", "0,0|1,0|0,1"],
        || {
            let sub_prod = SubProductAlgebra::new_safe(
                "TestSubProd".to_string(),
                product,
                gens.clone(),
                false
            ).unwrap();
            
            json!({
                "command": "cardinality",
                "cardinality": sub_prod.cardinality()
            })
        }
    );
}

#[test]
fn test_sub_product_algebra_element_index_java_comparison() {
    let config = TestConfig::default();
    
    let alg1 = create_simple_algebra("A1", 2);
    let alg2 = create_simple_algebra("A2", 3);
    
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
    
    let gens = vec![
        IntArray::from_array(vec![0, 0]).unwrap(),
        IntArray::from_array(vec![1, 0]).unwrap(),
        IntArray::from_array(vec![0, 1]).unwrap(),
    ];
    
    let sub_prod = SubProductAlgebra::new_safe(
        "TestSubProd".to_string(),
        product,
        gens.clone(),
        false
    ).unwrap();
    
    // Get the first element from the universe
    let first_elem = sub_prod.get_universe_list()[0].clone();
    let elem_slice = first_elem.as_slice();
    let elem_str = format!("{},{}", elem_slice[0], elem_slice[1]);
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.SubProductAlgebraWrapper",
        ["element_index", "--element", &elem_str, "--factors", "2", "--factor_sizes", "2,3", "--generators", "0,0|1,0|0,1"],
        || {
            let index = sub_prod.element_index(&first_elem).unwrap();
            
            json!({
                "command": "element_index",
                "element": elem_slice.to_vec(),
                "index": index
            })
        }
    );
}

#[test]
fn test_sub_product_algebra_get_element_java_comparison() {
    let config = TestConfig::default();
    
    let alg1 = create_simple_algebra("A1", 2);
    let alg2 = create_simple_algebra("A2", 3);
    
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
    
    let gens = vec![
        IntArray::from_array(vec![0, 0]).unwrap(),
        IntArray::from_array(vec![1, 0]).unwrap(),
        IntArray::from_array(vec![0, 1]).unwrap(),
    ];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.SubProductAlgebraWrapper",
        ["get_element", "--index", "0", "--factors", "2", "--factor_sizes", "2,3", "--generators", "0,0|1,0|0,1"],
        || {
            let sub_prod = SubProductAlgebra::new_safe(
                "TestSubProd".to_string(),
                product,
                gens.clone(),
                false
            ).unwrap();
            
            let element = sub_prod.get_element(0).unwrap();
            let elem_slice = element.as_slice();
            
            json!({
                "command": "get_element",
                "index": 0,
                "element": elem_slice.to_vec()
            })
        }
    );
}

#[test]
fn test_sub_product_algebra_generators_java_comparison() {
    let config = TestConfig::default();
    
    let alg1 = create_simple_algebra("A1", 2);
    let alg2 = create_simple_algebra("A2", 3);
    
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
    
    let gens = vec![
        IntArray::from_array(vec![0, 0]).unwrap(),
        IntArray::from_array(vec![1, 0]).unwrap(),
        IntArray::from_array(vec![0, 1]).unwrap(),
    ];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.SubProductAlgebraWrapper",
        ["generators", "--factors", "2", "--factor_sizes", "2,3", "--generators", "0,0|1,0|0,1"],
        || {
            let sub_prod = SubProductAlgebra::new_safe(
                "TestSubProd".to_string(),
                product,
                gens.clone(),
                false
            ).unwrap();
            
            let generators = sub_prod.generators();
            let gen_vecs: Vec<Vec<i32>> = generators.iter()
                .map(|g| g.as_slice().to_vec())
                .collect();
            
            json!({
                "command": "generators",
                "number_of_generators": generators.len(),
                "generators": gen_vecs
            })
        }
    );
}

#[test]
fn test_sub_product_algebra_get_universe_list_java_comparison() {
    let config = TestConfig::default();
    
    let alg1 = create_simple_algebra("A1", 2);
    let alg2 = create_simple_algebra("A2", 3);
    
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
    
    let gens = vec![
        IntArray::from_array(vec![0, 0]).unwrap(),
        IntArray::from_array(vec![1, 0]).unwrap(),
        IntArray::from_array(vec![0, 1]).unwrap(),
    ];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.SubProductAlgebraWrapper",
        ["get_universe_list", "--factors", "2", "--factor_sizes", "2,3", "--generators", "0,0|1,0|0,1"],
        || {
            let sub_prod = SubProductAlgebra::new_safe(
                "TestSubProd".to_string(),
                product,
                gens.clone(),
                false
            ).unwrap();
            
            let univ = sub_prod.get_universe_list();
            let univ_vecs: Vec<Vec<i32>> = univ.iter()
                .map(|e| e.as_slice().to_vec())
                .collect();
            
            json!({
                "command": "get_universe_list",
                "universe_size": univ.len(),
                "universe": univ_vecs
            })
        }
    );
}

#[test]
fn test_sub_product_algebra_transpose_java_comparison() {
    let config = TestConfig::default();
    
    let arrays = vec![
        IntArray::from_array(vec![0, 1]).unwrap(),
        IntArray::from_array(vec![2, 3]).unwrap(),
        IntArray::from_array(vec![4, 5]).unwrap(),
    ];
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.SubProductAlgebraWrapper",
        ["transpose", "--arrays", "0,1|2,3|4,5"],
        || {
            let transposed = SubProductAlgebra::<i32>::transpose(&arrays).unwrap();
            let transposed_vecs: Vec<Vec<i32>> = transposed.iter()
                .map(|a| a.as_slice().to_vec())
                .collect();
            
            json!({
                "command": "transpose",
                "input_size": arrays.len(),
                "output_size": transposed.len(),
                "transposed": transposed_vecs
            })
        }
    );
}

#[test]
fn test_sub_product_algebra_test_java_comparison() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.SubProductAlgebraWrapper",
        ["test"],
        || {
            let alg1 = create_simple_algebra("A1", 2);
            let alg2 = create_simple_algebra("A2", 3);
            
            let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
            
            let gens = vec![
                IntArray::from_array(vec![0, 0]).unwrap(),
                IntArray::from_array(vec![1, 0]).unwrap(),
                IntArray::from_array(vec![0, 1]).unwrap(),
            ];
            
            let sub_prod = SubProductAlgebra::new_safe(
                "TestSubProd".to_string(),
                product,
                gens.clone(),
                false
            ).unwrap();
            
            let card = sub_prod.cardinality();
            let univ = sub_prod.get_universe_list();
            let order = sub_prod.get_universe_order();
            let generators = sub_prod.generators();
            
            let first_elem = sub_prod.get_element(0).unwrap();
            let first_index = sub_prod.element_index(&first_elem).unwrap();
            
            json!({
                "command": "test",
                "name": "TestSubProd",
                "cardinality": card,
                "universe_size": univ.len(),
                "order_map_size": order.len(),
                "generators_count": generators.len(),
                "first_element_index": first_index,
                "test_passed": true
            })
        }
    );
}

