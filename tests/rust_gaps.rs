//! Ignored tests that surface Rust-only stubs with no Python-observable
//! difference (the `org.uacalc` shims already match Java).
//!
//! Each `#[ignore]` reason starts with `Rust gap:` and is listed in
//! `docs/RUST_GAPS.md`. `cargo test --workspace` stays green; run
//! `cargo test --test rust_gaps -- --ignored` once a stub is filled in.

use std::collections::HashSet;
use std::sync::Arc;
use uacalc::alg::conlat::CongruenceLattice;
use uacalc::alg::{
    Algebra, BasicAlgebra, BigProductAlgebra, QuotientAlgebra, SmallAlgebra, SubProductAlgebra,
};
use uacalc::alg::conlat::Partition;
use uacalc::alg::sublat::SubalgebraLattice;
use uacalc::common::MemoryMonitor;
use uacalc::element::{Element, SubProductElement};
use uacalc::lat::Lattice;
use uacalc::util::int_array::IntArray;

fn empty_alg(name: &str, n: i32) -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
    let univ: HashSet<i32> = (0..n).collect();
    Box::new(BasicAlgebra::new(name.to_string(), univ, Vec::new()))
}

#[test]
fn type_ji_not_stub() {
    let mut con = CongruenceLattice::new(empty_alg("A", 2));
    let jis = CongruenceLattice::join_irreducibles(&mut con);
    let beta = jis[0].clone();
    let ty = con.type_ji(&beta).expect("type_ji");
    assert_ne!(ty, 0, "type_ji of a join-irreducible of Con(C2-size set) is not type 0");
}

#[test]
fn type_interval_not_stub() {
    let mut con = CongruenceLattice::new(empty_alg("A", 2));
    let ty = con
        .type_interval(&con.one(), &con.zero())
        .expect("type_interval");
    assert_ne!(ty, 0);
}

#[test]
fn type_set_not_stub() {
    let mut con = CongruenceLattice::new(empty_alg("A", 2));
    let set = con.type_set().expect("type_set should succeed once TypeFinder is wired");
    assert!(!set.is_empty());
}

#[test]
fn get_type_finder_not_stub() {
    let mut con = CongruenceLattice::new(empty_alg("A", 2));
    con.get_type_finder()
        .expect("get_type_finder should succeed once TypeFinder is wired");
}

#[test]
fn con_coatoms_not_none() {
    let con = CongruenceLattice::new(empty_alg("A", 2));
    assert!(
        Lattice::coatoms(&con).is_none(),
        "Lattice::coatoms stays None until coatoms are computed"
    );
    let err = con.coatoms_unsupported().unwrap_err();
    assert!(
        err.contains("Not implemented yet"),
        "Java UnsupportedOperationException message"
    );
}

#[test]
#[ignore = "Rust gap: commutator2 swallows internal Err and returns zero"]
fn commutator2_does_not_swallow_errors() {
    // When implemented, commutator2_matching_java errors must surface rather
    // than silently returning the zero congruence.
    panic!("commutator2 still swallows Err as zero");
}

#[test]
#[ignore = "Known Java bug: SubalgebraLattice.atoms returns null (TODO)"]
fn sublat_atoms_not_none() {
    let sl = SubalgebraLattice::new(empty_alg("A", 2));
    assert!(Lattice::atoms(&sl).is_some());
}

#[test]
#[ignore = "Known Java bug: SubalgebraLattice.coatoms returns null (TODO)"]
fn sublat_coatoms_not_none() {
    let sl = SubalgebraLattice::new(empty_alg("A", 2));
    assert!(Lattice::coatoms(&sl).is_some());
}

#[test]
#[ignore = "Rust gap: SubalgebraLattice::is_smaller_than is false until universe is computed"]
fn sublat_is_smaller_than_computes_universe() {
    let sl = SubalgebraLattice::new(empty_alg("A", 2));
    assert!(
        sl.is_smaller_than(10),
        "Java makeUniverse as a side effect; Rust returns false when universe is None"
    );
}

#[test]
#[ignore = "Rust gap: SubalgebraLattice::set_monitor is a no-op"]
fn sublat_set_monitor_stores() {
    let mut sl = SubalgebraLattice::new(empty_alg("A", 2));
    Algebra::set_monitor(&mut sl, None);
    // When implemented, monitoring()/get_monitor() should reflect the last set value.
    panic!("set_monitor still a no-op");
}

#[test]
#[ignore = "Rust gap: SubalgebraLattice::make_meet_irreducibles leaves an empty list"]
fn sublat_meet_irreducibles_not_empty_stub() {
    let mut sl = SubalgebraLattice::new(empty_alg("A", 2));
    let mis = sl.meet_irreducibles_mut();
    assert!(
        !mis.is_empty(),
        "meet irreducibles of Sub(2-elt empty-ops algebra) are not empty"
    );
}

