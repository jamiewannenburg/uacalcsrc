# Algebra Loading Patterns - Implementation Summary

## Overview

Added comprehensive algebra loading patterns and utilities to streamline testing with loaded algebras across the UACalc Python test suite.

## What Was Added

### 1. Updated IMPLEMENTATION_PATTERNS.md

**Section 5: Test Utilities and Algebra Loading**

Added comprehensive documentation covering:

#### Algebra Loading Patterns
- Direct algebra loading with `AlgebraReader`
- Reusable helper function pattern
- Skipping tests when algebras are missing
- Testing with multiple algebras
- Parameterized tests with algebras

#### Code Examples
```python
# Simple loading
def load_test_algebra(name: str, skip_if_missing: bool = True):
    """Load a test algebra from resources/algebras/"""
    if not name.endswith('.ua'):
        name = f"{name}.ua"
    
    algebra_path = f"resources/algebras/{name}"
    
    if not os.path.exists(algebra_path):
        if skip_if_missing:
            pytest.skip(f"Algebra file {algebra_path} not found")
        else:
            raise FileNotFoundError(f"Algebra file {algebra_path} not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(algebra_path)
    return reader.read_algebra_file()
```

#### Available Test Algebras
Documented standard test algebras in `resources/algebras/`:
- `cyclic2.ua` - 2-element cyclic group
- `cyclic3.ua` - 3-element cyclic group  
- `n5.ua` - 5-element lattice (pentagon)
- `m3.ua` - 3-element lattice (diamond)

#### Testing Patterns
- **Skip on missing**: Tests gracefully skip if algebra files not found
- **Multiple algebras**: Test same operation across different algebras
- **Parameterized tests**: Use pytest parameterization for algebra variations
- **Fixtures**: Reusable pytest fixtures for common algebras

### 2. Enhanced conftest.py

**Location**: `python/uacalc/tests/conftest.py`

Added algebra loading infrastructure:

#### Helper Function
```python
def load_test_algebra(name: str, skip_if_missing: bool = True):
    """Load a test algebra from resources/algebras/"""
    # Implementation handles .ua extension, file checking, skipping
```

#### Pytest Fixtures
Added 6 new fixtures:

1. **`cyclic2_algebra`** - Fixture for 2-element cyclic group
2. **`cyclic3_algebra`** - Fixture for 3-element cyclic group
3. **`n5_algebra`** - Fixture for 5-element pentagon lattice
4. **`m3_algebra`** - Fixture for 3-element diamond lattice
5. **`test_algebra`** - Parameterized fixture (runs test with cyclic2, cyclic3, n5)
6. **`algebra_loader`** - Fixture that returns the loading function

#### Usage Examples
```python
# Using specific algebra fixture
def test_with_cyclic3(cyclic3_algebra):
    alg = cyclic3_algebra
    # Test with algebra

# Using parameterized fixture (runs 3 times)
def test_multiple_algebras(test_algebra):
    alg = test_algebra  # cyclic2, then cyclic3, then n5
    # Test with each algebra

# Using loader fixture
def test_custom_algebra(algebra_loader):
    alg = algebra_loader("custom_algebra")
    # Test with loaded algebra
```

### 3. Example Test File

**Location**: `python/uacalc/tests/test_algebra_loading_example.py`

Comprehensive example demonstrating all patterns:

#### Test Classes

1. **`TestAlgebraLoadingPatterns`** (unittest)
   - Direct algebra loading
   - Using helper function
   - Testing multiple algebras
   - Loading in `setUpClass`

2. **`TestWithPytestFixtures`** (pytest)
   - Using specific algebra fixtures
   - Using parameterized fixture
   - Using loader fixture

3. **`TestAdvancedPatterns`** (pytest)
   - Custom algebra paths
   - Testing algebra operations
   - Error handling

#### Example Tests

```python
class TestAlgebraLoadingPatterns(unittest.TestCase):
    def test_direct_algebra_loading(self):
        """Example: Direct algebra loading with skip on missing."""
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Use algebra for testing
        self.assertIsNotNone(alg)
    
    def test_with_helper_function(self):
        """Example: Using load_test_algebra helper."""
        from conftest import load_test_algebra
        
        alg = load_test_algebra("cyclic2")
        # Test with algebra

# Parameterized tests
@pytest.mark.parametrize("algebra_name", ["cyclic2", "cyclic3", "n5"])
def test_variable_evaluation(algebra_name, algebra_loader):
    """Example: Test across algebras."""
    alg = algebra_loader(algebra_name)
    
    VariableImp = uacalc_lib.terms.VariableImp
    x = VariableImp("x")
    
    result = x.eval(alg, {"x": 0})
    assert result == 0
```

