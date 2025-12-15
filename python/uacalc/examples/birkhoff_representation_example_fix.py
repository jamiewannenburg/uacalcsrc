#!/usr/bin/env python3
"""
Example showing how to use PowerAlgebra operations with coordinate tuples.

This demonstrates:
1. How to encode coordinate tuples to Horner integers
2. How to use int_value_at with encoded integers
3. How to decode results back to coordinates
"""

import uacalc_lib
import itertools

BasicAlgebra = uacalc_lib.alg.BasicAlgebra
PowerAlgebra = uacalc_lib.alg.PowerAlgebra
IntOperation = uacalc_lib.alg.IntOperation
OperationSymbol = uacalc_lib.alg.OperationSymbol
Horner = uacalc_lib.Horner

def example_power_algebra_operations():
    """Example of using PowerAlgebra operations with coordinates."""
    
    # Create a basic 2-element algebra with join operation
    universe = [0, 1]
    join_table = [
        [0, 1],
        [1, 1],
    ]
    
    def join_func(args):
        i, j = args[0], args[1]
        return join_table[i][j]
    
    join_op = IntOperation.from_int_value_at("join", 2, 2, join_func)
    ba2 = BasicAlgebra("DistributiveLattice2", universe, [join_op])
    
    # Create power algebra with power 2
    n = 2
    power_alg = PowerAlgebra(ba2, n)
    
    # Get the join operation from the power algebra
    for op in power_alg.operations():
        if op.symbol().name() == "join":
            join_op = op
            break
    
    # Root size is 2, power is 2
    root_size = 2
    power = 2
    
    # Generate all coordinate tuples
    pa_universe_iter = itertools.product([0, 1], repeat=power)
    pa_universe = list(pa_universe_iter)
    
    print("Method 1: Using int_value_at with Horner-encoded integers")
    print("=" * 60)
    for i_tuple in pa_universe:
        # Encode tuple to Horner integer
        i_encoded = Horner.horner_same_size(list(i_tuple), root_size)
        
        print(f"{i_tuple}: ", end="")
        for j_tuple in pa_universe:
            # Encode tuple to Horner integer
            j_encoded = Horner.horner_same_size(list(j_tuple), root_size)
            
            # Call int_value_at with encoded integers
            result_encoded = join_op.int_value_at([i_encoded, j_encoded])
            
            # Decode result back to coordinates
            result_tuple = Horner.horner_inv_same_size(result_encoded, root_size, power)
            
            print(f"{result_tuple} ", end="")
        print()
    
    print("\nMethod 2: Using value_at_arrays for batch evaluation")
    print("=" * 60)
    
    # Encode all tuples once
    encoded_universe = [Horner.horner_same_size(list(t), root_size) for t in pa_universe]
    
    for i, i_tuple in enumerate(pa_universe):
        print(f"{i_tuple}: ", end="")
        
        # Create arrays: first argument is i_encoded repeated, second is all encoded values
        i_encoded = encoded_universe[i]
        args_arrays = [
            [i_encoded] * len(encoded_universe),  # First argument: i repeated
            encoded_universe  # Second argument: all j values
        ]
        
        # Evaluate all at once
        results_encoded = join_op.value_at_arrays(args_arrays)
        
        # Decode all results
        for result_encoded in results_encoded:
            result_tuple = Horner.horner_inv_same_size(result_encoded, root_size, power)
            print(f"{result_tuple} ", end="")
        print()
    
    print("\nMethod 3: Direct table access (if available)")
    print("=" * 60)
    
    # Try to get the table directly
    table = join_op.get_table()
    if table is not None:
        print(f"Table size: {len(table)}")
        print("Table (as Horner-encoded indices -> results):")
        for idx in range(min(16, len(table))):  # Show first 16 entries
            args_tuple = Horner.horner_inv_same_size(idx, root_size, power)
            result_encoded = table[idx]
            result_tuple = Horner.horner_inv_same_size(result_encoded, root_size, power)
            print(f"  {args_tuple} -> {result_tuple} (encoded: {idx} -> {result_encoded})")
    else:
        print("Table not available (operation may be function-based)")
        print("You can create a table with: join_op.make_table()")
    
    print("\nMethod 4: Using BasicAlgebra conversion (simpler interface)")
    print("=" * 60)
    
    # Convert to BasicAlgebra - this uses integer indices 0, 1, 2, 3
    power_basic_alg = power_alg.to_basic_algebra()
    
    # Get operations from BasicAlgebra
    basic_ops = power_basic_alg.operations()
    for op in basic_ops:
        if op.symbol().name() == "join":
            basic_join_op = op
            break
    
    # Now we can use simple integer indices
    cardinality = power_basic_alg.cardinality()
    print(f"Cardinality: {cardinality}")
    print("Operation table using integer indices:")
    for i in range(cardinality):
        print(f"{i}: ", end="")
        for j in range(cardinality):
            result = basic_join_op.int_value_at([i, j])
            print(f"{result} ", end="")
        print()
    
    # Map integer indices back to coordinate tuples
    print("\nMapping integer indices to coordinate tuples:")
    for i in range(cardinality):
        coords = Horner.horner_inv_same_size(i, root_size, power)
        print(f"  {i} -> {coords}")


if __name__ == "__main__":
    example_power_algebra_operations()

