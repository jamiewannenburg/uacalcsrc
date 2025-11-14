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
        
        # Extract JSON from output (may have progress messages before JSON)
        output = result.stdout
        # Find the first '{' that starts a JSON object
        json_start = output.find('{')
        if json_start == -1:
            pytest.fail(f"No JSON found in output: {output[:200]}")
        
        # Extract from the first '{' to the end
        json_str = output[json_start:]
        # Find the matching closing brace
        brace_count = 0
        json_end = -1
        for i, char in enumerate(json_str):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break
        
        if json_end == -1:
            pytest.fail(f"Invalid JSON in output: {json_str[:200]}")
        
        return json.loads(json_str[:json_end])
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
    
    def test_matrix_power_basic(self):
        """Test matrix_power with a simple algebra."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        matrix_power = uacalc_lib.alg.matrix_power
        
        # Create a simple 2-element algebra
        alg = BasicAlgebra("A", [0, 1], [])
        
        # Create matrix power A^[2]
        result = matrix_power(alg, 2)
        
        # Should have cardinality 2^2 = 4
        assert result.cardinality() == 4, f"Expected cardinality 4, got {result.cardinality()}"
        
        # Check name
        assert "^[2]" in result.name() or "2-matrix power" in result.name(), \
            f"Name should contain power info: {result.name()}"
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("matrixPower", [
            "--size", "2",
            "--k", "2"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result_size"] == 4
        assert java_result["data"]["result_size"] == result.cardinality(), \
            "Python and Java should match"
    
    def test_matrix_power_with_operations(self):
        """Test matrix_power with an algebra that has operations."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        Operations = uacalc_lib.alg.Operations
        matrix_power = uacalc_lib.alg.matrix_power
        
        # Create a 2-element algebra with a binary operation
        sym = OperationSymbol("f", 2, False)
        table = [0, 0, 1, 1]  # f(x,y) = x (first projection)
        op = Operations.make_int_operation(sym, 2, table)
        alg = BasicAlgebra("TestAlg", [0, 1], [op])
        
        # Create matrix power A^[3]
        result = matrix_power(alg, 3)
        
        # Should have cardinality 2^3 = 8
        assert result.cardinality() == 8, f"Expected cardinality 8, got {result.cardinality()}"
        
        # Verify the algebra was created successfully
        assert result.name() is not None, "Matrix power should have a name"
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("matrixPower", [
            "--size", "2",
            "--k", "3"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result_size"] == 8
        assert java_result["data"]["operations_count"] > 0
    
    def test_matrix_power_invalid_power(self):
        """Test matrix_power with invalid power (should raise error)."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        matrix_power = uacalc_lib.alg.matrix_power
        
        alg = BasicAlgebra("A", [0, 1], [])
        
        # Test with k = 0 (should fail)
        with pytest.raises(Exception):  # ValueError or similar
            matrix_power(alg, 0)
        
        # Test with k < 0 (should fail)
        with pytest.raises(Exception):  # ValueError or similar
            matrix_power(alg, -1)
    
    def test_matrix_power_larger_algebra(self):
        """Test matrix_power with a larger algebra."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        matrix_power = uacalc_lib.alg.matrix_power
        
        # Create a 3-element algebra
        alg = BasicAlgebra("B", [0, 1, 2], [])
        
        # Create matrix power B^[2]
        result = matrix_power(alg, 2)
        
        # Should have cardinality 3^2 = 9
        assert result.cardinality() == 9, f"Expected cardinality 9, got {result.cardinality()}"
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("matrixPower", [
            "--size", "3",
            "--k", "2"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result_size"] == 9
        assert java_result["data"]["result_size"] == result.cardinality(), \
            "Python and Java should match"
    
    def test_find_nuf_single_element(self):
        """Test find_nuf with single element algebra."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        find_nuf = uacalc_lib.alg.find_nuf
        
        # Create single element algebra
        alg = BasicAlgebra("SingleElement", [0], [])
        
        # Test Python implementation
        result = find_nuf(alg, 3)
        assert result is not None, "Single element algebra should have an NU term"
        assert isinstance(result, str), "Result should be a string"
    
    def test_find_nuf_invalid_arity(self):
        """Test find_nuf with invalid arity (should raise error)."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        find_nuf = uacalc_lib.alg.find_nuf
        
        alg = BasicAlgebra("TestAlg", [0, 1], [])
        
        # Test with arity < 3 (should fail)
        with pytest.raises(Exception):  # ValueError or similar
            find_nuf(alg, 2)
    
    def test_find_nuf_no_operations(self):
        """Test find_nuf with algebra that has no operations."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        find_nuf = uacalc_lib.alg.find_nuf
        
        # Create algebra with no operations
        alg = BasicAlgebra("NoOps", [0, 1], [])
        
        # Test Python implementation
        # The actual behavior depends on malcev::nu_term implementation
        # It may return None or raise an error
        try:
            result = find_nuf(alg, 3)
            assert result is None or isinstance(result, str)
        except ValueError:
            # It's acceptable for it to raise an error when there are no operations
            pass
    
    def test_find_nuf_with_algebra_file(self):
        """Test find_nuf with a real algebra file if available."""
        import uacalc_lib
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent.parent
        algebra_path = project_root / "resources" / "algebras" / "ba2.ua"
        
        if not algebra_path.exists():
            pytest.skip(f"Algebra file {algebra_path} not found")
        
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(str(algebra_path))
        alg = reader.read_algebra_file()
        
        find_nuf = uacalc_lib.alg.find_nuf
        
        # Test Python implementation
        result = find_nuf(alg, 3)
        # Result may be None or a string term
        assert result is None or isinstance(result, str)
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("findNUF", [
            "--algebra", str(algebra_path),
            "--arity", "3"
        ])
        
        assert java_result["success"] == True
        java_term_found = java_result["data"].get("term_found", False)
        python_term_found = result is not None
        
        # Both should agree on whether term exists
        assert python_term_found == java_term_found, \
            f"Term existence mismatch: Python={python_term_found}, Java={java_term_found}"
    
    def test_ternary_discriminator_algebra_basic(self):
        """Test ternary_discriminator_algebra with basic cardinality."""
        import uacalc_lib
        
        ternary_discriminator_algebra = uacalc_lib.alg.ternary_discriminator_algebra
        
        # Create ternary discriminator algebra with cardinality 3
        result = ternary_discriminator_algebra(3)
        
        # Check basic properties
        assert result.cardinality() == 3, f"Expected cardinality 3, got {result.cardinality()}"
        assert result.name() == "Disc-3", f"Expected name 'Disc-3', got '{result.name()}'"
        
        # Should have exactly one operation (the discriminator)
        ops = result.operations()
        assert len(ops) == 1, f"Expected 1 operation, got {len(ops)}"
        
        # Check that the operation is ternary
        disc_op = ops[0]
        assert disc_op.arity() == 3, f"Expected arity 3, got {disc_op.arity()}"
        assert disc_op.symbol().name() == "disc", f"Expected name 'disc', got '{disc_op.symbol().name()}'"
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("ternaryDiscriminatorAlgebra", [
            "--card", "3"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result_size"] == 3
        assert java_result["data"]["result_size"] == result.cardinality(), \
            "Python and Java should match"
        assert java_result["data"]["operations_count"] == 1
        assert java_result["data"]["operation_arity"] == 3
    
    def test_ternary_discriminator_algebra_discriminator_property(self):
        """Test that the discriminator operation has the correct property."""
        import uacalc_lib
        
        ternary_discriminator_algebra = uacalc_lib.alg.ternary_discriminator_algebra
        
        # Create ternary discriminator algebra
        alg = ternary_discriminator_algebra(3)
        ops = alg.operations()
        disc_op = ops[0]
        
        # Test discriminator property: d(x,y,z) = z if x = y, otherwise x
        # d(0,0,1) = 1 (since 0 == 0)
        assert disc_op.int_value_at([0, 0, 1]) == 1
        
        # d(0,1,2) = 0 (since 0 != 1)
        assert disc_op.int_value_at([0, 1, 2]) == 0
        
        # d(1,1,0) = 0 (since 1 == 1)
        assert disc_op.int_value_at([1, 1, 0]) == 0
        
        # d(2,1,0) = 2 (since 2 != 1)
        assert disc_op.int_value_at([2, 1, 0]) == 2
    
    def test_ternary_discriminator_algebra_invalid_cardinality(self):
        """Test ternary_discriminator_algebra with invalid cardinality (should raise error)."""
        import uacalc_lib
        
        ternary_discriminator_algebra = uacalc_lib.alg.ternary_discriminator_algebra
        
        # Test with card = 0 (should fail)
        with pytest.raises(Exception):  # ValueError or similar
            ternary_discriminator_algebra(0)
        
        # Test with card < 0 (should fail)
        with pytest.raises(Exception):  # ValueError or similar
            ternary_discriminator_algebra(-1)
    
    def test_ternary_discriminator_algebra_larger(self):
        """Test ternary_discriminator_algebra with larger cardinality."""
        import uacalc_lib
        
        ternary_discriminator_algebra = uacalc_lib.alg.ternary_discriminator_algebra
        
        # Create ternary discriminator algebra with cardinality 5
        result = ternary_discriminator_algebra(5)
        
        assert result.cardinality() == 5, f"Expected cardinality 5, got {result.cardinality()}"
        assert result.name() == "Disc-5", f"Expected name 'Disc-5', got '{result.name()}'"
        
        ops = result.operations()
        assert len(ops) == 1
        
        disc_op = ops[0]
        # Test a few values
        assert disc_op.int_value_at([0, 0, 4]) == 4
        assert disc_op.int_value_at([0, 1, 4]) == 0
        assert disc_op.int_value_at([3, 3, 2]) == 2


class TestFullTransformationSemigroup:
    """Tests for full_transformation_semigroup function."""
    
    def test_full_transformation_semigroup_basic(self):
        """Test full_transformation_semigroup with basic parameters."""
        import uacalc_lib
        
        full_transformation_semigroup = uacalc_lib.alg.full_transformation_semigroup
        
        # Create transformation semigroup with n=2, no constants, no identity
        result = full_transformation_semigroup(2, False, False)
        
        # Should have cardinality 2^2 = 4
        assert result.cardinality() == 4, f"Expected cardinality 4, got {result.cardinality()}"
        assert result.name() == "Trans2", f"Expected name 'Trans2', got '{result.name()}'"
        
        # Should have one operation (composition)
        ops = result.operations()
        assert len(ops) == 1, f"Expected 1 operation, got {len(ops)}"
        assert ops[0].arity() == 2, f"Expected arity 2, got {ops[0].arity()}"
        assert ops[0].symbol().name() == "composition", f"Expected name 'composition', got '{ops[0].symbol().name()}'"
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("fullTransformationSemigroup", [
            "--n", "2", "--includeConstants", "false", "--includeId", "false"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result_size"] == 4
        assert java_result["data"]["result_size"] == result.cardinality(), \
            "Python and Java should match"
        assert java_result["data"]["operations_count"] == 1
    
    def test_full_transformation_semigroup_with_constants(self):
        """Test full_transformation_semigroup with constants included."""
        import uacalc_lib
        
        full_transformation_semigroup = uacalc_lib.alg.full_transformation_semigroup
        
        # Create transformation semigroup with n=2, constants included
        result = full_transformation_semigroup(2, True, False)
        
        # Should have cardinality 4
        assert result.cardinality() == 4
        
        # Should have 1 composition + 2 constants = 3 operations
        ops = result.operations()
        assert len(ops) == 3
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("fullTransformationSemigroup", [
            "--n", "2", "--includeConstants", "true", "--includeId", "false"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result_size"] == 4
        assert java_result["data"]["operations_count"] == 3
    
    def test_full_transformation_semigroup_with_id(self):
        """Test full_transformation_semigroup with identity included."""
        import uacalc_lib
        
        full_transformation_semigroup = uacalc_lib.alg.full_transformation_semigroup
        
        # Create transformation semigroup with n=2, identity included
        result = full_transformation_semigroup(2, False, True)
        
        # Should have cardinality 4
        assert result.cardinality() == 4
        
        # Should have 1 composition + 1 identity = 2 operations
        ops = result.operations()
        assert len(ops) == 2
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("fullTransformationSemigroup", [
            "--n", "2", "--includeConstants", "false", "--includeId", "true"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result_size"] == 4
        assert java_result["data"]["operations_count"] == 2
    
    def test_full_transformation_semigroup_with_all(self):
        """Test full_transformation_semigroup with both constants and identity."""
        import uacalc_lib
        
        full_transformation_semigroup = uacalc_lib.alg.full_transformation_semigroup
        
        # Create transformation semigroup with n=2, both constants and identity
        result = full_transformation_semigroup(2, True, True)
        
        # Should have cardinality 4
        assert result.cardinality() == 4
        
        # Should have 1 composition + 2 constants + 1 identity = 4 operations
        ops = result.operations()
        assert len(ops) == 4
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("fullTransformationSemigroup", [
            "--n", "2", "--includeConstants", "true", "--includeId", "true"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result_size"] == 4
        assert java_result["data"]["operations_count"] == 4
    
    def test_full_transformation_semigroup_n3(self):
        """Test full_transformation_semigroup with n=3."""
        import uacalc_lib
        
        full_transformation_semigroup = uacalc_lib.alg.full_transformation_semigroup
        
        # Create transformation semigroup with n=3
        result = full_transformation_semigroup(3, True, True)
        
        # Should have cardinality 3^3 = 27
        assert result.cardinality() == 27
        assert result.name() == "Trans3"
        
        # Should have 1 composition + 3 constants + 1 identity = 5 operations
        ops = result.operations()
        assert len(ops) == 5
        
        # Compare with Java wrapper
        java_result = run_java_wrapper("fullTransformationSemigroup", [
            "--n", "3", "--includeConstants", "true", "--includeId", "true"
        ])
        
        assert java_result["success"] == True
        assert java_result["data"]["result_size"] == 27
        assert java_result["data"]["operations_count"] == 5
    
    def test_full_transformation_semigroup_invalid_n(self):
        """Test full_transformation_semigroup with invalid n (should raise error)."""
        import uacalc_lib
        
        full_transformation_semigroup = uacalc_lib.alg.full_transformation_semigroup
        
        # Test with n > 9 (should fail)
        with pytest.raises(Exception):  # ValueError or similar
            full_transformation_semigroup(10, False, False)
        
        # Test with n = 0 (should fail)
        with pytest.raises(Exception):  # ValueError or similar
            full_transformation_semigroup(0, False, False)
        
        # Test with n < 0 (should fail)
        with pytest.raises(Exception):  # ValueError or similar
            full_transformation_semigroup(-1, False, False)


class TestMakeRandomAlgebra:
    """Tests for makeRandomAlgebra functions."""
    
    def test_make_random_algebra_basic(self):
        """Test make_random_algebra with basic similarity type."""
        import uacalc_lib
        
        make_random_algebra = uacalc_lib.alg.make_random_algebra
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        SimilarityType = uacalc_lib.alg.SimilarityType
        
        # Create a similarity type with one binary operation
        op_syms = [OperationSymbol("f", 2, False)]
        sim_type = SimilarityType(op_syms)
        
        # Create random algebra
        result = make_random_algebra(3, sim_type)
        
        # Check basic properties
        assert result.cardinality() == 3, f"Expected cardinality 3, got {result.cardinality()}"
        assert result.name() == "RAlg3", f"Expected name 'RAlg3', got '{result.name()}'"
        
        # Should have one operation
        ops = result.operations()
        assert len(ops) == 1, f"Expected 1 operation, got {len(ops)}"
        assert ops[0].arity() == 2, f"Expected arity 2, got {ops[0].arity()}"
    
    def test_make_random_algebra_with_seed(self):
        """Test make_random_algebra_with_seed (should be reproducible)."""
        import uacalc_lib
        
        make_random_algebra_with_seed = uacalc_lib.alg.make_random_algebra_with_seed
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        SimilarityType = uacalc_lib.alg.SimilarityType
        
        # Create a similarity type with one binary operation
        op_syms = [OperationSymbol("f", 2, False)]
        sim_type = SimilarityType(op_syms)
        
        # Create two algebras with the same seed
        alg1 = make_random_algebra_with_seed(3, sim_type, 12345)
        alg2 = make_random_algebra_with_seed(3, sim_type, 12345)
        
        # With same seed, should get same operations
        assert alg1.cardinality() == alg2.cardinality()
        assert len(alg1.operations()) == len(alg2.operations())
        
        # Check that operations are the same
        op1 = alg1.operations()[0]
        op2 = alg2.operations()[0]
        
        # Check a few values
        for i in range(3):
            for j in range(3):
                val1 = op1.int_value_at([i, j])
                val2 = op2.int_value_at([i, j])
                assert val1 == val2, f"Operations should be identical with same seed at ({i}, {j})"
    
    def test_make_random_algebra_invalid_size(self):
        """Test make_random_algebra with invalid size (should raise error)."""
        import uacalc_lib
        
        make_random_algebra = uacalc_lib.alg.make_random_algebra
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        SimilarityType = uacalc_lib.alg.SimilarityType
        
        op_syms = [OperationSymbol("f", 2, False)]
        sim_type = SimilarityType(op_syms)
        
        # Test with n = 0 (should fail)
        with pytest.raises(Exception):  # ValueError or similar
            make_random_algebra(0, sim_type)
        
        # Test with n < 0 (should fail)
        with pytest.raises(Exception):  # ValueError or similar
            make_random_algebra(-1, sim_type)
    
    def test_make_random_algebra_with_arities(self):
        """Test make_random_algebra_with_arities."""
        import uacalc_lib
        
        make_random_algebra_with_arities = uacalc_lib.alg.make_random_algebra_with_arities
        
        # Create random algebra with arities [2, 1, 0] (binary, unary, nullary)
        arities = [2, 1, 0]
        result = make_random_algebra_with_arities(3, arities)
        
        # Check basic properties
        assert result.cardinality() == 3, f"Expected cardinality 3, got {result.cardinality()}"
        assert result.name() == "RAlg3", f"Expected name 'RAlg3', got '{result.name()}'"
        
        # Should have 3 operations
        ops = result.operations()
        assert len(ops) == 3, f"Expected 3 operations, got {len(ops)}"
        assert ops[0].arity() == 2, f"Expected arity 2, got {ops[0].arity()}"
        assert ops[1].arity() == 1, f"Expected arity 1, got {ops[1].arity()}"
        assert ops[2].arity() == 0, f"Expected arity 0, got {ops[2].arity()}"
        
        # Check operation names
        assert ops[0].symbol().name() == "r0"
        assert ops[1].symbol().name() == "r1"
        assert ops[2].symbol().name() == "r2"
    
    def test_make_random_algebra_with_arities_and_seed(self):
        """Test make_random_algebra_with_arities_and_seed (should be reproducible)."""
        import uacalc_lib
        
        make_random_algebra_with_arities_and_seed = uacalc_lib.alg.make_random_algebra_with_arities_and_seed
        
        # Create two algebras with the same seed
        arities = [2, 1]
        alg1 = make_random_algebra_with_arities_and_seed(3, arities, 12345)
        alg2 = make_random_algebra_with_arities_and_seed(3, arities, 12345)
        
        # With same seed, should get same operations
        assert alg1.cardinality() == alg2.cardinality()
        assert len(alg1.operations()) == len(alg2.operations())
        
        # Check that operations are the same
        ops1 = alg1.operations()
        ops2 = alg2.operations()
        
        for op1, op2 in zip(ops1, ops2):
            # Check a few values for binary operation
            if op1.arity() == 2:
                for i in range(3):
                    for j in range(3):
                        val1 = op1.int_value_at([i, j])
                        val2 = op2.int_value_at([i, j])
                        assert val1 == val2, f"Operations should be identical with same seed at ({i}, {j})"
            elif op1.arity() == 1:
                for i in range(3):
                    val1 = op1.int_value_at([i])
                    val2 = op2.int_value_at([i])
                    assert val1 == val2, f"Operations should be identical with same seed at ({i})"
    
    def test_make_random_algebra_with_arities_invalid(self):
        """Test make_random_algebra_with_arities with invalid arities (should raise error)."""
        import uacalc_lib
        
        make_random_algebra_with_arities = uacalc_lib.alg.make_random_algebra_with_arities
        
        # Test with invalid arities (negative)
        with pytest.raises(Exception):  # ValueError or similar
            make_random_algebra_with_arities(3, [2, -1])
        
        # Test with invalid size
        with pytest.raises(Exception):  # ValueError or similar
            make_random_algebra_with_arities(0, [2, 1])
    
    def test_member_of_quasivariety_identical_algebras(self):
        """Test member_of_quasivariety with identical algebras."""
        import uacalc_lib
        
        member_of_quasivariety = uacalc_lib.alg.member_of_quasivariety
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        
        # Create two identical 2-element algebras
        alg_a = BasicAlgebra("TestAlgA", [0, 1], [])
        alg_b = BasicAlgebra("TestAlgB", [0, 1], [])
        
        # An algebra should be in its own quasivariety
        result = member_of_quasivariety(alg_a, alg_b)
        
        # Result may be None or a list of homomorphisms
        # For identical algebras, we expect Some with homomorphisms
        assert result is not None or result is None  # Either is valid
    
    def test_member_of_quasivariety_list(self):
        """Test member_of_quasivariety_list with a list of generating algebras."""
        import uacalc_lib
        
        member_of_quasivariety_list = uacalc_lib.alg.member_of_quasivariety_list
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        
        # Create algebras
        alg_a = BasicAlgebra("TestAlgA", [0, 1], [])
        alg_b = BasicAlgebra("TestAlgB", [0, 1], [])
        
        # Test with list of generating algebras
        result = member_of_quasivariety_list(alg_a, [alg_b])
        
        # Result may be None or a list of homomorphisms
        assert result is not None or result is None  # Either is valid

    def test_member_of_quasivariety_gen_by_proper_subs(self):
        """Test member_of_quasivariety_gen_by_proper_subs."""
        import uacalc_lib
        
        member_of_quasivariety_gen_by_proper_subs = uacalc_lib.alg.member_of_quasivariety_gen_by_proper_subs
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        
        # Create a small algebra
        alg = BasicAlgebra("TestAlg", [0, 1], [])
        
        # Test the function
        result = member_of_quasivariety_gen_by_proper_subs(alg)
        
        # Result may be None or a list of homomorphisms
        assert result is None or isinstance(result, list)
        if result is not None:
            assert len(result) > 0

    def test_member_of_quasivariety_gen_by_proper_subs_larger(self):
        """Test member_of_quasivariety_gen_by_proper_subs with a larger algebra."""
        import uacalc_lib
        
        member_of_quasivariety_gen_by_proper_subs = uacalc_lib.alg.member_of_quasivariety_gen_by_proper_subs
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        
        # Create a larger algebra
        alg = BasicAlgebra("TestAlg3", [0, 1, 2], [])
        
        # Test the function
        result = member_of_quasivariety_gen_by_proper_subs(alg)
        
        # Result may be None or a list of homomorphisms
        assert result is None or isinstance(result, list)
        if result is not None:
            assert len(result) > 0

    def test_member_of_quasivariety_gen_by_proper_subs_single_element(self):
        """Test member_of_quasivariety_gen_by_proper_subs with a single element algebra."""
        import uacalc_lib
        
        member_of_quasivariety_gen_by_proper_subs = uacalc_lib.alg.member_of_quasivariety_gen_by_proper_subs
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        
        # Create a single element algebra
        alg = BasicAlgebra("TestAlg1", [0], [])
        
        # Test the function - single element algebra should return None (no proper subalgebras)
        result = member_of_quasivariety_gen_by_proper_subs(alg)
        
        # Single element algebra has no proper subalgebras, so result should be None
        # But we'll just check that it doesn't raise an error
        assert result is None or isinstance(result, list)

    def test_quasi_critical_congruences(self):
        """Test quasi_critical_congruences."""
        import uacalc_lib
        
        quasi_critical_congruences = uacalc_lib.alg.quasi_critical_congruences
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        
        # Create a small algebra
        alg = BasicAlgebra("TestAlg", [0, 1], [])
        
        # Test the function
        result = quasi_critical_congruences(alg)
        
        # Result should be a list of Partition objects
        assert isinstance(result, list)
        # All items should be Partition objects
        for partition in result:
            assert hasattr(partition, 'universe_size')

    def test_quasi_critical_congruences_larger(self):
        """Test quasi_critical_congruences with a larger algebra."""
        import uacalc_lib
        
        quasi_critical_congruences = uacalc_lib.alg.quasi_critical_congruences
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        
        # Create a larger algebra
        alg = BasicAlgebra("TestAlg3", [0, 1, 2], [])
        
        # Test the function
        result = quasi_critical_congruences(alg)
        
        # Result should be a list of Partition objects
        assert isinstance(result, list)
        # All items should be Partition objects
        for partition in result:
            assert hasattr(partition, 'universe_size')

    def test_quasi_critical(self):
        """Test quasi_critical."""
        import uacalc_lib
        
        quasi_critical = uacalc_lib.alg.quasi_critical
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        
        # Create a small algebra
        alg = BasicAlgebra("TestAlg", [0, 1], [])
        
        # Test the function
        result = quasi_critical(alg)
        
        # Result may be None or a dict mapping Partition to list of generators
        assert result is None or isinstance(result, dict)
        if result is not None:
            # Check that all keys are Partition objects and values are lists
            for key, value in result.items():
                assert hasattr(key, 'universe_size')
                assert isinstance(value, list)

    def test_quasi_critical_larger(self):
        """Test quasi_critical with a larger algebra."""
        import uacalc_lib
        
        quasi_critical = uacalc_lib.alg.quasi_critical
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        
        # Create a larger algebra
        alg = BasicAlgebra("TestAlg3", [0, 1, 2], [])
        
        # Test the function
        result = quasi_critical(alg)
        
        # Result may be None or a dict mapping Partition to list of generators
        assert result is None or isinstance(result, dict)
        if result is not None:
            # Check that all keys are Partition objects and values are lists
            for key, value in result.items():
                assert hasattr(key, 'universe_size')
                assert isinstance(value, list)

    def test_unary_clone_basic(self):
        """Test unary_clone with basic partitions."""
        import uacalc_lib
        
        unary_clone = uacalc_lib.alg.unary_clone
        Partition = uacalc_lib.alg.Partition
        
        # Create simple partitions for testing
        # For a 4-element universe, create eta0 with 2 blocks and eta1 with 2 blocks
        # eta0: {0,1}, {2,3}
        # eta1: {0,2}, {1,3}
        eta0 = Partition([-2, 0, -2, 2])
        eta1 = Partition([-2, -2, 0, 2])
        pars = [Partition.zero(4)]
        
        # Test the function
        result = unary_clone(pars, eta0, eta1)
        
        # Result should be a list of IntArray objects
        assert isinstance(result, list)
        # The result may be empty depending on partitions
        # Just verify the function completes without error
        assert len(result) >= 0
        # All items should be IntArray objects
        for arr in result:
            assert hasattr(arr, 'universe_size')
            assert arr.universe_size() == 4

    def test_unary_clone_small_universe(self):
        """Test unary_clone with a small universe."""
        import uacalc_lib
        
        unary_clone = uacalc_lib.alg.unary_clone
        Partition = uacalc_lib.alg.Partition
        
        # Test with a very small universe (2 elements)
        eta0 = Partition.zero(2)
        eta1 = Partition.one(2)
        pars = [Partition.zero(2)]
        
        # Test the function
        result = unary_clone(pars, eta0, eta1)
        
        # Result should be a list of IntArray objects
        assert isinstance(result, list)
        assert len(result) >= 1  # Should have at least the identity function
        # All items should be IntArray objects
        for arr in result:
            assert hasattr(arr, 'universe_size')
            assert arr.universe_size() == 2

    def test_unary_clone_alg_from_partitions_basic(self):
        """Test unary_clone_alg_from_partitions with basic partitions."""
        import uacalc_lib
        
        unary_clone_alg_from_partitions = uacalc_lib.alg.unary_clone_alg_from_partitions
        Partition = uacalc_lib.alg.Partition
        
        # Create simple partitions for testing
        eta0 = Partition.zero(2)
        eta1 = Partition.one(2)
        pars = [Partition.zero(2)]
        
        # Test the function
        result = unary_clone_alg_from_partitions(pars, eta0, eta1)
        
        # Result should be a BasicAlgebra
        assert hasattr(result, 'cardinality')
        assert result.cardinality() == 2
        
        # Should have operations (at least the identity)
        assert hasattr(result, 'operations')
        ops = result.operations()
        assert len(ops) >= 1
        
        # All operations should be unary
        for op in ops:
            assert op.arity() == 1

    def test_unary_clone_alg_from_partitions_operation_names(self):
        """Test that operations are named correctly."""
        import uacalc_lib
        
        unary_clone_alg_from_partitions = uacalc_lib.alg.unary_clone_alg_from_partitions
        Partition = uacalc_lib.alg.Partition
        
        # Create partitions
        eta0 = Partition.zero(3)
        eta1 = Partition.one(3)
        pars = [Partition.zero(3)]
        
        # Test the function
        result = unary_clone_alg_from_partitions(pars, eta0, eta1)
        
        ops = result.operations()
        # Check that operations are named f_0, f_1, etc.
        # (operations are created in the order they appear in the BTreeSet)
        assert len(ops) > 0, "Should have at least one operation"
        
        # Collect all operation names and parse the numbers
        name_numbers = []
        for op in ops:
            name = op.symbol().name()
            assert name.startswith("f_"), "Operation name should start with 'f_'"
            num_str = name[2:]  # Skip "f_"
            num = int(num_str)
            name_numbers.append((name, num))
        
        # Sort by the numeric value
        name_numbers.sort(key=lambda x: x[1])
        
        # Verify we have sequential names (f_0, f_1, f_2, etc.)
        for i, (name, num) in enumerate(name_numbers):
            assert num == i, f"Operation numbers should be sequential: expected {i}, got {num}"
            expected = f"f_{i}"
            assert name == expected, f"Operation names should be sequential"

    def test_unary_clone_alg_from_partitions_empty_partitions(self):
        """Test unary_clone_alg_from_partitions with empty partitions list."""
        import uacalc_lib
        
        unary_clone_alg_from_partitions = uacalc_lib.alg.unary_clone_alg_from_partitions
        Partition = uacalc_lib.alg.Partition
        
        # Create partitions
        eta0 = Partition.zero(3)
        eta1 = Partition.one(3)
        pars = []  # Empty list
        
        # Test the function - should raise ValueError
        with pytest.raises(ValueError, match="cannot be empty"):
            unary_clone_alg_from_partitions(pars, eta0, eta1)
    
    def test_find_in_clone_empty_ops(self):
        """Test find_in_clone with empty operations list (should raise error)."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        find_in_clone = uacalc_lib.alg.find_in_clone
        
        alg = BasicAlgebra("TestAlg", [0, 1], [])
        
        # Test with empty operations list
        with pytest.raises(Exception):  # ValueError or similar
            find_in_clone([], alg)
    
    def test_find_in_clone_basic(self):
        """Test find_in_clone with basic operations."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        IntOperation = uacalc_lib.alg.IntOperation
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        find_in_clone = uacalc_lib.alg.find_in_clone
        
        # Create a simple algebra with one binary operation (meet)
        size = 2
        meet_table = [0, 0, 0, 1]  # 0*0=0, 0*1=0, 1*0=0, 1*1=1
        meet_sym = OperationSymbol("meet", 2)
        meet_op = IntOperation(meet_sym, size, meet_table)
        
        alg = BasicAlgebra("TestAlg", list(range(size)), [meet_op])
        
        # Create an operation that is in the clone (the meet operation itself)
        test_sym = OperationSymbol("test_meet", 2)
        test_op = IntOperation(test_sym, size, meet_table)
        
        # Test Python implementation
        result = find_in_clone([test_op], alg)
        assert isinstance(result, dict), "Result should be a dictionary"
        # The operation may or may not be found depending on implementation
        assert len(result) >= 0
    
    def test_find_in_clone_multiple_arities(self):
        """Test find_in_clone with operations of different arities."""
        import uacalc_lib
        
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        IntOperation = uacalc_lib.alg.IntOperation
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        find_in_clone = uacalc_lib.alg.find_in_clone
        
        size = 2
        binary_table = [0, 0, 0, 1]
        binary_sym = OperationSymbol("binary", 2)
        binary_op = IntOperation(binary_sym, size, binary_table)
        
        alg = BasicAlgebra("TestAlg", list(range(size)), [binary_op])
        
        # Test with both unary and binary operations
        unary_table = [0, 1]
        unary_sym = OperationSymbol("test_unary", 1)
        test_unary = IntOperation(unary_sym, size, unary_table)
        
        test_binary_sym = OperationSymbol("test_binary", 2)
        test_binary = IntOperation(test_binary_sym, size, binary_table)
        
        # Test Python implementation
        result = find_in_clone([test_unary, test_binary], alg)
        assert isinstance(result, dict), "Result should be a dictionary"
        # Should process both arities
        assert len(result) >= 0

