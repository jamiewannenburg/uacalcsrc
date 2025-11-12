"""Tests for the AlgebraFromMinimalSets module.

These tests verify that the Python implementation matches the Java implementation
by comparing outputs with the Java CLI wrapper.
"""

import pytest
import json
from pathlib import Path
import platform

# Import clean class names (Py* names are not available)
import uacalc_lib
AlgebraFromMinimalSets = uacalc_lib.alg.AlgebraFromMinimalSets
BasicAlgebra = uacalc_lib.alg.BasicAlgebra

# Get the project root directory
project_root = Path(__file__).parent.parent.parent.parent


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    from test_utils import build_java_command
    
    wrapper_class = "java_wrapper.src.alg.AlgebraFromMinimalSetsWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    import subprocess
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,
            cwd=project_root  # Run from project root so relative paths work
        )
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")
        
        # Parse the JSON output - handle multi-line JSON
        try:
            # Try to parse the entire output as JSON first
            output = json.loads(result.stdout.strip())
            # Parse the data field again if it's a string
            if "data" in output and isinstance(output["data"], str):
                output["data"] = json.loads(output["data"])
            return output
        except json.JSONDecodeError:
            # If that fails, try to parse multiple JSON objects
            output = result.stdout.strip()
            json_objects = []
            
            # Split by lines and try to parse each line as JSON
            output_lines = output.split('\n')
            for line in output_lines:
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                        # Parse the data field again if it's a string
                        if "data" in obj and isinstance(obj["data"], str):
                            obj["data"] = json.loads(obj["data"])
                        json_objects.append(obj)
                    except json.JSONDecodeError:
                        continue
            
            if json_objects:
                return json_objects[0]  # Return the first valid JSON object
            else:
                pytest.fail(f"Could not parse JSON from output: {output}")
                
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except Exception as e:
        pytest.fail(f"Error running Java wrapper: {e}")


def create_mock_algebra(name, universe):
    """Create a mock BasicAlgebra for testing."""
    return BasicAlgebra(name, universe, [])


