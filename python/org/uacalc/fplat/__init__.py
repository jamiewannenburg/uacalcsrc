"""Compatibility shim for ``org.uacalc.fplat`` (partially defined lattices).

CPython re-exports ``uacalc_lib.fplat`` when available. Jython uses the Java
package from the classpath.
"""


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _fplat = getattr(_uacalc_lib, "fplat", None)
    if _fplat is None:
        return
    g = globals()
    for _name in dir(_fplat):
        if not _name.startswith("_"):
            g[_name] = getattr(_fplat, _name)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.fplat import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
