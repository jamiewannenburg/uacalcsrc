//! Polymorphism search resource limits.

use uacalc::alg::conlat::partition::Partition;
use uacalc::resource::{reset_all_limits, set_element_limit, set_memory_limit, ComputationScope};

#[test]
fn unary_polymorphisms_element_limit() {
    reset_all_limits();
    let pars = vec![Partition::zero(3), Partition::one(3)];
    set_element_limit(Some(4));
    let _scope = ComputationScope::enter();
    let err = Partition::unary_polymorphisms(&pars).unwrap_err();
    reset_all_limits();
    assert!(
        err.contains("element limit") || err.contains("ElementLimit"),
        "got: {err}"
    );
    let full = Partition::unary_polymorphisms(&pars).expect("recovery");
    assert!(!full.is_empty());
}

#[test]
fn binary_polymorphisms_memory_limit() {
    reset_all_limits();
    let pars = vec![Partition::zero(4), Partition::one(4)];
    set_memory_limit(Some(32));
    let _scope = ComputationScope::enter();
    let err = Partition::binary_polymorphisms(&pars, None).unwrap_err();
    reset_all_limits();
    assert!(
        err.contains("memory") || err.contains("Memory"),
        "got: {err}"
    );
}