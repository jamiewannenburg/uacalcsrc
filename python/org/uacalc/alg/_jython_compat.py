"""Jython-facing helpers for ``org.uacalc.alg`` (CPython only).

Legacy scripts under ``~/uacalc`` construct algebras with Java call shapes:
``BasicAlgebra(name, cardinality, ops)``, subclass ``AbstractOperation`` with
``intValueAt``, call ``getOperation`` / ``getName`` / ``setName``, etc.

PyO3 bindings use snake_case and slightly different constructors; this module
bridges those gaps without changing Rust.
"""

from __future__ import annotations

import itertools
from typing import Any, Callable, Iterable, List, Optional, Sequence, Union


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

    class BasicAlgebra(object):
        """Jython-compatible constructor over ``uacalc_lib`` BasicAlgebra.

        Accepts ``BasicAlgebra(name, n, ops)`` (integer cardinality) as in Java,
        or ``BasicAlgebra(name, universe_list, ops)``.
        """

        def __init__(self, name: str, universe: Union[int, Sequence[int]], operations: Optional[Iterable[Any]] = None):
            if isinstance(universe, int):
                univ_list = list(range(int(universe)))
                card = int(universe)
            else:
                univ_list = list(universe)
                card = len(univ_list)
            ops_in = list(operations or [])
            ops = [_coerce_operation(op, set_size=card) for op in ops_in]
            self._inner = _LibBasicAlgebra(str(name), univ_list, ops)

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

    def getOperation(self: Any, sym: Any) -> Any:
        target_name = _sym_name(sym)
        target_arity = _sym_arity(sym)
        for op in self.operations():
            s = _op_symbol(op)
            if _sym_name(s) == target_name and _sym_arity(s) == target_arity:
                return op
        return None

    def setName(self: Any, name: str) -> None:
        self.set_name(str(name))

    def getName(self: Any) -> str:
        return self.name()

    def universe(self: Any) -> List[Any]:
        if hasattr(self, "get_universe_list"):
            return list(self.get_universe_list())
        if hasattr(self, "get_universe"):
            return list(self.get_universe())
        return list(range(self.cardinality()))

    def getUniverseList(self: Any) -> Any:
        if hasattr(self, "get_universe_list"):
            univ = self.get_universe_list()
            if univ is None:
                return None
            return list(univ)
        return None

    # --- patch SimilarityType ---
    if not hasattr(SimilarityType, "getOperationSymbols") and hasattr(
        SimilarityType, "get_operation_symbols"
    ):
        try:
            SimilarityType.getOperationSymbols = SimilarityType.get_operation_symbols
        except (TypeError, AttributeError):
            pass

    def similarityType(self: Any) -> Any:
        symbols = []
        for op in self.operations():
            symbols.append(op.symbol())
        try:
            st = SimilarityType(symbols)
            return st
        except TypeError:
            pass

        class _Sim(object):
            def getOperationSymbols(self_inner: Any) -> List[Any]:
                return list(symbols)

            def get_operation_symbols(self_inner: Any) -> List[Any]:
                return list(symbols)

        return _Sim()

    def constantOperations(self: Any) -> List[Any]:
        return [op for op in self.operations() if int(op.arity()) == 0]

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
        "universe": universe,
        "similarityType": similarityType,
        "constantOperations": constantOperations,
        "getUniverseList": getUniverseList,
        "elementIndex": lambda self, elem: self.element_index(elem),
        "getElement": lambda self, index: self.get_element(index),
        "superAlgebra": lambda self: self.super_algebra(),
        "algebraType": lambda self: self.algebra_type(),
        "resetConAndSub": lambda self: self.reset_con_and_sub(),
    }

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
        for camel, impl in _ALGEBRA_PATCHES.items():
            if not hasattr(target, camel):
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

    # Apply same algebra patches to our BasicAlgebra wrapper
    for camel, impl in _ALGEBRA_PATCHES.items():
        setattr(BasicAlgebra, camel, impl)

    # Export replacements
    alg_module_globals["AbstractOperation"] = AbstractOperation
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
    alg_module_globals["_CLASS_ALIASES"] = {
        "SmallAlgebra": {
            "getUniverseList": "get_universe_list",
            "elementIndex": "element_index",
            "algebraType": "algebra_type",
            "resetConAndSub": "reset_con_and_sub",
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "universe": "universe",
            "similarityType": "similarityType",
            "constantOperations": "constantOperations",
        },
        "BasicAlgebra": {
            "getUniverseList": "get_universe_list",
            "elementIndex": "element_index",
            "algebraType": "algebra_type",
            "resetConAndSub": "reset_con_and_sub",
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "universe": "universe",
            "similarityType": "similarityType",
            "constantOperations": "constantOperations",
        },
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
