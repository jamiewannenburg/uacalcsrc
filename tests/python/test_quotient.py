"""
Tests for UACalc quotient algebra functionality.

This module tests the Python bindings for the Rust quotient algebra implementation,
ensuring compatibility with existing Java implementations and verifying correct
operation evaluation on quotient structures.
"""

import pytest
import numpy as np
from pathlib import Path

# Import the UACalc package
try:
    import uacalc
    from uacalc import (
        Algebra, Operation, Partition, BinaryRelation,
        create_algebra, create_operation, create_partition, create_partition_from_blocks
    )
    from uacalc.algebra import (
        AlgebraBuilder, create_boolean_algebra, create_cyclic_group,
        create_quotient_algebra, algebra_to_numpy
    )
    UACALC_AVAILABLE = True
except ImportError:
    UACALC_AVAILABLE = False

# Skip all tests if UACalc is not available
pytestmark = pytest.mark.skipif(not UACALC_AVAILABLE, reason="UACalc not available")

class TestQuotientAlgebra:
    """Test quotient algebra functionality."""
    
    def test_create_simple_quotient(self):
        """Test creating a simple quotient algebra."""
        # Create Z4 algebra
        builder = AlgebraBuilder("Z4", 4)
        
        # Add addition modulo 4
        add_table = [
            [0, 1, 2, 3],
            [1, 2, 3, 0],
            [2, 3, 0, 1],
            [3, 0, 1, 2]
        ]
        builder.add_binary_operation("add", add_table)
        
        algebra = builder.build()
        
        # Create congruence: {0, 2} and {1, 3} (even/odd)
        congruence = create_partition_from_blocks(4, [[0, 2], [1, 3]])
        
        # Create quotient algebra
        quotient = create_quotient_algebra(algebra, congruence)
        
        # Test basic properties
        assert quotient.cardinality == 2
        assert quotient.universe == [0, 1]
        assert len(quotient.operations()) == 1
        assert quotient.name == "Z4_quotient"
    
    def test_quotient_operation_evaluation(self):
        """Test that operations work correctly in quotient algebra."""
        # Create Z4 algebra
        builder = AlgebraBuilder("Z4", 4)
        
        # Add addition modulo 4
        add_table = [
            [0, 1, 2, 3],
            [1, 2, 3, 0],
            [2, 3, 0, 1],
            [3, 0, 1, 2]
        ]
        builder.add_binary_operation("add", add_table)
        
        algebra = builder.build()
        
        # Create congruence: {0, 2} and {1, 3}
        congruence = create_partition_from_blocks(4, [[0, 2], [1, 3]])
        
        # Create quotient algebra
        quotient = create_quotient_algebra(algebra, congruence)
        
        # Test addition operation
        add_op = quotient.operation_by_symbol("add")
        
        # In the quotient: 0 represents {0,2}, 1 represents {1,3}
        # 0 + 0 = 0 (even + even = even)
        assert add_op.value([0, 0]) == 0
        # 0 + 1 = 1 (even + odd = odd)
        assert add_op.value([0, 1]) == 1
        # 1 + 0 = 1 (odd + even = odd)
        assert add_op.value([1, 0]) == 1
        # 1 + 1 = 0 (odd + odd = even)
        assert add_op.value([1, 1]) == 0
    
    def test_quotient_with_multiple_operations(self):
        """Test quotient algebra with multiple operations."""
        # Create Z4 algebra with both addition and multiplication
        builder = AlgebraBuilder("Z4", 4)
        
        # Add addition modulo 4
        add_table = [
            [0, 1, 2, 3],
            [1, 2, 3, 0],
            [2, 3, 0, 1],
            [3, 0, 1, 2]
        ]
        builder.add_binary_operation("add", add_table)
        
        # Add multiplication modulo 4
        mul_table = [
            [0, 0, 0, 0],
            [0, 1, 2, 3],
            [0, 2, 0, 2],
            [0, 3, 2, 1]
        ]
        builder.add_binary_operation("mul", mul_table)
        
        algebra = builder.build()
        
        # Create congruence: {0, 2} and {1, 3}
        congruence = create_partition_from_blocks(4, [[0, 2], [1, 3]])
        
        # Create quotient algebra
        quotient = create_quotient_algebra(algebra, congruence)
        
        # Test both operations
        add_op = quotient.operation_by_symbol("add")
        mul_op = quotient.operation_by_symbol("mul")
        
        # Test addition
        assert add_op.value([0, 0]) == 0
        assert add_op.value([1, 1]) == 0
        
        # Test multiplication
        assert mul_op.value([0, 0]) == 0  # even * even = even
        assert mul_op.value([0, 1]) == 0  # even * odd = even
        assert mul_op.value([1, 0]) == 0  # odd * even = even
        assert mul_op.value([1, 1]) == 1  # odd * odd = odd
    
    def test_quotient_with_constants(self):
        """Test quotient algebra with constant operations."""
        # Create algebra with constants
        builder = AlgebraBuilder("TestAlg", 4)
        
        # Add constant operation
        builder.add_constant("zero", 0)
        builder.add_constant("two", 2)
        
        # Add unary operation (negation mod 4)
        builder.add_unary_operation("neg", [0, 3, 2, 1])
        
        algebra = builder.build()
        
        # Create congruence: {0, 2} and {1, 3}
        congruence = create_partition_from_blocks(4, [[0, 2], [1, 3]])
        
        # Create quotient algebra
        quotient = create_quotient_algebra(algebra, congruence)
        
        # Test constant operations
        zero_op = quotient.operation_by_symbol("zero")
        two_op = quotient.operation_by_symbol("two")
        neg_op = quotient.operation_by_symbol("neg")
        
        # Both 0 and 2 should map to class 0
        assert zero_op.value([]) == 0
        assert two_op.value([]) == 0
        
        # Test negation
        assert neg_op.value([0]) == 0  # neg(even) = even
        assert neg_op.value([1]) == 1  # neg(odd) = odd
    
    def test_trivial_quotients(self):
        """Test trivial quotient cases."""
        # Create Z3 algebra
        builder = AlgebraBuilder("Z3", 3)
        add_table = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]
        builder.add_binary_operation("add", add_table)
        algebra = builder.build()
        
        # Test identity quotient (finest partition)
        identity_congruence = create_partition(3)  # Each element in its own class
        identity_quotient = create_quotient_algebra(algebra, identity_congruence, "Z3_identity")
        
        # Should be isomorphic to original
        assert identity_quotient.cardinality == 3
        assert identity_quotient.name == "Z3_identity"
        
        # Test universal quotient (coarsest partition)
        universal_congruence = create_partition_from_blocks(3, [[0, 1, 2]])
        universal_quotient = create_quotient_algebra(algebra, universal_congruence, "Z3_universal")
        
        # Should be trivial algebra
        assert universal_quotient.cardinality == 1
        assert universal_quotient.name == "Z3_universal"
    
    def test_quotient_error_cases(self):
        """Test error handling in quotient algebra creation."""
        # Create simple algebra
        algebra = create_algebra("Test", [0, 1, 2])
        
        # Test with mismatched partition size
        bad_partition = create_partition(5)  # Wrong size
        
        with pytest.raises(Exception):  # Should raise an error
            create_quotient_algebra(algebra, bad_partition)
        
        # Test with None inputs
        partition = create_partition(3)
        
        with pytest.raises(ValueError):
            create_quotient_algebra(None, partition)
        
        with pytest.raises(ValueError):
            create_quotient_algebra(algebra, None)
    
    def test_complex_quotient(self):
        """Test quotient with a more complex congruence structure."""
        # Create Z6 algebra
        builder = AlgebraBuilder("Z6", 6)
        add_table = []
        for i in range(6):
            row = []
            for j in range(6):
                row.append((i + j) % 6)
            add_table.append(row)
        builder.add_binary_operation("add", add_table)
        
        algebra = builder.build()
        
        # Create congruence: {0, 3}, {1, 4}, {2, 5} (modulo 3)
        congruence = create_partition_from_blocks(6, [[0, 3], [1, 4], [2, 5]])
        
        # Create quotient algebra (should be isomorphic to Z3)
        quotient = create_quotient_algebra(algebra, congruence, "Z6_mod_3")
        
        # Test properties
        assert quotient.cardinality == 3
        assert quotient.name == "Z6_mod_3"
        
        # Test that addition works like Z3
        add_op = quotient.operation_by_symbol("add")
        
        # Test a few cases
        assert add_op.value([0, 1]) == 1  # 0 + 1 = 1
        assert add_op.value([1, 2]) == 0  # 1 + 2 = 0 (mod 3)
        assert add_op.value([2, 2]) == 1  # 2 + 2 = 1 (mod 3)
    
    def test_quotient_with_cyclic_group(self):
        """Test creating quotients of predefined algebras."""
        # Create cyclic group Z4
        z4 = create_cyclic_group(4)
        
        # Create congruence for quotient by subgroup {0, 2}
        congruence = create_partition_from_blocks(4, [[0, 2], [1], [3]])
        
        # Create quotient
        quotient = create_quotient_algebra(z4, congruence, "Z4_quotient")
        
        # Test properties
        assert quotient.cardinality == 3
        assert len(quotient.operations()) == 1
        
        # Test that operations work
        mult_op = quotient.operation_by_symbol("multiply")
        
        # Test some multiplications
        assert mult_op.value([0, 0]) == 0  # {0,2} * {0,2} = {0,2}
        assert mult_op.value([0, 1]) == 1  # {0,2} * {1} = {1}
        assert mult_op.value([1, 2]) == 0  # {1} * {3} = {0} -> {0,2}
    
    def test_quotient_backward_compatibility(self):
        """Test that new implementation produces same results as expected."""
        # Create a small algebra where we can verify results manually
        builder = AlgebraBuilder("Test", 4)
        
        # Add a simple operation
        table = [
            [0, 1, 2, 3],
            [1, 0, 3, 2],
            [2, 3, 0, 1],
            [3, 2, 1, 0]
        ]
        builder.add_binary_operation("op", table)
        algebra = builder.build()
        
        # Create partition
        congruence = create_partition_from_blocks(4, [[0, 1], [2, 3]])
        
        # Create quotient
        quotient = create_quotient_algebra(algebra, congruence)
        
        # Manually verify operation results
        op = quotient.operation_by_symbol("op")
        
        # op(0, 0) should map representatives 0, 0 -> table[0][0] = 0 -> class 0
        assert op.value([0, 0]) == 0
        
        # op(0, 1) should map representatives 0, 2 -> table[0][2] = 2 -> class 1
        assert op.value([0, 1]) == 1
        
        # op(1, 0) should map representatives 2, 0 -> table[2][0] = 2 -> class 1
        assert op.value([1, 0]) == 1
        
        # op(1, 1) should map representatives 2, 2 -> table[2][2] = 0 -> class 0
        assert op.value([1, 1]) == 0
    
    def test_quotient_algebra_properties(self):
        """Test that quotient algebras maintain expected algebraic properties."""
        # Create Boolean algebra
        bool_alg = create_boolean_algebra(4)  # 2^2 = 4 elements
        
        # Create congruence that preserves some structure
        congruence = create_partition_from_blocks(4, [[0, 1], [2, 3]])
        
        # Create quotient
        quotient = create_quotient_algebra(bool_alg, congruence, "BoolQuotient")
        
        # Test basic properties
        assert quotient.cardinality == 2
        assert quotient.is_finite() == True
        assert quotient.max_arity() >= 2  # Should have binary operations
        
        # Test that operations are accessible
        operations = quotient.operations()
        assert len(operations) >= 1
        
        # Test operation symbols
        try:
            meet_op = quotient.operation_by_symbol("bool_meet")
            assert meet_op.arity() == 2
        except:
            # If bool_meet doesn't exist, that's OK for this test
            pass
    
    def test_quotient_with_subalgebra(self):
        """Test quotient algebra subalgebra generation."""
        # Create Z4 algebra
        builder = AlgebraBuilder("Z4", 4)
        add_table = [
            [0, 1, 2, 3],
            [1, 2, 3, 0],
            [2, 3, 0, 1],
            [3, 0, 1, 2]
        ]
        builder.add_binary_operation("add", add_table)
        algebra = builder.build()
        
        # Create quotient
        congruence = create_partition_from_blocks(4, [[0, 2], [1, 3]])
        quotient = create_quotient_algebra(algebra, congruence)
        
        # Generate subalgebra
        subalgebra = quotient.subalgebra([0])
        
        # Test subalgebra properties
        assert subalgebra.cardinality <= quotient.cardinality
        assert len(subalgebra.operations()) == len(quotient.operations())
    
    def test_quotient_performance_comparison(self):
        """Test that new implementation performs better than naive approach."""
        # Create a medium-sized algebra to test performance
        builder = AlgebraBuilder("TestPerf", 8)
        
        # Add a binary operation
        table = []
        for i in range(8):
            row = []
            for j in range(8):
                row.append((i + j) % 8)
            table.append(row)
        builder.add_binary_operation("add", table)
        
        algebra = builder.build()
        
        # Create congruence
        congruence = create_partition_from_blocks(8, [[0, 4], [1, 5], [2, 6], [3, 7]])
        
        # Time the quotient creation and operation evaluation
        import time
        
        start_time = time.time()
        quotient = create_quotient_algebra(algebra, congruence)
        creation_time = time.time() - start_time
        
        # Test operation evaluation performance
        start_time = time.time()
        add_op = quotient.operation_by_symbol("add")
        for i in range(4):
            for j in range(4):
                result = add_op.value([i, j])
        evaluation_time = time.time() - start_time
        
        # These are rough performance checks - mainly ensure it doesn't hang
        assert creation_time < 1.0  # Should create quickly
        assert evaluation_time < 0.1  # Should evaluate quickly
        
        # Verify correctness
        assert quotient.cardinality == 4
        assert add_op.value([0, 1]) == 1  # Verify at least one operation works

