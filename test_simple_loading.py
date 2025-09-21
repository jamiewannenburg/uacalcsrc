#!/usr/bin/env python3
"""
Simple test to debug algebra loading
"""

import sys
import os
sys.path.insert(0, 'python')

def test_simple_loading():
    print("Testing simple algebra loading...")
    
    try:
        import uacalc
        print("Successfully imported uacalc")
        
        # Test loading the baker2.ua algebra
        algebra_file = "resources/algebras/baker2.ua"
        print(f"Attempting to load {algebra_file}...")
        
        algebra = uacalc.load_algebra(algebra_file)
        print(f"Successfully loaded algebra: {algebra.name}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_loading()
