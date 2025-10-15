# UACalc Rust/Python Translation Plan

## Overview

This plan contains the ordered list of translation tasks for converting the UACalc Java library to Rust with Python bindings. Tasks are ordered by dependency count to ensure foundational classes are translated before dependent classes.

## Translation Strategy

### Approach
- Direct Java-to-Rust translation maintaining exact semantics
- Use Rust idioms where appropriate (traits for interfaces, Result/Option, etc.)
- All public methods must be translated and tested
- Output must match Java implementation exactly

### Testing Strategy
- Rust tests for all public methods with timeouts
- Python binding tests comparing against Java
- Java CLI wrappers for ground truth comparison
- Global memory limit configurable from Python

### ExcluRded Packages
The following packages are **excluded** from this plan:
- `org.uacalc.ui.*` - UI components (not needed for core library)
- `org.uacalc.nbui.*` - NetBeans UI components
- `org.uacalc.example.*` - Example/demo classes (NOTE: To be implemented later)


## Translation Tasks

## Task 55: Translate `Algebra`

**Java File:** `org/uacalc/alg/Algebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::Algebra`  
**Dependencies:** 3 (2 non-UI/example)  
**Estimated Public Methods:** ~28

### Description
Translate the Java class `org.uacalc.alg.Algebra` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.op.Operation` (Task 12 - Operation)
- `org.uacalc.alg.op.OperationSymbol` (Task 1 - OperationSymbol) ✅ **COMPLETED**
- `org.uacalc.alg.op.SimilarityType` (Task 2 - SimilarityType) ✅ **COMPLETED**
- `org.uacalc.ui.tm.ProgressReport` (UI dependency - excluded from translation)

### Implementation Steps

1. **Analyze Java Implementation**
   - Read and understand the Java source code
   - Identify all public methods and their signatures
   - Note any special patterns (interfaces, abstract classes, etc.)
   - Identify dependencies on other UACalc classes

2. **Design Rust Translation**
   - Determine if Java interfaces should become Rust traits
   - Design struct/enum representations matching Java semantics
   - Plan for Rust idioms (Option instead of null, Result for errors, etc.)
   - Ensure all public methods are translated

3. **Implement Rust Code**
   - Create Rust module structure
   - Implement all public methods
   - Add comprehensive documentation
   - Follow Rust naming conventions (snake_case)

4. **Create Python Bindings (PyO3)**
   - Expose all public methods to Python
   - Use appropriate PyO3 types (PyResult, etc.)
   - Add Python docstrings

5. **Create Java CLI Wrapper**
   - Create wrapper in `java_wrapper/src/` matching package structure
   - Implement `main` method accepting command-line arguments
   - Expose all public methods through CLI commands
   - Output results in JSON/text format for comparison

6. **Write Rust Tests**
   - Test all public methods
   - Add tests with timeouts (slightly longer than Java completion times)
   - Test edge cases and error conditions
   - Compare results against Java CLI wrapper output

7. **Write Python Tests**
   - Test all public methods through Python bindings
   - Compare results against Java CLI wrapper output
   - Verify Python API matches Rust API

8. **Verification**
   - Run all tests and ensure they pass
   - Verify outputs match Java implementation exactly
   - Check test coverage for all public methods

### Java Class Analysis

**Class Type**: Interface
**Key Characteristics**:
- Defines the core contract for all algebras in UACalc
- Contains 28 public methods covering universe, operations, cardinality, and metadata
- Uses Java generics and collections extensively
- Has static constants for cardinality types
- Includes monitoring/progress reporting capabilities

**Critical Methods**:
- `universe()` - Returns the universe set (may be infinite)
- `cardinality()` - Returns cardinality or negative values for unknown/infinite
- `operations()` - Returns list of operations
- `getOperation(OperationSymbol)` - Gets operation by symbol
- `similarityType()` - Returns the similarity type
- `isSimilarTo(Algebra)` - Compares similarity types

### Rust Implementation Strategy

**Rust Construct**: Trait
**Design Approach**:
- Convert Java interface to Rust trait with associated types
- Use `Box<dyn Iterator<Item = T>>` for universe iteration (handles infinite algebras)
- Use `Result<Option<T>, String>` for operations that may fail
- Implement proper error handling for cardinality calculations
- Use `Arc<Mutex<>>` for thread-safe monitoring

**Key Design Decisions**:
1. **Universe Representation**: Use `Box<dyn Iterator<Item = T>>` to handle infinite algebras
2. **Cardinality Handling**: Use `Option<i32>` with special negative values for unknown/infinite
3. **Operation Access**: Use `HashMap<OperationSymbol, Box<dyn Operation>>` for efficient lookup
4. **Monitoring**: Create separate `ProgressMonitor` trait to avoid UI dependencies

### Implementation Requirements

**Prerequisites**:
- Task 12 (Operation) must be completed first
- Task 1 (OperationSymbol) is already completed ✅
- Task 2 (SimilarityType) is already completed ✅

**Core Trait Design**:
```rust
pub trait Algebra {
    type UniverseItem;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>>;
    fn cardinality(&self) -> Option<i32>;
    fn input_size(&self) -> Option<i32>;
    fn is_unary(&self) -> bool;
    fn operations(&self) -> Vec<Box<dyn Operation>>;
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>>;
    fn operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>>;
    fn name(&self) -> &str;
    fn set_name(&mut self, name: String);
    fn description(&self) -> Option<&str>;
    fn set_description(&mut self, desc: Option<String>);
    fn similarity_type(&self) -> &SimilarityType;
    fn update_similarity_type(&mut self);
    fn is_similar_to(&self, other: &dyn Algebra) -> bool;
    fn make_operation_tables(&mut self);
    fn constant_operations(&self) -> Vec<Box<dyn Operation>>;
    fn is_idempotent(&self) -> bool;
    fn is_total(&self) -> bool;
}
```

### Java Wrapper Suitability

**Suitability**: **NOT SUITABLE** for direct testing
**Reason**: Algebra is an interface that cannot be instantiated directly
**Alternative Strategy**: 
- Test through concrete implementations (GeneralAlgebra, SmallAlgebra, etc.)
- Create wrapper for GeneralAlgebra which implements Algebra
- Focus testing on interface contract compliance

### Testing Strategy

**Rust Tests**:
- Test through concrete implementations (GeneralAlgebra, SmallAlgebra)
- Verify trait method implementations
- Test edge cases (infinite algebras, unknown cardinality)
- Test error conditions and validation

**Python Tests**:
- Test through concrete algebra implementations
- Verify Python API matches Rust API
- Test cardinality edge cases
- Test operation lookup and management

### Critical Implementation Notes

1. **Infinite Algebra Support**: The interface is designed to handle infinite algebras, so iterator-based universe access is crucial
2. **Cardinality Constants**: Implement the special negative constants for unknown/infinite cardinality
3. **Thread Safety**: Use proper synchronization for monitoring and mutable state
4. **Memory Management**: Handle large algebras efficiently with proper memory management
5. **Error Handling**: Provide comprehensive error handling for all operations that can fail

### Acceptance Criteria
- [x] Algebra trait defined with all 28 methods ✅ **COMPLETED**
- [x] Concrete implementations (GeneralAlgebra, SmallAlgebra) implement the trait ✅ **COMPLETED**
- [x] Python bindings expose trait through concrete implementations ✅ **COMPLETED**
- [x] Java CLI wrapper created for GeneralAlgebra (implements Algebra) ✅ **COMPLETED**
- [x] Rust tests pass with timeouts enabled ✅ **COMPLETED**
- [x] Python tests pass and match Java output ✅ **COMPLETED**
- [x] Code compiles without warnings ✅ **COMPLETED**
- [x] Documentation complete ✅ **COMPLETED**
- [x] Proper error handling for all edge cases ✅ **COMPLETED**
- [x] Thread-safe implementation ✅ **COMPLETED**

### Implementation Status: ✅ **COMPLETED**

**Completed Components:**
- ✅ Algebra trait implemented in `src/alg/algebra.rs`
- ✅ GeneralAlgebra implementation in `src/alg/general_algebra.rs`
- ✅ BasicSmallAlgebra implementation in `src/alg/small_algebra.rs`
- ✅ Python bindings in `uacalc_lib/src/alg.rs` with PyGeneralAlgebra and PyBasicSmallAlgebra
- ✅ Java CLI wrappers: GeneralAlgebraWrapper and SimpleAlgebraWrapper
- ✅ All classes accessible through Python: `uacalc_lib.alg.GeneralAlgebra`, `uacalc_lib.alg.BasicSmallAlgebra`
- ✅ Cardinality constants exported: CARDINALITY_UNKNOWN, CARDINALITY_FINITE, etc.
- ✅ Compilation successful with no errors
- ✅ Runtime functionality verified through testing
