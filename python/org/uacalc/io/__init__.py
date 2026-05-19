import sys

if sys.platform.startswith("java"):
    from org.uacalc.io import *  # noqa: F403
else:
    import uacalc_lib as _uacalc_lib

    _io = getattr(_uacalc_lib, "io")

    for _name in dir(_io):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_io, _name)

    from org.uacalc.io._jython_compat import (  # noqa: E402
        AlgebraIO,
        AlgebraReader,
        AlgebraWriter,
        BadAlgebraFileException,
        ExtFileFilter,
        Mace4Reader,
    )

    class JSONChannel:
        """Placeholder for Java ``org.uacalc.io.JSONChannel`` (not bound in ``uacalc_lib``)."""

        def __init__(self, *_args, **_kwargs):
            raise NotImplementedError(
                "JSONChannel is not implemented in uacalc_lib; use Jython with uacalc.jar."
            )

    del _uacalc_lib, _io

del sys
