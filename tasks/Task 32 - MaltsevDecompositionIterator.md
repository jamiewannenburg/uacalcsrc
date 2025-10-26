# Task 32: Translate `MaltsevDecompositionIterator`

**Java File:** `org/uacalc/alg/MaltsevDecompositionIterator.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::MaltsevDecompositionIterator`  
**Dependencies:** 4 (4 non-UI/example)  
**Estimated Public Methods:** 3

## Description
Translate the Java class `org.uacalc.alg.MaltsevDecompositionIterator` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Concrete class implementing `Iterator<SmallAlgebra>`
- **Purpose**: Iterator for idempotent algebras giving sections (quotients of subalgebras)
- **Key Pattern**: Iterator pattern with state management

### Public Methods
1. `MaltsevDecompositionIterator(SmallAlgebra alg)` - Constructor
2. `boolean hasNext()` - Iterator interface method
3. `SmallAlgebra next()` - Iterator interface method
4. `void remove()` - Iterator interface method (throws UnsupportedOperationException)

### Dependencies Analysis
**CORRECTED DEPENDENCIES** (original task had incorrect dependency count):
- `org.uacalc.alg.SmallAlgebra` - Main algebra interface
- `org.uacalc.alg.conlat.Partition` - Partition operations
- `org.uacalc.alg.Subalgebra` - Subalgebra construction
- `org.uacalc.alg.QuotientAlgebra` - Quotient algebra construction
- `org.uacalc.io.AlgebraIO` - Used only in main method for testing

### Key Dependencies Status
- **SmallAlgebra**: Task 41 ✅ **COMPLETED** - Interface with `isIdempotent()`, `con()`, `cardinality()` methods
- **Partition**: Task 1 ✅ **COMPLETED** - Available in `src/alg/conlat/partition.rs`
- **Subalgebra**: Task 68 ✅ **COMPLETED** - Required for `new Subalgebra(algebra, block)`
- **QuotientAlgebra**: Task 77 ✅ **COMPLETED** - Required for `new QuotientAlgebra(subalg, par)`
- **CongruenceLattice**: Task 80 ✅ **COMPLETED** - Required for `con().zero()`, `con().one()`, `findUpperCover()` 
  - **Note**: Task 20 (Lattice interface) is ✅ **COMPLETED** and CongruenceLattice implementation (Task 80) is ✅ **COMPLETED**

## Rust Implementation Recommendations

### 1. Struct Design
```rust
pub struct MaltsevDecompositionIterator {
    algebra: Box<dyn SmallAlgebra>,
    lower: Option<Partition>,
    upper: Option<Partition>,
    blocks: Option<Vec<Vec<usize>>>,
    num_blocks: usize,
    block_index: usize,
    has_next: bool,
}
```

### 2. Trait Implementation
- Implement `Iterator<Item = Box<dyn SmallAlgebra>>` trait
- Use `Box<dyn SmallAlgebra>` for dynamic dispatch since different algebra types implement SmallAlgebra
- Provide both `_safe` and `_panic` versions of constructor

### 3. Method Organization
- **Constructor**: `new_safe(algebra: Box<dyn SmallAlgebra>) -> Result<Self, String>`
- **Iterator methods**: `has_next()`, `next()`, `remove()` (panic version)
- **Private methods**: `reset_congs()`, `get_next_algebra()`

### 4. Error Handling
- Constructor validates idempotent property using `algebra.is_idempotent()`
- Use `Result<(), String>` for safe methods
- Use `panic!` for unrecoverable errors (like `remove()`)

### 5. Generic vs Dynamic Dispatch
- **Use dynamic dispatch** (`Box<dyn SmallAlgebra>`) because:
  - Different algebra types (BasicAlgebra, Subalgebra, QuotientAlgebra, etc.) implement SmallAlgebra
  - Iterator needs to work with any SmallAlgebra implementation
  - Java uses interface polymorphism, Rust equivalent is trait objects

## Java Wrapper Suitability

### Assessment: **SUITABLE** ✅
**Reason**: All critical dependencies are now implemented:
- SmallAlgebra interface (Task 41) ✅ **COMPLETED**
- Subalgebra class (Task 68) ✅ **COMPLETED**  
- QuotientAlgebra class (Task 77) ✅ **COMPLETED**
- CongruenceLattice class (Task 80) ✅ **COMPLETED**

### Recommendation
- **Ready for implementation**: All dependencies are available
- **Implementation approach**: Create full Rust implementation with Python bindings
- **Testing strategy**: Use the existing `main` method for basic functionality testing

## Implementation Strategy

