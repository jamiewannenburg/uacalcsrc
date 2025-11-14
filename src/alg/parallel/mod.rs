use once_cell::sync::Lazy;
use std::sync::Arc;

/// Internal static field for the runtime pool.
/// 
/// Uses `Lazy` for thread-safe lazy initialization on first access.
/// This is equivalent to Java's static ForkJoinPool fjPool field.
static FJ_POOL: Lazy<Arc<tokio::runtime::Runtime>> = Lazy::new(|| {
    Arc::new(
        tokio::runtime::Runtime::new()
            .expect("Failed to create Tokio runtime for Pool")
    )
});

/// A single global runtime pool for parallel processing.
/// 
/// This provides a thread-safe, lazily initialized runtime instance
/// that can be shared across the application. This is similar to
/// Java's ForkJoinPool - a single global pool is recommended rather
/// than creating multiple pools.
/// 
/// # Examples
/// ```
/// use uacalc::alg::parallel::Pool;
/// 
/// // Access the runtime pool
/// let runtime = Pool::fj_pool();
/// ```
pub struct Pool;

impl Pool {
    /// Static field equivalent to Java's static ForkJoinPool fjPool.
    /// 
    /// Returns a reference to the lazily initialized, thread-safe runtime.
    /// The runtime is created on first access and is shared across
    /// all subsequent accesses.
    /// 
    /// # Returns
    /// A reference-counted runtime that can be used for parallel processing.
    /// 
    /// # Thread Safety
    /// This method is thread-safe and can be called concurrently from
    /// multiple threads.
    pub fn fj_pool() -> Arc<tokio::runtime::Runtime> {
        FJ_POOL.clone()
    }
}

pub mod single_close;

pub use single_close::SingleClose;
