import os
import sys
from dmm import check_type, add_arrow_and_meet, AlgebraIO

dir = 'input'
name = sys.argv[1]
alg_file_name = os.path.join(dir,"{}.ua".format(name))
if not os.path.isfile(alg_file_name):
    raise Exception("Could not find: {}".format(alg_file_name))

alg = AlgebraIO.readAlgebraFile(alg_file_name)

if check_type(alg):
    new_alg = add_arrow_and_meet(alg)
    print "Created meet and arrow for {}.".format(new_alg.getName())
    AlgebraIO.writeAlgebraFile(new_alg, alg_file_name)
else:
    print "Not a dmm type."