# Parity Testing

This directory contains **parity tests** that ensure the Rust/Python implementation (`uacalc_lib` wrapped as `org.uacalc.*` in Python) matches the trusted **Java UACalc** implementation exactly.

**Source of Truth**: Java UACalc is the authoritative reference. Python outputs must match Java outputs exactly.

## Quick Start

### Run All Parity Tests

```bash
# Run all parity tests
pytest tests/parity/ -v

# Run only behavioral tests (exact parity checks)
pytest tests/parity/ -m behavioral -v

# Run smoke tests (import checks) only
pytest tests/parity/ -m smoke -v
```

### Generate Coverage Report

```bash
# Show parity test coverage
python3 tools/jython_contracts_cli.py parity-coverage

# Show detailed coverage for io package
python3 tools/jython_contracts_cli.py parity-coverage --package io --verbose

# Show which methods need behavioral tests
python3 tools/jython_contracts_cli.py parity-coverage --untested
```

### Generate Golden Data

Golden data files store expected outputs from Java/Jython for exact comparison:

```bash
# Generate golden data for io package
python3 tools/generate_golden_data.py --package io

# Generate for all packages with test cases
python3 tools/generate_golden_data.py --all

# Review changes before committing
python3 tools/generate_golden_data.py --package lat --diff
```

## Test Classification

Tests are marked with pytest markers based on what they verify:

### 1. **SMOKE** (`@pytest.mark.smoke`)
**Purpose**: Verify imports work and basic structure exists.
- Module can be imported
- Expected names exist in namespace
- **NOT** behavioral parity checks

**Example**: `test_io_shim_imports.py`

### 2. **SURFACE** (`@pytest.mark.surface`)
**Purpose**: Verify Python wrapper exposes same public API as Java.
- `dir()` output matches
- Public symbol counts match
- Class/method names exist
- **NOT** behavioral parity checks

**Example**: `test_lat_golden_surface.py`

### 3. **BEHAVIORAL** (`@pytest.mark.behavioral`)
**Purpose**: Verify **exact functional parity** - same inputs produce same outputs.
- Return values match exactly (no tolerances)
- String representations match Java `toString()`
- Exceptions match (type and message)
- **These are the only tests that prove parity**

**Example**: `test_io_behavioral_parity.py`

## Directory Structure

```
tests/parity/{package}/
├── test_cases/                  # Test case specifications
│   ├── algebraio_cases.py      # Test cases for AlgebraIO
│   └── lattices_cases.py       # Test cases for Lattices
├── golden_data/                 # Expected outputs from Java/Jython
│   ├── io_jython.json          # Golden data for org.uacalc.io
│   ├── terms_jython.json       # Golden data for org.uacalc.terms
│   └── lat_jython.json         # Golden data for org.uacalc.lat
├── fixtures/                    # Legacy surface test fixtures
│   ├── golden_*_surface.jython.txt
│   └── golden_*_surface.cpython.txt
├── test_*_behavioral_parity.py  # NEW: Behavioral parity tests
├── test_*_shim_imports.py       # Smoke tests
└── test_*_golden_surface.py     # Surface tests
```

## Workflow: Adding a New Behavioral Test

### Step 1: Create Test Case Specification

Edit or create `tests/parity/{package}/test_cases/{type}_cases.py`:

```python
from parity_test_base import TestCaseSpec

TEST_CASES = [
    TestCaseSpec(
        id="my_test_case",
        method="ClassName.methodName",
        args=["arg1", "arg2"],
        description="What this test does"
    ),
]
```

### Step 2: Generate Golden Data

```bash
python3 tools/generate_golden_data.py --package {package} --type {ClassName}
```

This runs test cases on Jython (real Java) and saves expected outputs to `golden_data/{package}_jython.json`.

### Step 3: Create or Update Behavioral Test

Edit `tests/parity/{package}/test_{type}_behavioral_parity.py`:

```python
import pytest
from parity_test_base import BehavioralParityTest

@pytest.mark.behavioral
class TestClassNameBehavioralParity(BehavioralParityTest):
    package = "{package}"
    golden_file = "{package}_jython.json"
    
    def test_my_test_case(self):
        """Test description."""
        self.run_golden_test_case("my_test_case")
```

### Step 4: Run and Verify

```bash
# Run the new test
pytest tests/parity/{package}/test_{type}_behavioral_parity.py -v

# Check coverage
python3 tools/jython_contracts_cli.py parity-coverage --package {package}
```

### Step 5: Handle Failures

If tests fail:

1. **Real bug**: Fix the Rust/Python implementation
2. **Intentional difference**: Document in `KNOWN_DIFFERENCES.md`
3. **Bad golden data**: Verify against Java and regenerate

## Coverage Metrics

Two coverage dimensions:

### 1. Wrapper Coverage
**Question**: Which Java public methods have Python wrappers?

- Scans Java source for `public` methods
- Scans Python `python/org/uacalc/{package}/__init__.py` for exports
- Reports unwrapped methods

### 2. Parity Test Coverage
**Question**: Which wrapped methods have behavioral parity tests?

- Scans golden data JSON files for tested methods
- Scans test files for `@pytest.mark.behavioral` tests
- Reports untested wrapped methods

**Goal**: 100% of wrapped methods should have behavioral tests.

## Regenerating Golden Data

### When to Regenerate

- After changing test cases in `test_cases/*.py`
- After updating Java UACalc (uacalc.jar)
- When adding new methods to test

### How to Regenerate

```bash
# Regenerate one package
python3 tools/generate_golden_data.py --package io

# Review diff before committing
python3 tools/generate_golden_data.py --package io --diff
git diff tests/parity/io/golden_data/

# Commit if changes are expected
git add tests/parity/io/golden_data/
git commit -m "Update golden data for io package"
```

### Important

**Always review diffs**. Changes indicate:
- Real bugs found (good!)
- Intentional differences (document them)
- Golden data corruption (fix it)

## Known Differences

See `KNOWN_DIFFERENCES.md` for documented intentional differences between Java and Python implementations.

## Troubleshooting

### "Golden data not generated" skip message

Run: `python3 tools/generate_golden_data.py --package {package}`

### "Jython not found" error

Install Jython:
```bash
pip install jython-installer
jython-installer
# Or set JYTHON environment variable
export JYTHON=/path/to/jython
```

### Test fails but outputs look identical

Check:
- Whitespace differences (trailing spaces, line endings)
- Float precision issues
- Object identity vs. semantic equality

### uacalc_lib not available

Compile the Rust library:
```bash
cd uacalc_lib
cargo build --release
# Install Python package
pip install -e .
```

## Best Practices

1. **Start with core packages**: io, lat, terms (already have tests)
2. **Small test cases**: Use small algebras (cyclic2, cyclic3) not large ones
3. **One type at a time**: Don't try to test entire packages at once
4. **Representative cases**: Cover happy path, edge cases, error cases
5. **Run against Jython first**: Verify test cases work before generating golden data
6. **Review all failures**: Every mismatch needs investigation
7. **Document differences**: If intentional, add to KNOWN_DIFFERENCES.md

## Migration from Old Tests

- Old smoke/surface tests remain for quick checks
- New behavioral tests provide exact parity verification
- Both are valuable: smoke/surface for structure, behavioral for correctness
- Eventually all wrapped methods should have behavioral tests
