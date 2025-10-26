// CongruenceLattice Java comparison tests
// These tests compare Rust CongruenceLattice output to Java implementation

use uacalc::alg::{SmallAlgebra, BasicSmallAlgebra};
use uacalc::alg::conlat::CongruenceLattice;
use std::collections::HashSet;

// NOTE: These tests should be enhanced with Java comparisons using the
// compare_with_java! macro once the macro import issues are resolved.
// For now, they verify the Rust implementation works correctly.

#[test]
fn test_principals_count_size_3() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    let principals = con_lat.principals();
    
    // For size 3 with no operations, we expect 3 principal congruences
    assert_eq!(principals.len(), 3);
    println!("Principals count for size 3: {}", principals.len());
}

#[test]
fn test_join_irreducibles_count_size_3() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    let jis = con_lat.join_irreducibles();
    
    // For size 3 with no operations, we expect 3 join irreducibles
    assert_eq!(jis.len(), 3);
    println!("Join irreducibles count for size 3: {}", jis.len());
}

#[test]
fn test_cardinality_size_3() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    let card = con_lat.con_cardinality();
    
    // For size 3 with no operations, Bell number B_3 = 5
    assert_eq!(card, 5);
    println!("Cardinality for size 3: {}", card);
}

#[test]
fn test_cardinality_size_2() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    let card = con_lat.con_cardinality();
    
    // For size 2 with no operations, Bell number B_2 = 2
    assert_eq!(card, 2);
    println!("Cardinality for size 2: {}", card);
}

#[test]
fn test_is_distributive_size_3() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    let is_dist = con_lat.is_distributive();
    
    // For size 3 with no operations, lattice is not distributive
    assert_eq!(is_dist, false);
    println!("Is distributive for size 3: {}", is_dist);
}

#[test]
fn test_atoms_count_size_3() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    let atoms = con_lat.atoms();
    
    // For size 3 with no operations, we expect 3 atoms
    assert_eq!(atoms.len(), 3);
    println!("Atoms count for size 3: {}", atoms.len());
}

#[test]
fn test_principals_size_4() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2, 3]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    let principals = con_lat.principals();
    
    // For size 4 with no operations, we expect 6 principal congruences (C(4,2) = 6)
    assert_eq!(principals.len(), 6);
    println!("Principals count for size 4: {}", principals.len());
}

// TODO: Add actual Java CLI wrapper comparison tests
// These require fixing the compare_with_java! macro import issues
// Example command that should work:
// java -cp "java_wrapper/build/classes:build/classes:org:jars/*" \
//      java_wrapper.src.alg.conlat.CongruenceLatticeWrapper \
//      principals --size 3
