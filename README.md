# UACalc Rust/Python Project

This is the Rust/Python implementation of the Universal Algebra Calculator (UACalc).

## Project Structure

- `uacalc_app/` - Main Rust application library
- `uacalc_lib/` - Python bindings for the Rust library using PyO3
- `python/uacalc/` - Python package structure
- `org/uacalc/` - Original Java implementation (for reference)

## Building

### Rust Application
```bash
cargo build
```

### Python Bindings
```bash
maturin develop
```

## Usage

### Rust
```rust
use uacalc_app::alg::*;
// Use the algebra structures
```

### Python
```python
import uacalc
# Use the Python bindings
```

## Development

This project uses a workspace structure with:
- Rust application code in `uacalc_app/src/`
- Python bindings in `uacalc_lib/src/`
- Python package in `python/uacalc/`

The structure mirrors the original Java implementation in `org/uacalc/` but excludes UI components.