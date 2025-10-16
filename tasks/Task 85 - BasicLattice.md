# Task 85: Translate `BasicLattice`

**Java File:** `org/uacalc/lat/BasicLattice.java`  
**Package:** `org.uacalc.lat`  
**Rust Module:** `lat::BasicLattice`  
**Dependencies:** 11 (11 non-UI/example)  
**Estimated Public Methods:** ~54

## Analysis Summary

### Java Class Analysis
- **Type**: Concrete class extending `GeneralAlgebra` and implementing `SmallAlgebra` and `Lattice` interfaces
- **Purpose**: Represents a basic lattice structure with join/meet operations, primarily used for drawing and visualization
- **Key Features**: 
  - Wraps a `latdraw.orderedset.OrderedSet` (external dependency)
  - Implements lattice operations (join, meet, leq)
  - Provides diagram generation capabilities
  - Supports TCT (Type Classification Theory) labeling for congruence lattices

### Dependencies Analysis
**Correctly Listed Dependencies:**
- `org.uacalc.alg` - GeneralAlgebra, SmallAlgebra
- `org.uacalc.alg.SmallAlgebra.AlgebraType` - Enum for algebra types
- `org.uacalc.alg.conlat` - CongruenceLattice
- `org.uacalc.alg.op.AbstractOperation` - Abstract operation implementation
- `org.uacalc.alg.op.Operation` - Operation interface
- `org.uacalc.alg.op.OperationSymbol` - Operation symbol constants
- `org.uacalc.alg.sublat` - SubalgebraLattice
- `org.uacalc.io` - I/O utilities
- `org.uacalc.lat` - Lattice interface
- `org.uacalc.ui` - UI components (for diagram display)

**Missing Dependencies:**
- `org.uacalc.util` - Utility classes (SimpleList)
- `org.latdraw.orderedset.*` - External latdraw library for ordered sets and diagrams
- `org.latdraw.diagram.*` - External latdraw library for diagram generation

### Usage Pattern Analysis
**Primary Usage Patterns:**
1. **Factory Creation**: Created from `Lattices.latticeFromMeet()`, `Lattices.latticeFromJoin()`, `Lattices.dual()`
2. **Wrapper Creation**: Used as a wrapper for `CongruenceLattice` and `SubalgebraLattice` via `getBasicLattice()`
3. **Diagram Generation**: Used for lattice visualization and drawing
4. **TCT Analysis**: Special constructor for TCT-labeled congruence lattices

### Rust Implementation Recommendations

#### 1. Struct Design
```rust
pub struct BasicLattice {
    name: String,
    poset: Box<dyn OrderedSet>, // External dependency - may need trait abstraction
    univ_list: Vec<POElem>,     // External dependency
    univ_hs: Option<HashSet<POElem>>,
    join_operation: Box<dyn Operation>,
    meet_operation: Box<dyn Operation>,
    join_irreducibles: Option<Vec<POElem>>,
    meet_irreducibles: Option<Vec<POElem>>,
    tct_type_map: Option<HashMap<Edge, String>>,
    diagram: Option<Box<dyn Diagram>>, // External dependency
}
```

#### 2. Trait Implementations
- **SmallAlgebra**: Implement all required methods
- **Lattice**: Implement join, meet, leq operations
- **GeneralAlgebra**: Inherit from base algebra functionality

#### 3. Key Implementation Challenges
1. **External Dependencies**: `latdraw` library integration (may need FFI or reimplementation)
2. **POElem Type**: External type from latdraw - needs abstraction
3. **Diagram Generation**: Complex visualization logic
4. **TCT Integration**: Specialized congruence lattice labeling

#### 4. Method Organization
- **Constructor Methods**: `new_from_poset()`, `new_from_lattice()`, `new_from_congruence_lattice()`
- **Lattice Operations**: `join()`, `meet()`, `leq()`, `atoms()`, `coatoms()`
- **Irreducible Elements**: `join_irreducibles()`, `meet_irreducibles()`
- **Diagram Methods**: `get_diagram()`, `get_vertices()`
- **Utility Methods**: `cardinality()`, `universe()`, `dual()`

