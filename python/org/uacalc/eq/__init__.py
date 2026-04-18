"""Compatibility shim for ``org.uacalc.eq`` (equations, presentations).

CPython re-exports ``uacalc_lib.eq`` when available. Jython uses the Java
package from the classpath.
"""


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _eq = getattr(_uacalc_lib, "eq", None)
    if _eq is None:
        return
    g = globals()
    for _name in dir(_eq):
        if not _name.startswith("_"):
            g[_name] = getattr(_eq, _name)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.eq import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
