"""Compatibility shim for ``org.uacalc.eq``.

Adds camelCase aliases used by ``~/uacalc`` scripts (``findFailureMap``,
``leftSide``, ``rightSide``) and a Java-style ``Equations`` facade.
"""

_CLASS_ALIASES = {
    "Equation": {
        "findFailureMap": "find_failure_map",
        "findFailure": "find_failure",
        "leftSide": "left_side",
        "rightSide": "right_side",
        "getOperationSymbols": "get_operation_symbols",
        "getVariableList": "get_variable_list",
        "toString": "toString",
    },
    "Presentation": {
        "getVariables": "get_variables",
        "getRelations": "get_relations",
    },
    "Equations": {},
}


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib
    from org.uacalc._exceptions import translate_illegal_argument

    _eq = getattr(_uacalc_lib, "eq", None)
    if _eq is None:
        return
    g = globals()
    for _name in dir(_eq):
        if not _name.startswith("_"):
            g[_name] = getattr(_eq, _name)

    _associative_law = getattr(_eq, "associative_law", None)
    _cyclic_law = getattr(_eq, "cyclic_law", None)
    _first_second = getattr(_eq, "first_second_symmetric_law", None)

    class Equations(object):
        """Static facade matching Java ``org.uacalc.eq.Equations``."""

        @staticmethod
        def associativeLaw(op_symbol):
            try:
                return _associative_law(op_symbol)
            except ValueError as exc:
                translate_illegal_argument(exc)

        @staticmethod
        def cyclicLaw(op_symbol):
            try:
                return _cyclic_law(op_symbol)
            except ValueError as exc:
                translate_illegal_argument(exc)

        @staticmethod
        def firstSecondSymmetricLaw(op_symbol):
            try:
                return _first_second(op_symbol)
            except ValueError as exc:
                translate_illegal_argument(exc)

    g["Equations"] = Equations

    from org.uacalc.eq._jython_compat import _install as _install_jython_compat

    _install_jython_compat(g)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.eq import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
