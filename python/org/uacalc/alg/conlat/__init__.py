"""Compatibility shim for ``org.uacalc.alg.conlat`` (congruences / partitions).

CPython: re-export Partition / BasicPartition / CongruenceLattice from
``org.uacalc.alg`` (where ``uacalc_lib`` binds them) and apply Jython facades.
Jython uses the Java package from the classpath.
"""

# Literal map for jython_contracts validate() (also applied by _jython_compat).
_CLASS_ALIASES = {
    "Partition": {
        "universeSize": "universe_size",
        "numberOfBlocks": "number_of_blocks",
        "isRelated": "is_related",
        "toArray": "to_array",
        "joinBlocks": "join_blocks",
        "isRepresentative": "is_representative",
        "blockIndex": "block_index",
        "getBlocks": "get_blocks",
        "isZero": "is_zero",
        "isUniform": "is_uniform",
        "isInitialLexRepresentative": "is_initial_lex_representative",
        "getPairs": "get_pairs",
        "compareTo": "compare_to",
        "hashCode": "hash_code",
        "toString": "toString",
    },
    "BasicPartition": {
        "universeSize": "universe_size",
        "numberOfBlocks": "number_of_blocks",
        "isRelated": "is_related",
        "toArray": "to_array",
        "joinBlocks": "join_blocks",
        "getArray": "get_array",
        "get": "get",
        "getPairs": "get_pairs",
        "compareTo": "compare_to",
        "hashCode": "hash_code",
        "toString": "toString",
    },
    "CongruenceLattice": {
        "getName": "get_name",
        "getAlgebra": "getAlgebra",
        "getDescription": "get_description",
        "similarityType": "similarityType",
        "isSimilarTo": "isSimilarTo",
        "upperCoversMap": "upper_covers_map",
        "getPermutabilityLevelWitnesses": "get_permutability_level_witnesses",
        "joinIrreduciblesFound": "join_irreducibles_found",
        "joinIrreducibles": "join_irreducibles",
        "meetIrreducibles": "meet_irreducibles",
        "getUniverseList": "get_universe_list",
        "isDistributive": "is_distributive",
        "generatingPair": "generating_pair",
        "findCoatomAbove": "find_coatom_above",
        "findJoinIrred": "find_join_irred",
        "findMeetIrred": "find_meet_irred",
        "findPrincipalChain": "find_principal_chain",
        "findUpperCover": "find_upper_cover",
        "irredundantMeetDecomposition": "irredundant_meet_decomposition",
        "permutabilityLevel": "permutability_level",
        "getBasicLattice": "get_basic_lattice",
        "universeFound": "universe_found",
        "makeUniverse": "make_universe",
        "makePrincipals": "make_principals",
        "joinIrreducible": "join_irreducible",
        "meetIrreducible": "meet_irreducible",
        "inputSize": "input_size",
    },
}


def _load_cp() -> None:
    import org.uacalc.alg as _alg

    for name in (
        "Partition",
        "BasicPartition",
        "CongruenceLattice",
        "PrintType",
        "BasicBinaryRelation",
        "CentralityData",
        "Polymorphisms",
        "Subtrace",
        "TypeFinder",
    ):
        if hasattr(_alg, name):
            globals()[name] = getattr(_alg, name)

    from org.uacalc.alg.conlat._jython_compat import _install as _install_jython_compat

    _install_jython_compat(globals())

    # Keep org.uacalc.alg facades in sync with this package.
    for name in ("Partition", "BasicPartition", "CongruenceLattice", "PrintType"):
        if name in globals():
            setattr(_alg, name, globals()[name])


if __import__("sys").platform.startswith("java"):
    from org.uacalc.alg.conlat import *  # noqa: F403
else:
    _load_cp()
    del _load_cp
