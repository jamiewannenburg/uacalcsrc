#!/usr/bin/env python3
"""
Test script for memory limiting functionality in UACalc Rust bindings.

This script demonstrates how to set memory limits and how they prevent
excessive memory allocation during free algebra generation.
"""

import uacalc_rust as ua
import sys

def test_memory_limiting():
    """Test memory limiting with free algebra generation."""
    
    print("=== UACalc Memory Limiting Test ===")
    print()
    
    # Test 1: Check if memory limit functions are available
    print("1. Checking memory limit functions availability...")
    try:
        current_limit = ua.get_memory_limit()
        print(f"   Current memory limit: {current_limit:,} bytes ({current_limit / (1024*1024):.1f} MB)")
        print("   ✓ Memory limit functions are available")
    except AttributeError:
        print("   ✗ Memory limit functions not available (memory-limit feature not enabled)")
        print("   To enable memory limiting, rebuild with: cargo build --features memory-limit")
        return False
    
    print()
    
    # Test 2: Set a small memory limit
    print("2. Setting memory limit to 10 MB...")
    limit_bytes = 10 * 1024 * 1024  # 10 MB
    try:
        ua.set_memory_limit(limit_bytes)
        print(f"   ✓ Memory limit set to {limit_bytes:,} bytes ({limit_bytes / (1024*1024):.1f} MB)")
    except Exception as e:
        print(f"   ✗ Failed to set memory limit: {e}")
        return False
    
    print()
    
    # Test 3: Check current memory usage
    print("3. Checking current memory usage...")
    allocated = ua.get_allocated_memory()
    peak = ua.get_peak_allocated_memory()
    print(f"   Currently allocated: {allocated:,} bytes ({allocated / 1024:.1f} KB)")
    print(f"   Peak allocated: {peak:,} bytes ({peak / 1024:.1f} KB)")
    
    print()
    
    # Test 4: Estimate memory for a small free algebra
    print("4. Estimating memory for small free algebra...")
    try:
        estimate = ua.estimate_free_algebra_memory(
            num_generators=2,
            num_operations=1,
            max_depth=2,
            operation_arities=[2]
        )
        print(f"   Estimated memory: {estimate:,} bytes ({estimate / 1024:.1f} KB)")
        
        # Check if it would exceed limit
        would_exceed = ua.would_exceed_limit(estimate)
        print(f"   Would exceed limit: {would_exceed}")
        
    except Exception as e:
        print(f"   ✗ Failed to estimate memory: {e}")
        return False
    
    print()
    
    # Test 5: Try to create a small free algebra (should succeed)
    print("5. Creating small free algebra (should succeed)...")
    try:
        generators = ["x", "y"]
        operations = [ua.OperationSymbol("*", 2)]
        variety = ua.VarietyConstraint("trivial")
        
        # Check memory limit before creation
        ua.check_free_algebra_memory_limit(2, 1, 2, [2])
        
        free_algebra = ua.create_free_algebra(
            name="SmallTest",
            generators=generators,
            variety_constraints=variety,
            operation_symbols=operations,
            max_depth=2
        )
        
        print(f"   ✓ Created free algebra '{free_algebra.name()}' with {free_algebra.cardinality()} elements")
        
    except Exception as e:
        print(f"   ✗ Failed to create small free algebra: {e}")
        return False
    
    print()
    
    # Test 6: Try to create a larger free algebra (should fail due to memory limit)
    print("6. Creating larger free algebra (should fail due to memory limit)...")
    try:
        generators = ["x", "y", "z"]
        operations = [ua.OperationSymbol("*", 2), ua.OperationSymbol("+", 2)]
        variety = ua.VarietyConstraint("trivial")
        
        # This should fail due to memory limit
        free_algebra = ua.create_free_algebra(
            name="LargeTest",
            generators=generators,
            variety_constraints=variety,
            operation_symbols=operations,
            max_depth=3
        )
        
        print(f"   ✗ Unexpectedly succeeded in creating large free algebra: {free_algebra.name()}")
        return False
        
    except Exception as e:
        print(f"   ✓ Correctly failed to create large free algebra: {e}")
    
    print()
    
    # Test 7: Increase memory limit and try again
    print("7. Increasing memory limit and trying again...")
    try:
        # Increase limit to 100 MB
        new_limit = 100 * 1024 * 1024  # 100 MB
        ua.set_memory_limit(new_limit)
        print(f"   ✓ Increased memory limit to {new_limit:,} bytes ({new_limit / (1024*1024):.1f} MB)")
        
        # Try creating the larger algebra again
        free_algebra = ua.create_free_algebra(
            name="LargeTest",
            generators=generators,
            variety_constraints=variety,
            operation_symbols=operations,
            max_depth=3
        )
        
        print(f"   ✓ Successfully created large free algebra '{free_algebra.name()}' with {free_algebra.cardinality()} elements")
        
    except Exception as e:
        print(f"   ✗ Still failed to create large free algebra: {e}")
        return False
    
    print()
    
    # Test 8: Check final memory usage
    print("8. Final memory usage...")
    allocated = ua.get_allocated_memory()
    peak = ua.get_peak_allocated_memory()
    print(f"   Currently allocated: {allocated:,} bytes ({allocated / (1024*1024):.1f} MB)")
    print(f"   Peak allocated: {peak:,} bytes ({peak / (1024*1024):.1f} MB)")
    
    print()
    print("=== All tests passed! ===")
    return True

if __name__ == "__main__":
    success = test_memory_limiting()
    sys.exit(0 if success else 1)


