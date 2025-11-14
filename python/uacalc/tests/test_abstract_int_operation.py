import unittest
import json
import subprocess
from test_utils import build_java_command


class TestAbstractIntOperation(unittest.TestCase):
    """Test AbstractIntOperation Python-instantiable implementation."""
    
    def test_abstract_int_operation_from_function(self):
        """Test creating AbstractIntOperation from Python function."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        # Define a custom binary operation: (a + b) mod 3
        def add_mod3(args):
            return (args[0] + args[1]) % 3
        
        # Create operation from function
        op = AbstractIntOperation.from_int_value_at_function("add_mod3", 2, 3, add_mod3)
        
        self.assertEqual(op.arity(), 2)
        self.assertEqual(op.get_set_size(), 3)
        self.assertFalse(op.is_table_based())  # Should start as function-based
        self.assertIsNone(op.get_table())  # No table initially
        
        # Test some values
        self.assertEqual(op.int_value_at([0, 1]), 1)
        self.assertEqual(op.int_value_at([1, 2]), 0)
        self.assertEqual(op.int_value_at([2, 2]), 1)
    
    def test_abstract_int_operation_from_table(self):
        """Test creating AbstractIntOperation from table."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        # XOR truth table
        table = [0, 1, 1, 0]
        op = AbstractIntOperation.from_table("xor", 2, 2, table)
        
        self.assertEqual(op.arity(), 2)
        self.assertEqual(op.get_set_size(), 2)
        self.assertTrue(op.is_table_based())  # Should start as table-based
        self.assertEqual(op.get_table(), table)
        
        # Test XOR operation
        self.assertEqual(op.int_value_at([0, 0]), 0)
        self.assertEqual(op.int_value_at([0, 1]), 1)
        self.assertEqual(op.int_value_at([1, 0]), 1)
        self.assertEqual(op.int_value_at([1, 1]), 0)
    
    def test_make_table_transition(self):
        """Test converting from function-based to table-based evaluation."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        # Define a binary AND operation
        def binary_and(args):
            return args[0] & args[1]
        
        op = AbstractIntOperation.from_int_value_at_function("and", 2, 2, binary_and)
        
        # Initially function-based
        self.assertFalse(op.is_table_based())
        self.assertIsNone(op.get_table())
        
        # Convert to table-based
        op.make_table()
        
        # Now should be table-based
        self.assertTrue(op.is_table_based())
        expected_table = [0, 0, 0, 1]  # AND truth table
        self.assertEqual(op.get_table(), expected_table)
        
        # Results should be the same
        self.assertEqual(op.int_value_at([0, 0]), 0)
        self.assertEqual(op.int_value_at([0, 1]), 0)
        self.assertEqual(op.int_value_at([1, 0]), 0)
        self.assertEqual(op.int_value_at([1, 1]), 1)
    
    def test_property_checks_function_based(self):
        """Test property checks work with function-based operations."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        # Define an idempotent operation: max(a, b)
        def binary_max(args):
            return max(args[0], args[1])
        
        op = AbstractIntOperation.from_int_value_at_function("max", 2, 3, binary_max)
        
        self.assertTrue(op.is_idempotent())
        self.assertTrue(op.is_associative())
        self.assertTrue(op.is_commutative())
        self.assertTrue(op.is_totally_symmetric())
        self.assertFalse(op.is_maltsev())  # Binary operation can't be Maltsev
        self.assertTrue(op.is_total())
    
    def test_property_checks_table_based(self):
        """Test property checks work with table-based operations."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        # XOR operation table
        xor_table = [0, 1, 1, 0]
        op = AbstractIntOperation.from_table("xor", 2, 2, xor_table)
        
        self.assertFalse(op.is_idempotent())  # XOR is not idempotent
        self.assertTrue(op.is_associative())  # XOR is associative
        self.assertTrue(op.is_commutative())  # XOR is commutative
        self.assertTrue(op.is_totally_symmetric())  # XOR is totally symmetric
        self.assertFalse(op.is_maltsev())  # Binary operation can't be Maltsev
        self.assertTrue(op.is_total())
    
    def test_unary_operation(self):
        """Test unary operations."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        # Define a unary operation: f(x) = (x + 1) mod 3
        def increment_mod3(args):
            return (args[0] + 1) % 3
        
        op = AbstractIntOperation.from_int_value_at_function("inc", 1, 3, increment_mod3)
        
        self.assertEqual(op.arity(), 1)
        self.assertEqual(op.get_set_size(), 3)
        
        # Test evaluation
        self.assertEqual(op.int_value_at([0]), 1)
        self.assertEqual(op.int_value_at([1]), 2)
        self.assertEqual(op.int_value_at([2]), 0)
        
        # Test properties
        self.assertFalse(op.is_idempotent())  # Not idempotent
        self.assertTrue(op.is_totally_symmetric())  # Unary operations are trivially symmetric
    
    def test_nullary_operation(self):
        """Test nullary (constant) operations."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        # Define a constant operation that returns 2
        def constant_2(args):
            return 2
        
        op = AbstractIntOperation.from_int_value_at_function("const2", 0, 4, constant_2)
        
        self.assertEqual(op.arity(), 0)
        self.assertEqual(op.get_set_size(), 4)
        self.assertEqual(op.int_value_at([]), 2)
        
        # Test properties
        self.assertTrue(op.is_totally_symmetric())  # Nullary operations are trivially symmetric
        self.assertTrue(op.is_total())
    
    def test_ternary_maltsev_operation(self):
        """Test ternary Maltsev operation."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        # Define a Maltsev operation: f(x,y,z) = (x - y + z) mod n
        # This satisfies f(x,y,y) = x and f(x,x,y) = y
        def maltsev_op(args):
            x, y, z = args[0], args[1], args[2]
            return (x - y + z) % 3
        
        op = AbstractIntOperation.from_int_value_at_function("maltsev", 3, 3, maltsev_op)
        
        self.assertEqual(op.arity(), 3)
        self.assertTrue(op.is_maltsev())  # Should be Maltsev
        
        # Verify Maltsev properties manually
        for x in range(3):
            for y in range(3):
                # f(x,y,y) should equal x
                xyy = op.int_value_at([x, y, y])
                self.assertEqual(xyy, x, f"f({x},{y},{y}) = {xyy}, expected {x}")
                
                # f(x,x,y) should equal y  
                xxy = op.int_value_at([x, x, y])
                self.assertEqual(xxy, y, f"f({x},{x},{y}) = {xxy}, expected {y}")
    
    def test_error_handling(self):
        """Test error handling for invalid operations."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        # Test function that returns out-of-range value
        def bad_function(args):
            return 999  # This will be out of range for set_size=2
        
        try:
            op = AbstractIntOperation.from_int_value_at_function("bad", 2, 2, bad_function)
            op.int_value_at([0, 1])  # This should fail when function is called
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertIn("out of range", str(e))
        
        # Test invalid table size
        try:
            bad_table = [0, 1, 2]  # Wrong size for binary operation on set of size 2
            op = AbstractIntOperation.from_table("bad", 2, 2, bad_table)
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertIn("Table size", str(e))
    
    def test_comparison_with_java_wrapper(self):
        """Test comparison with Java AbstractIntOperationWrapper."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        # Create a simple binary operation for testing - we'll use a table since 
        # Java wrapper can't accept arbitrary functions
        table = [0, 1, 1, 0]  # XOR table
        op = AbstractIntOperation.from_table("test", 2, 2, table)
        
        # Compare with Java wrapper basic properties
        java_result = run_java_wrapper(
            "java_wrapper.src.alg.op.AbstractIntOperationWrapper",
            ["arity", "--name", "test", "--arity", "2", "--algSize", "2"]
        )
        
        self.assertEqual(op.arity(), java_result["data"]["arity"])
    
    def test_string_representation(self):
        """Test string representations."""
        import uacalc_lib
        AbstractIntOperation = uacalc_lib.alg.AbstractIntOperation
        
        def simple_op(args):
            return args[0]
        
        op = AbstractIntOperation.from_int_value_at_function("identity", 1, 3, simple_op)
        
        # Test __str__ method
        str_repr = str(op)
        self.assertIn("AbstractIntOperation", str_repr)
        self.assertIn("identity", str_repr)
        self.assertIn("table_based=false", str_repr)
        
        # After making table
        op.make_table()
        str_repr_after = str(op)
        self.assertIn("table_based=true", str_repr_after)
        
        # Test __repr__ method
        repr_str = repr(op)
        self.assertIn("AbstractIntOperation", repr_str)
        self.assertIn("identity", repr_str)


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
