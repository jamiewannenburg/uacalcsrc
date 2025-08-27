#!/usr/bin/env python3
"""
Simple test to verify the refactored methods work.
"""

import uacalc_rust as uacalc

def simple_test():
    """Simple test of the refactored methods."""
    
    print("Creating simple algebra...")
    algebra = uacalc.create_algebra("test", [0, 1])
    
    print("Creating congruence lattice...")
    lattice = uacalc.create_congruence_lattice(algebra)
    
    print("Testing congruences() method...")
    congruences = lattice.congruences()
    print(f"Found {len(congruences)} congruences")
    
    print("Testing atoms() method...")
    atoms = lattice.atoms()
    print(f"Found {len(atoms)} atoms")
    
    print("Testing coatoms() method...")
    coatoms = lattice.coatoms()
    print(f"Found {len(coatoms)} coatoms")
    
    print("✅ Simple test completed successfully!")

if __name__ == "__main__":
    simple_test()
