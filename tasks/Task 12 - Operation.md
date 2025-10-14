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

## Task 12: Translate `Operation`

**Java File:** `org/uacalc/alg/op/Operation.java`  
**Package:** `org.uacalc.alg.op`  
**Rust Module:** `alg::op::Operation`  
**Dependencies:** 0 (0 non-UI/example)  
**Estimated Public Methods:** ~17

### Description
Translate the Java class `org.uacalc.alg.op.Operation` to Rust with Python bindings.

### Dependencies
- **OperationSymbol** (Task 1) - Used for operation symbol representation and comparison
- **Operations** (Task 50) - Used for static utility methods like isTotal, isAssociative, etc.

**Note**: While Operation itself has minimal dependencies, it is a foundational interface that many other classes depend on. The Operations utility class provides static methods that are used by Operation implementations.

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
- **Type**: Interface (17 public methods)
- **Key Methods**: 
  - `arity()`, `getSetSize()`, `symbol()` - Basic properties
  - `valueAt(List)`, `valueAt(int[][])`, `intValueAt(int[])`, `intValueAt(int)` - Operation evaluation
  - `makeTable()`, `getTable()`, `isTableBased()` - Table management
  - `isIdempotent()`, `isAssociative()`, `isCommutative()`, `isTotallySymmetric()`, `isMaltsev()`, `isTotal()` - Property checks
- **Dependencies**: Only OperationSymbol (already implemented) and standard Java collections
- **Usage**: Heavily used throughout codebase as foundational interface

#### Rust Implementation Strategy
- **Rust Construct**: `trait Operation` (interface → trait)
- **Trait Methods**: All 17 public methods should be trait methods
- **Generic vs Dynamic Dispatch**: Use dynamic dispatch (`dyn Operation`) for flexibility
- **Error Handling**: Use `Result<T, String>` for methods that can fail
- **Comparable**: Implement `Ord`, `PartialOrd`, `Eq`, `PartialEq` traits

#### Java Wrapper Suitability
- **NOT SUITABLE** - Operation is an interface that cannot be instantiated directly
- **Alternative**: Create wrapper for concrete implementations (AbstractOperation, OperationWithDefaultValue, etc.)
- **Testing Strategy**: Test through concrete implementations rather than interface directly

#### Dependencies Verification
- **OperationSymbol**: ✅ Already implemented (Task 1)
- **Operations**: ❌ Not yet implemented (Task 50) - provides static utility methods
- **Missing Dependencies**: None identified

#### Implementation Priority
- **HIGH PRIORITY** - This is a foundational interface that many other classes depend on
- **Blocking**: AbstractOperation, OperationWithDefaultValue, and other operation classes cannot be implemented without this trait
- **Recommendation**: Implement this trait first, then work on concrete implementations

### Acceptance Criteria
- [ ] Operation trait implemented with all 17 methods
- [ ] Trait implements Comparable (Ord, PartialOrd, Eq, PartialEq)
- [ ] Proper error handling with Result types
- [ ] Python bindings expose trait (though not directly instantiable)
- [ ] Java wrapper created for concrete implementations
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass through concrete implementations
- [ ] Code compiles without warnings
- [ ] Documentation complete
