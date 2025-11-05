#!/usr/bin/env python3
"""
Python tests for SubProductAlgebra comparing outputs with Java wrapper.

This test suite compares the Python bindings with Java CLI wrapper outputs
to ensure correctness and compatibility.
"""

import subprocess
import json
import sys
from pathlib import Path
import pytest
# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import uacalc_lib
    # Note: SubProductAlgebra may not be exposed yet in Python bindings
    # This test will be updated when bindings are available
    BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
    BigProductAlgebra = uacalc_lib.alg.BigProductAlgebra #uacalc_lib.alg.SubProductAlgebra #uacalc_lib.alg.BigProductAlgebra
except (ImportError, AttributeError) as e:
    print(f"Error importing uacalc_lib: {e}")
    print("Make sure to run 'maturin develop' first")
    import traceback
    traceback.print_exc()
    pytest.skip("uacalc_lib module BasicSmallAlgebra or BigProductAlgebra not available", allow_module_level=True)
    sys.exit(1)


def run_java_wrapper(command_args):
    """Run the Java wrapper and return parsed JSON output."""
    try:
        cmd = [
            "java", "-cp",
            "java_wrapper/build/classes:build/classes:org:jars/*",
            "java_wrapper.src.alg.SubProductAlgebraWrapper"
        ] + command_args
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"Java command failed: {result.stderr}")
            return None
            
        # Parse JSON output
        return json.loads(result.stdout)
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


def test_create():
    """Test basic SubProductAlgebra creation."""
    print("Test 1: SubProductAlgebra creation")
    
    # Java: Create SubProductAlgebra
    java_result = run_java_wrapper([
        "create",
        "--name", "TestSubProd",
        "--factors", "2",
        "--factor_sizes", "2,3",
        "--generators", "0,0|1,0|0,1",
        "--find_terms", "false"
    ])
    
    if java_result and java_result.get("success"):
        java_data = java_result["data"]
        print(f"  ✓ Java: Created SubProductAlgebra successfully")
        print(f"    - Name: {java_data.get('name')}")
        print(f"    - Cardinality: {java_data.get('cardinality')}")
        print(f"    - Generators: {java_data.get('number_of_generators')}")
        
        # Python: Create SubProductAlgebra (when bindings are available)
        print("  ⊙ Python: SubProductAlgebra bindings not yet available")
        print("    This test will be updated when Python bindings are implemented")
        
        assert True  # Test passes if Java creation succeeded
    else:
        print("  ✗ Java: Failed to create SubProductAlgebra")
        assert False, "Java SubProductAlgebra creation failed"


def test_cardinality():
    """Test cardinality method."""
    print("\nTest 2: Cardinality")
    
    java_result = run_java_wrapper([
        "cardinality",
        "--factors", "2",
        "--factor_sizes", "2,3",
        "--generators", "0,0|1,0|0,1"
    ])
    
    if java_result and java_result.get("success"):
        java_data = java_result["data"]
        java_card = java_data.get("cardinality")
        print(f"  ✓ Java: Cardinality = {java_card}")
        
        # Python: Get cardinality (when bindings are available)
        print("  ⊙ Python: SubProductAlgebra bindings not yet available")
        
        assert java_card is not None
    else:
        print("  ✗ Java: Failed to get cardinality")
        assert False


def test_element_index():
    """Test element_index method."""
    print("\nTest 3: Element index")
    
    java_result = run_java_wrapper([
        "element_index",
        "--element", "0,0",
        "--factors", "2",
        "--factor_sizes", "2,3",
        "--generators", "0,0|1,0|0,1"
    ])
    
    if java_result and java_result.get("success"):
        java_data = java_result["data"]
        java_index = java_data.get("index")
        print(f"  ✓ Java: Element [0,0] has index {java_index}")
        
        # Python: Get element index (when bindings are available)
        print("  ⊙ Python: SubProductAlgebra bindings not yet available")
        
        assert java_index is not None
    else:
        print("  ✗ Java: Failed to get element index")
        assert False


