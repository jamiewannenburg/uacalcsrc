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

## Task 84: Translate `Closer`

**Java File:** `org/uacalc/alg/Closer.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::Closer`  
**Dependencies:** 11 (10 non-UI/example)  
**Estimated Public Methods:** ~56

### Description
Translate the Java class `org.uacalc.alg.Closer` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.conlat` (Partition)
- `org.uacalc.alg.op.AbstractOperation`
- `org.uacalc.alg.op.Operation`
- `org.uacalc.alg.op.OperationSymbol`
- `org.uacalc.alg.op.OperationWithDefaultValue`
- `org.uacalc.alg.op.Operations`
- `org.uacalc.alg.parallel.SingleClose`
- `org.uacalc.alg.CloserTiming`
- `org.uacalc.eq` (Equation)
- `org.uacalc.terms` (Term, Variable, NonVariableTerm)
- `org.uacalc.util` (IntArray)
- `org.uacalc.ui.tm.ProgressReport` (UI dependency - may need mock)

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

### Acceptance Criteria
- [x] Core structure translated to Rust (40% of methods)
- [x] Python bindings created for core functionality
- [x] Java CLI wrapper created for basic testing
- [ ] Rust tests pass with timeouts enabled (basic tests exist)
- [ ] Python tests pass and match Java output (not yet written)
- [x] Code compiles successfully (with warnings)
- [x] Basic documentation complete

### Current Implementation Status

**Status**: PARTIALLY IMPLEMENTED (~40% complete)

**Rust Implementation**: 
- ✅ **Core structure implemented** - `src/alg/closer.rs`
- ✅ **Basic closure algorithm** - `sg_close()` method with framework
- ✅ **Configuration methods** - Generators, term map, progress reporting, etc.
- ⚠️ **Partial implementation** - Core closure loop needs operation application logic
- Path: `src/alg/closer.rs`
- Quality: Fair - Structure is good, core algorithm needs completion

**Python Bindings**: 
- ✅ **Bindings created** - `uacalc_lib/src/alg_bindings.rs`
- ✅ **PyCloser class** - Full API exposed to Python
- ✅ **PyBigProductAlgebra** - Support class for Closer
- ✅ **PyIntArray** - Element wrapper
- Path: `uacalc_lib/src/alg_bindings.rs`
- Quality: Good - Full API coverage for partial implementation
- Note: Requires `maturin develop` to build (not executed due to environment)

**Java Wrapper**: 
- ✅ **Wrapper created** - `java_wrapper/src/alg/CloserWrapper.java`
- ✅ **Test command** - Basic functionality testing
- ✅ **sg_close command** - Closure computation
- Path: `java_wrapper/src/alg/CloserWrapper.java`
- Quality: Good - Basic testing capability
- Note: Requires `ant compile-wrappers` to build (not executed due to environment)

**Tests**: 
- ✅ **Rust unit tests** - Basic tests in `closer.rs`
- ❌ **Integration tests** - Not yet written
- ❌ **Python tests** - Not yet written
- Path: `src/alg/closer.rs` (unit tests)
- Quality: Fair - Basic coverage only

**Dependencies**:
- ✅ `CloserTiming` - **IMPLEMENTED** in `src/alg/closer_timing.rs`
- ⚠️ `BigProductAlgebra` - **PARTIALLY IMPLEMENTED** in `src/alg/big_product_algebra.rs`
- ❌ `SingleClose` - Not yet implemented (parallel processing)
- ✅ `Partition` - Fully implemented in `src/alg/conlat/partition.rs`
- ✅ `Equation` - Fully implemented in `src/eq/mod.rs`
- ✅ `Term`, `Variable`, `NonVariableTerm` - Fully implemented in `src/terms/mod.rs`
- ✅ `IntArray` - Fully implemented in `src/util/int_array.rs`
- ✅ `Operation`, `OperationSymbol` - Fully implemented in `src/alg/op/`
- ✅ `SmallAlgebra` - Fully implemented in `src/alg/small_algebra.rs`

**What Was Implemented**:
1. ✅ Core `Closer` struct with all configuration fields
2. ✅ `CloserTiming` for progress tracking (basic, no UI)
3. ✅ `BigProductAlgebra` structure and basic methods
4. ✅ Python bindings for all core functionality
5. ✅ Java wrapper for testing
6. ✅ Basic Rust unit tests

**What Remains**:
1. ❌ **Complete closure algorithm** - Operation application loop in `sg_close_impl()`
2. ❌ **Operation creation** - `BigProductAlgebra::make_operations()`
3. ❌ **Parallel processing** - `SingleClose` and parallel closure variants
4. ❌ **Advanced features**:
   - Constraint handling (blocks, values, congruence)
   - Homomorphism checking
   - Element finding during closure
   - Term map generation
5. ❌ **Integration tests** - Full end-to-end testing
6. ❌ **Python test suite** - Comprehensive Python tests
7. ❌ **Build verification** - Actually compile and run all components

**Recommendations**:
1. **Priority 1**: Complete the closure algorithm in `Closer::sg_close_impl()`
2. **Priority 2**: Implement operation creation in `BigProductAlgebra::make_operations()`
3. **Priority 3**: Write comprehensive integration tests
4. **Priority 4**: Build and test with `maturin develop` and `ant`
5. **Priority 5**: Implement advanced features (constraints, etc.)

**Estimated Effort**: Medium - Core structure is done, main work is completing algorithms

**Compilation Status**:
- ✅ Rust code compiles successfully with `cargo build`
- ⚠️ Python bindings not built (requires `maturin`, not available in environment)
- ⚠️ Java wrapper not compiled (requires `ant`, not available in environment)
- ✅ No blocking compilation errors

### Implementation Recommendations

#### Java Class Analysis
- **Type**: Concrete class (not interface or abstract)
- **Key Purpose**: Computes closure of elements under operations in algebras
- **Main Methods**: `sgClose()`, `sgClosePower()`, various configuration methods
- **Complexity**: High - contains complex algorithms for closure computation

#### Rust Implementation Strategy
- **Struct Design**: Convert to `pub struct Closer` with public fields for Python access
- **Error Handling**: Use `Result<T, String>` for methods that can fail
- **Threading**: Implement parallel processing using `rayon` crate
- **Memory Management**: Use `Vec` for collections, `HashMap` for maps
- **Progress Reporting**: Create trait for progress reporting to avoid UI dependency

#### Key Implementation Challenges
1. **Complex Closure Algorithms**: The `sgClose` and `sgClosePower` methods contain complex nested loops and state management
2. **Parallel Processing**: The class has parallel processing capabilities that need to be implemented in Rust
3. **Progress Reporting**: UI dependency needs to be abstracted into a trait
4. **Term Mapping**: Complex term generation and mapping logic
5. **Constraint Handling**: Multiple constraint types (blocks, values, congruence)

#### Dependencies Status
- **Missing Dependencies**: Several dependencies are not yet translated:
  - `CloserTiming` (needs translation)
  - `SingleClose` (needs translation) 
  - `Partition` from conlat (needs translation)
  - `Equation` from eq (needs translation)
  - `Term`, `Variable`, `NonVariableTerm` from terms (needs translation)
  - `IntArray` from util (needs translation)

#### Java Wrapper Suitability
- **Suitable**: Yes - concrete class with many public methods
- **Testing Strategy**: Can test all public methods through CLI wrapper
- **Key Methods to Test**:
  - Constructors (3 variants)
  - `sgClose()`, `sgClosePower()`
  - All setter/getter methods
  - Constraint configuration methods
  - Progress reporting methods

#### Testing Recommendations
- **Rust Tests**: Focus on core closure algorithms with small test cases
- **Python Tests**: Test all public methods through bindings
- **Java Wrapper Tests**: Comprehensive testing of all functionality
- **Performance Tests**: Test with larger algebras to verify performance
- **Edge Cases**: Test with empty generators, single elements, etc.

#### Critical Implementation Notes
1. **State Management**: The class maintains complex state during closure computation
2. **Early Termination**: Multiple conditions can cause early termination of closure
3. **Memory Usage**: Large closures can consume significant memory
4. **Thread Safety**: Parallel processing requires careful synchronization
5. **Progress Tracking**: Real-time progress reporting for long-running operations
