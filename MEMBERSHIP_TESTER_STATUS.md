# MembershipTester Implementation Status

This document describes the status of implementing the `MembershipTester.java` example in Rust and Python, and compares outputs with the Java version.

## Overview

The `MembershipTester.java` example:
1. Loads two algebras (n5.ua and m3.ua)
2. Finds an equation that holds in alg0 (n5) but fails in alg1 (m3) using `FreeAlgebra.findEquationOfAnotB`
3. Tests the equation in both algebras using `findFailureMap`

## Test Files Created

1. **Rust Test**: `tests/membership_tester_test.rs`
2. **Python Test**: `python/uacalc/tests/test_membership_tester.py`
3. **Java Test Version**: `java_wrapper/src/org/uacalc/example/MembershipTesterTest.java` (with corrected paths)

## Current Status

### Java Implementation

**Known Issues:**
- The Java code has a bug: it doesn't check if `report` is null before calling `report.addLine()` at line 338 in `FreeAlgebra.java`
- This causes a `NullPointerException` when running the test version

**Expected Behavior (if bug were fixed):**
1. Should load n5.ua and m3.ua successfully
2. Should find an equation holding in n5 but failing in m3
3. Should print the equation
4. Should show failure map in m3 (not null)
5. Should show null failure in n5

### Rust Implementation

**Current Output:**
```
pass: 0, size: 3
eq is null (alg1 is in V(alg0))
```

**Status:** The Rust implementation currently returns `None` (no equation found), which indicates incomplete implementation.

**Python Output:**
```
Constructing free algebra on 3 generators over n5
pass: 0, size: 3
pass: 0, size: 3
done constructing free algebra, size = 3
Loaded alg0: n5 (size: 5)
Loaded alg1: m3 (size: 5)

Finding equation...
eq is null (alg1 is in V(alg0))
```

**Status:** The Python implementation successfully loads algebras and calls the Rust implementation, but gets `None` result due to incomplete Rust implementation.

**What Works:**
- ✅ Loading algebra files (`read_algebra_file`)
- ✅ Creating FreeAlgebra
- ✅ Calling `find_equation_of_a_not_b` (returns `Ok(None)`)

**What's Missing:**
1. ❌ `Closer::set_image_algebra` - Not implemented (commented out at line 806 in `free_algebra.rs`)
2. ❌ `Closer::set_homomorphism` - Not implemented (commented out at line 807 in `free_algebra.rs`)
3. ❌ `Closer::get_failing_equation` - Not implemented (commented out at line 814 in `free_algebra.rs`)

These are the critical methods needed for `find_equation_of_a_not_b` to work properly.

### Python Implementation

**Current Status:** The Python bindings have a stub implementation that returns `None`.

**What Works:**
- ✅ Loading algebra files (`uacalc_lib.io.read_algebra_file`)
- ✅ Creating FreeAlgebra objects

**What's Missing:**
1. ❌ `FreeAlgebra.find_equation_of_a_not_b` static method - Currently returns `None` (line 159 in `uacalc_lib/src/alg/free_algebra.rs`)
2. The Python bindings depend on the Rust implementation being complete

## Required Implementation Steps

### For Rust (`src/alg/closer.rs`):

1. **Implement `set_image_algebra`:**
   ```rust
   pub fn set_image_algebra(&mut self, alg: Arc<dyn SmallAlgebra<UniverseItem = T>>) -> Result<(), String> {
       // Verify similarity type matches
       // Set self.image_algebra
   }
   ```

2. **Implement `set_homomorphism`:**
   ```rust
   pub fn set_homomorphism(&mut self, b_gens: Vec<i32>) -> Result<(), String> {
       // Create map from generators to b_gens values
       // Set self.homomorphism
   }
   ```

3. **Implement `get_failing_equation`:**
   ```rust
   pub fn get_failing_equation(&self) -> Option<Equation> {
       // Return self.failing_equation
   }
   ```

4. **Update `sg_close` to detect failures:**
   - The `sg_close` method needs to check for homomorphism conflicts
   - When a conflict is found, set `self.failing_equation`
   - This matches the Java implementation in `Closer.java` (lines 498-515)

### For Python Bindings (`uacalc_lib/src/alg/free_algebra.rs`):

1. **Implement the static method properly:**
   - Convert Python `PyBasicSmallAlgebra` to Rust `Box<dyn SmallAlgebra>`
   - Call the Rust `find_equation_of_a_not_b` method
   - Convert result back to Python `PyEquation`

## Test Results Summary

| Implementation | Can Load Files | Can Find Equation | Can Test Equation | Status |
|---------------|----------------|-------------------|-------------------|--------|
| Java | ✅ | ❌ (bug: NPE) | ✅ | Needs bug fix |
| Rust | ✅ | ❌ (incomplete) | ✅ | Needs implementation |
| Python | ✅ | ❌ (incomplete) | ✅ | Depends on Rust |

## Next Steps

1. **Fix Java bug:** Add null check for `report` in `FreeAlgebra.java:338`
2. **Implement Rust Closer methods:** Add `set_image_algebra`, `set_homomorphism`, and `get_failing_equation`
3. **Update Rust sg_close:** Add failure detection logic during closure
4. **Update Python bindings:** Properly implement `find_equation_of_a_not_b` static method
5. **Re-run tests:** Verify all three implementations produce matching output

## Files Modified

- `tests/membership_tester_test.rs` - New Rust test
- `python/uacalc/tests/test_membership_tester.py` - New Python test
- `tests/mod.rs` - Added module
- `java_wrapper/src/org/uacalc/example/MembershipTesterTest.java` - Java test with corrected paths (moved from org/uacalc/example/)

