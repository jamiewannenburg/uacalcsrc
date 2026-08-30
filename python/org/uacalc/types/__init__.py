"""Compatibility shim for ``org.uacalc.types``.

CPython re-exports ``uacalc_lib.types`` when that submodule exposes names. The
Rust module is currently a placeholder (see ``uacalc_lib/src/types.rs``) and may
export nothing.

There is no ``org/uacalc/types`` Java package in this repo; on Jython we try the
classpath import and fall back to an empty namespace if the package is absent.
"""


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _types = getattr(_uacalc_lib, "types", None)
    if _types is None:
        return
    g = globals()
    for _name in dir(_types):
        if not _name.startswith("_"):
            g[_name] = getattr(_types, _name)


if __import__("sys").platform.startswith("java"):
    try:
        from org.uacalc.types import *  # noqa: F403
    except ImportError:
        pass
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
