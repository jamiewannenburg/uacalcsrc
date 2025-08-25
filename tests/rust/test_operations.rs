use uacalc_core::prelude::*;

#[test]
fn test_mixed_radix_encoding_decoding() {
    // Test round-trip conversion for various arities and set sizes
    let test_cases = vec![
        (vec![1, 2, 3], 5, 3), // arity 3, set size 5
        (vec![0, 1], 3, 2),    // arity 2, set size 3
        (vec![2], 4, 1),       // arity 1, set size 4
        (vec![], 5, 0),        // arity 0, set size 5
    ];
    
    for (args, base, arity) in test_cases {
        let encoded = horner_encode(&args, base).unwrap();
        let decoded = horner_decode(encoded, arity, base);
        assert_eq!(decoded, args);
    }
    
    // Test edge cases
    assert_eq!(horner_encode(&[], 5), Some(0));
    assert_eq!(horner_decode(0, 0, 5), vec![]);
    
    // Test overflow detection
    assert_eq!(horner_encode(&[usize::MAX], 2), None);
}

#[test]
fn test_horner_table_size() {
    assert_eq!(horner_table_size(0, 5), Some(1));
    assert_eq!(horner_table_size(1, 5), Some(5));
    assert_eq!(horner_table_size(2, 5), Some(25));
    assert_eq!(horner_table_size(3, 5), Some(125));
    
    // Test overflow detection
    assert_eq!(horner_table_size(20, 2), None);
}

#[test]
fn test_flat_operation_table() {
    let mut table = FlatOperationTable::new(2, 3).unwrap();
    
    // Test setting and getting values
    table.set_value(&[0, 1], 2).unwrap();
    assert_eq!(table.get_value(&[0, 1]).unwrap(), 2);
    
    // Test index-based access
    let index = horner_encode(&[0, 1], 3).unwrap();
    table.set(index, 3).unwrap();
    assert_eq!(table.get(index).unwrap(), 3);
    
    // Test bounds checking
    assert!(table.set_value(&[0, 3], 1).is_err()); // Invalid argument
    assert!(table.set(100, 1).is_err()); // Invalid index
}

#[test]
fn test_table_operation_creation() {
    // Test unary operation
    let unary_op = TableOperation::unary("neg".to_string(), 3, |x| (2 - x) % 3);
    assert_eq!(unary_op.arity(), 1);
    assert_eq!(unary_op.value(&[0]).unwrap(), 2);
    assert_eq!(unary_op.value(&[1]).unwrap(), 1);
    assert_eq!(unary_op.value(&[2]).unwrap(), 0);
    
    // Test binary operation
    let binary_op = TableOperation::binary("add".to_string(), 3, |a, b| (a + b) % 3);
    assert_eq!(binary_op.arity(), 2);
    assert_eq!(binary_op.value(&[1, 2]).unwrap(), 0);
    assert_eq!(binary_op.value(&[2, 2]).unwrap(), 1);
    
    // Test constant operation
    let const_op = TableOperation::constant("zero".to_string(), 0, 3).unwrap();
    assert_eq!(const_op.arity(), 0);
    assert_eq!(const_op.value(&[]).unwrap(), 0);
    
    // Test identity operation
    let id_op = TableOperation::identity(3);
    assert_eq!(id_op.arity(), 1);
    assert_eq!(id_op.value(&[0]).unwrap(), 0);
    assert_eq!(id_op.value(&[1]).unwrap(), 1);
    assert_eq!(id_op.value(&[2]).unwrap(), 2);
}

#[test]
fn test_operation_properties() {
    let set_size = 3;
    
    // Test idempotent operation
    let idempotent_op = TableOperation::unary("id".to_string(), set_size, |x| x);
    assert!(idempotent_op.is_idempotent_on_set(set_size).unwrap());
    
    // Test non-idempotent operation
    let non_idempotent_op = TableOperation::unary("inc".to_string(), set_size, |x| (x + 1) % set_size);
    assert!(!non_idempotent_op.is_idempotent_on_set(set_size).unwrap());
    
    // Test associative operation (addition modulo 3)
    let associative_op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size);
    assert!(associative_op.is_associative_on_set(set_size).unwrap());
    
    // Test commutative operation
    let commutative_op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size);
    assert!(commutative_op.is_commutative_on_set(set_size).unwrap());
    
    // Test non-commutative operation
    let non_commutative_op = TableOperation::binary("sub".to_string(), set_size, |a, b| (a + set_size - b) % set_size);
    assert!(!non_commutative_op.is_commutative_on_set(set_size).unwrap());
}

#[test]
fn test_function_operation() {
    let set_size = 4;
    let symbol = OperationSymbol::new("custom".to_string(), 2);
    
    let function_op = FunctionOperation::new(
        symbol.clone(),
        |args| {
            let a = args[0];
            let b = args[1];
            Ok((a + b) % set_size)
        },
        set_size,
    );
    
    assert_eq!(function_op.arity(), 2);
    assert_eq!(function_op.value(&[1, 2]).unwrap(), 3);
    assert_eq!(function_op.value(&[2, 3]).unwrap(), 1);
    
    // Test table generation
    let mut op_with_table = function_op;
    op_with_table.make_table(set_size).unwrap();
    
    // Verify table-based evaluation matches function evaluation
    assert_eq!(op_with_table.value(&[1, 2]).unwrap(), 3);
    assert_eq!(op_with_table.value(&[2, 3]).unwrap(), 1);
}

