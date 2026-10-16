"""Jython-facing helpers for ``org.uacalc.alg.op`` (CPython only).

Renames, overload dispatch, and Java exception translation only. Library
logic stays in ``uacalc_lib``.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

from org.uacalc._exceptions import (
    ClassCastException,
    IllegalArgumentException,
    NullPointerException,
    UnsupportedOperationException,
    translate_illegal_argument,
)


def _install(op_globals: dict) -> None:
    IntOperation = op_globals["IntOperation"]
    BasicOperation = op_globals.get("BasicOperation")
    OperationWithDefaultValue = op_globals.get("OperationWithDefaultValue")
    TermOperationImp = op_globals.get("TermOperationImp")
    SimilarityType = op_globals["SimilarityType"]
    OperationSymbol = op_globals["OperationSymbol"]
    _LibOperations = op_globals["Operations"]

    def _raise_npe(what: str = "null") -> None:
        raise NullPointerException(what)

    def _lib_call(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as exc:
            msg = str(exc)
            if "Unsupported operation" in msg:
                raise ClassCastException(msg) from exc
            translate_illegal_argument(exc)

    # PyIntOperation is not weakrefable and compares by value, so record
    # construction by identity. Java IntOperationImp / value-at / function
    # constructors leave AbstractOperation.isTableBased() as false; only
    # factories that override it (makeIntOperation(op), constants) are true.
    _CONSTRUCTED_TABLE_BASED = {}

    def _mark_constructed(op: Any, table_based: bool) -> Any:
        if op is None:
            return op
        _CONSTRUCTED_TABLE_BASED[id(op)] = (op, bool(table_based))
        return op

    def _mark_constructed_list(ops: Any, table_based: bool) -> list:
        return [_mark_constructed(op, table_based) for op in list(ops)]

    def _recorded_table_based(op: Any) -> Optional[bool]:
        item = _CONSTRUCTED_TABLE_BASED.get(id(op))
        if item is None:
            return None
        stored, flag = item
        if stored is op:
            return flag
        return None

    def _op_is_table_based(op: Any) -> bool:
        recorded = _recorded_table_based(op)
        if recorded is not None:
            return recorded
        return False

    def _as_int_list(args: Any) -> list:
        if args is None:
            _raise_npe()
        try:
            seq = list(args)
        except TypeError as exc:
            raise TypeError(str(exc)) from exc
        out = []
        for x in seq:
            try:
                out.append(int(x))
            except (TypeError, ValueError) as exc:
                raise TypeError(str(exc)) from exc
        return out

    def _int_value_at(self: Any, args: Any) -> int:
        if args is None:
            _raise_npe()
        if isinstance(args, bool):
            return int(_lib_call(self.int_value_at_horner, int(args)))
        if isinstance(args, int):
            return int(_lib_call(self.int_value_at_horner, args))
        return int(_lib_call(self.int_value_at, _as_int_list(args)))

    def _value_at(self: Any, args: Any) -> int:
        # Jython None hits Java valueAt(int[][]), which throws UOE.
        if args is None:
            raise UnsupportedOperationException()
        # Jython lists always hit Java valueAt(List), never valueAt(int[][]).
        return _int_value_at(self, args)

    def _get_table(self: Any, makeTable: Optional[bool] = None) -> Any:
        if makeTable is None:
            table = self.get_table() if hasattr(self, "get_table") else None
            return None if table is None else list(table)
        force = getattr(self, "get_table_force", None)
        if force is not None:
            table = _lib_call(force, bool(makeTable))
            return None if table is None else list(table)
        if makeTable and hasattr(self, "make_table"):
            _lib_call(self.make_table)
        table = self.get_table() if hasattr(self, "get_table") else None
        return None if table is None else list(table)

    def _make_table(self: Any) -> None:
        if hasattr(self, "make_table"):
            _lib_call(self.make_table)

    def _get_set_size(self: Any) -> int:
        return int(self.get_set_size())

    def _is_table_based(self: Any) -> bool:
        return _op_is_table_based(self)

    def _is_idempotent(self: Any) -> bool:
        return bool(_lib_call(self.is_idempotent))

    def _is_associative(self: Any) -> bool:
        return bool(_lib_call(self.is_associative))

    def _is_commutative(self: Any) -> bool:
        return bool(_lib_call(self.is_commutative))

    def _is_totally_symmetric(self: Any) -> bool:
        return bool(_lib_call(self.is_totally_symmetric))

    def _is_maltsev(self: Any) -> bool:
        return bool(_lib_call(self.is_maltsev))

    def _is_total(self: Any) -> bool:
        return bool(_lib_call(self.is_total))

    _OPERATION_ALIASES = {
        "intValueAt": _int_value_at,
        "valueAt": _value_at,
        "getTable": _get_table,
        "makeTable": _make_table,
        "getSetSize": _get_set_size,
        "isTableBased": _is_table_based,
        "isIdempotent": _is_idempotent,
        "isAssociative": _is_associative,
        "isCommutative": _is_commutative,
        "isTotallySymmetric": _is_totally_symmetric,
        "isMaltsev": _is_maltsev,
        "isTotal": _is_total,
    }

    for cls in (
        IntOperation,
        BasicOperation,
        OperationWithDefaultValue,
        TermOperationImp,
    ):
        if cls is None:
            continue
        for camel, impl in _OPERATION_ALIASES.items():
            # Always overwrite: alg/_jython_compat may have copied the
            # snake_case PyO3 method onto the camelCase name already.
            try:
                setattr(cls, camel, impl)
            except (TypeError, AttributeError):
                pass

    # --- SimilarityType ---
    _SIM_ALIASES = {
        "getOperationSymbols": "get_operation_symbols",
        "getSortedOperationSymbols": "get_sorted_operation_symbols",
        "inputSize": "input_size",
        "getAritiesMap": "get_arities_map",
        "getMaxArity": "get_max_arity",
        "aritiesString": "arities_string",
    }
    for camel, snake in _SIM_ALIASES.items():
        if not hasattr(SimilarityType, camel) and hasattr(SimilarityType, snake):
            try:
                setattr(SimilarityType, camel, getattr(SimilarityType, snake))
            except (TypeError, AttributeError):
                pass
    if hasattr(SimilarityType, "lattice_similarity_type"):
        try:
            SimilarityType.LATTICE_SIMILARITY_TYPE = (
                SimilarityType.lattice_similarity_type()
            )
        except (TypeError, AttributeError):
            pass
    if hasattr(SimilarityType, "group_similarity_type"):
        try:
            SimilarityType.GROUP_SIMILARITY_TYPE = SimilarityType.group_similarity_type()
        except (TypeError, AttributeError):
            pass
    if not hasattr(SimilarityType, "equals"):
        try:
            SimilarityType.equals = SimilarityType.__eq__
        except (TypeError, AttributeError):
            pass
    if not hasattr(SimilarityType, "toString"):
        try:
            SimilarityType.toString = SimilarityType.__str__
        except (TypeError, AttributeError):
            pass
    if hasattr(SimilarityType, "hash_code"):
        try:
            SimilarityType.hashCode = SimilarityType.hash_code
        except (TypeError, AttributeError):
            pass

    if hasattr(OperationSymbol, "hash_code"):
        try:
            OperationSymbol.hashCode = OperationSymbol.hash_code
        except (TypeError, AttributeError):
            pass
    if hasattr(OperationSymbol, "compare_to"):
        try:
            OperationSymbol.compareTo = OperationSymbol.compare_to
        except (TypeError, AttributeError):
            pass
    if not hasattr(OperationSymbol, "equals"):
        try:
            OperationSymbol.equals = OperationSymbol.__eq__
        except (TypeError, AttributeError):
            pass
    if not hasattr(OperationSymbol, "toString"):
        try:
            OperationSymbol.toString = OperationSymbol.__str__
        except (TypeError, AttributeError):
            pass

    class Operation(object):
        """Java ``org.uacalc.alg.op.Operation`` surface (instances are bound ops)."""

        def arity(self):
            raise NotImplementedError

        def getSetSize(self):
            raise NotImplementedError

        def symbol(self):
            raise NotImplementedError

        def valueAt(self, args):
            raise NotImplementedError

        def intValueAt(self, args):
            raise NotImplementedError

        def makeTable(self):
            raise NotImplementedError

        def getTable(self, makeTable=None):
            raise NotImplementedError

        def isTableBased(self):
            raise NotImplementedError

        def isIdempotent(self):
            raise NotImplementedError

        def isAssociative(self):
            raise NotImplementedError

        def isCommutative(self):
            raise NotImplementedError

        def isTotallySymmetric(self):
            raise NotImplementedError

        def isMaltsev(self):
            raise NotImplementedError

        def isTotal(self):
            raise NotImplementedError

    def _write_csv(out: Any, text: str) -> None:
        if out is None:
            _raise_npe()
        write = getattr(out, "write", None)
        if callable(write):
            write(text)
            return
        print_ = getattr(out, "print", None)
        if callable(print_):
            print_(text)
            return
        raise TypeError("binaryOpToCSV out must be a writable stream")

    class Operations(object):
        """Static facade matching Java ``org.uacalc.alg.op.Operations``."""

        _lib = _LibOperations

        @staticmethod
        def commutes(*args):
            if len(args) == 2:
                unary_op, op = args
                if unary_op is None or op is None:
                    _raise_npe()
                return _lib_call(Operations._lib.commutes, unary_op, op)
            if len(args) == 3:
                mapping, op0, op1 = args
                if mapping is None or op0 is None or op1 is None:
                    _raise_npe()
                return _lib_call(
                    Operations._lib.commutes_map, _as_int_list(mapping), op0, op1
                )
            raise TypeError("commutes() takes 2 or 3 arguments")

        @staticmethod
        def isTotal(op):
            # Java: only OperationWithDefaultValue can fail; null is not that type.
            if op is None:
                return True
            return _lib_call(Operations._lib.is_total, op)

        @staticmethod
        def isIdempotent(op):
            if op is None:
                _raise_npe()
            return _lib_call(Operations._lib.is_idempotent, op)

        @staticmethod
        def isCommutative(op):
            if op is None:
                _raise_npe()
            return _lib_call(Operations._lib.is_commutative, op)

        @staticmethod
        def isTotallySymmetric(op):
            if op is None:
                _raise_npe()
            return _lib_call(Operations._lib.is_totally_symmetric, op)

        @staticmethod
        def isAssociative(op):
            if op is None:
                _raise_npe()
            return _lib_call(Operations._lib.is_associative, op)

        @staticmethod
        def isMaltsev(op):
            if op is None:
                _raise_npe()
            return _lib_call(Operations._lib.is_maltsev, op)

        @staticmethod
        def findDifference(op0, op1, report=None):
            if op0 is None or op1 is None:
                _raise_npe()
            if report is not None:
                raise NotImplementedError(
                    "findDifference(op, op, ProgressReport) is not bound"
                )
            return _lib_call(Operations._lib.find_difference, op0, op1)

        @staticmethod
        def equalValues(op0, op1):
            if op0 is None or op1 is None:
                _raise_npe()
            return _lib_call(Operations._lib.equal_values, op0, op1)

        @staticmethod
        def makeMap(ops):
            if ops is None:
                _raise_npe()
            return _lib_call(Operations._lib.make_map, list(ops))

        @staticmethod
        def makeIntOperation(*args):
            if len(args) == 1:
                op = args[0]
                if op is None:
                    _raise_npe()
                # Java: if (opx.isTableBased()) return opx;
                if _op_is_table_based(op):
                    return op
                try:
                    result = Operations._lib.make_int_operation_from_op(op)
                except (TypeError, ValueError) as exc:
                    raise TypeError(str(exc)) from exc
                return _mark_constructed(result, True)
            if len(args) == 3:
                symbol, alg_size, table = args
                if symbol is None or table is None:
                    _raise_npe()
                # Java IntOperationImp does not override isTableBased().
                return _mark_constructed(
                    _lib_call(
                        Operations._lib.make_int_operation,
                        symbol,
                        int(alg_size),
                        list(table),
                    ),
                    False,
                )
            if len(args) == 4:
                name, arity, alg_size, table = args
                if name is None or table is None:
                    _raise_npe()
                return _mark_constructed(
                    _lib_call(
                        Operations._lib.make_int_operation,
                        str(name),
                        int(arity),
                        int(alg_size),
                        list(table),
                    ),
                    False,
                )
            raise TypeError("makeIntOperation() takes 1, 3, or 4 arguments")

        @staticmethod
        def makeIntOperations(ops):
            if ops is None:
                _raise_npe()
            try:
                results = Operations._lib.make_int_operations(list(ops))
            except ValueError as exc:
                raise ClassCastException(str(exc)) from exc
            return _mark_constructed_list(results, True)

        @staticmethod
        def makeBinaryIntOperation(symbol, algSize, table):
            if symbol is None or table is None:
                _raise_npe()
            rows = list(table)
            if rows and not isinstance(rows[0], (list, tuple)):
                return _mark_constructed(
                    _lib_call(
                        Operations._lib.make_binary_int_operation,
                        symbol,
                        int(algSize),
                        [int(x) for x in rows],
                    ),
                    False,
                )
            flat = []
            for row in rows:
                flat.extend(int(x) for x in list(row))
            return _mark_constructed(
                _lib_call(
                    Operations._lib.make_binary_int_operation, symbol, int(algSize), flat
                ),
                False,
            )

        @staticmethod
        def makeConstantIntOperation(*args):
            if len(args) == 2:
                alg_size, elt = args
                return _mark_constructed(
                    _lib_call(
                        Operations._lib.make_constant_int_operation,
                        int(alg_size),
                        int(elt),
                    ),
                    True,
                )
            if len(args) == 3:
                prefix, alg_size, elt = args
                if prefix is None:
                    _raise_npe()
                return _mark_constructed(
                    _lib_call(
                        Operations._lib.make_constant_int_operation,
                        str(prefix),
                        int(alg_size),
                        int(elt),
                    ),
                    True,
                )
            raise TypeError("makeConstantIntOperation() takes 2 or 3 arguments")

        @staticmethod
        def makeConstantIntOperations(algSize):
            return _mark_constructed_list(
                _lib_call(Operations._lib.make_constant_int_operations, int(algSize)),
                True,
            )

        @staticmethod
        def makeTransposition(algSize, a0, a1):
            return _mark_constructed(
                _lib_call(
                    Operations._lib.make_transposition, int(algSize), int(a0), int(a1)
                ),
                False,
            )

        @staticmethod
        def makeFullCycle(algSize):
            return _mark_constructed(
                _lib_call(Operations._lib.make_full_cycle, int(algSize)), False
            )

        @staticmethod
        def ternaryDiscriminator(size):
            return _mark_constructed(
                _lib_call(Operations._lib.ternary_discriminator, int(size)), False
            )

        @staticmethod
        def makeRandomOperation(n, opSym, seed=None):
            if opSym is None:
                _raise_npe()
            if seed is None:
                return _mark_constructed(
                    _lib_call(Operations._lib.make_random_operation, int(n), opSym),
                    False,
                )
            return _mark_constructed(
                _lib_call(
                    Operations._lib.make_random_operation_with_seed,
                    int(n),
                    opSym,
                    int(seed),
                ),
                False,
            )

        @staticmethod
        def makeRandomOperations(n, simType, seed=None):
            if simType is None:
                _raise_npe()
            if seed is None:
                return _mark_constructed_list(
                    _lib_call(Operations._lib.make_random_operations, int(n), simType),
                    False,
                )
            return _mark_constructed_list(
                _lib_call(
                    Operations._lib.make_random_operations_with_seed,
                    int(n),
                    simType,
                    int(seed),
                ),
                False,
            )

        @staticmethod
        def makeDerivedOperation(op, reductionArray, newArity):
            if op is None or reductionArray is None:
                _raise_npe()
            return _mark_constructed(
                _lib_call(
                    Operations._lib.make_derived_operation,
                    op,
                    _as_int_list(reductionArray),
                    int(newArity),
                ),
                False,
            )

        @staticmethod
        def makeJonssonOperationsFromNUF(nuf):
            if nuf is None:
                _raise_npe()
            return _mark_constructed_list(
                _lib_call(Operations._lib.make_jonsson_operations_from_nuf, nuf),
                False,
            )

        @staticmethod
        def power(base, pow):
            return int(_lib_call(Operations._lib.power, int(base), int(pow)))

        @staticmethod
        def makeLeftShift(vecSize, rootSize):
            return _mark_constructed(
                _lib_call(
                    Operations._lib.make_left_shift, int(vecSize), int(rootSize)
                ),
                False,
            )

        @staticmethod
        def makeBinaryLeftShift(vecSize, rootSize):
            return _mark_constructed(
                _lib_call(
                    Operations._lib.make_binary_left_shift, int(vecSize), int(rootSize)
                ),
                False,
            )

        @staticmethod
        def makeMatrixDiagonalOp(vecSize, rootSize):
            return _mark_constructed(
                _lib_call(
                    Operations._lib.make_matrix_diagonal_op, int(vecSize), int(rootSize)
                ),
                False,
            )

        @staticmethod
        def makeModuleOperation(modulus, coeffs):
            if coeffs is None:
                _raise_npe()
            return _mark_constructed(
                _lib_call(
                    Operations._lib.make_module_operation,
                    int(modulus),
                    _as_int_list(coeffs),
                ),
                False,
            )

        @staticmethod
        def makeCompositionOp(n, pow):
            return _mark_constructed(
                _lib_call(Operations._lib.make_composition_op, int(n), int(pow)),
                False,
            )

        @staticmethod
        def binaryOpToCSV(desc, binop, out):
            if desc is None or binop is None:
                _raise_npe()
            text = _lib_call(Operations._lib.binary_op_to_csv, str(desc), binop)
            _write_csv(out, text)

    # --- TermOperation / TermOperationImp ---
    _LibTOI = op_globals.get("TermOperationImp")
    if _LibTOI is None:
        try:
            import uacalc_lib as _uacalc_lib

            _LibTOI = getattr(getattr(_uacalc_lib, "terms", None), "TermOperationImp", None)
        except Exception:
            _LibTOI = None

    _TOI_STATE: dict = {}

    def _toi_state(obj: Any) -> dict:
        slot = _TOI_STATE.get(id(obj))
        if slot is None or slot[0] is not obj:
            slot = (obj, {})
            _TOI_STATE[id(obj)] = slot
        return slot[1]

    def _as_alg(alg: Any) -> Any:
        if alg is None:
            _raise_npe()
        inner = getattr(alg, "_inner", alg)
        conv = getattr(inner, "to_basic_algebra", None) or getattr(alg, "to_basic_algebra", None)
        tname = type(inner).__name__
        if tname not in ("PyBasicAlgebra", "BasicAlgebra") and callable(conv):
            return conv()
        return inner

    def _patch_toi() -> None:
        if _LibTOI is None:
            return
        _orig_get_term = getattr(_LibTOI, "get_term", None)
        _orig_get_vars = getattr(_LibTOI, "get_ordered_variables", None)
        _orig_iva = getattr(_LibTOI, "int_value_at", None)
        _orig_get_table = getattr(_LibTOI, "get_table", None)

        def getTerm(self: Any) -> Any:
            stored = _toi_state(self).get("term")
            if stored is not None:
                return stored
            if callable(_orig_get_term):
                return _orig_get_term(self)
            return None

        def getOrderedVariables(self: Any) -> Any:
            stored = _toi_state(self).get("variables")
            if stored is not None:
                return list(stored)
            if callable(_orig_get_vars):
                return list(_orig_get_vars(self))
            return []

        def intValueAt(self: Any, args: Any) -> int:
            return int(_int_value_at(self, args))

        def valueAt(self: Any, args: Any) -> Any:
            # Java TermOperationImp.valueAt delegates to the anonymous
            # interpretation Operation, whose valueAt(List) is a stub
            # that always returns null.
            return None

        def makeTable(self: Any) -> None:
            # Java TermOperationImp.makeTable is AbstractOperation's no-op.
            return None

        def _ensure_table_op(self: Any) -> Any:
            state = _toi_state(self)
            table_op = state.get("tableOp")
            if table_op is not None:
                return table_op
            size = int(self.getSetSize()) if hasattr(self, "getSetSize") else int(self.get_set_size())
            arity = int(self.arity())
            total = 1
            for _ in range(arity):
                total *= size
            values = []
            for idx in range(total):
                args = []
                remaining = idx
                for _ in range(arity):
                    args.append(remaining % size)
                    remaining //= size
                values.append(int(intValueAt(self, args)))
            term = getTerm(self)
            name = "Op_" + (str(term) if term is not None else "term")
            table_op = Operations.makeIntOperation(OperationSymbol(name, arity), size, values)
            state["tableOp"] = table_op
            return table_op

        def getTable(self: Any, makeTable: Optional[bool] = None) -> Any:
            # Java interpretation.getTable() uses tableOp without building it;
            # getTable(true) calls makeTable first. Horner encoding: args[0] LSB.
            if makeTable:
                table_op = _ensure_table_op(self)
            else:
                table_op = _toi_state(self).get("tableOp")
            if table_op is None:
                raise NullPointerException(
                    'Cannot invoke "org.uacalc.alg.op.Operation.getTable()" '
                    'because "this.tableOp" is null'
                )
            getter = getattr(table_op, "getTable", None) or getattr(table_op, "get_table", None)
            tab = getter() if callable(getter) else None
            return None if tab is None else list(tab)

        def toString(self: Any) -> str:
            term = getTerm(self)
            return str(term) if term is not None else str(self)

        for camel, impl in {
            "getTerm": getTerm,
            "getOrderedVariables": getOrderedVariables,
            "intValueAt": intValueAt,
            "valueAt": valueAt,
            "makeTable": makeTable,
            "getTable": getTable,
            "toString": toString,
        }.items():
            try:
                setattr(_LibTOI, camel, impl)
            except (TypeError, AttributeError):
                pass

    _patch_toi()

    class _TermOpMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            return isinstance(instance, _LibTOI) if _LibTOI else False

    class TermOperation(object, metaclass=_TermOpMeta):
        """Java ``org.uacalc.alg.op.TermOperation`` surface."""

        def getTerm(self):
            raise NotImplementedError

        def getOrderedVariables(self):
            raise NotImplementedError

    class _TOIMeta(type):
        def __instancecheck__(cls, instance: Any) -> bool:
            if instance is None:
                return False
            if type(instance) is cls:
                return True
            return isinstance(instance, _LibTOI) if _LibTOI else False

    class TermOperationImp(object, metaclass=_TOIMeta):
        def __new__(cls, *args: Any):
            if _LibTOI is None:
                raise TypeError("TermOperationImp is not bound")
            if len(args) == 3:
                term, variables, alg = args
                name = None
            elif len(args) == 4:
                name, term, variables, alg = args
            else:
                raise TypeError("TermOperationImp() takes 3 or 4 arguments")
            if term is None or variables is None or alg is None:
                _raise_npe()
            vars_list = list(variables)
            inner_alg = _as_alg(alg)
            if name is None:
                obj = _lib_call(_LibTOI, term, vars_list, inner_alg)
            else:
                obj = _lib_call(_LibTOI, term, vars_list, inner_alg, str(name))
            _toi_state(obj)["term"] = term
            _toi_state(obj)["variables"] = vars_list
            return obj

        def getTerm(self):
            raise NotImplementedError

        def getOrderedVariables(self):
            raise NotImplementedError

        def intValueAt(self, args):
            raise NotImplementedError

        def valueAt(self, args):
            raise NotImplementedError

        def makeTable(self):
            raise NotImplementedError

        def getTable(self, makeTable=None):
            raise NotImplementedError

        def toString(self):
            raise NotImplementedError

    # --- ParameterizedOperation (Java: default ctor + makeOp / subParmValues) ---
    class ParameterizedOperation(object):
        def __init__(self) -> None:
            self.algebra = None
            self.name = None
            self.symbolName = None
            self.setSizeExp = None
            self.parameterNames = None
            self.arityExp = None
            self.description = None
            self.defaultValueExp = None
            self.definitionExp = None

        @staticmethod
        def subParmValues(parameterizedString, parmMap):
            if parameterizedString is None:
                _raise_npe()
            # Java currently returns the string unchanged.
            return parameterizedString

        def makeOp(self, parmMap):
            if parmMap is None:
                _raise_npe()
            arity_s = ParameterizedOperation.subParmValues(self.arityExp, parmMap)
            size_s = ParameterizedOperation.subParmValues(self.setSizeExp, parmMap)
            if arity_s is None or size_s is None:
                _raise_npe()
            arity = int(str(arity_s))
            set_size = int(str(size_s))
            from org.uacalc.alg import AbstractOperation
            from org.uacalc._exceptions import UnsupportedOperationException as _UOE

            class _MaxOp(AbstractOperation):
                def valueAt(self, args):
                    raise _UOE()

                def intValueAt(self, args):
                    seq = list(args)
                    return max(int(seq[0]), int(seq[1]))

            name = self.symbolName if self.symbolName is not None else (self.name or "f")
            return _MaxOp(str(name), arity, set_size)

    # --- OperationWithDefaultValue ---
    def _is_operation(obj: Any) -> bool:
        if obj is None:
            return False
        return any(
            hasattr(obj, name)
            for name in ("intValueAt", "int_value_at", "valueAt", "value_at")
        )

    def _is_symbol(obj: Any) -> bool:
        if obj is None or _is_operation(obj):
            return False
        return hasattr(obj, "name") and hasattr(obj, "arity")

    def _horner(args: Sequence[int], size: int) -> int:
        # Match Java Horner.horner(int[], int): args[0] is least significant.
        ans = 0
        seq = list(args)
        for i in range(len(seq) - 1, -1, -1):
            ans = int(size) * ans + int(seq[i])
        return ans

    def _minus_one_table(arity: int, alg_size: int) -> list:
        n = 1
        for _ in range(int(arity)):
            n *= int(alg_size)
        return [-1] * n

    class OperationWithDefaultValue(object):
        def __init__(self, *args: Any) -> None:
            n = len(args)
            if n < 1:
                raise TypeError("OperationWithDefaultValue() missing arguments")
            self._idempotent_set = False
            self._random_value_table = None
            self._diag_indices = None
            self._op = None
            self._value_table = None
            self._default_value = -1
            self._diag_div = 1

            if n == 1:
                op = args[0]
                if op is None:
                    _raise_npe()
                make = getattr(op, "makeTable", None) or getattr(op, "make_table", None)
                if callable(make):
                    make()
                getter = getattr(op, "getTable", None) or getattr(op, "get_table", None)
                table = list(getter()) if callable(getter) else None
                self._symbol = op.symbol() if callable(getattr(op, "symbol", None)) else op.symbol
                size_fn = getattr(op, "getSetSize", None) or getattr(op, "get_set_size", None)
                self._alg_size = int(size_fn()) if callable(size_fn) else int(op.get_set_size())
                self._default_value = -1
                self._op = op
                self._value_table = table
                self._set_diag_div()
                return

            if n == 2:
                first, second = args
                if first is None:
                    _raise_npe()
                if _is_operation(first):
                    # Java (op, algSize): this.op is never assigned (stays null).
                    self._symbol = first.symbol() if callable(getattr(first, "symbol", None)) else first.symbol
                    self._alg_size = int(second)
                    self._default_value = -1
                    self._op = None
                    self._value_table = None
                    self.makeTable()
                    self._value_table = self.getTable()
                    self._set_diag_div()
                    return
                if _is_symbol(first):
                    self._symbol = first
                    self._alg_size = int(second)
                    self._default_value = -1
                    self._value_table = _minus_one_table(int(first.arity()), self._alg_size)
                    self._op = None
                    self._set_diag_div()
                    return
                raise TypeError("OperationWithDefaultValue(op_or_sym, algSize)")

            if n == 3:
                first, second, third = args
                if first is None:
                    _raise_npe()
                if _is_symbol(first):
                    self._symbol = first
                    self._alg_size = int(second)
                    self._default_value = int(third)
                    self._value_table = _minus_one_table(int(first.arity()), self._alg_size)
                    self._op = None
                    self._set_diag_div()
                    return
                raise TypeError("OperationWithDefaultValue(sym, algSize, defaultValue)")

            if n == 4:
                a, b, c, d = args
                if a is None:
                    _raise_npe()
                if isinstance(a, (str, bytes)):
                    self._symbol = OperationSymbol(str(a), int(b))
                    self._alg_size = int(c)
                    self._default_value = int(d)
                    self._value_table = _minus_one_table(int(b), self._alg_size)
                    self._op = None
                    self._set_diag_div()
                    return
                if _is_symbol(a):
                    self._symbol = a
                    self._alg_size = int(b)
                    table = None if c is None else [int(x) for x in list(c)]
                    self._default_value = int(d)
                    if table is None:
                        table = _minus_one_table(int(a.arity()), self._alg_size)
                    self._value_table = table
                    self._op = None
                    self._set_diag_div()
                    return
                raise TypeError("OperationWithDefaultValue 4-arg constructor")

            if n == 5:
                name, arity, alg_size, table, default = args
                if name is None:
                    _raise_npe()
                self._symbol = OperationSymbol(str(name), int(arity))
                self._alg_size = int(alg_size)
                self._default_value = int(default)
                if table is None:
                    self._value_table = _minus_one_table(int(arity), self._alg_size)
                else:
                    self._value_table = [int(x) for x in list(table)]
                self._op = None
                self._set_diag_div()
                return

            raise TypeError("OperationWithDefaultValue() takes 1 to 5 arguments")

        def _set_diag_div(self) -> None:
            arity = int(self.arity())
            if arity < 3:
                self._diag_div = 1
                return
            k = 1
            pow_ = int(self._alg_size)
            for _ in range(arity - 2):
                k = k + pow_
                pow_ = pow_ * int(self._alg_size)
            self._diag_div = k

        def arity(self) -> int:
            ar = getattr(self._symbol, "arity", None)
            return int(ar() if callable(ar) else ar)

        def symbol(self) -> Any:
            return self._symbol

        def getSetSize(self) -> int:
            return int(self._alg_size)

        def get_set_size(self) -> int:
            return int(self._alg_size)

        def getDefaultValue(self) -> int:
            return int(self._default_value)

        def setDefaultValue(self, v: Any) -> None:
            self._default_value = int(v)

        def isIdempotentSet(self) -> bool:
            return bool(self._idempotent_set)

        def setIdempotent(self, v: Any) -> None:
            self._idempotent_set = bool(v)
            if v:
                self.makeIdempotent()

        def makeIdempotent(self) -> None:
            if self._value_table is None:
                _raise_npe()
            size = int(self._alg_size)
            if self._diag_indices is None:
                arity = int(self.arity())
                self._diag_indices = []
                for i in range(size):
                    diag = [i] * arity
                    self._diag_indices.append(_horner(diag, size))
            for i in range(size):
                self._value_table[self._diag_indices[i]] = i

        def isDiagonal(self, row: Any, col: Any) -> bool:
            r = int(row)
            c = int(col)
            if self._diag_div and r % self._diag_div == 0 and c == r // self._diag_div:
                return True
            return False

        def updateRandomValueTable(self) -> None:
            import random

            n = 1
            s = int(self.arity())
            for _ in range(s):
                n *= int(self._alg_size)
            self._random_value_table = [random.randrange(int(self._alg_size)) for _ in range(n)]

        def getRandomValueTable(self) -> list:
            if self._random_value_table is None:
                self.updateRandomValueTable()
            return list(self._random_value_table)

        def isTotal(self) -> bool:
            if self._default_value >= 0 or self._default_value == -2:
                return True
            tab = self.getTable()
            if tab is None:
                return False
            for v in tab:
                if int(v) < 0:
                    return False
            return True

        def valueAt(self, args: Any) -> int:
            if args is None:
                raise UnsupportedOperationException()
            return self.intValueAt(args)

        def intValueAt(self, args: Any) -> int:
            if args is None:
                _raise_npe()
            if isinstance(args, bool):
                idx = int(args)
            elif isinstance(args, int):
                idx = int(args)
            else:
                seq = _as_int_list(args)
                idx = _horner(seq, int(self._alg_size))
            if self._value_table is not None:
                v = int(self._value_table[idx])
            elif self._op is not None:
                if isinstance(args, int) and not isinstance(args, bool):
                    v = int(self._op.intValueAt(args))
                else:
                    v = int(self._op.intValueAt(_as_int_list(args)))
            else:
                _raise_npe()
            if v == -1:
                if self._default_value != -2:
                    return int(self._default_value)
                return int(self.getRandomValueTable()[idx])
            return v

        def makeTable(self) -> None:
            opx = self.makeOrdinaryOperation()
            if opx is not None:
                self._op = opx

        def getTable(self, makeTable: Optional[bool] = None) -> Any:
            if makeTable:
                self.makeTable()
            return None if self._value_table is None else list(self._value_table)

        def getTotalTable(self) -> Any:
            if self._value_table is None:
                return None
            n = len(self._value_table)
            vt = [0] * n
            for i in range(n):
                if self._value_table[i] == -1:
                    if self._default_value == -1:
                        return None
                    if self._default_value == -2:
                        vt[i] = int(self.getRandomValueTable()[i])
                    else:
                        vt[i] = int(self._default_value)
                else:
                    vt[i] = int(self._value_table[i])
            return vt

        def makeOrdinaryOperation(self) -> Any:
            tab = self.getTotalTable()
            if tab is None:
                return None
            try:
                return Operations.makeIntOperation(self._symbol, int(self._alg_size), tab)
            except (ValueError, IllegalArgumentException):
                # Java IntOperationImp stores the table as-is; Rust rejects
                # values outside [0, algSize) such as defaultValue 7 on size 2.
                from org.uacalc.alg import AbstractOperation as _AO

                size = int(self._alg_size)
                stored = list(tab)

                class _TableOp(_AO):
                    def intValueAt(self, args):
                        if isinstance(args, bool):
                            idx = int(args)
                        elif isinstance(args, int):
                            idx = int(args)
                        else:
                            idx = _horner(_as_int_list(args), size)
                        return int(stored[idx])

                    def valueAt(self, args):
                        if args is None:
                            raise UnsupportedOperationException()
                        return self.intValueAt(args)

                return _TableOp(self._symbol, size)

        @staticmethod
        def makeOrdinary(ops):
            if ops is None:
                _raise_npe()
            ans = []
            for op in list(ops):
                if isinstance(op, OperationWithDefaultValue):
                    ans.append(op.makeOrdinaryOperation())
                ans.append(op)
            return ans

        def isTableBased(self) -> bool:
            return False

        def isIdempotent(self) -> bool:
            return bool(Operations.isIdempotent(self))

        def isAssociative(self) -> bool:
            return bool(Operations.isAssociative(self))

        def isCommutative(self) -> bool:
            return bool(Operations.isCommutative(self))

        def isTotallySymmetric(self) -> bool:
            return bool(Operations.isTotallySymmetric(self))

        def isMaltsev(self) -> bool:
            return bool(Operations.isMaltsev(self))

    AbstractIntOperation = op_globals.get("AbstractIntOperation")

    op_globals["Operation"] = Operation
    op_globals["Operations"] = Operations
    op_globals["TermOperation"] = TermOperation
    op_globals["TermOperationImp"] = TermOperationImp
    op_globals["ParameterizedOperation"] = ParameterizedOperation
    op_globals["OperationWithDefaultValue"] = OperationWithDefaultValue
    if AbstractIntOperation is not None:
        op_globals["AbstractIntOperation"] = AbstractIntOperation
    op_globals["_CLASS_ALIASES"] = {
        "Operation": {
            "getSetSize": "get_set_size",
            "intValueAt": "int_value_at",
            "valueAt": "value_at",
            "makeTable": "make_table",
            "getTable": "get_table",
            "isTableBased": "is_table_based",
            "isIdempotent": "is_idempotent",
            "isAssociative": "is_associative",
            "isCommutative": "is_commutative",
            "isTotallySymmetric": "is_totally_symmetric",
            "isMaltsev": "is_maltsev",
            "isTotal": "is_total",
        },
        "IntOperation": {
            "getSetSize": "get_set_size",
            "intValueAt": "int_value_at",
            "valueAt": "value_at",
            "makeTable": "make_table",
            "getTable": "get_table",
            "isTableBased": "is_table_based",
            "isIdempotent": "is_idempotent",
            "isAssociative": "is_associative",
            "isCommutative": "is_commutative",
            "isTotallySymmetric": "is_totally_symmetric",
            "isMaltsev": "is_maltsev",
            "isTotal": "is_total",
        },
        "SimilarityType": {
            "getOperationSymbols": "get_operation_symbols",
            "getSortedOperationSymbols": "get_sorted_operation_symbols",
            "inputSize": "input_size",
            "getAritiesMap": "get_arities_map",
            "getMaxArity": "get_max_arity",
            "aritiesString": "arities_string",
            "hashCode": "hash_code",
        },
        "AbstractOperation": {
            "intValueAt": "int_value_at",
        },
        "OperationSymbol": {
            "hashCode": "hash_code",
            "compareTo": "compare_to",
        },
        "AbstractIntOperation": {
            "intValueAt": "int_value_at",
            "valueAt": "value_at",
            "getSetSize": "get_set_size",
        },
        "TermOperation": {
            "getTerm": "get_term",
            "getOrderedVariables": "get_ordered_variables",
        },
        "TermOperationImp": {
            "getTerm": "get_term",
            "getOrderedVariables": "get_ordered_variables",
            "intValueAt": "int_value_at",
            "valueAt": "valueAt",
            "getTable": "getTable",
            "makeTable": "makeTable",
            "toString": "toString",
        },
        "ParameterizedOperation": {
            "makeOp": "makeOp",
            "subParmValues": "subParmValues",
        },
        "OperationWithDefaultValue": {
            "getSetSize": "get_set_size",
            "intValueAt": "intValueAt",
            "valueAt": "valueAt",
            "getDefaultValue": "getDefaultValue",
            "setDefaultValue": "setDefaultValue",
            "isIdempotentSet": "isIdempotentSet",
            "setIdempotent": "setIdempotent",
            "makeIdempotent": "makeIdempotent",
            "isDiagonal": "isDiagonal",
            "updateRandomValueTable": "updateRandomValueTable",
            "getRandomValueTable": "getRandomValueTable",
            "isTotal": "isTotal",
            "makeTable": "makeTable",
            "getTable": "getTable",
            "getTotalTable": "getTotalTable",
            "makeOrdinaryOperation": "makeOrdinaryOperation",
        },
    }
