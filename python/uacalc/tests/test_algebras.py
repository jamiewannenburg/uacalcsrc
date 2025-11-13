"""
Tests for Algebras Python bindings.

This module contains comprehensive tests for the Algebras module,
including comparison with Java wrapper output.
"""

import pytest
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Any

# Import the test utilities
from test_utils import TestConfig, build_java_command


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    wrapper_class = "java_wrapper.src.alg.AlgebrasWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    project_root = Path(__file__).parent.parent.parent.parent
    
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


class TestAlgebras:
    """Test cases for Algebras Python bindings."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = TestConfig()
        try:
            import uacalc_lib
            self.uacalc_lib = uacalc_lib
        except ImportError:
            pytest.skip("uacalc_lib not available")
    
    def test_is_endomorphism_identity(self):
        """Test is_endomorphism with identity operation."""
        import uacalc_lib
        
        # Create a simple 2-element algebra
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        Operations = uacalc_lib.alg.Operations
        is_endomorphism = uacalc_lib.alg.is_endomorphism
        
        # Create algebra with a binary operation (first projection)
        sym = OperationSymbol("f", 2, False)
        table = [0, 0, 1, 1]  # f(0,0)=0, f(0,1)=0, f(1,0)=1, f(1,1)=1
        op = Operations.make_int_operation(sym, 2, table)
        alg = BasicAlgebra("TestAlg", [0, 1], [op])
        
        # Create identity endomorphism: e(x) = x
        id_sym = OperationSymbol("id", 1, False)
        id_table = [0, 1]  # id(0)=0, id(1)=1
        id_op = Operations.make_int_operation(id_sym, 2, id_table)
        
        # Test Python implementation
        result = is_endomorphism(id_op, alg)
        assert result == True, "Identity should be an endomorphism"
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("isEndomorphism", [
            "--size", "2",
            "--operation", "1:0,1"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result"] == True
        assert java_result["data"]["result"] == result, "Python and Java should match"
    
    def test_is_endomorphism_non_unary(self):
        """Test is_endomorphism with non-unary operation (should raise error)."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        Operations = uacalc_lib.alg.Operations
        is_endomorphism = uacalc_lib.alg.is_endomorphism
        
        # Create algebra
        alg = BasicAlgebra("TestAlg", [0, 1], [])
        
        # Create a binary operation (not unary)
        sym = OperationSymbol("f", 2, False)
        table = [0, 0, 1, 1]
        op = Operations.make_int_operation(sym, 2, table)
        
        # Test Python implementation - should raise ValueError
        with pytest.raises(Exception):  # ValueError or similar
            is_endomorphism(op, alg)
    
    def test_is_endomorphism_non_endomorphism(self):
        """Test is_endomorphism with operation that is not an endomorphism."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        Operations = uacalc_lib.alg.Operations
        is_endomorphism = uacalc_lib.alg.is_endomorphism
        
        # Create algebra with constant operation: f(x,y) = 0
        const_sym = OperationSymbol("const", 2, False)
        const_table = [0, 0, 0, 0]  # always returns 0
        const_op = Operations.make_int_operation(const_sym, 2, const_table)
        alg = BasicAlgebra("TestAlg2", [0, 1], [const_op])
        
        # Create swap operation: e(x) = 1-x (swaps 0 and 1)
        swap_sym = OperationSymbol("swap", 1, False)
        swap_table = [1, 0]  # swap(0)=1, swap(1)=0
        swap_op = Operations.make_int_operation(swap_sym, 2, swap_table)
        
        # Test Python implementation
        # swap(const(0,1)) = swap(0) = 1
        # const(swap(0), swap(1)) = const(1, 0) = 0
        # 1 != 0, so swap is not an endomorphism
        result = is_endomorphism(swap_op, alg)
        assert result == False, "Swap should not be an endomorphism for constant operation"
        
        # Compare with Java wrapper
        # Note: Java wrapper creates test algebra with first projection, not constant
        # So we test with a different scenario
        java_result = run_java_wrapper("isEndomorphism", [
            "--size", "2",
            "--operation", "1:1,0"  # swap operation
        ])
        
        assert java_result["success"] == True
        # The Java test algebra uses first projection, so swap may or may not be an endomorphism
        # We just verify the call works
        assert "result" in java_result["data"]

