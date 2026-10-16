"""Compatibility shim for ``org.uacalc.alg.parallel`` (parallel pool / closers).

CPython loads ``Pool`` / ``SingleClose`` from ``uacalc_lib.alg.parallel`` when
present (falling back to ``uacalc_lib.alg.Pool``) and applies a Java-shaped
facade. Jython uses the Java package from the classpath.
"""

# Literal map for jython_contracts validate() (also applied by _jython_compat).
_CLASS_ALIASES = {
    "Pool": {
        "fj_pool": "fj_pool",
        "is_initialized": "is_initialized",
        "toString": "toString",
    },
    "SingleClose": {
        "doOneStep": "doOneStep",
        "toString": "toString",
    },
}


def _load_cp() -> None:
    import importlib

    import uacalc_lib as _uacalc_lib

    _alg = getattr(_uacalc_lib, "alg")
    _sub = getattr(_alg, "parallel", None)
    if _sub is None:
        try:
            _sub = importlib.import_module("uacalc_lib.alg.parallel")
        except ImportError:
            _sub = None
    g = globals()
    if _sub is not None:
        for _name in dir(_sub):
            if not _name.startswith("_"):
                g[_name] = getattr(_sub, _name)
    if "Pool" not in g:
        _pool = getattr(_alg, "Pool", None)
        if _pool is not None:
            g["Pool"] = _pool

    from org.uacalc.alg.parallel._jython_compat import _install as _install_jython_compat

    _install_jython_compat(g)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.alg.parallel import *  # noqa: F403
else:
    _load_cp()
    del _load_cp
