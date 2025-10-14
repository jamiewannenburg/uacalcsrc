# Task 66: Translate `GeneralAlgebra`

**Java File:** `org/uacalc/alg/GeneralAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::GeneralAlgebra`  
**Dependencies:** 5 (4 non-UI/example)  
**Estimated Public Methods:** ~25

## Description
Translate the Java class `org.uacalc.alg.GeneralAlgebra` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Java Type**: Concrete class implementing `Algebra` interface
- **Inheritance**: Implements `Algebra` interface
- **Usage**: Base class for all algebra implementations (BasicAlgebra, ProductAlgebra, etc.)

### Dependencies
This class depends on:
- `org.uacalc.alg.op.Operation` - Operation interface
- `org.uacalc.alg.op.OperationSymbol` - Operation symbol type
- `org.uacalc.alg.op.Operations` - Operations utility class
- `org.uacalc.alg.op.SimilarityType` - Similarity type for algebras
- `org.uacalc.alg.conlat.CongruenceLattice` - Congruence lattice (field only)
- `org.uacalc.alg.sublat.SubalgebraLattice` - Subalgebra lattice (field only)
- `org.uacalc.ui.tm.ProgressReport` - Progress reporting (excluded - UI package)

### Key Fields
- `List<Operation> operations` - List of operations
- `Map<OperationSymbol,Operation> operationsMap` - Map of operations by symbol
- `SimilarityType similarityType` - Similarity type of the algebra
- `Set universe` - Universe of the algebra
- `CongruenceLattice con` - Congruence lattice (protected, unused in base)
- `SubalgebraLattice sub` - Subalgebra lattice (protected, unused in base)
- `String name` - Name of the algebra
- `String description` - Description of the algebra
- `int size` - Size of the universe

### Public Methods (25 total)
1. `GeneralAlgebra(String name, Set univ)` - Constructor
2. `GeneralAlgebra(String name, Set univ, List<Operation> operations)` - Constructor
3. `setMonitor(ProgressReport m)` - Set progress monitor
4. `getMonitor()` - Get progress monitor
5. `monitoring()` - Check if monitoring is enabled
6. `isTotal()` - Check if all operations are total
7. `getOperationsMap()` - Get operations map
8. `operations()` - Get operations list
9. `getOperation(OperationSymbol sym)` - Get operation by symbol
10. `isUnary()` - Check if all operations are unary
11. `constantOperations()` - Get constant operations (arity 0)
12. `similarityType()` - Get similarity type
13. `updateSimilarityType()` - Update similarity type
14. `getName()` - Get algebra name
15. `setName(String v)` - Set algebra name
16. `getDescription()` - Get description
17. `setDescription(String desc)` - Set description
18. `isSimilarTo(Algebra alg2)` - Check if similar to another algebra
19. `iterator()` - Get universe iterator
20. `cardinality()` - Get cardinality
21. `inputSize()` - Get input size
22. `universe()` - Get universe set
23. `con()` - Get congruence lattice (throws UnsupportedOperationException)
24. `sub()` - Get subalgebra lattice (throws UnsupportedOperationException)
25. `resetConAndSub()` - Reset congruence and subalgebra lattices
26. `makeOperationTables()` - Make operation tables
27. `parent()` - Get parent algebra (returns null)
28. `parents()` - Get parent algebras list
29. `isIdempotent()` - Check if all operations are idempotent

## Rust Implementation Recommendations

### Struct Design
```rust
pub struct GeneralAlgebra {
    pub operations: Vec<Box<dyn Operation>>,
    pub operations_map: HashMap<OperationSymbol, Box<dyn Operation>>,
    pub similarity_type: Option<SimilarityType>,
    pub universe: HashSet<Element>,
    pub con: Option<Box<dyn CongruenceLattice>>,
    pub sub: Option<Box<dyn SubalgebraLattice>>,
    pub name: String,
    pub description: Option<String>,
    pub size: usize,
    pub monitor: Option<Box<dyn ProgressReport>>,
}
```

