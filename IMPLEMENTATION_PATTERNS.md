# UACalc Rust Translation Implementation Patterns

This document establishes the patterns and best practices for translating Java classes to Rust with Python bindings.

## 1. Java CLI Wrapper Pattern

### File Structure
- **Location**: `java_wrapper/src/[package]/[ClassName]Wrapper.java`
- **Package**: `java_wrapper.src.[package]` (matches directory structure)
- **Base Class**: Extends `WrapperBase` (imported from `java_wrapper.src.WrapperBase`)

### Template Structure
```java
/* [ClassName]Wrapper.java - CLI wrapper for org.uacalc.[package].[ClassName]
 * 
 * This wrapper exposes all public methods of the [ClassName] class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.[package];

import java.util.*;
import org.uacalc.[package].[ClassName];
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the [ClassName] class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class [ClassName]Wrapper extends WrapperBase {
    
    /**
     * Main entry point for the [ClassName] CLI wrapper.
     */
    public static void main(String[] args) {
        [ClassName]Wrapper wrapper = new [ClassName]Wrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("[ClassName] wrapper failed", e);
        }
    }
    
    /**
     * Run the [ClassName] CLI wrapper with the given arguments.
     */
    @Override
    public void run(String[] args) throws Exception {
        if (args.length == 0) {
            showUsage();
            return;
        }
        
        Map<String, String> options = parseArgs(args);
        String command = options.get("arg0");
        
        if (command == null) {
            showUsage();
            return;
        }
        
        switch (command) {
            case "help":
                showUsage();
                break;
                
            // Add command cases here
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    // Add handler methods here
    
    /**
     * Show usage information for the [ClassName] wrapper.
     */
    private void showUsage() {
        String[] examples = {
            // Add example commands here
        };
        
        showUsage("[ClassName]", 
                 "CLI wrapper for org.uacalc.[package].[ClassName] operations", 
                 examples);
    }
}
```

### Key Points
- Always extend `WrapperBase`
- Use `@Override` for the `run` method
- Use `parseArgs()` to parse command line arguments
- Use `getRequiredArg()`, `getOptionalArg()`, `getIntArg()`, `getBoolArg()` for argument parsing
- Use `handleSuccess()` and `handleError()` for responses
- Always include a `help` command
- Include a `test` command that runs basic functionality tests
- **Use `status` field instead of `result` field** in JSON responses to avoid conflicts with test comparison logic
- **Handle package-private field access** by storing input data during construction
- **Ensure proper JSON serialization** by updating `WrapperBase.java` to handle `List` objects correctly

## 2. Rust Implementation Pattern

### File Structure
- **Location**: `src/[module]/[submodule]/mod.rs` or separate `[class_name].rs`
- **Module**: `[module]::[submodule]::[ClassName]`

### Error Handling Pattern
```rust
impl [ClassName] {
    /// Method with proper error handling
    pub fn method_safe(&mut self, param: Type) -> Result<(), String> {
        // Validation logic
        if invalid_condition {
            return Err("Error message".to_string());
        }
        // Implementation
        Ok(())
    }
    
    /// Method with panic for compatibility (use sparingly)
    pub fn method_panic(&mut self, param: Type) {
        if invalid_condition {
            panic!("Error message");
        }
        // Implementation
    }
    
    /// Constructor with proper error handling
    pub fn new_safe(param: Type) -> Result<Self, String> {
        // Validation and construction
        Ok(instance)
    }
    
    /// Constructor with panic for compatibility
    pub fn new(param: Type) -> Self {
        // Use new_safe internally or implement directly
    }
}
```

### Key Points
- Provide both `_safe` and `_panic` versions of methods that can fail
- Use `Result<(), String>` for error handling
- Use `panic!` only for truly unrecoverable errors
- Implement proper trait implementations (`Ord`, `PartialOrd`, `Eq`, `PartialEq`, `Hash`, `Display`)
- Use `once_cell::sync::Lazy` for static constants
- Use `Mutex<HashMap>` for thread-safe static mutable state

## 3. Python Bindings Pattern

### File Structure
- **Location**: `uacalc_lib/src/[module].rs`
- **Class**: `Py[ClassName]` (internal), `[ClassName]` (exported)

### Loading Algebras in Python Tests

When testing operations that require algebras, use the `AlgebraReader` to load algebra files:

