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
- **Class**: `Py[ClassName]`

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

pub fn register_[module]_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Py[ClassName]>()?;
    Ok(())
}
```

### Key Points
- Always use `PyValueError::new_err()` for validation errors
- Use `PyResult<T>` for methods that can fail
- Implement Python magic methods (`__str__`, `__repr__`, `__eq__`, `__hash__`, comparison operators)
- Use `#[pyo3(signature = (...))]` for default parameters
- Always provide both `_safe` and regular versions of methods

## 4. Testing Pattern

### Rust Tests
```rust
#[test]
fn test_[method_name]() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "[ClassName]Wrapper",
        ["command", "--arg1", "value1", "--arg2", "value2"],
        || {
            let instance = [ClassName]::new(param1, param2);
            json!({
                "result": instance.method(),
                "param1": param1,
                "param2": param2
            })
        }
    );
}
```

### Python Tests
```python
def test_[method_name](self):
    """Test [method description]."""
    instance = [ClassName](param1, param2)
    java_result = run_java_wrapper("command", ["--arg1", "value1", "--arg2", "value2"])
    
    assert instance.method() == java_result["data"]["result"]
```

### Key Points
- Use `compare_with_java!` macro for Rust tests
- Use `run_java_wrapper()` function for Python tests
- Test both success and error cases
- Test all public methods
- Test edge cases and validation

## 5. Compilation and Build Pattern

### Build Commands
```bash
# Compile Java wrapper
ant compile-wrappers

# Create wrapper scripts
ant create-wrapper-scripts

# Test wrapper functionality
java_wrapper/build/scripts/[ClassName]Wrapper help

# Compile Rust library
cargo build --release

# Run Rust tests
cargo test [module]::[submodule]::[class_name] --test mod

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

## 6. Documentation Pattern

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
/// let instance = ClassName::new("example", 2);
/// assert_eq!(instance.method(), expected_result);
/// ```
```

### Key Points
- Use proper Rust documentation format
- Document all public methods
- Include examples where helpful
- Document error conditions
- Use `# Arguments`, `# Returns`, `# Panics` sections

## 7. Common Pitfalls to Avoid

1. **Don't use panics in Python bindings** - Always use proper error handling
2. **Don't skip validation** - Always validate inputs in both Rust and Python
3. **Don't ignore warnings** - Fix all compilation warnings
4. **Don't skip tests** - Test all public methods and edge cases
5. **Don't forget thread safety** - Use proper synchronization for static mutable state
6. **Don't hardcode paths** - Use relative paths and proper module structure
7. **Don't skip error handling** - Always handle errors gracefully

## 8. File Naming Conventions

- **Java Wrapper**: `[ClassName]Wrapper.java`
- **Rust Implementation**: `[class_name].rs` or in `mod.rs`
- **Python Tests**: `test_[class_name].py`
- **Rust Tests**: `[class_name]_tests.rs`

## 9. Module Registration

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

## 10. Cross-Platform Compatibility Pattern

### Windows Compatibility for Wrapper Scripts

The build system and test infrastructure must support both Windows and Unix/Linux platforms.

#### Build System (build.xml)

```xml
<!-- Create individual wrapper scripts -->
<scriptdef name="create-wrapper" language="javascript">
  <attribute name="classname"/>
  <attribute name="scriptname"/>
  <![CDATA[
    var classname = attributes.get("classname");
    var scriptname = attributes.get("scriptname");
    
    // Create Unix shell script
    var unixScript = "#!/bin/bash\n";
    unixScript += "java -cp " + project.getProperty("java.wrapper.classes") + ":" + 
                  project.getProperty("class.dir") + ":" + 
                  project.getProperty("jar.dir") + "/* " + 
                  "java_wrapper.src." + classname + " \"$@\"\n";
    
    var unixFile = new java.io.File(project.getProperty("java.wrapper.scripts") + "/" + scriptname);
    var unixWriter = new java.io.FileWriter(unixFile);
    unixWriter.write(unixScript);
    unixWriter.close();
    
    // Make Unix script executable
    var unixProcess = java.lang.Runtime.getRuntime().exec("chmod +x " + unixFile.getAbsolutePath());
    unixProcess.waitFor();
    
    // Create Windows batch script
    var winScript = "@echo off\n";
    winScript += "java -cp " + project.getProperty("java.wrapper.classes") + ";" + 
                 project.getProperty("class.dir") + ";" + 
                 project.getProperty("jar.dir") + "\\* " + 
                 "java_wrapper.src." + classname + " %*\n";
    
    var winFile = new java.io.File(project.getProperty("java.wrapper.scripts") + "/" + scriptname + ".bat");
    var winWriter = new java.io.FileWriter(winFile);
    winWriter.write(winScript);
    winWriter.close();
  ]]>
</scriptdef>

<!-- Generate scripts for each wrapper class -->
<create-wrapper classname="util.HornerWrapper" scriptname="HornerWrapper"/>
<create-wrapper classname="alg.op.OperationSymbolWrapper" scriptname="OperationSymbolWrapper"/>
<create-wrapper classname="alg.op.SimilarityTypeWrapper" scriptname="SimilarityTypeWrapper"/>
<create-wrapper classname="util.SimpleListWrapper" scriptname="SimpleListWrapper"/>
```

