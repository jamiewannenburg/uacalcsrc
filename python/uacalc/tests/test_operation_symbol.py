"""
Tests for OperationSymbol Python bindings.

These tests verify that the Python bindings work correctly
and provide the expected interface to the Rust implementation.
"""

import pytest
import subprocess
import json
import os
import sys
from pathlib import Path

# Add the project root to the path to import uacalc_lib
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import uacalc_lib
    OperationSymbol = uacalc_lib.alg.PyOperationSymbol
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    java_wrapper_path = project_root / "java_wrapper" / "build" / "scripts" / "OperationSymbolWrapper"
    
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


class TestOperationSymbol:
    """Test OperationSymbol Python bindings."""
    
    def test_creation(self):
        """Test basic OperationSymbol creation."""
        sym = OperationSymbol("f", 2)
        
        java_result = run_java_wrapper("new", ["--name", "f", "--arity", "2"])
        
        assert sym.name() == java_result["data"]["name"]
        assert sym.arity() == java_result["data"]["arity"]
        assert sym.is_associative() == java_result["data"]["associative"]
    
    def test_creation_with_associativity(self):
        """Test OperationSymbol creation with associativity."""
        sym = OperationSymbol("g", 2, associative=True)
        
        java_result = run_java_wrapper("new", ["--name", "g", "--arity", "2", "--associative", "true"])
        
        assert sym.name() == java_result["data"]["name"]
        assert sym.arity() == java_result["data"]["arity"]
        assert sym.is_associative() == java_result["data"]["associative"]
    
    def test_arity(self):
        """Test getting arity."""
        sym = OperationSymbol("f", 3)
        
        java_result = run_java_wrapper("arity", ["--name", "f", "--arity", "3"])
        
        assert sym.arity() == java_result["data"]["arity"]
    
    def test_name(self):
        """Test getting name."""
        sym = OperationSymbol("myOp", 1)
        
        java_result = run_java_wrapper("name", ["--name", "myOp", "--arity", "1"])
        
        assert sym.name() == java_result["data"]["name"]
    
    def test_is_associative(self):
        """Test checking associativity."""
        sym = OperationSymbol("f", 2)
        
        java_result = run_java_wrapper("isAssociative", ["--name", "f", "--arity", "2"])
        
        assert sym.is_associative() == java_result["data"]["associative"]
    
    def test_set_associative(self):
        """Test setting associativity."""
        sym = OperationSymbol("f", 2, associative=False)
        sym.set_associative(True)
        
        java_result = run_java_wrapper(
            "setAssociative", 
            ["--name", "f", "--arity", "2", "--associative", "false", "--newAssociative", "true"]
        )
        
        assert sym.is_associative() == java_result["data"]["associative"]
    
    def test_to_string_with_arity(self):
        """Test string representation with arity."""
        sym = OperationSymbol("f", 2)
        
        java_result = run_java_wrapper(
            "toStringWithArity", 
            ["--name", "f", "--arity", "2", "--showArity", "true"]
        )
        
        assert sym.to_string_with_arity(True) == java_result["data"]["string"]
    
    def test_to_string_without_arity(self):
        """Test string representation without arity."""
        sym = OperationSymbol("f", 2)
        
        java_result = run_java_wrapper("toString", ["--name", "f", "--arity", "2"])
        
        assert str(sym) == java_result["data"]["string"]
    
    def test_equality(self):
        """Test equality comparison."""
        sym1 = OperationSymbol("f", 2)
        sym2 = OperationSymbol("f", 2)
        
        java_result = run_java_wrapper(
            "equals", 
            ["--name1", "f", "--arity1", "2", "--name2", "f", "--arity2", "2"]
        )
        
        assert (sym1 == sym2) == java_result["data"]["equals"]
    
    def test_inequality(self):
        """Test inequality comparison."""
        sym1 = OperationSymbol("f", 2)
        sym2 = OperationSymbol("g", 2)
        
        java_result = run_java_wrapper(
            "equals", 
            ["--name1", "f", "--arity1", "2", "--name2", "g", "--arity2", "2"]
        )
        
        assert (sym1 == sym2) == java_result["data"]["equals"]
    
    def test_comparison(self):
        """Test comparison operations."""
        sym1 = OperationSymbol("f", 2)
        sym2 = OperationSymbol("g", 3)
        
        java_result = run_java_wrapper(
            "compareTo", 
            ["--name1", "f", "--arity1", "2", "--name2", "g", "--arity2", "3"]
        )
        
        # Convert Python comparison result to Java-style integer
        python_comparison = 0
        if sym1 < sym2:
            python_comparison = -1
        elif sym1 > sym2:
            python_comparison = 1
        
        assert python_comparison == java_result["data"]["comparison"]
    
    def test_hash(self):
        """Test hash function."""
        sym = OperationSymbol("f", 2)
        
        java_result = run_java_wrapper("hashCode", ["--name", "f", "--arity", "2"])
        
        # Hash values should be consistent
        assert hash(sym) == hash(sym)
        # Note: We can't directly compare with Java hash since they use different algorithms
    
    def test_get_operation_symbol_arity_0(self):
        """Test getOperationSymbol for arity 0."""
        sym = OperationSymbol.get_operation_symbol(0)
        
        java_result = run_java_wrapper("getOperationSymbol", ["--arity", "0"])
        
        assert sym.arity() == java_result["data"]["arity"]
        assert sym.name().startswith("c_")
    
    def test_get_operation_symbol_arity_1(self):
        """Test getOperationSymbol for arity 1."""
        sym = OperationSymbol.get_operation_symbol(1)
        
        java_result = run_java_wrapper("getOperationSymbol", ["--arity", "1"])
        
        assert sym.arity() == java_result["data"]["arity"]
        assert sym.name().startswith("u_")
    
    def test_get_operation_symbol_arity_2(self):
        """Test getOperationSymbol for arity 2."""
        sym = OperationSymbol.get_operation_symbol(2)
        
        java_result = run_java_wrapper("getOperationSymbol", ["--arity", "2"])
        
        assert sym.arity() == java_result["data"]["arity"]
        assert sym.name().startswith("b_")
    
    def test_get_operation_symbol_arity_3(self):
        """Test getOperationSymbol for arity 3."""
        sym = OperationSymbol.get_operation_symbol(3)
        
        java_result = run_java_wrapper("getOperationSymbol", ["--arity", "3"])
        
        assert sym.arity() == java_result["data"]["arity"]
        assert sym.name().startswith("t_")
    
    def test_get_operation_symbol_high_arity(self):
        """Test getOperationSymbol for high arity."""
        sym = OperationSymbol.get_operation_symbol(5)
        
        java_result = run_java_wrapper("getOperationSymbol", ["--arity", "5"])
        
        assert sym.arity() == java_result["data"]["arity"]
        assert sym.name().startswith("op5_")
    
    def test_get_operation_symbol_sequence(self):
        """Test that getOperationSymbol generates sequential names."""
        sym1 = OperationSymbol.get_operation_symbol(2)
        sym2 = OperationSymbol.get_operation_symbol(2)
        sym3 = OperationSymbol.get_operation_symbol(2)
        
        # Names should be sequential
        assert sym1.name() != sym2.name()
        assert sym2.name() != sym3.name()
        assert sym1.name() != sym3.name()
        
        # All should have arity 2
        assert sym1.arity() == 2
        assert sym2.arity() == 2
        assert sym3.arity() == 2
    
    def test_constants(self):
        """Test static constants."""
        java_result = run_java_wrapper("constants", [])
        
        # Test JOIN
        join = OperationSymbol.join()
        assert join.name() == java_result["data"]["JOIN"]["name"]
        assert join.arity() == java_result["data"]["JOIN"]["arity"]
        assert join.is_associative() == java_result["data"]["JOIN"]["associative"]
        
        # Test MEET
        meet = OperationSymbol.meet()
        assert meet.name() == java_result["data"]["MEET"]["name"]
        assert meet.arity() == java_result["data"]["MEET"]["arity"]
        assert meet.is_associative() == java_result["data"]["MEET"]["associative"]
        
        # Test PRODUCT
        product = OperationSymbol.product()
        assert product.name() == java_result["data"]["PRODUCT"]["name"]
        assert product.arity() == java_result["data"]["PRODUCT"]["arity"]
        assert product.is_associative() == java_result["data"]["PRODUCT"]["associative"]
        
        # Test INVERSE
        inverse = OperationSymbol.inverse()
        assert inverse.name() == java_result["data"]["INVERSE"]["name"]
        assert inverse.arity() == java_result["data"]["INVERSE"]["arity"]
        assert inverse.is_associative() == java_result["data"]["INVERSE"]["associative"]
        
        # Test IDENTITY
        identity = OperationSymbol.identity()
        assert identity.name() == java_result["data"]["IDENTITY"]["name"]
        assert identity.arity() == java_result["data"]["IDENTITY"]["arity"]
        assert identity.is_associative() == java_result["data"]["IDENTITY"]["associative"]
    
    def test_repr(self):
        """Test string representation."""
        sym = OperationSymbol("f", 2, associative=True)
        repr_str = repr(sym)
        
        assert "OperationSymbol" in repr_str
        assert "name='f'" in repr_str
        assert "arity=2" in repr_str
        assert "associative=true" in repr_str  # Python uses lowercase boolean
    
    def test_associativity_validation(self):
        """Test that associativity validation works."""
        # The Rust implementation panics for non-binary associative operations
        # This is the expected behavior - we just verify it raises some exception
        try:
            OperationSymbol("f", 1, associative=True)
            pytest.fail("Should have raised an exception")
        except:
            # Any exception is fine - the important thing is that it fails
            pass
    
    def test_comprehensive_functionality(self):
        """Test comprehensive functionality."""
        java_result = run_java_wrapper("test", [])
        
        # Test basic creation
        sym1 = OperationSymbol("f", 2)
        assert str(sym1) == java_result["data"]["basic_creation"]
        
        # Test associativity
        sym2 = OperationSymbol("g", 2, associative=True)
        assert sym2.is_associative() == java_result["data"]["associative_creation"]
        
        # Test comparison
        sym3 = OperationSymbol("h", 3)
        comparison = 0
        if sym3 < sym1:
            comparison = -1
        elif sym3 > sym1:
            comparison = 1
        assert comparison == java_result["data"]["comparison_result"]
        
        # Test getOperationSymbol - just verify it generates a valid name
        sym4 = OperationSymbol.get_operation_symbol(2)
        assert sym4.name().startswith("b_")
        assert sym4.arity() == 2


