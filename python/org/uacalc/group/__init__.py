"""Compatibility shim for ``org.uacalc.group`` (permutation groups).

CPython re-exports ``uacalc_lib.group`` when available. Jython uses the Java
package from the classpath.
"""


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _group = getattr(_uacalc_lib, "group", None)
    if _group is None:
        return
    g = globals()
    for _name in dir(_group):
        if not _name.startswith("_"):
            g[_name] = getattr(_group, _name)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.group import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
