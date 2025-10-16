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

## Task 15: Translate `SequenceGenerator`

**Java File:** `org/uacalc/util/SequenceGenerator.java`  
**Package:** `org.uacalc.util`  
**Rust Module:** `util::SequenceGenerator`  
**Dependencies:** 2 (2 non-UI/example)  
**Estimated Public Methods:** ~21

### Description
Translate the Java class `org.uacalc.util.SequenceGenerator` to Rust with Python bindings.

### Dependencies
- `ArrayIncrementor` interface (Task 14) - Required for all incrementor implementations
- `ArrayString` utility class (Task 6) - Used in main method for debugging output

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
- **Type**: Concrete class with static methods (utility class)
- **Public Methods**: 8 static methods + 1 private helper method
- **Dependencies**: 1 dependency on `ArrayIncrementor` interface (Task 14)
- **Usage Pattern**: Used extensively throughout the codebase for sequence generation

**Dependency Analysis:**
- **Correct Dependencies**: ✅ Yes - All dependencies correctly listed
- **Dependencies Found**: 
  - `ArrayIncrementor` interface (Task 14) - ✅ Correctly listed
  - `ArrayString` utility class (Task 6) - ✅ Correctly listed
- **Usage Found**: SequenceGenerator is used in:
  - Algorithm classes (SubalgebraLattice, SingleClose, Operations, etc.)
  - UI components (OperationTableModel)
  - Example classes (TupleStream, Michalewski, HasKaryNU)
  - Core algebra classes (Malcev, Closer, FreeAlgebra, etc.)

**Rust Implementation Analysis:**
- **Current Implementation**: ✅ Complete
  - `SequenceGenerator` struct with static methods in `src/util/sequence_generator.rs`
  - All incrementor types implemented as separate structs
  - All public methods properly translated with Rust idioms
  - Comprehensive documentation and examples

**Python Bindings Analysis:**
- **Current Implementation**: ✅ Complete
  - `PySequenceGenerator` class in `uacalc_lib/src/util.rs`
  - All static methods exposed with proper error handling
  - Clean export names (no Py prefix)
  - Proper Python magic methods implemented

**Java Wrapper Analysis:**
- **Current Implementation**: ✅ Complete
  - `SequenceGeneratorWrapper.java` exists and is functional
  - Exposes all sequence generation methods through CLI
  - Proper CLI interface with help, test, and specific commands
  - Uses `ArrayIncrementor` interface for concrete implementations

**Testing Analysis:**
- **Rust Tests**: ✅ Complete - `tests/util/sequence_generator_tests.rs`
- **Python Tests**: ✅ Complete - `python/uacalc/tests/test_sequence_generator.py`
- **Test Coverage**: All public methods tested with Java comparison

**Implementation Recommendations:**
1. **Rust Design**: ✅ Correctly implemented as utility struct with static methods
2. **Method Organization**: ✅ Static methods properly organized, incrementor types as separate structs
3. **Generic vs Dynamic Dispatch**: ✅ Uses trait objects appropriately for ArrayIncrementor
4. **Java Wrapper Suitability**: ✅ Suitable - concrete class with static methods
5. **Testing Strategy**: ✅ Comprehensive cross-language testing implemented

**Verification Status:**
- All acceptance criteria are properly met
- Implementation follows Rust idioms and patterns
- Python bindings are complete and functional
- Java wrapper provides adequate testing interface
- Cross-language compatibility verified
- **Issue**: None - All dependencies are correctly listed

**Missing Dependencies:**
- None - All dependencies are correctly listed

**Current Implementation Status (Updated):**
- **Rust Implementation**: ✅ Complete - All 8 public methods implemented with comprehensive documentation
- **Python Bindings**: ✅ Complete - All methods exposed with proper error handling and clean API
- **Java Wrapper**: ✅ Complete - Full CLI interface with all sequence generation methods
- **Tests**: ✅ Complete - Comprehensive test suite with cross-language validation
- **Dependencies**: ✅ All ready - ArrayIncrementor and ArrayString are fully implemented

### Acceptance Criteria
- [x] All public methods translated to Rust
- [x] Python bindings expose all public methods
- [x] Java CLI wrapper created with all public methods
- [x] Rust tests pass with timeouts enabled
- [x] Python tests pass and match Java output
- [x] Code compiles without warnings
- [x] Documentation complete
