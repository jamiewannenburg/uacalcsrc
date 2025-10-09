//! Tests for Python bindings in uacalc_lib
//! 
//! These tests verify that the PyO3 bindings work correctly
//! and that Python can properly interact with Rust code.

use pyo3::prelude::*;
use pyo3::types::PyDict;

#[test]
fn test_python_module_import() {
    Python::with_gil(|py| {
        // Test that the module can be imported
        let module = py.import("uacalc_lib").expect("Failed to import uacalc_lib");
        assert!(module.getattr("__name__").is_ok());
    });
}

#[test]
fn test_submodule_imports() {
    Python::with_gil(|py| {
        let module = py.import("uacalc_lib").expect("Failed to import uacalc_lib");
        
        // Test that all submodules can be imported
        let submodules = ["alg", "element", "eq", "example", "fplat", 
                         "group", "io", "lat", "terms", "types", "util"];
        
        for submodule_name in &submodules {
            let submodule = module.getattr(submodule_name)
                .expect(&format!("Failed to import submodule: {}", submodule_name));
            assert!(submodule.getattr("__name__").is_ok());
        }
    });
}

#[test]
fn test_python_type_annotations() {
    Python::with_gil(|py| {
        // Test that type annotations are available
        let module = py.import("uacalc_lib").expect("Failed to import uacalc_lib");
        let types_module = module.getattr("types").expect("Failed to import types module");
        assert!(types_module.getattr("__name__").is_ok());
    });
}

#[test]
fn test_error_handling() {
    Python::with_gil(|py| {
        // Test that errors are properly propagated to Python
        // TODO: Add specific error handling tests
    });
}

#[test]
fn test_memory_management() {
    Python::with_gil(|py| {
        // Test that memory is properly managed between Rust and Python
        // TODO: Add memory leak tests
    });
}
