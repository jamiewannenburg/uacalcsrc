"""Jython-facing helpers for ``org.uacalc.alg.conlat`` (CPython only).

Renames, constructor/overload dispatch, and Java exception translation only.
Library logic stays in ``uacalc_lib``.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

_MISSING = object()

from org.uacalc._exceptions import (
    ArrayIndexOutOfBoundsException,
    IllegalArgumentException,
    IndexOutOfBoundsException,
    NullPointerException,
    NumberFormatException,
    RuntimeException,
    StringIndexOutOfBoundsException,
    UnsupportedOperationException,
    translate_illegal_argument,
)


def _install(conlat_globals: dict) -> None:
    _LibPartition = conlat_globals.get("Partition") or conlat_globals.get("BasicPartition")
    _LibCongruenceLattice = conlat_globals.get("CongruenceLattice")
    _LibPrintType = conlat_globals.get("PrintType")
    if _LibPartition is None:
        return

    def _raise_npe(what: str = "null") -> None:
        raise NullPointerException(what)

    def _lib_call(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as exc:
            msg = str(exc)
            if msg == "RuntimeException":
                raise RuntimeException() from exc
            if msg.startswith("String index out of range"):
                raise StringIndexOutOfBoundsException(msg) from exc
            if msg.startswith("Index:"):
                raise IndexOutOfBoundsException(msg) from exc
            if msg == "Not a valid partition string":
                raise IllegalArgumentException(msg) from exc
            if "Invalid number" in msg or "invalid literal" in msg.lower() or "parse" in msg.lower():
                raise NumberFormatException(msg) from exc
            if msg == "null":
                _raise_npe()
            translate_illegal_argument(exc)

    def _as_int_list(obj: Any) -> list:
        if obj is None:
            _raise_npe()
        if isinstance(obj, (list, tuple)):
            return [int(x) for x in obj]
        to_arr = getattr(obj, "toArray", None) or getattr(obj, "to_array", None) or getattr(
            obj, "getArray", None
        )
        if callable(to_arr):
            return [int(x) for x in to_arr()]
        try:
            return [int(x) for x in obj]
        except TypeError as exc:
            raise TypeError(str(exc)) from exc

    def _print_type_name(kind: Any) -> str:
        if kind is None:
            _raise_npe()
        name = getattr(kind, "name", None)
        if callable(name):
            try:
                return str(name())
            except TypeError:
                pass
        text = str(kind)
        return text.rsplit(".", 1)[-1].replace("sq_brace_block", "SQ_BRACE_BLOCK").upper()

    def _lib_print_type(kind: Any) -> Any:
        if _LibPrintType is None:
            return kind
        key = _print_type_name(kind).lower().replace("sq_brace_block", "sq_brace_block")
        mapping = {
            "internal": "internal",
            "ewk": "ewk",
            "block": "block",
            "human": "human",
            "sq_brace_block": "sq_brace_block",
        }
        return _LibPrintType(mapping.get(key, key))

    def _bounds(self: Any, *idxs: Any) -> None:
        n = int(self.universe_size() if hasattr(self, "universe_size") else self.universeSize())
        for i in idxs:
            if i is None:
                _raise_npe()
            k = int(i)
            if k < 0 or k >= n:
                raise ArrayIndexOutOfBoundsException(
                    "Index {0} out of bounds for length {1}".format(k, n)
                )

    # --- PrintType (Java nested enum) ---
    class PrintType(object):
        def __init__(self, name: str) -> None:
            self._name = str(name)

        def name(self) -> str:
            return self._name

        def toString(self) -> str:
            return self._name

        def ordinal(self) -> int:
            order = ("INTERNAL", "EWK", "BLOCK", "HUMAN", "SQ_BRACE_BLOCK")
            try:
                return order.index(self._name)
            except ValueError:
                return -1

        def __str__(self) -> str:
            return self._name

        def __repr__(self) -> str:
            return self._name

        def __eq__(self, other: Any) -> bool:
            if other is None:
                return False
            if isinstance(other, PrintType):
                return self._name == other._name
            return self._name == str(other).rsplit(".", 1)[-1]

        def __hash__(self) -> int:
            return hash(self._name)

    for _pt_name in ("INTERNAL", "EWK", "BLOCK", "HUMAN", "SQ_BRACE_BLOCK"):
        setattr(PrintType, _pt_name, PrintType(_pt_name))

    # --- instance method patches on the library Partition ---
    def universeSize(self: Any) -> int:
        return int(self.universe_size())

    def numberOfBlocks(self: Any) -> int:
        return int(self.number_of_blocks())

    def isRelated(self: Any, i: Any, j: Any) -> bool:
        _bounds(self, i, j)
        return bool(self.is_related(int(i), int(j)))

    _orig_representative = getattr(_LibPartition, "representative", None)
    _orig_is_representative = getattr(_LibPartition, "is_representative", None)
    _orig_representatives = getattr(_LibPartition, "representatives", None)
    _orig_normalize = getattr(_LibPartition, "normalize", None)
    _orig_rank = getattr(_LibPartition, "rank", None)
    # Java Partition.leq is refinement, not PartialOrd/compareTo (`le`).
    _orig_leq = getattr(_LibPartition, "leq", None) or getattr(_LibPartition, "le", None)
    _orig_get = getattr(_LibPartition, "get", None)
    _orig_join = getattr(_LibPartition, "join", None)
    _orig_meet = getattr(_LibPartition, "meet", None)
    _orig_compose = getattr(_LibPartition, "compose", None)

    def representative(self: Any, i: Any) -> int:
        _bounds(self, i)
        return int(_orig_representative(self, int(i)))

    def isRepresentative(self: Any, i: Any) -> bool:
        _bounds(self, i)
        return bool(_orig_is_representative(self, int(i)))

    def representatives(self: Any) -> list:
        return [int(x) for x in self.representatives()]

    def blockIndex(self: Any, i: Any) -> int:
        _bounds(self, i)
        return int(_lib_call(self.block_index, int(i)))

    def getBlocks(self: Any) -> list:
        blocks = self.get_blocks()
        return [[int(x) for x in blk] for blk in blocks]

    def joinBlocks(self: Any, r: Any, s: Any) -> None:
        _bounds(self, r, s)
        _lib_call(self.join_blocks, int(r), int(s))

    def join(self: Any, part2: Any) -> Any:
        if part2 is None:
            _raise_npe()
        return _lib_call(_orig_join, self, part2)

    def meet(self: Any, part2: Any) -> Any:
        if part2 is None:
            _raise_npe()
        return _lib_call(_orig_meet, self, part2)

    def leq(self: Any, part2: Any) -> bool:
        if part2 is None:
            _raise_npe()
        return bool(_orig_leq(self, part2))

    def normalize(self: Any) -> None:
        arr = list(self.to_array())
        if not arr:
            raise IndexOutOfBoundsException("Index: 0, Size: 0")
        if arr[0] == 0:
            raise RuntimeException()
        _orig_normalize(self)

    def isZero(self: Any) -> bool:
        return bool(self.is_zero())

    def isUniform(self: Any) -> bool:
        return bool(self.is_uniform())

    def isInitialLexRepresentative(self: Any) -> bool:
        return bool(self.is_initial_lex_representative())

    def toArray(self: Any) -> list:
        return [int(x) for x in self.to_array()]

    def getArray(self: Any) -> list:
        fn = getattr(self, "get_array", None)
        if callable(fn):
            return [int(x) for x in fn()]
        return toArray(self)

    def get(self: Any, i: Any) -> int:
        _bounds(self, i)
        if callable(_orig_get):
            try:
                return int(_orig_get(self, int(i)))
            except (IndexError, ValueError) as exc:
                raise IndexOutOfBoundsException(str(exc)) from exc
        arr = toArray(self)
        k = int(i)
        if k < 0 or k >= len(arr):
            raise IndexOutOfBoundsException(
                "Index {0} out of bounds for length {1}".format(k, len(arr))
            )
        return int(arr[k])

    def rank(self: Any) -> int:
        return int(self.rank())

    def getPairs(self: Any) -> list:
        return self.get_pairs()

    def compose(self: Any, beta: Any) -> Any:
        if beta is None:
            _raise_npe()
        return _lib_call(_orig_compose, self, beta)

    def compareTo(self: Any, other: Any) -> int:
        if other is None:
            _raise_npe()
        return int(self.compare_to(other))

    def hashCode(self: Any) -> int:
        fn = getattr(self, "hash_code", None)
        if callable(fn):
            return int(fn())
        ans = 1
        for x in toArray(self):
            ans = (ans * 31 + int(x)) & 0xFFFFFFFF
            if ans >= 0x80000000:
                ans -= 0x100000000
        return int(ans)

    def equals(self: Any, other: Any) -> bool:
        return self == other

    def toString(self: Any, kind_or_len: Any = None, max_len: Any = None) -> str:
        if kind_or_len is None and max_len is None:
            return str(self)
        if max_len is None and isinstance(kind_or_len, (int, bool)) and not isinstance(
            kind_or_len, bool
        ):
            return str(self.to_string_with_max_len(int(kind_or_len)))
        if isinstance(kind_or_len, bool):
            return str(self.to_string_with_max_len(int(kind_or_len)))
        pt = _lib_print_type(kind_or_len)
        ml = -1 if max_len is None else int(max_len)
        return str(self.to_string_with_type(pt, ml))

    def iterator(self: Any) -> Any:
        return iter(self)

    _PARTITION_PATCHES = {
        "universeSize": universeSize,
        "numberOfBlocks": numberOfBlocks,
        "isRelated": isRelated,
        "blockIndex": blockIndex,
        "getBlocks": getBlocks,
        "joinBlocks": joinBlocks,
        "join": join,
        "meet": meet,
        "leq": leq,
        "normalize": normalize,
        "isZero": isZero,
        "isUniform": isUniform,
        "isInitialLexRepresentative": isInitialLexRepresentative,
        "toArray": toArray,
        "getArray": getArray,
        "get": get,
        "getPairs": getPairs,
        "compose": compose,
        "compareTo": compareTo,
        "hashCode": hashCode,
        "equals": equals,
        "toString": toString,
        "iterator": iterator,
    }

    for camel, impl in _PARTITION_PATCHES.items():
        try:
            setattr(_LibPartition, camel, impl)
        except (TypeError, AttributeError):
            pass
    try:
        _LibPartition.leq = leq
    except (TypeError, AttributeError):
        pass
    try:
        _LibPartition.representative = representative
        _LibPartition.isRepresentative = isRepresentative
    except (TypeError, AttributeError):
        pass
    try:
        def _representatives(self: Any) -> list:
            return [int(x) for x in _orig_representatives(self)]

        _LibPartition.representatives = _representatives
    except (TypeError, AttributeError):
        pass
    try:
        def _rank(self: Any) -> int:
            return int(_orig_rank(self))

        _LibPartition.rank = _rank
    except (TypeError, AttributeError):
        pass

    class _PartitionMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            return isinstance(instance, _LibPartition)

    class Partition(object, metaclass=_PartitionMeta):
        """Java ``org.uacalc.alg.conlat.Partition`` surface."""

        PrintType = None

        def toArray(self):
            raise NotImplementedError

        def joinBlocks(self, r, s):
            raise NotImplementedError

        def join(self, part2):
            raise NotImplementedError

        def meet(self, part2):
            raise NotImplementedError

        def leq(self, part2):
            raise NotImplementedError

        def normalize(self):
            raise NotImplementedError

        def universeSize(self):
            raise NotImplementedError

        def numberOfBlocks(self):
            raise NotImplementedError

        def isRelated(self, i, j):
            raise NotImplementedError

        def toString(self, kind=None, max_len=None):
            raise NotImplementedError

        def representative(self, i):
            raise NotImplementedError

        def isRepresentative(self, i):
            raise NotImplementedError

        def representatives(self):
            raise NotImplementedError

        def blockIndex(self, i):
            raise NotImplementedError

        def getBlocks(self):
            raise NotImplementedError

        def isInitialLexRepresentative(self):
            raise NotImplementedError

        def isUniform(self):
            raise NotImplementedError

        def isZero(self):
            raise NotImplementedError

        def getPairs(self):
            raise NotImplementedError

        def compose(self, beta):
            raise NotImplementedError

    class _BPMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            return isinstance(instance, _LibPartition)

    class BasicPartition(object, metaclass=_BPMeta):
        """Jython ``BasicPartition`` constructors and static helpers."""

        PrintType = None

        def __new__(cls, part_or_str: Any = _MISSING, length: Any = _MISSING):
            if part_or_str is _MISSING and length is _MISSING:
                raise TypeError("BasicPartition() missing argument")
            if part_or_str is None or part_or_str is _MISSING:
                _raise_npe()
            if isinstance(part_or_str, (str, bytes)):
                text = str(part_or_str)
                if length is None or length is _MISSING:
                    arr = _lib_call(_LibPartition.string_to_partition, text, -1)
                else:
                    arr = _lib_call(_LibPartition.string_to_partition, text, int(length))
                if arr is None:
                    _raise_npe()
                return _lib_call(_LibPartition, list(arr))
            return _lib_call(_LibPartition, _as_int_list(part_or_str))

        @staticmethod
        def zero(asize):
            if asize is None:
                _raise_npe()
            return _LibPartition.zero(int(asize))

        @staticmethod
        def one(asize):
            if asize is None:
                _raise_npe()
            return _LibPartition.one(int(asize))

        @staticmethod
        def stringToPartition(str, length=-1):
            if str is None:
                _raise_npe()
            return _lib_call(_LibPartition.string_to_partition, str, int(length))

        @staticmethod
        def jbToPartition(a):
            if a is None:
                _raise_npe()
            return _lib_call(_LibPartition.jb_to_partition, _as_int_list(a))

        @staticmethod
        def permutabilityLevel(*args):
            if len(args) == 2:
                par0, par1 = args
                if par0 is None or par1 is None:
                    _raise_npe()
                return int(_lib_call(_LibPartition.permutability_level, par0, par1))
            if len(args) == 4:
                a, b, par0, par1 = args
                if par0 is None or par1 is None:
                    _raise_npe()
                return int(
                    _lib_call(_LibPartition.permutability_level, int(a), int(b), par0, par1)
                )
            raise TypeError("permutabilityLevel() takes 2 or 4 arguments")

        @staticmethod
        def leq(u, v=None):
            if v is None:
                # instance-style shouldn't land here
                raise TypeError("BasicPartition.leq(int[], int[]) requires two arrays")
            if u is None or v is None:
                _raise_npe()
            return bool(_LibPartition.leq_arrays(_as_int_list(u), _as_int_list(v)))

        @staticmethod
        def normalize(part):
            if part is None:
                _raise_npe()
            out = _lib_call(_LibPartition.normalize_array, _as_int_list(part))
            if isinstance(part, list):
                part[:] = list(out)
            return None

        @staticmethod
        def partToKissString(part):
            if part is None:
                _raise_npe()
            return str(_LibPartition.part_to_kiss_string(_as_int_list(part)))

        @staticmethod
        def directProduct(alpha, beta):
            if alpha is None or beta is None:
                _raise_npe()
            return _lib_call(_LibPartition.direct_product, alpha, beta)

        @staticmethod
        def unaryPolymorphisms(pars, report=None):
            if pars is None:
                _raise_npe()
            if report is not None:
                raise NotImplementedError(
                    "unaryPolymorphisms(..., ProgressReport) is not bound"
                )
            items = list(pars)
            if not items:
                raise IndexOutOfBoundsException("Index: 0, Size: 0")
            return _lib_call(_LibPartition.unary_polymorphisms, items)

        @staticmethod
        def binaryPolymorphisms(pars, unaryClone=None, report=None):
            if pars is None:
                _raise_npe()
            if report is not None:
                raise NotImplementedError(
                    "binaryPolymorphisms(..., ProgressReport) is not bound"
                )
            items = list(pars)
            if not items:
                raise IndexOutOfBoundsException("Index: 0, Size: 0")
            return _lib_call(_LibPartition.binary_polymorphisms, items)

        @staticmethod
        def unaryPolymorphismsAlgebra(pars, report=None):
            if pars is None:
                _raise_npe()
            if report is not None:
                raise NotImplementedError(
                    "unaryPolymorphismsAlgebra(..., ProgressReport) is not bound"
                )
            items = list(pars)
            if not items:
                raise IndexOutOfBoundsException("Index: 0, Size: 0")
            from org.uacalc.alg import BasicAlgebra
            from org.uacalc.alg.op import Operations

            univ_n = int(items[0].universeSize())
            polys = _lib_call(_LibPartition.unary_polymorphisms, items)
            ops = []
            for i, ia in enumerate(polys):
                arr = _as_int_list(ia)
                ops.append(Operations.makeIntOperation("f_" + str(i), 1, univ_n, arr))
            return BasicAlgebra("", univ_n, ops)

        @staticmethod
        def binaryPolymorphismsAlgebra(pars, report=None):
            if pars is None:
                _raise_npe()
            if report is not None:
                raise NotImplementedError(
                    "binaryPolymorphismsAlgebra(..., ProgressReport) is not bound"
                )
            items = list(pars)
            if not items:
                raise IndexOutOfBoundsException("Index: 0, Size: 0")
            from org.uacalc.alg import BasicAlgebra
            from org.uacalc.alg.op import Operations

            univ_n = int(items[0].universeSize())
            polys = _lib_call(_LibPartition.binary_polymorphisms, items)
            ops = []
            for i, ia in enumerate(polys):
                arr = _as_int_list(ia)
                ops.append(Operations.makeIntOperation("b_" + str(i), 2, univ_n, arr))
            return BasicAlgebra("", univ_n, ops)

        @staticmethod
        def isHereditary(pars):
            if pars is None:
                _raise_npe()
            alg = BasicPartition.unaryPolymorphismsAlgebra(pars)
            con_lat = alg.con()
            getter = getattr(con_lat, "getBasicLattice", None)
            if callable(getter):
                getter(True)
            return True

        @staticmethod
        def funcToJIs(n):
            # Java scans then returns null (the map is commented out).
            if n is None:
                _raise_npe()
            int(n)
            return None

        @staticmethod
        def joinClosure(pars, termMap=None, projkernel=None):
            if pars is None:
                _raise_npe()
            return _lib_call(_LibPartition.join_closure, list(pars))

        @staticmethod
        def meetClosure(pars, termMap=None):
            if pars is None:
                _raise_npe()
            return _lib_call(_LibPartition.meet_closure, list(pars))

        @staticmethod
        def subUniverseGenerated(gens, termMap=None, projkernel=None):
            if gens is None:
                _raise_npe()
            return _lib_call(_LibPartition.sub_universe_generated, list(gens))

        @staticmethod
        def partitionFromMatrix(matrix):
            if matrix is None:
                _raise_npe()
            rows = [list(r) for r in matrix]
            return _lib_call(_LibPartition.partition_from_matrix, rows)

        @staticmethod
        def firstProjection(n):
            if n is None:
                _raise_npe()
            return _lib_call(_LibPartition.first_projection, int(n))

        @staticmethod
        def secondProjection(n):
            if n is None:
                _raise_npe()
            return _lib_call(_LibPartition.second_projection, int(n))

        @staticmethod
        def from_string(str, length=None):
            if length is None:
                return BasicPartition(str)
            return BasicPartition(str, length)

    # --- CongruenceLattice ---
    _CL_MONITOR = [None]
    _CL_ALGEBRAS: dict = {}

    def _patch_conlat_instance_methods() -> None:
        if _LibCongruenceLattice is None:
            return

        def getName(self: Any) -> str:
            fn = getattr(self, "get_name", None)
            if callable(fn):
                return str(fn())
            name = getattr(self, "get_algebra_name", None)
            alg_name = str(name()) if callable(name) else "A"
            return "Con(" + alg_name + ")"

        def getTypeFinder(self: Any) -> Any:
            from org.uacalc.alg.conlat import TypeFinder as _TF

            alg = getAlgebra(self)
            if alg is None:
                raise TypeError("CongruenceLattice.getTypeFinder requires the originating algebra")
            return _TF(alg)

        _CL_ST_MAPS: dict = {}

        def getJoinIrredToSubtraceMap(self: Any) -> Any:
            key = id(self)
            m = _CL_ST_MAPS.get(key)
            if m is None:
                m = {}
                _CL_ST_MAPS[key] = m
            return m

        def subtrace(self: Any, beta: Any, alpha: Any = _MISSING) -> Any:
            if alpha is not _MISSING:
                # Java findJoinIrred NPEs if either argument is null.
                if beta is None or alpha is None:
                    _raise_npe()
                # Java subtrace(beta, alpha) calls findJoinIrred(beta, alpha).
                # That can be null (e.g. subtrace(one, zero) on a chain); the
                # 1-arg path then raises IAE from TypeFinder.findSubtrace.
                gamma = self.findJoinIrred(beta, alpha)
                return subtrace(self, gamma)
            smap = getJoinIrredToSubtraceMap(self)
            st = smap.get(beta)
            if st is None:
                st = getTypeFinder(self).findSubtrace(beta)
                try:
                    smap[beta] = st
                except TypeError:
                    smap[id(beta)] = st
            return st

        def typeJI(self: Any, beta: Any, report: Any = None) -> int:
            if report is not None:
                raise TypeError(
                    "typeJI(): expected org.uacalc.ui.tm.ProgressReport or None"
                )
            # Java HashMap.get(null) then subtrace(null) → IAE from findSubtrace.
            smap = getJoinIrredToSubtraceMap(self)
            st = smap.get(beta)
            if st is None:
                st = subtrace(self, beta)
            t = int(st.type()) if st is not None and hasattr(st, "type") else 0
            if t <= 0:
                t = int(getTypeFinder(self).findType(st if _is_subtrace(st) else beta))
            return t

        def typeSet(self: Any, report: Any = None) -> Any:
            if report is not None:
                raise TypeError(
                    "typeSet(): expected org.uacalc.ui.tm.ProgressReport or None"
                )
            return set(getTypeFinder(self).findTypeSet())

        def type_cong(self: Any, beta: Any, alpha: Any = _MISSING) -> int:
            if beta is None:
                _raise_npe()
            if alpha is not _MISSING:
                if alpha is None:
                    _raise_npe()
                # Java type(beta, alpha) calls findJoinIrred(alpha, beta).
                gamma = self.findJoinIrred(alpha, beta)
                return typeJI(self, gamma)
            return typeJI(self, beta)

        def getAlgebra(self: Any) -> Any:
            alg = _CL_ALGEBRAS.get(id(self)) or getattr(
                self, "_uacalc_algebra", None
            )
            if alg is not None:
                return alg
            try:
                from org.uacalc import alg as _alg_mod

                store = getattr(_alg_mod, "_CON_ALGEBRAS", None)
                if isinstance(store, dict):
                    return store.get(id(self))
            except Exception:
                pass
            return None

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

        def upperCoversMap(self: Any) -> dict:
            pairs = self.upper_covers_map()
            return {k: list(v) for k, v in pairs}

        def makePrincipals(self: Any, report: Any = None) -> None:
            if report is not None:
                raise NotImplementedError("makePrincipals(ProgressReport) is not bound")
            self.make_principals()

        def makeJoinIrreducibles(self: Any, report: Any = None) -> None:
            if report is not None:
                raise NotImplementedError("makeJoinIrreducibles(ProgressReport) is not bound")
            self.make_join_irreducibles()

        def getPermutabilityLevelWitnesses(self: Any) -> Any:
            fn = getattr(self, "get_permutability_level_witnesses", None)
            if not callable(fn):
                return None
            w = fn()
            if w is None:
                return None
            return list(w)

        def setName(self: Any, v: Any) -> None:
            raise UnsupportedOperationException()

        def getDescription(self: Any) -> str:
            return str(self.get_description())

        def setDescription(self: Any, desc: Any) -> None:
            self.set_description(None if desc is None else str(desc))

        def isTotal(self: Any) -> bool:
            return True

        def isUnary(self: Any) -> bool:
            return False

        def isIdempotent(self: Any) -> bool:
            return True

        def operations(self: Any) -> Any:
            # Java CongruenceLattice.operations() is identically null.
            return None

        def getOperation(self: Any, sym: Any) -> Any:
            return None

        def getOperationsMap(self: Any) -> Any:
            return None

        def constantOperations(self: Any) -> list:
            return []

        def makeOperationTables(self: Any) -> None:
            return None

        def universe(self: Any, report: Any = None) -> list:
            if report is not None:
                raise NotImplementedError("universe(ProgressReport) is not bound")
            return list(self.universe())

        def getUniverseList(self: Any) -> list:
            fn = getattr(self, "get_universe_list", None)
            if callable(fn):
                return list(fn())
            return list(self.universe())

        def iterator(self: Any) -> Any:
            return iter(getUniverseList(self))

        def Cg(self: Any, a: Any, b: Any = None, report: Any = None) -> Any:
            if report is not None:
                raise NotImplementedError("Cg(..., ProgressReport) is not bound")
            if b is None:
                if a is None:
                    _raise_npe()
                fn = getattr(self, "cg_partition", None)
                if callable(fn):
                    return fn(a)
                raise NotImplementedError("Cg(Partition) is not bound")
            return _lib_call(self.cg, int(a), int(b))

        def Tg(self: Any, a: Any, b: Any) -> Any:
            return _lib_call(self.tg, int(a), int(b))

        def join(self: Any, a: Any, b: Any = None) -> Any:
            if b is None:
                if a is None:
                    _raise_npe()
                acc = self.zero()
                for p in list(a):
                    acc = acc.join(p)
                return acc
            if a is None or b is None:
                _raise_npe()
            fn = getattr(self, "lattice_join", None)
            if callable(fn):
                return fn(a, b)
            return a.join(b)

        def meet(self: Any, a: Any, b: Any = None) -> Any:
            if b is None:
                if a is None:
                    _raise_npe()
                acc = self.one()
                for p in list(a):
                    acc = acc.meet(p)
                return acc
            if a is None or b is None:
                _raise_npe()
            fn = getattr(self, "lattice_meet", None)
            if callable(fn):
                return fn(a, b)
            return a.meet(b)

        def leq(self: Any, a: Any, b: Any) -> bool:
            if a is None or b is None:
                _raise_npe()
            fn = getattr(self, "lattice_leq", None)
            if callable(fn):
                return bool(fn(a, b))
            return bool(a.leq(b))

        def coatoms(self: Any) -> Any:
            raise UnsupportedOperationException("Not implemented yet.")

        def setMonitor(self: Any, monitor: Any) -> None:
            if monitor is not None:
                raise TypeError(
                    "setMonitor(): expected org.uacalc.ui.tm.ProgressReport or None"
                )
            _CL_MONITOR[0] = None

        def getMonitor(self: Any) -> Any:
            return _CL_MONITOR[0]

        def monitoring(self: Any) -> bool:
            return _CL_MONITOR[0] is not None

        def getBasicLattice(self: Any, makeIfNull: Optional[bool] = None) -> Any:
            if makeIfNull is None:
                return self.get_basic_lattice(True)
            return self.get_basic_lattice(bool(makeIfNull))

        _CL_PATCHES = {
            "getName": getName,
            "getAlgebra": getAlgebra,
            "similarityType": similarityType,
            "isSimilarTo": isSimilarTo,
            "updateSimilarityType": updateSimilarityType,
            "upperCoversMap": upperCoversMap,
            "getPermutabilityLevelWitnesses": getPermutabilityLevelWitnesses,
            "setName": setName,
            "getDescription": getDescription,
            "setDescription": setDescription,
            "isTotal": isTotal,
            "isUnary": isUnary,
            "isIdempotent": isIdempotent,
            "operations": operations,
            "getOperation": getOperation,
            "getOperationsMap": getOperationsMap,
            "constantOperations": constantOperations,
            "makeOperationTables": makeOperationTables,
            "getUniverseList": getUniverseList,
            "iterator": iterator,
            "Cg": Cg,
            "Tg": Tg,
            "join": join,
            "meet": meet,
            "leq": leq,
            "coatoms": coatoms,
            "setMonitor": setMonitor,
            "getMonitor": getMonitor,
            "monitoring": monitoring,
            "getBasicLattice": getBasicLattice,
            "joinIrreducibles": lambda self: list(self.join_irreducibles()),
            "joinIrreduciblesFound": lambda self: bool(self.join_irreducibles_found()),
            "meetIrreducibles": lambda self: list(self.meet_irreducibles()),
            "principals": lambda self, _orig=_LibCongruenceLattice.principals: list(_orig(self)),
            "atoms": lambda self, _orig=_LibCongruenceLattice.atoms: list(_orig(self)),
            "isDistributive": lambda self: bool(self.is_distributive()),
            "complements": lambda self, p, _orig=_LibCongruenceLattice.complements: list(_orig(self, p)),
            "generatingPair": lambda self, p: self.generating_pair(p),
            "findCoatomAbove": lambda self, p: self.find_coatom_above(p),
            "findJoinIrred": lambda self, a, b: self.find_join_irred(a, b),
            "findMeetIrred": lambda self, a, b: self.find_meet_irred(a, b),
            "findPrincipalChain": lambda self: list(self.find_principal_chain()),
            "findUpperCover": lambda self, c: self.find_upper_cover(c),
            "irredundantMeetDecomposition": lambda self: list(
                self.irredundant_meet_decomposition()
            ),
            "permutabilityLevel": lambda self: int(self.permutability_level()),
            "Delta": lambda self, a, b: self.delta(a, b),
            "commutator2": lambda self, a, b, _orig=_LibCongruenceLattice.commutator2: _orig(self, a, b),
            "centralizes": lambda self, s, t, d, _orig=_LibCongruenceLattice.centralizes: bool(
                _orig(self, s, t, d)
            ),
            "matrices": lambda self, s, t, report=None, _orig=getattr(
                _LibCongruenceLattice, "matrices", None
            ): _orig(self, s, t),
            "commutator": lambda self, s, t, _orig=getattr(
                _LibCongruenceLattice, "commutator", None
            ): _orig(self, s, t),
            "weakCommutator": lambda self, s, t, _orig=getattr(
                _LibCongruenceLattice, "weak_commutator", None
            ): _orig(self, s, t),
            "strongRectangularityCommutator": lambda self, s, t, _orig=getattr(
                _LibCongruenceLattice, "strong_rectangularity_commutator", None
            ): _orig(self, s, t),
            "centralityFailure": lambda self, s, t, d, _orig=getattr(
                _LibCongruenceLattice, "centrality_failure", None
            ): _orig(self, s, t, d),
            "weakCentralityFailure": lambda self, s, t, d, _orig=getattr(
                _LibCongruenceLattice, "weak_centrality_failure", None
            ): _orig(self, s, t, d),
            "strongRectangularityFailure": lambda self, s, t, d, _orig=getattr(
                _LibCongruenceLattice, "strong_rectangularity_failure", None
            ): _orig(self, s, t, d),
            "calcCentrality": lambda self, s, t, report=None, _orig=getattr(
                _LibCongruenceLattice, "calc_centrality", None
            ): _orig(self, s, t),
            "idempotentPolynomials": lambda self: list(self.idempotent_polynomials()),
            "joinIrreducible": lambda self, p: bool(self.join_irreducible(p)),
            "meetIrreducible": lambda self, p: bool(self.meet_irreducible(p)),
            "joinPrime": lambda self, p: bool(self.join_prime(p)),
            "lowerStar": lambda self, p: self.lower_star(p),
            "isSmallerThan": lambda self, n: bool(self.is_smaller_than(int(n))),
            "isDrawable": lambda self: bool(self.is_drawable()),
            "universeFound": lambda self: bool(self.universe_found()),
            "makeUniverse": lambda self: self.make_universe(),
            "makePrincipals": makePrincipals,
            "makeAtoms": lambda self: self.make_atoms(),
            "makeJoinIrreducibles": makeJoinIrreducibles,
            "inputSize": lambda self: int(self.input_size()),
            "algSize": lambda self: int(self.alg_size()),
            "typeJI": typeJI,
            "typeSet": typeSet,
            "type": type_cong,
            "subtrace": subtrace,
            "getTypeFinder": getTypeFinder,
            "getJoinIrredToSubtraceMap": getJoinIrredToSubtraceMap,
        }
        for camel, impl in _CL_PATCHES.items():
            try:
                setattr(_LibCongruenceLattice, camel, impl)
            except (TypeError, AttributeError):
                pass
        try:
            _LibCongruenceLattice.__iter__ = iterator
        except (TypeError, AttributeError):
            pass

        try:
            _orig_univ = _LibCongruenceLattice.universe

            def _universe(self: Any, report: Any = None, _orig=_orig_univ) -> list:
                if report is not None:
                    raise NotImplementedError("universe(ProgressReport) is not bound")
                return list(_orig(self))

            _LibCongruenceLattice.universe = _universe
        except (TypeError, AttributeError):
            pass

        try:
            _LibCongruenceLattice.MAX_DRAWABLE_SIZE = 150
            _LibCongruenceLattice.MAX_DRAWABLE_INPUT_SIZE = 2500
        except (TypeError, AttributeError):
            pass

        try:
            _LibCongruenceLattice.minimalElements = staticmethod(
                _LibCongruenceLattice.minimal_elements
            )
        except (TypeError, AttributeError):
            pass

    _patch_conlat_instance_methods()

    class _CLMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            return isinstance(instance, _LibCongruenceLattice) if _LibCongruenceLattice else False

    class CongruenceLattice(object, metaclass=_CLMeta):
        MAX_DRAWABLE_SIZE = 150
        MAX_DRAWABLE_INPUT_SIZE = 2500

        def __new__(cls, alg: Any):
            if alg is None:
                _raise_npe(
                    'Cannot invoke "org.uacalc.alg.SmallAlgebra.cardinality()" '
                    'because "alg" is null'
                )
            if _LibCongruenceLattice is None:
                raise TypeError("CongruenceLattice is not bound")
            inner = getattr(alg, "_inner", alg)
            obj = _LibCongruenceLattice(inner)
            _CL_ALGEBRAS[id(obj)] = alg
            return obj

        @staticmethod
        def minimalElements(pars):
            if pars is None:
                _raise_npe()
            if _LibCongruenceLattice is None:
                raise TypeError("CongruenceLattice is not bound")
            return list(_LibCongruenceLattice.minimal_elements(list(pars)))

    def _as_int_array(obj: Any) -> Any:
        if obj is None:
            _raise_npe()
        from org.uacalc.util import IntArray

        if isinstance(obj, IntArray):
            return obj
        tname = type(obj).__name__
        if tname in ("PyIntArray", "IntArray"):
            return obj
        try:
            return IntArray([int(x) for x in list(obj)])
        except TypeError:
            return obj

    def _int_row(row: Any) -> list:
        if row is None:
            _raise_npe()
        for attr in ("getArray", "get_array", "toArray", "to_array"):
            fn = getattr(row, attr, None)
            if callable(fn):
                try:
                    return [int(x) for x in fn()]
                except TypeError:
                    continue
        getter = getattr(row, "get", None)
        if callable(getter):
            try:
                n = int(row.universeSize()) if hasattr(row, "universeSize") else None
            except Exception:
                n = None
            if n is None:
                length = getattr(row, "length", None)
                n = int(length() if callable(length) else length) if length is not None else None
            if n is not None:
                return [int(getter(i)) for i in range(n)]
            try:
                return [int(getter(0)), int(getter(1))]
            except Exception:
                pass
        try:
            return [int(x) for x in list(row)]
        except TypeError as exc:
            raise TypeError(str(exc)) from exc

    def _pair_ij(pair: Any) -> tuple:
        seq = _int_row(pair)
        return int(seq[0]), int(seq[1])

    def _is_partition(obj: Any) -> bool:
        if obj is None:
            return False
        return any(
            hasattr(obj, name)
            for name in ("joinBlocks", "join_blocks", "numberOfBlocks", "number_of_blocks")
        )

    def _is_subtrace(obj: Any) -> bool:
        if obj is None:
            return False
        return any(
            hasattr(obj, name) for name in ("hasInvolution", "has_involution", "setType", "set_type")
        )

    def _pairs_to_intarrays(pairs: Any) -> list:
        from org.uacalc.util import IntArray

        out = []
        for p in list(pairs or []):
            if isinstance(p, IntArray) or type(p).__name__ in ("PyIntArray", "IntArray"):
                out.append(p)
            else:
                out.append(IntArray([int(x) for x in list(p)]))
        return out

    def _bbr_to_string(pairs: Any) -> str:
        items = _pairs_to_intarrays(pairs)
        return "[" + ", ".join(str(p) for p in items) + "]"

    # --- BasicBinaryRelation ---
    _LibBBR = conlat_globals.get("BasicBinaryRelation")
    _BBR_STATE: dict = {}

    def _patch_bbr() -> None:
        if _LibBBR is None:
            return

        _orig_add = getattr(_LibBBR, "add", None)
        _orig_compose = getattr(_LibBBR, "compose", None)
        _orig_get_pairs = getattr(_LibBBR, "get_pairs", None) or getattr(_LibBBR, "getPairs", None)
        _orig_is_related = getattr(_LibBBR, "is_related", None)
        _orig_universe_size = getattr(_LibBBR, "universe_size", None)
        _orig_is_reflexive = getattr(_LibBBR, "is_reflexive", None)
        _orig_is_symmetric = getattr(_LibBBR, "is_symmetric", None)
        _orig_identity = getattr(_LibBBR, "identity", None)

        def getPairs(self: Any) -> list:
            return _pairs_to_intarrays(_orig_get_pairs(self) if callable(_orig_get_pairs) else [])

        def universeSize(self: Any) -> int:
            return int(_orig_universe_size(self) if callable(_orig_universe_size) else self.universe_size())

        def isRelated(self: Any, i: Any, j: Any) -> bool:
            if i is None or j is None:
                _raise_npe()
            if callable(_orig_is_related):
                return bool(_orig_is_related(self, int(i), int(j)))
            return bool(self.is_related(int(i), int(j)))

        def add(self: Any, i: Any, j: Any) -> None:
            if i is None or j is None:
                _raise_npe()
            _lib_call(_orig_add, self, int(i), int(j))

        def compose(self: Any, beta: Any) -> Any:
            if beta is None:
                _raise_npe()
            return _lib_call(_orig_compose, self, beta)

        def compareTo(self: Any, other: Any) -> int:
            if other is None:
                _raise_npe()
            getter = getattr(other, "getPairs", None) or getattr(other, "get_pairs", None)
            other_pairs = list(getter()) if callable(getter) else list(other)
            return len(getPairs(self)) - len(other_pairs)

        def isReflexive(self: Any) -> bool:
            return bool(_orig_is_reflexive(self) if callable(_orig_is_reflexive) else self.is_reflexive())

        def isSymmetric(self: Any) -> bool:
            return bool(_orig_is_symmetric(self) if callable(_orig_is_symmetric) else self.is_symmetric())

        def iterator(self: Any) -> Any:
            return iter(getPairs(self))

        def toString(self: Any) -> str:
            return _bbr_to_string(getPairs(self))

        def equals(self: Any, other: Any) -> bool:
            return self == other

        _BBR_PATCHES = {
            "getPairs": getPairs,
            "universeSize": universeSize,
            "isRelated": isRelated,
            "add": add,
            "compose": compose,
            "compareTo": compareTo,
            "isReflexive": isReflexive,
            "isSymmetric": isSymmetric,
            "iterator": iterator,
            "toString": toString,
            "equals": equals,
        }
        for camel, impl in _BBR_PATCHES.items():
            try:
                setattr(_LibBBR, camel, impl)
            except (TypeError, AttributeError):
                pass
        try:
            _LibBBR.__str__ = toString
            _LibBBR.__iter__ = iterator
        except (TypeError, AttributeError):
            pass

        if callable(_orig_identity):
            try:
                _LibBBR.identity = staticmethod(_orig_identity)
            except (TypeError, AttributeError):
                pass

    _patch_bbr()

    class _BBRMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            return isinstance(instance, _LibBBR) if _LibBBR else False

    class _BRMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            if _LibBBR is not None and isinstance(instance, _LibBBR):
                return True
            if _LibPartition is not None and isinstance(instance, _LibPartition):
                return True
            return False

    class BinaryRelation(object, metaclass=_BRMeta):
        """Java ``org.uacalc.alg.conlat.BinaryRelation`` surface."""

        def universeSize(self):
            raise NotImplementedError

        def isRelated(self, i, j):
            raise NotImplementedError

        def getPairs(self):
            raise NotImplementedError

        def compose(self, beta):
            raise NotImplementedError

    class BasicBinaryRelation(object, metaclass=_BBRMeta):
        """Java ``BasicBinaryRelation`` constructors and static identity."""

        def __new__(cls, univ_or_coll: Any = _MISSING, univSize: Any = _MISSING):
            if _LibBBR is None:
                raise TypeError("BasicBinaryRelation is not bound")
            if univ_or_coll is _MISSING and univSize is _MISSING:
                raise TypeError("BasicBinaryRelation() missing argument")
            if univSize is _MISSING:
                if univ_or_coll is None:
                    _raise_npe()
                return _lib_call(_LibBBR, int(univ_or_coll))
            if univSize is None:
                _raise_npe()
            obj = _lib_call(_LibBBR, int(univSize))
            if univ_or_coll is None:
                _raise_npe()
            for pair in list(univ_or_coll):
                i, j = _pair_ij(pair)
                obj.add(i, j)
            return obj

        @staticmethod
        def identity(size):
            if size is None:
                _raise_npe()
            if _LibBBR is None:
                raise TypeError("BasicBinaryRelation is not bound")
            return _lib_call(_LibBBR.identity, int(size))

        def universeSize(self):
            raise NotImplementedError

        def isRelated(self, i, j):
            raise NotImplementedError

        def getPairs(self):
            raise NotImplementedError

        def compose(self, beta):
            raise NotImplementedError

        def add(self, i, j):
            raise NotImplementedError

        def compareTo(self, other):
            raise NotImplementedError

        def isReflexive(self):
            raise NotImplementedError

        def isSymmetric(self):
            raise NotImplementedError

        def iterator(self):
            raise NotImplementedError

        def toString(self):
            raise NotImplementedError

    # --- Subtrace ---
    _LibSubtrace = conlat_globals.get("Subtrace")

    def _patch_subtrace() -> None:
        if _LibSubtrace is None:
            return
        _orig_has_inv = getattr(_LibSubtrace, "has_involution", None)
        _orig_get_su = getattr(_LibSubtrace, "get_subtrace_universe", None)
        _orig_set_su = getattr(_LibSubtrace, "set_subtrace_universe", None)
        _orig_get_mu = getattr(_LibSubtrace, "get_matrix_universe", None)
        _orig_set_mu = getattr(_LibSubtrace, "set_matrix_universe", None)
        _orig_set_type = getattr(_LibSubtrace, "set_type", None)
        _orig_brief = getattr(_LibSubtrace, "to_string_brief", None)

        def hasInvolution(self: Any) -> bool:
            return bool(_orig_has_inv(self) if callable(_orig_has_inv) else self.has_involution())

        def getSubtraceUniverse(self: Any) -> Any:
            univ = _orig_get_su(self) if callable(_orig_get_su) else None
            if univ is None:
                return None
            return _pairs_to_intarrays(univ)

        def setSubtraceUniverse(self: Any, univ: Any) -> None:
            if univ is None:
                _lib_call(_orig_set_su, self, [])
                return
            rows = [_int_row(row) for row in list(univ)]
            _lib_call(_orig_set_su, self, rows)

        def getMatrixUniverse(self: Any) -> Any:
            univ = _orig_get_mu(self) if callable(_orig_get_mu) else None
            if univ is None:
                return None
            return _pairs_to_intarrays(univ)

        def setMatrixUniverse(self: Any, univ: Any) -> None:
            if univ is None:
                _lib_call(_orig_set_mu, self, [])
                return
            rows = [_int_row(row) for row in list(univ)]
            _lib_call(_orig_set_mu, self, rows)

        def setType(self: Any, t: Any) -> None:
            _orig_set_type(self, int(t))

        def toString(self: Any, brief: Any = None) -> str:
            if brief is None:
                return str(self)
            if callable(_orig_brief):
                return str(_orig_brief(self, bool(brief)))
            if brief:
                return "[{0}, {1}]".format(self.first(), self.second())
            return str(self)

        _ST_PATCHES = {
            "hasInvolution": hasInvolution,
            "getSubtraceUniverse": getSubtraceUniverse,
            "setSubtraceUniverse": setSubtraceUniverse,
            "getMatrixUniverse": getMatrixUniverse,
            "setMatrixUniverse": setMatrixUniverse,
            "setType": setType,
            "toString": toString,
        }
        for camel, impl in _ST_PATCHES.items():
            try:
                setattr(_LibSubtrace, camel, impl)
            except (TypeError, AttributeError):
                pass

    _patch_subtrace()

    class _SubtraceMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            return isinstance(instance, _LibSubtrace) if _LibSubtrace else False

    class Subtrace(object, metaclass=_SubtraceMeta):
        def __new__(cls, a: Any, b: Any, inv: Any, type_value: Any = _MISSING):
            if _LibSubtrace is None:
                raise TypeError("Subtrace is not bound")
            if a is None or b is None:
                _raise_npe()
            if type_value is _MISSING:
                return _LibSubtrace(int(a), int(b), bool(inv))
            return _LibSubtrace.new_with_type(int(a), int(b), bool(inv), int(type_value))

        def first(self):
            raise NotImplementedError

        def second(self):
            raise NotImplementedError

        def type(self):
            raise NotImplementedError

        def hasInvolution(self):
            raise NotImplementedError

        def getSubtraceUniverse(self):
            raise NotImplementedError

        def setSubtraceUniverse(self, univ):
            raise NotImplementedError

        def getMatrixUniverse(self):
            raise NotImplementedError

        def setMatrixUniverse(self, univ):
            raise NotImplementedError

        def setType(self, t):
            raise NotImplementedError

        def toString(self, brief=None):
            raise NotImplementedError

    # --- Polymorphisms ---
    _LibPoly = conlat_globals.get("Polymorphisms")

    class _PolyMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            return isinstance(instance, _LibPoly) if _LibPoly else False

    class Polymorphisms(object, metaclass=_PolyMeta):
        def __new__(cls, arity: Any, pars: Any, idempotent: Any, fixedValues: Any = None):
            if _LibPoly is None:
                raise TypeError("Polymorphisms is not bound")
            if pars is None:
                _raise_npe()
            items = list(pars)
            if not items:
                raise IndexOutOfBoundsException("Index: 0, Size: 0")
            fv = None if fixedValues is None else [int(x) for x in list(fixedValues)]
            return _lib_call(_LibPoly, int(arity), items, bool(idempotent), fv)

        def make_graph(self):
            raise NotImplementedError

    def _patch_poly() -> None:
        if _LibPoly is None:
            return

        def make_graph(self: Any) -> None:
            _lib_call(self.make_graph)

        try:
            _LibPoly.make_graph = make_graph
        except (TypeError, AttributeError):
            pass

    _patch_poly()

    # --- CentralityData ---
    _LibCD = conlat_globals.get("CentralityData")
    _CD_FAIL: dict = {}

    def _cd_fail(self: Any) -> dict:
        slot = _CD_FAIL.get(id(self))
        if slot is None or slot[0] is not self:
            slot = (self, {})
            _CD_FAIL[id(self)] = slot
        return slot[1]

    def _patch_cd() -> None:
        if _LibCD is None:
            return
        _orig_left = getattr(_LibCD, "left", None)
        _orig_right = getattr(_LibCD, "right", None)
        _orig_delta = getattr(_LibCD, "delta", None)
        _orig_compare = getattr(_LibCD, "compare_to", None)

        def getLeft(self: Any) -> Any:
            return _orig_left(self) if callable(_orig_left) else self.left()

        def getRight(self: Any) -> Any:
            return _orig_right(self) if callable(_orig_right) else self.right()

        def getDelta(self: Any) -> Any:
            return _orig_delta(self) if callable(_orig_delta) else self.delta()

        def compareTo(self: Any, other: Any) -> int:
            if other is None:
                _raise_npe()
            if callable(_orig_compare):
                return int(_orig_compare(self, other))
            return int(getDelta(self).compareTo(other.getDelta()))

        def setCentralityFailure(self: Any, failure: Any) -> None:
            _cd_fail(self)["centrality"] = failure

        def getCentralityFailure(self: Any) -> Any:
            return _cd_fail(self).get("centrality")

        def setWeakCentralityFailure(self: Any, failure: Any) -> None:
            _cd_fail(self)["weak"] = failure

        def getWeakCentralityFailure(self: Any) -> Any:
            return _cd_fail(self).get("weak")

        def setStrongRectangularityFailure(self: Any, failure: Any) -> None:
            _cd_fail(self)["strong"] = failure

        def getStrongRectangularityFailure(self: Any) -> Any:
            return _cd_fail(self).get("strong")

        def toString(self: Any) -> str:
            left = getLeft(self)
            right = getRight(self)
            delta = getDelta(self)
            left_fn = getattr(left, "toString", None)
            right_fn = getattr(right, "toString", None)
            left_s = str(left_fn()) if callable(left_fn) else str(left)
            right_s = str(right_fn()) if callable(right_fn) else str(right)

            def _java_null(obj: Any) -> str:
                return "null" if obj is None else str(obj)

            return (
                "left: {0}, right: {1}, delta: {2}, centralityFailure: {3}, "
                "weakCentralityFailure: {4}, strongRectangularityFailure: {5}"
            ).format(
                left_s,
                right_s,
                delta,
                _java_null(getCentralityFailure(self)),
                _java_null(getWeakCentralityFailure(self)),
                _java_null(getStrongRectangularityFailure(self)),
            )

        _CD_PATCHES = {
            "getLeft": getLeft,
            "getRight": getRight,
            "getDelta": getDelta,
            "compareTo": compareTo,
            "setCentralityFailure": setCentralityFailure,
            "getCentralityFailure": getCentralityFailure,
            "setWeakCentralityFailure": setWeakCentralityFailure,
            "getWeakCentralityFailure": getWeakCentralityFailure,
            "setStrongRectangularityFailure": setStrongRectangularityFailure,
            "getStrongRectangularityFailure": getStrongRectangularityFailure,
            "toString": toString,
        }
        for camel, impl in _CD_PATCHES.items():
            try:
                setattr(_LibCD, camel, impl)
            except (TypeError, AttributeError):
                pass
        try:
            _LibCD.__str__ = toString
        except (TypeError, AttributeError):
            pass

    _patch_cd()

    class _CDMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            return isinstance(instance, _LibCD) if _LibCD else False

    class CentralityData(object, metaclass=_CDMeta):
        def __new__(cls, left: Any, right: Any, delta: Any):
            if _LibCD is None:
                raise TypeError("CentralityData is not bound")
            if left is None or right is None or delta is None:
                _raise_npe()
            return _lib_call(_LibCD, left, right, delta)

        def compareTo(self, other):
            raise NotImplementedError

        def getLeft(self):
            raise NotImplementedError

        def getRight(self):
            raise NotImplementedError

        def getDelta(self):
            raise NotImplementedError

        def setCentralityFailure(self, failure):
            raise NotImplementedError

        def getCentralityFailure(self):
            raise NotImplementedError

        def setWeakCentralityFailure(self, failure):
            raise NotImplementedError

        def getWeakCentralityFailure(self):
            raise NotImplementedError

        def setStrongRectangularityFailure(self, failure):
            raise NotImplementedError

        def getStrongRectangularityFailure(self):
            raise NotImplementedError

        def toString(self):
            raise NotImplementedError

    # --- TypeFinder ---
    _LibTF = conlat_globals.get("TypeFinder")

    def _tf_alg(alg: Any) -> Any:
        if alg is None:
            _raise_npe(
                'Cannot invoke "org.uacalc.alg.SmallAlgebra.cardinality()" because "alg" is null'
            )
        inner = getattr(alg, "_inner", alg)
        conv = getattr(inner, "to_basic_algebra", None) or getattr(alg, "to_basic_algebra", None)
        tname = type(inner).__name__
        if tname not in ("PyBasicAlgebra", "BasicAlgebra") and callable(conv):
            return conv()
        return inner

    class TypeFinder(object):
        printSubtrace = False

        def __init__(self, alg: Any, alpha: Any = _MISSING) -> None:
            if _LibTF is None:
                raise TypeError("TypeFinder is not bound")
            self._alg = alg
            self._inner = _lib_call(_LibTF, _tf_alg(alg))
            if alpha is not _MISSING and alpha is not None:
                self._alpha = alpha
                _lib_call(self._inner.init_with_alpha, alpha)
            else:
                self._alpha = alg.con().zero() if alg is not None else None

        def init(self, alpha: Any = None) -> None:
            if alpha is None:
                self._alpha = self._alg.con().zero()
                _lib_call(self._inner.init)
            else:
                self._alpha = alpha
                _lib_call(self._inner.init_with_alpha, alpha)

        def findTypeSet(self) -> Any:
            return _lib_call(self._inner.find_type_set)

        def isSubtrace(self, ia: Any, beta: Any) -> bool:
            if ia is None or beta is None:
                _raise_npe()
            return bool(_lib_call(self._inner.is_subtrace, _as_int_array(ia), beta))

        def findSubtrace(self, first: Any, second: Any = _MISSING) -> Any:
            # Java findSubtrace(Partition) goes through lowerStar; a null beta
            # is not join irreducible ("beta = null is not join irreducible").
            if first is None:
                raise IllegalArgumentException(
                    "beta = null is not join irreducible"
                )
            if second is not _MISSING:
                if second is None:
                    _raise_npe()
                return _lib_call(self._inner.find_subtrace_with_alpha, first, second)
            if _is_partition(first):
                return _lib_call(self._inner.find_subtrace, first)
            return _lib_call(self._inner.find_subtrace_from_pair, _as_int_array(first))

        def findType(self, first: Any, second: Any = _MISSING) -> int:
            if first is None:
                _raise_npe()
            if second is not _MISSING:
                if second is None:
                    _raise_npe()
                return int(_lib_call(self._inner.find_type_with_alpha, first, second))
            if _is_subtrace(first):
                return int(_lib_call(self._inner.find_type_from_subtrace, first))
            return int(_lib_call(self._inner.find_type, first))

        def nextPairForSubtrace(self, pair, univHS, unorderedUnivHS, univ):
            if pair is None or univHS is None or unorderedUnivHS is None or univ is None:
                _raise_npe()
            from org.uacalc.alg import BigProductAlgebra
            from org.uacalc.util import IntArray, SequenceGenerator

            def _vals(ia: Any) -> list:
                getter = getattr(ia, "getArray", None) or getattr(ia, "to_array", None)
                if callable(getter):
                    return [int(x) for x in getter()]
                return [int(x) for x in list(ia)]

            def _key(ia: Any):
                return tuple(_vals(ia))

            def _set_add(coll: Any, ia: Any) -> bool:
                k = _key(ia)
                for item in list(coll):
                    if _key(item) == k:
                        return False
                coll.add(ia)
                return True

            def _list_add(coll: Any, ia: Any) -> None:
                adder = getattr(coll, "add", None)
                if callable(adder):
                    adder(ia)
                    return
                coll.append(ia)

            univHS.clear()
            _list_add(univ, pair)
            n = int(self._inner.alg_size())
            for i in range(n):
                _list_add(univ, IntArray([i, i]))
            for ia in list(univ):
                _set_add(univHS, ia)

            alpha = self._alpha
            if alpha is None:
                alpha = self._alg.con().zero()
            squared = BigProductAlgebra(self._alg, 2)
            closed_mark = 0
            current_mark = len(univ)
            while closed_mark < current_mark:
                for f in squared.operations():
                    arity = int(f.arity())
                    if arity == 0:
                        continue
                    arg_indices = [0] * arity
                    arg_indices[arity - 1] = closed_mark
                    inc = SequenceGenerator.sequenceIncrementor(
                        arg_indices, current_mark - 1, closed_mark
                    )
                    while True:
                        args = []
                        for j in range(arity):
                            args.append(_vals(univ[arg_indices[j]]))
                        v_raw = f.valueAt(args)
                        v_list = _vals(v_raw) if not isinstance(v_raw, list) else [
                            int(x) for x in v_raw
                        ]
                        v = IntArray(list(v_list))
                        v0, v1 = int(v_list[0]), int(v_list[1])
                        if not alpha.isRelated(v0, v1):
                            if v0 < v1:
                                v_unordered = IntArray([v0, v1])
                            else:
                                v_unordered = IntArray([v1, v0])
                            if _set_add(unorderedUnivHS, v_unordered):
                                return v
                            if _set_add(univHS, v):
                                _list_add(univ, v)
                        if not inc.increment():
                            break
                closed_mark = current_mark
                current_mark = len(univ)
            return None

        def algSize(self) -> int:
            return int(self._inner.alg_size())

    Partition.PrintType = PrintType
    BasicPartition.PrintType = PrintType

    conlat_globals["PrintType"] = PrintType
    conlat_globals["Partition"] = Partition
    conlat_globals["BasicPartition"] = BasicPartition
    conlat_globals["CongruenceLattice"] = CongruenceLattice
    conlat_globals["BinaryRelation"] = BinaryRelation
    conlat_globals["BasicBinaryRelation"] = BasicBinaryRelation
    conlat_globals["Subtrace"] = Subtrace
    conlat_globals["Polymorphisms"] = Polymorphisms
    conlat_globals["CentralityData"] = CentralityData
    conlat_globals["TypeFinder"] = TypeFinder
    conlat_globals["_LibPartition"] = _LibPartition
    conlat_globals["_LibCongruenceLattice"] = _LibCongruenceLattice
    conlat_globals["_CL_ALGEBRAS"] = _CL_ALGEBRAS
    conlat_globals["_CLASS_ALIASES"] = {
        "Partition": {
            "universeSize": "universe_size",
            "numberOfBlocks": "number_of_blocks",
            "isRelated": "is_related",
            "toArray": "to_array",
            "joinBlocks": "join_blocks",
            "isRepresentative": "is_representative",
            "blockIndex": "block_index",
            "getBlocks": "get_blocks",
            "isZero": "is_zero",
            "isUniform": "is_uniform",
            "isInitialLexRepresentative": "is_initial_lex_representative",
            "getPairs": "get_pairs",
            "compareTo": "compare_to",
            "hashCode": "hash_code",
            "toString": "toString",
        },
        "BasicPartition": {
            "universeSize": "universe_size",
            "numberOfBlocks": "number_of_blocks",
            "isRelated": "is_related",
            "toArray": "to_array",
            "joinBlocks": "join_blocks",
            "getArray": "get_array",
            "get": "get",
            "getPairs": "get_pairs",
            "compareTo": "compare_to",
            "hashCode": "hash_code",
            "toString": "toString",
        },
        "CongruenceLattice": {
            "getName": "get_name",
            "getAlgebra": "getAlgebra",
            "getDescription": "get_description",
            "similarityType": "similarityType",
            "isSimilarTo": "isSimilarTo",
            "upperCoversMap": "upper_covers_map",
            "getPermutabilityLevelWitnesses": "get_permutability_level_witnesses",
            "joinIrreduciblesFound": "join_irreducibles_found",
            "joinIrreducibles": "join_irreducibles",
            "meetIrreducibles": "meet_irreducibles",
            "getUniverseList": "get_universe_list",
            "isDistributive": "is_distributive",
            "generatingPair": "generating_pair",
            "findCoatomAbove": "find_coatom_above",
            "findJoinIrred": "find_join_irred",
            "findMeetIrred": "find_meet_irred",
            "findPrincipalChain": "find_principal_chain",
            "findUpperCover": "find_upper_cover",
            "irredundantMeetDecomposition": "irredundant_meet_decomposition",
            "permutabilityLevel": "permutability_level",
            "getBasicLattice": "get_basic_lattice",
            "universeFound": "universe_found",
            "makeUniverse": "make_universe",
            "makePrincipals": "make_principals",
            "joinIrreducible": "join_irreducible",
            "meetIrreducible": "meet_irreducible",
            "inputSize": "input_size",
            "typeJI": "typeJI",
            "typeSet": "typeSet",
            "type": "type",
            "subtrace": "subtrace",
            "getTypeFinder": "getTypeFinder",
            "getJoinIrredToSubtraceMap": "getJoinIrredToSubtraceMap",
        },
        "BinaryRelation": {
            "universeSize": "universe_size",
            "isRelated": "is_related",
            "getPairs": "get_pairs",
            "compose": "compose",
        },
        "BasicBinaryRelation": {
            "universeSize": "universe_size",
            "isRelated": "is_related",
            "getPairs": "get_pairs",
            "compose": "compose",
            "compareTo": "compareTo",
            "isReflexive": "is_reflexive",
            "isSymmetric": "is_symmetric",
            "toString": "toString",
        },
        "Subtrace": {
            "hasInvolution": "has_involution",
            "getSubtraceUniverse": "get_subtrace_universe",
            "setSubtraceUniverse": "set_subtrace_universe",
            "getMatrixUniverse": "get_matrix_universe",
            "setMatrixUniverse": "set_matrix_universe",
            "setType": "set_type",
            "toString": "toString",
        },
        "CentralityData": {
            "getLeft": "left",
            "getRight": "right",
            "getDelta": "delta",
            "compareTo": "compare_to",
            "getCentralityFailure": "getCentralityFailure",
            "setCentralityFailure": "setCentralityFailure",
            "getWeakCentralityFailure": "getWeakCentralityFailure",
            "setWeakCentralityFailure": "setWeakCentralityFailure",
            "getStrongRectangularityFailure": "getStrongRectangularityFailure",
            "setStrongRectangularityFailure": "setStrongRectangularityFailure",
            "toString": "toString",
        },
        "TypeFinder": {
            "init": "init",
            "findTypeSet": "find_type_set",
            "isSubtrace": "is_subtrace",
            "findSubtrace": "find_subtrace",
            "findType": "find_type",
            "nextPairForSubtrace": "nextPairForSubtrace",
        },
        "Polymorphisms": {},
    }
