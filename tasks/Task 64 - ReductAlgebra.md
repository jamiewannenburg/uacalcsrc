# Task 64: Translate `ReductAlgebra`

**Java File:** `org/uacalc/alg/ReductAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::ReductAlgebra`  
**Dependencies:** 8 (8 non-UI/example)  
**Estimated Public Methods:** 12

### Description
Translate the Java class `org.uacalc.alg.ReductAlgebra` to Rust with Python bindings.

### Java Class Analysis
- **Type**: Concrete class extending `GeneralAlgebra` and implementing `SmallAlgebra`
- **Purpose**: Represents a reduct of a `SmallAlgebra` to a list of `Term`s
- **Key Features**: 
  - Creates operations from terms by interpreting them in the super algebra
  - Delegates universe and element access to the super algebra
  - Provides static methods for creating congruence algebras
  - Implements lazy initialization of congruence and subalgebra lattices

### Dependencies (Verified)
This class depends on:
- `org.uacalc.alg.SmallAlgebra` (interface) - **REQUIRED**
- `org.uacalc.alg.SmallAlgebra.AlgebraType` (enum) - **REQUIRED**
- `org.uacalc.alg.GeneralAlgebra` (parent class) - **REQUIRED**
- `org.uacalc.alg.conlat.CongruenceLattice` - **REQUIRED**
- `org.uacalc.alg.sublat.SubalgebraLattice` - **REQUIRED**
- `org.uacalc.alg.op.Operation` - **REQUIRED**
- `org.uacalc.terms.Term` - **REQUIRED**
- `org.uacalc.util.Horner` - **REQUIRED** (for static methods)
- `org.uacalc.alg.Subalgebra` - **REQUIRED** (for static methods)
- `org.uacalc.alg.ProductAlgebra` - **REQUIRED** (for static methods)

### Rust Implementation Design

#### Struct Design
```rust
pub struct ReductAlgebra {
    // Core fields
    pub super_algebra: Box<dyn SmallAlgebra>,
    pub term_list: Vec<Term>,
    
    // Inherited from GeneralAlgebra
    pub name: String,
    pub size: usize,
    pub universe: HashSet<Element>,
    pub operations: Vec<Operation>,
    
    // Lazy-initialized fields
    pub con: Option<CongruenceLattice>,
    pub sub: Option<SubalgebraLattice>,
}
```

#### Trait Implementation
- **SmallAlgebra trait**: Implement all required methods
- **Algebra trait**: Inherit from GeneralAlgebra implementation
- **Display trait**: For string representation
- **Debug trait**: For debugging

#### Method Organization
- **Constructor methods**: `new()`, `new_with_name()`
- **Instance methods**: Delegate to super algebra or implement directly
- **Static methods**: `congruence_as_algebra()` variants
- **Lazy initialization**: `con()`, `sub()` methods

#### Key Implementation Decisions
1. **Ownership**: Use `Box<dyn SmallAlgebra>` for super algebra to handle trait objects
2. **Error Handling**: Use `Result<T, String>` for operations that can fail
3. **Lazy Initialization**: Use `Option<T>` for con/sub lattices with lazy getters
4. **Static Methods**: Implement as associated functions
5. **Term Processing**: Filter out variables and interpret non-variable terms

### Java Wrapper Suitability
**SUITABLE** - This is a concrete class with:
- Clear constructor parameters (SmallAlgebra, List<Term>)
- Well-defined public methods
- Static utility methods
- No complex internal state dependencies

### Testing Strategy
1. **Constructor Tests**: Test both constructors with various inputs
2. **Delegation Tests**: Verify super algebra method delegation
3. **Lazy Initialization Tests**: Test con() and sub() lazy creation
4. **Static Method Tests**: Test congruence_as_algebra methods
5. **Edge Cases**: Empty term lists, null inputs, error conditions
6. **Cross-language Tests**: Compare Rust/Python/Java outputs

### Public Methods to Implement
1. **Constructors**:
   - `new(super_algebra: Box<dyn SmallAlgebra>, term_list: Vec<Term>) -> Self`
   - `new_with_name(name: String, super_algebra: Box<dyn SmallAlgebra>, term_list: Vec<Term>) -> Self`

