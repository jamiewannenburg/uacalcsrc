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

## Task 63: Translate `Malcev`

**Java File:** `org/uacalc/alg/Malcev.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::Malcev`  
**Dependencies:** 6 (5 non-UI/example)  
**Estimated Public Methods:** ~94

### Description
Translate the Java class `org.uacalc.alg.Malcev` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.conlat`
- `org.uacalc.alg.op`
- `org.uacalc.alg.sublat`
- `org.uacalc.terms`
- `org.uacalc.util`

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

### Current Implementation Status

**Status:** Not Started (0% complete)

**Rust Implementation:** 
- ❌ Only placeholder struct exists in `src/alg/mod.rs`
- ❌ No methods implemented
- ❌ No functionality

**Python Bindings:**
- ❌ No Python bindings exist
- ❌ No PyO3 integration

**Java Wrapper:**
- ❌ No Java wrapper exists
- ❌ No CLI interface

**Tests:**
- ❌ No Rust tests exist
- ❌ No Python tests exist
- ❌ No integration tests

**Dependencies Status:**
- ✅ `conlat` module: Fully implemented (binary_relation, partition, subtrace)
- ✅ `op` module: Fully implemented (operations, term operations, etc.)
- ✅ `terms` module: Fully implemented (Term trait, VariableImp, NonVariableTerm)
- ✅ `util` module: Fully implemented (horner, arrays, generators, etc.)
- ⚠️ `sublat` module: Only placeholder structs (BasicSet, SubalgebraLattice)

**Blocking Dependencies:** None - all core dependencies are implemented

**Java File Analysis:**
- **File Size:** 156,078 characters (3,500+ lines)
- **Public Methods:** 29 static methods identified
- **Key Methods:** joinTerm, sdmeetTerms, markovicMcKenzieSiggersTaylorTerm, nuTerm, jonssonTerms, etc.
- **Dependencies:** Uses conlat, sublat, op, terms, util modules

### Implementation Recommendations

1. **Start with Rust Implementation:**
   - Implement all 29 public static methods as associated functions
   - Use `SmallAlgebra` trait for algebra parameter
   - Return `Result<T, String>` for error handling
   - Add comprehensive documentation

2. **Priority Order:**
   - Basic term generation methods (joinTerm, nuTerm)
   - Idempotency checking methods
   - Jonsson terms and related algorithms
   - Edge term methods
   - Congruence distributivity methods

3. **Testing Strategy:**
   - Create comprehensive test suite with timeouts
   - Test against known algebra examples
   - Verify output matches Java implementation

### Acceptance Criteria
- [ ] All 29 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
