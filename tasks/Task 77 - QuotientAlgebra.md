# UACalc Rust/Python Translation Plan

## Task 77: Translate `QuotientAlgebra`

**Java File:** `org/uacalc/alg/QuotientAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::QuotientAlgebra`  
**Dependencies:** 12 (12 non-UI/example)  
**Estimated Public Methods:** 23

### Description
Translate the Java class `org.uacalc.alg.QuotientAlgebra` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Concrete class extending `GeneralAlgebra` and implementing `SmallAlgebra`
- **Purpose**: Represents a quotient algebra of a `SmallAlgebra` by a congruence relation
- **Key Fields**: 
  - `protected final SmallAlgebra superAlgebra` - The parent algebra
  - `protected final int[] representatives` - Representatives of congruence classes
  - `protected Partition congruence` - The congruence relation

### Public Methods (23 total)
1. `QuotientAlgebra(SmallAlgebra alg, Partition congruence)` - Constructor
2. `QuotientAlgebra(String name, SmallAlgebra alg, Partition congruence)` - Constructor with name
3. `makeOperationTables()` - Create operation tables for all operations
4. `superAlgebra()` - Get the super algebra
5. `getCongruence()` - Get the congruence partition
6. `con()` - Get congruence lattice (lazy initialization)
7. `sub()` - Get subalgebra lattice (lazy initialization)
8. `elementIndex(Object obj)` - Get element index in quotient algebra
9. `getElement(int index)` - Get element by index (returns QuotientElement)
10. `representativeIndex(int rep)` - Find index of representative in representatives array
11. `canonicalHomomorphism(int e)` - Get canonical homomorphism image
12. `getUniverseList()` - Get universe as list (returns null)
13. `getUniverseOrder()` - Get universe order (returns null)
14. `universe()` - Get universe as set
15. `convertToDefaultValueOps()` - Convert to default value operations (throws exception)
16. `algebraType()` - Get algebra type (returns QUOTIENT)
17. `makeUniverse()` - Create universe set (protected)
18. `makeOperations()` - Create operations (private)
19. `valueAt(List args)` - Operation value evaluation (in anonymous class)
20. `makeTable()` - Create operation table (in anonymous class)
21. `intValueAt(int[] args)` - Integer operation evaluation (in anonymous class)
22. `toString()` - String representation (inherited)
23. `main(String[] args)` - Main method for testing

### Dependencies Analysis

**Corrected Dependencies (12 total):**
- `org.uacalc.alg.GeneralAlgebra` - Parent class (Task 66 - ✅ **COMPLETED**)
- `org.uacalc.alg.SmallAlgebra` - Interface implemented (Task 41 - ✅ **COMPLETED**)
- `org.uacalc.alg.SmallAlgebra.AlgebraType` - Enum for algebra types (Task 41 - ✅ **COMPLETED**)
- `org.uacalc.alg.conlat.Partition` - Congruence partition (Task 5 - ✅ COMPLETED)
- `org.uacalc.alg.conlat.CongruenceLattice` - Congruence lattice (Task 80 - not completed)
- `org.uacalc.alg.sublat.SubalgebraLattice` - Subalgebra lattice (Task 76 - not completed)
- `org.uacalc.alg.op.AbstractOperation` - Abstract operation class (Task 11 - ✅ **COMPLETED**)
- `org.uacalc.alg.op.Operation` - Operation interface (Task 12 - ✅ **COMPLETED**)
- `org.uacalc.alg.op.Operations` - Operations utility (Task 50 - ✅ **COMPLETED**)
- `org.uacalc.io.AlgebraIO` - Algebra I/O (Task 65 - not completed)
- `org.uacalc.util.Horner` - Horner encoding (Task 3 - ✅ COMPLETED)
- `org.uacalc.util.Arrays` - Java Arrays utility (built-in)

**Dependency Status**: ⚠️ **PARTIALLY UNBLOCKED** - 6 out of 12 dependencies completed (core algebra and operation dependencies satisfied)

## Rust Implementation Recommendations

### Rust Construct Design
- **Rust Type**: `struct QuotientAlgebra` in `src/alg/quotient_algebra.rs`
- **Design Pattern**: Concrete struct implementing traits
- **Inheritance**: Implements `SmallAlgebra` trait, contains `GeneralAlgebra` functionality
- **Key Fields**:
  - `pub super_algebra: Box<dyn SmallAlgebra>` - Parent algebra (trait object for flexibility)
  - `pub representatives: Vec<usize>` - Representatives of congruence classes
  - `pub congruence: Partition` - The congruence relation
  - `pub operations: Vec<Box<dyn Operation>>` - Operations of the quotient algebra
  - `pub universe: HashSet<QuotientElement>` - Universe as set of quotient elements

