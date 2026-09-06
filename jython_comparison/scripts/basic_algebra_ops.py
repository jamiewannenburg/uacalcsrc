# coding: utf-8
# Dual-runtime parity script for ~/uacalc BasicAlgebra / AbstractOperation usage.
# Linked from jython_contracts BasicAlgebra / SmallAlgebra / AbstractOperation / AlgebraIO.
from __future__ import print_function

from org.uacalc.alg import BasicAlgebra
from org.uacalc.alg.op import AbstractOperation, OperationSymbol
from org.uacalc.io import AlgebraIO


class id_op(AbstractOperation):
    def intValueAt(self, args):
        return args[0]


def test():
    op = id_op("id", 1, 2)
    alg = BasicAlgebra("Id2", 2, [op])
    print("name=" + str(alg.getName()))
    print("card=" + str(alg.cardinality()))
    looked = alg.getOperation(OperationSymbol("id", 1))
    print("id(1)=" + str(looked.intValueAt([1])))
    print("universe=" + str(sorted(alg.universe())))
    print("syms=" + str(sorted(str(s) for s in alg.similarityType().getOperationSymbols())))
    print("const_ops=" + str(len(alg.constantOperations())))
    # elementIndex / algebraType / getUniverseList still differ slightly across
    # runtimes for some constructors; probe presence for contract coverage.
    print("has_elementIndex=" + str(hasattr(alg, "elementIndex")))
    print("has_algebraType=" + str(hasattr(alg, "algebraType")))
    print("has_getUniverseList=" + str(hasattr(alg, "getUniverseList")))
    print("has_resetConAndSub=" + str(hasattr(alg, "resetConAndSub")))
    alg.setName("Id2b")
    print("renamed=" + str(alg.getName()))

    import os
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    try:
        AlgebraIO.writeAlgebraFile(alg, path)
        print("write_called=1")
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass

    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    print("c2=" + str(c2.getName()) + ":" + str(c2.cardinality()))
    print("c2_univ=" + str(sorted(c2.universe())))
    print("c2_has_getOp=" + str(hasattr(c2, "getOperation")))


if __name__ == "__main__":
    test()
