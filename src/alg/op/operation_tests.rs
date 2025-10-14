#[cfg(test)]
mod tests {
    use crate::alg::op::{Operation, AbstractOperation, IntOperation, OperationSymbol};
    use crate::common::{TestConfig, compare_with_java, run_java_cli_with_timeout, compare_outputs};
    use serde_json::json;

    #[test]
    fn test_abstract_operation_creation() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "binary", "--setSize", "3"],
            || {
                let symbol = OperationSymbol::new("testBin", 2, false);
                let op = AbstractOperation::new(symbol, 3);
                json!({
                    "arity": op.arity(),
                    "type": "binary",
                    "setSize": op.get_set_size()
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_unary() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "unary", "--setSize", "4"],
            || {
                let op = AbstractOperation::simple_unary_op("testUn", 4).unwrap();
                json!({
                    "arity": op.arity(),
                    "type": "unary",
                    "setSize": op.get_set_size()
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_nullary() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "nullary", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_nullary_op("testNull", 3).unwrap();
                json!({
                    "arity": op.arity(),
                    "type": "nullary", 
                    "setSize": op.get_set_size()
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_value_at() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["intValueAt", "--type", "binary", "--args", "0,1", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_binary_op("testBin", 3).unwrap();
                let result = op.int_value_at(&[0, 1]).unwrap();
                json!({
                    "result": result,
                    "args": "[0, 1]",
                    "type": "binary"
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_unary_value() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["intValueAt", "--type", "unary", "--args", "2", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_unary_op("testUn", 3).unwrap();
                let result = op.int_value_at(&[2]).unwrap();
                json!({
                    "result": result,
                    "args": "[2]",
                    "type": "unary"
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_nullary_value() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["intValueAt", "--type", "nullary", "--args", "", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_nullary_op("testNull", 3).unwrap();
                let result = op.int_value_at(&[]).unwrap();
                json!({
                    "result": result,
                    "args": "[]",
                    "type": "nullary"
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_table_operations() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["makeTable", "--type", "binary", "--setSize", "2"],
            || {
                let mut op = AbstractOperation::simple_binary_op("testBin", 2).unwrap();
                op.make_table().unwrap();
                json!({
                    "status": "table_created",
                    "type": "binary",
                    "isTableBased": op.is_table_based()
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_get_table() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["getTable", "--type", "binary", "--setSize", "2"],
            || {
                let mut op = AbstractOperation::simple_binary_op("testBin", 2).unwrap();
                op.make_table().unwrap();
                let table = op.get_table().map(|slice| slice.to_vec());
                json!({
                    "table": table,
                    "hasTable": table.is_some(),
                    "type": "binary"
                })
            }
        );
    }
    
    #[test] 
    fn test_abstract_operation_is_table_based() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isTableBased", "--type", "binary", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_binary_op("testBin", 3).unwrap();
                json!({
                    "isTableBased": op.is_table_based(),
                    "type": "binary"
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_properties() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isIdempotent", "--type", "binary", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_binary_op("testBin", 3).unwrap();
                json!({
                    "isIdempotent": op.is_idempotent().unwrap(),
                    "type": "binary"
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_is_associative() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isAssociative", "--type", "binary", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_binary_op("testBin", 3).unwrap();
                json!({
                    "isAssociative": op.is_associative().unwrap(),
                    "type": "binary"
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_is_commutative() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isCommutative", "--type", "binary", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_binary_op("testBin", 3).unwrap();
                json!({
                    "isCommutative": op.is_commutative().unwrap(),
                    "type": "binary"
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_is_totally_symmetric() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isTotallySymmetric", "--type", "binary", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_binary_op("testBin", 3).unwrap();
                json!({
                    "isTotallySymmetric": op.is_totally_symmetric().unwrap(),
                    "type": "binary"
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_is_maltsev() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isMaltsev", "--type", "binary", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_binary_op("testBin", 3).unwrap();
                json!({
                    "isMaltsev": op.is_maltsev().unwrap(),
                    "type": "binary"
                })
            }
        );
    }
    
    #[test]
    fn test_abstract_operation_is_total() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isTotal", "--type", "binary", "--setSize", "3"],
            || {
                let op = AbstractOperation::simple_binary_op("testBin", 3).unwrap();
                json!({
                    "isTotal": op.is_total().unwrap(),
                    "type": "binary"
                })
            }
        );
    }
    
    // IntOperation tests
    
    #[test]
    fn test_int_operation_xor() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["xor"],
            || {
                let op = IntOperation::binary_xor("xor").unwrap();
                json!({
                    "name": op.symbol().name(),
                    "arity": op.arity(),
                    "setSize": op.get_set_size(),
                    "table": op.get_table().map(|slice| slice.to_vec()),
                    "result_0_0": op.int_value_at(&[0, 0]).unwrap(),
                    "result_0_1": op.int_value_at(&[0, 1]).unwrap(),
                    "result_1_0": op.int_value_at(&[1, 0]).unwrap(),
                    "result_1_1": op.int_value_at(&[1, 1]).unwrap()
                })
            }
        );
    }
    
    #[test]
    fn test_int_operation_and() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["and"],
            || {
                let op = IntOperation::binary_and("and").unwrap();
                json!({
                    "name": op.symbol().name(),
                    "arity": op.arity(),
                    "setSize": op.get_set_size(),
                    "table": op.get_table().map(|slice| slice.to_vec()),
                    "result_0_0": op.int_value_at(&[0, 0]).unwrap(),
                    "result_0_1": op.int_value_at(&[0, 1]).unwrap(),
                    "result_1_0": op.int_value_at(&[1, 0]).unwrap(),
                    "result_1_1": op.int_value_at(&[1, 1]).unwrap()
                })
            }
        );
    }
    
    #[test]
    fn test_int_operation_or() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["or"],
            || {
                let op = IntOperation::binary_or("or").unwrap();
                json!({
                    "name": op.symbol().name(),
                    "arity": op.arity(),
                    "setSize": op.get_set_size(),
                    "table": op.get_table().map(|slice| slice.to_vec()),
                    "result_0_0": op.int_value_at(&[0, 0]).unwrap(),
                    "result_0_1": op.int_value_at(&[0, 1]).unwrap(),
                    "result_1_0": op.int_value_at(&[1, 0]).unwrap(),
                    "result_1_1": op.int_value_at(&[1, 1]).unwrap()
                })
            }
        );
    }
    
    #[test]
    fn test_int_operation_table_access() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["getTable", "--type", "xor"],
            || {
                let op = IntOperation::binary_xor("xor").unwrap();
                let table = op.get_table().map(|slice| slice.to_vec());
                json!({
                    "table": table,
                    "tableSize": table.as_ref().map(|t| t.len()).unwrap_or(0),
                    "type": "xor"
                })
            }
        );
    }
    
    #[test]
    fn test_int_operation_is_table_based() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["isTableBased", "--type", "and"],
            || {
                let op = IntOperation::binary_and("and").unwrap();
                json!({
                    "isTableBased": op.is_table_based(),
                    "type": "and"
                })
            }
        );
    }
    
    #[test]
    fn test_int_operation_properties() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["isIdempotent", "--type", "and"],
            || {
                let op = IntOperation::binary_and("and").unwrap();
                json!({
                    "isIdempotent": op.is_idempotent().unwrap(),
                    "type": "and"
                })
            }
        );
    }
    
    #[test]
    fn test_int_operation_is_commutative() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["isCommutative", "--type", "or"],
            || {
                let op = IntOperation::binary_or("or").unwrap();
                json!({
                    "isCommutative": op.is_commutative().unwrap(),
                    "type": "or"
                })
            }
        );
    }
    
    #[test]
    fn test_int_operation_horner_access() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["intValueAtHorner", "--type", "xor", "--index", "1"],
            || {
                let op = IntOperation::binary_xor("xor").unwrap();
                let result = op.int_value_at_horner(1).unwrap();
                json!({
                    "result": result,
                    "index": 1,
                    "type": "xor"
                })
            }
        );
    }
}