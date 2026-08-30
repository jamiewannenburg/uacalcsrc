# Dual-runtime parity script: must produce identical stdout under
#   jython  (CLASSPATH=jars/uacalc.jar)
#   python3 (PYTHONPATH=python:python/uacalc_lib, org.uacalc shim)
#
# Linked from jython_contracts for AlgebraIO / SmallAlgebra / BasicAlgebra.
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import *

import sys


def test():
    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")

    print("Algebra: " + str(alg.getName()))
    print("Cardinality: " + str(alg.cardinality()))

    conlat = alg.con()
    print("Congruence Lattice size: " + str(conlat.cardinality()))

    # Universe formatting still differs between Jython and CPython; runner may
    # ignore lines starting with "Universe:" until str_parity is done.
    univ = alg.getUniverseList()
    print("Universe: " + str(univ))


if __name__ == "__main__":
    test()