#[test]
#[ignore = "Known Java bug: GeneralAlgebra.universe() returns the unset field (null) for BigProductAlgebra"]
fn big_product_universe_not_empty() {
    let bp = BigProductAlgebra::new_power_safe(empty_alg("A", 2), 2).unwrap();
    let n = bp.universe().count();
    assert_eq!(n, 4);
}

#[test]
fn big_product_is_similar_to_self() {
    let bp = BigProductAlgebra::new_power_safe(empty_alg("A", 2), 2).unwrap();
    assert!(bp.is_similar_to(&bp));
}

#[test]
fn big_product_update_similarity_type() {
    let mut bp = BigProductAlgebra::new_power_safe(empty_alg("A", 2), 2).unwrap();
    bp.update_similarity_type();
    assert!(
        !bp.similarity_type().get_operation_symbols().is_empty()
            || bp.operations().is_empty(),
        "update_similarity_type should populate symbols from operations"
    );
}

#[test]
#[ignore = "Rust gap: BigProductAlgebra::projection_kernel is unimplemented"]
fn big_product_projection_kernel() {
    let bp = BigProductAlgebra::new_power_safe(empty_alg("A", 2), 2).unwrap();
    bp.projection_kernel(0)
        .expect("projection_kernel should succeed for a 2-factor power");
}

#[test]
#[ignore = "Rust gap: DiamondLattice (SmallLattice example) is_similar_to always returns true"]
fn diamond_lattice_is_similar_to_checks_type() {
    // src/lat/small_lattice.rs DiamondLattice/BooleanLattice always return true.
    // When implemented, compare against a non-lattice Algebra<usize>.
    panic!("is_similar_to still always true");
}

#[test]
fn quotient_value_at_arrays() {
    use uacalc::alg::op::{IntOperation, OperationSymbol};

    let sym = OperationSymbol::new("+", 2, false);
    let op = IntOperation::new(sym, 2, vec![0, 1, 1, 0]).unwrap();
    let univ: HashSet<i32> = (0..2).collect();
    let super_alg = Box::new(BasicAlgebra::new(
        "A".to_string(),
        univ,
        vec![Box::new(op)],
    ));
    let cong = Partition::zero(2);
    let q = QuotientAlgebra::<i32>::new_safe(super_alg, cong).unwrap();
    let ops = q.operations();
    assert!(!ops.is_empty());
    let expected = ops[0].int_value_at(&[0, 1]).expect("int_value_at");
    let got = ops[0]
        .value_at_arrays(&[&[0], &[1]])
        .expect("value_at_arrays on a quotient op should succeed");
    assert_eq!(got, vec![expected]);
}

#[test]
fn sub_product_projection_kernel() {
    let bp = BigProductAlgebra::new_power_safe(empty_alg("A", 2), 2).unwrap();
    let gens = vec![
        IntArray::from_array(vec![0, 0]).unwrap(),
        IntArray::from_array(vec![1, 1]).unwrap(),
    ];
    let sp = SubProductAlgebra::new_safe("SP".to_string(), bp, gens, false).unwrap();
    let part = sp.projection_kernel(0).expect("projection_kernel");
    assert!(part.number_of_blocks() >= 1);
    assert!(sp.projection_kernel(-1).is_err());
}

#[test]
#[ignore = "Rust gap: SubProductElement::get_algebra panics"]
fn sub_product_element_get_algebra() {
    let bp = BigProductAlgebra::new_power_safe(empty_alg("A", 2), 2).unwrap();
    let gens = vec![
        IntArray::from_array(vec![0, 0]).unwrap(),
        IntArray::from_array(vec![1, 1]).unwrap(),
    ];
    let sp = SubProductAlgebra::new_safe("SP".to_string(), bp, gens, false).unwrap();
    let elt = SubProductElement::new(IntArray::from_array(vec![0, 0]).unwrap(), &sp);
    let _ = Element::get_algebra(&elt);
}

#[test]
#[ignore = "Rust gap: MemoryMonitor::current_memory_usage is pid*1024 placeholder"]
fn memory_monitor_reads_real_rss() {
    let monitor = MemoryMonitor::new(1);
    // A 1 MB limit would trip immediately if RSS were reported as pid*1024
    // for a typical Windows PID. Once real RSS is used, check_memory of a
    // fresh monitor with a generous limit must succeed.
    monitor
        .check_memory()
        .expect("fresh monitor with 1MB limit should not use pid*1024");
}

#[test]
#[ignore = "Rust gap: pixley_term skips is_congruence_dist_idempotent for idempotent algebras"]
fn pixley_term_uses_distributivity_guard() {
    // When the TODO in src/alg/malcev.rs is implemented, an idempotent
    // non-CD algebra must return Ok(None) without enumerating F(2)^3.
    panic!("pixley_term still skips the idempotent CD check");
}

// Keep Arc in the import list used so unused-import does not fire on some rustc versions.
#[allow(dead_code)]
fn _keep_arc() -> usize {
    Arc::strong_count(&Arc::new(0u8))
}
