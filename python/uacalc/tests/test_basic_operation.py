import unittest
import json
import subprocess
from test_utils import build_java_command


class TestBasicOperation(unittest.TestCase):
    """Test BasicOperation concrete implementation."""
    
    def test_basic_operation_creation(self):
        """Test BasicOperation creation and basic properties."""
        import uacalc_lib
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        symbol = OperationSymbol("testBin", 2, False)
        op = BasicOperation(symbol, 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
    
    def test_basic_operation_simple_binary(self):
        """Test simple binary operation creation."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
    
    def test_basic_operation_simple_unary(self):
        """Test simple unary operation creation."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_unary_op("testUn", 4)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "unary", "--setSize", "4"]
        )
        
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
    
    def test_basic_operation_simple_nullary(self):
        """Test simple nullary operation creation."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_nullary_op("testNull", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["arity", "--type", "nullary", "--setSize", "3"]
        )
        
        self.assertEqual(op.arity(), java_result["data"]["arity"])
        self.assertEqual(op.get_set_size(), java_result["data"]["setSize"])
    
    def test_basic_operation_value_at(self):
        """Test operation evaluation."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 3)
        result = op.int_value_at([0, 1])
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["intValueAt", "--type", "binary", "--args", "0,1", "--setSize", "3"]
        )
        
        self.assertEqual(result, java_result["data"]["result"])
    
    def test_basic_operation_unary_value(self):
        """Test unary operation evaluation."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_unary_op("testUn", 3)
        result = op.int_value_at([2])
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["intValueAt", "--type", "unary", "--args", "2", "--setSize", "3"]
        )
        
        self.assertEqual(result, java_result["data"]["result"])
    
    def test_basic_operation_nullary_value(self):
        """Test nullary operation evaluation."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_nullary_op("testNull", 3)
        result = op.int_value_at([])
        
        # Note: Java wrapper expects empty string for nullary args
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["intValueAt", "--type", "nullary", "--args", "", "--setSize", "3"]
        )
        
        self.assertEqual(result, java_result["data"]["result"])
    
    def test_basic_operation_symbol(self):
        """Test operation symbol access."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 3)
        symbol = op.symbol()
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["symbol", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(symbol.name(), java_result["data"]["symbolName"])
        self.assertEqual(symbol.arity(), java_result["data"]["symbolArity"])
        self.assertEqual(symbol.is_associative(), java_result["data"]["symbolAssociative"])
    
    def test_basic_operation_make_table(self):
        """Test table creation."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 2)
        op.make_table()
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["makeTable", "--type", "binary", "--setSize", "2"]
        )
        
        self.assertEqual(op.is_table_based(), java_result["data"]["isTableBased"])
    
    def test_basic_operation_get_table(self):
        """Test table retrieval."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 2)
        op.make_table()
        table = op.get_table()
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["getTable", "--type", "binary", "--setSize", "2"]
        )
        
        self.assertEqual(table, java_result["data"]["table"])
        self.assertEqual(table is not None, java_result["data"]["hasTable"])
    
    def test_basic_operation_is_table_based(self):
        """Test table-based check."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isTableBased", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_table_based(), java_result["data"]["isTableBased"])
    
    def test_basic_operation_is_idempotent(self):
        """Test idempotent property check."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isIdempotent", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_idempotent(), java_result["data"]["isIdempotent"])
    
    def test_basic_operation_is_associative(self):
        """Test associative property check."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isAssociative", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_associative(), java_result["data"]["isAssociative"])
    
    def test_basic_operation_is_commutative(self):
        """Test commutative property check."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isCommutative", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_commutative(), java_result["data"]["isCommutative"])
    
    def test_basic_operation_is_totally_symmetric(self):
        """Test totally symmetric property check."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isTotallySymmetric", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_totally_symmetric(), java_result["data"]["isTotallySymmetric"])
    
    def test_basic_operation_is_maltsev(self):
        """Test Maltsev operation check."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isMaltsev", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_maltsev(), java_result["data"]["isMaltsev"])
    
    def test_basic_operation_is_total(self):
        """Test total operation check."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op = BasicOperation.simple_binary_op("testBin", 3)
        
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractOperationWrapper",
            ["isTotal", "--type", "binary", "--setSize", "3"]
        )
        
        self.assertEqual(op.is_total(), java_result["data"]["isTotal"])
    
    def test_basic_operation_comparison(self):
        """Test operation comparison."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op1 = BasicOperation.simple_binary_op("a", 3)
        op2 = BasicOperation.simple_binary_op("b", 3)
        op3 = BasicOperation.simple_unary_op("c", 3)
        
        # Test equality
        op4 = BasicOperation.simple_binary_op("a", 3)
        self.assertEqual(op1, op4)
        
        # Test inequality
        self.assertNotEqual(op1, op2)
        self.assertNotEqual(op1, op3)
        
        # Test ordering
        self.assertTrue(op1 < op3)  # Binary < Unary in arity-based ordering
        
    def test_basic_operation_string_representation(self):
        """Test string representations."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        basic_op = BasicOperation.simple_binary_op("test", 3)
        
        # Test __str__ method
        basic_str = str(basic_op)
        self.assertIn("test", basic_str)
        
        # Test __repr__ method
        basic_repr = repr(basic_op)
        self.assertIn("BasicOperation", basic_repr)
        
    def test_basic_operation_hash(self):
        """Test hash functionality."""
        import uacalc_lib
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        op1 = BasicOperation.simple_binary_op("test", 3)
        op2 = BasicOperation.simple_binary_op("test", 3)
        op3 = BasicOperation.simple_binary_op("other", 3)
        
        # Equal operations should have equal hashes
        self.assertEqual(hash(op1), hash(op2))
        
        # Different operations should have different hashes (usually)
        self.assertNotEqual(hash(op1), hash(op3))
        
        # Operations should be usable in sets
        op_set = {op1, op2, op3}
        self.assertEqual(len(op_set), 2)  # op1 and op2 are equal


def run_java_wrapper(wrapper_class: str, args):
    """Run Java wrapper and return JSON output."""
    cmd = build_java_command(wrapper_class, args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30.0
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Java wrapper failed: {result.stderr}")
        
        return json.loads(result.stdout)
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("Java wrapper timed out")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Java wrapper output: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error running Java wrapper: {e}")


if __name__ == "__main__":
    unittest.main()
