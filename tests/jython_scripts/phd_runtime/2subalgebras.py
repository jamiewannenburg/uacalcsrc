import sys
import os
import re

dir_path = os.path.dirname(os.path.realpath(__file__))
dir = os.path.join(dir_path,'input')

os.chdir(dir_path)

sys.path.append("uacalc.jar")
sys.path.append("LatDraw.jar")

from org.uacalc.alg.sublat import SubalgebraLattice
import glob

from dmm import AlgebraIO, OperationSymbol,check_dmm
from latex import get_operation_table

# get patern
patern = sys.argv[1]
print(patern)
base = re.search(r'(.*)\*',patern).group(1)
out_file_name = os.path.join(dir_path,'output/'+base+'covers.tex')
paths = sorted(glob.glob(dir+r'/'+patern),  key=os.path.getmtime)

algebras = []
for path in paths:
    alg = AlgebraIO.readAlgebraFile(path)
    # # sanity check
    # if not check_dmm(alg):
        # raise Exception(alg.getName()+" is not a De Morgan Monoid!!!\n")
    
    subalg = SubalgebraLattice(alg)
    if subalg.cardinality() <= 2:
        print(path)
    algebras.append(alg)
algebras = sorted(algebras, key=lambda alg: alg.cardinality())