#### Rust Test Infrastructure (tests/common/mod.rs)

```rust
/// Get the appropriate script extension for the current platform.
fn get_script_extension() -> &'static str {
    if cfg!(target_os = "windows") {
        ".bat"
    } else {
        ""
    }
}

/// Get the full script path with appropriate extension for the current platform.
fn get_script_path(base_path: &str, script_name: &str) -> std::path::PathBuf {
    let extension = get_script_extension();
    Path::new(base_path).join(format!("{}{}", script_name, extension))
}

/// Run a Java CLI wrapper and capture its output.
pub fn run_java_cli(
    script_name: &str,
    args: &[&str],
    config: &TestConfig,
) -> TestResult<JavaCliOutput> {
    let script_path = get_script_path(&config.java_wrapper_path, script_name);
    
    if !script_path.exists() {
        return Err(TestError::JavaCliError(format!(
            "Java CLI script not found: {}",
            script_path.display()
        )));
    }
    
    // ... rest of implementation
}
```

#### Python Test Infrastructure (python/uacalc/tests/test_utils.py)

```python
import platform

class TestHarness:
    def get_script_extension(self) -> str:
        """Get the appropriate script extension for the current platform."""
        return ".bat" if platform.system() == "Windows" else ""
    
    def get_script_path(self, script_name: str) -> Path:
        """Get the full script path with appropriate extension for the current platform."""
        extension = self.get_script_extension()
        return Path(self.config.java_wrapper_path) / f"{script_name}{extension}"

    def run_java_cli(self, script_name: str, args: List[str]) -> JavaCliOutput:
        """Run a Java CLI wrapper and capture its output."""
        script_path = self.get_script_path(script_name)
        
        if not script_path.exists():
            raise FileNotFoundError(f"Java CLI script not found: {script_path}")
        
        # ... rest of implementation
```

#### Individual Python Test Files

```python
import platform

def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    # Use Windows-compatible script path
    script_extension = ".bat" if platform.system() == "Windows" else ""
    java_wrapper_path = project_root / "java_wrapper" / "build" / "scripts" / f"ClassNameWrapper{script_extension}"
    
    if not java_wrapper_path.exists():
        pytest.skip(f"Java wrapper not found at {java_wrapper_path}")
    
    cmd = [str(java_wrapper_path), command] + args
    
    # ... rest of implementation
```

### Key Points

- **Platform Detection**: Use `cfg!(target_os = "windows")` in Rust and `platform.system() == "Windows"` in Python
- **Script Extensions**: Use `.bat` for Windows, no extension for Unix/Linux
- **Path Separators**: Use `;` for Windows classpath, `:` for Unix classpath
- **File Separators**: Use `\` for Windows paths, `/` for Unix paths
- **Automatic Generation**: Build system creates both script types automatically
- **Test Compatibility**: Tests work on both platforms without modification

### Generated Scripts

**Unix Scripts (.sh):**
- `HornerWrapper`
- `OperationSymbolWrapper`
- `SimilarityTypeWrapper`
- `SimpleListWrapper`

**Windows Scripts (.bat):**
- `HornerWrapper.bat`
- `OperationSymbolWrapper.bat`
- `SimilarityTypeWrapper.bat`
- `SimpleListWrapper.bat`

### Testing Cross-Platform Compatibility

```bash
# Test on Windows
java_wrapper\build\scripts\HornerWrapper.bat help

# Test on Unix/Linux
./java_wrapper/build/scripts/HornerWrapper help

# Both should work identically
```

This pattern ensures consistent, maintainable, and robust implementations across all translated classes and all supported platforms.
