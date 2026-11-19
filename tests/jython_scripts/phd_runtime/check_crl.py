import os
import sys
from dmm import check_type, check_crl, AlgebraIO, add_dual_residuation_operation, add_dual_lattice_operation, add_neg

dir = 'input'
name = sys.argv[1]
alg_file_name = os.path.join(dir,"{}.ua".format(name))
if not os.path.isfile(alg_file_name):
    raise Exception("Could not find: {}".format(alg_file_name))

alg = AlgebraIO.readAlgebraFile(alg_file_name)

# check that algebra is a dmm
#alg = add_dual_lattice_operation(alg)
alg = add_dual_residuation_operation(alg)
alg = add_neg(alg)

if check_crl(alg):
    print "{} is a crl".format(alg.getName())
    AlgebraIO.writeAlgebraFile(alg, alg_file_name)