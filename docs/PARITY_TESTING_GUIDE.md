# Parity Testing Guide

## Overview

The parity test suite ensures that the Rust/Python implementation (uacalc_lib wrapped as org.uacalc in Python) matches the trusted Java UACalc implementation **exactly**. The Java results are the source of truth.

## Test Classification

Tests are classified into three categories:

### 1. SMOKE Tests
**Purpose**: Verify that modules can be imported and basic structure exists.
**What they check**: Import succeeds, basic attributes exist.
**Marker**: `@pytest.mark.smoke`
**Example**: `test_io_shim_imports.py` - checks that org.uacalc.io exports expected names

### 2. SURFACE Tests
**Purpose**: Verify that the Python wrapper exposes the same public API surface as Java.
**What they check**: Module dir() output, public symbol counts, class/method existence.
**Marker**: `@pytest.mark.surface`
**Example**: `test_lat_shim_exports.py` - checks dir(org.uacalc.lat) includes Java class names

### 3. BEHAVIORAL Tests
**Purpose**: Verify exact functional parity - same inputs produce same outputs.
**What they check**: 
- Return values match exactly
- String representations (__str__/__repr__) match
- Exceptions (type and message) match
- No tolerances or loose comparisons

**Marker**: `@pytest.mark.behavioral`
**Example**: `test_io_behavioral_parity.py` - reads algebra files and compares outputs

## Golden Output System

### Structure

```
tests/parity/{package}/
├── golden_data/                 # Structured behavioral test data
│   ├── {testcase}_jython.json  # Expected output from Java/Jython
│   └── {testcase}_cpython.json # Actual output from CPython
├── fixtures/                    # Legacy surface test fixtures
│   ├── golden_*_surface.jython.txt
│   └── golden_*_surface.cpython.txt
└── test_*.py                    # Test files
```

### Golden Data Format (JSON)

```json
{
  "metadata": {
    "package": "org.uacalc.io",
    "generated_at": "2026-10-13T08:30:00Z",
    "runtime": "jython",
    "java_version": "UACalc 4.1",
    "test_cases": 15
  },
  "test_cases": [
    {
      "id": "read_cyclic2",
      "method": "AlgebraIO.readAlgebraFile",
      "args": ["resources/algebras/cyclic2.ua"],
      "result": {
        "success": true,
        "return_value": {
          "name": "cyclic2",
          "cardinality": 2,
          "operations": ["op0", "op1"]
        },
        "return_type": "BasicAlgebra",
        "string_repr": "cyclic2, |A| = 2"
      }
    },
    {
      "id": "read_invalid",
      "method": "AlgebraIO.readAlgebraFile",
      "args": ["resources/algebras/invalid_parity.ua"],
      "result": {
        "success": false,
        "exception": {
          "type": "BadAlgebraFileException",
          "message": "Invalid algebra file format"
        }
      }
    }
  ]
}
```

### Regenerating Golden Data

```bash
# Regenerate for one package
python3 tools/generate_golden_data.py --package io

# Regenerate all packages
python3 tools/generate_golden_data.py --all

# Regenerate and review diff
python3 tools/generate_golden_data.py --package lat --diff
```

**Important**: Always review diffs before committing. New mismatches indicate:
- Real bugs in the Rust implementation (fix these)
- Intentional differences (document in KNOWN_DIFFERENCES.md)
- Golden data bugs (verify against Java behavior)

## Exact Comparison Rules

1. **Return Values**: Must match exactly (type and value)
   - Numbers: exact equality (no floating point tolerance unless documented)
   - Strings: exact character match (case-sensitive)
   - Collections: same order, same elements
   - Objects: compare by semantic fields (name, cardinality, etc.)

2. **String Representations**: Match the output of Java's toString()
   - Python __str__() should match Java toString()
   - Python __repr__() should provide useful debug info (may differ)

3. **Exceptions**:
   - Exception type must match (BadAlgebraFileException, etc.)
   - Exception message should match (document acceptable variations)
   - When Java throws, Python must throw (no silent failures)

4. **No Loose Checks**: 
   - ❌ `assert result is not None`  (too loose)
   - ❌ `assert "cyclic" in name`  (too loose)
   - ✅ `assert result == expected_golden_value`  (exact)
   - ✅ `assert str(result) == "cyclic2, |A| = 2"`  (exact)

## Coverage Reporting

Coverage is measured in two dimensions:

### 1. Wrapper Coverage
**Question**: Which Java public methods have Python wrappers?

```bash
# Show unwrapped methods
python3 tools/jython_contracts_cli.py coverage --unwrapped

# Show wrapper coverage by package
python3 tools/jython_contracts_cli.py coverage --by-package
```

**Computed from**:
- Java source: parse public methods from org/uacalc/**/*.java
- Python wrappers: parse python/org/uacalc/**/__init__.py

### 2. Parity Test Coverage
**Question**: Which wrapped methods have exact behavioral parity tests?

