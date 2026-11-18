//! Cooperative per-computation resource limits (phase 1).
//!
//! Thread-local budgets with a global cancel flag. Top-level [`ComputationScope`]
//! resets usage counters; nested scopes share the same budget.

use std::cell::RefCell;
use std::fmt;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Mutex;
use std::time::{Duration, Instant};

pub const CHECKPOINT_INTERVAL: u32 = 256;

/// Resource / cancellation errors surfaced to callers and Python.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum UaError {
    Message(String),
    Memory { used: u64, limit: u64 },
    Interrupted,
    TimeLimit,
    ElementLimit { count: u64, limit: u64 },
}

impl UaError {
    pub fn message(msg: impl Into<String>) -> Self {
        UaError::Message(msg.into())
    }
}

impl fmt::Display for UaError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            UaError::Message(s) => write!(f, "{s}"),
            UaError::Memory { used, limit } => {
                write!(f, "memory limit exceeded: used {used} bytes, limit {limit} bytes")
            }
            UaError::Interrupted => write!(f, "computation interrupted"),
            UaError::TimeLimit => write!(f, "time limit exceeded"),
            UaError::ElementLimit { count, limit } => {
                write!(
                    f,
                    "element limit exceeded: kept {count} elements, limit {limit}"
                )
            }
        }
    }
}

impl std::error::Error for UaError {}

impl From<String> for UaError {
    fn from(s: String) -> Self {
        UaError::Message(s)
    }
}

/// Lets legacy `Result<_, String>` call sites use `?` after `UaError` APIs.
impl From<UaError> for String {
    fn from(e: UaError) -> Self {
        e.to_string()
    }
}

static CANCEL_REQUESTED: AtomicBool = AtomicBool::new(false);

type SignalHookFn = Box<dyn Fn() -> Result<(), UaError> + Send + Sync>;

static SIGNAL_HOOK: Mutex<Option<SignalHookFn>> = Mutex::new(None);

/// Install a hook (from `uacalc_lib`) that polls Python signals on the main thread.
pub fn set_signal_hook(hook: Option<SignalHookFn>) {
    *SIGNAL_HOOK.lock().unwrap() = hook;
}

struct ThreadState {
    memory_limit: Option<u64>,
    element_limit: Option<u64>,
    time_limit: Option<Duration>,
    memory_used: u64,
    element_count: u64,
    deadline: Option<Instant>,
    scope_depth: u32,
    checkpoint_counter: u32,
    last_signal_check: Option<Instant>,
}

impl ThreadState {
    fn new() -> Self {
        Self {
            memory_limit: None,
            element_limit: None,
            time_limit: None,
            memory_used: 0,
            element_count: 0,
            deadline: None,
            scope_depth: 0,
            checkpoint_counter: 0,
            last_signal_check: None,
        }
    }
}

thread_local! {
    static TLS: RefCell<ThreadState> = RefCell::new(ThreadState::new());
}

fn with_state<R>(f: impl FnOnce(&mut ThreadState) -> R) -> R {
    TLS.with(|cell| f(&mut cell.borrow_mut()))
}

pub fn set_memory_limit(limit: Option<u64>) {
    with_state(|s| s.memory_limit = limit);
}

pub fn set_element_limit(limit: Option<u64>) {
    with_state(|s| s.element_limit = limit);
}

pub fn set_time_limit(limit: Option<Duration>) {
    with_state(|s| s.time_limit = limit);
}

pub fn request_cancel() {
    CANCEL_REQUESTED.store(true, Ordering::SeqCst);
}

pub fn clear_cancel() {
    CANCEL_REQUESTED.store(false, Ordering::SeqCst);
}

/// Reset all limit configuration and cancel flag (for tests).
pub fn reset_all_limits() {
    clear_cancel();
    set_memory_limit(None);
    set_element_limit(None);
    set_time_limit(None);
}

pub fn cancel_requested() -> bool {
    CANCEL_REQUESTED.load(Ordering::SeqCst)
}

/// RAII guard: entering depth 0 resets per-computation counters and deadline.
pub struct ComputationScope {
    _private: (),
}

impl ComputationScope {
    pub fn enter() -> Self {
        with_state(|s| {
            if s.scope_depth == 0 {
                s.memory_used = 0;
                s.element_count = 0;
                s.checkpoint_counter = 0;
                s.last_signal_check = None;
                s.deadline = s
                    .time_limit
                    .map(|d| Instant::now() + d);
            }
            s.scope_depth += 1;
        });
        ComputationScope { _private: () }
    }
}

impl Drop for ComputationScope {
    fn drop(&mut self) {
        with_state(|s| {
            s.scope_depth = s.scope_depth.saturating_sub(1);
        });
    }
}

fn consume_cancel_if_set() -> Result<(), UaError> {
    if CANCEL_REQUESTED.swap(false, Ordering::SeqCst) {
        return Err(UaError::Interrupted);
    }
    Ok(())
}

fn check_deadline(s: &ThreadState) -> Result<(), UaError> {
    if let Some(deadline) = s.deadline {
        if Instant::now() >= deadline {
            return Err(UaError::TimeLimit);
        }
    }
    Ok(())
}

fn check_budget(s: &ThreadState) -> Result<(), UaError> {
    if let Some(limit) = s.memory_limit {
        if s.memory_used > limit {
            return Err(UaError::Memory {
                used: s.memory_used,
                limit,
            });
        }
    }
    if let Some(limit) = s.element_limit {
        if s.element_count > limit {
            return Err(UaError::ElementLimit {
                count: s.element_count,
                limit,
            });
        }
    }
    Ok(())
}

