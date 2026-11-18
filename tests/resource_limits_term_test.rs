//! Term interpretation table resource limits.

use std::path::Path;
use std::sync::Arc;

use uacalc::alg::{BasicAlgebra, SmallAlgebra};
use uacalc::alg::op::ops::make_int_operations;
use uacalc::io::algebra_io::read_algebra_file;
use uacalc::resource::{reset_all_limits, set_memory_limit, ComputationScope, UaError};
use uacalc::terms::{Term, VariableImp};

#[test]
fn term_interpretation_hits_memory_limit() {
    reset_all_limits();
    let m4 = read_algebra_file(Path::new("resources/algebras/m4.ua")).expect("m4.ua");
    let int_ops = make_int_operations(m4.operations()).expect("ops");
    let card = m4.cardinality();
    let basic = BasicAlgebra::new("m4".into(), (0..card).map(|i| i as i32).collect(), int_ops);
    let alg: Arc<dyn SmallAlgebra<UniverseItem = i32>> = Arc::new(basic);
    let term = VariableImp::new("x0");
    let varlist = vec!["x0".to_string(), "x1".to_string()];

    set_memory_limit(Some(32));
    let err = term.interpretation(alg, &varlist, true).unwrap_err();
    reset_all_limits();
    assert!(
        err.contains("memory") || err.contains("limit"),
        "expected limit error, got: {err}"
    );
}

#[test]
fn term_interpretation_succeeds_after_reset() {
    reset_all_limits();
    let m4 = read_algebra_file(Path::new("resources/algebras/m4.ua")).expect("m4.ua");
    let int_ops = make_int_operations(m4.operations()).expect("ops");
    let card = m4.cardinality();
    let basic = BasicAlgebra::new("m4".into(), (0..card).map(|i| i as i32).collect(), int_ops);
    let alg: Arc<dyn SmallAlgebra<UniverseItem = i32>> = Arc::new(basic);
    let term = VariableImp::new("x0");
    let varlist = vec!["x0".to_string(), "x1".to_string()];

    set_memory_limit(Some(32));
    assert!(term.interpretation(alg.clone(), &varlist, true).is_err());
    reset_all_limits();
    assert!(term.interpretation(alg, &varlist, true).is_ok());
}