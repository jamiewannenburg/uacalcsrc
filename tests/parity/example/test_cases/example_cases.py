"""Test case specifications for org.uacalc.example behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_PKG_PRIVATE = (
    "Java method is package-private, so Jython scripts cannot call it. "
    "The CPython port exposes it as a public class method."
)
_CONWAY_XFAIL = (
    "Java FiniteField.conwayPolynomial loads CPimport-3500.txt from the "
    "classpath; the UACalc jar does not ship that resource, so Java returns null."
)

_SETUP = r"""
import sys
from org.uacalc.example import (
    Average, ConLyndonF3, FilteringAlgebras, FiniteField, FinitelyPresentedAlg,
    HasConstantTuple, HasKaryNU, Jipsen, KKMVWExample, Kearnes,
    MembershipTester, Michalewski, NoSymGroup, ParallelClose8, TupleStream, Type1,
)
from org.uacalc.io import AlgebraIO
from org.uacalc.terms import Variable, VariableImp
from org.uacalc.util import IntArray

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
    name = alg.getName() if hasattr(alg, 'getName') else alg.name()
    ops = alg.operations()
    nops = 0 if ops is None else len(list(ops))
    return [str(name), int(alg.cardinality()), nops]

def _card2_pred():
    if sys.platform.startswith('java'):
        class P(FilteringAlgebras.AlgebraPredicate):
            def test(self, alg):
                return int(alg.cardinality()) == 2
        return P()
    class P(object):
        def test(self, alg):
            return int(alg.cardinality()) == 2
        def __call__(self, alg):
            return self.test(alg)
    return P()

