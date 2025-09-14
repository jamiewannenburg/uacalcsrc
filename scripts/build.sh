#!/bin/bash
# Build script for UACalc

set -e

# Check if we're on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "Warning: You appear to be on Windows. Consider using build.ps1 for better Windows support."
    echo "To use PowerShell scripts:"
    echo "  1. Open PowerShell as Administrator"
    echo "  2. Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    echo "  3. Run: .\scripts\build.ps1"
    echo ""
fi

echo "Building UACalc..."

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Virtual environment not activated. Activating..."
    if [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
    else
        echo "Virtual environment not found. Please run setup.sh first."
        exit 1
    fi
fi

# Check if maturin is available
if ! command -v maturin &> /dev/null; then
    echo "maturin not found. Installing via pip..."
    pip install maturin
fi

# Change to uacalc-py directory where the Python package is located
echo "Changing to uacalc-py directory..."
cd uacalc-py

# Build the Rust extension
echo "Building Rust extension..."
if [[ "$1" == "--release" ]]; then
    maturin build --release
else
    maturin build
fi

# Install the extension in development mode
echo "Installing extension in development mode..."
# Temporarily unset CONDA_PREFIX to avoid conflicts with virtual environment
unset CONDA_PREFIX
maturin develop

# Return to root directory
cd ..

# Install the pure Python package
echo "Installing pure Python package..."
cd python
pip install -e .
cd ..

# Run tests
echo "Running tests..."
python -m pytest tests/python/ -v

echo "Build completed successfully!"