### Method Organization
- **Constructor Methods**: `new()` and `new_with_name()` for constructors
- **Getter Methods**: All public getters become struct methods
- **Operation Methods**: `make_operation_tables()`, `make_operations()` for operation management
- **Lattice Methods**: `con()`, `sub()` for lazy initialization of lattices
- **Element Methods**: `element_index()`, `get_element()`, `representative_index()`, `canonical_homomorphism()`
- **Universe Methods**: `universe()`, `get_universe_list()`, `get_universe_order()`
- **Utility Methods**: `algebra_type()`, `convert_to_default_value_ops()`

### Generic vs Dynamic Dispatch
- **Recommendation**: Use dynamic dispatch with trait objects
- **Reasoning**: QuotientAlgebra needs to work with any SmallAlgebra implementation
- **Pattern**: `Box<dyn SmallAlgebra>` for super_algebra field
- **Operations**: Use `Box<dyn Operation>` for operations vector
- **Lifetime Management**: Use owned types where possible, `Rc<RefCell<T>>` for shared mutable state

### Implementation Dependencies
**Blocking Dependencies (must be completed first):**
- `GeneralAlgebra` (Task 66) - Base class functionality
- `SmallAlgebra` (Task 41) - Interface contract
- `CongruenceLattice` (Task 80) - For `con()` method
- `SubalgebraLattice` (Task 76) - For `sub()` method
- `AbstractOperation` (Task 11) - For operation creation
- `Operation` (Task 12) - Operation interface
- `Operations` (Task 50) - Operations utility
- `AlgebraIO` (Task 65) - For I/O operations

**Non-blocking Dependencies:**
- `Partition` (Task 5) - ✅ Already available
- `Horner` (Task 3) - ✅ Already available

## Java Wrapper Suitability
- **Suitable**: ✅ Yes - Concrete class with comprehensive public API
- **Reasoning**: 
  - Concrete class can be instantiated for testing
  - All 23 public methods are testable
  - Complex state management but manageable through constructor parameters
- **Wrapper Location**: `java_wrapper/src/alg/QuotientAlgebraWrapper.java`
- **Test Commands**: All constructors, getters, operation methods, element methods, universe methods

## Testing Strategy
- **Rust Tests**: Test all 23 public methods with `compare_with_java!` macro
- **Python Tests**: Test through Python bindings comparing against Java wrapper
- **Java Wrapper**: Create CLI commands for all methods
- **Test Data**: Use various SmallAlgebra instances with different congruences
- **Edge Cases**: Test with empty algebras, single-element algebras, complex congruences

## Implementation Recommendations

### 1. Rust Struct Design
```rust
pub struct QuotientAlgebra {
    pub super_algebra: Box<dyn SmallAlgebra>,
    pub representatives: Vec<usize>,
    pub congruence: Partition,
    pub operations: Vec<Box<dyn Operation>>,
    pub universe: HashSet<QuotientElement>,
    pub name: String,
    pub description: String,
    pub size: usize,
    pub con: Option<CongruenceLattice>,
    pub sub: Option<SubalgebraLattice>,
}

impl QuotientAlgebra {
    pub fn new(super_algebra: Box<dyn SmallAlgebra>, congruence: Partition) -> Self {
        Self::new_with_name("".to_string(), super_algebra, congruence)
    }
    
    pub fn new_with_name(name: String, super_algebra: Box<dyn SmallAlgebra>, congruence: Partition) -> Self {
        let representatives = congruence.representatives();
        let size = representatives.len();
        let universe = Self::make_universe(&super_algebra, &representatives);
        let operations = Self::make_operations(&super_algebra, &representatives, &congruence, size);
        
        Self {
            super_algebra,
            representatives,
            congruence,
            operations,
            universe,
            name,
            description: String::new(),
            size,
            con: None,
            sub: None,
        }
    }
    
    // ... other methods
}
```

### 2. Python Bindings
- Use `PyQuotientAlgebra` as internal struct name
- Export clean `QuotientAlgebra` name to Python
- Implement `__str__`, `__repr__`, `__eq__` magic methods
- Use `PyResult<T>` for error handling
- Handle trait objects properly in Python bindings

### 3. Java Wrapper Commands
- `new` - Constructor with super_algebra and congruence
- `newWithName` - Constructor with name, super_algebra, and congruence
- `makeOperationTables` - Create operation tables
- `superAlgebra` - Get super algebra
- `getCongruence` - Get congruence
- `con` - Get congruence lattice
- `sub` - Get subalgebra lattice
- `elementIndex` - Get element index
- `getElement` - Get element by index
- `representativeIndex` - Get representative index
- `canonicalHomomorphism` - Get canonical homomorphism
- `universe` - Get universe
- `algebraType` - Get algebra type
- All other public methods

## Blocking Issues
1. **Cannot implement until dependencies are ready**: 10 out of 12 dependencies must be completed first
2. **Task ordering**: This task should be moved much later in the dependency order
3. **Dependency count incorrect**: Should be 12 dependencies, not 8
4. **Complex trait object management**: Requires careful design for Python bindings

## Acceptance Criteria
- [ ] All 23 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] All 10 blocking dependencies implemented first
