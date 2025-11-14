// Tests for con() and sub() methods on various algebra types
// These tests verify that congruence and subalgebra lattices work correctly
// for BigProductAlgebra, SubProductAlgebra, and QuotientAlgebra

use uacalc::alg::{SmallAlgebra, BasicAlgebra, Algebra};
use uacalc::alg::{BigProductAlgebra, SubProductAlgebra, QuotientAlgebra};
use uacalc::alg::conlat::Partition;
use uacalc::alg::op::{OperationSymbol, Operation};
use uacalc::alg::op::operations;
use uacalc::util::int_array::IntArray;
use std::collections::HashSet;

/// Helper function to create a BasicAlgebra with operations.
/// The algebra needs at least one operation for closure computation in con() and sub() methods.
fn create_algebra_with_ops(name: &str, universe: HashSet<i32>) -> BasicAlgebra<i32> {
    let mut ops: Vec<Box<dyn Operation>> = Vec::new();
    
    let size = universe.len() as i32;
    // Add a binary operation (e.g., addition mod size)
    let add_sym = OperationSymbol::new("add", 2, false);
    let mut add_table = Vec::new();
    let usize_size = universe.len();
    for i in 0..usize_size {
        for j in 0..usize_size {
            add_table.push(((i + j) % usize_size) as i32);
        }
    }
    let add_op = operations::make_int_operation(add_sym, size, add_table)
        .expect("Failed to create operation");
    ops.push(add_op);
    
    BasicAlgebra::new(name.to_string(), universe, ops)
}

#[test]
fn test_basic_algebra_con() {
    // Baseline test - BasicAlgebra con() should work
    let mut alg = create_algebra_with_ops("A", HashSet::from([0, 1, 2]));
    
    let con_lat_ref = alg.con();
    assert_eq!(con_lat_ref.alg_size(), 3);
    
    // Clone to get mutable access
    let mut con_lat = con_lat_ref.clone();
    assert!(con_lat.con_cardinality() > 0);
}

