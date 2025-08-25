#!/bin/bash

# UACalc Build Script
# This script builds the Rust code and Python extensions

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
BUILD_TYPE="release"
CLEAN=false
TEST=false
BENCH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            BUILD_TYPE="debug"
            shift
            ;;
        --release)
            BUILD_TYPE="release"
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        --test)
            TEST=true
            shift
            ;;
        --bench)
            BENCH=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --debug     Build in debug mode (default: release)"
            echo "  --release   Build in release mode"
            echo "  --clean     Clean build artifacts before building"
            echo "  --test      Run tests after building"
            echo "  --bench     Run benchmarks after building"
            echo "  --help      Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_status "Building UACalc in $BUILD_TYPE mode..."

# Check if we're in the right directory
if [ ! -f "Cargo.toml" ]; then
    print_error "Cargo.toml not found. Please run this script from the project root."
    exit 1
fi

# Clean if requested
if [ "$CLEAN" = true ]; then
    print_status "Cleaning build artifacts..."
    cargo clean
    if [ -d "target" ]; then
        rm -rf target
    fi
    if [ -d "uacalc-py/target" ]; then
        rm -rf uacalc-py/target
    fi
    print_success "Clean completed"
fi

# Build Rust core library
print_status "Building Rust core library..."
if [ "$BUILD_TYPE" = "release" ]; then
    cargo build --release
else
    cargo build
fi

# Run Rust tests
print_status "Running Rust tests..."
cargo test

# Run Rust benchmarks if requested
if [ "$BENCH" = true ]; then
    print_status "Running Rust benchmarks..."
    cargo bench
fi

# Build Python extension
print_status "Building Python extension..."
cd uacalc-py

if [ "$BUILD_TYPE" = "release" ]; then
    maturin build --release
else
    maturin build
fi

cd ..

# Install Python extension in development mode
print_status "Installing Python extension in development mode..."
cd uacalc-py
maturin develop --release
cd ..

# Run Python tests if requested
if [ "$TEST" = true ]; then
    print_status "Running Python tests..."
    
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
    
    # Run tests
    python -m pytest tests/python/ -v --tb=short
    
    # Run integration tests if they exist
    if [ -d "tests/integration" ]; then
        print_status "Running integration tests..."
        python -m pytest tests/integration/ -v --tb=short
    fi
fi

# Run benchmarks if requested
if [ "$BENCH" = true ]; then
    print_status "Running Python benchmarks..."
    python -m pytest tests/python/ -m benchmark -v
fi

print_success "Build completed successfully!"

# Show build information
print_status "Build information:"
echo "  Build type: $BUILD_TYPE"
echo "  Rust target: $(rustc --version)"
echo "  Python: $(python3 --version)"

if [ "$BUILD_TYPE" = "release" ]; then
    print_status "Release build completed. The extension is optimized for performance."
else
    print_status "Debug build completed. The extension includes debug symbols."
fi

print_status "To use the extension in Python:"
echo "  import uacalc"
echo "  algebra = uacalc.create_algebra('Test', [0, 1, 2])"

