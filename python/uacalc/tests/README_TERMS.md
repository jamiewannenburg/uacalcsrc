# Term Evaluation Tests

## Overview

This directory contains comprehensive tests for term evaluation in the UACalc Python bindings.

## Running the Tests

### Prerequisites

1. Build the Python bindings:
   ```bash
   cd uacalc_lib
   PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 maturin develop
   ```

2. Ensure algebra files are available in `resources/algebras/`

### Running Tests

```bash
# Run with unittest
python3 python/uacalc/tests/test_terms.py

# Or with pytest (if available)
pytest python/uacalc/tests/test_terms.py -v
```

## Test Coverage

### Basic Variable Tests
- ✅ Variable creation and properties
- ✅ Predefined variables (x, y, z)
- ✅ String representation and repr
- ✅ Equality and hashing

### Evaluation Tests
- ✅ Variable evaluation with loaded algebras
- ✅ int_eval() method
- ✅ Error handling for missing variables
- ✅ Evaluation with multiple algebra files

## Example Usage

```python
import uacalc_lib

# Load algebra
AlgebraReader = uacalc_lib.io.AlgebraReader
reader = AlgebraReader.from_file("resources/algebras/cyclic3.ua")
alg = reader.read_algebra_file()

# Create variable
VariableImp = uacalc_lib.terms.VariableImp
x = VariableImp("x")

# Evaluate
var_map = {"x": 2}
result = x.eval(alg, var_map)
print(f"x = {result}")  # Output: x = 2
```

## Test Files Tested

The tests validate evaluation with:
- `cyclic2.ua` - Cyclic group of order 2
- `cyclic3.ua` - Cyclic group of order 3
- `n5.ua` - 5-element algebra

## Implementation Status

### Completed
- ✅ VariableImp Python bindings
- ✅ eval() and int_eval() methods
- ✅ Integration with AlgebraReader
- ✅ Comprehensive test suite

### Future Work
- Add NonVariableTerm Python bindings
- Add tests for compound term evaluation
- Add interpretation method tests when TermOperation is ready

## Notes

- All tests use real algebra files from the `resources/algebras/` directory
- Tests skip gracefully if algebra files are not found
- Error handling is properly tested for missing variables
- Hash and equality tests verify correct implementation of Python magic methods

