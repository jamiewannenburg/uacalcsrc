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

## Task 83: Translate `SubProductAlgebra`

**Java File:** `org/uacalc/alg/SubProductAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::SubProductAlgebra`  
**Dependencies:** 10 (9 non-UI/example)  
**Estimated Public Methods:** ~40

### Description
Translate the Java class `org.uacalc.alg.SubProductAlgebra` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.SmallAlgebra.AlgebraType` ✓
- `org.uacalc.alg.conlat.*` (CongruenceLattice, BasicPartition) ✓
- `org.uacalc.alg.op.AbstractOperation` ✓
- `org.uacalc.alg.op.Operation` ✓
- `org.uacalc.alg.op.Operations` ✓
- `org.uacalc.alg.sublat.*` (SubalgebraLattice) ✓
- `org.uacalc.lat.*` (Order, OrderedSets) ✓
- `org.uacalc.terms.*` (Term, Variable, VariableImp) ✓
- `org.uacalc.util.*` (Horner, SequenceGenerator, ArrayIncrementor) ✓
- `org.uacalc.alg.BigProductAlgebra` ⚠️ **MISSING**
- `org.uacalc.alg.GeneralAlgebra` ⚠️ **MISSING** 
- `org.uacalc.alg.ProductAlgebra` ⚠️ **MISSING** (used in main method)
- `org.uacalc.alg.conlat.TypeFinder` ⚠️ **MISSING** (used in main method)
- `org.uacalc.ui.tm.ProgressReport` ⚠️ **MISSING** (UI dependency - may be excluded)
- `java.util.*` (List, Map, Set, HashSet, HashMap, ArrayList, Iterator, Arrays) ⚠️ **MISSING**

### Implementation Analysis

#### Java Class Structure
- **Type**: Concrete class extending `GeneralAlgebra` and implementing `SmallAlgebra`
- **Key Fields**: 
  - `BigProductAlgebra productAlgebra` - The underlying product algebra
  - `List<IntArray> gens` - Generators as IntArray list
  - `List<IntArray> univ` - Universe as IntArray list  
  - `Map<IntArray,Integer> univHashMap` - Element to index mapping
  - `Term[] terms` - Terms associated with elements
  - `Map<IntArray,Term> termMap` - Element to term mapping
  - `List<Variable> variables` - Variables for generators
  - `Map<Variable,IntArray> varsMap` - Variable to generator mapping

#### Constructor Patterns
- **Primary Constructor**: `(name, BigProductAlgebra, List<IntArray>, boolean, boolean, ProgressReport)`
- **Convenience Constructors**: Multiple overloads with different parameter combinations
- **Static Factory**: `universeFromRelations()` for creating from relations
- **Special Constructor**: For reading from file with pre-computed universe

#### Key Methods (40+ public methods)
- **Core Methods**: `generators()`, `getUniverseList()`, `getUniverseOrder()`, `elementIndex()`, `getElement()`
- **Term Methods**: `getTerms()`, `getTerm()`, `getElementFromTerm()`, `getVariables()`
- **Algebra Methods**: `con()`, `sub()`, `algebraType()`, `makeOperationTables()`
- **Utility Methods**: `transpose()`, `thinGenerators()`, `projectionKernel()`
- **Static Methods**: `universeFromRelations()`, `transpose()`

### Rust Implementation Recommendations

#### 1. Struct Design
```rust
pub struct SubProductAlgebra {
    pub product_algebra: BigProductAlgebra,
    pub gens: Vec<IntArray>,
    pub univ: Vec<IntArray>,
    pub univ_hash_map: HashMap<IntArray, usize>,
    pub terms: Option<Vec<Term>>,
    pub term_map: Option<HashMap<IntArray, Term>>,
    pub variables: Option<Vec<Variable>>,
    pub vars_map: Option<HashMap<Variable, IntArray>>,
    pub thin_generators: bool,
    pub decompose: bool,
    // Inherited from GeneralAlgebra
    pub operations: Vec<Operation>,
    pub operations_map: HashMap<OperationSymbol, Operation>,
    pub similarity_type: SimilarityType,
    pub universe: HashSet<IntArray>,
    pub con: Option<CongruenceLattice>,
    pub sub: Option<SubalgebraLattice>,
    pub name: String,
    pub description: Option<String>,
    pub size: usize,
}
```

#### 2. Constructor Strategy
- **Primary Constructor**: `new_safe()` with full parameter validation
- **Convenience Constructors**: `new()`, `new_with_terms()`, `new_from_file()`
- **Static Factory**: `from_relations()` for relation-based construction
- **Builder Pattern**: Consider for complex construction scenarios

#### 3. Method Organization
- **Trait Methods**: Implement `SmallAlgebra` trait methods
- **Struct Methods**: Core functionality methods
- **Static Methods**: `transpose()`, `universe_from_relations()`
- **Private Helpers**: `setup()`, `make_operations()`, `setup_gens_to_vars_map()`

#### 4. Error Handling
- **Result Types**: Use `Result<T, String>` for fallible operations
- **Validation**: Comprehensive input validation in constructors
- **Memory Management**: Handle large algebra size limits gracefully

#### 5. Generic vs Dynamic Dispatch
- **Use Generics**: For type-safe operation handling
- **Dynamic Dispatch**: For polymorphic algebra operations
- **Trait Objects**: For `SmallAlgebra` interface compliance

### Java Wrapper Suitability
**SUITABLE** - This is a concrete class with clear public API, making it ideal for Java wrapper testing.

### Testing Strategy
1. **Unit Tests**: Test all public methods individually
2. **Integration Tests**: Test with various algebra types and sizes
3. **Performance Tests**: Test with large algebras and operation table generation
4. **Cross-Language Tests**: Compare Rust/Python/Java outputs
5. **Edge Case Tests**: Empty algebras, single-element algebras, memory limits

### Critical Implementation Notes
1. **Memory Management**: `makeOperationTables()` has 8M element limit - implement similar protection
2. **Term Handling**: Complex term-to-variable mapping for generators
3. **Hash Consistency**: Ensure `IntArray` hashing is consistent across operations
4. **Thread Safety**: Consider `Mutex` for mutable fields if needed
5. **Progress Reporting**: Handle `ProgressReport` parameter (may be excluded as UI dependency)

### Implementation Steps

1. **Analyze Java Implementation** ✓
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

### Current Implementation Status

**Status**: NOT STARTED (0% Complete)  
**Last Updated**: 2024-12-16

#### Component Status
- **Rust Implementation**: ❌ Not implemented (only struct declaration exists)
- **Python Bindings**: ❌ Not implemented  
- **Java Wrapper**: ❌ Not implemented
- **Tests**: ❌ Not implemented

#### Implementation Details
- **Rust Path**: `src/alg/mod.rs` (line 86-88: only struct declaration)
- **Python Path**: Not implemented
- **Java Wrapper Path**: Not implemented
- **Test Path**: Not implemented

#### Blocking Dependencies Analysis
**CRITICAL BLOCKERS** (Must be completed first):
1. **BigProductAlgebra (Task 78)** - ❌ Not implemented
   - Required for constructor parameter
   - Used in `sgClose()` methods
   - Used in `projection()` method
   - Status: Only struct declaration exists

2. **GeneralAlgebra (Task 55)** - ⚠️ Partially implemented
   - Base class for SubProductAlgebra
   - Status: Basic implementation exists but may need extensions

3. **ProductAlgebra (Task 73)** - ❌ Not implemented
   - Used in main method for testing
   - Status: Only struct declaration exists

**READY DEPENDENCIES** (Available for use):
- ✅ `SmallAlgebra.AlgebraType` (Task 2) - Complete
- ✅ `CongruenceLattice` (Task 80) - Complete  
- ✅ `BasicPartition` (Task 69) - Complete
- ✅ `AbstractOperation` (Task 11) - Complete
- ✅ `Operation` (Task 12) - Complete
- ✅ `Operations` (Task 50) - Complete
- ✅ `SubalgebraLattice` (Task 76) - Complete
- ✅ `Order` (Task 18) - Complete
- ✅ `OrderedSets` (Task 16) - Complete
- ✅ `Term` (Task 44) - Complete
- ✅ `Variable` (Task 40) - Complete
- ✅ `VariableImp` (Task 67) - Complete
- ✅ `Horner` (Task 3) - Complete
- ✅ `SequenceGenerator` (Task 15) - Complete
- ✅ `ArrayIncrementor` (Task 14) - Complete
- ✅ `IntArray` (Task 23) - Complete

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods  
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] **CRITICAL**: All missing dependencies must be implemented first
- [ ] **CRITICAL**: BigProductAlgebra dependency must be completed
- [ ] **CRITICAL**: GeneralAlgebra dependency must be completed
