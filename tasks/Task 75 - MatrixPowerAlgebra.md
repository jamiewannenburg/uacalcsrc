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

## Task 75: Translate `MatrixPowerAlgebra`

**Java File:** `org/uacalc/alg/MatrixPowerAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::MatrixPowerAlgebra`  
**Dependencies:** 8 (8 non-UI/example)  
**Estimated Public Methods:** ~16

### Description
Translate the Java class `org.uacalc.alg.MatrixPowerAlgebra` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.GeneralAlgebra` (parent class)
- `org.uacalc.alg.SmallAlgebra` (interface implemented)
- `org.uacalc.alg.PowerAlgebra` (used as field)
- `org.uacalc.alg.SmallAlgebra.AlgebraType` (enum)
- `org.uacalc.alg.conlat.CongruenceLattice` (returned by con() method)
- `org.uacalc.alg.sublat.SubalgebraLattice` (returned by sub() method)
- `org.uacalc.alg.op.Operation` (used in operations list)
- `org.uacalc.alg.op.Operations` (static methods: makeLeftShift, makeMatrixDiagonalOp)
- `org.uacalc.util.Horner` (static method: hornerInv)

**Note**: `AlgebraIO` and `AbstractOperation` are imported but not used in the implementation.

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

#### Rust Design
- **Struct Type**: Concrete struct implementing both `GeneralAlgebra` and `SmallAlgebra` traits
- **Key Fields**:
  - `root: Box<dyn SmallAlgebra>` - The base algebra
  - `root_size: usize` - Cardinality of root algebra
  - `power: usize` - The power/exponent
  - `power_algebra: PowerAlgebra` - The underlying power algebra
- **Trait Implementation**: Implement both `GeneralAlgebra` and `SmallAlgebra` traits
- **Error Handling**: Use `Result<T, String>` for constructors and methods that can fail

#### Method Organization
- **Constructor Methods**: 
  - `new(name: String, alg: Box<dyn SmallAlgebra>, power: usize) -> Result<Self, String>`
  - `new_simple(alg: Box<dyn SmallAlgebra>, power: usize) -> Result<Self, String>`
- **Getter Methods**: All getters should be simple field accessors
- **Special Methods**:
  - `get_element(index: usize) -> Object` - Uses `Horner::horner_inv`
  - `element_index(obj: Object) -> usize` - Delegates to power_algebra
  - `con()` and `sub()` - Lazy initialization with `OnceCell` or similar

#### Dependencies
- **Required Traits**: `GeneralAlgebra`, `SmallAlgebra`
- **Required Structs**: `PowerAlgebra`, `CongruenceLattice`, `SubalgebraLattice`
- **Required Utils**: `Horner::horner_inv`, `Operations::make_left_shift`, `Operations::make_matrix_diagonal_op`
- **Enum**: `AlgebraType::MatrixPower`

#### Java Wrapper Suitability
- **Suitable**: Yes - This is a concrete class that can be instantiated and tested
- **Key Test Methods**:
  - Constructor with various parameters
  - `getElement()` and `elementIndex()` methods
  - `cardinality()` and `algebraType()` methods
  - `con()` and `sub()` lattice methods
- **Test Data**: Use small algebras (e.g., 2-element boolean algebra) with powers 2-4

#### Testing Strategy
- **Rust Tests**: Test all public methods with small test algebras
- **Python Tests**: Verify Python bindings work correctly
- **Java Comparison**: Compare results with Java implementation for exact behavior matching
- **Edge Cases**: Test with power=0, power=1, and large powers
- **Error Cases**: Test with invalid parameters

#### Special Considerations
- **Note**: The Java comment indicates this class "is not working yet" and may be better as a subclass of PowerAlgebra
- **Matrix Operations**: The class adds matrix-specific operations (left shift, diagonal) to the power algebra
- **Horner Encoding**: Uses Horner encoding for element indexing, which must be implemented correctly
- **Lazy Lattices**: Congruence and subalgebra lattices are created on-demand

### Current Implementation Status

**Status**: NOT STARTED (0% complete)

**Implementation Status**:
- ❌ **Rust Implementation**: Not implemented (only placeholder struct in mod.rs)
- ❌ **Python Bindings**: Not implemented
- ❌ **Java Wrapper**: Not implemented  
- ❌ **Tests**: Not implemented

**Dependency Analysis**:
- ✅ **GeneralAlgebra**: Implemented in `src/alg/general_algebra.rs`
- ✅ **SmallAlgebra trait**: Implemented in `src/alg/small_algebra.rs`
- ✅ **Horner utilities**: Implemented in `src/util/horner.rs` with `horner_inv` method
- ✅ **Operations factory**: Implemented in `src/alg/op/operations.rs` with `make_left_shift` and `make_matrix_diagonal_op`
- ❌ **PowerAlgebra**: Not implemented (only placeholder struct)
- ❌ **CongruenceLattice**: Not implemented (only placeholder in sublat/mod.rs)
- ❌ **SubalgebraLattice**: Not implemented (only placeholder in sublat/mod.rs)

**Blocking Dependencies**:
- PowerAlgebra implementation required
- CongruenceLattice implementation required  
- SubalgebraLattice implementation required

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Horner encoding implementation verified
- [ ] Matrix operations (left shift, diagonal) implemented correctly
- [ ] Lazy lattice initialization working properly

### Implementation Notes

**Java Implementation Analysis**:
- Extends `GeneralAlgebra` and implements `SmallAlgebra`
- Uses `PowerAlgebra` as underlying implementation
- Adds matrix-specific operations: left shift and diagonal operations
- Uses Horner encoding for element indexing
- Has lazy initialization for congruence and subalgebra lattices
- Java comment indicates "Not working yet" and suggests subclassing PowerAlgebra

**Key Dependencies Status**:
1. **PowerAlgebra** - Critical dependency, not implemented
2. **CongruenceLattice** - Required for `con()` method, not implemented
3. **SubalgebraLattice** - Required for `sub()` method, not implemented
4. **Operations factory methods** - ✅ Available (`make_left_shift`, `make_matrix_diagonal_op`)
5. **Horner utilities** - ✅ Available (`horner_inv`)

**Recommendations**:
1. Implement PowerAlgebra first (Task 78)
2. Implement CongruenceLattice and SubalgebraLattice
3. Then implement MatrixPowerAlgebra as a wrapper around PowerAlgebra
4. Consider the Java comment about subclassing PowerAlgebra instead of composition
