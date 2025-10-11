"""
Tests for SimilarityType Python bindings.

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
    SimilarityType = uacalc_lib.alg.SimilarityType
    OperationSymbol = uacalc_lib.alg.OperationSymbol
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    # Use Windows-compatible script path
    script_extension = ".bat" if platform.system() == "Windows" else ""
    java_wrapper_path = project_root / "java_wrapper" / "build" / "scripts" / f"SimilarityTypeWrapper{script_extension}"
    
    if not java_wrapper_path.exists():
        pytest.skip(f"Java wrapper not found at {java_wrapper_path}")
    
    cmd = [str(java_wrapper_path), command] + args
    
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


class TestSimilarityType:
    """Test SimilarityType Python bindings."""
    
    def test_creation(self):
        """Test basic SimilarityType creation."""
        ops = [OperationSymbol("join", 2), OperationSymbol("meet", 2)]
        st = SimilarityType(ops)
        
        java_result = run_java_wrapper("new", ["--operation_symbols", "join:2,meet:2"])
        
        assert str(st) == java_result["data"]["similarity_type"]
    
    def test_creation_sorted(self):
        """Test SimilarityType creation with sorting."""
        ops = [OperationSymbol("prod", 2), OperationSymbol("inv", 1), OperationSymbol("id", 0)]
        st = SimilarityType(ops, sort=True)
        
        java_result = run_java_wrapper("new_sorted", ["--operation_symbols", "prod:2,inv:1,id:0"])
        
        assert str(st) == java_result["data"]["similarity_type"]
        assert java_result["data"]["sorted"] is True
    
    def test_get_operation_symbols(self):
        """Test getting operation symbols."""
        ops = [OperationSymbol("join", 2), OperationSymbol("meet", 2)]
        st = SimilarityType(ops)
        result = st.get_operation_symbols()
        
        java_result = run_java_wrapper("get_operation_symbols", ["--operation_symbols", "join:2,meet:2"])
        
        assert len(result) == java_result["data"]["count"]
        # Check that we have the right operation symbols
        assert len(result) == 2
        assert result[0].name() in ["join", "meet"]
        assert result[1].name() in ["join", "meet"]
        assert result[0].arity() == 2
        assert result[1].arity() == 2
    
    def test_get_sorted_operation_symbols(self):
        """Test getting sorted operation symbols."""
        ops = [OperationSymbol("prod", 2), OperationSymbol("inv", 1), OperationSymbol("id", 0)]
        st = SimilarityType(ops)
        result = st.get_sorted_operation_symbols()
        
        java_result = run_java_wrapper("get_sorted_operation_symbols", ["--operation_symbols", "prod:2,inv:1,id:0"])
        
        assert len(result) == java_result["data"]["count"]
        # Should be sorted by arity (descending), then by name (ascending)
        # Expected order: prod(2), inv(1), id(0) - high arity first
        assert result[0].name() == "prod"
        assert result[0].arity() == 2
        assert result[1].name() == "inv"
        assert result[1].arity() == 1
        assert result[2].name() == "id"
        assert result[2].arity() == 0
    
    def test_input_size(self):
        """Test input size calculation."""
        ops = [OperationSymbol("join", 2), OperationSymbol("meet", 2)]
        st = SimilarityType(ops)
        input_size = st.input_size(5)
        
        java_result = run_java_wrapper("input_size", ["--operation_symbols", "join:2,meet:2", "--alg_size", "5"])
        
        assert input_size == java_result["data"]["input_size"]
        assert java_result["data"]["alg_size"] == 5
    
    def test_input_size_various(self):
        """Test input size with different algebra sizes."""
        ops = [OperationSymbol("join", 2), OperationSymbol("meet", 2)]
        st = SimilarityType(ops)
        
        # Test with algebra size 3
        input_size = st.input_size(3)
        java_result = run_java_wrapper("input_size", ["--operation_symbols", "join:2,meet:2", "--alg_size", "3"])
        
        assert input_size == java_result["data"]["input_size"]
        assert java_result["data"]["alg_size"] == 3
    
    def test_input_size_empty(self):
        """Test input size with empty similarity type."""
        ops = []
        st = SimilarityType(ops)
        input_size = st.input_size(5)
        
        java_result = run_java_wrapper("input_size", ["--operation_symbols", "", "--alg_size", "5"])
        
        assert input_size == java_result["data"]["input_size"]
        assert java_result["data"]["alg_size"] == 5
    
    def test_get_arities_map(self):
        """Test getting arities map."""
        ops = [OperationSymbol("join", 2), OperationSymbol("meet", 2), OperationSymbol("inv", 1)]
        st = SimilarityType(ops)
        arities_map = st.get_arities_map()
        
        java_result = run_java_wrapper("get_arities_map", ["--operation_symbols", "join:2,meet:2,inv:1"])
        
        # Convert Java result string keys to integers for comparison
        java_arities_map = {int(k): v for k, v in java_result["data"]["arities_map"].items()}
        assert arities_map == java_arities_map
        assert arities_map[2] == 2  # Two binary operations
        assert arities_map[1] == 1  # One unary operation
    
    def test_get_max_arity(self):
        """Test getting max arity."""
        ops = [OperationSymbol("join", 2), OperationSymbol("meet", 2), OperationSymbol("inv", 1)]
        st = SimilarityType(ops)
        max_arity = st.get_max_arity()
        
        java_result = run_java_wrapper("get_max_arity", ["--operation_symbols", "join:2,meet:2,inv:1"])
        
        assert max_arity == java_result["data"]["max_arity"]
        assert max_arity == 2
    
    def test_lattice_similarity_type(self):
        """Test lattice similarity type constant."""
        lattice_type = SimilarityType.lattice_similarity_type()
        
        java_result = run_java_wrapper("lattice_similarity_type", [])
        
        assert str(lattice_type) == java_result["data"]["similarity_type"]
        assert lattice_type.get_max_arity() == java_result["data"]["max_arity"]
        
        # Check that it contains join and meet
        ops = lattice_type.get_operation_symbols()
        op_names = [op.name() for op in ops]
        assert "join" in op_names
        assert "meet" in op_names
    
    def test_group_similarity_type(self):
        """Test group similarity type constant."""
        group_type = SimilarityType.group_similarity_type()
        
        java_result = run_java_wrapper("group_similarity_type", [])
        
        assert str(group_type) == java_result["data"]["similarity_type"]
        assert group_type.get_max_arity() == java_result["data"]["max_arity"]
        
        # Check that it contains product, inverse, and identity
        ops = group_type.get_operation_symbols()
        op_names = [op.name() for op in ops]
        assert "prod" in op_names
        assert "inv" in op_names
        assert "id" in op_names
    
    def test_arities_string(self):
        """Test arities string generation."""
        ops = [OperationSymbol("join", 2), OperationSymbol("meet", 2), OperationSymbol("inv", 1)]
        st = SimilarityType(ops)
        arities_string = st.arities_string()
        
        java_result = run_java_wrapper("arities_string", ["--operation_symbols", "join:2,meet:2,inv:1"])
        
        assert arities_string == java_result["data"]["arities_string"]
        assert "binary" in arities_string
        assert "unary" in arities_string
    
    def test_to_string(self):
        """Test string representation."""
        ops = [OperationSymbol("join", 2), OperationSymbol("meet", 2)]
        st = SimilarityType(ops)
        string_rep = str(st)
        
        java_result = run_java_wrapper("toString", ["--operation_symbols", "join:2,meet:2"])
        
        assert string_rep == java_result["data"]["string_representation"]
        assert string_rep.startswith("(")
        assert string_rep.endswith(")")
        assert "join" in string_rep
        assert "meet" in string_rep
    
    def test_equality(self):
        """Test equality comparison."""
        ops1 = [OperationSymbol("join", 2), OperationSymbol("meet", 2)]
        ops2 = [OperationSymbol("meet", 2), OperationSymbol("join", 2)]
        st1 = SimilarityType(ops1)
        st2 = SimilarityType(ops2)
        
        java_result = run_java_wrapper("equals", ["--operation_symbols1", "join:2,meet:2", "--operation_symbols2", "meet:2,join:2"])
        
        assert (st1 == st2) == java_result["data"]["equals"]
        assert st1 == st2  # Should be equal regardless of order
    
    def test_inequality(self):
        """Test inequality comparison."""
        ops1 = [OperationSymbol("join", 2), OperationSymbol("meet", 2)]
        ops2 = [OperationSymbol("join", 2), OperationSymbol("inv", 1)]
        st1 = SimilarityType(ops1)
        st2 = SimilarityType(ops2)
        
        java_result = run_java_wrapper("equals", ["--operation_symbols1", "join:2,meet:2", "--operation_symbols2", "join:2,inv:1"])
        
        assert (st1 == st2) == java_result["data"]["equals"]
        assert st1 != st2  # Should be different
    
    def test_hash(self):
        """Test hash function."""
        ops = [OperationSymbol("join", 2), OperationSymbol("meet", 2)]
        st = SimilarityType(ops)
        
        java_result = run_java_wrapper("hashCode", ["--operation_symbols", "join:2,meet:2"])
        
        # Hash values should be consistent
        assert hash(st) == hash(st)
        # Note: We can't directly compare with Java hash since they use different algorithms
    
    def test_repr(self):
        """Test string representation."""
        ops = [OperationSymbol("join", 2), OperationSymbol("meet", 2)]
        st = SimilarityType(ops)
        repr_str = repr(st)
        
        assert "SimilarityType" in repr_str
        assert "join" in repr_str
        assert "meet" in repr_str
    
    def test_comprehensive_functionality(self):
        """Test comprehensive functionality."""
        java_result = run_java_wrapper("test", [])
        
        # Test basic creation
        ops = [OperationSymbol.join(), OperationSymbol.meet()]
        st = SimilarityType(ops)
        assert str(st) == java_result["data"]["test_create"]
        
        # Test input size calculation
        input_size = st.input_size(3)
        assert input_size == java_result["data"]["test_input_size"]
        
        # Test max arity
        max_arity = st.get_max_arity()
        assert max_arity == java_result["data"]["test_max_arity"]
        
        # Test arities map
        arities_map = st.get_arities_map()
        java_arities_map = {int(k): v for k, v in java_result["data"]["test_arities_map"].items()}
        assert arities_map == java_arities_map
        
        # Test constants
        lattice_type = SimilarityType.lattice_similarity_type()
        assert str(lattice_type) == java_result["data"]["test_lattice_type"]
        
        group_type = SimilarityType.group_similarity_type()
        assert str(group_type) == java_result["data"]["test_group_type"]
        
        # Test equality
        st2 = SimilarityType([OperationSymbol.meet(), OperationSymbol.join()])
        assert (st == st2) == java_result["data"]["test_equals"]


class TestSimilarityTypeEdgeCases:
    """Test SimilarityType edge cases."""
    
    def test_empty_similarity_type(self):
        """Test empty similarity type."""
        st = SimilarityType([])
        assert str(st) == "()"
        assert st.input_size(5) == 5
        assert st.get_max_arity() == -1
        assert st.get_arities_map() == {}
    
    def test_single_operation(self):
        """Test similarity type with single operation."""
        ops = [OperationSymbol("f", 1)]
        st = SimilarityType(ops)
        assert st.input_size(3) == 3
        assert st.get_max_arity() == 1
        arities_map = st.get_arities_map()
        assert arities_map[1] == 1
    
    def test_high_arity_operations(self):
        """Test similarity type with high arity operations."""
        ops = [OperationSymbol("f", 5), OperationSymbol("g", 3)]
        st = SimilarityType(ops)
        assert st.get_max_arity() == 5
        arities_map = st.get_arities_map()
        assert arities_map[5] == 1
        assert arities_map[3] == 1
    
    def test_sorting_behavior(self):
        """Test sorting behavior."""
        ops = [
            OperationSymbol("z", 1),  # arity 1, name "z"
            OperationSymbol("a", 2),  # arity 2, name "a"
            OperationSymbol("b", 1),  # arity 1, name "b"
            OperationSymbol("c", 2),  # arity 2, name "c"
        ]
        
        st = SimilarityType(ops)
        sorted_ops = st.get_sorted_operation_symbols()
        
        # Should be sorted by arity (descending), then by name (ascending)
        # Expected order: a(2), c(2), b(1), z(1) - high arity first
        assert sorted_ops[0].name() == "a"
        assert sorted_ops[0].arity() == 2
        assert sorted_ops[1].name() == "c"
        assert sorted_ops[1].arity() == 2
        assert sorted_ops[2].name() == "b"
        assert sorted_ops[2].arity() == 1
        assert sorted_ops[3].name() == "z"
        assert sorted_ops[3].arity() == 1


class TestSimilarityTypeIntegration:
    """Test SimilarityType integration with OperationSymbol."""
    
    def test_with_operation_symbol_constants(self):
        """Test using OperationSymbol constants in SimilarityType."""
        ops = [OperationSymbol.join(), OperationSymbol.meet()]
        st = SimilarityType(ops)
        
        # Should be equivalent to lattice similarity type
        lattice_type = SimilarityType.lattice_similarity_type()
        assert st == lattice_type
    
    def test_mixed_operation_symbols(self):
        """Test mixing different types of operation symbols."""
        ops = [
            OperationSymbol("f", 0),  # nullary
            OperationSymbol("g", 1),  # unary
            OperationSymbol("h", 2),  # binary
            OperationSymbol("i", 3),  # ternary
        ]
        st = SimilarityType(ops)
        
        assert st.get_max_arity() == 3
        arities_map = st.get_arities_map()
        assert arities_map[0] == 1
        assert arities_map[1] == 1
        assert arities_map[2] == 1
        assert arities_map[3] == 1
        
        arities_string = st.arities_string()
        assert "3-ary" in arities_string
        assert "binary" in arities_string
        assert "unary" in arities_string
        # Note: nullary operations might not appear in arities_string depending on implementation
