# Task 47: Translate `BasicSet`

**Java File:** `org/uacalc/alg/sublat/BasicSet.java`  
**Package:** `org.uacalc.alg.sublat`  
**Rust Module:** `alg::sublat::BasicSet`  
**Dependencies:** 3 (3 non-UI/example)  
**Estimated Public Methods:** ~14

## Description
Translate the Java class `org.uacalc.alg.sublat.BasicSet` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Concrete class
- **Inheritance**: Extends `IntArray`, implements `Comparable`
- **Purpose**: Represents a set of integers {0, 1, ..., n-1} with basic set operations

### Public Methods Identified
1. `BasicSet(int[] set)` - Constructor
2. `normalize()` - Sorts the array in ascending order
3. `compareTo(Object o)` - Implements Comparable interface
4. `leq(BasicSet set2)` - Subset check
5. `leq(int[] u, int[] v)` - Static subset check
6. `contains(int i)` - Membership test
7. `setDifference(BasicSet set2)` - Set difference
8. `intersection(BasicSet set2)` - Set intersection
9. `intersection(BasicSet set1, BasicSet set2)` - Static intersection
10. `union(BasicSet set2)` - Set union
11. `union(BasicSet set1, BasicSet set2)` - Static union
12. `toString(SmallAlgebra alg)` - String representation with algebra elements

### Static Constants
- `EMPTY_SET` - Empty set constant

## Dependencies Analysis

### Direct Dependencies (Verified)
- `org.uacalc.alg.SmallAlgebra` - Used in `toString()` method
- `org.uacalc.util.ArrayString` - Used in `toString()` method  
- `org.uacalc.util.IntArray` - Parent class

### Usage Patterns Found
- Heavily used in `SubalgebraLattice` for representing subalgebras
- Used in `Algebras.java` for various algebra operations
- Used in `ComputationsController.java` for UI operations
- Core data structure for set operations in the algebra system

## Rust Implementation Recommendations

### Struct Design
```rust
pub struct BasicSet {
    pub elements: Vec<i32>,  // Sorted array of integers
}
```

### Trait Implementations Required
- `Clone` - For copying BasicSet instances
- `Debug` - For debugging output
- `PartialEq` and `Eq` - For equality comparison
- `PartialOrd` and `Ord` - For ordering (implements Comparable)
- `Hash` - For use in HashMap/HashSet
- `Display` - For string representation

### Method Organization
- **Constructor**: `new(elements: Vec<i32>) -> Self`
- **Instance Methods**: All non-static methods as `&self` or `&mut self`
- **Static Methods**: All static methods as associated functions
- **Error Handling**: Use `Result<T, String>` for methods that can fail

### Key Implementation Details
1. **Normalization**: Always keep elements sorted (ascending order)
2. **Empty Set**: Use `BasicSet::EMPTY_SET` constant
3. **Set Operations**: Implement efficient algorithms for union, intersection, difference
4. **Membership Test**: Use binary search for O(log n) performance
5. **Comparison**: First by size, then lexicographically

## Java Wrapper Suitability
- **Suitable**: Yes - Concrete class with clear public API
- **Testing Strategy**: Create wrapper with all public methods exposed via CLI
- **Key Methods to Test**: All constructors, set operations, comparison methods

## Implementation Priority
- **High Priority**: Core set operations (union, intersection, difference, contains)
- **Medium Priority**: Comparison and ordering methods
- **Low Priority**: String representation methods

## Testing Strategy
1. **Unit Tests**: Test each method individually with various inputs
2. **Integration Tests**: Test set operations with complex scenarios
3. **Cross-Language Tests**: Compare Rust output with Java wrapper output
4. **Edge Cases**: Empty sets, single elements, duplicate elements

## Current Implementation Status

### Overall Status: **NOT STARTED** (0% Complete)

### Component Status:
- **Rust Implementation**: ❌ Not Started - Only placeholder struct exists
- **Python Bindings**: ❌ Not Started - No bindings exist
- **Java Wrapper**: ❌ Not Started - No wrapper exists  
- **Tests**: ❌ Not Started - No tests exist

### Dependencies Status:
- **IntArray**: ✅ Complete - Fully implemented with comprehensive tests
- **SmallAlgebra**: ✅ Complete - Trait and BasicSmallAlgebra implementation ready
- **ArrayString**: ✅ Complete - Full utility functions implemented

### Implementation Details:
- **Rust Module**: `src/alg/sublat/mod.rs` contains only placeholder struct
- **Dependencies Ready**: All required dependencies are fully implemented
- **No Blocking Issues**: Task can proceed immediately

### Next Steps:
1. Implement complete BasicSet struct in Rust
2. Add all public methods from Java class
3. Implement Python bindings in uacalc_lib
4. Create Java wrapper in java_wrapper
5. Add comprehensive test suite

## Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