```python
import os
import uacalc_lib

def load_algebra(algebra_path: str):
    """Load an algebra from a .ua file."""
    if not os.path.exists(algebra_path):
        raise FileNotFoundError(f"Algebra file {algebra_path} not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(algebra_path)
    return reader.read_algebra_file()

# Example usage in tests
def test_with_algebra(self):
    # Load algebra
    alg = load_algebra("resources/algebras/cyclic3.ua")
    
    # Use algebra for testing
    VariableImp = uacalc_lib.terms.VariableImp
    x = VariableImp("x")
    
    result = x.eval(alg, {"x": 0})
    self.assertEqual(result, 0)
```

#### Common Test Algebras

Available test algebras in `resources/algebras/`:
- `cyclic2.ua` - 2-element cyclic group
- `cyclic3.ua` - 3-element cyclic group
- `n5.ua` - 5-element lattice (pentagon)
- `m3.ua` - 3-element lattice (diamond)

#### Pattern for Skipping Missing Algebras

```python
def test_with_optional_algebra(self):
    algebra_path = "resources/algebras/cyclic3.ua"
    if not os.path.exists(algebra_path):
        self.skipTest(f"Algebra file {algebra_path} not found")
    
    # Test code here
```

#### Pattern for Testing Multiple Algebras

```python
def test_with_multiple_algebras(self):
    algebra_files = [
        "resources/algebras/cyclic2.ua",
        "resources/algebras/cyclic3.ua",
        "resources/algebras/n5.ua",
    ]
    
    for algebra_path in algebra_files:
        if not os.path.exists(algebra_path):
            continue
        
        # Load and test with each algebra
        alg = load_algebra(algebra_path)
        # ... test operations
```

### Template Structure
```rust
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::[module]::*;

/// Python wrapper for [ClassName]
#[pyclass]
pub struct Py[ClassName] {
    inner: uacalc::[module]::[ClassName],
}

#[pymethods]
impl Py[ClassName] {
    /// Create a new [ClassName]
    #[new]
    #[pyo3(signature = (param1, param2, optional_param=None))]
    fn new(param1: Type1, param2: Type2, optional_param: Option<Type3>) -> PyResult<Self> {
        match uacalc::[module]::[ClassName]::new_safe(param1, param2, optional_param.unwrap_or(default)) {
            Ok(inner) => Ok(Py[ClassName] { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Method with proper error handling
    fn method(&mut self, param: Type) -> PyResult<()> {
        match self.inner.method_safe(param) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    // Add other methods here
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("[ClassName]({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &Py[ClassName]) -> bool {
        self.inner == other.inner
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
}

pub fn register_[module]_module(py: Python, m: &PyModule) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<Py[ClassName]>()?;
    
    // Export only clean names (without Py prefix)
    m.add("[ClassName]", m.getattr("Py[ClassName]")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("Py[ClassName]")?;
    
    Ok(())
}
```

### Key Points
- Always use `PyValueError::new_err()` for validation errors
- Use `PyResult<T>` for methods that can fail
- Implement Python magic methods (`__str__`, `__repr__`, `__eq__`, `__hash__`, comparison operators)
- Use `#[pyo3(signature = (...))]` for default parameters
- Always provide both `_safe` and regular versions of methods
- **Naming Convention**: Use `Py[ClassName]` for internal Rust struct names, but export ONLY clean `[ClassName]` names to Python
- **Module Registration**: Always export clean names and remove Py* names to avoid confusion
- **Clean API**: Only clean class names are available to Python users - no Py* prefixes

## 4. Testing Pattern

### Rust Tests
```rust
#[test]
fn test_[method_name]() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.[package].[ClassName]Wrapper",
        ["command", "--arg1", "value1", "--arg2", "value2"],
        || {
            let instance = [ClassName]::new(param1, param2);
            json!({
                "command": "command",
                "param1": param1,
                "param2": param2,
                "status": instance.method()  // Use 'status' not 'result'
            })
        }
    );
}
```

### Python Tests
```python
def test_[method_name](self):
    """Test [method description]."""
    # Import through uacalc_lib module (direct imports don't work)
    import uacalc_lib
    [ClassName] = uacalc_lib.[module].[ClassName]
    
    instance = [ClassName](param1, param2)
    java_result = run_java_wrapper("command", ["--arg1", "value1", "--arg2", "value2"])
    
    assert instance.method() == java_result["data"]["status"]  # Use 'status' not 'result'
```

