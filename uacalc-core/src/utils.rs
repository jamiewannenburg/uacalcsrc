use crate::{UACalcError, UACalcResult};
use smallvec::SmallVec;
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};
use std::time::Instant;

// Global allocator configuration
#[cfg(feature = "mimalloc")]
use mimalloc::MiMalloc;

#[cfg(feature = "jemalloc")]
use jemallocator::Jemalloc;

#[cfg(feature = "mimalloc")]
#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;

#[cfg(feature = "jemalloc")]
#[global_allocator]
static GLOBAL: Jemalloc = Jemalloc;

/// Mixed-radix encoding utilities for operation tables

/// Encode arguments using Horner's method for mixed-radix indexing
///
/// # Arguments
/// * `args` - The arguments to encode
/// * `base` - The base (set size) for encoding
///
/// # Returns
/// * `Some(index)` if encoding succeeds without overflow
/// * `None` if overflow would occur
pub fn horner_encode(args: &[usize], base: usize) -> Option<usize> {
    if base == 0 {
        return None;
    }

    let mut index: usize = 0;
    for &arg in args {
        if arg >= base {
            return None;
        }

        // Check for overflow in multiplication
        let new_index = index.checked_mul(base)?;
        // Check for overflow in addition
        let final_index = new_index.checked_add(arg)?;
        index = final_index;
    }

    Some(index)
}

/// Decode an index back to arguments using mixed-radix decoding
///
/// # Arguments
/// * `index` - The encoded index
/// * `arity` - The number of arguments
/// * `base` - The base (set size) used for encoding
///
/// # Returns
/// * Vector of decoded arguments
pub fn horner_decode(index: usize, arity: usize, base: usize) -> Vec<usize> {
    if base == 0 || arity == 0 {
        return vec![];
    }

    let mut args = Vec::with_capacity(arity);
    let mut remaining = index;

    for _ in 0..arity {
        args.push(remaining % base);
        remaining /= base;
    }

    args.reverse();
    args
}

/// Calculate the size of a Horner-encoded table
///
/// # Arguments
/// * `arity` - The arity of the operation
/// * `base` - The base (set size)
///
/// # Returns
/// * `Some(size)` if calculation succeeds without overflow
/// * `None` if overflow would occur
pub fn horner_table_size(arity: usize, base: usize) -> Option<usize> {
    if base == 0 {
        return Some(0);
    }
    if arity == 0 {
        return Some(1);
    }

    let mut size: usize = 1;
    for _ in 0..arity {
        size = size.checked_mul(base)?;
    }
    Some(size)
}

/// Mixed-radix encoding using little-endian order
///
/// # Arguments
/// * `coords` - The coordinates to encode
/// * `radices` - The radices (sizes) for each coordinate
///
/// # Returns
/// * `Some(encoded)` if encoding succeeds without overflow
/// * `None` if overflow would occur or invalid coordinates
pub fn mixed_radix_encode(coords: &[usize], radices: &[usize]) -> Option<usize> {
    if coords.len() != radices.len() {
        return None;
    }

    let mut result: usize = 0;
    let mut multiplier: usize = 1;

    for (i, (&coord, &radix)) in coords.iter().zip(radices.iter()).enumerate() {
        if radix == 0 || coord >= radix {
            return None;
        }

        // Add coordinate * multiplier to result
        let term = coord.checked_mul(multiplier)?;
        result = result.checked_add(term)?;

        // Update multiplier for next coordinate (except for the last one)
        if i < coords.len() - 1 {
            multiplier = multiplier.checked_mul(radix)?;
        }
    }

    Some(result)
}

/// Mixed-radix decoding using little-endian order
///
/// # Arguments
/// * `value` - The encoded value
/// * `radices` - The radices (sizes) for each coordinate
///
/// # Returns
/// * Vector of decoded coordinates
pub fn mixed_radix_decode(value: usize, radices: &[usize]) -> Vec<usize> {
    if radices.is_empty() {
        return vec![];
    }

    let mut coords = Vec::with_capacity(radices.len());
    let mut remaining = value;

    for &radix in radices {
        if radix == 0 {
            coords.push(0);
        } else {
            coords.push(remaining % radix);
            remaining /= radix;
        }
    }

    coords
}