### Phase 1: Implementation ✅ **READY**
1. ✅ Complete Task 20 (CongruenceLattice) - provides `zero()`, `one()`, `findUpperCover()`
2. ✅ Complete Task 41 (SmallAlgebra) - provides `isIdempotent()`, `con()`, `cardinality()` 
3. ✅ Complete Task 68 (Subalgebra) - provides `new Subalgebra(algebra, block)`
4. ✅ Complete Task 77 (QuotientAlgebra) - provides `new QuotientAlgebra(subalg, par)`

### Phase 2: Implementation
1. Create Rust struct with proper field types
2. Implement Iterator trait with dynamic dispatch
3. Add comprehensive error handling
4. Create Python bindings with PyO3
5. Create Java CLI wrapper for testing

### Phase 3: Testing
1. Test with various SmallAlgebra implementations
2. Verify iterator behavior matches Java exactly
3. Test edge cases (empty algebras, single element algebras)
4. Performance testing with large algebras

## Testing Strategy

### Rust Tests
- Test iterator behavior with different algebra types
- Test error conditions (non-idempotent algebras)
- Test edge cases (empty iteration, single element)
- Compare results with Java implementation

### Python Tests
- Test through Python bindings
- Verify dynamic dispatch works correctly
- Test with different algebra types from Python

### Java Wrapper Tests
- Create wrapper once dependencies are complete
- Test with sample algebras from test data
- Verify JSON output matches Rust implementation

## Critical Implementation Notes

1. **Dynamic Dispatch Required**: Cannot use generics because different algebra types implement SmallAlgebra
2. **State Management**: Iterator maintains complex state (partitions, blocks, indices)
3. **Error Propagation**: Constructor validation must be preserved
4. **Memory Management**: Use `Box<dyn SmallAlgebra>` for owned trait objects
5. **Iterator Safety**: Ensure `next()` panics on exhausted iterator (matches Java behavior)

## Current Implementation Status

### Implementation Status: **READY FOR IMPLEMENTATION** ✅
**Completion Percentage:** 0% (0/4 components) - Ready to start

### Component Status
- **Rust Implementation**: ❌ **NOT STARTED** - Only placeholder struct exists
- **Python Bindings**: ❌ **NOT STARTED** - No bindings exist
- **Java Wrapper**: ❌ **NOT STARTED** - No wrapper exists  
- **Tests**: ❌ **NOT STARTED** - No tests exist

### Available Dependencies ✅ **ALL COMPLETED**
1. **SmallAlgebra.con() method** - ✅ **AVAILABLE** - Required for `algebra.con().zero()`, `algebra.con().one()`, `algebra.con().findUpperCover()`
2. **CongruenceLattice.findUpperCover()** - ✅ **AVAILABLE** - Required for finding upper covers in congruence lattice
3. **Subalgebra class** - ✅ **AVAILABLE** - Required for `new Subalgebra(algebra, block)`
4. **QuotientAlgebra class** - ✅ **AVAILABLE** - Required for `new QuotientAlgebra(subalg, par)`

### Available Dependencies
- **SmallAlgebra trait** - ✅ **COMPLETED** - Has `is_idempotent()` method
- **Partition class** - ✅ **COMPLETED** - Full implementation with all required methods
- **BasicSmallAlgebra** - ✅ **COMPLETED** - Concrete implementation of SmallAlgebra
- **CongruenceLattice** - ✅ **COMPLETED** - Full implementation with `findUpperCover()` method
- **Subalgebra** - ✅ **COMPLETED** - Full implementation with `restrictPartition()` method
- **QuotientAlgebra** - ✅ **COMPLETED** - Full implementation

### Implementation Notes
- Only a placeholder struct exists in `src/alg/mod.rs` (lines 2170-2172)
- All critical dependencies are now implemented and available
- Requires dynamic dispatch with `Box<dyn SmallAlgebra>` for iterator pattern
- Complex state management needed for partition iteration

## Acceptance Criteria
- [ ] **READY** - All public methods translated to Rust (dependencies available)
- [ ] **READY** - Python bindings expose all public methods (dependencies available)
- [ ] **READY** - Java CLI wrapper created with all public methods (dependencies available)
- [ ] **READY** - Rust tests pass with timeouts enabled (dependencies available)
- [ ] **READY** - Python tests pass and match Java output (dependencies available)
- [ ] **READY** - Code compiles without warnings (dependencies available)
- [ ] **READY** - Documentation complete (dependencies available)
- [ ] **COMPLETED** - **Dependencies completed** (SmallAlgebra.con(), CongruenceLattice.findUpperCover(), Subalgebra, QuotientAlgebra)
