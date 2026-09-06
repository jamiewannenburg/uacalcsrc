"""Compatibility shim for ``org.uacalc.eq``.

Adds camelCase aliases used by ``~/uacalc`` scripts (``findFailureMap``,
``leftSide``, ``rightSide``).
"""

_CLASS_ALIASES = {
    "Equation": {
        "findFailureMap": "find_failure_map",
        "findFailure": "find_failure",
        "leftSide": "left_side",
        "rightSide": "right_side",
        "getOperationSymbols": "get_operation_symbols",
        "getVariableList": "get_variable_list",
    },
}


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _eq = getattr(_uacalc_lib, "eq", None)
    if _eq is None:
        return
    g = globals()
    for _name in dir(_eq):
        if not _name.startswith("_"):
            g[_name] = getattr(_eq, _name)

    Equation = g.get("Equation")
    if Equation is not None:
        for camel, snake in _CLASS_ALIASES["Equation"].items():
            if not hasattr(Equation, camel) and hasattr(Equation, snake):
                setattr(Equation, camel, getattr(Equation, snake))


if __import__("sys").platform.startswith("java"):
    from org.uacalc.eq import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