### Python Tests with Algebras
```python
import os
import uacalc_lib

def test_operation_with_algebra(self):
    """Test operation evaluation with loaded algebra."""
    # Load algebra
    algebra_path = "resources/algebras/cyclic3.ua"
    if not os.path.exists(algebra_path):
        self.skipTest(f"Algebra file {algebra_path} not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(algebra_path)
    alg = reader.read_algebra_file()
    
    # Create and test operation
    VariableImp = uacalc_lib.terms.VariableImp
    x = VariableImp("x")
    
    # Test evaluation
    result = x.eval(alg, {"x": 1})
    self.assertEqual(result, 1)
```

### Key Points
- Use `compare_with_java!` macro for Rust tests
- Use `run_java_wrapper()` function for Python tests
- Test both success and error cases
- Test all public methods
- Test edge cases and validation

## 5. Test Utilities and Algebra Loading

### Using Test Utilities

The project includes comprehensive test utilities in `python/uacalc/tests/test_utils.py`:

```python
from python.uacalc.tests.test_utils import (
    TestConfig,
    TestHarness,
    MemoryMonitor,
    TestDataGenerator,
    timeout,
    memory_limit,
)

# Use in tests
@timeout(30.0)
@memory_limit(1024)
def test_with_monitoring(self):
    config = TestConfig(default_timeout=30.0, memory_limit_mb=1024)
    with TestHarness(config) as harness:
        # Run tests with monitoring
        pass
```

### Reusable Algebra Loading Helper

Create a helper function in test files or conftest.py:

```python
import os
import uacalc_lib
from typing import Optional

def load_test_algebra(name: str, skip_if_missing: bool = True):
    """
    Load a test algebra from resources/algebras/
    
    Args:
        name: Algebra filename (with or without .ua extension)
        skip_if_missing: If True, skip test when algebra not found
        
    Returns:
        Loaded algebra object
        
    Raises:
        FileNotFoundError: If algebra not found and skip_if_missing=False
        unittest.SkipTest: If algebra not found and skip_if_missing=True
    """
    if not name.endswith('.ua'):
        name = f"{name}.ua"
    
    algebra_path = f"resources/algebras/{name}"
    
    if not os.path.exists(algebra_path):
        if skip_if_missing:
            import unittest
            raise unittest.SkipTest(f"Algebra file {algebra_path} not found")
        else:
            raise FileNotFoundError(f"Algebra file {algebra_path} not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(algebra_path)
    return reader.read_algebra_file()

# Usage in tests
def test_operation_with_cyclic3(self):
    alg = load_test_algebra("cyclic3")
    # Use algebra for testing
```

### Testing Pattern with Multiple Algebras

```python
import pytest
from typing import List

# Parameterized test for multiple algebras
@pytest.mark.parametrize("algebra_name", [
    "cyclic2",
    "cyclic3", 
    "n5",
    "m3",
])
def test_operation_with_various_algebras(algebra_name: str):
    """Test operation with different algebra types."""
    try:
        alg = load_test_algebra(algebra_name, skip_if_missing=False)
    except FileNotFoundError:
        pytest.skip(f"Algebra {algebra_name} not found")
    
    # Test with loaded algebra
    VariableImp = uacalc_lib.terms.VariableImp
    x = VariableImp("x")
    
    # Evaluate for each element in algebra
    for i in range(alg.cardinality()):
        result = x.eval(alg, {"x": i})
        assert result == i
```

### Creating conftest.py for Shared Fixtures

Create `python/uacalc/tests/conftest.py` for shared test fixtures:

