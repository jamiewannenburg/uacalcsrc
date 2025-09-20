#!/usr/bin/env python3
"""
Test script to investigate the build_universe process in detail
"""

import sys
import os
sys.path.append('python')

import uacalc

def test_detailed_build_universe():
    """Test the detailed build_universe process for sym3.ua"""
    print("Testing detailed build_universe process for sym3.ua...")
    
    # Load the algebra
    algebra_path = "resources/algebras/sym3.ua"
    try:
        algebra = uacalc.load_algebra(algebra_path)
        print(f"Loaded algebra: {algebra.name}")
        print(f"Cardinality: {algebra.cardinality}")
        print(f"Operations: {len(algebra.operations)}")
        
        # Print operation details
        for i, op in enumerate(algebra.operations):
            print(f"Operation {i}: {op.symbol}, arity: {op.arity}")
            
            # Print a few operation values to understand the structure
            if op.arity == 2:
                print("  Sample operation values:")
                for a in range(min(3, algebra.cardinality)):
                    for b in range(min(3, algebra.cardinality)):
                        try:
                            result = op.value([a, b])
                            print(f"    {op.symbol}({a}, {b}) = {result}")
                        except Exception as e:
                            print(f"    {op.symbol}({a}, {b}) = ERROR: {e}")
    except Exception as e:
        print(f"Failed to load algebra: {e}")
        return
    
    # Test individual principal congruences manually
    print("\nTesting individual principal congruences...")
    try:
        # Create a congruence lattice to test principal congruences
        con_lat = uacalc.create_congruence_lattice(algebra)
        
        # Test a few principal congruences
        for a in range(min(3, algebra.cardinality)):
            for b in range(a + 1, min(3, algebra.cardinality)):
                try:
                    principal = con_lat.principal_congruence(a, b)
                    print(f"Principal congruence θ({a},{b}): {principal.num_blocks()} blocks")
                    
                    # Print the blocks
                    blocks = principal.blocks()
                    print(f"  Blocks: {blocks}")
                except Exception as e:
                    print(f"Failed to compute principal congruence θ({a},{b}): {e}")
    except Exception as e:
        print(f"Failed to create congruence lattice: {e}")
    
    # Test the analyze_lattice_properties function with more debugging
    print("\nTesting analyze_lattice_properties with debugging...")
    try:
        props = uacalc.py_analyze_lattice_properties(algebra)
        print(f"Lattice properties: {props}")
        print(f"  Size: {props.congruence_lattice_size}")
        print(f"  Join irreducibles: {props.join_irreducibles_count}")
        print(f"  Atoms: {props.atoms_count}")
        print(f"  Height: {props.lattice_height}")
        print(f"  Width: {props.lattice_width}")
        print(f"  Is modular: {props.is_modular}")
        print(f"  Is distributive: {props.is_distributive}")
        print(f"  Is boolean: {props.is_boolean}")
        print(f"  Can construct basic lattice: {props.can_construct_basic_lattice}")
        if props.basic_lattice_error:
            print(f"  Basic lattice error: {props.basic_lattice_error}")
    except Exception as e:
        print(f"Failed to analyze lattice properties: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detailed_build_universe()
