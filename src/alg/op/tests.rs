//! Tests for Operation trait and implementations

#[cfg(test)]
mod tests {
    use crate::alg::op::{OperationSymbol, AbstractOperation, IntOperation, Operation};
    use crate::error::UaCalcError;

    #[test]
    fn test_operation_symbol_creation() {
        let symbol = OperationSymbol::new("add".to_string(), 2).unwrap();
        assert_eq!(symbol.name(), "add");
        assert_eq!(symbol.arity(), 2);
        assert!(!symbol.is_associative());
    }

    #[test]
    fn test_operation_symbol_associative() {
        let symbol = OperationSymbol::new_with_associative("mult".to_string(), 2, true).unwrap();
        assert!(symbol.is_associative());
        
        // Setting non-binary operation as associative should fail
        let result = OperationSymbol::new_with_associative("triple".to_string(), 3, true);
        assert!(result.is_err());
    }

    #[test]
    fn test_operation_symbol_ordering() {
        let op1 = OperationSymbol::new("a".to_string(), 3).unwrap();
        let op2 = OperationSymbol::new("b".to_string(), 2).unwrap();
        let op3 = OperationSymbol::new("c".to_string(), 3).unwrap();
        
        // According to Java: "This puts high arity operations first"
        // So op1 (arity 3) should be less than op2 (arity 2) in comparison order
        assert!(op1 < op2);
        // Same arity, compare by name: "a" < "c"
        assert!(op1 < op3);
    }

    #[test]
    fn test_operation_symbol_uniform_generation() {
        let op1 = OperationSymbol::get_operation_symbol(2).unwrap();
        let op2 = OperationSymbol::get_operation_symbol(2).unwrap();
        
        assert_eq!(op1.arity(), 2);
        assert_eq!(op2.arity(), 2);
        assert!(op1.name().starts_with("b_"));
        assert!(op2.name().starts_with("b_"));
        assert_ne!(op1.name(), op2.name()); // Should have different indices
    }

    #[test]
    fn test_abstract_operation_creation() {
        let op = AbstractOperation::new("test".to_string(), 2, 3).unwrap();
        assert_eq!(op.arity(), 2);
        assert_eq!(op.get_set_size(), 3);
        assert_eq!(op.symbol().name(), "test");
        assert!(!op.is_table_based());
    }

    #[test]
    fn test_abstract_operation_invalid_size() {
        let result = AbstractOperation::new("test".to_string(), 2, 0);
        assert!(matches!(result, Err(UaCalcError::InvalidSetSize(0))));
    }

    #[test]
    fn test_horner_encoding() {
        let op = AbstractOperation::new("test".to_string(), 2, 3).unwrap();
        
        // Test encoding [0, 0] = 0
        assert_eq!(op.horner_encode(&[0, 0]).unwrap(), 0);
        // Test encoding [0, 1] = 1
        assert_eq!(op.horner_encode(&[0, 1]).unwrap(), 1);
        // Test encoding [1, 0] = 3
        assert_eq!(op.horner_encode(&[1, 0]).unwrap(), 3);
        // Test encoding [2, 2] = 8
        assert_eq!(op.horner_encode(&[2, 2]).unwrap(), 8);
    }

    #[test]
    fn test_horner_decoding() {
        let op = AbstractOperation::new("test".to_string(), 2, 3).unwrap();
        
        assert_eq!(op.horner_decode(0).unwrap(), vec![0, 0]);
        assert_eq!(op.horner_decode(1).unwrap(), vec![0, 1]);
        assert_eq!(op.horner_decode(3).unwrap(), vec![1, 0]);
        assert_eq!(op.horner_decode(8).unwrap(), vec![2, 2]);
    }

    #[test]
    fn test_int_operation_creation() {
        // Create a simple addition operation on {0, 1, 2}
        let table = vec![
            0, 1, 2,  // 0 + {0,1,2} = {0,1,2}
            1, 2, 0,  // 1 + {0,1,2} = {1,2,0}
            2, 0, 1,  // 2 + {0,1,2} = {2,0,1}
        ];
        
        let symbol = OperationSymbol::new("add_mod3".to_string(), 2).unwrap();
        let op = IntOperation::new(symbol, table, 3).unwrap();
        
        assert_eq!(op.arity(), 2);
        assert_eq!(op.get_set_size(), 3);
        assert!(op.is_table_based());
    }

