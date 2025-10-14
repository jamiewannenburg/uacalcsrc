# Task 36: Translate `PartiallyDefinedLattice`

**Java File:** `org/uacalc/fplat/PartiallyDefinedLattice.java`  
**Package:** `org.uacalc.fplat`  
**Rust Module:** `fplat::PartiallyDefinedLattice`  
**Dependencies:** 2 (2 non-UI/example)  
**Estimated Public Methods:** 2

## Java File Analysis

### Class Structure
- **Type**: Concrete class implementing `Order<Variable>`
- **Package**: `org.uacalc.fplat`
- **Implements**: `Order<Variable>` interface
- **Fields**:
  - `Order<Variable> order` - The underlying order relation
  - `List<List<Variable>> definedJoins` - List of defined join operations
  - `List<List<Variable>> definedMeets` - List of defined meet operations

### Public Methods
1. `PartiallyDefinedLattice(String name, Order<Variable> order, List<List<Variable>> joins, List<List<Variable>> meets)` - Constructor
2. `boolean leq(Variable a, Variable b)` - Implements Order interface method

### Dependencies Analysis
**Correctly Identified Dependencies:**
- `org.uacalc.lat.Order` - Interface implemented by this class
- `org.uacalc.terms` - Package containing Variable interface and related classes

**Dependency Verification:**
- ✅ `Order<Variable>` - Used as field type and interface implementation
- ✅ `Variable` - Used as generic parameter and method parameters
- ✅ `List<List<Variable>>` - Used for joins and meets storage

## Rust Implementation Recommendations

### Design Decisions
- **Rust Construct**: `struct` (concrete class)
- **Trait Implementation**: Implement `Order<Variable>` trait
- **Generic Parameters**: Use `Variable` as the element type
- **Field Types**: 
  - `order: Box<dyn Order<Variable>>` - Trait object for order relation
  - `defined_joins: Vec<Vec<Variable>>` - Vector of join operations
  - `defined_meets: Vec<Vec<Variable>>` - Vector of meet operations

### Implementation Structure
```rust
pub struct PartiallyDefinedLattice {
    order: Box<dyn Order<Variable>>,
    defined_joins: Vec<Vec<Variable>>,
    defined_meets: Vec<Vec<Variable>>,
}

impl Order<Variable> for PartiallyDefinedLattice {
    fn leq(&self, a: &Variable, b: &Variable) -> bool {
        self.order.leq(a, b)
    }
}
```

### Method Organization
- **Constructor**: `new(name: String, order: Box<dyn Order<Variable>>, joins: Vec<Vec<Variable>>, meets: Vec<Vec<Variable>>) -> Self`
- **Trait Method**: `leq(&self, a: &Variable, b: &Variable) -> bool`
- **Accessor Methods**: 
  - `get_defined_joins(&self) -> &Vec<Vec<Variable>>`
  - `get_defined_meets(&self) -> &Vec<Vec<Variable>>`

### Error Handling
- Use `Result<Self, String>` for constructor validation
- Validate that joins and meets lists are not empty
- Validate that all variables in joins/meets are consistent

## Java Wrapper Suitability

### Assessment
- **Suitable**: YES - Concrete class with public methods
- **Testing Strategy**: Direct instantiation and method testing
- **Wrapper Methods**:
  - `create` - Test constructor with various parameters
  - `leq` - Test order relation with different variable pairs
  - `get_joins` - Test accessor for defined joins
  - `get_meets` - Test accessor for defined meets

### Java Wrapper Implementation
```java
public class PartiallyDefinedLatticeWrapper extends WrapperBase {
    // Test constructor with different order types
    // Test leq method with various variable combinations
    // Test accessor methods for joins and meets
}
```

## Python Bindings Strategy

### PyO3 Implementation
- **Class Name**: `PartiallyDefinedLattice` (clean export)
- **Internal Name**: `PyPartiallyDefinedLattice`
- **Methods**: Expose all public methods with proper error handling
- **Trait Objects**: Use `PyObject` for order parameter to handle trait objects

### Python API
```python
# Create with custom order
lattice = PartiallyDefinedLattice("test", order, joins, meets)

# Test order relation
result = lattice.leq(var1, var2)

# Access defined operations
joins = lattice.get_defined_joins()
meets = lattice.get_defined_meets()
```

## Testing Strategy

### Rust Tests
- **Unit Tests**: Test constructor validation and method behavior
- **Integration Tests**: Test with different Order implementations
- **Edge Cases**: Empty joins/meets, null parameters, invalid variables
- **Java Comparison**: Use `compare_with_java!` macro for exact behavior matching

### Python Tests
- **Method Tests**: Test all exposed methods through Python bindings
- **Error Handling**: Test validation errors and proper exception handling
- **Java Comparison**: Compare results with Java wrapper output

### Test Cases
1. **Constructor Tests**:
   - Valid parameters
   - Empty joins/meets lists
   - Invalid order parameter
   - Duplicate variable names

2. **leq Method Tests**:
   - Variables in order
   - Variables not in order
   - Same variable comparison
   - Variables from different sources

3. **Accessor Tests**:
   - Get defined joins
   - Get defined meets
   - Verify immutability

## Critical Implementation Notes

### Dependency Requirements
- **Order Trait**: Must be implemented before this class
- **Variable Struct**: Must be implemented before this class
- **Trait Objects**: Use `Box<dyn Order<Variable>>` for dynamic dispatch

### Integration Points
- **OrderedSets.maximals()**: This class will be used as Order parameter
- **Lattice Operations**: May be used in lattice construction algorithms
- **Term Evaluation**: Variables may be used in term evaluation contexts

### Memory Management
- **Trait Objects**: Use `Box<dyn Order<Variable>>` to avoid lifetime issues
- **Vector Storage**: Use `Vec<Vec<Variable>>` for efficient storage
- **Clone Requirements**: Implement `Clone` for Variable if needed

## Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Order trait dependency implemented
- [ ] Variable struct dependency implemented
- [ ] Trait object handling works correctly
