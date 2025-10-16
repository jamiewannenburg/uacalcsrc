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

## Task 80: Translate `CongruenceLattice`

**Java File:** `org/uacalc/alg/conlat/CongruenceLattice.java`  
**Package:** `org.uacalc.alg.conlat`  
**Rust Module:** `alg::conlat::CongruenceLattice`  
**Dependencies:** 10 (9 non-UI/example)  
**Estimated Public Methods:** ~137

### Description
Translate the Java class `org.uacalc.alg.conlat.CongruenceLattice` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.SmallAlgebra` - ✅ **COMPLETED** - Core algebra interface
- `org.uacalc.alg.Subalgebra` - ❌ **PENDING** - For congruence as algebra operations
- `org.uacalc.alg.SubProductAlgebra` - ❌ **PENDING** - For tolerance and centrality calculations
- `org.uacalc.alg.BigProductAlgebra` - ❌ **PENDING** - For product algebra operations
- `org.uacalc.alg.op.Operation` - ✅ **COMPLETED** - Operation interface
- `org.uacalc.alg.op.OperationSymbol` - ✅ **COMPLETED** - Operation symbol representation
- `org.uacalc.alg.op.SimilarityType` - ❌ **PENDING** - Similarity type definitions
- `org.uacalc.alg.sublat.SubalgebraLattice` - ❌ **PENDING** - Subalgebra lattice interface
- `org.uacalc.element.Partition` - Core partition representation
- `org.uacalc.element.BasicPartition` - Basic partition implementation
- `org.uacalc.element.IntArray` - Integer array wrapper
- `org.uacalc.element.BinaryRelation` - Binary relation interface
- `org.uacalc.element.BasicBinaryRelation` - Basic binary relation implementation
- `org.uacalc.element.SubProductElement` - Subproduct element representation
- `org.uacalc.element.CentralityData` - Centrality calculation data
- `org.uacalc.element.Subtrace` - Subtrace representation
- `org.uacalc.lat.Lattice` - Lattice interface
- `org.uacalc.lat.BasicLattice` - Basic lattice implementation
- `org.uacalc.util.SimpleList` - Simple list implementation
- `org.uacalc.util.ProgressReport` - Progress reporting interface
- `org.uacalc.io.*` - I/O utilities (minimal usage)
- `org.uacalc.alg.conlat.TypeFinder` - Type finding utility

### Implementation Analysis

#### Java Class Analysis
- **Type**: Concrete class implementing `Lattice` interface
- **Purpose**: Represents the congruence lattice of a `SmallAlgebra`
- **Key Features**: 
  - Implements lattice operations (join, meet, leq)
  - Computes principal congruences, join irreducibles, meet irreducibles
  - Provides centrality and commutator calculations
  - Supports TCT (Tame Congruence Theory) type finding
  - Handles progress reporting for long computations

#### Rust Translation Strategy

**Struct Design:**
```rust
pub struct CongruenceLattice {
    alg: Rc<dyn SmallAlgebra>,
    alg_size: usize,
    num_ops: usize,
    zero_cong: Partition,
    one_cong: Partition,
    con: Option<Rc<CongruenceLattice>>,
    sub: Option<Rc<SubalgebraLattice>>,
    description: Option<String>,
    basic_lat: Option<BasicLattice>,
    // Cached computations
    universe: Option<HashSet<Partition>>,
    principal_congruences: Option<Vec<Partition>>,
    join_irreducibles: Option<Vec<Partition>>,
    // ... other cached fields
}
```

**Key Design Decisions:**
1. **Reference Counting**: Use `Rc<dyn SmallAlgebra>` for shared ownership
2. **Lazy Computation**: Cache expensive computations (universe, principals, etc.)
3. **Error Handling**: Use `Result<T, String>` for fallible operations
4. **Progress Reporting**: Implement callback-based progress reporting
5. **Thread Safety**: Use `Mutex` for static mutable state

**Trait Implementation:**
- Implement `Lattice` trait for lattice operations
- Implement `Display`, `Debug`, `Clone`, `PartialEq`, `Eq`, `Hash`
- Provide both `_safe` and panic versions of methods

**Method Organization:**
- **Constructor**: `new(small_algebra: Rc<dyn SmallAlgebra>) -> Self`
- **Lattice Operations**: `join`, `meet`, `leq`, `zero`, `one`
- **Congruence Operations**: `cg`, `tg`, `principals`, `join_irreducibles`
- **Centrality Operations**: `commutator`, `weak_commutator`, `strong_rectangularity_commutator`
- **Utility Operations**: `is_distributive`, `permutability_level`, `type_set`

#### Java Wrapper Suitability
**Suitable for Java Wrapper**: YES
- Concrete class with clear public API
- Can be instantiated with a `SmallAlgebra`
- All public methods can be exposed through CLI
- No abstract methods or complex inheritance

**Wrapper Implementation Strategy:**
- Store input `SmallAlgebra` data during construction
- Expose all public methods through CLI commands
- Handle progress reporting through CLI output
- Use JSON serialization for complex return types

#### Testing Strategy
1. **Unit Tests**: Test individual methods with small algebras
2. **Integration Tests**: Test with various algebra types
3. **Performance Tests**: Test with larger algebras and timeouts
4. **Cross-Language Tests**: Compare Rust/Python/Java outputs
5. **Edge Case Tests**: Test with minimal algebras, empty results, etc.

#### Critical Implementation Notes
1. **Memory Management**: CongruenceLattice can be very large - implement lazy loading
2. **Progress Reporting**: Essential for long computations - implement proper callbacks
3. **Caching Strategy**: Cache expensive computations but allow invalidation
4. **Error Handling**: Many operations can fail - use proper Result types
5. **Thread Safety**: Static fields need proper synchronization
6. **Performance**: Some algorithms are computationally intensive - optimize carefully

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

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete

### Current Implementation Status (as of 2024-12-16)

**Overall Status: NOT STARTED (0% Complete)**

#### Component Status:
- **Rust Implementation**: ❌ **NOT IMPLEMENTED** - No CongruenceLattice struct exists
- **Python Bindings**: ❌ **NOT IMPLEMENTED** - No Python bindings exist
- **Java Wrapper**: ❌ **NOT IMPLEMENTED** - No Java wrapper exists
- **Tests**: ❌ **NOT IMPLEMENTED** - No tests exist

#### Dependency Analysis:
**Ready Dependencies (✅ Available):**
- `SmallAlgebra` - ✅ **COMPLETED** (Task 41)
- `Operation` - ✅ **COMPLETED** (Task 1)
- `OperationSymbol` - ✅ **COMPLETED** (Task 1)
- `SimilarityType` - ✅ **COMPLETED** (Task 2)
- `Partition` - ✅ **COMPLETED** (Task 5)
- `BasicPartition` - ✅ **COMPLETED** (Task 5)
- `IntArray` - ✅ **COMPLETED** (Task 23)
- `BinaryRelation` - ✅ **COMPLETED** (Task 21)
- `BasicBinaryRelation` - ✅ **COMPLETED** (Task 19)
- `Subtrace` - ✅ **COMPLETED** (Task 29)
- `Lattice` - ✅ **COMPLETED** (Task 20)
- `BasicLattice` - ✅ **COMPLETED** (Task 85)
- `SimpleList` - ✅ **COMPLETED** (Task 4)
- `ProgressReport` - ✅ **COMPLETED** (Task 34)

**Blocking Dependencies (❌ Missing):**
- `Subalgebra` - ❌ **PENDING** (Task 68) - Required for congruence as algebra operations
- `SubProductAlgebra` - ❌ **PENDING** (Task 83) - Required for tolerance and centrality calculations
- `BigProductAlgebra` - ❌ **PENDING** (Task 78) - Required for product algebra operations
- `SubalgebraLattice` - ❌ **PENDING** (Task 76) - Required for subalgebra lattice interface
- `CentralityData` - ❌ **PENDING** (Task 26) - Required for centrality calculations
- `TypeFinder` - ❌ **PENDING** (Task 46) - Required for TCT type finding

#### Implementation Priority:
**BLOCKED** - This task cannot proceed until critical dependencies are implemented. The following dependencies must be completed first:
1. `Subalgebra` (Task 68) - Core dependency for congruence operations
2. `SubProductAlgebra` (Task 83) - Required for tolerance calculations
3. `BigProductAlgebra` (Task 78) - Required for product operations
4. `CentralityData` (Task 26) - Required for centrality calculations
5. `TypeFinder` (Task 46) - Required for TCT analysis

#### Recommendations:
1. **Deprioritize this task** until blocking dependencies are resolved
2. **Implement blocking dependencies first** in the order listed above
3. **Consider implementing a simplified version** without TCT analysis if needed
4. **Plan for complex memory management** due to large lattice computations
5. **Implement progress reporting** for long-running computations

### Implementation Priority
**HIGH PRIORITY** - This is a core class with many dependencies. Should be implemented after:
- `SmallAlgebra` (Task 41)
- `Partition`/`BasicPartition` (Tasks 5, 6)
- `Lattice` interface (Task 20 - ✅ **COMPLETED**)
- `Operation`/`OperationSymbol` (Tasks 1, 45)
- `SimilarityType` (Task 2)

### Estimated Complexity
- **Rust Implementation**: High (complex algorithms, caching, progress reporting)
- **Python Bindings**: Medium (many methods, complex return types)
- **Java Wrapper**: Medium (many methods, complex data structures)
- **Testing**: High (performance testing, cross-language validation)

### Key Challenges
1. **Performance**: CongruenceLattice computations can be very expensive
2. **Memory Management**: Large lattices require careful memory management
3. **Progress Reporting**: Long computations need proper progress callbacks
4. **Caching**: Complex caching strategy for expensive computations
5. **Error Handling**: Many operations can fail in various ways
6. **Thread Safety**: Static fields need proper synchronization
