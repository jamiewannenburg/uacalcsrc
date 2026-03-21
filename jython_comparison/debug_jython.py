from org.uacalc.io import AlgebraIO
from org.uacalc.alg import *

def test():
    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    print("Algebra type: " + str(type(alg)))
    print("Universe list: " + str(alg.getUniverseList()))
    
    conlat = alg.con()
    print("ConLat type: " + str(type(conlat)))
    print("ConLat cardinality: " + str(conlat.cardinality()))

if __name__ == "__main__":
    test()
