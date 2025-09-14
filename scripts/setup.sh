#!/bin/bash
# Setup script for UACalc development environment

set -e

# Check if we're on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "Warning: You appear to be on Windows. Consider using setup.ps1 for better Windows support."
    echo "To use PowerShell scripts:"
    echo "  1. Open PowerShell as Administrator"
    echo "  2. Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    echo "  3. Run: .\scripts\setup.ps1"
    echo ""
fi

echo "Setting up UACalc development environment..."

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3.8+ from https://python.org"
    exit 1
fi

python_version=$(python3 --version 2>&1)
echo "Found: $python_version"

# Create virtual environment
if [ -d ".venv" ]; then
    echo "Virtual environment already exists."
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip

# Install from uacalc-py directory
echo "Installing Python package from uacalc-py..."
cd uacalc-py
pip install -e .
pip install -e ".[dev]"
cd ..

# Install the pure Python package
echo "Installing pure Python package..."
cd python
pip install -e .
cd ..

# Check Rust
echo "Checking Rust installation..."
if ! command -v rustc &> /dev/null; then
    echo "Rust not found. Please install Rust from https://rustup.rs"
    echo "Run: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

rust_version=$(rustc --version)
echo "Found: $rust_version"

# Install maturin if not present
if ! command -v maturin &> /dev/null; then
    echo "Installing maturin..."
    pip install maturin
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source .venv/bin/activate"
echo "2. Build Rust extension: cd uacalc-py && maturin develop"
echo "3. Run tests: python -m pytest tests/python/"
echo ""
echo "Note: Always run maturin commands from the uacalc-py directory!"

