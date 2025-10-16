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

## Task 61: Translate `SingleClose`

**Java File:** `org/uacalc/alg/parallel/SingleClose.java`  
**Package:** `org.uacalc.alg.parallel`  
**Rust Module:** `alg::parallel::SingleClose`  
**Dependencies:** 8 (7 non-UI/example)  
**Estimated Public Methods:** 3

### Description
Translate the Java class `org.uacalc.alg.parallel.SingleClose` to Rust with Python bindings.

### Java Class Analysis
- **Type**: Concrete class extending `RecursiveTask<List<List<IntArray>>>`
- **Purpose**: Performs one pass of partial closure with a single Operation using a parallel algorithm
- **Key Features**: 
  - Uses Java's Fork-Join framework for parallel computation
  - Manages concurrent access to shared data structures
  - Handles progress reporting and timing
  - Creates and manages multiple `SingleCloseSerial` tasks

### Dependencies
This class depends on:
- `org.uacalc.util.IntArray` - Array representation
- `org.uacalc.util.ArrayIncrementor` - Interface for array incrementing
- `org.uacalc.util.SequenceGenerator` - Static methods for sequence generation
- `org.uacalc.alg.op.Operation` - Operation interface
- `org.uacalc.terms.Term` - Term representation
- `org.uacalc.terms.NonVariableTerm` - Non-variable term implementation
- `org.uacalc.alg.CloserTiming` - Timing and progress tracking
- `org.uacalc.ui.tm.ProgressReport` - Progress reporting interface

### Dependencies Status
- ✅ `IntArray` - **COMPLETED** - Full implementation in `src/util/int_array.rs`
- ✅ `ArrayIncrementor` - **COMPLETED** - Full implementation in `src/util/array_incrementor.rs`
- ✅ `SequenceGenerator` - **COMPLETED** - Full implementation in `src/util/sequence_generator.rs`
- ✅ `Operation` - **COMPLETED** - Full trait implementation in `src/alg/op/operation.rs`
- ✅ `Term` - **COMPLETED** - Full trait implementation in `src/terms/mod.rs`
- ✅ `NonVariableTerm` - **COMPLETED** - Full implementation in `src/terms/mod.rs`
- ❌ `CloserTiming` - **MISSING** - Not yet implemented
- ✅ `ProgressReport` - **COMPLETED** - Abstraction implemented in `src/progress.rs`

### Rust Implementation Strategy

#### Struct Design
```rust
pub struct SingleClose {
    univ_list: Vec<IntArray>,
    map: Arc<Mutex<HashMap<IntArray, Term>>>,
    op: Box<dyn Operation>,
    min: usize,
    max: usize,
    elts_found: Arc<AtomicUsize>,
    increment: usize,
    computation_size: u64,
    too_small: bool,
    arrays: Vec<Vec<usize>>,
    incrementor_list: Vec<Box<dyn ArrayIncrementor>>,
    results: Vec<Vec<IntArray>>,
}
```

#### Key Implementation Challenges
1. **Parallel Processing**: Replace Java's Fork-Join with `rayon` crate
2. **Concurrent Data Structures**: Use `Arc<Mutex<>>` and `Arc<RwLock<>>` for thread safety
3. **Progress Reporting**: Create trait abstraction to avoid UI dependency
4. **Generic Operations**: Use trait objects or generics for `Operation`
5. **Memory Management**: Handle large computation sizes with proper memory management

#### Method Translation
- `new()` → `new()` - Constructor with validation
- `new_with_increment()` → `new_with_increment()` - Constructor with custom increment
- `do_one_step()` → `do_one_step()` - Main computation method
- `compute()` → `compute()` - RecursiveTask implementation (internal)

### Java Wrapper Suitability
✅ **Suitable** - This is a concrete class with public methods that can be easily wrapped for testing.

### Testing Strategy
1. **Rust Tests**: Focus on core parallel computation logic with small test cases
2. **Python Tests**: Test all public methods through bindings
3. **Java Wrapper Tests**: Comprehensive functionality testing with larger datasets
4. **Performance Tests**: Compare parallel vs serial performance
5. **Concurrency Tests**: Verify thread safety and proper synchronization

### Implementation Steps

1. **Analyze Java Implementation**
   - ✅ Read and understand the Java source code
   - ✅ Identify all public methods and their signatures
   - ✅ Note special patterns (RecursiveTask, parallel processing)
   - ✅ Identify dependencies on other UACalc classes

2. **Design Rust Translation**
   - Design struct representation matching Java semantics
   - Plan for Rust idioms (Arc<Mutex<>>, rayon, etc.)
   - Create trait abstractions for UI dependencies
   - Ensure all public methods are translated

3. **Implement Rust Code**
   - Create Rust module structure
   - Implement all public methods with proper error handling
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

### Current Implementation Status

**Overall Status: BLOCKED** - Missing CloserTiming dependency

**Implementation Progress: 0%** - Only placeholder struct exists

**Components Status:**
- ❌ **Rust Implementation** - Only placeholder struct in `src/alg/parallel/mod.rs`
- ❌ **Python Bindings** - Not implemented
- ❌ **Java Wrapper** - Not implemented  
- ❌ **Tests** - Not implemented

**Blocking Dependencies:**
- `CloserTiming` - Required for timing and progress tracking functionality

**Ready Dependencies:**
- `IntArray` - ✅ Complete implementation available
- `ArrayIncrementor` - ✅ Complete implementation available
- `SequenceGenerator` - ✅ Complete implementation available
- `Operation` - ✅ Complete trait implementation available
- `Term` - ✅ Complete trait implementation available
- `NonVariableTerm` - ✅ Complete implementation available
- `ProgressReport` - ✅ Complete abstraction available

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Parallel processing works correctly
- [ ] Thread safety verified
- [ ] Performance matches or exceeds Java implementation

### Next Steps
1. **Implement CloserTiming** - Create timing and progress tracking struct
2. **Implement SingleClose** - Translate Java class to Rust with parallel processing
3. **Add Python bindings** - Expose functionality through PyO3
4. **Create Java wrapper** - CLI wrapper for testing
5. **Write comprehensive tests** - Rust, Python, and integration tests
