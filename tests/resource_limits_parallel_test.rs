//! Parallel closer resource limits and shared budget.

use std::collections::HashSet;
use std::path::Path;
use std::sync::mpsc::sync_channel;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use serial_test::serial;
use uacalc::alg::op::ops::make_int_operations;
use uacalc::alg::{BasicAlgebra, BigProductAlgebra, Closer, SmallAlgebra};
use uacalc::io::algebra_io::read_algebra_file;
use uacalc::resource::{test_isolation_guard, 
    request_cancel, reset_all_limits, set_memory_limit, ComputationScope, UaError,
};
use uacalc::util::int_array::IntArray;

const HEAVY_POWER: usize = 5;
const CANCEL_WAKE_MS: u64 = 150;
const GENEROUS_TEST_BOUND: Duration = Duration::from_secs(10);

fn heavy_m4_closer_with_term_map() -> Closer<i32> {
    let m4 = read_algebra_file(Path::new("resources/algebras/m4.ua")).expect("m4.ua");
    let int_ops = make_int_operations(m4.operations()).expect("int ops");
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
    let mut closer = Closer::new_safe(alg, gens).unwrap();
    closer.setup_term_map();
    closer.set_suppress_output(true);
    closer
}

#[test]
#[serial]
fn parallel_closer_memory_limit() {
    let _resource_test_guard = test_isolation_guard();
    reset_all_limits();
    let mut closer = heavy_m4_closer_with_term_map();
    set_memory_limit(Some(64));
    let err = closer.sg_close_parallel();
    reset_all_limits();
    assert!(matches!(err, Err(UaError::Memory { .. }) | Err(UaError::ElementLimit { .. })));
    let ans = heavy_m4_closer_with_term_map()
        .sg_close_parallel()
        .expect("after reset");
    assert!(!ans.is_empty());
}

#[test]
#[serial]
fn parallel_closer_cancel_from_other_thread() {
    let _resource_test_guard = test_isolation_guard();
    reset_all_limits();
    let (ready_tx, ready_rx) = sync_channel::<()>(0);
    let outcome: Arc<Mutex<Option<Result<Vec<IntArray>, UaError>>>> = Arc::new(Mutex::new(None));
    let outcome_worker = outcome.clone();
    let handle = thread::spawn(move || {
        ready_tx.send(()).unwrap();
        let mut last = Ok(Vec::new());
        loop {
            let mut closer = heavy_m4_closer_with_term_map();
            match closer.sg_close_parallel() {
                Err(UaError::Interrupted) => {
                    last = Err(UaError::Interrupted);
                    break;
                }
                other => {
                    last = other;
                }
            }
        }
        outcome_worker.lock().unwrap().replace(last);
    });
    ready_rx.recv().unwrap();
    request_cancel();
    let cancel_start = Instant::now();
    handle.join().unwrap();
    let interrupted = cancel_start.elapsed();
    let run = outcome.lock().unwrap().take().unwrap();
    reset_all_limits();
    assert!(matches!(run, Err(UaError::Interrupted)));
    assert!(interrupted < GENEROUS_TEST_BOUND);
    heavy_m4_closer_with_term_map()
        .sg_close_parallel()
        .expect("recovery");
}