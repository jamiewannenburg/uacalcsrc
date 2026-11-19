import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
dir = os.path.join(dir_path,'input')
os.chdir(dir_path)
sys.path.append("uacalc.jar")
sys.path.append("LatDraw.jar")

from org.uacalc.alg import Subalgebra, ReductAlgebra
from org.uacalc.alg.sublat import SubalgebraLattice
from org.uacalc.terms import Terms, Variable, NonVariableTerm, VariableImp
from org.uacalc.io import AlgebraIO
from isomorphism import is_isomorphic

from mace4 import to_alg, to_alg_stream
import itertools

def subreducts(alg, signature):
    reduct_algebra = ReductAlgebra(alg, signature)
    SL = SubalgebraLattice(reduct_algebra)
    for gens in SL.iterator():
        subalg = Subalgebra(reduct_algebra,gens)
        yield subalg

def subreducts_stream(handle,signature):
    for alg in to_alg_stream(handle):
        for subalg in subreducts(alg, signature):
            yield subalg

if __name__=='__main__':
    signature = sys.argv[1].split(' ')
    signature = [Terms.stringToTerm(i) for i in signature]

    # get models file name from -f flag if present
    # otherwise assume it is read from stdin
    # get models file name from -f flag if present
    # otherwise assume it is read from stdin
    models_file_name = None
    for i,arg in enumerate(sys.argv):
        if arg.startswith('-f='):
            models_file_name = arg.split('=')[1]
            break
        elif arg.startswith('-f'):
            models_file_name = sys.argv[i+1]
            break
    if models_file_name is None:
        models_handle = sys.stdin
    else:
        models_handle = open(models_file_name)
    
    found = 0
    for i,alg in enumerate(to_alg_stream(models_handle)):
        for subalg in subreducts(alg, signature):
            found += 1
            print(found,i,subalg.cardinality())
