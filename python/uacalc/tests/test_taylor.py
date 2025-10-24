"""Tests for Taylor Python bindings.

These tests verify that the Python Taylor bindings work correctly and match
the Java implementation behavior.
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the Taylor class through uacalc_lib
import uacalc_lib
Taylor = uacalc_lib.terms.Taylor
IntArray = uacalc_lib.util.IntArray
OperationSymbol = uacalc_lib.alg.OperationSymbol


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    from test_utils import build_java_command
    
    wrapper_class = "java_wrapper.src.terms.TaylorWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")
        
        output = json.loads(result.stdout)
        # Parse the data field again if it's a string
        if "data" in output and isinstance(output["data"], str):
            output["data"] = json.loads(output["data"])
        return output
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Java wrapper output: {e}\nStdout: {result.stdout}")


class TestTaylor:
    """Test cases for Taylor Python bindings."""
    
    def test_markovic_mckenzie_term(self):
        """Test getting Markovic-McKenzie term."""
        java_result = run_java_wrapper("markovic_mckenzie_term", [])
        
        # Create Python Taylor
        taylor = Taylor.markovic_mckenzie_term()
        
        assert taylor.arity() == 4
        assert len(taylor.inteqs()) == 2
        assert java_result["data"]["arity"] == 4
        assert java_result["data"]["inteqs_count"] == 2
    
    def test_siggers_term(self):
        """Test getting Siggers term."""
        java_result = run_java_wrapper("siggers_term", [])
        
        # Create Python Taylor
        taylor = Taylor.siggers_term()
        
        assert taylor.arity() == 6
        assert len(taylor.inteqs()) == 2
        assert java_result["data"]["arity"] == 6
        assert java_result["data"]["inteqs_count"] == 2
    
    def test_new_with_arity(self):
        """Test creating Taylor with arity and equations."""
        eqs_str = "[[1,0,0,0],[0,0,1,1]]:[[0,0,1,0],[0,1,0,0]]"
        java_result = run_java_wrapper("new_with_arity", ["--arity", "4", "--eqs", eqs_str])
        
        # Create Python Taylor
        eqs = [
            [IntArray.from_array([1, 0, 0, 0]), IntArray.from_array([0, 0, 1, 1])],
            [IntArray.from_array([0, 0, 1, 0]), IntArray.from_array([0, 1, 0, 0])]
        ]
        taylor = Taylor.new_with_arity(4, eqs)
        
        assert taylor.arity() == 4
        assert len(taylor.inteqs()) == 2
        assert java_result["data"]["arity"] == 4
        assert java_result["data"]["inteqs_count"] == 2
    
    def test_new_with_operation_symbol(self):
        """Test creating Taylor with operation symbol."""
        # Create Python Taylor with operation symbol
        eqs = [
            [IntArray.from_array([1, 0, 0, 0]), IntArray.from_array([0, 0, 1, 1])],
            [IntArray.from_array([0, 0, 1, 0]), IntArray.from_array([0, 1, 0, 0])]
        ]
        op_sym = OperationSymbol("f", 4, False)
        taylor = Taylor(op_sym, eqs)
        
        assert taylor.arity() == 4
        assert len(taylor.inteqs()) == 2
    
    def test_term_from_array(self):
        """Test creating term from array."""
        eqs_str = "[[1,0],[0,1]]"
        arr_str = "0,1,1,0"
        java_result = run_java_wrapper("term_from_array", 
                                       ["--arr", arr_str, 
                                        "--arity", "2", 
                                        "--eqs", eqs_str])
        
        # Create Python Taylor and term
        eqs = [[IntArray.from_array([1, 0]), IntArray.from_array([0, 1])]]
        taylor = Taylor.new_with_arity(2, eqs)
        term = taylor.term_from_array([0, 1, 1, 0])
        
        # Convert term to string for comparison
        term_str = str(term)
        
        # Both should produce the same term structure
        assert java_result["data"]["status"] == term_str
    
    def test_lexicographically_compare_arrays(self):
        """Test lexicographic comparison of arrays."""
        java_result = run_java_wrapper("lexicographically_compare_arrays", 
                                       ["--a", "1,2,3", "--b", "1,2,4"])
        
        # Test Python comparison
        result = Taylor.lexicographically_compare_arrays([1, 2, 3], [1, 2, 4])
        
        assert result < 0
        assert java_result["data"]["status"] < 0
    
    def test_lexicographically_compare_arrays_equal(self):
        """Test lexicographic comparison with equal arrays."""
        java_result = run_java_wrapper("lexicographically_compare_arrays", 
                                       ["--a", "1,2,3", "--b", "1,2,3"])
        
        # Test Python comparison
        result = Taylor.lexicographically_compare_arrays([1, 2, 3], [1, 2, 3])
        
        assert result == 0
        assert java_result["data"]["status"] == 0
    
    def test_lexicographically_compare_arrays_greater(self):
        """Test lexicographic comparison with first array greater."""
        java_result = run_java_wrapper("lexicographically_compare_arrays", 
                                       ["--a", "1,3,3", "--b", "1,2,3"])
        
        # Test Python comparison
        result = Taylor.lexicographically_compare_arrays([1, 3, 3], [1, 2, 3])
        
        assert result > 0
        assert java_result["data"]["status"] > 0
    
    def test_lexicographically_compare_int_arrays(self):
        """Test lexicographic comparison of IntArrays."""
        # Test Python comparison
        a = IntArray.from_array([1, 2, 3])
        b = IntArray.from_array([1, 2, 4])
        
        result = Taylor.lexicographically_compare_int_arrays(a, b)
        
        assert result < 0
    
    def test_arity_getter(self):
        """Test arity getter."""
        eqs_str = "[[1,0,0,0],[0,0,1,1]]"
        java_result = run_java_wrapper("arity", ["--arity", "4", "--eqs", eqs_str])
        
        # Create Python Taylor
        eqs = [[IntArray.from_array([1, 0, 0, 0]), IntArray.from_array([0, 0, 1, 1])]]
        taylor = Taylor.new_with_arity(4, eqs)
        
        assert taylor.arity() == 4
        assert java_result["data"]["status"] == 4
    
    def test_inteqs_getter(self):
        """Test inteqs getter."""
        eqs_str = "[[1,0,0,0],[0,0,1,1]]"
        java_result = run_java_wrapper("inteqs", ["--arity", "4", "--eqs", eqs_str])
        
        # Create Python Taylor
        eqs = [[IntArray.from_array([1, 0, 0, 0]), IntArray.from_array([0, 0, 1, 1])]]
        taylor = Taylor.new_with_arity(4, eqs)
        
        inteqs = taylor.inteqs()
        assert len(inteqs) == 1
        assert len(inteqs[0]) == 2
        
        # Verify the equation values
        eq = inteqs[0]
        assert eq[0].to_array() == [1, 0, 0, 0]
        assert eq[1].to_array() == [0, 0, 1, 1]
    
    def test_comprehensive(self):
        """Test comprehensive Taylor functionality."""
        java_result = run_java_wrapper("test", [])
        
        # Run comprehensive tests in Python
        mm = Taylor.markovic_mckenzie_term()
        assert mm.arity() == 4, "Markovic-McKenzie arity should be 4"
        
        siggers = Taylor.siggers_term()
        assert siggers.arity() == 6, "Siggers arity should be 6"
        
        result = Taylor.lexicographically_compare_arrays([1, 2, 3], [1, 2, 4])
        assert result < 0, "a should be less than b"
        
        # Verify Java test passed
        assert java_result["data"]["status"] == "All tests passed"
    
    def test_taylor_with_different_arities(self):
        """Test creating Taylor with different arities."""
        for arity in range(2, 7):
            left = [0] * arity
            left[0] = 1
            right = [0] * arity
            right[1] = 1
            
            eqs = [[IntArray.from_array(left), IntArray.from_array(right)]]
            taylor = Taylor.new_with_arity(arity, eqs)
            
            assert taylor.arity() == arity
    
    def test_term_from_array_variable(self):
        """Test creating variable from array."""
        eqs = [[IntArray.from_array([1, 0]), IntArray.from_array([0, 1])]]
        taylor = Taylor.new_with_arity(2, eqs)
        
        # Create a term from single element array (should be a variable)
        term = taylor.term_from_array([0])
        # Variables don't have a reliable isa_variable method in Python,
        # so we check the string representation
        assert str(term) in ["x", "y"]
    
    def test_markovic_mckenzie_term_singleton(self):
        """Test that Markovic-McKenzie term is a singleton (or at least consistent)."""
        taylor1 = Taylor.markovic_mckenzie_term()
        taylor2 = Taylor.markovic_mckenzie_term()
        
        # Both should have the same properties
        assert taylor1.arity() == taylor2.arity()
        assert len(taylor1.inteqs()) == len(taylor2.inteqs())
    
    def test_siggers_term_singleton(self):
        """Test that Siggers term is a singleton (or at least consistent)."""
        taylor1 = Taylor.siggers_term()
        taylor2 = Taylor.siggers_term()
        
        # Both should have the same properties
        assert taylor1.arity() == taylor2.arity()
        assert len(taylor1.inteqs()) == len(taylor2.inteqs())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
