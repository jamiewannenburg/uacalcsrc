//! Congruence lattice algorithms and data structures
//!
//! This module provides efficient implementations of congruence generation,
//! lattice construction, and principal congruence computation algorithms.

#[cfg(feature = "conlat")]
pub mod cg;

#[cfg(feature = "conlat")]
pub mod lattice_builder;

#[cfg(feature = "conlat")]
pub mod lattice;

#[cfg(feature = "conlat")]
pub mod principal;

#[cfg(feature = "conlat")]
pub use cg::CongruenceGenerator;
#[cfg(feature = "conlat")]
pub use lattice::{BasicCongruenceLattice, BasicLattice, CongruenceLattice, CongruenceLatticeBuilder};
#[cfg(feature = "conlat")]
pub use lattice_builder::LatticeBuilder;

#[cfg(feature = "conlat")]
pub use cg::cg;
#[cfg(feature = "conlat")]
pub use cg::principal_congruence;
#[cfg(feature = "conlat")]
pub use lattice_builder::build_universe;
#[cfg(feature = "conlat")]
pub use lattice_builder::find_join_irreducibles;

/// Progress reporting trait for long-running congruence computations
#[cfg(feature = "conlat")]
pub trait ProgressCallback: Send + Sync {
    /// Report progress as a fraction between 0.0 and 1.0
    fn report_progress(&self, progress: f64);

    /// Check if computation should be cancelled
    fn should_cancel(&self) -> bool;
}

/// Progress reporting types
#[cfg(feature = "conlat")]
pub mod progress {
    use super::ProgressCallback;
    use std::sync::atomic::{AtomicBool, AtomicU64};
    use std::sync::Arc;

    /// Simple progress callback that tracks progress
    pub struct SimpleProgress {
        current: Arc<AtomicU64>,
        total: u64,
        cancelled: Arc<AtomicBool>,
    }

    impl SimpleProgress {
        pub fn new(total: u64) -> Self {
            Self {
                current: Arc::new(AtomicU64::new(0)),
                total,
                cancelled: Arc::new(AtomicBool::new(false)),
            }
        }

        pub fn increment(&self) {
            self.current
                .fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        }

        pub fn set_cancelled(&self) {
            self.cancelled
                .store(true, std::sync::atomic::Ordering::Relaxed);
        }

        pub fn progress(&self) -> f64 {
            let current = self.current.load(std::sync::atomic::Ordering::Relaxed);
            if self.total == 0 {
                0.0
            } else {
                current as f64 / self.total as f64
            }
        }
    }

    impl ProgressCallback for SimpleProgress {
        fn report_progress(&self, _progress: f64) {
            // Progress is tracked internally
        }

        fn should_cancel(&self) -> bool {
            self.cancelled.load(std::sync::atomic::Ordering::Relaxed)
        }
    }

    /// No-op progress callback for when progress reporting is not needed
    pub struct NoProgress;

    impl ProgressCallback for NoProgress {
        fn report_progress(&self, _progress: f64) {}

        fn should_cancel(&self) -> bool {
            false
        }
    }
}