```python
"""
Pytest configuration and shared fixtures for UACalc tests.

This module makes fixtures from test_utils available to all test files
in the tests directory and provides algebra loading utilities.
"""

import os
import pytest
import uacalc_lib
from typing import Optional

# Import all fixtures from test_utils to make them available
from test_utils import (
    test_config,
    test_harness, 
    memory_monitor,
    TestConfig,
    TestHarness,
    TestDataGenerator,
    JavaCliOutput,
    MemoryMonitor
)


def load_test_algebra(name: str, skip_if_missing: bool = True):
    """
    Load a test algebra from resources/algebras/
    
    Args:
        name: Algebra filename (with or without .ua extension)
        skip_if_missing: If True, skip test when algebra not found
        
    Returns:
        Loaded algebra object
        
    Raises:
        FileNotFoundError: If algebra not found and skip_if_missing=False
        unittest.SkipTest: If algebra not found and skip_if_missing=True
    """
    if not name.endswith('.ua'):
        name = f"{name}.ua"
    
    algebra_path = f"resources/algebras/{name}"
    
    if not os.path.exists(algebra_path):
        if skip_if_missing:
            import unittest
            raise unittest.SkipTest(f"Algebra file {algebra_path} not found")
        else:
            raise FileNotFoundError(f"Algebra file {algebra_path} not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(algebra_path)
    return reader.read_algebra_file()


@pytest.fixture
def cyclic2_algebra():
    """Fixture providing cyclic2 algebra."""
    if not os.path.exists("resources/algebras/cyclic2.ua"):
        pytest.skip("cyclic2.ua not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file("resources/algebras/cyclic2.ua")
    return reader.read_algebra_file()


@pytest.fixture
def cyclic3_algebra():
    """Fixture providing cyclic3 algebra."""
    if not os.path.exists("resources/algebras/cyclic3.ua"):
        pytest.skip("cyclic3.ua not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
    return reader.read_algebra_file()


@pytest.fixture(params=["cyclic2", "cyclic3", "n5"])
def test_algebra(request):
    """Parameterized fixture for multiple algebras."""
    algebra_name = request.param
    algebra_path = f"resources/algebras/{algebra_name}.ua"
    
    if not os.path.exists(algebra_path):
        pytest.skip(f"{algebra_name}.ua not found")
    
    AlgebraReader = uacalc_lib.io.AlgebraReader
    reader = AlgebraReader.new_from_file(algebra_path)
    return reader.read_algebra_file()


@pytest.fixture
def algebra_loader():
    """Fixture providing algebra loading function."""
    def load_algebra(name: str):
        """Load algebra by name."""
        return load_test_algebra(name, skip_if_missing=False)
    return load_algebra


# Re-export fixtures so they're available to all test files
__all__ = [
    'test_config',
    'test_harness',
    'memory_monitor',
    'TestConfig',
    'TestHarness', 
    'TestDataGenerator',
    'JavaCliOutput',
    'MemoryMonitor',
    'load_test_algebra',
    'cyclic2_algebra',
    'cyclic3_algebra',
    'test_algebra',
    'algebra_loader'
]

# Use in tests:
# def test_with_fixture(cyclic3_algebra):
#     alg = cyclic3_algebra
#     # Use algebra
#
# def test_with_loader(algebra_loader):
#     alg = algebra_loader("cyclic2")
#     # Use algebra
#
# def test_with_helper():
#     from conftest import load_test_algebra
#     alg = load_test_algebra("cyclic3")
#     # Use algebra
```

### Complete Test Example with Algebras

```python
import unittest
import os
import uacalc_lib

class TestTermOperations(unittest.TestCase):
    """Test term operations with loaded algebras."""
    
    @classmethod
    def setUpClass(cls):
        """Load algebras once for all tests."""
        cls.algebras = {}
        
        for name in ["cyclic2", "cyclic3", "n5"]:
            path = f"resources/algebras/{name}.ua"
            if os.path.exists(path):
                AlgebraReader = uacalc_lib.io.AlgebraReader
                reader = AlgebraReader.new_from_file(path)
                cls.algebras[name] = reader.read_algebra_file()
    
    def test_variable_eval_cyclic3(self):
        """Test variable evaluation with cyclic3."""
        if "cyclic3" not in self.algebras:
            self.skipTest("cyclic3 algebra not loaded")
        
        alg = self.algebras["cyclic3"]
        VariableImp = uacalc_lib.terms.VariableImp
        x = VariableImp("x")
        
        # Test each element
        for i in range(3):
            result = x.eval(alg, {"x": i})
            self.assertEqual(result, i)
    
    def test_all_algebras(self):
        """Test with all available algebras."""
        VariableImp = uacalc_lib.terms.VariableImp
        x = VariableImp("x")
        
        for name, alg in self.algebras.items():
            with self.subTest(algebra=name):
                result = x.eval(alg, {"x": 0})
                self.assertEqual(result, 0)
```

## 6. Compilation and Build Pattern

