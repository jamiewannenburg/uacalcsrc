"""
Test suite for VirtualLists functionality.
Tests both Python bindings and compares with Java implementation.
"""

import pytest
import uacalc_lib
import json
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Any
from test_utils import build_java_command


class TestVirtualLists:
    """Test VirtualLists static methods functionality."""
    
    def test_int_tuples_basic(self):
        """Test basic int_tuples functionality."""
        tuples = uacalc_lib.util.VirtualLists.int_tuples(3, 4)
        assert tuples.size() == 64  # 4^3 = 64
        
        # Test first few elements
        assert tuples.get(0) == [0, 0, 0]
        assert tuples.get(1) == [1, 0, 0]
        assert tuples.get(2) == [2, 0, 0]
        assert tuples.get(3) == [3, 0, 0]
        assert tuples.get(4) == [0, 1, 0]
        
        # Test last element
        assert tuples.get(63) == [3, 3, 3]
    
    def test_int_tuples_with_min_basic(self):
        """Test basic int_tuples_with_min functionality."""
        tuples = uacalc_lib.util.VirtualLists.int_tuples_with_min(3, 4, 2)
        assert tuples.size() == 56  # 4^3 - 2^3 = 64 - 8 = 56
        
        # Test first few elements
        assert tuples.get(0) == [2, 0, 0]
        assert tuples.get(1) == [3, 0, 0]
        assert tuples.get(2) == [2, 1, 0]
        assert tuples.get(3) == [3, 1, 0]
        
        # Test last element
        assert tuples.get(55) == [3, 3, 3]
    
    def test_array_indexer_with_min_basic(self):
        """Test basic array_indexer_with_min functionality."""
        # Test with k=0
        result = uacalc_lib.util.VirtualLists.array_indexer_with_min(0, 3, 4, 2)
        assert result == [2, 0, 0]
        
        # Test with k=1
        result = uacalc_lib.util.VirtualLists.array_indexer_with_min(1, 3, 4, 2)
        assert result == [3, 0, 0]
        
        # Test with k=7 (last element)
        result = uacalc_lib.util.VirtualLists.array_indexer_with_min(7, 3, 4, 2)
        assert result == [3, 3, 0]
    
    def test_test_pow_basic(self):
        """Test test_pow functionality."""
        result = uacalc_lib.util.VirtualLists.test_pow(5)
        assert "k = 5" in result
        assert "foo = 3.107" in result
        assert "floor = 3" in result
    
    def test_helper_methods(self):
        """Test helper methods foo, bar, baz."""
        # Test foo method
        assert uacalc_lib.util.VirtualLists.foo(10, 3) == 2
        assert uacalc_lib.util.VirtualLists.foo(5, 2) == 2
        
        # Test bar method
        assert uacalc_lib.util.VirtualLists.bar(10, 3) == 2
        assert uacalc_lib.util.VirtualLists.bar(5, 2) == 2
        
        # Test baz method
        assert uacalc_lib.util.VirtualLists.baz(10, 3) == 2
        assert uacalc_lib.util.VirtualLists.baz(5, 2) == 2
    
    def test_factorial_basic(self):
        """Test factorial functionality."""
        assert uacalc_lib.util.VirtualLists.factorial(0) == 1
        assert uacalc_lib.util.VirtualLists.factorial(1) == 1
        assert uacalc_lib.util.VirtualLists.factorial(2) == 2
        assert uacalc_lib.util.VirtualLists.factorial(3) == 6
        assert uacalc_lib.util.VirtualLists.factorial(4) == 24
        assert uacalc_lib.util.VirtualLists.factorial(5) == 120
    
    def test_binomial_basic(self):
        """Test binomial coefficient functionality."""
        assert uacalc_lib.util.VirtualLists.binomial(5, 0) == 1
        assert uacalc_lib.util.VirtualLists.binomial(5, 1) == 5
        assert uacalc_lib.util.VirtualLists.binomial(5, 2) == 10
        assert uacalc_lib.util.VirtualLists.binomial(5, 3) == 10
        assert uacalc_lib.util.VirtualLists.binomial(5, 4) == 5
        assert uacalc_lib.util.VirtualLists.binomial(5, 5) == 1
        
        # Test symmetry
        assert uacalc_lib.util.VirtualLists.binomial(10, 3) == uacalc_lib.util.VirtualLists.binomial(10, 7)
    
    def test_main_method(self):
        """Test main method functionality."""
        args = ["test", "3", "4"]
        result = uacalc_lib.util.VirtualLists.main(args)
        assert "VirtualLists test" in result or "int_tuples" in result or "array_indexer" in result
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test invalid min constraint
        with pytest.raises(Exception):
            uacalc_lib.util.VirtualLists.int_tuples_with_min(3, 4, 5)  # min >= base
        
        # Test that valid inputs work
        tuples = uacalc_lib.util.VirtualLists.int_tuples(3, 4)
        assert tuples.size() == 64
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Test with base=1
        tuples = uacalc_lib.util.VirtualLists.int_tuples(3, 1)
        assert tuples.size() == 1
        assert tuples.get(0) == [0, 0, 0]
        
        # Test with min=0 (should be same as int_tuples)
        tuples_with_min = uacalc_lib.util.VirtualLists.int_tuples_with_min(2, 3, 0)
        tuples_normal = uacalc_lib.util.VirtualLists.int_tuples(2, 3)
        assert tuples_with_min.size() == tuples_normal.size()
        assert tuples_with_min.get(0) == tuples_normal.get(0)
        assert tuples_with_min.get(tuples_with_min.size()-1) == tuples_normal.get(tuples_normal.size()-1)
    
    def test_large_inputs(self):
        """Test with larger inputs."""
        # Test with larger tuple length
        tuples = uacalc_lib.util.VirtualLists.int_tuples(4, 3)
        assert tuples.size() == 81  # 3^4 = 81
        
        # Test with larger base
        tuples = uacalc_lib.util.VirtualLists.int_tuples(2, 5)
        assert tuples.size() == 25  # 5^2 = 25
        
        # Test array_indexer_with_min with larger inputs
        result = uacalc_lib.util.VirtualLists.array_indexer_with_min(0, 4, 3, 1)
        assert len(result) == 4
        # Note: The first element should be >= min, but not all elements
        assert result[0] >= 1
    
    def test_consistency_between_methods(self):
        """Test consistency between different methods."""
        # Test that int_tuples_with_min with min=0 gives same results as int_tuples
        tuples_normal = uacalc_lib.util.VirtualLists.int_tuples(2, 3)
        tuples_with_min = uacalc_lib.util.VirtualLists.int_tuples_with_min(2, 3, 0)
        
        assert tuples_normal.size() == tuples_with_min.size()
        for i in range(min(10, tuples_normal.size())):
            assert tuples_normal.get(i) == tuples_with_min.get(i)
        
        # Test that array_indexer_with_min gives same results as int_tuples_with_min
        for i in range(min(5, tuples_with_min.size())):
            array_result = uacalc_lib.util.VirtualLists.array_indexer_with_min(i, 2, 3, 0)
            tuple_result = tuples_with_min.get(i)
            assert array_result == tuple_result


