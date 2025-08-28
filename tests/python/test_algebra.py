"""
Tests for UACalc algebra functionality.

This module tests the Python bindings for the Rust core library,
ensuring compatibility with existing Java implementations.
"""

import pytest
import numpy as np
from pathlib import Path

# Import the UACalc package
try:
    import uacalc
    from uacalc import (
        Algebra, Operation, Partition, BinaryRelation,
        create_algebra, create_operation, create_partition, create_binary_relation,
        load_algebra, save_algebra
    )
    from uacalc.algebra import (
        AlgebraBuilder, create_boolean_algebra, create_cyclic_group,
        create_symmetric_group, create_product_algebra, algebra_to_numpy
    )
    UACALC_AVAILABLE = True
except ImportError:
    UACALC_AVAILABLE = False

# Skip all tests if UACalc is not available
pytestmark = pytest.mark.skipif(not UACALC_AVAILABLE, reason="UACalc not available")

class TestAlgebra:
    """Test basic algebra functionality."""
    
    def test_create_algebra(self):
        """Test creating a basic algebra."""
        algebra = create_algebra("TestAlgebra", [0, 1, 2])
        
        assert algebra.name == "TestAlgebra"
        assert algebra.cardinality == 3
        assert list(algebra.universe) == [0, 1, 2]
        assert len(algebra.operations()) == 0
    
    def test_add_operation(self):
        """Test adding operations to an algebra."""
        algebra = create_algebra("TestAlgebra", [0, 1, 2])
        
        # Create a binary operation
        table = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]
        operation = create_operation("multiply", 2, table)
        
        algebra.add_operation("multiply", operation)
        
        assert len(algebra.operations()) == 1
        assert algebra.operation(0).symbol == "multiply"
        assert algebra.operation_by_symbol("multiply").symbol == "multiply"
    
    def test_operation_value(self):
        """Test computing operation values."""
        algebra = create_algebra("TestAlgebra", [0, 1, 2])
        
        # Create a binary operation
        table = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]
        operation = create_operation("multiply", 2, table)
        
        # Test operation values
        assert operation.value([0, 0]) == 0
        assert operation.value([0, 1]) == 1
        assert operation.value([1, 2]) == 0
        assert operation.value([2, 1]) == 0
    
    def test_operation_properties(self):
        """Test operation property methods."""
        algebra = create_algebra("TestAlgebra", [0, 1, 2])
        
        # Create an identity operation
        table = [[0], [1], [2]]
        identity_op = create_operation("identity", 1, table)
        
        assert identity_op.arity() == 1
        assert identity_op.symbol == "identity"
        assert identity_op.operation_type() == "unary"
    
    def test_algebra_properties(self):
        """Test algebra property methods."""
        algebra = create_algebra("TestAlgebra", [0, 1, 2])
        
        # Add a binary operation
        table = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]
        operation = create_operation("multiply", 2, table)
        algebra.add_operation("multiply", operation)
        
        assert algebra.is_finite() == True
        assert algebra.max_arity() == 2

class TestPartition:
    """Test partition functionality."""
    
    def test_create_partition(self):
        """Test creating a partition."""
        partition = create_partition(4)
        
        assert partition.size == 4
        assert partition.num_blocks == 4  # Initially all elements in separate blocks
    
    def test_partition_union(self):
        """Test union operations on partitions."""
        partition = create_partition(4)
        
        # Union elements 0 and 1
        partition.union(0, 1)
        
        assert partition.num_blocks == 3
        assert partition.same_block(0, 1) == True
        assert partition.same_block(0, 2) == False
    
    def test_partition_blocks(self):
        """Test getting blocks from partitions."""
        partition = create_partition(4)
        partition.union(0, 1)
        partition.union(2, 3)
        
        blocks = partition.blocks()
        assert len(blocks) == 2
        
        # Check that blocks contain the right elements
        block_sizes = [len(block) for block in blocks]
        assert sorted(block_sizes) == [2, 2]
    
    def test_partition_join_meet(self):
        """Test join and meet operations on partitions."""
        # Create two partitions
        p1 = create_partition(4)
        p1.union(0, 1)
        
        p2 = create_partition(4)
        p2.union(1, 2)
        
        join = p1.join(p2)
        assert join.num_blocks == 2  # Elements 0,1,2 in one block, element 3 in another
        assert join.same_block(0, 1) == True
        assert join.same_block(0, 2) == True
        assert join.same_block(1, 2) == True
        assert join.same_block(0, 3) == False
        # Test meet
        meet = p1.meet(p2)
        assert meet.num_blocks == 4  # All elements should be in separate blocks
        assert meet.same_block(0, 1) == False
        assert meet.same_block(0, 2) == False
        assert meet.same_block(1, 2) == False
        assert meet.same_block(0, 3) == False

