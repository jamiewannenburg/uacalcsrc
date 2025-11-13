# Task 82: Translate `Algebras`

**Java File:** `org/uacalc/alg/Algebras.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::Algebras`  
**Dependencies:** 15+ (many critical dependencies missing)  
**Estimated Public Methods:** ~23

## Java Class Analysis

### Class Type
- **Type**: Utility class with static methods only
- **Purpose**: Collection of static utility methods for algebra operations and analysis
- **Key Pattern**: All methods are static - no instance state
- **Constructor**: Private constructor to prevent instantiation

### Public Methods Analysis (23 total)
1. `unaryCloneAlgFromPartitions(List<Partition>, List<Partition>)` - Creates unary clone algebra from partitions
2. `unaryCloneAlgFromPartitions(List<Partition>, Partition, Partition)` - Creates unary clone algebra with eta partitions
3. `unaryClone(List<Partition>, Partition, Partition)` - Computes unary clone set
4. `findNUF(SmallAlgebra, int)` - Finds near unanimity term
5. `jonssonTerms(SmallAlgebra)` - Returns Jonsson terms for distributive variety
6. `jonssonLevel(SmallAlgebra)` - Returns minimal number of Jonsson terms
7. `isEndomorphism(Operation, SmallAlgebra)` - Tests if operation is endomorphism
8. `isHomomorphism(int[], SmallAlgebra, SmallAlgebra)` - Tests if map is homomorphism
9. `matrixPower(SmallAlgebra, int)` - Creates matrix power algebra
10. `fullTransformationSemigroup(int, boolean, boolean)` - Creates transformation semigroup
11. `findInClone(List<Operation>, SmallAlgebra, ProgressReport)` - Finds operations in clone
12. `makeRandomAlgebra(int, SimilarityType)` - Creates random algebra
13. `makeRandomAlgebra(int, SimilarityType, long)` - Creates random algebra with seed
14. `makeRandomAlgebra(int, int[])` - Creates random algebra with arities
15. `makeRandomAlgebra(int, int[], long)` - Creates random algebra with arities and seed
16. `ternaryDiscriminatorAlgebra(int)` - Creates ternary discriminator algebra
17. `memberOfQuasivariety(SmallAlgebra, SmallAlgebra, ProgressReport)` - Tests quasivariety membership
18. `memberOfQuasivariety(SmallAlgebra, List<SmallAlgebra>, ProgressReport)` - Tests quasivariety membership
19. `memberOfQuasivarietyGenByProperSubs(SmallAlgebra, ProgressReport)` - Tests membership in proper subalgebras
20. `quasiCriticalCongruences(SmallAlgebra, ProgressReport)` - Finds quasi-critical congruences
21. `quasiCritical(SmallAlgebra)` - Tests if algebra is quasi-critical
22. `quasiCritical(SmallAlgebra, ProgressReport)` - Tests if algebra is quasi-critical with report
23. `main(String[])` - Main method for testing

### Dependencies Analysis

**Critical Dependencies:**
- `SmallAlgebra` - ✅ **COMPLETED** - Core algebra interface (Task 41)
- `BasicAlgebra` - ✅ **COMPLETED** - Basic algebra implementation (Task 71)
- `QuotientAlgebra` - ✅ **COMPLETED** - Quotient algebra (Task 77)
- `Operation` - ✅ **COMPLETED** - Operation interface (Task 12)
- `Operations` - ✅ **COMPLETED** - Operation factory class (Task 50)
- `OperationSymbol` - ✅ **COMPLETED** - Operation symbol (Task 1)
- `SimilarityType` - ✅ **COMPLETED** - Similarity type (Task 2)
- `Partition` - ✅ **COMPLETED** - Partition class (Task 5)
- `IntArray` - ✅ **COMPLETED** - Integer array utility (Task 23)
- `Malcev` - ✅ **COMPLETED** - Malcev operations (Task 63)
- `FreeAlgebra` - ✅ **COMPLETED** - Free algebra (Task 81)
- `Closer` - ✅ **COMPLETED** - Closer for term generation (Task 84)
- `SubalgebraLattice` - ✅ **COMPLETED** - Subalgebra lattice (Task 76)
- `PowerAlgebra` - ✅ **COMPLETED** - Power algebra (Task 57)
- `Homomorphism` - ✅ **COMPLETED** - Homomorphism class (Task 43)
- `Term` - ✅ **COMPLETED** - Term class (Task 56)
- `Horner` - ✅ **COMPLETED** - Horner encoding (Task 3)
- `ArrayIncrementor` - ✅ **COMPLETED** - Array incrementor (Task 14)
- `SequenceGenerator` - ✅ **COMPLETED** - Sequence generator (Task 15)

