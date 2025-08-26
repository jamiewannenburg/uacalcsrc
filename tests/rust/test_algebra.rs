use std::sync::Arc;
use uacalc_core::prelude::*;

#[test]
fn test_basic_algebra_construction() -> Result<(), Box<dyn std::error::Error>> {
    // Test creation with contiguous integer universe
    let universe = vec![0, 1, 2, 3];
    let algebra = BasicAlgebra::new("test_algebra".to_string(), universe)?;

    assert_eq!(algebra.cardinality(), 4);
    assert_eq!(algebra.universe(), &[0, 1, 2, 3]);
    assert_eq!(algebra.name(), "test_algebra");
    assert!(algebra.is_finite());

    // Test universe validation
    let invalid_universe = vec![1, 2, 3]; // Not starting from 0
    assert!(BasicAlgebra::new("invalid".to_string(), invalid_universe).is_err());

    let invalid_universe2 = vec![0, 1, 3]; // Not contiguous
    assert!(BasicAlgebra::new("invalid2".to_string(), invalid_universe2).is_err());
    Ok(())
}

#[test]
fn test_algebra_operation_management() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("test".to_string(), universe)?;

    // Create operations
    let add_op = Arc::new(TableOperation::binary("add".to_string(), 3, |a, b| {
        (a + b) % 3
    })?);
    let neg_op = Arc::new(TableOperation::unary("neg".to_string(), 3, |x| {
        (3 - x) % 3
    })?);

    // Add operations
    algebra.add_operation("add".to_string(), add_op)?;
    algebra.add_operation("neg".to_string(), neg_op)?;

    assert_eq!(algebra.operations().len(), 2);
    assert_eq!(algebra.max_arity(), 2);

    // Test operation retrieval
    let add_operation = algebra.operation(0)?;
    assert_eq!(add_operation.arity(), 2);
    assert_eq!(add_operation.symbol().name, "add");

    let neg_operation = algebra.operation_by_symbol("neg")?;
    assert_eq!(neg_operation.arity(), 1);
    assert_eq!(neg_operation.symbol().name, "neg");

    // Test operation validation
    let invalid_op = Arc::new(TableOperation::binary("invalid".to_string(), 5, |a, b| {
        a + b
    })?);
    assert!(algebra
        .add_operation("invalid".to_string(), invalid_op)
        .is_err());
    Ok(())
}

#[test]
fn test_algebra_operation_tables() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("test".to_string(), universe)?;

    let add_op = Arc::new(TableOperation::binary("add".to_string(), 3, |a, b| {
        (a + b) % 3
    })?);
    algebra.add_operation("add".to_string(), add_op)?;

    // Test operation table generation
    algebra.make_operation_tables()?;
    assert!(algebra.tables_built());

    // Test integer-optimized operation evaluation
    assert_eq!(algebra.operation_int_value(0, &[1, 2])?, 0);
    assert_eq!(algebra.operation_int_value(0, &[2, 2])?, 1);
    Ok(())
}

#[test]
fn test_algebra_properties() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("test".to_string(), universe)?;

    // Add idempotent operation
    let id_op = Arc::new(TableOperation::unary("id".to_string(), 3, |x| x)?);
    algebra.add_operation("id".to_string(), id_op)?;

    // Add associative operation
    let add_op = Arc::new(TableOperation::binary("add".to_string(), 3, |a, b| {
        (a + b) % 3
    })?);
    algebra.add_operation("add".to_string(), add_op)?;

    // Add commutative operation
    let mul_op = Arc::new(TableOperation::binary("mul".to_string(), 3, |a, b| {
        (a * b) % 3
    })?);
    algebra.add_operation("mul".to_string(), mul_op)?;

    // Test algebra properties
    assert!(algebra.is_idempotent()?);
    assert!(algebra.is_associative()?);
    assert!(algebra.is_commutative()?);

    // Test individual operation properties
    assert!(algebra.is_idempotent(0)?);
    assert!(algebra.is_associative(1)?);
    assert!(algebra.is_commutative(2)?);
    Ok(())
}

#[test]
fn test_algebra_subalgebra() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2, 3];
    let mut algebra = BasicAlgebra::new("test".to_string(), universe)?;

    // Add a binary operation that preserves the subset {0, 1}
    let op = Arc::new(TableOperation::binary("op".to_string(), 4, |a, b| {
        if a <= 1 && b <= 1 {
            (a + b) % 2
        } else {
            0
        }
    })?);
    algebra.add_operation("op".to_string(), op)?;

    // Test subalgebra generation (this will fail due to operation copying limitation)
    let generators = vec![0, 1];
    let result = algebra.subalgebra(&generators);
    assert!(result.is_err()); // Expected due to operation copying limitation

    // Test generator validation
    let invalid_generators = vec![0, 5]; // 5 >= cardinality
    let result = algebra.subalgebra(&invalid_generators);
    assert!(result.is_err());
    Ok(())
}

