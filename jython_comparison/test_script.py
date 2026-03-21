# A script that should run in both Jython and Python (with compatibility layer)
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import *

import sys

def test():
    # Load cyclic2 algebra
    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    
    print("Algebra: " + str(alg.getName()))
    print("Cardinality: " + str(alg.cardinality()))
    
    # Get congruence lattice
    conlat = alg.con()
    print("Congruence Lattice size: " + str(conlat.cardinality()))
    
    # Check if elements are correctly loaded
    # Jython version usually prints something like [0, 1]
    # We'll use a standard print that should be similar
    univ = alg.getUniverseList()
    print("Universe: " + str(univ))

if __name__ == "__main__":
    test()
