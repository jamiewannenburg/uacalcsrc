import sys
import os

base_letter = 'E'
dir_path = os.path.dirname(os.path.realpath(__file__))
dir = os.path.join(dir_path,'input')
os.chdir(dir_path)
sys.path.append("uacalc.jar")
sys.path.append("LatDraw.jar")

from org.uacalc.alg import ProductAlgebra, Subalgebra
from org.uacalc.alg.sublat import SubalgebraLattice
from dmm import AlgebraIO
from isomorphism import is_isomorphic

import itertools
#from dmm import BasicAlgebra, AlgebraIO, AbstractOperation, add_arrow_and_meet, check_simple_chain, OperationSymbol


c4_covers_names = [
    'C-5-1',
    'C-5-2',
    'C-6-1',
    'C-6-2',
    'C-6-3',
    'C-8-6',
    'C-8-9',
    'C-10-27',
    'C-10-29',
    'C-12-16',
    'C-12-37',
    'C-12-39',
    'C-14-103',
    'C-14-121',
    'C-14-122',
    'C-14-202',
    'C-14-204',
    'C-14-239',
    'C-14-240',# ^ chains
    'x2',
    'x3',
    'x4',
    'x5'
]

d4_covers_names = [
    'd6',
    'd6p',
    'd8',
    'd8p',
    'd-8-3'
]

c4_covers = [AlgebraIO.readAlgebraFile( os.path.join(dir,"{}.ua".format(name)) ) for name in c4_covers_names]
d4_covers = [AlgebraIO.readAlgebraFile( os.path.join(dir,"{}.ua".format(name)) ) for name in d4_covers_names]

def all_true(a_list):
    for i in a_list:
        if not i:
            return 0
    return 1

import glob
paths = sorted(glob.glob(dir+r'/C-*-*.ua'),  key=os.path.getmtime)
simple_chains = []
for path in paths:
    alg = AlgebraIO.readAlgebraFile(path)
    if alg.cardinality() < 12:
        simple_chains.append(alg)
simple_chains = sorted(simple_chains, key=lambda alg: alg.cardinality())

import math
f = math.factorial

for algebras in [d4_covers,c4_covers]: #d4_covers,c4_covers,simple_chains # class of algebras to combine
    n = len(algebras)
    r = 3
    # combinations = f(n) / f(r) / f(n-r)
    combinations = f(n+r-1) / f(r) / f((n+r-1)-r) # with replacement
    print ''
    print "checking", combinations, 'combinations'
    prev = None
    for j,algs in enumerate(itertools.combinations_with_replacement(algebras,r)):
        names = [a.getName() for a in algs]
        print '{}%\r'.format(j*100/combinations),
        
        product = ProductAlgebra(algs)
        sa_lattice = SubalgebraLattice(product)
        
        # if prev == None:
            # prev = sa_lattice.getBasicLattice()
            # prev.setName('S('+' x '.join(names)+')')
        # else:
            # salgebra = sa_lattice.getBasicLattice()
            # salgebra.setName('S('+' x '.join(names)+')')
            # if not is_isomorphic(prev,salgebra):
                # print ''
                # print prev.getName(), 'is not isomorphic to', salgebra.getName()
                # break
            # prev = salgebra
        
        check = [0]*len(algs)
        for sa_universe in sa_lattice.universe():
            sa = Subalgebra(product,sa_universe)
            for i,alg in enumerate(algs):
                if is_isomorphic(alg,sa):
                    # print ''
                    # print alg.getName(),'is isomorphic to subalgebra', sa_universe, 'of', ' x '.join(names)
                    check[i] = 1
                    # break #assumes algs are non-isomorphic, so I can stop if I find one isomorphism
            
            if all_true(check):
                print ''
                print ', '.join(names),'are subalgebras of',' x '.join(names)
                break
    print ''