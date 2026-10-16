"""Compatibility shim for ``org.uacalc.alg.op``.

CPython: re-export operation types from ``org.uacalc.alg`` (where ``uacalc_lib``
binds them) so ``from org.uacalc.alg.op import AbstractOperation, OperationSymbol``
matches Jython. Jython uses the Java package from the classpath.
"""


# Literal map for jython_contracts validate() (also applied by _jython_compat).
_CLASS_ALIASES = {
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
    "AbstractOperation": {
        "intValueAt": "int_value_at",
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
    "SimilarityType": {
        "getOperationSymbols": "get_operation_symbols",
        "getSortedOperationSymbols": "get_sorted_operation_symbols",
        "inputSize": "input_size",
        "getAritiesMap": "get_arities_map",
        "getMaxArity": "get_max_arity",
        "aritiesString": "arities_string",
        "hashCode": "hash_code",
    },
    "OperationSymbol": {
        "hashCode": "hash_code",
        "compareTo": "compare_to",
    },
}


def _load_cp() -> None:
    import org.uacalc.alg as _alg

    for name in (
        "AbstractOperation",
        "AbstractIntOperation",
        "OperationSymbol",
        "OperationWithDefaultValue",
        "Operations",
        "BasicOperation",
        "IntOperation",
        "TermOperationImp",
        "SimilarityType",
        "ParameterizedOperation",
    ):
        if hasattr(_alg, name):
            globals()[name] = getattr(_alg, name)

    if "TermOperationImp" not in globals() or globals().get("TermOperationImp") is None:
        try:
            import uacalc_lib as _uacalc_lib

            _toi = getattr(getattr(_uacalc_lib, "terms", None), "TermOperationImp", None)
            if _toi is not None:
                globals()["TermOperationImp"] = _toi
        except Exception:
            pass

    from org.uacalc.alg.op._jython_compat import _install as _install_jython_compat

    _install_jython_compat(globals())

    # Keep org.uacalc.alg facades in sync with this package.
    for _sync in (
        "Operations",
        "SimilarityType",
        "Operation",
        "AbstractIntOperation",
        "TermOperation",
        "TermOperationImp",
        "ParameterizedOperation",
        "OperationWithDefaultValue",
    ):
        if _sync in globals():
            setattr(_alg, _sync, globals()[_sync])


if __import__("sys").platform.startswith("java"):
    from org.uacalc.alg.op import *  # noqa: F403
else:
    _load_cp()
    del _load_cp
