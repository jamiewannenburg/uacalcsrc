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

## Task 16: Translate `OrderedSets`

**Java File:** `org/uacalc/lat/OrderedSets.java`  
**Package:** `org.uacalc.lat`  
**Rust Module:** `lat::OrderedSets`  
**Dependencies:** 1 (Order interface)  
**Estimated Public Methods:** 2 (maximals, main)

### Description
Translate the Java class `org.uacalc.lat.OrderedSets` to Rust with Python bindings.

### Dependencies
**CORRECTED DEPENDENCIES:**
- `org.uacalc.lat.Order` - Interface for order relations (required for maximals method)
- `java.util.*` - Standard Java collections (Collection, List, ArrayList)

**USAGE ANALYSIS:**
- Used by `org.uacalc.alg.SubProductAlgebra.thinGenerators()` method
- No direct imports found in codebase (used via fully qualified name)
- Static utility class - no instantiation required

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

### Rust Implementation Recommendations

**Class Analysis:**
- **Java Type**: Concrete class with static methods only
- **Rust Construct**: Module with free functions (no struct needed)
- **Pattern**: Static utility module

**Method Translation:**
1. **`maximals<E>(Collection<? extends E> elems, Order<? super E> order) -> List<E>`**
   - **Rust**: `pub fn maximals<T, F>(elems: &[T], order: F) -> Vec<T> where F: Fn(&T, &T) -> bool`
   - **Pattern**: Generic function with closure parameter
   - **Note**: Use `&[T]` instead of `Collection` for better Rust ergonomics

2. **`main(String[] args)`**
   - **Rust**: `pub fn main()` (for testing)
   - **Pattern**: Test function, not part of public API

**Dependencies:**
- **Order Interface**: Translate to `Fn(&T, &T) -> bool` closure trait bound
- **Collections**: Use `Vec<T>` and `&[T]` instead of Java collections

**Rust Module Structure:**
```rust
// src/lat/ordered_sets.rs
pub fn maximals<T, F>(elems: &[T], order: F) -> Vec<T> 
where 
    F: Fn(&T, &T) -> bool 
{
    // Implementation matching Java algorithm exactly
}
```

**Python Bindings:**
- Expose `maximals` as static method
- Use `List[T]` for Python collections
- Accept callable for order relation

**Java Wrapper Suitability:**
- **SUITABLE**: Concrete class with static methods
- **Testing Strategy**: Unit tests with various order relations
- **CLI Commands**: `maximals` command with test data

**Testing Strategy:**
- Test with integer divisibility order (as in main method)
- Test with custom order relations
- Test edge cases (empty collections, single elements)
- Compare results with Java implementation

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Order interface dependency properly handled
- [ ] Generic type parameters correctly translated
