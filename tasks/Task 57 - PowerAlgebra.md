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
- **Rust Implementation**: ✅ **PARTIALLY IMPLEMENTED** - Core struct and methods implemented in `src/alg/mod.rs`
- **Python Bindings**: ✅ **PARTIALLY IMPLEMENTED** - Basic bindings added in `uacalc_lib/src/alg.rs`
- **Java Wrapper**: ✅ **PARTIALLY IMPLEMENTED** - CLI wrapper created in `java_wrapper/src/alg/PowerAlgebraWrapper.java`
- **Tests**: ✅ **PASSING** - All Rust and Python tests pass

### Dependency Analysis
**Critical Dependencies Status:**
- `GeneralAlgebra` ✅ **COMPLETED** - Fully implemented in `src/alg/general_algebra.rs`
- `SmallAlgebra` ✅ **COMPLETED** - Trait implemented in `src/alg/small_algebra.rs`
- `ProductAlgebra` ✅ **COMPLETED** - Fully implemented in `src/alg/product_algebra.rs`
- `CongruenceLattice` ❌ **NOT IMPLEMENTED** - Only empty struct stub exists in `src/alg/sublat/mod.rs`
- `SubalgebraLattice` ❌ **NOT IMPLEMENTED** - Only empty struct stub exists in `src/alg/sublat/mod.rs`

**Remaining Dependencies:**
- `CongruenceLattice` - Required for `con()` method (deferred)
- `SubalgebraLattice` - Required for `sub()` method (deferred)

## Implementation Priority
✅ **PARTIALLY COMPLETE** - Core functionality implemented, lattice methods deferred:
1. `ProductAlgebra` (Task 73 - ProductAlgebra) ✅ **COMPLETED**
2. `CongruenceLattice` (Task 45 - CongruenceLattice) ❌ **DEFERRED** - Not needed for partial implementation
3. `SubalgebraLattice` (Task 46 - SubalgebraLattice) ❌ **DEFERRED** - Not needed for partial implementation

## Acceptance Criteria
- [x] **COMPLETED**: Core dependencies implemented (ProductAlgebra, SmallAlgebra, GeneralAlgebra)
- [x] **PARTIALLY COMPLETE**: Core public methods translated to Rust (excluding lattice methods)
- [x] **PARTIALLY COMPLETE**: Python bindings expose core public methods (excluding lattice methods)
- [x] **PARTIALLY COMPLETE**: Java CLI wrapper created with core public methods (excluding lattice methods)
- [x] **COMPLETED**: Rust tests pass with timeouts enabled
- [x] **COMPLETED**: Python tests pass and match Java output
- [x] **COMPLETED**: Code compiles without warnings
- [ ] **DEFERRED**: Lattice methods (con(), sub()) - requires CongruenceLattice and SubalgebraLattice
- [ ] **DEFERRED**: Full documentation for lattice methods

## Implemented Methods
✅ **Core Methods Implemented:**
- `new_safe()` - Safe constructor with error handling
- `new_with_name_safe()` - Named constructor with error handling
- `new()` - Panic constructor
- `new_with_name()` - Named panic constructor
- `get_root()` - Returns the root algebra
- `parent()` - Returns the root algebra (alias for getRoot)
- `parents()` - Returns list containing root algebra
- `get_power()` - Returns the power/exponent
- `get_root_size()` - Returns the size of the root algebra
- `cardinality()` - Returns the total cardinality
- `name()` - Returns the algebra name
- `set_name()` - Sets the algebra name
- `description()` - Returns the algebra description
- `set_description()` - Sets the algebra description
- `algebra_type()` - Returns `AlgebraType.POWER`
- `operations()` - Returns list of operations (placeholder implementation)
- `is_unary()` - Checks if all operations are unary
- `is_idempotent()` - Checks if all operations are idempotent
- `is_total()` - Checks if all operations are total
- `__str__()` - String representation
- `__repr__()` - Debug representation
- `__eq__()` - Equality comparison
- `__hash__()` - Hash function

❌ **Deferred Methods (require lattice implementations):**
- `con()` - Returns congruence lattice (lazy initialization)
- `sub()` - Returns subalgebra lattice (lazy initialization)
