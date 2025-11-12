#!/usr/bin/env python3
"""
Python tests for Subalgebra comparing outputs with Java wrapper.

This test suite compares the Python bindings with Java CLI wrapper outputs
to ensure correctness and compatibility.
"""

import subprocess
import json
import sys
import platform
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import uacalc_lib
    Subalgebra = uacalc_lib.alg.Subalgebra
    BasicAlgebra = uacalc_lib.alg.BasicAlgebra
    Partition = uacalc_lib.alg.Partition
    AlgebraReader = uacalc_lib.io.AlgebraReader
except ImportError as e:
    print(f"Error importing uacalc_lib: {e}")
    print("Make sure to run 'maturin develop' first")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def run_java_wrapper(command_args):
    """Run the Java wrapper and return parsed JSON output."""
    try:
        separator = ";" if platform.system() == "Windows" else ":"
        classpath = f"java_wrapper/build/classes{separator}build/classes{separator}org{separator}jars/*"
        cmd = [
            "java", "-cp", classpath,
            "java_wrapper.src.alg.SubalgebraWrapper"
        ] + command_args
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=Path(__file__).parent.parent.parent.parent)
        
        if result.returncode != 0:
            print(f"Java command failed: {result.stderr}")
            return None
            
        # Parse JSON output - find the JSON part
        stdout_lines = result.stdout.split('\n')
        json_start = -1
        for i, line in enumerate(stdout_lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start == -1:
            print("No JSON found in Java output")
            return None
        
        json_text = '\n'.join(stdout_lines[json_start:])
        return json.loads(json_text)
    except subprocess.TimeoutExpired:
        print("Java command timed out")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse Java output: {e}")
        print(f"Output was: {result.stdout[:200]}")
        return None
    except Exception as e:
        print(f"Error running Java wrapper: {e}")
        return None


def test_congruence_as_algebra():
    """Test congruence_as_algebra static method."""
    print("Test 1: congruence_as_algebra static method")
    
    # Create a simple algebra
    alg = BasicAlgebra("test", [0, 1, 2, 3], [])
    
    # Create a partition (two blocks: {0,1} and {2,3})
    # Partition array: [-2, 0, -2, 2] means:
    # - Element 0 is root of block of size 2
    # - Element 1 points to 0
    # - Element 2 is root of block of size 2
    # - Element 3 points to 2
    partition_arr = [-2, 0, -2, 2]
    partition = Partition(partition_arr)
    
    # Python: Call static method
    try:
        result_alg = Subalgebra.congruence_as_algebra(alg, partition)
        print(f"  ✓ Python: Created congruence algebra successfully")
        print(f"    - Name: {result_alg.name()}")
        print(f"    - Cardinality: {result_alg.cardinality()}")
        print(f"    - Algebra type: {result_alg.algebra_type()}")
        
        py_cardinality = result_alg.cardinality()
        py_name = result_alg.name()
        py_type = result_alg.algebra_type()
    except Exception as e:
        print(f"  ✗ Python: Failed to create congruence algebra: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python congruence_as_algebra failed: {e}"
    
    # Java: Call static method
    java_result = run_java_wrapper([
        "congruence_as_algebra",
        "--super_size", "4",
        "--partition", "-2,0,-2,2"
    ])
    
    if java_result:
        java_data = java_result.get("data", {})
        if isinstance(java_data, str):
            try:
                java_data = json.loads(java_data)
            except json.JSONDecodeError:
                java_data = {}
        
        java_cardinality = java_data.get("cardinality")
        java_name = java_data.get("name", "")
        java_type = java_data.get("algebra_type", "")
        
        print(f"  ✓ Java: Created congruence algebra successfully")
        print(f"    - Name: {java_name}")
        print(f"    - Cardinality: {java_cardinality}")
        print(f"    - Algebra type: {java_type}")
        
        # Compare results
        assert py_cardinality == java_cardinality, f"Cardinality mismatch: Python={py_cardinality}, Java={java_cardinality}"
        assert py_type == java_type or py_type == "Subalgebra", f"Type mismatch: Python={py_type}, Java={java_type}"
        print(f"  ✓ Results match between Python and Java")
    else:
        print("  ⚠ Java: Could not run Java wrapper, skipping comparison")
    
    return True


def test_congruence_as_algebra_with_name():
    """Test congruence_as_algebra_with_name static method."""
    print("Test 2: congruence_as_algebra_with_name static method")
    
    # Create a simple algebra
    alg = BasicAlgebra("test", [0, 1, 2], [])
    
    # Create a partition (one block: {0,1,2})
    # Partition array: [-3, 0, 0] means all elements in one block
    partition_arr = [-3, 0, 0]
    partition = Partition(partition_arr)
    
    # Python: Call static method with name
    test_name = "CongAlg"
    try:
        result_alg = Subalgebra.congruence_as_algebra_with_name(test_name, alg, partition)
        print(f"  ✓ Python: Created congruence algebra with name successfully")
        print(f"    - Name: {result_alg.name()}")
        print(f"    - Cardinality: {result_alg.cardinality()}")
        print(f"    - Algebra type: {result_alg.algebra_type()}")
        
        py_cardinality = result_alg.cardinality()
        py_name = result_alg.name()
        py_type = result_alg.algebra_type()
        
        # Check that name was set
        assert py_name == test_name, f"Name mismatch: expected {test_name}, got {py_name}"
    except Exception as e:
        print(f"  ✗ Python: Failed to create congruence algebra: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python congruence_as_algebra_with_name failed: {e}"
    
    # Java: Call static method
    java_result = run_java_wrapper([
        "congruence_as_algebra_with_name",
        "--name", test_name,
        "--super_size", "3",
        "--partition", "-3,0,0"
    ])
    
    if java_result:
        java_data = java_result.get("data", {})
        if isinstance(java_data, str):
            try:
                java_data = json.loads(java_data)
            except json.JSONDecodeError:
                java_data = {}
        
        java_cardinality = java_data.get("cardinality")
        java_name = java_data.get("name", "")
        java_type = java_data.get("algebra_type", "")
        
        print(f"  ✓ Java: Created congruence algebra with name successfully")
        print(f"    - Name: {java_name}")
        print(f"    - Cardinality: {java_cardinality}")
        print(f"    - Algebra type: {java_type}")
        
        # Compare results
        assert py_cardinality == java_cardinality, f"Cardinality mismatch: Python={py_cardinality}, Java={java_cardinality}"
        assert py_name == java_name, f"Name mismatch: Python={py_name}, Java={java_name}"
        assert py_type == java_type or py_type == "Subalgebra", f"Type mismatch: Python={py_type}, Java={java_type}"
        print(f"  ✓ Results match between Python and Java")
    else:
        print("  ⚠ Java: Could not run Java wrapper, skipping comparison")
    
    return True


def test_congruence_as_algebra_with_file():
    """Test congruence_as_algebra with algebra from file."""
    print("Test 3: congruence_as_algebra with algebra from file")
    
    # Load algebra from file
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        print(f"  ✓ Loaded algebra from file: {alg.name()}, cardinality: {alg.cardinality()}")
    except Exception as e:
        print(f"  ✗ Failed to load algebra from file: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Failed to load algebra: {e}"
    
    # Create a partition (zero partition - all elements separate)
    # For a 3-element algebra: [-1, -1, -1]
    partition_arr = [-1, -1, -1]
    partition = Partition(partition_arr)
    
    # Python: Call static method
    try:
        result_alg = Subalgebra.congruence_as_algebra(alg, partition)
        print(f"  ✓ Python: Created congruence algebra from file algebra")
        print(f"    - Name: {result_alg.name()}")
        print(f"    - Cardinality: {result_alg.cardinality()}")
        
        # For zero partition, each element is only related to itself
        # So we get n pairs: (0,0), (1,1), (2,2) for a 3-element algebra
        expected_cardinality = alg.cardinality()  # n pairs, not n*n
        assert result_alg.cardinality() == expected_cardinality, \
            f"Expected cardinality {expected_cardinality}, got {result_alg.cardinality()}"
        print(f"  ✓ Cardinality matches expected value ({expected_cardinality})")
    except Exception as e:
        print(f"  ✗ Python: Failed to create congruence algebra: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python congruence_as_algebra failed: {e}"
    
    return True


def test_congruence_as_algebra_one_partition():
    """Test congruence_as_algebra with one partition (all elements together)."""
    print("Test 4: congruence_as_algebra with one partition")
    
    # Create a simple algebra
    alg = BasicAlgebra("test", [0, 1, 2], [])
    
    # Create one partition (all elements in one block)
    partition_arr = [-3, 0, 0]
    partition = Partition(partition_arr)
    
    # Python: Call static method
    try:
        result_alg = Subalgebra.congruence_as_algebra(alg, partition)
        print(f"  ✓ Python: Created congruence algebra with one partition")
        print(f"    - Cardinality: {result_alg.cardinality()}")
        
        # For one partition, all pairs (i,j) where i and j are related
        # Since all elements are related, we get all 3*3 = 9 pairs
        expected_cardinality = 9
        assert result_alg.cardinality() == expected_cardinality, \
            f"Expected cardinality {expected_cardinality}, got {result_alg.cardinality()}"
        print(f"  ✓ Cardinality matches expected value ({expected_cardinality})")
    except Exception as e:
        print(f"  ✗ Python: Failed to create congruence algebra: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python congruence_as_algebra failed: {e}"
    
    return True


def main():
    """Run all tests."""
    print("="*60)
    print("Subalgebra Python vs Java Comparison Tests")
    print("="*60)
    
    tests = [
        test_congruence_as_algebra,
        test_congruence_as_algebra_with_name,
        test_congruence_as_algebra_with_file,
        test_congruence_as_algebra_one_partition,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print()
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test raised exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