### Build Commands
```bash
# Compile Java wrapper (if using ant)
ant compile-wrappers

# OR manually compile Java wrapper
javac -cp "java_wrapper/src:org" java_wrapper/src/WrapperBase.java java_wrapper/src/[package]/[ClassName]Wrapper.java

# Test wrapper functionality
java -cp "java_wrapper/build/classes:build/classes:org:jars/*" java_wrapper.src.[package].[ClassName]Wrapper help

# Compile Rust library
cargo build --release

# Run Rust tests
cargo test [module]::[submodule]::[class_name] --test mod

# Run doctests specifically
cargo test --doc

# Build Python bindings
maturin develop

# Run Python tests
pytest python/uacalc/tests/test_[class_name].py -v
```


### Key Points
- Always compile and test all components
- Fix warnings before marking as complete
- Ensure all tests pass
- Verify cross-language compatibility
- **Update `WrapperBase.java`** to handle `List` serialization properly
- **Run doctests separately** to catch compilation issues early
- **Include `org` directory in classpath** for Java wrapper compilation and execution
- **Use `--key value` format for test arguments** instead of `--key=value` format

### Required WrapperBase.java Updates

The `WrapperBase.java` file must be updated to properly serialize Java `List` objects as JSON arrays:

```java
// Add this to the serializeObject method in WrapperBase.java
} else if (obj instanceof List) {
    List<?> list = (List<?>) obj;
    StringBuilder sb = new StringBuilder();
    sb.append("[");
    for (int i = 0; i < list.size(); i++) {
        if (i > 0) sb.append(", ");
        sb.append(serializeObject(list.get(i)));
    }
    sb.append("]");
    return sb.toString();
} else if (obj instanceof Map) {
    // ... existing Map handling code
```

## 7. Documentation Pattern

### Rust Documentation
```rust
/// Brief description of the struct/function.
/// 
/// Longer description if needed.
/// 
/// # Arguments
/// * `param1` - Description of parameter 1
/// * `param2` - Description of parameter 2
/// 
/// # Returns
/// * `Ok(T)` - Description of success case
/// * `Err(String)` - Description of error case
/// 
/// # Panics
/// Panics if [condition] (only for panic versions)
/// 
/// # Examples
/// ```
/// // For Result-returning methods, use .unwrap() not ? in doctests
/// let instance = ClassName::new_safe("example", 2).unwrap();
/// assert_eq!(instance.method(), expected_result);
/// ```
```

### Key Points
- Use proper Rust documentation format
- Document all public methods
- Include examples where helpful
- Document error conditions
- Use `# Arguments`, `# Returns`, `# Panics` sections

## 8. Python Binding Naming Convention

### Clean Export Names Only
- **Internal Rust Names**: Use `Py[ClassName]` for the actual PyO3 struct names
- **Exported Python Names**: Export ONLY clean `[ClassName]` names without the `Py` prefix
- **Module Registration**: Always export clean names and remove Py* names to avoid confusion

### Example Implementation
```rust
// Internal struct name with Py prefix
#[pyclass]
pub struct PySimpleList { ... }

// Module registration with clean export only
pub fn register_util_module(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySimpleList>()?;
    // Export clean name without Py prefix
    m.add("SimpleList", m.getattr("PySimpleList")?)?;
    // Remove Py* name to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PySimpleList")?;
    Ok(())
}
```

### Python Usage
```python
# Clean import (only option available)
from uacalc_lib.util import SimpleList
sl = SimpleList()

# Py* names are NOT available - this will raise AttributeError
# from uacalc_lib.util import PySimpleList  # This will fail
```

## 9. Common Pitfalls to Avoid

1. **Don't use panics in Python bindings** - Always use proper error handling
2. **Don't skip validation** - Always validate inputs in both Rust and Python
3. **Don't ignore warnings** - Fix all compilation warnings
4. **Don't skip tests** - Test all public methods and edge cases
5. **Don't forget thread safety** - Use proper synchronization for static mutable state
6. **Don't hardcode paths** - Use relative paths and proper module structure
7. **Don't skip error handling** - Always handle errors gracefully
8. **Don't forget clean exports** - Always export clean names and remove Py* names to avoid confusion
9. **Don't use `?` operator in doctests** - Use `.unwrap()` in doctest examples instead
10. **Don't assume Java behavior matches Rust** - Always verify exact behavior compatibility
11. **Don't forget to implement `Hash` trait manually** - When using `HashSet` in structs
12. **Don't use `result` field in test JSON** - Use `status` field to avoid conflicts with comparison logic
13. **Don't forget to handle `List` serialization in Java** - Update `WrapperBase` for proper JSON arrays
14. **Don't forget the `org` directory in Java classpath** - Always include it for compilation and execution
15. **Don't use `--key=value` format in tests** - Use `--key value` format instead
16. **Don't assume Java wrapper data is already parsed** - Parse the `data` field twice in Python tests
17. **Don't make Rust struct fields private if accessed by Python** - Make them public for Python bindings

