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

## Task 51: Translate `SubProductElement`

**Java File:** `org/uacalc/element/SubProductElement.java`  
**Package:** `org.uacalc.element`  
**Rust Module:** `element::SubProductElement`  
**Dependencies:** 3 (3 non-UI/example)  
**Estimated Public Methods:** ~10

### Description
Translate the Java class `org.uacalc.element.SubProductElement` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg` - Algebra interfaces and classes
- `org.uacalc.element.Element` - Element trait interface ✅ (Task 30 - COMPLETED)
- `org.uacalc.terms` - Term-related classes
- `org.uacalc.util` - Utility classes (IntArray, etc.)

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
- [x] All public methods translated to Rust
- [ ] Python bindings expose all public methods (DEFERRED)
- [ ] Java CLI wrapper created with all public methods (NOT IMPLEMENTED)
- [x] Rust tests pass (basic tests implemented)
- [ ] Python tests pass and match Java output (DEFERRED)
- [x] Code compiles without errors (compiles with warnings)
- [x] Basic documentation complete

### Partial Implementation Notes
This is a **partial implementation** with the following limitations:
1. Uses unsafe raw pointer for algebra reference (needs refactoring)
2. Python bindings deferred due to Element trait lifetime complexities
3. Java wrappers not implemented
4. `get_algebra()` method panics (not safely implementable with current design)

### Next Steps for Full Implementation
1. Refactor to use Rc/Arc for safer algebra reference management
2. Redesign Element trait to support Python bindings
3. Create Java wrappers for testing
4. Add comprehensive integration tests

## Current Implementation Status

**Status**: **PARTIALLY IMPLEMENTED** (50% Complete)

**Completion**: 2/4 components (Rust implementation and basic tests)

**Last Updated**: 2025-10-24

### Component Status

#### Rust Implementation: ✅ PARTIALLY IMPLEMENTED
- **Path**: `src/element/sub_product_element.rs` (full file)
- **Quality**: Working but with limitations due to lifetime management
- **Notes**: 
  - Fully implemented struct with Element trait
  - Methods implemented: `new()`, `get_term()`, `get_variable_list()`, `get_variable_map()`, `index()`
  - Display trait implemented
  - Uses unsafe pointer for algebra reference (temporary solution)

#### Python Bindings: ❌ NOT IMPLEMENTED
- **Path**: `uacalc_lib/src/element.rs` (documented)
- **Quality**: N/A - Deferred
- **Notes**: Deferred due to lifetime management complexities with Element trait's get_algebra() method

#### Java Wrapper: ❌ NOT IMPLEMENTED
- **Path**: Not implemented
- **Quality**: N/A
- **Notes**: Not implemented in this partial implementation

#### Tests: ✅ BASIC TESTS IMPLEMENTED
- **Path**: `tests/sub_product_algebra_basic_tests.rs`
- **Quality**: Basic compilation tests
- **Notes**: Basic tests verify struct compiles and works

### Dependency Analysis

#### Ready Dependencies: ✅
- **Element trait** (Task 30) - ✅ COMPLETE
- **IntArray** (Task 23) - ✅ COMPLETE  
- **Term/Variable** (Task 44) - ✅ COMPLETE
- **ArrayString** (Task 6) - ✅ COMPLETE
- **SubProductAlgebra** (Task 83) - ✅ PARTIALLY IMPLEMENTED (core methods available)

#### Resolved Dependencies: ✅
- **SubProductAlgebra** (Task 83) - ✅ PARTIALLY IMPLEMENTED
  - Status: Core methods implemented (excluding con/sub)
  - Impact: SubProductElement can now be implemented with basic functionality

### Implementation Details

#### What Was Implemented ✅
1. **Core Structure**:
   - SubProductElement struct with element (IntArray) and algebra pointer
   - new() constructor
   - Unsafe algebra reference management (temporary solution)

2. **Element Trait Methods**:
   - `index()` - returns element index in algebra
   - `get_parent()` - returns None (not applicable)
   - `get_parent_array()` - returns None
   - `parent_index_array()` - returns None

3. **SubProductElement-Specific Methods**:
   - `get_term()` - returns term for this element
   - `get_variable_list()` - returns list of variables
   - `get_variable_map()` - returns variable to generator mapping
   - `get_element()` - returns the IntArray element

4. **Display Implementation**:
   - Custom Display trait showing element, term, and variable mappings

#### Implementation Limitations ⚠️
1. **Lifetime Management**: Uses unsafe raw pointer for algebra reference
   - This is a temporary solution due to Rust lifetime constraints
   - Should be refactored to use a safer approach (e.g., Rc/Arc)

2. **Element Trait Compatibility**: The `get_algebra()` method is problematic
   - Returns `&dyn Algebra<UniverseItem = i32>` which requires complex lifetime management
   - Currently panics as a placeholder

3. **Python Bindings**: Deferred due to above lifetime complexities

### Recommendations

1. **Immediate Action**: Complete SubProductAlgebra implementation (Task 83)
   - This is the critical path blocker
   - Must implement BigProductAlgebra, GeneralAlgebra, ProductAlgebra first
   - Once SubProductAlgebra is complete, SubProductElement can proceed

2. **Implementation Order**:
   - Complete Task 83 (SubProductAlgebra) first
   - Then implement SubProductElement (Task 51)
   - All other dependencies are already ready

3. **Alternative Approach**: Consider implementing a minimal SubProductAlgebra mock for testing
   - Could allow SubProductElement development to proceed in parallel
   - Would need to be replaced with real implementation later

### Next Steps

1. **Priority 1**: Complete SubProductAlgebra dependencies (BigProductAlgebra, GeneralAlgebra, ProductAlgebra)
2. **Priority 2**: Implement SubProductAlgebra (Task 83)  
3. **Priority 3**: Implement SubProductElement (Task 51)
4. **Priority 4**: Add Python bindings and Java wrapper
5. **Priority 5**: Add comprehensive tests

**Estimated Time to Complete**: 2-3 weeks (blocked by SubProductAlgebra dependencies)
