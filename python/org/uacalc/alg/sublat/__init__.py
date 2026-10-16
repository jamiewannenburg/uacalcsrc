"""Compatibility shim for ``org.uacalc.alg.sublat``.

CPython: re-export ``SubalgebraLattice`` / ``BasicSet`` from ``org.uacalc.alg``
(where ``uacalc_lib`` binds them) and apply Jython facades.
Jython uses the Java package from the classpath.
"""

# Literal map for jython_contracts validate() (also applied by _jython_compat).
_CLASS_ALIASES = {
    "BasicSet": {
        "universeSize": "universe_size",
        "setDifference": "set_difference",
        "toArray": "to_array",
        "getArray": "get_array",
        "compareTo": "compare_to",
        "toString": "toString",
        "leq": "leq",
        "intersection": "intersection",
        "union": "union",
        "contains": "contains",
        "get": "get",
        "normalize": "normalize",
    },
    "SubalgebraLattice": {
        "iterator": "iterator",
        "Sg": "Sg",
        "sg": "sg",
        "getName": "getName",
        "getAlgebra": "getAlgebra",
        "getDescription": "getDescription",
        "setDescription": "setDescription",
        "joinIrreducibles": "joinIrreducibles",
        "meetIrreducibles": "meetIrreducibles",
        "oneGeneratedSubalgebras": "oneGeneratedSubalgebras",
        "findMinimalSizedGeneratingSet": "findMinimalSizedGeneratingSet",
        "getBasicLattice": "getBasicLattice",
        "universeFound": "universeFound",
        "makeUniverse": "makeUniverse",
        "makeJoinIrreducibles": "makeJoinIrreducibles",
        "joinIrreducible": "joinIrreducible",
        "inputSize": "inputSize",
        "similarityType": "similarityType",
        "isSimilarTo": "isSimilarTo",
        "isSmallerThan": "isSmallerThan",
        "isDrawable": "isDrawable",
        "constantOperations": "constantOperations",
        "makeSg": "makeSg",
        "joinClosure": "joinClosure",
        "noDuplicates": "noDuplicates",
        "extendToHomomorphism": "extendToHomomorphism",
        "getMakeUniverseK": "getMakeUniverseK",
        "getSizeComputed": "getSizeComputed",
        "stopMakeUniverse": "stopMakeUniverse",
        "setMonitor": "setMonitor",
        "getMonitor": "getMonitor",
        "monitoring": "monitoring",
        "updateSimilarityType": "updateSimilarityType",
        "makeOperationTables": "makeOperationTables",
        "getOperation": "getOperation",
        "getOperationsMap": "getOperationsMap",
        "operations": "operations",
        "atoms": "atoms",
        "coatoms": "coatoms",
        "meet": "meet",
        "join": "join",
        "leq": "leq",
        "filter": "filter",
        "cardinality": "cardinality",
        "universe": "universe",
        "zero": "zero",
        "one": "one",
        "con": "con",
        "sub": "sub",
        "setName": "setName",
        "isTotal": "isTotal",
        "isUnary": "isUnary",
        "isIdempotent": "isIdempotent",
    },
}


def _load_cp() -> None:
    import org.uacalc.alg as _alg

    for name in ("SubalgebraLattice", "BasicSet"):
        if hasattr(_alg, name):
            globals()[name] = getattr(_alg, name)

    from org.uacalc.alg.sublat._jython_compat import _install as _install_jython_compat

    _install_jython_compat(globals())

    # Keep org.uacalc.alg facades in sync with this package.
    for name in ("SubalgebraLattice", "BasicSet"):
        if name in globals():
            setattr(_alg, name, globals()[name])


if __import__("sys").platform.startswith("java"):
    from org.uacalc.alg.sublat import *  # noqa: F403
else:
    _load_cp()
    del _load_cp
