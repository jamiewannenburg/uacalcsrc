# Task 53: Translate `VirtualLists`

**Java File:** `org/uacalc/util/virtuallist/VirtualLists.java`  
**Package:** `org.uacalc.util.virtuallist`  
**Rust Module:** `util::virtuallist::VirtualLists`  
**Dependencies:** 1 (1 non-UI/example)  
**Estimated Public Methods:** 8

## Description
Translate the Java class `org.uacalc.util.virtuallist.VirtualLists` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Concrete utility class with static methods
- **Purpose**: Provides static utility methods for creating virtual lists and array indexing
- **Pattern**: Utility class with static factory methods

### Public Methods (8 total)
1. `intTuples(int tupleLen, int base)` - Returns LongList<int[]> of all tuples
2. `intTuplesWithMin(int tupleLen, int base, int min)` - Returns LongList<int[]> with min constraint
3. `arrayIndexerWithMin(long k, int arity, int base, int min)` - Array indexer with min constraint
4. `testPow(long k)` - Test method for power calculations
5. `foo(long k, int r)` - Helper method for binomial calculations
6. `bar(long k, int r)` - Helper method for binomial calculations  
7. `baz(long k, int r)` - Helper method for binomial calculations
8. `main(String[] args)` - Test/demo method

### Dependencies Analysis
**CORRECTED DEPENDENCIES:**
- `org.uacalc.util.virtuallist.LongList` - Used for return types
- `org.uacalc.util.virtuallist.TupleWithMin` - Used in main method for testing

**INCORRECT DEPENDENCIES (to be removed):**
- `org.uacalc.alg.op.Operation` - NOT USED (imported but never referenced)
- `org.uacalc.util` - NOT USED (imported but never referenced)

**Standard Java Dependencies:**
- `java.math.BigInteger` - For large number calculations
- `java.util.Arrays` - For array operations
- `java.util.concurrent.atomic.AtomicLong` - For thread-safe counters
- `java.util.stream.LongStream` - For stream operations
- `java.util.stream.Stream` - For stream operations
- `java.util.*` - For collections and utilities

## Rust Implementation Recommendations

### Design Pattern
- **Rust Construct**: Module with free functions (not a struct)
- **Reasoning**: Java class contains only static methods, so Rust module with free functions is most appropriate
- **Trait Needed**: No (utility functions only)
- **Generic Dispatch**: No (concrete types)
- **Dynamic Dispatch**: No (static functions)

### Method Organization
- **Free Functions**: All methods should be free functions in the module
- **Error Handling**: Use `Result<T, String>` for methods that can fail
- **Panic Versions**: Provide both `_safe` and panic versions for compatibility

### Implementation Structure
```rust
pub mod virtuallist {
    // Free functions matching Java static methods
    pub fn int_tuples(tuple_len: usize, base: usize) -> Result<Box<dyn LongList<Vec<i32>>>, String>
    pub fn int_tuples_with_min(tuple_len: usize, base: usize, min: usize) -> Result<Box<dyn LongList<Vec<i32>>>, String>
    pub fn array_indexer_with_min(k: i64, arity: usize, base: usize, min: usize) -> Result<Vec<i32>, String>
    pub fn test_pow(k: i64) -> String
    pub fn foo(k: i64, r: usize) -> i32
    pub fn bar(k: i64, r: usize) -> i32
    pub fn baz(k: i64, r: usize) -> i32
}
```

### Key Implementation Notes
1. **LongList Integration**: Use existing `LongList` trait and implementations
2. **BigInteger Handling**: Use Rust's `i64` with overflow checking
3. **Array Operations**: Use `Vec<i32>` instead of `int[]`
4. **Error Handling**: Convert Java exceptions to Rust `Result` types
5. **Thread Safety**: Ensure all functions are thread-safe (no mutable state)

## Java Wrapper Suitability
- **Suitable**: Yes - Concrete class with static methods
- **Testing Strategy**: Create wrapper that calls all static methods with various parameters
- **CLI Commands**: One command per public method with appropriate parameters

## Testing Strategy
- **Rust Tests**: Test all 8 public methods with various inputs
- **Python Tests**: Test through Python bindings with Java comparison
- **Edge Cases**: Test overflow conditions, invalid parameters, boundary values
- **Performance**: Test with large inputs to verify performance characteristics

## Implementation Status
- **Rust Implementation**: ❌ Not implemented
- **Python Bindings**: ❌ Not implemented  
- **Java Wrapper**: ❌ Not implemented
- **Tests**: ❌ Not implemented

## Next Steps
1. Implement Rust module with all 8 public methods
2. Create Python bindings for all methods
3. Create Java CLI wrapper for testing
4. Write comprehensive test suite
5. Verify exact behavior matches Java implementation

### Acceptance Criteria
- [ ] All 8 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
