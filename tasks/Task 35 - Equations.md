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

## Task 35: Translate `Equations`

**Java File:** `org/uacalc/eq/Equations.java`  
**Package:** `org.uacalc.eq`  
**Rust Module:** `eq::Equations`  
**Dependencies:** 2 (2 non-UI/example)  
**Estimated Public Methods:** ~4

### Description
Translate the Java class `org.uacalc.eq.Equations` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.op.OperationSymbol` ✅ **IMPLEMENTED** (Task 1 - Complete)
- `org.uacalc.terms.Variable` ❌ **NOT IMPLEMENTED** (Task 40 - Incomplete)
- `org.uacalc.terms.NonVariableTerm` ❌ **NOT IMPLEMENTED** (Task 74 - Incomplete)  
- `org.uacalc.eq.Equation` ❌ **NOT IMPLEMENTED** (Task 58 - Incomplete)

**Dependency Status**: 1 of 4 dependencies implemented. **BLOCKED** - Cannot proceed until terms package is implemented.

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

### Java Class Analysis

**Class Type**: Concrete class with static methods only  
**Public Methods**: 3 static methods + main method
- `associativeLaw(OperationSymbol f) -> Equation` - Creates associative law equation f(x,f(y,z)) = f(f(x,y),z)
- `cyclicLaw(OperationSymbol f) -> Equation` - Creates cyclic law equation f(x0,x1,...,x{k-1}) = f(x{k-1},x0,...,x{k-2})  
- `firstSecondSymmetricLaw(OperationSymbol f) -> Equation` - Creates symmetry law equation f(x0,x1,x2,...,xk) = f(x1,x0,x2,...,xk)

**Key Dependencies**:
- Uses `Variable.x`, `Variable.y`, `Variable.z` constants
- Creates `VariableImp` instances for dynamic variable names
- Constructs `NonVariableTerm` instances with operation symbols and variable lists
- Returns `Equation` objects with left and right terms

### Rust Implementation Strategy

**Rust Construct**: Module with free functions (not a struct)  
**Reasoning**: Equations is a utility class with only static methods, so Rust module with free functions is more idiomatic

**Implementation Pattern**:
```rust
// src/eq/equations.rs
pub mod equations {
    use crate::alg::op::OperationSymbol;
    use crate::terms::{Variable, NonVariableTerm, Equation};
    
    /// Create associative law equation: f(x,f(y,z)) = f(f(x,y),z)
    pub fn associative_law(f: &OperationSymbol) -> Result<Equation, String> {
        // Implementation with proper error handling
    }
    
    /// Create cyclic law equation: f(x0,x1,...,x{k-1}) = f(x{k-1},x0,...,x{k-2})
    pub fn cyclic_law(f: &OperationSymbol) -> Result<Equation, String> {
        // Implementation with proper error handling  
    }
    
    /// Create first-second symmetric law equation: f(x0,x1,x2,...,xk) = f(x1,x0,x2,...,xk)
    pub fn first_second_symmetric_law(f: &OperationSymbol) -> Result<Equation, String> {
        // Implementation with proper error handling
    }
}
```

**Error Handling**: All methods should return `Result<Equation, String>` for proper error handling:
- `associative_law`: Returns error if arity != 2
- `cyclic_law`: Returns error if arity < 1  
- `first_second_symmetric_law`: Returns error if arity < 2

### Python Bindings Strategy

**Module Structure**: `uacalc_lib.eq.equations`
**Exposed Functions**: All three equation generation functions
**Error Handling**: Convert Rust `Result` to Python exceptions

```python
# Python usage
import uacalc_lib
from uacalc_lib.alg.op import OperationSymbol

# Create operation symbol
op = OperationSymbol("multiply", 2)

# Generate equations
assoc_eq = uacalc_lib.eq.equations.associative_law(op)
cyclic_eq = uacalc_lib.eq.equations.cyclic_law(op) 
symm_eq = uacalc_lib.eq.equations.first_second_symmetric_law(op)
```

### Java Wrapper Strategy

**Suitability**: ✅ **SUITABLE** - All methods are static and can be easily tested
**Wrapper Location**: `java_wrapper/src/eq/EquationsWrapper.java`
**CLI Commands**:
- `associative-law --op-name <name> --op-arity <arity>`
- `cyclic-law --op-name <name> --op-arity <arity>`  
- `first-second-symmetric-law --op-name <name> --op-arity <arity>`
- `test` - Run basic functionality tests

### Testing Strategy

**Rust Tests**: Unit tests for each equation generation method with various operation symbols
**Python Tests**: Integration tests comparing equation generation with Java implementation
**Java Wrapper Tests**: CLI command tests with different operation symbols and arities

**Test Cases**:
- Valid operation symbols (binary, ternary, etc.)
- Invalid arities (associative law with arity != 2)
- Edge cases (unary operations for cyclic law)
- Cross-language comparison with Java implementation

### Current Implementation Status

**Rust Implementation**: ❌ **NOT IMPLEMENTED** - Only placeholder struct exists
**Python Bindings**: ❌ **NOT IMPLEMENTED** - Module exists but no bindings
**Java Wrapper**: ❌ **NOT IMPLEMENTED** - No wrapper exists
**Dependencies**: ❌ **BLOCKED** - Terms package not implemented

### Prerequisites

**Must Complete First**:
1. Task 40 - Variable (interface)
2. Task 67 - VariableImp (concrete implementation)  
3. Task 56 - Term (interface)
4. Task 74 - NonVariableTerm (concrete implementation)
5. Task 58 - Equation (concrete class)

**Estimated Effort**: 2-3 days after dependencies are complete

### Acceptance Criteria
- [ ] All 3 static methods translated to Rust with proper error handling
- [ ] Python bindings expose all equation generation functions
- [ ] Java CLI wrapper created with all equation generation commands
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] **BLOCKED**: Cannot proceed until terms package dependencies are implemented
