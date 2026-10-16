"""Jython-facing helpers for ``org.uacalc.util.virtuallist`` (CPython only)."""

from __future__ import annotations

from typing import Any

from org.uacalc._exceptions import IllegalArgumentException


def _bind(cls: Any, name: str, impl: Any) -> None:
    if cls is None:
        return
    try:
        setattr(cls, name, impl)
    except (TypeError, AttributeError):
        pass


def _tolist(arr: Any):
    if arr is None:
        return None
    return [int(x) for x in arr]


def _install(g: dict) -> None:
    IntTuples = g.get("IntTuples")
    IntTuplesWithMin = g.get("IntTuplesWithMin")
    FixedSizedSubsets = g.get("FixedSizedSubsets")
    Subsets = g.get("Subsets")
    Permutations = g.get("Permutations")
    TupleWithMin = g.get("TupleWithMin")
    VirtualLists = g.get("VirtualLists")
    Utils = g.get("LongListUtils")

    def _iae(exc: BaseException) -> None:
        if isinstance(exc, IllegalArgumentException):
            raise exc
        raise IllegalArgumentException(str(exc)) from exc

    def intTuples(tupleLength, base):
        try:
            return IntTuples(int(tupleLength), int(base))
        except Exception as exc:
            _iae(exc)

    def intTuplesWithMin(tupleLength, base, min):
        try:
            return IntTuplesWithMin(int(tupleLength), int(base), int(min))
        except Exception as exc:
            _iae(exc)

    def fixedSizedSubsets(subsetSize, setSize):
        try:
            return FixedSizedSubsets(int(subsetSize), int(setSize))
        except Exception as exc:
            _iae(exc)

    def subsets(setSize):
        try:
            return Subsets(int(setSize))
        except Exception as exc:
            _iae(exc)

    def permutations(n):
        try:
            return Permutations(int(n))
        except Exception as exc:
            _iae(exc)

    def factorial(n):
        if Utils is not None:
            return Utils.factorial(int(n))
        ans = 1
        for i in range(int(n), 1, -1):
            ans *= i
        return ans

    def binomial(n, r):
        if Utils is not None:
            return Utils.binomial(int(n), int(r))
        n, r = int(n), int(r)
        if r > n:
            return 0
        if n - r < r:
            r = n - r
        top = 1
        bot = 1
        for i in range(r):
            top *= n - i
            bot *= i + 1
        return top // bot

    def log2(k):
        k = int(k)
        if k <= 0:
            raise IllegalArgumentException("k must be positive.")
        if Utils is not None:
            try:
                return Utils.log2(k)
            except Exception as exc:
                _iae(exc)
        return k.bit_length() - 1

    def pow2(r):
        if Utils is not None:
            return Utils.pow2(int(r))
        return 1 << int(r)

    class LongList(object):
        def stream(self):
            raise NotImplementedError("Java 8 Stream is not bound")

        def parallelStream(self):
            raise NotImplementedError("Java 8 Stream is not bound")

    LongList.intTuples = staticmethod(intTuples)
    LongList.intTuplesWithMin = staticmethod(intTuplesWithMin)
    LongList.fixedSizedSubsets = staticmethod(fixedSizedSubsets)
    LongList.subsets = staticmethod(subsets)
    LongList.permutations = staticmethod(permutations)
    LongList.factorial = staticmethod(factorial)
    LongList.binomial = staticmethod(binomial)
    LongList.log2 = staticmethod(log2)
    LongList.pow2 = staticmethod(pow2)

    if VirtualLists is not None:
        _bind(VirtualLists, "intTuples", staticmethod(intTuples))
        _bind(VirtualLists, "intTuplesWithMin", staticmethod(intTuplesWithMin))

        def arrayIndexerWithMin(k, arity, base, min):
            fn = getattr(VirtualLists, "array_indexer_with_min", None)
            if callable(fn):
                try:
                    return fn(int(k), int(arity), int(base), int(min))
                except Exception as exc:
                    _iae(exc)
            raise IllegalArgumentException("arrayIndexerWithMin unavailable")

        _bind(VirtualLists, "arrayIndexerWithMin", staticmethod(arrayIndexerWithMin))

        _vl_foo = getattr(VirtualLists, "foo", None)
        _vl_bar = getattr(VirtualLists, "bar", None)
        _vl_baz = getattr(VirtualLists, "baz", None)
        _vl_test_pow = getattr(VirtualLists, "test_pow", None)

        def foo(k, r):
            if callable(_vl_foo):
                return _vl_foo(int(k), int(r))
            raise IllegalArgumentException("foo unavailable")

        def bar(k, r):
            if callable(_vl_bar):
                return _vl_bar(int(k), int(r))
            raise IllegalArgumentException("bar unavailable")

        def baz(k, r):
            if callable(_vl_baz):
                return _vl_baz(int(k), int(r))
            raise IllegalArgumentException("baz unavailable")

        def testPow(k):
            if callable(_vl_test_pow):
                _vl_test_pow(int(k))
            return None

        _bind(VirtualLists, "foo", staticmethod(foo))
        _bind(VirtualLists, "bar", staticmethod(bar))
        _bind(VirtualLists, "baz", staticmethod(baz))
        _bind(VirtualLists, "testPow", staticmethod(testPow))

    for cls in (IntTuples, IntTuplesWithMin, FixedSizedSubsets, Subsets, Permutations, TupleWithMin):
        if cls is None:
            continue
        _bind(cls, "stream", LongList.stream)
        _bind(cls, "parallelStream", LongList.parallelStream)

    g["LongList"] = LongList
    g["_tolist"] = _tolist
