"""Tests to debug ProductOperation component ordering issue"""

import pytest
import uacalc_lib

Horner = uacalc_lib.util.Horner
BasicAlgebra = uacalc_lib.alg.BasicAlgebra
IntOperation = uacalc_lib.alg.IntOperation
PowerAlgebra = uacalc_lib.alg.PowerAlgebra


def test_power_algebra_join_idempotency():
    """Test that join is idempotent in power algebra"""
    # Create 2-element boolean algebra
    universe = [0, 1]
    join_table = [
        [0, 1],
        [1, 1],
    ]
    
    def join_func(args):
        i, j = args[0], args[1]
        return join_table[i][j]
    
    join_op = IntOperation.from_int_value_at("join", 2, 2, join_func)
    ba2 = BasicAlgebra("DistributiveLattice2", universe, [join_op])
    
    # Create power algebra with n=2
    power_alg = PowerAlgebra(ba2, 2)
    power_basic_alg = power_alg.to_basic_algebra()
    
    # Get join operation
    operations = power_basic_alg.operations()
    join_op_power = None
    for op in operations:
        if op.symbol().name() == "join":
            join_op_power = op
            break
    
    assert join_op_power is not None, "Join operation not found"
    
    # Test idempotency: join(x, x) should equal x
    print("\nTesting idempotency:")
    for i in range(power_basic_alg.cardinality()):
        result = join_op_power.int_value_at([i, i])
        status = "✓" if result == i else "✗"
        print(f"  join({i}, {i}) = {result} {status}")
        assert result == i, f"join({i}, {i}) should equal {i}, but got {result}"


def test_horner_encoding_decoding():
    """Test that horner and horner_inv are inverses"""
    sizes = [2, 2]
    
    print("\nTesting Horner encoding/decoding:")
    for k in range(4):
        decoded = Horner.horner_inv(k, sizes)
        encoded = Horner.horner(decoded, sizes)
        status = "✓" if encoded == k else "✗"
        print(f"  {k} -> {decoded} -> {encoded} {status}")
        assert encoded == k, f"Encoding/decoding mismatch: {k} -> {decoded} -> {encoded}"


def test_component_extraction():
    """Test what components we get when decoding element 1"""
    sizes = [2, 2]
    element_1 = 1
    decoded = Horner.horner_inv(element_1, sizes)
    
    print(f"\nElement 1 decodes to: {decoded}")
    assert decoded == [1, 0], f"Element 1 should decode to [1, 0], got {decoded}"
    
    # When we compute join(1, 1), we should get:
    # - Component 0: join(1, 1) = 1
    # - Component 1: join(0, 0) = 0
    # Result should be [1, 0] which encodes to 1
    result_components = [1, 0]
    encoded_result = Horner.horner(result_components, sizes)
    print(f"Result {result_components} encodes to: {encoded_result}")
    assert encoded_result == 1, f"Result {result_components} should encode to 1, got {encoded_result}"


def test_manual_computation():
    """Manually trace through what should happen for join(1, 1)"""
    sizes = [2, 2]
    
    # Decode element 1
    args_expanded_0 = Horner.horner_inv(1, sizes)  # [1, 0]
    args_expanded_1 = Horner.horner_inv(1, sizes)  # [1, 0]
    
    print(f"\nManual computation for join(1, 1):")
    print(f"  args_expanded[0] = {args_expanded_0}")
    print(f"  args_expanded[1] = {args_expanded_1}")
    
    # Join table: join(0,0)=0, join(0,1)=1, join(1,0)=1, join(1,1)=1
    def join_table(i, j):
        if i == 0 and j == 0:
            return 0
        elif i == 0 and j == 1:
            return 1
        elif i == 1 and j == 0:
            return 1
        else:  # i == 1 and j == 1
            return 1
    
    # When iterating in reverse (i = 1, then i = 0):
    # i = 1 (most significant, second algebra):
    #   component_args = [args_expanded[0][1], args_expanded[1][1]] = [0, 0]
    #   result = join(0, 0) = 0
    #   ans = sizes[1] * 0 + 0 = 2 * 0 + 0 = 0
    i = 1
    comp_args_i1 = [args_expanded_0[i], args_expanded_1[i]]
    result_i1 = join_table(comp_args_i1[0], comp_args_i1[1])
    ans = sizes[i] * 0 + result_i1
    print(f"  i={i}: component_args={comp_args_i1}, result={result_i1}, ans={ans}")
    
    # i = 0 (least significant, first algebra):
    #   component_args = [args_expanded[0][0], args_expanded[1][0]] = [1, 1]
    #   result = join(1, 1) = 1
    #   ans = sizes[0] * 0 + 1 = 2 * 0 + 1 = 1
    i = 0
    comp_args_i0 = [args_expanded_0[i], args_expanded_1[i]]
    result_i0 = join_table(comp_args_i0[0], comp_args_i0[1])
    ans = sizes[i] * ans + result_i0
    print(f"  i={i}: component_args={comp_args_i0}, result={result_i0}, ans={ans}")
    
    assert ans == 1, f"join(1, 1) should equal 1, but got {ans}"


def test_all_join_operations():
    """Test all join operations in the power algebra"""
    universe = [0, 1]
    join_table = [
        [0, 1],
        [1, 1],
    ]
    
    def join_func(args):
        i, j = args[0], args[1]
        return join_table[i][j]
    
    join_op = IntOperation.from_int_value_at("join", 2, 2, join_func)
    ba2 = BasicAlgebra("DistributiveLattice2", universe, [join_op])
    power_alg = PowerAlgebra(ba2, 2)
    power_basic_alg = power_alg.to_basic_algebra()
    
    operations = power_basic_alg.operations()
    join_op_power = None
    for op in operations:
        if op.symbol().name() == "join":
            join_op_power = op
            break
    
    assert join_op_power is not None
    
    print("\nFull join operation table:")
    cardinality = power_basic_alg.cardinality()
    for i in range(cardinality):
        print(f"{i}: ", end="")
        for j in range(cardinality):
            result = join_op_power.int_value_at([i, j])
            print(f"{result} ", end="")
        print()
    
    # Expected results based on componentwise join:
    # Element 0 = [0, 0], Element 1 = [1, 0], Element 2 = [0, 1], Element 3 = [1, 1]
    # join(0, 0) = join([0,0], [0,0]) = [join(0,0), join(0,0)] = [0, 0] = 0
    # join(1, 1) = join([1,0], [1,0]) = [join(1,1), join(0,0)] = [1, 0] = 1
    # join(2, 2) = join([0,1], [0,1]) = [join(0,0), join(1,1)] = [0, 1] = 2
    # join(3, 3) = join([1,1], [1,1]) = [join(1,1), join(1,1)] = [1, 1] = 3
    
    expected = {
        (0, 0): 0,
        (1, 1): 1,
        (2, 2): 2,
        (3, 3): 3,
    }
    
    print("\nChecking idempotency:")
    for (i, j), expected_result in expected.items():
        actual = join_op_power.int_value_at([i, j])
        status = "✓" if actual == expected_result else "✗"
        print(f"  join({i}, {j}) = {actual} (expected {expected_result}) {status}")
        assert actual == expected_result, f"join({i}, {j}) should equal {expected_result}, got {actual}"


# Tests can be run with pytest:
# pytest python/uacalc/tests/test_product_operation_ordering.py -v

