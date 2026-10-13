"""Jython-facing helpers for ``org.uacalc.alg`` (CPython only).

Renames, constructor overload dispatch, and Java exception translation only.
Library logic stays in ``uacalc_lib``.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Optional, Sequence, Union

from org.uacalc._exceptions import (
    IndexOutOfBoundsException,
    NullPointerException,
    translate_illegal_argument,
)


def _install(alg_module_globals: dict) -> None:
    """Mutate the ``org.uacalc.alg`` module globals in place."""
    IntOperation = alg_module_globals["IntOperation"]
    OperationSymbol = alg_module_globals["OperationSymbol"]
    SimilarityType = alg_module_globals["SimilarityType"]
    _LibBasicAlgebra = alg_module_globals["BasicAlgebra"]
    _LibFreeAlgebra = alg_module_globals["FreeAlgebra"]
    _LibProductAlgebra = alg_module_globals["ProductAlgebra"]
    _LibSubalgebraLattice = alg_module_globals["SubalgebraLattice"]
    _LibReductAlgebra = alg_module_globals.get("ReductAlgebra")
    _LibSubalgebra = alg_module_globals.get("Subalgebra")
    _LibBigProductAlgebra = alg_module_globals.get("BigProductAlgebra")
    _LibAbstractOperation = alg_module_globals.get("AbstractOperation")

    def _sym_name(sym: Any) -> str:
        name = getattr(sym, "name", None)
        if callable(name):
            return str(name())
        return str(sym)

    def _sym_arity(sym: Any) -> int:
        arity = getattr(sym, "arity", None)
        if callable(arity):
            return int(arity())
        return int(arity)

    def _op_symbol(op: Any) -> Any:
        sym = op.symbol()
        return sym

    def _coerce_operation(op: Any, set_size: Optional[int] = None) -> Any:
        """Turn a Jython-style AbstractOperation (or PyAO) into IntOperation."""
        if op is None:
            return None
        typ = type(op).__name__
        if typ in ("PyIntOperation", "PyBasicOperation", "PyTermOperationImp"):
            return op
        if isinstance(op, AbstractOperation):
            return op._as_int_operation()
        # Native PyAbstractOperationNew
        if hasattr(op, "make_table") and hasattr(op, "from_int_value_at_function"):
            size = set_size
            if size is None:
                size = int(op.get_set_size())
            return IntOperation.from_int_value_at(
                _sym_name(op.symbol()),
                int(op.arity()),
                size,
                lambda args, _op=op: int(_op.int_value_at(list(args))),
            )
        if hasattr(op, "int_value_at") and hasattr(op, "symbol") and hasattr(op, "arity"):
            size = set_size if set_size is not None else int(op.get_set_size())
            return IntOperation.from_int_value_at(
                _sym_name(op.symbol()),
                int(op.arity()),
                size,
                lambda args, _op=op: int(_op.int_value_at(list(args))),
            )
        raise TypeError(
            "unsupported operation type {!r}; expected IntOperation / "
            "AbstractOperation subclass".format(type(op))
        )

    class AbstractOperation(object):
        """Subclassable stand-in for Java ``org.uacalc.alg.op.AbstractOperation``.

        Scripts do::

            class op(AbstractOperation):
                def intValueAt(self, args):
                    ...
            op_fun = op(name, arity, cardinality)
        """

        def __init__(self, name_or_symbol: Any, arity: Optional[int] = None, set_size: Optional[int] = None):
            # Java: AbstractOperation(String name, int arity, int algSize)
            #   or: AbstractOperation(OperationSymbol symbol, int algSize)
            if (
                hasattr(name_or_symbol, "name")
                and hasattr(name_or_symbol, "arity")
                and not isinstance(name_or_symbol, (str, bytes))
            ):
                self._symbol = name_or_symbol
                self._arity = _sym_arity(name_or_symbol)
                size = arity if set_size is None else set_size
                if size is None:
                    raise TypeError("AbstractOperation(symbol, set_size) requires set_size")
                self._set_size = int(size)
            else:
                if arity is None or set_size is None:
                    raise TypeError(
                        "AbstractOperation(name, arity, set_size) requires three arguments"
                    )
                self._symbol = OperationSymbol(str(name_or_symbol), int(arity))
                self._arity = int(arity)
                self._set_size = int(set_size)
            self._cached_int_op = None

        def intValueAt(self, args: Sequence[int]) -> int:
            raise NotImplementedError("subclass must implement intValueAt")

        def int_value_at(self, args: Sequence[int]) -> int:
            return int(self.intValueAt(list(args)))

        def arity(self) -> int:
            return self._arity

        def symbol(self) -> Any:
            return self._symbol

        def get_set_size(self) -> int:
            return self._set_size

        def _as_int_operation(self) -> Any:
            if self._cached_int_op is not None:
                return self._cached_int_op
            self._cached_int_op = IntOperation.from_int_value_at(
                _sym_name(self._symbol),
                self._arity,
                self._set_size,
                lambda args, _self=self: int(_self.intValueAt(list(args))),
            )
            return self._cached_int_op

    class _BasicAlgebraMeta(type):
        """Treat native ``uacalc_lib`` BasicAlgebra values as this Jython type."""

        def __instancecheck__(cls, instance: Any) -> bool:
            if type(instance) is cls:
                return True
            return isinstance(instance, _LibBasicAlgebra)

    class BasicAlgebra(object, metaclass=_BasicAlgebraMeta):
        """Jython-compatible constructor over ``uacalc_lib`` BasicAlgebra.

        Accepts ``BasicAlgebra(name, n, ops)`` (integer cardinality) as in Java,
        or ``BasicAlgebra(name, universe_list, ops)``.
        """

        def __init__(self, name: str, universe: Union[int, Sequence[Any]], operations: Optional[Iterable[Any]] = None):
            java_int = isinstance(universe, int) and not isinstance(universe, bool)
            if java_int:
                univ_list = list(range(int(universe)))
                card = int(universe)
            else:
                univ_list = list(universe)
                card = len(univ_list)
            if operations is None:
                ops_in = []
            else:
                ops_in = list(operations)
            ops = [_coerce_operation(op, set_size=card) for op in ops_in]
            self._inner = _LibBasicAlgebra(str(name), univ_list, ops)
            self._java_int_universe = java_int
            if not java_int:
                self._java_universe_list = univ_list

        def __getattr__(self, item: str) -> Any:
            return getattr(self._inner, item)

        def __repr__(self) -> str:
            return repr(self._inner)

        def __str__(self) -> str:
            return str(self._inner)

    def _free_algebra(base: Any, number_of_gens: int, *rest: Any) -> Any:
        """``FreeAlgebra(alg, n)`` or ``FreeAlgebra(alg, n, makeUniverse, thinGens)``."""
        base_inner = getattr(base, "_inner", base)
        if not rest:
            return _LibFreeAlgebra(base_inner, int(number_of_gens))
        if len(rest) == 1:
            # makeUniverse only
            return _LibFreeAlgebra.new_with_progress(
                base_inner, int(number_of_gens), bool(rest[0]), False, False
            )
        # makeUniverse, thinGenerators
        return _LibFreeAlgebra.new_with_progress(
            base_inner,
            int(number_of_gens),
            bool(rest[0]),
            bool(rest[1]),
            False,
        )

    def _product_algebra(*args: Any) -> Any:
        """``ProductAlgebra(algs)`` or ``ProductAlgebra(name, algs)``."""
        if len(args) == 1:
            algs = list(args[0])
            name = "x".join(str(getattr(a, "getName", getattr(a, "name"))()) for a in algs)
            return _LibProductAlgebra(name, algs)
        if len(args) == 2:
            return _LibProductAlgebra(str(args[0]), list(args[1]))
        raise TypeError("ProductAlgebra() takes 1 or 2 arguments")

    def _unwrap_algebra(alg: Any) -> Any:
        """Prefer the PyO3 inner object when a Jython wrapper is present."""
        return getattr(alg, "_inner", alg)

    def _term_to_name(term: Any) -> str:
        """Map a Jython Term (or already-a-string) to the Rust string binding."""
        if isinstance(term, (str, bytes)):
            return str(term)
        for attr in ("name", "getName", "get_name"):
            fn = getattr(term, attr, None)
            if callable(fn):
                try:
                    return str(fn())
                except TypeError:
                    continue
            if fn is not None and not callable(fn):
                return str(fn)
        return str(term)

    def _terms_to_names(terms: Any) -> List[str]:
        if terms is None:
            return []
        return [_term_to_name(t) for t in list(terms)]

    def _as_universe_indices(obj: Any) -> List[int]:
        """Coerce Java BasicSet / IntArray / list into ``list[int]`` indices."""
        if obj is None:
            return []
        if isinstance(obj, (list, tuple)):
            return [int(x) for x in obj]
        for attr in ("elements", "to_array", "toArray", "getArray", "get_array"):
            fn = getattr(obj, attr, None)
            if callable(fn):
                try:
                    return [int(x) for x in fn()]
                except TypeError:
                    continue
        size_fn = getattr(obj, "universeSize", None) or getattr(obj, "universe_size", None)
        getter = getattr(obj, "get", None)
        if callable(size_fn) and callable(getter):
            try:
                n = int(size_fn())
                return [int(getter(i)) for i in range(n)]
            except TypeError:
                pass
        try:
            return [int(x) for x in obj]
        except TypeError:
            raise TypeError(
                "cannot coerce {!r} to a subuniverse index list".format(type(obj))
            )

    def _reduct_algebra(*args: Any) -> Any:
        """``ReductAlgebra(alg, terms)`` or ``ReductAlgebra(name, alg, terms)``."""
        if _LibReductAlgebra is None:
            raise TypeError("ReductAlgebra is not bound")
        if len(args) == 2:
            alg, terms = args
            name = None
        elif len(args) == 3:
            name, alg, terms = args
        else:
            raise TypeError("ReductAlgebra() takes 2 or 3 arguments")
        reduct = _LibReductAlgebra(_unwrap_algebra(alg), list(terms))
        if name is not None:
            reduct.set_name(str(name))
        return reduct

    def _subalgebra(*args: Any) -> Any:
        """``Subalgebra(alg, univ)`` or ``Subalgebra(name, alg, univ)``."""
        if _LibSubalgebra is None:
            raise TypeError("Subalgebra is not bound")
        if len(args) == 2:
            alg, univ = args
            name = ""
        elif len(args) == 3:
            name, alg, univ = args
        else:
            raise TypeError("Subalgebra() takes 2 or 3 arguments")
        return _LibSubalgebra(str(name), _unwrap_algebra(alg), _as_universe_indices(univ))

    def _raise_npe(what: str = "null") -> None:
        raise NullPointerException(what)

    def _lib_call(fn: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except ValueError as exc:
            translate_illegal_argument(exc)

    def _as_algebra(alg: Any) -> Any:
        return getattr(alg, "_inner", alg)

    _ALG_TYPE_JAVA = {
        "Basic": "BASIC",
        "BASIC": "BASIC",
        "BasicLattice": "BASIC_LATTICE",
        "BASIC_LATTICE": "BASIC_LATTICE",
        "Quotient": "QUOTIENT",
        "QUOTIENT": "QUOTIENT",
        "Subalgebra": "SUBALGEBRA",
        "SUBALGEBRA": "SUBALGEBRA",
        "Product": "PRODUCT",
        "PRODUCT": "PRODUCT",
        "Power": "POWER",
        "POWER": "POWER",
        "MatrixPower": "MATRIX_POWER",
        "MATRIX_POWER": "MATRIX_POWER",
        "Reduct": "REDUCT",
        "REDUCT": "REDUCT",
        "Subproduct": "SUBPRODUCT",
        "SUBPRODUCT": "SUBPRODUCT",
        "Free": "FREE",
        "FREE": "FREE",
        "PolinLike": "POLIN_LIKE",
        "POLIN_LIKE": "POLIN_LIKE",
        "UnaryTermsMonoid": "UNARY_TERMS_MONOID",
        "UNARY_TERMS_MONOID": "UNARY_TERMS_MONOID",
        "FiniteField": "FINITE_FIELD",
        "FINITE_FIELD": "FINITE_FIELD",
    }

    class AlgebraType(object):
        """Java ``SmallAlgebra.AlgebraType`` enum stand-in."""

        def __init__(self, name: str) -> None:
            self._name = str(name)

        def name(self) -> str:
            return self._name

        def toString(self) -> str:
            return self._name

        def equals(self, other: Any) -> bool:
            return self.__eq__(other)

        def __str__(self) -> str:
            return self._name

        def __repr__(self) -> str:
            return self._name

        def __eq__(self, other: Any) -> bool:
            if other is None:
                return False
            if isinstance(other, AlgebraType):
                return self._name == other._name
            return self._name == str(other)

        def __hash__(self) -> int:
            return hash(self._name)

    for _type_name in (
        "BASIC",
        "BASIC_LATTICE",
        "QUOTIENT",
        "SUBALGEBRA",
        "PRODUCT",
        "POWER",
        "MATRIX_POWER",
        "REDUCT",
        "SUBPRODUCT",
        "FREE",
        "POLIN_LIKE",
        "UNARY_TERMS_MONOID",
        "FINITE_FIELD",
    ):
        setattr(AlgebraType, _type_name, AlgebraType(_type_name))

    _ALGEBRA_MONITOR = [None]  # Java GeneralAlgebra.monitor is static

    def getOperation(self: Any, sym: Any) -> Any:
        fn = getattr(self, "get_operation", None)
        if callable(fn):
            return _lib_call(fn, sym)
        if sym is None:
            return None
        target_name = _sym_name(sym)
        target_arity = _sym_arity(sym)
        for op in self.operations():
            s = _op_symbol(op)
            if _sym_name(s) == target_name and _sym_arity(s) == target_arity:
                return op
        return None

    def setName(self: Any, name: Any) -> None:
        self.set_name(None if name is None else str(name))

    def getName(self: Any) -> Any:
        return self.name()

    def getDescription(self: Any) -> Any:
        fn = getattr(self, "description", None)
        if callable(fn):
            return fn()
        return None

    def setDescription(self: Any, desc: Any) -> None:
        fn = getattr(self, "set_description", None)
        if callable(fn):
            fn(None if desc is None else str(desc))

    def intUniverse(self: Any) -> bool:
        flag = getattr(self, "_java_int_universe", None)
        if flag is not None:
            return bool(flag)
        fn = getattr(self, "int_universe", None)
        if callable(fn):
            return bool(fn())
        return False

    def getUniverseList(self: Any) -> Any:
        if hasattr(self, "_java_universe_list"):
            lst = self._java_universe_list
            return None if lst is None else list(lst)
        if intUniverse(self):
            return None
        fn = getattr(self, "get_universe_list", None)
        if callable(fn):
            univ = fn()
            if univ is None:
                return None
            return list(univ)
        return None

    def setUniverseList(self: Any, lst: Any) -> None:
        value = None if lst is None else list(lst)
        try:
            object.__setattr__(self, "_java_universe_list", value)
            object.__setattr__(self, "_java_int_universe", lst is None)
        except (TypeError, AttributeError):
            pass

    def getUniverseOrder(self: Any) -> Any:
        if hasattr(self, "_java_universe_order"):
            return self._java_universe_order
        if intUniverse(self):
            return None
        fn = getattr(self, "get_universe_order", None)
        if callable(fn):
            return fn()
        return None

    def setUniverseOrder(self: Any, ord_map: Any) -> None:
        try:
            object.__setattr__(self, "_java_universe_order", ord_map)
        except (TypeError, AttributeError):
            pass

    def universe(self: Any) -> List[Any]:
        fn = getattr(self, "universe", None)
        # Prefer the bound universe() only when it is the library method, not
        # this shim (would recurse). Call get_universe / get_universe_list.
        get_u = getattr(self, "get_universe", None)
        if callable(get_u):
            return list(get_u())
        lst = getUniverseList(self)
        if lst is not None:
            return list(lst)
        return list(range(int(self.cardinality())))

    def _algebra_iterator(self: Any) -> Any:
        get_u = getattr(self, "get_universe", None)
        if callable(get_u):
            return iter(list(get_u()))
        return iter(universe(self))

    def getElement(self: Any, k: Any) -> Any:
        # Java getElement(int) — Jython None→int is TypeError, not NPE.
        idx = int(k)
        if intUniverse(self):
            return idx
        lst = getUniverseList(self)
        if lst is None:
            fn = getattr(self, "get_element", None)
            if callable(fn):
                return fn(idx)
            return idx
        try:
            return lst[idx]
        except IndexError as exc:
            raise IndexOutOfBoundsException(
                "Index: {0}, Size: {1}".format(idx, len(lst))
            ) from exc

    def elementIndex(self: Any, elem: Any) -> int:
        if intUniverse(self):
            if elem is None:
                _raise_npe()
            if isinstance(elem, bool) or not isinstance(elem, int):
                return -1
            k = int(elem)
            card = int(self.cardinality())
            if 0 <= k < card:
                return k
            return -1
        if elem is None:
            _raise_npe()
        fn = getattr(self, "element_index", None)
        idx = int(fn(elem)) if callable(fn) else -1
        if idx < 0:
            _raise_npe()
        return idx

    def similarityType(self: Any) -> Any:
        fn = getattr(self, "similarity_type", None)
        if callable(fn):
            return _lib_call(fn)
        symbols = [op.symbol() for op in self.operations()]
        return SimilarityType(symbols)

    def updateSimilarityType(self: Any) -> None:
        fn = getattr(self, "update_similarity_type", None)
        if callable(fn):
            _lib_call(fn)

    def constantOperations(self: Any) -> List[Any]:
        fn = getattr(self, "constant_operations", None)
        if callable(fn):
            return list(_lib_call(fn))
        return [op for op in self.operations() if int(op.arity()) == 0]

    def getOperationsMap(self: Any) -> Any:
        fn = getattr(self, "get_operations_map", None)
        if callable(fn):
            return _lib_call(fn)
        out = {}
        for op in self.operations():
            out[op.symbol()] = op
        return out

    def isSimilarTo(self: Any, alg: Any) -> bool:
        if alg is None:
            _raise_npe()
        fn = getattr(self, "is_similar_to", None)
        other = _as_algebra(alg)
        if callable(fn):
            try:
                return bool(_lib_call(fn, other))
            except TypeError:
                pass
        st = similarityType(self)
        other_st = (
            alg.similarityType() if hasattr(alg, "similarityType") else alg.similarity_type()
        )
        equals = getattr(st, "equals", None)
        if callable(equals):
            return bool(equals(other_st))
        return st == other_st

    def makeOperationTables(self: Any) -> None:
        fn = getattr(self, "make_operation_tables", None)
        if callable(fn):
            _lib_call(fn)

    def inputSize(self: Any) -> int:
        return int(self.input_size())

    def isUnary(self: Any) -> bool:
        return bool(self.is_unary())

    def isIdempotent(self: Any) -> bool:
        return bool(_lib_call(self.is_idempotent))

    def isTotal(self: Any) -> bool:
        return bool(_lib_call(self.is_total))

    def algebraType(self: Any) -> Any:
        raw = self.algebra_type()
        name = _ALG_TYPE_JAVA.get(str(raw), str(raw).upper())
        mapped = getattr(AlgebraType, name, None)
        return mapped if mapped is not None else AlgebraType(name)

    def resetConAndSub(self: Any) -> None:
        fn = getattr(self, "reset_con_and_sub", None)
        if callable(fn):
            fn()

    def convertToDefaultValueOps(self: Any) -> None:
        fn = getattr(self, "convert_to_default_value_ops", None)
        if callable(fn):
            _lib_call(fn)

    def parent(self: Any) -> Any:
        # Java BasicAlgebra / GeneralAlgebra.parent() is identically null.
        return None

    def parents(self: Any) -> Any:
        # Java GeneralAlgebra.parents() returns null when parent() is null.
        return None

    def setMonitor(self: Any, monitor: Any) -> None:
        # Java signature is setMonitor(ProgressReport). Jython rejects a
        # non-ProgressReport argument with TypeError; ProgressReport itself
        # is a UI type and is not bound, so only None is accepted.
        if monitor is not None:
            raise TypeError(
                "setMonitor(): expected org.uacalc.ui.tm.ProgressReport or None"
            )
        _ALGEBRA_MONITOR[0] = None

    def getMonitor(self: Any) -> Any:
        return _ALGEBRA_MONITOR[0]

    def monitoring(self: Any) -> bool:
        return _ALGEBRA_MONITOR[0] is not None

    # --- patch SimilarityType ---
    if not hasattr(SimilarityType, "getOperationSymbols") and hasattr(
        SimilarityType, "get_operation_symbols"
    ):
        try:
            SimilarityType.getOperationSymbols = SimilarityType.get_operation_symbols
        except (TypeError, AttributeError):
            pass

    def numberOfFactors(self: Any) -> int:
        return int(self.number_of_factors())

    def iterator(self: Any) -> Any:
        """Match Java ``SubalgebraLattice.iterator()`` → iterate ``universe()``."""
        return iter(self.universe())

    def Sg(self: Any, generators: Sequence[Any]) -> Any:
        """Java-style ``sub().Sg(gens)`` alias for ``sg``."""
        return self.sg(list(generators))

    # --- patch operation classes with camelCase ---
    for cls_name in (
        "IntOperation",
        "BasicOperation",
        "OperationWithDefaultValue",
        "TermOperationImp",
    ):
        cls = alg_module_globals.get(cls_name)
        if cls is None:
            continue
        if not hasattr(cls, "intValueAt") and hasattr(cls, "int_value_at"):
            cls.intValueAt = cls.int_value_at
        if not hasattr(cls, "valueAt") and hasattr(cls, "value_at"):
            cls.valueAt = cls.value_at

    # --- patch algebra-like classes ---
    _ALGEBRA_PATCHES = {
        "getOperation": getOperation,
        "setName": setName,
        "getName": getName,
        "getDescription": getDescription,
        "setDescription": setDescription,
        "universe": universe,
        "similarityType": similarityType,
        "updateSimilarityType": updateSimilarityType,
        "constantOperations": constantOperations,
        "getOperationsMap": getOperationsMap,
        "superAlgebra": lambda self, _sa=None: self.super_algebra(),
        "algebraType": algebraType,
        "resetConAndSub": resetConAndSub,
        "convertToDefaultValueOps": convertToDefaultValueOps,
        "isSimilarTo": isSimilarTo,
        "makeOperationTables": makeOperationTables,
        "inputSize": inputSize,
        "isUnary": isUnary,
        "isIdempotent": isIdempotent,
        "isTotal": isTotal,
        "setMonitor": setMonitor,
        "getMonitor": getMonitor,
        "monitoring": monitoring,
    }
    _BASIC_ALGEBRA_PATCHES = dict(_ALGEBRA_PATCHES)
    _BASIC_ALGEBRA_PATCHES.update(
        {
            "iterator": _algebra_iterator,
            "getUniverseList": getUniverseList,
            "setUniverseList": setUniverseList,
            "getUniverseOrder": getUniverseOrder,
            "setUniverseOrder": setUniverseOrder,
            "elementIndex": elementIndex,
            "getElement": getElement,
            "intUniverse": intUniverse,
            "parent": parent,
            "parents": parents,
        }
    )

    for cls_name in (
        "BasicAlgebra",
        "SmallAlgebra",
        "FreeAlgebra",
        "ProductAlgebra",
        "ReductAlgebra",
        "Subalgebra",
        "PowerAlgebra",
        "GeneralAlgebra",
    ):
        # Patch the *library* class (what AlgebraIO returns), not only wrappers.
        lib_cls = alg_module_globals.get(cls_name)
        if lib_cls is None:
            continue
        # Prefer library class before we overwrite BasicAlgebra export
        target = {
            "BasicAlgebra": _LibBasicAlgebra,
            "FreeAlgebra": _LibFreeAlgebra,
            "ProductAlgebra": _LibProductAlgebra,
            "ReductAlgebra": _LibReductAlgebra,
            "Subalgebra": _LibSubalgebra,
        }.get(cls_name, lib_cls)
        if target is None:
            continue
        patches = (
            _BASIC_ALGEBRA_PATCHES if cls_name == "BasicAlgebra" else _ALGEBRA_PATCHES
        )
        for camel, impl in patches.items():
            try:
                setattr(target, camel, impl)
            except (TypeError, AttributeError):
                pass

    # FreeAlgebra / ProductAlgebra extras
    if not hasattr(_LibProductAlgebra, "numberOfFactors"):
        try:
            _LibProductAlgebra.numberOfFactors = numberOfFactors
        except (TypeError, AttributeError):
            pass
    if _LibBigProductAlgebra is not None:
        for camel, impl in (
            ("numberOfFactors", numberOfFactors),
            ("getNumberOfFactors", numberOfFactors),
        ):
            if not hasattr(_LibBigProductAlgebra, camel):
                try:
                    setattr(_LibBigProductAlgebra, camel, impl)
                except (TypeError, AttributeError):
                    pass

    if not hasattr(_LibSubalgebraLattice, "iterator"):
        try:
            _LibSubalgebraLattice.iterator = iterator
        except (TypeError, AttributeError):
            pass
    if not hasattr(_LibSubalgebraLattice, "Sg"):
        try:
            _LibSubalgebraLattice.Sg = Sg
        except (TypeError, AttributeError):
            pass

    # Also patch SubalgebraLattice returned via .sub()
    for meth_name, meth in (("Sg", Sg), ("iterator", iterator)):
        try:
            if not hasattr(_LibSubalgebraLattice, meth_name):
                setattr(_LibSubalgebraLattice, meth_name, meth)
        except (TypeError, AttributeError):
            pass

    # Apply BasicAlgebra Java-shape patches to our wrapper
    for camel, impl in _BASIC_ALGEBRA_PATCHES.items():
        setattr(BasicAlgebra, camel, impl)

    class _AlgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            if isinstance(instance, (BasicAlgebra, _LibBasicAlgebra)):
                return True
            name = type(instance).__name__
            if "Algebra" not in name and "algebra" not in name:
                return False
            if any(tag in name for tag in ("Similarity", "Operation", "Type")):
                return False
            if cls.__name__ == "Algebra":
                return True
            if "BigProduct" in name:
                return False
            return True

    class Algebra(object, metaclass=_AlgebraMeta):
        CARDINALITY_UNKNOWN = -1
        CARDINALITY_FINITE = -2
        CARDINALITY_INFINITE = -3
        CARDINALITY_COUNTABLE = -4
        CARDINALITY_COUNTABLY_INFINITE = -5

        def universe(self):
            raise NotImplementedError

        def cardinality(self):
            raise NotImplementedError

        def inputSize(self):
            raise NotImplementedError

        def isUnary(self):
            raise NotImplementedError

        def iterator(self):
            raise NotImplementedError

        def operations(self):
            raise NotImplementedError

        def getOperation(self, sym):
            raise NotImplementedError

        def getOperationsMap(self):
            raise NotImplementedError

        def getName(self):
            raise NotImplementedError

        def setName(self, v):
            raise NotImplementedError

        def getDescription(self):
            raise NotImplementedError

        def setDescription(self, desc):
            raise NotImplementedError

        def similarityType(self):
            raise NotImplementedError

        def updateSimilarityType(self):
            raise NotImplementedError

        def isSimilarTo(self, alg):
            raise NotImplementedError

        def makeOperationTables(self):
            raise NotImplementedError

        def constantOperations(self):
            raise NotImplementedError

        def isIdempotent(self):
            raise NotImplementedError

        def isTotal(self):
            raise NotImplementedError

        def monitoring(self):
            raise NotImplementedError

        def getMonitor(self):
            raise NotImplementedError

        def setMonitor(self, monitor):
            raise NotImplementedError

    class SmallAlgebra(Algebra):
        def algebraType(self):
            raise NotImplementedError

        def getElement(self, k):
            raise NotImplementedError

        def elementIndex(self, elem):
            raise NotImplementedError

        def getUniverseList(self):
            raise NotImplementedError

        def getUniverseOrder(self):
            raise NotImplementedError

        def con(self):
            raise NotImplementedError

        def sub(self):
            raise NotImplementedError

        def resetConAndSub(self):
            raise NotImplementedError

        def parent(self):
            raise NotImplementedError

        def parents(self):
            raise NotImplementedError

        def convertToDefaultValueOps(self):
            raise NotImplementedError

    SmallAlgebra.AlgebraType = AlgebraType

    # Export replacements
    alg_module_globals["AbstractOperation"] = AbstractOperation
    alg_module_globals["Algebra"] = Algebra
    alg_module_globals["AlgebraType"] = AlgebraType
    alg_module_globals["SmallAlgebra"] = SmallAlgebra
    alg_module_globals["BasicAlgebra"] = BasicAlgebra
    alg_module_globals["FreeAlgebra"] = _free_algebra
    alg_module_globals["ProductAlgebra"] = _product_algebra
    if _LibReductAlgebra is not None:
        alg_module_globals["ReductAlgebra"] = _reduct_algebra
        alg_module_globals["_LibReductAlgebra"] = _LibReductAlgebra
    if _LibSubalgebra is not None:
        alg_module_globals["Subalgebra"] = _subalgebra
        alg_module_globals["_LibSubalgebra"] = _LibSubalgebra
    # Keep native classes available for isinstance checks / advanced use
    alg_module_globals["_LibBasicAlgebra"] = _LibBasicAlgebra
    alg_module_globals["_LibFreeAlgebra"] = _LibFreeAlgebra
    alg_module_globals["_LibProductAlgebra"] = _LibProductAlgebra
    alg_module_globals["_LibAbstractOperation"] = _LibAbstractOperation

    # Class-alias map kept for jython_contracts validate()
    _ALGEBRA_INTERFACE_ALIASES = {
        "universe": "universe",
        "cardinality": "cardinality",
        "inputSize": "input_size",
        "isUnary": "is_unary",
        "iterator": "iterator",
        "operations": "operations",
        "getOperation": "get_operation",
        "getOperationsMap": "get_operations_map",
        "getName": "name",
        "setName": "set_name",
        "getDescription": "description",
        "setDescription": "set_description",
        "similarityType": "similarity_type",
        "updateSimilarityType": "update_similarity_type",
        "isSimilarTo": "is_similar_to",
        "makeOperationTables": "make_operation_tables",
        "constantOperations": "constant_operations",
        "isIdempotent": "is_idempotent",
        "isTotal": "is_total",
        "monitoring": "monitoring",
        "getMonitor": "getMonitor",
        "setMonitor": "setMonitor",
    }
    _SMALL_ALGEBRA_ALIASES = dict(_ALGEBRA_INTERFACE_ALIASES)
    _SMALL_ALGEBRA_ALIASES.update(
        {
            "algebraType": "algebra_type",
            "getElement": "get_element",
            "elementIndex": "element_index",
            "getUniverseList": "get_universe_list",
            "getUniverseOrder": "get_universe_order",
            "con": "con",
            "sub": "sub",
            "resetConAndSub": "reset_con_and_sub",
            "parent": "parent",
            "parents": "parents",
            "convertToDefaultValueOps": "convert_to_default_value_ops",
        }
    )
    _BASIC_ALGEBRA_ALIASES = dict(_SMALL_ALGEBRA_ALIASES)
    _BASIC_ALGEBRA_ALIASES.update(
        {
            "intUniverse": "int_universe",
            "setUniverseList": "setUniverseList",
            "setUniverseOrder": "setUniverseOrder",
        }
    )

    alg_module_globals["_CLASS_ALIASES"] = {
        "Algebra": _ALGEBRA_INTERFACE_ALIASES,
        "SmallAlgebra": _SMALL_ALGEBRA_ALIASES,
        "BasicAlgebra": _BASIC_ALGEBRA_ALIASES,
        "FreeAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "elementIndex": "element_index",
            "getElement": "get_element",
            "getOperation": "getOperation",
            "getUniverseList": "get_universe_list",
            "getTerms": "get_terms",
            "getTerm": "get_term",
            "getElementFromTerm": "get_element_from_term",
            "getProductAlgebra": "get_product_algebra",
            "generators": "generators",
            "getVariables": "get_variables",
            "getIdempotentTerms": "get_idempotent_terms",
            "superAlgebra": "super_algebra",
            "algebraType": "algebra_type",
        },
        "ProductAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "numberOfFactors": "number_of_factors",
            "getOperation": "getOperation",
        },
        "BigProductAlgebra": {
            "numberOfFactors": "number_of_factors",
            "getNumberOfFactors": "number_of_factors",
        },
        "ReductAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "superAlgebra": "super_algebra",
            "elementIndex": "element_index",
            "getElement": "get_element",
            "getUniverseList": "get_universe_list",
            "algebraType": "algebra_type",
        },
        "Subalgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "superAlgebra": "super_algebra",
            "getSubuniverseArray": "get_subuniverse_array",
            "elementIndex": "element_index",
            "getElement": "get_element",
            "index": "index",
            "algebraType": "algebra_type",
            "getUniverseList": "get_universe_list",
        },
        "SubalgebraLattice": {
            "iterator": "iterator",
            "Sg": "sg",
        },
    }

    def _apply_class_aliases() -> None:
        for class_name, aliases in alg_module_globals["_CLASS_ALIASES"].items():
            cls = {
                "BasicAlgebra": _LibBasicAlgebra,
                "FreeAlgebra": _LibFreeAlgebra,
                "ProductAlgebra": _LibProductAlgebra,
                "BigProductAlgebra": _LibBigProductAlgebra,
                "SubalgebraLattice": _LibSubalgebraLattice,
                "ReductAlgebra": _LibReductAlgebra,
                "Subalgebra": _LibSubalgebra,
            }.get(class_name, alg_module_globals.get(class_name))
            if cls is None:
                continue
            for camel, snake in aliases.items():
                if hasattr(cls, camel):
                    continue
                impl = getattr(cls, snake, None)
                if impl is not None:
                    try:
                        setattr(cls, camel, impl)
                    except (TypeError, AttributeError):
                        pass

    _apply_class_aliases()
    alg_module_globals["_apply_class_aliases"] = _apply_class_aliases

    Operations = alg_module_globals.get("Operations")
    if Operations is not None and not hasattr(Operations, "makeIntOperation"):
        make_int = getattr(Operations, "make_int_operation", None)
        if make_int is not None:
            try:
                Operations.makeIntOperation = staticmethod(make_int)
            except (TypeError, AttributeError):
                Operations.makeIntOperation = make_int
