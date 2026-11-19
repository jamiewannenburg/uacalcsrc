import os
import sys
from dmm import leq, Variable, equation_to_term, check_crl, AlgebraIO, add_dual_residuation_operation, add_dual_lattice_operation, add_neg, make_readable

dir = 'input'
name = sys.argv[1]
alg_file_name = os.path.join(dir,"{}.ua".format(name))
if not os.path.isfile(alg_file_name):
    raise Exception("Could not find: {}".format(alg_file_name))

alg = AlgebraIO.readAlgebraFile(alg_file_name)

# check that algebra is a dmm
#alg = add_dual_lattice_operation(alg)
#alg = add_dual_residuation_operation(alg)
#alg = add_neg(alg)

complementation_axioms = [
    # commutative monoid operations
    leq(['meet(x,neg(x))','f()',[Variable.x]]),
    leq(['meet(x,neg(arrow(x,y)))','f()',[Variable.x,Variable.y]]),
]
complementation_axioms = map(equation_to_term,complementation_axioms)

def check_andrew(alg,example=True):
    for eq in complementation_axioms:
        result = eq.findFailureMap(alg)
        if result:
            l = eq.leftSide()
            r = eq.rightSide()
            if example:
                print "{} is not a crl as {}={} fails at {}.".format(alg.getName(),make_readable(l),make_readable(r),result)
            return False
    return True

check_andrew(alg)