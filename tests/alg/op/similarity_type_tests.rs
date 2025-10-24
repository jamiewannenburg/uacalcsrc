use uacalc::alg::op::{SimilarityType, OperationSymbol};
use crate::common::*;
use serde_json::json;
// use std::time::Duration; // TODO: Add when implementing timeout tests

/// Test basic SimilarityType creation
#[test]
fn test_similarity_type_creation() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["new", "--operation_symbols", "join:2,meet:2"],
        || {
            let ops = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
            ];
            let st = SimilarityType::new(ops.clone());
            json!({
                "similarity_type": st.to_string(),
                "operation_symbols": format_operation_symbols(&ops)
            })
        }
    );
}

/// Test SimilarityType creation with sorting
#[test]
fn test_similarity_type_creation_sorted() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["new_sorted", "--operation_symbols", "prod:2,inv:1,id:0"],
        || {
            let ops = vec![
                OperationSymbol::new("prod", 2, false),
                OperationSymbol::new("inv", 1, false),
                OperationSymbol::new("id", 0, false),
            ];
            let st = SimilarityType::new_with_sort(ops.clone(), true);
            json!({
                "similarity_type": st.to_string(),
                "operation_symbols": format_operation_symbols(&ops),
                "sorted": true
            })
        }
    );
}

/// Test getting operation symbols
#[test]
fn test_similarity_type_get_operation_symbols() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["get_operation_symbols", "--operation_symbols", "join:2,meet:2"],
        || {
            let ops = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
            ];
            let st = SimilarityType::new(ops.clone());
            let result = st.get_operation_symbols();
            json!({
                "operation_symbols": format_operation_symbols(result),
                "count": result.len()
            })
        }
    );
}

/// Test getting sorted operation symbols
#[test]
fn test_similarity_type_get_sorted_operation_symbols() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["get_sorted_operation_symbols", "--operation_symbols", "prod:2,inv:1,id:0"],
        || {
            let ops = vec![
                OperationSymbol::new("prod", 2, false),
                OperationSymbol::new("inv", 1, false),
                OperationSymbol::new("id", 0, false),
            ];
            let st = SimilarityType::new(ops.clone());
            let result = st.get_sorted_operation_symbols();
            json!({
                "sorted_operation_symbols": format_operation_symbols(&result),
                "count": result.len()
            })
        }
    );
}

/// Test input size calculation
#[test]
fn test_similarity_type_input_size() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["input_size", "--operation_symbols", "join:2,meet:2", "--alg_size", "5"],
        || {
            let ops = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
            ];
            let st = SimilarityType::new(ops.clone());
            let input_size = st.input_size(5);
            json!({
                "input_size": input_size,
                "alg_size": 5,
                "operation_symbols": format_operation_symbols(&ops)
            })
        }
    );
}

/// Test input size with different algebra sizes
#[test]
fn test_similarity_type_input_size_various() {
    let config = TestConfig::default();
    
    // Test with algebra size 3
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["input_size", "--operation_symbols", "join:2,meet:2", "--alg_size", "3"],
        || {
            let ops = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
            ];
            let st = SimilarityType::new(ops.clone());
            let input_size = st.input_size(3);
            json!({
                "input_size": input_size,
                "alg_size": 3,
                "operation_symbols": format_operation_symbols(&ops)
            })
        }
    );
}

/// Test input size with empty similarity type
#[test]
fn test_similarity_type_input_size_empty() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["input_size", "--operation_symbols", "", "--alg_size", "5"],
        || {
            let ops = vec![];
            let st = SimilarityType::new(ops.clone());
            let input_size = st.input_size(5);
            json!({
                "input_size": input_size,
                "alg_size": 5,
                "operation_symbols": format_operation_symbols(&ops)
            })
        }
    );
}

/// Test getting arities map
#[test]
fn test_similarity_type_get_arities_map() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["get_arities_map", "--operation_symbols", "join:2,meet:2,inv:1"],
        || {
            let ops = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
                OperationSymbol::new("inv", 1, false),
            ];
            let mut st = SimilarityType::new(ops.clone());
            let arities_map = st.get_arities_map().clone();
            json!({
                "arities_map": arities_map,
                "operation_symbols": format_operation_symbols(&ops)
            })
        }
    );
}