/// Calculate the total size for a mixed-radix system
///
/// # Arguments
/// * `radices` - The radices (sizes) for each position
///
/// # Returns
/// * `Some(size)` if calculation succeeds without overflow
/// * `None` if overflow would occur
pub fn mixed_radix_size(radices: &[usize]) -> Option<usize> {
    if radices.is_empty() {
        return Some(1);
    }

    let mut size: usize = 1;
    for &radix in radices {
        if radix == 0 {
            return Some(0);
        }
        size = size.checked_mul(radix)?;
    }
    Some(size)
}

/// Memory Pool Implementation for reusable allocations
pub struct MemoryPool<T> {
    pool: Arc<Mutex<VecDeque<T>>>,
    max_size: usize,
}

impl<T> MemoryPool<T> {
    /// Create a new memory pool with the specified maximum size
    pub fn new(max_size: usize) -> Self {
        Self {
            pool: Arc::new(Mutex::new(VecDeque::new())),
            max_size,
        }
    }

    /// Get an item from the pool, or create a new one if pool is empty
    pub fn get<F>(&self, create_fn: F) -> T
    where
        F: FnOnce() -> T,
    {
        if let Ok(mut pool) = self.pool.lock() {
            if let Some(item) = pool.pop_front() {
                return item;
            }
        }
        create_fn()
    }

    /// Return an item to the pool for reuse
    pub fn return_to_pool(&self, item: T) {
        if let Ok(mut pool) = self.pool.lock() {
            if pool.len() < self.max_size {
                pool.push_back(item);
            }
        }
    }

    /// Get current pool size
    pub fn size(&self) -> usize {
        self.pool.lock().map(|p| p.len()).unwrap_or(0)
    }

    /// Clear the pool
    pub fn clear(&self) {
        if let Ok(mut pool) = self.pool.lock() {
            pool.clear();
        }
    }
}

/// Thread-local memory pool for multi-threaded scenarios
pub struct ThreadLocalPool<T> {
    pools: Vec<Arc<MemoryPool<T>>>,
}

impl<T> ThreadLocalPool<T> {
    /// Create a new thread-local pool with the specified number of threads
    pub fn new(thread_count: usize, max_size_per_thread: usize) -> Self {
        let pools = (0..thread_count)
            .map(|_| Arc::new(MemoryPool::new(max_size_per_thread)))
            .collect();
        Self { pools }
    }

    /// Get a pool for the specified thread ID
    pub fn get_pool(&self, thread_id: usize) -> &Arc<MemoryPool<T>> {
        &self.pools[thread_id % self.pools.len()]
    }
}

/// SIMD Utilities for bulk operations
#[cfg(all(target_arch = "x86_64", feature = "simd"))]
pub mod simd {
    use std::arch::x86_64::*;

    /// Compare two arrays for equality using SIMD
    #[target_feature(enable = "avx2")]
    pub unsafe fn simd_compare_arrays(a: &[usize], b: &[usize]) -> bool {
        if a.len() != b.len() {
            return false;
        }

        let mut i = 0;
        let len = a.len();

        // Use 64-bit comparisons for usize on 64-bit platforms
        #[cfg(target_pointer_width = "64")]
        {
            // Process 4 elements at a time with AVX2 (64-bit lanes)
            while i + 4 <= len {
                let va = _mm256_loadu_si256(a.as_ptr().add(i) as *const __m256i);
                let vb = _mm256_loadu_si256(b.as_ptr().add(i) as *const __m256i);
                let cmp = _mm256_cmpeq_epi64(va, vb);
                let mask = _mm256_movemask_pd(_mm256_castsi256_pd(cmp));
                if mask != 0b1111 {
                    return false;
                }
                i += 4;
            }
        }

        #[cfg(target_pointer_width = "32")]
        {
            // Process 8 elements at a time with AVX2 (32-bit lanes)
            while i + 8 <= len {
                let va = _mm256_loadu_si256(a.as_ptr().add(i) as *const __m256i);
                let vb = _mm256_loadu_si256(b.as_ptr().add(i) as *const __m256i);
                let cmp = _mm256_cmpeq_epi32(va, vb);
                let mask = _mm256_movemask_ps(_mm256_castsi256_ps(cmp));
                if mask != 0b11111111 {
                    return false;
                }
                i += 8;
            }
        }

        // Handle remaining elements
        while i < len {
            if a[i] != b[i] {
                return false;
            }
            i += 1;
        }

        true
    }