2. **Instance Methods**:
   - `make_operation_tables(&mut self) -> ()`
   - `super_algebra(&self) -> &dyn SmallAlgebra`
   - `con(&mut self) -> &CongruenceLattice` (lazy initialization)
   - `sub(&mut self) -> &SubalgebraLattice` (lazy initialization)
   - `element_index(&self, obj: &Element) -> i32`
   - `get_element(&self, index: usize) -> Element`
   - `get_universe_list(&self) -> Option<Vec<Element>>`
   - `get_universe_order(&self) -> Option<HashMap<Element, usize>>`
   - `convert_to_default_value_ops(&mut self) -> Result<(), String>`
   - `algebra_type(&self) -> AlgebraType`

3. **Static Methods**:
   - `congruence_as_algebra(alg: Box<dyn SmallAlgebra>, cong: Partition) -> Box<dyn SmallAlgebra>`
   - `congruence_as_algebra_with_name(name: String, alg: Box<dyn SmallAlgebra>, cong: Partition) -> Box<dyn SmallAlgebra>`

### Implementation Recommendations

#### 1. Dependency Management
- Ensure all 10 dependencies are translated before this class
- Pay special attention to `SmallAlgebra` trait and `GeneralAlgebra` base class
- Verify `Term` interpretation methods are available

#### 2. Memory Management
- Use `Box<dyn SmallAlgebra>` for trait object storage
- Implement proper cloning for `Term` objects
- Handle large term lists efficiently

#### 3. Error Handling
- Use `Result<T, String>` for operations that can fail
- Implement proper validation for term lists
- Handle edge cases in static methods

#### 4. Performance Considerations
- Lazy initialization of con/sub lattices
- Efficient term filtering and interpretation
- Minimize allocations in hot paths

### Current Implementation Status

**Overall Status: NOT STARTED (0% complete)**

#### Component Status:
- **Rust Implementation**: ❌ NOT IMPLEMENTED (0%)
  - Only placeholder struct exists in `src/alg/mod.rs`
  - No actual implementation of methods or functionality
  
- **Python Bindings**: ❌ NOT IMPLEMENTED (0%)
  - No Python bindings found in `uacalc_lib/src/`
  
- **Java Wrapper**: ❌ NOT IMPLEMENTED (0%)
  - No Java wrapper found in `java_wrapper/src/`
  
- **Tests**: ❌ NOT IMPLEMENTED (0%)
  - No tests found for ReductAlgebra

#### Dependency Analysis:
**Ready Dependencies (6/10):**
- ✅ `SmallAlgebra` trait - Fully implemented
- ✅ `GeneralAlgebra` - Fully implemented
- ✅ `Term` trait and implementations - Fully implemented
- ✅ `Operation` trait - Fully implemented
- ✅ `Partition` - Fully implemented
- ✅ `Horner` utilities - Fully implemented

**Blocking Dependencies (4/10):**
- ❌ `CongruenceLattice` - Only placeholder exists
- ❌ `SubalgebraLattice` - Only placeholder exists
- ❌ `Subalgebra` - Only placeholder exists
- ❌ `ProductAlgebra` - Only placeholder exists

#### Implementation Blockers:
1. **Missing CongruenceLattice**: Required for `con()` method
2. **Missing SubalgebraLattice**: Required for `sub()` method
3. **Missing Subalgebra**: Required for static `congruence_as_algebra()` methods
4. **Missing ProductAlgebra**: Required for static `congruence_as_algebra()` methods

### Acceptance Criteria
- [ ] All 12 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] All dependencies correctly identified and available

### Next Steps
1. **Implement blocking dependencies first**:
   - Implement `CongruenceLattice` (Task 2)
   - Implement `SubalgebraLattice` (Task 3) 
   - Implement `Subalgebra` (Task 4)
   - Implement `ProductAlgebra` (Task 5)

2. **Once dependencies are ready**:
   - Implement `ReductAlgebra` struct and methods
   - Add Python bindings
   - Create Java wrapper
   - Write comprehensive tests
