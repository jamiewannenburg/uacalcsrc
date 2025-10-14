# Task 41: Translate `SmallAlgebra`

**Java File:** `org/uacalc/alg/SmallAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::SmallAlgebra`  
**Dependencies:** 2 (2 non-UI/example)  
**Estimated Public Methods:** ~12

## Analysis Summary

### Java Class Analysis
- **Type**: Interface extending `Algebra`
- **Purpose**: Defines contract for small algebras with universe indexed by {0,...,n-1}
- **Key Methods**: 12 public methods including element access, lattice operations, and algebra type identification
- **Special Patterns**: Uses enum for `AlgebraType`, extends parent `Algebra` interface

### Dependency Analysis
**Current Dependencies Listed:**
- `org.uacalc.alg.conlat.CongruenceLattice` ✅ (Task 80 - not completed)
- `org.uacalc.alg.sublat.SubalgebraLattice` ✅ (Task 76 - not completed)

**Additional Dependencies Found:**
- `org.uacalc.alg.Algebra` (parent interface) - **MISSING from dependencies**
- `java.util.List` (for universe and parents)
- `java.util.Map` (for universe order)
- `java.util.Iterator` (from parent Algebra)

**Dependency Status**: ❌ **BLOCKED** - Both CongruenceLattice and SubalgebraLattice are not completed yet

### Rust Implementation Recommendations

#### 1. Trait Design
```rust
/// SmallAlgebra trait - equivalent to Java interface
pub trait SmallAlgebra: Algebra {
    /// Algebra type enumeration
    fn algebra_type(&self) -> AlgebraType;
    
    /// Get element by index
    fn get_element(&self, k: usize) -> Option<Element>;
    
    /// Get element index
    fn element_index(&self, elem: &Element) -> Option<usize>;
    
    /// Get universe as list
    fn get_universe_list(&self) -> Option<Vec<Element>>;
    
    /// Get universe order mapping
    fn get_universe_order(&self) -> Option<HashMap<Element, usize>>;
    
    /// Get congruence lattice
    fn con(&self) -> Option<Box<dyn CongruenceLattice>>;
    
    /// Get subalgebra lattice  
    fn sub(&self) -> Option<Box<dyn SubalgebraLattice>>;
    
    /// Reset congruence and subalgebra lattices
    fn reset_con_and_sub(&mut self);
    
    /// Get parent algebra
    fn parent(&self) -> Option<Box<dyn SmallAlgebra>>;
    
    /// Get parent algebras list
    fn parents(&self) -> Option<Vec<Box<dyn SmallAlgebra>>>;
    
    /// Convert to default value operations (UI only)
    fn convert_to_default_value_ops(&mut self);
}

/// Algebra type enumeration
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum AlgebraType {
    Basic,
    BasicLattice,
    Quotient,
    Subalgebra,
    Product,
    Power,
    MatrixPower,
    Reduct,
    Subproduct,
    Free,
    PolinLike,
    UnaryTermsMonoid,
    FiniteField,
}
```

#### 2. Implementation Strategy
- **Interface → Trait**: Convert Java interface to Rust trait
- **Enum Translation**: Convert Java enum to Rust enum with proper derives
- **Generic vs Dynamic Dispatch**: Use `Box<dyn SmallAlgebra>` for dynamic dispatch in parent/children relationships
- **Error Handling**: Use `Option<T>` for nullable returns, `Result<T, E>` for operations that can fail
- **Memory Management**: Use `Box<dyn Trait>` for trait objects to avoid size issues

#### 3. Method Organization
- **Trait Methods**: All methods defined in trait (no default implementations needed)
- **Associated Types**: Consider using associated types for Element type
- **Lifetime Management**: Use appropriate lifetimes for references

### Java Wrapper Suitability
**Status**: ❌ **NOT SUITABLE** - Interface cannot be instantiated directly

**Reasoning**: 
- SmallAlgebra is an interface, not a concrete class
- Cannot create instances for testing without concrete implementations
- Wrapper should be created for concrete implementations (BasicAlgebra, ProductAlgebra, etc.)

### Testing Strategy
1. **Unit Tests**: Test trait methods through concrete implementations
2. **Integration Tests**: Test with actual algebra instances
3. **Cross-Language Tests**: Compare against Java implementations of concrete classes
4. **Mock Testing**: Use mock implementations for testing trait behavior

### Implementation Priority
**BLOCKED** - Cannot proceed until dependencies are completed:
1. Complete CongruenceLattice (Task 80)
2. Complete SubalgebraLattice (Task 76) 
3. Complete Algebra interface (parent dependency)
4. Then implement SmallAlgebra trait

### Recommendations
1. **Update Dependencies**: Add `Algebra` interface to dependency list
2. **Wait for Dependencies**: Do not start implementation until CongruenceLattice and SubalgebraLattice are complete
3. **Design for Extensibility**: Ensure trait design accommodates all concrete implementations
4. **Consider Associated Types**: Use associated types for Element type to allow different element types
5. **Plan for Dynamic Dispatch**: Design parent/children relationships to work with trait objects

### Acceptance Criteria
- [ ] All dependencies completed (CongruenceLattice, SubalgebraLattice, Algebra)
- [ ] SmallAlgebra trait implemented with all 12 methods
- [ ] AlgebraType enum implemented
- [ ] Trait works with all concrete implementations
- [ ] Rust tests pass for trait methods
- [ ] Documentation complete
- [ ] Code compiles without warnings
