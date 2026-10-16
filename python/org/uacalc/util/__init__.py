"""Compatibility shim for ``org.uacalc.util``.

CPython: re-export ``uacalc_lib.util`` and apply Jython facades.
Jython uses the Java package from the classpath.
"""

# Literal map for jython_contracts validate() (also applied by _jython_compat).
_CLASS_ALIASES = {
    "IntArray": {
        "clone": "clone_array",
        "universeSize": "universe_size",
        "getArray": "to_array",
        "toArray": "to_array",
        "setIntArray": "setIntArray",
        "isIdempotent": "is_idempotent",
        "isConstant": "is_constant",
        "satisfiesBlocksConstraint": "satisfies_blocks_constraint",
        "satisfiesValuesConstraint": "satisfies_values_constraint",
        "satisfiesSetConstraint": "satisfies_set_constraint",
        "satisfiesCongruenceConstraint": "satisfiesCongruenceConstraint",
        "intArrayToString": "intArrayToString",
        "stringToArray": "stringToArray",
        "equalIntArrays": "equalIntArrays",
        "lexicographicComparitor": "lexicographicComparitor",
        "toString": "toString",
        "hashCode": "hashCode",
        "equals": "equals",
    },
    "Horner": {
        "horner": "horner",
        "hornerInv": "hornerInv",
        "reverseArray": "reverseArray",
        "leftRightReverse": "leftRightReverse",
    },
    "SequenceGenerator": {
        "nondecreasingSequenceIncrementor": "nondecreasingSequenceIncrementor",
        "increasingSequenceIncrementor": "increasingSequenceIncrementor",
        "increasingSequenceIncrementorOld": "increasingSequenceIncrementorOld",
        "sequenceIncrementor": "sequenceIncrementor",
        "leftSequenceIncrementor": "leftSequenceIncrementor",
        "initialPartition": "initialPartition",
        "partitionArrayIncrementor": "partitionArrayIncrementor",
    },
    "PermutationGenerator": {
        "reset": "reset",
        "nextIndex": "nextIndex",
        "iterator": "iterator",
        "arrayIncrementor": "arrayIncrementor",
        "listIncrementor": "listIncrementor",
    },
    "ArrayString": {
        "toString": "toString",
    },
    "ArrayIncrementor": {
        "increment": "increment",
    },
    "SimpleList": {
        "makeList": "makeList",
        "isEmpty": "isEmpty",
        "copyList": "copyList",
        "indexOf": "indexOf",
        "lastIndexOf": "lastIndexOf",
        "containsAll": "containsAll",
        "subList": "subList",
        "toArray": "toArray",
        "toString": "toString",
        "frontIterator": "frontIterator",
        "getIterator": "getIterator",
        "elements": "elements",
        "listIterator": "listIterator",
    },
}


def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _util = getattr(_uacalc_lib, "util")
    g = globals()
    for _name in dir(_util):
        if not _name.startswith("_"):
            g[_name] = getattr(_util, _name)

    if "ArrayIncrementorImpl" in g:
        g["ArrayIncrementor"] = g["ArrayIncrementorImpl"]
    if "LongListUtils" in g:
        g["LongList"] = g["LongListUtils"]

    _LibIntArray = g.get("IntArray")
    if _LibIntArray is not None:
        g["_LibIntArray"] = _LibIntArray

    from org.uacalc.util._jython_compat import _install as _install_jython_compat

    _install_jython_compat(g)


if __import__("sys").platform.startswith("java"):
    from org.uacalc.util import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
