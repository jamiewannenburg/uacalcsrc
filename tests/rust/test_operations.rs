use uacalc_core::prelude::*;

#[test]
fn test_mixed_radix_encoding_decoding() -> Result<(), Box<dyn std::error::Error>> {
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
    Ok(())
}

#[test]
fn test_horner_table_size() -> Result<(), Box<dyn std::error::Error>> {
    assert_eq!(horner_table_size(0, 5), Some(1));
    assert_eq!(horner_table_size(1, 5), Some(5));
    assert_eq!(horner_table_size(2, 5), Some(25));
    assert_eq!(horner_table_size(3, 5), Some(125));

    // Test overflow detection
    assert_eq!(horner_table_size(20, 2), None);
    Ok(())
}

#[test]
fn test_flat_operation_table() -> Result<(), Box<dyn std::error::Error>> {
    let mut table = FlatOperationTable::new(2, 3)?;

    // Test setting and getting values
    table.set_value(&[0, 1], 2)?;
    assert_eq!(table.get_value(&[0, 1])?, 2);

    // Test index-based access
    let index = horner_encode(&[0, 1], 3).unwrap();
    table.set(index, 3)?;
    assert_eq!(table.get(index)?, 3);

    // Test bounds checking
    assert!(table.set_value(&[0, 3], 1).is_err()); // Invalid argument
    assert!(table.set(100, 1).is_err()); // Invalid index
    Ok(())
}

#[test]
fn test_table_operation_creation() -> Result<(), Box<dyn std::error::Error>> {
    // Test unary operation
    let unary_op = TableOperation::unary("neg".to_string(), 3, |x| (2 - x) % 3)?;
    assert_eq!(unary_op.arity(), 1);
    assert_eq!(unary_op.value(&[0])?, 2);
    assert_eq!(unary_op.value(&[1])?, 1);
    assert_eq!(unary_op.value(&[2])?, 0);

    // Test binary operation
    let binary_op = TableOperation::binary("add".to_string(), 3, |a, b| (a + b) % 3)?;
    assert_eq!(binary_op.arity(), 2);
    assert_eq!(binary_op.value(&[1, 2])?, 0);
    assert_eq!(binary_op.value(&[2, 2])?, 1);

    // Test constant operation
    let const_op = TableOperation::constant("zero".to_string(), 0, 3)?;
    assert_eq!(const_op.arity(), 0);
    assert_eq!(const_op.value(&[])?, 0);

    // Test identity operation
    let id_op = TableOperation::identity(3)?;
    assert_eq!(id_op.arity(), 1);
    assert_eq!(id_op.value(&[0])?, 0);
    assert_eq!(id_op.value(&[1])?, 1);
    assert_eq!(id_op.value(&[2])?, 2);
    Ok(())
}

#[test]
fn test_operation_properties() -> Result<(), Box<dyn std::error::Error>> {
    let set_size = 3;

    // Test idempotent operation
    let idempotent_op = TableOperation::unary("id".to_string(), set_size, |x| x)?;
    assert!(idempotent_op.is_idempotent_on_set(set_size)?);

    // Test non-idempotent operation
    let non_idempotent_op =
        TableOperation::unary("inc".to_string(), set_size, |x| (x + 1) % set_size)?;
    assert!(!non_idempotent_op.is_idempotent_on_set(set_size)?);

    // Test associative operation (addition modulo 3)
    let associative_op =
        TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size)?;
    assert!(associative_op.is_associative_on_set(set_size)?);

    // Test commutative operation
    let commutative_op =
        TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size)?;
    assert!(commutative_op.is_commutative_on_set(set_size)?);

    // Test non-commutative operation
    let non_commutative_op = TableOperation::binary("sub".to_string(), set_size, |a, b| {
        (a + set_size - b) % set_size
    })?;
    assert!(!non_commutative_op.is_commutative_on_set(set_size)?);
    Ok(())
}

#[test]
fn test_function_operation() -> Result<(), Box<dyn std::error::Error>> {
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
    assert_eq!(function_op.value(&[1, 2])?, 3);
    assert_eq!(function_op.value(&[2, 3])?, 1);

    // Test table generation
    let mut op_with_table = function_op;
    op_with_table.make_table(set_size)?;

    // Verify table-based evaluation matches function evaluation
    assert_eq!(op_with_table.value(&[1, 2])?, 3);
    assert_eq!(op_with_table.value(&[2, 3])?, 1);
    Ok(())
}

#[test]
fn test_operation_validation() -> Result<(), Box<dyn std::error::Error>> {
    let set_size = 3;
    let op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size)?;

    // Test valid arguments
    assert!(op.value(&[0, 1]).is_ok());
    assert!(op.value(&[2, 2]).is_ok());

    // Test invalid arity
    assert!(op.value(&[0]).is_err());
    assert!(op.value(&[0, 1, 2]).is_err());

    // Test invalid arguments (out of bounds)
    assert!(op.value(&[0, 3]).is_err());
    assert!(op.value(&[3, 1]).is_err());
    Ok(())
}

