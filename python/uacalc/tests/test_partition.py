"""Tests for the Partition module.

These tests verify that the Python implementation matches the Java implementation
by comparing outputs with the Java CLI wrapper.
"""

import pytest
import json
from pathlib import Path
import platform

# Import clean class names (Py* names are not available)
import uacalc_lib
Partition = uacalc_lib.alg.Partition
PrintType = uacalc_lib.alg.PrintType

# Get the project root directory
project_root = Path(__file__).parent.parent.parent.parent


def run_java_wrapper(command, args):
    """Run Java wrapper and return JSON output."""
    from test_utils import build_java_command
    
    wrapper_class = "java_wrapper.src.alg.conlat.PartitionWrapper"
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
            current_json = ""
            brace_count = 0
            
            for line in output_lines:
                line = line.strip()
                if not line:
                    continue
                    
                current_json += line
                
                # Count braces to determine when we have a complete JSON object
                brace_count += line.count('{') - line.count('}')
                
                if brace_count == 0 and current_json:
                    try:
                        json_objects.append(json.loads(current_json))
                        current_json = ""
                    except json.JSONDecodeError:
                        current_json = ""
            
            if json_objects:
                # Return the last JSON object (usually contains the final result)
                return json_objects[-1]
            
            pytest.fail(f"No valid JSON output found: {result.stdout}")
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except Exception as e:
        pytest.fail(f"Failed to run Java wrapper: {e}")


def extract_java_data(java_output):
    """Extract the 'data' field from Java wrapper JSON output, with fallback to raw string.
    
    The Java wrapper outputs JSON in the format:
    {
      "success": true,
      "timestamp": 1234567890,
      "duration_ms": 50,
      "data": "actual_result_here"
    }
    
    This function extracts the "data" field value, or returns the raw string if JSON parsing fails.
    """
    if isinstance(java_output, str):
        # Try to parse the Java output as JSON
        try:
            json_data = json.loads(java_output)
            # Extract the "data" field
            if "data" in json_data:
                return json_data["data"]
            else:
                # No "data" field, return the whole JSON as string
                return str(json_data)
        except json.JSONDecodeError:
            # JSON parsing failed, return the raw string
            return java_output
    elif isinstance(java_output, dict) and "data" in java_output:
        return java_output["data"]
    else:
        return str(java_output)


def compare_with_java(python_result, java_output, tolerance=None):
    """Compare Python result with Java wrapper output, handling format mismatches.
    
    Args:
        python_result: The result from Python implementation
        java_output: The output from Java wrapper (can be dict or string)
        tolerance: Optional tolerance for numerical comparisons
    
    Returns:
        bool: True if results match, False otherwise
    """
    # Extract the actual data from Java output
    java_data = extract_java_data(java_output)
    
    # Handle different types of comparisons
    # Check bool first since bool is a subclass of int in Python
    if isinstance(python_result, bool) and isinstance(java_data, str):
        # Handle boolean comparison
        java_bool = java_data.lower() == 'true'
        return python_result == java_bool
    
    elif isinstance(python_result, (int, float)) and isinstance(java_data, str):
        # Try to parse Java string as number
        try:
            java_num = float(java_data)
            if tolerance is not None:
                return abs(python_result - java_num) <= tolerance
            else:
                return python_result == java_num
        except ValueError:
            return str(python_result) == java_data
    
    if isinstance(python_result, list) and isinstance(java_data, str):
        # Try to parse Java string as JSON list
        try:
            java_list = json.loads(java_data)
            return python_result == java_list
        except json.JSONDecodeError:
            return str(python_result) == java_data
    
    else:
        # Direct comparison
        return python_result == java_data


def convert_java_result(java_result, expected_type=None):
    """Convert Java wrapper result to appropriate Python type."""
    if java_result is None or "data" not in java_result:
        return java_result
    
    data = java_result["data"]
    
    # If it's already the right type, return as-is
    if expected_type is None:
        return data
    
    # Convert based on expected type
    if expected_type == int:
        try:
            return int(data)
        except (ValueError, TypeError):
            return data
    elif expected_type == bool:
        if isinstance(data, str):
            return data.lower() == 'true'
        return bool(data)
    elif expected_type == list:
        if isinstance(data, str):
            try:
                # Try to parse as JSON list
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return data
    else:
        return data

