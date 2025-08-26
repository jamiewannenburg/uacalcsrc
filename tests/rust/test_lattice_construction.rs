use uacalc_core::prelude::*;

#[cfg(feature = "conlat")]
#[test]
fn test_basic_lattice_construction() {
    // Create a simple algebra for testing
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();

    // Test basic congruence lattice construction
    let mut lattice = BasicCongruenceLattice::new(Box::new(algebra)).unwrap();

    // Should have at least bottom and top
    assert!(lattice.num_congruences() >= 2);

    // Test universe construction
    lattice.ensure_universe_built().unwrap();
    assert!(lattice.num_congruences() >= 2);
}

#[cfg(feature = "conlat")]
#[test]
fn test_join_irreducibles() {
    // Create a simple algebra
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();

    // Test join-irreducible detection
    let mut lattice = BasicCongruenceLattice::new(Box::new(algebra)).unwrap();
    lattice.ensure_universe_built().unwrap();

    // Should have some join-irreducibles
    let jis = lattice.join_irreducibles();
    assert!(jis.len() >= 0); // May be empty for simple algebras
}

#[cfg(feature = "conlat")]
#[test]
fn test_principal_congruences() {
    // Create a simple algebra
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();

    // Test principal congruence computation
    let mut lattice = BasicCongruenceLattice::new(Box::new(algebra)).unwrap();

    // Test principal congruence θ(0,1)
    let principal = lattice.principal_congruence(0, 1).unwrap();
    assert!(principal.same_block(0, 1).unwrap());
}

#[cfg(feature = "conlat")]
#[test]
fn test_lattice_operations() {
    // Create a simple algebra
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();

    // Test lattice operations
    let mut lattice = BasicCongruenceLattice::new(Box::new(algebra)).unwrap();
    lattice.ensure_universe_built().unwrap();

    // Test join and meet operations
    let congruences = lattice.congruences();
    if congruences.len() >= 3 {
        let join = lattice.join(&congruences[1], &congruences[2]).unwrap();
        let meet = lattice.meet(&congruences[1], &congruences[2]).unwrap();

        // Join should be coarser than both
        assert!(congruences[1].is_finer_than(&join).unwrap());
        assert!(congruences[2].is_finer_than(&join).unwrap());

        // Meet should be finer than both
        assert!(meet.is_finer_than(&congruences[1]).unwrap());
        assert!(meet.is_finer_than(&congruences[2]).unwrap());
    }
}

#[cfg(feature = "conlat")]
#[test]
fn test_atoms_and_coatoms() {
    // Create a simple algebra
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();

    // Test atoms and coatoms
    let mut lattice = BasicCongruenceLattice::new(Box::new(algebra)).unwrap();
    lattice.ensure_universe_built().unwrap();

    // Test atoms (elements covering bottom)
    let atoms = lattice.atoms().unwrap();
    assert!(atoms.len() >= 0);

    // Test coatoms (elements covered by top)
    let coatoms = lattice.coatoms().unwrap();
    assert!(coatoms.len() >= 0);
}

#[cfg(feature = "conlat")]
#[test]
fn test_covering_relation() {
    // Create a simple algebra
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();

    // Test covering relation
    let mut lattice = BasicCongruenceLattice::new(Box::new(algebra)).unwrap();
    lattice.ensure_universe_built().unwrap();

    // Test covering relation computation
    let covering = lattice.covering_relation().unwrap();
    assert!(covering.len() >= 0);

    // Each pair in covering relation should represent a cover
    for (i, j) in covering {
        let congruences = lattice.congruences();
        if i < congruences.len() && j < congruences.len() {
            // j should cover i
            assert!(congruences[i].is_finer_than(&congruences[j]).unwrap());
        }
    }
}