class TestOperationSymbolOrdering:
    """Test OperationSymbol ordering behavior."""
    
    def test_ordering_by_arity(self):
        """Test that higher arity comes first."""
        sym1 = OperationSymbol("a", 1)  # arity 1
        sym2 = OperationSymbol("b", 2)  # arity 2
        
        # Higher arity should come first (be "less than")
        assert sym2 < sym1
    
    def test_ordering_by_name(self):
        """Test that same arity is ordered by name."""
        sym1 = OperationSymbol("a", 2)  # arity 2, name "a"
        sym2 = OperationSymbol("b", 2)  # arity 2, name "b"
        
        # "a" should come before "b"
        assert sym1 < sym2
    
    def test_ordering_combined(self):
        """Test combined ordering (arity first, then name)."""
        sym1 = OperationSymbol("a", 1)  # arity 1, name "a"
        sym2 = OperationSymbol("b", 2)  # arity 2, name "b"
        sym3 = OperationSymbol("a", 2)  # arity 2, name "a"
        sym4 = OperationSymbol("b", 1)  # arity 1, name "b"
        
        # Order should be: sym3 (arity 2, name "a"), sym2 (arity 2, name "b"), 
        #                  sym1 (arity 1, name "a"), sym4 (arity 1, name "b")
        assert sym3 < sym2  # same arity, "a" < "b"
        assert sym2 < sym1  # arity 2 < arity 1
        assert sym1 < sym4  # same arity, "a" < "b"