    #[test]
    fn test_int_operation_evaluation() {
        // Create a simple addition operation on {0, 1, 2}
        let table = vec![
            0, 1, 2,  // 0 + {0,1,2} = {0,1,2}
            1, 2, 0,  // 1 + {0,1,2} = {1,2,0}
            2, 0, 1,  // 2 + {0,1,2} = {2,0,1}
        ];
        
        let symbol = OperationSymbol::new("add_mod3".to_string(), 2).unwrap();
        let op = IntOperation::new(symbol, table, 3).unwrap();
        
        // Test some operations
        assert_eq!(op.int_value_at(&[0, 0]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[0, 1]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1, 0]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1, 2]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[2, 1]).unwrap(), 0);
    }

    #[test]
    fn test_int_operation_horner_access() {
        // Create a simple binary operation
        let table = vec![0, 1, 1, 0]; // XOR on {0, 1}
        
        let symbol = OperationSymbol::new("xor".to_string(), 2).unwrap();
        let op = IntOperation::new(symbol, table, 2).unwrap();
        
        // Test Horner encoded access
        assert_eq!(op.int_value_at_horner(0).unwrap(), 0); // [0,0] -> 0
        assert_eq!(op.int_value_at_horner(1).unwrap(), 1); // [0,1] -> 1
        assert_eq!(op.int_value_at_horner(2).unwrap(), 1); // [1,0] -> 1
        assert_eq!(op.int_value_at_horner(3).unwrap(), 0); // [1,1] -> 0
    }

    #[test]
    fn test_operation_properties() {
        // Create an idempotent operation (max on {0, 1, 2})
        let max_table = vec![
            0, 1, 2,  // max(0, {0,1,2}) = {0,1,2}
            1, 1, 2,  // max(1, {0,1,2}) = {1,1,2}
            2, 2, 2,  // max(2, {0,1,2}) = {2,2,2}
        ];
        
        let symbol = OperationSymbol::new("max".to_string(), 2).unwrap();
        let max_op = IntOperation::new(symbol, max_table, 3).unwrap();
        
        assert!(max_op.is_idempotent().unwrap());
        assert!(max_op.is_commutative().unwrap());
        assert!(max_op.is_associative().unwrap());
        assert!(max_op.is_totally_symmetric().unwrap());
        assert!(max_op.is_total().unwrap());
    }

    #[test]
    fn test_maltsev_operation() {
        // Create a proper ternary Maltsev operation on {0, 1}
        // A Maltsev operation satisfies: f(x,y,y) = x and f(x,x,y) = y
        let maltsev_table = vec![
            // Args in order: (0,0,0) (0,0,1) (0,1,0) (0,1,1) (1,0,0) (1,0,1) (1,1,0) (1,1,1)
            // f(0,0,0)=0, f(0,0,1)=1, f(0,1,0)=0, f(0,1,1)=0, f(1,0,0)=1, f(1,0,1)=1, f(1,1,0)=0, f(1,1,1)=1
            0, 1, 0, 0, 1, 1, 0, 1
        ];
        
        let symbol = OperationSymbol::new("maltsev".to_string(), 3).unwrap();
        let maltsev_op = IntOperation::new(symbol, maltsev_table, 2).unwrap();
        
        // Verify manually that this satisfies Maltsev conditions:
        // f(0,0,0) = 0 ✓, f(0,1,1) = 0 ✓, f(1,0,0) = 1 ✓, f(1,1,1) = 1 ✓ 
        // f(0,0,1) = 1 ✓, f(1,1,0) = 0 ✓
        assert!(maltsev_op.is_maltsev().unwrap());
    }

    #[test]
    fn test_create_binary_operation_helper() {
        // Create addition modulo 3
        let add_mod3 = IntOperation::create_binary_operation(
            "add_mod3".to_string(),
            3,
            |a, b| (a + b) % 3
        ).unwrap();
        
        assert_eq!(add_mod3.int_value_at(&[1, 2]).unwrap(), 0);
        assert_eq!(add_mod3.int_value_at(&[2, 2]).unwrap(), 1);
    }

    #[test]
    fn test_create_unary_operation_helper() {
        // Create negation modulo 3
        let neg_mod3 = IntOperation::create_unary_operation(
            "neg_mod3".to_string(),
            3,
            |a| (3 - a) % 3
        ).unwrap();
        
        assert_eq!(neg_mod3.int_value_at(&[0]).unwrap(), 0);
        assert_eq!(neg_mod3.int_value_at(&[1]).unwrap(), 2);
        assert_eq!(neg_mod3.int_value_at(&[2]).unwrap(), 1);
    }

    #[test]
    fn test_invalid_table_size() {
        let symbol = OperationSymbol::new("test".to_string(), 2).unwrap();
        
        // Wrong table size
        let result = IntOperation::new(symbol, vec![0, 1, 2], 2);
        assert!(result.is_err());
    }

    #[test]
    fn test_invalid_table_values() {
        let symbol = OperationSymbol::new("test".to_string(), 2).unwrap();
        
        // Table values out of range
        let result = IntOperation::new(symbol, vec![0, 1, 2, 3], 2);
        assert!(result.is_err());
    }
}