# coding: utf-8
# Dual-runtime parity script for Algebra / SmallAlgebra / BasicAlgebra.
from __future__ import print_function

import sys

from org.uacalc.alg import Algebra, SmallAlgebra, BasicAlgebra
from org.uacalc.alg.op import Operations, OperationSymbol
from org.uacalc.io import AlgebraIO


def _op(name, arity, size, table):
    return Operations.makeIntOperation(OperationSymbol(name, arity), size, table)


def _map_keys(m):
    if m is None:
        return []
    if hasattr(m, "keySet"):
        return sorted(str(k) for k in m.keySet())
    return sorted(str(k) for k in m)


def test():
    xor2 = _op("xor", 2, 2, [0, 1, 1, 0])
    id1 = _op("id", 1, 2, [0, 1])
    c0 = Operations.makeConstantIntOperation(2, 0)
    alg = BasicAlgebra("Xor2", 2, [xor2])
    alg_id = BasicAlgebra("Id2", 2, [id1])
    alg_const = BasicAlgebra("C2", 2, [c0])
    alg_list = BasicAlgebra("Listed", ["a", "b"], [id1])

    print("card_unknown=" + str(Algebra.CARDINALITY_UNKNOWN))
    print("name=" + str(alg.getName()))
    alg.setName("Xor2b")
    print("renamed=" + str(alg.getName()))
    alg.setName("Xor2")
    print("card=" + str(alg.cardinality()))
    print("inputSize=" + str(alg.inputSize()))
    print("isUnary_xor=" + str(alg.isUnary()))
    print("isUnary_id=" + str(alg_id.isUnary()))
    print("univ=" + str(sorted(alg.universe())))
    print("iter=" + str(list(alg.iterator())))
    print("ops_n=" + str(len(alg.operations())))
    looked = alg.getOperation(OperationSymbol("xor", 2))
    print("xor(1,0)=" + str(looked.intValueAt([1, 0])))
    print("missing_op=" + str(alg.getOperation(OperationSymbol("nope", 1))))
    print("map_keys=" + str(_map_keys(alg.getOperationsMap())))
    print("desc=" + str(alg.getDescription()))
    alg.setDescription("xor on 2")
    print("desc2=" + str(alg.getDescription()))
    print("syms=" + str(sorted(str(s) for s in alg.similarityType().getOperationSymbols())))
    alg.updateSimilarityType()
    print("similar_self=" + str(alg.isSimilarTo(alg)))
    print("similar_id=" + str(alg.isSimilarTo(alg_id)))
    alg.makeOperationTables()
    print("const_n=" + str(len(alg.constantOperations())))
    print("const_c=" + str(len(alg_const.constantOperations())))
    print("idem_xor=" + str(alg.isIdempotent()))
    print("idem_id=" + str(alg_id.isIdempotent()))
    print("total=" + str(alg.isTotal()))
    print("monitor0=" + str(alg.getMonitor()))
    print("monitoring0=" + str(alg.monitoring()))
    alg.setMonitor(None)
    print("monitor_none=" + str(alg.getMonitor()))
    try:
        alg.setMonitor("report")
        print("setMonitor_bad=ok")
    except Exception:
        print("setMonitor_bad=" + str(sys.exc_info()[1].__class__.__name__))
    print("atype=" + str(alg.algebraType()))
    print("elem0=" + str(alg.getElement(0)))
    print("idx1=" + str(alg.elementIndex(1)))
    print("idx_bad=" + str(alg.elementIndex("x")))
    print("univ_list_int=" + str(alg.getUniverseList()))
    print("univ_order_int=" + str(alg.getUniverseOrder()))
    print("intUniv=" + str(alg.intUniverse()))
    print("parent=" + str(alg.parent()))
    print("parents=" + str(alg.parents()))
    print("con_card=" + str(alg.con().cardinality()))
    print("sub_card=" + str(alg.sub().cardinality()))
    alg.resetConAndSub()
    alg.convertToDefaultValueOps()
    print("after_convert_xor=" + str(alg.getOperation(OperationSymbol("xor", 2)).intValueAt([1, 0])))

    print("list_intUniv=" + str(alg_list.intUniverse()))
    print("list_univ=" + str(alg_list.getUniverseList()))
    print("list_elem1=" + str(alg_list.getElement(1)))
    alg_list.setUniverseList(["x", "y"])
    print("list_univ2=" + str(alg_list.getUniverseList()))
    alg_list.setUniverseOrder(None)
    print("list_order_set=" + str(alg_list.getUniverseOrder()))

    import os
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    try:
        AlgebraIO.writeAlgebraFile(alg_id, path)
        back = AlgebraIO.readAlgebraFile(path)
        print("round_name=" + str(back.getName()))
        print("round_card=" + str(back.cardinality()))
        print("round_type=" + str(back.algebraType()))
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass

    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    print("c2=" + str(c2.getName()) + ":" + str(c2.cardinality()))
    print("c2_small=" + str(isinstance(c2, SmallAlgebra)))
    print("c2_alg=" + str(isinstance(c2, Algebra)))


if __name__ == "__main__":
    test()