#[test]
fn test_subproduct_algebra_con() {
    // Test that SubProductAlgebra.con() works
    let alg1 = Box::new(create_algebra_with_ops("A1", HashSet::from([0, 1]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let alg2 = Box::new(create_algebra_with_ops("A2", HashSet::from([0, 1]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
    
    // Create a simple subproduct with 2 generators
    let gen1 = IntArray::from_array(vec![0, 0]).unwrap();
    let gen2 = IntArray::from_array(vec![1, 1]).unwrap();
    
    let mut sub_prod = SubProductAlgebra::new_safe(
        "SubProd".to_string(),
        product,
        vec![gen1, gen2],
        false
    ).unwrap();
    
    // Test con() method
    let con_lat_ref = sub_prod.con();
    assert!(con_lat_ref.alg_size() > 0);
    println!("SubProductAlgebra con lattice size: {}", con_lat_ref.alg_size());
}

#[test]
fn test_subproduct_algebra_con_larger() {
    // Test with a slightly larger subproduct
    let alg1 = Box::new(create_algebra_with_ops("A1", HashSet::from([0, 1, 2]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let alg2 = Box::new(create_algebra_with_ops("A2", HashSet::from([0, 1]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
    
    // Create generators
    let gen1 = IntArray::from_array(vec![0, 0]).unwrap();
    let gen2 = IntArray::from_array(vec![1, 0]).unwrap();
    let gen3 = IntArray::from_array(vec![2, 1]).unwrap();
    
    let mut sub_prod = SubProductAlgebra::new_safe(
        "SubProd".to_string(),
        product,
        vec![gen1, gen2, gen3],
        false
    ).unwrap();
    
    // Test con() method
    let subprod_size = sub_prod.cardinality() as usize;
    let con_lat_ref = sub_prod.con();
    assert!(con_lat_ref.alg_size() > 0);
    assert!(con_lat_ref.alg_size() <= subprod_size); // Should be at most size of subproduct
    println!("Larger SubProductAlgebra con lattice size: {}", con_lat_ref.alg_size());
}

#[test]
fn test_quotient_algebra_con() {
    // Test that QuotientAlgebra.con() works
    let super_algebra = Box::new(create_algebra_with_ops("A", HashSet::from([0, 1, 2, 3]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Create a congruence: {0,1}, {2,3}
    let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
    
    let mut quot = QuotientAlgebra::<i32>::new_safe(super_algebra, congruence).unwrap();
    
    // Test con() method
    let con_lat_ref = quot.con();
    assert_eq!(con_lat_ref.alg_size(), 2); // Quotient has 2 elements
    
    // Clone to get mutable access for cardinality
    let mut con_lat = con_lat_ref.clone();
    
    // For a 2-element algebra with no operations, con lattice should have 2 elements
    let card = con_lat.con_cardinality();
    assert_eq!(card, 2);
    println!("QuotientAlgebra con lattice cardinality: {}", card);
}

#[test]
fn test_quotient_algebra_con_larger() {
    // Test with a larger quotient
    let super_algebra = Box::new(create_algebra_with_ops("A", HashSet::from([0, 1, 2, 3, 4, 5]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Create a congruence: {0,1}, {2,3}, {4,5}
    let congruence = Partition::new(vec![-2, 0, -2, 2, -2, 4]).unwrap();
    
    let mut quot = QuotientAlgebra::<i32>::new_safe(super_algebra, congruence).unwrap();
    
    // Test con() method
    let con_lat_ref = quot.con();
    assert_eq!(con_lat_ref.alg_size(), 3); // Quotient has 3 elements
    
    // Clone to get mutable access for cardinality
    let mut con_lat = con_lat_ref.clone();
    
    // With operations, the congruence lattice cardinality depends on the operations
    // Just verify it's positive (there's at least the trivial congruence)
    let card = con_lat.con_cardinality();
    assert!(card > 0);
    assert!(card <= 5); // Should be at most B_3 (Bell number for 3 elements) without operations
    println!("Larger QuotientAlgebra con lattice cardinality: {}", card);
}

#[test]
fn test_subproduct_algebra_sub() {
    // Test that SubProductAlgebra.sub() works
    let alg1 = Box::new(create_algebra_with_ops("A1", HashSet::from([0, 1]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let alg2 = Box::new(create_algebra_with_ops("A2", HashSet::from([0, 1]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
    
    let gen1 = IntArray::from_array(vec![0, 0]).unwrap();
    let gen2 = IntArray::from_array(vec![1, 1]).unwrap();
    
    let mut sub_prod = SubProductAlgebra::new_safe(
        "SubProd".to_string(),
        product,
        vec![gen1, gen2],
        false
    ).unwrap();
    
    // Test sub() method
    let _sub_lat_ref = sub_prod.sub();
    // SubalgebraLattice doesn't have public alg_size, just verify it's not panicking
    println!("SubProductAlgebra sub lattice created successfully");
    assert!(true); // If we get here, sub() worked
}

#[test]
fn test_congruence_lattice_operations_on_subproduct() {
    // Test that we can perform congruence operations on a SubProductAlgebra
    let alg1 = Box::new(create_algebra_with_ops("A1", HashSet::from([0, 1, 2]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let alg2 = Box::new(create_algebra_with_ops("A2", HashSet::from([0, 1]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
    
    let gen1 = IntArray::from_array(vec![0, 0]).unwrap();
    let gen2 = IntArray::from_array(vec![1, 1]).unwrap();
    
    let mut sub_prod = SubProductAlgebra::new_safe(
        "SubProd".to_string(),
        product,
        vec![gen1, gen2],
        false
    ).unwrap();
    
    // Get congruence lattice
    let mut con_lat = sub_prod.con().clone();
    
    // Test basic congruence operations
    let zero = con_lat.zero();
    let one = con_lat.one();
    
    assert!(zero.number_of_blocks() >= one.number_of_blocks());
    
    // Test principal congruence computation
    let cg = con_lat.cg(0, 1);
    assert!(cg.number_of_blocks() > 0);
    
    println!("SubProductAlgebra congruence lattice operations successful");
}

#[test]
fn test_congruence_lattice_operations_on_quotient() {
    // Test that we can perform congruence operations on a QuotientAlgebra
    let super_algebra = Box::new(create_algebra_with_ops("A", HashSet::from([0, 1, 2, 3, 4, 5]))) 
        as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Create a congruence: {0,1}, {2,3}, {4,5}
    let congruence = Partition::new(vec![-2, 0, -2, 2, -2, 4]).unwrap();
    
    let mut quot = QuotientAlgebra::<i32>::new_safe(super_algebra, congruence).unwrap();
    
    // Get congruence lattice and clone it for mutation
    let mut con_lat = quot.con().clone();
    
    // Test basic congruence operations
    let zero = con_lat.zero();
    let one = con_lat.one();
    
    assert_eq!(zero.number_of_blocks(), 3); // 3 elements in quotient
    assert_eq!(one.number_of_blocks(), 1); // All in one block
    
    // Test principal congruence computation
    let cg = con_lat.cg(0, 1);
    assert!(cg.number_of_blocks() > 0);
    
    // Test universe generation
    con_lat.make_universe();
    assert!(con_lat.universe_found());
    
    println!("QuotientAlgebra congruence lattice operations successful");
}
