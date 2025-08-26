use uacalc_core::algebra::BasicAlgebra;
use uacalc_core::operation::OperationSymbol;
use uacalc_core::prelude::*;
use uacalc_core::term::evaluation::{EvaluationContext, EvaluationStats};

#[test]
fn test_zero_allocation_evaluation() {
    // Create a simple algebra
    let algebra = BasicAlgebra::with_cardinality("test".to_string(), 3).unwrap();

    // Create a term arena with some terms
    let mut arena = TermArena::new();
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);

    // Create a binary operation term
    let symbol = OperationSymbol::new("f".to_string(), 2);
    let op_id = arena.make_term(&symbol, &[x0, x1]);

    // Create variable assignment
    let variables = VariableAssignment::from_values(vec![1, 2]);

    // Test evaluation with zero allocation context
    let mut context = EvaluationContext::new(&algebra, &variables);
    let result = context.eval_term(op_id, &arena);

    assert!(result.is_ok());

    // Check memory stats
    let stats = context.memory_stats();
    assert!(stats.cache_size > 0);
    assert!(stats.stack_size == 0); // Stack should be empty after evaluation
    assert!(stats.max_arity > 0);
}

#[test]
fn test_stack_allocated_args() {
    // Create algebra with multiple operations
    let algebra = BasicAlgebra::with_cardinality("test".to_string(), 2).unwrap();

    // Create a complex term structure
    let mut arena = TermArena::new();
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);

    // Create nested operations to test stack allocation
    let symbol1 = OperationSymbol::new("f".to_string(), 2);
    let op1 = arena.make_term(&symbol1, &[x0, x1]);

    let symbol2 = OperationSymbol::new("g".to_string(), 1);
    let op2 = arena.make_term(&symbol2, &[op1]);

    let variables = VariableAssignment::from_values(vec![0, 1]);

    let mut context = EvaluationContext::new(&algebra, &variables);
    let result = context.eval_term(op2, &arena);

    assert!(result.is_ok());

    // Verify cache efficiency
    let stats = context.memory_stats();
    assert!(stats.cache_size >= 3); // Should cache x0, x1, op1, op2
}

#[test]
fn test_arity_validation() {
    let algebra = BasicAlgebra::with_cardinality("test".to_string(), 2).unwrap();
    let mut arena = TermArena::new();

    // Create a term with reasonable arity
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);
    let symbol = OperationSymbol::new("f".to_string(), 2);
    let op_id = arena.make_term(&symbol, &[x0, x1]);

    let variables = VariableAssignment::from_values(vec![0, 1]);
    let mut context = EvaluationContext::new(&algebra, &variables);

    // This should work fine
    let result = context.eval_term(op_id, &arena);
    assert!(result.is_ok());

    // Check that arity validation was performed
    let stats = context.memory_stats();
    assert_eq!(stats.max_arity, 2);
}

#[test]
fn test_cache_efficiency() {
    let algebra = BasicAlgebra::with_cardinality("test".to_string(), 3).unwrap();
    let mut arena = TermArena::new();

    // Create shared subterms to test caching
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);

    let symbol1 = OperationSymbol::new("f".to_string(), 2);
    let shared_term = arena.make_term(&symbol1, &[x0, x1]);

    let symbol2 = OperationSymbol::new("g".to_string(), 2);
    let op1 = arena.make_term(&symbol2, &[shared_term, x0]);
    let op2 = arena.make_term(&symbol2, &[shared_term, x1]);

    let variables = VariableAssignment::from_values(vec![1, 2]);
    let mut context = EvaluationContext::new(&algebra, &variables);

    // Evaluate both terms
    let result1 = context.eval_term(op1, &arena);
    let result2 = context.eval_term(op2, &arena);

    assert!(result1.is_ok());
    assert!(result2.is_ok());

    // The shared term should only be evaluated once
    let stats = context.memory_stats();
    assert!(stats.cache_size >= 4); // x0, x1, shared_term, op1, op2
}
