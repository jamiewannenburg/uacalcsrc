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
            "getElement": "get_element",
            "getOperation": "getOperation",
            "getUniverseList": "get_universe_list",
            "getTerms": "get_terms",
            "getTerm": "get_term",
            "getElementFromTerm": "get_element_from_term",
            "getProductAlgebra": "get_product_algebra",
            "generators": "generators",
            "getVariables": "get_variables",
            "getIdempotentTerms": "get_idempotent_terms",
            "superAlgebra": "super_algebra",
            "algebraType": "algebra_type",
        },
        "ProductAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "numberOfFactors": "number_of_factors",
            "getOperation": "getOperation",
        },
        "BigProductAlgebra": {
            "numberOfFactors": "number_of_factors",
            "getNumberOfFactors": "number_of_factors",
        },
        "ReductAlgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "superAlgebra": "super_algebra",
            "elementIndex": "element_index",
            "getElement": "get_element",
            "getUniverseList": "get_universe_list",
            "algebraType": "algebra_type",
        },
        "Subalgebra": {
            "getName": "name",
            "setName": "set_name",
            "getOperation": "getOperation",
            "superAlgebra": "super_algebra",
            "getSubuniverseArray": "get_subuniverse_array",
            "elementIndex": "element_index",
            "getElement": "get_element",
            "index": "index",
            "algebraType": "algebra_type",
            "getUniverseList": "get_universe_list",
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
