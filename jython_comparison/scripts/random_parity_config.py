# coding: utf-8
"""Seed lists and xfail table for randomized parity (no org.uacalc imports)."""

# Similarity types cycled by seed. Sizes stay tiny so Java Con/Sub/F(1) are fast.
FAMILIES = (
    (2, (1,)),
    (2, (2,)),
    (2, (1, 2)),
    (2, (1, 1)),
    (3, (1,)),
    (3, (2,)),
    (3, (1, 1)),
    (4, (1,)),
    (2, (2, 1)),
    (4, (1, 1)),
    (3, (1, 2)),
)

# Checked-in CI seed list. Each seed is one golden snapshot.
# 582/632/841/621/687/863 are typeSet library-bug xfails found in the local sweep.
CI_SEEDS = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
    42, 99, 127, 256, 2026,
    582, 621, 632, 687, 841, 863,
)

DEFAULT_CASE_TIMEOUT = 15

_TYPESET_REASON = (
    "uacalc_lib CongruenceLattice.typeSet / TypeFinder disagrees with Java "
    "on some size-3 random algebras with a unique covering congruence "
    "(Con card 2). Not a contained TCT fix here. Minimal repro seed 582 "
    "(n=3, arities (1,2)): Python typeSet [1] vs Java [3]. Related: 621, "
    "687, 863 ([1] vs [3]); 632 ([2] vs [3]); 841 ([5] vs [4])."
)

# Per-seed / dotted-path xfails: expected Java vs Python mismatches.
# Values are human-readable reasons. Strict: an xfail that starts matching fails.
XFAILS = {
    (582, "con.typeSet"): _TYPESET_REASON,
    (621, "con.typeSet"): _TYPESET_REASON,
    (632, "con.typeSet"): _TYPESET_REASON,
    (687, "con.typeSet"): _TYPESET_REASON,
    (841, "con.typeSet"): _TYPESET_REASON,
    (863, "con.typeSet"): _TYPESET_REASON,
}

# Java malcevTerm(alg) sometimes NPEs on null ProgressReport.addStartLine
# (same class of known Java bug as gummTerms). Python returns a term or None.
KNOWN_JAVA_NPE_PATHS = (
    "malcev.malcevTerm",
)

# Prefixes skipped in extra live-Java sweeps (unknown extra seeds).
# CI seeds that hit this bug are listed in XFAILS (strict).
LIBRARY_BUG_PREFIXES = {
    "con.typeSet": _TYPESET_REASON,
}


def family_for_seed(seed):
    n, arities = FAMILIES[int(seed) % len(FAMILIES)]
    return int(n), tuple(int(a) for a in arities)
