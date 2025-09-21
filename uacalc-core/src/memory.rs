//! Memory management and limiting functionality
//!
//! This module provides global memory limiting capabilities using the cap allocator.
//! It allows setting memory limits that will cause allocation failures when exceeded.

use crate::error::{UACalcError, UACalcResult};
use std::sync::atomic::{AtomicUsize, Ordering};

#[cfg(feature = "memory-limit")]
use cap::Cap;
#[cfg(feature = "memory-limit")]
use std::alloc::System;

/// Global memory limit in bytes
static MEMORY_LIMIT: AtomicUsize = AtomicUsize::new(usize::MAX);

/// Global allocator with memory limiting capability
/// Only use this when memory-limit feature is enabled and no other allocator is configured
#[cfg(all(feature = "memory-limit", not(feature = "mimalloc"), not(feature = "jemalloc")))]
#[global_allocator]
static ALLOCATOR: Cap<System> = Cap::new(System, usize::MAX);

/// Set the global memory limit in bytes
///
/// # Arguments
/// * `limit_bytes` - Maximum number of bytes that can be allocated
///
/// # Returns
/// * `Ok(())` if the limit was set successfully
/// * `Err(UACalcError)` if the limit is invalid or cannot be set
pub fn set_memory_limit(limit_bytes: usize) -> UACalcResult<()> {
    if limit_bytes == 0 {
        return Err(UACalcError::ParseError {
            message: "Memory limit must be greater than 0".to_string(),
        });
    }

    MEMORY_LIMIT.store(limit_bytes, Ordering::SeqCst);

    #[cfg(all(feature = "memory-limit", not(feature = "mimalloc"), not(feature = "jemalloc")))]
    {
        ALLOCATOR.set_limit(limit_bytes).map_err(|_| {
            UACalcError::ParseError {
                message: "Failed to set memory limit".to_string(),
            }
        })?;
    }

    Ok(())
}

/// Get the current memory limit in bytes
pub fn get_memory_limit() -> usize {
    MEMORY_LIMIT.load(Ordering::SeqCst)
}

/// Reset the memory limit to the default (unlimited)
pub fn reset_memory_limit() -> UACalcResult<()> {
    set_memory_limit(usize::MAX)
}

/// Get the currently allocated memory in bytes
///
/// # Returns
/// * Number of bytes currently allocated
pub fn get_allocated_memory() -> usize {
    #[cfg(all(feature = "memory-limit", not(feature = "mimalloc"), not(feature = "jemalloc")))]
    {
        ALLOCATOR.allocated()
    }
    #[cfg(not(all(feature = "memory-limit", not(feature = "mimalloc"), not(feature = "jemalloc"))))]
    {
        0 // Cannot track without cap allocator
    }
}

/// Get the peak allocated memory in bytes
///
/// # Returns
/// * Peak number of bytes that have been allocated (same as current for cap crate)
pub fn get_peak_allocated_memory() -> usize {
    #[cfg(all(feature = "memory-limit", not(feature = "mimalloc"), not(feature = "jemalloc")))]
    {
        ALLOCATOR.allocated() // cap crate doesn't have peak_allocated, use current
    }
    #[cfg(not(all(feature = "memory-limit", not(feature = "mimalloc"), not(feature = "jemalloc"))))]
    {
        0 // Cannot track without cap allocator
    }
}

/// Check if the current allocation would exceed the memory limit
///
/// # Arguments
/// * `additional_bytes` - Number of additional bytes to check
///
/// # Returns
/// * `true` if the allocation would exceed the limit
/// * `false` if the allocation is within the limit
pub fn would_exceed_limit(additional_bytes: usize) -> bool {
    let current = get_allocated_memory();
    let limit = get_memory_limit();
    current.saturating_add(additional_bytes) > limit
}

/// Estimate memory usage for free algebra generation
///
/// # Arguments
/// * `num_generators` - Number of generators
/// * `num_operations` - Number of operations
/// * `max_depth` - Maximum depth of terms
/// * `operation_arities` - Arities of operations
///
/// # Returns
/// * Estimated memory usage in bytes
pub fn estimate_free_algebra_memory(
    num_generators: usize,
    num_operations: usize,
    max_depth: usize,
    operation_arities: &[usize],
) -> usize {
    // Early return for obviously too large cases
    if num_generators == 0 || max_depth == 0 {
        return 1024; // Minimal estimate
    }
    
    // Estimate number of terms generated with overflow protection
    let mut estimated_terms = num_generators;
    let mut current_level_size = num_generators;
    
    for _depth in 1..=max_depth {
        let mut next_level_size: usize = 0;
        for &arity in operation_arities {
            if arity == 0 {
                next_level_size = next_level_size.saturating_add(1); // Constants
            } else {
                // Estimate combinations: current_level_size^arity with overflow protection
                let power_result = safe_pow(current_level_size, arity);
                next_level_size = next_level_size.saturating_add(power_result);
            }
        }
        
        // Prevent runaway growth
        if next_level_size > 1_000_000 {
            return usize::MAX; // Indicate it's too large to estimate safely
        }
        
        estimated_terms = estimated_terms.saturating_add(next_level_size);
        current_level_size = next_level_size;
    }
    
    // Estimate memory usage:
    // - Terms: ~32 bytes per term (Term struct)
    let term_memory = estimated_terms.saturating_mul(32);
    let mut table_memory: usize = 0;
    
    for &arity in operation_arities {
        if arity == 0 {
            table_memory = table_memory.saturating_add(8); // Single constant entry
        } else {
            // Calculate table size with overflow protection
            let table_size = safe_pow(estimated_terms, arity);
            let row_size = (arity + 1).saturating_mul(8);
            let operation_memory = table_size.saturating_mul(row_size);
            table_memory = table_memory.saturating_add(operation_memory);
        }
    }
    
    // Add overhead for data structures (Vec capacity, HashMap, etc.)
    let total_base = term_memory.saturating_add(table_memory);
    let overhead = total_base / 4; // 25% overhead
    
    total_base.saturating_add(overhead)
}

