# coding: utf-8
# Dual-runtime parity script for org.uacalc.example demo constructors.
from __future__ import print_function

import sys

from org.uacalc.example import (
    Average,
    ConLyndonF3,
    FilteringAlgebras,
    FiniteField,
    FinitelyPresentedAlg,
    HasConstantTuple,
    HasKaryNU,
    Jipsen,
    KKMVWExample,
    Kearnes,
    MembershipTester,
    Michalewski,
    NoSymGroup,
    ParallelClose8,
    TupleStream,
    Type1,
)
from org.uacalc.io import AlgebraIO
from org.uacalc.terms import Variable, VariableImp
from org.uacalc.util import IntArray


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except:  # noqa: E722 — Jython 2: Java UOE is not always a Python Exception
        e = sys.exc_info()[1]
        name = type(e).__name__
        if "." in name:
            name = name.rsplit(".", 1)[-1]
        print(label + "=EXC:" + name)


def _collect(stream):
    if stream is None:
        return None
    if isinstance(stream, (list, tuple)):
        rows = list(stream)
    else:
        try:
            from java.util.stream import Collectors

            rows = list(stream.collect(Collectors.toList()))
        except Exception:
            rows = list(stream)
    out = []
    for row in rows:
        if row is None:
            out.append(None)
            continue
        try:
            out.append([int(x) for x in list(row)])
        except TypeError:
            out.append([int(row[i]) for i in range(len(row))])
    return out


def _alg_info(alg):
    name = alg.getName() if hasattr(alg, "getName") else alg.name()
    ops = alg.operations()
    nops = 0 if ops is None else len(list(ops))
    return [str(name), int(alg.cardinality()), nops]


class _Card2(object):
    def test(self, alg):
        return int(alg.cardinality()) == 2

    def __call__(self, alg):
        return self.test(alg)


def main():
    _show("ave_3_3", lambda: Average.ave(3, 3).intValueAt([0, 1, 2]))
    _show("averageAlg_3", lambda: _alg_info(Average.averageAlg(3)))
    _show("averageAlg_3_3", lambda: _alg_info(Average.averageAlg(3, 3)))
    _show("type1_full_3", lambda: _alg_info(Type1.fullPermutationAlgebra(3)))
    _show("type1_cyc_3", lambda: _alg_info(Type1.cyclicPermutationAlgebra(3)))
    kkm = KKMVWExample(2)
    _show("kkm_a12", lambda: _alg_info(kkm.makeAin(1)))
    _show("kkm_an", lambda: _alg_info(kkm.makeAn()))
    _show("kkm_tin", lambda: kkm.makeTin(1).intValueAt([1, 1, 1, 1, 1]))
    _show("nosym_add_01", lambda: NoSymGroup.Addition(0, 1))
    _show("nosym_add_12", lambda: NoSymGroup.Addition(1, 2))
    _show("nosym_tern", lambda: NoSymGroup.TernaryOp(1, 2, 0))
    _show("nosym_idtern", lambda: NoSymGroup.MakeIdTernaryOp(0, 4).intValueAt([1, 2, 3]))
    _show("tuple_pow", lambda: TupleStream.pow(2, 3))
    _show("tuple_max", lambda: TupleStream.maxOfArray([1, 4, 2]))
    _show("tuple_horner", lambda: list(TupleStream.hornerInvLong(5, 3, 3)))
    ts = TupleStream([10, 20, 30])
    _show("tuple_ints", lambda: _collect(TupleStream.intTupleStream(2, 2)))
    _show("tuple_stream", lambda: _collect(ts.tupleStream(2)))
    _show("ff_poly_2_1", lambda: list(FiniteField.conwayPolynomial(2, 1)))
    ff = FiniteField(2, 1)
    _show("ff_card", lambda: ff.cardinality())
    _show("ff_prime", lambda: ff.getPrime())
    _show("ff_power", lambda: ff.getPower())
    _show("ff_plus", lambda: ff.plusInt(0, 1))
    _show("ff_times", lambda: ff.timesInt(1, 1))
    _show("ff_zero", lambda: ff.zeroIndex())
    _show("ff_one", lambda: ff.oneIndex())
    _show("kearnes_3", lambda: _alg_info(Kearnes.makeKearnesAlg(3)))
    _show("kearnes_ops", lambda: len(list(Kearnes.makeKearnesOps(3))))
    _show("kearnes_join", lambda: Kearnes.makeJoinOp(3).intValueAt([1, 2]))
    _show("kearnes_meet", lambda: Kearnes.makeMeetOp(3).intValueAt([1, 2]))
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
    filtered = FilteringAlgebras.filter([c2, c3], _Card2())
    _show("filter_card2", lambda: [int(a.cardinality()) for a in filtered])
    eq = FinitelyPresentedAlg.makeOrderRelation(
        Variable.x, Variable.y, [Variable.x, Variable.y, Variable.z, VariableImp("u")]
    )
    _show("fp_eq", lambda: str(eq))
    _show("jipsen_noarg", lambda: Jipsen.main([]))
    gens = [IntArray([0, 0]), IntArray([1, 1])]
    _show("hct_c2", lambda: HasConstantTuple.hasConstantTuple(c2, 2, gens))
    lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
    consts = [IntArray([i, i, i, i]) for i in range(int(lat2.cardinality()))]
    _show(
        "mich_test",
        lambda: Michalewski.testJoinMeetMatPower([0], [1], lat2, consts),
    )
    _show("parallel8_main", lambda: ParallelClose8.main([]))
    _show("mt_main", lambda: MembershipTester.main([]))


if __name__ == "__main__":
    main()
