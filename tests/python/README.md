# Java UACalc Compatibility Test Suite

This directory contains a comprehensive test suite for validating compatibility between the Java UACalc implementation and the Rust/Python implementation. The test suite ensures that both implementations produce identical results for all major UACalc operations.

## Overview

The compatibility test suite addresses the requirements from Task 13 of the comprehensive Java compatibility testing specification:

- **Task 13.1**: Integrate all test classes into unified test suite
- **Task 13.2**: Validate comprehensive coverage of Java UACalc functionality  
- **Task 13.3**: Create documentation and usage guidelines for the test suite

## Test Suite Architecture

### Core Components

1. **BaseCompatibilityTest** (`base_compatibility_test.py`)
   - Foundation class for all compatibility tests
   - Provides Java environment setup and validation
   - Implements generic Java operation execution and result parsing
   - Handles comprehensive result comparison and error reporting

2. **ComprehensiveTestSuite** (`comprehensive_test_suite.py`)
   - Unified test execution framework with advanced features
   - Integrates all compatibility test classes
   - Manages test dependencies and execution order
   - Provides filtering and selective execution capabilities
   - **NEW**: Resource monitoring and parallel execution support
   - **NEW**: Enhanced timeout management and conflict detection

3. **CoverageValidator** (`coverage_validator.py`)
   - Validates comprehensive coverage of Java UACalc functionality
   - Maps Java packages to test classes
   - Identifies gaps in test coverage
   - Generates coverage reports and recommendations

4. **Enhanced Test Runner** (`scripts/run_comprehensive_tests.py`)
   - **NEW**: Unified interface for both pytest and comprehensive suite
   - **NEW**: Advanced parallel execution with resource management
   - **NEW**: Combined reporting and result aggregation
   - **NEW**: CI/CD integration support

5. **Resource Manager** (integrated in ComprehensiveTestSuite)
   - **NEW**: Real-time memory and CPU monitoring
   - **NEW**: Automatic resource limit enforcement
   - **NEW**: Performance statistics collection

### Test Categories

The test suite is organized by Java UACalc packages:

#### Core Algebra Tests (`org.uacalc.alg`)
- `test_algebra_compatibility.py` - Algebra interface methods
- `test_basic_algebra_compatibility.py` - BasicAlgebra construction and operations
- `test_small_algebra_compatibility.py` - SmallAlgebra interface and properties
- `test_algebras_compatibility.py` - Algebras utility class methods
- `test_free_algebra_compatibility.py` - Free algebra generation
- `test_homomorphism_compatibility.py` - Homomorphism detection and properties
- `test_malcev_compatibility.py` - Maltsev condition checking
- `test_product_algebra_compatibility.py` - Direct product construction
- `test_quotient_algebra_compatibility.py` - Quotient algebra construction
- `test_subalgebra_compatibility.py` - Subalgebra generation

#### Congruence and Lattice Tests (`org.uacalc.alg.conlat`)
- `test_congruence_lattice_compatibility.py` - Congruence lattice operations
- `test_partition_compatibility.py` - Partition operations and refinement
- `test_binary_relation_compatibility.py` - Binary relation operations and closures
- `test_polymorphisms_compatibility.py` - Polymorphism detection and classification
- `test_type_finder_compatibility.py` - Tame congruence theory type detection

#### Operation Tests (`org.uacalc.alg.op`)
- `test_operation_compatibility.py` - Operation interface methods
- `test_operations_compatibility.py` - Operations utility class methods
- `test_operation_symbol_compatibility.py` - Operation symbol creation and comparison
- `test_term_operation_compatibility.py` - Term-based operation construction

#### Term Tests (`org.uacalc.terms`)
- `test_term_compatibility.py` - Term parsing and evaluation
- `test_terms_compatibility.py` - Terms utility class methods
- `test_variable_compatibility.py` - Variable handling and substitution
- `test_taylor_compatibility.py` - Taylor term operations

