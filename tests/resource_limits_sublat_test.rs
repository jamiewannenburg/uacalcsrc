//! Resource limits on SubalgebraLattice and partition join closures.

use std::path::Path;
use std::sync::mpsc::sync_channel;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use uacalc::alg::conlat::partition::Partition;
use uacalc::alg::conlat::CongruenceLattice;
use uacalc::alg::sublat::SubalgebraLattice;
use uacalc::io::algebra_io::read_algebra_file;
use uacalc::resource::{
    checkpoint_force, request_cancel, reset_all_limits, set_element_limit, set_memory_limit,
    set_time_limit, ComputationScope, UaError,
};
use serial_test::serial;

const STRESS_REPEATS_UNBOUNDED: usize = usize::MAX / 4;
const CANCEL_WAKE_MS: u64 = 150;
const GENEROUS_TEST_BOUND: Duration = Duration::from_secs(10);
const M4_SUB_CARD: usize = 31;

fn m4_sub_lat() -> SubalgebraLattice<i32> {
    let alg = read_algebra_file(Path::new("resources/algebras/m4.ua")).expect("m4.ua");
    SubalgebraLattice::new_safe(alg).expect("sub lattice")
}

fn lyndon_con_lat() -> CongruenceLattice<i32> {
    let alg = read_algebra_file(Path::new("resources/algebras/lyndon.ua")).expect("lyndon.ua");
    CongruenceLattice::new(alg)
}

#[test]
fn sublattice_memory_limit_universe() {
    reset_all_limits();
    let mut lat = m4_sub_lat();
    set_memory_limit(Some(64));
    assert!(matches!(
        lat.cardinality_checked(),
        Err(UaError::Memory { .. })
    ));
    reset_all_limits();
    assert_eq!(lat.cardinality_checked().unwrap(), M4_SUB_CARD);
}

#[test]
fn sublattice_element_limit_universe() {
    reset_all_limits();
    let mut lat = m4_sub_lat();
    set_element_limit(Some(4));
    let _scope = ComputationScope::enter();
    assert!(matches!(
        lat.cardinality_checked(),
        Err(UaError::ElementLimit { .. })
    ));
    reset_all_limits();
    assert_eq!(lat.cardinality_checked().unwrap(), M4_SUB_CARD);
}

#[test]
#[serial]
fn sublattice_time_limit_universe() {
    reset_all_limits();
    let mut lat = m4_sub_lat();
    set_time_limit(Some(Duration::ZERO));
    assert!(matches!(lat.cardinality_checked(), Err(UaError::TimeLimit)));
    reset_all_limits();
    assert_eq!(lat.cardinality_checked().unwrap(), M4_SUB_CARD);
}

#[test]
#[serial]
fn sublattice_cancel_during_stress_universe() {
    reset_all_limits();
    let (ready_tx, ready_rx) = sync_channel::<()>(0);
    let outcome: Arc<Mutex<Option<Result<usize, UaError>>>> = Arc::new(Mutex::new(None));
    let outcome_worker = outcome.clone();
    let handle = thread::spawn(move || {
        let mut lat = m4_sub_lat();
        ready_tx.send(()).unwrap();
        outcome_worker
            .lock()
            .unwrap()
            .replace(lat.universe_stress(STRESS_REPEATS_UNBOUNDED));
    });
    ready_rx.recv().unwrap();
    thread::sleep(Duration::from_millis(CANCEL_WAKE_MS));
    request_cancel();
    let t0 = Instant::now();
    handle.join().unwrap();
    let run = outcome.lock().unwrap().take().unwrap();
    reset_all_limits();
    assert!(matches!(run, Err(UaError::Interrupted)));
    assert!(t0.elapsed() < GENEROUS_TEST_BOUND);
    assert_eq!(m4_sub_lat().cardinality_checked().unwrap(), M4_SUB_CARD);
}

#[test]
fn con_lattice_memory_limit_universe_lyndon() {
    reset_all_limits();
    let mut con = lyndon_con_lat();
    set_memory_limit(Some(128));
    assert!(matches!(
        con.con_cardinality_checked(),
        Err(UaError::Memory { .. })
    ));
    reset_all_limits();
    let card = con.con_cardinality_checked().unwrap();
    assert!(card >= 10);
    assert_eq!(con.con_cardinality_checked().unwrap(), card);
}

#[test]
fn con_lattice_element_limit_universe_lyndon_recovery() {
    reset_all_limits();
    let expected = {
        let mut con = lyndon_con_lat();
        con.con_cardinality_checked().unwrap()
    };
    assert!(expected >= 10);
    reset_all_limits();
    set_element_limit(Some(4));
    let _scope = ComputationScope::enter();
    let mut con = lyndon_con_lat();
    assert!(matches!(
        con.con_cardinality_checked(),
        Err(UaError::ElementLimit { .. })
    ));
    assert!(!con.universe_found());
    reset_all_limits();
    let mut con = lyndon_con_lat();
    assert_eq!(con.con_cardinality_checked().unwrap(), expected);
}

#[test]
fn partition_join_closure_respects_memory_limit() {
    reset_all_limits();
    let p = Partition::from_string("|0 1|2|").unwrap();
    let q = Partition::from_string("|0|1 2|").unwrap();
    let parts = [p, q];
    set_memory_limit(Some(48));
    let _scope = ComputationScope::enter();
    let err = Partition::join_closure_checked(&parts).unwrap_err();
    assert!(matches!(err, UaError::Memory { .. }));
    reset_all_limits();
    assert!(Partition::join_closure_checked(&parts).is_ok());
}

#[test]
#[serial]
fn sublattice_no_stale_cache_after_limit_failure() {
    reset_all_limits();
    let mut lat = m4_sub_lat();
    set_memory_limit(Some(64));
    let _ = lat.cardinality_checked();
    assert!(!lat.universe_found());
    reset_all_limits();
    assert_eq!(lat.cardinality_checked().unwrap(), M4_SUB_CARD);
    assert!(lat.universe_found());
}

#[test]
#[serial]
fn cancel_consumed_at_checkpoint_force() {
    reset_all_limits();
    request_cancel();
    assert!(matches!(checkpoint_force(), Err(UaError::Interrupted)));
    reset_all_limits();
}