/// Test getting max arity
#[test]
fn test_similarity_type_get_max_arity() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["get_max_arity", "--operation_symbols", "join:2,meet:2,inv:1"],
        || {
            let ops = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
                OperationSymbol::new("inv", 1, false),
            ];
            let mut st = SimilarityType::new(ops.clone());
            let max_arity = st.get_max_arity();
            json!({
                "max_arity": max_arity,
                "operation_symbols": format_operation_symbols(&ops)
            })
        }
    );
}

/// Test lattice similarity type constant
#[test]
fn test_similarity_type_lattice_similarity_type() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["lattice_similarity_type"],
        || {
            let lattice_type = SimilarityType::lattice_similarity_type();
            let mut lattice_type_clone = lattice_type.clone();
            json!({
                "similarity_type": lattice_type.to_string(),
                "operation_symbols": format_operation_symbols(lattice_type.get_operation_symbols()),
                "max_arity": lattice_type_clone.get_max_arity()
            })
        }
    );
}

/// Test group similarity type constant
#[test]
fn test_similarity_type_group_similarity_type() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["group_similarity_type"],
        || {
            let group_type = SimilarityType::group_similarity_type();
            let mut group_type_clone = group_type.clone();
            json!({
                "similarity_type": group_type.to_string(),
                "operation_symbols": format_operation_symbols(group_type.get_operation_symbols()),
                "max_arity": group_type_clone.get_max_arity()
            })
        }
    );
}

/// Test arities string
#[test]
fn test_similarity_type_arities_string() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["arities_string", "--operation_symbols", "join:2,meet:2,inv:1"],
        || {
            let ops = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
                OperationSymbol::new("inv", 1, false),
            ];
            let mut st = SimilarityType::new(ops.clone());
            let arities_string = st.arities_string();
            json!({
                "arities_string": arities_string,
                "operation_symbols": format_operation_symbols(&ops)
            })
        }
    );
}

/// Test toString
#[test]
fn test_similarity_type_to_string() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["toString", "--operation_symbols", "join:2,meet:2"],
        || {
            let ops = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
            ];
            let st = SimilarityType::new(ops.clone());
            let string_rep = st.to_string();
            json!({
                "string_representation": string_rep,
                "operation_symbols": format_operation_symbols(&ops)
            })
        }
    );
}

/// Test equality
#[test]
fn test_similarity_type_equals() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["equals", "--operation_symbols1", "join:2,meet:2", "--operation_symbols2", "meet:2,join:2"],
        || {
            let ops1 = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
            ];
            let ops2 = vec![
                OperationSymbol::new("meet", 2, false),
                OperationSymbol::new("join", 2, false),
            ];
            let st1 = SimilarityType::new(ops1.clone());
            let st2 = SimilarityType::new(ops2.clone());
            let equals = st1 == st2;
            json!({
                "equals": equals,
                "operation_symbols1": format_operation_symbols(&ops1),
                "operation_symbols2": format_operation_symbols(&ops2)
            })
        }
    );
}

/// Test equality with different similarity types
#[test]
fn test_similarity_type_equals_different() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["equals", "--operation_symbols1", "join:2,meet:2", "--operation_symbols2", "join:2,inv:1"],
        || {
            let ops1 = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
            ];
            let ops2 = vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("inv", 1, false),
            ];
            let st1 = SimilarityType::new(ops1.clone());
            let st2 = SimilarityType::new(ops2.clone());
            let equals = st1 == st2;
            json!({
                "equals": equals,
                "operation_symbols1": format_operation_symbols(&ops1),
                "operation_symbols2": format_operation_symbols(&ops2)
            })
        }
    );
}

