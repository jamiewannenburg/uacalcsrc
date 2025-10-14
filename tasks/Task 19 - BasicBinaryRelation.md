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

## Task 19: Translate `BasicBinaryRelation`

**Java File:** `org/uacalc/alg/conlat/BasicBinaryRelation.java`  
**Package:** `org.uacalc.alg.conlat`  
**Rust Module:** `alg::conlat::BasicBinaryRelation`  
**Dependencies:** 1 (1 non-UI/example)  
**Estimated Public Methods:** ~14

### Description
Translate the Java class `org.uacalc.alg.conlat.BasicBinaryRelation` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.util.IntArray` - For representing pairs in the relation
- `org.uacalc.alg.conlat.BinaryRelation` - Interface that this class implements

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

### Implementation Analysis

#### Java Class Analysis
- **Type**: Concrete class implementing `BinaryRelation` interface
- **Key Features**: 
  - Uses `NavigableSet<IntArray>` for storing pairs
  - Implements relation composition, reflexivity, symmetry checks
  - Provides static factory methods (identity, universal, empty)
  - Implements `Comparable` and `Iterable` interfaces
- **Public Methods**: 12 methods including constructors, mutators, accessors, and static factory methods
- **Dependencies**: 
  - `org.uacalc.util.IntArray` - For pair representation
  - `org.uacalc.alg.conlat.BinaryRelation` - Interface implementation

#### Rust Translation Design
- **Rust Construct**: `struct BasicBinaryRelation` with trait implementations
- **Key Design Decisions**:
  - Uses `BTreeSet<IntArray>` for ordered pair storage (matches Java's NavigableSet)
  - Implements multiple traits: `BinaryRelation`, `MutableBinaryRelation`, `BinaryRelationCompare`, etc.
  - Provides both `_safe` and panic versions of methods for error handling
  - Uses `Result<(), String>` for proper error handling
- **Trait Organization**:
  - Core functionality in `BinaryRelation<IntArray>` trait
  - Mutation operations in `MutableBinaryRelation<IntArray>` trait
  - Comparison operations in `BinaryRelationCompare<IntArray>` trait
  - Factory methods in `BinaryRelationFactory<IntArray>` trait

#### Implementation Status Verification
- **Rust Implementation**: ✅ Complete and working (20 tests pass)
- **Python Bindings**: ✅ Complete with PyO3 integration
- **Java Wrapper**: ✅ Complete with comprehensive CLI interface
- **Dependencies**: ✅ All dependencies (IntArray, BinaryRelation) are translated
- **Testing**: ✅ Comprehensive test coverage for all public methods

#### Java Wrapper Suitability
- **Suitable**: ✅ Yes - Concrete class with all public methods accessible
- **Features**: 
  - Complete CLI interface for all public methods
  - JSON output for test comparison
  - Proper error handling and validation
  - Test command for comprehensive functionality verification

#### Testing Strategy
- **Rust Tests**: Unit tests with Java comparison using `compare_with_java!` macro
- **Python Tests**: Comprehensive test suite with Java wrapper comparison
- **Java Wrapper**: CLI-based testing with JSON output for validation
- **Coverage**: All public methods, edge cases, and error conditions tested

### Acceptance Criteria
- [x] All public methods translated to Rust
- [x] Python bindings expose all public methods
- [x] Java CLI wrapper created with all public methods
- [x] Rust tests pass with timeouts enabled
- [x] Python tests pass and match Java output
- [x] Code compiles without warnings
- [x] Documentation complete
