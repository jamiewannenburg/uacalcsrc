# coding: utf-8
# Dual-runtime parity script for Lattices facade (~/uacalc dmm.py).
from __future__ import print_function

from org.uacalc.alg import BasicAlgebra
from org.uacalc.alg.op import AbstractOperation
from org.uacalc.lat import Lattices


class join_op(AbstractOperation):
    def intValueAt(self, args):
        return max(args[0], args[1])


class meet_op(AbstractOperation):
    def intValueAt(self, args):
        return min(args[0], args[1])


def test():
    j = join_op("join", 2, 2)
    m = meet_op("meet", 2, 2)
    # Materialize as table-backed ops for lattice helpers
    alg = BasicAlgebra("Chain2", 2, [j, m])
    join = alg.getOperation(j.symbol())
    meet = alg.getOperation(m.symbol())
    lj = Lattices.latticeFromJoin("J", join)
    lm = Lattices.latticeFromMeet("M", meet)
    print("join_lat=" + str(lj.cardinality() if hasattr(lj, "cardinality") else lj))
    print("meet_lat=" + str(lm.cardinality() if hasattr(lm, "cardinality") else lm))


if __name__ == "__main__":
    test()
