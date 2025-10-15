# Task 16: Translate `OrderedSets`

**Java File:** `org/uacalc/lat/OrderedSets.java`  
**Package:** `org.uacalc.lat`  
**Rust Module:** `lat::ordered_sets`  
**Dependencies:** 1 (Order interface)  
**Estimated Public Methods:** 2 (maximals, main)

## Description
Translate the Java class `org.uacalc.lat.OrderedSets` to Rust with Python bindings.

## Java Class Analysis

**Class Type:** Concrete class with static methods only  
**Pattern:** Static utility class  
**Key Methods:**
- `maximals<E>(Collection<? extends E> elems, Order<? super E> order) -> List<E>` - Main algorithm method
- `main(String[] args)` - Test/demo method

**Dependencies Analysis:**
- `org.uacalc.lat.Order` - Simple interface with single `leq(E a, E b) -> boolean` method
- `java.util.*` - Standard Java collections (Collection, List, ArrayList)

**Usage Patterns:**
- Used in `org.uacalc.alg.SubProductAlgebra.thinGenerators()` method
- Called via fully qualified name: `OrderedSets.maximals(projs, new Order<IntArray>() { ... })`
- No instantiation required - pure static utility class

## Rust Implementation Recommendations

### Design Decisions
- **Rust Construct**: Module with free functions (no struct needed)
- **Order Interface**: Translate to `Fn(&T, &T) -> bool` closure trait bound
- **Collections**: Use `Vec<T>` and `&[T]` instead of Java collections
- **Generics**: Use Rust generics with trait bounds for type safety

### Method Translation

1. **`maximals` Method**
   ```rust
   pub fn maximals<T, F>(elems: &[T], order: F) -> Vec<T> 
   where 
       F: Fn(&T, &T) -> bool 
   {
       // Implementation matching Java algorithm exactly
   }
   ```
   - **Pattern**: Generic function with closure parameter
   - **Note**: Use `&[T]` instead of `Collection` for better Rust ergonomics
   - **Algorithm**: Must match Java implementation exactly (O(n²) complexity)

2. **`main` Method**
   ```rust
   pub fn main() {
       // Test implementation with integer divisibility order
   }
   ```
   - **Pattern**: Test function, not part of public API
   - **Purpose**: Demonstrate usage and provide test data

### Rust Module Structure
```rust
// src/lat/ordered_sets.rs
pub fn maximals<T, F>(elems: &[T], order: F) -> Vec<T> 
where 
    F: Fn(&T, &T) -> bool 
{
    // Implementation matching Java algorithm exactly
}

pub fn main() {
    // Test implementation
}
```

### Python Bindings
- Expose `maximals` as static method
- Use `List[T]` for Python collections
- Accept callable for order relation
- **Pattern**: Static method binding with generic type support

### Java Wrapper Suitability
- **SUITABLE**: Concrete class with static methods
- **Testing Strategy**: Unit tests with various order relations
- **CLI Commands**: `maximals` command with test data
- **Location**: `java_wrapper/src/lat/OrderedSetsWrapper.java`

### Testing Strategy
- Test with integer divisibility order (as in main method)
- Test with custom order relations
- Test edge cases (empty collections, single elements)
- Compare results with Java implementation
- **Timeout**: Use standard timeout (no special requirements)

## Implementation Status

### Current State
- [x] Rust implementation not started (only placeholder in mod.rs)
- [x] Python bindings not implemented
- [x] Java wrapper not created
- [x] Tests not written

### Required Actions
1. **Implement Rust Module**
   - Create `src/lat/ordered_sets.rs`
   - Implement `maximals` function with exact Java algorithm
   - Implement `main` function for testing
   - Add comprehensive documentation

2. **Create Python Bindings**
   - Add to `uacalc_lib/src/lat.rs`
   - Expose `maximals` as static method
   - Handle generic types properly

3. **Create Java Wrapper**
   - Create `java_wrapper/src/lat/OrderedSetsWrapper.java`
   - Implement `maximals` command with test data
   - Support custom order relations via command line

4. **Write Tests**
   - Rust unit tests for `maximals` function
   - Python tests comparing with Java wrapper
   - Test various order relations and edge cases

## Acceptance Criteria
- [x] All public methods translated to Rust ✅ **COMPLETED**
- [x] Python bindings expose all public methods ✅ **COMPLETED**
- [x] Java CLI wrapper created with all public methods ✅ **COMPLETED**
- [x] Rust tests pass with timeouts enabled ✅ **COMPLETED**
- [x] Python tests pass and match Java output ✅ **COMPLETED**
- [x] Code compiles without warnings ✅ **COMPLETED**
- [x] Documentation complete ✅ **COMPLETED**
- [x] Order interface dependency properly handled ✅ **COMPLETED**
- [x] Generic type parameters correctly translated ✅ **COMPLETED**

### Implementation Status: ✅ **COMPLETED**

**Completed Components:**
- ✅ OrderedSets module implemented in `src/lat/ordered_sets.rs`
- ✅ `maximals` function with exact Java algorithm implementation
- ✅ Generic type support with proper trait bounds
- ✅ Integration with Order trait verified and working
- ✅ Comprehensive test suite with 4 test cases
- ✅ Python bindings available through uacalc_lib
- ✅ Java CLI wrapper for testing and comparison
- ✅ Performance optimized O(n²) algorithm matching Java
- ✅ Memory-safe implementation with proper ownership patterns
