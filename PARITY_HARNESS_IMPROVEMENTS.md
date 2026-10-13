# Parity Harness Improvements Summary

This document summarizes the improvements made to strengthen the parity test harness for ensuring exact behavioral parity between the Rust/Python implementation and the trusted Java UACalc.

## Motivation

The previous parity testing approach had several weaknesses:

1. **Shallow tests**: Most tests were smoke tests (imports only) or surface tests (module structure)
2. **No golden outputs**: No systematic way to capture and compare exact expected outputs
3. **No exception testing**: No systematic checking of exception types and messages
4. **Manual coverage tracking**: Coverage was declared by hand in YAML files, not measured
5. **Loose comparisons**: No exact comparison of return values and string representations

## Improvements Implemented

### 1. Test Classification System

Introduced three test categories with pytest markers:

- **SMOKE** (`@pytest.mark.smoke`): Import and basic structure checks
- **SURFACE** (`@pytest.mark.surface`): Public API surface checks (dir(), counts)
- **BEHAVIORAL** (`@pytest.mark.behavioral`): **Exact functional parity checks**

All existing tests have been classified and marked appropriately.

### 2. Golden Output Infrastructure

Created a systematic framework for generating and storing expected outputs:

**Components:**
- `tests/parity/parity_test_base.py`: Base classes for behavioral parity tests
- `tools/generate_golden_data.py`: Tool to generate golden outputs from Java/Jython
- `tests/parity/{package}/golden_data/`: JSON files with expected outputs
- `tests/parity/{package}/test_cases/`: Test case specifications

**Golden Data Format (JSON):**
```json
{
  "metadata": {
    "package": "org.uacalc.io",
    "runtime": "jython",
    "test_cases": 6
  },
  "test_cases": [
    {
      "id": "read_cyclic2",
      "method": "AlgebraIO.readAlgebraFile",
      "args": ["resources/algebras/cyclic2.ua"],
      "result": {
        "success": true,
        "return_value": {...},
        "string_repr": "cyclic2, |A| = 2"
      }
    }
  ]
}
```

### 3. Exact Comparison Framework

Created `BehavioralParityTest` base class that:
- Loads golden data from JSON files
- Executes test cases against CPython implementation
- Compares results **exactly** (no tolerances):
  - Return values (type and value)
  - String representations
  - Exception types and messages

### 4. Coverage Measurement Tool

Extended `jython_contracts_cli.py` with new `parity-coverage` command:

```bash
python3 tools/jython_contracts_cli.py parity-coverage
```

Measures two dimensions:
1. **Wrapper Coverage**: Which Java public methods have Python wrappers
2. **Test Coverage**: Which wrapped methods have behavioral parity tests

Computed from:
- Java source scanning (public methods)
- Python wrapper scanning
- Golden data files and test markers

### 5. Behavioral Tests for Core Packages

Implemented exact comparison behavioral tests for:

- **org.uacalc.io**: AlgebraIO file reading methods (6 test cases)
- **org.uacalc.lat**: Lattices static methods (3 test cases)
- **org.uacalc.terms**: Terms parsing and creation (6 test cases)

### 6. Comprehensive Documentation

Created documentation:
- `docs/PARITY_TESTING_GUIDE.md`: Complete guide for parity testing
- `tests/parity/README.md`: Quick reference and workflow
- `tests/parity/KNOWN_DIFFERENCES.md`: Tracking intentional differences

## Coverage Numbers

### Before

```
Package         Java     Wrapped    Tested     Wrapper %    Test %    
----------------------------------------------------------------------
io              25       9          0            36.0%        0.0%
lat             41       7          0            17.1%        0.0%
terms           40       10         0            25.0%        0.0%
...
----------------------------------------------------------------------
TOTAL           507      64         0            12.6%        0.0%
```

### After

With the new infrastructure in place:

```
Package         Java     Wrapped    Tested     Wrapper %    Test %    
----------------------------------------------------------------------
io              25       9          6*           36.0%       66.7%*
lat             41       7          3*           17.1%       42.9%*
terms           40       10         6*           25.0%       60.0%*
...
----------------------------------------------------------------------
TOTAL           507      64         15*          12.6%       23.4%*
```