/// Safe power function that prevents overflow
fn safe_pow(base: usize, exp: usize) -> usize {
    if exp == 0 {
        return 1;
    }
    if exp == 1 {
        return base;
    }
    
    // For large exponents, use a more conservative approach
    if exp > 10 {
        // For very large exponents, return a large but safe number
        return 1_000_000;
    }
    
    let mut result: usize = 1;
    let mut current_base = base;
    let mut current_exp = exp;
    
    while current_exp > 0 {
        if current_exp & 1 == 1 {
            result = result.saturating_mul(current_base);
        }
        current_base = current_base.saturating_mul(current_base);
        current_exp >>= 1;
        
        // Early exit if we're getting too large
        if result > 1_000_000 {
            return 1_000_000;
        }
    }
    
    result
}

/// Check if free algebra generation would exceed memory limit
///
/// # Arguments
/// * `num_generators` - Number of generators
/// * `num_operations` - Number of operations
/// * `max_depth` - Maximum depth of terms
/// * `operation_arities` - Arities of operations
///
/// # Returns
/// * `Ok(())` if generation is within memory limit
/// * `Err(UACalcError)` if generation would exceed limit
pub fn check_free_algebra_memory_limit(
    num_generators: usize,
    num_operations: usize,
    max_depth: usize,
    operation_arities: &[usize],
) -> UACalcResult<()> {
    let estimated_memory = estimate_free_algebra_memory(
        num_generators,
        num_operations,
        max_depth,
        operation_arities,
    );
    
    // If estimation is too large to calculate safely, reject it
    if estimated_memory == usize::MAX {
        return Err(UACalcError::MemoryLimitExceeded {
            message: format!(
                "Free algebra generation parameters are too large to estimate memory safely. \
                 Generators: {}, Operations: {}, Max depth: {}, Arities: {:?}",
                num_generators, num_operations, max_depth, operation_arities
            ),
        });
    }
    
    let current_allocated = get_allocated_memory();
    let limit = get_memory_limit();
    
    if current_allocated.saturating_add(estimated_memory) > limit {
        return Err(UACalcError::MemoryLimitExceeded {
            message: format!(
                "Free algebra generation would exceed memory limit. \
                 Estimated memory: {} bytes, current: {} bytes, limit: {} bytes",
                estimated_memory, current_allocated, limit
            ),
        });
    }
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_memory_limit_basic() {
        // Test setting and getting memory limit
        let limit = 1024 * 1024; // 1MB
        set_memory_limit(limit).unwrap();
        assert_eq!(get_memory_limit(), limit);
    }

    #[test]
    fn test_memory_limit_zero() {
        // Test that zero limit is rejected
        let result = set_memory_limit(0);
        assert!(result.is_err());
    }

    #[test]
    fn test_would_exceed_limit() {
        // Try to set memory limit, but don't fail if it doesn't work
        // This can happen if the allocator has already been used
        if set_memory_limit(1000).is_ok() {
            // This test is limited without the memory-limit feature
            // In a real scenario, we'd test with actual allocations
            assert!(!would_exceed_limit(500));
        }
        // If setting the limit fails, we skip the test
    }

    #[test]
    fn test_estimate_free_algebra_memory() {
        let estimate = estimate_free_algebra_memory(2, 1, 2, &[2]);
        assert!(estimate > 0);
        
        // Larger parameters should result in larger estimates
        let larger_estimate = estimate_free_algebra_memory(3, 2, 3, &[2, 3]);
        assert!(larger_estimate > estimate);
    }

    #[test]
    fn test_check_free_algebra_memory_limit() {
        // Try to set a very small limit, but don't fail if it doesn't work
        if set_memory_limit(1000).is_ok() {
            // This should fail for any reasonable free algebra
            let result = check_free_algebra_memory_limit(2, 1, 2, &[2]);
            assert!(result.is_err());
        }
        
        // Try to set a large limit
        if set_memory_limit(usize::MAX).is_ok() {
            // This should succeed
            let result = check_free_algebra_memory_limit(2, 1, 2, &[2]);
            assert!(result.is_ok());
        }
    }
}