fn maybe_poll_signals(s: &mut ThreadState) -> Result<(), UaError> {
    let now = Instant::now();
    let should = match s.last_signal_check {
        None => true,
        Some(t) => now.duration_since(t) >= Duration::from_millis(50),
    };
    if !should {
        return Ok(());
    }
    s.last_signal_check = Some(now);
    if let Ok(guard) = SIGNAL_HOOK.lock() {
        if let Some(hook) = guard.as_ref() {
            hook()?;
        }
    }
    Ok(())
}

/// Amortized cancel / deadline / budget check (every [`CHECKPOINT_INTERVAL`] calls).
pub fn checkpoint() -> Result<(), UaError> {
    with_state(|s| {
        s.checkpoint_counter = s.checkpoint_counter.wrapping_add(1);
        if s.checkpoint_counter % CHECKPOINT_INTERVAL != 0 {
            return Ok(());
        }
        consume_cancel_if_set()?;
        check_deadline(s)?;
        check_budget(s)?;
        maybe_poll_signals(s)
    })
}

/// Force a full checkpoint (for tests).
pub fn checkpoint_force() -> Result<(), UaError> {
    with_state(|s| {
        consume_cancel_if_set()?;
        check_deadline(s)?;
        check_budget(s)?;
        maybe_poll_signals(s)
    })
}

/// Record `bytes` against the memory budget (checks limit after increment).
pub fn try_charge(bytes: u64) -> Result<(), UaError> {
    with_state(|s| {
        consume_cancel_if_set()?;
        check_deadline(s)?;
        s.memory_used = s.memory_used.saturating_add(bytes);
        if let Some(limit) = s.memory_limit {
            if s.memory_used > limit {
                return Err(UaError::Memory {
                    used: s.memory_used,
                    limit,
                });
            }
        }
        Ok(())
    })
}

pub fn try_charge_element() -> Result<(), UaError> {
    with_state(|s| {
        s.element_count = s.element_count.saturating_add(1);
        if let Some(limit) = s.element_limit {
            if s.element_count > limit {
                return Err(UaError::ElementLimit {
                    count: s.element_count,
                    limit,
                });
            }
        }
        Ok(())
    })
}

/// Estimate for one newly kept closure element (IntArray + HashSet node + vec slot).
pub fn charge_kept_closure_element(slice_len: usize, has_term_map: bool) -> Result<(), UaError> {
    const ARC_AND_VEC: u64 = 32;
    const HASHSET_NODE: u64 = 48;
    const TERM_MAP_SURCHARGE: u64 = 128;
    let mut bytes = ARC_AND_VEC + (slice_len as u64).saturating_mul(4) + HASHSET_NODE;
    if has_term_map {
        bytes = bytes.saturating_add(TERM_MAP_SURCHARGE);
    }
    try_charge(bytes)?;
    try_charge_element()
}

/// Estimate for one newly kept congruence-lattice partition.
pub fn charge_kept_partition(universe_size: usize) -> Result<(), UaError> {
    const PARTITION_OVERHEAD: u64 = 64;
    let bytes = PARTITION_OVERHEAD + (universe_size as u64).saturating_mul(8);
    try_charge(bytes)?;
    try_charge_element()
}

/// Allocate a flat `i32` op table with charging and checked size.
pub fn alloc_i32_table(n: usize, arity: u32) -> Result<Vec<i32>, UaError> {
    let table_size = n
        .checked_pow(arity)
        .ok_or_else(|| UaError::Memory {
            used: u64::MAX,
            limit: 0,
        })?;
    let bytes = (table_size as u64).saturating_mul(4);
    try_charge(bytes)?;
    let mut table = Vec::new();
    table
        .try_reserve_exact(table_size)
        .map_err(|_| UaError::Memory {
            used: bytes,
            limit: u64::MAX,
        })?;
    table.resize(table_size, 0);
    Ok(table)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn per_computation_reset_allows_second_run() {
        clear_cancel();
        set_memory_limit(Some(1000));
        let _s1 = ComputationScope::enter();
        assert!(try_charge(900).is_ok());
        assert!(try_charge(200).is_err());
        drop(_s1);

        let _s2 = ComputationScope::enter();
        assert!(try_charge(900).is_ok());
    }

    #[test]
    fn cancel_from_other_thread() {
        clear_cancel();
        set_memory_limit(None);
        let _scope = ComputationScope::enter();
        let h = thread::spawn(|| {
            thread::sleep(Duration::from_millis(50));
            request_cancel();
        });
        loop {
            if checkpoint_force().is_err() {
                break;
            }
            thread::sleep(Duration::from_millis(5));
        }
        h.join().unwrap();
        assert!(!cancel_requested());
    }

    #[test]
    fn element_limit_enforced() {
        clear_cancel();
        set_element_limit(Some(2));
        let _scope = ComputationScope::enter();
        assert!(try_charge_element().is_ok());
        assert!(try_charge_element().is_ok());
        assert!(try_charge_element().is_err());
    }

    #[test]
    fn time_limit_deadline() {
        clear_cancel();
        set_time_limit(Some(Duration::from_millis(1)));
        let _scope = ComputationScope::enter();
        thread::sleep(Duration::from_millis(5));
        assert!(matches!(checkpoint_force(), Err(UaError::TimeLimit)));
    }

    #[test]
    fn nested_scopes_do_not_reset() {
        clear_cancel();
        set_memory_limit(Some(500));
        let _outer = ComputationScope::enter();
        try_charge(400).unwrap();
        let _inner = ComputationScope::enter();
        assert!(try_charge(200).is_err());
    }
}