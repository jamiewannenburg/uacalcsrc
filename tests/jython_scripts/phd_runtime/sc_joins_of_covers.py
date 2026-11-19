import os
import sys
sys.path.append("uacalc.jar")
import itertools
import re

from org.uacalc.alg import ProductAlgebra
from dmm import BasicAlgebra, AlgebraIO, AbstractOperation, OperationSymbol, add_arrow_and_meet
from isomorphism import is_isomorphic
from skew_reflection import slaney, dunn_reduct

covers_names = ['b2_reflection','s3_reflection','s3_weaved','c4_weaved','t5_skew','t6_skew']

# load algebras and get their dunn reducts
dir = 'input'
covers = []
for name in covers_names:
    alg_file_name = os.path.join(dir,"{}.ua".format(name))
    alg = AlgebraIO.readAlgebraFile(alg_file_name)
    covers.append({'algebra':alg,'dunn_reduct':dunn_reduct(alg)})

# get distinct pairs of covers
for cover1,cover2 in itertools.combinations(covers,2):
    alg1 = cover1['algebra']
    dunn1 = cover1['dunn_reduct']
    alg2 = cover2['algebra']
    dunn2 = cover2['dunn_reduct']
    # get skew reflection of their product
    #product = add_arrow_and_meet(slaney(ProductAlgebra("%s \times %s"%(alg1.getName(),alg2.getName()),[dunn1,dunn2])))
    product = slaney(ProductAlgebra("%s \\times %s"%(dunn1.getName(),dunn2.getName()),[dunn1,dunn2]))
    product.setName("S(%s)"%(product.getName()))
    
    # get subalgebras of the product and check if they are isomorphic to alg1 and alg2
    subalgebra_lattice = product.sub()
    print "%s has size %d and %d subalgebras"%(product.getName(),product.cardinality(),subalgebra_lattice.cardinality())
    
    first_iso = False
    second_iso = False
    for gens in subalgebra_lattice.iterator():
        sub_alg = subalgebra_lattice.Sg(gens)
        if is_isomorphic(sub_alg,alg1):
            first_iso = True
        elif is_isomorphic(sub_alg,alg2):
            second_iso = True
    
    if first_iso and second_iso:
        print "%s and %s embedds into %s"%(alg1.getName(),alg2.getName(),product.getName())


