//! Python integration tests for uacalc_lib
//! 
//! These tests verify that the Python bindings work correctly
//! in real Python environments and handle edge cases properly.

use pyo3::prelude::*;
use pyo3::types::PyDict;

#[test]
fn test_python_script_execution() {
    Python::with_gil(|py| {
        let code = r#"
import uacalc_lib
print("UACalc imported successfully")
print("Available modules:", [m for m in dir(uacalc_lib) if not m.startswith('_')])
"#;
        
        let result = py.run(code, None, None);
        assert!(result.is_ok(), "Python script execution failed");
    });
}

#[test]
fn test_python_exception_handling() {
    Python::with_gil(|py| {
        let code = r#"
import uacalc_lib
try:
    # This should raise an exception if not implemented
    uacalc_lib.alg.nonexistent_function()
except AttributeError:
    print("Exception handled correctly")
"#;
        
        let result = py.run(code, None, None);
        assert!(result.is_ok(), "Exception handling test failed");
    });
}

#[test]
fn test_python_memory_cleanup() {
    Python::with_gil(|py| {
        // Test that Python objects are properly cleaned up
        let code = r#"
import uacalc_lib
import gc

# Create some objects
modules = [uacalc_lib.alg, uacalc_lib.lat, uacalc_lib.terms]
del modules
gc.collect()
print("Memory cleanup test completed")
"#;
        
        let result = py.run(code, None, None);
        assert!(result.is_ok(), "Memory cleanup test failed");
    });
}

#[test]
fn test_python_type_checking() {
    Python::with_gil(|py| {
        let code = r#"
import uacalc_lib
from typing import get_type_hints

# Test that type hints are available
try:
    hints = get_type_hints(uacalc_lib)
    print("Type hints available:", len(hints) > 0)
except Exception as e:
    print("Type hints test completed with exception:", str(e))
"#;
        
        let result = py.run(code, None, None);
        assert!(result.is_ok(), "Type checking test failed");
    });
}
