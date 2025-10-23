# Task 68: Translate `Subalgebra`

**Java File:** `org/uacalc/alg/Subalgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::Subalgebra`  
**Dependencies:** 8 (8 non-UI/example) - **CORRECTED**  
**Estimated Public Methods:** 26

## Java Class Analysis

### Class Structure
- **Type**: Concrete class extending `GeneralAlgebra` and implementing `SmallAlgebra`
- **Purpose**: Represents a subalgebra of a `SmallAlgebra` with a restricted universe
- **Key Features**: 
  - Maintains reference to super algebra
  - Manages subuniverse as sorted array
  - Creates restricted operations that delegate to super algebra
  - Provides lattice operations (congruence and subalgebra lattices)

### Public Methods (26 total)
1. **Constructors (4)**:
   - `Subalgebra(SmallAlgebra alg, int[] univ)`
   - `Subalgebra(SmallAlgebra alg, IntArray univ)`
   - `Subalgebra(String name, SmallAlgebra alg, IntArray univ)`
   - `Subalgebra(String name, SmallAlgebra alg, int[] univ)`

2. **Core Methods (8)**:
   - `index(int k)` - Find index in subalgebra for super algebra element
   - `restrictPartition(Partition par)` - Restrict partition to subalgebra
   - `makeOperations()` - Create restricted operations (private)
   - `makeOperationTables()` - Build operation tables
   - `superAlgebra()` - Get super algebra reference
   - `getSubuniverseArray()` - Get subuniverse array
   - `con()` - Get congruence lattice
   - `sub()` - Get subalgebra lattice

3. **Element Access (4)**:
   - `elementIndex(Object obj)` - Get element index
   - `getElement(int index)` - Get element by index
   - `getUniverseList()` - Get universe as list (returns null)
   - `getUniverseOrder()` - Get universe order (returns null)
   - `universe()` - Get universe set

4. **Static Methods (2)**:
   - `congruenceAsAlgebra(SmallAlgebra alg, Partition cong)`
   - `congruenceAsAlgebra(String name, SmallAlgebra alg, Partition cong)`

5. **Utility Methods (3)**:
   - `convertToDefaultValueOps()` - Throws UnsupportedOperationException
   - `algebraType()` - Returns `AlgebraType.SUBALGEBRA`
   - `main(String[] args)` - Test method

6. **Private Methods (5)**:
   - `makeUniverse()` - Create universe set
   - Various helper methods in operation creation

### Dependencies Analysis

**CORRECTED DEPENDENCIES:**
This class depends on:
- `org.uacalc.alg.SmallAlgebra` (Task 41 - ✅ **COMPLETED**) - Interface implementation
- `org.uacalc.alg.SmallAlgebra.AlgebraType` (Task 41 - ✅ **COMPLETED**) - Enum type
- `org.uacalc.alg.GeneralAlgebra` (Task 66 - ✅ **COMPLETED**) - Parent class
- `org.uacalc.alg.conlat.Partition` (Task 5 - COMPLETED) - Partition operations
- `org.uacalc.alg.conlat.BasicPartition` (Task 5 - COMPLETED) - Partition creation
- `org.uacalc.alg.conlat.CongruenceLattice` (Task 80 - NOT COMPLETED) - Lattice operations
  - **Note**: Task 20 (Lattice interface) is ✅ **COMPLETED**
- `org.uacalc.alg.sublat.SubalgebraLattice` (Task 76 - NOT COMPLETED) - Lattice operations
- `org.uacalc.alg.op.AbstractOperation` (Task 11 - ✅ **COMPLETED**) - Operation creation
- `org.uacalc.alg.op.Operation` (Task 12 - ✅ **COMPLETED**) - Operation interface
- `org.uacalc.alg.op.Operations` (Task 50 - ✅ **COMPLETED**) - Operation utilities
- `org.uacalc.alg.ProductAlgebra` (Task 57 - NOT COMPLETED) - Used in static methods
- `org.uacalc.util.IntArray` (Task 23 - COMPLETED) - Array wrapper
- `org.uacalc.util.Horner` (Task 3 - COMPLETED) - Horner encoding
- `java.util.*` - Standard Java collections

**Dependency Status**: ⚠️ **PARTIALLY UNBLOCKED** - 6 out of 13 dependencies completed (core algebra and operation dependencies satisfied)