    /// Find first difference between two arrays using SIMD
    #[target_feature(enable = "avx2")]
    pub unsafe fn simd_find_first_difference(a: &[usize], b: &[usize]) -> Option<usize> {
        let min_len = a.len().min(b.len());
        let mut i = 0;

        // Use 64-bit comparisons for usize on 64-bit platforms
        #[cfg(target_pointer_width = "64")]
        {
            // Process 4 elements at a time with AVX2 (64-bit lanes)
            while i + 4 <= min_len {
                let va = _mm256_loadu_si256(a.as_ptr().add(i) as *const __m256i);
                let vb = _mm256_loadu_si256(b.as_ptr().add(i) as *const __m256i);
                let cmp = _mm256_cmpeq_epi64(va, vb);
                let mask = _mm256_movemask_pd(_mm256_castsi256_pd(cmp));

                if mask != 0b1111 {
                    // Find the first difference in this block
                    for j in 0..4 {
                        if a[i + j] != b[i + j] {
                            return Some(i + j);
                        }
                    }
                }
                i += 4;
            }
        }

        #[cfg(target_pointer_width = "32")]
        {
            // Process 8 elements at a time with AVX2 (32-bit lanes)
            while i + 8 <= min_len {
                let va = _mm256_loadu_si256(a.as_ptr().add(i) as *const __m256i);
                let vb = _mm256_loadu_si256(b.as_ptr().add(i) as *const __m256i);
                let cmp = _mm256_cmpeq_epi32(va, vb);
                let mask = _mm256_movemask_ps(_mm256_castsi256_ps(cmp));

                if mask != 0b11111111 {
                    // Find the first difference in this block
                    for j in 0..8 {
                        if a[i + j] != b[i + j] {
                            return Some(i + j);
                        }
                    }
                }
                i += 8;
            }
        }

        // Handle remaining elements
        while i < min_len {
            if a[i] != b[i] {
                return Some(i);
            }
            i += 1;
        }

        if a.len() != b.len() {
            Some(min_len)
        } else {
            None
        }
    }
}

#[cfg(not(all(target_arch = "x86_64", feature = "simd")))]
pub mod simd {
    /// Fallback implementation for non-x86_64 architectures or when SIMD feature is disabled
    pub fn simd_compare_arrays(a: &[usize], b: &[usize]) -> bool {
        a == b
    }

    /// Fallback implementation for non-x86_64 architectures or when SIMD feature is disabled
    pub fn simd_find_first_difference(a: &[usize], b: &[usize]) -> Option<usize> {
        a.iter().zip(b.iter()).position(|(x, y)| x != y)
    }
}

/// Cache-friendly data structures

/// Compact vector that stores small vectors inline
pub struct CompactVec<T> {
    data: SmallVec<[T; 8]>,
}

impl<T> CompactVec<T> {
    pub fn new() -> Self {
        Self {
            data: SmallVec::new(),
        }
    }

    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            data: SmallVec::with_capacity(capacity),
        }
    }

    pub fn push(&mut self, item: T) {
        self.data.push(item);
    }

    pub fn len(&self) -> usize {
        self.data.len()
    }

    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }

    pub fn clear(&mut self) {
        self.data.clear();
    }
}

impl<T> std::ops::Deref for CompactVec<T> {
    type Target = [T];

    fn deref(&self) -> &Self::Target {
        &self.data
    }
}

impl<T> std::ops::DerefMut for CompactVec<T> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.data
    }
}

/// Efficient bit set for small universes
pub struct BitSet {
    bits: u64,
    size: usize,
}

impl BitSet {
    pub fn new(size: usize) -> Self {
        assert!(size <= 64, "BitSet only supports universes up to size 64");
        Self { bits: 0, size }
    }

