import unittest
import json
from test_utils import run_java_wrapper


class TestOperation(unittest.TestCase):
    """Test Operation interface and concrete implementations."""
    
    def test_abstract_operation_creation(self):
        """Test AbstractOperation creation and basic properties."""
        import uacalc_lib
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        symbol = OperationSymbol("testBin", 2, False)
        op = AbstractOperation(symbol, 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
    
    def test_abstract_operation_simple_binary(self):
        """Test simple binary operation creation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
    
    def test_abstract_operation_simple_unary(self):
        """Test simple unary operation creation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_unary_op("testUn", 4)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "unary", "--setSize", "4"]
        )
        
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
    
    def test_abstract_operation_simple_nullary(self):
        """Test simple nullary operation creation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_nullary_op("testNull", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "nullary", "--setSize", "3"]
        )
        
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
    
    def test_abstract_operation_value_at(self):
        """Test operation evaluation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 3)
        result = op.int_value_at([0, 1])
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["intValueAt", "--type", "binary", "--args", "0,1", "--setSize", "3"]
        )
        
        self.assertEqual(result, java_result["data"]["result"])
    
    def test_abstract_operation_unary_value(self):
        """Test unary operation evaluation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_unary_op("testUn", 3)
        result = op.int_value_at([2])
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["intValueAt", "--type", "unary", "--args", "2", "--setSize", "3"]
        )
        
        self.assertEqual(result, java_result["data"]["result"])
    
    def test_abstract_operation_nullary_value(self):
        """Test nullary operation evaluation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_nullary_op("testNull", 3)
        result = op.int_value_at([])
        
        # Note: Java wrapper expects empty string for nullary args
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["intValueAt", "--type", "nullary", "--args", "", "--setSize", "3"]
        )
        
        self.assertEqual(result, java_result["data"]["result"])
    
    def test_abstract_operation_symbol(self):
        """Test operation symbol access."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 3)
        symbol = op.symbol()
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["symbol", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(symbol.name(), java_result["data"]["symbolName"])
        self.assertEqual(symbol.arity(), java_result["data"]["symbolArity"])
        self.assertEqual(symbol.is_associative(), java_result["data"]["symbolAssociative"])
    
    def test_abstract_operation_make_table(self):
        """Test table creation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 2)
        op.make_table()
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["makeTable", "--type", "binary", "--setSize", "2"]
        )
        
        self.assertEqual(op.is_table_based(), java_result["data"]["isTableBased"])
    
    def test_abstract_operation_get_table(self):
        """Test table retrieval."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 2)
        op.make_table()
        table = op.get_table()
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["getTable", "--type", "binary", "--setSize", "2"]
        )
        
        self.assertEqual(table, java_result["data"]["table"])
        self.assertEqual(table is not None, java_result["data"]["hasTable"])
    
    def test_abstract_operation_is_table_based(self):
        """Test table-based check."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isTableBased", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_table_based(), java_result["data"]["isTableBased"])
    
    def test_abstract_operation_is_idempotent(self):
        """Test idempotent property check."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isIdempotent", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_idempotent(), java_result["data"]["isIdempotent"])
    
    def test_abstract_operation_is_associative(self):
        """Test associative property check."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isAssociative", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_associative(), java_result["data"]["isAssociative"])
    
    def test_abstract_operation_is_commutative(self):
        """Test commutative property check."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isCommutative", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_commutative(), java_result["data"]["isCommutative"])
    
    def test_abstract_operation_is_totally_symmetric(self):
        """Test totally symmetric property check."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isTotallySymmetric", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_totally_symmetric(), java_result["data"]["isTotallySymmetric"])
    
    def test_abstract_operation_is_maltsev(self):
        """Test Maltsev operation check."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isMaltsev", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_maltsev(), java_result["data"]["isMaltsev"])
    
    def test_abstract_operation_is_total(self):
        """Test total operation check."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op = AbstractOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isTotal", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_total(), java_result["data"]["isTotal"])
    
    # IntOperation tests
    
    def test_int_operation_xor(self):
        """Test XOR operation."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        op = IntOperation.binary_xor("xor")
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["xor"]
        )
        
        self.assertEqual(op.symbol().name(), java_result["data"]["name"])
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
        self.assertEqual(op.get_table(), java_result["data"]["table"])
        self.assertEqual(op.int_value_at([0, 0]), java_result["data"]["result_0_0"])
        self.assertEqual(op.int_value_at([0, 1]), java_result["data"]["result_0_1"])
        self.assertEqual(op.int_value_at([1, 0]), java_result["data"]["result_1_0"])
        self.assertEqual(op.int_value_at([1, 1]), java_result["data"]["result_1_1"])
    
    def test_int_operation_and(self):
        """Test AND operation."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        op = IntOperation.binary_and("and")
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["and"]
        )
        
        self.assertEqual(op.symbol().name(), java_result["data"]["name"])
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
        self.assertEqual(op.get_table(), java_result["data"]["table"])
        self.assertEqual(op.int_value_at([0, 0]), java_result["data"]["result_0_0"])
        self.assertEqual(op.int_value_at([0, 1]), java_result["data"]["result_0_1"])
        self.assertEqual(op.int_value_at([1, 0]), java_result["data"]["result_1_0"])
        self.assertEqual(op.int_value_at([1, 1]), java_result["data"]["result_1_1"])
    
    def test_int_operation_or(self):
        """Test OR operation."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        op = IntOperation.binary_or("or")
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["or"]
        )
        
        self.assertEqual(op.symbol().name(), java_result["data"]["name"])
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
        self.assertEqual(op.get_table(), java_result["data"]["table"])
        self.assertEqual(op.int_value_at([0, 0]), java_result["data"]["result_0_0"])
        self.assertEqual(op.int_value_at([0, 1]), java_result["data"]["result_0_1"])
        self.assertEqual(op.int_value_at([1, 0]), java_result["data"]["result_1_0"])
        self.assertEqual(op.int_value_at([1, 1]), java_result["data"]["result_1_1"])
    
    def test_int_operation_custom(self):
        """Test custom IntOperation creation."""
        import uacalc_lib
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        IntOperation = uacalc_lib.alg.IntOperation
        
        symbol = OperationSymbol("f", 2, False)
        table = [0, 1, 1, 0]  # XOR table
        op = IntOperation(symbol, 2, table)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["create", "--name", "f", "--arity", "2", "--setSize", "2", "--table", "0,1,1,0"]
        )
        
        self.assertEqual(op.symbol().name(), java_result["data"]["name"])
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
        self.assertEqual(op.get_table(), java_result["data"]["table"])
        self.assertEqual(op.is_table_based(), java_result["data"]["isTableBased"])
    
    def test_int_operation_table_access(self):
        """Test table access."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        op = IntOperation.binary_xor("xor")
        table = op.get_table()
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["getTable", "--type", "xor"]
        )
        
        self.assertEqual(table, java_result["data"]["table"])
        self.assertEqual(len(table), java_result["data"]["tableSize"])
    
    def test_int_operation_is_table_based(self):
        """Test table-based check."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        op = IntOperation.binary_and("and")
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["isTableBased", "--type", "and"]
        )
        
        self.assertEqual(op.is_table_based(), java_result["data"]["isTableBased"])
    
    def test_int_operation_properties(self):
        """Test operation properties."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        op = IntOperation.binary_and("and")
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["isIdempotent", "--type", "and"]
        )
        
        self.assertEqual(op.is_idempotent(), java_result["data"]["isIdempotent"])
    
    def test_int_operation_is_commutative(self):
        """Test commutative property."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        op = IntOperation.binary_or("or")
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["isCommutative", "--type", "or"]
        )
        
        self.assertEqual(op.is_commutative(), java_result["data"]["isCommutative"])
    
    def test_int_operation_horner_access(self):
        """Test Horner encoding access."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        op = IntOperation.binary_xor("xor")
        result = op.int_value_at_horner(1)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.IntOperationWrapper",
            ["intValueAtHorner", "--type", "xor", "--index", "1"]
        )
        
        self.assertEqual(result, java_result["data"]["result"])
    
    def test_int_operation_unary_not(self):
        """Test unary NOT operation."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        op = IntOperation.unary_not("not")
        
        self.assertEqual(op.arity(), 1)
        self.assertEqual(op.get_set_size(), 2)
        self.assertEqual(op.int_value_at([0]), 1)
        self.assertEqual(op.int_value_at([1]), 0)
    
    def test_int_operation_nullary_constant(self):
        """Test nullary constant operation."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        op = IntOperation.nullary_constant("const", 5)
        
        self.assertEqual(op.arity(), 0)
        self.assertEqual(op.int_value_at([]), 5)
    
    def test_operation_comparison(self):
        """Test operation comparison."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op1 = AbstractOperation.simple_binary_op("a", 3)
        op2 = AbstractOperation.simple_binary_op("b", 3)
        op3 = AbstractOperation.simple_unary_op("c", 3)
        
        # Test equality
        op4 = AbstractOperation.simple_binary_op("a", 3)
        self.assertEqual(op1, op4)
        
        # Test inequality
        self.assertNotEqual(op1, op2)
        self.assertNotEqual(op1, op3)
        
        # Test ordering
        self.assertTrue(op1 < op3)  # Binary < Unary in arity-based ordering
        
    def test_operation_string_representation(self):
        """Test string representations."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        IntOperation = uacalc_lib.alg.IntOperation
        
        abstract_op = AbstractOperation.simple_binary_op("test", 3)
        int_op = IntOperation.binary_xor("xor")
        
        # Test __str__ method
        abstract_str = str(abstract_op)
        int_str = str(int_op)
        
        self.assertIn("test", abstract_str)
        self.assertIn("xor", int_str)
        
        # Test __repr__ method
        abstract_repr = repr(abstract_op)
        int_repr = repr(int_op)
        
        self.assertIn("AbstractOperation", abstract_repr)
        self.assertIn("IntOperation", int_repr)
        
    def test_operation_hash(self):
        """Test hash functionality."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        op1 = AbstractOperation.simple_binary_op("test", 3)
        op2 = AbstractOperation.simple_binary_op("test", 3)
        op3 = AbstractOperation.simple_binary_op("other", 3)
        
        # Equal operations should have equal hashes
        self.assertEqual(hash(op1), hash(op2))
        
        # Different operations should have different hashes (usually)
        self.assertNotEqual(hash(op1), hash(op3))
        
        # Operations should be usable in sets
        op_set = {op1, op2, op3}
        self.assertEqual(len(op_set), 2)  # op1 and op2 are equal


if __name__ == "__main__":
    unittest.main()