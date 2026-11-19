import os
import sys
from dmm import check_type, check_m, AlgebraIO, check_full

dir = 'input'
name = sys.argv[1]
alg_file_name = os.path.join(dir,"{}.ua".format(name))
if not os.path.isfile(alg_file_name):
    raise Exception("Could not find: {}".format(alg_file_name))

alg = AlgebraIO.readAlgebraFile(alg_file_name)

# Add arrow and meet if not already there
if check_type(alg):
    if not check_full(alg):
        raise Exception("Meet or arrow not defined, run add_arrow_and_meet first.")
else:
    raise Exception("Not a dmm type.")
    
# check that algebra is a dmm
if check_m(alg):
    print "{} is in M".format(alg.getName())