#[test]
fn test_operation_validation() {
    let set_size = 3;
    let op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size);
    
    // Test valid arguments
    assert!(op.value(&[0, 1]).is_ok());
    assert!(op.value(&[2, 2]).is_ok());
    
    // Test invalid arity
    assert!(op.value(&[0]).is_err());
    assert!(op.value(&[0, 1, 2]).is_err());
    
    // Test invalid arguments (out of bounds)
    assert!(op.value(&[0, 3]).is_err());
    assert!(op.value(&[3, 1]).is_err());
}

#[test]
fn test_operation_table_memory_estimation() {
    // Test memory estimation for various table sizes
    assert_eq!(estimate_table_memory(2, 5), Some(200)); // 25 * 8 bytes
    assert_eq!(estimate_table_memory(3, 4), Some(512)); // 64 * 8 bytes
    
    // Test overflow detection
    assert_eq!(estimate_table_memory(10, 2), None);
}

#[test]
fn test_operation_from_function() {
    let set_size = 3;
    let symbol = OperationSymbol::new("ternary".to_string(), 3);
    
    let op = TableOperation::from_function(
        symbol,
        set_size,
        |args| {
            let a = args[0];
            let b = args[1];
            let c = args[2];
            Ok((a + b + c) % set_size)
        },
    ).unwrap();
    
    assert_eq!(op.arity(), 3);
    assert_eq!(op.value(&[0, 1, 2]).unwrap(), 0);
    assert_eq!(op.value(&[1, 1, 1]).unwrap(), 0);
    assert_eq!(op.value(&[2, 2, 2]).unwrap(), 0);
}

#[test]
fn test_operation_int_value_methods() {
    let set_size = 4;
    let op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size);
    
    // Test int_value_at
    assert_eq!(op.int_value_at(&[1, 2]).unwrap(), 3);
    assert_eq!(op.int_value_at(&[2, 3]).unwrap(), 1);
    
    // Test int_value_at_index
    let index = horner_encode(&[1, 2], set_size).unwrap();
    assert_eq!(op.int_value_at_index(index).unwrap(), 3);
    
    // Test decode_index
    let decoded = op.decode_index(index).unwrap();
    assert_eq!(decoded, vec![1, 2]);
}

#[test]
fn test_operation_table_completeness() {
    let set_size = 2;
    let op = TableOperation::binary("and".to_string(), set_size, |a, b| a & b);
    
    // Verify all possible combinations are defined
    for a in 0..set_size {
        for b in 0..set_size {
            assert!(op.value(&[a, b]).is_ok());
        }
    }
    
    // Verify table size is correct
    if let Some(table) = op.get_table() {
        assert_eq!(table.table_size(), set_size.pow(2));
    }
}

#[test]
fn test_operation_serialization() {
    let set_size = 3;
    let op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size);
    
    // Test serialization
    let serialized = serde_json::to_string(&op).unwrap();
    let deserialized: TableOperation = serde_json::from_str(&serialized).unwrap();
    
    // Verify deserialized operation works correctly
    assert_eq!(deserialized.arity(), 2);
    assert_eq!(deserialized.value(&[1, 2]).unwrap(), 0);
    assert_eq!(deserialized.value(&[2, 2]).unwrap(), 1);
}

#[test]
fn test_operation_error_handling() {
    let set_size = 3;
    let op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size);
    
    // Test various error conditions
    assert!(op.value(&[0]).is_err()); // Wrong arity
    assert!(op.value(&[0, 1, 2]).is_err()); // Wrong arity
    assert!(op.value(&[0, 3]).is_err()); // Out of bounds
    assert!(op.value(&[3, 1]).is_err()); // Out of bounds
    
    // Test table access errors
    assert!(op.int_value_at_index(100).is_err()); // Invalid index
}

#[test]
fn test_operation_performance_benchmarks() {
    let set_size = 10;
    let op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size);
    
    // Benchmark table lookup vs function evaluation
    let iterations = 1000;
    
    // Time table-based evaluation
    let start = std::time::Instant::now();
    for _ in 0..iterations {
        for a in 0..set_size {
            for b in 0..set_size {
                op.value(&[a, b]).unwrap();
            }
        }
    }
    let table_time = start.elapsed();
    
    // Time function-based evaluation (if we had a function-only version)
    let start = std::time::Instant::now();
    for _ in 0..iterations {
        for a in 0..set_size {
            for b in 0..set_size {
                (a + b) % set_size;
            }
        }
    }
    let function_time = start.elapsed();
    
    // Table-based should be faster for repeated lookups
    println!("Table-based evaluation: {:?}", table_time);
    println!("Function-based evaluation: {:?}", function_time);
    
    // This is a basic benchmark - in practice, you'd use criterion for more accurate measurements
}
