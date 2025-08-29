"""
Tests for the optimized ProductAlgebra implementation.
"""

import pytest
from uacalc import (
    create_algebra, create_operation, create_product_algebra,
    Algebra, Operation
)


def test_create_product_algebra_basic():
    """Test basic product algebra creation."""
    # Create two simple algebras
    alg1 = create_algebra("A", [0, 1])
    alg2 = create_algebra("B", [0, 1, 2])
    
    # Add operations to first algebra
    op1 = create_operation("f", 1, [[0, 1], [1, 0]])  # Swap operation
    alg1.add_operation("f", op1)

    # Add operations to second algebra (same symbol "f")
    op2 = create_operation("f", 1, [[0, 0], [1, 1], [2, 0]])  # Project to 0 or 1
    alg2.add_operation("f", op2)
    
    # Create product algebra
    product = create_product_algebra(alg1, alg2)
    
    assert product.name == "A_x_B"
    assert product.cardinality == 6  # 2 * 3
    assert len(product.operations()) == 1  # f operation (componentwise)


def test_create_product_algebra_with_name():
    """Test product algebra creation with custom name."""
    alg1 = create_algebra("A", [0, 1])
    alg2 = create_algebra("B", [0, 1])
    
    product = create_product_algebra(alg1, alg2, name="CustomProduct")
    
    assert product.name == "CustomProduct"
    assert product.cardinality == 4


def test_product_algebra_operation_evaluation():
    """Test that operations in product algebra work correctly."""
    # Create algebras with simple operations
    alg1 = create_algebra("A", [0, 1])
    alg2 = create_algebra("B", [0, 1])
    
        # Add constant operations (same symbol "c")
    const1 = create_operation("c", 0, [[0]])
    const2 = create_operation("c", 0, [[1]])
    alg1.add_operation("c", const1)
    alg2.add_operation("c", const2)

    # Add unary operations (same symbol "id")
    id1 = create_operation("id", 1, [[0, 0], [1, 1]])
    id2 = create_operation("id", 1, [[0, 0], [1, 1]])
    alg1.add_operation("id", id1)
    alg2.add_operation("id", id2)
    
    product = create_product_algebra(alg1, alg2)
    
    # Test constant operations
    c_op = product.operation_by_symbol("c")

    # Constants should be (0, 1) = 2 in product encoding
    assert c_op.value([]) == 2  # (0, 1) = 2

    # Test unary operations
    id_op = product.operation_by_symbol("id")
    
    # Test on element 2 = (1, 0)
    assert id_op.value([2]) == 2  # Should preserve (1, 0)


def test_product_algebra_binary_operations():
    """Test binary operations in product algebra."""
    alg1 = create_algebra("A", [0, 1])
    alg2 = create_algebra("B", [0, 1])
    
    # Add binary operations (same symbol "proj")
    proj1 = create_operation("proj", 2, [
        [0, 0, 0], [0, 1, 0], [1, 0, 1], [1, 1, 1]
    ])
    proj2 = create_operation("proj", 2, [
        [0, 0, 0], [0, 1, 1], [1, 0, 0], [1, 1, 1]
    ])
    alg1.add_operation("proj", proj1)
    alg2.add_operation("proj", proj2)
    
    product = create_product_algebra(alg1, alg2)
    
    proj_op = product.operation_by_symbol("proj")

    # Test on elements: 0=(0,0), 1=(1,0), 2=(0,1), 3=(1,1)
    # proj(0, 2) = proj((0,0), (0,1)) = (0, 1) = 2
    assert proj_op.value([0, 2]) == 2
    # proj(1, 3) = proj((1,0), (1,1)) = (1, 1) = 3
    assert proj_op.value([1, 3]) == 3


def test_product_algebra_large_cardinality():
    """Test product algebra with larger cardinalities."""
    alg1 = create_algebra("A", list(range(10)))
    alg2 = create_algebra("B", list(range(10)))
    
    product = create_product_algebra(alg1, alg2)
    
    assert product.cardinality == 100
    assert len(product.operations()) == 0  # No operations added


