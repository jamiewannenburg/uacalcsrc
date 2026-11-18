//! Resource limit smoke tests (Rust).

use std::collections::HashSet;
use std::sync::mpsc::sync_channel;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use uacalc::alg::op::operations::make_int_operation_str;
use uacalc::alg::{BasicAlgebra, BigProductAlgebra, Closer, SmallAlgebra};
use uacalc::resource::{
    checkpoint_force, request_cancel, reset_all_limits, set_element_limit, set_memory_limit,
    set_time_limit, try_charge_element, ComputationScope, UaError,
};
use uacalc::util::int_array::IntArray;
use serial_test::serial;

fn c2_power_closer(power: usize) -> Closer<i32> {
    let op = make_int_operation_str("m", 2, 2, vec![0, 1, 1, 0]).unwrap();
    let c2 = BasicAlgebra::new("C2".into(), HashSet::from([0, 1]), vec![op]);
    let boxed: Box<dyn SmallAlgebra<UniverseItem = i32>> = Box::new(c2);
    let alg = Arc::new(BigProductAlgebra::new_power_safe(boxed, power).unwrap());
    let gens = vec![
        IntArray::from_array(vec![0_i32; power]).unwrap(),
        IntArray::from_array(vec![1_i32; power]).unwrap(),
    ];
    Closer::new_safe(alg, gens).unwrap()
}

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
#[serial]
fn cancel_is_consumed_at_checkpoint() {
    reset_all_limits();
    request_cancel();
    assert!(matches!(checkpoint_force(), Err(UaError::Interrupted)));
    reset_all_limits();
    assert!(checkpoint_force().is_ok());
}

#[test]
#[serial]
fn cancel_during_sg_close_power_from_other_thread() {
    reset_all_limits();
    let (ready_tx, ready_rx) = sync_channel::<()>(0);
    let (go_tx, go_rx) = sync_channel::<()>(0);
    let outcome: Arc<Mutex<Option<Result<Vec<IntArray>, UaError>>>> = Arc::new(Mutex::new(None));
    let outcome_worker = outcome.clone();
    let handle = thread::spawn(move || {
        let mut closer = c2_power_closer(6);
        ready_tx.send(()).unwrap();
        let _ = go_rx.recv();
        outcome_worker
            .lock()
            .unwrap()
            .replace(closer.sg_close_power());
    });
    ready_rx.recv().unwrap();
    request_cancel();
    go_tx.send(()).unwrap();
    handle.join().unwrap();
    let run = outcome.lock().unwrap().take().unwrap();
    reset_all_limits();
    assert!(matches!(run, Err(UaError::Interrupted)));
    let mut closer = c2_power_closer(6);
    assert!(closer.sg_close_power().is_ok());
}

#[test]
#[serial]
fn time_limit_on_sg_close_power() {
    reset_all_limits();
    set_time_limit(Some(Duration::ZERO));
    let mut closer = c2_power_closer(6);
    assert!(matches!(closer.sg_close_power(), Err(UaError::TimeLimit)));
    reset_all_limits();
    assert!(closer.sg_close_power().is_ok());
}