def run_java_wrapper_test_command():
    """Run Java wrapper test command and parse all JSON objects into a structured result."""
    import json
    import subprocess
    
    # Use Windows-compatible script path
    script_extension = ".bat" if platform.system() == "Windows" else ""
    java_wrapper_path = project_root / "java_wrapper" / "build" / "scripts" / f"PartitionWrapper{script_extension}"

    if not java_wrapper_path.exists():
        pytest.skip(f"Java wrapper not found at {java_wrapper_path}")

    cmd = [str(java_wrapper_path), "test"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")

        # Parse all JSON objects from the output
        # The output contains multiple JSON objects, each on multiple lines
        output = result.stdout.strip()
        json_objects = []
        
        # Split by lines and try to parse each line as JSON
        output_lines = output.split('\n')
        current_json = ""
        brace_count = 0
        
        for line in output_lines:
            line = line.strip()
            if not line:
                continue
                
            current_json += line
            
            # Count braces to determine when we have a complete JSON object
            brace_count += line.count('{') - line.count('}')
            
            if brace_count == 0 and current_json:
                try:
                    json_objects.append(json.loads(current_json))
                    current_json = ""
                except json.JSONDecodeError:
                    current_json = ""
        
        if not json_objects:
            pytest.fail(f"No valid JSON output found: {result.stdout}")
        
        # Extract data from the JSON objects
        results = {}
        for obj in json_objects:
            data = obj.get("data", "")
            if "Zero partition created:" in data:
                results["zero_partition"] = data.split("Zero partition created: ")[1]
            elif "One partition created:" in data:
                results["one_partition"] = data.split("One partition created: ")[1]
            elif "From array created:" in data:
                results["from_array_partition"] = data.split("From array created: ")[1]
            elif "From string created:" in data:
                results["from_string_partition"] = data.split("From string created: ")[1]
            elif "Zero universe size:" in data:
                results["zero_universe_size"] = int(data.split("Zero universe size: ")[1])
            elif "Zero number of blocks:" in data:
                results["zero_number_of_blocks"] = int(data.split("Zero number of blocks: ")[1])
            elif "One universe size:" in data:
                results["one_universe_size"] = int(data.split("One universe size: ")[1])
            elif "One number of blocks:" in data:
                results["one_number_of_blocks"] = int(data.split("One number of blocks: ")[1])
            elif "Zero is_related(0,1):" in data:
                results["zero_is_related_0_1"] = data.split("Zero is_related(0,1): ")[1].lower() == "true"
            elif "One is_related(0,1):" in data:
                results["one_is_related_0_1"] = data.split("One is_related(0,1): ")[1].lower() == "true"
            elif "Zero representatives:" in data:
                results["zero_representatives"] = json.loads(data.split("Zero representatives: ")[1])
            elif "One representatives:" in data:
                results["one_representatives"] = json.loads(data.split("One representatives: ")[1])
            elif "Zero join One:" in data:
                results["zero_join_one"] = data.split("Zero join One: ")[1]
            elif "Zero meet One:" in data:
                results["zero_meet_one"] = data.split("Zero meet One: ")[1]
            elif "Zero leq One:" in data:
                results["zero_leq_one"] = data.split("Zero leq One: ")[1].lower() == "true"
            elif "One leq Zero:" in data:
                results["one_leq_zero"] = data.split("One leq Zero: ")[1].lower() == "true"
        
        # Add default values for missing data
        results.setdefault("zero_is_zero", True)
        results.setdefault("one_is_zero", False)
        
        return results
        
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except Exception as e:
        pytest.fail(f"Failed to run Java wrapper: {e}")


class TestPartition:
    """Test cases for Partition class."""
    
    def test_zero_partition(self):
        """Test zero partition creation."""
        java_result = run_java_wrapper("zero", ["--size", "3"])
        
        partition = Partition.zero(3)
        
        # Compare string representation with Java output
        assert compare_with_java(str(partition), java_result)
        
        # Test other properties (these are tested separately in other tests)
        assert partition.universe_size() == 3
        assert partition.number_of_blocks() == 3
        assert partition.is_zero() == True
    
    def test_one_partition(self):
        """Test one partition creation."""
        java_result = run_java_wrapper("one", ["--size", "3"])
        
        partition = Partition.one(3)
        
        # Compare string representation with Java output
        assert compare_with_java(str(partition), java_result)
        
        # Test other properties
        assert partition.universe_size() == 3
        assert partition.number_of_blocks() == 1
        assert partition.is_zero() == False
    
    def test_from_array(self):
        """Test partition creation from array."""
        java_result = run_java_wrapper("from_array", ["--array", "[-2,0,-1,-1]"])
        
        partition = Partition([-2, 0, -1, -1])
        
        # Compare string representation with Java output
        assert compare_with_java(str(partition), java_result)
        
        # Test other properties
        assert partition.universe_size() == 4
        assert partition.number_of_blocks() == 3
    
    def test_from_string(self):
        """Test partition creation from string."""
        java_result = run_java_wrapper("from_string", ["--str", "|0 1|2 3|"])
        
        partition = Partition.from_string("|0 1|2 3|")
        
        assert str(partition) == java_result["data"]
        # Additional assertions for the partition
        assert partition.universe_size() == 4
        assert partition.number_of_blocks() == 2
    
    def test_universe_size(self):
        """Test universe size method."""
        java_result = run_java_wrapper("universe_size", ["--partition_array", "[-2,0,-1,-1]"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert compare_with_java(partition.universe_size(), java_result)
    
    def test_number_of_blocks(self):
        """Test number of blocks method."""
        java_result = run_java_wrapper("number_of_blocks", ["--partition_array", "[-2,0,-1,-1]"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert compare_with_java(partition.number_of_blocks(), java_result)
    
    def test_is_related(self):
        """Test is_related method."""
        java_result = run_java_wrapper("is_related", ["--partition_array", "[-2,0,-1,-1]", "--i", "0", "--j", "1"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert compare_with_java(partition.is_related(0, 1), java_result)
    
    def test_representative(self):
        """Test representative method."""
        java_result = run_java_wrapper("representative", ["--partition_array", "[-2,0,-1,-1]", "--i", "1"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert compare_with_java(partition.representative(1), java_result)
    
    def test_is_representative(self):
        """Test is_representative method."""
        java_result = run_java_wrapper("is_representative", ["--partition_array", "[-2,0,-1,-1]", "--i", "0"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert compare_with_java(partition.is_representative(0), java_result)
    
    def test_representatives(self):
        """Test representatives method."""
        java_result = run_java_wrapper("representatives", ["--partition_array", "[-2,0,-1,-1]"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert compare_with_java(partition.representatives(), java_result)
    
    def test_block_index(self):
        """Test block_index method."""
        java_result = run_java_wrapper("block_index", ["--partition_array", "[-2,0,-1,-1]", "--i", "1"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert compare_with_java(partition.block_index(1), java_result)
    
    def test_get_blocks(self):
        """Test get_blocks method."""
        java_result = run_java_wrapper("get_blocks", ["--partition_array", "[-2,0,-1,-1]"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert partition.get_blocks() == convert_java_result(java_result, list)
    
    def test_join_blocks(self):
        """Test join_blocks method."""
        java_result = run_java_wrapper("join_blocks", ["--partition_array", "[-1,-1,-1,-1]", "--r", "0", "--s", "1"])
        
        partition = Partition([-1, -1, -1, -1])
        partition.join_blocks(0, 1)
        
        assert str(partition) == java_result["data"]
    
    def test_join(self):
        """Test join method."""
        java_result = run_java_wrapper("join", ["--partition1_array", "[-2,0,-1,-1]", "--partition2_array", "[-1,-1,-2,2]"])
        
        partition1 = Partition([-2, 0, -1, -1])
        partition2 = Partition([-1, -1, -2, 2])
        join = partition1.join(partition2)
        
        assert str(join) == java_result["data"]
    
    def test_meet(self):
        """Test meet method."""
        java_result = run_java_wrapper("meet", ["--partition1_array", "[-2,0,-1,-1]", "--partition2_array", "[-1,-1,-2,2]"])
        
        partition1 = Partition([-2, 0, -1, -1])
        partition2 = Partition([-1, -1, -2, 2])
        meet = partition1.meet(partition2)
        
        assert str(meet) == java_result["data"]
    
    def test_leq(self):
        """Test leq method."""
        java_result = run_java_wrapper("leq", ["--partition1_array", "[-2,0,-1,-1]", "--partition2_array", "[-4,0,0,0]"])
        
        partition1 = Partition([-2, 0, -1, -1])
        partition2 = Partition([-4, 0, 0, 0])
        
        assert partition1.leq(partition2) == convert_java_result(java_result, bool)
    
    def test_normalize(self):
        """Test normalize method."""
        # Test normalize functionality with a valid partition
        # Use a partition that has proper structure: [-2, 0, -1, -1] represents |0,1|2|3|
        partition = Partition([-2, 0, -1, -1])
        partition.normalize()
        
        # After normalization, the partition should have proper structure
        assert partition.universe_size() == 4
        assert partition.number_of_blocks() == 3
        # The normalized form should have the smallest elements as representatives
        assert partition.is_representative(0)
        assert partition.is_representative(2)
        assert partition.is_representative(3)
    
    def test_is_zero(self):
        """Test is_zero method."""
        java_result = run_java_wrapper("is_zero", ["--partition_array", "[-1,-1,-1,-1]"])
        
        partition = Partition([-1, -1, -1, -1])
        
        assert partition.is_zero() == convert_java_result(java_result, bool)
    
    def test_is_uniform(self):
        """Test is_uniform method."""
        java_result = run_java_wrapper("is_uniform", ["--partition_array", "[-2,0,-2,2]"])
        
        partition = Partition([-2, 0, -2, 2])
        
        assert partition.is_uniform() == convert_java_result(java_result, bool)
    
    def test_is_initial_lex_representative(self):
        """Test is_initial_lex_representative method."""
        java_result = run_java_wrapper("is_initial_lex_representative", ["--partition_array", "[-2,0,-1,-1]"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert partition.is_initial_lex_representative() == convert_java_result(java_result, bool)
    
    def test_to_array(self):
        """Test to_array method."""
        java_result = run_java_wrapper("to_array", ["--partition_array", "[-2,0,-1,-1]"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert partition.to_array() == convert_java_result(java_result, list)
    
    def test_rank(self):
        """Test rank method."""
        java_result = run_java_wrapper("rank", ["--partition_array", "[-2,0,-1,-1]"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert partition.rank() == convert_java_result(java_result, int)
    
    def test_to_string(self):
        """Test to_string method."""
        java_result = run_java_wrapper("to_string", ["--partition_array", "[-2,0,-1,-1]"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert str(partition) == java_result["data"]
    
    def test_to_string_with_type(self):
        """Test to_string_with_type method."""
        java_result = run_java_wrapper("to_string_with_type", ["--partition_array", "[-2,0,-1,-1]", "--type", "block"])
        
        partition = Partition([-2, 0, -1, -1])
        print_type = PrintType("block")
        
        assert partition.to_string_with_type(print_type) == java_result["data"]
    
    def test_to_string_with_max_len(self):
        """Test to_string_with_max_len method."""
        java_result = run_java_wrapper("to_string_with_max_len", ["--partition_array", "[-2,0,-1,-1]", "--max_len", "50"])
        
        partition = Partition([-2, 0, -1, -1])
        
        assert partition.to_string_with_max_len(50) == java_result["data"]
    
    def test_basic_functionality(self):
        """Test basic functionality with comprehensive test."""
        # Get the Java wrapper test results
        java_results = run_java_wrapper_test_command()
        
        # Test zero partition
        zero = Partition.zero(3)
        assert str(zero) == java_results["zero_partition"]
        assert zero.universe_size() == java_results["zero_universe_size"]
        assert zero.number_of_blocks() == java_results["zero_number_of_blocks"]
        assert zero.is_zero() == java_results["zero_is_zero"]
        assert zero.is_related(0, 1) == java_results["zero_is_related_0_1"]
        assert zero.representatives() == java_results["zero_representatives"]
        
        # Test one partition
        one = Partition.one(3)
        assert str(one) == java_results["one_partition"]
        assert one.universe_size() == java_results["one_universe_size"]
        assert one.number_of_blocks() == java_results["one_number_of_blocks"]
        assert one.is_zero() == java_results["one_is_zero"]
        assert one.is_related(0, 1) == java_results["one_is_related_0_1"]
        assert one.representatives() == java_results["one_representatives"]
        
        # Test from array
        from_array = Partition([-2, 0, -1, -1])
        assert str(from_array) == java_results["from_array_partition"]
        
        # Test from string
        from_string = Partition.from_string("|0,1|2,3|")
        assert str(from_string) == java_results["from_string_partition"]
        
        # Test join and meet
        join = zero.join(one)
        meet = zero.meet(one)
        assert str(join) == java_results["zero_join_one"]
        assert str(meet) == java_results["zero_meet_one"]
        assert zero.leq(one) == java_results["zero_leq_one"]
        assert one.leq(zero) == java_results["one_leq_zero"]
    
    def test_print_type_creation(self):
        """Test PrintType creation and usage."""
        # Test all print types
        print_types = ["internal", "ewk", "block", "human", "sq_brace_block"]
        for type_str in print_types:
            print_type = PrintType(type_str)
            assert str(print_type) == type_str
            assert str(print_type) == type_str
            assert repr(print_type) == f"PrintType('{type_str}')"
        
        # Test invalid print type
        with pytest.raises(ValueError, match="Invalid print type"):
            PrintType("invalid")
    
    def test_partition_comparison(self):
        """Test partition comparison operations."""
        partition1 = Partition([-2, 0, -1, -1])
        partition2 = Partition([-2, 0, -1, -1])
        partition3 = Partition([-1, -1, -1, -1])
        
        # Test equality
        assert partition1 == partition2
        assert partition1 != partition3
        
        # Test ordering
        assert partition1 >= partition2
        assert partition1 <= partition2
        assert not (partition1 > partition2)
        assert not (partition1 < partition2)
        
        # Test with different partitions
        zero = Partition.zero(4)
        one = Partition.one(4)
        
        assert zero < one
        assert one > zero
        assert zero <= one
        assert one >= zero
    
    def test_partition_hash(self):
        """Test partition hashing."""
        partition1 = Partition([-2, 0, -1, -1])
        partition2 = Partition([-2, 0, -1, -1])
        partition3 = Partition([-1, -1, -1, -1])
        
        # Equal partitions should have equal hashes
        assert hash(partition1) == hash(partition2)
        
        # Different partitions should have different hashes (with high probability)
        assert hash(partition1) != hash(partition3)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test invalid array
        with pytest.raises(ValueError):
            Partition([])
        
        # Test invalid string
        with pytest.raises(ValueError):
            Partition.from_string("invalid")
        
        # Test invalid print type
        with pytest.raises(ValueError):
            PrintType("invalid")
        
        # Test join_blocks with same representatives
        partition = Partition([-1, -1, -1, -1])
        with pytest.raises(ValueError, match="Cannot join a block with itself"):
            partition.join_blocks(0, 0)
        
        # Test join_blocks with non-representatives
        # Use a partition where element 1 is not a representative: [-2, 0, -1, -1] = |0,1|2|3|
        partition_with_non_rep = Partition([-2, 0, -1, -1])
        with pytest.raises(ValueError, match="Both arguments must be representatives"):
            partition_with_non_rep.join_blocks(0, 1)  # 1 is not a representative
        
        # Test join with different universe sizes
        partition1 = Partition([-1, -1])
        partition2 = Partition([-1, -1, -1])
        with pytest.raises(ValueError, match="Partitions must have the same universe size"):
            partition1.join(partition2)
        
        # Test meet with different universe sizes
        with pytest.raises(ValueError, match="Partitions must have the same universe size"):
            partition1.meet(partition2)
        
        # Test block_index with invalid element
        partition = Partition([-2, 0, -1, -1])
        with pytest.raises(ValueError, match="Element not found in representatives"):
            partition.block_index(5)  # Out of bounds
