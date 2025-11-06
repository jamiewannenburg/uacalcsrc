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

## Task 79: Translate `PolinLikeAlgebra`

**Java File:** `org/uacalc/alg/PolinLikeAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::PolinLikeAlgebra`  
**Dependencies:** 9 (9 non-UI/example)  
**Estimated Public Methods:** ~22

### Description
Translate the Java class `org.uacalc.alg.PolinLikeAlgebra` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.GeneralAlgebra` (extends)
- `org.uacalc.alg.SmallAlgebra` (implements)
- `org.uacalc.alg.conlat.CongruenceLattice` (creates instances)
- `org.uacalc.alg.sublat.SubalgebraLattice` (creates instances)
- `org.uacalc.alg.op.AbstractOperation` (creates instances)
- `org.uacalc.alg.op.Operation` (uses as field and parameter)
- `org.uacalc.alg.op.OperationSymbol` (uses in method parameters)
- `org.uacalc.alg.op.SimilarityType` (accessed via topAlg.similarityType())
- `org.uacalc.alg.Malcev` (used in main method)
- `org.uacalc.io.AlgebraIO` (used in main method)
- `org.uacalc.lat.BasicLattice` (used in main method)
- `org.uacalc.ui.LatDrawer` (used in main method)
- `java.util.AbstractSet` (creates anonymous instances)
- `java.util.logging.Logger` (static logger)

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
- **Type**: Concrete class extending `GeneralAlgebra` and implementing `SmallAlgebra`
- **Key Features**: 
  - Constructs Polin-type algebra from homomorphism between two algebras
  - Uses disjoint union of two algebras with specific element ordering
  - Creates polinized operations that handle mixed arguments
  - Implements lazy initialization of congruence and subalgebra lattices

#### Rust Implementation Design
- **Struct Design**: 
  ```rust
  pub struct PolinLikeAlgebra {
      pub name: String,
      pub top_alg: Box<dyn SmallAlgebra>,
      pub bot_alg: Box<dyn SmallAlgebra>, 
      pub map: Option<Box<dyn Operation>>,
      pub top_const_index: usize,
      pub bot_const_index: usize,
      pub con: Option<CongruenceLattice>,
      pub sub: Option<SubalgebraLattice>,
  }
  ```

- **Trait Implementation**: Implement `SmallAlgebra` trait with all required methods
- **Generic vs Dynamic Dispatch**: Use `Box<dyn SmallAlgebra>` for dynamic dispatch since algebras can be different types
- **Error Handling**: Use `Result<T, String>` for methods that can fail, provide both `_safe` and panic versions

#### Key Methods to Implement
1. **Constructor**: `new(name, top_alg, bot_alg, map, top_const_index, bot_const_index)`
2. **Polinization**: `polinize_operation(sym)` - creates polinized version of operation
3. **Element Access**: `get_element(index)`, `element_index(element)` 
4. **Lattice Access**: `con()`, `sub()` with lazy initialization
5. **Algebra Type**: `algebra_type()` returning `AlgebraType::PolinLike`
6. **Utility Methods**: `arg_type()`, `id()` helper methods

#### Dependencies Analysis
- **Critical Dependencies**: `GeneralAlgebra`, `SmallAlgebra`, `CongruenceLattice`, `SubalgebraLattice`
- **Operation Dependencies**: `AbstractOperation`, `Operation`, `OperationSymbol`, `SimilarityType`
- **UI Dependencies**: Only used in main method, not core functionality
- **Missing Dependencies**: The current task file lists some incorrect dependencies

#### Java Wrapper Suitability
- **Suitable**: Yes, this is a concrete class that can be instantiated and tested
- **Testing Strategy**: Test constructor, polinization methods, element access, and lattice operations
- **Main Method**: Contains example usage that can be converted to CLI commands

#### Testing Strategy
- **Rust Tests**: Test all public methods with various algebra inputs
- **Python Tests**: Verify Python bindings work correctly
- **Java Wrapper**: Test against Java implementation for ground truth
- **Edge Cases**: Test with null map, different algebra types, boundary conditions

### Current Implementation Status

**Overall Status:** BLOCKED - Cannot proceed due to missing critical dependencies

**Completion Percentage:** 5% (only placeholder struct exists)

#### Component Status

**Rust Implementation:** ❌ NOT STARTED
- **Path:** `src/alg/mod.rs` (lines 74-76)
- **Status:** Only placeholder struct declaration exists
- **Quality:** Poor - No actual implementation
- **Notes:** Only contains `// TODO: Implement Polin-like algebra` comment

**Python Bindings:** ❌ NOT STARTED  
- **Path:** N/A
- **Status:** No Python bindings exist
- **Quality:** N/A
- **Notes:** No references found in `uacalc_lib/src/`

**Java Wrapper:** ❌ NOT STARTED
- **Path:** N/A  
- **Status:** No Java wrapper exists
- **Quality:** N/A
- **Notes:** No references found in `java_wrapper/src/`

**Tests:** ❌ NOT STARTED
- **Path:** N/A
- **Status:** No tests exist
- **Quality:** N/A
- **Notes:** No test files found for PolinLikeAlgebra

#### Dependency Analysis

**Blocking Dependencies (Critical):**
- `CongruenceLattice` - NOT IMPLEMENTED (Task 80)
- `SubalgebraLattice` - NOT IMPLEMENTED (Task 76) 
- `GeneralAlgebra` - PARTIALLY IMPLEMENTED (generic version exists, but PolinLikeAlgebra needs specific version)
- `SmallAlgebra` - IMPLEMENTED (trait exists with BasicAlgebra concrete implementation)

**Ready Dependencies:**
- `Operation` trait - IMPLEMENTED
- `OperationSymbol` - IMPLEMENTED  
- `SimilarityType` - IMPLEMENTED
- `AbstractOperation` - IMPLEMENTED

#### Implementation Blockers

1. **CongruenceLattice Missing:** The `con()` method requires CongruenceLattice which is not implemented
2. **SubalgebraLattice Missing:** The `sub()` method requires SubalgebraLattice which is not implemented  
3. **Design Mismatch:** Java uses inheritance (extends GeneralAlgebra), but Rust uses composition
4. **Dynamic Dispatch:** PolinLikeAlgebra needs to work with different algebra types using `Box<dyn SmallAlgebra>`

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete

**Current Status:** All criteria blocked due to missing dependencies

### Recommendations

**Priority 1 - Resolve Blocking Dependencies:**
1. **Implement CongruenceLattice (Task 80)** - Required for `con()` method
2. **Implement SubalgebraLattice (Task 76)** - Required for `sub()` method
3. **Design GeneralAlgebra Integration** - Resolve inheritance vs composition design

**Priority 2 - Implementation Strategy:**
1. **Use Composition Pattern** - Instead of inheritance, use composition with GeneralAlgebra
2. **Dynamic Dispatch** - Use `Box<dyn SmallAlgebra>` for top_alg and bot_alg fields
3. **Lazy Initialization** - Implement lazy initialization for con() and sub() methods
4. **Polinization Logic** - Implement the core polinize_operation method with proper argument type handling

**Priority 3 - Testing Strategy:**
1. **Unit Tests** - Test constructor, polinization, element access methods
2. **Integration Tests** - Test with various algebra types and homomorphisms
3. **Cross-Language Tests** - Compare results with Java implementation
4. **Edge Cases** - Test with null maps, different algebra sizes, boundary conditions

**Estimated Effort:** 2-3 days once dependencies are resolved
