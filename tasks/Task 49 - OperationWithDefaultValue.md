# Task 49: Translate `OperationWithDefaultValue`

**Java File:** `org/uacalc/alg/op/OperationWithDefaultValue.java`  
**Package:** `org.uacalc.alg.op`  
**Rust Module:** `alg::op::OperationWithDefaultValue`  
**Dependencies:** 6 (5 non-UI/example)  
**Estimated Public Methods:** ~23

### Description
Translate the Java class `org.uacalc.alg.op.OperationWithDefaultValue` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.op.AbstractOperation` (Task 11) - ✅ **COMPLETED** - Parent class
- `org.uacalc.alg.op.Operation` (Task 12) - ✅ **COMPLETED** - Interface implemented by parent
- `org.uacalc.alg.op.OperationSymbol` (Task 1) - ✅ **COMPLETED** - Already implemented
- `org.uacalc.alg.op.Operations` (Task 50) - ✅ **COMPLETED** - Static utility methods (being implemented)
- `org.uacalc.util.Horner` (Task 3) - ✅ **COMPLETED** - Already implemented
- `org.uacalc.ui.util.RandomGenerator` - UI utility (excluded - using Rust rand crate instead)

**Note**: `ArrayString` is imported but not used in the implementation.

### Java Class Analysis

**Type**: Concrete class extending `AbstractOperation`
**Purpose**: Convenience class for UI that wraps operations with default value handling
**Key Features**:
- Wraps an `Operation` with default value semantics
- Supports random value generation for undefined entries
- Provides idempotent operation support
- Can convert to ordinary operations by filling in default values

**Public Methods** (23 methods):
1. **Constructors** (6): Various constructors for different initialization patterns
2. **Value Access** (3): `intValueAt(int[])`, `intValueAt(int)`, `valueAt(List)`
3. **Default Value Management** (3): `getDefaultValue()`, `setDefaultValue(int)`, `isTotal()`
4. **Random Value Management** (2): `updateRandomValueTable()`, `getRandomValueTable()`
5. **Idempotent Operations** (3): `isIdempotentSet()`, `setIdempotent(boolean)`, `makeIdempotent()`
6. **Diagonal Operations** (1): `isDiagonal(int, int)`
7. **Table Operations** (3): `makeTable()`, `getTotalTable()`, `makeOrdinaryOperation()`
8. **Static Methods** (1): `makeOrdinary(List<Operation>)`
9. **Inherited Methods**: All methods from `AbstractOperation` and `Operation`

### Rust Implementation Recommendations

**Struct Design**: Concrete struct implementing `Operation` trait through `AbstractOperation` trait
**Pattern**: Wrapper struct that delegates to internal `Operation` and adds default value logic

```rust
pub struct OperationWithDefaultValue {
    // Core operation being wrapped
    op: Box<dyn Operation>,
    // Default value (-1 = undefined, -2 = random, >=0 = specific value)
    default_value: i32,
    // Random value table for undefined entries
    random_value_table: Option<Vec<i32>>,
    // Idempotent operation support
    idempotent_set: bool,
    // Diagonal indices for idempotent operations
    diag_indices: Option<Vec<i32>>,
    // Diagonal divisor for diagonal checking
    diag_div: i32,
    // Random number generator
    random: std::collections::hash_map::DefaultHasher,
}
```

**Trait Implementation**: Implement `Operation` trait by delegating to internal `Operation`
**Method Organization**: 
- Core methods as struct methods
- Inherited methods through trait delegation
- Static methods as associated functions

**Generic vs Dynamic Dispatch**: Use dynamic dispatch (`Box<dyn Operation>`) for flexibility
**Error Handling**: Use `Result<T, String>` for methods that can fail, `Option<T>` for nullable returns

### Java Wrapper Suitability

**SUITABLE** - This is a concrete class that can be instantiated and tested
**Testing Strategy**: 
- Test all constructors with various parameter combinations
- Test default value handling (undefined, specific, random)
- Test idempotent operations
- Test table operations and conversions
- Test static utility methods

### Implementation Dependencies

**Blocking Dependencies**:
- `AbstractOperation` (Task 11) - Parent class must be implemented first
- `Operation` (Task 12) - Interface must be implemented first  
- `Operations` (Task 50) - Static utility methods required

**Available Dependencies**:
- `OperationSymbol` (Task 1) - ✅ Already implemented
- `Horner` (Task 3) - ✅ Already implemented

### Usage Pattern Analysis

**Primary Usage**: UI convenience class for operation editing and manipulation
**Common Patterns**:
- Wrapping existing operations with default value semantics
- Converting between partial and total operations
- Random value generation for testing
- Idempotent operation creation

**Integration Points**:
- Used in `AlgebraEditor` for operation management
- Used in `OperationTableModel` for UI display
- Used in `Closer` for algorithm operations
- Used in `BasicAlgebra` for operation wrapping

### Testing Strategy

**Rust Tests**:
- Test all constructors with various parameter combinations
- Test default value handling scenarios
- Test random value generation
- Test idempotent operations
- Test table operations and conversions
- Test static utility methods
- Compare results against Java implementation

**Python Tests**:
- Test all public methods through Python bindings
- Test default value behavior
- Test random value generation
- Test idempotent operations
- Verify Python API matches Rust API

**Java Wrapper Tests**:
- Test all constructors
- Test default value operations
- Test random value generation
- Test idempotent operations
- Test table operations
- Test static utility methods

### Acceptance Criteria
- [x] All public methods translated to Rust ✅
- [x] Python bindings expose all public methods ✅
- [x] Java CLI wrapper present; used for comparison where applicable ✅
- [x] Rust tests pass with timeouts enabled ✅
- [x] Python tests pass and match Java behavior ✅
- [x] Documentation complete ✅
- [x] Default value handling works correctly ✅
- [x] Random value generation works correctly ✅
- [x] Idempotent operations work correctly ✅
- [x] Table operations work correctly ✅
- [x] Static utility methods work correctly ✅

### Implementation Status: ✅ **COMPLETED**
- All core functionality implemented in `src/alg/op/operation_with_default_value.rs`
- Python bindings implemented with Java-style overloads (`int_value_at` supports list or single int)
- Java wrapper used as interface; minor wrapper-side normalizations applied
- Comprehensive Python tests implemented in `python/uacalc/tests/test_operation_with_default_value.py`
- All dependencies (AbstractOperation, Operations, OperationSymbol, Horner) are implemented and available
- Full Operation trait implementation with all required methods
- Static utility methods implemented and working
