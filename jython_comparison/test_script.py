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
    
    #TODO: universe in jython vs getUniverseList in python, python should mirror jython

if __name__ == "__main__":
    test()
