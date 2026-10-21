"""Jython-facing helpers for ``org.uacalc.alg.sublat`` (CPython only).

Renames, constructor/overload dispatch, and Java stub matching only.
Library logic stays in ``uacalc_lib``.
"""

from __future__ import annotations

from typing import Any, Optional

from org.uacalc._exceptions import (
    ArrayIndexOutOfBoundsException,
    IllegalArgumentException,
    NullPointerException,
    UnsupportedOperationException,
    translate_illegal_argument,
)


def _install(sublat_globals: dict) -> None:
    _LibBasicSet = sublat_globals.get("BasicSet")
    _LibSubalgebraLattice = sublat_globals.get("SubalgebraLattice")
    if _LibBasicSet is None or _LibSubalgebraLattice is None:
        return

    _SL_ALGEBRAS: dict = {}
    _SL_MONITOR = [None]
    _ORIG_BS_LEQ = _LibBasicSet.leq
    _ORIG_BS_INTER = _LibBasicSet.intersection
    _ORIG_BS_GET = getattr(_LibBasicSet, "get", None)
    _ORIG_BS_CONTAINS = _LibBasicSet.contains
    _ORIG_BS_NORMALIZE = getattr(_LibBasicSet, "normalize", None)
    _ORIG_SL_JOIN = getattr(_LibSubalgebraLattice, "join", None)
    _ORIG_SL_LEQ = getattr(_LibSubalgebraLattice, "leq", None)
    _ORIG_SL_SG = getattr(_LibSubalgebraLattice, "sg", None)
    _ORIG_SL_FILTER = getattr(_LibSubalgebraLattice, "filter", None)

    def _raise_npe(what: str = "null") -> None:
        raise NullPointerException(what)

    def _lib_call(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as exc:
            msg = str(exc)
            if "generating sets must have the same size" in msg:
                raise IllegalArgumentException(msg) from exc
            if msg.startswith("Index ") and "out of bounds" in msg:
                raise ArrayIndexOutOfBoundsException(msg) from exc
            translate_illegal_argument(exc)

    def _is_basic_set(obj: Any) -> bool:
        if obj is None:
            return False
        return isinstance(obj, _LibBasicSet) or type(obj).__name__ in (
            "BasicSet",
            "PyBasicSet",
        )

    def _as_int_list(obj: Any) -> list:
        if obj is None:
            _raise_npe()
        if _is_basic_set(obj):
            fn = getattr(obj, "toArray", None) or getattr(obj, "to_array", None) or getattr(
                obj, "elements", None
            )
            if callable(fn):
                return [int(x) for x in fn()]
        if isinstance(obj, (list, tuple)):
            return [int(x) for x in obj]
        try:
            return [int(x) for x in obj]
        except TypeError:
            return [int(obj)]

    def _is_java_set(obj: Any) -> bool:
        if obj is None:
            return False
        if isinstance(obj, (set, frozenset)):
            return True
        mod = type(obj).__module__ or ""
        name = type(obj).__name__
        if "java.util" in mod or name in ("HashSet", "TreeSet", "LinkedHashSet", "Set"):
            return True
        return False

    # --- BasicSet ---
    def universeSize(self: Any) -> int:
        fn = getattr(self, "universe_size", None)
        if callable(fn):
            return int(fn())
        return int(self.size())

    def get(self: Any, index: Any) -> int:
        if index is None:
            _raise_npe()
        n = universeSize(self)
        k = int(index)
        if k < 0 or k >= n:
            raise ArrayIndexOutOfBoundsException(
                "Index {0} out of bounds for length {1}".format(k, n)
            )
        if callable(_ORIG_BS_GET):
            try:
                return int(_lib_call(_ORIG_BS_GET, self, k))
            except TypeError:
                pass
        elems = _as_int_list(self)
        return int(elems[k])

    def toArray(self: Any) -> list:
        fn = getattr(self, "to_array", None) or getattr(self, "elements", None)
        if callable(fn):
            return [int(x) for x in fn()]
        return _as_int_list(self)

    def getArray(self: Any) -> list:
        return toArray(self)

    def _bs_str(self: Any) -> str:
        elems = toArray(self)
        if not elems:
            return "[]"
        return "[" + ", ".join(str(int(x)) for x in elems) + "]"

    def toString(self: Any) -> str:
        return _bs_str(self)

    def compareTo(self: Any, other: Any) -> int:
        if other is None:
            _raise_npe()
        fn = getattr(self, "compare_to", None)
        if callable(fn):
            return int(fn(other))
        if self < other:
            return -1
        if self == other:
            return 0
        return 1

    def setDifference(self: Any, other: Any) -> Any:
        if other is None:
            _raise_npe()
        fn = getattr(self, "set_difference", None)
        if callable(fn):
            return fn(other)
        raise TypeError("setDifference is not bound")

    def leq(self_or_u: Any, other: Any) -> bool:
        if self_or_u is None or other is None:
            _raise_npe()
        if _is_basic_set(self_or_u) and _is_basic_set(other):
            return bool(_ORIG_BS_LEQ(self_or_u, other))
        u = _as_int_list(self_or_u)
        v = _as_int_list(other)
        fn = getattr(_LibBasicSet, "leq_static", None)
        if callable(fn):
            return bool(fn(u, v))
        return set(u).issubset(set(v))

    def intersection(self_or_a: Any, other: Any) -> Any:
        if self_or_a is None or other is None:
            _raise_npe()
        if _is_basic_set(self_or_a) and _is_basic_set(other):
            return _ORIG_BS_INTER(self_or_a, other)
        a = BasicSet(_as_int_list(self_or_a)) if not _is_basic_set(self_or_a) else self_or_a
        b = BasicSet(_as_int_list(other)) if not _is_basic_set(other) else other
        return _ORIG_BS_INTER(a, b)

    def union(self_or_a: Any, other: Any) -> Any:
        # Java BasicSet.union uses ``lst.contains(i)`` on the *index*, not the
        # element (a real Java bug). Match that, then construct BasicSet (sorts).
        if self_or_a is None or other is None:
            _raise_npe()
        set1 = self_or_a if _is_basic_set(self_or_a) else BasicSet(_as_int_list(self_or_a))
        set2 = other if _is_basic_set(other) else BasicSet(_as_int_list(other))
        lst = [int(get(set1, i)) for i in range(universeSize(set1))]
        for i in range(universeSize(set2)):
            if i not in lst:
                lst.append(int(get(set2, i)))
        return _LibBasicSet(lst)

    def contains(self: Any, element: Any) -> bool:
        if element is None:
            _raise_npe()
        return bool(_ORIG_BS_CONTAINS(self, int(element)))

    def normalize(self: Any) -> None:
        if callable(_ORIG_BS_NORMALIZE):
            _ORIG_BS_NORMALIZE(self)

    class _BSMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            return isinstance(instance, _LibBasicSet)

    class BasicSet(object, metaclass=_BSMeta):
        def __new__(cls, elements: Any = None):
            if elements is None:
                _raise_npe(
                    'Cannot read the array length because "set" is null'
                )
            return _LibBasicSet(_as_int_list(elements))

    BasicSet.EMPTY_SET = _LibBasicSet([])
    try:
        _LibBasicSet.EMPTY_SET = BasicSet.EMPTY_SET
    except (TypeError, AttributeError):
        pass

    _BS_PATCHES = {
        "universeSize": universeSize,
        "get": get,
        "toArray": toArray,
        "getArray": getArray,
        "toString": toString,
        "__str__": _bs_str,
        "__repr__": lambda self: "BasicSet(" + _bs_str(self) + ")",
        "compareTo": compareTo,
        "setDifference": setDifference,
        "contains": contains,
        "normalize": normalize,
        "leq": leq,
        "intersection": intersection,
        "union": union,
    }
    for camel, impl in _BS_PATCHES.items():
        try:
            setattr(_LibBasicSet, camel, impl)
        except (TypeError, AttributeError):
            pass
        try:
            setattr(BasicSet, camel, impl)
        except (TypeError, AttributeError):
            pass

    # --- SubalgebraLattice ---
    def getAlgebra(self: Any) -> Any:
        return _SL_ALGEBRAS.get(id(self))

    def _remember(sl: Any, alg: Any) -> Any:
        if sl is not None:
            _SL_ALGEBRAS[id(sl)] = alg
        return sl

    def getName(self: Any) -> str:
        alg = getAlgebra(self)
        return "Sub(" + str(alg) + ")"

    def setName(self: Any, v: Any) -> None:
        raise UnsupportedOperationException()

    def getDescription(self: Any) -> str:
        fn = getattr(self, "get_description", None)
        if callable(fn):
            return str(fn())
        return "Subalgebra Lattice of " + str(getAlgebra(self))

    def setDescription(self: Any, desc: Any) -> None:
        fn = getattr(self, "set_description", None)
        if callable(fn):
            fn(None if desc is None else str(desc))

    def similarityType(self: Any) -> Any:
        from org.uacalc.alg.op import SimilarityType

        return SimilarityType.LATTICE_SIMILARITY_TYPE

    def isSimilarTo(self: Any, other: Any) -> bool:
        if other is None:
            _raise_npe()
        st = similarityType(self)
        ost = getattr(other, "similarityType", None) or getattr(
            other, "similarity_type", None
        )
        if callable(ost):
            ost = ost()
        eq = getattr(st, "equals", None)
        if callable(eq):
            return bool(eq(ost))
        return st == ost

    def updateSimilarityType(self: Any) -> None:
        return None

    def isTotal(self: Any) -> bool:
        return True

    def isUnary(self: Any) -> bool:
        return False

    def isIdempotent(self: Any) -> bool:
        return True

    def operations(self: Any) -> Any:
        return None

    def getOperation(self: Any, sym: Any) -> Any:
        return None

    def getOperationsMap(self: Any) -> Any:
        return None

    def constantOperations(self: Any) -> list:
        return []

    def makeOperationTables(self: Any) -> None:
        return None

    def atoms(self: Any) -> Any:
        return None

    def coatoms(self: Any) -> Any:
        return None

    def meetIrreducibles(self: Any) -> Any:
        # Java makeMeetIrreducibles is an empty stub; the field stays null.
        return None

    def meet(self: Any, a: Any, b: Any = None) -> Any:
        # Java meet(Object,Object) and meet(List) are identically null.
        return None

    def join(self: Any, a: Any, b: Any = None) -> Any:
        # Java join(List) is identically null; join(a,b) is implemented.
        if b is None:
            return None
        if a is None or b is None:
            _raise_npe()
        if _ORIG_SL_JOIN is None:
            raise TypeError("join is not bound")
        return _ORIG_SL_JOIN(self, a, b)

    def leq_sl(self: Any, a: Any, b: Any) -> bool:
        if a is None or b is None:
            _raise_npe()
        if _ORIG_SL_LEQ is not None:
            return bool(_ORIG_SL_LEQ(self, a, b))
        return bool(a.leq(b))

    def sg(self: Any, gens: Any) -> Any:
        if _is_java_set(gens):
            return None
        if gens is None:
            _raise_npe()
        if _is_basic_set(gens):
            gens = _as_int_list(gens)
        if _ORIG_SL_SG is None:
            raise TypeError("sg is not bound")
        return _ORIG_SL_SG(self, _as_int_list(gens))

    def Sg(self: Any, gens: Any) -> Any:
        from org.uacalc.alg import Subalgebra

        alg = getAlgebra(self)
        if _is_basic_set(gens):
            univ = gens
        else:
            univ = sg(self, gens)
        alg_name = ""
        if alg is not None:
            gname = getattr(alg, "getName", None) or getattr(alg, "get_name", None) or getattr(
                alg, "name", None
            )
            alg_name = str(gname() if callable(gname) else (gname or ""))
        return Subalgebra("Subalgebra Of " + alg_name, alg, univ)

    def iterator(self: Any) -> Any:
        return iter(self.universe())

    def oneGeneratedSubalgebras(self: Any) -> list:
        return list(self.one_generated_subalgebras())

    def joinIrreducibles(self: Any) -> list:
        return list(self.join_irreducibles())

    def joinIrreducible(self: Any, subalg: Any) -> bool:
        if subalg is None:
            _raise_npe()
        fn = getattr(self, "join_irreducible", None)
        if callable(fn):
            return bool(fn(subalg))
        return subalg in joinIrreducibles(self)

    def findMinimalSizedGeneratingSet(self: Any) -> Any:
        return self.find_minimal_sized_generating_set()

    def universeFound(self: Any) -> bool:
        fn = getattr(self, "universe_found", None)
        if callable(fn):
            return bool(fn())
        return True

    def makeUniverse(self: Any, maxSize: Any = None) -> None:
        if maxSize is None:
            self.universe()
            return
        fn = getattr(self, "make_universe", None)
        if callable(fn):
            fn(int(maxSize))
            return
        self.universe()

    def makeJoinIrreducibles(self: Any) -> None:
        joinIrreducibles(self)

    def makeSg(self: Any, gens: Any, closedMark: Any = None, maxSize: Any = None) -> Any:
        if gens is None:
            _raise_npe()
        fn = getattr(self, "make_sg", None)
        mark = 0 if closedMark is None else int(closedMark)
        if callable(fn):
            return fn(_as_int_list(gens), mark)
        return sg(self, gens)

    def joinClosure(self: Any, gens: Any, maxSize: Any = None) -> Any:
        if gens is None:
            _raise_npe()
        stop_if_big = maxSize is not None and int(maxSize) > 0
        items = list(gens)
        ans = list(items)
        ans_list = list(items)
        for s in items:
            n = len(ans_list)
            for i in range(n):
                joined = join(self, s, ans_list[i])
                if joined not in ans:
                    ans.append(joined)
                    ans_list.append(joined)
                    if stop_if_big and len(ans_list) >= int(maxSize):
                        return None
        return ans

    def filter(self: Any, elt: Any) -> list:
        if elt is None:
            _raise_npe()
        if callable(_ORIG_SL_FILTER):
            return list(_ORIG_SL_FILTER(self, elt))
        return [x for x in self.universe() if leq_sl(self, elt, x)]

    def getBasicLattice(self: Any, makeIfNull: Optional[bool] = None) -> Any:
        fn = getattr(self, "get_basic_lattice", None)
        make = True if makeIfNull is None else bool(makeIfNull)
        if callable(fn):
            result = fn(make)
            if isinstance(result, tuple) or result is None:
                return result
            return result
        return None

    def inputSize(self: Any) -> int:
        card = int(self.cardinality())
        if card < 0:
            return -1
        st = similarityType(self)
        fn = getattr(st, "inputSize", None) or getattr(st, "input_size", None)
        if callable(fn):
            return int(fn(card))
        return card

    def isSmallerThan(self: Any, size: Any) -> bool:
        # Java computes the universe as a side effect (makeUniverse).
        return int(self.cardinality()) < int(size)

    def isDrawable(self: Any) -> bool:
        return int(self.cardinality()) <= int(
            getattr(self, "MAX_DRAWABLE_SIZE", 100) or 100
        )

    def setMonitor(self: Any, monitor: Any) -> None:
        if monitor is not None:
            raise TypeError(
                "setMonitor(): expected org.uacalc.ui.tm.ProgressReport or None"
            )
        _SL_MONITOR[0] = None

    def getMonitor(self: Any) -> Any:
        return _SL_MONITOR[0]

    def monitoring(self: Any) -> bool:
        return _SL_MONITOR[0] is not None

    def getMakeUniverseK(self: Any) -> int:
        # Java field is only written by the commented-out Task helper.
        return 0

    def getSizeComputed(self: Any) -> int:
        fn = getattr(self, "get_size_computed", None)
        if callable(fn):
            return int(fn())
        return len(joinIrreducibles(self))

    def stopMakeUniverse(self: Any) -> None:
        return None

    def noDuplicates(lst: Any) -> list:
        if lst is None:
            _raise_npe()
        fn = getattr(_LibSubalgebraLattice, "no_duplicates", None)
        items = list(lst)
        if callable(fn) and items and all(isinstance(x, int) for x in items):
            return list(fn(items))
        if not items:
            return items
        out = []
        previous = items[0]
        out.append(previous)
        for nxt in items[1:]:
            if nxt != previous:
                out.append(nxt)
            previous = nxt
        return out

    def extendToHomomorphism(gens: Any, gensB: Any, A: Any, B: Any) -> Any:
        if gens is None or gensB is None:
            _raise_npe()
        g = _as_int_list(gens)
        gb = _as_int_list(gensB)
        if len(g) != len(gb):
            raise IllegalArgumentException("generating sets must have the same size")
        fn = getattr(_LibSubalgebraLattice, "extend_to_homomorphism", None)
        if not callable(fn):
            raise TypeError("extendToHomomorphism is not bound")
        a = getattr(A, "_inner", A)
        b = getattr(B, "_inner", B)
        return _lib_call(fn, g, gb, a, b)

    def con(self: Any) -> Any:
        lat = getBasicLattice(self)
        fn = getattr(lat, "con", None)
        if not callable(fn):
            raise NotImplementedError(
                "SubalgebraLattice.con() needs BasicLattice.con on a BasicSet lattice"
            )
        return fn()

    def sub(self: Any) -> Any:
        lat = getBasicLattice(self)
        fn = getattr(lat, "sub", None)
        if not callable(fn):
            raise NotImplementedError(
                "SubalgebraLattice.sub() needs BasicLattice.sub on a BasicSet lattice"
            )
        return fn()

    _SL_PATCHES = {
        "getAlgebra": getAlgebra,
        "getName": getName,
        "setName": setName,
        "getDescription": getDescription,
        "setDescription": setDescription,
        "similarityType": similarityType,
        "isSimilarTo": isSimilarTo,
        "updateSimilarityType": updateSimilarityType,
        "isTotal": isTotal,
        "isUnary": isUnary,
        "isIdempotent": isIdempotent,
        "operations": operations,
        "getOperation": getOperation,
        "getOperationsMap": getOperationsMap,
        "constantOperations": constantOperations,
        "makeOperationTables": makeOperationTables,
        "atoms": atoms,
        "coatoms": coatoms,
        "meetIrreducibles": meetIrreducibles,
        "meet": meet,
        "join": join,
        "leq": leq_sl,
        "sg": sg,
        "Sg": Sg,
        "iterator": iterator,
        "oneGeneratedSubalgebras": oneGeneratedSubalgebras,
        "joinIrreducibles": joinIrreducibles,
        "joinIrreducible": joinIrreducible,
        "findMinimalSizedGeneratingSet": findMinimalSizedGeneratingSet,
        "universeFound": universeFound,
        "makeUniverse": makeUniverse,
        "makeJoinIrreducibles": makeJoinIrreducibles,
        "makeSg": makeSg,
        "joinClosure": joinClosure,
        "filter": filter,
        "getBasicLattice": getBasicLattice,
        "inputSize": inputSize,
        "isSmallerThan": isSmallerThan,
        "isDrawable": isDrawable,
        "setMonitor": setMonitor,
        "getMonitor": getMonitor,
        "monitoring": monitoring,
        "getMakeUniverseK": getMakeUniverseK,
        "getSizeComputed": getSizeComputed,
        "stopMakeUniverse": stopMakeUniverse,
        "con": con,
        "sub": sub,
    }
    for camel, impl in _SL_PATCHES.items():
        try:
            setattr(_LibSubalgebraLattice, camel, impl)
        except (TypeError, AttributeError):
            pass

    try:
        _LibSubalgebraLattice.noDuplicates = staticmethod(noDuplicates)
    except (TypeError, AttributeError):
        _LibSubalgebraLattice.noDuplicates = noDuplicates
    try:
        _LibSubalgebraLattice.extendToHomomorphism = staticmethod(extendToHomomorphism)
    except (TypeError, AttributeError):
        _LibSubalgebraLattice.extendToHomomorphism = extendToHomomorphism
    try:
        _LibSubalgebraLattice.MAX_DRAWABLE_SIZE = 100
    except (TypeError, AttributeError):
        pass
    try:
        _LibSubalgebraLattice.__iter__ = iterator
    except (TypeError, AttributeError):
        pass

    class _SLMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            return isinstance(instance, _LibSubalgebraLattice)

    class SubalgebraLattice(object, metaclass=_SLMeta):
        MAX_DRAWABLE_SIZE = 100

        def __new__(cls, alg: Any):
            if alg is None:
                _raise_npe(
                    'Cannot invoke "org.uacalc.alg.SmallAlgebra.cardinality()" '
                    "because \"alg\" is null"
                )
            inner = getattr(alg, "_inner", alg)
            typ = type(inner).__name__
            if typ in ("PyBasicAlgebra", "BasicAlgebra"):
                obj = _LibSubalgebraLattice(inner)
            elif hasattr(alg, "sub") and callable(alg.sub):
                obj = alg.sub()
            else:
                conv = getattr(alg, "to_basic_algebra", None) or getattr(
                    inner, "to_basic_algebra", None
                )
                if callable(conv):
                    obj = _LibSubalgebraLattice(conv())
                else:
                    obj = _LibSubalgebraLattice(inner)
            return _remember(obj, alg)

        @staticmethod
        def noDuplicates(lst: Any) -> list:
            return noDuplicates(lst)

        @staticmethod
        def extendToHomomorphism(gens: Any, gensB: Any, A: Any, B: Any) -> Any:
            return extendToHomomorphism(gens, gensB, A, B)

    # Remember the algebra on alg.sub() as well as SubalgebraLattice(alg).
    try:
        import org.uacalc.alg as _algmod
    except ImportError:
        _algmod = None
    if _algmod is not None:
        def _wrap_alg_sub(orig):
            def sub(self, _orig=orig):
                return _remember(_orig(self), self)

            return sub

        for _name in (
            "BasicAlgebra",
            "ProductAlgebra",
            "PowerAlgebra",
            "QuotientAlgebra",
            "Subalgebra",
            "SubProductAlgebra",
            "FreeAlgebra",
            "ReductAlgebra",
            "GeneralAlgebra",
            "MatrixPowerAlgebra",
            "PolinLikeAlgebra",
            "UnaryTermsMonoid",
        ):
            # Python wrappers often have no .sub; AlgebraIO/ctors return _Lib* PyO3 types.
            for attr in (_name, "_Lib" + _name):
                cls = getattr(_algmod, attr, None)
                if cls is None or not hasattr(cls, "sub"):
                    continue
                orig = cls.sub
                if getattr(orig, "_sublat_remember", False):
                    continue
                wrapped = _wrap_alg_sub(orig)
                wrapped._sublat_remember = True
                try:
                    cls.sub = wrapped
                except (TypeError, AttributeError):
                    pass

    _CLASS_ALIASES = {
        "BasicSet": {
            "universeSize": "universe_size",
            "setDifference": "set_difference",
            "toArray": "to_array",
            "getArray": "get_array",
            "compareTo": "compare_to",
            "toString": "toString",
            "leq": "leq",
            "intersection": "intersection",
            "union": "union",
            "contains": "contains",
            "get": "get",
            "normalize": "normalize",
        },
        "SubalgebraLattice": {
            "iterator": "iterator",
            "Sg": "Sg",
            "sg": "sg",
            "getName": "getName",
            "getAlgebra": "getAlgebra",
            "getDescription": "getDescription",
            "setDescription": "setDescription",
            "joinIrreducibles": "joinIrreducibles",
            "meetIrreducibles": "meetIrreducibles",
            "oneGeneratedSubalgebras": "oneGeneratedSubalgebras",
            "findMinimalSizedGeneratingSet": "findMinimalSizedGeneratingSet",
            "getBasicLattice": "getBasicLattice",
            "universeFound": "universeFound",
            "makeUniverse": "makeUniverse",
            "makeJoinIrreducibles": "makeJoinIrreducibles",
            "joinIrreducible": "joinIrreducible",
            "inputSize": "inputSize",
            "similarityType": "similarityType",
            "isSimilarTo": "isSimilarTo",
            "isSmallerThan": "isSmallerThan",
            "isDrawable": "isDrawable",
            "constantOperations": "constantOperations",
            "makeSg": "makeSg",
            "joinClosure": "joinClosure",
            "noDuplicates": "noDuplicates",
            "extendToHomomorphism": "extendToHomomorphism",
            "getMakeUniverseK": "getMakeUniverseK",
            "getSizeComputed": "getSizeComputed",
            "stopMakeUniverse": "stopMakeUniverse",
            "setMonitor": "setMonitor",
            "getMonitor": "getMonitor",
            "monitoring": "monitoring",
            "updateSimilarityType": "updateSimilarityType",
            "makeOperationTables": "makeOperationTables",
            "getOperation": "getOperation",
            "getOperationsMap": "getOperationsMap",
            "operations": "operations",
            "atoms": "atoms",
            "coatoms": "coatoms",
            "meet": "meet",
            "join": "join",
            "leq": "leq",
            "filter": "filter",
            "cardinality": "cardinality",
            "universe": "universe",
            "zero": "zero",
            "one": "one",
            "con": "con",
            "sub": "sub",
            "setName": "setName",
            "isTotal": "isTotal",
            "isUnary": "isUnary",
            "isIdempotent": "isIdempotent",
        },
    }

    sublat_globals["BasicSet"] = BasicSet
    sublat_globals["SubalgebraLattice"] = SubalgebraLattice
    sublat_globals["_CLASS_ALIASES"] = _CLASS_ALIASES
    sublat_globals["_SL_ALGEBRAS"] = _SL_ALGEBRAS