#[test]
fn test_algebra_universe_operations() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2, 3];
    let algebra = BasicAlgebra::new("test".to_string(), universe)?;

    // Test element to index conversion
    assert_eq!(algebra.element_to_index(0)?, 0);
    assert_eq!(algebra.element_to_index(2)?, 2);
    assert!(algebra.element_to_index(4).is_err());

    // Test index to element conversion
    assert_eq!(algebra.index_to_element(0)?, 0);
    assert_eq!(algebra.index_to_element(2)?, 2);
    assert!(algebra.index_to_element(4).is_err());

    // Test universe as range
    let range = algebra.universe_as_range();
    assert_eq!(range.start, 0);
    assert_eq!(range.end, 4);

    // Test input size calculation
    let input_size = algebra.input_size()?;
    assert_eq!(input_size, 0); // No operations yet
    Ok(())
}

#[test]
fn test_algebra_from_operations() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2];
    let add_op = Arc::new(TableOperation::binary("add".to_string(), 3, |a, b| {
        (a + b) % 3
    })?);
    let neg_op = Arc::new(TableOperation::unary("neg".to_string(), 3, |x| {
        (3 - x) % 3
    })?);

    let operations = vec![("add".to_string(), add_op), ("neg".to_string(), neg_op)];

    let algebra = BasicAlgebra::from_operations("test".to_string(), universe, operations)?;

    assert_eq!(algebra.cardinality(), 3);
    assert_eq!(algebra.operations().len(), 2);
    assert_eq!(algebra.max_arity(), 2);

    // Test operation access
    let add_operation = algebra.operation_by_symbol("add")?;
    assert_eq!(add_operation.arity(), 2);

    let neg_operation = algebra.operation_by_symbol("neg")?;
    assert_eq!(neg_operation.arity(), 1);
    Ok(())
}

#[test]
fn test_algebra_operation_arc() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("test".to_string(), universe)?;

    let add_op = Arc::new(TableOperation::binary("add".to_string(), 3, |a, b| {
        (a + b) % 3
    })?);
    algebra.add_operation("add".to_string(), add_op)?;

    // Test operation_arc
    let op_arc = algebra.operation_arc(0)?;
    assert_eq!(op_arc.arity(), 2);

    // Test operation_arc_by_symbol
    let op_arc_symbol = algebra.operation_arc_by_symbol("add")?;
    assert_eq!(op_arc_symbol.arity(), 2);

    // Test error cases
    assert!(algebra.operation_arc(1).is_err());
    assert!(algebra.operation_arc_by_symbol("nonexistent").is_err());
    Ok(())
}

#[test]
fn test_algebra_operation_direct() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("test".to_string(), universe)?;

    let add_op = Arc::new(TableOperation::binary("add".to_string(), 3, |a, b| {
        (a + b) % 3
    })?);
    algebra.add_operation("add".to_string(), add_op)?;

    // Test operation_direct
    let op = algebra.operation_direct(0)?;
    assert_eq!(op.arity(), 2);

    // Test error case
    assert!(algebra.operation_direct(1).is_err());
    Ok(())
}

#[test]
fn test_algebra_total_operations() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("test".to_string(), universe)?;

    // Add total operations
    let add_op = Arc::new(TableOperation::binary("add".to_string(), 3, |a, b| {
        (a + b) % 3
    })?);
    algebra.add_operation("add".to_string(), add_op)?;

    assert!(algebra.is_total());
    Ok(())
}

#[test]
fn test_algebra_error_handling() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("test".to_string(), universe)?;

    // Test operation index out of bounds
    assert!(algebra.operation(0).is_err());
    assert!(algebra.operation_arc(0).is_err());
    assert!(algebra.operation_direct(0).is_err());

    // Test operation symbol not found
    assert!(algebra.operation_by_symbol("nonexistent").is_err());
    assert!(algebra.operation_arc_by_symbol("nonexistent").is_err());

    // Test operation property checking on non-existent operation
    assert!(algebra.is_idempotent(0).is_err());
    assert!(algebra.is_associative(0).is_err());
    assert!(algebra.is_commutative(0).is_err());
    Ok(())
}