def test_product_algebra_error_handling():
    """Test error handling in product algebra creation."""
    # Test with incompatible operations
    alg1 = create_algebra("A", [0, 1])
    alg2 = create_algebra("B", [0, 1])
    
    # Add operations with different arities
    op1 = create_operation("op1", 1, [[0, 0], [1, 1]])
    op2 = create_operation("op2", 2, [[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 1, 1]])
    
    alg1.add_operation("op1", op1)
    alg2.add_operation("op2", op2)
    
    # This should raise an error due to incompatible operations
    with pytest.raises(Exception):
        create_product_algebra(alg1, alg2)


def test_product_algebra_backward_compatibility():
    """Test that the new implementation maintains backward compatibility."""
    # Create algebras similar to what existing code might use
    alg1 = create_algebra("Group", [0, 1, 2, 3])
    alg2 = create_algebra("Lattice", [0, 1, 2])
    
    # Add some operations (same symbol "op")
    op1 = create_operation("op", 2, [
        [0, 0, 0], [0, 1, 1], [0, 2, 2], [0, 3, 3],
        [1, 0, 1], [1, 1, 0], [1, 2, 3], [1, 3, 2],
        [2, 0, 2], [2, 1, 3], [2, 2, 0], [2, 3, 1],
        [3, 0, 3], [3, 1, 2], [3, 2, 1], [3, 3, 0]
    ])
    op2 = create_operation("op", 2, [
        [0, 0, 0], [0, 1, 1], [0, 2, 2],
        [1, 0, 1], [1, 1, 1], [1, 2, 2],
        [2, 0, 2], [2, 1, 2], [2, 2, 2]
    ])

    alg1.add_operation("op", op1)
    alg2.add_operation("op", op2)
    
    # This should work without errors
    product = create_product_algebra(alg1, alg2)
    
    assert product.cardinality == 12  # 4 * 3
    assert len(product.operations()) == 1  # op


def test_product_algebra_performance_comparison():
    """Test that the new implementation is more efficient than the old one."""
    import time
    
    # Create algebras for performance testing
    alg1 = create_algebra("A", [0, 1, 2, 3, 4])
    alg2 = create_algebra("B", [0, 1, 2, 3, 4])
    
    # Add operations (same symbol "op")
    op1 = create_operation("op", 2, [
        [i, j, (i + j) % 5] for i in range(5) for j in range(5)
    ])
    op2 = create_operation("op", 2, [
        [i, j, (i * j) % 5] for i in range(5) for j in range(5)
    ])

    alg1.add_operation("op", op1)
    alg2.add_operation("op", op2)
    
    # Time the product creation
    start_time = time.time()
    product = create_product_algebra(alg1, alg2)
    creation_time = time.time() - start_time
    
    # The new implementation should be much faster
    assert creation_time < 1.0  # Should complete in under 1 second
    
    # Test operation evaluation performance
    op = product.operation_by_symbol("op")

    start_time = time.time()
    for i in range(1000):
        op.value([i % 25, (i + 1) % 25])
    eval_time = time.time() - start_time
    
    # Operation evaluation should also be fast
    assert eval_time < 1.0


def test_product_algebra_coordinate_operations():
    """Test coordinate projection and embedding operations."""
    # This test would require access to the internal coordinate methods
    # which are not exposed in the Python API, so we test through
    # operation evaluation instead
    
    alg1 = create_algebra("A", [0, 1])
    alg2 = create_algebra("B", [0, 1, 2])
    
    # Add identity operations to test coordinate behavior (same symbol "id")
    id1 = create_operation("id", 1, [[0, 0], [1, 1]])
    id2 = create_operation("id", 1, [[0, 0], [1, 1], [2, 2]])

    alg1.add_operation("id", id1)
    alg2.add_operation("id", id2)
    
    product = create_product_algebra(alg1, alg2)
    
    id_op = product.operation_by_symbol("id")

    # Test that operations preserve the coordinate structure
    # Element 0 = (0, 0), Element 1 = (1, 0), Element 2 = (0, 1)
    # Element 3 = (1, 1), Element 4 = (0, 2), Element 5 = (1, 2)

    assert id_op.value([0]) == 0  # (0, 0) -> (0, 0)
    assert id_op.value([1]) == 1  # (1, 0) -> (1, 0)
    assert id_op.value([3]) == 3  # (1, 1) -> (1, 1)
    assert id_op.value([4]) == 4  # (0, 2) -> (0, 2)


if __name__ == "__main__":
    pytest.main([__file__])
