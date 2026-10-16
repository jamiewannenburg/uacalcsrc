"""CPython ports of ``org.uacalc.example`` demo classes.

Java remains the source of truth. Methods that are GUI-only, interactive,
or Malcev-only are stubs that raise with a reason so tests can skip/xfail.
"""

from __future__ import annotations

import math
import os
import struct
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional, Sequence

from org.uacalc.alg import (
    BasicAlgebra,
    BigProductAlgebra,
    Closer,
    ProductAlgebra,
    SubProductAlgebra,
)
from org.uacalc.alg.conlat import TypeFinder
from org.uacalc.alg.op import AbstractOperation, OperationSymbol, Operations
from org.uacalc.eq import Equation
from org.uacalc.io import AlgebraIO
from org.uacalc.terms import NonVariableTerm, Variable, VariableImp
from org.uacalc.util import IntArray, SequenceGenerator

DEMO_CLASS_NAMES = (
    "Average",
    "ConLyndonF3",
    "FilteringAlgebras",
    "FiniteField",
    "FinitelyPresentedAlg",
    "HasConstantTuple",
    "HasKaryNU",
    "Jipsen",
    "KKMVWExample",
    "Kearnes",
    "MembershipTester",
    "Michalewski",
    "NoSymGroup",
    "ParallelClose8",
    "TupleStream",
    "Type1",
)

GUI_OR_INTERACTIVE = {
    "ParallelClose": "ForkJoinPool timing demo; not a packaged org.uacalc.example class",
    "ParallelClose8": "Incomplete Java 8 stream closer; main() is an empty stub",
    "HasKaryNU.main": "CLI with optional filesystem args and ProgressReport",
    "TupleStream.main": "Timing benchmark (serial vs parallel stream counts)",
    "ConLyndonF3.main": "Computes Con(F(4)) of the Lyndon algebra; too heavy for parity",
    "FilteringAlgebras.main": "Uses Malcev.sdMeetIdempotent (Malcev is out of scope)",
    "Type1.main": "Prints subtraces of a size-5 matrix power; interactive/demo main",
    "Average.main": "Writes sample algebras to /tmp",
    "FiniteField.main": "Prints Conway polynomials and multiplication tables",
    "KKMVWExample.main": "Writes /tmp/A2.ua",
    "NoSymGroup.main": "Writes SymTestGroup.ua and runs a large HasConstantTuple search",
}


def _java_round_float(value: float) -> int:
    packed = struct.unpack("f", struct.pack("f", float(value)))[0]
    return int(math.floor(packed + 0.5))


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "resources" / "algebras").is_dir():
            return parent
    return Path.cwd()


class Average(object):
    @staticmethod
    def ave(n, r):
        class _AveOp(AbstractOperation):
            def intValueAt(self, args):
                total = 0
                for i in range(int(r)):
                    total += int(args[i])
                return _java_round_float(float(total) / float(r))

        return _AveOp("ave" + str(r), int(r), int(n))

    @staticmethod
    def averageAlg(n, r=None):
        if r is None:
            r = 2 * int(n) - 1
        return BasicAlgebra("AveAlgebra" + str(n) + "," + str(r), int(n), [Average.ave(n, r)])

    @staticmethod
    def main(args=None):
        raise NotImplementedError(GUI_OR_INTERACTIVE["Average.main"])


