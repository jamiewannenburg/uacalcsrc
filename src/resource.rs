//! Cooperative per-computation resource limits (phase 1).
//!
//! Thread-local budgets with a global cancel flag. Top-level [`ComputationScope`]
//! resets usage counters; nested scopes share the same budget.

use std::cell::RefCell;
use std::fmt;
use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
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
/// Set when any thread has a non-None memory/element/time limit (fast path for overhead-free runs).
static LIMITS_CONFIGURED: AtomicBool = AtomicBool::new(false);

fn sync_limits_configured() {
    let configured = with_state(|s| {
        s.memory_limit.is_some() || s.element_limit.is_some() || s.time_limit.is_some()
    });
    LIMITS_CONFIGURED.store(configured, Ordering::Release);
}

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
    static SHARED_BUDGET: RefCell<Option<Arc<SharedBudget>>> = RefCell::new(None);
}

/// Per-computation counters shared across parallel worker threads.
#[derive(Debug)]
pub struct SharedBudget {
    memory_used: AtomicU64,
    element_count: AtomicU64,
    checkpoint_counter: AtomicU32,
    memory_limit: Option<u64>,
    element_limit: Option<u64>,
    deadline: Option<Instant>,
}

impl SharedBudget {
    fn from_thread(s: &ThreadState) -> Self {
        Self {
            memory_used: AtomicU64::new(s.memory_used),
            element_count: AtomicU64::new(s.element_count),
            checkpoint_counter: AtomicU32::new(s.checkpoint_counter),
            memory_limit: s.memory_limit,
            element_limit: s.element_limit,
            deadline: s.deadline,
        }
    }

    fn sync_to_thread(&self, s: &mut ThreadState) {
        s.memory_used = self.memory_used.load(Ordering::SeqCst);
        s.element_count = self.element_count.load(Ordering::SeqCst);
        s.checkpoint_counter = self.checkpoint_counter.load(Ordering::SeqCst);
    }

    fn try_charge_shared(&self, bytes: u64) -> Result<(), UaError> {
        let prev = self.memory_used.fetch_add(bytes, Ordering::SeqCst);
        let new_used = prev.saturating_add(bytes);
        if let Some(limit) = self.memory_limit {
            if new_used > limit {
                return Err(UaError::Memory {
                    used: new_used,
                    limit,
                });
            }
        }
        Ok(())
    }

    fn try_charge_element_shared(&self) -> Result<(), UaError> {
        let prev = self.element_count.fetch_add(1, Ordering::SeqCst);
        let new_count = prev.saturating_add(1);
        if let Some(limit) = self.element_limit {
            if new_count > limit {
                return Err(UaError::ElementLimit {
                    count: new_count,
                    limit,
                });
            }
        }
        Ok(())
    }

    fn checkpoint_shared(&self) -> Result<(), UaError> {
        let n = self
            .checkpoint_counter
            .fetch_add(1, Ordering::SeqCst)
            .wrapping_add(1);
        if n % CHECKPOINT_INTERVAL != 0 {
            return Ok(());
        }
        consume_cancel_if_set()?;
        if let Some(deadline) = self.deadline {
            if Instant::now() >= deadline {
                return Err(UaError::TimeLimit);
            }
        }
        let used = self.memory_used.load(Ordering::SeqCst);
        if let Some(limit) = self.memory_limit {
            if used > limit {
                return Err(UaError::Memory {
                    used,
                    limit,
                });
            }
        }
        let count = self.element_count.load(Ordering::SeqCst);
        if let Some(limit) = self.element_limit {
            if count > limit {
                return Err(UaError::ElementLimit {
                    count,
                    limit,
                });
            }
        }
        with_state(|s| maybe_poll_signals(s))
    }

    fn checkpoint_force_shared(&self) -> Result<(), UaError> {
        consume_cancel_if_set()?;
        if let Some(deadline) = self.deadline {
            if Instant::now() >= deadline {
                return Err(UaError::TimeLimit);
            }
        }
        let used = self.memory_used.load(Ordering::SeqCst);
        if let Some(limit) = self.memory_limit {
            if used > limit {
                return Err(UaError::Memory {
                    used,
                    limit,
                });
            }
        }
        let count = self.element_count.load(Ordering::SeqCst);
        if let Some(limit) = self.element_limit {
            if count > limit {
                return Err(UaError::ElementLimit {
                    count,
                    limit,
                });
            }
        }
        with_state(|s| maybe_poll_signals(s))
    }
}

fn shared_budget_ref() -> Option<Arc<SharedBudget>> {
    SHARED_BUDGET.with(|c| c.borrow().clone())
}