## Rust Implementation Recommendations

### 1. Struct Design
```rust
/// A subalgebra of a SmallAlgebra with a restricted universe.
/// 
/// This struct represents a subalgebra by maintaining a reference to the
/// super algebra and a sorted array of universe indices that form the
/// subuniverse. All operations are restricted to this subuniverse.
pub struct Subalgebra {
    /// Name of the subalgebra
    name: String,
    /// Reference to the super algebra
    super_algebra: Box<dyn SmallAlgebra>,
    /// Sorted array of universe indices forming the subuniverse
    univ_array: Vec<i32>,
    /// Size of the subuniverse
    size: usize,
    /// Universe set (cached)
    universe: HashSet<Element>,
    /// Operations restricted to this subalgebra
    operations: Vec<Box<dyn Operation>>,
    /// Congruence lattice (lazy initialization)
    con: Option<CongruenceLattice>,
    /// Subalgebra lattice (lazy initialization)
    sub: Option<SubalgebraLattice>,
}
```

### 2. Trait Implementation
```rust
impl SmallAlgebra for Subalgebra {
    fn algebra_type(&self) -> AlgebraType {
        AlgebraType::Subalgebra
    }
    
    fn get_element(&self, k: usize) -> Option<Element> {
        if k < self.size {
            self.super_algebra.get_element(self.univ_array[k] as usize)
        } else {
            None
        }
    }
    
    fn element_index(&self, elem: &Element) -> Option<usize> {
        if let Some(super_index) = self.super_algebra.element_index(elem) {
            self.index(super_index as i32)
        } else {
            None
        }
    }
    
    // ... other trait methods
}
```

### 3. Key Implementation Patterns

#### Constructor Pattern
```rust
impl Subalgebra {
    /// Create a new subalgebra with the given super algebra and subuniverse.
    pub fn new_safe(
        name: String,
        super_algebra: Box<dyn SmallAlgebra>,
        univ: Vec<i32>
    ) -> Result<Self, String> {
        // Validate inputs
        if univ.is_empty() {
            return Err("Subuniverse cannot be empty".to_string());
        }
        
        // Sort and validate universe indices
        let mut univ_array = univ;
        univ_array.sort();
        univ_array.dedup();
        
        // Validate indices are within super algebra bounds
        let super_size = super_algebra.cardinality();
        for &idx in &univ_array {
            if idx < 0 || idx >= super_size as i32 {
                return Err(format!("Invalid universe index: {}", idx));
            }
        }
        
        let size = univ_array.len();
        let universe = Self::make_universe(&super_algebra, &univ_array)?;
        
        Ok(Subalgebra {
            name,
            super_algebra,
            univ_array,
            size,
            universe,
            operations: Vec::new(),
            con: None,
            sub: None,
        })
    }
}
```

#### Operation Restriction Pattern
```rust
impl Subalgebra {
    /// Create restricted operations that delegate to the super algebra.
    fn make_operations(&mut self) -> Result<(), String> {
        let k = self.super_algebra.operations().len();
        let mut ops = Vec::with_capacity(k);
        
        for i in 0..k {
            let super_op = &self.super_algebra.operations()[i];
            let arity = super_op.arity();
            
            // Create a restricted operation that maps subalgebra indices
            // to super algebra indices, applies the operation, then maps back
            let restricted_op = RestrictedOperation::new(
                super_op.symbol().clone(),
                self.size,
                arity,
                self.univ_array.clone(),
                super_op.clone(),
            )?;
            
            ops.push(Box::new(restricted_op));
        }
        
        self.operations = ops;
        Ok(())
    }
}
```

### 4. Critical Implementation Notes

#### Binary Search for Index Mapping
- The `index()` method uses binary search to find subalgebra index for super algebra element
- This requires the `univ_array` to be kept sorted
- Returns negative value if element not in subalgebra

#### Lazy Lattice Initialization
- Both `con()` and `sub()` methods use lazy initialization
- Store as `Option<LatticeType>` and create on first access
- This matches Java's pattern of checking for null

#### Static Method Translation
- `congruenceAsAlgebra()` methods should be associated functions (not methods)
- Use `ProductAlgebra` to create A² algebra
- Use `Horner` encoding for universe pairs

#### Error Handling Strategy
- Use `Result<T, String>` for constructors and operations that can fail
- Provide both `_safe` and `_panic` versions for compatibility
- Validate all inputs thoroughly

