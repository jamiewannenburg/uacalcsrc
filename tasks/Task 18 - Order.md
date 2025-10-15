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

## Task 18: Translate `Order`

**Java File:** `org/uacalc/lat/Order.java`  
**Package:** `org.uacalc.lat`  
**Rust Module:** `lat::Order`  
**Dependencies:** 0 (0 non-UI/example) - **VERIFIED CORRECT**  
**Estimated Public Methods:** 1

### Description
Translate the Java interface `org.uacalc.lat.Order` to Rust with Python bindings.

### Dependencies
**VERIFIED DEPENDENCIES:**
This interface has **NO ACTUAL DEPENDENCIES** on other UACalc classes.

**Analysis Results:**
- The `import org.uacalc.alg.*;` statement in Order.java is **UNUSED**
- No classes from org.uacalc.alg are referenced in the Order interface
- The interface only uses standard Java types (generic type parameter E)
- **Dependency count is correctly 0**

**Usage Patterns Found:**
- Used by `PartiallyDefinedLattice` (implements Order<Variable>)
- Used by `OrderedSets.maximals()` method as a parameter
- Used in `SubProductAlgebra.thinGenerators()` method
- Anonymous implementations in test code (OrderedSets.main())
- Used in `LatDrawer.java` for diagram operations

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
- **Type**: Interface (generic)
- **Generic Parameter**: `E` (element type)
- **Public Methods**: 1 (`leq(E a, E b) -> boolean`)
- **Dependencies**: None (unused import should be removed)
- **File Size**: 20 lines, 1 method
- **Mathematical Purpose**: Defines a partial order relation (reflexive, antisymmetric, transitive)

#### Rust Translation Design
- **Rust Construct**: Trait (not struct)
- **Trait Name**: `Order<E>`
- **Method Signature**: `fn leq(&self, a: &E, b: &E) -> bool`
- **Generic Dispatch**: Yes (trait with generic parameter)
- **Dynamic Dispatch**: Yes (trait objects)
- **No Associated Types**: Simple trait with single method
- **Trait Bounds**: No additional bounds required on E

#### Implementation Strategy
```rust
/// A partial order relation on elements of type E.
/// 
/// This trait defines the "less than or equal to" relation (≤) for elements.
/// Implementations must satisfy the mathematical properties of a partial order:
/// - Reflexivity: leq(a, a) == true for all a
/// - Antisymmetry: if leq(a, b) && leq(b, a) then a == b
/// - Transitivity: if leq(a, b) && leq(b, c) then leq(a, c)
pub trait Order<E> {
    /// Returns true if a ≤ b in this order relation
    fn leq(&self, a: &E, b: &E) -> bool;
}
```

#### Java Wrapper Suitability
- **Suitable**: NO - Interface cannot be instantiated directly
- **Reason**: Order is an interface, not a concrete class
- **Alternative**: Create wrapper for concrete implementations like PartiallyDefinedLattice
- **Testing Strategy**: Test through implementing classes, not direct interface testing
- **Note**: The interface itself cannot be tested in isolation

#### Python Bindings Strategy
- **Approach**: Export as trait, not concrete struct
- **Usage**: Python users implement the trait for their types
- **Example**: `class MyOrder(Order): def leq(self, a, b): return a <= b`
- **Integration**: Must work with OrderedSets.maximals() method
- **Type Safety**: Ensure proper generic type handling in Python

#### Testing Strategy
- **Rust Tests**: Test trait implementations, not trait itself
- **Python Tests**: Test through implementing classes
- **Integration Tests**: Test with OrderedSets.maximals() method
- **Edge Cases**: Test with different element types (Integer, String, custom types)
- **Mathematical Properties**: Test reflexivity, antisymmetry, transitivity
- **Performance**: Test with large collections in OrderedSets.maximals()

#### Dependencies Verification
- **Current Status**: CORRECT - No dependencies listed
- **Actual Status**: NO DEPENDENCIES
- **Action Required**: Remove unused import from Java file
- **Task Order**: Can be implemented immediately (no dependencies)

#### Critical Implementation Notes
1. **Generic Trait**: Must support any type E that implements appropriate bounds
2. **Trait Objects**: Support both static and dynamic dispatch
3. **Documentation**: Include mathematical definition of order relation
4. **Examples**: Provide examples with different element types
5. **Integration**: Ensure compatibility with OrderedSets.maximals()
6. **Mathematical Correctness**: Implementations must satisfy partial order properties
7. **Performance**: Consider performance implications for large collections
8. **Error Handling**: No error conditions - always returns bool

### Acceptance Criteria
- [x] Order trait implemented in Rust with proper documentation ✅ **COMPLETED**
- [x] Python bindings expose Order trait for user implementation ✅ **COMPLETED**
- [x] Java wrapper created for concrete implementations (not interface) ✅ **COMPLETED**
- [x] Rust tests pass for trait implementations with various element types ✅ **COMPLETED**
- [x] Python tests pass for trait implementations ✅ **COMPLETED**
- [x] Code compiles without warnings ✅ **COMPLETED**
- [x] Documentation complete with mathematical properties and examples ✅ **COMPLETED**
- [x] Integration with OrderedSets.maximals() verified ✅ **COMPLETED**
- [x] Mathematical properties (reflexivity, antisymmetry, transitivity) tested ✅ **COMPLETED**
- [x] Performance tests with large collections ✅ **COMPLETED**
- [x] Generic type handling works correctly in both Rust and Python ✅ **COMPLETED**
- [x] Trait objects support both static and dynamic dispatch ✅ **COMPLETED**
- [x] Examples provided for common order relations (integer divisibility, string ordering, etc.) ✅ **COMPLETED**

### Implementation Status: ✅ **COMPLETED**

**Completed Components:**
- ✅ Order trait implemented in `src/lat/mod.rs` with comprehensive documentation
- ✅ Example implementations: DivisibilityOrder, PrefixOrder, NaturalOrder
- ✅ Integration with OrderedSets.maximals() verified and working
- ✅ Comprehensive test suite with mathematical property validation
- ✅ Python bindings available through uacalc_lib
- ✅ Java CLI wrappers for concrete implementations
- ✅ All mathematical properties (reflexivity, antisymmetry, transitivity) tested
- ✅ Generic type support for any element type E
- ✅ Performance optimized for large collections
