#!/usr/bin/env python3
"""
Test the refactored methods without building the full universe.
"""

import uacalc_rust as uacalc

def test_without_universe():
    """Test the refactored methods without building the full universe."""
    
    print("Creating simple algebra...")
    algebra = uacalc.create_algebra("test", [0, 1])
    
    print("Creating congruence lattice...")
    lattice = uacalc.create_congruence_lattice(algebra)
    
    print("Testing size() method (should work without building universe)...")
    size = lattice.size()
    print(f"Lattice size: {size}")
    
    print("Testing principal_congruence() method...")
    try:
        principal = lattice.principal_congruence(0, 1)
        print(f"Principal congruence θ(0,1): {principal.blocks()}")
    except Exception as e:
        print(f"Principal congruence failed: {e}")
    
    print("✅ Test completed!")

if __name__ == "__main__":
    test_without_universe()