### 5. Python Bindings Strategy

#### PyO3 Implementation
```rust
#[pyclass]
pub struct PySubalgebra {
    inner: Subalgebra,
}

#[pymethods]
impl PySubalgebra {
    #[new]
    #[pyo3(signature = (name, super_algebra, univ))]
    fn new(name: String, super_algebra: PySmallAlgebra, univ: Vec<i32>) -> PyResult<Self> {
        match Subalgebra::new_safe(name, super_algebra.into(), univ) {
            Ok(inner) => Ok(PySubalgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn index(&self, k: i32) -> PyResult<i32> {
        Ok(self.inner.index(k))
    }
    
    // ... other methods
}
```

### 6. Java Wrapper Suitability

**✅ SUITABLE** - Subalgebra is a concrete class that can be instantiated and tested.

#### Java Wrapper Commands
- `create` - Create subalgebra with given super algebra and universe
- `index` - Find index of element in subalgebra
- `restrict_partition` - Restrict partition to subalgebra
- `congruence_as_algebra` - Static method to create congruence as algebra
- `get_super_algebra` - Get reference to super algebra
- `get_subuniverse` - Get subuniverse array
- `make_operation_tables` - Build operation tables
- `test` - Run basic functionality tests

### 7. Testing Strategy

#### Rust Tests
- Test all constructors with valid and invalid inputs
- Test `index()` method with elements in and out of subalgebra
- Test `restrictPartition()` with various partitions
- Test static `congruenceAsAlgebra()` methods
- Test operation restriction and delegation
- Test lazy lattice initialization

#### Python Tests
- Test subalgebra creation and basic operations
- Test element access and indexing
- Test lattice operations
- Compare results with Java wrapper output

#### Edge Cases
- Empty subuniverse (should fail)
- Invalid universe indices (should fail)
- Single element subalgebra
- Full universe subalgebra (should be isomorphic to super algebra)

### 8. Implementation Priority

**BLOCKED** - Cannot implement until dependencies are completed:
1. **SmallAlgebra** (Task 41) - Core interface
2. **GeneralAlgebra** (Task 66) - Parent class
3. **CongruenceLattice** (Task 80) - Lattice operations
   - **Note**: Task 20 (Lattice interface) is ✅ **COMPLETED**
4. **SubalgebraLattice** (Task 76) - Lattice operations
5. **Operation/AbstractOperation** (Task 12) - Operation system
6. **Operations** (Task 50) - Operation utilities
7. **ProductAlgebra** (Task 57) - Used in static methods

## Current Implementation Status

### Implementation Status: **PARTIALLY IMPLEMENTED** (70% Complete)

**Status Date:** 2025-10-23

### Component Status
- **Rust Implementation**: ✅ **PARTIALLY IMPLEMENTED** - Core struct and methods implemented in `src/alg/subalgebra.rs`
  - ✅ Constructors (new, new_safe)
  - ✅ Core methods (index, restrict_partition, super_algebra, get_subuniverse_array)
  - ✅ Element access (element_index, get_element)
  - ✅ SmallAlgebra trait implementation
  - ✅ RestrictedOperation for delegating to super algebra
  - ❌ Congruence lattice methods (con) - SKIPPED (requires CongruenceLattice)
  - ❌ Subalgebra lattice methods (sub) - SKIPPED (requires SubalgebraLattice)
  - ❌ Static congruenceAsAlgebra methods - SKIPPED (requires ProductAlgebra)
- **Python Bindings**: ✅ **IMPLEMENTED** - PySubalgebra in `uacalc_lib/src/alg.rs`
  - ✅ All core methods exposed
  - ✅ Partition restriction support
  - ❌ Lattice methods not exposed (dependencies missing)
- **Java Wrapper**: ✅ **IMPLEMENTED** - SubalgebraWrapper in `java_wrapper/src/alg/SubalgebraWrapper.java`
  - ✅ All core commands (create, index, restrict_partition, etc.)
  - ✅ Test command for basic functionality
  - ❌ Lattice-related commands not implemented (dependencies missing)
- **Tests**: ⚠️ **PARTIAL** - Compilation tests pass, specific tests not yet added

### Dependency Analysis

