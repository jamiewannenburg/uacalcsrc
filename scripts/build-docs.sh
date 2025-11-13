#!/bin/bash
# Build documentation for both Rust crates
# Usage: ./scripts/build-docs.sh [--open]

set -e

OPEN_DOCS=false
if [[ "$1" == "--open" ]]; then
    OPEN_DOCS=true
fi

echo "Building Rust documentation for main crate..."
cargo doc --no-deps --all-features

echo "Building Rust documentation for Python bindings..."
cd uacalc_lib
cargo doc --no-deps --all-features
cd ..

if [ "$OPEN_DOCS" = true ]; then
    echo "Opening documentation in browser..."
    if command -v xdg-open > /dev/null; then
        xdg-open target/doc/uacalc/index.html
    elif command -v open > /dev/null; then
        open target/doc/uacalc/index.html
    else
        echo "Documentation built at: target/doc/uacalc/index.html"
        echo "Python bindings docs at: target/doc/uacalc_lib/index.html"
    fi
else
    echo "Documentation built successfully!"
    echo "Main crate docs: target/doc/uacalc/index.html"
    echo "Python bindings docs: target/doc/uacalc_lib/index.html"
fi