c2 = AlgebraIO.readAlgebraFile('resources/algebras/cyclic2.ua')
c3 = AlgebraIO.readAlgebraFile('resources/algebras/cyclic3.ua')
lat2 = AlgebraIO.readAlgebraFile('resources/algebras/lat2.ua')
kkm = KKMVWExample(2)
ts = TupleStream([10, 20, 30])
ff21 = FiniteField(2, 1)
"""

_SKIP = dict(skip_string_check=True)

_GUI_XFAIL = "GUI/interactive/demo main; not part of the constructable parity surface"
_MALCEV_XFAIL = "FilteringAlgebras.main uses Malcev.sdMeetIdempotent (Malcev is out of scope)"
_PARALLEL8_XFAIL = "Incomplete Java 8 stream closer; constructor is not a portable API"
_HASKARY_XFAIL = "HasKaryNU.hasNUHorowitz uses ProgressReport and a large BigProduct close"
_CONLYNDON_XFAIL = "Computes Con(F(4)) of the Lyndon algebra; too heavy for parity"
_REDUCT_XFAIL = "Type1.reductAlg builds a size-8 matrix-power reduct and looks up terms by IntArray identity"
_HCT_XFAIL = "HasConstantTuple prints to stdout and uses Closer.setBlocks on a BigProduct"
_MICH_XFAIL = "Michalewski.findJoinMeetMatPower enumerates A^k pairs (too heavy for goldens)"
_MT_XFAIL = "Known Java bug: FreeAlgebra.findEquationOfAnotB 3-arg overload NPEs on a null ProgressReport"


def _c(cid, method, call, description, **kw):
    return TestCaseSpec(
        id=cid,
        method=method,
        setup=_SETUP,
        call=call,
        description=description,
        **kw
    )


TEST_CASES = [
    _c("ave_3_3", "Average.ave", "Average.ave(3, 3).intValueAt([0, 1, 2])",
       "Average.ave(3,3) at (0,1,2)", **_SKIP),
    _c("ave_3_3_000", "Average.ave", "Average.ave(3, 3).intValueAt([0, 0, 0])",
       "Average.ave(3,3) at (0,0,0)", **_SKIP),
    _c("ave_3_3_222", "Average.ave", "Average.ave(3, 3).intValueAt([2, 2, 2])",
       "Average.ave(3,3) at (2,2,2)", **_SKIP),
    _c("average_alg_3", "Average.averageAlg", "_alg_info(Average.averageAlg(3))",
       "Average.averageAlg(3) default r=5", **_SKIP),
    _c("average_alg_3_3", "Average.averageAlg", "_alg_info(Average.averageAlg(3, 3))",
       "Average.averageAlg(3, 3)", **_SKIP),
    _c("average_main", "Average.main", "Average.main([])",
       "Average.main writes /tmp sample algebras", xfail_reason=_GUI_XFAIL, **_SKIP),
    _c("type1_full_3", "Type1.fullPermutationAlgebra",
       "_alg_info(Type1.fullPermutationAlgebra(3))",
       "Type1.fullPermutationAlgebra(3)", **_SKIP),
    _c("type1_cyc_3", "Type1.cyclicPermutationAlgebra",
       "_alg_info(Type1.cyclicPermutationAlgebra(3))",
       "Type1.cyclicPermutationAlgebra(3)", **_SKIP),
    _c("type1_full_2", "Type1.fullPermutationAlgebra",
       "_alg_info(Type1.fullPermutationAlgebra(2))",
       "Type1.fullPermutationAlgebra(2)", **_SKIP),
    _c("kkm_a12", "KKMVWExample.makeAin", "_alg_info(kkm.makeAin(1))",
       "KKMVWExample(2).makeAin(1)", xfail_reason=_PKG_PRIVATE, **_SKIP),
    _c("kkm_an", "KKMVWExample.makeAn", "_alg_info(kkm.makeAn())",
       "KKMVWExample(2).makeAn product", xfail_reason=_PKG_PRIVATE, **_SKIP),
    _c("kkm_tin", "KKMVWExample.makeTin",
       "kkm.makeTin(1).intValueAt([1, 1, 1, 1, 1])",
       "KKMVWExample(2).makeTin(1) at all-1s", xfail_reason=_PKG_PRIVATE, **_SKIP),
    _c("kkm_tin_zero", "KKMVWExample.makeTin",
       "kkm.makeTin(1).intValueAt([0, 1, 1, 1, 1])",
       "KKMVWExample(2).makeTin(1) hits a leading 0", xfail_reason=_PKG_PRIVATE, **_SKIP),
    _c("kkm_main", "KKMVWExample.main", "KKMVWExample.main([])",
       "KKMVWExample.main writes /tmp/A2.ua", xfail_reason=_GUI_XFAIL, **_SKIP),
    _c("nosym_add_01", "NoSymGroup.Addition", "NoSymGroup.Addition(0, 1)",
       "NoSymGroup.Addition(0,1)", **_SKIP),
    _c("nosym_add_12", "NoSymGroup.Addition", "NoSymGroup.Addition(1, 2)",
       "NoSymGroup.Addition(1,2)", **_SKIP),
    _c("nosym_add_eq", "NoSymGroup.Addition", "NoSymGroup.Addition(2, 2)",
       "NoSymGroup.Addition equal args", **_SKIP),
    _c("nosym_tern", "NoSymGroup.TernaryOp", "NoSymGroup.TernaryOp(1, 2, 0)",
       "NoSymGroup.TernaryOp(1,2,0)", **_SKIP),
    _c("nosym_idtern", "NoSymGroup.MakeIdTernaryOp",
       "NoSymGroup.MakeIdTernaryOp(0, 4).intValueAt([1, 2, 3])",
       "NoSymGroup.MakeIdTernaryOp(0,4) at (1,2,3)", **_SKIP),
    _c("tuple_pow", "TupleStream.pow", "TupleStream.pow(2, 3)",
       "TupleStream.pow(2,3)", **_SKIP),
    _c("tuple_max", "TupleStream.maxOfArray", "TupleStream.maxOfArray([1, 4, 2])",
       "TupleStream.maxOfArray", **_SKIP),
    _c("tuple_horner_5", "TupleStream.hornerInvLong",
       "list(TupleStream.hornerInvLong(5, 3, 3))",
       "TupleStream.hornerInvLong(5,3,3) including Java index bug", **_SKIP),
    _c("tuple_horner_0", "TupleStream.hornerInvLong",
       "list(TupleStream.hornerInvLong(0, 2, 3))",
       "TupleStream.hornerInvLong zero encoding", **_SKIP),
    _c("tuple_ints", "TupleStream.intTupleStream",
       "_collect(TupleStream.intTupleStream(2, 2))",
       "TupleStream.intTupleStream(2,2)", **_SKIP),
    _c("tuple_ints_min", "TupleStream.intTupleStream",
       "_collect(TupleStream.intTupleStream(2, 2, 1))",
       "TupleStream.intTupleStream(2,2,min=1)", **_SKIP),
    _c("tuple_stream", "TupleStream.tupleStream",
       "_collect(ts.tupleStream(2))",
       "TupleStream([10,20,30]).tupleStream(2)", **_SKIP),
    _c("ff_poly_2_1", "FiniteField.conwayPolynomial",
       "list(FiniteField.conwayPolynomial(2, 1) or [])",
       "Conway polynomial for GF(2)", xfail_reason=_CONWAY_XFAIL, **_SKIP),
    _c("ff_poly_2_2", "FiniteField.conwayPolynomial",
       "list(FiniteField.conwayPolynomial(2, 2) or [])",
       "Conway polynomial for GF(4)", xfail_reason=_CONWAY_XFAIL, **_SKIP),
    _c("ff_card", "FiniteField.cardinality", "ff21.cardinality()",
       "FiniteField(2,1) cardinality", **_SKIP),
    _c("ff_prime", "FiniteField.getPrime", "ff21.getPrime()",
       "FiniteField(2,1) prime", **_SKIP),
    _c("ff_power", "FiniteField.getPower", "ff21.getPower()",
       "FiniteField(2,1) power", **_SKIP),
    _c("ff_plus", "FiniteField.plusInt", "ff21.plusInt(0, 1)",
       "FiniteField(2,1) plusInt", **_SKIP),
    _c("ff_times", "FiniteField.timesInt", "ff21.timesInt(1, 1)",
       "FiniteField(2,1) timesInt", **_SKIP),
    _c("ff_inv", "FiniteField.inverseInt", "ff21.inverseInt(1)",
       "FiniteField(2,1) inverseInt(1)", **_SKIP),
    _c("ff_zero", "FiniteField.zeroIndex", "ff21.zeroIndex()",
       "FiniteField(2,1) zeroIndex", **_SKIP),
    _c("ff_one", "FiniteField.oneIndex", "ff21.oneIndex()",
       "FiniteField(2,1) oneIndex", **_SKIP),
    _c("ff_main", "FiniteField.main", "FiniteField.main([])",
       "FiniteField.main prints Conway tables", xfail_reason=_GUI_XFAIL, **_SKIP),
    _c("kearnes_3", "Kearnes.makeKearnesAlg", "_alg_info(Kearnes.makeKearnesAlg(3))",
       "Kearnes.makeKearnesAlg(3)", **_SKIP),
    _c("kearnes_join", "Kearnes.makeJoinOp", "Kearnes.makeJoinOp(3).intValueAt([1, 2])",
       "Kearnes.makeJoinOp(3) at (1,2)", **_SKIP),
    _c("kearnes_meet", "Kearnes.makeMeetOp", "Kearnes.makeMeetOp(3).intValueAt([1, 2])",
       "Kearnes.makeMeetOp(3) at (1,2)", **_SKIP),
    _c("kearnes_main", "Kearnes.main", "Kearnes.main([])",
       "Kearnes.main is a Java demo driver", xfail_reason=_GUI_XFAIL, **_SKIP),
    _c("filter_card2", "FilteringAlgebras.filter",
       "[int(a.cardinality()) for a in FilteringAlgebras.filter([c2, c3], _card2_pred())]",
       "FilteringAlgebras.filter keeps cardinality-2 algebras",
       xfail_reason=(
           "Java AlgebraPredicate is a package-private nested interface; "
           "Jython cannot subclass it from a script. CPython accepts a callable."
       ), **_SKIP),
    _c("fp_eq", "FinitelyPresentedAlg.makeOrderRelation",
       "str(FinitelyPresentedAlg.makeOrderRelation(Variable.x, Variable.y, [Variable.x, Variable.y]))",
       "FinitelyPresentedAlg.makeOrderRelation x <= y", xfail_reason=_PKG_PRIVATE, **_SKIP),
    _c("jipsen_noarg", "Jipsen.main", "Jipsen.main([])",
       "Jipsen.main with no args prints usage", **_SKIP),
    _c("hct_c2", "HasConstantTuple.hasConstantTuple",
       "HasConstantTuple.hasConstantTuple(c2, 2, [IntArray([0, 0]), IntArray([1, 1])])",
       "HasConstantTuple on C2 arity 2 diagonal gens", **_SKIP),
    _c("mich_test", "Michalewski.testJoinMeetMatPower",
       "Michalewski.testJoinMeetMatPower([0], [1], lat2, [IntArray([i, i, i, i]) for i in range(int(lat2.cardinality()))])",
       "Michalewski.testJoinMeetMatPower on lat2 k=1", **_SKIP),
    _c("mich_find", "Michalewski.findJoinMeetMatPower",
       "[list(a.toArray() if hasattr(a, 'toArray') else a.getArray()) for a in Michalewski.findJoinMeetMatPower(lat2, 1)]",
       "Michalewski.findJoinMeetMatPower enumerates pairs", **_SKIP),
    _c("parallel8_ctor", "ParallelClose8", "ParallelClose8(None, [], None)",
       "ParallelClose8 constructor",
       xfail_reason=_PARALLEL8_XFAIL, **_SKIP),
    _c("parallel8_main", "ParallelClose8.main", "ParallelClose8.main([])",
       "ParallelClose8.main is an empty/incomplete stub",
       xfail_reason=_PARALLEL8_XFAIL, **_SKIP),
    _c("mt_main", "MembershipTester.main", "MembershipTester.main([])",
       "MembershipTester.main hits the Java findEquationOfAnotB NPE", **_SKIP),
]