    pub fn insert(&mut self, element: usize) {
        if element < self.size {
            self.bits |= 1 << element;
        }
    }

    pub fn remove(&mut self, element: usize) {
        if element < self.size {
            self.bits &= !(1 << element);
        }
    }

    pub fn contains(&self, element: usize) -> bool {
        element < self.size && (self.bits & (1 << element)) != 0
    }

    pub fn clear(&mut self) {
        self.bits = 0;
    }

    pub fn len(&self) -> usize {
        self.bits.count_ones() as usize
    }

    pub fn is_empty(&self) -> bool {
        self.bits == 0
    }
}

/// Sparse set for efficient set operations on small universes
pub struct SparseSet {
    dense: Vec<usize>,
    sparse: Vec<usize>,
    size: usize,
}

impl SparseSet {
    pub fn new(size: usize) -> Self {
        Self {
            dense: Vec::new(),
            sparse: vec![usize::MAX; size],
            size,
        }
    }

    pub fn insert(&mut self, element: usize) {
        if element < self.size && !self.contains(element) {
            self.sparse[element] = self.dense.len();
            self.dense.push(element);
        }
    }

    pub fn remove(&mut self, element: usize) {
        if element < self.size && self.contains(element) {
            let dense_index = self.sparse[element];
            let last_element = self.dense[self.dense.len() - 1];
            self.dense[dense_index] = last_element;
            self.sparse[last_element] = dense_index;
            self.dense.pop();
            self.sparse[element] = usize::MAX;
        }
    }

    pub fn contains(&self, element: usize) -> bool {
        element < self.size && self.sparse[element] < self.dense.len()
    }

    pub fn clear(&mut self) {
        self.dense.clear();
        for i in 0..self.size {
            self.sparse[i] = usize::MAX;
        }
    }

    pub fn len(&self) -> usize {
        self.dense.len()
    }

    pub fn is_empty(&self) -> bool {
        self.dense.is_empty()
    }

    pub fn iter(&self) -> impl Iterator<Item = &usize> {
        self.dense.iter()
    }
}

/// Performance profiling utilities

/// Global allocation counter for debugging memory usage
static ALLOCATION_COUNTER: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);

/// Increment allocation counter
pub fn increment_allocation_counter() {
    ALLOCATION_COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
}

/// Get current allocation count
pub fn get_allocation_count() -> usize {
    ALLOCATION_COUNTER.load(std::sync::atomic::Ordering::Relaxed)
}

/// Reset allocation counter
pub fn reset_allocation_counter() {
    ALLOCATION_COUNTER.store(0, std::sync::atomic::Ordering::Relaxed);
}

/// Performance scope for automatic timing
pub struct PerformanceScope {
    name: String,
    start: Instant,
}

impl PerformanceScope {
    pub fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            start: Instant::now(),
        }
    }
}

impl Drop for PerformanceScope {
    fn drop(&mut self) {
        let duration = self.start.elapsed();
        println!("{}: {:?}", self.name, duration);
    }
}

/// Macro for automatic performance scoping
#[macro_export]
macro_rules! profile_scope {
    ($name:expr) => {
        let _scope = $crate::utils::PerformanceScope::new($name);
    };
}

/// Macro for memory usage tracking
#[macro_export]
macro_rules! memory_usage {
    () => {{
        let usage = $crate::utils::get_allocation_count();
        println!("Memory allocations: {}", usage);
        usage
    }};
}

/// Macro for function benchmarking
#[macro_export]
macro_rules! benchmark_function {
    ($name:expr, $func:expr) => {{
        let start = std::time::Instant::now();
        let result = $func;
        let duration = start.elapsed();
        println!("{}: {:?}", $name, duration);
        result
    }};
}

/// Validation utilities

/// Validate that a universe is contiguous starting from 0
pub fn validate_universe_contiguous(universe: &[usize]) -> UACalcResult<()> {
    if universe.is_empty() {
        return Err(UACalcError::InvalidOperation {
            message: "Universe cannot be empty".to_string(),
        });
    }

    for (i, &element) in universe.iter().enumerate() {
        if element != i {
            return Err(UACalcError::InvalidOperation {
                message: format!(
                    "Universe must be contiguous starting from 0, found {} at position {}",
                    element, i
                ),
            });
        }
    }

    Ok(())
}

