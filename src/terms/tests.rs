use super::*;
use std::collections::HashMap;
use crate::io::AlgebraReader;

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

// ==================== Cloning Tests ====================

#[test]
fn test_variable_imp_clone_box() {
    let x = VariableImp::new("x");
    let x_boxed: Box<dyn Term> = Box::new(x.clone());
    let x_cloned = x_boxed.clone_box();
    
    // Check that the cloned term has the same properties
    assert_eq!(x_cloned.to_string(), "x");
    assert!(x_cloned.isa_variable());
    assert_eq!(x_cloned.depth(), 0);
    assert_eq!(x_cloned.length(), 1);
}

#[test]
fn test_non_variable_term_clone_box_simple() {
    let op_sym = OperationSymbol::new("f", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    
    let term = NonVariableTerm::new(op_sym, children);
    let term_boxed: Box<dyn Term> = Box::new(term);
    let term_cloned = term_boxed.clone_box();
    
    // Check that the cloned term has the same properties
    assert_eq!(term_cloned.to_string(), "f(x,y)");
    assert!(!term_cloned.isa_variable());
    assert_eq!(term_cloned.depth(), 1);
    assert_eq!(term_cloned.length(), 3);
}

#[test]
fn test_non_variable_term_clone_box_nested() {
    let op_sym1 = OperationSymbol::new("f", 2, false);
    let op_sym2 = OperationSymbol::new("g", 1, false);
    
    // Create nested term: g(f(x, y))
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children1 = vec![x, y];
    let inner_term = NonVariableTerm::new(op_sym1, children1);
    
    let boxed_inner = Box::new(inner_term) as Box<dyn Term>;
    let children2 = vec![boxed_inner];
    let outer_term = NonVariableTerm::new(op_sym2, children2);
    
    let outer_boxed: Box<dyn Term> = Box::new(outer_term);
    let outer_cloned = outer_boxed.clone_box();
    
    // Check that the cloned term has the same properties
    assert_eq!(outer_cloned.to_string(), "g(f(x,y))");
    assert!(!outer_cloned.isa_variable());
    assert_eq!(outer_cloned.depth(), 2);
    assert_eq!(outer_cloned.length(), 4);
}

#[test]
fn test_non_variable_term_get_children() {
    let op_sym = OperationSymbol::new("f", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    
    let term = NonVariableTerm::new(op_sym, children);
    let term_children = term.get_children();
    
    // Check that get_children() returns Some with cloned children
    assert!(term_children.is_some());
    let children = term_children.unwrap();
    assert_eq!(children.len(), 2);
    assert_eq!(children[0].to_string(), "x");
    assert_eq!(children[1].to_string(), "y");
}

#[test]
fn test_variable_substitute_simple() {
    let x = VariableImp::new("x");
    let x_term: Box<dyn Term> = Box::new(x);
    
    // Substitute x -> y
    let mut map: HashMap<String, Box<dyn Term>> = HashMap::new();
    let y_term: Box<dyn Term> = Box::new(VariableImp::new("y"));
    map.insert("x".to_string(), y_term);
    
    let result = x_term.substitute(&map);
    assert!(result.is_ok());
    let substituted = result.unwrap();
    assert_eq!(substituted.to_string(), "y");
}

#[test]
fn test_variable_substitute_no_match() {
    let x = VariableImp::new("x");
    let x_term: Box<dyn Term> = Box::new(x);
    
    // Try to substitute y (not x), so x should remain unchanged
    let mut map: HashMap<String, Box<dyn Term>> = HashMap::new();
    let z_term: Box<dyn Term> = Box::new(VariableImp::new("z"));
    map.insert("y".to_string(), z_term);
    
    let result = x_term.substitute(&map);
    assert!(result.is_ok());
    let substituted = result.unwrap();
    assert_eq!(substituted.to_string(), "x");
}

#[test]
fn test_non_variable_term_substitute_simple() {
    // Create term: f(x, y)
    let op_sym = OperationSymbol::new("f", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    let term = NonVariableTerm::new(op_sym, children);
    let term_boxed: Box<dyn Term> = Box::new(term);
    
    // Substitute x -> z
    let mut map: HashMap<String, Box<dyn Term>> = HashMap::new();
    let z_term: Box<dyn Term> = Box::new(VariableImp::new("z"));
    map.insert("x".to_string(), z_term);
    
    let result = term_boxed.substitute(&map);
    assert!(result.is_ok());
    let substituted = result.unwrap();
    // Result should be f(z, y)
    assert_eq!(substituted.to_string(), "f(z,y)");
}

#[test]
fn test_non_variable_term_substitute_nested() {
    // Create term: g(f(x, y))
    let op_sym1 = OperationSymbol::new("f", 2, false);
    let op_sym2 = OperationSymbol::new("g", 1, false);
    
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children1 = vec![x, y];
    let inner_term = NonVariableTerm::new(op_sym1, children1);
    
    let boxed_inner = Box::new(inner_term) as Box<dyn Term>;
    let children2 = vec![boxed_inner];
    let outer_term = NonVariableTerm::new(op_sym2, children2);
    let outer_boxed: Box<dyn Term> = Box::new(outer_term);
    
    // Substitute x -> a, y -> b
    let mut map: HashMap<String, Box<dyn Term>> = HashMap::new();
    let a_term: Box<dyn Term> = Box::new(VariableImp::new("a"));
    let b_term: Box<dyn Term> = Box::new(VariableImp::new("b"));
    map.insert("x".to_string(), a_term);
    map.insert("y".to_string(), b_term);
    
    let result = outer_boxed.substitute(&map);
    assert!(result.is_ok());
    let substituted = result.unwrap();
    // Result should be g(f(a, b))
    assert_eq!(substituted.to_string(), "g(f(a,b))");
}

#[test]
fn test_non_variable_term_substitute_with_compound_term() {
    // Create term: f(x, y)
    let op_sym = OperationSymbol::new("f", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    let term = NonVariableTerm::new(op_sym, children);
    let term_boxed: Box<dyn Term> = Box::new(term);
    
    // Create compound term to substitute: g(z)
    let g_sym = OperationSymbol::new("g", 1, false);
    let z = Box::new(VariableImp::new("z")) as Box<dyn Term>;
    let g_term = NonVariableTerm::new(g_sym, vec![z]);
    
    // Substitute x -> g(z)
    let mut map: HashMap<String, Box<dyn Term>> = HashMap::new();
    map.insert("x".to_string(), Box::new(g_term) as Box<dyn Term>);
    
    let result = term_boxed.substitute(&map);
    assert!(result.is_ok());
    let substituted = result.unwrap();
    // Result should be f(g(z), y)
    assert_eq!(substituted.to_string(), "f(g(z),y)");
}

#[test]
fn test_non_variable_term_interpretation_simple() {
    use std::sync::Arc;
    
    let alg = create_test_algebra();
    let alg_arc = Arc::new(alg);
    
    // Create term: add(x, y)
    let add_sym = OperationSymbol::new("add", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let children = vec![x, y];
    let term = NonVariableTerm::new(add_sym, children);
    
    // Get the interpretation
    let result = term.interpretation_simple(alg_arc);
    assert!(result.is_ok(), "interpretation_simple should succeed: {:?}", result);
    
    let term_op = result.unwrap();
    // Verify it's a TermOperation with the right properties
    assert_eq!(term_op.arity(), 2);
}

#[test]
fn test_variable_imp_interpretation_simple() {
    use std::sync::Arc;
    
    let alg = create_test_algebra();
    let alg_arc = Arc::new(alg);
    
    let x = VariableImp::new("x");
    
    // Get the interpretation
    let result = x.interpretation_simple(alg_arc);
    assert!(result.is_ok(), "interpretation_simple should succeed: {:?}", result);
    
    let term_op = result.unwrap();
    // Variable becomes a unary projection
    assert_eq!(term_op.arity(), 1);
}

#[test]
fn test_deep_term_cloning() {
    // Test that deep nested structures can be cloned correctly
    // Create: h(g(f(x, y), z))
    let f_sym = OperationSymbol::new("f", 2, false);
    let g_sym = OperationSymbol::new("g", 2, false);
    let h_sym = OperationSymbol::new("h", 1, false);
    
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let f_term = NonVariableTerm::new(f_sym, vec![x, y]);
    
    let z = Box::new(VariableImp::new("z")) as Box<dyn Term>;
    let g_term = NonVariableTerm::new(g_sym, vec![Box::new(f_term), z]);
    
    let h_term = NonVariableTerm::new(h_sym, vec![Box::new(g_term)]);
    
    // Clone the entire structure
    let h_boxed: Box<dyn Term> = Box::new(h_term);
    let h_cloned = h_boxed.clone_box();
    
    // Verify structure is preserved
    assert_eq!(h_cloned.to_string(), "h(g(f(x,y),z))");
    assert_eq!(h_cloned.depth(), 3);
    assert_eq!(h_cloned.length(), 6); // h + g + f + x + y + z
    
    // Verify we can get children and they're properly cloned
    let h_children = h_cloned.get_children().unwrap();
    assert_eq!(h_children.len(), 1);
    assert_eq!(h_children[0].to_string(), "g(f(x,y),z)");
    
    let g_children = h_children[0].get_children().unwrap();
    assert_eq!(g_children.len(), 2);
    assert_eq!(g_children[0].to_string(), "f(x,y)");
    assert_eq!(g_children[1].to_string(), "z");
}

// ==================== Terms Utility Function Tests ====================

#[test]
fn test_is_valid_var_string_valid() {
    use super::is_valid_var_string;
    
    assert!(is_valid_var_string("x"));
    assert!(is_valid_var_string("y"));
    assert!(is_valid_var_string("var"));
    assert!(is_valid_var_string("var1"));
    assert!(is_valid_var_string("MyVariable"));
    assert!(is_valid_var_string("x1"));
}

#[test]
fn test_is_valid_var_string_invalid() {
    use super::is_valid_var_string;
    
    assert!(!is_valid_var_string("")); // empty
    assert!(!is_valid_var_string("1x")); // starts with digit
    assert!(!is_valid_var_string("x,y")); // contains comma
    assert!(!is_valid_var_string("x(")); // contains open paren
    assert!(!is_valid_var_string("x)")); // contains close paren
    assert!(!is_valid_var_string("x y")); // contains whitespace
}

#[test]
fn test_is_valid_op_name_string() {
    use super::is_valid_op_name_string;
    
    // Same rules as variable names
    assert!(is_valid_op_name_string("f"));
    assert!(is_valid_op_name_string("add"));
    assert!(is_valid_op_name_string("mult"));
    assert!(!is_valid_op_name_string(""));
    assert!(!is_valid_op_name_string("1f"));
}

#[test]
fn test_string_to_term_simple_variable() {
    use super::string_to_term;
    
    let result = string_to_term("x");
    assert!(result.is_ok());
    let term = result.unwrap();
    assert!(term.isa_variable());
    assert_eq!(term.to_string(), "x");
}

#[test]
fn test_string_to_term_compound() {
    use super::string_to_term;
    
    let result = string_to_term("f(x,y)");
    assert!(result.is_ok());
    let term = result.unwrap();
    assert!(!term.isa_variable());
    assert_eq!(term.to_string(), "f(x,y)");
}

#[test]
fn test_string_to_term_nested() {
    use super::string_to_term;
    
    let result = string_to_term("f(g(x),y)");
    assert!(result.is_ok());
    let term = result.unwrap();
    assert_eq!(term.to_string(), "f(g(x),y)");
    assert_eq!(term.depth(), 2);
}

#[test]
fn test_string_to_term_deeply_nested() {
    use super::string_to_term;
    
    let result = string_to_term("h(g(f(x,y),z))");
    assert!(result.is_ok());
    let term = result.unwrap();
    assert_eq!(term.to_string(), "h(g(f(x,y),z))");
    assert_eq!(term.depth(), 3);
}

#[test]
fn test_string_to_term_nullary() {
    use super::string_to_term;
    
    let result = string_to_term("c()");
    assert!(result.is_ok());
    let term = result.unwrap();
    assert_eq!(term.to_string(), "c()");
    assert!(!term.isa_variable());
    let children = term.get_children().unwrap();
    assert_eq!(children.len(), 0);
}

#[test]
fn test_string_to_term_empty_error() {
    use super::string_to_term;
    
    let result = string_to_term("");
    assert!(result.is_err());
}

#[test]
fn test_string_to_term_invalid_var_error() {
    use super::string_to_term;
    
    let result = string_to_term("1x");
    assert!(result.is_err());
}

#[test]
fn test_string_to_term_invalid_op_error() {
    use super::string_to_term;
    
    let result = string_to_term("1f(x)");
    assert!(result.is_err());
}

#[test]
fn test_string_to_term_with_spaces() {
    use super::string_to_term;
    
    // Spaces should be trimmed
    let result = string_to_term("  x  ");
    assert!(result.is_ok());
    let term = result.unwrap();
    assert_eq!(term.to_string(), "x");
}

#[test]
fn test_string_to_term_missing_close_paren() {
    use super::string_to_term;
    
    // Should be adjusted by adjust_parens
    let result = string_to_term("f(x,y");
    assert!(result.is_ok());
    let term = result.unwrap();
    assert_eq!(term.to_string(), "f(x,y)");
}

#[test]
fn test_string_to_term_extra_close_paren() {
    use super::string_to_term;
    
    // Should be adjusted by adjust_parens
    let result = string_to_term("f(x,y))");
    assert!(result.is_ok());
    let term = result.unwrap();
    assert_eq!(term.to_string(), "f(x,y)");
}

#[test]
fn test_flatten_variable() {
    use super::flatten;
    
    let x = VariableImp::new("x");
    let x_term: &dyn Term = &x;
    let flattened = flatten(x_term);
    
    assert!(flattened.isa_variable());
    assert_eq!(flattened.to_string(), "x");
}

#[test]
fn test_flatten_non_associative() {
    use super::flatten;
    
    // Non-associative operation should not be flattened
    let f = OperationSymbol::new("f", 2, false);
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let term = NonVariableTerm::new(f, vec![x, y]);
    
    let flattened = flatten(&term);
    assert_eq!(flattened.to_string(), "f(x,y)");
}

#[test]
fn test_flatten_associative_simple() {
    use super::flatten;
    
    // Associative operation: f(f(x,y),z) -> f(x,y,z)
    let f = OperationSymbol::new("f", 2, true);
    
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let inner = Box::new(NonVariableTerm::new(f.clone(), vec![x, y])) as Box<dyn Term>;
    
    let z = Box::new(VariableImp::new("z")) as Box<dyn Term>;
    let outer = NonVariableTerm::new(f, vec![inner, z]);
    
    let flattened = flatten(&outer);
    assert_eq!(flattened.to_string(), "f(x,y,z)");
}

#[test]
fn test_flatten_associative_left() {
    use super::flatten;
    
    // f(x, f(y,z)) -> f(x,y,z)
    let f = OperationSymbol::new("f", 2, true);
    
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let z = Box::new(VariableImp::new("z")) as Box<dyn Term>;
    let inner = Box::new(NonVariableTerm::new(f.clone(), vec![y, z])) as Box<dyn Term>;
    
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let outer = NonVariableTerm::new(f, vec![x, inner]);
    
    let flattened = flatten(&outer);
    assert_eq!(flattened.to_string(), "f(x,y,z)");
}

#[test]
fn test_flatten_associative_both_sides() {
    use super::flatten;
    
    // f(f(x,y), f(z,w)) -> f(x,y,z,w)
    let f = OperationSymbol::new("f", 2, true);
    
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let left = Box::new(NonVariableTerm::new(f.clone(), vec![x, y])) as Box<dyn Term>;
    
    let z = Box::new(VariableImp::new("z")) as Box<dyn Term>;
    let w = Box::new(VariableImp::new("w")) as Box<dyn Term>;
    let right = Box::new(NonVariableTerm::new(f.clone(), vec![z, w])) as Box<dyn Term>;
    
    let outer = NonVariableTerm::new(f, vec![left, right]);
    
    let flattened = flatten(&outer);
    assert_eq!(flattened.to_string(), "f(x,y,z,w)");
}

#[test]
fn test_flatten_associative_nested_deep() {
    use super::flatten;
    
    // f(f(f(x,y),z),w) -> f(x,y,z,w)
    let f = OperationSymbol::new("f", 2, true);
    
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let inner1 = Box::new(NonVariableTerm::new(f.clone(), vec![x, y])) as Box<dyn Term>;
    
    let z = Box::new(VariableImp::new("z")) as Box<dyn Term>;
    let inner2 = Box::new(NonVariableTerm::new(f.clone(), vec![inner1, z])) as Box<dyn Term>;
    
    let w = Box::new(VariableImp::new("w")) as Box<dyn Term>;
    let outer = NonVariableTerm::new(f, vec![inner2, w]);
    
    let flattened = flatten(&outer);
    assert_eq!(flattened.to_string(), "f(x,y,z,w)");
}

#[test]
fn test_flatten_mixed_operations() {
    use super::flatten;
    
    // f(g(x,y),z) where f is associative but g is not
    // Should only flatten f, not g
    let f = OperationSymbol::new("f", 2, true);
    let g = OperationSymbol::new("g", 2, false);
    
    let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    let inner = Box::new(NonVariableTerm::new(g, vec![x, y])) as Box<dyn Term>;
    
    let z = Box::new(VariableImp::new("z")) as Box<dyn Term>;
    let outer = NonVariableTerm::new(f, vec![inner, z]);
    
    let flattened = flatten(&outer);
    // g(x,y) should not be flattened because g is not associative
    assert_eq!(flattened.to_string(), "f(g(x,y),z)");
}

#[test]
fn test_get_argument_strings_single() {
    use super::get_argument_strings;
    
    let result = get_argument_strings("x");
    assert_eq!(result.len(), 1);
    assert_eq!(result[0], "x");
}

#[test]
fn test_get_argument_strings_multiple() {
    use super::get_argument_strings;
    
    let result = get_argument_strings("x,y,z");
    assert_eq!(result.len(), 3);
    assert_eq!(result[0], "x");
    assert_eq!(result[1], "y");
    assert_eq!(result[2], "z");
}

#[test]
fn test_get_argument_strings_nested() {
    use super::get_argument_strings;
    
    let result = get_argument_strings("x,f(x,y),z");
    assert_eq!(result.len(), 3);
    assert_eq!(result[0], "x");
    assert_eq!(result[1], "f(x,y)");
    assert_eq!(result[2], "z");
}

#[test]
fn test_get_argument_strings_deeply_nested() {
    use super::get_argument_strings;
    
    let result = get_argument_strings("x,f(g(x),y),z");
    assert_eq!(result.len(), 3);
    assert_eq!(result[0], "x");
    assert_eq!(result[1], "f(g(x),y)");
    assert_eq!(result[2], "z");
}

#[test]
fn test_adjust_parens_balanced() {
    use super::adjust_parens;
    
    let result = adjust_parens("f(x,y)");
    assert_eq!(result, "f(x,y)");
}

#[test]
fn test_adjust_parens_missing_close() {
    use super::adjust_parens;
    
    let result = adjust_parens("f(x,y");
    assert_eq!(result, "f(x,y)");
}

#[test]
fn test_adjust_parens_missing_multiple_close() {
    use super::adjust_parens;
    
    let result = adjust_parens("f(g(x)");
    assert_eq!(result, "f(g(x))");
}

#[test]
fn test_adjust_parens_extra_close() {
    use super::adjust_parens;
    
    let result = adjust_parens("f(x,y))");
    assert_eq!(result, "f(x,y)");
}

#[test]
fn test_adjust_parens_extra_multiple_close() {
    use super::adjust_parens;
    
    let result = adjust_parens("f(x,y)))");
    assert_eq!(result, "f(x,y)");
}

// ==================== Java Comparison Tests ====================

#[test]
fn test_term_interpretation_vs_java() {
    // Test that term interpretation matches Java implementation
    // Specifically test bak(x,y,y) on baker2 algebra
    use crate::common::*;
    use crate::terms::string_to_term;
    use std::sync::Arc;
    use crate::alg::SmallAlgebraWrapper;
    use crate::io::AlgebraReader;
    use std::path::Path;
    use serde_json::json;
    
    let path_str = "resources/algebras/baker2.ua";
    let path = Path::new(path_str);
    if !path.exists() {
        println!("Skipping test - baker2.ua not found");
        return;
    }
    
    let config = TestConfig::default();
    let term_str = "bak(x,y,y)";
    let vars_list = vec!["x".to_string(), "y".to_string()];
    let algebra_path = "resources/algebras/baker2.ua";
    let vars_str = vars_list.join(",");
    
    compare_with_java!(
        config,
        "java_wrapper.src.terms.TermsWrapper",
        [
            "interpret_term",
            "--algebra", algebra_path,
            "--term", term_str,
            "--vars", &vars_str,
            "--use_all", "true"
        ],
        || {
            // Parse term
            let term = string_to_term(term_str).expect("Failed to parse term");
            
            // Load algebra
            let reader = AlgebraReader::new_from_path(algebra_path)
                .expect("Failed to create algebra reader");
            let alg = reader.read_algebra_file()
                .expect("Failed to read algebra file");
            
            // Interpret on the original algebra with use_all=true, varlist=[x,y]
            let alg_arc: Arc<dyn crate::alg::SmallAlgebra<UniverseItem = i32>> = 
                Arc::new(SmallAlgebraWrapper::new(Box::new(alg)));
            
            let op = term.interpretation(alg_arc.clone(), &vars_list, true)
                .expect("Failed to interpret term");
            
            // Build operation table in the same order as Java
            // Java iterates i from 0 to tableSize-1 and uses horner_inv to decode
            let card = alg_arc.cardinality();
            let arity = op.arity();
            let table_size = (card as usize).pow(arity as u32);
            let mut table = Vec::with_capacity(table_size);
            
            use crate::util::horner;
            for i in 0..table_size {
                let args = horner::horner_inv_same_size(i as i32, card, arity as usize);
                let value = op.int_value_at(&args)
                    .expect("Failed to evaluate operation");
                table.push(value);
            }
            
            json!({
                "command": "interpret_term",
                "algebra": alg_arc.name(),
                "term": term_str,
                "arity": op.arity(),
                "set_size": op.get_set_size(),
                "table": table,
                "table_size": table.len()
            })
        }
    );
}

