//! Tests for SingleClose parallel closure implementation

use crate::common::*;
use uacalc::alg::parallel::SingleClose;
use uacalc::util::IntArray;
use uacalc::alg::op::{OperationSymbol, operations};
use std::sync::{Arc, Mutex};
use std::sync::atomic::AtomicUsize;
use std::collections::HashMap;
use uacalc::terms::{Term, VariableImp};

#[test]
fn test_new() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.parallel.SingleCloseWrapper",
        ["new", "--min", "0", "--max", "1"],
        || {
            let op_sym = OperationSymbol::new_safe("f", 2, false).unwrap();
            let table = vec![0, 1, 1, 0]; // XOR
            let op = operations::make_int_operation(op_sym, 2, table).unwrap();
            let arc_op = Arc::from(op);
            
            let univ_list = vec![
                IntArray::from_array(vec![0]).unwrap(),
                IntArray::from_array(vec![1]).unwrap(),
            ];
            
            let map = Arc::new(Mutex::new(HashMap::new()));
            {
                let mut map_guard = map.lock().unwrap();
                map_guard.insert(univ_list[0].clone(), Box::new(VariableImp::new("x")) as Box<dyn Term>);
                map_guard.insert(univ_list[1].clone(), Box::new(VariableImp::new("y")) as Box<dyn Term>);
            }
            
            let elts_found = Arc::new(AtomicUsize::new(0));
            let sc = SingleClose::new(univ_list, map, arc_op, 0, 1, elts_found).unwrap();
            
            serde_json::json!({
                "status": "created",
                "increment": sc.get_increment(),
                "computation_size": sc.get_computation_size(),
                "too_small": sc.is_too_small()
            })
        }
    );
}

#[test]
fn test_get_increment() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.parallel.SingleCloseWrapper",
        ["get_increment"],
        || {
            let op_sym = OperationSymbol::new_safe("f", 2, false).unwrap();
            let table = vec![0, 1, 1, 0];
            let op = operations::make_int_operation(op_sym, 2, table).unwrap();
            let arc_op = Arc::from(op);
            
            let univ_list = vec![
                IntArray::from_array(vec![0]).unwrap(),
                IntArray::from_array(vec![1]).unwrap(),
            ];
            
            let map = Arc::new(Mutex::new(HashMap::new()));
            let elts_found = Arc::new(AtomicUsize::new(0));
            let sc = SingleClose::new(univ_list, map, arc_op, 0, 1, elts_found).unwrap();
            
            serde_json::json!({
                "increment": sc.get_increment()
            })
        }
    );
}

#[test]
fn test_get_computation_size() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.parallel.SingleCloseWrapper",
        ["get_computation_size"],
        || {
            let op_sym = OperationSymbol::new_safe("f", 2, false).unwrap();
            let table = vec![0, 1, 1, 0];
            let op = operations::make_int_operation(op_sym, 2, table).unwrap();
            let arc_op = Arc::from(op);
            
            let univ_list = vec![
                IntArray::from_array(vec![0]).unwrap(),
                IntArray::from_array(vec![1]).unwrap(),
            ];
            
            let map = Arc::new(Mutex::new(HashMap::new()));
            let elts_found = Arc::new(AtomicUsize::new(0));
            let sc = SingleClose::new(univ_list, map, arc_op, 0, 1, elts_found).unwrap();
            
            serde_json::json!({
                "computation_size": sc.get_computation_size()
            })
        }
    );
}

#[test]
fn test_is_too_small() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.parallel.SingleCloseWrapper",
        ["is_too_small"],
        || {
            let op_sym = OperationSymbol::new_safe("f", 2, false).unwrap();
            let table = vec![0, 1, 1, 0];
            let op = operations::make_int_operation(op_sym, 2, table).unwrap();
            let arc_op = Arc::from(op);
            
            let univ_list = vec![
                IntArray::from_array(vec![0]).unwrap(),
                IntArray::from_array(vec![1]).unwrap(),
            ];
            
            let map = Arc::new(Mutex::new(HashMap::new()));
            let elts_found = Arc::new(AtomicUsize::new(0));
            let sc = SingleClose::new(univ_list, map, arc_op, 0, 1, elts_found).unwrap();
            
            serde_json::json!({
                "too_small": sc.is_too_small()
            })
        }
    );
}

#[test]
fn test_compute_size() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.parallel.SingleCloseWrapper",
        ["compute_size", "--min", "0", "--max", "1"],
        || {
            let op_sym = OperationSymbol::new_safe("f", 2, false).unwrap();
            let table = vec![0, 1, 1, 0];
            let op = operations::make_int_operation(op_sym, 2, table).unwrap();
            let arc_op = Arc::from(op);
            
            let univ_list = vec![
                IntArray::from_array(vec![0]).unwrap(),
                IntArray::from_array(vec![1]).unwrap(),
            ];
            
            let map = Arc::new(Mutex::new(HashMap::new()));
            let elts_found = Arc::new(AtomicUsize::new(0));
            let sc = SingleClose::new(univ_list, map, arc_op, 0, 1, elts_found).unwrap();
            
            serde_json::json!({
                "computation_size": sc.get_computation_size()
            })
        }
    );
}

#[test]
fn test_test() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.parallel.SingleCloseWrapper",
        ["test"],
        || {
            let op_sym = OperationSymbol::new_safe("f", 2, false).unwrap();
            let table = vec![0, 1, 1, 0];
            let op = operations::make_int_operation(op_sym, 2, table).unwrap();
            let arc_op = Arc::from(op);
            
            let univ_list = vec![
                IntArray::from_array(vec![0]).unwrap(),
                IntArray::from_array(vec![1]).unwrap(),
            ];
            
            let map = Arc::new(Mutex::new(HashMap::new()));
            {
                let mut map_guard = map.lock().unwrap();
                map_guard.insert(univ_list[0].clone(), Box::new(VariableImp::new("x")) as Box<dyn Term>);
                map_guard.insert(univ_list[1].clone(), Box::new(VariableImp::new("y")) as Box<dyn Term>);
            }
            
            let elts_found = Arc::new(AtomicUsize::new(0));
            let sc = SingleClose::new(univ_list, map, arc_op, 0, 1, elts_found).unwrap();
            
            serde_json::json!({
                "status": "test_passed",
                "increment": sc.get_increment(),
                "computation_size": sc.get_computation_size(),
                "too_small": sc.is_too_small()
            })
        }
    );
}