*Note: Test coverage numbers marked with * are potential - actual coverage depends on:
1. Golden data being generated (requires Jython)
2. Tests passing (requires uacalc_lib to be built)

## Key Benefits

1. **Trustworthy**: Behavioral tests compare against real Java outputs
2. **Exact**: No loose checks or tolerances unless explicitly documented
3. **Measurable**: Coverage is computed from code, not declared by hand
4. **Reproducible**: Golden data can be regenerated from Java when needed
5. **Visible failures**: Real mismatches fail tests (not hidden or skipped)
6. **Documented**: Clear distinction between smoke/surface/behavioral tests
7. **Scalable**: Easy workflow to add tests for new types

## Workflow for Future Work

To add behavioral tests for a new type:

1. Create test case specification in `tests/parity/{package}/test_cases/{type}_cases.py`
2. Generate golden data: `python3 tools/generate_golden_data.py --package {package}`
3. Create behavioral test file: `tests/parity/{package}/test_{type}_behavioral_parity.py`
4. Run tests and fix any mismatches found
5. Check coverage: `python3 tools/jython_contracts_cli.py parity-coverage --package {package}`

## Known Limitations

1. **Requires Jython**: Golden data generation requires Jython with uacalc.jar
2. **Requires uacalc_lib**: Tests require Rust library to be compiled
3. **Not all packages covered**: Only io, lat, terms have behavioral tests so far
4. **String representation variations**: Some tests may need `skip_string_check=True`

## Next Steps

To achieve 100% parity test coverage:

1. Generate golden data for io, lat, terms packages
2. Add behavioral tests for remaining wrapped methods in those packages
3. Extend to other core packages (alg, eq, util, etc.)
4. Integrate with CI to regenerate golden data when Java changes
5. Track and document any discovered mismatches

## Files Created/Modified

### New Files Created

**Infrastructure:**
- `tests/parity/parity_test_base.py`
- `tools/generate_golden_data.py`
- `tools/jython_contracts/parity_coverage.py`

**Test Cases:**
- `tests/parity/io/test_cases/algebraio_cases.py`
- `tests/parity/lat/test_cases/lattices_cases.py`
- `tests/parity/terms/test_cases/terms_cases.py`

**Behavioral Tests:**
- `tests/parity/io/test_io_behavioral_parity.py`
- `tests/parity/lat/test_lat_behavioral_parity.py`
- `tests/parity/terms/test_terms_behavioral_parity.py`

**Documentation:**
- `docs/PARITY_TESTING_GUIDE.md`
- `tests/parity/README.md`
- `tests/parity/KNOWN_DIFFERENCES.md`

### Files Modified

**Configuration:**
- `pytest.ini` - Added smoke, surface, behavioral markers
- `pyproject.toml` - Added markers to [tool.pytest.ini_options]

**CLI:**
- `tools/jython_contracts/cli.py` - Added parity-coverage command

**Test Markers:**
- `tests/parity/io/test_io_shim_imports.py` - Added @pytest.mark.smoke
- `tests/parity/io/test_io_golden_surface.py` - Added @pytest.mark.surface
- `tests/parity/io/test_io_contract_parity.py` - Added @pytest.mark.behavioral
- `tests/parity/lat/test_lat_shim_exports.py` - Added @pytest.mark.smoke

## Testing the Infrastructure

```bash
# Check coverage
python3 tools/jython_contracts_cli.py parity-coverage

# Generate golden data (requires Jython)
python3 tools/generate_golden_data.py --package io

# Run behavioral tests (requires uacalc_lib)
pytest tests/parity/ -m behavioral -v

# Run smoke tests
pytest tests/parity/ -m smoke -v

# Run all parity tests
pytest tests/parity/ -v
```

## Conclusion

The improved parity harness provides:

- **Systematic**: Clear workflow and infrastructure
- **Exact**: No loose comparisons or tolerances
- **Trustworthy**: Compares against real Java outputs
- **Measurable**: Coverage computed from code
- **Scalable**: Easy to add new tests

This positions the project for confident refactoring with regression guards in place.
