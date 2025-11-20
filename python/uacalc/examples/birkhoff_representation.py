#!/usr/bin/env python3
"""
Example illustrating Birkhoff's representation for finite distributive lattices.

This example:
1. Creates a 6-element distributive lattice (as a BasicAlgebra)
2. Gets its join irreducible elements as a partial order
3. Creates a new general algebra with intersection and union on the downward closed sets
4. Converts it to a basic algebra
5. Checks that the original is isomorphic to the constructed algebra

Birkhoff's representation states that every finite distributive lattice is isomorphic
to the lattice of lower closed sets (ideals) of its join irreducibles,
ordered by inclusion.
"""

import uacalc_lib

BasicAlgebra = uacalc_lib.alg.BasicAlgebra
GeneralAlgebra = uacalc_lib.alg.GeneralAlgebra
IntOperation = uacalc_lib.alg.IntOperation
AbstractOperation = uacalc_lib.alg.AbstractOperation
OrderedSet = uacalc_lib.lat.OrderedSet

def create_6_element_distributive_lattice():
    """
    Create a 6-element distributive lattice.
    
    Structure:
    - 0 (bottom)
    - 1, 2 (atoms, incomparable)
    - 3 = 1 ∨ 2
    - 4 (above 3)
    - 5 (top)
    
    Order: 0 < 1, 2 < 3 < 4 < 5
    """
    universe = [0, 1, 2, 3, 4, 5]
    
    # Define join operation table
    # join[i][j] = join of elements i and j
    join_table = [
        [0, 1, 2, 3, 4, 5],  # 0 join anything = that element (0 is bottom)
        [1, 1, 3, 3, 4, 5],  # 1 join 2 = 3, etc.
        [2, 3, 2, 3, 4, 5],
        [3, 3, 3, 3, 4, 5],
        [4, 4, 4, 4, 4, 5],
        [5, 5, 5, 5, 5, 5],  # 5 join anything = 5 (5 is top)
    ]
    
    # Define meet operation table
    meet_table = [
        [0, 0, 0, 0, 0, 0],  # 0 meet anything = 0 (0 is bottom)
        [0, 1, 0, 1, 1, 1],  # 1 meet 2 = 0, etc.
        [0, 0, 2, 2, 2, 2],
        [0, 1, 2, 3, 3, 3],
        [0, 1, 2, 3, 4, 4],
        [0, 1, 2, 3, 4, 5],  # 5 meet anything = that element (5 is top)
    ]
    
    def join_func(args):
        i, j = args[0], args[1]
        return join_table[i][j]
    
    def meet_func(args):
        i, j = args[0], args[1]
        return meet_table[i][j]
    
    join_op = IntOperation.from_int_value_at("join", 2, 6, join_func)
    meet_op = IntOperation.from_int_value_at("meet", 2, 6, meet_func)
    
    alg = BasicAlgebra("DistributiveLattice6", universe, [join_op, meet_op])
    return alg


def get_downward_closed_sets(poset):
    """
    Get all downward closed sets (ideals) of a poset.
    
    A downward closed set U is a set such that if x in U and x >= y, then y in U.
    Uses the ideal() method to get principal ideals, then computes closure under union.
    """
    universe = poset.universe()
    
    # Start with principal ideals (ideals of each element)
    principal_ideals = []
    for elem in universe:
        ideal = poset.ideal(elem)
        principal_ideals.append(set(ideal))
    
    # Also include the empty set
    all_ideals = {frozenset()}
    
    # Add all principal ideals
    for ideal in principal_ideals:
        all_ideals.add(frozenset(ideal))
    
    # Compute closure under union: keep adding unions until no new ideals are found
    changed = True
    while changed:
        changed = False
        new_ideals = set(all_ideals)
        for ideal1 in all_ideals:
            for ideal2 in all_ideals:
                union_ideal = ideal1 | ideal2
                if frozenset(union_ideal) not in all_ideals:
                    new_ideals.add(frozenset(union_ideal))
                    changed = True
        all_ideals = new_ideals
    
    # Convert to sorted list of sorted tuples
    downward_closed_sets = sorted([tuple(sorted(list(ideal))) for ideal in all_ideals])
    return downward_closed_sets


