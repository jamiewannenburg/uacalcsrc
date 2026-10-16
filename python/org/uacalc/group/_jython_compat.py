"""Jython-facing helpers for ``org.uacalc.group`` (CPython only).

Java ``PermutationGroup`` is a thin ``GeneralAlgebra`` shell: constructors
store generators (and an unused universe list) but never install a universe
or operations, so ``cardinality()`` is ``-1`` and ``universe()`` /
``operations()`` are null. Static ``prod`` / ``inv`` / ``id`` and the
``make*Op`` factories are the live API. Library extras on ``uacalc_lib``
(``to_basic_algebra``, ``automorphism_group``, safe constructors) stay
available as non-Java methods.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence

from org.uacalc._exceptions import (
    ArrayIndexOutOfBoundsException,
    IndexOutOfBoundsException,
    NegativeArraySizeException,
    NullPointerException,
    UnsupportedOperationException,
)


def _install(g: dict) -> None:
    _LibPermutationGroup = g.get("PermutationGroup")
    g["_LibPermutationGroup"] = _LibPermutationGroup

    def _npe(msg: str = "") -> None:
        raise NullPointerException(msg)

    def _is_int_array(obj: Any) -> bool:
        if obj is None:
            return False
        for name in ("getArray", "toArray", "to_array", "get_array"):
            if callable(getattr(obj, name, None)):
                return True
        return False

    def _raw_array(p: Any) -> List[int]:
        if p is None:
            _npe()
        for name in ("getArray", "toArray", "to_array", "get_array"):
            fn = getattr(p, name, None)
            if callable(fn):
                try:
                    return [int(x) for x in list(fn())]
                except TypeError:
                    continue
        # Jython reports Java ClassCast / failed coercion as TypeError.
        raise TypeError(
            "arg can't be coerced to org.uacalc.util.IntArray"
        )

    def _as_int_array(values: Sequence[int]) -> Any:
        from org.uacalc.util import IntArray

        return IntArray([int(x) for x in list(values)])

    def _aioobe(index: Any = None) -> None:
        if index is None:
            raise ArrayIndexOutOfBoundsException()
        raise ArrayIndexOutOfBoundsException(str(index))

    def _group_symbol(const_name: str, factory_name: str, name: str, arity: int) -> Any:
        from org.uacalc.alg.op import OperationSymbol

        const = getattr(OperationSymbol, const_name, None)
        if const is not None and not callable(const):
            return const
        factory = getattr(OperationSymbol, factory_name, None)
        if callable(factory):
            try:
                return factory()
            except TypeError:
                pass
        return OperationSymbol(name, arity)

    def prod(p0: Any, p1: Any) -> Any:
        """Java ``PermutationGroup.prod``: ``(p0 * p1)(i) = p0(p1(i))``."""
        arr0 = _raw_array(p0)
        arr1 = _raw_array(p1)
        n = len(arr0)
        out = [0] * n
        for i in range(n):
            try:
                idx = arr1[i]
            except IndexError:
                _aioobe(i)
            if idx < 0 or idx >= n:
                _aioobe(idx)
            out[i] = arr0[idx]
        return _as_int_array(out)

    def inv(a: Any) -> Any:
        """Java ``PermutationGroup.inv`` (unmapped slots stay 0)."""
        arr0 = _raw_array(a)
        n = len(arr0)
        out = [0] * n
        for i in range(n):
            idx = arr0[i]
            if idx < 0 or idx >= n:
                _aioobe(idx)
            out[idx] = i
        return _as_int_array(out)

    def id(setSize: Any) -> Any:
        """Java ``PermutationGroup.id``: ``[0, 1, ..., setSize-1]``."""
        if setSize is None:
            _npe()
        try:
            n = int(setSize)
        except (TypeError, ValueError):
            _npe()
        if n < 0:
            raise NegativeArraySizeException()
        return _as_int_array(list(range(n)))

    class _GroupOperation(object):
        """Anonymous ``AbstractOperation`` from ``makeProdOp`` / ``makeInvOp`` / ``makeIdOp``."""

        def __init__(self, symbol: Any, alg_size: int, kind: str, set_size: Optional[int] = None) -> None:
            self._symbol = symbol
            self._alg_size = int(alg_size)
            self._kind = kind
            self._set_size = int(set_size) if set_size is not None else None
            self.valueTable = None

        def arity(self) -> int:
            fn = getattr(self._symbol, "arity", None)
            return int(fn() if callable(fn) else self._symbol)

        def getSetSize(self) -> int:
            return self._alg_size

        get_set_size = getSetSize

        def symbol(self) -> Any:
            return self._symbol

        def valueAt(self, args: Any) -> Any:
            # Jython overload resolution: null / empty list hit
            # AbstractOperation.valueAt(int[][]) which throws UOE.
            # A non-empty Python list hits valueAt(List).
            if args is None:
                raise UnsupportedOperationException()
            try:
                seq = list(args)
            except TypeError as exc:
                raise UnsupportedOperationException(str(exc)) from exc
            if len(seq) == 0:
                raise UnsupportedOperationException()
            try:
                if self._kind == "id":
                    return id(self._set_size)
                if self._kind == "prod":
                    return prod(seq[0], seq[1])
                return inv(seq[0])
            except IndexError as exc:
                raise IndexOutOfBoundsException(str(exc)) from exc

        value_at = valueAt

        def intValueAt(self, args: Any = None) -> int:
            raise UnsupportedOperationException()

        int_value_at = intValueAt

        def isTableBased(self) -> bool:
            return False

        is_table_based = isTableBased

        def makeTable(self) -> None:
            return None

        make_table = makeTable

        def getTable(self, makeTable: Optional[bool] = None) -> Any:
            return self.valueTable

        get_table = getTable

        def toString(self) -> str:
            return str(self)

        def __str__(self) -> str:
            return "{0}(algSize={1})".format(type(self._symbol).__name__, self._alg_size)

    def makeProdOp(algSize: Any) -> _GroupOperation:
        if algSize is None:
            _npe()
        return _GroupOperation(
            _group_symbol("PRODUCT", "product", "prod", 2),
            int(algSize),
            "prod",
        )

    def makeInvOp(algSize: Any) -> _GroupOperation:
        if algSize is None:
            _npe()
        return _GroupOperation(
            _group_symbol("INVERSE", "inverse", "inv", 1),
            int(algSize),
            "inv",
        )

    def makeIdOp(algSize: Any, setSize: Any) -> _GroupOperation:
        if algSize is None or setSize is None:
            _npe()
        return _GroupOperation(
            _group_symbol("IDENTITY", "identity", "id", 0),
            int(algSize),
            "id",
            int(setSize),
        )

    class PermutationGroup(object):
        """Java ``org.uacalc.group.PermutationGroup`` facade."""

        def __init__(self, name: Any, generators: Any, universeList: Any = None) -> None:
            self._name = name
            self._generators = None if generators is None else list(generators)
            self._universe_list = None if universeList is None else list(universeList)
            self._description = None
            self._lib = None

        def _ensure_lib(self) -> Any:
            if self._lib is not None:
                return self._lib
            if _LibPermutationGroup is None:
                return None
            gens = []
            for g in self._generators or []:
                if _is_int_array(g):
                    gens.append(_raw_array(g))
                else:
                    try:
                        gens.append([int(x) for x in list(g)])
                    except (TypeError, ValueError):
                        return None
            try:
                self._lib = _LibPermutationGroup(self._name or "", gens)
            except Exception:
                self._lib = None
            return self._lib

        def getName(self) -> Any:
            return self._name

        get_name = getName

        def setName(self, v: Any) -> None:
            self._name = v

        def getDescription(self) -> Any:
            return self._description

        def setDescription(self, desc: Any) -> None:
            self._description = desc

        def cardinality(self) -> int:
            # Java GeneralAlgebra.cardinality: universe is never set → -1.
            return -1

        def universe(self) -> Any:
            return None

        def operations(self) -> Any:
            return None

        def inputSize(self) -> int:
            return -1

        def parent(self) -> Any:
            return None

        def parents(self) -> Any:
            return None

        def makeOperationTables(self) -> None:
            return None

        def resetConAndSub(self) -> None:
            return None

        def iterator(self) -> Any:
            _npe()

        def isTotal(self) -> bool:
            _npe()
            return False

        def isUnary(self) -> bool:
            _npe()
            return False

        def isIdempotent(self) -> bool:
            _npe()
            return False

        def similarityType(self) -> Any:
            _npe()

        def getOperationsMap(self) -> Any:
            _npe()

        def getOperation(self, sym: Any = None) -> Any:
            _npe()

        def constantOperations(self) -> Any:
            _npe()

        def isSimilarTo(self, alg2: Any) -> bool:
            _npe()
            return False

        def con(self) -> Any:
            raise UnsupportedOperationException()

        def sub(self) -> Any:
            raise UnsupportedOperationException()

        def toString(self) -> str:
            return str(self)

        def __str__(self) -> str:
            return "PermutationGroup({0})".format(self._name)

        def __repr__(self) -> str:
            return "PermutationGroup({0})".format(self._name)

        @staticmethod
        def prod(p0: Any, p1: Any) -> Any:
            return prod(p0, p1)

        @staticmethod
        def inv(a: Any) -> Any:
            return inv(a)

        @staticmethod
        def id(setSize: Any) -> Any:
            return id(setSize)

        @staticmethod
        def makeProdOp(algSize: Any) -> _GroupOperation:
            return makeProdOp(algSize)

        @staticmethod
        def makeInvOp(algSize: Any) -> _GroupOperation:
            return makeInvOp(algSize)

        @staticmethod
        def makeIdOp(algSize: Any, setSize: Any) -> _GroupOperation:
            return makeIdOp(algSize, setSize)

        @staticmethod
        def new_with_universe(name: Any, generators: Any, universe: Any) -> "PermutationGroup":
            return PermutationGroup(name, generators, universe)

        @staticmethod
        def new_safe(name: Any, generators: Any) -> "PermutationGroup":
            return PermutationGroup(name, generators)

        @staticmethod
        def new_with_universe_safe(name: Any, generators: Any, universe: Any) -> "PermutationGroup":
            return PermutationGroup(name, generators, universe)

        @staticmethod
        def automorphism_group(alg: Any) -> Any:
            if _LibPermutationGroup is None:
                raise UnsupportedOperationException("automorphism_group is a uacalc_lib extra")
            return _LibPermutationGroup.automorphism_group(alg)

        def get_generators(self) -> Any:
            if self._generators is None:
                return None
            out = []
            for g in self._generators:
                if _is_int_array(g):
                    out.append(_raw_array(g))
                else:
                    try:
                        out.append([int(x) for x in list(g)])
                    except (TypeError, ValueError):
                        out.append(g)
            return out

        def get_universe_list(self) -> Any:
            if self._universe_list is None:
                return None
            out = []
            for g in self._universe_list:
                if _is_int_array(g):
                    out.append(_raw_array(g))
                else:
                    try:
                        out.append([int(x) for x in list(g)])
                    except (TypeError, ValueError):
                        out.append(g)
            return out

        def get_underlying_set_size(self) -> int:
            gens = self.get_generators() or []
            if not gens:
                return 0
            first = gens[0]
            try:
                return len(first)
            except TypeError:
                return 0

        def get_identity(self) -> Any:
            n = self.get_underlying_set_size()
            if n <= 0:
                return None
            return list(range(n))

        def to_basic_algebra(self, name: Any) -> Any:
            lib = self._ensure_lib()
            if lib is None:
                raise UnsupportedOperationException(
                    "to_basic_algebra is a uacalc_lib extra; Java has no conversion"
                )
            return lib.to_basic_algebra(name)

    g["PermutationGroup"] = PermutationGroup
