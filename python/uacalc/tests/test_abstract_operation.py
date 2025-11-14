import unittest
import json
import subprocess
from test_utils import build_java_command


class TestAbstractOperation(unittest.TestCase):
    """Test AbstractOperation Python-instantiable implementation."""
    
    def test_abstract_operation_from_int_function(self):
        """Test creating AbstractOperation from integer function."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Define a custom binary operation: (a + b) mod 3
        def add_mod3(args):
            return (args[0] + args[1]) % 3
        
        # Create operation from integer function
        op = AbstractOperation.from_int_value_at_function("add_mod3", 2, 3, add_mod3)
        
        self.assertEqual(op.arity(), 2)
        self.assertEqual(op.get_set_size(), 3)
        self.assertFalse(op.is_table_based())  # Should start as function-based
        self.assertIsNone(op.get_table())  # No table initially
        
        # Test some values
        self.assertEqual(op.int_value_at([0, 1]), 1)
        self.assertEqual(op.int_value_at([1, 2]), 0)
        self.assertEqual(op.int_value_at([2, 2]), 1)
    
    def test_abstract_operation_from_value_function(self):
        """Test creating AbstractOperation from non-integer universe function."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Define universe of strings
        universe = ["red", "green", "blue"]
        
        # Define a string operation: "mix" colors
        def color_mix(args):
            color1, color2 = args[0], args[1]
            if color1 == color2:
                return color1
            elif {color1, color2} == {"red", "green"}:
                return "blue"
            elif {color1, color2} == {"red", "blue"}:
                return "green" 
            elif {color1, color2} == {"green", "blue"}:
                return "red"
            else:
                return "red"  # default
        
        # Create operation from function
        op = AbstractOperation.from_value_at_function("color_mix", 2, universe, color_mix)
        
        self.assertEqual(op.arity(), 2)
        self.assertEqual(op.get_set_size(), 3)
        self.assertFalse(op.is_table_based())
        
        # Test some combinations (using integer indices)
        self.assertEqual(op.int_value_at([0, 0]), 0)  # red + red = red (index 0)
        self.assertEqual(op.int_value_at([0, 1]), 2)  # red + green = blue (index 2)
        self.assertEqual(op.int_value_at([1, 2]), 0)  # green + blue = red (index 0)
    
    def test_make_table_int_function(self):
        """Test converting integer function to table-based evaluation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Define a binary AND operation
        def binary_and(args):
            return args[0] & args[1]
        
        op = AbstractOperation.from_int_value_at_function("and", 2, 2, binary_and)
        
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
    
    def test_make_table_value_function(self):
        """Test converting value function to table-based evaluation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Define universe and operation
        universe = ["x", "y"]
        def string_op(args):
            # Simple operation: return second argument
            return args[1]
        
        op = AbstractOperation.from_value_at_function("second", 2, universe, string_op)
        
        # Initially function-based
        self.assertFalse(op.is_table_based())
        
        # Convert to table-based
        op.make_table()
        
        # Now should be table-based
        self.assertTrue(op.is_table_based())
        expected_table = [0, 1, 0, 1]  # f(x,x)=x, f(x,y)=y, f(y,x)=x, f(y,y)=y → [0,1,0,1]
        self.assertEqual(op.get_table(), expected_table)
    
    def test_property_checks(self):
        """Test property checks work with both function types."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Test with integer function: max operation
        def binary_max(args):
            return max(args[0], args[1])
        
        max_op = AbstractOperation.from_int_value_at_function("max", 2, 3, binary_max)
        
        self.assertTrue(max_op.is_idempotent())
        self.assertTrue(max_op.is_associative())
        self.assertTrue(max_op.is_commutative())
        self.assertTrue(max_op.is_totally_symmetric())
        self.assertFalse(max_op.is_maltsev())  # Binary operation can't be Maltsev
        self.assertTrue(max_op.is_total())
        
        # Test with value function: string concatenation
        universe = ["a", "b"]
        def concat_op(args):
            return args[0] + args[1]
        
        concat_universe = ["aa", "ab", "ba", "bb"]
        concat_op_expanded = AbstractOperation.from_value_at_function("concat", 2, concat_universe, concat_op)
        
        # This should work even with string universe
        self.assertTrue(concat_op_expanded.is_total())
    
    def test_unary_operation(self):
        """Test unary operations."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Define a unary operation: f(x) = (x + 1) mod 3
        def increment_mod3(args):
            return (args[0] + 1) % 3
        
        op = AbstractOperation.from_int_value_at_function("inc", 1, 3, increment_mod3)
        
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
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Define a constant operation that returns 1
        def constant_1(args):
            return 1
        
        op = AbstractOperation.from_int_value_at_function("const1", 0, 4, constant_1)
        
        self.assertEqual(op.arity(), 0)
        self.assertEqual(op.get_set_size(), 4)
        self.assertEqual(op.int_value_at([]), 1)
        
        # Test properties
        self.assertTrue(op.is_totally_symmetric())  # Nullary operations are trivially symmetric
        self.assertTrue(op.is_total())
    
    def test_ternary_maltsev_operation(self):
        """Test ternary Maltsev operation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Define a Maltsev operation: f(x,y,z) = (x - y + z) mod n
        def maltsev_op(args):
            x, y, z = args[0], args[1], args[2]
            return (x - y + z) % 3
        
        op = AbstractOperation.from_int_value_at_function("maltsev", 3, 3, maltsev_op)
        
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
    
    def test_string_operations(self):
        """Test operations on string universes."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Define a universe of words
        universe = ["cat", "dog", "fish"]
        
        # Define an operation that returns the "dominant" animal
        def animal_dominance(args):
            animal1, animal2 = args[0], args[1]
            # Simple dominance: fish > dog > cat
            dominance = {"cat": 0, "dog": 1, "fish": 2}
            if dominance[animal1] >= dominance[animal2]:
                return animal1
            else:
                return animal2
        
        op = AbstractOperation.from_value_at_function("dominance", 2, universe, animal_dominance)
        
        self.assertEqual(op.arity(), 2)
        self.assertEqual(op.get_set_size(), 3)
        
        # Test dominance (using indices: cat=0, dog=1, fish=2)
        self.assertEqual(op.int_value_at([0, 1]), 1)  # dog > cat
        self.assertEqual(op.int_value_at([1, 2]), 2)  # fish > dog
        self.assertEqual(op.int_value_at([2, 0]), 2)  # fish > cat
        self.assertEqual(op.int_value_at([1, 1]), 1)  # dog = dog
    
    def test_string_representation(self):
        """Test string representations."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Test integer function
        def simple_op(args):
            return args[0]
        
        int_op = AbstractOperation.from_int_value_at_function("identity", 1, 3, simple_op)
        
        str_repr = str(int_op)
        self.assertIn("AbstractOperation", str_repr)
        self.assertIn("identity", str_repr)
        self.assertIn("universe=integer", str_repr)
        self.assertIn("table_based=false", str_repr)
        
        # Test value function 
        universe = ["a", "b"]
        def value_op(args):
            return args[0]
        
        value_op = AbstractOperation.from_value_at_function("identity_str", 1, universe, value_op)
        
        str_repr = str(value_op)
        self.assertIn("universe=general", str_repr)
        
        # Test __repr__ method
        repr_str = repr(int_op)
        self.assertIn("AbstractOperation", repr_str)
        self.assertIn("identity", repr_str)
    
    def test_error_handling(self):
        """Test error handling for invalid operations."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        
        # Test integer function that returns out-of-range value
        def bad_int_function(args):
            return 999  # This will be out of range for set_size=2
        
        try:
            op = AbstractOperation.from_int_value_at_function("bad", 2, 2, bad_int_function)
            op.int_value_at([0, 1])  # This should fail when function is called
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertIn("out of range", str(e))
        
        # Test value function that returns value not in universe
        def bad_value_function(args):
            return "yellow"  # Not in universe ["red", "green", "blue"]
        
        try:
            op = AbstractOperation.from_value_at_function("bad", 2, ["red", "green", "blue"], bad_value_function)
            op.int_value_at([0, 1])  # This should fail when function is called
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertIn("not in the universe", str(e))
    
    def test_comparison_with_basic_operation(self):
        """Test that AbstractOperation can do similar things to BasicOperation."""
        import uacalc_lib
        AbstractOperation = uacalc_lib.alg.AbstractOperation
        BasicOperation = uacalc_lib.alg.BasicOperation
        
        # Create equivalent operations
        def add_mod3(args):
            return (args[0] + args[1]) % 3
        
        abstract_op = AbstractOperation.from_int_value_at_function("add_mod3", 2, 3, add_mod3)
        basic_op = BasicOperation.simple_binary_op("test", 3)  # This uses a similar add operation
        
        # Both should have same basic properties
        self.assertEqual(abstract_op.arity(), basic_op.arity())
        self.assertEqual(abstract_op.get_set_size(), basic_op.get_set_size())
        
        # Both should support table creation
        abstract_op.make_table()
        basic_op.make_table()
        
        self.assertTrue(abstract_op.is_table_based())
        self.assertTrue(basic_op.is_table_based())


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
