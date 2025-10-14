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

## Task 11: Translate `AbstractOperation`

**Java File:** `org/uacalc/alg/op/AbstractOperation.java`  
**Package:** `org.uacalc.alg.op`  
**Rust Module:** `alg::op::AbstractOperation`  
**Dependencies:** 3 (3 non-UI/example)  
**Estimated Public Methods:** ~20

### Description
Translate the Java class `org.uacalc.alg.op.AbstractOperation` to Rust with Python bindings.

### Dependencies
- **Operation** (interface) - AbstractOperation implements this interface
- **OperationSymbol** - Used for operation symbol representation and comparison
- **Operations** (utility class) - Used for static methods like isTotal, isAssociative, etc.

**Note**: The original task incorrectly listed 0 dependencies. This is a foundational class with 3 key dependencies that must be implemented first.

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
- **Type**: Abstract class implementing Operation interface
- **Key Fields**: 
  - `OperationSymbol symbol` - Operation symbol with name and arity
  - `int algSize` - Size of the algebra set
  - `int[] valueTable` - Optional value table for fast lookup
- **Abstract Method**: `valueAt(List args)` - Must be implemented by subclasses
- **Key Methods**: 20+ public methods including arity(), getSetSize(), isIdempotent(), etc.

#### Rust Implementation Strategy
- **Trait Design**: Convert Java interface to Rust trait with default implementations
- **Struct Design**: Use trait objects or generics for dynamic dispatch
- **Error Handling**: Use Result<T, String> for operations that can fail
- **Memory Management**: Use Box<dyn Operation> for trait objects

#### Dependencies Required
1. **Operation Trait** (Task 12) - Must be implemented first
2. **OperationSymbol** (Task 1) - Already implemented
3. **Operations Utility** (Task 50) - Static methods for operation analysis

#### Java Wrapper Suitability
- **NOT SUITABLE** - AbstractOperation cannot be instantiated directly
- **Alternative**: Create wrapper for concrete subclasses (AbstractIntOperation, OperationWithDefaultValue)
- **Testing Strategy**: Test through concrete implementations

#### Critical Implementation Notes
- AbstractOperation is a base class - focus on trait design and default implementations
- Many methods delegate to Operations utility class - implement that first
- Logger usage requires Rust logging framework integration
- Value table management needs careful memory handling
- Comparison methods need proper trait implementations

### Acceptance Criteria
- [ ] Operation trait implemented with all required methods
- [ ] AbstractOperation trait with default implementations
- [ ] Operations utility class with static methods
- [ ] Concrete implementations (AbstractIntOperation, OperationWithDefaultValue)
- [ ] Python bindings for concrete implementations
- [ ] Java CLI wrappers for concrete implementations
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
