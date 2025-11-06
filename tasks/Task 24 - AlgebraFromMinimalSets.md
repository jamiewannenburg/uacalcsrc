# Task 24: Translate `AlgebraFromMinimalSets`

**Java File:** `org/uacalc/alg/AlgebraFromMinimalSets.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::AlgebraFromMinimalSets`  
**Dependencies:** 4 (4 non-UI/example)  
**Estimated Public Methods:** 6

## Description
Translate the Java class `org.uacalc.alg.AlgebraFromMinimalSets` to Rust with Python bindings.

## Java File Analysis

### Class Structure
- **Type**: Concrete class extending `BasicAlgebra` and implementing `SmallAlgebra`
- **Public Methods**: 5 constructors + 1 static main method
- **Key Fields**: 
  - `SmallAlgebra minimalAlgebra` - the base minimal algebra
  - `int minAlgSize` - size of minimal algebra
  - `List<Integer> connectingPts` - connecting points
  - `int a, b` - connection indices
  - `List<int[]> maps` - mapping arrays
  - `int[] mapToB` - mapping from algebra to minimal algebra

### Dependencies Analysis
**Corrected Dependencies** (original list was incomplete):
- `org.uacalc.alg.op.Operation` - Operation interface
- `org.uacalc.alg.op.Operations` - Operations factory class
- `org.uacalc.alg.op.AbstractOperation` - Abstract operation implementation
- `org.uacalc.alg.op.OperationSymbol` - Operation symbol class
- `org.uacalc.alg.BasicAlgebra` - Parent class
- `org.uacalc.alg.SmallAlgebra` - Interface implemented
- `org.uacalc.alg.GeneralAlgebra` - Grandparent class
- `org.uacalc.alg.Algebra` - Great-grandparent interface

**Missing Dependencies** (not listed in original task):
- `org.uacalc.alg.BasicAlgebra` - Critical parent class dependency
- `org.uacalc.alg.SmallAlgebra` - Critical interface dependency
- `org.uacalc.alg.GeneralAlgebra` - Critical grandparent class dependency
- `org.uacalc.alg.Algebra` - Critical great-grandparent interface dependency

## Rust Implementation Recommendations

