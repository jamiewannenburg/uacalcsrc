"""Compatibility shim for ``org.uacalc.example`` (demo / example Java classes).

CPython loads symbols from ``uacalc_lib.example`` when that submodule exposes names;
today the Rust ``example`` module is a placeholder, so the namespace may be empty.
Jython uses the real Java package from the classpath.
"""


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _example = getattr(_uacalc_lib, "example", None)
    if _example is None:
        return
    g = globals()
    for _name in dir(_example):
        if not _name.startswith("_"):
            g[_name] = getattr(_example, _name)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.example import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