**UI Dependencies (can be made optional):**
- `ProgressReport` - ✅ **COMPLETED** - Progress reporting interface (implemented as trait in `src/progress.rs`)

## Rust Implementation Recommendations

### 1. Struct Design
```rust
// Since Algebras is a utility class with only static methods,
// we don't need a struct - just implement as a module with functions
pub mod algebras {
    // All methods will be public functions, not methods
}
```

### 2. Method Organization
- **Static Methods → Free Functions**: All Java static methods become Rust free functions
- **Error Handling**: Use `Result<T, String>` for methods that can fail
- **Optional Parameters**: Use `Option<T>` for optional parameters
- **Collections**: Use `Vec<T>` instead of `List<T>`

### 3. Key Implementation Patterns
```rust
// Example method signature translation
pub fn find_nuf(alg: &SmallAlgebra, arity: i32) -> Option<Term> {
    // Implementation
}

pub fn make_random_algebra_safe(
    n: i32, 
    sim_type: &SimilarityType, 
    seed: Option<i64>
) -> Result<BasicAlgebra, String> {
    // Implementation with proper error handling
}
```

### 4. Dependencies Resolution
- **Cannot implement until dependencies are complete**: This class has too many critical dependencies
- **Priority order**: Implement in dependency order (Tasks 1-84 before this)
- **Mock implementations**: Consider creating mock implementations for testing

### 5. Java Wrapper Suitability
- **Suitable for testing**: Yes, once dependencies are implemented
- **All methods can be exposed**: All 23 public methods can be wrapped
- **Complex parameter types**: Will need careful handling of collections and complex objects

## Implementation Status

### Current State
- **Rust Implementation**: Not started (blocked by dependencies)
- **Python Bindings**: Not created (blocked by dependencies)
- **Java Wrapper**: Not created (blocked by dependencies)
- **Tests**: Not created (blocked by dependencies)

### Dependency Analysis

**✅ ALL DEPENDENCIES COMPLETED:**
- `OperationSymbol` (Task 1) - ✅ **COMPLETED** - Full implementation in `src/alg/op/mod.rs`
- `SimilarityType` (Task 2) - ✅ **COMPLETED** - Full implementation in `src/alg/op/mod.rs`
- `Partition` (Task 5) - ✅ **COMPLETED** - Full implementation in `src/alg/conlat/partition.rs`
- `IntArray` (Task 23) - ✅ **COMPLETED** - Full implementation in `src/util/int_array.rs`
- `Horner` (Task 3) - ✅ **COMPLETED** - Full implementation in `src/util/horner.rs`
- `ArrayIncrementor` (Task 14) - ✅ **COMPLETED** - Full implementation in `src/util/array_incrementor.rs`
- `SequenceGenerator` (Task 15) - ✅ **COMPLETED** - Full implementation in `src/util/sequence_generator.rs`
- `Operations` (Task 50) - ✅ **COMPLETED** - Full implementation in `src/alg/op/operations.rs`
- `Term` (Task 56) - ✅ **COMPLETED** - Full implementation in `src/terms/mod.rs`
- `SmallAlgebra` (Task 41) - ✅ **COMPLETED** - Fully implemented trait with concrete implementations
- `BasicAlgebra` (Task 71) - ✅ **COMPLETED** - Fully implemented in `src/alg/basic_algebra.rs`
- `QuotientAlgebra` (Task 77) - ✅ **COMPLETED** - Fully implemented in `src/alg/quotient_algebra.rs`
- `Operation` (Task 12) - ✅ **COMPLETED** - Fully implemented trait in `src/alg/op/operation.rs`
- `Malcev` (Task 63) - ✅ **COMPLETED** - Fully implemented in `src/alg/malcev.rs`
- `FreeAlgebra` (Task 81) - ✅ **COMPLETED** - Fully implemented in `src/alg/free_algebra.rs`
- `Closer` (Task 84) - ✅ **COMPLETED** - Fully implemented in `src/alg/closer.rs`
- `SubalgebraLattice` (Task 76) - ✅ **COMPLETED** - Fully implemented in `src/alg/sublat/mod.rs`
- `PowerAlgebra` (Task 57) - ✅ **COMPLETED** - Fully implemented in `src/alg/power_algebra.rs`
- `Homomorphism` (Task 43) - ✅ **COMPLETED** - Fully implemented in `src/alg/homomorphism.rs`
- `ProgressReport` - ✅ **COMPLETED** - Progress reporting trait in `src/progress.rs`