#[test]
fn test_operation_creation_with_validation() -> Result<(), Box<dyn std::error::Error>> {
    let set_size = 3;

    // This should fail because the function returns values >= set_size
    let result = TableOperation::unary("invalid".to_string(), set_size, |x| x + 1);
    assert!(result.is_err());

    // This should also fail for the same reason
    let result = TableOperation::binary("invalid".to_string(), set_size, |a, b| a + b);
    assert!(result.is_err());

    // These should succeed because they use modulo arithmetic
    let result = TableOperation::unary("valid".to_string(), set_size, |x| (x + 1) % set_size);
    assert!(result.is_ok());

    let result = TableOperation::binary("valid".to_string(), set_size, |a, b| (a + b) % set_size);
    assert!(result.is_ok());
    Ok(())
}

#[test]
fn test_set_value_validation() -> Result<(), Box<dyn std::error::Error>> {
    let set_size = 3;
    let mut table = FlatOperationTable::new(2, set_size)?;

    // Test valid values
    assert!(table.set_value(&[0, 1], 2).is_ok());
    assert!(table.set_value(&[1, 2], 0).is_ok());

    // Test invalid values (out of bounds)
    assert!(table.set_value(&[0, 1], 3).is_err()); // 3 >= set_size
    assert!(table.set_value(&[1, 2], 5).is_err()); // 5 >= set_size

    // Test that the error is the correct type
    let result = table.set_value(&[0, 0], 3);
    assert!(matches!(
        result,
        Err(UACalcError::IndexOutOfBounds { index: 3, size: 3 })
    ));
    Ok(())
}

#[test]
fn test_operation_table_memory_estimation() -> Result<(), Box<dyn std::error::Error>> {
    // Test memory estimation for various table sizes
    assert_eq!(estimate_table_memory(2, 5), Some(200)); // 25 * 8 bytes
    assert_eq!(estimate_table_memory(3, 4), Some(512)); // 64 * 8 bytes

    // Test overflow detection
    assert_eq!(estimate_table_memory(10, 2), None);
    Ok(())
}

#[test]
fn test_operation_from_function() -> Result<(), Box<dyn std::error::Error>> {
    let set_size = 3;
    let symbol = OperationSymbol::new("ternary".to_string(), 3);

    let op = TableOperation::from_function(symbol, set_size, |args| {
        let a = args[0];
        let b = args[1];
        let c = args[2];
        Ok((a + b + c) % set_size)
    })?;

    assert_eq!(op.arity(), 3);
    assert_eq!(op.value(&[0, 1, 2])?, 0);
    assert_eq!(op.value(&[1, 1, 1])?, 0);
    assert_eq!(op.value(&[2, 2, 2])?, 0);
    Ok(())
}

#[test]
fn test_operation_int_value_methods() -> Result<(), Box<dyn std::error::Error>> {
    let set_size = 4;
    let op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size)?;

    // Test int_value_at
    assert_eq!(op.int_value_at(&[1, 2])?, 3);
    assert_eq!(op.int_value_at(&[2, 3])?, 1);

    // Test int_value_at_index
    let index = horner_encode(&[1, 2], set_size).unwrap();
    assert_eq!(op.int_value_at_index(index)?, 3);

    // Test decode_index
    let decoded = op.decode_index(index)?;
    assert_eq!(decoded, vec![1, 2]);
    Ok(())
}

#[test]
fn test_operation_table_completeness() -> Result<(), Box<dyn std::error::Error>> {
    let set_size = 2;
    let op = TableOperation::binary("and".to_string(), set_size, |a, b| a & b)?;

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
    Ok(())
}

#[test]
fn test_operation_serialization() -> Result<(), Box<dyn std::error::Error>> {
    let set_size = 3;
    let op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size)?;

    // Test serialization
    let serialized = serde_json::to_string(&op)?;
    let deserialized: TableOperation = serde_json::from_str(&serialized)?;

    // Verify deserialized operation works correctly
    assert_eq!(deserialized.arity(), 2);
    assert_eq!(deserialized.value(&[1, 2])?, 0);
    assert_eq!(deserialized.value(&[2, 2])?, 1);
    Ok(())
}

#[test]
fn test_operation_error_handling() -> Result<(), Box<dyn std::error::Error>> {
    let set_size = 3;
    let op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size)?;

    // Test various error conditions
    assert!(op.value(&[0]).is_err()); // Wrong arity
    assert!(op.value(&[0, 1, 2]).is_err()); // Wrong arity
    assert!(op.value(&[0, 3]).is_err()); // Out of bounds
    assert!(op.value(&[3, 1]).is_err()); // Out of bounds

    // Test table access errors
    assert!(op.int_value_at_index(100).is_err()); // Invalid index
    Ok(())
}

