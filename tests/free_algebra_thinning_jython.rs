//! Jython FreeAlgebra thinning parity: after thinGens, rebuild the product
//! to `alg ^ gens[0].universeSize()` the way Java FreeAlgebra does.

use std::path::Path;
use uacalc::alg::{Algebra, FreeAlgebra};
use uacalc::io::algebra_io::read_algebra_file;
use uacalc::util::int_array::IntArrayTrait;

#[test]
fn thinned_f1_over_cyclic2_rebuilds_product() {
    let alg_file = Path::new("resources/algebras/cyclic2.ua");
    if !alg_file.exists() {
        eprintln!("Skipping test: {} not found", alg_file.display());
        return;
    }

    let base = read_algebra_file(alg_file).expect("Failed to load cyclic2.ua");
    let f = FreeAlgebra::new_with_thin_safe(base, 1, true, true)
        .expect("Failed to construct thinned FreeAlgebra(c2, 1)");

    assert_eq!(f.cardinality(), 2, "F(1) over C2 has two elements");

    let product = f.get_inner().get_product_algebra();
    assert_eq!(
        product.get_number_of_factors(),
        1,
        "thinned product should have one factor"
    );
    assert_eq!(product.cardinality(), 2);

    let univ: Vec<Vec<i32>> = f
        .universe()
        .map(|ia| ia.as_slice().to_vec())
        .collect();
    assert_eq!(univ, vec![vec![1], vec![0]]);
}
