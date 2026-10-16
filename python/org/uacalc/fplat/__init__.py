"""Compatibility shim for ``org.uacalc.fplat`` (partially defined lattices).

CPython: re-export ``uacalc_lib.fplat`` and apply a Java-shaped facade whose
constructor matches the JAR: ``(name, order, joins, meets)``. Jython uses the
Java package from the classpath.
"""

# Literal map for jython_contracts validate() (also applied by _jython_compat).
_CLASS_ALIASES = {
    "PartiallyDefinedLattice": {
        "leq": "leq",
        "toString": "toString",
        "getDefinedJoins": "getDefinedJoins",
        "getDefinedMeets": "getDefinedMeets",
    },
}


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _fplat = getattr(_uacalc_lib, "fplat", None)
    if _fplat is None:
        return
    g = globals()
    for _name in dir(_fplat):
        if not _name.startswith("_"):
            g[_name] = getattr(_fplat, _name)

    from org.uacalc.fplat._jython_compat import _install as _install_jython_compat

    _install_jython_compat(g)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.fplat import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
