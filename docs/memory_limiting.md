# Memory Limiting in UACalc Rust

This document describes how to use the memory limiting functionality in UACalc Rust to prevent excessive memory allocation during computationally intensive operations like free algebra generation.

## Overview

The memory limiting system provides:
- Global memory limit enforcement using a custom allocator
- Memory usage tracking and monitoring
- Pre-allocation memory estimation for free algebra generation
- Python bindings for runtime memory limit control

## Building with Memory Limiting

To enable memory limiting, build with the `memory-limit` feature:

```bash
# For Rust code
cargo build --features memory-limit

# For Python bindings
cargo build --features memory-limit
```

**Note**: The memory limiting allocator is only active when the `memory-limit` feature is enabled and no other allocator (like `mimalloc` or `jemalloc`) is being used.

## Rust API

### Setting Memory Limits

```rust
use uacalc_core::memory::{set_memory_limit, get_memory_limit};

// Set memory limit to 100 MB
set_memory_limit(100 * 1024 * 1024)?;

// Get current limit
let limit = get_memory_limit();
println!("Current limit: {} bytes", limit);
```

### Monitoring Memory Usage

```rust
use uacalc_core::memory::{get_allocated_memory, get_peak_allocated_memory};

// Get current memory usage
let current = get_allocated_memory();
let peak = get_peak_allocated_memory();

println!("Current: {} bytes, Peak: {} bytes", current, peak);
```

### Free Algebra Memory Estimation

```rust
use uacalc_core::memory::{estimate_free_algebra_memory, check_free_algebra_memory_limit};

// Estimate memory for free algebra generation
let estimate = estimate_free_algebra_memory(
    3,  // num_generators
    2,  // num_operations  
    4,  // max_depth
    &[2, 2]  // operation_arities
);

println!("Estimated memory: {} bytes", estimate);

// Check if generation would exceed limit
check_free_algebra_memory_limit(3, 2, 4, &[2, 2])?;
```

## Python API

### Setting Memory Limits

```python
import uacalc_rust as ua

# Set memory limit to 50 MB
ua.set_memory_limit(50 * 1024 * 1024)

# Get current limit
limit = ua.get_memory_limit()
print(f"Current limit: {limit:,} bytes ({limit / (1024*1024):.1f} MB)")
```

### Monitoring Memory Usage

```python
# Get current memory usage
current = ua.get_allocated_memory()
peak = ua.get_peak_allocated_memory()

print(f"Current: {current:,} bytes ({current / (1024*1024):.1f} MB)")
print(f"Peak: {peak:,} bytes ({peak / (1024*1024):.1f} MB)")
```

### Free Algebra Memory Estimation

```python
# Estimate memory for free algebra generation
estimate = ua.estimate_free_algebra_memory(
    num_generators=3,
    num_operations=2,
    max_depth=4,
    operation_arities=[2, 2]
)

print(f"Estimated memory: {estimate:,} bytes ({estimate / (1024*1024):.1f} MB)")

# Check if generation would exceed limit
try:
    ua.check_free_algebra_memory_limit(3, 2, 4, [2, 2])
    print("Memory check passed")
except ua.UACalcError as e:
    print(f"Memory limit would be exceeded: {e}")
```

## Error Handling

When memory limits are exceeded, the system will raise a `UACalcError::MemoryLimitExceeded` error:

```rust
use uacalc_core::error::UACalcError;

match result {
    Err(UACalcError::MemoryLimitExceeded { message }) => {
        println!("Memory limit exceeded: {}", message);
    }
    // ... other error handling
}
```

In Python:

```python
try:
    # Some operation that might exceed memory limit
    result = ua.create_free_algebra(...)
except ua.UACalcError as e:
    if "Memory limit exceeded" in str(e):
        print("Memory limit exceeded, try reducing parameters")
    else:
        print(f"Other error: {e}")
```

## Example: Safe Free Algebra Generation

Here's a complete example showing how to safely generate free algebras with memory limiting:

```python
import uacalc_rust as ua

def create_free_algebra_safely(generators, operations, max_depth, memory_limit_mb):
    """Create a free algebra with memory limit checking."""
    
    # Set memory limit
    memory_limit_bytes = memory_limit_mb * 1024 * 1024
    ua.set_memory_limit(memory_limit_bytes)
    
    # Get operation arities
    operation_arities = [op.arity() for op in operations]
    
    # Check memory limit before generation
    try:
        ua.check_free_algebra_memory_limit(
            len(generators),
            len(operations),
            max_depth,
            operation_arities
        )
    except ua.UACalcError as e:
        print(f"Memory limit check failed: {e}")
        return None
    
    # Estimate memory usage
    estimate = ua.estimate_free_algebra_memory(
        len(generators),
        len(operations),
        max_depth,
        operation_arities
    )
    
    print(f"Estimated memory: {estimate / (1024*1024):.1f} MB")
    print(f"Memory limit: {memory_limit_mb} MB")
    
    # Create the free algebra
    try:
        variety = ua.VarietyConstraint("trivial")
        free_algebra = ua.create_free_algebra(
            name="TestAlgebra",
            generators=generators,
            variety_constraints=variety,
            operation_symbols=operations,
            max_depth=max_depth
        )
        
        print(f"Successfully created free algebra with {free_algebra.cardinality()} elements")
        return free_algebra
        
    except ua.UACalcError as e:
        print(f"Failed to create free algebra: {e}")
        return None

# Example usage
generators = ["x", "y", "z"]
operations = [
    ua.OperationSymbol("*", 2),
    ua.OperationSymbol("+", 2)
]

# Try with 10 MB limit
algebra = create_free_algebra_safely(generators, operations, 3, 10)

if algebra is None:
    print("Failed with 10 MB limit, trying with 50 MB")
    algebra = create_free_algebra_safely(generators, operations, 3, 50)
```

## Limitations

1. **Allocator Conflicts**: The memory limiting allocator cannot be used simultaneously with other custom allocators like `mimalloc` or `jemalloc`.

2. **Python Memory**: The memory limit only applies to Rust allocations, not Python's memory usage.

3. **External Libraries**: Memory allocated by external libraries may not be tracked by the custom allocator.

4. **Peak Tracking**: The current implementation doesn't track peak memory usage separately from current usage.

## Best Practices

1. **Set Limits Early**: Set memory limits before starting computationally intensive operations.

2. **Estimate First**: Always estimate memory usage before attempting large operations.

3. **Handle Errors Gracefully**: Implement proper error handling for memory limit exceeded scenarios.

4. **Monitor Usage**: Regularly check memory usage during long-running operations.

5. **Test with Small Limits**: Test your code with small memory limits to ensure proper error handling.

## Testing

Run the provided test script to verify memory limiting functionality:

```bash
python test_memory_limit.py
```

This script demonstrates:
- Setting and getting memory limits
- Monitoring memory usage
- Memory estimation for free algebra generation
- Error handling when limits are exceeded
- Dynamic limit adjustment


