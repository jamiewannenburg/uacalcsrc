# Task 24: Translate `AlgebraFromMinimalSets`

**Java File:** `org/uacalc/alg/AlgebraFromMinimalSets.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::AlgebraFromMinimalSets`  
**Dependencies:** 4 (4 non-UI/example)  
**Estimated Public Methods:** 6

## Description
Translate the Java class `org.uacalc.alg.AlgebraFromMinimalSets` to Rust with Python bindings.

## Java File Analysis

### Class Structure
- **Type**: Concrete class extending `BasicAlgebra` and implementing `SmallAlgebra`
- **Public Methods**: 5 constructors + 1 static main method
- **Key Fields**: 
  - `SmallAlgebra minimalAlgebra` - the base minimal algebra
  - `int minAlgSize` - size of minimal algebra
  - `List<Integer> connectingPts` - connecting points
  - `int a, b` - connection indices
  - `List<int[]> maps` - mapping arrays
  - `int[] mapToB` - mapping from algebra to minimal algebra

### Dependencies Analysis
**Corrected Dependencies** (original list was incomplete):
- `org.uacalc.alg.op.Operation` - Operation interface
- `org.uacalc.alg.op.Operations` - Operations factory class
- `org.uacalc.alg.op.AbstractOperation` - Abstract operation implementation
- `org.uacalc.alg.op.OperationSymbol` - Operation symbol class
- `org.uacalc.alg.BasicAlgebra` - Parent class
- `org.uacalc.alg.SmallAlgebra` - Interface implemented
- `org.uacalc.alg.GeneralAlgebra` - Grandparent class
- `org.uacalc.alg.Algebra` - Great-grandparent interface

**Missing Dependencies** (not listed in original task):
- `org.uacalc.alg.BasicAlgebra` - Critical parent class dependency
- `org.uacalc.alg.SmallAlgebra` - Critical interface dependency
- `org.uacalc.alg.GeneralAlgebra` - Critical grandparent class dependency
- `org.uacalc.alg.Algebra` - Critical great-grandparent interface dependency

## Rust Implementation Recommendations

### Design Decisions
- **Rust Construct**: `struct` (concrete class)
- **Trait Implementation**: Implement `SmallAlgebra` trait
- **Inheritance**: Use composition instead of inheritance (Rust doesn't have inheritance)
- **Error Handling**: Use `Result<T, String>` for operations that can fail
- **Null Safety**: Use `Option<T>` instead of nullable references

### Struct Design
```rust
pub struct AlgebraFromMinimalSets {
    pub minimal_algebra: Box<dyn SmallAlgebra>,
    pub min_alg_size: usize,
    pub connecting_pts: Option<Vec<i32>>,
    pub a: usize,
    pub b: usize,
    pub maps: Vec<Vec<i32>>,
    pub map_to_b: Vec<i32>,
    // Inherited from BasicAlgebra/GeneralAlgebra
    pub name: Option<String>,
    pub size: usize,
    pub operations: Vec<Box<dyn Operation>>,
}
```

### Method Organization
- **Constructors**: Multiple `new` methods with different parameter combinations
- **Private Methods**: `make_default_maps()`, `make_map_to_b()`, `make_ops()`
- **Trait Methods**: Implement `SmallAlgebra` trait methods
- **Error Handling**: Provide both `_safe` and `_panic` versions of methods

### Generic vs Dynamic Dispatch
- **Dynamic Dispatch**: Use `Box<dyn SmallAlgebra>` for minimal algebra (polymorphic)
- **Dynamic Dispatch**: Use `Box<dyn Operation>` for operations (polymorphic)
- **Reasoning**: The Java code uses interface types, so dynamic dispatch is appropriate

## Java Wrapper Suitability
- **Suitable**: Yes - concrete class with public constructors and methods
- **Testing Strategy**: Create wrapper with all constructor variants and main method
- **CLI Commands**: 
  - `construct` - test all constructor variants
  - `test` - run basic functionality tests
  - `main` - test the static main method

## Implementation Priority
- **Priority**: Medium (depends on 4 other classes)
- **Blocking Dependencies**: Must implement `BasicAlgebra`, `SmallAlgebra`, `GeneralAlgebra`, `Algebra` first
- **Operation Dependencies**: Must implement `Operation`, `Operations`, `AbstractOperation`, `OperationSymbol` first

## Testing Strategy
- **Unit Tests**: Test all constructor variants and private methods
- **Integration Tests**: Test with different minimal algebra inputs
- **Error Tests**: Test invalid map configurations and inconsistent maps
- **Performance Tests**: Test with various algebra sizes
- **Cross-Language Tests**: Compare results with Java wrapper

## Critical Implementation Notes
1. **Map Validation**: The `makeMapToB()` method validates map consistency - implement proper error handling
2. **Default Maps**: The `makeDefaultMaps()` method creates 3 default maps (B, C, D) - ensure exact behavior match
3. **Operation Creation**: Operations are created dynamically based on minimal algebra operations - use trait objects
4. **Size Calculation**: Default size is `3 * minAlgSize - 2` - ensure exact calculation
5. **Connection Points**: Optional connecting points affect the `a` and `b` values - handle `None` case properly

## Acceptance Criteria
- [ ] All 5 public constructors translated to Rust
- [ ] Static main method translated to Rust
- [ ] All private methods (`makeDefaultMaps`, `makeMapToB`, `makeOps`) implemented
- [ ] `SmallAlgebra` trait properly implemented
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all constructor variants
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] **Dependencies correctly listed and implemented first**
