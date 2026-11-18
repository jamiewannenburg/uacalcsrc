//! Phase 4 resource limit sites (lazy tables, random ops, close).

use std::collections::HashSet;
use std::path::Path;

use uacalc::alg::op::operations::{make_int_operation_str, make_random_operations_with_seed};
use uacalc::alg::op::{OperationSymbol, SimilarityType};
use uacalc::alg::{Algebra, BasicAlgebra, BigProductAlgebra, Closer, SmallAlgebra};
use uacalc::io::algebra_io::read_algebra_file;
use uacalc::resource::{reset_all_limits, set_memory_limit, ComputationScope, UaError};
use uacalc::util::int_array::IntArray;

#[test]
fn lazy_product_make_table_memory_limit_and_recovery() {
    reset_all_limits();
    let path = Path::new("resources/algebras/m4.ua");
    let m4 = read_algebra_file(path).expect("m4.ua");
    let product = uacalc::alg::ProductAlgebra::new_safe(
        "m4^2".into(),
        vec![m4.clone_box(), m4.clone_box()],
    )
    .expect("product");
    let sym = product.operations()[0].symbol().clone();
    let mut op = product
        .get_operation_ref(&sym)
        .expect("op")
        .clone_box();
    set_memory_limit(Some(64));
    let _scope = ComputationScope::enter();
    assert!(op.make_table().is_err());
    assert!(op.get_table().is_none());
    reset_all_limits();
    op.make_table().expect("recovery build");
    assert!(op.get_table().is_some());
}

#[test]
fn random_operations_batch_memory_limit() {
    reset_all_limits();
    let sim = SimilarityType::new(vec![
        OperationSymbol::new_safe("f", 2, false).unwrap(),
        OperationSymbol::new_safe("g", 2, false).unwrap(),
    ]);
    set_memory_limit(Some(128));
    let _scope = ComputationScope::enter();
    let err = make_random_operations_with_seed(8, &sim, Some(1)).unwrap_err();
    assert!(err.contains("memory limit") || err.contains("Memory"));
    reset_all_limits();
    let ops = make_random_operations_with_seed(2, &sim, Some(1)).expect("small");
    assert_eq!(ops.len(), 2);
}

#[test]
fn closer_close_power_under_scope() {
    reset_all_limits();
    let path = Path::new("resources/algebras/m4.ua");
    let m4 = read_algebra_file(path).expect("m4");
    let ops = m4.operations();
    let int_ops = uacalc::alg::op::ops::make_int_operations(ops).expect("int ops");
    let card = m4.cardinality();
    let universe: HashSet<i32> = (0..card).map(|i| i as i32).collect();
    let basic = BasicAlgebra::new("m4".into(), universe, int_ops);
    let boxed: Box<dyn SmallAlgebra<UniverseItem = i32>> = Box::new(basic);
    let alg = std::sync::Arc::new(BigProductAlgebra::new_power_safe(boxed, 2).unwrap());
    let gens = vec![IntArray::from_array(vec![0, 0]).unwrap()];
    let mut closer = Closer::new_safe(alg, gens).unwrap();
    let _scope = ComputationScope::enter();
    let ans = closer.close_checked().expect("close");
    assert_eq!(ans.len(), 1);
    reset_all_limits();
}

#[test]
fn make_int_operation_recovery_after_table_limit() {
    reset_all_limits();
    set_memory_limit(Some(100));
    let _scope = ComputationScope::enter();
    let err = make_int_operation_str("h", 2, 50, vec![0; 2500]).unwrap_err();
    assert!(matches!(err, UaError::Memory { .. }));
    reset_all_limits();
    assert!(make_int_operation_str("h", 2, 2, vec![0, 1, 1, 0]).is_ok());
}