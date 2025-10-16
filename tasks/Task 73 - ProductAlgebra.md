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

## Task 73: Translate `ProductAlgebra`

**Java File:** `org/uacalc/alg/ProductAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::ProductAlgebra`  
**Dependencies:** 12 (12 non-UI/example)  
**Estimated Public Methods:** ~29

### Description
Translate the Java class `org.uacalc.alg.ProductAlgebra` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.SmallAlgebra.AlgebraType` - Used for algebra type identification
- `org.uacalc.alg.conlat.CongruenceLattice` - Used in con() method
- `org.uacalc.alg.conlat.BasicPartition` - Used in projectionKernel() method
- `org.uacalc.alg.op.AbstractOperation` - Used in makeOperations() method
- `org.uacalc.alg.op.Operation` - Used in makeOperations() method
- `org.uacalc.alg.op.Operations` - Used in makeOperations() method
- `org.uacalc.alg.sublat.SubalgebraLattice` - Used in sub() method
- `org.uacalc.io.AlgebraIO` - Used in main() method for file I/O
- `org.uacalc.util.Horner` - Used for horner calculations
- `org.uacalc.util.IntArray` - Used for element representation
- `org.uacalc.util.ArrayString` - Used in debug output (commented out)
- `java.util.*` - Standard Java collections
- `java.math.BigInteger` - Used in calcCard() method

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

#### Class Analysis
- **Java Class Type**: Concrete class extending `GeneralAlgebra` and implementing `SmallAlgebra`
- **Rust Construct**: Should be a struct implementing appropriate traits
- **Key Features**: 
  - Direct product of `SmallAlgebra` instances
  - Complex operation construction using `AbstractOperation`
  - Cartesian product universe generation
  - Horner-based indexing system

#### Struct Design
```rust
pub struct ProductAlgebra {
    pub algebras: Vec<Box<dyn SmallAlgebra>>,
    pub sizes: Vec<usize>,
    pub number_of_products: usize,
    pub size: usize,
    pub universe: Vec<IntArray>,
    pub operations: Vec<Box<dyn Operation>>,
    pub con: Option<CongruenceLattice>,
    pub sub: Option<SubalgebraLattice>,
}
```

#### Method Translation Patterns
- **Constructors**: `new(name: String, algs: Vec<Box<dyn SmallAlgebra>>) -> Self`
- **Operation Methods**: `make_operations()`, `make_operation_tables()`
- **Accessor Methods**: `factors()`, `parents()`, `projection(k: usize)`
- **Utility Methods**: `element_index(obj: &dyn Any) -> Result<usize, String>`
- **Static Methods**: `calc_card(sizes: &[usize]) -> Result<usize, String>`

#### Key Implementation Challenges
1. **Generic Operations**: The `makeOperations()` method creates `AbstractOperation` instances with complex `valueAt()` implementations
2. **Cartesian Product**: The `makeCartesianProduct()` method creates a complex `AbstractSet` with custom iterator
3. **Horner Calculations**: Heavy use of `Horner.horner()` and `Horner.hornerInv()` for indexing
4. **Lazy Initialization**: `con()` and `sub()` methods use lazy initialization patterns

#### Python Bindings Strategy
- Export as `ProductAlgebra` class with all public methods
- Handle `Vec<Box<dyn SmallAlgebra>>` through trait objects
- Implement proper error handling for `Result` types
- Provide convenient constructors for common use cases

#### Java Wrapper Suitability
- **Suitable**: Yes - concrete class with public methods
- **Testing Strategy**: Test all public methods with various algebra combinations
- **Key Test Cases**: 
  - Construction with different algebra lists
  - Operation table generation
  - Element indexing and retrieval
  - Projection operations
  - Cardinality calculations

### Implementation Status

**Current Status:** NOT STARTED (0% complete)

**Analysis Date:** 2024-12-19

#### Component Status:
- **Rust Implementation:** ❌ NOT STARTED
  - Only placeholder struct exists in `src/alg/mod.rs`
  - No actual implementation of ProductAlgebra methods
  - Missing all core functionality

- **Python Bindings:** ❌ NOT STARTED  
  - No Python bindings found in `uacalc_lib/src/`
  - No PyO3 integration for ProductAlgebra

- **Java Wrapper:** ❌ NOT STARTED
  - No Java wrapper found in `java_wrapper/src/`
  - No CLI interface for ProductAlgebra

- **Tests:** ❌ NOT STARTED
  - No tests found for ProductAlgebra
  - No test coverage

#### Dependency Analysis:
**Ready Dependencies (Implemented):**
- ✅ `SmallAlgebra` trait - Implemented in `src/alg/small_algebra.rs`
- ✅ `GeneralAlgebra` - Implemented in `src/alg/general_algebra.rs`  
- ✅ `Horner` utilities - Implemented in `src/util/horner.rs`
- ✅ `IntArray` - Implemented in `src/util/int_array.rs`
- ✅ `AbstractOperation` trait - Implemented in `src/alg/op/abstract_operation.rs`
- ✅ `Operation` trait - Implemented in `src/alg/op/operation.rs`
- ✅ `Operations` - Implemented in `src/alg/op/operations.rs`
- ✅ `BasicPartition` - Implemented in `src/alg/conlat/partition.rs`

**Blocking Dependencies (Missing):**
- ❌ `CongruenceLattice` - NOT IMPLEMENTED (used in `con()` method)
- ❌ `SubalgebraLattice` - NOT IMPLEMENTED (used in `sub()` method)
- ❌ `AlgebraIO` - NOT IMPLEMENTED (used in `main()` method)

#### Blocking Issues:
1. **CongruenceLattice Missing**: The `con()` method requires CongruenceLattice which is not implemented
2. **SubalgebraLattice Missing**: The `sub()` method requires SubalgebraLattice which is not implemented  
3. **AlgebraIO Missing**: The `main()` method requires AlgebraIO for file operations

#### Recommendations:
1. **Implement Missing Dependencies First**: Complete CongruenceLattice and SubalgebraLattice before starting ProductAlgebra
2. **Start with Basic Structure**: Implement the core ProductAlgebra struct and basic methods
3. **Implement Operations**: Focus on `makeOperations()` method which is the core functionality
4. **Add Tests**: Create comprehensive tests for all public methods
5. **Consider Stubbing**: May need to stub CongruenceLattice and SubalgebraLattice initially

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Horner calculations implemented correctly
- [ ] Cartesian product iterator works properly
- [ ] Operation construction handles all arities
- [ ] Lazy initialization patterns implemented