class Type1(object):
    @staticmethod
    def fullPermutationAlgebra(algSize):
        ops = []
        ops.append(Operations.makeFullCycle(int(algSize)))
        ops.append(Operations.makeTransposition(int(algSize), 0, 1))
        ops.extend(list(Operations.makeConstantIntOperations(int(algSize))))
        return BasicAlgebra("minType1-" + str(algSize), int(algSize), ops)

    @staticmethod
    def cyclicPermutationAlgebra(algSize):
        ops = []
        ops.append(Operations.makeFullCycle(int(algSize)))
        ops.extend(list(Operations.makeConstantIntOperations(int(algSize))))
        return BasicAlgebra("minType1-" + str(algSize), int(algSize), ops)

    @staticmethod
    def reductAlg(alg):
        from org.uacalc.alg import Algebras

        matpow = Algebras.matrixPower(alg, 3)
        big_prod = BigProductAlgebra(matpow, 4)
        gens = []
        term_map = {}
        var_list = []
        g0 = IntArray([0, 0, 1, 1])
        g1 = IntArray([0, 1, 0, 1])
        term_map[g0] = Variable.x
        term_map[g1] = Variable.y
        var_list.append(Variable.x)
        var_list.append(Variable.y)
        gens.append(g0)
        gens.append(g1)
        for i in range(int(matpow.cardinality())):
            c = IntArray([i, i, i, i])
            gens.append(c)
            var = VariableImp("c" + str(i))
            term_map[c] = var
            var_list.append(var)
        closer = Closer(big_prod, gens, term_map)
        closer.sgClose()
        ia0 = IntArray([0, 1, 2, 3])
        ia1 = IntArray([0, 4, 3, 7])
        t0 = term_map.get(ia0)
        t1 = term_map.get(ia1)
        h = t0.interpretation(matpow, var_list, False)
        k = t1.interpretation(matpow, var_list, False)
        return BasicAlgebra("reduct", int(matpow.cardinality()), [h, k])

    @staticmethod
    def subtraces(alg, beta):
        tfinder = TypeFinder(alg)
        subtr = tfinder.findSubtrace(beta)
        return subtr.getSubtraceUniverse()

    @staticmethod
    def main(args=None):
        raise NotImplementedError(GUI_OR_INTERACTIVE["Type1.main"])


class KKMVWExample(object):
    def __init__(self, n):
        self.n = int(n)

    def makeTin(self, i):
        n = self.n
        idx = int(i)

        class _Tin(AbstractOperation):
            def intValueAt(self, args):
                for j in range(2 * idx - 1):
                    if int(args[j]) == 0:
                        return 0
                if int(args[2 * idx - 1]) == 1 and int(args[2 * idx]) == 0:
                    return 0
                return 1

        return _Tin("t", 2 * n + 1, 2)

    def makeAin(self, i):
        return BasicAlgebra("A_" + str(i) + str(self.n), 2, [self.makeTin(i)])

    def makeAn(self):
        algs = [self.makeAin(i) for i in range(1, self.n + 1)]
        return ProductAlgebra("A_" + str(self.n), algs)

    @staticmethod
    def main(args=None):
        raise NotImplementedError(GUI_OR_INTERACTIVE["KKMVWExample.main"])


class HasConstantTuple(object):
    @staticmethod
    def hasConstantTuple(alg, arity, gens):
        if int(alg.cardinality()) < 2:
            return True
        gens = list(gens)
        big_prod = BigProductAlgebra(alg, int(arity))
        term_map = {}
        for i, gen in enumerate(gens):
            term_map[gen] = VariableImp("x" + str(i))
        closer = Closer(big_prod, gens, term_map)
        closer.setBlocks([[j for j in range(int(arity))]])
        lst = list(closer.sgClose())
        last = lst[len(lst) - 1]
        arr = last.toArray() if hasattr(last, "toArray") else last.getArray()
        arr = list(arr)
        c = int(arr[0])
        for i in range(1, int(arity)):
            if int(arr[i]) != c:
                return False
        return True


class NoSymGroup(object):
    @staticmethod
    def Addition(x, y):
        x = int(x)
        y = int(y)
        if x == y:
            return 0
        if x == 0:
            return y
        if y == 0:
            return x
        if x < 3 and y < 3:
            return 3
        if x == 1 or y == 1:
            return 2
        return 1

    @staticmethod
    def TernaryOp(x, y, z):
        x = int(x)
        y = int(y)
        z = int(z)
        if x == 4 or y == 4 or z == 4:
            return x
        return NoSymGroup.Addition(NoSymGroup.Addition(x, y), z)

    @staticmethod
    def MakeIdTernaryOp(i, Size):
        idx = int(i)
        size = int(Size)

        class _T(AbstractOperation):
            def intValueAt(self, args):
                return (
                    NoSymGroup.TernaryOp(
                        (int(args[0]) + size - 1 - idx) % size,
                        (int(args[1]) + size - 1 - idx) % size,
                        (int(args[2]) + size - 1 - idx) % size,
                    )
                    + 1
                    + idx
                ) % size

        return _T("t" + str(idx), 3, size)

    @staticmethod
    def main(args=None):
        raise NotImplementedError(GUI_OR_INTERACTIVE["NoSymGroup.main"])


