//! Tests for UACalc operations

use uacalc_rust::alg::op::*;

#[test]
fn test_operation_symbol_creation() {
    let symbol = OperationSymbol::new("test".to_string(), 2);
    assert_eq!(symbol.name, "test");
    assert_eq!(symbol.arity, 2);
    assert!(!symbol.associative);
}

#[test]
fn test_operation_symbol_predefined() {
    let join = OperationSymbol::join();
    assert_eq!(join.name, "join");
    assert_eq!(join.arity, 2);
    
    let meet = OperationSymbol::meet();
    assert_eq!(meet.name, "meet");
    assert_eq!(meet.arity, 2);
}

#[test]
fn test_operation_symbol_comparison() {
    let sym1 = OperationSymbol::new("a".to_string(), 3);
    let sym2 = OperationSymbol::new("b".to_string(), 2);
    let sym3 = OperationSymbol::new("a".to_string(), 3);
    
    assert!(sym1 < sym2); // Higher arity comes first
    assert_eq!(sym1, sym3);
}

#[test]
fn test_int_operation_identity() {
    let op = IntOperation::identity(3).unwrap();
    
    assert_eq!(op.arity(), 1);
    assert_eq!(op.get_set_size(), 3);
    assert!(op.is_table_based());
    
    // Test identity property: f(x) = x
    assert_eq!(op.int_value_at(&[0]).unwrap(), 0);
    assert_eq!(op.int_value_at(&[1]).unwrap(), 1);
    assert_eq!(op.int_value_at(&[2]).unwrap(), 2);
}

#[test]
fn test_int_operation_constant() {
    let op = IntOperation::constant(2, 3, 1).unwrap();
    
    assert_eq!(op.arity(), 2);
    assert_eq!(op.get_set_size(), 3);
    
    // Test constant property: f(x,y) = 1 for all x,y
    for x in 0..3 {
        for y in 0..3 {
            assert_eq!(op.int_value_at(&[x, y]).unwrap(), 1);
        }
    }
}

#[test]
fn test_int_operation_properties() {
    // Create identity operation
    let identity = IntOperation::identity(3).unwrap();
    assert!(identity.is_idempotent().unwrap());
    assert!(identity.is_total().unwrap());
    
    // Create constant operation - only constant 0 on single element set is idempotent
    let constant = IntOperation::constant(2, 1, 0).unwrap();
    assert!(constant.is_idempotent().unwrap()); // f(0,0) = 0 = 0 ✓
    assert!(constant.is_total().unwrap());
    assert!(constant.is_commutative().unwrap()); // Constant operations are commutative
    
    // Test non-idempotent constant
    let non_idem_constant = IntOperation::constant(2, 3, 1).unwrap();
    assert!(!non_idem_constant.is_idempotent().unwrap()); // f(0,0) = 1 ≠ 0
}

#[test]
fn test_operation_table_access() {
    let op = IntOperation::identity(2).unwrap();
    
    // Test table access
    let table = op.get_table().unwrap();
    assert_eq!(table, &[0, 1]); // Identity table for set size 2
    
    // Test Horner encoding access
    assert_eq!(op.int_value_at_horner(0).unwrap(), 0);
    assert_eq!(op.int_value_at_horner(1).unwrap(), 1);
}

#[test]
fn test_abstract_operation_basics() {
    let abs_op = AbstractOperation::new("test".to_string(), 2, 3);
    
    assert_eq!(abs_op.arity(), 2);
    assert_eq!(abs_op.get_set_size(), 3);
    assert_eq!(abs_op.symbol().name, "test");
    assert!(!abs_op.is_table_based());
    
    // Abstract operation doesn't implement evaluation, so it should error
    assert!(abs_op.int_value_at(&[0, 1]).is_err());
}

#[test]
fn test_maltsev_operation() {
    // Create a ternary operation table for a Maltsev operation
    // f(x,y,z) should satisfy f(x,y,y) = x and f(x,x,y) = y
    let mut table = vec![0i32; 27]; // 3^3 = 27 entries
    
    for x in 0i32..3 {
        for y in 0i32..3 {
            for z in 0i32..3 {
                let index = (x * 9 + y * 3 + z) as usize;
                if y == z {
                    table[index] = x; // f(x,y,y) = x
                } else if x == y {
                    table[index] = z; // f(x,x,z) = z
                } else {
                    // For other cases, we can define arbitrarily, let's use majority
                    if x == y { table[index] = x; }
                    else if x == z { table[index] = x; }
                    else if y == z { table[index] = y; }
                    else { table[index] = 0; } // Default case
                }
            }
        }
    }
    
    let maltsev_op = IntOperation::new("maltsev".to_string(), 3, 3, table).unwrap();
    assert!(maltsev_op.is_maltsev().unwrap());
}