def create_ideal_algebra(downward_closed_sets):
    """
    Create a GeneralAlgebra with intersection and union operations
    on the downward closed sets.
    """
    # Convert to list of lists for easier manipulation
    universe = [list(s) for s in downward_closed_sets]
    
    def intersection_func(args):
        # args[0] and args[1] are actual universe elements (lists)
        set1 = set(args[0])
        set2 = set(args[1])
        result_set = set1 & set2
        # Find the result in universe (as a sorted list)
        result_list = sorted(list(result_set))
        # Find matching element in universe
        for elem in universe:
            if sorted(elem) == result_list:
                return elem
        # Should not happen if universe is complete
        raise ValueError(f"Intersection result {result_list} not in universe")
    
    def union_func(args):
        # args[0] and args[1] are actual universe elements (lists)
        set1 = set(args[0])
        set2 = set(args[1])
        result_set = set1 | set2
        # Find the result in universe (as a sorted list)
        result_list = sorted(list(result_set))
        # Find matching element in universe
        for elem in universe:
            if sorted(elem) == result_list:
                return elem
        # Should not happen if universe is complete
        raise ValueError(f"Union result {result_list} not in universe")
    
    # Use from_value_at_function to work with actual universe elements
    intersection_op = AbstractOperation.from_value_at_function(
        "meet", 2, universe, intersection_func
    )
    union_op = AbstractOperation.from_value_at_function(
        "join", 2, universe, union_func
    )
    
    alg = GeneralAlgebra("IdealAlgebra", universe, [intersection_op, union_op])
    return alg


def check_isomorphism(alg1, alg2):
    """
    Check if two algebras are isomorphic by trying all permutations.
    
    Two algebras are isomorphic if there exists a bijective homomorphism
    (i.e., an isomorphism) between them.
    """
    import itertools
    
    if alg1.cardinality() != alg2.cardinality():
        return False, "Different cardinalities"
    
    n = alg1.cardinality()
    
    # Get operations - BasicAlgebra uses operations(), GeneralAlgebra uses get_operations()
    if hasattr(alg1, 'operations'):
        ops1 = alg1.operations()
    else:
        ops1 = alg1.get_operations()
    if hasattr(alg2, 'operations'):
        ops2 = alg2.operations()
    else:
        ops2 = alg2.get_operations()
    
    if len(ops1) != len(ops2):
        return False, "Different number of operations"
    
    # Check that operations have matching names
    op_names1 = {op.symbol().name() for op in ops1}
    op_names2 = {op.symbol().name() for op in ops2}
    if op_names1 != op_names2:
        return False, f"Operation names don't match: {op_names1} vs {op_names2}"
    
    is_homomorphism = uacalc_lib.alg.is_homomorphism
    
    # For small algebras, try all permutations
    # For larger algebras (n > 8), this becomes expensive, but we'll try anyway
    # In practice, for lattices from Birkhoff representation, n is usually small
    for perm in itertools.permutations(range(n)):
        # Check if this permutation is a homomorphism
        try:
            if is_homomorphism(list(perm), alg1, alg2):
                # Found an isomorphism!
                return True, f"Algebras are isomorphic (found isomorphism)"
        except Exception as e:
            # Skip this permutation if there's an error (e.g., missing operation)
            continue
    
    return False, "No isomorphism found (tried all permutations)"