/// Fork thread-local usage into a budget shared by parallel workers.
pub fn begin_shared_budget() -> Arc<SharedBudget> {
    let arc = with_state(|s| Arc::new(SharedBudget::from_thread(s)));
    SHARED_BUDGET.with(|c| *c.borrow_mut() = Some(Arc::clone(&arc)));
    arc
}

/// Attach an existing shared budget on a worker thread (no scope reset).
pub fn attach_shared_budget(arc: Arc<SharedBudget>) {
    SHARED_BUDGET.with(|c| *c.borrow_mut() = Some(arc));
}

/// Detach shared budget and merge counters back into thread-local state.
pub fn end_shared_budget() {
    if let Some(arc) = SHARED_BUDGET.with(|c| c.borrow_mut().take()) {
        with_state(|s| arc.sync_to_thread(s));
    }
}

fn with_state<R>(f: impl FnOnce(&mut ThreadState) -> R) -> R {
    TLS.with(|cell| f(&mut cell.borrow_mut()))
}

pub fn set_memory_limit(limit: Option<u64>) {
    with_state(|s| s.memory_limit = limit);
    sync_limits_configured();
}

pub fn set_element_limit(limit: Option<u64>) {
    with_state(|s| s.element_limit = limit);
    sync_limits_configured();
}

pub fn set_time_limit(limit: Option<Duration>) {
    with_state(|s| {
        s.time_limit = limit;
        if limit.is_none() {
            s.deadline = None;
        } else if s.scope_depth == 0 {
            s.deadline = Some(Instant::now() + limit.unwrap());
        }
    });
    // Detach stale parallel budgets left over from limit stress tests.
    if limit.is_none() {
        end_shared_budget();
    }
    sync_limits_configured();
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
    end_shared_budget();
    with_state(|s| {
        s.memory_limit = None;
        s.element_limit = None;
        s.time_limit = None;
        s.deadline = None;
    });
    sync_limits_configured();
}

pub fn cancel_requested() -> bool {
    CANCEL_REQUESTED.load(Ordering::SeqCst)
}

/// True when any thread has configured a cooperative limit (global flag, see [`sync_limits_configured`]).
pub fn limits_configured_globally() -> bool {
    LIMITS_CONFIGURED.load(Ordering::Acquire)
}

/// Enter a computation scope only when a limit is configured (not for cancel alone).
///
/// Cancel and Python signals are still honored via [`checkpoint`] / [`poll_cancel`] on the
/// global cancel flag and signal hook without a scope. Core lattice paths may still enter
/// their own inner scopes.
pub fn maybe_computation_scope() -> Option<ComputationScope> {
    if limits_configured_globally() {
        Some(ComputationScope::enter())
    } else {
        None
    }
}

/// Limit knobs from the thread that schedules `py.allow_threads` work (usually the main thread).
#[derive(Clone, Copy, Debug)]
pub struct WorkerLimitsSnapshot {
    memory_limit: Option<u64>,
    element_limit: Option<u64>,
    time_limit: Option<Duration>,
}

/// Copy configured limits from the current thread before moving closure to a worker thread.
pub fn snapshot_worker_limits() -> WorkerLimitsSnapshot {
    with_state(|s| WorkerLimitsSnapshot {
        memory_limit: s.memory_limit,
        element_limit: s.element_limit,
        time_limit: s.time_limit,
    })
}

fn install_worker_limits(snapshot: WorkerLimitsSnapshot) {
    with_state(|s| {
        s.memory_limit = snapshot.memory_limit;
        s.element_limit = snapshot.element_limit;
        s.time_limit = snapshot.time_limit;
    });
}

/// RAII: install caller limits on a worker thread and optionally open a top-level scope.
pub struct AllowThreadsResourceGuard {
    _scope: Option<ComputationScope>,
}

