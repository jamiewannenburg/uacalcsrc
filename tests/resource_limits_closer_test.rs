//! Smoke test: closure entry runs under a computation scope.

use std::collections::HashSet;
use std::sync::Arc;
use uacalc::alg::op::operations::make_int_operation_str;
use uacalc::alg::{BasicAlgebra, BigProductAlgebra, Closer, SmallAlgebra};
use uacalc::resource::{clear_cancel, set_memory_limit, set_time_limit};
use uacalc::util::int_array::IntArray;

#[test]
fn closure_succeeds_with_limits_unset() {
    clear_cancel();
    set_memory_limit(None);
    set_time_limit(None);
    let op = make_int_operation_str("m", 2, 2, vec![0, 1, 1, 0]).unwrap();
    let c2 = BasicAlgebra::new("C2".into(), HashSet::from([0, 1]), vec![op]);
    let boxed: Box<dyn SmallAlgebra<UniverseItem = i32>> = Box::new(c2);
    let alg = Arc::new(BigProductAlgebra::new_power_safe(boxed, 2).unwrap());
    let gens = vec![
        IntArray::from_array(vec![0, 0]).unwrap(),
        IntArray::from_array(vec![0, 1]).unwrap(),
    ];
    let mut closer = Closer::new_safe(alg, gens).unwrap();
    assert!(closer.sg_close().is_ok());
}