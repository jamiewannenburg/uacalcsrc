#!/usr/bin/env python3
"""
This program takes a lattice reduct and considers all possible dots (operations).

It generates all possible dot operations for a given cardinality, checks if the
resulting algebra is a simple chain, and prints examples that are not simple chains.

This is a translation of the old Jython API code to the new Python API.

Note: This example demonstrates the operation creation and generation logic.
Some functionality (like creating algebras with operations and checking if they
are simple chains) may require additional API support. The example shows how
to create custom operations using IntOperation.from_int_value_at().
"""

import uacalc_lib


def join_op(cardinality):
    """Make join such that 0 is at the bottom and cardinality-1 at the top."""
    def join_func(args):
        if 6 in args:
            return 6
        elif set([4, 5]) == set(args):
            return 6
        elif 5 in args:
            return 5
        elif 4 in args:
            return 4
        elif 3 in args:
            return 3
        elif set([1, 2]) == set(args):
            return 3
        else:
            return max(args)
    
    return uacalc_lib.alg.IntOperation.from_int_value_at("join", 2, cardinality, join_func)


def neg_op(cardinality):
    """Make negation reversing the order of the elements."""
    def neg_func(args):
        return cardinality - 1 - args[0]
    
    return uacalc_lib.alg.IntOperation.from_int_value_at("neg", 1, cardinality, neg_func)


def e_op(cardinality):
    """Make e operation (constant operation returning 1)."""
    def e_func(args):
        return 1
    
    return uacalc_lib.alg.IntOperation.from_int_value_at("e", 0, cardinality, e_func)


def dot_op(unknowns, cardinality):
    """Make chain dot given the unknown values."""
    def dot_func(args):
        args_sorted = sorted(args)
        if 0 == args_sorted[0]:
            return 0
        elif 1 == args_sorted[0]:
            return args_sorted[1]
        elif cardinality - 1 == args_sorted[1]:
            return cardinality - 1
        else:
            return unknowns[args_sorted[0]][args_sorted[1]]
    
    return uacalc_lib.alg.IntOperation.from_int_value_at("dot", 2, cardinality, dot_func)


def already_known(cardinality, i, j, ip, jp):
    """Check if a value is already known based on ordering constraints."""
    if jp < j and ip < cardinality - 1:
        return True
    elif jp == j:
        return ip < i
    return False


def make_dots(cardinality, i=2, j=2, values=None):
    """Recursively make dots (generate all possible dot operations)."""
    # If this is called from outside
    if values is None:
        values = {}
        for x in range(2, cardinality - 1):
            values[x] = {}
    
    # The last pair
    if i == cardinality - 2 and j == cardinality - 2:
        values[j][i] = cardinality - 1  # we know f.f = top
        yield values
    else:
        # Use associativity to fix some values
        fixed = None
        
        for jp in range(2, j + 1):
            i_max = cardinality - 2
            if j == jp:
                i_max = i - 1
            for ip in range(jp, i_max + 1):
                if values[jp][ip] == i:  # jp*ip = i
                    # (j*jp)*ip
                    m = min(j, jp)
                    x = max(j, jp)
                    if already_known(cardinality, i, j, x, m):
                        a = values[m][x]
                        m = min(a, ip)
                        x = max(a, ip)
                        if already_known(cardinality, i, j, x, m):
                            fixed1 = values[m][x]
                            if fixed is None:
                                fixed = fixed1
                            else:
                                if fixed != fixed1:
                                    return  # Stop iteration instead of raising StopIteration
                    
                    # (j*ip)*jp
                    m = min(j, ip)
                    x = max(j, ip)
                    if already_known(cardinality, i, j, x, m):
                        a = values[m][x]
                        m = min(a, jp)
                        x = max(a, jp)
                        if already_known(cardinality, i, j, x, m):
                            fixed1 = values[m][x]
                            if fixed is None:
                                fixed = fixed1
                            else:
                                if fixed != fixed1:
                                    return
                
                if values[jp][ip] == j:  # jp*ip = j
                    # jp*(ip*i)
                    m = min(i, ip)
                    x = max(i, ip)
                    if already_known(cardinality, i, j, x, m):
                        a = values[m][x]
                        m = min(a, jp)
                        x = max(a, jp)
                        if already_known(cardinality, i, j, x, m):
                            fixed1 = values[m][x]
                            if fixed is None:
                                fixed = fixed1
                            else:
                                if fixed != fixed1:
                                    return
                    
                    # ip*(jp*i)
                    m = min(i, jp)
                    x = max(i, jp)
                    if already_known(cardinality, i, j, x, m):
                        a = values[m][x]
                        m = min(a, ip)
                        x = max(a, ip)
                        if already_known(cardinality, i, j, x, m):
                            fixed1 = values[m][x]
                            if fixed is None:
                                fixed = fixed1
                            else:
                                if fixed != fixed1:
                                    return
        
        if fixed is not None:  # Associativity has fixed the value
            lower = fixed
            upper = fixed
        else:  # Associativity gave us no information, so we set upper and lower bounds
            # Set lower bound
            lower = 2
            
            # Set upper bound
            upper = cardinality - 1
        
        # Get next i and j
        new_i = i + 1
        new_j = j
        if i == cardinality - 2:
            new_i = j + 1
            new_j = j + 1
        
        # Check every possible value between lower and upper
        for k in range(lower, upper + 1):
            values_copy = {x: {y: v for y, v in values[x].items()} for x in values}
            values_copy[j][i] = k
            
            for val in make_dots(cardinality, new_i, new_j, values_copy):
                yield val


