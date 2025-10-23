# Task 57: Translate `PowerAlgebra`

**Java File:** `org/uacalc/alg/PowerAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::PowerAlgebra`  
**Dependencies:** 6 (6 non-UI/example)  
**Estimated Public Methods:** ~8

## Description
Translate the Java class `org.uacalc.alg.PowerAlgebra` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Java Type**: Concrete class extending `ProductAlgebra` implementing `SmallAlgebra`
- **Rust Construct**: Struct with trait implementations
- **Inheritance**: `PowerAlgebra extends ProductAlgebra implements SmallAlgebra`

### Public Methods Identified
1. `PowerAlgebra(SmallAlgebra alg, int power)` - Constructor
2. `PowerAlgebra(String name, SmallAlgebra alg, int power)` - Named constructor  
3. `getRoot()` - Returns the root algebra
4. `parent()` - Returns the root algebra (alias for getRoot)
5. `parents()` - Returns list containing root algebra
6. `getPower()` - Returns the power/exponent
7. `con()` - Returns congruence lattice (lazy initialization)
8. `sub()` - Returns subalgebra lattice (lazy initialization)
9. `algebraType()` - Returns `AlgebraType.POWER`

### Dependencies Analysis
**Corrected Dependencies** (analyzed from actual imports and usage):
- `org.uacalc.alg.ProductAlgebra` - **CRITICAL**: Parent class, not yet implemented
- `org.uacalc.alg.SmallAlgebra` - Interface, not yet implemented  
- `org.uacalc.alg.GeneralAlgebra` - **CRITICAL**: Grandparent class, not yet implemented
- `org.uacalc.alg.conlat.CongruenceLattice` - For `con()` method
- `org.uacalc.alg.sublat.SubalgebraLattice` - For `sub()` method
- `org.uacalc.alg.op.Operation` - For operations
- `org.uacalc.util.*` - Utility classes

**Missing Dependencies** (not listed in original task):
- `org.uacalc.alg.GeneralAlgebra` - Contains `con` and `sub` fields
- `org.uacalc.alg.ProductAlgebra` - Parent class with core functionality

## Rust Implementation Recommendations

### Struct Design
```rust
pub struct PowerAlgebra {
    // Inherited from ProductAlgebra
    pub algebras: Vec<Box<dyn SmallAlgebra>>,
    pub sizes: Vec<usize>,
    pub number_of_products: usize,
    pub size: usize,
    pub universe: Vec<Vec<usize>>, // Cartesian product
    
    // Inherited from GeneralAlgebra  
    pub operations: Vec<Box<dyn Operation>>,
    pub operations_map: HashMap<OperationSymbol, Box<dyn Operation>>,
    pub similarity_type: SimilarityType,
    pub universe_set: HashSet<Vec<usize>>,
    pub con: Option<Box<CongruenceLattice>>,
    pub sub: Option<Box<SubalgebraLattice>>,
    pub name: String,
    pub description: String,
    
    // PowerAlgebra specific
    pub root: Box<dyn SmallAlgebra>,
    pub root_size: usize,
}
```

### Trait Implementations
- Implement `SmallAlgebra` trait (when available)
- Implement `Display` for string representation
- Implement `Debug` for debugging
- Implement `Clone` if needed

### Method Organization
- **Constructor methods**: `new()`, `new_with_name()`
- **Accessor methods**: `get_root()`, `parent()`, `parents()`, `get_power()`
- **Lazy initialization methods**: `con()`, `sub()`
- **Type method**: `algebra_type()`

### Error Handling
- Use `Result<T, String>` for constructors that can fail
- Provide both `_safe` and panic versions of methods
- Validate power parameter (must be > 0)
- Handle memory overflow for large powers

### Generic vs Dynamic Dispatch
- Use `Box<dyn SmallAlgebra>` for root algebra (dynamic dispatch needed)
- Use `Box<dyn Operation>` for operations (dynamic dispatch needed)
- Use concrete types where possible for performance

## Java Wrapper Suitability
**NOT SUITABLE** - This is a concrete class that can be instantiated, but it depends on:
1. `ProductAlgebra` (not yet implemented)
2. `SmallAlgebra` interface (not yet implemented)  
3. `GeneralAlgebra` (not yet implemented)

The wrapper should be created after these dependencies are implemented.

## Testing Strategy
1. **Unit Tests**: Test all public methods with small test algebras
2. **Integration Tests**: Test with various algebra types as roots
3. **Edge Cases**: Test power=0, power=1, very large powers
4. **Memory Tests**: Test with algebras that would cause memory issues
5. **Cross-language Tests**: Compare with Java implementation

## Current Implementation Status

### Implementation Status Verification
- **Rust Implementation**: ❌ **NOT IMPLEMENTED** - Only empty struct stub exists in `src/alg/mod.rs`
- **Python Bindings**: ❌ **NOT IMPLEMENTED** - No bindings found in `uacalc_lib/src/`
- **Java Wrapper**: ❌ **NOT IMPLEMENTED** - No wrapper found in `java_wrapper/src/`
- **Tests**: ❌ **NOT IMPLEMENTED** - No tests found

### Dependency Analysis
**Critical Dependencies Status:**
- `GeneralAlgebra` ✅ **COMPLETED** - Fully implemented in `src/alg/general_algebra.rs`
- `SmallAlgebra` ✅ **COMPLETED** - Trait implemented in `src/alg/small_algebra.rs`
- `ProductAlgebra` ❌ **NOT IMPLEMENTED** - Only empty struct stub exists
- `CongruenceLattice` ❌ **NOT IMPLEMENTED** - Only empty struct stub exists in `src/alg/sublat/mod.rs`
- `SubalgebraLattice` ❌ **NOT IMPLEMENTED** - Only empty struct stub exists in `src/alg/sublat/mod.rs`

**Blocking Dependencies:**
- `ProductAlgebra` - Parent class, must be implemented first
- `CongruenceLattice` - Required for `con()` method
- `SubalgebraLattice` - Required for `sub()` method

## Implementation Priority
🚫 **BLOCKED** - Critical dependencies missing:
<<<<<<< Current (Your changes)
1. `ProductAlgebra` (Task 73 - ProductAlgebra) ❌ **NOT IMPLEMENTED**
=======
1. `ProductAlgebra` (Task 73 - ProductAlgebra) ✅ **PARTIALLY IMPLEMENTED** (70% complete, core methods available)
>>>>>>> Incoming (Background Agent changes)
2. `CongruenceLattice` (Task 45 - CongruenceLattice) ❌ **NOT IMPLEMENTED**
3. `SubalgebraLattice` (Task 46 - SubalgebraLattice) ❌ **NOT IMPLEMENTED**

## Acceptance Criteria
- [ ] **BLOCKED**: Dependencies must be implemented first
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods  
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
