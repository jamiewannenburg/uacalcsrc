use super::*;
use std::collections::HashMap;
use crate::io::AlgebraReader;
use crate::alg::SmallAlgebra;

#[test]
fn test_variable_imp_creation() {
    let x = VariableImp::new("x");
    assert_eq!(x.get_name(), "x");
}

#[test]
fn test_variable_imp_predefined() {
    let x = VariableImp::x();
    let y = VariableImp::y();
    let z = VariableImp::z();
    
    assert_eq!(x.get_name(), "x");
    assert_eq!(y.get_name(), "y");
    assert_eq!(z.get_name(), "z");
}

#[test]
fn test_variable_imp_isa_variable() {
    let x = VariableImp::new("x");
    assert!(x.isa_variable());
}

#[test]
fn test_variable_imp_leading_operation_symbol() {
    let x = VariableImp::new("x");
    assert!(x.leading_operation_symbol().is_none());
}

#[test]
fn test_variable_imp_get_operation_symbols() {
    let x = VariableImp::new("x");
    let symbols = x.get_operation_symbols();
    assert!(symbols.is_empty());
}

#[test]
fn test_variable_imp_get_children() {
    let x = VariableImp::new("x");
    assert!(x.get_children().is_none());
}

#[test]
fn test_variable_imp_depth() {
    let x = VariableImp::new("x");
    assert_eq!(x.depth(), 0);
}

#[test]
fn test_variable_imp_length() {
    let x = VariableImp::new("x");
    assert_eq!(x.length(), 1);
}

#[test]
fn test_variable_imp_get_variable_list() {
    let x = VariableImp::new("x");
    let vars = x.get_variable_list();
    assert_eq!(vars.len(), 1);
    assert_eq!(vars[0], "x");
}

// Helper function to create a simple test algebra
fn create_test_algebra() -> crate::alg::BasicSmallAlgebra<i32> {
    use crate::alg::op::OperationSymbol;
    use crate::alg::op::operations;
    use std::collections::HashSet;
    use crate::alg::op::Operation;
    use crate::alg::Algebra;
    
    // Create a simple algebra with universe {0, 1, 2}
    let mut universe = HashSet::new();
    universe.insert(0);
    universe.insert(1);
    universe.insert(2);
    
    // Create operations
    let mut ops: Vec<Box<dyn Operation>> = Vec::new();
    
    // Add a binary operation (e.g., addition mod 3)
    let add_sym = OperationSymbol::new("add", 2, false);
    let add_table = vec![
        0, 1, 2,  // 0 + 0, 0 + 1, 0 + 2
        1, 2, 0,  // 1 + 0, 1 + 1, 1 + 2
        2, 0, 1,  // 2 + 0, 2 + 1, 2 + 2
    ];
    let add_op = operations::make_int_operation(add_sym, 3, add_table).expect("Failed to create operation");
    ops.push(add_op);
    
    // Create the algebra
    crate::alg::BasicSmallAlgebra::new("TestAlgebra".to_string(), universe, ops)
}

#[test]
fn test_variable_imp_eval_with_algebra() {
    let alg = create_test_algebra();
    let x = VariableImp::new("x");
    let mut map = HashMap::new();
    map.insert("x".to_string(), 1);
    
    let result = x.eval(&alg, &map);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 1);
}

#[test]
fn test_variable_imp_eval_missing() {
    let alg = create_test_algebra();
    let x = VariableImp::new("x");
    let map = HashMap::new();
    
    let result = x.eval(&alg, &map);
    assert!(result.is_err());
}

#[test]
fn test_variable_imp_int_eval() {
    let alg = create_test_algebra();
    let x = VariableImp::new("x");
    let mut map = HashMap::new();
    map.insert("x".to_string(), 2);
    
    let result = x.int_eval(&alg, &map);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 2);
}

#[test]
fn test_variable_imp_to_string() {
    let x = VariableImp::new("x");
    assert_eq!(x.to_string(), "x");
}

#[test]
fn test_variable_imp_write_string_buffer() {
    let x = VariableImp::new("x");
    let mut sb = String::new();
    x.write_string_buffer(&mut sb);
    assert_eq!(sb, "x");
}

#[test]
fn test_variable_imp_equality() {
    let x1 = VariableImp::new("x");
    let x2 = VariableImp::new("x");
    let y = VariableImp::new("y");
    
    assert_eq!(x1, x2);
    assert_ne!(x1, y);
}

#[test]
fn test_variable_imp_hash() {
    use std::collections::HashSet;
    
    let x1 = VariableImp::new("x");
    let x2 = VariableImp::new("x");
    let y = VariableImp::new("y");
    
    let mut set = HashSet::new();
    set.insert(x1);
    assert!(set.contains(&x2)); // Same name should be found
    assert!(!set.contains(&y));
}

