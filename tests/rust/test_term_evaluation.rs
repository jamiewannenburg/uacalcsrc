use uacalc_core::prelude::*;
use uacalc_core::term::evaluation::*;
use uacalc_core::term::*;

#[test]
fn test_eval_variable() {
    let mut arena = TermArena::new();
    let var_id = arena.make_variable(0);
    
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let variables = VariableAssignment::from_values(vec![1, 2, 3]);
    
    let result = eval_term(var_id, &arena, &algebra, &variables);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 1);
}

#[test]
fn test_eval_constant() {
    let mut arena = TermArena::new();
    let symbol = OperationSymbol::new("const".to_string(), 0);
    let const_id = arena.make_term(&symbol, &[]);
    
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let variables = VariableAssignment::new();
    
    let result = eval_term(const_id, &arena, &algebra, &variables);
    assert!(result.is_ok());
}

#[test]
fn test_eval_operation() {
    let mut arena = TermArena::new();
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);
    
    // Create a binary operation
    let symbol = OperationSymbol::new("f".to_string(), 2);
    let op_id = arena.make_term(&symbol, &[x0, x1]);
    
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let variables = VariableAssignment::from_values(vec![1, 2]);
    
    let result = eval_term(op_id, &arena, &algebra, &variables);
    assert!(result.is_ok());
}

#[test]
fn test_eval_term_int() {
    let mut arena = TermArena::new();
    let var_id = arena.make_variable(0);
    
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let variable_values = vec![1, 2, 3];
    
    let result = eval_term_int(var_id, &arena, &algebra, &variable_values);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 1);
}

#[test]
fn test_eval_terms() {
    let mut arena = TermArena::new();
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);
    let term_ids = vec![x0, x1];
    
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let variables = VariableAssignment::from_values(vec![1, 2]);
    
    let result = eval_terms(&term_ids, &arena, &algebra, &variables);
    assert!(result.is_ok());
    let results = result.unwrap();
    assert_eq!(results.len(), 2);
    assert_eq!(results[0], 1);
    assert_eq!(results[1], 2);
}

#[test]
fn test_is_constant_term() {
    let mut arena = TermArena::new();
    let var_id = arena.make_variable(0);
    let symbol = OperationSymbol::new("const".to_string(), 0);
    let const_id = arena.make_term(&symbol, &[]);
    
    assert!(!is_constant_term(var_id, &arena).unwrap());
    assert!(is_constant_term(const_id, &arena).unwrap());
}

#[test]
fn test_get_constant_value() {
    let mut arena = TermArena::new();
    let symbol = OperationSymbol::new("const".to_string(), 0);
    let const_id = arena.make_term(&symbol, &[]);
    
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let result = get_constant_value(const_id, &arena, &algebra);
    assert!(result.is_ok());
    assert!(result.unwrap().is_some());
}

#[test]
fn test_evaluation_context() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let variables = VariableAssignment::from_values(vec![1, 2, 3]);
    let mut context = EvaluationContext::new(&algebra, &variables);
    
    let mut arena = TermArena::new();
    let var_id = arena.make_variable(0);
    
    let result = context.eval_term(var_id, &arena);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 1);
}

#[test]
fn test_evaluation_context_cache() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let variables = VariableAssignment::from_values(vec![1, 2, 3]);
    let mut context = EvaluationContext::new(&algebra, &variables);
    
    let mut arena = TermArena::new();
    let var_id = arena.make_variable(0);
    
    // First evaluation
    let result1 = context.eval_term(var_id, &arena);
    assert!(result1.is_ok());
    
    // Second evaluation should use cache
    let result2 = context.eval_term(var_id, &arena);
    assert!(result2.is_ok());
    
    assert_eq!(result1.unwrap(), result2.unwrap());
    assert_eq!(context.cache_size(), 1);
}

#[test]
fn test_evaluation_context_clear_cache() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let variables = VariableAssignment::from_values(vec![1, 2, 3]);
    let mut context = EvaluationContext::new(&algebra, &variables);
    
    let mut arena = TermArena::new();
    let var_id = arena.make_variable(0);
    
    // First evaluation
    let _result1 = context.eval_term(var_id, &arena);
    assert_eq!(context.cache_size(), 1);
    
    // Clear cache
    context.clear_cache();
    assert_eq!(context.cache_size(), 0);
}

#[test]
fn test_eval_term_as_term() {
    let mut arena = TermArena::new();
    let var_id = arena.make_variable(0);
    
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let variables = VariableAssignment::from_values(vec![1, 2, 3]);
    
    let result = eval_term_as_term(var_id, &arena, &algebra, &variables);
    assert!(result.is_ok());
    let term_id = result.unwrap();
    assert!(arena.is_valid_term(term_id));
}

#[test]
fn test_nested_term_evaluation() {
    let mut arena = TermArena::new();
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);
    
    // Create nested term: f(x0, f(x1, x0))
    let symbol = OperationSymbol::new("f".to_string(), 2);
    let inner_op = arena.make_term(&symbol, &[x1, x0]);
    let outer_op = arena.make_term(&symbol, &[x0, inner_op]);
    
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let variables = VariableAssignment::from_values(vec![1, 2]);
    
    let result = eval_term(outer_op, &arena, &algebra, &variables);
    assert!(result.is_ok());
}

