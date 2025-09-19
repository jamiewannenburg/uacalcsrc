#!/bin/bash
# Comprehensive build script for all UACalc components

set -e

echo "Building all UACalc components..."
echo "=================================="

# Check if we're on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "Warning: You appear to be on Windows. Consider using build.ps1 for better Windows support."
    echo ""
fi

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

# 1. Build Java components
echo "1. Building Java components..."
echo "------------------------------"
if command -v ant &> /dev/null; then
    ant dist
    # Copy uacalc.jar to jars/ directory for compatibility tests
    if [[ -f "../dist/lib/uacalc.jar" ]]; then
        cp ../dist/lib/uacalc.jar jars/uacalc.jar
        echo "✓ Copied uacalc.jar to jars/ directory"
    fi
    # Compile JavaWrapper for compatibility tests
    if command -v javac &> /dev/null; then
        javac -cp "jars/*" scripts/JavaWrapper.java
        echo "✓ JavaWrapper compiled successfully"
    fi
    echo "✓ Java components built successfully"
else
    echo "⚠ Apache Ant not found. Skipping Java build."
    echo "  Install with: sudo apt install ant (Ubuntu/Debian)"
fi
echo ""

# 2. Build Rust core library
echo "2. Building Rust core library..."
echo "--------------------------------"
if command -v cargo &> /dev/null; then
    cargo build --release
    echo "✓ Rust core library built successfully"
else
    echo "✗ Rust not found. Please install Rust from https://rustup.rs"
    exit 1
fi
echo ""

# 3. Build Python extension (Rust bindings)
echo "3. Building Python extension..."
echo "------------------------------"
if ! command -v maturin &> /dev/null; then
    echo "Installing maturin..."
    pip install maturin
fi

cd uacalc-py
# Temporarily unset CONDA_PREFIX to avoid conflicts
unset CONDA_PREFIX
maturin build --release
maturin develop
cd ..
echo "✓ Python extension built successfully"
echo ""

# 4. Install pure Python package
echo "4. Installing pure Python package..."
echo "-----------------------------------"
cd python
pip install -e .
cd ..
echo "✓ Pure Python package installed successfully"
echo ""

# # 5. Run tests
# echo "5. Running tests..."
# echo "------------------"
# echo "Running Python tests..."
# python -m pytest tests/python/ -v --tb=short

# echo ""
# echo "Running Rust tests..."
# cargo test

echo ""
echo "Running setup verification..."
python scripts/test_setup.py

echo ""
echo "Running Java compatibility verification..."
python scripts/test_java_compatibility.py

echo ""
echo "=================================="
echo "🎉 All components built successfully!"
echo ""
echo "You can now:"
echo "  - Use the Python API: import uacalc"
echo "  - Use the Rust library: cargo run --example <example>"
echo "  - Use the Java JAR: java -jar ../dist/lib/uacalc.jar"
echo "  - Run Java compatibility tests: python -m pytest tests/python/test_java_compatibility.py"
echo ""
echo "For development:"
echo "  - Run Python tests: python -m pytest tests/python/"
echo "  - Run Rust tests: cargo test"
echo "  - Run Java compatibility tests: python -m pytest tests/python/test_java_compatibility.py"
echo "  - Build Java: ant dist"