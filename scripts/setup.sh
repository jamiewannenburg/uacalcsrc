#!/bin/bash

# UACalc Rust/Python Development Environment Setup Script
# This script sets up the development environment for the UACalc project

set -e  # Exit on any error

echo "Setting up UACalc Rust/Python development environment..."

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

# Check if we're on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    print_warning "Detected Windows environment. Some commands may need adjustment."
fi

# Check if Rust is installed
print_status "Checking Rust installation..."
if ! command -v rustc &> /dev/null; then
    print_error "Rust is not installed. Please install Rust from https://rustup.rs/"
    print_status "Run: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

RUST_VERSION=$(rustc --version)
print_success "Found Rust: $RUST_VERSION"

# Check if Cargo is installed
if ! command -v cargo &> /dev/null; then
    print_error "Cargo is not installed. Please install Rust with Cargo."
    exit 1
fi

# Check if Python is installed
print_status "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_success "Found Python: $PYTHON_VERSION"

# Check Python version
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or later is required. Found Python $PYTHON_MAJOR.$PYTHON_MINOR"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip."
    exit 1
fi

# Install Rust components
print_status "Installing Rust components..."
rustup component add rustfmt
rustup component add clippy
rustup target add wasm32-unknown-unknown  # For potential future web support

# Install maturin for Python extension building
print_status "Installing maturin..."
pip3 install --user maturin

# Check if maturin is in PATH
if ! command -v maturin &> /dev/null; then
    print_warning "maturin not found in PATH. You may need to add ~/.local/bin to your PATH"
    print_status "Add this line to your shell profile:"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# Create Python virtual environment
print_status "Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_success "Created virtual environment"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -e ".[dev,test]"

# Install development tools
print_status "Installing development tools..."
pip install black isort flake8 mypy pytest pytest-cov

# Build the Rust extension
print_status "Building Rust extension..."
cd uacalc-py
maturin develop --release
cd ..

# Run basic tests
print_status "Running basic tests..."
python -m pytest tests/python/ -v --tb=short

print_success "Setup completed successfully!"
print_status "To activate the virtual environment in the future, run:"
echo "source .venv/bin/activate"

print_status "To build the extension for development, run:"
echo "cd uacalc-py && maturin develop"

print_status "To run tests, run:"
echo "python -m pytest tests/python/"

print_status "To format code, run:"
echo "black python/ tests/python/"
echo "isort python/ tests/python/"

print_status "To check code quality, run:"
echo "flake8 python/ tests/python/"
echo "mypy python/"

print_success "Development environment is ready!"

