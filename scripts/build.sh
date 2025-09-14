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
    echo "maturin not found. Installing..."
    cargo install maturin
fi

# Build the Rust extension
echo "Building Rust extension..."
if [[ "$1" == "--release" ]]; then
    maturin build --release
else
    maturin build
fi

# Install the extension in development mode
echo "Installing extension in development mode..."
maturin develop

# Run tests
echo "Running tests..."
python -m pytest tests/python/ -v

echo "Build completed successfully!"