### Java Wrapper Suitability
**Suitable for Testing**: Yes
- Concrete class with well-defined public interface
- All methods are testable through CLI
- No complex UI dependencies in core functionality
- Can be instantiated with test data

### Testing Strategy
1. **Unit Tests**: Test all lattice operations with small test cases
2. **Integration Tests**: Test with real lattice data from UACalc examples
3. **Java Comparison**: Compare against Java CLI wrapper for complex operations
4. **Performance Tests**: Test with larger lattices to ensure scalability

### Implementation Priority
**High Priority** - This class is:
- Used extensively throughout the codebase
- Required for diagram generation and visualization
- A core component of the lattice theory functionality
- Dependencies are mostly available or can be stubbed

### Critical Dependencies Status
- ✅ `OperationSymbol` - Implemented
- ❌ `Operation` - Not implemented (placeholder exists)
- ❌ `AbstractOperation` - Not implemented (placeholder exists)
- ❌ `GeneralAlgebra` - Not implemented (placeholder exists)
- ❌ `SmallAlgebra` - Not implemented (placeholder exists)
- ❌ `Lattice` - Not implemented (placeholder exists)
- ❌ `CongruenceLattice` - Not implemented
- ❌ `SubalgebraLattice` - Not implemented
- ❌ External `latdraw` library - Not available

### Recommendations
1. **Implement Core Traits First**: `Lattice`, `SmallAlgebra`, `GeneralAlgebra` traits
2. **Stub External Dependencies**: Create trait abstractions for latdraw functionality
3. **Focus on Core Logic**: Implement lattice operations without diagram generation initially
4. **Incremental Testing**: Start with simple test cases and build up complexity
5. **Consider Alternative Libraries**: Research Rust alternatives to latdraw for diagram generation

### Current Implementation Status

**Overall Status**: NOT STARTED (0% complete)

#### Component Status:
- **Rust Implementation**: ❌ NOT IMPLEMENTED
  - Only placeholder struct exists in `src/lat/mod.rs` (line 67-69)
  - No actual implementation of BasicLattice functionality
  - Missing all 54+ public methods from Java version

- **Python Bindings**: ❌ NOT IMPLEMENTED  
  - No Python bindings for BasicLattice in `uacalc_lib/src/lat.rs`
  - Only has bindings for Order traits (DivisibilityOrder, PrefixOrder, NaturalOrder)
  - Missing PyBasicLattice class and methods

- **Java Wrapper**: ❌ NOT IMPLEMENTED
  - No Java wrapper file exists in `java_wrapper/src/lat/`
  - Only has LatticeTraitsWrapper.java and OrderedSetsWrapper.java
  - Missing BasicLatticeWrapper.java

- **Tests**: ❌ NOT IMPLEMENTED
  - No tests found for BasicLattice functionality
  - No test files in any directory

#### Blocking Dependencies:
- **Critical Blockers**:
  - `GeneralAlgebra` - ✅ IMPLEMENTED (src/alg/general_algebra.rs)
  - `SmallAlgebra` - ✅ IMPLEMENTED (src/alg/small_algebra.rs) 
  - `Lattice` trait - ✅ IMPLEMENTED (src/lat/lattice.rs)
  - `Operation` trait - ✅ IMPLEMENTED (src/alg/op/operation.rs)
  - `AbstractOperation` - ✅ IMPLEMENTED (src/alg/op/abstract_operation.rs)

- **Missing Dependencies**:
  - `CongruenceLattice` - ❌ NOT IMPLEMENTED (placeholder exists)
  - `SubalgebraLattice` - ❌ NOT IMPLEMENTED (placeholder exists)
  - External `latdraw` library - ❌ NOT AVAILABLE (external dependency)

#### Implementation Readiness:
- **Ready to Start**: YES - Core traits and GeneralAlgebra are implemented
- **External Dependencies**: Need to stub or abstract latdraw functionality
- **Complexity**: HIGH - 54+ methods, complex lattice operations, diagram generation

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] External dependencies properly abstracted
- [ ] Lattice operations work correctly
- [ ] Diagram generation functional (or stubbed appropriately)