/// Validate operation arguments against arity and set size
pub fn validate_operation_args(args: &[usize], arity: usize, set_size: usize) -> UACalcResult<()> {
    if args.len() != arity {
        return Err(UACalcError::InvalidArity {
            expected: arity,
            actual: args.len(),
        });
    }

    for &arg in args {
        if arg >= set_size {
            return Err(UACalcError::IndexOutOfBounds {
                index: arg,
                size: set_size,
            });
        }
    }

    Ok(())
}

/// Validate partition elements against size
pub fn validate_partition_elements(elements: &[usize], size: usize) -> UACalcResult<()> {
    for &element in elements {
        if element >= size {
            return Err(UACalcError::IndexOutOfBounds {
                index: element,
                size,
            });
        }
    }

    Ok(())
}

/// Mathematical utilities

/// Safe exponentiation with overflow checking
pub fn power_checked(base: usize, exp: usize) -> Option<usize> {
    if base == 0 {
        return Some(if exp == 0 { 1 } else { 0 });
    }
    if base == 1 {
        return Some(1);
    }

    let mut result: usize = 1;
    for _ in 0..exp {
        result = result.checked_mul(base)?;
    }
    Some(result)
}

/// Factorial with overflow checking
pub fn factorial(n: usize) -> Option<usize> {
    if n == 0 || n == 1 {
        return Some(1);
    }

    let mut result: usize = 1;
    for i in 2..=n {
        result = result.checked_mul(i)?;
    }
    Some(result)
}

/// Binomial coefficient with overflow checking
pub fn binomial_coefficient(n: usize, k: usize) -> Option<usize> {
    if k > n {
        return Some(0);
    }
    if k == 0 || k == n {
        return Some(1);
    }

    // Use symmetry to minimize computation
    let k = k.min(n - k);

    let mut result: usize = 1;
    for i in 0..k {
        result = result.checked_mul(n - i)?;
        result = result.checked_div((i + 1) as usize)?;
    }
    Some(result)
}

/// Performance utilities

/// Timing macro for benchmarking critical operations
#[macro_export]
macro_rules! time_operation {
    ($name:expr, $operation:expr) => {{
        use std::time::Instant;
        let start = Instant::now();
        let result = $operation;
        let duration = start.elapsed();
        println!("{} took {:?}", $name, duration);
        result
    }};
}

/// Estimate memory usage for operation tables
pub fn estimate_table_memory(arity: usize, set_size: usize) -> Option<usize> {
    let table_size = horner_table_size(arity, set_size)?;
    // Each entry is a usize (8 bytes on 64-bit systems)
    table_size.checked_mul(std::mem::size_of::<usize>())
}

/// Common constants

/// Maximum practical universe size for different operations
pub const MAX_UNIVERSE_SIZE: usize = 1 << 20; // 1M elements
pub const MAX_OPERATION_ARITY: usize = 10;
pub const MAX_TABLE_SIZE: usize = 1 << 30; // 1GB table size limit

/// Default cache sizes and performance thresholds
pub const DEFAULT_CACHE_SIZE: usize = 1000;
pub const PERFORMANCE_THRESHOLD: usize = 100; // Use optimized algorithms above this size

