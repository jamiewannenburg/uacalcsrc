"""Compatibility shim for ``org.uacalc.alg.op`` (operation symbols / operations).

CPython loads from ``uacalc_lib.alg.op`` when that submodule exists; otherwise the
namespace stays empty until Rust exposes it. Jython uses the Java package from
the classpath.
"""


def _load_cp() -> None:
    import importlib

    import uacalc_lib as _uacalc_lib

    _alg = getattr(_uacalc_lib, "alg")
    _op = getattr(_alg, "op", None)
    if _op is None:
        try:
            _op = importlib.import_module("uacalc_lib.alg.op")
        except ImportError:
            return
    g = globals()
    for _name in dir(_op):
        if not _name.startswith("_"):
            g[_name] = getattr(_op, _name)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.alg.op import *  # noqa: F403
else:
    _load_cp()
    del _load_cp
