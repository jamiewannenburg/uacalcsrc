"""Compatibility shim for ``org.uacalc.element``.

CPython: re-export ``uacalc_lib.element`` and apply Jython facades.
Jython uses the Java package from the classpath.
"""

# Literal map for jython_contracts validate() (also applied by _jython_compat).
_CLASS_ALIASES = {
    "Element": {
        "getAlgebra": "get_algebra",
        "index": "index",
        "getParent": "get_parent",
        "getParentArray": "get_parent_array",
        "parentIndexArray": "parent_index_array",
        "toString": "toString",
    },
    "SubProductElement": {
        "getAlgebra": "get_algebra",
        "index": "index",
        "getTerm": "get_term",
        "getVariableList": "get_variable_list",
        "getVariableMap": "get_variable_map",
        "getParent": "get_parent",
        "getParentArray": "get_parent_array",
        "parentIndexArray": "parent_index_array",
        "toString": "toString",
    },
}


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _element = getattr(_uacalc_lib, "element")
    g = globals()
    for _name in dir(_element):
        if not _name.startswith("_"):
            g[_name] = getattr(_element, _name)

    from org.uacalc.element._jython_compat import _install as _install_jython_compat

    _install_jython_compat(g)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.element import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
