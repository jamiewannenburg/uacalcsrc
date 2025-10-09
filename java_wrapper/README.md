# Java Wrapper Directory

This directory contains command-line wrapper classes that expose Java UACalc functionality for testing and validation against Rust/Python implementations.

## Purpose

The `java_wrapper` directory serves as a bridge between the original Java implementation and the new Rust/Python implementation by providing:

1. **Command-line interfaces** for Java classes
2. **Standardized output formats** for comparison testing
3. **Validation tools** to ensure Rust/Python implementations produce equivalent results
4. **Test harnesses** for automated comparison testing

## Directory Structure

The directory structure follows Option 3 (Build Output Directory) pattern:

```
java_wrapper/
├── src/                    # Source files (mirrors Java org/uacalc/ package structure)
│   ├── alg/               # Algebra structures
│   │   ├── op/            # Operations
│   │   ├── conlat/        # Congruence lattices
│   │   ├── sublat/        # Subalgebra lattices
│   │   └── parallel/      # Parallel computation
│   ├── element/           # Element representations
│   ├── eq/                # Equation handling
│   ├── example/           # Example implementations
│   ├── fplat/             # Partially defined lattices
│   ├── group/             # Group theory
│   ├── io/                # Input/output operations
│   ├── lat/               # Lattice theory
│   ├── terms/             # Term structures
│   └── util/              # Utility functions
│       └── virtuallist/   # Virtual list implementations
├── build/                  # Build output directory
│   ├── classes/           # Compiled .class files
│   └── scripts/           # Executable wrapper scripts
└── README.md              # This documentation
```

## Build Process

The Java wrappers are integrated with the main Ant build system:

### Compilation

```bash
# Compile Java wrapper classes
ant compile-wrappers

# Create executable wrapper scripts
ant create-wrapper-scripts

# Test wrapper scripts
ant test-wrappers

# Clean wrapper build files
ant clean-wrappers
```

### Build Targets

- **`compile-wrappers`**: Compiles all Java wrapper classes to `java_wrapper/build/classes/`
- **`create-wrapper-scripts`**: Creates executable shell scripts in `java_wrapper/build/scripts/`
- **`test-wrappers`**: Tests that wrapper scripts are properly created
- **`clean-wrappers`**: Removes all build artifacts

### Integration with Main Build

The wrapper compilation is automatically included in the main distribution build:

```bash
# Build everything including wrappers
ant dist

# This runs: dist-jar + compile-dist-work + compile-wrappers
```

## Implementation Plan

Each wrapper class will:

1. **Accept command-line arguments** for configuration
2. **Load/create appropriate Java objects** from the original implementation
3. **Execute the requested operation**
4. **Output results in a standardized format** (JSON, CSV, or plain text)
5. **Handle errors gracefully** with informative messages

## Usage Examples

### Direct Class Usage

```bash
# Create a small algebra and output its properties
java -cp java_wrapper/build/classes:build/classes:jars/* org.uacalc.alg.SmallAlgebra create 4 "meet,join"

# Find subalgebras of an algebra
java -cp java_wrapper/build/classes:build/classes:jars/* org.uacalc.alg.SmallAlgebra subalgebras algebra_001
```

### Script Usage (After Running `ant create-wrapper-scripts`)

```bash
# Using executable wrapper scripts
./java_wrapper/build/scripts/small-algebra create 4 "meet,join"
./java_wrapper/build/scripts/small-algebra subalgebras algebra_001
```

### Compatibility Testing

```bash
# Compare with Rust implementation
./target/release/uacalc alg create 4 "meet,join" > rust_output.txt
./java_wrapper/build/scripts/small-algebra create 4 "meet,join" > java_output.txt
diff rust_output.txt java_output.txt

# Compare with Python implementation
python -c "import uacalc_lib; ..." > python_output.txt
diff java_output.txt python_output.txt
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

## Adding New Wrapper Classes

To add a new wrapper class:

1. **Create the Java source file** in the appropriate `java_wrapper/src/` subdirectory
2. **Follow the naming convention**: Use the same name as the original Java class
3. **Implement the main method** with command-line argument handling
4. **Add to build script** (optional): Add a `create-wrapper` task in `build.xml` for automatic script generation

### Example: Adding SmallAlgebra Wrapper

1. Create `java_wrapper/src/alg/SmallAlgebra.java`
2. Implement command-line interface
3. Run `ant compile-wrappers` to compile
4. Run `ant create-wrapper-scripts` to create executable script

### Build Script Integration

To automatically generate wrapper scripts, add this to `build.xml` in the `create-wrapper-scripts` target:

```xml
<create-wrapper classname="alg.SmallAlgebra" scriptname="small-algebra"/>
<create-wrapper classname="lat.BasicLattice" scriptname="basic-lattice"/>
```

## Future Development

This directory will be populated incrementally as the Rust/Python implementation progresses. Priority will be given to:

1. Core algebra operations
2. Lattice computations
3. Congruence finding algorithms
4. Subalgebra enumeration
5. Term operations

Each wrapper will be created as needed for testing and validation purposes.
