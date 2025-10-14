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
- `org.uacalc.alg.SmallAlgebra` (Task 41 - NOT COMPLETED) - Interface implementation
- `org.uacalc.alg.SmallAlgebra.AlgebraType` (Task 41 - NOT COMPLETED) - Enum type
- `org.uacalc.alg.GeneralAlgebra` (Task 66 - NOT COMPLETED) - Parent class
- `org.uacalc.alg.conlat.Partition` (Task 5 - COMPLETED) - Partition operations
- `org.uacalc.alg.conlat.BasicPartition` (Task 5 - COMPLETED) - Partition creation
- `org.uacalc.alg.conlat.CongruenceLattice` (Task 20 - NOT COMPLETED) - Lattice operations
- `org.uacalc.alg.sublat.SubalgebraLattice` (Task 76 - NOT COMPLETED) - Lattice operations
- `org.uacalc.alg.op.AbstractOperation` (Task 12 - NOT COMPLETED) - Operation creation
- `org.uacalc.alg.op.Operation` (Task 12 - NOT COMPLETED) - Operation interface
- `org.uacalc.alg.op.Operations` (Task 50 - NOT COMPLETED) - Operation utilities
- `org.uacalc.alg.ProductAlgebra` (Task 57 - NOT COMPLETED) - Used in static methods
- `org.uacalc.util.IntArray` (Task 23 - COMPLETED) - Array wrapper
- `org.uacalc.util.Horner` (Task 3 - COMPLETED) - Horner encoding
- `java.util.*` - Standard Java collections

**Dependency Status**: ❌ **BLOCKED** - 8 out of 13 dependencies are NOT COMPLETED

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
3. **CongruenceLattice** (Task 20) - Lattice operations
4. **SubalgebraLattice** (Task 76) - Lattice operations
5. **Operation/AbstractOperation** (Task 12) - Operation system
6. **Operations** (Task 50) - Operation utilities
7. **ProductAlgebra** (Task 57) - Used in static methods

### Acceptance Criteria
- [ ] All 26 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] **All dependencies completed before implementation**