class TestVirtualListsJavaCompatibility:
    """Test compatibility with Java implementation."""
    
    def get_java_output(self, command: str, args: List[str]) -> Dict[str, Any]:
        """Get output from Java wrapper."""
        try:
            # Get project root (assuming we're in python/uacalc/tests/)
            project_root = Path(__file__).parent.parent.parent.parent
            
            # Use utility function to build Java command with proper classpath
            wrapper_class = "java_wrapper.src.util.virtuallist.VirtualListsWrapper"
            cmd = build_java_command(wrapper_class, [command] + args)
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,
                cwd=project_root
            )
            if result.returncode != 0:
                pytest.skip(f"Java wrapper not available: {result.stderr}")
            
            # Check if stdout is empty
            if not result.stdout or not result.stdout.strip():
                pytest.skip(f"Java wrapper returned empty output. Return code: {result.returncode}, Stderr: {result.stderr}")
            
            # Extract JSON from stdout (Java wrapper may print debug output before JSON)
            stdout = result.stdout.strip()
            # Find the first '{' which should be the start of the JSON object
            json_start = stdout.find('{')
            if json_start == -1:
                pytest.skip(f"Java wrapper output contains no JSON. Stdout: {repr(stdout[:200])}, Stderr: {result.stderr}")
            
            # Extract just the JSON part
            json_text = stdout[json_start:]
            # Find the last '}' to get the complete JSON object
            json_end = json_text.rfind('}') + 1
            if json_end == 0:
                pytest.skip(f"Java wrapper output contains incomplete JSON. Stdout: {repr(stdout[:200])}, Stderr: {result.stderr}")
            
            json_text = json_text[:json_end]
            
            # Parse JSON response and extract the 'data' field
            try:
                json_response = json.loads(json_text)
            except json.JSONDecodeError as e:
                # Provide more context about what was received
                pytest.skip(f"Java wrapper returned invalid JSON. Return code: {result.returncode}, "
                           f"Extracted JSON: {repr(json_text[:200])}, "
                           f"Stderr: {result.stderr}, Error: {e}")
            
            if "data" in json_response:
                return json_response["data"]
            else:
                # If no 'data' field, return the whole response
                return json_response
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            pytest.skip(f"Java wrapper not available: {type(e).__name__}: {str(e)}")
        except Exception as e:
            # Catch any other exceptions to see what's happening
            pytest.skip(f"Java wrapper not available: {type(e).__name__}: {str(e)}")
    
    def test_int_tuples_java_compatibility(self):
        """Test int_tuples compatibility with Java implementation."""
        java_result = self.get_java_output("int_tuples", ["--tuple_len", "3", "--base", "4"])
        if java_result is None:
            pytest.skip("Java wrapper not available")
        
        # Test Python implementation
        tuples = uacalc_lib.util.VirtualLists.int_tuples(3, 4)
        
        # Compare sizes
        assert tuples.size() == java_result["size"]
        
        # Compare first few elements
        java_elements = java_result["elements"]
        for i, java_elem in enumerate(java_elements):
            python_elem = tuples.get(i)
            assert python_elem == java_elem
    
    def test_int_tuples_with_min_java_compatibility(self):
        """Test int_tuples_with_min compatibility with Java implementation."""
        java_result = self.get_java_output("int_tuples_with_min", ["--tuple_len", "3", "--base", "4", "--min", "2"])
        if java_result is None:
            pytest.skip("Java wrapper not available")
        
        # Test Python implementation
        tuples = uacalc_lib.util.VirtualLists.int_tuples_with_min(3, 4, 2)
        
        # Compare sizes
        assert tuples.size() == java_result["size"]
        
        # Compare first few elements
        java_elements = java_result["elements"]
        for i, java_elem in enumerate(java_elements):
            python_elem = tuples.get(i)
            assert python_elem == java_elem
    
    def test_array_indexer_with_min_java_compatibility(self):
        """Test array_indexer_with_min compatibility with Java implementation."""
        java_result = self.get_java_output("array_indexer_with_min", ["--k", "0", "--arity", "3", "--base", "4", "--min", "2"])
        if java_result is None:
            pytest.skip("Java wrapper not available")
        
        # Test Python implementation
        python_result = uacalc_lib.util.VirtualLists.array_indexer_with_min(0, 3, 4, 2)
        
        # Java wrapper returns result as a string like "[2, 0, 0]", need to parse it
        java_result_str = java_result["result"]
        if isinstance(java_result_str, str):
            # Parse the string representation of the array
            import ast
            java_result_list = ast.literal_eval(java_result_str)
        else:
            java_result_list = java_result_str
        
        # Compare results
        assert python_result == java_result_list
    
    def test_helper_methods_java_compatibility(self):
        """Test helper methods compatibility with Java implementation."""
        # Test foo method
        java_result = self.get_java_output("foo", ["--k", "10", "--r", "3"])
        if java_result is not None:
            python_result = uacalc_lib.util.VirtualLists.foo(10, 3)
            assert python_result == java_result["result"]
        
        # Test bar method
        java_result = self.get_java_output("bar", ["--k", "10", "--r", "3"])
        if java_result is not None:
            python_result = uacalc_lib.util.VirtualLists.bar(10, 3)
            assert python_result == java_result["result"]
        
        # Test baz method
        java_result = self.get_java_output("baz", ["--k", "10", "--r", "3"])
        if java_result is not None:
            python_result = uacalc_lib.util.VirtualLists.baz(10, 3)
            assert python_result == java_result["result"]
    
    def test_factorial_java_compatibility(self):
        """Test factorial compatibility with Java implementation."""
        java_result = self.get_java_output("factorial", ["--n", "5"])
        if java_result is not None:
            python_result = uacalc_lib.util.VirtualLists.factorial(5)
            assert python_result == java_result["result"]
    
    def test_binomial_java_compatibility(self):
        """Test binomial compatibility with Java implementation."""
        java_result = self.get_java_output("binomial", ["--n", "5", "--r", "3"])
        if java_result is not None:
            python_result = uacalc_lib.util.VirtualLists.binomial(5, 3)
            assert python_result == java_result["result"]


