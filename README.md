# UACalc Rust Implementation - Task 12: Operation

This directory contains the Rust implementation of the Universal Algebra Calculator's `Operation` interface with Python bindings.

## Overview

Task 12 implements the foundational `Operation` trait that defines operations in universal algebra, corresponding to the Java `org.uacalc.alg.op.Operation` interface.

## Implementation Status

✅ **COMPLETED**: All core components implemented and tested

### Components Implemented

1. **Operation Trait** (`src/alg/op/operation_trait.rs`)
   - All 17 methods from Java interface
   - Core properties: `arity()`, `get_set_size()`, `symbol()`
   - Operation evaluation: `int_value_at()`, `int_value_at_horner()`, `value_at_arrays()`
   - Table management: `make_table()`, `get_table()`, `is_table_based()`
   - Property checks: `is_idempotent()`, `is_associative()`, `is_commutative()`, etc.

2. **OperationSymbol** (`src/alg/op/operation_symbol.rs`)
   - Name and arity storage
   - Associative flag for binary operations
   - Comparison and hashing support
   - Uniform symbol generation
   - Python bindings with `@pyclass`

3. **AbstractOperation** (`src/alg/op/abstract_operation.rs`)
   - Base implementation providing common functionality
   - Horner encoding/decoding for table indexing
   - Default implementations for most Operation methods
   - Python bindings with `@pyclass`

4. **IntOperation** (`src/alg/op/int_operation.rs`)
   - Table-based concrete implementation
   - Fast operation evaluation using lookup tables
   - Factory methods for creating common operations
   - All property checking implementations
   - Python bindings with `@pyclass`

5. **Comprehensive Tests** (`src/alg/op/tests.rs`)
   - 17 test functions covering all functionality
   - Operation symbol creation and ordering
   - Table-based operation evaluation
   - Property testing (idempotent, associative, etc.)
   - Error handling validation

## Key Features

### Rust Traits Implemented
- `Operation` - Core trait with all 17 methods
- `Ord`, `PartialOrd`, `Eq`, `PartialEq` - For comparison
- `Hash` - For use in collections
- `Display` - For string representation
- `Send`, `Sync` - For thread safety

### Error Handling
- Custom `UaCalcError` enum with descriptive error types
- `Result<T, UaCalcError>` return types for fallible operations
- Proper validation of arguments and table sizes

### Python Bindings
- All classes exposed to Python via PyO3
- Pythonic method names (`is_idempotent_py()`, etc.)
- Magic methods (`__str__`, `__repr__`, `__hash__`, `__eq__`, etc.)
- Factory methods for easy operation creation

## Usage Examples

### Rust
```rust
use uacalc::alg::op::{OperationSymbol, IntOperation};

// Create a binary XOR operation
let xor_table = vec![0, 1, 1, 0];
let symbol = OperationSymbol::new("xor".to_string(), 2)?;
let xor_op = IntOperation::new(symbol, xor_table, 2)?;

// Evaluate the operation
let result = xor_op.int_value_at(&[1, 0])?; // returns 1

// Test properties
assert_eq!(xor_op.is_commutative()?, true);
assert_eq!(xor_op.is_associative()?, true);
```

### Python
```python
import uacalc

# Create a binary operation
xor_table = [0, 1, 1, 0]
xor_op = uacalc.IntOperation.create_binary_operation_py("xor", 2, xor_table)

# Evaluate the operation
result = xor_op.int_value_at_py([1, 0])  # returns 1

# Test properties
print(f"Commutative: {xor_op.is_commutative_py()}")
print(f"Associative: {xor_op.is_associative_py()}")
```

## Testing

### Run Rust Tests
```bash
cargo test
```

### Test Python Bindings
```bash
# First build the Python module
pip install maturin
maturin develop

# Then run the test script
python test_python_bindings.py
```

### Test Java Integration
```bash
# Compile and run Java wrapper tests
javac -cp ".:jars/*" test_wrappers/OperationTest.java
java -cp ".:jars/*" test_wrappers.OperationTest
```

## File Structure

```
├── Cargo.toml                      # Rust project configuration
├── src/
│   ├── lib.rs                      # Main library entry point
│   ├── error.rs                    # Error types
│   └── alg/
│       └── op/
│           ├── mod.rs              # Module exports
│           ├── operation_trait.rs  # Core Operation trait
│           ├── operation_symbol.rs # OperationSymbol implementation
│           ├── abstract_operation.rs # AbstractOperation base class
│           ├── int_operation.rs    # IntOperation table-based impl
│           └── tests.rs            # Comprehensive test suite
├── test_wrappers/
│   └── OperationTest.java          # Java integration tests
├── test_python_bindings.py         # Python binding tests
└── README.md                       # This file
```

## Dependencies

### Runtime Dependencies
- `pyo3` - Python bindings
- `thiserror` - Error handling
- `serde` - Serialization support

### Dependencies Status
- ✅ **OperationSymbol** - Self-contained implementation
- ❌ **Operations** (Task 50) - Static utility methods (future dependency)
- ❌ **Horner** (Task 3) - Table encoding utilities (future dependency)
- ❌ **ArrayString** (Task 6) - Debug output formatting (future dependency)

## Future Enhancements

1. **Performance Optimizations**
   - Lazy table generation for large operations
   - SIMD operations for bulk evaluation
   - Parallel property checking for large algebras

2. **Additional Operation Types**
   - `OperationWithDefaultValue` implementation
   - `TermOperation` for term-based operations
   - Custom operation types for specific algebras

3. **Enhanced Property Testing**
   - More efficient totally symmetric checking
   - Specialized algorithms for large arity operations
   - Approximate property checking for very large operations

## Integration Notes

This implementation is designed to integrate with the existing Java UACalc codebase while providing modern Rust performance and safety guarantees. The Python bindings enable easy scripting and interactive exploration of algebraic structures.

The trait-based design allows for easy extension with new operation types while maintaining compatibility with existing code patterns from the Java implementation.