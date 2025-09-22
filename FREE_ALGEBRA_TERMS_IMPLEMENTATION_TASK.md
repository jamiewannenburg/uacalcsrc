# Free Algebra Terms Implementation Task

## Overview

This document outlines the missing functionality needed to complete the Rust/Python implementation of free algebra terms functionality to mirror the Java library. The goal is to implement the same methods and behavior as the Java `org.uacalc.alg.FreeAlgebra` and `org.uacalc.alg.SubProductAlgebra` classes.

## Current Status

### ✅ Implemented
- Basic free algebra creation in Rust (`uacalc-core/src/free_algebra.rs`)
- Python wrapper for free algebra creation (`uacalc-py/src/lib.rs`)
- JavaWrapper commands for free algebra terms (`scripts/JavaWrapper.java`)
- Test framework for comparing implementations (`tests/python/test_free_algebra_compatibility.py`)
- Tests that attempt to call missing methods and handle failures gracefully

### ❌ Missing Implementation

**Note**: The tests are designed to fail gracefully when trying to access missing methods. This is the expected behavior until the implementation is complete.

## 1. Rust Core Implementation (`uacalc-core/src/free_algebra.rs`)

### Missing Methods

#### `get_variables()` - Mirror Java `getVariables()`
**Java Reference**: `org.uacalc.alg.SubProductAlgebra.getVariables()` (lines 339-341)
```java
public List<Variable> getVariables() {
    if (variables != null) return variables;
    if (terms == null) return null;
    // Implementation details...
}
```

**Rust Implementation Needed**:
```rust
impl FreeAlgebra {
    pub fn get_variables(&self) -> UACalcResult<Vec<Variable>> {
        // Return the list of variables (generators) used in the free algebra
        // Should return variables corresponding to the generators
    }
}
```

#### `get_term_map()` - Mirror Java `getTermMap()`
**Java Reference**: `org.uacalc.alg.SubProductAlgebra.getTermMap()` (lines 359-361)
```java
public Map<IntArray,Term> getTermMap() {
    return termMap;
}
```

**Rust Implementation Needed**:
```rust
impl FreeAlgebra {
    pub fn get_term_map(&self) -> HashMap<usize, TermId> {
        // Return mapping from universe elements to terms
        // Should map each element index to its corresponding term
    }
}
```

#### `get_term(element)` - Mirror Java `getTerm(IntArray elt)`
**Java Reference**: `org.uacalc.alg.SubProductAlgebra.getTerm()` (lines 354-357)
```java
public Term getTerm(IntArray elt) {
    if (getTerms() == null) return null;
    return getTerms()[getUniverseOrder().get(elt).intValue()];
}
```

**Rust Implementation Needed**:
```rust
impl FreeAlgebra {
    pub fn get_term(&self, element_index: usize) -> UACalcResult<TermId> {
        // Return the term corresponding to a specific element
        // Should return the term at the given element index
    }
}
```

#### `get_element_from_term(term)` - Mirror Java `getElementFromTerm(Term t)`
**Java Reference**: `org.uacalc.alg.SubProductAlgebra.getElementFromTerm()` (lines 401-416)
```java
public IntArray getElementFromTerm(Term t) {
    final Term[] terms = getTerms();
    final int size = terms.length;
    int i = 0;
    for ( ; i < size; i++) {
        if (terms[i].equals(t)) break;
    }
    // Return corresponding element...
}
```

**Rust Implementation Needed**:
```rust
impl FreeAlgebra {
    pub fn get_element_from_term(&self, term_id: TermId) -> UACalcResult<usize> {
        // Return the element index corresponding to a specific term
        // Should find the term in the terms list and return its index
    }
}
```

#### `get_variable_to_generator_map()` - Mirror Java `getVariableToGeneratorMap()`
**Java Reference**: `org.uacalc.alg.SubProductAlgebra.getVariableToGeneratorMap()` (lines 325-327)
```java
public Map<Variable,IntArray> getVariableToGeneratorMap() {
    return varsMap;
}
```

**Rust Implementation Needed**:
```rust
impl FreeAlgebra {
    pub fn get_variable_to_generator_map(&self) -> HashMap<usize, usize> {
        // Return mapping from variables to generator indices
        // Should map variable indices to their corresponding generator indices
    }
}
```

## 2. Python Wrapper Implementation (`uacalc-py/src/lib.rs`)

### Missing Methods in PyFreeAlgebra

#### `get_terms()` - Expose Rust `get_terms()`
**Current Status**: Rust method exists but not exposed in Python wrapper

**Implementation Needed**:
```rust
#[pymethods]
impl PyFreeAlgebra {
    fn get_terms(&self) -> PyResult<Vec<PyTerm>> {
        let terms = self.inner.get_terms();
        // Convert TermId to PyTerm objects
        // Return list of PyTerm objects
    }
}
```

#### `get_variables()` - Expose Rust `get_variables()`
**Implementation Needed**:
```rust
#[pymethods]
impl PyFreeAlgebra {
    fn get_variables(&self) -> PyResult<Vec<PyVariable>> {
        let variables = self.inner.get_variables()?;
        // Convert to PyVariable objects
        // Return list of PyVariable objects
    }
}
```

#### `get_term(element_index)` - Expose Rust `get_term()`
**Implementation Needed**:
```rust
#[pymethods]
impl PyFreeAlgebra {
    fn get_term(&self, element_index: usize) -> PyResult<PyTerm> {
        let term_id = self.inner.get_term(element_index)?;
        // Convert TermId to PyTerm
        // Return PyTerm object
    }
}
```