class TestBinaryRelation:
    """Test binary relation functionality."""
    
    def test_create_binary_relation(self):
        """Test creating a binary relation."""
        relation = create_binary_relation(3)
        
        assert relation.size == 3
        assert len(relation.pairs()) == 0  # Initially empty
    
    def test_relation_operations(self):
        """Test basic relation operations."""
        relation = create_binary_relation(3)
        
        # Add some pairs
        relation.add(0, 1)
        relation.add(1, 2)
        
        assert relation.contains(0, 1) == True
        assert relation.contains(1, 2) == True
        assert relation.contains(0, 2) == False
        
        # Remove a pair
        relation.remove(0, 1)
        assert relation.contains(0, 1) == False
    
    def test_relation_closures(self):
        """Test relation closure operations."""
        relation = create_binary_relation(3)
        relation.add(0, 1)
        relation.add(1, 2)
        
        # Test reflexive closure
        reflexive = relation.reflexive_closure()
        assert reflexive.contains(0, 0) == True
        assert reflexive.contains(1, 1) == True
        assert reflexive.contains(2, 2) == True
        
        # Test transitive closure
        transitive = relation.transitive_closure()
        assert transitive.contains(0, 2) == True  # 0 -> 1 -> 2
    
    def test_relation_properties(self):
        """Test relation property checks."""
        relation = create_binary_relation(3)
        
        # Test reflexive
        assert relation.is_reflexive() == False
        relation.add(0, 0)
        relation.add(1, 1)
        relation.add(2, 2)
        assert relation.is_reflexive() == True
        
        # Test symmetric
        relation.add(0, 1)
        assert relation.is_symmetric() == False
        relation.add(1, 0)
        assert relation.is_symmetric() == True

class TestAlgebraBuilder:
    """Test the algebra builder utility."""
    
    def test_algebra_builder(self):
        """Test building an algebra with the builder pattern."""
        builder = AlgebraBuilder("TestAlgebra", 3)
        
        # Add a constant
        builder.add_constant("zero", 0)
        
        # Add a unary operation
        builder.add_unary_operation("neg", [0, 2, 1])
        
        # Add a binary operation
        table = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]
        builder.add_binary_operation("add", table)
        
        algebra = builder.build()
        
        assert algebra.name == "TestAlgebra"
        assert algebra.cardinality == 3
        assert len(algebra.operations()) == 3

class TestPredefinedAlgebras:
    """Test predefined algebra constructors."""
    
    def test_boolean_algebra(self):
        """Test creating a Boolean algebra."""
        algebra = create_boolean_algebra(2)
        
        assert algebra.cardinality == 2
        assert len(algebra.operations()) == 3  # meet, join, complement
        
        # Test meet operation (AND)
        meet_op = algebra.operation_by_symbol("bool_meet")
        assert meet_op.value([0, 0]) == 0
        assert meet_op.value([0, 1]) == 0
        assert meet_op.value([1, 0]) == 0
        assert meet_op.value([1, 1]) == 1
    
    def test_cyclic_group(self):
        """Test creating a cyclic group."""
        algebra = create_cyclic_group(3)
        
        assert algebra.cardinality == 3
        assert len(algebra.operations()) == 1  # multiply
        
        # Test multiplication
        mult_op = algebra.operation_by_symbol("multiply")
        assert mult_op.value([0, 0]) == 0
        assert mult_op.value([1, 2]) == 0  # (1 + 2) mod 3 = 0
        assert mult_op.value([2, 2]) == 1  # (2 + 2) mod 3 = 1
    
    def test_symmetric_group(self):
        """Test creating a symmetric group."""
        algebra = create_symmetric_group(2)
        
        assert algebra.cardinality == 2  # S_2 has 2 elements
        assert len(algebra.operations()) == 1  # compose

class TestIO:
    """Test I/O functionality."""
    
    def test_save_and_load_algebra(self, tmp_path):
        """Test saving and loading an algebra."""
        # Create a simple algebra
        algebra = create_algebra("TestAlgebra", [0, 1, 2])
        
        # Add an operation
        table = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]
        operation = create_operation("multiply", 2, table)
        algebra.add_operation("multiply", operation)
        
        # Save to file
        file_path = tmp_path / "test.ua"
        save_algebra(algebra, file_path)
        
        # Load from file
        loaded_algebra = load_algebra(file_path)
        
        assert loaded_algebra.name == algebra.name
        assert loaded_algebra.cardinality == algebra.cardinality
        assert len(loaded_algebra.operations()) == len(algebra.operations())

class TestNumPyIntegration:
    """Test NumPy integration."""
    
    def test_algebra_to_numpy(self):
        """Test converting algebra to NumPy arrays."""
        algebra = create_algebra("TestAlgebra", [0, 1, 2])
        
        # Add a binary operation
        table = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]
        operation = create_operation("multiply", 2, table)
        algebra.add_operation("multiply", operation)
        
        # Convert to NumPy
        np_arrays = algebra_to_numpy(algebra)
        
        assert "multiply" in np_arrays
        assert isinstance(np_arrays["multiply"], np.ndarray)
        assert np_arrays["multiply"].shape == (3, 3)
        
        # Test that the values match
        assert np_arrays["multiply"][0, 1] == 1
        assert np_arrays["multiply"][1, 2] == 0

class TestCompatibility:
    """Test compatibility with existing Java implementations."""
    
    def test_load_existing_ua_files(self):
        """Test loading existing .ua files from the resources directory."""
        resources_dir = Path(__file__).parent.parent.parent / "resources" / "algebras"
        
        if not resources_dir.exists():
            pytest.skip("Resources directory not found")
        
        # Try to load some existing .ua files
        ua_files = list(resources_dir.glob("*.ua"))
        
        if not ua_files:
            pytest.skip("No .ua files found in resources directory")
        
        # Test loading the first few files
        for ua_file in ua_files[:3]:  # Limit to first 3 files
            try:
                algebra = load_algebra(ua_file)
                assert algebra is not None
                assert algebra.cardinality > 0
                print(f"Successfully loaded {ua_file.name}")
            except Exception as e:
                pytest.fail(f"Failed to load {ua_file.name}: {e}")

if __name__ == "__main__":
    pytest.main([__file__])

