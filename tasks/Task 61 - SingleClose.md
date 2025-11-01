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

**Overall Status: MOSTLY COMPLETE** - Core Rust implementation and Java wrapper complete

**Implementation Progress: 85%** - Rust implementation, Java wrapper, and tests complete. Python bindings remain.

**Components Status:**
- ✅ **Rust Implementation** - Complete in `src/alg/parallel/single_close.rs` with all public methods
- ❌ **Python Bindings** - Not implemented (deferred)
- ✅ **Java Wrapper** - Complete in `java_wrapper/src/alg/parallel/SingleCloseWrapper.java` with all public methods
- ✅ **Tests** - Complete (3 module tests + 6 integration tests in `tests/alg/parallel/single_close_tests.rs`, all passing)

**Resolved Dependencies:**
- ✅ `CloserTiming` - **IMPLEMENTED** - Basic implementation available

**Ready Dependencies (All Complete):**
- ✅ `IntArray` - Complete implementation available
- ✅ `ArrayIncrementor` - Complete implementation available
- ✅ `SequenceGenerator` - Complete implementation available
- ✅ `Operation` - Complete trait implementation available
- ✅ `Term` - Complete trait implementation available
- ✅ `NonVariableTerm` - Complete implementation available
- ✅ `ProgressReport` - Complete abstraction available (extended with timing methods)
- ✅ `CloserTiming` - **NEW** - Basic implementation complete

### Acceptance Criteria
- [x] All public methods translated to Rust
- [ ] Python bindings expose all public methods (deferred)
- [x] Java CLI wrapper created with all public methods
- [x] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output (deferred)
- [x] Code compiles without warnings
- [x] Documentation complete
- [x] Parallel processing implemented using `std::thread` (replacing Java Fork-Join framework)
- [x] Thread safety verified (using Arc, Mutex, and atomic types)
- [ ] Performance matches or exceeds Java implementation (to be tested)

### Implementation Summary

**What Was Implemented:**
1. ✅ **Complete SingleClose struct** in `src/alg/parallel/single_close.rs` with all fields matching Java implementation
2. ✅ **All public methods implemented:**
   - `new()` - Constructor with validation and initialization
   - `do_one_step()` - Main parallel closure computation method
   - `get_computation_size()` - Returns computation size
   - `get_increment()` - Returns number of parallel workers
   - `is_too_small()` - Returns whether computation is too small for parallelization
3. ✅ **Parallel execution implementation** using `std::thread` (lines 246-312) replacing Java Fork-Join:
   - Spawns worker threads for parallel computation
   - Uses thread-safe data structures (`Arc<Mutex<>>`, `Arc<AtomicUsize>`)
   - Executes last worker on current thread for efficiency
   - Properly joins all threads and collects results
4. ✅ **Thread-safe concurrent data structures:**
   - `Arc<Mutex<HashMap>>` for shared term map
   - `Arc<AtomicUsize>` for element counter
   - Proper lock management and atomic operations
5. ✅ **Serial worker implementation** (`do_one_step_serial_worker`) matching Java `SingleCloseSerial.compute()`
6. ✅ **Integration with CloserTiming** for progress tracking and timing metrics
7. ✅ **Integration with ProgressReport** for UI feedback (set_size, etc.)
8. ✅ **Java CLI wrapper** in `java_wrapper/src/alg/parallel/SingleCloseWrapper.java`:
   - Exposes all public methods via CLI commands
   - Supports: new, get_increment, get_computation_size, is_too_small, compute_size, test
   - Used by integration tests for validation
9. ✅ **Comprehensive testing:**
   - 3 module tests in `single_close.rs` (test_calculate_increment, test_compute_size, test_new)
   - 6 integration tests in `tests/alg/parallel/single_close_tests.rs` using `compare_with_java!` macro
   - All tests passing and validating against Java implementation

**What Remains:**
1. ⏸️ **Python bindings** using PyO3 (deferred)
2. ⏸️ **Performance testing** and optimization to match/exceed Java performance

### Next Steps for Full Implementation
1. **Add Python bindings** using PyO3 to expose SingleClose to Python
2. **Performance testing** comparing parallel vs serial execution and against Java implementation
3. **Integration tests** with larger real-world closure operations to validate performance