## 10. File Naming Conventions

- **Java Wrapper**: `[ClassName]Wrapper.java`
- **Rust Implementation**: `[class_name].rs` or in `mod.rs`
- **Python Tests**: `test_[class_name].py`
- **Rust Tests**: `[class_name]_tests.rs`

## 11. Module Registration

### In `uacalc_lib/src/lib.rs`
```rust
// [Module] module
let [module]_module = PyModule::new(_py, "[module]")?;
[module]::register_[module]_module(_py, [module]_module)?;
m.add_submodule([module]_module)?;
```

### In `uacalc_lib/src/[module].rs`
```rust
pub fn register_[module]_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Py[ClassName]>()?;
    // Add other classes here
    Ok(())
}
```

## 12. Critical Implementation Issues and Solutions

### Issue 1: Doctest Compilation Failures

**Problem**: Doctests using the `?` operator fail to compile because the containing function doesn't return `Result`.

**Solution**: Always use `.unwrap()` in doctest examples instead of `?`.

```rust
// ❌ WRONG - Causes compilation error
/// # Examples
/// ```
/// let result = ClassName::new_safe("param")?;
/// ```

// ✅ CORRECT - Compiles and runs
/// # Examples
/// ```
/// let result = ClassName::new_safe("param").unwrap();
/// ```
```

### Issue 2: Java vs Rust Behavior Mismatch

**Problem**: Java and Rust implementations may have subtle behavioral differences that cause test failures.

**Example**: Java's `splitOffExtension` returns `null` for both name and extension when no extension exists, but Rust initially returned empty strings.

**Solution**: Always verify exact behavior compatibility by testing edge cases.

```rust
// ❌ WRONG - Assumes behavior without verification
pub fn split_off_extension(path: &Path) -> (String, String) {
    // Returns ("filename", "") for no extension
}

// ✅ CORRECT - Matches Java behavior exactly
pub fn split_off_extension(path: &Path) -> (Option<String>, Option<String>) {
    // Returns (None, None) for no extension to match Java's null, null
}
```

### Issue 3: HashSet Hash Implementation

**Problem**: `HashSet` doesn't implement `Hash` trait, causing compilation errors when the struct containing it needs to implement `Hash`.

**Solution**: Manually implement `Hash` trait by converting to sorted collection.

```rust
// ❌ WRONG - Compilation error
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct ExtFileFilter {
    exts: HashSet<String>,  // HashSet doesn't implement Hash
    description: String,
}

// ✅ CORRECT - Manual Hash implementation
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExtFileFilter {
    exts: HashSet<String>,
    description: String,
}

impl Hash for ExtFileFilter {
    fn hash<H: Hasher>(&self, state: &mut H) {
        // Convert HashSet to sorted Vec for consistent hashing
        let mut sorted_exts: Vec<&String> = self.exts.iter().collect();
        sorted_exts.sort();
        sorted_exts.hash(state);
        self.description.hash(state);
    }
}
```

### Issue 4: Test JSON Field Conflicts

**Problem**: Using `result` field in test JSON causes conflicts with the `compare_outputs` macro logic.

**Solution**: Use `status` field instead of `result` field in test JSON.

```rust
// ❌ WRONG - Causes comparison conflicts
json!({
    "command": "method_name",
    "result": actual_result  // Conflicts with macro logic
})

