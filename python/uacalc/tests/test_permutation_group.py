"""
Tests for PermutationGroup Python bindings.
"""

import pytest
import uacalc_lib


class TestPermutationGroup:
    """Test cases for PermutationGroup Python bindings."""

    def test_permutation_group_creation(self):
        """Test basic PermutationGroup creation."""
        generators = [[1, 2, 0], [2, 0, 1]]
        pg = uacalc_lib.group.PermutationGroup("TestGroup", generators)
        
        assert pg.get_name() == "TestGroup"
        assert pg.get_generators() == generators
        assert pg.get_underlying_set_size() == 3

    def test_permutation_group_with_universe(self):
        """Test PermutationGroup creation with universe."""
        generators = [[1, 2, 0], [2, 0, 1]]
        universe = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
        pg = uacalc_lib.group.PermutationGroup.new_with_universe("TestGroup", generators, universe)
        
        assert pg.get_name() == "TestGroup"
        assert pg.get_generators() == generators
        assert pg.get_universe_list() == universe
        assert pg.get_underlying_set_size() == 3

    def test_permutation_group_safe_creation(self):
        """Test safe PermutationGroup creation."""
        generators = [[1, 2, 0], [2, 0, 1]]
        pg = uacalc_lib.group.PermutationGroup.new_safe("TestGroup", generators)
        
        assert pg.get_name() == "TestGroup"
        assert pg.get_generators() == generators
        assert pg.get_underlying_set_size() == 3

    def test_permutation_group_safe_with_universe(self):
        """Test safe PermutationGroup creation with universe."""
        generators = [[1, 2, 0], [2, 0, 1]]
        universe = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
        pg = uacalc_lib.group.PermutationGroup.new_with_universe_safe("TestGroup", generators, universe)
        
        assert pg.get_name() == "TestGroup"
        assert pg.get_generators() == generators
        assert pg.get_universe_list() == universe
        assert pg.get_underlying_set_size() == 3

    def test_permutation_product(self):
        """Test permutation product operation."""
        p1 = [1, 2, 0]
        p2 = [2, 0, 1]
        result = uacalc_lib.group.PermutationGroup.prod(p1, p2)
        
        # Expected: p1 * p2 = [1, 2, 0] * [2, 0, 1] = [0, 1, 2]
        assert result == [0, 1, 2]

    def test_permutation_inverse(self):
        """Test permutation inverse operation."""
        p = [1, 2, 0]
        result = uacalc_lib.group.PermutationGroup.inv(p)
        
        # Expected: inv([1, 2, 0]) = [2, 0, 1]
        assert result == [2, 0, 1]

    def test_permutation_identity(self):
        """Test permutation identity operation."""
        result = uacalc_lib.group.PermutationGroup.id(3)
        
        # Expected: id(3) = [0, 1, 2]
        assert result == [0, 1, 2]

    def test_permutation_group_identity(self):
        """Test that PermutationGroup has correct identity."""
        generators = [[1, 2, 0], [2, 0, 1]]
        pg = uacalc_lib.group.PermutationGroup("TestGroup", generators)
        
        identity = pg.get_identity()
        assert identity is not None
        assert identity == [0, 1, 2]

    def test_permutation_group_string_representation(self):
        """Test string representation of PermutationGroup."""
        generators = [[1, 2, 0], [2, 0, 1]]
        pg = uacalc_lib.group.PermutationGroup("TestGroup", generators)
        
        str_repr = str(pg)
        assert "TestGroup" in str_repr
        
        repr_str = repr(pg)
        assert "PermutationGroup(TestGroup)" == repr_str

    def test_permutation_group_validation(self):
        """Test that PermutationGroup validates input correctly."""
        # Test with empty generators
        with pytest.raises(Exception):
            uacalc_lib.group.PermutationGroup.new_safe("TestGroup", [])
        
        # Test with mismatched generator sizes
        with pytest.raises(Exception):
            uacalc_lib.group.PermutationGroup.new_safe("TestGroup", [[1, 2, 0], [1, 2]])

    def test_permutation_operations_validation(self):
        """Test that permutation operations validate input correctly."""
        # Test with invalid permutation - mismatched sizes should raise an exception
        with pytest.raises(Exception):
            uacalc_lib.group.PermutationGroup.prod([1, 2], [1, 2, 0])
        
        # Test with invalid permutation for inverse - should raise an exception
        with pytest.raises(Exception):
            uacalc_lib.group.PermutationGroup.inv([1, 2])

    def test_permutation_group_complex_operations(self):
        """Test complex permutation operations."""
        # Test product of multiple permutations
        p1 = [1, 2, 0]
        p2 = [2, 0, 1]
        p3 = [0, 1, 2]
        
        # (p1 * p2) * p3
        result1 = uacalc_lib.group.PermutationGroup.prod(p1, p2)
        result2 = uacalc_lib.group.PermutationGroup.prod(result1, p3)
        
        # p1 * (p2 * p3)
        result3 = uacalc_lib.group.PermutationGroup.prod(p2, p3)
        result4 = uacalc_lib.group.PermutationGroup.prod(p1, result3)
        
        # Should be associative
        assert result2 == result4

    def test_permutation_group_inverse_property(self):
        """Test that p * inv(p) = identity."""
        p = [1, 2, 0]
        inv_p = uacalc_lib.group.PermutationGroup.inv(p)
        identity = uacalc_lib.group.PermutationGroup.id(3)
        
        # p * inv(p) should equal identity
        result = uacalc_lib.group.PermutationGroup.prod(p, inv_p)
        assert result == identity

    def test_permutation_group_identity_property(self):
        """Test that p * identity = p."""
        p = [1, 2, 0]
        identity = uacalc_lib.group.PermutationGroup.id(3)
        
        # p * identity should equal p
        result = uacalc_lib.group.PermutationGroup.prod(p, identity)
        assert result == p

    def test_automorphism_group_trivial(self):
        """Test automorphism group of a trivial algebra (no operations)."""
        # Create a trivial algebra with no operations
        universe = [0, 1, 2]
        alg = uacalc_lib.alg.BasicAlgebra("Trivial", universe, None)
        
        # Compute automorphism group
        aut_group = uacalc_lib.group.PermutationGroup.automorphism_group(alg)
        
        # For a set with no operations, all permutations are automorphisms
        # So we should have 3! = 6 automorphisms
        assert aut_group.get_underlying_set_size() == 3
        assert len(aut_group.get_generators()) == 6

    def test_automorphism_group_with_operation(self):
        """Test automorphism group of an algebra with operations."""
        # Create an algebra with a constant operation
        universe = [0, 1]
        const_op = uacalc_lib.alg.Operations.make_constant_int_operation(2, 0)
        alg = uacalc_lib.alg.BasicAlgebra("ConstAlg", universe, [const_op])
        
        # Compute automorphism group
        aut_group = uacalc_lib.group.PermutationGroup.automorphism_group(alg)
        
        # Should have at least the identity automorphism
        assert aut_group.get_underlying_set_size() == 2
        assert len(aut_group.get_generators()) >= 1

    def test_to_basic_algebra(self):
        """Test converting PermutationGroup to BasicAlgebra."""
        # Create a permutation group
        generators = [[1, 0]]
        pg = uacalc_lib.group.PermutationGroup("S2", generators)
        
        # Convert to BasicAlgebra
        alg = pg.to_basic_algebra("S2_algebra")
        
        # Check basic properties
        assert alg.cardinality() == 2
        assert alg.name() == "S2_algebra"
        
        # Should have 3 operations (product, inverse, identity)
        assert alg.operations_count() == 3

    def test_to_basic_algebra_universe(self):
        """Test that to_basic_algebra creates correct universe."""
        # Create a permutation group
        generators = [[1, 0, 2]]
        pg = uacalc_lib.group.PermutationGroup("S3", generators)
        
        # Convert to BasicAlgebra
        alg = pg.to_basic_algebra("S3_algebra")
        
        # Check universe
        universe = alg.get_universe()
        assert len(universe) == 3
        assert 0 in universe
        assert 1 in universe
        assert 2 in universe
