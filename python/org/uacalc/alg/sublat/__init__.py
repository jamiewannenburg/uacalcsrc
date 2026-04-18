"""Compatibility shim for ``org.uacalc.alg.sublat`` (subalgebra lattice helpers).

CPython loads from ``uacalc_lib.alg.sublat`` when present; otherwise the
namespace may be empty. Jython uses the Java package from the classpath.
"""


def _load_cp() -> None:
    import importlib

    import uacalc_lib as _uacalc_lib

    _alg = getattr(_uacalc_lib, "alg")
    _sub = getattr(_alg, "sublat", None)
    if _sub is None:
        try:
            _sub = importlib.import_module("uacalc_lib.alg.sublat")
        except ImportError:
            return
    g = globals()
    for _name in dir(_sub):
        if not _name.startswith("_"):
            g[_name] = getattr(_sub, _name)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.alg.sublat import *  # noqa: F403
else:
    _load_cp()
    del _load_cp
