//! Resource limit smoke tests (Rust).

use std::collections::HashSet;
use std::path::Path;
use std::sync::mpsc::sync_channel;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use uacalc::alg::op::operations::make_int_operation_str;
use uacalc::alg::{BasicAlgebra, BigProductAlgebra, Closer, SmallAlgebra};
use uacalc::io::algebra_io::read_algebra_file;
use uacalc::resource::{
    checkpoint_force, request_cancel, reset_all_limits, set_element_limit, set_memory_limit,
    set_time_limit, try_charge_element, ComputationScope, UaError,
};
use uacalc::util::int_array::IntArray;
use serial_test::serial;

const HEAVY_POWER: usize = 5;
/// Effectively unbounded for CI: uncancelled run would exceed any test timeout.
const STRESS_REPEATS_UNBOUNDED: usize = usize::MAX / 4;
const CANCEL_WAKE_MS: u64 = 150;
const GENEROUS_TEST_BOUND: Duration = Duration::from_secs(10);

fn heavy_m4_closer() -> Closer<i32> {
    let path = Path::new("resources/algebras/m4.ua");
    let m4 = read_algebra_file(path).expect("m4.ua");
    let ops = m4.operations();
    let int_ops = uacalc::alg::op::ops::make_int_operations(ops).expect("int ops");
    let card = m4.cardinality();
    let universe: HashSet<i32> = (0..card).map(|i| i as i32).collect();
    let basic = BasicAlgebra::new("m4".into(), universe, int_ops);
    let boxed: Box<dyn SmallAlgebra<UniverseItem = i32>> = Box::new(basic);
    let alg = Arc::new(BigProductAlgebra::new_power_safe(boxed, HEAVY_POWER).unwrap());
    let gens = vec![
        IntArray::from_array(vec![0, 0, 1, 0, 0]).unwrap(),
        IntArray::from_array(vec![1, 1, 0, 1, 0]).unwrap(),
        IntArray::from_array(vec![2, 1, 2, 0, 1]).unwrap(),
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
    let outcome: Arc<Mutex<Option<Result<(), UaError>>>> = Arc::new(Mutex::new(None));
    let outcome_worker = outcome.clone();
    let handle = thread::spawn(move || {
        let mut closer = heavy_m4_closer();
        ready_tx.send(()).unwrap();
        outcome_worker.lock().unwrap().replace(
            closer.sg_close_power_stress(STRESS_REPEATS_UNBOUNDED),
        );
    });
    ready_rx.recv().unwrap();
    thread::sleep(Duration::from_millis(CANCEL_WAKE_MS));
    request_cancel();
    let cancel_start = Instant::now();
    handle.join().unwrap();
    let interrupted = cancel_start.elapsed();
    let run = outcome.lock().unwrap().take().unwrap();
    reset_all_limits();
    assert!(matches!(run, Err(UaError::Interrupted)));
    assert!(interrupted < GENEROUS_TEST_BOUND);
    heavy_m4_closer()
        .sg_close_power_stress(5)
        .expect("after reset");
}

#[test]
#[serial]
fn time_limit_on_sg_close_power() {
    reset_all_limits();
    set_time_limit(Some(Duration::ZERO));
    assert!(matches!(
        heavy_m4_closer().sg_close_power(),
        Err(UaError::TimeLimit)
    ));
    reset_all_limits();
    assert!(heavy_m4_closer().sg_close_power().is_ok());
}

#[test]
#[serial]
fn time_limit_realistic_on_stress_closure() {
    reset_all_limits();
    set_time_limit(Some(Duration::from_millis(200)));
    let start = Instant::now();
    let err = heavy_m4_closer().sg_close_power_stress(STRESS_REPEATS_UNBOUNDED);
    reset_all_limits();
    assert!(matches!(err, Err(UaError::TimeLimit)));
    assert!(start.elapsed() < GENEROUS_TEST_BOUND);
}