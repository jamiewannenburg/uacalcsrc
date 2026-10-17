# coding: utf-8
# Dual-runtime parity script for Algebras static helpers (Java/Jython source of truth).
# Malcev helpers (findNUF, jonssonTerms, jonssonLevel) delegate to Malcev.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import Algebras
from org.uacalc.alg.op import OperationSymbol, Operations


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    id1 = Operations.makeIntOperation(OperationSymbol("id", 1), 2, [0, 1])
    swap1 = Operations.makeIntOperation(OperationSymbol("swap", 1), 2, [1, 0])
    zero_p = c2.con().zero()
    one_p = c2.con().one()
    _show("isEndo_id", lambda: Algebras.isEndomorphism(id1, c2))
    _show("isEndo_swap", lambda: Algebras.isEndomorphism(swap1, c2))
    _show("isHom_id", lambda: Algebras.isHomomorphism([0, 1], c2, c2))
    _show("isHom_const1", lambda: Algebras.isHomomorphism([1, 1], c2, c2))
    mp = Algebras.matrixPower(c2, 1)
    print("matrixPower=" + str(mp.cardinality()) + "," + str(mp.getName()))
    _show("matrixPower0", lambda: Algebras.matrixPower(c2, 0))
    trans = Algebras.fullTransformationSemigroup(2, True, True)
    print("trans=" + str(trans.cardinality()) + "," + str(trans.getName()))
    _show("trans10", lambda: Algebras.fullTransformationSemigroup(10, False, False))
    disc = Algebras.ternaryDiscriminatorAlgebra(2)
    print("disc=" + str(disc.cardinality()) + "," + str(disc.getName()))
    rnd = Algebras.makeRandomAlgebra(2, [1])
    print("random=" + str(rnd.cardinality()) + "," + str(rnd.getName()))
    _show("findInClone_empty", lambda: Algebras.findInClone([], c2))
    _show("unary2arg", lambda: Algebras.unaryCloneAlgFromPartitions([zero_p], [zero_p]))
    _show("memberQV_null", lambda: Algebras.memberOfQuasivariety(None, c2))
    _show("findNUF_c2", lambda: Algebras.findNUF(c2, 3))
    _show("jonssonLevel_c2", lambda: Algebras.jonssonLevel(c2))


if __name__ == "__main__":
    test()
