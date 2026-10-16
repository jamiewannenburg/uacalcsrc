"""Compatibility shim for ``org.uacalc.util.virtuallist``."""

_CLASS_ALIASES = {
    "LongList": {
        "intTuples": "intTuples",
        "intTuplesWithMin": "intTuplesWithMin",
        "fixedSizedSubsets": "fixedSizedSubsets",
        "subsets": "subsets",
        "permutations": "permutations",
        "factorial": "factorial",
        "binomial": "binomial",
        "log2": "log2",
        "pow2": "pow2",
        "stream": "stream",
        "parallelStream": "parallelStream",
    },
    "VirtualLists": {
        "intTuples": "intTuples",
        "intTuplesWithMin": "intTuplesWithMin",
        "arrayIndexerWithMin": "arrayIndexerWithMin",
        "testPow": "testPow",
        "foo": "foo",
        "bar": "bar",
        "baz": "baz",
    },
    "TupleWithMin": {
        "get": "get",
        "size": "size",
    },
}


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _util = getattr(_uacalc_lib, "util")
    g = globals()
    for _name in (
        "LongListUtils",
        "TupleWithMin",
        "VirtualLists",
        "IntTuples",
        "IntTuplesWithMin",
        "FixedSizedSubsets",
        "Subsets",
        "Permutations",
    ):
        if hasattr(_util, _name):
            g[_name] = getattr(_util, _name)

    if "LongListUtils" in g:
        g["LongList"] = g["LongListUtils"]

    from org.uacalc.util.virtuallist._jython_compat import _install as _install_jython_compat

    _install_jython_compat(g)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.util.virtuallist import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
