# Task 59: Translate `Lattices`

**Java File:** `org/uacalc/lat/Lattices.java`  
**Package:** `org.uacalc.lat`  
**Rust Module:** `lat::Lattices`  
**Dependencies:** 6 (6 non-UI/example)  
**Estimated Public Methods:** 6

## Description
Translate the Java class `org.uacalc.lat.Lattices` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Utility class with static methods (6 public methods)
- **Constructor**: Private (utility class pattern)
- **Purpose**: Factory methods for creating lattices from operations and other lattice operations

### Method Analysis
**Factory Methods (4 methods):**
- `latticeFromMeet(String name, Operation meet) -> BasicLattice` - Creates lattice from meet operation using integers
- `latticeFromJoin(String name, Operation join) -> BasicLattice` - Creates lattice from join operation using integers  
- `latticeFromMeet(String name, List univ, Operation meet) -> BasicLattice` - Creates lattice from meet operation with custom universe
- `latticeFromJoin(String name, List univ, Operation join) -> BasicLattice` - Creates lattice from join operation with custom universe

**Lattice Operations (2 methods):**
- `conToSmallLattice(CongruenceLattice con) -> SmallLattice` - Converts congruence lattice to small lattice
- `dual(BasicLattice lat) -> BasicLattice` - Creates dual of a basic lattice

## Dependencies Analysis

### Direct Dependencies
- **CongruenceLattice** (Task 80) - Used in conToSmallLattice method
- **BasicLattice** (Task 85) - Return type for factory methods and dual method
- **Operation** (Task 12) - Used in all factory methods
- **SmallLattice** (Task 28 - ✅ **COMPLETED**) - Return type for conToSmallLattice method
- **Partition** (Task 5) - Used in conToSmallLattice method
- **org.latdraw.orderedset.OrderedSet** - External dependency for lattice construction

### Missing Dependencies
The current dependency list is **INCORRECT**. Missing dependencies:
- **SmallLattice** (Task 28 - ✅ **COMPLETED**) - Return type for conToSmallLattice
- **Partition** (Task 5) - Used in conToSmallLattice method
- **org.latdraw.orderedset.OrderedSet** - External dependency (excluded from translation)

### Dependency Order
This task should be implemented **AFTER**:
1. Task 5: Partition ✅ (completed)
2. Task 12: Operation ✅ (completed) 
3. Task 28: SmallLattice (✅ **COMPLETED**)
4. Task 80: CongruenceLattice (pending)
5. Task 85: BasicLattice (pending)

## Rust Implementation Recommendations

### Design Pattern
- **Rust Construct**: Module with free functions (utility class pattern)
- **No struct needed**: All methods are static/utility functions
- **Error Handling**: Use `Result<BasicLattice, String>` for factory methods that can fail
- **External Dependencies**: Handle `org.latdraw.orderedset.OrderedSet` dependency by either:
  1. Creating a minimal Rust equivalent
  2. Using `Option<OrderedSet>` and returning `None` when external dependency unavailable
  3. Marking methods as `unimplemented!()` until external dependency is available

### Method Organization
- **Factory Methods**: Implement as free functions in `lat::lattices` module
- **Lattice Operations**: Implement as free functions
- **Error Handling**: All methods that can fail should return `Result<T, String>`
- **Null Handling**: Replace Java `null` returns with `Option<T>` or `Result<T, String>`

### Key Implementation Challenges
1. **External Dependency**: `org.latdraw.orderedset.OrderedSet` is not part of UACalc
2. **Exception Handling**: Java methods catch `NonOrderedSetException` and print stack trace
3. **Generic Lists**: Java uses raw `List` types - need proper generic constraints
4. **Iterator Patterns**: Convert Java iterators to Rust iterator patterns

### Java Wrapper Suitability
- **Suitable**: Yes - concrete utility class with static methods
- **Testing Strategy**: Can test all methods with mock data
- **CLI Commands**: One command per method with appropriate parameters

## Implementation Steps

1. **Wait for Dependencies**
   - Complete Task 28: SmallLattice (✅ **COMPLETED**)
   - Complete Task 80: CongruenceLattice  
   - Complete Task 85: BasicLattice

2. **Design Rust Module**
   - Create `src/lat/lattices.rs` module
   - Implement free functions for each static method
   - Handle external dependency appropriately

3. **Implement Core Methods**
   - `lattice_from_meet` (both variants)
   - `lattice_from_join` (both variants)
   - `con_to_small_lattice`
   - `dual`

4. **Create Python Bindings**
   - Expose all functions to Python
   - Use `#[pyfunction]` for static methods
   - Handle error cases with `PyResult`

5. **Create Java CLI Wrapper**
   - Implement wrapper with all 6 methods
   - Use appropriate test data for each method
   - Handle external dependency gracefully

6. **Write Tests**
   - Test all methods with valid inputs
   - Test error cases and edge conditions
   - Compare outputs with Java implementation

## Acceptance Criteria
- [ ] All 6 public methods translated to Rust
- [ ] Python bindings expose all methods as functions
- [ ] Java CLI wrapper created with all methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] External dependency handled appropriately
