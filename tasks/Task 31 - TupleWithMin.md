# UACalc Rust/Python Translation Plan

## Overview

This plan contains the ordered list of translation tasks for converting the UACalc Java library to Rust with Python bindings. Tasks are ordered by dependency count to ensure foundational classes are translated before dependent classes.

## Translation Strategy

### Approach
- Direct Java-to-Rust translation maintaining exact semantics
- Use Rust idioms where appropriate (traits for interfaces, Result/Option, etc.)
- All public methods must be translated and tested
- Output must match Java implementation exactly

### Testing Strategy
- Rust tests for all public methods with timeouts
- Python binding tests comparing against Java
- Java CLI wrappers for ground truth comparison
- Global memory limit configurable from Python

### ExcluRded Packages
The following packages are **excluded** from this plan:
- `org.uacalc.ui.*` - UI components (not needed for core library)
- `org.uacalc.nbui.*` - NetBeans UI components
- `org.uacalc.example.*` - Example/demo classes (NOTE: To be implemented later)


## Translation Tasks

## Task 31: Translate `TupleWithMin`

**Java File:** `org/uacalc/util/virtuallist/TupleWithMin.java`  
**Package:** `org.uacalc.util.virtuallist`  
**Rust Module:** `util::virtuallist::TupleWithMin`  
**Dependencies:** 1 (1 non-UI/example)  
**Estimated Public Methods:** 3

### Description
Translate the Java class `org.uacalc.util.virtuallist.TupleWithMin` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.util.virtuallist.LongList` (interface)

### Implementation Steps

1. **Analyze Java Implementation**
   - Read and understand the Java source code
   - Identify all public methods and their signatures
   - Note any special patterns (interfaces, abstract classes, etc.)
   - Identify dependencies on other UACalc classes

2. **Design Rust Translation**
   - Determine if Java interfaces should become Rust traits
   - Design struct/enum representations matching Java semantics
   - Plan for Rust idioms (Option instead of null, Result for errors, etc.)
   - Ensure all public methods are translated

3. **Implement Rust Code**
   - Create Rust module structure
   - Implement all public methods
   - Add comprehensive documentation
   - Follow Rust naming conventions (snake_case)

4. **Create Python Bindings (PyO3)**
   - Expose all public methods to Python
   - Use appropriate PyO3 types (PyResult, etc.)
   - Add Python docstrings

5. **Create Java CLI Wrapper**
   - Create wrapper in `java_wrapper/src/` matching package structure
   - Implement `main` method accepting command-line arguments
   - Expose all public methods through CLI commands
   - Output results in JSON/text format for comparison

6. **Write Rust Tests**
   - Test all public methods
   - Add tests with timeouts (slightly longer than Java completion times)
   - Test edge cases and error conditions
   - Compare results against Java CLI wrapper output

7. **Write Python Tests**
   - Test all public methods through Python bindings
   - Compare results against Java CLI wrapper output
   - Verify Python API matches Rust API

8. **Verification**
   - Run all tests and ensure they pass
   - Verify outputs match Java implementation exactly
   - Check test coverage for all public methods

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete

## Detailed Analysis

### Java Class Analysis
- **Class Type**: Concrete class implementing `LongList<int[]>`
- **Public Methods**: 3 methods
  - `TupleWithMin(int arrayLen, int base, int min)` - Constructor
  - `get(long k)` - Get kth element (from LongList interface)
  - `size()` - Get size (from LongList interface)
- **Special Patterns**: Implements LongList interface, uses complex mathematical algorithm for tuple generation

### Dependencies Analysis
- **Direct Dependencies**: 
  - `org.uacalc.util.virtuallist.LongList` (interface) - ✅ Already implemented in Rust
- **Standard Java Dependencies**: 
  - `java.util.Arrays` - ✅ Available in Rust as `std::fmt::Debug`
  - `java.util.stream.*` - ✅ Available in Rust as iterators
- **Dependencies Correct**: ✅ Yes, only depends on LongList which is already implemented

### Rust Implementation Recommendations

#### 1. Struct Design
```rust
pub struct TupleWithMin {
    pub array_len: usize,
    pub size: i64,
    pub min: usize,
    pub diff: usize,
    partial_sums: Vec<i64>,
}
```

#### 2. Trait Implementation
- Implement `LongList<Vec<i32>>` trait
- Provide both `new_safe()` and `new()` constructors
- Use `Result<Self, String>` for error handling

#### 3. Method Organization
- **Constructor**: `new_safe(array_len: usize, base: usize, min: usize) -> Result<Self, String>`
- **Trait Methods**: `get(&self, k: i64) -> Vec<i32>` and `size(&self) -> i64`
- **Private Methods**: Helper methods for mathematical calculations

#### 4. Generic vs Dynamic Dispatch
- Use concrete struct (not dynamic dispatch) since it's a specific implementation
- Implement `LongList<Vec<i32>>` trait for interface compliance

#### 5. Error Handling
- Use `Result<Self, String>` for constructor validation
- Validate input parameters (array_len > 0, base > min, etc.)
- Handle overflow cases in mathematical calculations

### Java Wrapper Suitability
- **Suitable**: ✅ Yes, concrete class with clear public interface
- **Wrapper Location**: `java_wrapper/src/util/virtuallist/TupleWithMinWrapper.java`
- **Required Methods**: Constructor, get, size, main (for testing)

### Testing Strategy
- **Rust Tests**: Add to `tests/util/long_list_tests.rs`
- **Python Tests**: Add to `python/uacalc/tests/test_long_list.py`
- **Java Wrapper Tests**: Add to `LongListWrapper.java` or create separate wrapper
- **Test Cases**: Basic functionality, edge cases, error conditions, mathematical correctness

### Implementation Priority
1. **High Priority**: Core functionality (constructor, get, size)
2. **Medium Priority**: Error handling and validation
3. **Low Priority**: Performance optimizations

### Key Implementation Notes
- The algorithm is mathematically complex and must match Java exactly
- Partial sums calculation is critical for correct tuple generation
- Stage-based tuple generation requires careful implementation
- Must handle large numbers without overflow
- Thread safety is important for parallel processing

### Expected Challenges
1. **Mathematical Accuracy**: Complex algorithm must match Java exactly
2. **Overflow Handling**: Large number calculations need careful handling
3. **Performance**: Algorithm should be efficient for large datasets
4. **Testing**: Comprehensive testing against Java ground truth

### Success Metrics
- All tests pass against Java implementation
- Performance matches or exceeds Java version
- Memory usage is reasonable
- Code is maintainable and well-documented