class TupleStream(object):
    def __init__(self, lst):
        self.sourceList = list(lst)

    @staticmethod
    def pow(base, exponent):
        ans = 1
        exp = int(exponent)
        b = int(base)
        while exp > 0:
            ans = ans * b
            exp -= 1
        return ans

    @staticmethod
    def maxOfArray(arr):
        ans = int(arr[0])
        for i in range(1, len(arr)):
            if int(arr[i]) > ans:
                ans = int(arr[i])
        return ans

    @staticmethod
    def hornerInvLong(k, size, length, min=None):
        n = int(length)
        ans = [0] * n
        if n == 0:
            return ans
        remaining = int(k)
        size = int(size)
        for i in range(n - 1):
            ans[n - i - 1] = int(remaining % size)
            remaining = (remaining - ans[i]) // size
        ans[0] = int(remaining)
        return ans

    @staticmethod
    def intTupleStream(size, length, min=None):
        rng = TupleStream.pow(int(size), int(length))
        rows = [TupleStream.hornerInvLong(i, size, length) for i in range(rng)]
        if min is not None:
            rows = [row for row in rows if TupleStream.maxOfArray(row) >= int(min)]
        return rows

    def tupleStream(self, length, min=None):
        int_stream = TupleStream.intTupleStream(len(self.sourceList), int(length), min)
        return [[self.sourceList[i] for i in row] for row in int_stream]

    @staticmethod
    def main(args=None):
        raise NotImplementedError(GUI_OR_INTERACTIVE["TupleStream.main"])