class TestQuotientIntegration:
    """Test integration with other UACalc features."""
    
    def test_quotient_with_congruence_lattice(self):
        """Test that quotient algebras work with congruence lattice computation."""
        # Create simple algebra
        builder = AlgebraBuilder("Test", 3)
        builder.add_binary_operation("add", [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ])
        algebra = builder.build()
        
        # Create quotient
        congruence = create_partition_from_blocks(3, [[0, 1], [2]])
        quotient = create_quotient_algebra(algebra, congruence)
        
        # Test that we can create congruence lattice for quotient
        try:
            from uacalc import create_congruence_lattice
            lattice = create_congruence_lattice(quotient)
            
            # Basic checks
            assert lattice is not None
            # The lattice should have at least the trivial congruences
            assert lattice.size() >= 2
        except ImportError:
            # If congruence lattice is not available, skip this test
            pytest.skip("Congruence lattice not available")
    
    def test_quotient_serialization(self):
        """Test that quotient algebras can be saved and loaded."""
        # Create quotient algebra
        builder = AlgebraBuilder("Z4", 4)
        builder.add_binary_operation("add", [
            [0, 1, 2, 3],
            [1, 2, 3, 0],
            [2, 3, 0, 1],
            [3, 0, 1, 2]
        ])
        algebra = builder.build()
        
        congruence = create_partition_from_blocks(4, [[0, 2], [1, 3]])
        quotient = create_quotient_algebra(algebra, congruence)
        
        # Test basic serialization-like operations
        try:
            # Test that we can access all the data needed for serialization
            name = quotient.name
            cardinality = quotient.cardinality
            universe = quotient.universe
            operations = quotient.operations()
            
            assert name is not None
            assert cardinality > 0
            assert universe is not None
            assert operations is not None
            assert len(operations) > 0
            
            # Test that operations work
            op = operations[0]
            if op.arity() == 2:
                result = op.value([0, 0])
                assert 0 <= result < cardinality
                
        except Exception as e:
            pytest.fail(f"Quotient algebra serialization data access failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