#### `get_element_from_term(term)` - Expose Rust `get_element_from_term()`
**Implementation Needed**:
```rust
#[pymethods]
impl PyFreeAlgebra {
    fn get_element_from_term(&self, term: &PyTerm) -> PyResult<usize> {
        let element_index = self.inner.get_element_from_term(term.inner)?;
        Ok(element_index)
    }
}
```

#### `get_idempotent_terms()` - Expose Rust `get_idempotent_terms()`
**Current Status**: Rust method exists but not exposed in Python wrapper

**Implementation Needed**:
```rust
#[pymethods]
impl PyFreeAlgebra {
    fn get_idempotent_terms(&self) -> PyResult<Vec<PyTerm>> {
        let idempotent_terms = self.inner.get_idempotent_terms()?;
        // Convert TermId to PyTerm objects
        // Return list of PyTerm objects
    }
}
```

## 3. JavaWrapper Implementation (`scripts/JavaWrapper.java`)

### Missing Commands

#### `free_algebra_idempotent_terms` - Mirror Java `getIdempotentTerms()`
**Java Reference**: `org.uacalc.alg.FreeAlgebra.getIdempotentTerms()` (lines 347-362)

**Implementation Needed**:
```java
case "free_algebra_idempotent_terms":
    if (args.length < 3) {
        System.err.println("Usage: JavaWrapper free_algebra_idempotent_terms <ua_file> <generators_json> <variety_constraints_json>");
        System.exit(1);
    }
    outputFreeAlgebraIdempotentTerms(args[1], args[2], args[3]);
    break;

private static void outputFreeAlgebraIdempotentTerms(String uaFile, String generatorsJson, String varietyConstraintsJson) throws Exception {
    // Load algebra, create free algebra, call getIdempotentTerms()
    // Return JSON with idempotent terms information
}
```

#### `free_algebra_term_map` - Mirror Java `getTermMap()`
**Implementation Needed**:
```java
case "free_algebra_term_map":
    // Similar structure to existing commands
    // Return mapping from elements to terms
```

## 4. Test Implementation (`tests/python/test_free_algebra_compatibility.py`)

### Current Test Status
- ✅ Basic structure exists
- ✅ Tests attempt to call missing methods (will fail as expected)
- ✅ Comparison framework in place

### Test Behavior
The tests are designed to:
1. Try to call the missing methods on both Rust and Java implementations
2. Handle failures gracefully (expected for unfinished implementation)
3. Compare results when both implementations are available
4. Log differences appropriately

**Current Test Status**: All tests pass because they handle missing method failures gracefully. The tests attempt to access methods like `free_algebra.inner.get_terms()` which fail as expected since:
- The `inner` attribute is not accessible from Python (security feature)
- The methods are not yet exposed in the Python wrapper
- The tests catch these exceptions and log them as expected failures

## Implementation Priority

### Phase 1: Core Rust Methods
1. `get_variables()` - Essential for term functionality
2. `get_term_map()` - Core mapping functionality
3. `get_term(element)` - Element to term lookup
4. `get_element_from_term(term)` - Term to element lookup

### Phase 2: Rust Test Methods
1. Make rust tests for these methods, ensuring memory cap works

### Phase 3: Python Wrapper Exposure
1. Expose all Phase 1 methods in PyFreeAlgebra
2. Create PyTerm and PyVariable classes if needed
3. Ensure proper error handling and type conversion

### Phase 4: JavaWrapper Commands
1. Add `free_algebra_idempotent_terms` command
2. Add `free_algebra_term_map` command
3. Ensure JSON output format matches existing patterns

### Phase 5: Test Completion
1. Update tests to use exposed methods
2. Verify all test cases pass
3. Add additional edge case testing

## Key Java Files for Reference

### Primary Implementation Files
- `org/uacalc/alg/FreeAlgebra.java` - Main free algebra implementation
- `org/uacalc/alg/SubProductAlgebra.java` - Base class with term methods
- `org/uacalc/terms/Term.java` - Term interface and implementation
- `org/uacalc/terms/Variable.java` - Variable implementation

### Key Methods to Mirror
- `FreeAlgebra.getIdempotentTerms()` (lines 347-362)
- `SubProductAlgebra.getTerms()` (lines 329-331)
- `SubProductAlgebra.getVariables()` (lines 339-341)
- `SubProductAlgebra.getTerm(IntArray)` (lines 354-357)
- `SubProductAlgebra.getTermMap()` (lines 359-361)
- `SubProductAlgebra.getElementFromTerm(Term)` (lines 401-416)
- `SubProductAlgebra.getVariableToGeneratorMap()` (lines 325-327)

## Notes

- The Rust implementation already has the core `get_terms()` and `get_idempotent_terms()` methods
- The main work is exposing these in the Python wrapper and adding missing methods
- The JavaWrapper commands are straightforward additions following existing patterns
- Tests are designed to fail gracefully until implementation is complete
- All implementations should maintain the same JSON output format for compatibility

## Testing

Run the tests with:
```bash
python -m pytest tests/python/test_free_algebra_compatibility.py::FreeAlgebraCompatibilityTest::test_free_algebra_terms_from_small_algebras_compatibility -v
python -m pytest tests/python/test_free_algebra_compatibility.py::FreeAlgebraCompatibilityTest::test_free_algebra_idempotent_terms_compatibility -v
```

Expected behavior: Tests should run and log expected failures until implementation is complete.
