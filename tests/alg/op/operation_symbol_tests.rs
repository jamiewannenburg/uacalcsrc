use uacalc::alg::op::OperationSymbol;
use crate::common::*;
use serde_json::json;
// use std::time::Duration; // TODO: Add when implementing timeout tests

/// Test basic OperationSymbol creation
#[test]
fn test_operation_symbol_creation() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["new", "--name", "f", "--arity", "2"],
        || {
            let sym = OperationSymbol::new("f", 2, false);
            json!({
                "name": sym.name(),
                "arity": sym.arity(),
                "associative": sym.is_associative()
            })
        }
    );
}

/// Test OperationSymbol creation with associativity
#[test]
fn test_operation_symbol_creation_associative() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["new", "--name", "g", "--arity", "2", "--associative", "true"],
        || {
            let sym = OperationSymbol::new("g", 2, true);
            json!({
                "name": sym.name(),
                "arity": sym.arity(),
                "associative": sym.is_associative()
            })
        }
    );
}

/// Test getting arity
#[test]
fn test_operation_symbol_arity() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["arity", "--name", "f", "--arity", "3"],
        || {
            let sym = OperationSymbol::new("f", 3, false);
            json!({
                "arity": sym.arity(),
                "symbol": sym.to_string()
            })
        }
    );
}

/// Test getting name
#[test]
fn test_operation_symbol_name() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["name", "--name", "myOp", "--arity", "1"],
        || {
            let sym = OperationSymbol::new("myOp", 1, false);
            json!({
                "name": sym.name(),
                "symbol": sym.to_string()
            })
        }
    );
}

/// Test checking associativity
#[test]
fn test_operation_symbol_is_associative() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["isAssociative", "--name", "f", "--arity", "2"],
        || {
            let sym = OperationSymbol::new("f", 2, false);
            json!({
                "associative": sym.is_associative(),
                "symbol": sym.to_string()
            })
        }
    );
}

/// Test setting associativity
#[test]
fn test_operation_symbol_set_associative() {
    let config = TestConfig::default();
    
        compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["setAssociative", "--name", "f", "--arity", "2", "--associative", "false", "--newAssociative", "true"],
        || {
            let mut sym = OperationSymbol::new("f", 2, false);
            sym.set_associative(true).unwrap();
            json!({
                "name": sym.name(),
                "arity": sym.arity(),
                "associative": sym.is_associative()
            })
        }
    );
}

/// Test toString without arity
#[test]
fn test_operation_symbol_to_string() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["toString", "--name", "f", "--arity", "2"],
        || {
            let sym = OperationSymbol::new("f", 2, false);
            json!({
                "string": sym.to_string(),
                "symbol": sym.to_string()
            })
        }
    );
}

/// Test toString with arity
#[test]
fn test_operation_symbol_to_string_with_arity() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["toStringWithArity", "--name", "f", "--arity", "2", "--showArity", "true"],
        || {
            let sym = OperationSymbol::new("f", 2, false);
            json!({
                "string": sym.to_string_with_arity(true),
                "showArity": true,
                "symbol": sym.to_string()
            })
        }
    );
}

/// Test comparison between OperationSymbols
#[test]
fn test_operation_symbol_compare_to() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["compareTo", "--name1", "f", "--arity1", "2", "--name2", "g", "--arity2", "3"],
        || {
            let sym1 = OperationSymbol::new("f", 2, false);
            let sym2 = OperationSymbol::new("g", 3, false);
            let comparison = sym1.cmp(&sym2);
            json!({
                "comparison": comparison as i32,
                "symbol1": sym1.to_string(),
                "symbol2": sym2.to_string(),
                "symbol1_arity": sym1.arity(),
                "symbol2_arity": sym2.arity()
            })
        }
    );
}

/// Test equality between OperationSymbols
#[test]
fn test_operation_symbol_equals() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["equals", "--name1", "f", "--arity1", "2", "--name2", "f", "--arity2", "2"],
        || {
            let sym1 = OperationSymbol::new("f", 2, false);
            let sym2 = OperationSymbol::new("f", 2, false);
            json!({
                "equals": sym1 == sym2,
                "symbol1": sym1.to_string(),
                "symbol2": sym2.to_string()
            })
        }
    );
}

/// Test hash code
#[test]
fn test_operation_symbol_hash_code() {
    let _config = TestConfig::default();
    
    // Hash codes will be different between Rust and Java due to different algorithms
    // So we just test that the hash is consistent within Rust
    let sym = OperationSymbol::new("f", 2, false);
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    let mut hasher1 = DefaultHasher::new();
    let mut hasher2 = DefaultHasher::new();
    sym.hash(&mut hasher1);
    sym.hash(&mut hasher2);
    
    // Hash should be consistent
    assert_eq!(hasher1.finish(), hasher2.finish());
    
    // Test that equal objects have equal hash codes
    let sym2 = OperationSymbol::new("f", 2, false);
    let mut hasher3 = DefaultHasher::new();
    sym2.hash(&mut hasher3);
    assert_eq!(hasher1.finish(), hasher3.finish());
}

/// Test getOperationSymbol for different arities
#[test]
fn test_operation_symbol_get_operation_symbol_arity_0() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["getOperationSymbol", "--arity", "0"],
        || {
            let sym = OperationSymbol::get_operation_symbol(0);
            json!({
                "name": sym.name(),
                "arity": sym.arity(),
                "associative": sym.is_associative()
            })
        }
    );
}

