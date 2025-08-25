#!/bin/bash

# UACalc Testing Script
# This script runs comprehensive tests for the UACalc project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
RUST_TESTS=true
PYTHON_TESTS=true
INTEGRATION_TESTS=true
BENCHMARK_TESTS=false
COVERAGE=false
VERBOSE=false
QUICK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --rust-only)
            PYTHON_TESTS=false
            INTEGRATION_TESTS=false
            shift
            ;;
        --python-only)
            RUST_TESTS=false
            INTEGRATION_TESTS=false
            shift
            ;;
        --integration-only)
            RUST_TESTS=false
            PYTHON_TESTS=false
            shift
            ;;
        --benchmark)
            BENCHMARK_TESTS=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --rust-only       Run only Rust tests"
            echo "  --python-only     Run only Python tests"
            echo "  --integration-only Run only integration tests"
            echo "  --benchmark       Run benchmark tests"
            echo "  --coverage        Generate coverage reports"
            echo "  --verbose         Verbose output"
            echo "  --quick           Quick test run (skip slow tests)"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_status "Running UACalc tests..."

# Set pytest options
PYTEST_OPTS=""
if [ "$VERBOSE" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS -v"
else
    PYTEST_OPTS="$PYTEST_OPTS -q"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS --cov=uacalc --cov-report=html --cov-report=term-missing"
fi

if [ "$QUICK" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS -m 'not slow'"
fi

# Check if we're in the right directory
if [ ! -f "Cargo.toml" ]; then
    print_error "Cargo.toml not found. Please run this script from the project root."
    exit 1
fi

# Function to run tests with timing
run_tests() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Running $test_name..."
    start_time=$(date +%s)
    
    if eval "$test_command"; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        print_success "$test_name completed in ${duration}s"
        return 0
    else
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        print_error "$test_name failed after ${duration}s"
        return 1
    fi
}

# Track overall test results
TESTS_PASSED=0
TESTS_FAILED=0

# Run Rust tests
if [ "$RUST_TESTS" = true ]; then
    if run_tests "Rust unit tests" "cargo test"; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
    
    # Run Rust integration tests if they exist
    if [ -d "tests/rust" ]; then
        if run_tests "Rust integration tests" "cargo test --test '*'"; then
            ((TESTS_PASSED++))
        else
            ((TESTS_FAILED++))
        fi
    fi
    
    # Run Rust benchmarks if requested
    if [ "$BENCHMARK_TESTS" = true ]; then
        if run_tests "Rust benchmarks" "cargo bench"; then
            ((TESTS_PASSED++))
        else
            ((TESTS_FAILED++))
        fi
    fi
fi

# Run Python tests
if [ "$PYTHON_TESTS" = true ]; then
    # Check if virtual environment is activated
    if [ -z "$VIRTUAL_ENV" ]; then
        print_warning "Virtual environment not activated. Attempting to activate..."
        if [ -f ".venv/bin/activate" ]; then
            source .venv/bin/activate
        else
            print_error "Virtual environment not found. Please run setup.sh first."
            exit 1
        fi
    fi
    
    # Check if the extension is built
    if ! python -c "import uacalc" 2>/dev/null; then
        print_warning "UACalc extension not found. Building..."
        cd uacalc-py
        maturin develop --release
        cd ..
    fi
    
    # Run Python unit tests
    if run_tests "Python unit tests" "python -m pytest tests/python/ $PYTEST_OPTS"; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
    
    # Run Python benchmarks if requested
    if [ "$BENCHMARK_TESTS" = true ]; then
        if run_tests "Python benchmarks" "python -m pytest tests/python/ -m benchmark $PYTEST_OPTS"; then
            ((TESTS_PASSED++))
        else
            ((TESTS_FAILED++))
        fi
    fi
fi

# Run integration tests
if [ "$INTEGRATION_TESTS" = true ]; then
    # Test compatibility with existing .ua files
    if [ -d "resources/algebras" ]; then
        print_status "Testing compatibility with existing .ua files..."
        
        # Find .ua files
        ua_files=$(find resources/algebras -name "*.ua" | head -5)  # Limit to first 5 files
        
        if [ -n "$ua_files" ]; then
            compatibility_passed=0
            compatibility_failed=0
            
            for ua_file in $ua_files; do
                print_status "Testing compatibility with $(basename "$ua_file")..."
                if python -c "
import uacalc
try:
    algebra = uacalc.load_algebra('$ua_file')
    print(f'Successfully loaded {algebra.name} with {algebra.cardinality()} elements')
except Exception as e:
    print(f'Failed to load {ua_file}: {e}')
    exit(1)
"; then
                    ((compatibility_passed++))
                else
                    ((compatibility_failed++))
                fi
            done
            
            if [ $compatibility_failed -eq 0 ]; then
                print_success "Compatibility tests passed: $compatibility_passed files"
                ((TESTS_PASSED++))
            else
                print_error "Compatibility tests failed: $compatibility_failed files"
                ((TESTS_FAILED++))
            fi
        else
            print_warning "No .ua files found for compatibility testing"
        fi
    fi
    
    # Run integration tests if they exist
    if [ -d "tests/integration" ]; then
        if run_tests "Integration tests" "python -m pytest tests/integration/ $PYTEST_OPTS"; then
            ((TESTS_PASSED++))
        else
            ((TESTS_FAILED++))
        fi
    fi
fi

# Performance comparison tests
if [ "$BENCHMARK_TESTS" = true ]; then
    print_status "Running performance comparison tests..."
    
    # Create a simple algebra for benchmarking
    python -c "
import time
import uacalc

# Create a test algebra
algebra = uacalc.create_algebra('Benchmark', list(range(10)))

# Add a binary operation
table = [[(i + j) % 10 for j in range(10)] for i in range(10)]
operation = uacalc.create_operation('add', 2, table)
algebra.add_operation('add', operation)

# Benchmark operation evaluation
start_time = time.time()
for _ in range(10000):
    operation.value([5, 3])
end_time = time.time()

print(f'Operation evaluation: {(end_time - start_time) * 1000:.2f} ms for 10000 calls')
"
fi

# Generate coverage report
if [ "$COVERAGE" = true ]; then
    print_status "Generating coverage report..."
    if [ -f "htmlcov/index.html" ]; then
        print_success "Coverage report generated: htmlcov/index.html"
    fi
fi

# Summary
print_status "Test Summary:"
echo "  Tests passed: $TESTS_PASSED"
echo "  Tests failed: $TESTS_FAILED"

if [ $TESTS_FAILED -eq 0 ]; then
    print_success "All tests passed!"
    exit 0
else
    print_error "Some tests failed!"
    exit 1
fi

