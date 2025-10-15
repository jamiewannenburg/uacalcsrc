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

## Task 43: Translate `Homomorphism`

**Java File:** `org/uacalc/alg/Homomorphism.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::Homomorphism`  
**Dependencies:** 3 (3 non-UI/example)  
**Estimated Public Methods:** 8

### Description
Translate the Java class `org.uacalc.alg.Homomorphism` to Rust with Python bindings.

### Dependencies
This class depends on:
- `org.uacalc.alg.conlat.Partition` (Task 5 - completed)
- `org.uacalc.util.IntArray` (Task 23 - completed)  
- `org.uacalc.alg.SmallAlgebra` (Task 41 - ✅ **COMPLETED**)

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

### Java Class Analysis

**Class Type:** Concrete class  
**Purpose:** Represents a homomorphism from domain algebra to range algebra  
**Key Features:** Kernel computation, product homomorphism construction, element mapping  
**Public Methods:** 8 methods including constructors, getters/setters, kernel computation, and static utility

**Method Analysis:**
- `Homomorphism(SmallAlgebra, SmallAlgebra, Map<Integer,Integer>)` - Constructor
- `kernel()` - Computes kernel partition using BasicPartition.zero()
- `productHomo(List<Homomorphism>)` - Static method creating product homomorphism
- `getDomain()`, `setDomain(SmallAlgebra)` - Domain algebra accessors
- `getRange()`, `setRange(SmallAlgebra)` - Range algebra accessors  
- `getMap()`, `setMap(Map<Integer,Integer>)` - Mapping accessors
- `toString()` - String representation

**Dependencies Analysis:**
- `org.uacalc.alg.conlat.Partition` - Used in kernel() method via BasicPartition.zero()
- `org.uacalc.util.IntArray` - Used in productHomo() static method
- `org.uacalc.alg.SmallAlgebra` - Domain and range algebra types
- `java.util.Map<Integer,Integer>` - Internal mapping representation
- `java.util.List<Homomorphism>` - Product homomorphism parameter

### Rust Implementation Recommendations

#### 1. Struct Design
```rust
/// Homomorphism from domain algebra to range algebra
pub struct Homomorphism {
    domain: SmallAlgebra,
    range: SmallAlgebra, 
    map: HashMap<usize, usize>,
}
```

#### 2. Method Translation
- **Constructor**: `new(domain: SmallAlgebra, range: SmallAlgebra, map: HashMap<usize, usize>) -> Result<Self, String>`
- **Kernel**: `kernel(&self) -> Result<Partition, String>` - Uses BasicPartition::zero()
- **Product**: `product_homo(homomorphisms: &[Homomorphism]) -> Result<Vec<IntArray>, String>` - Static method
- **Accessors**: Standard getter/setter methods with proper error handling
- **Display**: Implement `Display` trait for string representation

#### 3. Error Handling
- Use `Result<T, String>` for methods that can fail
- Validate domain/range compatibility in constructor
- Handle empty homomorphism lists in product_homo
- Provide both safe and panic versions of methods

#### 4. Generic Considerations
- Use `usize` instead of `Integer` for indices (Rust convention)
- Use `HashMap<usize, usize>` instead of `Map<Integer, Integer>`
- Use `Vec<IntArray>` instead of `List<IntArray>`

### Python Bindings Strategy
- Expose as `Homomorphism` class with clean API
- Use `PyResult<T>` for error handling
- Implement Python magic methods (`__str__`, `__repr__`, `__eq__`)
- Handle `HashMap` serialization for Python access

### Java Wrapper Suitability
**Status:** ✅ **SUITABLE** - Concrete class with clear public interface
- Can instantiate with test data
- All methods can be called directly
- Static method `productHomo` can be tested
- Kernel computation can be verified

### Testing Strategy
1. **Unit Tests**: Test all 8 public methods with various inputs
2. **Integration Tests**: Test with different algebra types and mappings
3. **Edge Cases**: Empty mappings, invalid domains, kernel computation
4. **Cross-Language**: Compare Rust/Python results with Java wrapper
5. **Performance**: Test kernel computation with large algebras

### Implementation Order
1. **Prerequisites**: Complete SmallAlgebra (Task 41) first
2. **Core Implementation**: Implement Homomorphism struct and methods
3. **Python Bindings**: Add PyO3 bindings with error handling
4. **Java Wrapper**: Create CLI wrapper for testing
5. **Testing**: Comprehensive test suite with cross-language validation

### Critical Implementation Notes
- **Kernel Algorithm**: Must match Java implementation exactly using BasicPartition.zero()
- **Product Method**: Static method that creates IntArray elements from homomorphism list
- **Memory Management**: Use owned types for domain/range algebras
- **Error Propagation**: Proper Result handling throughout the call chain
- **Documentation**: Include mathematical definitions and usage examples

### Acceptance Criteria
- [ ] All 8 public methods translated to Rust
- [ ] Python bindings expose all public methods with proper error handling
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Kernel computation matches Java implementation exactly
- [ ] Product homomorphism method works correctly
- [ ] Code compiles without warnings
- [ ] Documentation complete with mathematical context
- [ ] SmallAlgebra dependency completed (Task 41)
