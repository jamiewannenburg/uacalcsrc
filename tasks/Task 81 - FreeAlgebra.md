# Task 81: Translate `FreeAlgebra`

**Java File:** `org/uacalc/alg/FreeAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::FreeAlgebra`  
**Dependencies:** 15 (14 non-UI/example)  
**Estimated Public Methods:** ~19

## Description
Translate the Java class `org.uacalc.alg.FreeAlgebra` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Concrete class extending `SubProductAlgebra` and implementing `SmallAlgebra`
- **Rust Construct**: `struct` with trait implementations
- **Key Characteristics**:
  - Represents a subalgebra of a direct product of `SmallAlgebra`s
  - Allows construction of algebras too large to be `SmallAlgebra`s
  - Implements free algebra construction with generators and relations
  - Supports thinning of generators and subdirect decomposition

### Public Methods (19 total)
1. **Constructors (8 variants)**:
   - `FreeAlgebra(SmallAlgebra, int, List<Equation>, ProgressReport)`
   - `FreeAlgebra(SmallAlgebra, int)`
   - `FreeAlgebra(SmallAlgebra, int, ProgressReport)`
   - `FreeAlgebra(SmallAlgebra, int, boolean)`
   - `FreeAlgebra(SmallAlgebra, int, boolean, boolean)`
   - `FreeAlgebra(String, SmallAlgebra, int)`
   - `FreeAlgebra(String, SmallAlgebra, int, boolean)`
   - `FreeAlgebra(String, SmallAlgebra, int, boolean, boolean)`
   - `FreeAlgebra(String, SmallAlgebra, int, boolean, boolean, ProgressReport)`
   - `FreeAlgebra(SmallAlgebra, int, boolean, boolean, boolean, List<Equation>, ProgressReport)`
   - `FreeAlgebra(String, SmallAlgebra, int, boolean, boolean, boolean, List<Equation>, ProgressReport)`
   - `FreeAlgebra(String, BigProductAlgebra, List<IntArray>, List<IntArray>)`

2. **Instance Methods (7)**:
   - `getIdempotentTerms() -> List<Term>`
   - `algebraType() -> AlgebraType`
   - `switchXandYAutomorphism() -> Operation`

3. **Static Methods (2)**:
   - `findEquationOfAnotB(SmallAlgebra, SmallAlgebra, int[]) -> Equation`
   - `findEquationOfAnotB(SmallAlgebra, SmallAlgebra, int[], ProgressReport) -> Equation`

4. **Main Method (1)**:
   - `main(String[])` - for testing and CLI usage

## Dependencies Analysis

### Corrected Dependencies (15 total)
This class depends on:
- `org.uacalc.alg.SubProductAlgebra` (parent class)
- `org.uacalc.alg.SmallAlgebra` (interface)
- `org.uacalc.alg.SmallAlgebra.AlgebraType` (enum)
- `org.uacalc.alg.BigProductAlgebra` (used in constructors)
- `org.uacalc.alg.Closer` (used in findEquationOfAnotB)
- `org.uacalc.alg.AlgebraWithGeneratingVector` (used in setupSIProjections)
- `org.uacalc.alg.conlat.*` (congruence lattice operations)
- `org.uacalc.alg.op.Operation` (operation interface)
- `org.uacalc.alg.op.Operations` (operation utilities)
- `org.uacalc.alg.sublat.*` (subalgebra lattice operations)
- `org.uacalc.eq.Equation` (equation representation)
- `org.uacalc.io.AlgebraIO` (used in main method)
- `org.uacalc.terms.*` (Term, Variable, VariableImp)
- `org.uacalc.util.*` (IntArray, ArrayString, SequenceGenerator, ArrayIncrementor)
- `org.uacalc.ui.tm.ProgressReport` (progress reporting)

### Missing Dependencies (not in original list)
- `org.uacalc.alg.BigProductAlgebra` - Critical for construction
- `org.uacalc.alg.Closer` - Used in findEquationOfAnotB
- `org.uacalc.alg.AlgebraWithGeneratingVector` - Used in setupSIProjections
- `org.uacalc.util.IntArray` - Core data structure
- `org.uacalc.util.ArrayString` - Used in main method
- `org.uacalc.util.SequenceGenerator` - Used for iteration
- `org.uacalc.util.ArrayIncrementor` - Used for iteration

## Rust Implementation Recommendations

### Struct Design
```rust
pub struct FreeAlgebra {
    // Inherited from SubProductAlgebra
    product_algebra: BigProductAlgebra,
    gens: Vec<IntArray>,
    univ: Vec<IntArray>,
    thin_generators: bool,
    decompose: bool,
    univ_hash_map: HashMap<IntArray, usize>,
    terms: Vec<Term>,
    term_map: HashMap<IntArray, Term>,
    variables: Vec<Variable>,
    vars_map: HashMap<Variable, IntArray>,
    
    // FreeAlgebra specific
    name: String,
    size: usize,
}
```

### Trait Implementations
- `SmallAlgebra` - Main interface
- `Display` - String representation
- `Debug` - Debug representation
- `Clone` - Cloning support
- `PartialEq`, `Eq` - Equality comparison
- `Hash` - Hashing support

### Method Organization
- **Constructors**: Multiple `new` variants with different parameter combinations
- **Instance Methods**: Implement `SmallAlgebra` trait methods + specific methods
- **Static Methods**: Associated functions
- **Error Handling**: Use `Result<T, String>` for fallible operations