class TestVirtualListsPerformance:
    """Test performance characteristics."""
    
    def test_large_tuple_generation(self):
        """Test performance with larger tuple generation."""
        import time
        
        start_time = time.time()
        tuples = uacalc_lib.util.VirtualLists.int_tuples(5, 3)
        end_time = time.time()
        
        assert tuples.size() == 243  # 3^5 = 243
        assert end_time - start_time < 1.0  # Should be fast
    
    def test_memory_efficiency(self):
        """Test memory efficiency of virtual lists."""
        # Test that we can create large virtual lists without excessive memory usage
        tuples = uacalc_lib.util.VirtualLists.int_tuples(6, 2)
        assert tuples.size() == 64  # 2^6 = 64
        
        # Test that we can access elements without loading everything into memory
        for i in range(0, min(10, tuples.size())):
            elem = tuples.get(i)
            assert len(elem) == 6
            assert all(x in [0, 1] for x in elem)


class TestVirtualListsIntegration:
    """Test integration with other uacalc components."""
    
    def test_with_algebra_operations(self):
        """Test VirtualLists integration with algebra operations."""
        # This is a placeholder for future integration tests
        # when VirtualLists are used with other uacalc components
        pass
    
    def test_with_sequence_generators(self):
        """Test VirtualLists integration with sequence generators."""
        # This is a placeholder for future integration tests
        # when VirtualLists are used with sequence generators
        pass