### Design Decisions
- **Rust Construct**: `struct` (concrete class)
- **Trait Implementation**: Implement `SmallAlgebra` trait
- **Inheritance**: Use composition instead of inheritance (Rust doesn't have inheritance)
- **Error Handling**: Use `Result<T, String>` for operations that can fail
- **Null Safety**: Use `Option<T>` instead of nullable references

### Struct Design
```rust
pub struct AlgebraFromMinimalSets {
    pub minimal_algebra: Box<dyn SmallAlgebra>,
    pub min_alg_size: usize,
    pub connecting_pts: Option<Vec<i32>>,
    pub a: usize,
    pub b: usize,
    pub maps: Vec<Vec<i32>>,
    pub map_to_b: Vec<i32>,
    // Inherited from BasicAlgebra/GeneralAlgebra
    pub name: Option<String>,
    pub size: usize,
    pub operations: Vec<Box<dyn Operation>>,
}
```

### Method Organization
- **Constructors**: Multiple `new` methods with different parameter combinations
- **Private Methods**: `make_default_maps()`, `make_map_to_b()`, `make_ops()`
- **Trait Methods**: Implement `SmallAlgebra` trait methods
- **Error Handling**: Provide both `_safe` and `_panic` versions of methods

### Generic vs Dynamic Dispatch
- **Dynamic Dispatch**: Use `Box<dyn SmallAlgebra>` for minimal algebra (polymorphic)
- **Dynamic Dispatch**: Use `Box<dyn Operation>` for operations (polymorphic)
- **Reasoning**: The Java code uses interface types, so dynamic dispatch is appropriate

## Java Wrapper Suitability
- **Suitable**: Yes - concrete class with public constructors and methods
- **Testing Strategy**: Create wrapper with all constructor variants and main method
- **CLI Commands**: 
  - `construct` - test all constructor variants
  - `test` - run basic functionality tests
  - `main` - test the static main method

## Implementation Priority
- **Priority**: HIGH (all dependencies complete)
- **Dependencies**: All critical dependencies are now available
- **Operation Dependencies**: `Operation`, `Operations`, `AbstractOperation`, `OperationSymbol` are all implemented

## Testing Strategy
- **Unit Tests**: Test all constructor variants and private methods
- **Integration Tests**: Test with different minimal algebra inputs
- **Error Tests**: Test invalid map configurations and inconsistent maps
- **Performance Tests**: Test with various algebra sizes
- **Cross-Language Tests**: Compare results with Java wrapper

## Critical Implementation Notes
1. **Map Validation**: The `makeMapToB()` method validates map consistency - implement proper error handling
2. **Default Maps**: The `makeDefaultMaps()` method creates 3 default maps (B, C, D) - ensure exact behavior match
3. **Operation Creation**: Operations are created dynamically based on minimal algebra operations - use trait objects
4. **Size Calculation**: Default size is `3 * minAlgSize - 2` - ensure exact calculation
5. **Connection Points**: Optional connecting points affect the `a` and `b` values - handle `None` case properly

## Implementation Status

**Current Status**: READY FOR IMPLEMENTATION - All dependencies complete
**Completion**: 5% (only placeholder struct exists)
**Last Updated**: 2025-10-27

### Implementation Components Status

#### Rust Implementation
- **Status**: NOT STARTED
- **Current State**: Only placeholder struct in `src/alg/mod.rs` (line 54-56)
- **Quality**: Poor (empty placeholder)
- **Notes**: Struct exists but has no implementation

#### Python Bindings  
- **Status**: NOT STARTED
- **Current State**: No bindings found in `uacalc_lib/src/`
- **Quality**: N/A
- **Notes**: No Python bindings implemented

#### Java Wrapper
- **Status**: NOT STARTED  
- **Current State**: No wrapper found in `java_wrapper/src/`
- **Quality**: N/A
- **Notes**: No Java wrapper implemented

#### Tests
- **Status**: NOT STARTED
- **Current State**: No tests found
- **Quality**: N/A
- **Notes**: No test implementation

### Dependency Analysis

#### Dependencies Status
1. **BasicAlgebra** - Parent class (✅ **COMPLETED**)
   - Java: `org.uacalc.alg.BasicAlgebra`
   - Rust: Implemented in `src/alg/basic_algebra.rs` (Task 71 - ✅ **COMPLETED**)
   - Status: READY

2. **SmallAlgebra** - Interface implemented (✅ **COMPLETED**)
   - Java: `org.uacalc.alg.SmallAlgebra`
   - Rust: Trait fully implemented in `src/alg/small_algebra.rs` (Task 41 - ✅ **COMPLETED**)
   - Status: READY

3. **GeneralAlgebra** - Grandparent class (✅ **COMPLETED**)
   - Java: `org.uacalc.alg.GeneralAlgebra`
   - Rust: Implemented in `src/alg/general_algebra.rs` (Task 66 - ✅ **COMPLETED**)
   - Status: READY

4. **Algebra** - Great-grandparent interface (IMPLEMENTED)
   - Java: `org.uacalc.alg.Algebra`
   - Rust: Trait exists in `src/alg/algebra.rs`
   - Status: READY

#### Operation Dependencies (READY)
1. **Operation** - Interface (IMPLEMENTED)
2. **Operations** - Factory class (IMPLEMENTED) 
3. **AbstractOperation** - Abstract implementation (IMPLEMENTED)
4. **OperationSymbol** - Symbol class (IMPLEMENTED)

### Critical Issues

1. **Missing BasicAlgebra**: The Java class extends `BasicAlgebra`, but Rust only has `BasicAlgebra`. Need to either:
   - Implement `BasicAlgebra` as a separate class, or
   - Modify `AlgebraFromMinimalSets` to extend `BasicAlgebra` instead

2. **Inheritance vs Composition**: Java uses inheritance, but Rust uses composition. Need to design proper composition structure.

3. **Dynamic Dispatch**: Java uses `SmallAlgebra` interface, Rust needs `Box<dyn SmallAlgebra>` for polymorphism.

### Recommendations

1. **IMMEDIATE**: Implement `BasicAlgebra` class or modify design to use `BasicAlgebra`
2. **NEXT**: Implement the core `AlgebraFromMinimalSets` struct with proper composition
3. **THEN**: Add Python bindings and Java wrapper
4. **FINALLY**: Add comprehensive tests

## Acceptance Criteria
- [ ] **BLOCKED** - All 5 public constructors translated to Rust (depends on BasicAlgebra)
- [ ] **BLOCKED** - Static main method translated to Rust (depends on BasicAlgebra)
- [ ] **BLOCKED** - All private methods (`makeDefaultMaps`, `makeMapToB`, `makeOps`) implemented (depends on BasicAlgebra)
- [ ] **READY** - `SmallAlgebra` trait properly implemented (trait exists)
- [ ] **BLOCKED** - Python bindings expose all public methods (depends on Rust implementation)
- [ ] **BLOCKED** - Java CLI wrapper created with all constructor variants (depends on Rust implementation)
- [ ] **BLOCKED** - Rust tests pass with timeouts enabled (depends on Rust implementation)
- [ ] **BLOCKED** - Python tests pass and match Java output (depends on implementations)
- [ ] **BLOCKED** - Code compiles without warnings (depends on BasicAlgebra)
- [ ] **BLOCKED** - Documentation complete (depends on implementation)
- [ ] **INCOMPLETE** - **Dependencies correctly listed and implemented first** (BasicAlgebra missing)
