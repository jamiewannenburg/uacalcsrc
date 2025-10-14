# Task 70: Translate `PermutationGroup`

**Java File:** `org/uacalc/group/PermutationGroup.java`  
**Package:** `org.uacalc.group`  
**Rust Module:** `group::PermutationGroup`  
**Dependencies:** 7 (7 non-UI/example)  
**Estimated Public Methods:** 11

## Description
Translate the Java class `org.uacalc.group.PermutationGroup` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Java Type**: Concrete class extending `GeneralAlgebra`
- **Inheritance**: Extends `GeneralAlgebra` (which implements `Algebra` interface)
- **Usage**: Represents a group of permutations on the set {0, ..., n-1}

### Java Class Structure
- **Type**: Concrete class with static factory methods
- **Purpose**: Permutation group operations with static utility methods
- **Key Features**: Static methods for creating operations (product, inverse, identity)
- **Public Methods**: 11 methods (2 constructors + 9 static methods)

### Public Methods (11 total)
1. `PermutationGroup(String name, List generators)` - Constructor
2. `PermutationGroup(String name, List generators, List universeList)` - Constructor
3. `makeProdOp(int algSize)` - Static factory for product operation
4. `prod(IntArray p0, IntArray p1)` - Static product of two permutations
5. `makeInvOp(int algSize)` - Static factory for inverse operation
6. `inv(IntArray a)` - Static inverse of a permutation
7. `makeIdOp(int algSize, int setSize)` - Static factory for identity operation
8. `id(int setSize)` - Static identity permutation

### Dependencies Analysis
**Correctly Identified:**
- `org.uacalc.alg` - GeneralAlgebra base class
- `org.uacalc.alg.conlat` - Congruence lattice (imported but not used)
- `org.uacalc.alg.op.AbstractOperation` - For creating operations
- `org.uacalc.alg.op.Operation` - Operation interface
- `org.uacalc.alg.op.OperationSymbol` - Operation symbol constants
- `org.uacalc.alg.sublat` - Subalgebra lattice (imported but not used)
- `org.uacalc.util` - IntArray utility class

**Dependencies are accurate** - All listed dependencies are correctly identified from imports.

## Rust Implementation Recommendations

### Struct Design
```rust
pub struct PermutationGroup {
    pub name: String,
    pub generators: Vec<IntArray>,
    pub universe_list: Option<Vec<IntArray>>,
    pub underlying_set_size: usize,
    pub identity: Option<IntArray>,
}
```

### Key Design Decisions
1. **Inheritance**: Since PermutationGroup extends GeneralAlgebra, it should contain a GeneralAlgebra instance or implement the same traits
2. **Static Methods**: Convert to associated functions (no `self` parameter)
3. **IntArray Usage**: Use the existing IntArray implementation from util module
4. **Operation Creation**: Use trait objects for operations to allow different operation types
5. **Error Handling**: Use `Result<T, String>` for methods that can fail

### Method Organization
- **Constructor Methods**: `new()`, `new_with_universe()`
- **Static Factory Methods**: `make_prod_op()`, `make_inv_op()`, `make_id_op()`
- **Static Utility Methods**: `prod()`, `inv()`, `id()`
- **Instance Methods**: Inherited from GeneralAlgebra

### Dependencies Required
1. **GeneralAlgebra**: Base class functionality
2. **IntArray**: From util module (already implemented)
3. **Operation System**: AbstractOperation, Operation, OperationSymbol (need implementation)
4. **Unused Dependencies**: conlat and sublat packages are imported but not used

## Python Bindings Strategy

### Class Design
```rust
#[pyclass]
pub struct PyPermutationGroup {
    inner: PermutationGroup,
}
```

### Key Points
- Expose all public methods through Python bindings
- Use `PyResult<T>` for error handling
- Implement Python magic methods (`__str__`, `__repr__`, `__eq__`)
- Static methods should be exposed as class methods

## Java Wrapper Suitability

### Assessment: **SUITABLE**
- **Reason**: PermutationGroup is a concrete class with public methods
- **Testing Strategy**: Create wrapper with methods to test all public functionality
- **Key Test Cases**:
  - Constructor with different parameters
  - Static factory methods (makeProdOp, makeInvOp, makeIdOp)
  - Static utility methods (prod, inv, id)
  - Permutation operations and validation

## Testing Strategy

### Rust Tests
- Unit tests for all public methods
- Integration tests with different permutation sizes
- Error handling tests for invalid inputs
- Performance tests for large permutations

### Python Tests
- Test all methods through Python bindings
- Compare results with Java wrapper output
- Test error conditions and edge cases

### Java Wrapper Tests
- Test constructor variations
- Test static factory methods
- Test permutation operations
- Test edge cases (empty permutations, single elements)

## Implementation Priority

### Phase 1: Core Structure
1. Implement `PermutationGroup` struct
2. Implement constructor methods
3. Implement static utility methods (prod, inv, id)

### Phase 2: Operation Factories
1. Implement static factory methods
2. Integrate with Operation system
3. Test operation creation

### Phase 3: Integration
1. Create Python bindings
2. Create Java wrapper
3. Implement comprehensive tests

## Critical Implementation Notes

1. **GeneralAlgebra Integration**: PermutationGroup extends GeneralAlgebra, so it needs to either contain a GeneralAlgebra instance or implement the same traits.

2. **Static Methods**: The Java class has many static methods that should become associated functions in Rust.

3. **IntArray Dependency**: Uses IntArray from util module, which is already implemented.

4. **Operation System**: Needs integration with the Operation system (AbstractOperation, Operation, OperationSymbol).

5. **Unused Imports**: The conlat and sublat imports are not used in the current implementation.

## Acceptance Criteria
- [ ] All 11 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] GeneralAlgebra integration properly handled
- [ ] Static methods converted to associated functions
- [ ] IntArray integration working correctly