**BLOCKING DEPENDENCIES** (Must be completed first):
- `CongruenceLattice` (Task 80) - ❌ **NOT IMPLEMENTED** - Required for `con()` method
- `SubalgebraLattice` (Task 76) - ❌ **NOT IMPLEMENTED** - Required for `sub()` method  
- `ProductAlgebra` (Task 73) - ✅ **PARTIALLY IMPLEMENTED** (70% complete) - Core methods available for static `congruenceAsAlgebra()` methods

**READY DEPENDENCIES** (Available for use):
- `SmallAlgebra` (Task 41) - ✅ **COMPLETED** - Core interface implemented
- `GeneralAlgebra` (Task 66) - ✅ **COMPLETED** - Parent class implemented
- `Partition` (Task 5) - ✅ **COMPLETED** - Partition operations available
- `Operation` (Task 12) - ✅ **COMPLETED** - Operation interface implemented
- `Operations` (Task 50) - ✅ **COMPLETED** - Operation utilities available
- `IntArray` (Task 23) - ✅ **COMPLETED** - Array wrapper available
- `Horner` (Task 3) - ✅ **COMPLETED** - Horner encoding available

### Implementation Blockers
1. **CongruenceLattice** - Required for lazy initialization of congruence lattice
2. **SubalgebraLattice** - Required for lazy initialization of subalgebra lattice
3. **ProductAlgebra** - Required for static methods that create congruence as algebra

### Current Code Status
- **Rust Implementation**: Full struct implementation in `src/alg/subalgebra.rs`
  - Main Subalgebra struct with all core fields
  - RestrictedOperation struct for operation delegation
  - Complete SmallAlgebra trait implementation
  - All non-lattice methods implemented
- **Python Bindings**: PySubalgebra wrapper with all core methods
- **Java Wrapper**: SubalgebraWrapper with comprehensive CLI interface
- **Module Integration**: Properly integrated into `src/alg/mod.rs`

### Recommendations
1. ✅ **PARTIALLY COMPLETED** - Core functionality implemented without lattice dependencies
2. **Remaining Work**: Add lattice methods once CongruenceLattice and SubalgebraLattice are available
3. **Future Enhancement**: Implement congruenceAsAlgebra static methods once ProductAlgebra is available
4. **Testing**: Add comprehensive unit tests for all implemented methods

### Acceptance Criteria
- [x] Core public methods translated to Rust (18 of 26 - lattice methods excluded)
- [x] Python bindings expose all core methods  
- [x] Java CLI wrapper created with core commands
- [x] Code compiles successfully (with minor warnings)
- [ ] Rust tests pass with timeouts enabled - **Tests not yet written**
- [ ] Python tests pass and match Java output - **Tests not yet written**
- [x] Code compiles without errors
- [x] Documentation complete for implemented methods
- [ ] Lattice methods (con, sub) - **DEFERRED** pending dependencies
- [ ] Static congruenceAsAlgebra methods - **DEFERRED** pending ProductAlgebra

### Implemented Methods (18 of 26)
- ✅ Constructors (4): new, new_safe, from name+algebra+universe
- ✅ index - Find element in subalgebra
- ✅ restrict_partition - Restrict partition to subalgebra
- ✅ super_algebra - Get super algebra reference
- ✅ get_subuniverse_array - Get subuniverse indices
- ✅ element_index - Get index of element
- ✅ get_element - Get element by index
- ✅ cardinality - Get size
- ✅ algebra_type - Return AlgebraType::Subalgebra
- ✅ make_operation_tables - Build operation tables
- ✅ All SmallAlgebra trait methods
- ✅ All Algebra trait methods

### Deferred Methods (8 of 26)
- ❌ con() - Requires CongruenceLattice (Task 80)
- ❌ sub() - Requires SubalgebraLattice (Task 76)
- ⚠️ congruenceAsAlgebra (static, 2 variants) - Can now be implemented (ProductAlgebra available)
- ❌ get_universe_list - Returns None (can be implemented later)
- ❌ get_universe_order - Returns None (can be implemented later)
- ❌ convert_to_default_value_ops - Panics (only for basic algebras)
- ❌ main test method - Not applicable to Rust

### Next Steps
1. Add unit tests for all implemented methods
2. Add integration tests for subalgebra creation and operations
3. Implement lattice methods once dependencies are available
4. Implement congruenceAsAlgebra once ProductAlgebra is available
