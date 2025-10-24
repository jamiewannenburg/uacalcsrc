use uacalc::alg::{SmallAlgebra, BasicSmallAlgebra, Algebra};
use uacalc::alg::conlat::{CongruenceLattice, Partition};
use std::collections::HashSet;

#[test]
fn test_new_congruence_lattice() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let con_lat = CongruenceLattice::new(alg);
    assert_eq!(con_lat.alg_size(), 3);
}

#[test]
fn test_zero_and_one() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let con_lat = CongruenceLattice::new(alg);
    
    let zero = con_lat.zero();
    assert_eq!(zero.number_of_blocks(), 3);
    
    let one = con_lat.one();
    assert_eq!(one.number_of_blocks(), 1);
}

#[test]
fn test_principal_congruence() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Cg(0, 1) for an algebra with no operations should relate 0 and 1
    let cg = con_lat.cg(0, 1);
    assert!(cg.is_related(0, 1));
    
    // Cg(0, 0) should be zero
    let cg_same = con_lat.cg(0, 0);
    assert_eq!(cg_same.number_of_blocks(), 3);
}

#[test]
fn test_cardinality() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // For a 3-element algebra with no operations, Con(A) should have 5 congruences
    let card = con_lat.con_cardinality();
    assert_eq!(card, 5);
}

#[test]
fn test_principals() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2, 3]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    let principals = con_lat.principals();
    
    // For a 4-element algebra with no operations, should have 6 principal congruences
    assert_eq!(principals.len(), 6);
}

#[test]
fn test_join_irreducibles() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    let jis = con_lat.join_irreducibles();
    
    // For a 3-element algebra with no operations, should have 3 join irreducibles
    assert_eq!(jis.len(), 3);
}

#[test]
fn test_atoms() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    let atoms = con_lat.atoms();
    
    // For a 3-element algebra with no operations, should have 3 atoms
    assert_eq!(atoms.len(), 3);
}

#[test]
fn test_is_distributive() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // For a 3-element algebra with no operations, the congruence lattice should not be distributive
    let is_dist = con_lat.is_distributive();
    assert_eq!(is_dist, false);
}

#[test]
fn test_find_principal_chain() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    let chain = con_lat.find_principal_chain();
    
    // Should have at least the zero congruence
    assert!(!chain.is_empty());
    assert_eq!(chain[0].number_of_blocks(), 3); // First should be zero
}

#[test]
fn test_complements() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    let zero = con_lat.zero();
    let complements = con_lat.complements(&zero);
    
    // Zero should have one as its complement
    assert!(!complements.is_empty());
}

#[test]
fn test_universe_generation() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Make universe
    con_lat.make_universe();
    
    // Check it was created
    assert!(con_lat.universe_found());
    
    // Check cardinality
    assert_eq!(con_lat.con_cardinality(), 5);
}

#[test]
fn test_meet_irreducibles() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    let mis = con_lat.meet_irreducibles();
    
    // Should have at least one meet irreducible
    assert!(!mis.is_empty());
}