### Key Implementation Considerations
1. **Memory Management**: FreeAlgebra can be very large - consider memory limits
2. **Progress Reporting**: Integrate with progress reporting system
3. **Generator Thinning**: Implement coordinate projection thinning
4. **Subdirect Decomposition**: Support for SI algebra decomposition
5. **Term Mapping**: Maintain mapping between elements and terms
6. **Automorphism**: Support for generator switching automorphisms

## Usage Pattern Analysis

### Primary Usage Patterns
1. **Construction**: `new FreeAlgebra(alg, numGens)` - Most common
2. **With Relations**: `new FreeAlgebra(alg, numGens, relations, report)` - For finitely presented algebras
3. **With Options**: `new FreeAlgebra(alg, numGens, makeUniverse, thinGens)` - With configuration
4. **Equation Finding**: `FreeAlgebra.findEquationOfAnotB(A, B, gens)` - Static method

### Usage Context
- **Malcev.java**: Extensively used for term finding algorithms
- **UnaryTermsMonoid.java**: Used for unary term construction
- **Example classes**: Used for testing and demonstration
- **UI classes**: Used in computation panels

## Java Wrapper Suitability

### Assessment: **SUITABLE**
- **Reason**: Concrete class with public constructors and methods
- **Testing Strategy**: 
  - Test all constructor variants
  - Test instance methods (getIdempotentTerms, switchXandYAutomorphism)
  - Test static methods (findEquationOfAnotB)
  - Test main method with various arguments
- **CLI Commands**:
  - `construct` - Test various constructor combinations
  - `idempotent-terms` - Test getIdempotentTerms method
  - `automorphism` - Test switchXandYAutomorphism method
  - `find-equation` - Test findEquationOfAnotB static method
  - `main` - Test main method functionality

## Testing Strategy

### Rust Tests
- Test all constructor variants with various parameters
- Test instance methods with different algebra types
- Test static methods with various input combinations
- Test error conditions and edge cases
- Test memory limits and large algebra handling
- Compare results with Java implementation

### Python Tests
- Test Python bindings for all public methods
- Test constructor parameter combinations
- Test method chaining and complex operations
- Verify Python API matches Rust API exactly

### Java Wrapper Tests
- Test CLI commands with various arguments
- Test constructor parameter parsing
- Test method execution and result formatting
- Test error handling and validation

## Implementation Priority

### Phase 1: Core Structure
1. Implement basic struct and trait implementations
2. Implement core constructors
3. Implement basic SmallAlgebra trait methods

### Phase 2: Advanced Features
1. Implement generator thinning
2. Implement subdirect decomposition
3. Implement term mapping and operations

### Phase 3: Specialized Methods
1. Implement getIdempotentTerms
2. Implement switchXandYAutomorphism
3. Implement findEquationOfAnotB static method

### Phase 4: Testing and Validation
1. Create comprehensive test suite
2. Create Java wrapper
3. Create Python bindings
4. Validate against Java implementation

## Implementation Status

### Current Status: **READY FOR IMPLEMENTATION** (0% Complete)

**Last Updated:** 2025-01-27

### Component Status

#### Rust Implementation
- **Status:** Not Started
- **Location:** `src/alg/mod.rs` (line 26-28)
- **Quality:** N/A - Only struct declaration exists
- **Notes:** Only empty struct declaration with TODO comment

#### Python Bindings
- **Status:** Not Started  
- **Location:** Not found
- **Quality:** N/A
- **Notes:** No Python bindings found in uacalc_lib/src

#### Java Wrapper
- **Status:** Not Started
- **Location:** Not found
- **Quality:** N/A
- **Notes:** No Java wrapper found in java_wrapper/src

#### Tests
- **Status:** Not Started
- **Location:** Not found
- **Quality:** N/A
- **Notes:** No tests found for FreeAlgebra

### Dependency Analysis

#### Blocking Dependencies (Now Implemented)
- **SubProductAlgebra**: ✅ **FULLY IMPLEMENTED** (src/alg/sub_product_algebra.rs)
- **BigProductAlgebra**: ✅ **FULLY IMPLEMENTED** (src/alg/big_product_algebra.rs)
- **Closer**: ✅ **FULLY IMPLEMENTED** (src/alg/closer.rs)
- **AlgebraWithGeneratingVector**: ✅ **FULLY IMPLEMENTED** (src/alg/algebra_with_generating_vector.rs)

#### Ready Dependencies (Implemented)
- **IntArray**: ✅ Fully implemented (src/util/int_array.rs)
- **Equation**: ✅ Fully implemented (src/eq/equations.rs)
- **Term**: ✅ Fully implemented (src/terms/mod.rs)
- **ProgressReport**: ✅ Fully implemented (src/progress.rs)
- **SmallAlgebra**: ✅ Trait defined (src/alg/small_algebra.rs)
- **Operation**: ✅ Fully implemented (src/alg/op/)
- **CongruenceLattice**: ✅ Fully implemented (src/alg/conlat/)
- **SubalgebraLattice**: ✅ Fully implemented (src/alg/sublat/)

### Recommendations

1. **READY**: All major dependencies are now implemented
2. **Implementation Order**:
   - Create FreeAlgebra struct extending SubProductAlgebra
   - Implement constructor methods (8 variants)
   - Implement instance methods (7 methods)
   - Implement static methods (2 methods)
   - Add comprehensive tests
3. **Estimated Effort**: Medium - all dependencies available
4. **Key Features**: 
   - Free algebra construction with generators and relations
   - Thinning of generators and subdirect decomposition
   - Equation finding between algebras

## Acceptance Criteria
- [ ] All 19 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Memory limits properly handled
- [ ] Progress reporting integrated
- [ ] All dependency classes available
