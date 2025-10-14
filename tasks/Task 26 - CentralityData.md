# UACalc Rust/Python Translation Plan

## Task 26: Translate `CentralityData`

**Java File:** `org/uacalc/alg/conlat/CentralityData.java`  
**Package:** `org.uacalc.alg.conlat`  
**Rust Module:** `alg::conlat::CentralityData`  
**Dependencies:** 3 (3 non-UI/example)  
**Estimated Public Methods:** 13

### Description
Translate the Java class `org.uacalc.alg.conlat.CentralityData` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.conlat.BinaryRelation` (Task 21 - COMPLETED)
- `org.uacalc.alg.conlat.Partition` (Task 5 - COMPLETED)  
- `org.uacalc.element.SubProductElement` (Task 51 - NOT COMPLETED)

### Java Class Analysis

#### Class Type
- **Type**: Concrete class implementing `Comparable<CentralityData>`
- **Purpose**: Holds centrality data including two tolerance relations (S and T), a congruence delta, and failure information for centrality, weak centrality, and strong rectangularity

#### Public Methods (13 total)
1. `CentralityData(BinaryRelation S, BinaryRelation T, Partition delta)` - Constructor
2. `compareTo(CentralityData data)` - Comparable implementation
3. `getLeft()` - Get left relation
4. `getRight()` - Get right relation  
5. `getDelta()` - Get delta partition
6. `setCentralityFailure(SubProductElement)` - Set centrality failure
7. `getCentralityFailure()` - Get centrality failure
8. `setWeakCentralityFailure(SubProductElement)` - Set weak centrality failure
9. `getWeakCentralityFailure()` - Get weak centrality failure
10. `setStrongRectangularityFailure(SubProductElement)` - Set strong rectangularity failure
11. `getStrongRectangularityFailure()` - Get strong rectangularity failure
12. `toString()` - String representation
13. `main(String[] args)` - Main method (empty implementation)

#### Fields
- `left: BinaryRelation` (final)
- `right: BinaryRelation` (final) 
- `delta: Partition` (final)
- `centralityFailure: SubProductElement` (mutable)
- `weakCentralityFailure: SubProductElement` (mutable)
- `strongRectangularityFailure: SubProductElement` (mutable)

### Usage Pattern Analysis
- Used in `CongruenceLattice.java` for centrality calculations
- Used in `TermTableModel.java` for UI display
- Used in `ComputationsController.java` for background computations
- Typically created in lists and iterated over
- Used for storing and comparing centrality results

### Rust Implementation Recommendations

#### Struct Design
```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CentralityData {
    pub left: Box<dyn BinaryRelation<IntArray>>,
    pub right: Box<dyn BinaryRelation<IntArray>>, 
    pub delta: Partition,
    pub centrality_failure: Option<SubProductElement>,
    pub weak_centrality_failure: Option<SubProductElement>,
    pub strong_rectangularity_failure: Option<SubProductElement>,
}
```

#### Key Design Decisions
1. **Trait Objects**: Use `Box<dyn BinaryRelation<IntArray>>` for left/right relations to allow different implementations
2. **Option Types**: Use `Option<SubProductElement>` for failure fields (null in Java becomes None in Rust)
3. **Comparable**: Implement `Ord` and `PartialOrd` traits for comparison
4. **Ownership**: Use owned types for better memory management

#### Method Organization
- **Constructor**: `new(left, right, delta) -> Self`
- **Getters**: Simple field access (public fields)
- **Setters**: Mutable field access (public fields)
- **Comparison**: Implement `Ord` trait
- **Display**: Implement `Display` trait for `toString()`

#### Error Handling
- Constructor should validate inputs
- Use `Result<Self, String>` for construction errors
- Provide both `new()` and `new_safe()` versions

### Java Wrapper Suitability
**SUITABLE** - This is a concrete class with:
- Simple constructor taking 3 parameters
- Clear getter/setter methods
- Comparable interface for testing
- No complex internal state or algorithms

### Testing Strategy
1. **Constructor Tests**: Test with valid/invalid BinaryRelation and Partition inputs
2. **Comparison Tests**: Test `compareTo` equivalent with different delta values
3. **Getter/Setter Tests**: Test all field access methods
4. **Display Tests**: Test `toString` output format
5. **Integration Tests**: Test with actual BinaryRelation and Partition instances

### Implementation Priority
**BLOCKED** - Cannot proceed until:
- `SubProductElement` (Task 51) is completed
- All dependencies must be available for proper testing

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods  
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] **BLOCKED**: SubProductElement dependency must be completed first
