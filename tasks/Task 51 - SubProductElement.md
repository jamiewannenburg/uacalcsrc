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
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete

## Current Implementation Status

**Status**: **BLOCKED** - Missing critical dependency (SubProductAlgebra)

**Completion**: 5% (1/4 components)

### Component Status

#### Rust Implementation: ❌ NOT STARTED
- **Path**: `src/element/mod.rs` (placeholder only)
- **Quality**: N/A - Only empty struct placeholder exists
- **Notes**: Only contains `pub struct SubProductElement { // TODO: Implement subproduct element }`

#### Python Bindings: ❌ NOT STARTED  
- **Path**: `uacalc_lib/src/element.rs` (infrastructure only)
- **Quality**: N/A - No SubProductElement bindings exist
- **Notes**: Only contains Element trait infrastructure, no concrete implementation bindings

#### Java Wrapper: ❌ NOT STARTED
- **Path**: Not found
- **Quality**: N/A - No wrapper exists
- **Notes**: No Java wrapper implementation found

#### Tests: ❌ NOT STARTED
- **Path**: Not found
- **Quality**: N/A - No tests exist
- **Notes**: No SubProductElement-specific tests found

### Dependency Analysis

#### Ready Dependencies: ✅
- **Element trait** (Task 30) - ✅ COMPLETE
- **IntArray** (Task 23) - ✅ COMPLETE  
- **Term/Variable** (Task 44) - ✅ COMPLETE
- **ArrayString** (Task 6) - ✅ COMPLETE

#### Blocking Dependencies: ❌
- **SubProductAlgebra** (Task 83) - ❌ BLOCKED
  - Status: Not implemented due to missing dependencies
  - Blocked by: BigProductAlgebra, GeneralAlgebra, ProductAlgebra
  - Impact: Cannot implement SubProductElement without SubProductAlgebra

### Implementation Blockers

1. **Critical Blocker**: SubProductAlgebra (Task 83) is not implemented
   - SubProductElement requires SubProductAlgebra for constructor and methods
   - SubProductAlgebra is blocked by missing BigProductAlgebra, GeneralAlgebra, ProductAlgebra
   - This creates a dependency chain that prevents SubProductElement implementation

2. **Missing Methods**: Cannot implement without SubProductAlgebra:
   - `getTerm()` - requires `algebra.getTerm(element)`
   - `getVariableMap()` - requires `algebra.getVariableToGeneratorMap()`
   - `index()` - requires `algebra.elementIndex(element)`
   - `toString()` - requires term and variable information from algebra

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