/// Test hash code
#[test]
fn test_similarity_type_hash_code() {
    let _config = TestConfig::default();
    
    // Hash codes will be different between Rust and Java due to different algorithms
    // So we just test that the hash is consistent within Rust
    let ops = vec![
        OperationSymbol::new("join", 2, false),
        OperationSymbol::new("meet", 2, false),
    ];
    let st = SimilarityType::new(ops.clone());
    
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    let mut hasher1 = DefaultHasher::new();
    let mut hasher2 = DefaultHasher::new();
    st.hash(&mut hasher1);
    st.hash(&mut hasher2);
    
    // Hash should be consistent
    assert_eq!(hasher1.finish(), hasher2.finish());
    
    // Test that equal objects have equal hash codes
    let st2 = SimilarityType::new(ops);
    let mut hasher3 = DefaultHasher::new();
    st2.hash(&mut hasher3);
    assert_eq!(hasher1.finish(), hasher3.finish());
}

/// Test comprehensive functionality
#[test]
fn test_similarity_type_comprehensive() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.op.SimilarityTypeWrapper",
        ["test"],
        || {
            // Test basic creation
            let ops = vec![
                OperationSymbol::join().clone(),
                OperationSymbol::meet().clone(),
            ];
            let mut st = SimilarityType::new(ops.clone());
            
            // Test input size calculation
            let input_size = st.input_size(3);
            
            // Test max arity
            let max_arity = st.get_max_arity();
            
            // Test arities map
            let arities_map = st.get_arities_map().clone();
            
            // Test constants
            let lattice_type = SimilarityType::lattice_similarity_type();
            let group_type = SimilarityType::group_similarity_type();
            
            // Test equality
            let st2 = SimilarityType::new(vec![OperationSymbol::meet().clone(), OperationSymbol::join().clone()]);
            let equals = st == st2;
            
            json!({
                "test_create": st.to_string(),
                "test_input_size": input_size,
                "test_max_arity": max_arity,
                "test_arities_map": arities_map,
                "test_lattice_type": lattice_type.to_string(),
                "test_group_type": group_type.to_string(),
                "test_equals": equals
            })
        }
    );
}

/// Test edge cases
#[test]
fn test_similarity_type_edge_cases() {
    // Test empty similarity type
    let empty_st = SimilarityType::new(vec![]);
    assert_eq!(empty_st.to_string(), "()");
    assert_eq!(empty_st.input_size(5), 5);
    
    // Test single operation
    let single_op = vec![OperationSymbol::new("f", 1, false)];
    let single_st = SimilarityType::new(single_op);
    assert_eq!(single_st.input_size(3), 3);
    
    // Test high arity operations
    let high_arity_ops = vec![
        OperationSymbol::new("f", 5, false),
        OperationSymbol::new("g", 3, false),
    ];
    let mut high_arity_st = SimilarityType::new(high_arity_ops);
    assert_eq!(high_arity_st.get_max_arity(), 5);
}

/// Test sorting behavior
#[test]
fn test_similarity_type_sorting() {
    let ops = vec![
        OperationSymbol::new("z", 1, false),  // arity 1, name "z"
        OperationSymbol::new("a", 2, false),  // arity 2, name "a"
        OperationSymbol::new("b", 1, false),  // arity 1, name "b"
        OperationSymbol::new("c", 2, false),  // arity 2, name "c"
    ];
    
    let st = SimilarityType::new(ops);
    let sorted = st.get_sorted_operation_symbols();
    
    // Should be sorted by arity (descending), then by name (ascending)
    // Expected order: a(2), c(2), b(1), z(1)
    assert_eq!(sorted[0].name(), "a");
    assert_eq!(sorted[0].arity(), 2);
    assert_eq!(sorted[1].name(), "c");
    assert_eq!(sorted[1].arity(), 2);
    assert_eq!(sorted[2].name(), "b");
    assert_eq!(sorted[2].arity(), 1);
    assert_eq!(sorted[3].name(), "z");
    assert_eq!(sorted[3].arity(), 1);
}

/// Helper function to format operation symbols for comparison
fn format_operation_symbols(ops: &[OperationSymbol]) -> String {
    ops.iter()
        .map(|op| format!("{}:{}", op.name(), op.arity()))
        .collect::<Vec<_>>()
        .join(",")
}
