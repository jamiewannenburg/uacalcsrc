"""Compatibility shim for ``org.uacalc.example`` (demo / example Java classes).

CPython ports the constructable demo APIs onto existing ``org.uacalc`` types.
Jython uses the real Java package from the classpath.

GUI / interactive / Malcev-only entry points stay unported and are skipped
or strict-xfail in the parity tests.
"""

# Literal map for jython_contracts validate().
_CLASS_ALIASES = {
    "Average": {
        "ave": "ave",
        "averageAlg": "averageAlg",
    },
    "Type1": {
        "fullPermutationAlgebra": "fullPermutationAlgebra",
        "cyclicPermutationAlgebra": "cyclicPermutationAlgebra",
        "reductAlg": "reductAlg",
        "subtraces": "subtraces",
    },
    "KKMVWExample": {
        "makeAn": "makeAn",
        "makeAin": "makeAin",
        "makeTin": "makeTin",
    },
    "HasConstantTuple": {
        "hasConstantTuple": "hasConstantTuple",
    },
    "NoSymGroup": {
        "Addition": "Addition",
        "TernaryOp": "TernaryOp",
        "MakeIdTernaryOp": "MakeIdTernaryOp",
    },
    "TupleStream": {
        "pow": "pow",
        "maxOfArray": "maxOfArray",
        "hornerInvLong": "hornerInvLong",
        "intTupleStream": "intTupleStream",
        "tupleStream": "tupleStream",
    },
    "FiniteField": {
        "conwayPolynomial": "conwayPolynomial",
        "cardinality": "cardinality",
        "getPrime": "getPrime",
        "getPower": "getPower",
        "plusInt": "plusInt",
        "timesInt": "timesInt",
        "inverseInt": "inverseInt",
        "zeroIndex": "zeroIndex",
        "oneIndex": "oneIndex",
    },
    "Kearnes": {
        "makeKearnesAlg": "makeKearnesAlg",
        "makeKearnesOps": "makeKearnesOps",
        "makeJoinOp": "makeJoinOp",
        "makeMeetOp": "makeMeetOp",
    },
    "FilteringAlgebras": {
        "filter": "filter",
    },
    "FinitelyPresentedAlg": {
        "makeOrderRelation": "makeOrderRelation",
    },
    "HasKaryNU": {
        "hasNUHorowitz": "hasNUHorowitz",
    },
    "Jipsen": {
        "main": "main",
    },
    "MembershipTester": {
        "main": "main",
    },
    "Michalewski": {
        "findJoinMeetMatPower": "findJoinMeetMatPower",
        "testJoinMeetMatPower": "testJoinMeetMatPower",
    },
    "ConLyndonF3": {
        "main": "main",
    },
    "ParallelClose8": {
        "main": "main",
    },
}


if __import__("sys").platform.startswith("java"):
    from org.uacalc.example import *  # noqa: F403
else:
    from org.uacalc.example._demos import (  # noqa: F401
        Average,
        ConLyndonF3,
        FilteringAlgebras,
        FiniteField,
        FinitelyPresentedAlg,
        HasConstantTuple,
        HasKaryNU,
        Jipsen,
        KKMVWExample,
        Kearnes,
        MembershipTester,
        Michalewski,
        NoSymGroup,
        ParallelClose8,
        TupleStream,
        Type1,
    )
    from org.uacalc.example._demos import (  # noqa: F401
        DEMO_CLASS_NAMES as _DEMO_CLASS_NAMES,
        GUI_OR_INTERACTIVE as _GUI_OR_INTERACTIVE,
    )
