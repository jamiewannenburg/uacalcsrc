use crate::{UACalcError, UACalcResult};

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
                message: format!("Universe must be contiguous starting from 0, found {} at position {}", element, i),
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
        assert_eq!(horner_decode(0, 0, 5), vec![]);
        
        // Test overflow detection
        assert_eq!(horner_encode(&[usize::MAX], 2), None);
    }

    #[test]
    fn test_horner_table_size() {
        assert_eq!(horner_table_size(0, 5), Some(1));
        assert_eq!(horner_table_size(1, 5), Some(5));
        assert_eq!(horner_table_size(2, 5), Some(25));
        assert_eq!(horner_table_size(3, 5), Some(125));
        
        // Test overflow detection
        assert_eq!(horner_table_size(20, 2), None);
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
        assert_eq!(factorial(20), None); // Overflow
        
        assert_eq!(binomial_coefficient(5, 2), Some(10));
        assert_eq!(binomial_coefficient(5, 0), Some(1));
        assert_eq!(binomial_coefficient(5, 6), Some(0));
    }

    #[test]
    fn test_memory_estimation() {
        assert_eq!(estimate_table_memory(2, 5), Some(200)); // 25 * 8 bytes
        assert_eq!(estimate_table_memory(10, 2), None); // Overflow
    }
}