def _conway_path() -> Optional[Path]:
    candidates = [
        _repo_root() / "resources" / "CPimport-3500.txt",
        Path.cwd() / "resources" / "CPimport-3500.txt",
        Path("CPimport-3500.txt"),
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


class FiniteField(object):
    def __init__(self, prime, power):
        self._prime = int(prime)
        self._power = int(power)
        self._polynomial = FiniteField.conwayPolynomial(self._prime, self._power)
        self._zero = IntArray([0] * self._power)
        one_vec = [0] * self._power
        one_vec[0] = 1
        self._one = IntArray(one_vec)
        card = 1
        for _ in range(self._power):
            card *= self._prime
        self._cardinality = card
        self._universe = []
        self._power_map = {}
        self._inv_power_map = {}
        self._set_univ_and_maps()
        plus = self._make_plus()
        neg = self._make_neg()
        times = self._make_times()
        inv = self._make_inv()
        # Java leaves these as AbstractOperations (inv(0) throws). Do not
        # coerce through BasicAlgebra, which eagerly tables every input.
        self._name = "Field" + str(self._prime) + "^" + str(self._power)
        self._ops = [plus, neg, times, inv]

    def _set_univ_and_maps(self):
        vec = [0] * self._power
        ia = IntArray(list(vec))
        self._universe.append(ia)
        vec = [0] * self._power
        vec[0] = 1
        ia = IntArray(list(vec))
        self._universe.append(ia)
        self._power_map[0] = ia
        for i in range(1, self._cardinality - 1):
            vec = self._next_vector(vec)
            ia = IntArray(list(vec))
            self._universe.append(ia)
            self._power_map[i] = ia
        for i in range(self._cardinality - 1):
            self._inv_power_map[self._ia_key(self._power_map[i])] = i

    def _next_vector(self, vec):
        last = int(vec[self._power - 1])
        poly = self._polynomial
        ans = [0] * self._power
        ans[0] = (last * int(poly[0])) % self._prime
        for i in range(1, self._power):
            ans[i] = (last * int(poly[i]) + int(vec[i - 1])) % self._prime
        return ans

    def _ia_key(self, ia):
        arr = ia.toArray() if hasattr(ia, "toArray") else ia.getArray()
        return tuple(int(x) for x in list(arr))

    def _make_plus(self):
        field = self

        class _Plus(AbstractOperation):
            def intValueAt(self, args):
                return field.plusInt(args[0], args[1])

        return _Plus("+", 2, self._cardinality)

    def _make_neg(self):
        field = self

        class _Neg(AbstractOperation):
            def intValueAt(self, args):
                return field.negationInt(args[0])

        return _Neg("-", 1, self._cardinality)

    def _make_times(self):
        field = self

        class _Times(AbstractOperation):
            def intValueAt(self, args):
                return field.timesInt(args[0], args[1])

        return _Times("*", 2, self._cardinality)

    def _make_inv(self):
        field = self

        class _Inv(AbstractOperation):
            def intValueAt(self, args):
                return field.inverseInt(args[0])

        return _Inv("inv", 1, self._cardinality)

    @staticmethod
    def conwayPolynomial(prime, power):
        prime = int(prime)
        power = int(power)
        ans = [0] * power
        path = _conway_path()
        if path is None:
            return None
        import re

        with open(str(path)) as handle:
            for line in handle:
                toks = re.split(r"[,\[\]]+", line.strip())
                while toks and toks[-1] == "":
                    toks.pop()
                if len(toks) > 3:
                    try:
                        if prime == int(toks[1]) and power == int(toks[2]):
                            for i in range(len(toks) - 4):
                                coeff = int(toks[i + 3])
                                if coeff != 0:
                                    coeff = prime - coeff
                                ans[i] = coeff
                            return ans
                    except (ValueError, IndexError):
                        continue
        return None

    def cardinality(self):
        return self._cardinality

    def getPrime(self):
        return self._prime

    def getPower(self):
        return self._power

    def getPolynomial(self):
        return list(self._polynomial) if self._polynomial is not None else None

    def zeroIndex(self):
        return 0

    def oneIndex(self):
        return 1

    def plusInt(self, index0, index1):
        a = self.getElement(int(index0))
        b = self.getElement(int(index1))
        return self.elementIndex(self.plus(a, b))

    def timesInt(self, a0, a1):
        a0 = int(a0)
        a1 = int(a1)
        if a0 == 0 or a1 == 0:
            return 0
        return (a0 + a1 - 2) % (self._cardinality - 1) + 1

    def inverseInt(self, index):
        index = int(index)
        if index == 0:
            raise ValueError("Division by zero")
        return self._cardinality - index + 1

    def negationInt(self, index):
        return self.elementIndex(self.negation(self.getElement(int(index))))

    def plus(self, arg0, arg1):
        a = list(arg0.toArray() if hasattr(arg0, "toArray") else arg0)
        b = list(arg1.toArray() if hasattr(arg1, "toArray") else arg1)
        return IntArray([(int(a[i]) + int(b[i])) % self._prime for i in range(self._power)])

    def negation(self, arg):
        a = list(arg.toArray() if hasattr(arg, "toArray") else arg)
        out = []
        for v in a:
            v = int(v)
            out.append(0 if v == 0 else self._prime - v)
        return IntArray(out)

    def getElement(self, k):
        k = int(k)
        if k == 0:
            return self._zero
        return self._power_map[k - 1]

    def elementIndex(self, elem):
        key = self._ia_key(elem)
        if key == self._ia_key(self._zero):
            return 0
        return int(self._inv_power_map[key]) + 1

    def operations(self):
        return self._ops

    def name(self):
        return self._name

    def getName(self):
        return self.name()

    def algebraType(self):
        return "FINITE_FIELD"

    @staticmethod
    def main(args=None):
        raise NotImplementedError(GUI_OR_INTERACTIVE["FiniteField.main"])


def _op_symbol_const(name):
    field = getattr(OperationSymbol, name.upper(), None)
    if field is not None and not callable(field):
        return field
    fn = getattr(OperationSymbol, name, None)
    if callable(fn):
        return fn()
    return field


class Kearnes(object):
    @staticmethod
    def makeJoinOp(n):
        n = int(n)

        class _Join(AbstractOperation):
            def intValueAt(self, args):
                return max(int(args[0]), int(args[1]))

        return _Join(_op_symbol_const("join"), n)

    @staticmethod
    def makeMeetOp(n):
        n = int(n)

        class _Meet(AbstractOperation):
            def intValueAt(self, args):
                return min(int(args[0]), int(args[1]))

        return _Meet(_op_symbol_const("meet"), n)

    @staticmethod
    def makeKearnesOps(n):
        n = int(n)
        ops = [Kearnes.makeJoinOp(n), Kearnes.makeMeetOp(n)]
        for i in range(1, n):
            k = i

            class _P(AbstractOperation):
                def intValueAt(self, args, _k=k):
                    if int(args[0]) < _k:
                        return _k
                    return _k - 1

            ops.append(_P("p_" + str(i), 1, n))
        return ops

    @staticmethod
    def makeKearnesAlg(n):
        n = int(n)
        return BasicAlgebra("Kearnes" + str(n), n, Kearnes.makeKearnesOps(n))

    @staticmethod
    def main(args=None):
        raise NotImplementedError("Kearnes.main is a Java demo driver")


class FilteringAlgebras(object):
    @staticmethod
    def filter(algebras, predicate):
        result = []
        for alg in list(algebras):
            if hasattr(predicate, "test"):
                ok = predicate.test(alg)
            else:
                ok = predicate(alg)
            if ok:
                result.append(alg)
        return result

    @staticmethod
    def main(args=None):
        raise NotImplementedError(GUI_OR_INTERACTIVE["FilteringAlgebras.main"])


class FinitelyPresentedAlg(object):
    @staticmethod
    def makeOrderRelation(u, v, vars):
        meet = _op_symbol_const("meet")
        uv = NonVariableTerm(meet, [u, v])
        names = []
        for var in list(vars):
            getter = getattr(var, "getName", None) or getattr(var, "get_name", None)
            names.append(str(getter()) if callable(getter) else str(var))
        return Equation(u, uv, names)

    @staticmethod
    def main(args=None):
        raise NotImplementedError("FinitelyPresentedAlg.main builds F(4) over M3")


class HasKaryNU(object):
    @staticmethod
    def hasNUHorowitz(testalg, arity):
        raise NotImplementedError(
            "HasKaryNU.hasNUHorowitz uses ProgressReport and a large BigProduct close"
        )

    @staticmethod
    def main(args=None):
        raise NotImplementedError(GUI_OR_INTERACTIVE["HasKaryNU.main"])


class Jipsen(object):
    @staticmethod
    def main(args=None):
        args = list(args or [])
        if not args:
            print("need a file name of an algebra")
            return
        try:
            alg = AlgebraIO.readAlgebraFile(str(args[0]))
        except Exception:
            return
        elts = alg.con().universe()
        k = 0
        for par in elts:
            print(str(k) + ": " + str(par))
            k += 1


class MembershipTester(object):
    alg0File = "resources/algebras/n5.ua"
    alg1File = "resources/algebras/m3.ua"
    alg1Generators = [1, 2, 3]

    @staticmethod
    def main(args=None):
        from org.uacalc.alg import FreeAlgebra

        alg0 = AlgebraIO.readAlgebraFile(MembershipTester.alg0File)
        alg1 = AlgebraIO.readAlgebraFile(MembershipTester.alg1File)
        return FreeAlgebra.findEquationOfAnotB(
            alg0, alg1, MembershipTester.alg1Generators
        )


class Michalewski(object):
    @staticmethod
    def testJoinMeetMatPower(a, b, alg, consts):
        k = len(a)
        big = BigProductAlgebra(alg, 4)
        gens = []
        elts_to_find = []
        for i in range(k):
            gens.append(IntArray([int(a[i]), int(a[i]), int(b[i]), int(b[i])]))
            gens.append(IntArray([int(a[i]), int(b[i]), int(a[i]), int(b[i])]))
            elts_to_find.append(IntArray([int(a[i]), int(b[i]), int(b[i]), int(b[i])]))
            elts_to_find.append(IntArray([int(a[i]), int(a[i]), int(a[i]), int(b[i])]))
        gens.extend(list(consts))
        closer = Closer(big, gens, True)
        closer.setElementsToFind(elts_to_find, gens)
        closer.sgClose()
        return bool(closer.allElementsFound())

    @staticmethod
    def findJoinMeetMatPower(alg, k):
        n = int(alg.cardinality())
        consts = [IntArray([i, i, i, i]) for i in range(n)]
        a = [0] * int(k)
        ainc = SequenceGenerator.sequenceIncrementor(a, n - 1)
        while True:
            b = [0] * int(k)
            binc = SequenceGenerator.sequenceIncrementor(b, n - 1)
            while True:
                if Michalewski._compare(a, b) < 0:
                    if Michalewski.testJoinMeetMatPower(a, b, alg, consts):
                        return [IntArray(list(a)), IntArray(list(b))]
                if not binc.increment():
                    break
            if not ainc.increment():
                break
        return None

    @staticmethod
    def _compare(a, b):
        if list(a) == list(b):
            return 0
        for i in range(len(a)):
            if int(a[i]) < int(b[i]):
                return -1
            if int(a[i]) > int(b[i]):
                return 1
        return 0

    @staticmethod
    def main(args=None):
        raise NotImplementedError("Michalewski.main is a Java demo driver")


class ConLyndonF3(object):
    @staticmethod
    def main(args=None):
        raise NotImplementedError(GUI_OR_INTERACTIVE["ConLyndonF3.main"])


class ParallelClose8(object):
    def __init__(self, *args):
        raise NotImplementedError(GUI_OR_INTERACTIVE["ParallelClose8"])

    @staticmethod
    def main(args=None):
        raise NotImplementedError(GUI_OR_INTERACTIVE["ParallelClose8"])