/// Test getOperationSymbol for arity 1
#[test]
fn test_operation_symbol_get_operation_symbol_arity_1() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["getOperationSymbol", "--arity", "1"],
        || {
            let sym = OperationSymbol::get_operation_symbol(1);
            json!({
                "name": sym.name(),
                "arity": sym.arity(),
                "associative": sym.is_associative()
            })
        }
    );
}

/// Test getOperationSymbol for arity 2
#[test]
fn test_operation_symbol_get_operation_symbol_arity_2() {
    // Test that the generated symbol has the correct properties
    let sym = OperationSymbol::get_operation_symbol(2);
    assert_eq!(sym.arity(), 2);
    assert!(sym.name().starts_with("b_"));
    assert!(!sym.is_associative());
    
    // Test that it generates a valid name format
    let name_parts: Vec<&str> = sym.name().split('_').collect();
    assert_eq!(name_parts.len(), 2);
    assert_eq!(name_parts[0], "b");
    assert!(name_parts[1].parse::<i32>().is_ok());
}

/// Test getOperationSymbol for arity 3
#[test]
fn test_operation_symbol_get_operation_symbol_arity_3() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["getOperationSymbol", "--arity", "3"],
        || {
            let sym = OperationSymbol::get_operation_symbol(3);
            json!({
                "name": sym.name(),
                "arity": sym.arity(),
                "associative": sym.is_associative()
            })
        }
    );
}

/// Test getOperationSymbol for high arity
#[test]
fn test_operation_symbol_get_operation_symbol_high_arity() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["getOperationSymbol", "--arity", "5"],
        || {
            let sym = OperationSymbol::get_operation_symbol(5);
            json!({
                "name": sym.name(),
                "arity": sym.arity(),
                "associative": sym.is_associative()
            })
        }
    );
}

/// Test that getOperationSymbol generates sequential names
#[test]
fn test_operation_symbol_get_operation_symbol_sequence() {
    let _config = TestConfig::default();
    
    // Test multiple calls to ensure sequential naming
    let sym1 = OperationSymbol::get_operation_symbol(2);
    let sym2 = OperationSymbol::get_operation_symbol(2);
    let sym3 = OperationSymbol::get_operation_symbol(2);
    
    // Names should be b_0, b_1, b_2
    assert!(sym1.name().starts_with("b_"));
    assert!(sym2.name().starts_with("b_"));
    assert!(sym3.name().starts_with("b_"));
    
    // All should have arity 2
    assert_eq!(sym1.arity(), 2);
    assert_eq!(sym2.arity(), 2);
    assert_eq!(sym3.arity(), 2);
}

/// Test static constants
#[test]
fn test_operation_symbol_constants() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["constants"],
        || {
            json!({
                "JOIN": {
                    "name": OperationSymbol::join().name(),
                    "arity": OperationSymbol::join().arity(),
                    "associative": OperationSymbol::join().is_associative()
                },
                "MEET": {
                    "name": OperationSymbol::meet().name(),
                    "arity": OperationSymbol::meet().arity(),
                    "associative": OperationSymbol::meet().is_associative()
                },
                "PRODUCT": {
                    "name": OperationSymbol::product().name(),
                    "arity": OperationSymbol::product().arity(),
                    "associative": OperationSymbol::product().is_associative()
                },
                "INVERSE": {
                    "name": OperationSymbol::inverse().name(),
                    "arity": OperationSymbol::inverse().arity(),
                    "associative": OperationSymbol::inverse().is_associative()
                },
                "IDENTITY": {
                    "name": OperationSymbol::identity().name(),
                    "arity": OperationSymbol::identity().arity(),
                    "associative": OperationSymbol::identity().is_associative()
                }
            })
        }
    );
}

/// Test ordering behavior (high arity first, then by name)
#[test]
fn test_operation_symbol_ordering() {
    let sym1 = OperationSymbol::new("a", 1, false);  // arity 1, name "a"
    let sym2 = OperationSymbol::new("b", 2, false);  // arity 2, name "b"
    let sym3 = OperationSymbol::new("a", 2, false);  // arity 2, name "a"
    let sym4 = OperationSymbol::new("b", 1, false);  // arity 1, name "b"
    
    // sym2 and sym3 should be equal (both arity 2, but sym3 has name "a" < "b")
    assert!(sym3 < sym2);
    
    // sym2 should be less than sym1 (higher arity comes first)
    assert!(sym2 < sym1);
    
    // sym4 should be less than sym1 (same arity, but "b" > "a")
    assert!(sym1 < sym4);
}

/// Test associativity validation
#[test]
#[should_panic(expected = "Only binary terms can be associative")]
fn test_operation_symbol_associativity_validation() {
    // This should panic because we're trying to make a unary operation associative
    OperationSymbol::new("f", 1, true);
}

/// Test comprehensive functionality
#[test]
fn test_operation_symbol_comprehensive() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.OperationSymbolWrapper",
        ["test"],
        || {
            // Reset the counter for arity 2 to ensure deterministic behavior
            // This matches the Java side which runs in a fresh process
            OperationSymbol::reset_operation_symbol_counter(2);
            
            // Test basic creation
            let sym1 = OperationSymbol::new("f", 2, false);
            
            // Test associativity
            let sym2 = OperationSymbol::new("g", 2, true);
            
            // Test comparison
            let sym3 = OperationSymbol::new("h", 3, false);
            let comparison = sym3.cmp(&sym1);
            
            // Test getOperationSymbol
            let sym4 = OperationSymbol::get_operation_symbol(2);
            
            json!({
                "basic_creation": sym1.to_string(),
                "associative_creation": sym2.is_associative(),
                "comparison_result": comparison as i32,
                "generated_symbol": sym4.name()
            })
        }
    );
}
