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

## Task 58: Translate `Equation`

**Java File:** `org/uacalc/eq/Equation.java`  
**Package:** `org.uacalc.eq`  
**Rust Module:** `eq::Equation`  
**Dependencies:** 4 (3 non-UI/example)  
**Estimated Public Methods:** 8

### Description
Translate the Java class `org.uacalc.eq.Equation` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg` - Uses `SmallAlgebra` class
- `org.uacalc.alg.op` - Uses `Operation`, `OperationSymbol`, `Operations` classes
- `org.uacalc.terms` - Uses `Term`, `Variable` classes
- `org.uacalc.ui.tm` - Uses `ProgressReport` class (UI dependency, but needed for core functionality)

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
- **Class Type**: Concrete class with immutable fields
- **Key Fields**: `leftSide: Term`, `rightSide: Term`, `varList: Option<List<Variable>>`
- **Public Methods**: 8 methods total
  - Constructors: `new(left: Term, right: Term)`, `new(left: Term, right: Term, vars: List<Variable>)`
  - Getters: `leftSide()`, `rightSide()`, `getVariableList()`, `getOperationSymbols()`
  - Core functionality: `findFailure(alg: SmallAlgebra)`, `findFailure(alg: SmallAlgebra, report: Option<ProgressReport>)`, `findFailureMap(alg: SmallAlgebra)`, `findFailureMap(alg: SmallAlgebra, report: Option<ProgressReport>)`
  - Utility: `toString()`

#### Rust Translation Strategy
- **Rust Construct**: `struct` (not trait or enum)
- **Field Design**: 
  - `left_side: Term` (immutable)
  - `right_side: Term` (immutable) 
  - `var_list: Option<Vec<Variable>>` (lazy-computed, cached)
- **Method Organization**: All methods as struct methods (no trait needed)
- **Error Handling**: Use `Result<T, String>` for methods that can fail
- **Null Handling**: Use `Option<T>` instead of null returns

#### Key Implementation Details
1. **Lazy Variable List**: Implement `getVariableList()` with lazy computation and caching
2. **Operation Symbol Collection**: Use `HashSet<OperationSymbol>` for `getOperationSymbols()`
3. **Failure Detection**: Implement `findFailure()` methods that return `Option<Vec<i32>>` instead of `int[]`
4. **Failure Map**: Implement `findFailureMap()` that returns `Option<HashMap<Variable, i32>>`
5. **Progress Reporting**: Handle optional `ProgressReport` parameter in failure detection methods
6. **String Representation**: Implement `Display` trait for `toString()` functionality

#### Dependencies Required
- `Term` and `Variable` from `terms` module
- `SmallAlgebra` from `alg` module  
- `Operation`, `OperationSymbol`, `Operations` from `alg::op` module
- `ProgressReport` from `progress` module (or create minimal version)

#### Java Wrapper Suitability
- **Suitable**: Yes - concrete class with public constructors and methods
- **Testing Strategy**: Create wrapper with methods to test all public functionality
- **Key Test Cases**: 
  - Constructor with 2 and 3 parameters
  - Getter methods (leftSide, rightSide, getVariableList, getOperationSymbols)
  - findFailure methods with various algebra inputs
  - findFailureMap methods
  - toString method

#### Python Bindings Strategy
- **Export as**: `Equation` class (clean name, no Py prefix)
- **Constructor**: Support both 2-parameter and 3-parameter constructors
- **Error Handling**: Use `PyValueError` for validation errors
- **Return Types**: Convert `Option<T>` to Python `None`/value, `HashMap` to Python `dict`

#### Testing Strategy
- **Rust Tests**: Unit tests for all methods, integration tests with mock algebras
- **Python Tests**: Test all methods through Python bindings
- **Java Wrapper Tests**: Compare results against Java implementation
- **Edge Cases**: Test with empty variable lists, null/None values, various algebra sizes

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Lazy variable list computation implemented
- [ ] Progress reporting support added
- [ ] Error handling matches Java behavior exactly
