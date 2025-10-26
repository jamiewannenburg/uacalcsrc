use uacalc::alg::{SubProductAlgebra, BigProductAlgebra, SmallAlgebra, BasicSmallAlgebra};
use uacalc::util::int_array::IntArray;
use std::collections::HashSet;

#[test]
fn test_sub_product_algebra_sub_method() {
    // Create two small algebras
    let alg1 = Box::new(BasicSmallAlgebra::new(
        "A1".to_string(),
        HashSet::from([0, 1]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;

    let alg2 = Box::new(BasicSmallAlgebra::new(
        "A2".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;

    // Create big product algebra
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();

    // Create generators for SubProductAlgebra
    let mut gens = vec![];
    gens.push(IntArray::from_array(vec![0, 0]).unwrap());
    gens.push(IntArray::from_array(vec![1, 0]).unwrap());
    gens.push(IntArray::from_array(vec![0, 1]).unwrap());

    // Create SubProductAlgebra
    let mut sub_prod = SubProductAlgebra::new_safe(
        "SubProd".to_string(),
        product,
        gens,
        false
    ).unwrap();

    // Test that sub() method works without panicking
    let sub_lat = sub_prod.sub();
    
    // Basic checks
    assert_eq!(sub_lat.get_algebra().name(), "SubProd");
    assert!(sub_lat.get_algebra().cardinality() > 0);
    
    // Test that we can call sub() multiple times (lazy initialization)
    // We need to drop the first reference before getting the second
    drop(sub_lat);
    let sub_lat2 = sub_prod.sub();
    assert_eq!(sub_lat2.get_algebra().name(), "SubProd");
}

#[test]
fn test_sub_product_algebra_sub_with_single_factor() {
    // Create a single small algebra
    let alg = Box::new(BasicSmallAlgebra::new(
        "Single".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;

    // Create big product algebra with single factor
    let product = BigProductAlgebra::new_safe(vec![alg]).unwrap();

    // Create generators
    let mut gens = vec![];
    gens.push(IntArray::from_array(vec![0]).unwrap());
    gens.push(IntArray::from_array(vec![1]).unwrap());

    // Create SubProductAlgebra
    let mut sub_prod = SubProductAlgebra::new_safe(
        "SingleSubProd".to_string(),
        product,
        gens,
        false
    ).unwrap();

    // Test sub() method
    let sub_lat = sub_prod.sub();
    assert_eq!(sub_lat.get_algebra().name(), "SingleSubProd");
    assert!(sub_lat.get_algebra().cardinality() > 0);
}

#[test]
fn test_sub_product_algebra_sub_with_terms() {
    // Create two small algebras
    let alg1 = Box::new(BasicSmallAlgebra::new(
        "A1".to_string(),
        HashSet::from([0, 1]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;

    let alg2 = Box::new(BasicSmallAlgebra::new(
        "A2".to_string(),
        HashSet::from([0, 1]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;

    // Create big product algebra
    let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();

    // Create generators
    let mut gens = vec![];
    gens.push(IntArray::from_array(vec![0, 0]).unwrap());
    gens.push(IntArray::from_array(vec![1, 1]).unwrap());

    // Create SubProductAlgebra with terms
    let mut sub_prod = SubProductAlgebra::new_safe(
        "SubProdWithTerms".to_string(),
        product,
        gens,
        true  // find_terms = true
    ).unwrap();

    // Test sub() method
    let sub_lat = sub_prod.sub();
    assert_eq!(sub_lat.get_algebra().name(), "SubProdWithTerms");
    assert!(sub_lat.get_algebra().cardinality() > 0);
    
    // Test that terms are available
    assert!(sub_prod.get_terms().is_some());
    assert!(sub_prod.get_term_map().is_some());
}
