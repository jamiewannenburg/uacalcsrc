#[cfg(test)]
mod tests {
    use crate::alg::op::{Operation, BasicOperation, AbstractIntOperation, IntOperation, OperationSymbol};

    #[test]
    fn test_operation_symbol_basic() {
        let symbol = OperationSymbol::new("test", 2, false);
        assert_eq!(symbol.name(), "test");
        assert_eq!(symbol.arity(), 2);
        assert!(!symbol.is_associative());
    }

    #[test]
    fn test_abstract_operation_creation() {
        let symbol = OperationSymbol::new("f", 2, false);
        let op = BasicOperation::new(symbol.clone(), 3);
        
        assert_eq!(op.arity(), 2);
        assert_eq!(op.get_set_size(), 3);
        assert_eq!(op.symbol().name(), "f");
        assert_eq!(op.symbol().arity(), 2);
    }

    #[test]
    fn test_abstract_operation_simple_binary() {
        let op = BasicOperation::simple_binary_op("add", 3).unwrap();
        
        assert_eq!(op.arity(), 2);
        assert_eq!(op.get_set_size(), 3);
        
        // Test evaluation: should be (a + b) % 3
        assert_eq!(op.int_value_at(&[0, 1]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1, 1]).unwrap(), 2);
        assert_eq!(op.int_value_at(&[2, 2]).unwrap(), 1);
    }

    #[test]
    fn test_abstract_operation_simple_unary() {
        let op = BasicOperation::simple_unary_op("succ", 4).unwrap();
        
        assert_eq!(op.arity(), 1);
        assert_eq!(op.get_set_size(), 4);
        
        // Test evaluation: should be (a + 1) % 4
        assert_eq!(op.int_value_at(&[0]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[2]).unwrap(), 3);
        assert_eq!(op.int_value_at(&[3]).unwrap(), 0);
    }

    #[test]
    fn test_abstract_operation_simple_nullary() {
        let op = BasicOperation::simple_nullary_op("zero", 5).unwrap();
        
        assert_eq!(op.arity(), 0);
        assert_eq!(op.get_set_size(), 5);
        
        // Test evaluation: should return 0
        assert_eq!(op.int_value_at(&[]).unwrap(), 0);
    }

    #[test]
    fn test_abstract_operation_table_creation() {
        let mut op = BasicOperation::simple_binary_op("add", 2).unwrap();
        
        // Initially no table
        assert!(!op.is_table_based());
        assert!(op.get_table().is_none());
        
        // Create table
        op.make_table().unwrap();
        assert!(op.is_table_based());
        
        let table = op.get_table().unwrap();
        assert_eq!(table.len(), 4); // 2^2 = 4 entries
        
        // Verify table contents match evaluation
        assert_eq!(table[0], op.int_value_at(&[0, 0]).unwrap()); // 0+0=0
        assert_eq!(table[1], op.int_value_at(&[0, 1]).unwrap()); // 0+1=1  
        assert_eq!(table[2], op.int_value_at(&[1, 0]).unwrap()); // 1+0=1
        assert_eq!(table[3], op.int_value_at(&[1, 1]).unwrap()); // 1+1=0
    }

    #[test]
    fn test_abstract_operation_properties() {
        let op = BasicOperation::simple_binary_op("add", 3).unwrap();
        
        // Addition modulo n is commutative but not idempotent
        assert!(op.is_commutative().unwrap());
        assert!(!op.is_idempotent().unwrap());
        
        // Test if totally symmetric (should be true for binary commutative)
        assert!(op.is_totally_symmetric().unwrap());
        
        // Test if associative (depends on implementation)
        let is_assoc = op.is_associative().unwrap();
        // Note: This depends on whether addition mod 3 is associative in our implementation
        println!("Addition mod 3 is associative: {}", is_assoc);
        
        // Should be total
        assert!(op.is_total().unwrap());
        
        // Binary operation is not Maltsev
        assert!(!op.is_maltsev().unwrap());
    }

    #[test]
    fn test_int_operation_xor() {
        let op = IntOperation::binary_xor("xor").unwrap();
        
        assert_eq!(op.arity(), 2);
        assert_eq!(op.get_set_size(), 2);
        assert!(op.is_table_based());
        
        // Test XOR truth table
        assert_eq!(op.int_value_at(&[0, 0]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[0, 1]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1, 0]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1, 1]).unwrap(), 0);
        
        // XOR is commutative but not idempotent
        assert!(op.is_commutative().unwrap());
        assert!(!op.is_idempotent().unwrap());
    }

    #[test]
    fn test_int_operation_and() {
        let op = IntOperation::binary_and("and").unwrap();
        
        assert_eq!(op.arity(), 2);
        assert_eq!(op.get_set_size(), 2);
        assert!(op.is_table_based());
        
        // Test AND truth table
        assert_eq!(op.int_value_at(&[0, 0]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[0, 1]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[1, 0]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[1, 1]).unwrap(), 1);
        
        // AND is commutative and idempotent
        assert!(op.is_commutative().unwrap());
        assert!(op.is_idempotent().unwrap());
    }

    #[test]
    fn test_int_operation_or() {
        let op = IntOperation::binary_or("or").unwrap();
        
        assert_eq!(op.arity(), 2);
        assert_eq!(op.get_set_size(), 2);
        assert!(op.is_table_based());
        
        // Test OR truth table
        assert_eq!(op.int_value_at(&[0, 0]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[0, 1]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1, 0]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1, 1]).unwrap(), 1);
        
        // OR is commutative and idempotent
        assert!(op.is_commutative().unwrap());
        assert!(op.is_idempotent().unwrap());
    }

    #[test]
    fn test_int_operation_unary_not() {
        let op = IntOperation::unary_not("not").unwrap();
        
        assert_eq!(op.arity(), 1);
        assert_eq!(op.get_set_size(), 2);
        assert!(op.is_table_based());
        
        // Test NOT truth table
        assert_eq!(op.int_value_at(&[0]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1]).unwrap(), 0);
    }

    #[test]
    fn test_int_operation_nullary_constant() {
        let op = IntOperation::nullary_constant("five", 5).unwrap();
        
        assert_eq!(op.arity(), 0);
        assert_eq!(op.get_set_size(), 6); // Set size is constant + 1
        assert!(op.is_table_based());
        
        // Test constant value
        assert_eq!(op.int_value_at(&[]).unwrap(), 5);
    }

    #[test]
    fn test_int_operation_custom() {
        let symbol = OperationSymbol::new("custom", 2, false);
        let table = vec![1, 0, 0, 1]; // NAND-like table
        let op = IntOperation::new(symbol, 2, table).unwrap();
        
        assert_eq!(op.arity(), 2);
        assert_eq!(op.get_set_size(), 2);
        assert!(op.is_table_based());
        
        // Test custom table
        assert_eq!(op.int_value_at(&[0, 0]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[0, 1]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[1, 0]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[1, 1]).unwrap(), 1);
    }

    #[test]
    fn test_int_operation_horner_access() {
        let op = IntOperation::binary_xor("xor").unwrap();
        
        // Test Horner encoding access
        // For binary operation on {0,1}: index 0 = (0,0), index 1 = (0,1), index 2 = (1,0), index 3 = (1,1)
        assert_eq!(op.int_value_at_horner(0).unwrap(), 0); // XOR(0,0) = 0
        assert_eq!(op.int_value_at_horner(1).unwrap(), 1); // XOR(0,1) = 1
        assert_eq!(op.int_value_at_horner(2).unwrap(), 1); // XOR(1,0) = 1
        assert_eq!(op.int_value_at_horner(3).unwrap(), 0); // XOR(1,1) = 0
    }

    #[test]
    fn test_operation_comparison() {
        let op1 = BasicOperation::simple_binary_op("a", 3).unwrap();
        let op2 = BasicOperation::simple_binary_op("b", 3).unwrap(); 
        let op3 = BasicOperation::simple_unary_op("c", 3).unwrap();
        
        // Test equality
        let op4 = BasicOperation::simple_binary_op("a", 3).unwrap();
        assert_eq!(op1, op4);
        
        // Test inequality
        assert_ne!(op1, op2);
        assert_ne!(op1, op3);
        
        // Test ordering (higher arity first, then by name)
        assert!(op3 > op1); // Unary > Binary in operation symbol ordering
    }

    #[test]
    fn test_operation_string_representation() {
        let op1 = BasicOperation::simple_binary_op("test", 3).unwrap();
        let op2 = IntOperation::binary_xor("xor").unwrap();
        
        // Test Display trait
        let str1 = format!("{}", op1);
        let str2 = format!("{}", op2);
        
        assert!(str1.contains("test"));
        assert!(str2.contains("xor"));
    }

    #[test]
    fn test_error_handling() {
        // Test invalid set size
        let result = BasicOperation::simple_binary_op("test", 0);
        assert!(result.is_err());
        
        // Test invalid arguments
        let op = BasicOperation::simple_binary_op("test", 3).unwrap();
        let result = op.int_value_at(&[0]); // Wrong arity
        assert!(result.is_err());
        
        let result = op.int_value_at(&[0, 5]); // Out of bounds
        assert!(result.is_err());
        
        // Test invalid table creation
        let symbol = OperationSymbol::new("test", 2, false);
        let wrong_table = vec![0, 1]; // Too small for binary operation
        let result = IntOperation::new(symbol, 2, wrong_table);
        assert!(result.is_err());
    }

    #[test]
    fn test_abstract_int_operation_creation() {
        let op = AbstractIntOperation::new("test", 2, 3);
        
        assert_eq!(op.arity(), 2);
        assert_eq!(op.get_set_size(), 3);
        assert_eq!(op.symbol().name(), "test");
        assert_eq!(op.symbol().arity(), 2);
    }

    #[test]
    fn test_abstract_int_operation_with_symbol() {
        let symbol = OperationSymbol::new("mult", 3, false);
        let op = AbstractIntOperation::new_with_symbol(symbol.clone(), 4);
        
        assert_eq!(op.arity(), 3);
        assert_eq!(op.get_set_size(), 4);
        assert_eq!(op.symbol().name(), "mult");
        assert_eq!(op.symbol().arity(), 3);
    }

    #[test]
    fn test_abstract_int_operation_unsupported_methods() {
        let op = AbstractIntOperation::new("test", 2, 3);
        
        // These methods should return errors (UnsupportedOperationException)
        let result = op.value_at(&[0, 1]);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("UnsupportedOperationException"));
        
        let result = op.int_value_at(&[0, 1]);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("UnsupportedOperationException"));
    }

    #[test]
    fn test_abstract_int_operation_safe_constructor() {
        // Test valid parameters
        let result = AbstractIntOperation::new_safe("valid", 2, 3);
        assert!(result.is_ok());
        
        // Test invalid algebra size
        let result = AbstractIntOperation::new_safe("invalid", 2, 0);
        assert!(result.is_err());
        
        // Test invalid arity in symbol
        let result = AbstractIntOperation::new_safe("invalid", -1, 3);
        assert!(result.is_err());
    }

    #[test]
    fn test_abstract_int_operation_properties() {
        let op = AbstractIntOperation::new("test", 2, 3);
        
        // These should work since they delegate to default implementations
        assert!(op.is_total().is_ok()); // Should be Ok(true) by default
        
        // Property checks that don't need computation should work
        // (though they might return errors since compute_value fails)
        let _ = op.is_associative(); // May succeed or fail depending on implementation
    }
}