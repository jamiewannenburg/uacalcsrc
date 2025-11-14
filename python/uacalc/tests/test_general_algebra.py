"""
Tests for GeneralAlgebra Python bindings.

This module tests the GeneralAlgebra class which supports:
- Different universe types (integers, strings, custom objects)
- AbstractOperations
- All GeneralAlgebra methods
"""

import unittest
import uacalc_lib

GeneralAlgebra = uacalc_lib.alg.GeneralAlgebra
AbstractOperation = uacalc_lib.alg.AbstractOperation


class TestGeneralAlgebra(unittest.TestCase):
    """Test GeneralAlgebra functionality with different universe types."""
    
    def test_creation_with_integer_universe(self):
        """Test creating a GeneralAlgebra with integer universe."""
        universe = [0, 1, 2, 3, 4]
        alg = GeneralAlgebra("TestInt", universe)
        
        self.assertEqual(alg.name(), "TestInt")
        self.assertEqual(alg.cardinality(), 5)
        self.assertEqual(alg.input_size(), 5)
        
        # Check universe
        universe_list = alg.get_universe()
        self.assertEqual(len(universe_list), 5)
        # Universe elements should be integers
        for elem in universe_list:
            self.assertIsInstance(elem, int)
    
    def test_creation_with_string_universe(self):
        """Test creating a GeneralAlgebra with string universe."""
        universe = ["red", "green", "blue"]
        alg = GeneralAlgebra("TestString", universe)
        
        self.assertEqual(alg.name(), "TestString")
        self.assertEqual(alg.cardinality(), 3)
        self.assertEqual(alg.input_size(), 3)
        
        # Check universe
        universe_list = alg.get_universe()
        self.assertEqual(len(universe_list), 3)
        # Universe elements should be strings
        for elem in universe_list:
            self.assertIsInstance(elem, str)
    
    def test_creation_with_mixed_universe(self):
        """Test creating a GeneralAlgebra with mixed type universe."""
        universe = [1, "two", 3.0, (4, 5)]
        alg = GeneralAlgebra("TestMixed", universe)
        
        self.assertEqual(alg.name(), "TestMixed")
        self.assertEqual(alg.cardinality(), 4)
        
        # Check universe
        universe_list = alg.get_universe()
        self.assertEqual(len(universe_list), 4)
    
    def test_creation_with_operations(self):
        """Test creating a GeneralAlgebra with AbstractOperations."""
        universe = [0, 1, 2]
        
        # Create a binary operation: (a + b) mod 3
        def add_mod3(args):
            return (args[0] + args[1]) % 3
        
        op = AbstractOperation.from_int_value_at_function("add_mod3", 2, 3, add_mod3)
        
        alg = GeneralAlgebra("TestWithOps", universe, [op])
        
        self.assertEqual(alg.name(), "TestWithOps")
        self.assertEqual(alg.cardinality(), 3)
        self.assertEqual(alg.operations_count(), 1)
        
        # Check operations
        ops = alg.get_operations()
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].arity(), 2)
    
    def test_creation_with_string_universe_and_operations(self):
        """Test creating a GeneralAlgebra with string universe and operations."""
        universe = ["a", "b", "c"]
        
        # Create operation for string universe
        def string_op(args):
            # Simple operation: return first argument
            return args[0]
        
        op = AbstractOperation.from_value_at_function("first", 1, universe, string_op)
        
        alg = GeneralAlgebra("TestStringOps", universe, [op])
        
        self.assertEqual(alg.name(), "TestStringOps")
        self.assertEqual(alg.cardinality(), 3)
        self.assertEqual(alg.operations_count(), 1)
    
    def test_name_and_description(self):
        """Test name and description getters/setters."""
        universe = [0, 1, 2]
        alg = GeneralAlgebra("Test", universe)
        
        # Test name
        self.assertEqual(alg.name(), "Test")
        alg.set_name("NewName")
        self.assertEqual(alg.name(), "NewName")
        
        # Test description
        self.assertIsNone(alg.description())
        alg.set_description("Test description")
        self.assertEqual(alg.description(), "Test description")
        alg.set_description(None)
        self.assertIsNone(alg.description())
    
    def test_cardinality_and_input_size(self):
        """Test cardinality and input_size methods."""
        universe = [0, 1, 2, 3, 4, 5]
        alg = GeneralAlgebra("Test", universe)
        
        self.assertEqual(alg.cardinality(), 6)
        self.assertEqual(alg.input_size(), 6)
    
    def test_is_unary(self):
        """Test is_unary method."""
        universe = [0, 1, 2]
        
        # Create unary operation
        def unary_op(args):
            return (args[0] + 1) % 3
        
        unary = AbstractOperation.from_int_value_at_function("inc", 1, 3, unary_op)
        
        # Create binary operation
        def binary_op(args):
            return (args[0] + args[1]) % 3
        
        binary = AbstractOperation.from_int_value_at_function("add", 2, 3, binary_op)
        
        # Test with unary operations only
        alg_unary = GeneralAlgebra("Unary", universe, [unary])
        self.assertTrue(alg_unary.is_unary())
        
        # Test with binary operation
        alg_binary = GeneralAlgebra("Binary", universe, [binary])
        self.assertFalse(alg_binary.is_unary())
        
        # Test with mixed
        alg_mixed = GeneralAlgebra("Mixed", universe, [unary, binary])
        self.assertFalse(alg_mixed.is_unary())
    
    def test_is_idempotent(self):
        """Test is_idempotent method."""
        universe = [0, 1, 2]
        
        # Create idempotent operation: f(x, x) = x
        def idempotent_op(args):
            return args[0]  # Always return first argument
        
        idem_op = AbstractOperation.from_int_value_at_function("idem", 2, 3, idempotent_op)
        
        # Create non-idempotent operation
        def non_idem_op(args):
            return (args[0] + 1) % 3
        
        non_idem = AbstractOperation.from_int_value_at_function("inc", 1, 3, non_idem_op)
        
        # Test with idempotent operation
        alg_idem = GeneralAlgebra("Idem", universe, [idem_op])
        self.assertTrue(alg_idem.is_idempotent())
        
        # Test with non-idempotent operation
        alg_non_idem = GeneralAlgebra("NonIdem", universe, [non_idem])
        self.assertFalse(alg_non_idem.is_idempotent())
    
    def test_is_total(self):
        """Test is_total method."""
        universe = [0, 1, 2]
        
        def op(args):
            return (args[0] + args[1]) % 3
        
        operation = AbstractOperation.from_int_value_at_function("add", 2, 3, op)
        alg = GeneralAlgebra("Test", universe, [operation])
        
        # AbstractOperations are always total
        self.assertTrue(alg.is_total())
    
    def test_monitoring(self):
        """Test monitoring method."""
        universe = [0, 1, 2]
        alg = GeneralAlgebra("Test", universe)
        
        # Monitoring is not implemented, should return False
        self.assertFalse(alg.monitoring())
    
    def test_add_operation(self):
        """Test adding operations to an algebra."""
        universe = [0, 1, 2]
        alg = GeneralAlgebra("Test", universe)
        
        self.assertEqual(alg.operations_count(), 0)
        
        # Add first operation
        def op1(args):
            return (args[0] + 1) % 3
        
        op1_obj = AbstractOperation.from_int_value_at_function("inc", 1, 3, op1)
        alg.add_operation(op1_obj)
        self.assertEqual(alg.operations_count(), 1)
        
        # Add second operation
        def op2(args):
            return (args[0] + args[1]) % 3
        
        op2_obj = AbstractOperation.from_int_value_at_function("add", 2, 3, op2)
        alg.add_operation(op2_obj)
        self.assertEqual(alg.operations_count(), 2)
        
        # Check operations
        ops = alg.get_operations()
        self.assertEqual(len(ops), 2)
        self.assertEqual(ops[0].arity(), 1)
        self.assertEqual(ops[1].arity(), 2)
    
    def test_get_operation(self):
        """Test getting operation by index."""
        universe = [0, 1, 2]
        
        def op1(args):
            return (args[0] + 1) % 3
        
        def op2(args):
            return (args[0] + args[1]) % 3
        
        op1_obj = AbstractOperation.from_int_value_at_function("inc", 1, 3, op1)
        op2_obj = AbstractOperation.from_int_value_at_function("add", 2, 3, op2)
        
        alg = GeneralAlgebra("Test", universe, [op1_obj, op2_obj])
        
        # Get operations by index
        retrieved_op1 = alg.get_operation(0)
        retrieved_op2 = alg.get_operation(1)
        
        self.assertEqual(retrieved_op1.arity(), 1)
        self.assertEqual(retrieved_op2.arity(), 2)
        
        # Test out of bounds
        with self.assertRaises(Exception):  # Should raise ValueError or similar
            alg.get_operation(2)
    
    def test_str_and_repr(self):
        """Test string representation methods."""
        universe = [0, 1, 2]
        alg = GeneralAlgebra("Test", universe)
        
        str_repr = str(alg)
        repr_repr = repr(alg)
        
        self.assertIn("GeneralAlgebra", str_repr)
        self.assertIn("Test", str_repr)
        self.assertIn("GeneralAlgebra", repr_repr)
        self.assertIn("Test", repr_repr)
    
    def test_equality(self):
        """Test equality comparison."""
        universe1 = [0, 1, 2]
        universe2 = [0, 1, 2]
        universe3 = [0, 1, 2, 3]
        
        alg1 = GeneralAlgebra("Test", universe1)
        alg2 = GeneralAlgebra("Test", universe2)
        alg3 = GeneralAlgebra("Test", universe3)
        alg4 = GeneralAlgebra("Different", universe1)
        
        # Same name and universe should be equal
        self.assertEqual(alg1, alg2)
        
        # Different universe should not be equal
        self.assertNotEqual(alg1, alg3)
        
        # Different name should not be equal
        self.assertNotEqual(alg1, alg4)
    
    def test_with_name_static_method(self):
        """Test with_name static method."""
        alg = GeneralAlgebra.with_name("Empty")
        
        self.assertEqual(alg.name(), "Empty")
        self.assertEqual(alg.cardinality(), 0)
        self.assertEqual(alg.operations_count(), 0)
    
    def test_empty_universe_error(self):
        """Test that empty universe raises an error."""
        with self.assertRaises(Exception):  # Should raise ValueError
            GeneralAlgebra("Test", [])
    
    def test_duplicate_universe_elements(self):
        """Test that duplicate universe elements are handled."""
        # Duplicates should be removed
        universe = [0, 1, 2, 0, 1]  # Contains duplicates
        alg = GeneralAlgebra("Test", universe)
        
        # Should only have unique elements
        self.assertEqual(alg.cardinality(), 3)
        universe_list = alg.get_universe()
        self.assertEqual(len(universe_list), 3)
    
    def test_string_universe_with_operations(self):
        """Test string universe with operations that work on strings."""
        universe = ["apple", "banana", "cherry"]
        
        # Create operation that works with string universe
        def first_string(args):
            return args[0]
        
        op = AbstractOperation.from_value_at_function("first", 1, universe, first_string)
        alg = GeneralAlgebra("Fruit", universe, [op])
        
        self.assertEqual(alg.cardinality(), 3)
        self.assertEqual(alg.operations_count(), 1)
        
        # Test the operation
        ops = alg.get_operations()
        self.assertEqual(ops[0].arity(), 1)
        # Operation should work with string indices
        result = ops[0].int_value_at([0])  # First element
        self.assertEqual(result, 0)
    
    def test_custom_object_universe(self):
        """Test with custom Python objects as universe elements."""
        class CustomObj:
            def __init__(self, value):
                self.value = value
            
            def __eq__(self, other):
                return isinstance(other, CustomObj) and self.value == other.value
        
        universe = [CustomObj(1), CustomObj(2), CustomObj(3)]
        alg = GeneralAlgebra("Custom", universe)
        
        self.assertEqual(alg.cardinality(), 3)
        universe_list = alg.get_universe()
        self.assertEqual(len(universe_list), 3)
        
        # Check that elements are CustomObj instances
        for elem in universe_list:
            self.assertIsInstance(elem, CustomObj)
    
    def test_to_basic_algebra_with_integer_universe(self):
        """Test converting GeneralAlgebra with integer universe to BasicAlgebra."""
        universe = [0, 1, 2, 3]
        alg = GeneralAlgebra("TestInt", universe)
        
        # Convert to BasicAlgebra
        basic_alg = alg.to_basic_algebra()
        
        # Verify properties
        self.assertEqual(basic_alg.name(), "TestInt")
        self.assertEqual(basic_alg.cardinality(), 4)
        self.assertEqual(basic_alg.algebra_type(), "Basic")
        
        # Check universe
        basic_universe = basic_alg.get_universe()
        self.assertEqual(len(basic_universe), 4)
        self.assertEqual(set(basic_universe), {0, 1, 2, 3})
    
    def test_to_basic_algebra_with_string_universe(self):
        """Test converting GeneralAlgebra with string universe to BasicAlgebra."""
        universe = ["a", "b", "c"]
        alg = GeneralAlgebra("TestString", universe)
        
        # Convert to BasicAlgebra
        basic_alg = alg.to_basic_algebra()
        
        # Verify properties
        self.assertEqual(basic_alg.name(), "TestString")
        self.assertEqual(basic_alg.cardinality(), 3)
        self.assertEqual(basic_alg.algebra_type(), "Basic")
        
        # Check universe - should be integers (indices)
        basic_universe = basic_alg.get_universe()
        self.assertEqual(len(basic_universe), 3)
        # Should be integers 0, 1, 2
        self.assertEqual(set(basic_universe), {0, 1, 2})
    
    def test_to_basic_algebra_with_operations(self):
        """Test converting GeneralAlgebra with operations to BasicAlgebra."""
        universe = [0, 1, 2]
        
        # Create a binary operation: (a + b) mod 3
        def add_mod3(args):
            return (args[0] + args[1]) % 3
        
        op = AbstractOperation.from_int_value_at_function("add_mod3", 2, 3, add_mod3)
        alg = GeneralAlgebra("TestWithOps", universe, [op])
        
        # Convert to BasicAlgebra
        basic_alg = alg.to_basic_algebra()
        
        # Verify properties
        self.assertEqual(basic_alg.name(), "TestWithOps")
        self.assertEqual(basic_alg.cardinality(), 3)
        self.assertEqual(basic_alg.operations_count(), 1)
        
        # Check operations
        basic_ops = basic_alg.operations()
        self.assertEqual(len(basic_ops), 1)
        self.assertEqual(basic_ops[0].arity(), 2)
        self.assertEqual(basic_ops[0].get_set_size(), 3)
        
        # Verify operation works correctly
        self.assertEqual(basic_ops[0].int_value_at([0, 1]), 1)  # (0 + 1) % 3 = 1
        self.assertEqual(basic_ops[0].int_value_at([1, 2]), 0)  # (1 + 2) % 3 = 0
        self.assertEqual(basic_ops[0].int_value_at([2, 2]), 1)  # (2 + 2) % 3 = 1
    
    def test_to_basic_algebra_with_multiple_operations(self):
        """Test converting GeneralAlgebra with multiple operations to BasicAlgebra."""
        universe = [0, 1, 2]
        
        # Create unary operation: increment mod 3
        def inc(args):
            return (args[0] + 1) % 3
        
        # Create binary operation: addition mod 3
        def add(args):
            return (args[0] + args[1]) % 3
        
        unary_op = AbstractOperation.from_int_value_at_function("inc", 1, 3, inc)
        binary_op = AbstractOperation.from_int_value_at_function("add", 2, 3, add)
        
        alg = GeneralAlgebra("TestMultiOps", universe, [unary_op, binary_op])
        
        # Convert to BasicAlgebra
        basic_alg = alg.to_basic_algebra()
        
        # Verify properties
        self.assertEqual(basic_alg.name(), "TestMultiOps")
        self.assertEqual(basic_alg.cardinality(), 3)
        self.assertEqual(basic_alg.operations_count(), 2)
        
        # Check operations
        basic_ops = basic_alg.operations()
        self.assertEqual(len(basic_ops), 2)
        
        # Find unary and binary operations
        unary = None
        binary = None
        for op in basic_ops:
            if op.arity() == 1:
                unary = op
            elif op.arity() == 2:
                binary = op
        
        self.assertIsNotNone(unary)
        self.assertIsNotNone(binary)
        
        # Verify unary operation
        self.assertEqual(unary.int_value_at([0]), 1)
        self.assertEqual(unary.int_value_at([1]), 2)
        self.assertEqual(unary.int_value_at([2]), 0)
        
        # Verify binary operation
        self.assertEqual(binary.int_value_at([0, 1]), 1)
        self.assertEqual(binary.int_value_at([1, 2]), 0)
        self.assertEqual(binary.int_value_at([2, 2]), 1)
    
    def test_powerset_boolean_algebra_three_generators(self):
        """Test building a GeneralAlgebra for powerset boolean algebra with three generators."""
        # Universe: all subsets of {0, 1, 2}
        # There are 2^3 = 8 subsets
        base_set = {0, 1, 2}
        universe = []
        # Generate all subsets
        for i in range(8):
            subset = frozenset(j for j in range(3) if (i >> j) & 1)
            universe.append(subset)
        
        # Intersection operation (binary) - works directly with frozensets
        def intersection(args):
            subset1, subset2 = args[0], args[1]
            return subset1 & subset2
        
        # Union operation (binary) - works directly with frozensets
        def union(args):
            subset1, subset2 = args[0], args[1]
            return subset1 | subset2
        
        # Complement operation (unary) - works directly with frozensets
        def complement(args):
            subset = args[0]
            return base_set - subset
        
        # Create operations using value_at (works with actual universe elements)
        intersection_op = AbstractOperation.from_value_at_function("intersection", 2, universe, intersection)
        union_op = AbstractOperation.from_value_at_function("union", 2, universe, union)
        complement_op = AbstractOperation.from_value_at_function("complement", 1, universe, complement)
        
        # Create algebra
        alg = GeneralAlgebra("PowersetBoolean3", universe, [intersection_op, union_op, complement_op])
        
        # Verify properties
        self.assertEqual(alg.name(), "PowersetBoolean3")
        self.assertEqual(alg.cardinality(), 8)
        self.assertEqual(alg.operations_count(), 3)
        
        # Verify operations
        ops = alg.get_operations()
        self.assertEqual(len(ops), 3)
        
        # Define test subsets
        empty_set = frozenset()
        zero_set = frozenset({0})
        one_set = frozenset({1})
        zero_one_set = frozenset({0, 1})
        one_two_set = frozenset({1, 2})
        
        # Identify intersection: {0} ∩ {1} = ∅
        intersection_op_obj = None
        for op in ops:
            if op.arity() == 2:
                result = op.value_at([zero_set, one_set])
                if result == empty_set:
                    intersection_op_obj = op
                    break
        
        # Identify union: {0} ∪ {1} = {0, 1}
        union_op_obj = None
        for op in ops:
            if op.arity() == 2:
                result = op.value_at([zero_set, one_set])
                if result == zero_one_set:
                    union_op_obj = op
                    break
        
        # Identify complement: complement of {0} = {1, 2}
        complement_op_obj = None
        for op in ops:
            if op.arity() == 1:
                result = op.value_at([zero_set])
                if result == one_two_set:
                    complement_op_obj = op
                    break
        
        self.assertIsNotNone(intersection_op_obj, "Could not identify intersection operation")
        self.assertIsNotNone(union_op_obj, "Could not identify union operation")
        self.assertIsNotNone(complement_op_obj, "Could not identify complement operation")
        
        # Test intersection: {0} ∩ {1} = ∅
        self.assertEqual(intersection_op_obj.value_at([zero_set, one_set]), empty_set)
        
        # Test union: {0} ∪ {1} = {0, 1}
        self.assertEqual(union_op_obj.value_at([zero_set, one_set]), zero_one_set)
        
        # Test complement: complement of {0} = {1, 2}
        self.assertEqual(complement_op_obj.value_at([zero_set]), one_two_set)
        
        # Test intersection with itself (idempotent): {0} ∩ {0} = {0}
        self.assertEqual(intersection_op_obj.value_at([zero_set, zero_set]), zero_set)
        
        # Test union with empty set: {0} ∪ ∅ = {0}
        self.assertEqual(union_op_obj.value_at([zero_set, empty_set]), zero_set)
        
        # Test complement of complement: complement(complement({0})) = {0}
        comp_result = complement_op_obj.value_at([zero_set])
        self.assertEqual(complement_op_obj.value_at([comp_result]), zero_set)

        # Check that this algebra can be converted to a BasicAlgebra
        basic_alg = alg.to_basic_algebra()
        self.assertEqual(basic_alg.name(), "PowersetBoolean3")
        self.assertEqual(basic_alg.cardinality(), 8)
        self.assertEqual(basic_alg.operations_count(), 3)
        
        # Check that the operations are the same
        basic_ops = basic_alg.operations()
        self.assertEqual(len(basic_ops), 3)
    
    def test_binary_relation_algebra_two_elements(self):
        """Test building a GeneralAlgebra for binary relation algebra on a two element set."""
        # Universe: all binary relations on {0, 1}
        # A binary relation is a subset of {0,1} × {0,1}
        # There are 2^4 = 16 relations
        base_set = {0, 1}
        universe = []
        # Generate all relations (all subsets of the 4-element set of pairs)
        for i in range(16):
            relation = frozenset(
                (j // 2, j % 2) for j in range(4) if (i >> j) & 1
            )
            universe.append(relation)
        
        # Composition operation (binary): R ∘ S = {(a,c) | ∃b: (a,b) ∈ R and (b,c) ∈ S}
        def composition(args):
            R, S = args[0], args[1]
            return frozenset(
                (a, c) for a in base_set for c in base_set
                if any((a, b) in R and (b, c) in S for b in base_set)
            )
        
        # Union operation (binary)
        def union(args):
            R, S = args[0], args[1]
            return R | S
        
        # Intersection operation (binary)
        def intersection(args):
            R, S = args[0], args[1]
            return R & S
        
        # Complement operation (unary)
        def complement(args):
            R = args[0]
            full_relation = frozenset((a, b) for a in base_set for b in base_set)
            return full_relation - R
        
        # Transpose/Converse operation (unary): R^T = {(b,a) | (a,b) ∈ R}
        def transpose(args):
            R = args[0]
            return frozenset((b, a) for (a, b) in R)
        
        # Create operations using value_at (works with actual universe elements)
        composition_op = AbstractOperation.from_value_at_function("composition", 2, universe, composition)
        union_op = AbstractOperation.from_value_at_function("union", 2, universe, union)
        intersection_op = AbstractOperation.from_value_at_function("intersection", 2, universe, intersection)
        complement_op = AbstractOperation.from_value_at_function("complement", 1, universe, complement)
        transpose_op = AbstractOperation.from_value_at_function("transpose", 1, universe, transpose)
        
        # Create algebra
        alg = GeneralAlgebra("BinaryRelation2", universe, [
            composition_op, union_op, intersection_op, complement_op, transpose_op
        ])
        
        # Verify properties
        self.assertEqual(alg.name(), "BinaryRelation2")
        self.assertEqual(alg.cardinality(), 16)
        self.assertEqual(alg.operations_count(), 5)
        
        # Verify operations
        ops = alg.get_operations()
        self.assertEqual(len(ops), 5)
        
        # Find operations by arity
        binary_ops = [op for op in ops if op.arity() == 2]
        unary_ops = [op for op in ops if op.arity() == 1]
        self.assertEqual(len(binary_ops), 3)  # composition, union, intersection
        self.assertEqual(len(unary_ops), 2)  # complement, transpose
        
        # Define test relations
        # Identity relation: {(0,0), (1,1)}
        identity_relation = frozenset({(0, 0), (1, 1)})
        
        # Empty relation
        empty_relation = frozenset()
        
        # Full relation: all 4 pairs
        full_relation = frozenset((a, b) for a in base_set for b in base_set)
        
        # Simple relation {(0,1)}
        simple_relation = frozenset({(0, 1)})
        
        # Find composition operation: R ∘ I = R (for any R)
        composition_op_obj = None
        for op in binary_ops:
            result = op.value_at([simple_relation, identity_relation])
            if result == simple_relation:
                composition_op_obj = op
                break
        
        self.assertIsNotNone(composition_op_obj, "Could not identify composition operation")
        
        # Find transpose operation: transpose of {(0,1)} is {(1,0)}
        transpose_result_relation = frozenset({(1, 0)})
        transpose_op_obj = None
        for op in unary_ops:
            result = op.value_at([simple_relation])
            if result == transpose_result_relation:
                transpose_op_obj = op
                break
        
        self.assertIsNotNone(transpose_op_obj, "Could not identify transpose operation")
        
        # Find complement operation: complement of empty is full
        complement_op_obj = None
        for op in unary_ops:
            result = op.value_at([empty_relation])
            if result == full_relation:
                complement_op_obj = op
                break
        
        self.assertIsNotNone(complement_op_obj, "Could not identify complement operation")
        
        # Find union operation: empty ∪ R = R
        union_op_obj = None
        for op in binary_ops:
            # Check if this is not the composition operation we already found
            if composition_op_obj is None or op.value_at([simple_relation, identity_relation]) != simple_relation:
                result = op.value_at([empty_relation, simple_relation])
                if result == simple_relation:
                    union_op_obj = op
                    break
        
        self.assertIsNotNone(union_op_obj, "Could not identify union operation")
        
        # Find intersection operation: empty ∩ R = empty
        intersection_op_obj = None
        for op in binary_ops:
            # Check if this is neither composition nor union
            is_composition = composition_op_obj is not None and op.value_at([simple_relation, identity_relation]) == simple_relation
            is_union = union_op_obj is not None and op.value_at([empty_relation, simple_relation]) == simple_relation
            if not is_composition and not is_union:
                result = op.value_at([empty_relation, simple_relation])
                if result == empty_relation:
                    intersection_op_obj = op
                    break
        
        self.assertIsNotNone(intersection_op_obj, "Could not identify intersection operation")
        
        # Additional tests
        # Test transpose of transpose: (R^T)^T = R
        transposed = transpose_op_obj.value_at([simple_relation])
        self.assertEqual(transpose_op_obj.value_at([transposed]), simple_relation)
        
        # Test complement of complement: (R^c)^c = R
        complemented = complement_op_obj.value_at([simple_relation])
        self.assertEqual(complement_op_obj.value_at([complemented]), simple_relation)
        
        # Test composition with identity: R ∘ I = R
        self.assertEqual(composition_op_obj.value_at([simple_relation, identity_relation]), simple_relation)
        
        # Test union: R ∪ R = R (idempotent)
        self.assertEqual(union_op_obj.value_at([simple_relation, simple_relation]), simple_relation)
        
        # Test intersection: R ∩ R = R (idempotent)
        self.assertEqual(intersection_op_obj.value_at([simple_relation, simple_relation]), simple_relation)

        # Check that this algebra can be converted to a BasicAlgebra
        basic_alg = alg.to_basic_algebra()
        self.assertEqual(basic_alg.name(), "BinaryRelation2")
        self.assertEqual(basic_alg.cardinality(), 16)
        self.assertEqual(basic_alg.operations_count(), 5)
        
        # Check that the operations are the same
        basic_ops = basic_alg.operations()
        self.assertEqual(len(basic_ops), 5)

        
        # Check that this algebra can be converted to a BasicAlgebra
        basic_alg = alg.to_basic_algebra()
        self.assertEqual(basic_alg.name(), "BinaryRelation2")
        self.assertEqual(basic_alg.cardinality(), 16)
        self.assertEqual(basic_alg.operations_count(), 5)
        
        # Check that the operations are the same
        basic_ops = basic_alg.operations()
        self.assertEqual(len(basic_ops), 5)
    
if __name__ == '__main__':
    unittest.main()