class TestAlgebraFromMinimalSets:
    """Test cases for the AlgebraFromMinimalSets class."""
    
    def test_algebra_from_minimal_sets_new(self):
        """Test creating a new AlgebraFromMinimalSets with default constructor."""
        # Create mock minimal algebra
        min_alg = create_mock_algebra("minimal", [0, 1, 2])
        
        # Create algebra from minimal sets
        alg = AlgebraFromMinimalSets(min_alg)
        
        # Test basic properties
        # Default size should be 3 * 3 - 2 = 7
        assert alg.cardinality() == 7
        assert alg.name() == "AlgebraFromMinimalSets"
        
        # Compare with Java implementation
        java_result = run_java_wrapper("new", ["--min_alg_size", "3"])
        assert java_result["success"] is True
        assert java_result["data"]["cardinality"] == 7
    
    def test_algebra_from_minimal_sets_new_with_name(self):
        """Test creating a new AlgebraFromMinimalSets with a name."""
        # Create mock minimal algebra
        min_alg = create_mock_algebra("minimal", [0, 1, 2])
        
        # Create algebra from minimal sets with name
        alg = AlgebraFromMinimalSets.new_with_name(min_alg, "TestAlgebra")
        
        # Test basic properties
        assert alg.cardinality() == 7
        assert alg.name() == "TestAlgebra"
        
        # Compare with Java implementation
        java_result = run_java_wrapper("new_with_name", ["--name", "TestAlgebra", "--min_alg_size", "3"])
        assert java_result["success"] is True
        assert java_result["data"]["cardinality"] == 7
        assert java_result["data"]["name"] == "TestAlgebra"
    
    def test_algebra_from_minimal_sets_new_with_size(self):
        """Test creating a new AlgebraFromMinimalSets with explicit size."""
        # Create mock minimal algebra
        min_alg = create_mock_algebra("minimal", [0, 1, 2])
        
        # Create algebra from minimal sets with explicit size (using default maps)
        alg = AlgebraFromMinimalSets.new_with_size(min_alg, 7, None)
        
        # Test basic properties
        assert alg.cardinality() == 7
        
        # Compare with Java implementation
        java_result = run_java_wrapper("new_with_size", ["--min_alg_size", "3", "--alg_size", "7"])
        assert java_result["success"] is True
        assert java_result["data"]["cardinality"] == 7
    
    def test_algebra_from_minimal_sets_new_with_connecting_pts(self):
        """Test creating a new AlgebraFromMinimalSets with connecting points."""
        # Create mock minimal algebra
        min_alg = create_mock_algebra("minimal", [0, 1, 2])
        
        # Create algebra from minimal sets with connecting points
        alg = AlgebraFromMinimalSets.new_with_connecting_pts(min_alg, "TestAlgebra", [0, 2])
        
        # Test basic properties
        assert alg.cardinality() == 7
        assert alg.name() == "TestAlgebra"
        
        # Compare with Java implementation
        java_result = run_java_wrapper("new_with_connecting_pts", [
            "--name", "TestAlgebra",
            "--min_alg_size", "3",
            "--connect_pts", "0,2"
        ])
        assert java_result["success"] is True
        assert java_result["data"]["cardinality"] == 7
    
    def test_algebra_from_minimal_sets_cardinality(self):
        """Test cardinality method."""
        # Create mock minimal algebra
        min_alg = create_mock_algebra("minimal", [0, 1, 2])
        
        # Create algebra from minimal sets
        alg = AlgebraFromMinimalSets(min_alg)
        
        # Test cardinality
        assert alg.cardinality() == 7
        
        # Compare with Java implementation
        java_result = run_java_wrapper("cardinality", ["--min_alg_size", "3"])
        assert java_result["success"] is True
        assert java_result["data"]["cardinality"] == 7
    
    def test_algebra_from_minimal_sets_get_element(self):
        """Test get_element method."""
        # Create mock minimal algebra
        min_alg = create_mock_algebra("minimal", [0, 1, 2])
        
        # Create algebra from minimal sets
        alg = AlgebraFromMinimalSets(min_alg)
        
        # Test get_element
        assert alg.get_element(0) == 0
        assert alg.get_element(6) == 6
        assert alg.get_element(7) is None  # Out of bounds
        
        # Compare with Java implementation
        java_result = run_java_wrapper("get_element", ["--min_alg_size", "3", "--k", "0"])
        assert java_result["success"] is True
        assert java_result["data"]["element"] == 0
    
    def test_algebra_from_minimal_sets_element_index(self):
        """Test element_index method."""
        # Create mock minimal algebra
        min_alg = create_mock_algebra("minimal", [0, 1, 2])
        
        # Create algebra from minimal sets
        alg = AlgebraFromMinimalSets(min_alg)
        
        # Test element_index
        assert alg.element_index(0) == 0
        assert alg.element_index(6) == 6
        assert alg.element_index(7) is None  # Out of bounds
        
        # Compare with Java implementation
        java_result = run_java_wrapper("element_index", ["--min_alg_size", "3", "--elem", "0"])
        assert java_result["success"] is True
        assert java_result["data"]["index"] == 0
    
    def test_algebra_from_minimal_sets_different_sizes(self):
        """Test with different minimal algebra sizes."""
        # Test with different minimal algebra sizes
        for min_size in range(2, 6):
            universe = list(range(min_size))
            min_alg = create_mock_algebra("minimal", universe)
            
            alg = AlgebraFromMinimalSets(min_alg)
            
            # Default size should be 3 * min_size - 2
            expected_size = 3 * min_size - 2
            assert alg.cardinality() == expected_size
    
    def test_algebra_from_minimal_sets_to_string(self):
        """Test string representation."""
        # Create mock minimal algebra
        min_alg = create_mock_algebra("minimal", [0, 1, 2])
        
        # Create algebra from minimal sets
        alg = AlgebraFromMinimalSets(min_alg)
        
        # Test string representation
        str_repr = str(alg)
        assert "AlgebraFromMinimalSets" in str_repr


if __name__ == "__main__":
    pytest.main([__file__])

