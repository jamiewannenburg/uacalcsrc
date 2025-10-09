# Java Wrapper Directory

This directory contains command-line wrapper classes that expose Java UACalc functionality for testing and validation against Rust/Python implementations.

## Purpose

The `java_wrapper` directory serves as a bridge between the original Java implementation and the new Rust/Python implementation by providing:

1. **Command-line interfaces** for Java classes
2. **Standardized output formats** for comparison testing
3. **Validation tools** to ensure Rust/Python implementations produce equivalent results
4. **Test harnesses** for automated comparison testing

## Directory Structure

The directory structure mirrors the Java `org/uacalc/` package structure:

```
java_wrapper/
├── alg/                    # Algebra structures
│   ├── op/                # Operations
│   ├── conlat/            # Congruence lattices
│   ├── sublat/            # Subalgebra lattices
│   └── parallel/          # Parallel computation
├── element/               # Element representations
├── eq/                    # Equation handling
├── example/               # Example implementations
├── fplat/                 # Partially defined lattices
├── group/                 # Group theory
├── io/                    # Input/output operations
├── lat/                   # Lattice theory
├── terms/                 # Term structures
└── util/                  # Utility functions
    └── virtuallist/       # Virtual list implementations
```

## Implementation Plan

Each wrapper class will:

1. **Accept command-line arguments** for configuration
2. **Load/create appropriate Java objects** from the original implementation
3. **Execute the requested operation**
4. **Output results in a standardized format** (JSON, CSV, or plain text)
5. **Handle errors gracefully** with informative messages

## Usage Example

```bash
# Create a small algebra and output its properties
java -cp uacalc.jar org.uacalc.alg.SmallAlgebra create 4 "meet,join"

# Find subalgebras of an algebra
java -cp uacalc.jar org.uacalc.alg.SmallAlgebra subalgebras algebra_001

# Compare with Rust implementation
./target/release/uacalc alg create 4 "meet,join" > rust_output.txt
java -cp uacalc.jar org.uacalc.alg.SmallAlgebra create 4 "meet,join" > java_output.txt
diff rust_output.txt java_output.txt
```

## Testing Strategy

1. **Unit Tests**: Each wrapper will have corresponding test cases
2. **Integration Tests**: Compare outputs between Java, Rust, and Python
3. **Performance Tests**: Benchmark implementations against each other
4. **Regression Tests**: Ensure changes don't break compatibility

## File Naming Convention

- Wrapper classes use the same name as the original Java class
- Each wrapper includes a `main` method for command-line execution
- Additional utility classes may be added with descriptive names

## Future Development

This directory will be populated incrementally as the Rust/Python implementation progresses. Priority will be given to:

1. Core algebra operations
2. Lattice computations
3. Congruence finding algorithms
4. Subalgebra enumeration
5. Term operations

Each wrapper will be created as needed for testing and validation purposes.