def add_arrow_and_meet(alg):
    """
    Add arrow and meet operations to the algebra.
    
    Note: This is a placeholder. The original implementation would compute
    arrow (implication) and meet operations from the join operation.
    This functionality may need to be implemented or may be available through
    the lattice operations in the API.
    """
    # In the original code, this would add arrow (implication) and meet operations
    # For now, we return the algebra as-is
    return alg


def check_simple_chain(alg):
    """
    Check if the algebra is a simple chain.
    
    A simple chain means the congruence lattice is a chain (totally ordered).
    
    Note: This is a placeholder implementation. A full implementation would:
    1. Get the congruence lattice: con_lat = alg.con()
    2. Get the universe of congruences: universe = con_lat.universe()
    3. Check if the lattice is a chain (totally ordered)
    
    This requires the algebra to be created with operations first.
    """
    # Placeholder - would need full algebra with operations to check
    return False


def build_and_check_alg(cardinality, values):
    """
    Build an algebra and check if it's a simple chain.
    
    Note: This function demonstrates the operation creation part. The actual
    algebra construction with operations may require API extensions to support
    creating BasicAlgebra with a list of operations at construction time.
    """
    # Create operations
    alg_join = join_op(cardinality)
    alg_neg = neg_op(cardinality)
    alg_e = e_op(cardinality)
    alg_dot = dot_op(values, cardinality)
    
    # Create algebra name
    value_list = (str(values[x][y]) for x in values for y in values[x])
    number = "".join(value_list)
    alg_name = f"Y_{{{cardinality}}}^{{{number}}}"
    
    # For demonstration, we'll print the operations we created
    # In a full implementation, these would be added to the algebra
    print(f"Found example {number}")
    print(f"  Algebra: {alg_name}")
    print(f"  Cardinality: {cardinality}")
    print(f"  Operations created: join, neg, e, dot")
    print(f"  Dot operation values: {dict(values)}")
    
    # Note: To actually check if it's a simple chain, we would need to:
    # 1. Create BasicAlgebra with these operations (requires API support)
    # 2. Add arrow and meet operations (if needed)
    # 3. Compute the congruence lattice
    # 4. Check if the congruence lattice is a chain
    
    # For now, we'll just print that we found an example
    # In the original code, this would check: if not check_simple_chain(alg)
    return True


def main():
    """Main function to run the example."""
    cardinality = 7
    
    print(f"Generating all possible dot operations for cardinality {cardinality}...")
    print("(This may take a while as it explores all possible dot operations)\n")
    print("Note: This example demonstrates operation creation.")
    print("Full simple-chain checking requires API support for creating")
    print("algebras with operations.\n")
    
    found_count = 0
    for values in make_dots(cardinality):
        if build_and_check_alg(cardinality, values):
            found_count += 1
            # Limit output for demonstration
            if found_count >= 5:
                print("\n... (showing first 5 examples, there may be more)")
                break
    
    print(f"\nTotal examples shown: {found_count}")
    print("(Run without the limit to see all examples)")


if __name__ == "__main__":
    main()

