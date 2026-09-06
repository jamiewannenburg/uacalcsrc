import sys

is_jython = sys.platform.startswith("java")

if not is_jython:
    import uacalc_lib

    _alg = getattr(uacalc_lib, "alg")

    # Export everything from _alg to this module
    for _name in dir(_alg):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_alg, _name)

    # Literal map for jython_contracts validate() (also applied by _jython_compat).
    _CLASS_ALIASES = {
        "SmallAlgebra": {
            "getUniverseList": "get_universe_list",
            "elementIndex": "element_index",
            "algebraType": "algebra_type",
            "resetConAndSub": "reset_con_and_sub",
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "universe": "universe",
            "similarityType": "similarityType",
            "constantOperations": "constantOperations",
        },
        "BasicAlgebra": {
            "getUniverseList": "get_universe_list",
            "elementIndex": "element_index",
            "algebraType": "algebra_type",
            "resetConAndSub": "reset_con_and_sub",
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "universe": "universe",
            "similarityType": "similarityType",
            "constantOperations": "constantOperations",
        },
        "FreeAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "elementIndex": "element_index",
            "getOperation": "getOperation",
        },
        "ProductAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "numberOfFactors": "number_of_factors",
            "getOperation": "getOperation",
        },
        "ReductAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
        },
        "Subalgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
        },
        "SubalgebraLattice": {
            "iterator": "iterator",
            "Sg": "sg",
        },
    }

    # Jython call-shape bridges (BasicAlgebra(name, n, ops), AbstractOperation
    # subclassing, getOperation / setName / …). Kept in sync with file-level
    # contracts under jython_contracts/org.uacalc.alg.*.yaml
    from org.uacalc.alg._jython_compat import _install as _install_jython_compat

    _install_jython_compat(globals())
    del _install_jython_compat
else:
    # In Jython, import from the Java package
    from org.uacalc.alg import *  # noqa: F403,F401