#[test]
fn test_operation_performance_benchmarks() -> Result<(), Box<dyn std::error::Error>> {
    let set_size = 10;
    let op = TableOperation::binary("add".to_string(), set_size, |a, b| (a + b) % set_size)?;

    // Benchmark table lookup vs function evaluation
    let iterations = 1000;

    // Time table-based evaluation
    let start = std::time::Instant::now();
    for _ in 0..iterations {
        for a in 0..set_size {
            for b in 0..set_size {
                op.value(&[a, b])?;
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
    Ok(())
}

#[test]
fn test_basic_algebra_make_operation_tables() -> Result<(), Box<dyn std::error::Error>> {
    use std::sync::{Arc, Mutex};

    // Create a basic algebra with universe {0, 1, 2}
    let mut algebra = BasicAlgebra::new("test_algebra".to_string(), vec![0, 1, 2])?;

    // Create some operations
    let unary_op = Arc::new(Mutex::new(TableOperation::unary(
        "neg".to_string(),
        3,
        |x| (2 - x) % 3,
    )?));
    let binary_op = Arc::new(Mutex::new(TableOperation::binary(
        "add".to_string(),
        3,
        |a, b| (a + b) % 3,
    )?));

    // Add operations to algebra
    algebra.add_operation("neg".to_string(), unary_op)?;
    algebra.add_operation("add".to_string(), binary_op)?;

    // Initially, tables should not be built
    assert!(!algebra.tables_built());

    // Call make_operation_tables
    algebra.make_operation_tables()?;

    // Now tables should be built
    assert!(algebra.tables_built());

    // Verify operations still work correctly
    let neg_op = algebra.operation_arc_by_symbol("neg")?;
    let add_op = algebra.operation_arc_by_symbol("add")?;

    let neg_guard = neg_op.lock().unwrap();
    let add_guard = add_op.lock().unwrap();

    assert_eq!(neg_guard.value(&[0])?, 2);
    assert_eq!(neg_guard.value(&[1])?, 1);
    assert_eq!(neg_guard.value(&[2])?, 0);

    assert_eq!(add_guard.value(&[1, 2])?, 0);
    assert_eq!(add_guard.value(&[2, 2])?, 1);

    // Verify tables are available
    assert!(neg_guard.get_table().is_some());
    assert!(add_guard.get_table().is_some());
    Ok(())
}

#[test]
fn test_basic_algebra_subalgebra() -> Result<(), Box<dyn std::error::Error>> {
    use std::sync::{Arc, Mutex};

    // Create a basic algebra with universe {0, 1, 2, 3}
    let mut algebra = BasicAlgebra::new("test_algebra".to_string(), vec![0, 1, 2, 3])?;

    // Create a binary operation: addition modulo 4
    let add_op = Arc::new(Mutex::new(TableOperation::binary(
        "add".to_string(),
        4,
        |a, b| (a + b) % 4,
    )?));

    // Create a unary operation: negation modulo 4
    let neg_op = Arc::new(Mutex::new(TableOperation::unary(
        "neg".to_string(),
        4,
        |x| (4 - x) % 4,
    )?));

    // Add operations to algebra
    algebra.add_operation("add".to_string(), add_op)?;
    algebra.add_operation("neg".to_string(), neg_op)?;

    // Create subalgebra generated by {1}
    // This should generate the universe {0, 1, 2, 3} because:
    // - 1 is in the generators
    // - neg(1) = 3 is in the closure
    // - add(1, 1) = 2 is in the closure
    // - add(1, 2) = 3 is in the closure
    // - add(1, 3) = 0 is in the closure
    // - etc.
    let subalgebra = algebra.subalgebra(&[1])?;

    // Verify subalgebra properties
    assert_eq!(subalgebra.name(), "test_algebra_sub");
    assert_eq!(subalgebra.cardinality(), 4); // Should generate the full algebra
    assert_eq!(subalgebra.universe(), &[0, 1, 2, 3]);

    // Verify operations are preserved
    assert_eq!(subalgebra.operations().len(), 2);

    // Test that operations work correctly in the subalgebra
    let add_op_sub = subalgebra.operation_arc_by_symbol("add")?;
    let neg_op_sub = subalgebra.operation_arc_by_symbol("neg")?;

    let add_guard = add_op_sub.lock().unwrap();
    let neg_guard = neg_op_sub.lock().unwrap();

    // Test addition in subalgebra
    assert_eq!(add_guard.value(&[1, 2])?, 3);
    assert_eq!(add_guard.value(&[2, 3])?, 1);
    assert_eq!(add_guard.value(&[3, 1])?, 0);

    // Test negation in subalgebra
    assert_eq!(neg_guard.value(&[1])?, 3);
    assert_eq!(neg_guard.value(&[2])?, 2);
    assert_eq!(neg_guard.value(&[3])?, 1);

    // Test subalgebra with different generators
    let subalgebra2 = algebra.subalgebra(&[0, 2])?;
    assert_eq!(subalgebra2.cardinality(), 4); // Should still generate the full algebra

    // Test subalgebra with single generator that doesn't generate everything
    let subalgebra3 = algebra.subalgebra(&[0])?;
    // This should only contain {0} since 0 + 0 = 0 and neg(0) = 0
    assert_eq!(subalgebra3.cardinality(), 1);
    assert_eq!(subalgebra3.universe(), &[0]);

    Ok(())
}
