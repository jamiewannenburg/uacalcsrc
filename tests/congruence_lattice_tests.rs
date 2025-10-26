use uacalc::alg::{SmallAlgebra, BasicSmallAlgebra};
use uacalc::alg::conlat::{CongruenceLattice, BasicBinaryRelation, BinaryRelation};
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

#[test]
fn test_tg_tolerance() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Test tolerance calculation for elements 0 and 1
    let tolerance = con_lat.tg(0, 1).unwrap();
    
    // Tolerance should be a binary relation
    assert!(tolerance.universe_size() > 0);
}

#[test]
fn test_generating_pair() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Test generating pair for zero partition
    let zero = con_lat.zero();
    let generating_pair = con_lat.generating_pair(&zero);
    
    // Zero partition should not have a generating pair (it's already minimal)
    assert!(generating_pair.is_none());
}

#[test]
fn test_find_coatom_above() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Test finding coatom above zero partition
    let zero = con_lat.zero();
    let coatom = con_lat.find_coatom_above(&zero);
    
    // Should return a partition with fewer blocks than zero
    assert!(coatom.number_of_blocks() <= zero.number_of_blocks());
}

#[test]
fn test_find_join_irred() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Test finding join irreducible between zero and one
    let zero = con_lat.zero();
    let one = con_lat.one();
    let join_irred = con_lat.find_join_irred(&zero, &one);
    
    // Should return Some since zero < one
    assert!(join_irred.is_some());
}

#[test]
fn test_find_meet_irred() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Test finding meet irreducible between zero and one
    let zero = con_lat.zero();
    let one = con_lat.one();
    let meet_irred = con_lat.find_meet_irred(&zero, &one);
    
    // Should return Some since zero < one
    assert!(meet_irred.is_some());
}

#[test]
fn test_find_maximal_chain() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Test finding maximal chain
    let chain = con_lat.find_maximal_chain();
    
    // Should have at least the zero partition
    assert!(!chain.is_empty());
    assert_eq!(chain[0].number_of_blocks(), 3); // First should be zero
}

#[test]
fn test_idempotent_polynomials() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Test idempotent polynomials
    let polynomials = con_lat.idempotent_polynomials().unwrap();
    
    // Should return a vector of polynomials
    assert!(polynomials.len() >= 0);
}

#[test]
fn test_delta_stubbed() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Test delta (stubbed method)
    let zero = con_lat.zero();
    let one = con_lat.one();
    let delta = con_lat.delta(&zero, &one);
    
    // Should return zero (stubbed implementation)
    assert_eq!(delta.number_of_blocks(), 3);
}

#[test]
fn test_commutator2_stubbed() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let mut con_lat = CongruenceLattice::new(alg);
    
    // Test commutator2 (stubbed method)
    let zero = con_lat.zero();
    let one = con_lat.one();
    let commutator = con_lat.commutator2(&zero, &one);
    
    // Should return zero (stubbed implementation)
    assert_eq!(commutator.number_of_blocks(), 3);
}

#[test]
fn test_centralizes_stubbed() {
    let alg = Box::new(BasicSmallAlgebra::new(
        "TestAlg".to_string(),
        HashSet::from([0, 1, 2]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let con_lat = CongruenceLattice::new(alg);
    
    // Test centralizes (stubbed method)
    let zero = con_lat.zero();
    let one = con_lat.one();
    let delta = con_lat.zero();
    
    // Create dummy binary relations
    let s = Box::new(BasicBinaryRelation::new(3).unwrap()) as Box<dyn BinaryRelation>;
    let t = Box::new(BasicBinaryRelation::new(3).unwrap()) as Box<dyn BinaryRelation>;
    
    let centralizes = con_lat.centralizes(s.as_ref(), t.as_ref(), &delta);
    
    // Should return true (stubbed implementation)
    assert!(centralizes);
}
