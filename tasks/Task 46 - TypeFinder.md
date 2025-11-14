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

## Task 46: Translate `TypeFinder`

**Java File:** `org/uacalc/alg/conlat/TypeFinder.java`  
**Package:** `org.uacalc.alg.conlat`  
**Rust Module:** `alg::conlat::TypeFinder`  
**Dependencies:** 3 (3 non-UI/example)  
**Estimated Public Methods:** ~15

### Description
Translate the Java class `org.uacalc.alg.conlat.TypeFinder` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.SmallAlgebra` (interface)
- `org.uacalc.alg.BigProductAlgebra` (class)
- `org.uacalc.alg.conlat.CongruenceLattice` (class)
- `org.uacalc.alg.conlat.Subtrace` (class)
- `org.uacalc.alg.conlat.Partition` (class)
- `org.uacalc.alg.op.Operation` (interface)
- `org.uacalc.util.IntArray` (class)
- `org.uacalc.util.SequenceGenerator` (class)
- `org.uacalc.util.ArrayIncrementor` (class)
- `org.uacalc.util.ArrayString` (class)

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

### Implementation Recommendations

#### Java Class Analysis
- **Type**: Concrete class (not interface or abstract)
- **Purpose**: Utility class for finding subtraces and TCT types in algebras
- **Key Features**: 
  - Reusable for efficiency (maintains state)
  - Works with join irreducible congruences
  - Implements complex algorithm for finding subtraces
  - Thread-safe considerations (interrupt handling)

#### Rust Implementation Design
- **Primary Construct**: `struct TypeFinder` (not trait)
- **State Management**: Mutable struct with internal state
- **Error Handling**: Use `Result<T, String>` for methods that can fail
- **Thread Safety**: Consider `Arc<Mutex<>>` for shared state if needed

#### Method Organization
- **Constructor**: `new(small_algebra: SmallAlgebra) -> Self`
- **Constructor with alpha**: `new_with_alpha(small_algebra: SmallAlgebra, alpha: Partition) -> Self`
- **Public Methods** (all should be translated):
  - `init()` -> `init() -> Result<(), String>`
  - `init(alpha: Partition)` -> `init_with_alpha(alpha: Partition) -> Result<(), String>`
  - `find_type_set()` -> `find_type_set() -> Result<HashSet<i32>, String>`
  - `is_subtrace(ia: IntArray, beta: Partition)` -> `is_subtrace(ia: IntArray, beta: Partition) -> Result<bool, String>`
  - `find_subtrace(beta: Partition)` -> `find_subtrace(beta: Partition) -> Result<Subtrace, String>`
  - `find_subtrace(beta: Partition, alpha: Partition)` -> `find_subtrace_with_alpha(beta: Partition, alpha: Partition) -> Result<Subtrace, String>`
  - `find_subtrace(ia: IntArray)` -> `find_subtrace_from_pair(ia: IntArray) -> Result<Subtrace, String>`
  - `next_pair_for_subtrace(...)` -> `next_pair_for_subtrace(...) -> Result<Option<IntArray>, String>`
  - `find_type(beta: Partition)` -> `find_type(beta: Partition) -> Result<i32, String>`
  - `find_type(beta: Partition, alpha: Partition)` -> `find_type_with_alpha(beta: Partition, alpha: Partition) -> Result<i32, String>`
  - `find_type(subtrace: Subtrace)` -> `find_type_from_subtrace(subtrace: Subtrace) -> Result<i32, String>`

#### Key Implementation Considerations
1. **State Management**: The class maintains significant internal state (visited sets, diagonal sets, etc.)
2. **Algorithm Complexity**: Implements complex graph traversal algorithms
3. **Memory Management**: Uses multiple collections (HashSet, List) that need careful Rust ownership
4. **Thread Interruption**: Java version checks `Thread.currentThread().isInterrupted()` - consider using `std::sync::atomic::AtomicBool` for cancellation
5. **Generic vs Dynamic Dispatch**: Use dynamic dispatch for `SmallAlgebra` and `Operation` interfaces
6. **Error Propagation**: Many methods can fail and should return `Result<T, String>`

#### Java Wrapper Suitability
- **Suitable**: Yes, this is a concrete class that can be instantiated and tested
- **Testing Strategy**: Create wrapper that can load algebras and test all public methods
- **Key Test Cases**: Test with different algebra types, edge cases for type finding

#### Dependencies Verification
- **Missing Dependencies**: The original dependency list was incomplete
- **Corrected Dependencies**: Added all specific classes that TypeFinder actually uses
- **Dependency Order**: Ensure all dependencies are translated before TypeFinder

### Current Implementation Status

**Status**: ✅ COMPLETE (Implemented 2025-10-27)

**Analysis Date**: 2025-10-27

#### Component Status
- **Rust Implementation**: ✅ Fully implemented in `src/alg/conlat/type_finder.rs`
- **Python Bindings**: ✅ Fully implemented in `uacalc_lib/src/alg.rs`
- **Java Wrapper**: ✅ Implemented in `java_wrapper/src/alg/conlat/TypeFinderWrapper.java`
- **Tests**: ✅ Implemented (Python tests in `python/uacalc/tests/test_type_finder.py`)

#### Dependency Analysis
**All Dependencies Complete**:
- `BigProductAlgebra` - ✅ **COMPLETED** (Task 78 - implemented in `src/alg/big_product_algebra.rs`)
- `CongruenceLattice` - ✅ **COMPLETED** (Task 80 - implemented in `src/alg/conlat/congruence_lattice.rs`)
- `Operation` interface - ✅ **COMPLETED** (Task 12 - fully implemented in `src/alg/op/operation.rs`)

**Ready Dependencies** (implemented):
- `SmallAlgebra` trait - ✅ Fully implemented
- `Subtrace` struct - ✅ Fully implemented with comprehensive tests
- `Partition` struct - ✅ Fully implemented with comprehensive functionality
- `IntArray` - ✅ Fully implemented with trait system
- `SequenceGenerator` - ✅ Fully implemented
- `ArrayIncrementor` - ✅ Fully implemented

#### Implementation Status
All critical dependencies are now complete. TypeFinder is ready for implementation.

#### Recommendations
1. **Priority 1**: Implement TypeFinder now that all dependencies are complete
2. **Priority 2**: Create comprehensive test suite for all TypeFinder methods
3. **Priority 3**: Verify integration with BigProductAlgebra and CongruenceLattice

### Acceptance Criteria
- [x] All public methods translated to Rust
- [x] Python bindings expose all public methods
- [x] Java CLI wrapper created with all public methods
- [x] Rust tests pass with timeouts enabled
- [x] Python tests pass and match Java output
- [x] Code compiles without warnings
- [x] Documentation complete
- [x] All dependencies correctly identified and translated
- [x] Thread safety considerations implemented
- [x] Memory management optimized for Rust ownership model
