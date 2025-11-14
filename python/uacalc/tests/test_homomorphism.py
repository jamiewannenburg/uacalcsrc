"""Tests for the Homomorphism module.

These tests verify that the Python implementation matches the Java implementation
by comparing outputs with the Java CLI wrapper.
"""

import pytest
import json
from pathlib import Path
import platform

# Import clean class names (Py* names are not available)
import uacalc_lib
Homomorphism = uacalc_lib.alg.Homomorphism
BasicAlgebra = uacalc_lib.alg.BasicAlgebra

# Get the project root directory
project_root = Path(__file__).parent.parent.parent.parent


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    from test_utils import build_java_command
    
    wrapper_class = "java_wrapper.src.alg.HomomorphismWrapper"
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
            return json.loads(result.stdout.strip())
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
                        json_objects.append(json.loads(line))
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
    return BasicAlgebra(name, universe ,[])


class TestHomomorphism:
    """Test cases for the Homomorphism class."""
    
    def test_homomorphism_new(self):
        """Test creating a new homomorphism."""
        # Create mock algebras
        domain = create_mock_algebra("domain", [0, 1])
        range_algebra = create_mock_algebra("range", [0, 1])
        
        # Create mapping
        mapping = {0: 0, 1: 1}
        
        # Create homomorphism
        homo = Homomorphism(domain, range_algebra, mapping)
        
        # Test basic properties
        assert homo.get_domain().name() == "domain"
        assert homo.get_range().name() == "range"
        assert homo.get_map() == mapping
        
        # TODO: Compare with Java implementation once wrapper is created
        # java_result = run_java_wrapper("new", [
        #     "--domain_name", "domain",
        #     "--range_name", "range", 
        #     "--map", "0:0,1:1"
        # ])
        # 
        # assert java_result["command"] == "new"
        # assert java_result["domain_name"] == "domain"
        # assert java_result["range_name"] == "range"
        # assert java_result["map_size"] == 2
        # assert java_result["created"] is True
    
    def test_homomorphism_kernel(self):
        """Test kernel computation."""
        # Create mock algebras
        domain = create_mock_algebra("domain", [0, 1])
        range_algebra = create_mock_algebra("range", [0, 1])
        
        # Create mapping
        mapping = {0: 0, 1: 1}
        
        # Create homomorphism
        homo = Homomorphism(domain, range_algebra, mapping)
        
        # Compute kernel
        kernel = homo.kernel()
        
        # Test kernel properties
        assert kernel.number_of_blocks() == 2  # Each element in its own block
        
        # TODO: Compare with Java implementation once wrapper is created
        # java_result = run_java_wrapper("kernel", [
        #     "--domain_name", "domain",
        #     "--range_name", "range",
        #     "--map", "0:0,1:1"
        # ])
        # 
        # assert java_result["command"] == "kernel"
        # assert java_result["number_of_blocks"] == 2
    
    def test_homomorphism_kernel_with_duplicate_mapping(self):
        """Test kernel computation with duplicate mapping."""
        # Create mock algebras
        domain = create_mock_algebra("domain", [0, 1])
        range_algebra = create_mock_algebra("range", [0])  # Only one element in range
        
        # Create mapping where both domain elements map to the same range element
        mapping = {0: 0, 1: 0}
        
        # Create homomorphism
        homo = Homomorphism(domain, range_algebra, mapping)
        
        # Compute kernel
        kernel = homo.kernel()
        
        # Test kernel properties - should have 1 block since both elements map to same value
        assert kernel.number_of_blocks() == 1
        
        # TODO: Compare with Java implementation once wrapper is created
        # java_result = run_java_wrapper("kernel", [
        #     "--domain_name", "domain",
        #     "--range_name", "range",
        #     "--map", "0:0,1:0"
        # ])
        # 
        # assert java_result["command"] == "kernel"
        # assert java_result["number_of_blocks"] == 1
    
    def test_homomorphism_to_string(self):
        """Test string representation."""
        # Create mock algebras
        domain = create_mock_algebra("domain", [0, 1])
        range_algebra = create_mock_algebra("range", [0, 1])
        
        # Create mapping
        mapping = {0: 0, 1: 1}
        
        # Create homomorphism
        homo = Homomorphism(domain, range_algebra, mapping)
        
        # Test string representation
        str_repr = str(homo)
        assert "domain" in str_repr
        assert "range" in str_repr
        assert "homomorphism" in str_repr.lower()
        
        # TODO: Compare with Java implementation once wrapper is created
        # java_result = run_java_wrapper("to_string", [
        #     "--domain_name", "domain",
        #     "--range_name", "range",
        #     "--map", "0:0,1:1"
        # ])
        # 
        # assert java_result["command"] == "to_string"
        # assert "domain" in java_result["result"]
        # assert "range" in java_result["result"]
    
    def test_homomorphism_get_set_methods(self):
        """Test getter and setter methods."""
        # Create mock algebras
        domain = create_mock_algebra("domain", [0, 1])
        range_algebra = create_mock_algebra("range", [0, 1])
        
        # Create mapping
        mapping = {0: 0, 1: 1}
        
        # Create homomorphism
        homo = Homomorphism(domain, range_algebra, mapping)
        
        # Test getters
        assert homo.get_domain().name() == "domain"
        assert homo.get_range().name() == "range"
        assert homo.get_map() == mapping
        
        # Test setters
        new_domain = create_mock_algebra("new_domain", [0, 1, 2])
        new_range = create_mock_algebra("new_range", [0, 1, 2])
        new_mapping = {0: 0, 1: 1, 2: 2}
        
        homo.set_domain(new_domain)
        homo.set_range(new_range)
        homo.set_map(new_mapping)
        
        assert homo.get_domain().name() == "new_domain"
        assert homo.get_range().name() == "new_range"
        assert homo.get_map() == new_mapping
    
    def test_homomorphism_validation(self):
        """Test homomorphism validation."""
        # Test invalid mapping - missing domain element
        domain = create_mock_algebra("domain", [0, 1])
        range_algebra = create_mock_algebra("range", [0, 1])
        
        # Missing element 1 in mapping
        mapping = {0: 0}
        
        with pytest.raises(Exception) as exc_info:
            Homomorphism(domain, range_algebra, mapping)
        
        # Should get an error about missing domain element
        assert "Domain element 1 is not mapped" in str(exc_info.value)
    
    def test_homomorphism_validation_out_of_range(self):
        """Test homomorphism validation with out-of-range values."""
        # Test invalid mapping - out of range value
        domain = create_mock_algebra("domain", [0, 1])
        range_algebra = create_mock_algebra("range", [0])  # Only one element in range
        
        # Element 1 maps to 1, which is out of range
        mapping = {0: 0, 1: 1}
        
        with pytest.raises(Exception) as exc_info:
            Homomorphism(domain, range_algebra, mapping)
        
        # Should get an error about out of range value
        assert "Mapped value 1 is out of range" in str(exc_info.value)
    
    def test_homomorphism_basic_functionality(self):
        """Test basic homomorphism functionality."""
        # Create mock algebras
        domain = create_mock_algebra("domain", [0, 1, 2])
        range_algebra = create_mock_algebra("range", [0, 1])
        
        # Create mapping where 0 and 2 both map to 0
        mapping = {0: 0, 1: 1, 2: 0}
        
        # Create homomorphism
        homo = Homomorphism(domain, range_algebra, mapping)
        
        # Test kernel - should have 2 blocks: {0, 2} and {1}
        kernel = homo.kernel()
        assert kernel.number_of_blocks() == 2
        
        # Test that 0 and 2 are in the same block
        assert kernel.is_related(0, 2)
        assert not kernel.is_related(0, 1)
        assert not kernel.is_related(1, 2)
        
        # Test string representation
        str_repr = str(homo)
        assert "domain" in str_repr
        assert "range" in str_repr
        assert "homomorphism" in str_repr.lower()
    
    def test_homomorphism_product_homo(self):
        """Test product_homo functionality."""
        # Create mock algebras
        domain = create_mock_algebra("domain", [0, 1])
        range_algebra = create_mock_algebra("range", [0, 1])
        
        # Create mapping
        mapping = {0: 0, 1: 1}
        
        # Create homomorphism
        homo = Homomorphism(domain, range_algebra, mapping)
        
        # Test product_homo with single homomorphism
        result = Homomorphism.product_homo([homo])
        
        assert len(result) == 2  # Two elements in domain
        assert result[0].universe_size() == 1  # Each IntArray has size 1 (one homomorphism)
        assert result[0].get(0) == 0  # First element maps to 0
        assert result[1].get(0) == 1  # Second element maps to 1


if __name__ == "__main__":
    pytest.main([__file__])
