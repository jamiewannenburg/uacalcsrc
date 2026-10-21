"""Jython-facing helpers for ``org.uacalc.alg`` (CPython only).

Renames, constructor overload dispatch, and Java exception translation only.
Library logic stays in ``uacalc_lib``.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Optional, Sequence, Union

from org.uacalc._exceptions import (
    ArrayIndexOutOfBoundsException,
    IllegalArgumentException,
    IndexOutOfBoundsException,
    NoSuchElementException,
    NullPointerException,
    UnsupportedOperationException,
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
    _LibPowerAlgebra = alg_module_globals.get("PowerAlgebra")
    _LibQuotientAlgebra = alg_module_globals.get("QuotientAlgebra")
    _LibQuotientElement = alg_module_globals.get("QuotientElement")
    _LibSubProductAlgebra = alg_module_globals.get("SubProductAlgebra")
    _LibAbstractOperation = alg_module_globals.get("AbstractOperation")
    _LibHomomorphism = alg_module_globals.get("Homomorphism")
    _LibCloser = alg_module_globals.get("Closer")
    _LibCloserTiming = alg_module_globals.get("CloserTiming")
    _LibMaltsevProductDecomposition = alg_module_globals.get(
        "MaltsevProductDecomposition"
    )
    _CON_ALGEBRAS: dict = {}
    _CON_CACHE: dict = {}
    _MISSING = object()
    _LibAlgebraFromMinimalSets = alg_module_globals.get("AlgebraFromMinimalSets")
    _LibAlgebraWithGeneratingVector = alg_module_globals.get("AlgebraWithGeneratingVector")
    _LibGeneralAlgebra = alg_module_globals.get("GeneralAlgebra")
    _LibMatrixPowerAlgebra = alg_module_globals.get("MatrixPowerAlgebra")
    _LibParameterizedAlgebra = alg_module_globals.get("ParameterizedAlgebra")
    _LibPolinLikeAlgebra = alg_module_globals.get("PolinLikeAlgebra")
    _LibUnaryTermsMonoid = alg_module_globals.get("UnaryTermsMonoid")

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

        def getSetSize(self) -> int:
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

    class AbstractIntOperation(AbstractOperation):
        """Java ``org.uacalc.alg.op.AbstractIntOperation``: concrete for Jython.

        ``valueAt(List)`` is always UOE (Java override). ``intValueAt`` stays
        UOE unless a subclass implements it.
        """

        def valueAt(self, args: Any) -> Any:
            raise UnsupportedOperationException()

        def intValueAt(self, args: Any) -> int:
            raise UnsupportedOperationException()

        def int_value_at(self, args: Sequence[int]) -> int:
            return int(self.intValueAt(list(args)))

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

    def _as_basic_algebra(alg: Any) -> Any:
        if alg is None:
            _raise_npe()
        inner = getattr(alg, "_inner", alg)
        typ = type(inner).__name__
        if typ in ("PyBasicAlgebra", "BasicAlgebra"):
            return inner
        conv = getattr(inner, "to_basic_algebra", None) or getattr(
            alg, "to_basic_algebra", None
        )
        if callable(conv):
            return conv()
        return inner

    class _FreeAlgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return isinstance(instance, _LibFreeAlgebra)

    class FreeAlgebra(object, metaclass=_FreeAlgebraMeta):
        """Java constructor overloads over ``uacalc_lib`` FreeAlgebra."""

        def __new__(cls, *args: Any) -> Any:
            if not args:
                raise TypeError("FreeAlgebra() takes at least 2 arguments")
            # FreeAlgebra(name, prod, gens, univList)
            if len(args) == 4 and not isinstance(args[2], (int, bool)):
                name, prod, gens, univ = args
                return _lib_call(
                    _LibFreeAlgebra.new_from_product,
                    str(name),
                    prod,
                    [_int_array(g) for g in list(gens)],
                    [_int_array(u) for u in list(univ)],
                )
            # FreeAlgebra(name, alg, n[, makeUniverse[, thinGens]])
            if isinstance(args[0], (str, bytes)):
                name = str(args[0])
                if len(args) < 3:
                    raise TypeError("FreeAlgebra(name, alg, n) requires 3 arguments")
                base = _as_basic_algebra(args[1])
                n = int(args[2])
                make_universe = True if len(args) < 4 else bool(args[3])
                thin_gens = False if len(args) < 5 else bool(args[4])
                return _lib_call(
                    _LibFreeAlgebra.new_with_name_thin,
                    name,
                    base,
                    n,
                    make_universe,
                    thin_gens,
                )
            # FreeAlgebra(alg, n[, makeUniverse[, thinGens]])
            # or FreeAlgebra(alg, n, ProgressReport) with report=None.
            base = _as_basic_algebra(args[0])
            if len(args) < 2:
                raise TypeError("FreeAlgebra(alg, n) requires 2 arguments")
            n = int(args[1])
            if len(args) == 2:
                return _lib_call(_LibFreeAlgebra, base, n)
            third = args[2]
            if third is None:
                if len(args) > 3:
                    raise TypeError(
                        "FreeAlgebra(): expected org.uacalc.ui.tm.ProgressReport or None"
                    )
                # Java (alg, n, report=null): makeUniverse=true, thinGens=true,
                # decompose=true. Non-None ProgressReport is not bound.
                return _lib_call(
                    _LibFreeAlgebra.new_with_progress,
                    base,
                    n,
                    True,
                    True,
                    True,
                )
            if not isinstance(third, bool):
                raise TypeError(
                    "FreeAlgebra(): expected org.uacalc.ui.tm.ProgressReport or None"
                )
            make_universe = bool(third)
            thin_gens = False if len(args) < 4 else bool(args[3])
            return _lib_call(
                _LibFreeAlgebra.new_with_progress,
                base,
                n,
                make_universe,
                thin_gens,
                False,
            )

        @staticmethod
        def findEquationOfAnotB(a: Any, b: Any, bGens: Any, report: Any = None) -> Any:
            # Java 3-arg overload always NPEs: report.addLine on null report.
            if report is None:
                raise NullPointerException()
            raise TypeError(
                "findEquationOfAnotB(): expected org.uacalc.ui.tm.ProgressReport or None"
            )

    def _as_product_factor(alg: Any) -> Any:
        inner = getattr(alg, "_inner", alg)
        typ = type(inner).__name__
        if typ in ("PyBasicAlgebra", "BasicAlgebra"):
            return inner
        conv = getattr(inner, "to_basic_algebra", None)
        if callable(conv):
            return conv()
        return inner

    def _product_factors(algs: Any) -> List[Any]:
        return [_as_product_factor(a) for a in list(algs)]

    def _product_name(algs: List[Any]) -> str:
        names = []
        for a in algs:
            getter = getattr(a, "getName", None) or getattr(a, "name", None)
            names.append(str(getter() if callable(getter) else getter))
        return "x".join(names)

    class _ProductAlgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return isinstance(instance, _LibProductAlgebra)

    class ProductAlgebra(object, metaclass=_ProductAlgebraMeta):
        """``ProductAlgebra(algs)`` or ``ProductAlgebra(name, algs)``."""

        def __new__(cls, *args: Any) -> Any:
            if len(args) == 1:
                algs = _product_factors(args[0])
            elif len(args) == 2:
                algs = _product_factors(args[1])
            else:
                raise TypeError("ProductAlgebra() takes 1 or 2 arguments")
            # Java makeOperations() does algebras.get(0) and throws IOBE.
            if not algs:
                raise IndexOutOfBoundsException(
                    "Index 0 out of bounds for length 0"
                )
            if len(args) == 1:
                # Java ProductAlgebra(List) passes an empty name.
                return _lib_call(_LibProductAlgebra, "", algs)
            return _lib_call(_LibProductAlgebra, str(args[0]), algs)

        @staticmethod
        def calcCard(sizes: Any) -> int:
            # Java starts from BigInteger.ONE, so the empty product is 1.
            items = [int(x) for x in list(sizes)]
            if not items:
                return 1
            return int(_lib_call(_LibProductAlgebra.calc_card, items))

    class _PowerAlgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibPowerAlgebra is not None and isinstance(instance, _LibPowerAlgebra)

    class PowerAlgebra(object, metaclass=_PowerAlgebraMeta):
        """``PowerAlgebra(alg, power)`` or ``PowerAlgebra(name, alg, power)``."""

        def __new__(cls, *args: Any) -> Any:
            if _LibPowerAlgebra is None:
                raise TypeError("PowerAlgebra is not bound")
            if len(args) == 2:
                alg, power = args
                name = ""
            elif len(args) == 3:
                name, alg, power = args
            else:
                raise TypeError("PowerAlgebra() takes 2 or 3 arguments")
            # Java PowerAlgebra(alg, 0) hits ProductAlgebra.makeOperations IOBE.
            if int(power) == 0:
                raise IndexOutOfBoundsException(
                    "Index 0 out of bounds for length 0"
                )
            return _lib_call(
                _LibPowerAlgebra.new_with_name,
                str(name),
                _as_product_factor(alg),
                int(power),
            )

    class _QuotientAlgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibQuotientAlgebra is not None and isinstance(instance, _LibQuotientAlgebra)

    class QuotientAlgebra(object, metaclass=_QuotientAlgebraMeta):
        """``QuotientAlgebra(alg, cong)`` or ``QuotientAlgebra(name, alg, cong)``."""

        def __new__(cls, *args: Any) -> Any:
            if _LibQuotientAlgebra is None:
                raise TypeError("QuotientAlgebra is not bound")
            if len(args) == 2:
                alg, cong = args
                return _lib_call(_LibQuotientAlgebra, "", alg, cong)
            if len(args) == 3:
                name, alg, cong = args
                return _lib_call(_LibQuotientAlgebra, str(name), alg, cong)
            raise TypeError("QuotientAlgebra() takes 2 or 3 arguments")

    class _SubProductAlgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibSubProductAlgebra is not None and isinstance(
                instance, _LibSubProductAlgebra
            )

    class SubProductAlgebra(object, metaclass=_SubProductAlgebraMeta):
        """``SubProductAlgebra(name, prod, gens[, findTerms])``."""

        def __new__(cls, *args: Any) -> Any:
            if _LibSubProductAlgebra is None:
                raise TypeError("SubProductAlgebra is not bound")
            if len(args) == 3:
                name, prod, gens = args
                return _LibSubProductAlgebra(str(name), prod, list(gens), False)
            if len(args) == 4:
                name, prod, gens, find_terms = args
                return _LibSubProductAlgebra(str(name), prod, list(gens), bool(find_terms))
            if len(args) >= 5:
                name, prod, gens, find_terms = args[:4]
                return _LibSubProductAlgebra(str(name), prod, list(gens), bool(find_terms))
            raise TypeError("SubProductAlgebra() takes 3 or more arguments")

    class _BigProductAlgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibBigProductAlgebra is not None and isinstance(
                instance, _LibBigProductAlgebra
            )

    class BigProductAlgebra(object, metaclass=_BigProductAlgebraMeta):
        """Java constructor overloads over ``new_from_algebras`` / ``new_power``."""

        def __new__(cls, *args: Any) -> Any:
            if _LibBigProductAlgebra is None:
                raise TypeError("BigProductAlgebra is not bound")
            if len(args) == 1:
                return _LibBigProductAlgebra.new_from_algebras(_product_factors(args[0]))
            if len(args) == 2:
                a0, a1 = args
                if isinstance(a1, int) and not isinstance(a1, bool):
                    return _LibBigProductAlgebra.new_power(_unwrap_algebra(a0), int(a1))
                if isinstance(a0, (str, bytes)):
                    return _LibBigProductAlgebra.new_from_algebras_named(
                        str(a0), _product_factors(a1)
                    )
                # Java BigProductAlgebra(List, int[] powers).
                try:
                    powers = [int(x) for x in list(a1)]
                except (TypeError, ValueError):
                    powers = None
                if powers is not None:
                    expanded = []
                    for i, alg in enumerate(_product_factors(a0)):
                        copies = powers[i] if i < len(powers) else 1
                        for _ in range(int(copies)):
                            expanded.append(alg)
                    return _LibBigProductAlgebra.new_from_algebras(
                        expanded or _product_factors(a0)
                    )
                return _LibBigProductAlgebra.new_from_algebras(_product_factors(a0))
            if len(args) == 3:
                name, alg, power = args
                return _LibBigProductAlgebra.new_power_named(
                    str(name), _unwrap_algebra(alg), int(power)
                )
            raise TypeError("BigProductAlgebra() takes 1, 2, or 3 arguments")

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

    class _AlgebraFromMinimalSetsMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibAlgebraFromMinimalSets is not None and isinstance(
                instance, _LibAlgebraFromMinimalSets
            )

    class AlgebraFromMinimalSets(object, metaclass=_AlgebraFromMinimalSetsMeta):
        """Java constructor overloads over the Rust ``new_*`` factories."""

        def __new__(cls, *args: Any) -> Any:
            if _LibAlgebraFromMinimalSets is None:
                raise TypeError("AlgebraFromMinimalSets is not bound")
            if len(args) == 1:
                return _lib_call(_LibAlgebraFromMinimalSets, _as_product_factor(args[0]))
            if len(args) == 2:
                name, alg = args
                return _lib_call(
                    _LibAlgebraFromMinimalSets.new_with_name,
                    _as_product_factor(alg),
                    str(name) if name is not None else None,
                )
            if len(args) == 3:
                if isinstance(args[0], (str, bytes)) or args[0] is None:
                    name, alg, connect_pts = args
                    return _lib_call(
                        _LibAlgebraFromMinimalSets.new_with_connecting_pts,
                        _as_product_factor(alg),
                        str(name) if name is not None else None,
                        None if connect_pts is None else [int(x) for x in list(connect_pts)],
                    )
                min_alg, alg_size, maps = args
                return _lib_call(
                    _LibAlgebraFromMinimalSets.new_with_size,
                    _as_product_factor(min_alg),
                    int(alg_size),
                    None if maps is None else list(maps),
                )
            if len(args) == 5:
                name, alg, alg_size, maps, connect_pts = args
                return _lib_call(
                    _LibAlgebraFromMinimalSets.new_full,
                    _as_product_factor(alg),
                    int(alg_size),
                    str(name) if name is not None else None,
                    None if maps is None else list(maps),
                    None if connect_pts is None else [int(x) for x in list(connect_pts)],
                )
            raise TypeError("AlgebraFromMinimalSets() takes 1, 2, 3, or 5 arguments")

    class _MatrixPowerAlgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibMatrixPowerAlgebra is not None and isinstance(
                instance, _LibMatrixPowerAlgebra
            )

    class MatrixPowerAlgebra(object, metaclass=_MatrixPowerAlgebraMeta):
        """``MatrixPowerAlgebra(alg, power)`` or ``MatrixPowerAlgebra(name, alg, power)``."""

        def __new__(cls, *args: Any) -> Any:
            if _LibMatrixPowerAlgebra is None:
                raise TypeError("MatrixPowerAlgebra is not bound")
            if len(args) == 2:
                alg, power = args
                name = None
            elif len(args) == 3:
                name, alg, power = args
            else:
                raise TypeError("MatrixPowerAlgebra() takes 2 or 3 arguments")
            if int(power) == 0:
                raise IndexOutOfBoundsException(
                    "Index 0 out of bounds for length 0"
                )
            root = _as_product_factor(alg)
            if name is None or name == "":
                getter = getattr(root, "getName", None) or getattr(root, "name", None)
                root_name = getter() if callable(getter) else getter
                if root_name is None:
                    name = "{}-matrix pwoer".format(int(power))
                else:
                    name = "{}^[{}]".format(root_name, int(power))
            return _lib_call(
                _LibMatrixPowerAlgebra.new_with_name,
                str(name),
                root,
                int(power),
            )

    class _PolinLikeAlgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibPolinLikeAlgebra is not None and isinstance(
                instance, _LibPolinLikeAlgebra
            )

    class PolinLikeAlgebra(object, metaclass=_PolinLikeAlgebraMeta):
        """Java ``PolinLikeAlgebra(name, topAlg, botAlg, map, topConst, botConst)``."""

        def __new__(cls, *args: Any) -> Any:
            if _LibPolinLikeAlgebra is None:
                raise TypeError("PolinLikeAlgebra is not bound")
            if len(args) != 6:
                raise TypeError("PolinLikeAlgebra() takes 6 arguments")
            name, top, bot, mapping, top_const, bot_const = args
            return _lib_call(
                _LibPolinLikeAlgebra,
                str(name),
                _as_product_factor(top),
                _as_product_factor(bot),
                mapping,
                int(top_const),
                int(bot_const),
            )

        @staticmethod
        def constructPolinAlgebra(alg: Any, elem: Any) -> Any:
            # Java stub: both overloads end at the unimplemented int version.
            if _LibPolinLikeAlgebra is None:
                return None
            fn = getattr(_LibPolinLikeAlgebra, "construct_polin_algebra", None)
            if callable(fn):
                return _lib_call(fn, alg, elem)
            return None

    class _UnaryTermsMonoidMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibUnaryTermsMonoid is not None and isinstance(
                instance, _LibUnaryTermsMonoid
            )

    class UnaryTermsMonoid(object, metaclass=_UnaryTermsMonoidMeta):
        """``UnaryTermsMonoid(alg)`` or ``UnaryTermsMonoid(alg, includeId)``."""

        def __new__(cls, *args: Any) -> Any:
            if _LibUnaryTermsMonoid is None:
                raise TypeError("UnaryTermsMonoid is not bound")
            if len(args) == 1:
                return _lib_call(_LibUnaryTermsMonoid, _as_product_factor(args[0]))
            if len(args) == 2:
                return _lib_call(
                    _LibUnaryTermsMonoid.new_with_id,
                    _as_product_factor(args[0]),
                    bool(args[1]),
                )
            raise TypeError("UnaryTermsMonoid() takes 1 or 2 arguments")

    class _GeneralAlgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibGeneralAlgebra is not None and isinstance(
                instance, _LibGeneralAlgebra
            )

    class GeneralAlgebra(object, metaclass=_GeneralAlgebraMeta):
        """``GeneralAlgebra(name, univ)`` or ``GeneralAlgebra(name, univ, ops)``."""

        def __new__(cls, *args: Any) -> Any:
            if _LibGeneralAlgebra is None:
                raise TypeError("GeneralAlgebra is not bound")
            if len(args) == 2:
                name, univ = args
                return _lib_call(_LibGeneralAlgebra, str(name), list(univ), None)
            if len(args) == 3:
                name, univ, ops = args
                return _lib_call(
                    _LibGeneralAlgebra,
                    str(name),
                    list(univ),
                    None if ops is None else list(ops),
                )
            raise TypeError("GeneralAlgebra() takes 2 or 3 arguments")

    class _AlgebraWithGeneratingVectorMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibAlgebraWithGeneratingVector is not None and isinstance(
                instance, _LibAlgebraWithGeneratingVector
            )

    class AlgebraWithGeneratingVector(object, metaclass=_AlgebraWithGeneratingVectorMeta):
        """``AlgebraWithGeneratingVector(alg, vec)``."""

        def __new__(cls, *args: Any) -> Any:
            if _LibAlgebraWithGeneratingVector is None:
                raise TypeError("AlgebraWithGeneratingVector is not bound")
            if len(args) != 2:
                raise TypeError("AlgebraWithGeneratingVector() takes 2 arguments")
            alg, vec = args
            if vec is None:
                _raise_npe()
            return _lib_call(
                _LibAlgebraWithGeneratingVector,
                _as_product_factor(alg),
                [int(x) for x in list(vec)],
            )

        @staticmethod
        def siDecompose(alg: Any, vec: Any, relations: Any = None) -> Any:
            if _LibAlgebraWithGeneratingVector is None:
                raise TypeError("AlgebraWithGeneratingVector is not bound")
            if vec is None:
                _raise_npe()
            vec_list = [int(x) for x in list(vec)]
            if relations is None:
                return _lib_call(
                    _LibAlgebraWithGeneratingVector.si_decompose,
                    _as_product_factor(alg),
                    vec_list,
                )
            rels = list(relations)
            if not rels:
                return _lib_call(
                    _LibAlgebraWithGeneratingVector.si_decompose,
                    _as_product_factor(alg),
                    vec_list,
                )
            return _lib_call(
                _LibAlgebraWithGeneratingVector.si_decompose_with_relations,
                _as_product_factor(alg),
                vec_list,
                rels,
            )

    class ParameterizedAlgebra(object):
        """Java default constructor plus package-private fields Jython can set."""

        def __init__(self, *args: Any) -> None:
            if len(args) == 0:
                self.parameterNames = None
                self.name = None
                self.setSizeExp = None
                self.description = None
                self.ops = None
                self._inner = None
                return
            if len(args) == 5 and _LibParameterizedAlgebra is not None:
                names, name, set_size_exp, description, ops = args
                self.parameterNames = list(names) if names is not None else None
                self.name = name
                self.setSizeExp = set_size_exp
                self.description = description
                self.ops = ops
                self._inner = _lib_call(
                    _LibParameterizedAlgebra,
                    [] if names is None else list(names),
                    "" if name is None else str(name),
                    "" if set_size_exp is None else str(set_size_exp),
                    "" if description is None else str(description),
                    [] if ops is None else list(ops),
                )
                return
            raise TypeError("ParameterizedAlgebra() takes 0 or 5 arguments")

        def getParameterMap(self, values: Any) -> Any:
            if self.parameterNames is None:
                _raise_npe()
            iterator = iter([] if values is None else list(values))
            out = {}
            try:
                for name in list(self.parameterNames):
                    out[str(name)] = str(int(next(iterator)))
            except StopIteration:
                raise NoSuchElementException()
            return out

    class _SubalgebraMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibSubalgebra is not None and isinstance(instance, _LibSubalgebra)

    class Subalgebra(object, metaclass=_SubalgebraMeta):
        """``Subalgebra(alg, univ)`` or ``Subalgebra(name, alg, univ)``."""

        def __new__(cls, *args: Any) -> Any:
            if _LibSubalgebra is None:
                raise TypeError("Subalgebra is not bound")
            if len(args) == 2:
                alg, univ = args
                name = ""
            elif len(args) == 3:
                name, alg, univ = args
            else:
                raise TypeError("Subalgebra() takes 2 or 3 arguments")
            return _lib_call(
                _LibSubalgebra, str(name), alg, _as_universe_indices(univ)
            )

        @staticmethod
        def congruenceAsAlgebra(*args: Any) -> Any:
            if _LibSubalgebra is None:
                raise TypeError("Subalgebra is not bound")
            if len(args) == 2:
                alg, cong = args
                return _lib_call(
                    _LibSubalgebra.congruence_as_algebra, _unwrap_algebra(alg), cong
                )
            if len(args) == 3:
                name, alg, cong = args
                return _lib_call(
                    _LibSubalgebra.congruence_as_algebra_with_name,
                    str(name),
                    _unwrap_algebra(alg),
                    cong,
                )
            raise TypeError("congruenceAsAlgebra() takes 2 or 3 arguments")

    class _ReductAlgebraClassMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibReductAlgebra is not None and isinstance(
                instance, _LibReductAlgebra
            )

    class ReductAlgebra(object, metaclass=_ReductAlgebraClassMeta):
        """``ReductAlgebra(alg, terms)`` or ``ReductAlgebra(name, alg, terms)``."""

        def __new__(cls, *args: Any) -> Any:
            return _reduct_algebra(*args)

        @staticmethod
        def congruenceAsAlgebra(*args: Any) -> Any:
            return Subalgebra.congruenceAsAlgebra(*args)

    class _HomomorphismMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibHomomorphism is not None and isinstance(
                instance, _LibHomomorphism
            )

    class Homomorphism(object, metaclass=_HomomorphismMeta):
        """Java ``Homomorphism(domain, range, map)``."""

        def __new__(cls, domain: Any, range_alg: Any, mapping: Any) -> Any:
            if _LibHomomorphism is None:
                raise TypeError("Homomorphism is not bound")
            # Java stores null domain/range/map; toString NPEs on a null domain.
            if domain is None:
                _raise_npe()
            if range_alg is None:
                _raise_npe()
            raw = {}
            if mapping is not None:
                items = mapping.items() if hasattr(mapping, "items") else mapping
                for item in items:
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        k, v = item
                    else:
                        k, v = item, mapping[item]
                    raw[int(k)] = int(v)
            return _LibHomomorphism.new_java(
                _as_basic_algebra(domain), _as_basic_algebra(range_alg), raw
            )

        @staticmethod
        def productHomo(lst: Any) -> Any:
            if lst is None:
                _raise_npe()
            items = list(lst)
            if not items:
                raise IndexOutOfBoundsException(
                    "Index 0 out of bounds for length 0"
                )
            rows = _lib_call(_LibHomomorphism.product_homo, items)
            out = []
            for row in rows:
                if _is_int_array(row):
                    out.append(row)
                else:
                    out.append(_int_array(row))
            return out

    _CLOSER_ORIG_CLOSE = [None]

    class _CloserMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if type(instance) is cls:
                return True
            return _LibCloser is not None and isinstance(instance, _LibCloser)

    class Closer(object, metaclass=_CloserMeta):
        """Java ``Closer(alg, gens)`` / term-map / makeTermMap overloads."""

        def __init__(self, algebra: Any, generators: Any, third: Any = None) -> None:
            if _LibCloser is None:
                raise TypeError("Closer is not bound")
            # Java Closer(null, gens) stores the algebra and only NPEs later.
            # setGenerators(null) NPEs while iterating gens.
            if generators is None:
                _raise_npe()
            if algebra is None:
                _raise_npe()
            gens = [_int_array(g) for g in list(generators)]
            if third is None:
                inner = _lib_call(_LibCloser, algebra, gens)
            elif isinstance(third, bool):
                inner = _lib_call(
                    _LibCloser.new_with_make_term_map, algebra, gens, third
                )
            else:
                inner = _lib_call(
                    _LibCloser.new_with_term_map, algebra, gens, third
                )
            self._inner = inner
            self._ans = None
            self._ans_set = False

        def __getattr__(self, item: str) -> Any:
            return getattr(self._inner, item)

        def getAnswer(self) -> Any:
            return self._ans if self._ans_set else None

        doParallel = False

        def sgClose(self, elems: Any = None, closedMark: Any = None, termMap: Any = None) -> Any:
            # Java Closer.doParallel routes no-arg sgClose() through sgCloseParallel.
            if elems is None and closedMark is None and termMap is None:
                if getattr(Closer, "doParallel", False):
                    fn = getattr(self._inner, "sg_close_parallel", None)
                    if callable(fn):
                        self._ans = _lib_call(fn)
                        self._ans_set = True
                        return self._ans
                self._ans = _lib_call(self._inner.sg_close)
                self._ans_set = True
                return self._ans
            if termMap is not None:
                setter = getattr(self._inner, "set_term_map", None) or getattr(
                    self._inner, "setTermMap", None
                )
                if callable(setter):
                    setter(termMap)
            fn = getattr(self._inner, "sg_close_from", None)
            if not callable(fn):
                raise TypeError("sgClose(elems, closedMark, termMap) is not bound")
            mark = 0 if closedMark is None else int(closedMark)
            self._ans = _lib_call(fn, elems, mark)
            self._ans_set = True
            return self._ans

        def sgCloseParallel(self, elems: Any = None, closedMark: Any = None, termMap: Any = None) -> Any:
            """No-arg form uses the library parallel closer on the stored gens.

            The Java 3-arg ``(elems, closedMark, ConcurrentMap)`` overload is
            wrapped as the matching serial ``sgClose`` element-set path
            (thread/timing internals are not compared).
            """
            if elems is not None or closedMark is not None or termMap is not None:
                return sgClose(self, elems, closedMark, termMap)
            fn = getattr(self._inner, "sg_close_parallel", None)
            if not callable(fn):
                raise TypeError("sgCloseParallel is not bound")
            self._ans = _lib_call(fn)
            self._ans_set = True
            return self._ans

        def sgClosePower(self) -> Any:
            self._ans = _lib_call(self._inner.sg_close_power)
            self._ans_set = True
            return self._ans

        def close(self) -> Any:
            orig = getattr(self._inner, "close")
            # Prefer the original PyO3 close; fall back if already wrapped.
            self._ans = _lib_call(_CLOSER_ORIG_CLOSE[0] or orig, self._inner)
            self._ans_set = True
            return self._ans

        def getmaxSize(self) -> int:
            return closerGetmaxSize(self._inner)

        def setMaxSize(self, k: Any) -> None:
            closerSetMaxSize(self._inner, k)

        def getGenerators(self) -> Any:
            return closerGetGenerators(self._inner)

        def setGenerators(self, gens: Any) -> None:
            closerSetGenerators(self._inner, gens)

        def getTermMap(self) -> Any:
            return closerGetTermMap(self._inner)

        def setTermMap(self, term_map: Any) -> None:
            closerSetTermMap(self._inner, term_map)

        def getElementToFind(self) -> Any:
            return closerGetElementToFind(self._inner)

        def setElementToFind(self, e: Any) -> None:
            closerSetElementToFind(self._inner, e)

        def getElementsToFind(self) -> Any:
            return closerGetElementsToFind(self._inner)

        def setElementsToFind(self, elts: Any, gens: Any = None) -> None:
            closerSetElementsToFind(self._inner, elts, gens)

        def allElementsFound(self) -> bool:
            return closerAllElementsFound(self._inner)

        def getBlocks(self) -> Any:
            return closerGetBlocks(self._inner)

        def setBlocks(self, blocks: Any) -> None:
            closerSetBlocks(self._inner, blocks)

        def getValues(self) -> Any:
            return closerGetValues(self._inner)

        def setValues(self, values: Any) -> None:
            closerSetValues(self._inner, values)

        def getSetConstraint(self) -> Any:
            return closerGetSetConstraint(self._inner)

        def setConstraintSet(self, s: Any) -> None:
            closerSetConstraintSet(self._inner, s)

        def getIndexForConstraintSet(self) -> int:
            return closerGetIndexForConstraintSet(self._inner)

        def setIndexForConstraintSet(self, k: Any) -> None:
            closerSetIndexForConstraintSet(self._inner, k)

        def getIndexForCongruenceConstraint(self) -> int:
            return closerGetIndexForCongruenceConstraint(self._inner)

        def setIndexForCongruenceConstraint(self, k: Any) -> None:
            closerSetIndexForCongruenceConstraint(self._inner, k)

        def getCongruenceConstraintElemIndex(self) -> int:
            return closerGetCongruenceConstraintElemIndex(self._inner)

        def setCongruenceConstraintElemIndex(self, k: Any) -> None:
            closerSetCongruenceConstraintElemIndex(self._inner, k)

        def getCongruenceForCongruenceConstraint(self) -> Any:
            return closerGetCongruenceForCongruenceConstraint(self._inner)

        def setCongruenceForCongruenceConstraint(self, alpha: Any) -> None:
            closerSetCongruenceForCongruenceConstraint(self._inner, alpha)

        def setupCongruenceConstraint(self, alpha: Any, index: Any, elemIndex: Any) -> None:
            closerSetupCongruenceConstraint(self._inner, alpha, index, elemIndex)

        def getFailingEquation(self) -> Any:
            return closerGetFailingEquation(self._inner)

        def getImageAlgebra(self) -> Any:
            return closerGetImageAlgebra(self._inner)

        def setImageAlgebra(self, alg: Any) -> None:
            closerSetImageAlgebra(self._inner, alg)

        def getHomomorphism(self) -> Any:
            return closerGetHomomorphism(self._inner)

        def setHomomorphism(self, arg: Any) -> None:
            closerSetHomomorphism(self._inner, arg)

        def getTermMapForOperations(self) -> Any:
            return closerGetTermMapForOperations(self._inner)

        def setRootAlgebra(self, alg: Any) -> None:
            closerSetRootAlgebra(self._inner, alg)

        def setOperations(self, ops: Any) -> None:
            closerSetOperations(self._inner, ops)

        def isSuppressOutput(self) -> bool:
            return closerIsSuppressOutput(self._inner)

        def setSuppressOutput(self, suppress: Any) -> None:
            closerSetSuppressOutput(self._inner, suppress)

    def _algebras_fn(name: str) -> Any:
        fn = alg_module_globals.get(name)
        if fn is None:
            raise TypeError("Algebras.{} is not bound".format(name))
        return fn

    class Algebras(object):
        """Static facade matching Java ``org.uacalc.alg.Algebras``."""

        @staticmethod
        def isEndomorphism(endo: Any, alg: Any) -> bool:
            if endo is None or alg is None:
                _raise_npe()
            return bool(
                _lib_call(_algebras_fn("is_endomorphism"), endo, _as_basic_algebra(alg))
            )

        @staticmethod
        def isHomomorphism(mapping: Any, alg0: Any, alg1: Any) -> bool:
            if mapping is None or alg0 is None or alg1 is None:
                _raise_npe()
            return bool(
                _lib_call(
                    _algebras_fn("is_homomorphism"),
                    [int(x) for x in list(mapping)],
                    _as_basic_algebra(alg0),
                    _as_basic_algebra(alg1),
                )
            )

        @staticmethod
        def matrixPower(alg: Any, k: Any) -> Any:
            if alg is None:
                _raise_npe()
            if int(k) == 0:
                raise IndexOutOfBoundsException(
                    "Index 0 out of bounds for length 0"
                )
            return _lib_call(
                _algebras_fn("matrix_power"), _as_basic_algebra(alg), int(k)
            )

        @staticmethod
        def fullTransformationSemigroup(
            n: Any, includeConstants: Any, includeId: Any
        ) -> Any:
            return _lib_call(
                _algebras_fn("full_transformation_semigroup"),
                int(n),
                bool(includeConstants),
                bool(includeId),
            )

        @staticmethod
        def ternaryDiscriminatorAlgebra(card: Any) -> Any:
            return _lib_call(
                _algebras_fn("ternary_discriminator_algebra"), int(card)
            )

        @staticmethod
        def makeRandomAlgebra(*args: Any) -> Any:
            # Java: (n, simType), (n, simType, seed), (n, arities), (n, arities, seed)
            if len(args) == 2:
                n, second = args
                if second is None:
                    _raise_npe()
                if isinstance(second, (list, tuple)):
                    return _lib_call(
                        _algebras_fn("make_random_algebra_with_arities"),
                        int(n),
                        [int(x) for x in list(second)],
                    )
                return _lib_call(
                    _algebras_fn("make_random_algebra"), int(n), second
                )
            if len(args) == 3:
                n, second, seed = args
                if second is None:
                    _raise_npe()
                if isinstance(second, (list, tuple)):
                    return _lib_call(
                        _algebras_fn("make_random_algebra_with_arities_and_seed"),
                        int(n),
                        [int(x) for x in list(second)],
                        int(seed),
                    )
                return _lib_call(
                    _algebras_fn("make_random_algebra_with_seed"),
                    int(n),
                    second,
                    int(seed),
                )
            raise TypeError("makeRandomAlgebra() takes 2 or 3 arguments")

        @staticmethod
        def findInClone(ops: Any, alg: Any, report: Any = None) -> Any:
            if ops is None or alg is None:
                raise IllegalArgumentException(
                    "ops cannot be empty and the algebra cannot be null"
                )
            op_list = list(ops)
            if not op_list:
                raise IllegalArgumentException(
                    "ops cannot be empty and the algebra cannot be null"
                )
            if report is not None:
                raise TypeError(
                    "findInClone(): expected org.uacalc.ui.tm.ProgressReport or None"
                )
            return _lib_call(
                _algebras_fn("find_in_clone"), op_list, _as_basic_algebra(alg)
            )

        @staticmethod
        def memberOfQuasivariety(a: Any, b_or_list: Any, report: Any = None) -> Any:
            if a is None or b_or_list is None:
                _raise_npe()
            if report is not None:
                raise TypeError(
                    "memberOfQuasivariety(): expected org.uacalc.ui.tm.ProgressReport or None"
                )
            # Java: (A, B, report) vs (A, List, report). A list of algebras is not
            # a SmallAlgebra; a single algebra is not a List.
            if isinstance(b_or_list, (list, tuple)):
                algs = [_as_basic_algebra(x) for x in list(b_or_list)]
                return _lib_call(
                    _algebras_fn("member_of_quasivariety_list"),
                    _as_basic_algebra(a),
                    algs,
                )
            return _lib_call(
                _algebras_fn("member_of_quasivariety"),
                _as_basic_algebra(a),
                _as_basic_algebra(b_or_list),
            )

        @staticmethod
        def memberOfQuasivarietyGenByProperSubs(a: Any, report: Any = None) -> Any:
            if a is None:
                _raise_npe()
            if report is not None:
                raise TypeError(
                    "memberOfQuasivarietyGenByProperSubs(): expected "
                    "org.uacalc.ui.tm.ProgressReport or None"
                )
            return _lib_call(
                _algebras_fn("member_of_quasivariety_gen_by_proper_subs"),
                _as_basic_algebra(a),
            )

        @staticmethod
        def quasiCriticalCongruences(a: Any, report: Any = None) -> Any:
            if a is None:
                _raise_npe()
            if report is not None:
                raise TypeError(
                    "quasiCriticalCongruences(): expected "
                    "org.uacalc.ui.tm.ProgressReport or None"
                )
            return _lib_call(
                _algebras_fn("quasi_critical_congruences"), _as_basic_algebra(a)
            )

        @staticmethod
        def quasiCritical(a: Any, report: Any = None) -> Any:
            if a is None:
                _raise_npe()
            if report is not None:
                raise TypeError(
                    "quasiCritical(): expected org.uacalc.ui.tm.ProgressReport or None"
                )
            return _lib_call(_algebras_fn("quasi_critical"), _as_basic_algebra(a))

        @staticmethod
        def unaryClone(pars: Any, eta0: Any, eta1: Any) -> Any:
            if pars is None or eta0 is None or eta1 is None:
                _raise_npe()
            return _lib_call(
                _algebras_fn("unary_clone"), list(pars), eta0, eta1
            )

        @staticmethod
        def unaryCloneAlgFromPartitions(*args: Any) -> Any:
            # Java (pars, decomp) is incomplete and always returns null.
            if len(args) == 2:
                pars, decomp = args
                if pars is None or decomp is None:
                    _raise_npe()
                return None
            if len(args) == 3:
                pars, eta0, eta1 = args
                if pars is None or eta0 is None or eta1 is None:
                    _raise_npe()
                return _lib_call(
                    _algebras_fn("unary_clone_alg_from_partitions"),
                    list(pars),
                    eta0,
                    eta1,
                )
            raise TypeError("unaryCloneAlgFromPartitions() takes 2 or 3 arguments")

        @staticmethod
        def findNUF(alg: Any, arity: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "findNUF")
            return Malcev.nuTerm(alg, arity)

        @staticmethod
        def jonssonTerms(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "jonssonTerms")
            return Malcev.jonssonTerms(alg)

        @staticmethod
        def jonssonLevel(alg: Any) -> Any:
            if alg is None:
                _raise_npe()
            return Malcev.jonssonLevel(alg)

    def _reject_progress_report(report: Any, name: str) -> None:
        if report is not None:
            raise TypeError(
                "{}(): expected org.uacalc.ui.tm.ProgressReport or None".format(name)
            )

    def _malcev_fn(name: str) -> Any:
        fn = alg_module_globals.get(name)
        if fn is None:
            raise TypeError("Malcev.{} is not bound".format(name))
        return fn

    class Malcev(object):
        """Static facade matching Java ``org.uacalc.alg.Malcev``.

        ProgressReport overloads accept ``None`` only. ``main`` is not wrapped.
        """

        @staticmethod
        def malcevTerm(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "malcevTerm")
            return _lib_call(_malcev_fn("malcev_term"), _as_basic_algebra(alg))

        @staticmethod
        def majorityTerm(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "majorityTerm")
            return _lib_call(_malcev_fn("majority_term"), _as_basic_algebra(alg))

        @staticmethod
        def minorityTerm(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "minorityTerm")
            return _lib_call(_malcev_fn("minority_term"), _as_basic_algebra(alg))

        @staticmethod
        def pixleyTerm(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "pixleyTerm")
            return _lib_call(_malcev_fn("pixley_term"), _as_basic_algebra(alg))

        @staticmethod
        def nuTerm(alg: Any, arity: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "nuTerm")
            return _lib_call(
                _malcev_fn("nu_term"), _as_basic_algebra(alg), int(arity)
            )

        @staticmethod
        def nuTermIdempotent(alg: Any, arity: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "nuTermIdempotent")
            return bool(
                _lib_call(
                    _malcev_fn("nu_term_idempotent"),
                    _as_basic_algebra(alg),
                    int(arity),
                )
            )

        @staticmethod
        def weakNUTerm(alg: Any, arity: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "weakNUTerm")
            return _lib_call(
                _malcev_fn("weak_nu_term"), _as_basic_algebra(alg), int(arity)
            )

        @staticmethod
        def findWeakNUTerm(alg: Any, arity: Any, report: Any = None) -> Any:
            return Malcev.weakNUTerm(alg, arity, report)

        @staticmethod
        def weakMajorityTerm(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "weakMajorityTerm")
            return _lib_call(
                _malcev_fn("weak_majority_term"), _as_basic_algebra(alg)
            )

        @staticmethod
        def semilatticeTerm(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "semilatticeTerm")
            return _lib_call(
                _malcev_fn("semilattice_term"), _as_basic_algebra(alg)
            )

        @staticmethod
        def differenceTerm(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "differenceTerm")
            return _lib_call(
                _malcev_fn("difference_term"), _as_basic_algebra(alg)
            )

        @staticmethod
        def jonssonTerms(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "jonssonTerms")
            return _lib_call(_malcev_fn("jonsson_terms"), _as_basic_algebra(alg))

        @staticmethod
        def hagemannMitschkeTerms(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "hagemannMitschkeTerms")
            return _lib_call(
                _malcev_fn("hagemann_mitschke_terms"), _as_basic_algebra(alg)
            )

        @staticmethod
        def gummTerms(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "gummTerms")
            return _lib_call(_malcev_fn("gumm_terms"), _as_basic_algebra(alg))

        @staticmethod
        def joinTerm(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "joinTerm")
            return _lib_call(_malcev_fn("join_term"), _as_basic_algebra(alg))

        @staticmethod
        def sdmeetTerms(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "sdmeetTerms")
            return _lib_call(_malcev_fn("sd_meet_terms"), _as_basic_algebra(alg))

        @staticmethod
        def sdTerms(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "sdTerms")
            return _lib_call(_malcev_fn("sd_terms"), _as_basic_algebra(alg))

        @staticmethod
        def markovicMcKenzieSiggersTaylorTerm(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "markovicMcKenzieSiggersTaylorTerm")
            return _lib_call(
                _malcev_fn("markovic_mckenzie_siggers_taylor_term"),
                _as_basic_algebra(alg),
            )

        @staticmethod
        def weak3EdgeTerm(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "weak3EdgeTerm")
            return _lib_call(
                _malcev_fn("weak_3_edge_term"), _as_basic_algebra(alg)
            )

        @staticmethod
        def isCongruenceDistIdempotent(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "isCongruenceDistIdempotent")
            return bool(
                _lib_call(
                    _malcev_fn("is_congruence_dist_idempotent"),
                    _as_basic_algebra(alg),
                )
            )

        @staticmethod
        def isCongruenceModularIdempotent(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "isCongruenceModularIdempotent")
            return bool(
                _lib_call(
                    _malcev_fn("is_congruence_modular_idempotent"),
                    _as_basic_algebra(alg),
                )
            )

        @staticmethod
        def congruenceModularVariety(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "congruenceModularVariety")
            return bool(
                _lib_call(
                    _malcev_fn("congruence_modular_variety"),
                    _as_basic_algebra(alg),
                )
            )

        @staticmethod
        def jonssonLevel(alg: Any) -> Any:
            if alg is None:
                _raise_npe()
            return int(
                _lib_call(_malcev_fn("jonsson_level"), _as_basic_algebra(alg))
            )

        @staticmethod
        def localDistributivityLevel(a: Any, b: Any, c: Any, alg: Any) -> Any:
            if alg is None:
                _raise_npe()
            return int(
                _lib_call(
                    _malcev_fn("local_distributivity_level"),
                    int(a),
                    int(b),
                    int(c),
                    _as_basic_algebra(alg),
                )
            )

        @staticmethod
        def findDayQuadrupleInSquare(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "findDayQuadrupleInSquare")
            return _lib_call(
                _malcev_fn("find_day_quadruple_in_square"),
                _as_basic_algebra(alg),
            )

        @staticmethod
        def sdMeetIdempotent(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "sdMeetIdempotent")
            return _lib_call(
                _malcev_fn("sd_meet_idempotent"), _as_basic_algebra(alg)
            )

        @staticmethod
        def dayQuadruple(a: Any, b: Any, c: Any, d: Any, alg: Any) -> Any:
            if alg is None:
                _raise_npe()
            con = alg.con()
            cgcd = con.Cg(int(c), int(d))
            cgab_cd = con.Cg(int(a), int(b)).join(cgcd)
            cgac_bd = con.Cg(int(a), int(c)).join(con.Cg(int(b), int(d)))
            return not cgcd.join(cgab_cd.meet(cgac_bd)).isRelated(int(a), int(b))

        @staticmethod
        def cyclicTermIdempotent(alg: Any, arity: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "cyclicTermIdempotent")
            return bool(
                _lib_call(
                    _malcev_fn("cyclic_term_idempotent"),
                    _as_basic_algebra(alg),
                    int(arity),
                )
            )

        @staticmethod
        def primalityTerms(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "primalityTerms")
            return _lib_call(
                _malcev_fn("primality_terms"), _as_basic_algebra(alg)
            )

        @staticmethod
        def fixedKEdgeTerm(alg: Any, k: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "fixedKEdgeTerm")
            return _lib_call(
                _malcev_fn("fixed_k_edge_term"),
                _as_basic_algebra(alg),
                int(k),
            )

        @staticmethod
        def fixedKQwnu(alg: Any, arity: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "fixedKQwnu")
            return bool(
                _lib_call(
                    _malcev_fn("fixed_k_qwnu"),
                    _as_basic_algebra(alg),
                    int(arity),
                )
            )

        @staticmethod
        def congruenceModularForIdempotent(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "congruenceModularForIdempotent")
            return Malcev.findDayQuadrupleInSquare(alg, None) is None

        @staticmethod
        def makeCyclicGens(v: Any) -> Any:
            if v is None:
                _raise_npe()
            from org.uacalc.util import IntArray

            u = [int(x) for x in list(v)]
            k = len(u)
            ans = [IntArray(list(u))]
            # Java adds inside the inner loop while sharing one backing array,
            # so each shift contributes k copies of the fully filled vector.
            for i in range(1, k):
                w = [u[(j + i) % k] for j in range(k)]
                for _ in range(k):
                    ans.append(IntArray(list(w)))
            return ans

        @staticmethod
        def typesInSofAStrictlySimpleIdempotent(
            alg: Any, typesFound: Any, report: Any = None
        ) -> Any:
            if alg is None or typesFound is None:
                _raise_npe()
            _reject_progress_report(report, "typesInSofAStrictlySimpleIdempotent")
            alg = _as_basic_algebra(alg)
            n = int(alg.cardinality())
            for a in range(n):
                for b in range(a + 1, n):
                    B = alg.sub().Sg([a, b])
                    a_in_b = int(B.index(a))
                    b_in_b = int(B.index(b))
                    one = B.con().one()
                    if not B.con().Cg(a_in_b, b_in_b).equals(one):
                        continue
                    if not B.con().joinIrreducible(one):
                        continue
                    typesFound.add(int(B.con().typeJI(one, None)))
            return typesFound

        @staticmethod
        def typesInSofAIdempotent(alg: Any, typesFound: Any, report: Any = None) -> Any:
            if alg is None or typesFound is None:
                _raise_npe()
            _reject_progress_report(report, "typesInSofAIdempotent")
            from org.uacalc.alg import QuotientAlgebra

            decomp = list(alg.con().irredundantMeetDecomposition())
            for th in decomp:
                Malcev.typesInSofAStrictlySimpleIdempotent(
                    QuotientAlgebra(alg, th), typesFound, None
                )
            return typesFound

        @staticmethod
        def typesInSofAIRobustDecompdempotent(
            alg: Any, typesFound: Any, report: Any = None
        ) -> Any:
            if alg is None or typesFound is None:
                _raise_npe()
            _reject_progress_report(report, "typesInSofAIRobustDecompdempotent")
            if int(alg.cardinality()) == 1:
                return typesFound
            from org.uacalc.alg import MaltsevProductDecomposition

            coatom = alg.con().findCoatomAbove(alg.con().zero())
            decomp = MaltsevProductDecomposition(_as_basic_algebra(alg), coatom)
            Malcev.typesInSofAStrictlySimpleIdempotent(
                decomp.getQuotientAlgebra(), typesFound, None
            )
            for blk in decomp.getBlockAlgebras():
                if int(blk.cardinality()) > 1:
                    Malcev.typesInSofAIdempotent(blk, typesFound, None)
            return typesFound

        @staticmethod
        def omittedIdealIdempotent(alg: Any, typesFound=None, report: Any = _MISSING) -> Any:
            if alg is None:
                _raise_npe()
            # Java: (alg, report) vs (alg, typesFound, report).
            if report is _MISSING:
                report = typesFound
                typesFound = None
                _reject_progress_report(report, "omittedIdealIdempotent")
                found = set()
                Malcev.typesInSofAStrictlySimpleIdempotent(alg, found, None)
                typesFound = found
            else:
                _reject_progress_report(report, "omittedIdealIdempotent")
                if typesFound is None:
                    _raise_npe()
            ans = set()
            if 1 not in typesFound:
                ans.add(1)
                if 2 not in typesFound:
                    ans.add(2)
                if 5 not in typesFound:
                    ans.add(5)
                    if 4 not in typesFound:
                        ans.add(4)
            return ans

        @staticmethod
        def typeSetIdempotent(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "typeSetIdempotent")
            # Match Java including the types1.add(2) bug that aliases {1,2}.
            types12 = set([1, 2])
            types1 = set([1])
            types2 = set()
            types1.add(2)
            types_of_a = set(int(x) for x in alg.con().typeSet())
            if types_of_a == types1:
                return [set(types1), set(types1)]
            if types_of_a == types12:
                return [set(types12), set(types12)]
            types_found = set()
            Malcev.typesInSofAIdempotent(alg, types_found, None)
            if types_of_a == types2:
                if 1 in types_found:
                    return [set(types12), set(types12)]
                return [set(types2), set(types2)]
            possible = set([1, 2, 3, 4, 5])
            types_found = set(types_found)
            types_found.update(types_of_a)
            ans = [types_found]
            if 1 in types_found:
                ans.append(possible)
                return ans
            possible.discard(1)
            if 5 in types_found:
                if 2 in types_found:
                    ans.append(possible)
                    return ans
                possible.discard(2)
                ans.append(possible)
                return ans
            possible.discard(5)
            if 3 in types_found:
                ans.append(set(types_found))
                return ans
            upper = set(types_found)
            upper.add(3)
            ans.append(upper)
            return ans

        @staticmethod
        def cubeTermBlockerIdempotent(*args: Any) -> Any:
            if not args:
                raise TypeError("cubeTermBlockerIdempotent() takes at least 1 argument")
            first = args[0]
            tname = type(first).__name__ if first is not None else ""
            if first is not None and (
                "Algebra" in tname or hasattr(first, "cardinality")
            ):
                if len(args) == 2 or (len(args) == 3 and args[2] is None):
                    alg, report = args[0], args[1] if len(args) > 1 else None
                    _reject_progress_report(report, "cubeTermBlockerIdempotent")
                    return _cube_term_blocker_alg(alg)
                if len(args) >= 3:
                    alg, C, D = args[0], args[1], args[2]
                    if alg is None or C is None or D is None:
                        _raise_npe()
                    for op in alg.operations():
                        if _cube_term_blocker_op(op, C, D) < 0:
                            return False
                    return True
            if len(args) == 3:
                op, C, D = args
                if op is None or C is None or D is None:
                    _raise_npe()
                return _cube_term_blocker_op(op, C, D)
            if len(args) == 4:
                op, j, C, D = args
                if op is None or C is None or D is None:
                    _raise_npe()
                return _cube_term_blocker_at(op, int(j), C, D)
            raise TypeError("cubeTermBlockerIdempotent() argument mismatch")

        @staticmethod
        def sdIdempotent(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "sdIdempotent")
            from org.uacalc.alg import BigProductAlgebra, SubProductAlgebra
            from org.uacalc.util import IntArray

            n = int(alg.cardinality())
            sq = BigProductAlgebra(alg, 2)
            a = IntArray(2)
            b = IntArray(2)
            c = IntArray(2)
            gens = [a, b, c]
            for x in range(n):
                for y in range(n):
                    if x == y:
                        continue
                    a.set(0, x)
                    a.set(1, x)
                    b.set(0, x)
                    b.set(1, y)
                    c.set(0, y)
                    c.set(1, x)
                    sub = SubProductAlgebra("", sq, gens)
                    a_i = int(sub.elementIndex(a))
                    b_i = int(sub.elementIndex(b))
                    c_i = int(sub.elementIndex(c))
                    alpha = sub.con().Cg(a_i, c_i)
                    beta = sub.con().Cg(a_i, b_i)
                    gamma = sub.con().Cg(b_i, c_i)
                    if not alpha.meet(beta).join(gamma).isRelated(a_i, c_i):
                        return IntArray([x, y])
            return None

        @staticmethod
        def cpIdempotent(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "cpIdempotent")
            from org.uacalc.alg import BigProductAlgebra, SubProductAlgebra
            from org.uacalc.util import IntArray

            n = int(alg.cardinality())
            if n == 1:
                return None
            sq = BigProductAlgebra(alg, 2)
            a = IntArray(2)
            b = IntArray(2)
            c = IntArray(2)
            gens = [a, b, c]
            for x0 in range(n):
                for y0 in range(n):
                    for x1 in range(n):
                        for y1 in range(n):
                            a.set(0, x0)
                            a.set(1, y0)
                            b.set(0, x0)
                            b.set(1, y1)
                            c.set(0, x1)
                            c.set(1, y1)
                            if a.equals(b) or a.equals(c) or b.equals(c):
                                continue
                            sub = SubProductAlgebra("", sq, gens)
                            a_i = int(sub.elementIndex(a))
                            b_i = int(sub.elementIndex(b))
                            c_i = int(sub.elementIndex(c))
                            alpha = sub.con().Cg(a_i, b_i)
                            beta = sub.con().Cg(b_i, c_i)
                            compose = getattr(alpha, "compose", None)
                            related = compose(beta) if callable(compose) else None
                            if related is None or not related.isRelated(c_i, a_i):
                                return IntArray([x0, y0, x1, y1])
            return None

        @staticmethod
        def sdPath(subalg: Any, g0: Any, g2: Any) -> Any:
            if subalg is None or g0 is None or g2 is None:
                _raise_npe()
            from org.uacalc.util import IntArray

            def _vals(ia: Any) -> list:
                getter = getattr(ia, "getArray", None) or getattr(ia, "to_array", None)
                if callable(getter):
                    return [int(x) for x in getter()]
                return [int(x) for x in list(ia)]

            def _key(ia: Any):
                return tuple(_vals(ia))

            parent = {_key(g0): None}
            current = [g0]
            classes01 = {}
            classes2 = {}
            univ_fn = getattr(subalg, "getUniverseList", None) or getattr(
                subalg, "get_universe_list", None
            )
            universe_elems = list(univ_fn()) if callable(univ_fn) else list(subalg)
            for ia in universe_elems:
                vals = _vals(ia)
                k01 = (vals[0], vals[1])
                classes01.setdefault(k01, []).append(ia)
                classes2.setdefault(vals[2], []).append(ia)
            even = False
            first = True
            while True:
                even = not even
                next_level = []
                for ia in current:
                    iv = _vals(ia)
                    eqclass = (
                        classes01.get((iv[0], iv[1]), [])
                        if even
                        else classes2.get(iv[2], [])
                    )
                    for ia2 in eqclass:
                        k2 = _key(ia2)
                        if k2 not in parent:
                            parent[k2] = ia
                            next_level.append(ia2)
                        if _key(ia2) == _key(g2):
                            path = [ia2]
                            cur = parent.get(k2)
                            while cur is not None:
                                path.append(cur)
                                ck = _key(cur)
                                cur = parent.get(ck)
                            path.reverse()
                            return path
                if not next_level:
                    if not first:
                        break
                    first = False
                    continue
                first = False
                current = next_level
            return None

        @staticmethod
        def jonssonLevelPath(middleZero: Any, g0: Any, g2: Any, alvinVariant: Any = False) -> Any:
            if middleZero is None or g0 is None or g2 is None:
                _raise_npe()
            path = _lib_call(
                _malcev_fn("jonsson_level_path"),
                [_int_array_values(x) for x in list(middleZero)],
                _int_array_values(g0),
                _int_array_values(g2),
                bool(alvinVariant),
            )
            return _path_to_intarrays(path)

        @staticmethod
        def gummLevelPath(middleZero: Any, firstOne: Any, g0: Any, g2: Any) -> Any:
            if middleZero is None or firstOne is None or g0 is None or g2 is None:
                _raise_npe()
            path = _lib_call(
                _malcev_fn("gumm_level_path"),
                [_int_array_values(x) for x in list(middleZero)],
                [_int_array_values(x) for x in list(firstOne)],
                _int_array_values(g0),
                _int_array_values(g2),
            )
            return _path_to_intarrays(path)

        @staticmethod
        def hagemannMitschkeLevelPath(sub: Any, g0: Any, g2: Any) -> Any:
            if sub is None or g0 is None or g2 is None:
                _raise_npe()
            path = _lib_call(
                _malcev_fn("hagemann_mitschke_level_path"),
                [_int_array_values(x) for x in list(sub)],
                _int_array_values(g0),
                _int_array_values(g2),
            )
            return _path_to_intarrays(path)

        @staticmethod
        def jonssonLevelAux(middleZero: Any, g0: Any, g2: Any) -> Any:
            if middleZero is None or g0 is None or g2 is None:
                _raise_npe()
            return int(
                _lib_call(
                    _malcev_fn("jonsson_level_aux"),
                    [_int_array_values(x) for x in list(middleZero)],
                    _int_array_values(g0),
                    _int_array_values(g2),
                )
            )

        @staticmethod
        def nuTermIdempotent_Bad(testalg: Any, arity: Any, report: Any = None) -> Any:
            if testalg is None:
                _raise_npe()
            _reject_progress_report(report, "nuTermIdempotent_Bad")
            return bool(
                _lib_call(
                    _malcev_fn("nu_term_idempotent_bad"),
                    _as_basic_algebra(testalg),
                    int(arity),
                )
            )

        @staticmethod
        def fixedKEdgeIdempotent(testalg: Any, level: Any, report: Any = None) -> Any:
            if testalg is None:
                _raise_npe()
            _reject_progress_report(report, "fixedKEdgeIdempotent")
            return bool(
                _lib_call(
                    _malcev_fn("fixed_k_edge_idempotent"),
                    _as_basic_algebra(testalg),
                    int(level),
                )
            )

        @staticmethod
        def fixedKPermIdempotent(alg: Any, level: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "fixedKPermIdempotent")
            return bool(
                _lib_call(
                    _malcev_fn("fixed_k_perm_idempotent"),
                    _as_basic_algebra(alg),
                    int(level),
                )
            )

        @staticmethod
        def permLevelIdempotent(alg: Any, report: Any = None) -> Any:
            if alg is None:
                _raise_npe()
            _reject_progress_report(report, "permLevelIdempotent")
            return int(
                _lib_call(_malcev_fn("perm_level_idempotent"), _as_basic_algebra(alg))
            )

    def _cube_term_blocker_alg(alg: Any) -> Any:
        from org.uacalc.alg.sublat import BasicSet

        if alg is None:
            _raise_npe()
        n = int(alg.cardinality())
        for c in range(n):
            S = set([c])
            while len(S) < n:
                ce = None
                for e in range(n):
                    if e not in S:
                        ce2 = alg.sub().sg([c, e])
                        if ce is None or ce2.leq(ce):
                            ce = ce2
                if ce is None:
                    break
                ce_arr = [int(x) for x in ce.getArray()]
                intersection = [x for x in ce_arr if x in S]
                C = BasicSet(intersection)
                if Malcev.cubeTermBlockerIdempotent(alg, C, ce):
                    return [C, ce]
                for x in ce_arr:
                    S.add(int(x))
        return None

    def _cube_term_blocker_op(op: Any, C: Any, D: Any) -> int:
        arity = int(op.arity())
        for j in range(arity):
            if _cube_term_blocker_at(op, j, C, D):
                return j
        return -1

    def _cube_term_blocker_at(op: Any, j: int, C: Any, D: Any) -> bool:
        from org.uacalc.util import SequenceGenerator

        arity = int(op.arity())
        if arity < 2:
            return True
        c_size = int(C.universeSize())
        d_size = int(D.universeSize())
        if arity - 1 <= 0:
            return True
        arr = [0] * (arity - 1)
        inc = SequenceGenerator.sequenceIncrementor(arr, d_size - 1)
        while True:
            args = [0] * arity
            for k in range(j):
                args[k] = int(D.get(arr[k]))
            for k in range(j + 1, arity):
                args[k] = int(D.get(arr[k - 1]))
            for i in range(c_size):
                args[j] = int(C.get(i))
                if not C.contains(op.intValueAt(args)):
                    return False
            if not inc.increment():
                break
        return True

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

    def convertToDefaultValueOps_uoe(self: Any) -> None:
        raise UnsupportedOperationException("Only for basic algebras")

    def _int_array(values: Any) -> Any:
        from org.uacalc.util import IntArray

        if values is None:
            return None
        if _is_int_array(values):
            return values
        return IntArray([int(x) for x in list(values)])

    def _is_int_array(elem: Any) -> bool:
        if elem is None:
            return False
        name = type(elem).__name__
        if name in ("IntArray", "PyIntArray"):
            return True
        return hasattr(elem, "to_array") and hasattr(elem, "universeSize")

    def _int_array_values(elem: Any) -> List[int]:
        for attr in ("to_array", "getArray", "get_array"):
            fn = getattr(elem, attr, None)
            if callable(fn):
                return [int(x) for x in fn()]
        return [int(x) for x in list(elem)]

    def _path_to_intarrays(path: Any) -> Any:
        if path is None:
            return None
        from org.uacalc.util import IntArray

        return [IntArray([int(x) for x in list(row)]) for row in list(path)]

    def productGetElement(self: Any, k: Any) -> Any:
        idx = int(k)
        fn = getattr(self, "get_element_tuple", None)
        if callable(fn):
            return list(fn(idx))
        return getElement(self, k)

    def productElementIndex(self: Any, elem: Any) -> int:
        # Java ProductAlgebra.elementIndex only accepts IntArray; else UOE.
        if not _is_int_array(elem):
            raise UnsupportedOperationException()
        fn = getattr(self, "element_index_tuple", None)
        if callable(fn):
            return int(fn(_int_array_values(elem)))
        return int(self.element_index(_int_array_values(elem)))

    def powerElementIndex(self: Any, elem: Any) -> int:
        # Java PowerAlgebra.elementIndex searches universe() for IntArray, but
        # ProductIterator yields ArrayLists, so the result is always -1.
        return -1

    def productGetUniverseList(self: Any) -> Any:
        fn = getattr(self, "get_universe_tuples", None) or getattr(
            self, "get_universe_list", None
        )
        if callable(fn):
            univ = fn()
            return None if univ is None else [list(row) for row in univ]
        return getUniverseList(self)

    def productSg(self: Any, elems: Any) -> Any:
        gens = [productElementIndex(self, e) for e in list(elems)]
        # Java ProductAlgebra.Sg is `return sub().Sg(gens)` (already a Subalgebra).
        return self.sub().Sg(gens)

    def sgClose(self: Any, elems: Any) -> Any:
        fn = getattr(self, "sg_close", None)
        if callable(fn):
            return list(fn(list(elems)))
        return []

    def productFactors(self: Any) -> Any:
        impl = getattr(type(self), "factors", None)
        if callable(impl) and impl is not productFactors:
            try:
                return impl(self)
            except TypeError:
                return impl()
        return None

    def projection(self: Any, k: Any) -> Any:
        fn = getattr(self, "projection", None)
        if callable(fn):
            return _lib_call(fn, int(k))
        return None

    def projectionKernel(self: Any, k: Any) -> Any:
        fn = getattr(self, "projection_kernel", None)
        if callable(fn):
            return fn(int(k))
        return None

    def getRoot(self: Any) -> Any:
        fn = getattr(self, "get_root", None)
        if callable(fn):
            return fn()
        return None

    def getPower(self: Any) -> int:
        fn = getattr(self, "get_power", None)
        if callable(fn):
            return int(fn())
        return int(self.number_of_factors())

    def powerParent(self: Any) -> Any:
        return getRoot(self)

    def powerParents(self: Any) -> Any:
        root = getRoot(self)
        return None if root is None else [root]

    def subalgebraGetElement(self: Any, k: Any) -> Any:
        idx = int(k)
        arr = list(self.get_subuniverse_array())
        n = len(arr)
        if idx < 0 or idx >= n:
            raise ArrayIndexOutOfBoundsException(
                "Index: {0}, Size: {1}".format(idx, n)
            )
        super_alg = self.super_algebra()
        get = getattr(super_alg, "getElement", None) or getattr(
            super_alg, "get_element", None
        )
        return get(arr[idx])

    def subalgebraElementIndex(self: Any, elem: Any) -> int:
        super_alg = self.super_algebra()
        eidx = getattr(super_alg, "elementIndex", None) or getattr(
            super_alg, "element_index", None
        )
        super_idx = eidx(elem)
        return int(self.index(int(super_idx)))

    def restrictPartition(self: Any, par: Any) -> Any:
        fn = getattr(self, "restrict_partition", None)
        if callable(fn):
            return _lib_call(fn, par)
        raise TypeError("restrictPartition is not bound")

    def nullUniverseList(self: Any) -> Any:
        return None

    def quotientGetElement(self: Any, k: Any) -> Any:
        fn = getattr(self, "get_element", None)
        if callable(fn):
            return _lib_call(fn, int(k))
        return getElement(self, k)

    def quotientElementIndex(self: Any, obj: Any) -> int:
        # Java returns congruence.representative(super.elementIndex(obj)),
        # which is a super-algebra representative, not the quotient index.
        super_alg = self.super_algebra()
        eidx = getattr(super_alg, "elementIndex", None) or getattr(
            super_alg, "element_index", None
        )
        super_idx = int(eidx(obj))
        cong = self.get_congruence()
        rep = getattr(cong, "representative", None)
        return int(rep(super_idx)) if callable(rep) else super_idx

    def representativeIndex(self: Any, rep: Any) -> int:
        fn = getattr(self, "representative_index", None)
        if callable(fn):
            return int(fn(int(rep)))
        return -1

    def canonicalHomomorphism(self: Any, e: Any) -> int:
        fn = getattr(self, "canonical_homomorphism", None)
        if callable(fn):
            return int(fn(int(e)))
        return representativeIndex(self, self.get_congruence().representative(int(e)))

    def getCongruence(self: Any) -> Any:
        fn = getattr(self, "get_congruence", None)
        if callable(fn):
            return fn()
        return None

    def getAlgebra(self: Any) -> Any:
        fn = getattr(self, "get_algebra", None)
        if callable(fn):
            return fn()
        return None

    def getIndex(self: Any) -> int:
        fn = getattr(self, "get_index", None)
        if callable(fn):
            return int(fn())
        return -1

    def getIndexInSuperAlgebra(self: Any) -> int:
        fn = getattr(self, "get_index_in_super_algebra", None)
        if callable(fn):
            return int(fn())
        return -1

    def toString(self: Any) -> str:
        return str(self)

    def subproductGetElement(self: Any, k: Any) -> Any:
        fn = getattr(self, "get_element", None)
        if not callable(fn):
            return getElement(self, k)
        raw = fn(int(k))
        if raw is None:
            return None
        if _is_int_array(raw):
            return raw
        return _int_array(raw)

    def subproductElementIndex(self: Any, obj: Any) -> int:
        fn = getattr(self, "element_index", None)
        if not callable(fn):
            return -1
        if _is_int_array(obj):
            return int(fn(_int_array_values(obj)))
        if isinstance(obj, (list, tuple)):
            return int(fn([int(x) for x in obj]))
        return -1

    def subproductGenerators(self: Any) -> Any:
        impl = getattr(type(self), "generators", None)
        if callable(impl) and impl is not subproductGenerators:
            raw = impl(self)
            return [_int_array(row) for row in list(raw)]
        return None

    def getProductAlgebra(self: Any) -> Any:
        fn = getattr(self, "get_product_algebra", None)
        if callable(fn):
            return fn()
        return None

    def getTerms(self: Any) -> Any:
        fn = getattr(self, "get_terms", None)
        if callable(fn):
            return fn()
        return None

    def getTerm(self: Any, elt: Any) -> Any:
        fn = getattr(self, "get_term", None)
        if callable(fn):
            return fn(elt)
        return None

    def getVariableToGeneratorMap(self: Any) -> Any:
        fn = getattr(self, "get_variable_to_generator_map", None)
        if callable(fn):
            return fn()
        return None

    def getVariables(self: Any) -> Any:
        fn = getattr(self, "get_variables", None)
        if callable(fn):
            return fn()
        return None

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
        "QuotientAlgebra",
        "SubProductAlgebra",
        "GeneralAlgebra",
        "AlgebraFromMinimalSets",
        "MatrixPowerAlgebra",
        "PolinLikeAlgebra",
        "UnaryTermsMonoid",
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
            "PowerAlgebra": _LibPowerAlgebra,
            "QuotientAlgebra": _LibQuotientAlgebra,
            "SubProductAlgebra": _LibSubProductAlgebra,
            "GeneralAlgebra": _LibGeneralAlgebra,
            "AlgebraFromMinimalSets": _LibAlgebraFromMinimalSets,
            "MatrixPowerAlgebra": _LibMatrixPowerAlgebra,
            "PolinLikeAlgebra": _LibPolinLikeAlgebra,
            "UnaryTermsMonoid": _LibUnaryTermsMonoid,
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

    def _bind(cls: Any, name: str, impl: Any) -> None:
        if cls is None:
            return
        try:
            setattr(cls, name, impl)
        except (TypeError, AttributeError):
            pass

    _orig_prod_proj = getattr(_LibProductAlgebra, "projection", None)

    def productProjection(self: Any, k: Any, _orig: Any = _orig_prod_proj) -> Any:
        try:
            return _lib_call(_orig, self, int(k)) if _orig is not None else None
        except Exception as exc:
            if type(exc).__name__ in (
                "ValueError",
                "IllegalArgumentException",
                "IndexError",
            ):
                raise IndexOutOfBoundsException(str(exc)) from exc
            raise

    _PRODUCT_EXTRA = {
        "getElement": productGetElement,
        "elementIndex": productElementIndex,
        "getUniverseList": productGetUniverseList,
        "getUniverseOrder": lambda self: None,
        "Sg": productSg,
        "sgClose": sgClose,
        "projection": productProjection,
        "projectionKernel": projectionKernel,
        "numberOfFactors": numberOfFactors,
        "convertToDefaultValueOps": convertToDefaultValueOps_uoe,
        "iterator": _algebra_iterator,
        "parent": parent,
        "parents": lambda self: self.factors(),
    }
    for camel, impl in _PRODUCT_EXTRA.items():
        _bind(_LibProductAlgebra, camel, impl)

    _POWER_EXTRA = dict(_PRODUCT_EXTRA)
    _orig_pow_proj = (
        getattr(_LibPowerAlgebra, "projection", None)
        if _LibPowerAlgebra is not None
        else None
    )

    def powerProjection(self: Any, k: Any, _orig: Any = _orig_pow_proj) -> Any:
        try:
            return _lib_call(_orig, self, int(k)) if _orig is not None else None
        except Exception as exc:
            if type(exc).__name__ in (
                "ValueError",
                "IllegalArgumentException",
                "IndexError",
            ):
                raise IndexOutOfBoundsException(str(exc)) from exc
            raise

    _POWER_EXTRA.update(
        {
            "elementIndex": powerElementIndex,
            "getRoot": getRoot,
            "getPower": getPower,
            "parent": powerParent,
            "parents": powerParents,
            "projection": powerProjection,
        }
    )
    for camel, impl in _POWER_EXTRA.items():
        _bind(_LibPowerAlgebra, camel, impl)

    def subalgebraUniverse(self: Any) -> List[Any]:
        n = int(self.cardinality())
        return [subalgebraGetElement(self, i) for i in range(n)]

    def quotientUniverse(self: Any) -> List[Any]:
        super_alg = self.super_algebra()
        reps = self.representatives()
        get = getattr(super_alg, "getElement", None) or getattr(
            super_alg, "get_element", None
        )
        return [get(int(r)) for r in list(reps)]

    _SUBALG_EXTRA = {
        "getElement": subalgebraGetElement,
        "elementIndex": subalgebraElementIndex,
        "getUniverseList": nullUniverseList,
        "getUniverseOrder": lambda self: None,
        "restrictPartition": restrictPartition,
        "convertToDefaultValueOps": convertToDefaultValueOps_uoe,
        "universe": subalgebraUniverse,
        "iterator": lambda self: iter(subalgebraUniverse(self)),
        "parent": parent,
        "parents": parents,
    }
    for camel, impl in _SUBALG_EXTRA.items():
        _bind(_LibSubalgebra, camel, impl)

    _QUOT_EXTRA = {
        "getElement": quotientGetElement,
        "elementIndex": quotientElementIndex,
        "getUniverseList": nullUniverseList,
        "getUniverseOrder": lambda self: None,
        "representativeIndex": representativeIndex,
        "canonicalHomomorphism": canonicalHomomorphism,
        "getCongruence": getCongruence,
        "convertToDefaultValueOps": convertToDefaultValueOps_uoe,
        "universe": quotientUniverse,
        "iterator": lambda self: iter(quotientUniverse(self)),
        "parent": parent,
        "parents": parents,
    }
    for camel, impl in _QUOT_EXTRA.items():
        _bind(_LibQuotientAlgebra, camel, impl)

    if _LibQuotientElement is not None:
        for camel, impl in (
            ("getAlgebra", getAlgebra),
            ("superAlgebra", lambda self: self.super_algebra()),
            ("getCongruence", getCongruence),
            ("getIndex", getIndex),
            ("getIndexInSuperAlgebra", getIndexInSuperAlgebra),
            ("toString", toString),
        ):
            _bind(_LibQuotientElement, camel, impl)

    _orig_sp_gens = (
        getattr(_LibSubProductAlgebra, "generators", None)
        if _LibSubProductAlgebra is not None
        else None
    )
    _orig_sp_univ = (
        getattr(_LibSubProductAlgebra, "get_universe_list", None)
        if _LibSubProductAlgebra is not None
        else None
    )

    def subproductGeneratorsBound(self: Any, _orig: Any = _orig_sp_gens) -> Any:
        if _orig is None:
            return None
        return [_int_array(row) for row in list(_orig(self))]

    def subproductUniverseListBound(self: Any, _orig: Any = _orig_sp_univ) -> Any:
        if _orig is None:
            return None
        univ = _orig(self)
        return None if univ is None else [_int_array(row) for row in univ]

    _SUBPROD_EXTRA = {
        "getElement": subproductGetElement,
        "elementIndex": subproductElementIndex,
        "getUniverseList": subproductUniverseListBound,
        "getUniverseOrder": lambda self: None,
        "generators": subproductGeneratorsBound,
        "getProductAlgebra": getProductAlgebra,
        "getTerms": getTerms,
        "getTerm": getTerm,
        "getVariableToGeneratorMap": getVariableToGeneratorMap,
        "getVariables": getVariables,
        "convertToDefaultValueOps": convertToDefaultValueOps_uoe,
        "iterator": _algebra_iterator,
        "parent": parent,
        "parents": parents,
        "numberOfFactors": numberOfFactors,
    }
    for camel, impl in _SUBPROD_EXTRA.items():
        _bind(_LibSubProductAlgebra, camel, impl)

    def generalAlgebraCon(self: Any) -> Any:
        raise UnsupportedOperationException()

    def generalAlgebraSub(self: Any) -> Any:
        raise UnsupportedOperationException()

    def generalAlgebraParent(self: Any) -> Any:
        return None

    def generalAlgebraParents(self: Any) -> Any:
        return None

    _orig_ga_ops = (
        getattr(_LibGeneralAlgebra, "operations", None)
        if _LibGeneralAlgebra is not None
        else None
    )

    def generalAlgebraOperations(self: Any, _orig: Any = _orig_ga_ops) -> Any:
        if _orig is None:
            return None
        ops = _orig(self)
        if ops is None:
            return None
        try:
            seq = list(ops)
        except TypeError:
            return ops
        # Java 2-arg constructor leaves the operations field null.
        # Rust stores an empty vec for that path.
        if not seq:
            return None
        return seq

    _GENERAL_EXTRA = {
        "con": generalAlgebraCon,
        "sub": generalAlgebraSub,
        "parent": generalAlgebraParent,
        "parents": generalAlgebraParents,
        "operations": generalAlgebraOperations,
        "getUniverseList": lambda self: list(self.universe()) if hasattr(self, "universe") else None,
        "iterator": _algebra_iterator,
        "convertToDefaultValueOps": convertToDefaultValueOps_uoe,
    }
    for camel, impl in _GENERAL_EXTRA.items():
        _bind(_LibGeneralAlgebra, camel, impl)

    def matrixGetRoot(self: Any) -> Any:
        return self.get_root()

    def matrixGetPower(self: Any) -> int:
        return int(self.get_power())

    def matrixGetPowerAlgebra(self: Any) -> Any:
        return self.get_power_algebra()

    def matrixGetElement(self: Any, index: Any) -> Any:
        from org.uacalc.util import IntArray

        return IntArray([int(x) for x in list(self.get_element(int(index)))])

    def matrixElementIndex(self: Any, obj: Any) -> int:
        if obj is None:
            _raise_npe()
        coords = _as_universe_indices(obj)
        return int(self.element_index(coords))

    _MATRIX_EXTRA = {
        "getRoot": matrixGetRoot,
        "getPower": matrixGetPower,
        "getPowerAlgebra": matrixGetPowerAlgebra,
        "getElement": matrixGetElement,
        "elementIndex": matrixElementIndex,
        "getUniverseList": lambda self: [
            matrixGetElement(self, i) for i in range(int(self.cardinality()))
        ],
        "getUniverseOrder": lambda self: None,
        "convertToDefaultValueOps": convertToDefaultValueOps_uoe,
        "parent": lambda self: self.get_root(),
        "parents": lambda self: [self.get_root()],
        "iterator": _algebra_iterator,
    }
    for camel, impl in _MATRIX_EXTRA.items():
        _bind(_LibMatrixPowerAlgebra, camel, impl)

    def polinGetElement(self: Any, index: Any) -> Any:
        # Java PolinLikeAlgebra.getElement is a stub that always returns null.
        return None

    def polinElementIndex(self: Any, elem: Any) -> int:
        # Java PolinLikeAlgebra.elementIndex is a stub that always returns -1.
        return -1

    def polinizeOperation(self: Any, sym: Any) -> Any:
        fn = getattr(self, "polinize_operation", None)
        if callable(fn):
            return _lib_call(fn, sym)
        return None

    _POLIN_EXTRA = {
        "getElement": polinGetElement,
        "elementIndex": polinElementIndex,
        "getUniverseList": lambda self: None,
        "getUniverseOrder": lambda self: None,
        "convertToDefaultValueOps": convertToDefaultValueOps_uoe,
        "iterator": _algebra_iterator,
        "polinizeOperation": polinizeOperation,
        "constructPolinAlgebra": PolinLikeAlgebra.constructPolinAlgebra,
    }
    for camel, impl in _POLIN_EXTRA.items():
        _bind(_LibPolinLikeAlgebra, camel, impl)
    if _LibPolinLikeAlgebra is not None:
        try:
            _LibPolinLikeAlgebra.constructPolinAlgebra = staticmethod(
                PolinLikeAlgebra.constructPolinAlgebra
            )
        except (TypeError, AttributeError):
            _LibPolinLikeAlgebra.constructPolinAlgebra = (
                PolinLikeAlgebra.constructPolinAlgebra
            )

    def unaryGetElement(self: Any, index: Any) -> Any:
        # Java UnaryTermsMonoid.getElement is a TODO stub (always null).
        return None

    def unaryElementIndex(self: Any, elem: Any) -> int:
        # Java UnaryTermsMonoid.elementIndex is a TODO stub (always 0).
        return 0

    def unaryCon(self: Any) -> Any:
        return None

    def unarySub(self: Any) -> Any:
        return None

    def unaryIsUnary(self: Any) -> bool:
        # Java isUnary() is false: the monoid operation is binary PRODUCT.
        return False

    _UNARY_EXTRA = {
        "getElement": unaryGetElement,
        "elementIndex": unaryElementIndex,
        "con": unaryCon,
        "sub": unarySub,
        "isUnary": unaryIsUnary,
        "getUniverseOrder": lambda self: None,
        "convertToDefaultValueOps": convertToDefaultValueOps_uoe,
        "makeOperationTables": lambda self: None,
    }
    for camel, impl in _UNARY_EXTRA.items():
        _bind(_LibUnaryTermsMonoid, camel, impl)

    def awgvGetAlgebra(self: Any) -> Any:
        return self.get_algebra()

    def awgvGetVector(self: Any) -> Any:
        return list(self.get_vector())

    def awgvIsImageOf(self: Any, other: Any) -> bool:
        return bool(self.is_image_of(other))

    def awgvToString(self: Any) -> str:
        vec = list(self.get_vector())
        body = "[" + ",".join(str(int(x)) for x in vec) + "]"
        alg = self.get_algebra()
        card = int(alg.cardinality())
        return "Alg with vector, alg size = {}, vec = {}".format(card, body)

    def awgvCompareTo(self: Any, other: Any) -> int:
        if awgvIsImageOf(self, other):
            if awgvIsImageOf(other, self):
                return 0
            return -1
        if awgvIsImageOf(other, self):
            return 1
        return 0

    def awgvEquals(self: Any, other: Any) -> bool:
        if other is None:
            return False
        try:
            return bool(awgvIsImageOf(self, other) and awgvIsImageOf(other, self))
        except Exception:
            return False

    if _LibAlgebraWithGeneratingVector is not None:
        for camel, impl in (
            ("getAlgebra", awgvGetAlgebra),
            ("getVector", awgvGetVector),
            ("isImageOf", awgvIsImageOf),
            ("toString", awgvToString),
            ("compareTo", awgvCompareTo),
            ("equals", awgvEquals),
            ("siDecompose", AlgebraWithGeneratingVector.siDecompose),
        ):
            _bind(_LibAlgebraWithGeneratingVector, camel, impl)
        try:
            _LibAlgebraWithGeneratingVector.siDecompose = staticmethod(
                AlgebraWithGeneratingVector.siDecompose
            )
        except (TypeError, AttributeError):
            _LibAlgebraWithGeneratingVector.siDecompose = (
                AlgebraWithGeneratingVector.siDecompose
            )

    def switchXandYAutomorphism(self: Any) -> Any:
        fn = getattr(self, "switch_x_and_y_automorphism", None)
        if callable(fn):
            return _lib_call(fn)
        return None

    def _java_map_str(mapping: Any) -> str:
        if mapping is None:
            return "null"
        items = []
        try:
            keys = list(mapping.keys())
        except Exception:
            return str(mapping)
        for k in keys:
            items.append("{}={}".format(k, mapping[k]))
        return "{" + ", ".join(items) + "}"

    def homomorphismToString(self: Any) -> str:
        domain = self.getDomain() if hasattr(self, "getDomain") else self.get_domain()
        range_alg = self.getRange() if hasattr(self, "getRange") else self.get_range()
        dname = domain.getName() if hasattr(domain, "getName") else domain.name()
        rname = range_alg.getName() if hasattr(range_alg, "getName") else range_alg.name()
        mapping = self.getMap() if hasattr(self, "getMap") else self.get_map()
        return "homomorphism: {} --> {} : {}".format(
            dname, rname, _java_map_str(mapping)
        )

    def homomorphismGetDomain(self: Any) -> Any:
        return self.get_domain()

    def homomorphismSetDomain(self: Any, domain: Any) -> None:
        if domain is None:
            _raise_npe()
        self.set_domain(_as_basic_algebra(domain))

    def homomorphismGetRange(self: Any) -> Any:
        return self.get_range()

    def homomorphismSetRange(self: Any, range_alg: Any) -> None:
        if range_alg is None:
            _raise_npe()
        self.set_range(_as_basic_algebra(range_alg))

    def homomorphismGetMap(self: Any) -> Any:
        raw = self.get_map()
        return {int(k): int(v) for k, v in dict(raw).items()}

    def homomorphismSetMap(self: Any, mapping: Any) -> None:
        if mapping is None:
            _raise_npe()
        raw = {int(k): int(v) for k, v in dict(mapping).items()}
        self.set_map(raw)

    _orig_homo_kernel = (
        getattr(_LibHomomorphism, "kernel", None) if _LibHomomorphism is not None else None
    )

    def homomorphismKernel(self: Any, _orig: Any = _orig_homo_kernel) -> Any:
        mapping = homomorphismGetMap(self)
        domain = homomorphismGetDomain(self)
        n = int(domain.cardinality())
        # Java: map.get(i).equals(map.get(j)) NPEs only when get(i) is null
        # for some i with a later j, i.e. a missing non-last key.
        for i in range(max(0, n - 1)):
            if i not in mapping:
                _raise_npe()
        if _orig is None:
            raise TypeError("kernel is not bound")
        return _lib_call(_orig, self)

    _HOMO_EXTRA = {
        "getDomain": homomorphismGetDomain,
        "setDomain": homomorphismSetDomain,
        "getRange": homomorphismGetRange,
        "setRange": homomorphismSetRange,
        "getMap": homomorphismGetMap,
        "setMap": homomorphismSetMap,
        "kernel": homomorphismKernel,
        "toString": homomorphismToString,
        "__str__": homomorphismToString,
    }
    if _LibHomomorphism is not None:
        for camel, impl in _HOMO_EXTRA.items():
            _bind(_LibHomomorphism, camel, impl)
        try:
            _LibHomomorphism.productHomo = staticmethod(Homomorphism.productHomo)
        except (TypeError, AttributeError):
            _LibHomomorphism.productHomo = Homomorphism.productHomo

    if _LibCloser is not None:
        _CLOSER_ORIG_CLOSE[0] = getattr(_LibCloser, "close", None)

    def _mark_closer_answer(self: Any, result: Any) -> Any:
        try:
            self._ans_set = True
            self._ans = result
        except (AttributeError, TypeError):
            pass
        return result

    def closerGetAnswer(self: Any) -> Any:
        if not getattr(self, "_ans_set", False):
            return None
        return getattr(self, "_ans", None)

    def closerSgClose(self: Any, elems: Any = None, closedMark: Any = None, termMap: Any = None) -> Any:
        if elems is None and closedMark is None and termMap is None:
            if getattr(Closer, "doParallel", False):
                fn = getattr(self, "sg_close_parallel", None)
                if callable(fn):
                    return _mark_closer_answer(self, _lib_call(fn))
            return _mark_closer_answer(self, _lib_call(self.sg_close))
        if termMap is not None:
            setter = getattr(self, "set_term_map", None) or getattr(self, "setTermMap", None)
            if callable(setter):
                setter(termMap)
        fn = getattr(self, "sg_close_from", None)
        if not callable(fn):
            raise TypeError("sgClose(elems, closedMark, termMap) is not bound")
        mark = 0 if closedMark is None else int(closedMark)
        return _mark_closer_answer(self, _lib_call(fn, elems, mark))

    def closerSgCloseParallel(self: Any, elems: Any = None, closedMark: Any = None, termMap: Any = None) -> Any:
        if elems is not None or closedMark is not None or termMap is not None:
            return closerSgClose(self, elems, closedMark, termMap)
        fn = getattr(self, "sg_close_parallel", None)
        if not callable(fn):
            raise TypeError("sgCloseParallel is not bound")
        return _mark_closer_answer(self, _lib_call(fn))

    def closerSgClosePower(self: Any) -> Any:
        return _mark_closer_answer(self, _lib_call(self.sg_close_power))

    def closerClose(self: Any) -> Any:
        orig = _CLOSER_ORIG_CLOSE[0]
        if orig is None:
            raise TypeError("close is not bound")
        return _mark_closer_answer(self, _lib_call(orig, self))

    def closerGetmaxSize(self: Any) -> int:
        v = self.get_max_size()
        return -1 if v is None else int(v)

    def closerSetMaxSize(self: Any, k: Any) -> None:
        n = int(k)
        self.set_max_size(None if n < 0 else n)

    def closerGetIndexForConstraintSet(self: Any) -> int:
        v = self.get_index_for_constraint_set()
        return -1 if v is None else int(v)

    def closerSetIndexForConstraintSet(self: Any, k: Any) -> None:
        self.set_index_for_constraint_set(int(k))

    def closerGetIndexForCongruenceConstraint(self: Any) -> int:
        v = self.get_index_for_congruence_constraint()
        return 0 if v is None else int(v)

    def closerSetIndexForCongruenceConstraint(self: Any, k: Any) -> None:
        self.set_index_for_congruence_constraint(int(k))

    def closerGetCongruenceConstraintElemIndex(self: Any) -> int:
        v = self.get_congruence_constraint_elem_index()
        return 0 if v is None else int(v)

    def closerSetCongruenceConstraintElemIndex(self: Any, k: Any) -> None:
        self.set_congruence_constraint_elem_index(int(k))

    def closerSetImageAlgebra(self: Any, alg: Any) -> None:
        if alg is None:
            _raise_npe()
        _lib_call(self.set_image_algebra, alg)

    def closerSetHomomorphism(self: Any, arg: Any) -> None:
        if arg is None:
            _raise_npe()
        _lib_call(self.set_homomorphism, arg)

    def closerSetElementToFind(self: Any, e: Any) -> None:
        self.set_element_to_find(None if e is None else _int_array(e))

    def closerSetElementsToFind(self: Any, elts: Any, gens: Any = None) -> None:
        if elts is None:
            _raise_npe()
        args = [[_int_array(x) for x in list(elts)]]
        if gens is not None:
            args.append([_int_array(x) for x in list(gens)])
        _lib_call(self.set_elements_to_find, *args)

    def closerSetGenerators(self: Any, gens: Any) -> None:
        if gens is None:
            _raise_npe()
        _lib_call(self.set_generators, [_int_array(g) for g in list(gens)])

    def closerGetGenerators(self: Any) -> Any:
        return list(self.get_generators())

    def closerGetTermMap(self: Any) -> Any:
        return self.get_term_map()

    def closerSetTermMap(self: Any, term_map: Any) -> None:
        self.set_term_map(term_map)

    def closerGetElementToFind(self: Any) -> Any:
        return self.get_element_to_find()

    def closerGetElementsToFind(self: Any) -> Any:
        return self.get_elements_to_find()

    def closerAllElementsFound(self: Any) -> bool:
        return bool(self.all_elements_found())

    def closerGetBlocks(self: Any) -> Any:
        return self.get_blocks()

    def closerSetBlocks(self: Any, blocks: Any) -> None:
        self.set_blocks(blocks)

    def closerGetValues(self: Any) -> Any:
        return self.get_values()

    def closerSetValues(self: Any, values: Any) -> None:
        # Java int[][]; the binding wants a sequence of (index, value) pairs.
        if values is None:
            self.set_values(None)
            return
        pairs = []
        for row in list(values):
            items = list(row)
            if len(items) >= 2:
                pairs.append((int(items[0]), int(items[1])))
            elif len(items) == 1:
                pairs.append((0, int(items[0])))
        self.set_values(pairs)

    def closerGetSetConstraint(self: Any) -> Any:
        return self.get_set_constraint()

    def closerSetConstraintSet(self: Any, s: Any) -> None:
        self.set_constraint_set(None if s is None else set(s))

    def closerGetCongruenceForCongruenceConstraint(self: Any) -> Any:
        return self.get_congruence_for_congruence_constraint()

    def closerSetCongruenceForCongruenceConstraint(self: Any, alpha: Any) -> None:
        self.set_congruence_for_congruence_constraint(alpha)

    def closerSetupCongruenceConstraint(self: Any, alpha: Any, index: Any, elemIndex: Any) -> None:
        _lib_call(self.setup_congruence_constraint, alpha, int(index), int(elemIndex))

    def closerGetFailingEquation(self: Any) -> Any:
        return self.get_failing_equation()

    def closerGetImageAlgebra(self: Any) -> Any:
        return self.get_image_algebra()

    def closerGetHomomorphism(self: Any) -> Any:
        return self.get_homomorphism()

    def closerGetTermMapForOperations(self: Any) -> Any:
        return self.get_term_map_for_operations()

    def closerSetRootAlgebra(self: Any, alg: Any) -> None:
        if alg is None:
            _raise_npe()
        _lib_call(self.set_root_algebra, alg)

    def closerSetOperations(self: Any, ops: Any) -> None:
        if ops is None:
            _raise_npe()
        _lib_call(self.set_operations, list(ops))

    def closerIsSuppressOutput(self: Any) -> bool:
        return bool(self.is_suppress_output())

    def closerSetSuppressOutput(self: Any, suppress: Any) -> None:
        self.set_suppress_output(bool(suppress))

    _CLOSER_EXTRA = {
        "getAnswer": closerGetAnswer,
        "sgClose": closerSgClose,
        "sgCloseParallel": closerSgCloseParallel,
        "sgClosePower": closerSgClosePower,
        "close": closerClose,
        "getmaxSize": closerGetmaxSize,
        "setMaxSize": closerSetMaxSize,
        "getIndexForConstraintSet": closerGetIndexForConstraintSet,
        "setIndexForConstraintSet": closerSetIndexForConstraintSet,
        "getIndexForCongruenceConstraint": closerGetIndexForCongruenceConstraint,
        "setIndexForCongruenceConstraint": closerSetIndexForCongruenceConstraint,
        "getCongruenceConstraintElemIndex": closerGetCongruenceConstraintElemIndex,
        "setCongruenceConstraintElemIndex": closerSetCongruenceConstraintElemIndex,
        "setImageAlgebra": closerSetImageAlgebra,
        "setHomomorphism": closerSetHomomorphism,
        "setElementToFind": closerSetElementToFind,
        "setElementsToFind": closerSetElementsToFind,
        "setGenerators": closerSetGenerators,
        "getGenerators": closerGetGenerators,
        "getTermMap": closerGetTermMap,
        "setTermMap": closerSetTermMap,
        "getElementToFind": closerGetElementToFind,
        "getElementsToFind": closerGetElementsToFind,
        "allElementsFound": closerAllElementsFound,
        "getBlocks": closerGetBlocks,
        "setBlocks": closerSetBlocks,
        "getValues": closerGetValues,
        "setValues": closerSetValues,
        "getSetConstraint": closerGetSetConstraint,
        "setConstraintSet": closerSetConstraintSet,
        "getCongruenceForCongruenceConstraint": closerGetCongruenceForCongruenceConstraint,
        "setCongruenceForCongruenceConstraint": closerSetCongruenceForCongruenceConstraint,
        "setupCongruenceConstraint": closerSetupCongruenceConstraint,
        "getFailingEquation": closerGetFailingEquation,
        "getImageAlgebra": closerGetImageAlgebra,
        "getHomomorphism": closerGetHomomorphism,
        "getTermMapForOperations": closerGetTermMapForOperations,
        "setRootAlgebra": closerSetRootAlgebra,
        "setOperations": closerSetOperations,
        "isSuppressOutput": closerIsSuppressOutput,
        "setSuppressOutput": closerSetSuppressOutput,
    }
    if _LibCloser is not None:
        for camel, impl in _CLOSER_EXTRA.items():
            _bind(_LibCloser, camel, impl)

    _bind(_LibFreeAlgebra, "switchXandYAutomorphism", switchXandYAutomorphism)
    try:
        _LibFreeAlgebra.findEquationOfAnotB = staticmethod(FreeAlgebra.findEquationOfAnotB)
    except (TypeError, AttributeError):
        _LibFreeAlgebra.findEquationOfAnotB = FreeAlgebra.findEquationOfAnotB

    # FreeAlgebra / ProductAlgebra extras
    if not hasattr(_LibProductAlgebra, "numberOfFactors"):
        try:
            _LibProductAlgebra.numberOfFactors = numberOfFactors
        except (TypeError, AttributeError):
            pass
    class _BigProductOp(object):
        """Product operation whose ``valueAt`` evaluates coordinate-wise."""

        def __init__(self, prod: Any, index: int, name: str, arity: int) -> None:
            self._prod = prod
            self._index = int(index)
            self._name = str(name)
            self._arity = int(arity)

        def arity(self) -> int:
            return self._arity

        def symbol(self) -> Any:
            return OperationSymbol(self._name, self._arity)

        def valueAt(self, args: Any) -> Any:
            arrays = []
            for a in args:
                getter = getattr(a, "getArray", None) or getattr(a, "to_array", None)
                if callable(getter):
                    arrays.append([int(x) for x in getter()])
                else:
                    arrays.append([int(x) for x in list(a)])
            return list(self._prod.value_at_arrays(self._index, arrays))

    def operations(self: Any) -> Any:
        meta = self.operations_meta()
        return [
            _BigProductOp(self, i, name, arity)
            for i, (name, arity) in enumerate(meta)
        ]

    def getNumberOfFactors(self: Any) -> int:
        return numberOfFactors(self)

    def getPowers(self: Any) -> Any:
        fn = getattr(self, "get_powers", None)
        if not callable(fn):
            return None
        powers = [int(x) for x in list(fn())]
        return None if not powers else powers

    def isPower(self: Any) -> bool:
        fn = getattr(self, "is_power", None)
        if callable(fn):
            return bool(fn())
        powers = getPowers(self)
        return powers is not None and len(powers) == 1

    def rootFactors(self: Any) -> Any:
        fn = getattr(self, "root_factors_or_none", None)
        if callable(fn):
            return fn()
        fn2 = getattr(self, "root_factors", None)
        return fn2() if callable(fn2) else None

    def sizeMultiplicities(self: Any) -> Any:
        fn = getattr(self, "size_multiplicities", None)
        if not callable(fn):
            return None
        raw = fn()
        if raw is None:
            return None
        if hasattr(raw, "items"):
            return {int(k): int(v) for k, v in raw.items()}
        return dict(raw)

    def getConstants(self: Any) -> Any:
        fn = getattr(self, "get_constants", None)
        if not callable(fn):
            return []
        return list(fn())

    def getConstantSymbol(self: Any, constant: Any) -> Any:
        fn = getattr(self, "get_constant_symbol", None)
        if constant is None or not callable(fn):
            return None
        return fn(_int_array(constant))

    def getConstantTerm(self: Any, constant: Any) -> Any:
        fn = getattr(self, "get_constant_term", None)
        if constant is None or not callable(fn):
            return None
        return fn(_int_array(constant))

    def bigProductSgClose(self: Any, elems: Any, *rest: Any) -> Any:
        if elems is None:
            _raise_npe()
        ias = [_int_array(e) for e in list(elems)]
        if rest:
            elt = rest[-1] if rest[-1] is None or _is_int_array(rest[-1]) else None
            fn = getattr(self, "sg_close_with_elt", None)
            if callable(fn):
                return list(fn(ias, elt))
        fn = getattr(self, "sg_close", None)
        if callable(fn):
            return list(fn(ias))
        return []

    def getBlockAlgebras(self: Any) -> Any:
        fn = getattr(self, "get_block_algebras", None)
        return list(fn()) if callable(fn) else []

    def getQuotientAlgebra(self: Any) -> Any:
        fn = getattr(self, "get_quotient_algebra", None)
        return fn() if callable(fn) else None

    def updatePass(self: Any, size: Any) -> None:
        self.update_pass(int(size))

    def incrementApps(self: Any) -> None:
        self.increment_apps()

    def incrementNextPassSize(self: Any) -> None:
        self.increment_next_pass_size()

    if _LibBigProductAlgebra is not None:
        for camel, impl in (
            ("numberOfFactors", numberOfFactors),
            ("getNumberOfFactors", getNumberOfFactors),
            ("operations", operations),
            ("getPowers", getPowers),
            ("isPower", isPower),
            ("rootFactors", rootFactors),
            ("sizeMultiplicities", sizeMultiplicities),
            ("getConstants", getConstants),
            ("getConstantSymbol", getConstantSymbol),
            ("getConstantTerm", getConstantTerm),
            ("sgClose", bigProductSgClose),
            ("projectionKernel", projectionKernel),
            ("makeOperationTables", makeOperationTables),
            ("getName", getName),
        ):
            _bind(_LibBigProductAlgebra, camel, impl)

    if _LibMaltsevProductDecomposition is not None:
        for camel, impl in (
            ("getBlockAlgebras", getBlockAlgebras),
            ("getQuotientAlgebra", getQuotientAlgebra),
            ("getCongruence", lambda self: self.get_congruence()),
        ):
            _bind(_LibMaltsevProductDecomposition, camel, impl)

    if _LibCloserTiming is not None:
        for camel, impl in (
            ("updatePass", updatePass),
            ("incrementApps", incrementApps),
            ("incrementNextPassSize", incrementNextPassSize),
        ):
            _bind(_LibCloserTiming, camel, impl)

    class _CloserTimingMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            return _LibCloserTiming is not None and isinstance(
                instance, _LibCloserTiming
            )

    class CloserTiming(object, metaclass=_CloserTimingMeta):
        """Java ``CloserTiming(BigProductAlgebra, ProgressReport)``."""

        def __new__(cls, algebra: Any, report: Any = None) -> Any:
            if algebra is None:
                _raise_npe(
                    'Cannot invoke "org.uacalc.alg.BigProductAlgebra.getNumberOfFactors()" '
                    'because "algebra" is null'
                )
            if report is not None:
                raise TypeError(
                    "CloserTiming(): expected org.uacalc.ui.tm.ProgressReport or None"
                )
            if _LibCloserTiming is None:
                raise TypeError("CloserTiming is not bound")
            return _LibCloserTiming(algebra)

        def updatePass(self, size: Any) -> None:
            updatePass(self, size)

        def incrementApps(self) -> None:
            incrementApps(self)

        def incrementNextPassSize(self) -> None:
            incrementNextPassSize(self)

    def _stash_con_result(alg: Any, lat: Any) -> Any:
        if lat is None:
            return lat
        _CON_ALGEBRAS[id(lat)] = alg
        try:
            from org.uacalc.alg import conlat as _conlat_mod

            store = getattr(_conlat_mod, "_CL_ALGEBRAS", None)
            if isinstance(store, dict):
                store[id(lat)] = alg
        except Exception:
            pass
        try:
            object.__setattr__(lat, "_uacalc_algebra", alg)
        except Exception:
            try:
                lat._uacalc_algebra = alg
            except Exception:
                pass
        return lat

    def _wrap_con_stash(cls: Any) -> None:
        if cls is None:
            return
        orig = getattr(cls, "con", None)
        if orig is None or getattr(orig, "_stashes_algebra", False):
            return

        def con(self: Any, _orig: Any = orig) -> Any:
            # Java SmallAlgebra.con() caches the lattice. Keep one wrapper so
            # getJoinIrredToSubtraceMap / typeJI persist across con() calls.
            key = id(self)
            cached = _CON_CACHE.get(key)
            if cached is not None:
                return cached
            lat = _stash_con_result(self, _orig(self))
            _CON_CACHE[key] = lat
            return lat

        con._stashes_algebra = True  # type: ignore[attr-defined]
        _bind(cls, "con", con)

    for _cls in (
        _LibBasicAlgebra,
        _LibFreeAlgebra,
        _LibProductAlgebra,
        _LibPowerAlgebra,
        _LibQuotientAlgebra,
        _LibSubalgebra,
        _LibReductAlgebra,
        _LibPolinLikeAlgebra,
        _LibSubProductAlgebra,
        _LibMatrixPowerAlgebra,
        _LibAlgebraFromMinimalSets,
        _LibUnaryTermsMonoid,
    ):
        _wrap_con_stash(_cls)

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
                if "UnaryTermsMonoid" not in name:
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
    alg_module_globals["AbstractIntOperation"] = AbstractIntOperation
    alg_module_globals["Algebra"] = Algebra
    alg_module_globals["AlgebraType"] = AlgebraType
    alg_module_globals["SmallAlgebra"] = SmallAlgebra
    alg_module_globals["BasicAlgebra"] = BasicAlgebra
    alg_module_globals["FreeAlgebra"] = FreeAlgebra
    alg_module_globals["Homomorphism"] = Homomorphism
    alg_module_globals["Closer"] = Closer
    alg_module_globals["Algebras"] = Algebras
    alg_module_globals["Malcev"] = Malcev
    alg_module_globals["ProductAlgebra"] = ProductAlgebra
    alg_module_globals["PowerAlgebra"] = PowerAlgebra
    alg_module_globals["QuotientAlgebra"] = QuotientAlgebra
    alg_module_globals["SubProductAlgebra"] = SubProductAlgebra
    alg_module_globals["BigProductAlgebra"] = BigProductAlgebra
    alg_module_globals["CloserTiming"] = CloserTiming
    alg_module_globals["_LibCloserTiming"] = _LibCloserTiming
    alg_module_globals["_CON_ALGEBRAS"] = _CON_ALGEBRAS
    if _LibReductAlgebra is not None:
        alg_module_globals["ReductAlgebra"] = ReductAlgebra
        alg_module_globals["_LibReductAlgebra"] = _LibReductAlgebra
        try:
            _LibReductAlgebra.congruenceAsAlgebra = staticmethod(
                ReductAlgebra.congruenceAsAlgebra
            )
        except (TypeError, AttributeError):
            _LibReductAlgebra.congruenceAsAlgebra = ReductAlgebra.congruenceAsAlgebra
    if _LibSubalgebra is not None:
        alg_module_globals["Subalgebra"] = Subalgebra
        alg_module_globals["_LibSubalgebra"] = _LibSubalgebra
    if _LibQuotientElement is not None:
        alg_module_globals["QuotientElement"] = _LibQuotientElement
        alg_module_globals["_LibQuotientElement"] = _LibQuotientElement
    if _LibAlgebraFromMinimalSets is not None:
        alg_module_globals["AlgebraFromMinimalSets"] = AlgebraFromMinimalSets
        alg_module_globals["_LibAlgebraFromMinimalSets"] = _LibAlgebraFromMinimalSets
    if _LibMatrixPowerAlgebra is not None:
        alg_module_globals["MatrixPowerAlgebra"] = MatrixPowerAlgebra
        alg_module_globals["_LibMatrixPowerAlgebra"] = _LibMatrixPowerAlgebra
    if _LibPolinLikeAlgebra is not None:
        alg_module_globals["PolinLikeAlgebra"] = PolinLikeAlgebra
        alg_module_globals["_LibPolinLikeAlgebra"] = _LibPolinLikeAlgebra
    if _LibUnaryTermsMonoid is not None:
        alg_module_globals["UnaryTermsMonoid"] = UnaryTermsMonoid
        alg_module_globals["_LibUnaryTermsMonoid"] = _LibUnaryTermsMonoid
    if _LibGeneralAlgebra is not None:
        alg_module_globals["GeneralAlgebra"] = GeneralAlgebra
        alg_module_globals["_LibGeneralAlgebra"] = _LibGeneralAlgebra
    if _LibAlgebraWithGeneratingVector is not None:
        alg_module_globals["AlgebraWithGeneratingVector"] = AlgebraWithGeneratingVector
        alg_module_globals["_LibAlgebraWithGeneratingVector"] = _LibAlgebraWithGeneratingVector
    alg_module_globals["ParameterizedAlgebra"] = ParameterizedAlgebra
    if _LibParameterizedAlgebra is not None:
        alg_module_globals["_LibParameterizedAlgebra"] = _LibParameterizedAlgebra
    # Keep native classes available for isinstance checks / advanced use
    alg_module_globals["_LibBasicAlgebra"] = _LibBasicAlgebra
    alg_module_globals["_LibFreeAlgebra"] = _LibFreeAlgebra
    alg_module_globals["_LibProductAlgebra"] = _LibProductAlgebra
    alg_module_globals["_LibPowerAlgebra"] = _LibPowerAlgebra
    alg_module_globals["_LibQuotientAlgebra"] = _LibQuotientAlgebra
    alg_module_globals["_LibSubProductAlgebra"] = _LibSubProductAlgebra
    alg_module_globals["_LibBigProductAlgebra"] = _LibBigProductAlgebra
    alg_module_globals["_LibAbstractOperation"] = _LibAbstractOperation
    alg_module_globals["_LibHomomorphism"] = _LibHomomorphism
    alg_module_globals["_LibCloser"] = _LibCloser

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
            "getVariableToGeneratorMap": "get_variable_to_generator_map",
            "getIdempotentTerms": "get_idempotent_terms",
            "superAlgebra": "super_algebra",
            "algebraType": "algebra_type",
            "switchXandYAutomorphism": "switch_x_and_y_automorphism",
            "findEquationOfAnotB": "findEquationOfAnotB",
        },
        "Homomorphism": {
            "getDomain": "get_domain",
            "setDomain": "set_domain",
            "getRange": "get_range",
            "setRange": "set_range",
            "getMap": "get_map",
            "setMap": "set_map",
            "kernel": "kernel",
            "toString": "toString",
            "productHomo": "productHomo",
        },
        "Closer": {
            "getAnswer": "get_answer",
            "sgClose": "sg_close",
            "sgCloseParallel": "sgCloseParallel",
            "sgClosePower": "sg_close_power",
            "close": "close",
            "getmaxSize": "getmaxSize",
            "setMaxSize": "set_max_size",
            "getGenerators": "get_generators",
            "setGenerators": "set_generators",
            "getTermMap": "get_term_map",
            "setTermMap": "set_term_map",
            "getElementToFind": "get_element_to_find",
            "setElementToFind": "set_element_to_find",
            "getElementsToFind": "get_elements_to_find",
            "setElementsToFind": "set_elements_to_find",
            "allElementsFound": "all_elements_found",
            "getBlocks": "get_blocks",
            "setBlocks": "set_blocks",
            "getValues": "get_values",
            "setValues": "set_values",
            "getSetConstraint": "get_set_constraint",
            "setConstraintSet": "set_constraint_set",
            "getIndexForConstraintSet": "getIndexForConstraintSet",
            "setIndexForConstraintSet": "set_index_for_constraint_set",
            "getIndexForCongruenceConstraint": "getIndexForCongruenceConstraint",
            "setIndexForCongruenceConstraint": "set_index_for_congruence_constraint",
            "getCongruenceConstraintElemIndex": "getCongruenceConstraintElemIndex",
            "setCongruenceConstraintElemIndex": "set_congruence_constraint_elem_index",
            "getCongruenceForCongruenceConstraint": "get_congruence_for_congruence_constraint",
            "setCongruenceForCongruenceConstraint": "set_congruence_for_congruence_constraint",
            "setupCongruenceConstraint": "setup_congruence_constraint",
            "getFailingEquation": "get_failing_equation",
            "getImageAlgebra": "get_image_algebra",
            "setImageAlgebra": "set_image_algebra",
            "getHomomorphism": "get_homomorphism",
            "setHomomorphism": "set_homomorphism",
            "getTermMapForOperations": "get_term_map_for_operations",
            "setRootAlgebra": "set_root_algebra",
            "setOperations": "set_operations",
            "isSuppressOutput": "is_suppress_output",
            "setSuppressOutput": "set_suppress_output",
        },
        "Algebras": {},
        "ProductAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "numberOfFactors": "number_of_factors",
            "getOperation": "getOperation",
            "getElement": "get_element_tuple",
            "elementIndex": "element_index_tuple",
            "getUniverseList": "get_universe_list",
            "getUniverseOrder": "get_universe_order",
            "algebraType": "algebra_type",
            "factors": "factors",
            "parents": "parents",
            "parent": "parent",
            "projection": "projection",
            "projectionKernel": "projection_kernel",
            "Sg": "Sg",
            "sgClose": "sg_close",
            "makeOperationTables": "make_operation_tables",
            "convertToDefaultValueOps": "convertToDefaultValueOps",
            "con": "con",
            "sub": "sub",
        },
        "PowerAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "getRoot": "get_root",
            "getPower": "get_power",
            "parent": "parent",
            "parents": "parents",
            "getElement": "get_element_tuple",
            "elementIndex": "element_index",
            "getUniverseList": "get_universe_list",
            "algebraType": "algebra_type",
            "factors": "factors",
            "projection": "projection",
            "numberOfFactors": "number_of_factors",
            "convertToDefaultValueOps": "convertToDefaultValueOps",
            "con": "con",
            "sub": "sub",
            "makeOperationTables": "make_operation_tables",
        },
        "QuotientAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "superAlgebra": "super_algebra",
            "getCongruence": "get_congruence",
            "getElement": "get_element",
            "elementIndex": "element_index",
            "representativeIndex": "representative_index",
            "canonicalHomomorphism": "canonical_homomorphism",
            "getUniverseList": "get_universe_list",
            "getUniverseOrder": "get_universe_order",
            "algebraType": "algebra_type",
            "convertToDefaultValueOps": "convertToDefaultValueOps",
            "con": "con",
            "sub": "sub",
            "makeOperationTables": "make_operation_tables",
            "universe": "universe",
        },
        "QuotientElement": {
            "getAlgebra": "get_algebra",
            "superAlgebra": "super_algebra",
            "getCongruence": "get_congruence",
            "getIndex": "get_index",
            "getIndexInSuperAlgebra": "get_index_in_super_algebra",
            "toString": "toString",
        },
        "SubProductAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "generators": "generators",
            "getProductAlgebra": "get_product_algebra",
            "superAlgebra": "super_algebra",
            "getElement": "get_element",
            "elementIndex": "element_index",
            "getUniverseList": "get_universe_list",
            "getUniverseOrder": "get_universe_order",
            "algebraType": "algebra_type",
            "convertToDefaultValueOps": "convertToDefaultValueOps",
            "getTerms": "get_terms",
            "getTerm": "get_term",
            "getVariableToGeneratorMap": "get_variable_to_generator_map",
            "getVariables": "get_variables",
            "con": "con",
            "sub": "sub",
            "makeOperationTables": "make_operation_tables",
        },
        "BigProductAlgebra": {
            "numberOfFactors": "number_of_factors",
            "getNumberOfFactors": "getNumberOfFactors",
            "getPowers": "getPowers",
            "isPower": "isPower",
            "rootFactors": "rootFactors",
            "sizeMultiplicities": "sizeMultiplicities",
            "getConstants": "getConstants",
            "getConstantSymbol": "getConstantSymbol",
            "getConstantTerm": "getConstantTerm",
            "sgClose": "sgClose",
            "operations": "operations",
            "projectionKernel": "projectionKernel",
            "makeOperationTables": "makeOperationTables",
            "getName": "getName",
            "cardinality": "cardinality",
            "factors": "factors",
            "projection": "projection",
        },
        "CloserTiming": {
            "updatePass": "updatePass",
            "incrementApps": "incrementApps",
            "incrementNextPassSize": "incrementNextPassSize",
        },
        "MaltsevProductDecomposition": {
            "getBlockAlgebras": "getBlockAlgebras",
            "getQuotientAlgebra": "getQuotientAlgebra",
            "getCongruence": "getCongruence",
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
            "congruenceAsAlgebra": "congruenceAsAlgebra",
        },
        "AlgebraFromMinimalSets": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "getElement": "get_element",
            "elementIndex": "element_index",
            "getUniverseList": "get_universe_list",
            "algebraType": "algebra_type",
        },
        "MatrixPowerAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "getRoot": "get_root",
            "getPower": "get_power",
            "getPowerAlgebra": "get_power_algebra",
            "parent": "parent",
            "parents": "parents",
            "getElement": "getElement",
            "elementIndex": "elementIndex",
            "getUniverseList": "getUniverseList",
            "algebraType": "algebra_type",
            "convertToDefaultValueOps": "convertToDefaultValueOps",
            "con": "con",
            "sub": "sub",
        },
        "PolinLikeAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "getElement": "getElement",
            "elementIndex": "elementIndex",
            "getUniverseList": "getUniverseList",
            "algebraType": "algebra_type",
            "convertToDefaultValueOps": "convertToDefaultValueOps",
            "con": "con",
            "sub": "sub",
            "polinizeOperation": "polinize_operation",
            "constructPolinAlgebra": "construct_polin_algebra",
        },
        "UnaryTermsMonoid": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "getElement": "getElement",
            "elementIndex": "elementIndex",
            "getUniverseList": "get_universe_list",
            "algebraType": "algebra_type",
            "parent": "parent",
            "convertToDefaultValueOps": "convertToDefaultValueOps",
            "isUnary": "isUnary",
        },
        "GeneralAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "getDescription": "description",
            "setDescription": "set_description",
            "universe": "universe",
            "operations": "operations",
            "parent": "parent",
            "parents": "parents",
            "con": "con",
            "sub": "sub",
        },
        "AlgebraWithGeneratingVector": {
            "getAlgebra": "get_algebra",
            "getVector": "get_vector",
            "isImageOf": "is_image_of",
            "toString": "toString",
            "compareTo": "compareTo",
            "equals": "equals",
            "siDecompose": "siDecompose",
        },
        "ParameterizedAlgebra": {
            "getParameterMap": "getParameterMap",
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
            "getUniverseOrder": "get_universe_order",
            "restrictPartition": "restrict_partition",
            "convertToDefaultValueOps": "convertToDefaultValueOps",
            "con": "con",
            "sub": "sub",
            "makeOperationTables": "make_operation_tables",
            "universe": "universe",
            "parent": "parent",
            "parents": "parents",
        },
        "SubalgebraLattice": {
            "iterator": "iterator",
            "Sg": "Sg",
            "sg": "sg",
        },
        "Malcev": {},
    }

    def _apply_class_aliases() -> None:
        for class_name, aliases in alg_module_globals["_CLASS_ALIASES"].items():
            cls = {
                "BasicAlgebra": _LibBasicAlgebra,
                "FreeAlgebra": _LibFreeAlgebra,
                "Homomorphism": _LibHomomorphism,
                "Closer": _LibCloser,
                "ProductAlgebra": _LibProductAlgebra,
                "PowerAlgebra": _LibPowerAlgebra,
                "QuotientAlgebra": _LibQuotientAlgebra,
                "QuotientElement": _LibQuotientElement,
                "SubProductAlgebra": _LibSubProductAlgebra,
                "BigProductAlgebra": _LibBigProductAlgebra,
                "CloserTiming": _LibCloserTiming,
                "MaltsevProductDecomposition": _LibMaltsevProductDecomposition,
                "SubalgebraLattice": _LibSubalgebraLattice,
                "ReductAlgebra": _LibReductAlgebra,
                "Subalgebra": _LibSubalgebra,
                "AlgebraFromMinimalSets": _LibAlgebraFromMinimalSets,
                "MatrixPowerAlgebra": _LibMatrixPowerAlgebra,
                "PolinLikeAlgebra": _LibPolinLikeAlgebra,
                "UnaryTermsMonoid": _LibUnaryTermsMonoid,
                "GeneralAlgebra": _LibGeneralAlgebra,
                "AlgebraWithGeneratingVector": _LibAlgebraWithGeneratingVector,
                "ParameterizedAlgebra": ParameterizedAlgebra,
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
