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

    from org.uacalc.alg.op._jython_compat import _install as _install_jython_compat

    _install_jython_compat(globals())

    # Keep org.uacalc.alg facades in sync with this package.
    if "Operations" in globals():
        setattr(_alg, "Operations", globals()["Operations"])
    if "SimilarityType" in globals():
        setattr(_alg, "SimilarityType", globals()["SimilarityType"])
    if "Operation" in globals():
        setattr(_alg, "Operation", globals()["Operation"])


if __import__("sys").platform.startswith("java"):
    from org.uacalc.alg.op import *  # noqa: F403
else:
    _load_cp()
    del _load_cp