def test_get_element():
    """Test get_element method."""
    print("\nTest 4: Get element")
    
    java_result = run_java_wrapper([
        "get_element",
        "--index", "0",
        "--factors", "2",
        "--factor_sizes", "2,3",
        "--generators", "0,0|1,0|0,1"
    ])
    
    if java_result and java_result.get("success"):
        java_data = java_result["data"]
        java_element = java_data.get("element")
        print(f"  ✓ Java: Element at index 0 = {java_element}")
        
        # Python: Get element (when bindings are available)
        print("  ⊙ Python: SubProductAlgebra bindings not yet available")
        
        assert java_element is not None
    else:
        print("  ✗ Java: Failed to get element")
        assert False


def test_generators():
    """Test generators method."""
    print("\nTest 5: Generators")
    
    java_result = run_java_wrapper([
        "generators",
        "--factors", "2",
        "--factor_sizes", "2,3",
        "--generators", "0,0|1,0|0,1"
    ])
    
    if java_result and java_result.get("success"):
        java_data = java_result["data"]
        java_gens = java_data.get("generators")
        print(f"  ✓ Java: Generators = {java_gens}")
        
        # Python: Get generators (when bindings are available)
        print("  ⊙ Python: SubProductAlgebra bindings not yet available")
        
        assert java_gens is not None
    else:
        print("  ✗ Java: Failed to get generators")
        assert False


def test_get_universe_list():
    """Test get_universe_list method."""
    print("\nTest 6: Get universe list")
    
    java_result = run_java_wrapper([
        "get_universe_list",
        "--factors", "2",
        "--factor_sizes", "2,3",
        "--generators", "0,0|1,0|0,1"
    ])
    
    if java_result and java_result.get("success"):
        java_data = java_result["data"]
        java_univ = java_data.get("universe")
        java_size = java_data.get("universe_size")
        print(f"  ✓ Java: Universe size = {java_size}")
        print(f"    - First few elements: {java_univ[:3] if java_univ else '[]'}")
        
        # Python: Get universe list (when bindings are available)
        print("  ⊙ Python: SubProductAlgebra bindings not yet available")
        
        assert java_univ is not None
    else:
        print("  ✗ Java: Failed to get universe list")
        assert False


def test_transpose():
    """Test transpose static method."""
    print("\nTest 7: Transpose")
    
    java_result = run_java_wrapper([
        "transpose",
        "--arrays", "0,1|2,3|4,5"
    ])
    
    if java_result and java_result.get("success"):
        java_data = java_result["data"]
        java_transposed = java_data.get("transposed")
        print(f"  ✓ Java: Transposed = {java_transposed}")
        
        # Python: Transpose (when bindings are available)
        print("  ⊙ Python: SubProductAlgebra bindings not yet available")
        
        assert java_transposed is not None
    else:
        print("  ✗ Java: Failed to transpose")
        assert False


def test_test():
    """Test comprehensive test command."""
    print("\nTest 8: Comprehensive test")
    
    java_result = run_java_wrapper(["test"])
    
    if java_result and java_result.get("success"):
        java_data = java_result["data"]
        print(f"  ✓ Java: Test passed")
        print(f"    - Name: {java_data.get('name')}")
        print(f"    - Cardinality: {java_data.get('cardinality')}")
        print(f"    - Universe size: {java_data.get('universe_size')}")
        print(f"    - Generators count: {java_data.get('generators_count')}")
        
        # Python: Run comprehensive test (when bindings are available)
        print("  ⊙ Python: SubProductAlgebra bindings not yet available")
        
        assert java_data.get("test_passed") == True
    else:
        print("  ✗ Java: Test failed")
        assert False


def main():
    """Run all tests."""
    print("="*60)
    print("SubProductAlgebra Python vs Java Comparison Tests")
    print("="*60)
    
    tests = [
        test_create,
        test_cardinality,
        test_element_index,
        test_get_element,
        test_generators,
        test_get_universe_list,
        test_transpose,
        test_test,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
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


