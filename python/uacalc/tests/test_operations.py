"""
Tests for Operations Python bindings.

These tests verify that the Python bindings work correctly
and provide the expected interface to the Rust implementation.
"""

import pytest
import subprocess
import json
import os
import sys
import platform
from pathlib import Path

# Add the project root to the path to import uacalc_lib
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import uacalc_lib
    Operations = uacalc_lib.alg.Operations
    OperationSymbol = uacalc_lib.alg.OperationSymbol
    SimilarityType = uacalc_lib.alg.SimilarityType
    BasicOperation = uacalc_lib.alg.BasicOperation
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    from test_utils import build_java_command
    
    wrapper_class = "java_wrapper.src.alg.op.OperationsWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=project_root
        )
        
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")
        
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Java wrapper output: {e}")


class TestOperations:
    """Test Operations Python bindings."""
    
    # =============================================================================
    # Property Testing Methods
    # =============================================================================
    
    def test_commutes(self):
        """Test commutes method."""
        # Create test operations
        unary_symbol = OperationSymbol("f", 1)
        unary_table = [1, 2, 0]
        unary_op = BasicOperation(unary_symbol, 3, unary_table)
        
        binary_symbol = OperationSymbol("g", 2)
        binary_table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        binary_op = BasicOperation(binary_symbol, 3, binary_table)
        
        result = Operations.commutes(unary_op, binary_op)
        
        java_result = run_java_wrapper("commutes", [
            "--type1", "unary", "--type2", "binary", "--setSize", "3"
        ])
        
        assert result == java_result["data"]["commutes"]
    
    def test_is_total(self):
        """Test isTotal method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op = BasicOperation(symbol, 3, table)
        
        result = Operations.is_total(op)
        
        java_result = run_java_wrapper("isTotal", [
            "--type", "binary", "--setSize", "3"
        ])
        
        assert result == java_result["data"]["isTotal"]
    
    def test_is_idempotent(self):
        """Test isIdempotent method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op = BasicOperation(symbol, 3, table)
        
        result = Operations.is_idempotent(op)
        
        java_result = run_java_wrapper("isIdempotent", [
            "--type", "binary", "--setSize", "3"
        ])
        
        assert result == java_result["data"]["isIdempotent"]
    
    def test_is_commutative(self):
        """Test isCommutative method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op = BasicOperation(symbol, 3, table)
        
        result = Operations.is_commutative(op)
        
        java_result = run_java_wrapper("isCommutative", [
            "--type", "binary", "--setSize", "3"
        ])
        
        assert result == java_result["data"]["isCommutative"]
    
    def test_is_totally_symmetric(self):
        """Test isTotallySymmetric method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op = BasicOperation(symbol, 3, table)
        
        result = Operations.is_totally_symmetric(op)
        
        java_result = run_java_wrapper("isTotallySymmetric", [
            "--type", "binary", "--setSize", "3"
        ])
        
        assert result == java_result["data"]["isTotallySymmetric"]
    
    def test_is_associative(self):
        """Test isAssociative method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op = BasicOperation(symbol, 3, table)
        
        result = Operations.is_associative(op)
        
        java_result = run_java_wrapper("isAssociative", [
            "--type", "binary", "--setSize", "3"
        ])
        
        assert result == java_result["data"]["isAssociative"]
    
    def test_is_maltsev(self):
        """Test isMaltsev method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op = BasicOperation(symbol, 3, table)
        
        result = Operations.is_maltsev(op)
        
        java_result = run_java_wrapper("isMaltsev", [
            "--type", "binary", "--setSize", "3"
        ])
        
        assert result == java_result["data"]["isMaltsev"]
    
    def test_find_difference(self):
        """Test findDifference method."""
        symbol1 = OperationSymbol("f", 2)
        table1 = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op1 = BasicOperation(symbol1, 3, table1)
        
        symbol2 = OperationSymbol("g", 2)
        table2 = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op2 = BasicOperation(symbol2, 3, table2)
        
        result = Operations.find_difference(op1, op2)
        
        java_result = run_java_wrapper("findDifference", [
            "--type1", "binary", "--type2", "binary", "--setSize", "3"
        ])
        
        if java_result["data"]["hasDifference"]:
            assert result is not None
        else:
            assert result is None
    
    def test_equal_values(self):
        """Test equalValues method."""
        symbol1 = OperationSymbol("f", 2)
        table1 = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op1 = BasicOperation(symbol1, 3, table1)
        
        symbol2 = OperationSymbol("g", 2)
        table2 = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op2 = BasicOperation(symbol2, 3, table2)
        
        result = Operations.equal_values(op1, op2)
        
        java_result = run_java_wrapper("equalValues", [
            "--type1", "binary", "--type2", "binary", "--setSize", "3"
        ])
        
        assert result == java_result["data"]["equalValues"]
    
    # =============================================================================
    # Factory Methods - Basic Operations
    # =============================================================================
    
    def test_make_int_operation(self):
        """Test makeIntOperation method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        
        op = Operations.make_int_operation(symbol, 3, table)
        
        java_result = run_java_wrapper("makeIntOperation", [
            "--name", "f", "--arity", "2", "--setSize", "3", 
            "--valueTable", "0,1,2,1,2,0,2,0,1"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["tableSize"] == len(table)
    
    def test_make_int_operation_str(self):
        """Test makeIntOperation with string symbol."""
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        
        op = Operations.make_int_operation("f", 2, 3, table)
        
        java_result = run_java_wrapper("makeIntOperationStr", [
            "--name", "f", "--arity", "2", "--setSize", "3", 
            "--valueTable", "0,1,2,1,2,0,2,0,1"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["tableSize"] == len(table)
    
    def test_make_binary_int_operation(self):
        """Test makeBinaryIntOperation method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        
        op = Operations.make_binary_int_operation(symbol, 3, table)
        
        java_result = run_java_wrapper("makeBinaryIntOperation", [
            "--name", "f", "--setSize", "3", 
            "--valueTable", "0,1,2,1,2,0,2,0,1"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["tableSize"] == len(table)
    
    def test_make_constant_int_operation(self):
        """Test makeConstantIntOperation method."""
        op = Operations.make_constant_int_operation(3, 1)
        
        java_result = run_java_wrapper("makeConstantIntOperation", [
            "--setSize", "3", "--elt", "1"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["constantValue"] == 1
    
    def test_make_constant_int_operation_with_prefix(self):
        """Test makeConstantIntOperation with prefix."""
        op = Operations.make_constant_int_operation("c", 3, 2)
        
        java_result = run_java_wrapper("makeConstantIntOperationWithPrefix", [
            "--prefix", "c", "--setSize", "3", "--elt", "2"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["constantValue"] == 2
        assert java_result["data"]["prefix"] == "c"
    
    def test_make_constant_int_operations(self):
        """Test makeConstantIntOperations method."""
        ops = Operations.make_constant_int_operations(3)
        
        java_result = run_java_wrapper("makeConstantIntOperations", [
            "--setSize", "3"
        ])
        
        assert len(ops) == java_result["data"]["operationCount"]
        assert java_result["data"]["setSize"] == 3
    
    def test_make_transposition(self):
        """Test makeTransposition method."""
        op = Operations.make_transposition(3, 0, 1)
        
        java_result = run_java_wrapper("makeTransposition", [
            "--setSize", "3", "--a0", "0", "--a1", "1"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["a0"] == 0
        assert java_result["data"]["a1"] == 1
    
    def test_make_full_cycle(self):
        """Test makeFullCycle method."""
        op = Operations.make_full_cycle(3)
        
        java_result = run_java_wrapper("makeFullCycle", [
            "--setSize", "3"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
    
    def test_make_int_operations(self):
        """Test makeIntOperations method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        base_op = BasicOperation(symbol, 3, table)
        
        ops = [base_op]
        int_ops = Operations.make_int_operations(ops)
        
        java_result = run_java_wrapper("makeIntOperations", [
            "--type", "binary", "--setSize", "3"
        ])
        
        assert len(int_ops) == java_result["data"]["intOpCount"]
        assert java_result["data"]["originalCount"] == len(ops)
    
    # =============================================================================
    # Factory Methods - Random Operations
    # =============================================================================
    
    def test_make_random_operation(self):
        """Test makeRandomOperation method."""
        symbol = OperationSymbol("f", 2)
        
        op = Operations.make_random_operation(3, symbol)
        
        java_result = run_java_wrapper("makeRandomOperation", [
            "--name", "f", "--arity", "2", "--setSize", "3"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
    
    def test_make_random_operation_with_seed(self):
        """Test makeRandomOperationWithSeed method."""
        symbol = OperationSymbol("f", 2)
        
        op = Operations.make_random_operation_with_seed(3, symbol, 12345)
        
        java_result = run_java_wrapper("makeRandomOperationWithRandom", [
            "--name", "f", "--arity", "2", "--setSize", "3", "--seed", "12345"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["seed"] == 12345
    
    def test_make_random_operations(self):
        """Test makeRandomOperations method."""
        symbols = [OperationSymbol("f", 2), OperationSymbol("g", 1)]
        sim_type = SimilarityType(symbols)
        
        ops = Operations.make_random_operations(3, sim_type)
        
        java_result = run_java_wrapper("makeRandomOperations", [
            "--setSize", "3"
        ])
        
        assert len(ops) == java_result["data"]["operationCount"]
        assert java_result["data"]["setSize"] == 3
    
    def test_make_random_operations_with_seed(self):
        """Test makeRandomOperationsWithSeed method."""
        symbols = [OperationSymbol("f", 2), OperationSymbol("g", 1)]
        sim_type = SimilarityType(symbols)
        
        ops = Operations.make_random_operations_with_seed(3, sim_type, 12345)
        
        java_result = run_java_wrapper("makeRandomOperationsWithSeed", [
            "--setSize", "3", "--seed", "12345"
        ])
        
        assert len(ops) == java_result["data"]["operationCount"]
        assert java_result["data"]["setSize"] == 3
        assert java_result["data"]["seed"] == 12345
    
    # =============================================================================
    # Factory Methods - Derived Operations
    # =============================================================================
    
    def test_make_derived_operation(self):
        """Test makeDerivedOperation method."""
        symbol = OperationSymbol("f", 3)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1, 1, 2, 0, 2, 0, 1, 0, 1, 2, 2, 0, 1, 0, 1, 2, 1, 2, 0]
        base_op = BasicOperation(symbol, 3, table)
        
        reduction_array = [0, 1, 0]
        op = Operations.make_derived_operation(base_op, reduction_array, 2)
        
        java_result = run_java_wrapper("makeDerivedOperation", [
            "--type", "binary", "--setSize", "3", 
            "--reductionArray", "0,1,0", "--newArity", "2"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["newArity"] == 2
    
    def test_ternary_discriminator(self):
        """Test ternaryDiscriminator method."""
        op = Operations.ternary_discriminator(3)
        
        java_result = run_java_wrapper("ternaryDiscriminator", [
            "--setSize", "3"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
    
    # =============================================================================
    # Special Operations
    # =============================================================================
    
    def test_make_jonsson_operations_from_nuf(self):
        """Test makeJonssonOperationsFromNUF method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        nuf = BasicOperation(symbol, 3, table)
        
        ops = Operations.make_jonsson_operations_from_nuf(nuf)
        
        java_result = run_java_wrapper("makeJonssonOperationsFromNUF", [
            "--type", "binary", "--setSize", "3"
        ])
        
        assert len(ops) == java_result["data"]["operationCount"]
        assert java_result["data"]["setSize"] == 3
    
    def test_make_left_shift(self):
        """Test makeLeftShift method."""
        op = Operations.make_left_shift(3, 2)
        
        java_result = run_java_wrapper("makeLeftShift", [
            "--vecSize", "3", "--rootSize", "2"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["vecSize"] == 3
        assert java_result["data"]["rootSize"] == 2
    
    def test_make_binary_left_shift(self):
        """Test makeBinaryLeftShift method."""
        op = Operations.make_binary_left_shift(3, 2)
        
        java_result = run_java_wrapper("makeBinaryLeftShift", [
            "--vecSize", "3", "--rootSize", "2"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["vecSize"] == 3
        assert java_result["data"]["rootSize"] == 2
    
    def test_make_matrix_diagonal_op(self):
        """Test makeMatrixDiagonalOp method."""
        op = Operations.make_matrix_diagonal_op(3, 2)
        
        java_result = run_java_wrapper("makeMatrixDiagonalOp", [
            "--vecSize", "3", "--rootSize", "2"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["vecSize"] == 3
        assert java_result["data"]["rootSize"] == 2
    
    def test_make_module_operation(self):
        """Test makeModuleOperation method."""
        coeffs = [1, 2, 1]
        op = Operations.make_module_operation(3, coeffs)
        
        java_result = run_java_wrapper("makeModuleOperation", [
            "--modulus", "3", "--coeffs", "1,2,1"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["modulus"] == 3
        assert java_result["data"]["coeffs"] == "[1, 2, 1]"
    
    def test_make_composition_op(self):
        """Test makeCompositionOp method."""
        op = Operations.make_composition_op(3, 2)
        
        java_result = run_java_wrapper("makeCompositionOp", [
            "--n", "3", "--pow", "2"
        ])
        
        assert op.symbol().name() == java_result["data"]["symbolName"]
        assert op.arity() == java_result["data"]["arity"]
        assert op.get_set_size() == java_result["data"]["setSize"]
        assert java_result["data"]["n"] == 3
        assert java_result["data"]["pow"] == 2
    
    # =============================================================================
    # Utility Methods
    # =============================================================================
    
    def test_make_map(self):
        """Test makeMap method."""
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op = BasicOperation(symbol, 3, table)
        
        ops = [op]
        op_map = Operations.make_map(ops)
        
        java_result = run_java_wrapper("makeMap", [
            "--type", "binary", "--setSize", "3"
        ])
        
        assert len(op_map) == java_result["data"]["mapSize"]
    
    def test_comprehensive_functionality(self):
        """Test comprehensive functionality."""
        java_result = run_java_wrapper("test", [])
        
        # Test property methods
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op = BasicOperation(symbol, 3, table)
        
        assert Operations.is_total(op) == java_result["data"]["isTotal"]
        assert Operations.is_idempotent(op) == java_result["data"]["isIdempotent"]
        assert Operations.is_commutative(op) == java_result["data"]["isCommutative"]
        assert Operations.is_associative(op) == java_result["data"]["isAssociative"]
        
        # Test factory methods
        int_op = Operations.make_int_operation(symbol, 3, table)
        assert int_op.arity() == java_result["data"]["intOpArity"]
        assert int_op.get_set_size() == java_result["data"]["intOpSetSize"]
        
        # Test random operations
        rand_op = Operations.make_random_operation(3, symbol)
        assert rand_op.arity() == java_result["data"]["randOpArity"]
        assert rand_op.get_set_size() == java_result["data"]["randOpSetSize"]
        
        # Test derived operations
        reduction = [0, 1, 0]
        derived_op = Operations.make_derived_operation(op, reduction, 2)
        assert derived_op.arity() == java_result["data"]["derivedOpArity"]
        assert derived_op.get_set_size() == java_result["data"]["derivedOpSetSize"]
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test invalid set size
        with pytest.raises(ValueError, match="Set size must be positive"):
            Operations.make_constant_int_operation(0, 1)
        
        # Test invalid default value
        with pytest.raises(ValueError, match="Default value.*is out of range"):
            Operations.make_constant_int_operation(3, 5)
        
        # Test invalid reduction array
        symbol = OperationSymbol("f", 2)
        table = [0, 1, 2, 1, 2, 0, 2, 0, 1]
        op = BasicOperation(symbol, 3, table)
        
        with pytest.raises(ValueError, match="reduction_array contains invalid index"):
            Operations.make_derived_operation(op, [0, 5], 2)
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Test nullary operation
        nullary_op = Operations.make_constant_int_operation(3, 0)
        assert nullary_op.arity() == 0
        assert nullary_op.get_set_size() == 3
        
        # Test unary operation
        unary_symbol = OperationSymbol("f", 1)
        unary_table = [1, 2, 0]
        unary_op = Operations.make_int_operation(unary_symbol, 3, unary_table)
        assert unary_op.arity() == 1
        assert unary_op.get_set_size() == 3
        
        # Test high arity operation
        high_arity_symbol = OperationSymbol("f", 4)
        high_arity_table = [0] * (3 ** 4)  # 3^4 = 81 entries
        high_arity_op = Operations.make_int_operation(high_arity_symbol, 3, high_arity_table)
        assert high_arity_op.arity() == 4
        assert high_arity_op.get_set_size() == 3
        
        # Test large set size
        large_set_op = Operations.make_constant_int_operation(10, 5)
        assert large_set_op.arity() == 0
        assert large_set_op.get_set_size() == 10


class TestOperationsEdgeCases:
    """Test Operations edge cases and error conditions."""
    
    def test_empty_similarity_type(self):
        """Test with empty similarity type."""
        symbols = []
        sim_type = SimilarityType(symbols)
        
        ops = Operations.make_random_operations(3, sim_type)
        assert len(ops) == 0
    
    def test_single_operation_similarity_type(self):
        """Test with single operation similarity type."""
        symbols = [OperationSymbol("f", 2)]
        sim_type = SimilarityType(symbols)
        
        ops = Operations.make_random_operations(3, sim_type)
        assert len(ops) == 1
        assert ops[0].symbol().name() == "f"
        assert ops[0].arity() == 2
    
    def test_mixed_arity_similarity_type(self):
        """Test with mixed arity similarity type."""
        symbols = [
            OperationSymbol("f", 0),  # nullary
            OperationSymbol("g", 1),  # unary
            OperationSymbol("h", 2),  # binary
            OperationSymbol("i", 3),  # ternary
        ]
        sim_type = SimilarityType(symbols)
        
        ops = Operations.make_random_operations(2, sim_type)
        assert len(ops) == 4
        
        # Check that each operation has the correct arity
        arities = [op.arity() for op in ops]
        assert 0 in arities
        assert 1 in arities
        assert 2 in arities
        assert 3 in arities
    
    def test_deterministic_random_operations(self):
        """Test that seeded random operations are deterministic."""
        symbols = [OperationSymbol("f", 2)]
        sim_type = SimilarityType(symbols)
        
        # Generate operations with the same seed
        ops1 = Operations.make_random_operations_with_seed(3, sim_type, 12345)
        ops2 = Operations.make_random_operations_with_seed(3, sim_type, 12345)
        
        assert len(ops1) == len(ops2)
        
        # Check that the operations are identical
        for op1, op2 in zip(ops1, ops2):
            assert op1.symbol().name() == op2.symbol().name()
            assert op1.arity() == op2.arity()
            assert op1.get_set_size() == op2.get_set_size()
            
            # Check that the tables are identical
            table1 = op1.get_table()
            table2 = op2.get_table()
            assert table1 == table2
    
    def test_different_seeds_produce_different_operations(self):
        """Test that different seeds produce different operations."""
        symbols = [OperationSymbol("f", 2)]
        sim_type = SimilarityType(symbols)
        
        # Generate operations with different seeds
        ops1 = Operations.make_random_operations_with_seed(3, sim_type, 12345)
        ops2 = Operations.make_random_operations_with_seed(3, sim_type, 54321)
        
        assert len(ops1) == len(ops2)
        
        # Check that the operations are different
        for op1, op2 in zip(ops1, ops2):
            assert op1.symbol().name() == op2.symbol().name()
            assert op1.arity() == op2.arity()
            assert op1.get_set_size() == op2.get_set_size()
            
            # Check that the tables are different
            table1 = op1.get_table()
            table2 = op2.get_table()
            assert table1 != table2
