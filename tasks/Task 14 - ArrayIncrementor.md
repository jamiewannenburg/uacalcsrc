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

## Task 14: Translate `ArrayIncrementor`

**Java File:** `org/uacalc/util/ArrayIncrementor.java`  
**Package:** `org.uacalc.util`  
**Rust Module:** `util::ArrayIncrementor`  
**Dependencies:** 0 (0 non-UI/example)  
**Estimated Public Methods:** ~1

### Description
Translate the Java class `org.uacalc.util.ArrayIncrementor` to Rust with Python bindings.

### Dependencies
No dependencies on other UACalc classes (leaf node).

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

### Analysis Results

**Java Class Analysis:**
- **Type**: Interface (not abstract class or concrete class)
- **Public Methods**: 1 method (`increment()`)
- **Dependencies**: 0 direct dependencies on other UACalc classes
- **Usage Pattern**: Used extensively throughout the codebase as a trait/interface for array iteration

**Dependency Analysis:**
- **Correct Dependencies**: ✅ Yes - No dependencies on other UACalc classes
- **Usage Found**: ArrayIncrementor is used in:
  - `SequenceGenerator.java` - Creates various incrementor implementations
  - `PermutationGenerator.java` - Creates array and list incrementors
  - Multiple algorithm classes (SubalgebraLattice, SingleClose, etc.)
  - UI components (OperationTableModel)
  - Example classes (TupleStream, Michalewski, HasKaryNU)

**Rust Implementation Analysis:**
- **Current Implementation**: ✅ Complete
  - `ArrayIncrementor` trait defined in `src/util/array_incrementor.rs`
  - `ArrayIncrementorImpl` struct implementing the trait
  - `SimpleArrayIncrementor` struct for basic array incrementing
  - All methods properly translated with Rust idioms

**Python Bindings Analysis:**
- **Current Implementation**: ✅ Complete
  - `PyArrayIncrementorImpl` and `PySimpleArrayIncrementor` classes
  - All methods exposed with proper error handling
  - Clean export names (no Py prefix)
  - Proper Python magic methods implemented

**Java Wrapper Analysis:**
- **Current Implementation**: ✅ Complete
  - `ArrayIncrementorWrapper.java` exists and is functional
  - Exposes both array and list incrementor functionality
  - Proper CLI interface with help, test, and specific commands
  - Uses `PermutationGenerator` to create concrete implementations

**Testing Analysis:**
- **Rust Tests**: ✅ Complete - `tests/util/array_incrementor_tests.rs`
- **Python Tests**: ✅ Complete - `python/uacalc/tests/test_array_incrementor.py`
- **Test Coverage**: All public methods tested with Java comparison

**Implementation Recommendations:**
1. **Rust Design**: ✅ Correctly implemented as trait + struct implementations
2. **Method Organization**: ✅ Trait methods properly defined, struct methods for construction
3. **Generic vs Dynamic Dispatch**: ✅ Uses trait objects appropriately
4. **Java Wrapper Suitability**: ✅ Suitable - interface can be tested through concrete implementations
5. **Testing Strategy**: ✅ Comprehensive cross-language testing implemented

**Verification Status:**
- All acceptance criteria are properly met
- Implementation follows Rust idioms and patterns
- Python bindings are complete and functional
- Java wrapper provides adequate testing interface
- Cross-language compatibility verified

### Acceptance Criteria
- [x] All public methods translated to Rust
- [x] Python bindings expose all public methods
- [x] Java CLI wrapper created with all public methods
- [x] Rust tests pass with timeouts enabled
- [x] Python tests pass and match Java output
- [x] Code compiles without warnings
- [x] Documentation complete