impl AllowThreadsResourceGuard {
    /// Call at the start of every `py.allow_threads` lattice/closure body.
    pub fn enter() -> Self {
        install_worker_limits(snapshot_worker_limits());
        AllowThreadsResourceGuard {
            _scope: maybe_computation_scope(),
        }
    }
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

/// Entry check: honor cancel/deadline before a heavy computation (no signal poll).
pub fn checkpoint_entry() -> Result<(), UaError> {
    if let Some(shared) = shared_budget_ref() {
        consume_cancel_if_set()?;
        if let Some(deadline) = shared.deadline {
            if Instant::now() >= deadline {
                return Err(UaError::TimeLimit);
            }
        }
        return Ok(());
    }
    with_state(|s| {
        consume_cancel_if_set()?;
        check_deadline(s)?;
        Ok(())
    })
}

/// Cheap cooperative cancel poll (no counter increment, no memory budget scan).
pub fn poll_cancel() -> Result<(), UaError> {
    consume_cancel_if_set()
}

/// Amortized cancel / deadline / budget check (every [`CHECKPOINT_INTERVAL`] calls).
pub fn checkpoint() -> Result<(), UaError> {
    if let Some(shared) = shared_budget_ref() {
        return shared.checkpoint_shared();
    }
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

/// Force a full checkpoint (for tests and explicit polling).
pub fn checkpoint_force() -> Result<(), UaError> {
    if let Some(shared) = shared_budget_ref() {
        return shared.checkpoint_force_shared();
    }
    with_state(|s| {
        consume_cancel_if_set()?;
        check_deadline(s)?;
        check_budget(s)?;
        maybe_poll_signals(s)
    })
}

/// Record `bytes` against the memory budget (limit only; cancel/time at checkpoints).
pub fn try_charge(bytes: u64) -> Result<(), UaError> {
    if let Some(shared) = shared_budget_ref() {
        return shared.try_charge_shared(bytes);
    }
    with_state(|s| {
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
    if let Some(shared) = shared_budget_ref() {
        return shared.try_charge_element_shared();
    }
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

/// RAII: merge shared-budget counters when parallel section ends.
pub struct SharedBudgetGuard {
    _private: (),
}

impl SharedBudgetGuard {
    pub fn attach(arc: Arc<SharedBudget>) -> Self {
        attach_shared_budget(arc);
        SharedBudgetGuard { _private: () }
    }
}

impl Drop for SharedBudgetGuard {
    fn drop(&mut self) {
        SHARED_BUDGET.with(|c| {
            c.borrow_mut().take();
        });
    }
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

/// Estimate for one newly kept subalgebra-lattice element (`BasicSet`).
pub fn charge_kept_subalgebra(encoded_size: usize) -> Result<(), UaError> {
    const BASICSET_OVERHEAD: u64 = 48;
    let bytes = BASICSET_OVERHEAD + (encoded_size as u64).saturating_mul(4);
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

/// Fill an operation table by Horner index (charges up front; checkpoints in the loop).
pub fn build_i32_table_horner<F>(
    set_size: i32,
    arity: usize,
    mut fill: F,
) -> Result<Vec<i32>, UaError>
where
    F: FnMut(&[i32]) -> Result<i32, String>,
{
    use crate::util::horner;
    if arity == 0 {
        let v = fill(&[]).map_err(UaError::from)?;
        let mut table = alloc_i32_table(1, 0)?;
        table[0] = v;
        return Ok(table);
    }
    let mut table = alloc_i32_table(set_size as usize, arity as u32)?;
    for i in 0..table.len() {
        checkpoint()?;
        let args = horner::horner_inv_same_size(i as i32, set_size, arity);
        table[i] = fill(&args).map_err(UaError::from)?;
    }
    Ok(table)
}

/// Charge for a newly stored homomorphism / equation-search map entry.
pub fn charge_homomorphism_entry(slice_len: usize) -> Result<(), UaError> {
    const MAP_ENTRY: u64 = 96;
    let bytes = MAP_ENTRY.saturating_add((slice_len as u64).saturating_mul(4));
    try_charge(bytes)
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
    fn clear_time_limit_clears_stale_deadline() {
        clear_cancel();
        set_time_limit(Some(Duration::from_millis(1)));
        let _scope = ComputationScope::enter();
        thread::sleep(Duration::from_millis(5));
        assert!(matches!(checkpoint_force(), Err(UaError::TimeLimit)));
        drop(_scope);
        set_time_limit(None);
        assert!(checkpoint_entry().is_ok());
        reset_all_limits();
    }

    #[test]
    fn worker_inherits_caller_memory_limit() {
        clear_cancel();
        set_memory_limit(Some(64));
        let snap = snapshot_worker_limits();
        set_memory_limit(None);
        let err = thread::spawn(move || {
            install_worker_limits(snap);
            let _scope = maybe_computation_scope();
            try_charge(128)
        })
        .join()
        .unwrap();
        assert!(matches!(err, Err(UaError::Memory { .. })));
        reset_all_limits();
    }

    #[test]
    fn cancel_without_scope_or_limits_at_checkpoints() {
        clear_cancel();
        reset_all_limits();
        for _ in 0..CHECKPOINT_INTERVAL - 1 {
            checkpoint().unwrap();
        }
        request_cancel();
        assert!(matches!(checkpoint(), Err(UaError::Interrupted)));
        clear_cancel();
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