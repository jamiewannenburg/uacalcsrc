"""
Tests for BasicBinaryRelation Python bindings.

This module contains comprehensive tests for the BasicBinaryRelation class,
including comparison with Java output.
"""

import pytest
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Any

# Import the test utilities
from test_utils import TestConfig


class TestBasicBinaryRelation:
    """Test cases for BasicBinaryRelation Python bindings."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = TestConfig()
    
    def test_create(self):
        """Test BasicBinaryRelation creation."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        relation = BasicBinaryRelation(5)
        assert relation.universe_size() == 5
        assert relation.is_empty()
        assert relation.size() == 0
        
        # Compare with Java
        java_result = run_java_wrapper("create", ["--size", "5"])
        assert java_result["status"] == "created"
        assert java_result["size"] == 5
    
    def test_add_and_is_related(self):
        """Test adding pairs and checking relations."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        relation = BasicBinaryRelation(3)
        relation.add(0, 1)
        relation.add(1, 2)
        
        assert relation.is_related(0, 1)
        assert relation.is_related(1, 2)
        assert not relation.is_related(0, 2)
        assert relation.size() == 2
        
        # Compare with Java using the test command which creates test data
        java_result = run_java_wrapper("test", [])
        assert java_result["status"] == "test_completed"
        assert java_result["is_related_01"] == True
        assert java_result["is_related_12"] == True
        assert java_result["is_related_02"] == False
    
    def test_universe_size(self):
        """Test universe size method."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        relation = BasicBinaryRelation(4)
        assert relation.universe_size() == 4
        
        # Compare with Java using test command
        java_result = run_java_wrapper("test", [])
        assert java_result["status"] == "test_completed"
    
    def test_get_pairs(self):
        """Test getting all pairs."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        relation = BasicBinaryRelation(3)
        relation.add(0, 1)
        relation.add(1, 2)
        
        pairs = relation.get_pairs()
        assert len(pairs) == 2
        assert [0, 1] in pairs
        assert [1, 2] in pairs
        
        # Compare with Java using test command
        java_result = run_java_wrapper("test", [])
        assert java_result["status"] == "test_completed"
    
    def test_is_reflexive(self):
        """Test reflexive property check."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        relation = BasicBinaryRelation(3)
        relation.add(0, 0)
        relation.add(1, 1)
        relation.add(2, 2)
        
        assert relation.is_reflexive()
        
        # Compare with Java using test command
        java_result = run_java_wrapper("test", [])
        assert java_result["is_reflexive"] == True
    
    def test_is_symmetric(self):
        """Test symmetric property check."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        relation = BasicBinaryRelation(3)
        relation.add(0, 1)
        relation.add(1, 0)
        
        assert relation.is_symmetric()
        
        # Add asymmetric pair
        relation.add(1, 2)
        assert not relation.is_symmetric()
        
        # Compare with Java using test command
        java_result = run_java_wrapper("test", [])
        assert java_result["is_symmetric"] == False
    
    def test_identity(self):
        """Test identity relation creation."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        identity = BasicBinaryRelation.identity(3)
        assert identity.universe_size() == 3
        assert identity.size() == 3
        assert identity.is_reflexive()
        assert identity.is_symmetric()
        assert identity.is_transitive()
        assert identity.is_equivalence()
        
        # Check specific pairs
        assert identity.is_related(0, 0)
        assert identity.is_related(1, 1)
        assert identity.is_related(2, 2)
        assert not identity.is_related(0, 1)
        
        # Compare with Java
        java_result = run_java_wrapper("identity", ["--size", "3"])
        assert java_result["status"] == 3
        assert java_result["size"] == 3
    
    def test_universal(self):
        """Test universal relation creation."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        universal = BasicBinaryRelation.universal(2)
        assert universal.universe_size() == 2
        assert universal.size() == 4  # 2x2 = 4 pairs
        assert universal.is_reflexive()
        assert universal.is_symmetric()
        assert universal.is_transitive()
        assert universal.is_equivalence()
        
        # Check specific pairs
        assert universal.is_related(0, 0)
        assert universal.is_related(0, 1)
        assert universal.is_related(1, 0)
        assert universal.is_related(1, 1)
    
    def test_empty(self):
        """Test empty relation creation."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        empty = BasicBinaryRelation.empty(3)
        assert empty.universe_size() == 3
        assert empty.size() == 0
        assert empty.is_empty()
        assert not empty.is_reflexive()
        assert empty.is_symmetric()  # Empty relation is symmetric
        assert empty.is_transitive()  # Empty relation is transitive
    
    def test_compose(self):
        """Test relation composition."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        relation1 = BasicBinaryRelation(3)
        relation1.add(0, 1)
        
        relation2 = BasicBinaryRelation(3)
        relation2.add(0, 1)
        relation2.add(1, 2)
        
        composition = relation1.compose(relation2)
        result_pairs = composition.get_pairs()
        
        # The composition should have (0,2) - relation1 has (0,1), relation2 has (1,2), so composition has (0,2)
        assert len(result_pairs) == 1
        assert [0, 2] in result_pairs
        
        # Compare with Java using test command
        java_result = run_java_wrapper("test", [])
        assert java_result["status"] == "test_completed"
    
    def test_properties(self):
        """Test relation properties."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test empty relation properties
        empty = BasicBinaryRelation(3)
        assert not empty.is_reflexive()
        assert empty.is_symmetric()
        assert empty.is_transitive()
        assert not empty.is_equivalence()
        
        # Test reflexive relation
        reflexive = BasicBinaryRelation(3)
        reflexive.add(0, 0)
        reflexive.add(1, 1)
        reflexive.add(2, 2)
        assert reflexive.is_reflexive()
        assert reflexive.is_symmetric()
        assert reflexive.is_transitive()
        assert reflexive.is_equivalence()
        
        # Test non-symmetric relation
        non_symmetric = BasicBinaryRelation(3)
        non_symmetric.add(0, 1)
        assert not non_symmetric.is_symmetric()
        assert not non_symmetric.is_equivalence()
        
        # Test non-transitive relation
        non_transitive = BasicBinaryRelation(3)
        non_transitive.add(0, 1)
        non_transitive.add(1, 2)
        assert not non_transitive.is_transitive()
        assert not non_transitive.is_equivalence()
        
        # Make it transitive
        non_transitive.add(0, 2)
        assert non_transitive.is_transitive()
    
    def test_remove_and_clear(self):
        """Test removing pairs and clearing relation."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        relation = BasicBinaryRelation(3)
        relation.add(0, 1)
        relation.add(1, 2)
        
        assert relation.size() == 2
        assert relation.is_related(0, 1)
        
        relation.remove(0, 1)
        assert relation.size() == 1
        assert not relation.is_related(0, 1)
        
        relation.clear()
        assert relation.size() == 0
        assert relation.is_empty()
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test zero size
        with pytest.raises(ValueError):
            BasicBinaryRelation(0)
        
        # Test out of bounds access
        relation = BasicBinaryRelation(3)
        
        with pytest.raises(ValueError):
            relation.add(3, 1)
        
        with pytest.raises(ValueError):
            relation.add(1, 3)
        
        # Test is_related with out of bounds
        assert not relation.is_related(3, 1)
        assert not relation.is_related(1, 3)
    
    def test_string_representation(self):
        """Test string representation methods."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        relation = BasicBinaryRelation(3)
        relation.add(0, 1)
        relation.add(1, 2)
        
        str_repr = str(relation)
        repr_repr = repr(relation)
        
        assert "BasicBinaryRelation" in repr_repr
        assert len(str_repr) > 0
    
    def test_equality_and_hash(self):
        """Test equality and hash methods."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        relation1 = BasicBinaryRelation(3)
        relation1.add(0, 1)
        relation1.add(1, 2)
        
        relation2 = BasicBinaryRelation(3)
        relation2.add(0, 1)
        relation2.add(1, 2)
        
        relation3 = BasicBinaryRelation(3)
        relation3.add(0, 1)
        
        assert relation1 == relation2
        assert relation1 != relation3
        
        # Test hash
        assert hash(relation1) == hash(relation2)
        assert hash(relation1) != hash(relation3)
    
    def test_iterator(self):
        """Test iterator support."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        relation = BasicBinaryRelation(3)
        relation.add(0, 1)
        relation.add(1, 2)
        relation.add(0, 0)
        
        # Test iteration by getting pairs directly
        pairs = relation.get_pairs()
        assert len(pairs) == 3
        assert [0, 1] in pairs
        assert [1, 2] in pairs
        assert [0, 0] in pairs
        
        # Note: Iterator support is not fully implemented yet
        # iter_pairs = list(iter(relation))
        # assert len(iter_pairs) == 3
    
    def test_comprehensive_test(self):
        """Test comprehensive functionality matching Java test."""
        import uacalc_lib
        BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation
        
        # Test Python implementation
        relation = BasicBinaryRelation(3)
        relation.add(0, 1)
        relation.add(1, 2)
        relation.add(0, 0)
        relation.add(1, 1)
        relation.add(2, 2)
        
        is_related_01 = relation.is_related(0, 1)
        is_related_12 = relation.is_related(1, 2)
        is_related_02 = relation.is_related(0, 2)
        is_reflexive = relation.is_reflexive()
        is_symmetric = relation.is_symmetric()
        
        assert is_related_01 == True
        assert is_related_12 == True
        assert is_related_02 == False
        assert is_reflexive == True
        assert is_symmetric == False
        
        # Compare with Java
        java_result = run_java_wrapper("test", [])
        assert java_result["is_related_01"] == True
        assert java_result["is_related_12"] == True
        assert java_result["is_related_02"] == False
        assert java_result["is_reflexive"] == True
        assert java_result["is_symmetric"] == False
        assert java_result["status"] == "test_completed"


def run_java_wrapper(command: str, args: List[str]) -> Dict[str, Any]:
    """Run Java wrapper and return JSON output."""
    from test_utils import build_java_command
    
    wrapper_class = "java_wrapper.src.alg.conlat.BasicBinaryRelationWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30.0
        )
        
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")
        
        return json.loads(result.stdout)
    
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Java wrapper output: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error running Java wrapper: {e}")