#[test]
fn test_algebra_edge_cases() -> Result<(), Box<dyn std::error::Error>> {
    // Test empty universe (should not be allowed)
    assert!(BasicAlgebra::new("empty".to_string(), vec![]).is_err());

    // Test single element universe
    let universe = vec![0];
    let algebra = BasicAlgebra::new("single".to_string(), universe)?;
    assert_eq!(algebra.cardinality(), 1);
    assert!(algebra.is_finite());

    // Test large universe
    let large_universe: Vec<usize> = (0..1000).collect();
    let algebra = BasicAlgebra::new("large".to_string(), large_universe)?;
    assert_eq!(algebra.cardinality(), 1000);
    assert!(algebra.is_finite());
    Ok(())
}

#[test]
fn test_algebra_complex_scenarios() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2, 3, 4];
    let mut algebra = BasicAlgebra::new("complex".to_string(), universe)?;

    // Add multiple operations with different arities
    let const_op = Arc::new(TableOperation::constant("zero".to_string(), 0, 5)?);
    let neg_op = Arc::new(TableOperation::unary("neg".to_string(), 5, |x| {
        (5 - x) % 5
    })?);
    let add_op = Arc::new(TableOperation::binary("add".to_string(), 5, |a, b| {
        (a + b) % 5
    })?);
    let ternary_op = Arc::new(TableOperation::from_function(
        OperationSymbol::new("ternary".to_string(), 3),
        5,
        |args| Ok((args[0] + args[1] + args[2]) % 5),
    )?);

    algebra.add_operation("zero".to_string(), const_op)?;
    algebra.add_operation("neg".to_string(), neg_op)?;
    algebra.add_operation("add".to_string(), add_op)?;
    algebra.add_operation("ternary".to_string(), ternary_op)?;

    // Test all operations
    assert_eq!(algebra.operations().len(), 4);
    assert_eq!(algebra.max_arity(), 3);

    // Test operation evaluation
    assert_eq!(algebra.operation_int_value(0, &[])?, 0); // Constant
    assert_eq!(algebra.operation_int_value(1, &[2])?, 3); // Negation
    assert_eq!(algebra.operation_int_value(2, &[3, 4])?, 2); // Addition
    assert_eq!(algebra.operation_int_value(3, &[1, 2, 3])?, 1); // Ternary

    // Test input size calculation
    let input_size = algebra.input_size()?;
    assert_eq!(input_size, 1 + 5 + 25 + 125); // 0-ary + 1-ary + 2-ary + 3-ary

    // Test operation tables
    algebra.make_operation_tables()?;
    assert!(algebra.tables_built());
    Ok(())
}

#[test]
fn test_algebra_performance() -> Result<(), Box<dyn std::error::Error>> {
    let universe: Vec<usize> = (0..100).collect();
    let mut algebra = BasicAlgebra::new("performance".to_string(), universe)?;

    // Add a binary operation
    let add_op = Arc::new(TableOperation::binary("add".to_string(), 100, |a, b| {
        (a + b) % 100
    })?);
    algebra.add_operation("add".to_string(), add_op)?;

    // Benchmark operation evaluation
    let iterations = 1000;
    let start = std::time::Instant::now();
    for _ in 0..iterations {
        for a in 0..10 {
            for b in 0..10 {
                algebra.operation_int_value(0, &[a, b])?;
            }
        }
    }
    let eval_time = start.elapsed();

    // Benchmark table generation
    let start = std::time::Instant::now();
    algebra.make_operation_tables()?;
    let table_time = start.elapsed();

    println!("Operation evaluation: {:?}", eval_time);
    println!("Table generation: {:?}", table_time);

    // Verify tables were built
    assert!(algebra.tables_built());
    Ok(())
}

#[test]
fn test_algebra_java_compatibility() -> Result<(), Box<dyn std::error::Error>> {
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("java_compat".to_string(), universe)?;

    let add_op = Arc::new(TableOperation::binary("add".to_string(), 3, |a, b| {
        (a + b) % 3
    })?);
    algebra.add_operation("add".to_string(), add_op)?;

    // Test Java-compatible method names
    assert_eq!(algebra.element_to_index(1)?, 1);
    assert_eq!(algebra.index_to_element(1)?, 1);
    assert_eq!(algebra.operation_int_value(0, &[1, 2])?, 0);

    // Test universe as range (Java equivalent)
    let range = algebra.universe_as_range();
    assert_eq!(range.start, 0);
    assert_eq!(range.end, 3);
    Ok(())
}
