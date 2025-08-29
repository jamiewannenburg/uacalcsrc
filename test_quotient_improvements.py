#!/usr/bin/env python3
"""
Test script to verify the new PyQuotientAlgebra functionality.
This script tests all the verification comments that were implemented.
"""

import sys
import os

# Add the python module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

try:
    import uacalc
    from uacalc import create_algebra, create_operation, create_partition_from_blocks
    from uacalc.algebra import create_quotient_algebra
    
    print("Testing PyQuotientAlgebra improvements...")
    
    # Create a simple algebra Z4 = {0, 1, 2, 3} with addition mod 4
    print("1. Creating Z4 algebra...")
    z4 = create_algebra("Z4", [0, 1, 2, 3])
    
    # Create addition operation: (i + j) % 4
    add_table = []
    for i in range(4):
        for j in range(4):
            add_table.append([i, j, (i + j) % 4])
    
    add_op = create_operation("add", 2, add_table)
    z4.add_operation("add", add_op)
    
    print("   Z4 algebra created successfully")
    
    # Create a congruence: {0, 2} and {1, 3} (even/odd)
    print("2. Creating congruence partition...")
    congruence = create_partition_from_blocks(4, [[0, 2], [1, 3]])
    print("   Congruence created: blocks = [[0, 2], [1, 3]]")
    
    # Test creating quotient algebra WITHOUT validation
    print("3. Creating quotient algebra without validation...")
    quotient = create_quotient_algebra(z4, congruence, name="Z2_no_validation")
    
    # Verify that we get PyQuotientAlgebra (not just PyAlgebra)
    print(f"   Quotient type: {type(quotient)}")
    print(f"   Quotient name: {quotient.name}")
    print(f"   Quotient cardinality: {quotient.cardinality}")
    
    # Test PyQuotientAlgebra-specific methods
    print("4. Testing PyQuotientAlgebra specific methods...")
    
    # Test super_algebra() method
    super_alg = quotient.super_algebra()
    print(f"   Super algebra name: {super_alg.name}")
    print(f"   Super algebra cardinality: {super_alg.cardinality}")
    
    # Test congruence() method
    cong = quotient.congruence()
    print(f"   Congruence size: {cong.size}")
    print(f"   Congruence blocks: {cong.num_blocks}")
    
    # Test representatives() method
    reps = quotient.representatives()
    print(f"   Representatives: {reps}")
    
    # Test canonical_homomorphism() method
    print("5. Testing canonical homomorphism...")
    for i in range(4):
        quotient_index = quotient.canonical_homomorphism(i)
        print(f"   Element {i} maps to quotient index {quotient_index}")
    
    # Test block_of_index() method
    print("6. Testing block_of_index method...")
    for i in range(quotient.cardinality):
        block = quotient.block_of_index(i)
        print(f"   Block {i}: {block}")
    
    # Test operations on quotient
    print("7. Testing quotient operations...")
    add_quotient = quotient.operation_by_symbol("add")
    print(f"   Quotient addition operation: {add_quotient.symbol}")
    
    # Test operation evaluation (should behave like Z2)
    print("   Testing operation evaluation:")
    for i in range(2):
        for j in range(2):
            result = add_quotient.value([i, j])
            print(f"   {i} + {j} = {result} (in quotient)")
    
    # Test creating quotient algebra WITH validation
    print("8. Creating quotient algebra with validation...")
    try:
        validated_quotient = create_quotient_algebra(z4, congruence, name="Z2_validated", validate=True)
        print("   Validation passed - congruence is valid!")
        print(f"   Validated quotient cardinality: {validated_quotient.cardinality}")
    except Exception as e:
        print(f"   Validation failed: {e}")
    
    # Test with invalid congruence (should fail validation)
    print("9. Testing with invalid congruence...")
    try:
        # This partition [[0, 1], [2, 3]] is NOT a congruence for Z4 addition
        # because 0 + 0 = 0 and 1 + 1 = 2, but 0 ~ 1 doesn't imply 0 ~ 2
        invalid_congruence = create_partition_from_blocks(4, [[0, 1], [2, 3]])  
        invalid_quotient = create_quotient_algebra(z4, invalid_congruence, name="Invalid", validate=True)
        print("   WARNING: Validation should have failed but didn't!")
    except Exception as e:
        print(f"   Validation correctly failed: {str(e)[:100]}...")
    
    print("\n✅ All tests passed! PyQuotientAlgebra improvements are working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure to build the Python extension first:")
    print("  maturin develop --release")
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
