#!/usr/bin/env python3
"""
This program takes a lattice reduct and considers all possible dots (operations).

It generates all possible dot operations for a given cardinality, checks if the
resulting algebra is simple, and prints examples that are not simple.

This is a translation of the old Jython API code to the new Python API.

The program creates BasicAlgebra instances with operations and checks if they
are simple by computing the congruence lattice. An algebra is simple if it has
exactly 2 congruences (the zero and one congruences).
"""

import uacalc_lib


def join_op(cardinality):
    """Make join such that 0 is at the bottom and cardinality-1 at the top."""
    def join_func(args):
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
    """Add arrow and meet operations to the algebra using terms."""
    Variable = uacalc_lib.terms.VariableImp
    TermOperationImp = uacalc_lib.terms.TermOperationImp
    
    # Create meet operation: neg(join(neg(x),neg(y)))
    meet_term = uacalc_lib.terms.string_to_term('neg(join(neg(x),neg(y)))')
    x = Variable('x')
    y = Variable('y')
    meet_op = TermOperationImp(meet_term, [x, y], alg, name="meet")
    
    # Create arrow operation: neg(dot(x,neg(y)))
    arrow_term = uacalc_lib.terms.string_to_term('neg(dot(x,neg(y)))')
    arrow_op = TermOperationImp(arrow_term, [x, y], alg, name="arrow")
    
    # Get existing operations and add new ones
    existing_ops = alg.operations()
    all_ops = existing_ops + [meet_op, arrow_op]
    
    # Create new algebra with all operations
    BasicAlgebra = uacalc_lib.alg.BasicAlgebra
    universe = alg.get_universe()
    return BasicAlgebra(alg.name(), universe, all_ops)

Equation = uacalc_lib.eq.Equation
string_to_term = uacalc_lib.terms.string_to_term
Variable = uacalc_lib.terms.VariableImp

crl_axioms = [
    # commutative monoid operations
    Equation(string_to_term('dot(x,y)'), string_to_term('dot(y,x)'), ['x','y']),
    Equation(string_to_term('dot(x,e())'), string_to_term('x'), ['x']),
    Equation(string_to_term('dot(x,dot(y,z))'), string_to_term('dot(dot(x,y),z)'), ['x','y','z']),
    # crl axioms
    Equation(string_to_term('join(x,arrow(y,dot(y,x)))'), string_to_term('arrow(y,dot(y,x))'), ['x','y']),
    Equation(string_to_term('join(dot(x,arrow(x,y)),y)'), string_to_term('y'), ['x','y']),
    Equation(string_to_term('join(dot(x,meet(y,z)),meet(dot(x,y),dot(x,z)))'), string_to_term('meet(dot(x,y),dot(x,z))'), ['x','y','z']),
    Equation(string_to_term('meet(arrow(x,y),arrow(x,z))'), string_to_term('arrow(x,meet(y,z))'), ['x','y','z']),
]
icrl_axioms = crl_axioms + [
    # involution
    Equation(string_to_term('x'), string_to_term('neg(neg(x))'), ['x']),
    Equation(string_to_term('neg(x)'), string_to_term('arrow(x,neg(e()))'), ['x']),
]

def build_and_check_alg(cardinality, values):
    """
    Build an algebra and check if it's simple.
    
    Creates a BasicAlgebra with the join, neg, e, and dot operations,
    then checks if it's simple by computing the congruence lattice.
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
    
    # Create universe as list of integers from 0 to cardinality-1
    universe = list(range(cardinality))
    
    # Create BasicAlgebra with operations
    BasicAlgebra = uacalc_lib.alg.BasicAlgebra
    alg = BasicAlgebra(alg_name, universe, [alg_join, alg_neg, alg_e, alg_dot])

    # Add arrow and meet operations
    alg = add_arrow_and_meet(alg)
    
    # Check if the algebra satisfies the ICRLAxioms
    for axiom in icrl_axioms:
        result = axiom.find_failure_map(alg)
        if result:
            return False

    # Get the congruence lattice and check if the algebra is simple
    con_lat = alg.con()
    con_cardinality = con_lat.cardinality()
    is_simple = con_cardinality == 2
    
    # If algebra is not simple return False
    if not is_simple:
        return False

    # Check if the subalgebra lattice has only 2 elements
    sub_lat = alg.sub()
    sub_cardinality = sub_lat.cardinality()
    print(f"Subalgebra lattice cardinality: {sub_cardinality}")
    if sub_cardinality != 2:
        return False

    print(f"Found simple crl with one proper subalgebra: {number}")
    print(f"  Algebra: {alg_name}")
    print(f"  Cardinality: {cardinality}")
    print(f"  Dot operation values: {dict(values)}")
    return True


def main():
    """Main function to run the example."""
    cardinality = 6
    
    print(f"Generating all possible dot operations for cardinality {cardinality}...")
    print("(This may take a while as it explores all possible dot operations)\n")
    print("Checking if algebras are simple crls with one proper subalgebra.\n")
    
    found_count = 0
    for values in make_dots(cardinality):
        if build_and_check_alg(cardinality, values):
            found_count += 1
            # Limit output for demonstration
            if found_count >= 3:
                print("\n... (showing first 3 simple crls with one proper subalgebra, there may be more)")
                break
    
    print(f"\nTotal examples shown: {found_count}")
    print("(Run without the limit to see all simple crls with one proper subalgebra)")


if __name__ == "__main__":
    main()

