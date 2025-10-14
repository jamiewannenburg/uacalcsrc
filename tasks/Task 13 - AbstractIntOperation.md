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

## Task 13: Translate `AbstractIntOperation`

**Java File:** `org/uacalc/alg/op/AbstractIntOperation.java`  
**Package:** `org.uacalc.alg.op`  
**Rust Module:** `alg::op::AbstractIntOperation`  
**Dependencies:** 3 (3 non-UI/example)  
**Estimated Public Methods:** ~4

### Description
Translate the Java class `org.uacalc.alg.op.AbstractIntOperation` to Rust with Python bindings.

### Dependencies
- **AbstractOperation** (Task 11) - Parent class that AbstractIntOperation extends
- **OperationSymbol** (Task 1) - Used in constructors for operation symbol representation
- **Operation interface** (Task 12) - Inherited through AbstractOperation

**Note**: Despite the name "Abstract", this is actually a concrete class designed for Jython/Groovy compatibility. It has optional methods that throw UnsupportedOperationException.

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
- **Type**: Concrete class extending AbstractOperation (despite "Abstract" name)
- **Purpose**: Jython/Groovy compatibility - provides optional methods that throw UnsupportedOperationException
- **Key Methods**: 
  - 2 constructors (String name + arity + algSize, OperationSymbol + algSize)
  - 1 overridden method (`valueAt` that throws UnsupportedOperationException)
  - 1 main method (empty stub)
- **Inheritance**: Extends AbstractOperation, inherits all Operation interface methods

#### Rust Implementation Strategy
- **Struct Design**: Concrete struct implementing Operation trait through AbstractOperation trait
- **Trait Implementation**: Implement Operation trait methods by delegating to AbstractOperation
- **Error Handling**: Use `Result<T, String>` for methods that can fail
- **Constructor Pattern**: Provide both `new` and `new_safe` constructors
- **Method Delegation**: Override `value_at` to return `Err("UnsupportedOperationException")`

#### Dependencies Required (MUST be implemented first)
1. **Operation Trait** (Task 12) - Core interface that must be implemented first
2. **AbstractOperation Trait** (Task 11) - Parent trait with default implementations
3. **OperationSymbol** (Task 1) - Already implemented ✅

#### Java Wrapper Suitability
- **NOT SUITABLE** - This class is designed as a base class for Jython/Groovy compatibility
- **Issue**: Most methods throw UnsupportedOperationException, making direct testing impractical
- **Alternative**: Test through concrete subclasses that properly implement the methods
- **Testing Strategy**: Focus on constructor testing and basic functionality

#### Critical Implementation Notes
- This is a concrete class despite the "Abstract" name - it can be instantiated
- The `valueAt` method intentionally throws UnsupportedOperationException
- Designed for inheritance by Jython/Groovy subclasses that implement the actual logic
- Very minimal implementation - mostly just constructor delegation to parent
- Main method is empty stub - not suitable for CLI testing

#### Rust Implementation Pattern
```rust
pub struct AbstractIntOperation {
    // Delegate to AbstractOperation implementation
    inner: AbstractOperationImpl,
}

impl Operation for AbstractIntOperation {
    // Delegate all methods to inner implementation
}

impl AbstractIntOperation {
    pub fn new(name: &str, arity: i32, alg_size: i32) -> Self {
        // Delegate to AbstractOperation::new
    }
    
    pub fn new_with_symbol(symbol: OperationSymbol, alg_size: i32) -> Self {
        // Delegate to AbstractOperation::new_with_symbol
    }
    
    // Override value_at to throw UnsupportedOperationException
    pub fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        Err("UnsupportedOperationException".to_string())
    }
}
```

### Acceptance Criteria
- [ ] Operation trait implemented (Task 12)
- [ ] AbstractOperation trait implemented (Task 11)  
- [ ] AbstractIntOperation struct implemented
- [ ] All constructors translated to Rust
- [ ] valueAt method throws appropriate error
- [ ] Python bindings expose constructors
- [ ] Rust tests for constructors and error cases
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] **Java wrapper NOT suitable - skip CLI wrapper**
