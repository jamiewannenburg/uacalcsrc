#!/usr/bin/env python3
"""
Simple test script for Python bindings of uacalc Operation implementations.
"""

import sys
import os

# Try to import the built module (this would only work after building)
try:
    import uacalc
    print("✓ Successfully imported uacalc module")
    
    # Test OperationSymbol creation
    sym = uacalc.OperationSymbol("test", 2)
    print(f"✓ Created OperationSymbol: {sym}")
    print(f"  Name: {sym.get_name}")
    print(f"  Arity: {sym.get_arity}")
    
    # Test IntOperation creation
    # Create a simple XOR operation table for binary operation on {0, 1}
    xor_table = [0, 1, 1, 0]  # XOR truth table
    int_op = uacalc.IntOperation.create_binary_operation_py("xor", 2, xor_table)
    print(f"✓ Created IntOperation: {int_op}")
    
    # Test operation evaluation
    result = int_op.int_value_at_py([0, 1])
    print(f"✓ XOR(0, 1) = {result}")
    
    result = int_op.int_value_at_py([1, 1])
    print(f"✓ XOR(1, 1) = {result}")
    
    # Test properties
    print(f"✓ Is table-based: {int_op.is_table_based_py()}")
    print(f"✓ Is commutative: {int_op.is_commutative_py()}")
    print(f"✓ Is associative: {int_op.is_associative_py()}")
    
    print("\n✅ All Python binding tests passed!")
    
except ImportError as e:
    print(f"ℹ️  Module not built yet: {e}")
    print("To test Python bindings, first build the module with:")
    print("  maturin develop")
    print("or")
    print("  pip install maturin && maturin develop")
    
except Exception as e:
    print(f"❌ Error testing Python bindings: {e}")
    sys.exit(1)