// ✅ CORRECT - Uses status field
json!({
    "command": "method_name", 
    "status": actual_result  // No conflicts
})
```

### Issue 5: Java List Serialization

**Problem**: Java `List` objects are serialized as strings instead of JSON arrays in the wrapper.

**Solution**: Update `WrapperBase.java` to handle `List` serialization properly.

```java
// Add to WrapperBase.java serializeObject method
} else if (obj instanceof List) {
    List<?> list = (List<?>) obj;
    StringBuilder sb = new StringBuilder();
    sb.append("[");
    for (int i = 0; i < list.size(); i++) {
        if (i > 0) sb.append(", ");
        sb.append(serializeObject(list.get(i)));
    }
    sb.append("]");
    return sb.toString();
```

### Issue 6: Python Import Path Issues

**Problem**: Python tests fail to import modules due to incorrect import paths.

**Solution**: Use the correct import pattern for Python bindings.

```python
# ❌ WRONG - Direct import fails
from uacalc_lib.io import ExtFileFilter

# ✅ CORRECT - Access through uacalc_lib module
import uacalc_lib
ExtFileFilter = uacalc_lib.io.ExtFileFilter
```

### Issue 7: Static Method Parameter Types

**Problem**: PyO3 static methods may have issues with parameter types.

**Solution**: Use `String` instead of `&str` for static method parameters.

```rust
// ❌ WRONG - May cause compilation issues
#[staticmethod]
fn static_method(path: &str) -> PyResult<...> { ... }

// ✅ CORRECT - Use String for static methods
#[staticmethod] 
fn static_method(path: String) -> PyResult<...> { ... }
```

### Issue 8: Java Wrapper Access Modifiers

**Problem**: Java wrapper can't access package-private fields from the original class.

**Solution**: Work around access limitations by returning input data or using reflection.

```java
// ❌ WRONG - Can't access package-private field
public List<String> getExtensions() {
    return this.filter.exts;  // exts is package-private
}

// ✅ CORRECT - Return the input extensions
public List<String> getExtensions() {
    return this.inputExtensions;  // Store input during construction
}
```

### Issue 9: Java Wrapper Classpath Issues

**Problem**: Java wrapper compilation and execution fails due to missing `org` directory in classpath.

**Solution**: Always include the `org` directory in the classpath for both compilation and execution.

```bash
# ❌ WRONG - Missing org directory
javac -cp "java_wrapper/src" java_wrapper/src/WrapperBase.java
java -cp "java_wrapper/build/classes:build/classes:jars/*" java_wrapper.src.util.LongListWrapper

# ✅ CORRECT - Include org directory
javac -cp "java_wrapper/src:org" java_wrapper/src/WrapperBase.java
java -cp "java_wrapper/build/classes:build/classes:org:jars/*" java_wrapper.src.util.LongListWrapper
```

### Issue 10: Java Argument Parsing Format

**Problem**: Java `WrapperBase.parseArgs()` method doesn't handle `--key=value` format correctly, causing tests to fail.

**Solution**: Use `--key value` format in tests instead of `--key=value` format.

```rust
// ❌ WRONG - Causes argument parsing failures
compare_with_java!(
    config,
    "java_wrapper.src.util.LongListWrapper",
    ["factorial", "--n=5"],  // This format fails
    || { ... }
);

// ✅ CORRECT - Use space-separated format
compare_with_java!(
    config,
    "java_wrapper.src.util.LongListWrapper", 
    ["factorial", "--n", "5"],  // This format works
    || { ... }
);
```

### Issue 11: Python Test JSON Parsing

**Problem**: Java wrapper returns nested JSON where the `data` field contains a JSON string, not a JSON object.

**Solution**: Parse the `data` field twice in Python tests.

```python
# ❌ WRONG - Assumes data is already a JSON object
java_result = run_java_wrapper("factorial", ["--n", "5"])
assert result == java_result["data"]["status"]  # Fails: data is a string

# ✅ CORRECT - Parse data field twice
def run_java_wrapper(command, args):
    # ... existing code ...
    output = json.loads(result.stdout)
    # Parse the data field again if it's a string
    if "data" in output and isinstance(output["data"], str):
        output["data"] = json.loads(output["data"])
    return output
```

### Issue 12: Rust Field Visibility for Python Bindings

**Problem**: Python bindings can't access private fields of Rust structs, causing compilation errors.

**Solution**: Make fields public that need to be accessed by Python bindings.

```rust
// ❌ WRONG - Private fields cause Python binding errors
pub struct IntTuples {
    tuple_length: usize,  // Private field
    base: usize,          // Private field
    size: i64,           // Private field
}

// ✅ CORRECT - Make fields public for Python access
pub struct IntTuples {
    pub tuple_length: usize,  // Public field
    pub base: usize,          // Public field  
    pub size: i64,           // Public field
}
```

### Issue 13: PyO3 API Compatibility Issues

**Problem**: Compilation failures due to PyO3 API version mismatches between module registration functions. Newer PyO3 versions use `&Bound<'_, PyModule>` while older code may still use `&PyModule`.

**Error Example**:
```
error[E0308]: mismatched types
  --> src/lib.rs:20:35
   |
20 |     alg::register_alg_module(_py, &alg_module)?;
   |     ------------------------      ^^^^^^^^^^^ expected `&PyModule`, found `&Bound<'_, PyModule>`
```

**Solution**: Update all module registration functions to use the newer `&Bound<'_, PyModule>` signature.

```rust
// ❌ WRONG - Old PyO3 API signature
pub fn register_alg_module(py: Python, m: &PyModule) -> PyResult<()> {
    // ...
}

// ✅ CORRECT - New PyO3 API signature
pub fn register_alg_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // ...
}
```

**Detection**: Look for compilation errors mentioning type mismatches between `&PyModule` and `&Bound<'_, PyModule>`.

**Fix Process**:
1. Check all `register_*_module` functions for consistent signatures
2. Update any functions still using `&PyModule` to use `&Bound<'_, PyModule>`
3. Consider prefixing unused `py` parameters with underscore (`_py`) to avoid warnings
4. Test compilation with `maturin develop` to verify the fix

### Issue 14: Missing Test Fixtures and Helper Functions

**Problem**: Python tests fail with `ImportError` and missing fixture errors when trying to use algebra loading patterns.

**Error Examples**:
```
ImportError: cannot import name 'load_test_algebra' from 'conftest'
fixture 'cyclic2_algebra' not found
fixture 'algebra_loader' not found
```

**Solution**: Create comprehensive `conftest.py` with all required fixtures and helper functions.

```python
# ❌ WRONG - Missing fixtures and helper functions
# conftest.py only imports test_utils fixtures

# ✅ CORRECT - Complete conftest.py with algebra fixtures
"""
Pytest configuration and shared fixtures for UACalc tests.
"""

import os
import pytest
import uacalc_lib

def load_test_algebra(name: str, skip_if_missing: bool = True):
    """Load a test algebra from resources/algebras/"""
    # Implementation with proper error handling

@pytest.fixture
def cyclic2_algebra():
    """Fixture providing cyclic2 algebra."""
    # Implementation

@pytest.fixture
def cyclic3_algebra():
    """Fixture providing cyclic3 algebra."""
    # Implementation

@pytest.fixture(params=["cyclic2", "cyclic3", "n5"])
def test_algebra(request):
    """Parameterized fixture for multiple algebras."""
    # Implementation

@pytest.fixture
def algebra_loader():
    """Fixture providing algebra loading function."""
    # Implementation
```

**Detection**: Look for test failures mentioning missing imports or fixtures in `test_algebra_loading_example.py`.

**Fix Process**:
1. Add `load_test_algebra` helper function to `conftest.py`
2. Add individual algebra fixtures (`cyclic2_algebra`, `cyclic3_algebra`)
3. Add parameterized fixture (`test_algebra`)
4. Add algebra loader fixture (`algebra_loader`)
5. Update `__all__` list to export all fixtures
6. Run tests to verify all fixtures are available

## 13. Verification Checklist

Before marking a translation as complete, verify:

- [ ] All doctests compile and run without errors
- [ ] All unit tests pass (Rust and Python)
- [ ] All integration tests pass
- [ ] Java wrapper works correctly
- [ ] Cross-language behavior matches exactly
- [ ] No compilation warnings
- [ ] All public methods are tested
- [ ] Edge cases are handled correctly
- [ ] Error conditions are properly tested
- [ ] Documentation is complete and accurate
- [ ] Python bindings work correctly
- [ ] Hash implementations are consistent
- [ ] JSON serialization works correctly
- [ ] Platform compatibility is maintained
- [ ] **Java wrapper classpath includes `org` directory**
- [ ] **Test arguments use `--key value` format, not `--key=value`**
- [ ] **Python tests handle nested JSON parsing correctly**
- [ ] **Rust struct fields are public if accessed by Python bindings**
- [ ] **Java wrapper argument parsing works correctly**
- [ ] **conftest.py includes all required algebra fixtures and helper functions**
- [ ] **All test fixtures are properly exported in `__all__` list**
- [ ] **Algebra loading patterns work correctly in all test scenarios**