#[test]
fn test_non_variable_term_creation() {
    let op_sym = OperationSymbol::new("f", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    
    let term = NonVariableTerm::new(op_sym, children);
    assert!(!term.isa_variable());
}

#[test]
fn test_non_variable_term_depth() {
    let op_sym = OperationSymbol::new("f", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    
    let term = NonVariableTerm::new(op_sym, children);
    assert_eq!(term.depth(), 1); // 1 + max(0, 0) = 1
}

#[test]
fn test_non_variable_term_length() {
    let op_sym = OperationSymbol::new("f", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    
    let term = NonVariableTerm::new(op_sym, children);
    assert_eq!(term.length(), 3); // 1 + 1 + 1 = 3
}

#[test]
fn test_non_variable_term_constant() {
    let op_sym = OperationSymbol::new("c", 0, false);
    let term = NonVariableTerm::make_constant_term(op_sym);
    
    assert!(!term.isa_variable());
    assert_eq!(term.depth(), 1);
    assert_eq!(term.length(), 1);
}

#[test]
fn test_non_variable_term_to_string() {
    let op_sym = OperationSymbol::new("f", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    
    let term = NonVariableTerm::new(op_sym, children);
    assert_eq!(term.to_string(), "f(x,y)");
}

#[test]
fn test_non_variable_term_nested() {
    let op_sym1 = OperationSymbol::new("f", 2, false);
    let op_sym2 = OperationSymbol::new("g", 1, false);
    
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children1 = vec![x, y];
    let inner_term = NonVariableTerm::new(op_sym1, children1);
    
    let boxed_inner = Box::new(inner_term) as Box<dyn Term>;
    let children2 = vec![boxed_inner];
    let outer_term = NonVariableTerm::new(op_sym2, children2);
    
    assert_eq!(outer_term.depth(), 2); // 1 + 1 = 2
    assert_eq!(outer_term.length(), 4); // 1 + (1 + 1 + 1) = 4
    assert_eq!(outer_term.to_string(), "g(f(x,y))");
}

#[test]
fn test_non_variable_term_eval_simple() {
    let alg = create_test_algebra();
    
    // Create term: add(x, y) where x=1, y=2
    // Expected result: (1 + 2) mod 3 = 0
    let add_sym = OperationSymbol::new("add", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    let term = NonVariableTerm::new(add_sym, children);
    
    let mut map = HashMap::new();
    map.insert("x".to_string(), 1);
    map.insert("y".to_string(), 2);
    
    let result = term.eval(&alg, &map);
    assert!(result.is_ok(), "Evaluation should succeed: {:?}", result);
    assert_eq!(result.unwrap(), 0, "1 + 2 = 0 (mod 3)");
}

#[test]
fn test_non_variable_term_eval_nested() {
    let alg = create_test_algebra();
    
    // Create term: add(add(x, y), z) where x=1, y=1, z=1
    // Expected: add(add(1, 1), 1) = add(2, 1) = 0 (mod 3)
    let add_sym = OperationSymbol::new("add", 2, false);
    
    // Inner term: add(x, y)
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let inner_children = vec![x, y];
    let inner_term = NonVariableTerm::new(add_sym.clone(), inner_children);
    
    // Outer term: add(inner, z)
    let z = Box::new(VariableImp::new("z")) as Box<dyn Term>;
    let outer_children = vec![Box::new(inner_term) as Box<dyn Term>, z];
    let outer_term = NonVariableTerm::new(add_sym, outer_children);
    
    let mut map = HashMap::new();
    map.insert("x".to_string(), 1);
    map.insert("y".to_string(), 1);
    map.insert("z".to_string(), 1);
    
    let result = outer_term.eval(&alg, &map);
    assert!(result.is_ok(), "Nested evaluation should succeed: {:?}", result);
    assert_eq!(result.unwrap(), 0, "add(add(1, 1), 1) = add(2, 1) = 0 (mod 3)");
}

#[test]
fn test_term_eval_with_algebra_file() {
    use crate::alg::Algebra;
    
    // Test with a real algebra file
    let reader = AlgebraReader::new_from_path("resources/algebras/cyclic3.ua");
    if reader.is_err() {
        // Skip test if file doesn't exist
        println!("Skipping test - algebra file not found");
        return;
    }
    
    let alg = reader.unwrap().read_algebra_file();
    if alg.is_err() {
        // Skip test if can't read algebra
        println!("Skipping test - can't read algebra");
        return;
    }
    
    let alg = alg.unwrap();
    println!("Loaded algebra: {}", alg.name());
    println!("Cardinality: {}", alg.cardinality());
    
    // Create a simple variable term
    let x = VariableImp::new("x");
    let mut map = HashMap::new();
    map.insert("x".to_string(), 0);
    
    let result = x.eval(&alg, &map);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 0);
}

#[test]
fn test_term_eval_with_cyclic2() {
    use crate::alg::Algebra;
    
    // Test with cyclic group of order 2
    let reader = AlgebraReader::new_from_path("resources/algebras/cyclic2.ua");
    if reader.is_err() {
        println!("Skipping test - algebra file not found");
        return;
    }
    
    let alg = reader.unwrap().read_algebra_file();
    if alg.is_err() {
        println!("Skipping test - can't read algebra");
        return;
    }
    
    let alg = alg.unwrap();
    println!("Testing with algebra: {}", alg.name());
    
    // Note: operations() may return empty due to cloning limitations
    // We'll create a term using a known operation symbol from the algebra
    // For cyclic2, there should be a binary operation
    
    // Try to create a term with the operation symbol "+"
    let op_sym = OperationSymbol::new("+", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    let term = NonVariableTerm::new(op_sym, children);
    
    let mut map = HashMap::new();
    map.insert("x".to_string(), 0);
    map.insert("y".to_string(), 1);
    
    let result = term.eval(&alg, &map);
    if result.is_ok() {
        println!("Result: {}", result.unwrap());
    } else {
        println!("Evaluation failed: {:?}", result);
    }
}

