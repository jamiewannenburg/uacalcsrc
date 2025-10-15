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

## Task 50: Translate `Operations`

**Java File:** `org/uacalc/alg/op/Operations.java`  
**Package:** `org.uacalc.alg.op`  
**Rust Module:** `alg::op::Operations`  
**Dependencies:** 15 (12 non-UI/example)  
**Estimated Public Methods:** ~76

### Description
Translate the Java class `org.uacalc.alg.op.Operations` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Concrete utility class with static methods
- **Purpose**: Factory class for creating and testing operations
- **Key Features**: 
  - 76+ public static methods for operation creation and testing
  - Factory methods for various operation types
  - Property testing methods (commutative, associative, etc.)
  - Script-based operation creation using Groovy

### Dependencies
This class depends on:
- `org.uacalc.alg.conlat.BasicPartition` (Task 5) - ❌ **PENDING**
- `org.uacalc.util.*` (Multiple utility classes):
  - `ArrayString` (Task 6) ✅ **COMPLETED**
  - `ArrayIncrementor` (Task 4) - ❌ **PENDING**
  - `SequenceGenerator` (Task 15) - ❌ **PENDING**
  - `PermutationGenerator` (Task 9) - ❌ **PENDING**
  - `Horner` (Task 3) ✅ **COMPLETED**
  - `IntArray` (Task 23) - ❌ **PENDING**
- `org.uacalc.alg.op.*` (Operation-related classes):
  - `Operation` (Task 12) ✅ **COMPLETED**
  - `OperationSymbol` (Task 1) ✅ **COMPLETED**
  - `AbstractOperation` (Task 11) ✅ **COMPLETED**
  - `OperationWithDefaultValue` (Task 49) - ❌ **PENDING**
  - `SimilarityType` (Task 2) - ❌ **PENDING**
- `org.uacalc.ui.tm.ProgressReport` (UI class - excluded)
- `javax.script.*` (Java Scripting API for Groovy support)

## Rust Implementation Strategy

### Module Structure
- **Rust Module**: `alg::op::operations` (module with free functions)
- **Pattern**: Static utility class → Rust module with free functions
- **Error Handling**: Use `Result<T, String>` for methods that can fail
- **Logging**: Use `log` crate for logging functionality

### Key Implementation Decisions

#### 1. Static Methods → Free Functions
- All 76+ static methods become free functions in the module
- Use `pub fn` for public functions
- Group related functions in submodules if needed

#### 2. Operation Creation Methods
- `makeIntOperation()` → `make_int_operation()`
- `makeRandomOperation()` → `make_random_operation()`
- `makeDerivedOperation()` → `make_derived_operation()`
- Return `Result<Box<dyn Operation>, String>` for error handling

#### 3. Property Testing Methods
- `isCommutative()` → `is_commutative()`
- `isAssociative()` → `is_associative()`
- `isTotallySymmetric()` → `is_totally_symmetric()`
- `isMaltsev()` → `is_maltsev()`
- `isIdempotent()` → `is_idempotent()`

#### 4. Script-Based Operation Creation
- `makeOperationFromScript()` → `make_operation_from_script()`
- **Challenge**: Java uses Groovy scripting engine
- **Solution**: Either implement a simple expression parser or skip this functionality initially
- **Alternative**: Use a Rust scripting library like `rhai` or `mlua`

#### 5. Array and Collection Handling
- Use `Vec<T>` instead of Java arrays
- Use `&[T]` for slice parameters
- Use `HashMap<K, V>` for maps
- Use `Vec<T>` for lists

#### 6. Progress Reporting
- `ProgressReport` is UI-related and excluded
- Use Rust logging or callback functions for progress updates
- Or implement a simple progress trait

### Dependencies Implementation Order
1. **Prerequisites** (must be completed first):
   - Task 1: OperationSymbol ✅ **COMPLETED**
   - Task 3: Horner ✅ **COMPLETED**
   - Task 6: ArrayString ✅ **COMPLETED**
   - Task 2: SimilarityType - ❌ **PENDING**
   - Task 4: ArrayIncrementor - ❌ **PENDING**
   - Task 9: PermutationGenerator - ❌ **PENDING**
   - Task 11: AbstractOperation ✅ **COMPLETED**
   - Task 12: Operation ✅ **COMPLETED**
   - Task 15: SequenceGenerator - ❌ **PENDING**
   - Task 23: IntArray - ❌ **PENDING**
   - Task 49: OperationWithDefaultValue - ❌ **PENDING**

2. **This Task**: Operations (Task 50)

3. **Dependents**: Many classes depend on Operations for operation creation and testing

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

## Critical Implementation Notes

### 1. Script-Based Operation Creation
- **Challenge**: `makeOperationFromScript()` uses Java's Groovy scripting engine
- **Impact**: High - this is a key feature for dynamic operation creation
- **Solutions**:
  - Implement a simple expression parser for basic operations
  - Use Rust scripting libraries (`rhai`, `mlua`, or `pest`)
  - Skip initially and implement later
  - Create a simplified version that handles common patterns

### 2. Progress Reporting
- **Challenge**: `ProgressReport` is UI-related and excluded
- **Impact**: Medium - affects `findDifference()` method
- **Solution**: Use Rust logging or callback functions for progress updates

### 3. Array and Collection Handling
- **Challenge**: Java uses arrays and collections extensively
- **Impact**: High - affects all methods
- **Solution**: Use `Vec<T>` and `&[T]` consistently, implement proper conversions

### 4. Error Handling
- **Challenge**: Java uses exceptions, Rust uses Result
- **Impact**: High - affects all methods
- **Solution**: Use `Result<T, String>` for methods that can fail, implement proper error propagation

### 5. Static Method Organization
- **Challenge**: 76+ static methods in one class
- **Impact**: Medium - affects code organization
- **Solution**: Group related methods in submodules (creation, testing, utilities)

## Testing Strategy

### Java Wrapper Suitability
- **Suitable**: Yes - Operations is a concrete class with static methods
- **Testing Approach**: Test all static methods through CLI commands
- **Key Methods to Test**:
  - Operation creation methods (`makeIntOperation`, `makeRandomOperation`, etc.)
  - Property testing methods (`isCommutative`, `isAssociative`, etc.)
  - Utility methods (`commutes`, `findDifference`, etc.)

### Rust Testing Strategy
- **Unit Tests**: Test each static method individually
- **Integration Tests**: Test method combinations and workflows
- **Property Tests**: Test operation properties with various inputs
- **Performance Tests**: Test with large operations and timeouts

### Python Testing Strategy
- **API Tests**: Test all exposed methods through Python bindings
- **Compatibility Tests**: Compare results with Java implementation
- **Error Handling Tests**: Test error conditions and edge cases

## Acceptance Criteria
- [ ] All 76+ public static methods translated to Rust free functions
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] All dependencies properly handled (12 non-UI dependencies)
- [ ] Script-based operation creation implemented or properly handled
- [ ] Progress reporting implemented or properly handled
- [ ] Array and collection handling properly implemented
- [ ] Error handling properly implemented with Result types
