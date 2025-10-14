# UACalc Rust Implementation - Task 12: Operation

This project implements the UACalc `Operation` interface in Rust with Python bindings and Java compatibility wrappers.

## Overview

Task 12 involves translating the Java interface `org.uacalc.alg.op.Operation` to Rust with Python bindings. The Operation interface is foundational to universal algebra operations and provides 17 methods grouped into:

- **Core Properties** (3 methods): `arity()`, `getSetSize()`, `symbol()`
- **Operation Evaluation** (4 methods): Various `valueAt()` and `intValueAt()` methods
- **Table Management** (4 methods): `makeTable()`, `getTable()`, `isTableBased()`
- **Property Checks** (6 methods): `isIdempotent()`, `isAssociative()`, `isCommutative()`, etc.

## Implementation Structure

### Rust Code (`src/`)

- **`alg/op/operation.rs`**: Core `Operation` trait definition with all 17 methods
- **`alg/op/operation_symbol.rs`**: `OperationSymbol` struct with Python bindings
- **`alg/op/abstract_operation.rs`**: Base implementation providing common functionality
- **`alg/op/int_operation.rs`**: Table-based operation implementation for fast evaluation

### Python Bindings

All Rust structs are exposed to Python using PyO3:

```python
from uacalc_rust import OperationSymbol, AbstractOperation, IntOperation

# Create operation symbol
symbol = OperationSymbol("test", 2)
print(f"Symbol: {symbol.name}, Arity: {symbol.arity}")

# Create identity operation
identity = IntOperation.py_identity(3)
print(f"f(1) = {identity.evaluate([1])}")  # Output: f(1) = 1

# Create constant operation
constant = IntOperation.py_constant(2, 3, 1)
print(f"f(0,2) = {constant.evaluate([0, 2])}")  # Output: f(0,2) = 1
```

### Java Wrappers (`java_wrappers/`)

Compatibility wrappers for testing with existing Java UACalc code:

```java
import org.uacalc.alg.op.rust.RustOperationWrapper;

// Create operations
RustOperationWrapper identity = RustOperationWrapper.identity(3);
RustOperationWrapper constant = RustOperationWrapper.constant(2, 3, 1);

// Test properties
assert identity.isIdempotent();
assert constant.isCommutative();
```

## Key Features

### 1. Complete Operation Interface
- All 17 methods from Java Operation interface implemented
- Proper error handling with `Result<T, OperationError>` types
- Support for both table-based and computed operations

### 2. Table-Based Operations
- Fast lookup tables using Horner encoding
- Efficient evaluation for repeated computations
- Automatic table validation

### 3. Property Checking
- **Idempotent**: f(x,x,...,x) = x for all x
- **Associative**: (a ○ b) ○ c = a ○ (b ○ c) for binary operations
- **Commutative**: a ○ b = b ○ a for binary operations
- **Maltsev**: f(x,y,y) = x and f(x,x,y) = y for ternary operations

### 4. Multiple Evaluation Methods
- **Generic objects**: `value_at_objects()` for compatibility
- **Integer arrays**: `int_value_at()` for numeric operations
- **Horner encoding**: `int_value_at_horner()` for table-based fast access
- **Product operations**: `value_at_arrays()` for batch evaluation

## Usage Examples

### Creating Operations

```rust
use uacalc_rust::alg::op::*;

// Identity operation: f(x) = x
let identity = IntOperation::identity(3)?;

// Constant operation: f(x,y) = c
let constant = IntOperation::constant(2, 3, 1)?;

// Custom operation with lookup table
let table = vec![0, 1, 1, 0]; // XOR operation on {0,1}
let xor_op = IntOperation::new("xor".to_string(), 2, 2, table)?;
```

### Evaluating Operations

```rust
// Direct evaluation
let result = identity.int_value_at(&[2])?;  // Returns 2

// Table-based evaluation
let table_result = identity.int_value_at_horner(1)?;  // Returns 1

// Batch evaluation
let arrays = vec![vec![0, 1], vec![1, 0]].iter().map(|v| v.as_slice()).collect::<Vec<_>>();
let batch_result = xor_op.value_at_arrays(&arrays)?;  // Returns [1, 1]
```

### Property Checking

```rust
// Check if operation is idempotent
assert!(identity.is_idempotent()?);

// Check if binary operation is commutative
assert!(xor_op.is_commutative()?);

// Check if ternary operation is Maltsev
assert!(maltsev_op.is_maltsev()?);
```

## Building and Testing

### Rust Tests
```bash
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
cargo test
```

### Python Bindings
```bash
# Install maturin for building Python wheels
pip install maturin

# Build and install the Python module
maturin develop

# Test in Python
python -c "from uacalc_rust import OperationSymbol; print(OperationSymbol('test', 2))"
```

### Java Wrappers
```bash
cd java_wrappers
mvn test
```

## Performance Characteristics

- **Table Creation**: O(n^k) where n is set size and k is arity
- **Table Evaluation**: O(1) lookup time
- **Property Checking**: Varies by property, generally O(n^k) to O(n^(2k))
- **Memory Usage**: Tables require n^k integers of storage

## Error Handling

The implementation uses comprehensive error handling:

```rust
pub enum OperationError {
    InvalidArguments(String),
    NotImplemented(String),
    TableCreationFailed(String),
    // ... more error types
}
```

All fallible operations return `Result<T, OperationError>` for proper error propagation.

## Dependencies

- **Required**: `OperationSymbol` (Task 1) ✅ - Already implemented
- **Optional**: `Operations` (Task 50), `Horner` (Task 3), `ArrayString` (Task 6) - For enhanced functionality

## Compatibility

This implementation maintains full compatibility with the Java UACalc Operation interface while providing additional Rust safety guarantees and Python accessibility.

## Task Completion Status

- ✅ Operation trait implemented with all 17 methods
- ✅ Trait implements Ord, PartialOrd, Eq, PartialEq, Hash, Display
- ✅ Proper error handling with Result types
- ✅ AbstractOperation struct implementing Operation trait
- ✅ IntOperation struct for table-based operations
- ✅ Python bindings for concrete implementations
- ✅ Java wrappers for concrete implementations
- ✅ Rust tests pass with comprehensive coverage
- ✅ Python bindings tested and functional
- ✅ Code compiles without warnings
- ✅ Documentation complete with examples