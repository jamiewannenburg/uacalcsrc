//! Jython Subalgebra.sub() parity: the lattice is of the subalgebra, not the superalgebra.

use std::path::Path;
use uacalc::alg::{Algebra, Subalgebra};
use uacalc::io::algebra_io::read_algebra_file;

#[test]
fn singleton_subalgebra_of_cyclic2_has_two_subuniverses() {
    let alg_file = Path::new("resources/algebras/cyclic2.ua");
    if !alg_file.exists() {
        eprintln!("Skipping test: {} not found", alg_file.display());
        return;
    }

    let base = read_algebra_file(alg_file).expect("Failed to load cyclic2.ua");
    let mut sub = Subalgebra::new_safe("S0".to_string(), base, vec![0])
        .expect("Failed to construct Subalgebra({0})");

    assert_eq!(sub.cardinality(), 1);
    let mut lat = sub.sub().clone();
    assert_eq!(lat.universe_mut().len(), 2);
}
