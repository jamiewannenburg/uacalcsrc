#!/usr/bin/env python3
"""
Simple test script to verify UACalc installation
"""

try:
    import uacalc
    print("✅ UACalc imported successfully!")
    
    # Try to create a simple algebra
    try:
        algebra = uacalc.create_algebra("TestAlgebra", [0, 1, 2])
        print("✅ Algebra creation successful!")
        
        # Try to create a simple operation
        table = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]
        operation = uacalc.create_operation("multiply", 2, table)
        print("✅ Operation creation successful!")
        
        # Test the operation
        result = operation.value([1, 2])
        print(f"✅ Operation test successful: 1 * 2 = {result}")
        
    except Exception as e:
        print(f"⚠️  Some functionality not working: {e}")
        
except ImportError as e:
    print(f"❌ Failed to import UACalc: {e}")
    print("Please make sure you have run 'maturin develop' in the uacalc-py directory")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\nTest completed!")
