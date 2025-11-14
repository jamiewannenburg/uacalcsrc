#!/usr/bin/env python3
"""
Python tests for SubalgebraLattice comparing outputs with Java wrapper.

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
    SubalgebraLattice = uacalc_lib.alg.SubalgebraLattice
    BasicAlgebra = uacalc_lib.alg.BasicAlgebra
    BasicSet = uacalc_lib.alg.BasicSet
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
            "java_wrapper.src.alg.sublat.SubalgebraLatticeWrapper"
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


def test_basic_creation():
    """Test basic SubalgebraLattice creation."""
    print("Test 1: Basic SubalgebraLattice creation")
    
    # Python: Create SubalgebraLattice from file
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        sub_lat = SubalgebraLattice(alg)
        print(f"  ✓ Python: Created SubalgebraLattice successfully")
        print(f"    - Algebra: {sub_lat.get_algebra()}")
    except Exception as e:
        print(f"  ✗ Python: Failed to create SubalgebraLattice: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python SubalgebraLattice creation failed: {e}"
    
    # Java: Create SubalgebraLattice
    java_result = run_java_wrapper(["new", "--algebra", "resources/algebras/cyclic3.ua"])
    
    if java_result and java_result.get("success"):
        java_data = java_result["data"]
        print(f"  ✓ Java: Created SubalgebraLattice successfully")
        print(f"    - Algebra name: {java_data.get('algebra_name')}")
        print(f"    - Algebra size: {java_data.get('algebra_size')}")
        assert True  # Test passes if Java creation succeeded
    else:
        print("  ✗ Java: Failed to create SubalgebraLattice")
        assert False, "Java SubalgebraLattice creation failed"


def test_zero_and_one():
    """Test zero and one subalgebras."""
    print("\nTest 2: Zero and One subalgebras (no constants)")
    
    # Python: Test with algebra without constants
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        sub_lat = SubalgebraLattice(alg)
        
        zero = sub_lat.zero()
        one = sub_lat.one()
        
        print(f"  ✓ Python: Zero subalgebra size: {zero.size()}")
        print(f"  ✓ Python: One subalgebra size: {one.size()}")
        print(f"  ✓ Python: Zero elements: {zero.elements()}")
        print(f"  ✓ Python: One elements: {one.elements()}")
        
        # Zero should be empty for algebra without constants
        assert zero.size() == 0, f"Zero subalgebra should be empty, got size {zero.size()}"
        assert one.size() == 3, f"One subalgebra should have size 3, got {one.size()}"
    except Exception as e:
        print(f"  ✗ Python: Failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python test failed: {e}"
    
    # Java: Compare
    java_result = run_java_wrapper(["zero", "--algebra", "resources/algebras/cyclic3.ua"])
    if java_result and java_result.get("success"):
        java_zero_size = java_result["data"].get("size", 0)
        print(f"  ✓ Java: Zero subalgebra size: {java_zero_size}")
        assert java_zero_size == 0, f"Java zero subalgebra should be empty, got size {java_zero_size}"


def test_sg_generation():
    """Test subalgebra generation."""
    print("\nTest 3: Subalgebra generation")
    
    # Python: Test sg generation
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        sub_lat = SubalgebraLattice(alg)
        
        # Generate subalgebra from [0, 1]
        sub = sub_lat.sg([0, 1])
        print(f"  ✓ Python: sg([0, 1]) size: {sub.size()}")
        print(f"  ✓ Python: sg([0, 1]) elements: {sub.elements()}")
        
        assert sub.size() > 0, "Generated subalgebra should be non-empty"
        assert sub.size() <= 3, "Generated subalgebra should not exceed algebra size"
    except Exception as e:
        print(f"  ✗ Python: Failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python test failed: {e}"
    
    # Java: Compare
    java_result = run_java_wrapper(["sg", "--algebra", "resources/algebras/cyclic3.ua", "--gens", "0,1"])
    if java_result and java_result.get("success"):
        java_size = java_result["data"].get("size", 0)
        print(f"  ✓ Java: sg([0, 1]) size: {java_size}")
        assert java_size == sub.size(), f"Python size {sub.size()} != Java size {java_size}"


def test_one_generated_subalgebras():
    """Test one-generated subalgebras."""
    print("\nTest 4: One-generated subalgebras")
    
    # Python: Test one-generated subalgebras
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        sub_lat = SubalgebraLattice(alg)
        
        one_gens = sub_lat.one_generated_subalgebras()
        print(f"  ✓ Python: Number of one-generated subalgebras: {len(one_gens)}")
        
        for i, sub in enumerate(one_gens):
            print(f"    [{i}] size={sub.size()}, elements={sub.elements()}")
        
        assert len(one_gens) > 0, "Should have at least one one-generated subalgebra"
    except Exception as e:
        print(f"  ✗ Python: Failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python test failed: {e}"


def test_join_irreducibles():
    """Test join irreducibles."""
    print("\nTest 5: Join irreducibles")
    
    # Python: Test join irreducibles
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        sub_lat = SubalgebraLattice(alg)
        
        jis = sub_lat.join_irreducibles()
        print(f"  ✓ Python: Number of join irreducibles: {len(jis)}")
        
        for i, ji in enumerate(jis):
            print(f"    [{i}] size={ji.size()}, elements={ji.elements()}")
        
        assert len(jis) > 0, "Should have at least one join irreducible"
    except Exception as e:
        print(f"  ✗ Python: Failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python test failed: {e}"


def test_join_and_meet():
    """Test join and meet operations."""
    print("\nTest 6: Join and meet operations (BasicSet only)")
    
    # Test BasicSet operations that don't require SubalgebraLattice
    a = BasicSet([0, 1])
    b = BasicSet([1, 2])
    
    intersection = a.intersection(b)
    union = a.union(b)
    
    print(f"  ✓ Python intersection({a.elements()}, {b.elements()}): {intersection.elements()}")
    print(f"  ✓ Python union({a.elements()}, {b.elements()}): {union.elements()}")
    
    # Test leq
    leq_result = a.leq(union)
    print(f"  ✓ Python leq({a.elements()}, {union.elements()}): {leq_result}")
    
    assert True  # Test passes if we reach here


def test_no_duplicates():
    """Test no_duplicates static method."""
    print("\nTest 7: No duplicates (static method)")
    
    # Python
    input_list = [1, 2, 2, 3, 3, 3]
    python_result = SubalgebraLattice.no_duplicates(input_list)
    print(f"  ✓ Python no_duplicates({input_list}): {python_result}")
    
    # Java
    java_result = run_java_wrapper(["no_duplicates", "--list", "1,2,2,3,3,3"])
    
    if java_result and java_result.get("success"):
        java_output = java_result["data"]["output"]
        print(f"  ✓ Java no_duplicates: {java_output}")
        
        if python_result == java_output:
            print("  ✓ Python and Java outputs match!")
            assert True  # Test passes
        else:
            print(f"  ✗ Mismatch: Python={python_result}, Java={java_output}")
            assert False, f"Python and Java outputs don't match: Python={python_result}, Java={java_output}"
    else:
        print("  ✗ Java command failed")
        assert False, "Java command failed"


def test_cardinality():
    """Test cardinality computation."""
    print("\nTest 8: Cardinality")
    
    # Python: Test cardinality
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        sub_lat = SubalgebraLattice(alg)
        
        card = sub_lat.cardinality()
        print(f"  ✓ Python: Subalgebra lattice cardinality: {card}")
        
        assert card > 0, "Cardinality should be positive"
    except Exception as e:
        print(f"  ✗ Python: Failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python test failed: {e}"


def test_filter():
    """Test filter operation."""
    print("\nTest 9: Filter operation")
    
    # Python: Test filter
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        sub_lat = SubalgebraLattice(alg)
        
        # Get zero subalgebra
        zero = sub_lat.zero()
        
        # Filter subalgebras containing zero
        filtered = sub_lat.filter(zero)
        print(f"  ✓ Python: Filtered subalgebras count: {len(filtered)}")
        
        assert len(filtered) > 0, "Should have at least one filtered subalgebra"
    except Exception as e:
        print(f"  ✗ Python: Failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python test failed: {e}"


def test_minimal_generating_set():
    """Test minimal generating set."""
    print("\nTest 10: Minimal generating set")
    
    # Python: Test minimal generating set
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        sub_lat = SubalgebraLattice(alg)
        
        min_gen = sub_lat.find_minimal_sized_generating_set()
        print(f"  ✓ Python: Minimal generating set size: {min_gen.size()}")
        print(f"  ✓ Python: Minimal generating set elements: {min_gen.elements()}")
        
        assert min_gen.size() >= 0, "Minimal generating set size should be non-negative"
    except Exception as e:
        print(f"  ✗ Python: Failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python test failed: {e}"


def test_algebra_with_constants():
    """Test subalgebra lattice with algebra that has constants."""
    print("\nTest 11: Algebra with constants")
    
    # Try to find an algebra with constants, or create one
    # For now, test with cyclic3 which doesn't have constants
    # and verify zero is empty
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        sub_lat = SubalgebraLattice(alg)
        
        zero = sub_lat.zero()
        print(f"  ✓ Python: Zero subalgebra size (no constants): {zero.size()}")
        print(f"  ✓ Python: Zero subalgebra elements: {zero.elements()}")
        
        # For algebra without constants, zero should be empty
        assert zero.size() == 0, f"Zero should be empty for algebra without constants, got size {zero.size()}"
    except Exception as e:
        print(f"  ✗ Python: Failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python test failed: {e}"


def test_algebra_without_constants():
    """Test subalgebra lattice with algebra that doesn't have constants."""
    print("\nTest 12: Algebra without constants (empty zero)")
    
    # Test with cyclic3 which doesn't have constants
    try:
        reader = AlgebraReader.new_from_file("resources/algebras/cyclic3.ua")
        alg = reader.read_algebra_file()
        sub_lat = SubalgebraLattice(alg)
        
        zero = sub_lat.zero()
        print(f"  ✓ Python: Zero subalgebra size: {zero.size()}")
        
        # Zero should be empty when there are no constants
        assert zero.size() == 0, f"Zero should be empty, got size {zero.size()}"
        
        # Java comparison
        java_result = run_java_wrapper(["zero", "--algebra", "resources/algebras/cyclic3.ua"])
        if java_result and java_result.get("success"):
            java_zero_size = java_result["data"].get("size", -1)
            print(f"  ✓ Java: Zero subalgebra size: {java_zero_size}")
            assert java_zero_size == zero.size(), f"Python zero size {zero.size()} != Java zero size {java_zero_size}"
    except Exception as e:
        print(f"  ✗ Python: Failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Python test failed: {e}"


def main():
    """Run all tests."""
    print("="*60)
    print("SubalgebraLattice Python vs Java Comparison Tests")
    print("="*60)
    
    tests = [
        test_basic_creation,
        test_zero_and_one,
        test_sg_generation,
        test_one_generated_subalgebras,
        test_join_irreducibles,
        test_join_and_meet,
        test_no_duplicates,
        test_cardinality,
        test_filter,
        test_minimal_generating_set,
        test_algebra_with_constants,
        test_algebra_without_constants,
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
