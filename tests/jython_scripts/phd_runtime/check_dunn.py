import os
import sys
from dmm import check_type, check_dunn, AlgebraIO, check_full

dir = 'input'
name = sys.argv[1]
alg_file_name = os.path.join(dir,"{}.ua".format(name))
if not os.path.isfile(alg_file_name):
    raise Exception("Could not find: {}".format(alg_file_name))

alg = AlgebraIO.readAlgebraFile(alg_file_name)

# check that algebra is a dmm
if check_dunn(alg):
    print "{} is a Dunn monoid".format(alg.getName())