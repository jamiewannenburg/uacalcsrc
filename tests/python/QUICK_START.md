# Quick Start Guide - Java UACalc Compatibility Tests

This guide provides quick instructions for running and understanding the Java UACalc compatibility test suite.

## Prerequisites

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Verify Java is available
java -version

# 3. Check UACalc JAR exists
ls jars/uacalc.jar

# 4. Verify JavaWrapper is compiled
ls scripts/JavaWrapper.class
```

## Quick Commands

### Run All Tests
```bash
# Comprehensive test suite (recommended)
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py

# Using pytest directly
PYTHONPATH=/home/jamie/Documents/uacalcsrc pytest tests/python/ -v
```

### Run Specific Test Categories
```bash
# Only algebra tests
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py --no-congruence --no-operation --no-term --no-lattice --no-equation --no-group --no-io --no-utility

# Only high-priority tests (algebra, congruence, operation, term, io)
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py --no-lattice --no-equation --no-group --no-utility
```

### Run Individual Test Classes
```bash
# Single test class
PYTHONPATH=/home/jamie/Documents/uacalcsrc python -m pytest tests/python/test_algebra_compatibility.py -v

# Specific test method
PYTHONPATH=/home/jamie/Documents/uacalcsrc python -m pytest tests/python/test_algebra_compatibility.py::AlgebraCompatibilityTest::test_algebra_properties -v
```

### Check Test Coverage
```bash
# Validate coverage
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/coverage_validator.py

# Generate coverage report
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/coverage_validator.py --output-file my_coverage.json
```

## Common Issues & Solutions

### Issue: Import Errors
```
ModuleNotFoundError: No module named 'tests'
```
**Solution**: Always set `PYTHONPATH=/home/jamie/Documents/uacalcsrc` before running tests.

### Issue: Java Not Found
```
Java operation returned None (Java unavailable)
```
**Solution**: 
1. Check Java installation: `java -version`
2. Verify UACalc JAR: `ls jars/uacalc.jar`
3. Compile JavaWrapper: `javac -cp jars/uacalc.jar scripts/JavaWrapper.java`

### Issue: Test Timeouts
```
Operation timed out after 300s
```
**Solution**: 
1. Increase timeout: `--timeout 600`
2. Use smaller algebras: `--max-algebra-size 8`
3. Skip complex tests: `--no-malcev --no-congruence`

### Issue: Memory Problems
```
Out of memory during test execution
```
**Solution**:
1. Reduce parallel execution: `--max-parallel 2`
2. Use smaller test set: `--max-algebra-size 6`
3. Run tests sequentially: Remove `--parallel`

## Test Results Interpretation

### Success Indicators
- ✅ **Compatibility: 95%+** - Excellent compatibility
- ⚠️ **Compatibility: 80-95%** - Good compatibility, minor issues
- ❌ **Compatibility: <80%** - Significant compatibility issues

### Common Failure Patterns
- **Floating-point precision**: `numeric mismatch (Rust: 1.0, Java: 1.0000001)`
- **Ordering differences**: `sequence order mismatch`
- **Missing features**: `Java operation failed: Method not implemented`

## Performance Tips

### Fast Test Runs
```bash
# Quick smoke test
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py \
    --max-algebra-size 4 \
    --timeout 60 \
    --no-utility
```

### Comprehensive Testing
```bash
# Full test suite with detailed reporting
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py \
    --timeout 600 \
    --output-file full_test_results.json
```

### CI/CD Integration
```bash
# Automated testing with exit codes
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py \
    --max-algebra-size 8 \
    --timeout 300 \
    --output-file ci_results.json
echo "Exit code: $?"
```

## File Locations

- **Test Results**: `comprehensive_test_results.json`
- **Coverage Report**: `coverage_report.json`
- **Test Logs**: `comprehensive_test_suite.log`
- **Test Algebras**: `resources/algebras/*.ua`
- **Java Wrapper**: `scripts/JavaWrapper.java`

## Getting Help

1. **Check logs**: Look at `comprehensive_test_suite.log` for detailed error information
2. **Run with verbose output**: Add `-v` flag to pytest commands
3. **Test Java wrapper directly**: `java -cp jars/uacalc.jar:scripts JavaWrapper properties resources/algebras/ba2.ua`
4. **Validate environment**: Run `python tests/python/coverage_validator.py` to check setup

## Next Steps

After running tests successfully:
1. Review test results in the generated JSON files
2. Check coverage report for any missing test areas
3. Address any compatibility issues found
4. Consider adding new test cases for uncovered functionality

For detailed information, see the full [README.md](README.md) documentation.
