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

## Task 60: Translate `AlgebraWithGeneratingVector`

**Java File:** `org/uacalc/alg/AlgebraWithGeneratingVector.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::AlgebraWithGeneratingVector`  
**Dependencies:** 7 (7 non-UI/example)  
**Estimated Public Methods:** 9

### Description
Translate the Java class `org.uacalc.alg.AlgebraWithGeneratingVector` to Rust with Python bindings.

### Java Class Analysis
- **Type**: Concrete class implementing `Comparable<AlgebraWithGeneratingVector>`
- **Purpose**: Represents an algebra with an associated vector of elements that generates it
- **Key Features**: Allows repeats in generating vector, supports subdirect decomposition
- **Usage**: Used in `FreeAlgebra` for subdirect decomposition and `ProgressReport` as witness algebra

### Dependencies
This class depends on:
- `org.uacalc.alg.SmallAlgebra` - Core dependency (field type)
- `org.uacalc.alg.QuotientAlgebra` - Used in `siDecompose` method
- `org.uacalc.alg.conlat` - Used for congruence lattice operations
- `org.uacalc.alg.sublat` - Used for subalgebra lattice operations
- `org.uacalc.eq` - Used for `Equation` class
- `org.uacalc.terms` - Used for `Variable` class
- `org.uacalc.util` - Used for `ArrayString.toString()`

### Rust Implementation Recommendations

#### 1. Struct Design
```rust
pub struct AlgebraWithGeneratingVector {
    pub alg: SmallAlgebra,
    pub gens_vector: Vec<i32>,
}
```

#### 2. Trait Implementations
- `PartialEq` and `Eq` - Based on `equals()` method logic
- `PartialOrd` and `Ord` - Based on `compareTo()` method logic  
- `Display` - Based on `toString()` method
- `Debug` - For debugging support

#### 3. Method Organization
**Instance Methods:**
- `new(alg: SmallAlgebra, vec: Vec<i32>) -> Self` - Constructor
- `get_algebra(&self) -> &SmallAlgebra` - Getter
- `get_vector(&self) -> &[i32]` - Getter
- `is_image_of(&self, other: &AlgebraWithGeneratingVector) -> bool` - Image check
- `to_string(&self) -> String` - String representation

**Static Methods:**
- `si_decompose(alg: &SmallAlgebra, vec: &[i32]) -> Vec<Self>` - Decomposition (2 overloads)

#### 4. Error Handling
- Use `Result<T, String>` for methods that can fail
- Provide both `_safe` and `_panic` versions of methods
- Handle null checks with `Option<T>` where appropriate

#### 5. Dependencies Required
- `SmallAlgebra` - Must be implemented first (core dependency)
- `QuotientAlgebra` - Must be implemented first (used in `si_decompose`)
- `conlat` module - For congruence lattice operations
- `sublat` module - For subalgebra lattice operations
- `eq` module - For `Equation` class
- `terms` module - For `Variable` class
- `util` module - For `ArrayString.toString()`

### Java Wrapper Suitability
**SUITABLE** - This is a concrete class with clear public methods that can be easily wrapped for testing.

### Testing Strategy
1. **Unit Tests** - Test all public methods with various inputs
2. **Integration Tests** - Test with real algebra instances
3. **Cross-Language Tests** - Compare Rust/Python results with Java wrapper
4. **Edge Cases** - Test with empty vectors, null algebras, etc.

### Implementation Steps

1. **Prerequisites**
   - Implement `SmallAlgebra` (Task 55)
   - Implement `QuotientAlgebra` (Task 77)
   - Implement `conlat` module (congruence lattice)
   - Implement `sublat` module (subalgebra lattice)
   - Implement `eq` module (equations)
   - Implement `terms` module (variables)
   - Implement `util` module (ArrayString)

2. **Implement Rust Code**
   - Create `src/alg/algebra_with_generating_vector.rs`
   - Implement struct with proper field visibility
   - Implement all trait methods (Eq, PartialEq, Ord, PartialOrd, Display, Debug)
   - Implement instance methods
   - Implement static methods
   - Add comprehensive documentation

3. **Create Python Bindings**
   - Add PyO3 bindings in `uacalc_lib/src/alg.rs`
   - Expose all public methods
   - Implement Python magic methods (`__str__`, `__repr__`, `__eq__`, `__hash__`)
   - Use clean export names (no Py prefix)

4. **Create Java CLI Wrapper**
   - Create `java_wrapper/src/alg/AlgebraWithGeneratingVectorWrapper.java`
   - Implement all public methods as CLI commands
   - Handle constructor parameters and return values
   - Output results in JSON format

5. **Write Tests**
   - Rust unit tests for all methods
   - Python integration tests
   - Cross-language comparison tests
   - Edge case testing

### Acceptance Criteria
- [ ] All 9 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] All dependencies properly implemented first
