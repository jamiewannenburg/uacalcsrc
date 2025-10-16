use super::*;
use std::collections::HashMap;

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

#[test]
fn test_variable_imp_eval() {
    let x = VariableImp::new("x");
    let mut map = HashMap::new();
    map.insert("x".to_string(), 5);
    
    let result = x.eval(&map);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 5);
}

#[test]
fn test_variable_imp_eval_missing() {
    let x = VariableImp::new("x");
    let map = HashMap::new();
    
    let result = x.eval(&map);
    assert!(result.is_err());
}

#[test]
fn test_variable_imp_int_eval() {
    let x = VariableImp::new("x");
    let mut map = HashMap::new();
    map.insert("x".to_string(), 3);
    
    let result = x.int_eval(&map);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 3);
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
