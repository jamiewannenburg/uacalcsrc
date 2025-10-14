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

## Task 3: Translate `Horner` ✅ COMPLETED

**Java File:** `org/uacalc/util/Horner.java`  
**Package:** `org.uacalc.util`  
**Rust Module:** `util::horner`  
**Dependencies:** 1 (ArrayString - used only in main method for testing)  
**Public Methods:** 8 static methods

### Description
Translate the Java class `org.uacalc.util.Horner` to Rust with Python bindings.

### Java Class Analysis
- **Type:** Final utility class with static methods only
- **Purpose:** Horner encoding/decoding for direct products of algebras
- **Pattern:** Static utility class (no instantiation needed)
- **Key Methods:**
  - `horner(int[], int[])` - Encode with variable sizes
  - `hornerInv(int, int[])` - Decode with variable sizes  
  - `horner(int[], int)` - Encode with same size
  - `hornerInv(int, int, int)` - Decode with same size
  - `horner(Integer[], int)` - Encode Integer arrays
  - `reverseArray(int[])` - Array reversal utility
  - `leftRightReverse(int[], int, int)` - Complex transformation

### Dependencies Analysis
- **Direct Dependencies:** ArrayString (used only in main method for testing)
- **Usage Pattern:** Widely used across UACalc for encoding/decoding operations
- **Dependency Status:** ✅ ArrayString already translated (Task 6)

### Rust Implementation Analysis
- **Rust Construct:** Module with free functions (no struct needed)
- **Pattern:** Static utility functions matching Java static methods
- **Error Handling:** Both panic and safe versions provided
- **Memory Management:** Uses Vec<i32> for arrays, proper ownership
- **Performance:** Uses wrapping arithmetic for compatibility

### Implementation Status
- ✅ **Rust Implementation:** Complete in `src/util/horner.rs`
- ✅ **Python Bindings:** Complete in `uacalc_lib/src/util.rs` (PyHorner)
- ✅ **Java Wrapper:** Complete in `java_wrapper/src/util/HornerWrapper.java`
- ✅ **Rust Tests:** Complete in `tests/horner_tests.rs` (16 tests)
- ✅ **Python Tests:** Complete in `python/uacalc/tests/test_horner.py` (25 tests)
- ✅ **Documentation:** Complete with examples and error handling

### Verification Results
- ✅ All Rust tests pass (16/16)
- ✅ All Python tests pass (25/25) 
- ✅ Java wrapper functional and tested
- ✅ Cross-language behavior matches exactly
- ✅ Error handling works correctly
- ✅ Performance tests pass with timeouts
- ✅ Round-trip encoding/decoding verified

### Implementation Recommendations
1. **Rust Design:** Module with free functions is correct for static utility class
2. **Error Handling:** Both panic and safe versions provide flexibility
3. **Python API:** Clean static methods exposed through PyHorner class
4. **Testing:** Comprehensive test coverage with Java comparison
5. **Documentation:** Well-documented with examples and error conditions

### Acceptance Criteria
- [x] All public methods translated to Rust
- [x] Python bindings expose all public methods
- [x] Java CLI wrapper created with all public methods
- [x] Rust tests pass with timeouts enabled
- [x] Python tests pass and match Java output
- [x] Code compiles without warnings
- [x] Documentation complete