def main():
    """Main function demonstrating Birkhoff's representation."""
    print("=" * 70)
    print("Birkhoff's representation Example for Finite Distributive Lattices")
    print("=" * 70)
    print()
    
    # Step 1: Create a 6-element distributive lattice
    print("Step 1: Creating a 6-element distributive lattice...")
    original_lattice = create_6_element_distributive_lattice()
    print(f"  Created lattice: {original_lattice.name()}")
    print(f"  Cardinality: {original_lattice.cardinality()}")
    ops = original_lattice.operations()
    print(f"  Operations: {[op.symbol().name() for op in ops]}")
    print()
    
    # Extract the join operation from the algebra (needed for both diagram and Step 2)
    join_op = None
    for op in original_lattice.operations():
        if op.symbol().name() == "join":
            join_op = op
            break
    
    if join_op is None:
        raise ValueError("Join operation not found")
    
    # Create a BasicLattice for visualization and further processing
    join_lattice = uacalc_lib.lat.lattice_from_join("BasicLattice", join_op)

    # Print lattice diagram
    print("  Lattice diagram (DOT format):")
    # Convert BasicLattice to OrderedSet using the from_lattice method
    lattice_poset = OrderedSet.from_lattice(join_lattice, name="LatticePoset")
    lattice_graph = lattice_poset.to_graph_data()
    lattice_dot = lattice_graph.to_dot()
    print(lattice_dot)
    print()
    
    # Step 2: Get join irreducibles as a partial order
    print("Step 2: Getting join irreducibles as a partial order...")
    print(f"  Created BasicLattice from join operation using lattice_from_join()")
    
    # Get join irreducibles from the lattice
    join_irreducibles = join_lattice.join_irreducibles()
    join_irreducibles_set = set(join_irreducibles)
    print(f"  Join irreducibles: {join_irreducibles}")
    upper_covers_list = []
    for ji in join_irreducibles:
        filter = list(join_irreducibles_set.intersection(join_lattice.filter(ji)))
        upper_covers_list.append(filter)
    
    # Create OrderedSet from join irreducibles
    jis_po = OrderedSet(join_irreducibles, upper_covers_list, name="JoinIrreducibles")
    print(f"  Join irreducibles poset: {jis_po.name()}")
    print(f"  Join irreducibles cardinality: {jis_po.cardinality()}")
    jis_universe = jis_po.universe()
    print(f"  Join irreducibles (from poset): {jis_universe}")
    print()
    
    # Print poset diagram
    print("  Join irreducibles poset diagram (DOT format):")
    poset_graph = jis_po.to_graph_data()
    poset_dot = poset_graph.to_dot()
    print(poset_dot)
    print()
    
    # Step 3: Create downward closed sets (ideals) of the partial order
    print("Step 3: Creating downward closed sets (ideals) of the partial order...")
    downward_closed_sets = get_downward_closed_sets(jis_po)
    print(f"  Number of downward closed sets: {len(downward_closed_sets)}")
    print(f"  Downward closed sets:")
    for i, dcs in enumerate(downward_closed_sets):
        print(f"    {i}: {list(dcs)}")
    print()
    
    # Step 4: Create a general algebra with intersection and union
    print("Step 4: Creating general algebra with intersection and union...")
    ideal_alg = create_ideal_algebra(downward_closed_sets)
    print(f"  Created algebra: {ideal_alg.name()}")
    print(f"  Cardinality: {ideal_alg.cardinality()}")
    ideal_ops = ideal_alg.get_operations()
    print(f"  Operations: {[op.symbol().name() for op in ideal_ops]}")
    print()
    
    # Step 5: Convert to basic algebra
    print("Step 5: Converting general algebra to basic algebra...")
    ideal_basic_alg = ideal_alg.to_basic_algebra()
    print(f"  Converted to BasicAlgebra")
    print(f"  Cardinality: {ideal_basic_alg.cardinality()}")
    ideal_basic_ops = ideal_basic_alg.operations()
    print(f"  Operations: {[op.symbol().name() for op in ideal_basic_ops]}")
    print()
    
    # Step 6: Check isomorphism
    print("Step 6: Checking if original lattice is isomorphic to constructed algebra...")
    is_iso, message = check_isomorphism(original_lattice, ideal_basic_alg)
    print(f"  Result: {message}")
    
    if is_iso:
        print()
        print("SUCCESS: The original lattice is isomorphic to the lattice of")
        print("  downward closed sets of its join irreducibles!")
        print()
        print("This demonstrates Birkhoff representation: every finite distributive")
        print("lattice is isomorphic to the lattice of downward closed sets")
        print("(ideals) of its join irreducibles, ordered by inclusion.")
    else:
        print()
        print("NOTE: The algebras are not isomorphic (or isomorphism check failed).")
        print(f"  Reason: {message}")
        print()
        print("This might be due to:")
        print("  - The lattice structure or join irreducibles computation")
        print("  - The way downward closed sets are computed")
        print("  - The isomorphism check being too simplistic")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()

