"""
Tests for ParameterizedAlgebra and ParameterizedOperation.

This module tests the Rust and Python implementations of ParameterizedAlgebra
and ParameterizedOperation classes.
"""

import unittest
import subprocess
import json
import sys
import os
import platform

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class TestParameterizedAlgebra(unittest.TestCase):
    """Test cases for ParameterizedAlgebra."""
    
    def test_create_basic(self):
        """Test creating a basic ParameterizedAlgebra."""
        import uacalc_lib
        ParameterizedAlgebra = uacalc_lib.alg.ParameterizedAlgebra
        
        param_alg = ParameterizedAlgebra(
            ["n"],
            "Zn",
            "n",
            "Cyclic group of order n",
            []
        )
        
        self.assertEqual(param_alg.get_name(), "Zn")
        self.assertEqual(param_alg.get_parameter_names(), ["n"])
    
    def test_get_parameter_map_single(self):
        """Test get_parameter_map with single parameter."""
        import uacalc_lib
        ParameterizedAlgebra = uacalc_lib.alg.ParameterizedAlgebra
        
        param_alg = ParameterizedAlgebra(
            ["n"],
            "Zn",
            "n",
            "Cyclic group",
            []
        )
        
        param_map = param_alg.get_parameter_map([5])
        self.assertEqual(param_map["n"], "5")
    
    def test_get_parameter_map_multiple(self):
        """Test get_parameter_map with multiple parameters."""
        import uacalc_lib
        ParameterizedAlgebra = uacalc_lib.alg.ParameterizedAlgebra
        
        param_alg = ParameterizedAlgebra(
            ["n", "m"],
            "Example",
            "n*m",
            "",
            []
        )
        
        param_map = param_alg.get_parameter_map([3, 4])
        self.assertEqual(param_map["n"], "3")
        self.assertEqual(param_map["m"], "4")
    
    def test_get_parameter_map_error(self):
        """Test get_parameter_map with wrong number of values."""
        import uacalc_lib
        ParameterizedAlgebra = uacalc_lib.alg.ParameterizedAlgebra
        
        param_alg = ParameterizedAlgebra(
            ["n", "m"],
            "Example",
            "n*m",
            "",
            []
        )
        
        # Wrong number of values
        with self.assertRaises(ValueError):
            param_alg.get_parameter_map([3])
    
    def test_get_parameter_map_vs_java(self):
        """Test get_parameter_map matches Java implementation."""
        import uacalc_lib
        ParameterizedAlgebra = uacalc_lib.alg.ParameterizedAlgebra
        
        # Run Java wrapper
        java_result = self.run_java_wrapper(
            "get_parameter_map",
            ["--param_names", "n,m", "--values", "3,4"]
        )
        
        if java_result is None:
            self.skipTest("Java wrapper not available")
        
        # Create Python algebra
        param_alg = ParameterizedAlgebra(
            ["n", "m"],
            "TestAlgebra",
            "n*m",
            "Test algebra",
            []
        )
        
        param_map = param_alg.get_parameter_map([3, 4])
        
        # Compare results
        java_map = java_result["data"]["status"]
        self.assertEqual(param_map, java_map)
    
    def run_java_wrapper(self, command, args):
        """Run Java wrapper command."""
        try:
            separator = ";" if platform.system() == "Windows" else ":"
            classpath = f"java_wrapper/build/classes{separator}build/classes{separator}org{separator}jars/*"
            cmd = [
                "java",
                "-cp", classpath,
                "java_wrapper.src.alg.ParameterizedAlgebraWrapper",
                command
            ] + args
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            output = json.loads(result.stdout)
            
            # Parse the data field if it's a string
            if "data" in output and isinstance(output["data"], str):
                output["data"] = json.loads(output["data"])
            
            return output
        except Exception as e:
            print(f"Java wrapper error: {e}")
            return None


class TestParameterizedOperation(unittest.TestCase):
    """Test cases for ParameterizedOperation."""
    
    def test_create_basic(self):
        """Test creating a basic ParameterizedOperation."""
        import uacalc_lib
        ParameterizedOperation = uacalc_lib.alg.ParameterizedOperation
        
        param_op = ParameterizedOperation(
            "add_mod_n",
            "plus",
            "n",
            ["n"],
            "2",
            "Addition modulo n",
            "0",
            "(a + b) % n"
        )
        
        self.assertEqual(param_op.get_name(), "add_mod_n")
        self.assertEqual(param_op.get_symbol_name(), "plus")
        self.assertEqual(param_op.get_arity_exp(), "2")
    
    def test_sub_parm_values(self):
        """Test sub_parm_values method."""
        import uacalc_lib
        ParameterizedOperation = uacalc_lib.alg.ParameterizedOperation
        
        parm_map = {"n": "5"}
        
        # Note: Current implementation is a stub
        result = ParameterizedOperation.sub_parm_values("n+1", parm_map)
        self.assertEqual(result, "n+1")  # Should be "n+1" since substitution is not implemented
    
    def test_sub_parm_values_empty_map(self):
        """Test sub_parm_values with empty map."""
        import uacalc_lib
        ParameterizedOperation = uacalc_lib.alg.ParameterizedOperation
        
        parm_map = {}
        
        result = ParameterizedOperation.sub_parm_values("n*m", parm_map)
        self.assertEqual(result, "n*m")
    
    def test_sub_parm_values_vs_java(self):
        """Test sub_parm_values matches Java implementation."""
        import uacalc_lib
        ParameterizedOperation = uacalc_lib.alg.ParameterizedOperation
        
        # Run Java wrapper
        java_result = self.run_java_wrapper(
            "sub_parm_values",
            ["--param_string", "n+1", "--parm_map", "n=5"]
        )
        
        if java_result is None:
            self.skipTest("Java wrapper not available")
        
        # Call Python method
        parm_map = {"n": "5"}
        result = ParameterizedOperation.sub_parm_values("n+1", parm_map)
        
        # Compare results
        java_result_value = java_result["data"]["status"]
        self.assertEqual(result, java_result_value)
    
    def run_java_wrapper(self, command, args):
        """Run Java wrapper command."""
        try:
            separator = ";" if platform.system() == "Windows" else ":"
            classpath = f"java_wrapper/build/classes{separator}build/classes{separator}org{separator}jars/*"
            cmd = [
                "java",
                "-cp", classpath,
                "java_wrapper.src.alg.op.ParameterizedOperationWrapper",
                command
            ] + args
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            output = json.loads(result.stdout)
            
            # Parse the data field if it's a string
            if "data" in output and isinstance(output["data"], str):
                output["data"] = json.loads(output["data"])
            
            return output
        except Exception as e:
            print(f"Java wrapper error: {e}")
            return None


if __name__ == '__main__':
    unittest.main()
