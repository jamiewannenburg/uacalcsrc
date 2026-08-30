"""Compatibility shim for ``org.uacalc.terms`` (terms, Taylor operations).

CPython re-exports ``uacalc_lib.terms`` when available. Jython uses the Java
package from the classpath.
"""


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _terms = getattr(_uacalc_lib, "terms", None)
    if _terms is None:
        return
    g = globals()
    for _name in dir(_terms):
        if not _name.startswith("_"):
            g[_name] = getattr(_terms, _name)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.terms import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