#### Lattice Tests (`org.uacalc.lat`)
- `test_lattice_compatibility.py` - Lattice interface methods
- `test_basic_lattice_compatibility.py` - BasicLattice construction and operations
- `test_order_compatibility.py` - Partial order operations
- `test_lattices_compatibility.py` - Lattices utility class methods

#### Equation Tests (`org.uacalc.eq`)
- `test_equation_compatibility.py` - Equation construction and satisfaction
- `test_equations_compatibility.py` - Equations utility class methods
- `test_presentation_compatibility.py` - Algebraic presentation operations

#### Group Tests (`org.uacalc.group`)
- `test_permutation_group_compatibility.py` - Permutation group operations

#### I/O Tests (`org.uacalc.io`)
- `test_algebra_io_compatibility.py` - AlgebraIO static methods
- `test_algebra_reader_compatibility.py` - AlgebraReader parsing operations
- `test_algebra_writer_compatibility.py` - AlgebraWriter file generation

#### Utility Tests (`org.uacalc.util`)
- `test_int_array_compatibility.py` - IntArray operations
- `test_horner_compatibility.py` - Horner encoding/decoding
- `test_sequence_generator_compatibility.py` - Sequence generation utilities

## Prerequisites

### Environment Setup

1. **Python Environment**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Verify Python version (3.8+ recommended)
   python --version
   ```

2. **Java Environment**
   - Java 8 or higher
   - UACalc JAR file at `jars/uacalc.jar`
   - JavaWrapper compiled at `scripts/JavaWrapper.class`

3. **Dependencies**
   ```bash
   # Install required packages with enhanced testing support
   pip install -e uacalc-py[dev,test]
   pip install psutil  # For resource monitoring
   ```

4. **Enhanced pytest Plugins**
   The test suite now includes advanced pytest plugins:
   - `pytest-html` - HTML report generation
   - `pytest-json-report` - Structured JSON reporting
   - `pytest-timeout` - Individual test timeouts
   - `pytest-xdist` - Parallel test execution
   - `pytest-mock` - Enhanced mocking capabilities
   - `pytest-clarity` - Improved assertion reporting

### Test Data

The test suite uses algebra files from `resources/algebras/` directory. Ensure these files are available:
- Small algebras: `ba2.ua`, `cyclic2.ua`, `cyclic3.ua`
- Medium algebras: `d16.ua`, `m3.ua`, `m4.ua`
- Large algebras: `bergman/*.ua`

## Usage

### Running Individual Test Classes

```bash
# Run a specific test class
source .venv/bin/activate
PYTHONPATH=/home/jamie/Documents/uacalcsrc python -m pytest tests/python/test_algebra_compatibility.py -v

# Run with coverage
PYTHONPATH=/home/jamie/Documents/uacalcsrc python -m pytest tests/python/test_algebra_compatibility.py --cov=uacalc --cov-report=html
```

### Running the Comprehensive Test Suite

#### Enhanced Test Runner (Recommended)
```bash
# Run both pytest and comprehensive suite with enhanced features
source .venv/bin/activate
python scripts/run_comprehensive_tests.py

# Run with parallel execution and resource monitoring
python scripts/run_comprehensive_tests.py --parallel --max-workers 4 --memory-limit 2048

# Run only specific test categories
python scripts/run_comprehensive_tests.py --comprehensive-only --no-lattice --no-equation

# Run with custom timeout and resource limits
python scripts/run_comprehensive_tests.py --timeout 600 --memory-limit 4096 --cpu-limit 90
```

#### Direct Comprehensive Suite
```bash
# Run all compatibility tests
source .venv/bin/activate
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py

# Run with specific options
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py \
    --no-utility \
    --max-algebra-size 10 \
    --timeout 600 \
    --output-file my_test_results.json

# Run with parallel execution and resource monitoring
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py \
    --parallel --max-parallel 4 --memory-limit 2048 --cpu-limit 80
```

### Available Command Line Options

#### Test Category Selection
- `--no-algebra` - Skip algebra tests
- `--no-congruence` - Skip congruence tests
- `--no-operation` - Skip operation tests
- `--no-term` - Skip term tests
- `--no-lattice` - Skip lattice tests
- `--no-equation` - Skip equation tests
- `--no-group` - Skip group tests
- `--no-io` - Skip I/O tests
- `--no-utility` - Skip utility tests

#### Filtering Options
- `--max-algebra-size N` - Test only algebras with size ≤ N
- `--specific-algebras ALG1 ALG2` - Test only specified algebras
- `--specific-operations OP1 OP2` - Test only specified operations

#### Performance Options
- `--timeout N` - Timeout per test in seconds (default: 300)
- `--parallel` - Enable parallel execution
- `--max-parallel N` - Maximum parallel tests (default: 4)

#### Output Options
- `--output-file FILE` - Output file for results (default: comprehensive_test_results.json)
- `--no-save` - Do not save results to file

### Running Coverage Validation

```bash
# Validate test coverage
source .venv/bin/activate
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/coverage_validator.py

# Generate coverage report
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/coverage_validator.py \
    --output-file coverage_report.json
```

### Using pytest Directly

```bash
# Run all tests with pytest
source .venv/bin/activate
PYTHONPATH=/home/jamie/Documents/uacalcsrc pytest tests/python/ -v

# Run specific test patterns
PYTHONPATH=/home/jamie/Documents/uacalcsrc pytest tests/python/test_*algebra* -v

# Run with detailed output
PYTHONPATH=/home/jamie/Documents/uacalcsrc pytest tests/python/ -v -s --tb=long
```

## Understanding Test Results

### Test Result Structure

Each test produces a `CompatibilityTestResult` with:
- `test_name` - Name of the test method
- `algebra_name` - Name of the algebra being tested
- `operation` - Name of the operation being tested
- `rust_result` - Result from Rust implementation
- `java_result` - Result from Java implementation
- `matches` - Whether results match
- `error_message` - Error details if mismatch
- `execution_time_rust` - Rust execution time
- `execution_time_java` - Java execution time

### Test Suite Report

The comprehensive test suite generates a `TestSuiteReport` with:
- `total_tests` - Total number of tests executed
- `passed_tests` - Number of passing tests
- `failed_tests` - Number of failing tests
- `skipped_tests` - Number of skipped tests
- `compatibility_percentage` - Overall compatibility percentage
- `feature_coverage` - Coverage by feature area
- `execution_time_total` - Total execution time

### Interpreting Failures

#### Common Failure Types

1. **Java Environment Issues**
   ```
   Java operation returned None (Java unavailable)
   ```
   - Check Java installation and UACalc JAR availability
   - Verify JavaWrapper compilation

2. **Result Mismatches**
   ```
   Results differ: at root: numeric mismatch (Rust: 1.0, Java: 1.0000001, diff: 1e-07)
   ```
   - Usually indicates floating-point precision differences
   - Check tolerance settings in test configuration

3. **Timeout Errors**
   ```
   Operation timed out after 300s
   ```
   - Increase timeout for complex operations
   - Consider using smaller test algebras

4. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'tests'
   ```
   - Ensure PYTHONPATH is set correctly
   - Check that `__init__.py` files exist

#### Debugging Tips

1. **Enable Verbose Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Run Individual Tests**
   ```bash
   PYTHONPATH=/home/jamie/Documents/uacalcsrc python -m pytest tests/python/test_algebra_compatibility.py::AlgebraCompatibilityTest::test_algebra_properties -v -s
   ```

3. **Check Java Wrapper Output**
   ```bash
   java -cp jars/uacalc.jar:scripts JavaWrapper properties resources/algebras/ba2.ua
   ```

## Test Data Management

### Algebra File Organization

Test algebras are organized by complexity:
- **Small** (≤ 4 elements): `ba2.ua`, `cyclic2.ua`, `cyclic3.ua`
- **Medium** (5-8 elements): `d16.ua`, `m3.ua`, `m4.ua`
- **Large** (> 8 elements): `bergman/*.ua`

### Adding New Test Algebras

1. Place algebra file in `resources/algebras/`
2. Update test data discovery in `BaseCompatibilityTest`
3. Consider complexity for timeout settings

### Test Case Generation

The test suite automatically generates test cases based on:
- Available algebra files
- Operation complexity
- Resource constraints

## Performance Considerations

### Timeout Management

Different operations have different timeout requirements:
- **Simple operations** (properties): 30s
- **Standard operations** (congruence generation): 60s
- **Complex operations** (lattice construction): 300s

### Memory Usage

- Large algebras (> 20 elements) may require significant memory
- Consider using smaller test sets for CI/CD environments
- Monitor memory usage during long test runs
- **NEW**: Automatic memory monitoring with configurable limits
- **NEW**: Resource usage statistics in test reports

### Parallel Execution

- Use `--parallel` for faster execution on multi-core systems
- Limit parallel tests with `--max-parallel` to avoid resource exhaustion
- Some tests may not be suitable for parallel execution
- **NEW**: Intelligent resource checking before parallel execution
- **NEW**: Automatic fallback to sequential execution if resources are insufficient

### Enhanced Features

#### Resource Monitoring
- **Real-time monitoring**: Memory and CPU usage tracked during test execution
- **Configurable limits**: Set memory and CPU limits to prevent system overload
- **Performance statistics**: Peak and average resource usage in reports
- **Automatic enforcement**: Tests automatically adjust behavior based on resource availability

#### Advanced Reporting
- **HTML reports**: Self-contained HTML reports with detailed test results
- **JSON reports**: Structured JSON output for programmatic analysis
- **Combined reports**: Integration of pytest and comprehensive suite results
- **CI/CD integration**: GitHub Actions workflow with automated result publishing

#### Parallel Execution Improvements
- **Test isolation**: Tests grouped by class to maintain proper isolation
- **Resource-aware execution**: Automatic detection of system capacity
- **Graceful degradation**: Fallback to sequential execution when needed
- **Progress tracking**: Real-time progress updates for long-running test suites

## Troubleshooting

### Common Issues

1. **pytest Import Errors**
   - **Problem**: `ModuleNotFoundError: No module named 'tests'`
   - **Solution**: Set `PYTHONPATH=/home/jamie/Documents/uacalcsrc` before running pytest

2. **Java Compilation Errors**
   - **Problem**: `JavaWrapper compilation failed`
   - **Solution**: Check Java installation and UACalc JAR path

3. **Test Timeouts**
   - **Problem**: Tests timing out on large algebras
   - **Solution**: Increase timeout or use smaller test algebras

4. **Memory Issues**
   - **Problem**: Out of memory during test execution
   - **Solution**: Reduce parallel execution or use smaller test sets

### Getting Help

1. Check the test logs in `comprehensive_test_suite.log`
2. Review the coverage report in `coverage_report.json`
3. Examine individual test output with `-v` flag
4. Use `--tb=long` for detailed tracebacks

## Contributing

### Adding New Tests

1. Create new test class inheriting from `BaseCompatibilityTest`
2. Implement test methods following naming convention `test_*_compatibility`
3. Add test class to `ComprehensiveTestSuite._discover_test_classes()`
4. Update package mapping in `CoverageValidator._initialize_package_mapping()`

### Test Guidelines

1. **Test Naming**: Use descriptive names indicating what is being tested
2. **Error Handling**: Always handle Java unavailability gracefully
3. **Resource Management**: Clean up resources in `tearDown()` methods
4. **Documentation**: Document complex test logic and expected behavior

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Add docstrings for all public methods
- Include logging statements for debugging

## Requirements Compliance

This test suite addresses the following requirements from the comprehensive Java compatibility testing specification:

### Requirements 7.1, 7.2, 7.3, 7.4, 7.5
- **7.1**: Unified test execution framework with comprehensive result aggregation
- **7.2**: Detailed result comparison with tolerance handling and error reporting
- **7.3**: Test data discovery and management with systematic coverage
- **7.4**: Performance monitoring and resource usage tracking
- **7.5**: Test filtering and selective execution capabilities

The test suite provides a complete solution for validating Java UACalc compatibility across all major functionality areas, ensuring that the Rust/Python implementation produces identical results to the original Java implementation.
