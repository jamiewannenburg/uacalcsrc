//! Resource limit smoke tests (Rust).

use std::collections::HashSet;

use uacalc::alg::op::operations::make_int_operation_str;
use uacalc::resource::{
    checkpoint_force, request_cancel, reset_all_limits, set_element_limit, set_memory_limit,
    try_charge_element, ComputationScope, UaError,
};

#[test]
fn memory_limit_on_make_int_operation() {
    reset_all_limits();
    set_memory_limit(Some(64));
    let err = make_int_operation_str("t", 2, 200, vec![0; 200 * 200]).unwrap_err();
    assert!(matches!(err, UaError::Memory { .. }));
    reset_all_limits();
    assert!(make_int_operation_str("t", 2, 2, vec![0, 1, 1, 0]).is_ok());
}

#[test]
fn element_limit_via_try_charge_element() {
    reset_all_limits();
    set_element_limit(Some(1));
    let _scope = ComputationScope::enter();
    assert!(try_charge_element().is_ok());
    assert!(matches!(
        try_charge_element(),
        Err(UaError::ElementLimit { .. })
    ));
    reset_all_limits();
}

#[test]
fn cancel_is_consumed_at_checkpoint() {
    reset_all_limits();
    request_cancel();
    assert!(matches!(checkpoint_force(), Err(UaError::Interrupted)));
    reset_all_limits();
    assert!(checkpoint_force().is_ok());
}