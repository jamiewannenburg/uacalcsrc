"""Compatibility shim for ``org.uacalc.group`` (permutation groups).

CPython: re-export ``uacalc_lib.group`` and apply a Java-shaped facade.
Jython uses the Java package from the classpath.
"""

# Literal map for jython_contracts validate() (also applied by _jython_compat).
_CLASS_ALIASES = {
    "PermutationGroup": {
        "getName": "get_name",
        "setName": "setName",
        "getDescription": "getDescription",
        "setDescription": "setDescription",
        "cardinality": "cardinality",
        "universe": "universe",
        "operations": "operations",
        "inputSize": "inputSize",
        "toString": "toString",
        "prod": "prod",
        "inv": "inv",
        "id": "id",
        "makeProdOp": "makeProdOp",
        "makeInvOp": "makeInvOp",
        "makeIdOp": "makeIdOp",
    },
}


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _group = getattr(_uacalc_lib, "group", None)
    if _group is None:
        return
    g = globals()
    for _name in dir(_group):
        if not _name.startswith("_"):
            g[_name] = getattr(_group, _name)

    from org.uacalc.group._jython_compat import _install as _install_jython_compat

    _install_jython_compat(g)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.group import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