## Testing Strategy

### Rust Tests
- Test all 23 public methods
- Use mock implementations for dependencies initially
- Test error conditions and edge cases
- Compare against Java implementation

### Python Tests
- Expose all methods through Python bindings
- Test parameter validation
- Test return value types

### Java Wrapper
- Create comprehensive CLI wrapper
- Support all method signatures
- Handle complex parameter types (collections, objects)
- Output results in JSON format for comparison

## Acceptance Criteria
- [ ] All 23 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] **All blocking dependencies implemented first**

## Current Implementation Status
- **Status**: ✅ READY (All dependencies complete)
- **Completion**: 0% (0/23 methods implemented)
- **Rust Implementation**: ❌ Not started
- **Python Bindings**: ❌ Not started
- **Java Wrapper**: ❌ Not started
- **Tests**: ❌ Not started

## Public Methods List

All 23 public static methods from `org/uacalc/alg/Algebras.java`:

- [ ] `unaryCloneAlgFromPartitions(List<Partition> pars, List<Partition> decomp)` - Creates unary clone algebra from partitions (WARNING: not complete in Java)
- [ ] `unaryCloneAlgFromPartitions(List<Partition> pars, Partition eta0, Partition eta1)` - Creates unary clone algebra with eta partitions
- [ ] `unaryClone(List<Partition> pars, Partition eta0, Partition eta1)` - Computes unary clone set (returns NavigableSet<IntArray>)
- [ ] `findNUF(SmallAlgebra alg, int arity)` - Finds near unanimity term (delegates to Malcev.nuTerm)
- [ ] `jonssonTerms(SmallAlgebra alg)` - Returns Jonsson terms for distributive variety (delegates to Malcev.jonssonTerms)
- [ ] `jonssonLevel(SmallAlgebra alg)` - Returns minimal number of Jonsson terms (delegates to Malcev.jonssonLevel)
- [x] `isEndomorphism(Operation endo, SmallAlgebra alg)` - Tests if operation is endomorphism ✅
- [ ] `isHomomorphism(int[] map, SmallAlgebra alg0, SmallAlgebra alg1)` - Tests if map is homomorphism
- [ ] `matrixPower(SmallAlgebra alg, int k)` - Creates matrix power algebra
- [ ] `fullTransformationSemigroup(int n, boolean includeConstants, boolean includeId)` - Creates transformation semigroup
- [ ] `findInClone(List<Operation> ops, SmallAlgebra A, ProgressReport report)` - Finds operations in clone
- [ ] `makeRandomAlgebra(int n, SimilarityType simType)` - Creates random algebra
- [ ] `makeRandomAlgebra(int n, SimilarityType simType, long seed)` - Creates random algebra with seed
- [ ] `makeRandomAlgebra(int n, int[] arities)` - Creates random algebra with arities
- [ ] `makeRandomAlgebra(int n, int[] arities, long seed)` - Creates random algebra with arities and seed
- [ ] `ternaryDiscriminatorAlgebra(int card)` - Creates ternary discriminator algebra
- [ ] `memberOfQuasivariety(SmallAlgebra A, SmallAlgebra B, ProgressReport report)` - Tests quasivariety membership
- [ ] `memberOfQuasivariety(SmallAlgebra A, List<SmallAlgebra> genAlgs, ProgressReport report)` - Tests quasivariety membership
- [ ] `memberOfQuasivarietyGenByProperSubs(SmallAlgebra A, ProgressReport report)` - Tests membership in proper subalgebras
- [ ] `quasiCriticalCongruences(SmallAlgebra A, ProgressReport report)` - Finds quasi-critical congruences
- [ ] `quasiCritical(SmallAlgebra A)` - Tests if algebra is quasi-critical
- [ ] `quasiCritical(SmallAlgebra A, ProgressReport report)` - Tests if algebra is quasi-critical with report
- [ ] `main(String[] args)` - Main method for testing (not needed in Rust)
