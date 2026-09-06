import sys

if sys.platform.startswith("java"):
    from org.uacalc.util import *  # noqa: F403
else:
    import uacalc_lib as _uacalc_lib

    _util = getattr(_uacalc_lib, "util")

    for _name in dir(_util):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_util, _name)

    if "ArrayIncrementorImpl" in globals():
        globals()["ArrayIncrementor"] = globals()["ArrayIncrementorImpl"]
    if "LongListUtils" in globals():
        globals()["LongList"] = globals()["LongListUtils"]

    _LibIntArray = globals().get("IntArray")
    if _LibIntArray is not None:
        # Java IntArray.get / set already match the binding names.
        # clone() is used by free_algebras.py (el.clone()).
        if not hasattr(_LibIntArray, "clone") and hasattr(_LibIntArray, "clone_array"):
            _LibIntArray.clone = _LibIntArray.clone_array
        if not hasattr(_LibIntArray, "universeSize") and hasattr(
            _LibIntArray, "universe_size"
        ):
            _LibIntArray.universeSize = _LibIntArray.universe_size
        if not hasattr(_LibIntArray, "getArray") and hasattr(_LibIntArray, "to_array"):
            _LibIntArray.getArray = _LibIntArray.to_array

        class _IntArrayMeta(type):
            def __instancecheck__(cls, instance):
                return isinstance(instance, _LibIntArray)

        class IntArray(object, metaclass=_IntArrayMeta):  # noqa: N801
            """Jython ``IntArray(size)`` / ``IntArray([ints])`` plus ``from_array``."""

            from_array = staticmethod(_LibIntArray.from_array)

            def __new__(cls, *args):
                if len(args) == 0:
                    return _LibIntArray.from_array([])
                if len(args) != 1:
                    raise TypeError("IntArray() takes 0 or 1 arguments")
                arg = args[0]
                if isinstance(arg, _LibIntArray):
                    return arg
                if isinstance(arg, (list, tuple)):
                    return _LibIntArray.from_array([int(x) for x in arg])
                return _LibIntArray(int(arg))

        globals()["IntArray"] = IntArray
        globals()["_LibIntArray"] = _LibIntArray

    del _uacalc_lib, _util

del sys