```bash
# Show methods without parity tests
python3 tools/jython_contracts_cli.py parity-coverage --untested

# Show full coverage report
python3 tools/jython_contracts_cli.py parity-coverage --full
```

**Computed from**:
- Wrapped methods (from wrapper coverage above)
- Parity test markers: methods covered by @pytest.mark.behavioral tests
- Golden data: test_cases in golden_data/*.json files

**Goal**: 100% of wrapped methods should have behavioral parity tests.

## Adding Parity Tests for a New Type

### Step 1: Create Test Case Specification

Create `tests/parity/{package}/test_cases/{type}_cases.py`:

```python
"""Test cases for org.uacalc.lat.Lattices behavioral parity."""

from tests.parity.parity_test_base import TestCase

# Define test cases with inputs and method to call
LATTICE_TEST_CASES = [
    TestCase(
        id="lattice_from_join_simple",
        method="Lattices.latticeFromJoin",
        args=[
            # Join table for 2-element chain
            [[0, 1], [1, 1]]
        ],
        description="Build 2-element chain from join table"
    ),
    TestCase(
        id="lattice_from_meet_simple",
        method="Lattices.latticeFromMeet",
        args=[
            # Meet table for 2-element chain
            [[0, 0], [0, 1]]
        ],
        description="Build 2-element chain from meet table"
    ),
]
```

### Step 2: Generate Golden Data

```bash
# This runs test cases on Jython (Java) to generate expected outputs
python3 tools/generate_golden_data.py --package lat --type Lattices

# Review the generated golden data
cat tests/parity/lat/golden_data/Lattices_jython.json
```

### Step 3: Write Behavioral Test

Create `tests/parity/{package}/test_{type}_behavioral_parity.py`:

```python
"""Behavioral parity tests for org.uacalc.lat.Lattices."""

import pytest
from tests.parity.parity_test_base import BehavioralParityTest, load_golden_data

@pytest.mark.behavioral
class TestLatticesBehavioralParity(BehavioralParityTest):
    package = "lat"
    golden_file = "Lattices_jython.json"
    
    def test_lattice_from_join_simple(self):
        """Test latticeFromJoin with 2-element chain."""
        self.run_golden_test_case("lattice_from_join_simple")
    
    def test_lattice_from_meet_simple(self):
        """Test latticeFromMeet with 2-element chain."""
        self.run_golden_test_case("lattice_from_meet_simple")
```

### Step 4: Run and Verify

```bash
# Run the new tests
pytest tests/parity/lat/test_Lattices_behavioral_parity.py -v

# Check coverage
python3 tools/jython_contracts_cli.py parity-coverage --package lat
```

### Step 5: Document Known Differences

If tests reveal intentional differences, document them:

```markdown
# tests/parity/KNOWN_DIFFERENCES.md

## org.uacalc.lat.Lattices

### latticeFromJoin string representation
- **Java**: "BasicLattice@4a574795"
- **Python**: "BasicLattice(cardinality=2)"
- **Reason**: Python provides more useful default repr
- **Status**: Accepted - Python __repr__ is better for debugging
```

## Best Practices

1. **Start with core packages**: io, lat, terms (already have some tests)
2. **One type at a time**: Don't try to test entire packages at once
3. **Representative test cases**: Cover happy path, edge cases, error cases
4. **Keep golden data small**: Use small algebras (cyclic2, cyclic3) not large ones
5. **Run against Jython first**: Verify test cases work with real Java UACalc
6. **Review all failures**: Every mismatch is either a bug or needs documentation
7. **Update regularly**: Re-run golden generation when Java UACalc changes

## Troubleshooting

### "Jython not found" when generating golden data
- Install Jython: `pip install jython-installer; jython-installer`
- Or: Use system Jython: `export JYTHON=/path/to/jython`
- Or: Skip Jython golden generation (test against existing golden files only)

### Test fails but outputs look the same
- Check whitespace differences (trailing spaces, \r\n vs \n)
- Check float precision (may need documented tolerance)
- Check object identity vs equality (use semantic comparison)

### Coverage report shows wrapped method as untested
- Add test case to test_cases/{type}_cases.py
- Regenerate golden data
- Create or update test_{type}_behavioral_parity.py
- Mark test with @pytest.mark.behavioral

## Migration from Old Tests

Existing smoke and surface tests are kept for backward compatibility:
- `test_*_shim_imports.py` → remains as smoke tests
- `test_*_shim_exports.py` → remains as surface tests  
- `golden_*_surface.py` → remains for surface checks
- `test_*_golden_surface.py` → remains for surface checks

New behavioral tests are added alongside them:
- `test_*_behavioral_parity.py` → new behavioral tests
- `golden_data/*.json` → new structured golden data

The goal is to eventually have behavioral tests for all wrapped methods, making smoke/surface tests a quick sanity check layer.
