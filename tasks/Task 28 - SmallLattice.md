# Task 28: Translate `SmallLattice`

**Java File:** `org/uacalc/lat/SmallLattice.java`  
**Package:** `org.uacalc.lat`  
**Rust Module:** `lat::SmallLattice`  
**Dependencies:** 1 (1 non-UI/example) - **VERIFIED CORRECT**  
**Estimated Public Methods:** 1

### Description
Translate the Java interface `org.uacalc.lat.SmallLattice` to Rust with Python bindings.

### Dependencies
**VERIFIED DEPENDENCIES:**
This interface depends on:
- `org.uacalc.lat.Lattice` (Task 20 - NOT COMPLETED)

**Analysis Results:**
- SmallLattice extends Lattice interface
- Lattice interface has 2 dependencies (Algebra + Order)
- **Dependency count is correctly 1** (only Lattice)
- **Dependency is NOT COMPLETED** - cannot implement SmallLattice yet

### Implementation Recommendations

#### Java Class Analysis
- **Type**: Interface (extends Lattice)
- **Generic Parameter**: None
- **Public Methods**: 1 method
  - `upperCoversIndices(int index) -> int[]`
- **Dependencies**: Lattice (8 methods from Lattice + 1 from SmallLattice = 9 total)
- **Mathematical Purpose**: Defines lattice operations for small finite lattices with indexed elements
- **Usage Patterns**: Used in Lattices.conToSmallLattice() method, referenced in CongruenceLattice comments

#### Rust Translation Design
- **Rust Construct**: Trait (not struct)
- **Trait Name**: `SmallLattice`
- **Inheritance**: Must extend `Lattice` trait
- **Method Signature**: `fn upper_covers_indices(&self, index: usize) -> Vec<usize>`
- **Generic Dispatch**: Yes (trait with generic parameter from Lattice)
- **Dynamic Dispatch**: Yes (trait objects)
- **Associated Types**: None
- **Trait Bounds**: Must implement Lattice trait

#### Implementation Strategy
```rust
/// A small lattice is a finite lattice with indexed elements.
/// 
/// This trait extends the general Lattice trait with operations
/// specific to small finite lattices where elements can be indexed.
/// The main addition is the ability to get upper covers by index.
pub trait SmallLattice: Lattice {
    /// Returns the indices of the upper covers of the element at the given index.
    /// 
    /// # Arguments
    /// * `index` - The index of the element whose upper covers are requested
    /// 
    /// # Returns
    /// A vector of indices representing the upper covers of the element
    fn upper_covers_indices(&self, index: usize) -> Vec<usize>;
}
```

#### Java Wrapper Suitability
- **Suitable**: NO - Interface cannot be instantiated directly
- **Reason**: SmallLattice is an interface, not a concrete class
- **Alternative**: Create wrapper for concrete implementations that implement SmallLattice
- **Testing Strategy**: Test through implementing classes, not direct interface testing
- **Note**: The interface itself cannot be tested in isolation

#### Python Bindings Strategy
- **Approach**: Export as trait, not concrete struct
- **Usage**: Python users implement the trait for their small lattice types
- **Example**: `class MySmallLattice(SmallLattice): def upper_covers_indices(self, index): return ...`
- **Integration**: Must work with Lattices.conToSmallLattice() method
- **Type Safety**: Ensure proper index handling in Python

#### Testing Strategy
- **Rust Tests**: Test trait implementations, not trait itself
- **Python Tests**: Test through implementing classes
- **Integration Tests**: Test with Lattices.conToSmallLattice() method
- **Edge Cases**: Test with empty lattices, single element lattices, large lattices
- **Mathematical Properties**: Test lattice laws and upper cover properties
- **Performance**: Test with large small lattices and complex operations

#### Dependencies Verification
- **Current Status**: CORRECT - Listed as 1 dependency
- **Actual Status**: 1 DEPENDENCY (Lattice)
- **Action Required**: None - dependency count is correct
- **Task Order**: Cannot be implemented until Lattice is completed
- **Blocking Tasks**: Task 20 (Lattice)

#### Critical Implementation Notes
1. **Trait Inheritance**: Must extend Lattice trait
2. **Index Handling**: Use usize for indices (Rust standard)
3. **Upper Covers**: Return Vec<usize> for indices of upper covers
4. **Mathematical Correctness**: Implementations must satisfy lattice laws
5. **Performance**: Consider performance for large small lattices
6. **Error Handling**: No error conditions - always returns Vec<usize>
7. **Documentation**: Include mathematical definitions and lattice theory concepts
8. **Integration**: Must work with Lattices.conToSmallLattice() method

### Acceptance Criteria
- [ ] SmallLattice trait implemented in Rust with proper documentation
- [ ] Python bindings expose SmallLattice trait for user implementation
- [ ] Java wrapper created for concrete implementations (not interface)
- [ ] Rust tests pass for trait implementations with various small lattice types
- [ ] Python tests pass for trait implementations
- [ ] Code compiles without warnings
- [ ] Documentation complete with mathematical properties and examples
- [ ] Integration with Lattices.conToSmallLattice() verified
- [ ] Mathematical properties (lattice laws) tested
- [ ] Performance tests with large small lattices
- [ ] Index handling works correctly in both Rust and Python
- [ ] Trait objects support both static and dynamic dispatch
- [ ] Examples provided for common small lattice types
- [ ] **Dependencies completed**: Lattice (Task 20) must be finished first
