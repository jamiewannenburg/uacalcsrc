"""Compatibility shim for ``org.uacalc.alg.op``.

CPython: re-export operation types from ``org.uacalc.alg`` (where ``uacalc_lib``
binds them) so ``from org.uacalc.alg.op import AbstractOperation, OperationSymbol``
matches Jython. Jython uses the Java package from the classpath.
"""


def _load_cp() -> None:
    import org.uacalc.alg as _alg

    # Prefer names already bridged by alg._jython_compat
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

    # Contract validate looks for class bodies / alias assignments in this module.
    _CLASS_ALIASES = {
        "AbstractOperation": {
            "intValueAt": "int_value_at",
        },
        "OperationSymbol": {},
        "IntOperation": {
            "intValueAt": "int_value_at",
        },
    }
    globals()["_CLASS_ALIASES"] = _CLASS_ALIASES


if __import__("sys").platform.startswith("java"):
    from org.uacalc.alg.op import *  # noqa: F403
else:
    _load_cp()
    del _load_cp