/// Error messages as constants
pub const ERR_OVERFLOW: &str = "Arithmetic overflow occurred";
pub const ERR_INVALID_UNIVERSE: &str = "Universe must be contiguous starting from 0";
pub const ERR_TABLE_TOO_LARGE: &str = "Operation table would be too large";
pub const ERR_INVALID_ARITY: &str = "Invalid operation arity";

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_horner_encode_decode() {
        // Test basic encoding/decoding
        let args = vec![1, 2, 3];
        let base = 5;
        let encoded = horner_encode(&args, base).unwrap();
        let decoded = horner_decode(encoded, 3, base);
        assert_eq!(decoded, args);

        // Test edge cases
        assert_eq!(horner_encode(&[], 5), Some(0));
        assert_eq!(horner_decode(0, 0, 5), vec![] as Vec<usize>);

        // Test overflow detection
        assert_eq!(horner_encode(&[usize::MAX], 2), None);
    }

    #[test]
    fn test_horner_table_size() {
        assert_eq!(horner_table_size(0, 5), Some(1));
        assert_eq!(horner_table_size(1, 5), Some(5));
        assert_eq!(horner_table_size(2, 5), Some(25));
        assert_eq!(horner_table_size(3, 5), Some(125));

        // Test overflow detection - use a larger exponent that will definitely overflow
        assert_eq!(horner_table_size(64, 2), None);
    }

    #[test]
    fn test_validation_functions() {
        // Test valid universe
        validate_universe_contiguous(&[0, 1, 2, 3]).unwrap();

        // Test invalid universe
        assert!(validate_universe_contiguous(&[1, 2, 3]).is_err());
        assert!(validate_universe_contiguous(&[0, 1, 3]).is_err());

        // Test operation args validation
        validate_operation_args(&[0, 1], 2, 5).unwrap();
        assert!(validate_operation_args(&[0, 1], 1, 5).is_err());
        assert!(validate_operation_args(&[0, 5], 2, 5).is_err());
    }

    #[test]
    fn test_mathematical_utilities() {
        assert_eq!(power_checked(2, 3), Some(8));
        assert_eq!(power_checked(0, 0), Some(1));
        assert_eq!(power_checked(2, 100), None); // Overflow

        assert_eq!(factorial(0), Some(1));
        assert_eq!(factorial(5), Some(120));
        assert_eq!(factorial(21), None); // Overflow

        assert_eq!(binomial_coefficient(5, 2), Some(10));
        assert_eq!(binomial_coefficient(5, 0), Some(1));
        assert_eq!(binomial_coefficient(5, 6), Some(0));
    }

    #[test]
    fn test_memory_estimation() {
        assert_eq!(estimate_table_memory(2, 5), Some(200)); // 25 * 8 bytes
        assert_eq!(estimate_table_memory(64, 2), None); // Overflow
    }

    #[test]
    fn test_mixed_radix_encode_decode() {
        // Test basic encoding/decoding
        let coords = vec![1, 2, 0];
        let radices = vec![2, 3, 4];
        let encoded = mixed_radix_encode(&coords, &radices).unwrap();
        let decoded = mixed_radix_decode(encoded, &radices);
        assert_eq!(decoded, coords);

        // Test round-trip for all valid coordinates with 3 factors
        let radices = vec![2, 3, 2];
        for a in 0..2 {
            for b in 0..3 {
                for c in 0..2 {
                    let coords = vec![a, b, c];
                    let encoded = mixed_radix_encode(&coords, &radices).unwrap();
                    let decoded = mixed_radix_decode(encoded, &radices);
                    assert_eq!(decoded, coords, "Round-trip failed for coords {:?}", coords);
                }
            }
        }

        // Test edge cases
        assert_eq!(mixed_radix_encode(&[], &[]), Some(0));
        assert_eq!(mixed_radix_decode(0, &[]), Vec::<usize>::new());

        // Test error cases
        assert_eq!(mixed_radix_encode(&[0, 1], &[2]), None); // Length mismatch
        assert_eq!(mixed_radix_encode(&[2], &[2]), None); // Coordinate out of bounds
        assert_eq!(mixed_radix_encode(&[0], &[0]), None); // Zero radix
    }

    #[test]
    fn test_mixed_radix_size() {
        assert_eq!(mixed_radix_size(&[]), Some(1));
        assert_eq!(mixed_radix_size(&[2]), Some(2));
        assert_eq!(mixed_radix_size(&[2, 3]), Some(6));
        assert_eq!(mixed_radix_size(&[2, 3, 4]), Some(24));
        assert_eq!(mixed_radix_size(&[0]), Some(0));
        
        // Test overflow detection
        let large_radices = vec![usize::MAX, 2];
        assert_eq!(mixed_radix_size(&large_radices), None);
    }
}
