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

## Task 21: Translate `BinaryRelation`

**Java File:** `org/uacalc/alg/conlat/BinaryRelation.java`  
**Package:** `org.uacalc.alg.conlat`  
**Rust Module:** `alg::conlat::BinaryRelation`  
**Dependencies:** 1 (1 non-UI/example)  
**Estimated Public Methods:** ~5

### Description
Translate the Java interface `org.uacalc.alg.conlat.BinaryRelation` to Rust with Python bindings.

### Dependencies
This interface depends on:
- `org.uacalc.util.IntArray` (translated)

### Implementation Analysis

#### Java Interface Analysis
- **Type**: Interface extending `Iterable<IntArray>` and `Comparable`
- **Public Methods**: 4 methods (not 5 as estimated)
  - `universeSize()` - Get the size of the universe
  - `isRelated(int i, int j)` - Check if elements are related
  - `getPairs()` - Get all pairs as NavigableSet<IntArray>
  - `compose(BinaryRelation beta)` - Compose with another relation
- **Dependencies**: Only depends on `IntArray` (which has been translated)
- **Implementations**: `BasicBinaryRelation` and `Partition` implement this interface

#### Rust Translation Design
- **Trait Design**: Converted to `BinaryRelation<T>` trait with generic type parameter
- **Method Organization**: All 4 methods translated to trait methods
- **Additional Functionality**: Extended with helper traits:
  - `MutableBinaryRelation<T>` - For adding/removing pairs
  - `BinaryRelationCompare<T>` - For comparison operations
  - `BinaryRelationIterator<T>` - For iteration over pairs
  - `BinaryRelationFactory<T>` - For creating common relations
- **Error Handling**: Uses `Result<(), String>` for operations that can fail
- **Type Safety**: Generic over `IntArray` type with trait bounds

#### Implementation Status
- **Rust Implementation**: ✅ Complete - Comprehensive trait system implemented
- **Python Bindings**: ✅ Complete - Full PyO3 bindings for BasicBinaryRelation
- **Java Wrapper**: ✅ Complete - BasicBinaryRelationWrapper provides CLI access to interface methods
- **Dependencies**: ✅ All dependencies (IntArray) are translated
- **Testing**: ✅ Comprehensive test coverage in both Rust and Python

#### Dependencies Analysis
- **Correctly Identified**: ✅ Yes - Only depends on `IntArray`
- **Status**: `IntArray` has been translated and is available
- **No Missing Dependencies**: ✅ Confirmed through code analysis

#### Java Wrapper Suitability
- **Suitable**: ✅ Yes - BasicBinaryRelationWrapper provides comprehensive CLI access
- **Reason**: `BinaryRelation` is an interface, but `BasicBinaryRelation` implements it
- **Implementation**: `BasicBinaryRelationWrapper` exposes all interface methods through CLI
- **Coverage**: All interface methods are tested through concrete implementation wrapper

#### Testing Strategy
- **Rust Tests**: Comprehensive testing through `BasicBinaryRelation` implementation
- **Python Tests**: Testing through concrete implementations that implement the trait
- **Java Wrapper**: Not applicable for interface - testing done through `BasicBinaryRelation` wrapper
- **Coverage**: All trait methods are covered through implementation testing

### Implementation Steps

1. **Analyze Java Implementation** ✅
   - Read and understand the Java source code
   - Identify all public methods and their signatures
   - Note any special patterns (interfaces, abstract classes, etc.)
   - Identify dependencies on other UACalc classes

2. **Design Rust Translation** ✅
   - Determine if Java interfaces should become Rust traits
   - Design struct/enum representations matching Java semantics
   - Plan for Rust idioms (Option instead of null, Result for errors, etc.)
   - Ensure all public methods are translated

3. **Implement Rust Code** ✅
   - Create Rust module structure
   - Implement all public methods
   - Add comprehensive documentation
   - Follow Rust naming conventions (snake_case)

4. **Create Python Bindings (PyO3)** ✅
   - Expose all public methods to Python
   - Use appropriate PyO3 types (PyResult, etc.)
   - Add Python docstrings

5. **Create Java CLI Wrapper** ✅
   - BasicBinaryRelationWrapper provides comprehensive CLI access
   - All interface methods exposed through concrete implementation

6. **Write Rust Tests** ✅
   - Test all public methods through concrete implementations
   - Add tests with timeouts (slightly longer than Java completion times)
   - Test edge cases and error conditions
   - Compare results against Java CLI wrapper output

7. **Write Python Tests** ✅
   - Test all public methods through Python bindings
   - Compare results against Java CLI wrapper output
   - Verify Python API matches Rust API

8. **Verification** ✅
   - Run all tests and ensure they pass
   - Verify outputs match Java implementation exactly
   - Check test coverage for all public methods

### Acceptance Criteria
- [x] All public methods translated to Rust
- [x] Python bindings expose all public methods
- [x] Java CLI wrapper created with all public methods
- [x] Rust tests pass with timeouts enabled
- [x] Python tests pass and match Java output
- [x] Code compiles without warnings
- [x] Documentation complete
