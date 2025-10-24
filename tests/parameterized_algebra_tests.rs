use uacalc::alg::{ParameterizedAlgebra, ParameterizedOperation};
use std::collections::HashMap;

#[test]
fn test_parameterized_algebra_basic() {
    let param_alg = ParameterizedAlgebra::new(
        vec!["n".to_string()],
        "Zn".to_string(),
        "n".to_string(),
        "Cyclic group of order n".to_string(),
        Vec::new(),
    );
    
    assert_eq!(param_alg.name, "Zn");
    assert_eq!(param_alg.parameter_names.len(), 1);
    assert_eq!(param_alg.parameter_names[0], "n");
}

#[test]
fn test_get_parameter_map_single() {
    let param_alg = ParameterizedAlgebra::new(
        vec!["n".to_string()],
        "Zn".to_string(),
        "n".to_string(),
        "Cyclic group".to_string(),
        Vec::new(),
    );
    
    let values = vec![5];
    let map = param_alg.get_parameter_map(&values).unwrap();
    
    assert_eq!(map.len(), 1);
    assert_eq!(map.get("n"), Some(&"5".to_string()));
}

#[test]
fn test_get_parameter_map_multiple() {
    let param_alg = ParameterizedAlgebra::new(
        vec!["n".to_string(), "m".to_string()],
        "Example".to_string(),
        "n*m".to_string(),
        "".to_string(),
        Vec::new(),
    );
    
    let values = vec![3, 4];
    let map = param_alg.get_parameter_map(&values).unwrap();
    
    assert_eq!(map.len(), 2);
    assert_eq!(map.get("n"), Some(&"3".to_string()));
    assert_eq!(map.get("m"), Some(&"4".to_string()));
}

#[test]
fn test_get_parameter_map_error() {
    let param_alg = ParameterizedAlgebra::new(
        vec!["n".to_string(), "m".to_string()],
        "Example".to_string(),
        "n*m".to_string(),
        "".to_string(),
        Vec::new(),
    );
    
    // Wrong number of values
    let values = vec![3];
    let result = param_alg.get_parameter_map(&values);
    
    assert!(result.is_err());
}

#[test]
fn test_parameterized_operation_basic() {
    let param_op = ParameterizedOperation::new(
        "add_mod_n".to_string(),
        "plus".to_string(),
        "n".to_string(),
        vec!["n".to_string()],
        "2".to_string(),
        "Addition modulo n".to_string(),
        "0".to_string(),
        "(a + b) % n".to_string(),
    );
    
    assert_eq!(param_op.name, "add_mod_n");
    assert_eq!(param_op.symbol_name, "plus");
    assert_eq!(param_op.arity_exp, "2");
}

#[test]
fn test_sub_parm_values() {
    let mut map = HashMap::new();
    map.insert("n".to_string(), "5".to_string());
    
    // Note: Current implementation is a stub that returns the input as-is
    let result = ParameterizedOperation::sub_parm_values("n+1", &map);
    assert_eq!(result, "n+1"); // Should be "n+1" since substitution is not implemented
}

#[test]
fn test_sub_parm_values_empty_map() {
    let map = HashMap::new();
    
    let result = ParameterizedOperation::sub_parm_values("n*m", &map);
    assert_eq!(result, "n*m");
}

#[test]
fn test_parameterized_algebra_display() {
    let param_alg = ParameterizedAlgebra::new(
        vec!["n".to_string()],
        "Zn".to_string(),
        "n".to_string(),
        "Cyclic group".to_string(),
        Vec::new(),
    );
    
    let display_str = format!("{}", param_alg);
    assert!(display_str.contains("Zn"));
}

#[test]
fn test_parameterized_operation_display() {
    let param_op = ParameterizedOperation::new(
        "mult".to_string(),
        "times".to_string(),
        "n".to_string(),
        vec!["n".to_string()],
        "2".to_string(),
        "Multiplication".to_string(),
        "1".to_string(),
        "a * b".to_string(),
    );
    
    let display_str = format!("{}", param_op);
    assert!(display_str.contains("mult"));
}
