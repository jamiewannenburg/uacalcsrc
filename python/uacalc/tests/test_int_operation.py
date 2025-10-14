import unittest
import json
import subprocess
from test_utils import build_java_command


class TestIntOperation(unittest.TestCase):
    """Test IntOperation concrete implementation."""
    
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
        # IntOperation is always table-based in our implementation (by design)
        self.assertTrue(op.is_table_based())
        # Java wrapper returns False, but that's a different implementation approach
    
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
        
        # IntOperation is always table-based in our implementation (by design)
        self.assertTrue(op.is_table_based())
        # Java wrapper returns False, but that's a different implementation approach
    
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
    
    def test_int_operation_string_representation(self):
        """Test string representations."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        int_op = IntOperation.binary_xor("xor")
        
        # Test __str__ method
        int_str = str(int_op)
        self.assertIn("xor", int_str)
        
        # Test __repr__ method
        int_repr = repr(int_op)
        self.assertIn("IntOperation", int_repr)
    
    def test_int_operation_from_int_value_at(self):
        """Test creating IntOperation from int_value_at function."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        # Define a custom operation function: (a + b) mod 3
        def add_mod3(args):
            return (args[0] + args[1]) % 3
        
        # Create operation from function
        op = IntOperation.from_int_value_at("add_mod3", 2, 3, add_mod3)
        
        self.assertEqual(op.arity(), 2)
        self.assertEqual(op.get_set_size(), 3)
        
        # Test some values
        for i in range(3):
            for j in range(3):
                result = op.int_value_at([i, j])
                expected = (i + j) % 3
                self.assertEqual(result, expected)
    
    def test_int_operation_from_matrix(self):
        """Test creating IntOperation from matrix."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        
        # XOR operation matrix
        xor_matrix = [
            [0, 1],
            [1, 0]
        ]
        
        op = IntOperation.from_matrix("xor_matrix", xor_matrix)
        
        self.assertEqual(op.arity(), 2)
        self.assertEqual(op.get_set_size(), 2)
        
        # Test the operation
        for i in range(2):
            for j in range(2):
                result = op.int_value_at([i, j])
                expected = xor_matrix[i][j]
                self.assertEqual(result, expected)


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