### Key Design Decisions
1. **Trait Objects**: Use `Box<dyn Operation>` for operations to allow different operation types
2. **Generic Universe**: Use `HashSet<Element>` where `Element` is a generic type
3. **Optional Fields**: Use `Option<T>` for fields that may be null in Java
4. **Error Handling**: Use `Result<T, String>` for methods that can fail
5. **Progress Reporting**: Create a trait for progress reporting (exclude UI dependency)

### Method Organization
- **Constructor Methods**: `new()`, `new_with_operations()`
- **Getter/Setter Methods**: Standard getters and setters
- **Validation Methods**: `is_total()`, `is_unary()`, `is_idempotent()`
- **Operation Methods**: `get_operation()`, `operations()`, `constant_operations()`
- **Algebra Methods**: `similarity_type()`, `is_similar_to()`, `cardinality()`
- **Lattice Methods**: `con()`, `sub()` (return errors instead of throwing)

### Dependencies Required
1. **Operation Module**: `Operation`, `OperationSymbol`, `Operations`, `SimilarityType`
2. **Conlat Module**: `CongruenceLattice` (trait)
3. **Sublat Module**: `SubalgebraLattice` (trait)
4. **Progress Module**: `ProgressReport` (trait, exclude UI dependency)

## Python Bindings Strategy

### Class Design
```rust
#[pyclass]
pub struct PyGeneralAlgebra {
    inner: GeneralAlgebra,
}
```

### Key Points
- Expose all public methods through Python bindings
- Use `PyResult<T>` for error handling
- Implement Python magic methods (`__str__`, `__repr__`, `__eq__`)
- Handle generic types appropriately for Python

## Java Wrapper Suitability

### Assessment: **SUITABLE**
- **Reason**: GeneralAlgebra is a concrete class with many public methods
- **Testing Strategy**: Create wrapper with methods to test all public functionality
- **Key Test Cases**:
  - Constructor with different parameters
  - Operation management (add, get, list operations)
  - Similarity type operations
  - Algebra properties (is_total, is_unary, is_idempotent)
  - Universe operations (cardinality, iterator)

## Testing Strategy

### Rust Tests
- Unit tests for all public methods
- Integration tests with different operation types
- Error handling tests for invalid inputs
- Performance tests for large algebras

### Python Tests
- Test all methods through Python bindings
- Compare results with Java wrapper output
- Test error conditions and edge cases

### Java Wrapper Tests
- Test constructor variations
- Test operation management
- Test algebra properties
- Test similarity operations

## Implementation Priority

### Phase 1: Core Structure
1. Implement `GeneralAlgebra` struct
2. Implement basic constructor methods
3. Implement getter/setter methods

### Phase 2: Operation Management
1. Implement operation-related methods
2. Implement similarity type methods
3. Implement algebra property methods

### Phase 3: Advanced Features
1. Implement lattice methods (with proper error handling)
2. Implement universe operations
3. Implement progress reporting

### Phase 4: Integration
1. Create Python bindings
2. Create Java wrapper
3. Implement comprehensive tests

## Critical Implementation Notes

1. **ProgressReport Dependency**: The Java class imports `ProgressReport` from UI package, but this should be excluded. Create a trait for progress reporting instead.

2. **Lattice Methods**: The `con()` and `sub()` methods throw `UnsupportedOperationException` in the base class. In Rust, return `Result<Box<dyn CongruenceLattice>, String>` with appropriate error messages.

3. **Generic Universe**: The universe is a `Set` in Java, but should be generic in Rust to handle different element types.

4. **Operation Storage**: Use trait objects for operations to allow different operation types while maintaining type safety.

5. **Memory Management**: Use `Box<dyn Trait>` for trait objects to avoid lifetime issues.

## Acceptance Criteria
- [ ] All 25+ public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Progress reporting trait implemented (excluding UI dependency)
- [ ] Lattice methods return proper errors instead of panicking
- [ ] Generic universe type properly handled
