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
    
    def test_is_homomorphism_identity(self):
        """Test is_homomorphism with identity map."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        Operations = uacalc_lib.alg.Operations
        is_homomorphism = uacalc_lib.alg.is_homomorphism
        
        # Create two identical algebras with a binary operation (first projection)
        sym = OperationSymbol("f", 2, False)
        table = [0, 0, 1, 1]  # f(0,0)=0, f(0,1)=0, f(1,0)=1, f(1,1)=1
        op = Operations.make_int_operation(sym, 2, table)
        alg0 = BasicAlgebra("Alg0", [0, 1], [op])
        alg1 = BasicAlgebra("Alg1", [0, 1], [op])
        
        # Identity map: 0 -> 0, 1 -> 1
        map = [0, 1]
        
        # Test Python implementation
        result = is_homomorphism(map, alg0, alg1)
        assert result == True, "Identity map should be a homomorphism"
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("isHomomorphism", [
            "--size", "2",
            "--map", "0,1"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result"] == True
        assert java_result["data"]["result"] == result, "Python and Java should match"
    
    def test_is_homomorphism_constant(self):
        """Test is_homomorphism with constant map."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        Operations = uacalc_lib.alg.Operations
        is_homomorphism = uacalc_lib.alg.is_homomorphism
        
        # Create two algebras with constant operation
        const_sym = OperationSymbol("const", 2, False)
        const_table = [0, 0, 0, 0]  # always returns 0
        const_op = Operations.make_int_operation(const_sym, 2, const_table)
        alg0 = BasicAlgebra("Alg0", [0, 1], [const_op])
        alg1 = BasicAlgebra("Alg1", [0, 1], [const_op])
        
        # Constant map: 0 -> 0, 1 -> 0
        map = [0, 0]
        
        # Test Python implementation
        result = is_homomorphism(map, alg0, alg1)
        assert result == True, "Constant map should be a homomorphism for constant operation"
    
    def test_is_homomorphism_non_homomorphism(self):
        """Test is_homomorphism with map that is not a homomorphism."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        Operations = uacalc_lib.alg.Operations
        is_homomorphism = uacalc_lib.alg.is_homomorphism
        
        # Alg0: f(x,y) = x (first projection)
        sym0 = OperationSymbol("f", 2, False)
        table0 = [0, 0, 1, 1]  # f(0,0)=0, f(0,1)=0, f(1,0)=1, f(1,1)=1
        op0 = Operations.make_int_operation(sym0, 2, table0)
        alg0 = BasicAlgebra("Alg0", [0, 1], [op0])
        
        # Alg1: f(x,y) = y (second projection)
        sym1 = OperationSymbol("f", 2, False)
        table1 = [0, 1, 0, 1]  # f(0,0)=0, f(0,1)=1, f(1,0)=0, f(1,1)=1
        op1 = Operations.make_int_operation(sym1, 2, table1)
        alg1 = BasicAlgebra("Alg1", [0, 1], [op1])
        
        # Identity map: 0 -> 0, 1 -> 1
        map = [0, 1]
        
        # Test Python implementation
        # Identity map is NOT a homomorphism from first projection to second projection
        # f(0,1) = 0 in alg0, so h(f(0,1)) = h(0) = 0
        # f(h(0), h(1)) = f(0, 1) = 1 in alg1
        # 0 != 1, so not a homomorphism
        result = is_homomorphism(map, alg0, alg1)
        assert result == False, "Identity map should not be a homomorphism for different operations"
    
    def test_is_homomorphism_wrong_map_size(self):
        """Test is_homomorphism with wrong map size (should raise error)."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        is_homomorphism = uacalc_lib.alg.is_homomorphism
        
        alg0 = BasicAlgebra("Alg0", [0, 1], [])
        alg1 = BasicAlgebra("Alg1", [0, 1], [])
        
        # Map with wrong size
        map = [0]  # Should be size 2
        
        # Test Python implementation - should raise ValueError
        with pytest.raises(Exception):  # ValueError or similar
            is_homomorphism(map, alg0, alg1)
    
    def test_jonsson_terms_single_element(self):
        """Test jonsson_terms with single element algebra."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        jonsson_terms = uacalc_lib.alg.jonsson_terms
        
        # Create single element algebra
        alg = BasicAlgebra("SingleElement", [0], [])
        
        # Test Python implementation
        result = jonsson_terms(alg)
        assert result is not None, "Single element algebra should have Jonsson terms"
        assert len(result) == 2, "Single element algebra should have 2 Jonsson terms"
    
    def test_jonsson_level_single_element(self):
        """Test jonsson_level with single element algebra."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        jonsson_level = uacalc_lib.alg.jonsson_level
        
        # Create single element algebra
        alg = BasicAlgebra("SingleElement", [0], [])
        
        # Test Python implementation
        result = jonsson_level(alg)
        assert result == 1, "Single element algebra should have Jonsson level 1"
    
    def test_jonsson_terms_with_algebra_file(self):
        """Test jonsson_terms with a real algebra file if available."""
        import uacalc_lib
        import os
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent.parent
        algebra_path = project_root / "resources" / "algebras" / "ba2.ua"
        
        if not algebra_path.exists():
            pytest.skip(f"Algebra file {algebra_path} not found")
        
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(str(algebra_path))
        alg = reader.read_algebra_file()
        
        jonsson_terms = uacalc_lib.alg.jonsson_terms
        
        # Test Python implementation
        result = jonsson_terms(alg)
        # Result may be None or a list of terms
        assert result is None or isinstance(result, list)
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("jonssonTerms", [
            "--algebra", str(algebra_path)
        ])
        
        assert java_result["success"] == True
        java_terms_found = java_result["data"].get("terms_found", False)
        python_terms_found = result is not None and len(result) > 0
        
        # Both should agree on whether terms exist
        assert python_terms_found == java_terms_found, \
            f"Terms existence mismatch: Python={python_terms_found}, Java={java_terms_found}"
        
        # If both found terms, count should match
        if python_terms_found and java_terms_found:
            java_count = java_result["data"].get("count", 0)
            python_count = len(result)
            assert python_count == java_count, \
                f"Term count mismatch: Python={python_count}, Java={java_count}"
    
    def test_jonsson_level_with_algebra_file(self):
        """Test jonsson_level with a real algebra file if available."""
        import uacalc_lib
        import os
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent.parent
        algebra_path = project_root / "resources" / "algebras" / "ba2.ua"
        
        if not algebra_path.exists():
            pytest.skip(f"Algebra file {algebra_path} not found")
        
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(str(algebra_path))
        alg = reader.read_algebra_file()
        
        jonsson_level = uacalc_lib.alg.jonsson_level
        
        # Test Python implementation
        python_result = jonsson_level(alg)
        assert isinstance(python_result, int)
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("jonssonLevel", [
            "--algebra", str(algebra_path)
        ])
        
        assert java_result["success"] == True
        java_level = java_result["data"].get("level", -1)
        
        assert python_result == java_level, \
            f"Jonsson level mismatch: Python={python_result}, Java={java_level}"

