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

    op_globals["Operation"] = Operation
    op_globals["Operations"] = Operations
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
    }
