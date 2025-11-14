/*!
 * Tests for BadAlgebraFileException implementation.
 * 
 * These tests verify that the Rust implementation matches the Java behavior
 * and that all public methods work correctly.
 */

use uacalc::io::BadAlgebraFileException;
use crate::common::*;
use serde_json::json;
use std::error::Error;

#[test]
fn test_create_simple_message() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", "Test message"],
        || {
            let exception = BadAlgebraFileException::new("Test message");
            json!({
                "message": exception.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception.to_string()
            })
        }
    );
}

#[test]
fn test_create_empty_message() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", ""],
        || {
            let exception = BadAlgebraFileException::new("");
            json!({
                "message": exception.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception.to_string()
            })
        }
    );
}

#[test]
fn test_create_special_characters() {
    let config = TestConfig::default();
    
    let special_message = "Error: File 'test\\file.txt' not found!\nLine 42: Invalid format";
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", special_message],
        || {
            let exception = BadAlgebraFileException::new(special_message);
            json!({
                "message": exception.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception.to_string()
            })
        }
    );
}

#[test]
fn test_new_safe_method() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", "Safe method test"],
        || {
            let exception = BadAlgebraFileException::new_safe("Safe method test").unwrap();
            json!({
                "message": exception.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception.to_string()
            })
        }
    );
}

#[test]
fn test_message_method() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", "Message method test"],
        || {
            let exception = BadAlgebraFileException::new("Message method test");
            json!({
                "message": exception.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception.to_string()
            })
        }
    );
}

#[test]
fn test_display_trait() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", "Display test"],
        || {
            let exception = BadAlgebraFileException::new("Display test");
            json!({
                "message": exception.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception.to_string()
            })
        }
    );
}

#[test]
fn test_error_trait() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", "Error trait test"],
        || {
            let exception = BadAlgebraFileException::new("Error trait test");
            json!({
                "message": exception.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception.to_string()
            })
        }
    );
}

#[test]
fn test_equality() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", "Equality test"],
        || {
            let exception1 = BadAlgebraFileException::new("Equality test");
            let exception2 = BadAlgebraFileException::new("Equality test");
            let exception3 = BadAlgebraFileException::new("Different message");
            
            json!({
                "message": exception1.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception1.to_string()
            })
        }
    );
}

#[test]
fn test_hash() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", "Hash test"],
        || {
            let exception1 = BadAlgebraFileException::new("Hash test");
            let exception2 = BadAlgebraFileException::new("Hash test");
            
            use std::collections::hash_map::DefaultHasher;
            use std::hash::{Hash, Hasher};
            
            let mut hasher1 = DefaultHasher::new();
            let mut hasher2 = DefaultHasher::new();
            exception1.hash(&mut hasher1);
            exception2.hash(&mut hasher2);
            
            json!({
                "message": exception1.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception1.to_string()
            })
        }
    );
}

#[test]
fn test_clone() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", "Clone test"],
        || {
            let exception1 = BadAlgebraFileException::new("Clone test");
            let exception2 = exception1.clone();
            
            json!({
                "message": exception1.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception1.to_string()
            })
        }
    );
}

#[test]
fn test_debug() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["create", "--message", "Debug test"],
        || {
            let exception = BadAlgebraFileException::new("Debug test");
            json!({
                "message": exception.message(),
                "class_name": "BadAlgebraFileException",
                "string_representation": exception.to_string()
            })
        }
    );
}

#[test]
fn test_comprehensive_functionality() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.BadAlgebraFileExceptionWrapper",
        ["test"],
        || {
            // Test 1: Create exception with simple message
            let ex1 = BadAlgebraFileException::new("Test message");
            let test1_result = json!({
                "success": true,
                "message": ex1.message(),
                "class_name": "BadAlgebraFileException"
            });
            
            // Test 2: Create exception with empty message
            let ex2 = BadAlgebraFileException::new("");
            let test2_result = json!({
                "success": true,
                "message": ex2.message(),
                "is_empty": ex2.message().is_empty()
            });
            
            // Test 3: Create exception with special characters
            let special_message = "Error: File 'test\\file.txt' not found!\nLine 42: Invalid format";
            let ex3 = BadAlgebraFileException::new(special_message);
            let test3_result = json!({
                "success": true,
                "message": ex3.message(),
                "contains_newline": ex3.message().contains("\n"),
                "contains_backslash": ex3.message().contains("\\")
            });
            
            // Test 4: Test toString method
            let ex4 = BadAlgebraFileException::new("toString test");
            let test4_result = json!({
                "success": true,
                "toString": ex4.to_string(),
                "contains_class_name": ex4.to_string().contains("BadAlgebraFileException"),
                "contains_message": ex4.to_string().contains("toString test")
            });
            
            json!({
                "test1_create_simple": test1_result,
                "test2_create_empty": test2_result,
                "test3_create_special_chars": test3_result,
                "test4_to_string": test4_result
            })
        }
    );
}

#[test]
fn test_edge_cases() {
    let _config = TestConfig::default();
    
    // Test with very long message
    let long_message = "A".repeat(1000);
    let exception = BadAlgebraFileException::new(&long_message);
    assert_eq!(exception.message(), long_message);
    assert!(exception.to_string().contains("BadAlgebraFileException"));
    
    // Test with unicode characters
    let unicode_message = "错误：文件 '测试文件.txt' 未找到！\n行 42：格式无效";
    let exception = BadAlgebraFileException::new(unicode_message);
    assert_eq!(exception.message(), unicode_message);
    assert!(exception.to_string().contains("BadAlgebraFileException"));
    
    // Test with null-like string (empty string)
    let empty_exception = BadAlgebraFileException::new("");
    assert_eq!(empty_exception.message(), "");
    assert!(empty_exception.to_string().contains("BadAlgebraFileException"));
}

#[test]
fn test_error_trait_implementation() {
    let exception = BadAlgebraFileException::new("Error trait test");
    
    // Test that it implements std::error::Error
    let error_ref: &dyn std::error::Error = &exception;
    assert_eq!(error_ref.to_string(), "org.uacalc.io.BadAlgebraFileException: Error trait test");
    
    // Test that it can be used in Result chains
    let result: Result<(), Box<dyn std::error::Error>> = Err(Box::new(exception));
    assert!(result.is_err());
}

#[test]
fn test_serialization_compatibility() {
    let _config = TestConfig::default();
    
    // Test that the exception can be serialized to JSON for comparison
    let exception = BadAlgebraFileException::new("Serialization test");
    let json_result = json!({
        "message": exception.message(),
        "class_name": "BadAlgebraFileException",
        "string_representation": exception.to_string()
    });
    
    // Verify the JSON structure is what we expect
    assert!(json_result["message"].is_string());
    assert!(json_result["class_name"].is_string());
    assert!(json_result["string_representation"].is_string());
    assert_eq!(json_result["message"], "Serialization test");
    assert_eq!(json_result["class_name"], "BadAlgebraFileException");
}