## Benefits

### 1. Consistency
- Standardized way to load algebras across all tests
- Consistent error handling and skipping
- Reusable patterns reduce code duplication

### 2. Flexibility
- Multiple loading patterns for different use cases
- Support for both unittest and pytest styles
- Easy to add new test algebras

### 3. Robustness
- Graceful handling of missing algebra files
- Clear error messages when algebras not found
- Tests skip rather than fail when optional algebras missing

### 4. Developer Experience
- Well-documented patterns with examples
- Easy to copy/paste working code
- Comprehensive example file as reference

## Usage in Tests

### Quick Start - Direct Loading
```python
def test_my_operation(self):
    from conftest import load_test_algebra
    
    alg = load_test_algebra("cyclic3")
    # Test with algebra
```

### Quick Start - Using Fixture
```python
def test_my_operation(cyclic3_algebra):
    # cyclic3_algebra is automatically loaded
    # Test with algebra
```

### Quick Start - Multiple Algebras
```python
@pytest.mark.parametrize("name", ["cyclic2", "cyclic3"])
def test_multiple(name, algebra_loader):
    alg = algebra_loader(name)
    # Test runs twice, once for each algebra
```

## Files Modified/Created

### Modified
1. **IMPLEMENTATION_PATTERNS.md**
   - Added Section 5: Test Utilities and Algebra Loading
   - Updated section numbering (5→6, 6→7, etc.)
   - Added comprehensive algebra loading documentation

2. **python/uacalc/tests/conftest.py**
   - Added `load_test_algebra` helper function
   - Added 6 algebra-related fixtures
   - Updated exports in `__all__`

### Created
1. **python/uacalc/tests/test_algebra_loading_example.py**
   - Comprehensive example tests
   - Multiple test classes showing different patterns
   - Parameterized test examples
   - Error handling examples

2. **ALGEBRA_LOADING_PATTERNS_SUMMARY.md** (this file)
   - Documentation of what was added
   - Usage examples
   - Benefits and patterns

## Integration with Existing Tests

The new patterns integrate seamlessly with existing tests:

### Existing test_terms.py
Already uses direct loading pattern - can be refactored to use helpers:

**Before:**
```python
def test_variable_eval(self):
    algebra_path = "resources/algebras/cyclic3.ua"
    if not os.path.exists(algebra_path):
        self.skipTest(f"Algebra file {algebra_path} not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(algebra_path)
    alg = reader.read_algebra_file()
    # ... test code
```

**After:**
```python
def test_variable_eval(self):
    from conftest import load_test_algebra
    
    alg = load_test_algebra("cyclic3")
    # ... test code
```

Or even simpler with fixtures:
```python
def test_variable_eval(cyclic3_algebra):
    alg = cyclic3_algebra
    # ... test code
```

## Future Work

### Potential Enhancements
1. Add more algebra fixtures as needed (cyclic4, cyclic5, etc.)
2. Create fixtures for specific algebra types (lattices, groups, etc.)
3. Add algebra factory functions for generating test algebras
4. Cache loaded algebras to improve test performance
5. Add algebra validation utilities

### Documentation
- Add to README with examples
- Create tutorial for testing with algebras
- Document available test algebras and their properties

## Testing the Patterns

The example file serves as both documentation and tests:

```bash
# Run all example tests
pytest python/uacalc/tests/test_algebra_loading_example.py -v

# Run specific test class
pytest python/uacalc/tests/test_algebra_loading_example.py::TestAlgebraLoadingPatterns -v

# Run parameterized tests
pytest python/uacalc/tests/test_algebra_loading_example.py::test_algebra_size -v
```

## Summary

✅ **IMPLEMENTATION_PATTERNS.md** updated with comprehensive algebra loading patterns  
✅ **conftest.py** enhanced with reusable helpers and fixtures  
✅ **test_algebra_loading_example.py** created as comprehensive reference  
✅ All patterns documented with clear examples  
✅ Multiple usage patterns for different scenarios  
✅ Backward compatible with existing tests  

The algebra loading infrastructure is now standardized, well-documented, and ready for use across all Python tests in the UACalc project.