#[test]
fn test_term_depth() {
    let mut arena = TermArena::new();
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);
    
    let symbol = OperationSymbol::new("f".to_string(), 2);
    let op = arena.make_term(&symbol, &[x0, x1]);
    
    let x0_term = arena.get_term(x0).unwrap();
    assert_eq!(x0_term.depth(&arena).unwrap(), 0);
    
    let op_term = arena.get_term(op).unwrap();
    assert_eq!(op_term.depth(&arena).unwrap(), 1);
}

#[test]
fn test_term_variables() {
    let mut arena = TermArena::new();
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);
    
    let symbol = OperationSymbol::new("f".to_string(), 2);
    let op = arena.make_term(&symbol, &[x0, x1]);
    
    let op_term = arena.get_term(op).unwrap();
    let vars = op_term.variables(&arena).unwrap();
    assert_eq!(vars, vec![0, 1]);
}

#[test]
fn test_term_to_string() {
    let mut arena = TermArena::new();
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);
    
    let symbol = OperationSymbol::new("f".to_string(), 2);
    let op = arena.make_term(&symbol, &[x0, x1]);
    
    let op_term = arena.get_term(op).unwrap();
    let string = op_term.to_string(&arena).unwrap();
    assert!(string.contains("f"));
    assert!(string.contains("x0"));
    assert!(string.contains("x1"));
}

#[test]
fn test_variable_assignment() {
    let mut assignment = VariableAssignment::new();
    assignment.assign(0, 5);
    assignment.assign(1, 10);
    
    assert_eq!(assignment.get(0), 5);
    assert_eq!(assignment.get(1), 10);
    assert_eq!(assignment.get(2), 0); // Default value
    
    assert!(assignment.is_assigned(0));
    assert!(assignment.is_assigned(1));
    assert!(!assignment.is_assigned(2));
}

#[test]
fn test_variable_assignment_from_values() {
    let assignment = VariableAssignment::from_values(vec![1, 2, 3]);
    assert_eq!(assignment.get(0), 1);
    assert_eq!(assignment.get(1), 2);
    assert_eq!(assignment.get(2), 3);
}

#[test]
fn test_variable_scope() {
    let mut scope = VariableScope::new();
    scope.assign(0, 5);
    
    scope.enter_scope();
    scope.assign(0, 10);
    scope.assign(1, 15);
    
    assert_eq!(scope.get(0), 10); // From inner scope
    assert_eq!(scope.get(1), 15); // From inner scope
    
    scope.exit_scope().unwrap();
    
    assert_eq!(scope.get(0), 5); // From outer scope
    assert_eq!(scope.get(1), 0); // Default value
}

#[test]
fn test_evaluation_with_safe_resolver() {
    // Create a simple algebra with a table operation
    let mut algebra = BasicAlgebra::with_cardinality("test".to_string(), 3).unwrap();
    
    // Create a simple binary operation table
    let mut table_op = TableOperation::new(
        OperationSymbol::new("f".to_string(), 2),
        3,
    );
    
    // Set up a simple operation: f(x,y) = (x + y) % 3
    table_op.make_table(3).unwrap();
    for x in 0..3 {
        for y in 0..3 {
            table_op.set_value(&[x, y], (x + y) % 3).unwrap();
        }
    }
    
    // Add the operation to the algebra
    algebra.add_operation_simple(table_op).unwrap();
    
    // Create a term: f(x0, x1)
    let mut arena = TermArena::new();
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);
    let symbol = OperationSymbol::new("f".to_string(), 2);
    let term_id = arena.make_term(&symbol, &[x0, x1]);
    
    // Test evaluation with different variable assignments
    let variables = VariableAssignment::from_values(vec![1, 2]);
    let result = eval_term(term_id, &arena, &algebra, &variables);
    
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 0); // (1 + 2) % 3 = 0
    
    // Test with different variables
    let variables2 = VariableAssignment::from_values(vec![2, 1]);
    let result2 = eval_term(term_id, &arena, &algebra, &variables2);
    
    assert!(result2.is_ok());
    assert_eq!(result2.unwrap(), 0); // (2 + 1) % 3 = 0
}

#[test]
fn test_evaluation_context_caching() {
    // Create a simple algebra
    let mut algebra = BasicAlgebra::with_cardinality("test".to_string(), 2).unwrap();
    
    // Create a simple unary operation
    let mut table_op = TableOperation::new(
        OperationSymbol::new("g".to_string(), 1),
        2,
    );
    table_op.make_table(2).unwrap();
    table_op.set_value(&[0], 1).unwrap();
    table_op.set_value(&[1], 0).unwrap();
    
    algebra.add_operation_simple(table_op).unwrap();
    
    // Create a term: g(x0)
    let mut arena = TermArena::new();
    let x0 = arena.make_variable(0);
    let symbol = OperationSymbol::new("g".to_string(), 1);
    let term_id = arena.make_term(&symbol, &[x0]);
    
    // Test that the evaluation context properly caches operation table availability
    let variables = VariableAssignment::from_values(vec![0]);
    let mut context = EvaluationContext::new(&algebra, &variables);
    
    let result = context.eval_term(term_id, &arena);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 1);
    
    // The context should have cached that the operation has a flat table
    assert_eq!(context.cache_size(), 1);
}
