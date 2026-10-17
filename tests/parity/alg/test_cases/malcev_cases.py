"""Golden parity cases for org.uacalc.alg.Malcev and Algebras Malcev delegates."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import Malcev, Algebras
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
z3 = AlgebraIO.readAlgebraFile("resources/algebras/z3.ua")
polin = AlgebraIO.readAlgebraFile("resources/algebras/polin.ua")

def _term(t):
    if t is None:
        return None
    return str(t).replace(" ", "")

def _terms(lst):
    if lst is None:
        return None
    return [_term(t) for t in list(lst)]

def _ints(v):
    if v is None:
        return None
    try:
        return [int(x) for x in list(v)]
    except TypeError:
        pass
    for attr in ("getArray", "get_array", "toArray", "to_array"):
        fn = getattr(v, attr, None)
        if callable(fn):
            return [int(x) for x in fn()]
    return str(v)
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")
_LIST = dict(skip_string_check=True, notes="Java List/Term toString vs Python list/str.")
_TERM = dict(skip_string_check=True, notes="Java Term toString vs Python term string.")

TEST_CASES = [
    TestCaseSpec(
        id="malcev_term_c2",
        method="Malcev.malcevTerm",
        setup=_SETUP,
        call="_term(Malcev.malcevTerm(c2))",
        description="Malcev term of C2 (group of order 2)",
        **_TERM
    ),
    TestCaseSpec(
        id="malcev_term_c3",
        method="Malcev.malcevTerm",
        setup=_SETUP,
        call="_term(Malcev.malcevTerm(c3))",
        description="Malcev term of C3 (group of order 3)",
        **_TERM
    ),
    TestCaseSpec(
        id="malcev_term_lat2",
        method="Malcev.malcevTerm",
        setup=_SETUP,
        call="_term(Malcev.malcevTerm(lat2))",
        description="lat2 has no Malcev term",
        **_NONE
    ),
    TestCaseSpec(
        id="malcev_term_null",
        method="Malcev.malcevTerm",
        setup=_SETUP,
        call="Malcev.malcevTerm(None)",
        description="malcevTerm(null) NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="majority_term_lat2",
        method="Malcev.majorityTerm",
        setup=_SETUP,
        call="_term(Malcev.majorityTerm(lat2))",
        description="majority term of the 2-element lattice",
        **_TERM
    ),
    TestCaseSpec(
        id="majority_term_c2",
        method="Malcev.majorityTerm",
        setup=_SETUP,
        call="_term(Malcev.majorityTerm(c2))",
        description="majority term of C2 if any",
        **_TERM
    ),
    TestCaseSpec(
        id="minority_term_c2",
        method="Malcev.minorityTerm",
        setup=_SETUP,
        call="_term(Malcev.minorityTerm(c2))",
        description="minority term of C2",
        **_TERM
    ),
    TestCaseSpec(
        id="pixley_term_c2",
        method="Malcev.pixleyTerm",
        setup=_SETUP,
        call="_term(Malcev.pixleyTerm(c2))",
        description="Pixley term of C2 if any",
        **_TERM
    ),
    TestCaseSpec(
        id="nu_term_lat2_arity3",
        method="Malcev.nuTerm",
        setup=_SETUP,
        call="_term(Malcev.nuTerm(lat2, 3))",
        description="ternary NU term of lat2",
        **_TERM
    ),
    TestCaseSpec(
        id="nu_term_c2_arity3",
        method="Malcev.nuTerm",
        setup=_SETUP,
        call="_term(Malcev.nuTerm(c2, 3))",
        description="ternary NU term of C2 if any",
        **_TERM
    ),
    TestCaseSpec(
        id="nu_term_idempotent_lat2",
        method="Malcev.nuTermIdempotent",
        setup=_SETUP,
        call="Malcev.nuTermIdempotent(lat2, 3, None)",
        description="lat2 has a ternary NU term (idempotent test)",
        **_BOOL
    ),
    TestCaseSpec(
        id="weak_nu_term_lat2",
        method="Malcev.weakNUTerm",
        setup=_SETUP,
        call="_term(Malcev.weakNUTerm(lat2, 3))",
        description="weak NU term of lat2",
        **_TERM
    ),
    TestCaseSpec(
        id="find_weak_nu_term_alias",
        method="Malcev.findWeakNUTerm",
        setup=_SETUP,
        call="_term(Malcev.findWeakNUTerm(lat2, 3, None))",
        description="findWeakNUTerm aliases weakNUTerm",
        **_TERM
    ),
    TestCaseSpec(
        id="weak_majority_term_lat2",
        method="Malcev.weakMajorityTerm",
        setup=_SETUP,
        call="_term(Malcev.weakMajorityTerm(lat2))",
        description="weak majority term of lat2",
        **_TERM
    ),
    TestCaseSpec(
        id="semilattice_term_lat2",
        method="Malcev.semilatticeTerm",
        setup=_SETUP,
        call="_term(Malcev.semilatticeTerm(lat2))",
        description="semilattice term of lat2",
        **_TERM
    ),
    TestCaseSpec(
        id="difference_term_c3",
        method="Malcev.differenceTerm",
        setup=_SETUP,
        call="_term(Malcev.differenceTerm(c3))",
        description="difference term of C3",
        **_TERM
    ),
    TestCaseSpec(
        id="jonsson_terms_lat2",
        method="Malcev.jonssonTerms",
        setup=_SETUP,
        call="_terms(Malcev.jonssonTerms(lat2))",
        description="Jonsson terms of lat2",
        **_LIST
    ),
    TestCaseSpec(
        id="jonsson_terms_c2",
        method="Malcev.jonssonTerms",
        setup=_SETUP,
        call="_terms(Malcev.jonssonTerms(c2))",
        description="Jonsson terms of C2",
        **_LIST
    ),
    TestCaseSpec(
        id="jonsson_level_lat2",
        method="Malcev.jonssonLevel",
        setup=_SETUP,
        call="Malcev.jonssonLevel(lat2)",
        description="Jonsson level of lat2 is 2 (majority witness)",
    ),
    TestCaseSpec(
        id="jonsson_level_c2",
        method="Malcev.jonssonLevel",
        setup=_SETUP,
        call="Malcev.jonssonLevel(c2)",
        description="Jonsson level of C2",
    ),
    TestCaseSpec(
        id="hagemann_mitschke_c3",
        method="Malcev.hagemannMitschkeTerms",
        setup=_SETUP,
        call="_terms(Malcev.hagemannMitschkeTerms(c3))",
        description="Hagemann-Mitschke terms of C3",
        **_LIST
    ),
    TestCaseSpec(
        id="gumm_terms_lat2",
        method="Malcev.gummTerms",
        setup=_SETUP,
        call="_terms(Malcev.gummTerms(lat2))",
        description="Gumm terms of lat2",
        xfail_reason=(
            "known Java bug: gummTerms(alg) NPEs because ProgressReport.addStartLine "
            "is invoked on a null report inside the no-arg overload."
        ),
        **_LIST
    ),
    TestCaseSpec(
        id="join_term_lat2",
        method="Malcev.joinTerm",
        setup=_SETUP,
        call="_term(Malcev.joinTerm(lat2))",
        description="Kearnes-Kiss join term of lat2",
        **_TERM
    ),
    TestCaseSpec(
        id="sdmeet_terms_lat2",
        method="Malcev.sdmeetTerms",
        setup=_SETUP,
        call="_terms(Malcev.sdmeetTerms(lat2))",
        description="SD-meet terms of lat2",
        **_LIST
    ),
    TestCaseSpec(
        id="sd_terms_lat2",
        method="Malcev.sdTerms",
        setup=_SETUP,
        call="_terms(Malcev.sdTerms(lat2, None))",
        description="SD terms of lat2",
        **_LIST
    ),
    TestCaseSpec(
        id="mmst_term_lat2",
        method="Malcev.markovicMcKenzieSiggersTaylorTerm",
        setup=_SETUP,
        call="_term(Malcev.markovicMcKenzieSiggersTaylorTerm(lat2))",
        description="MMST term of lat2",
        **_TERM
    ),
    TestCaseSpec(
        id="weak_3_edge_term_c2",
        method="Malcev.weak3EdgeTerm",
        setup=_SETUP,
        call="_term(Malcev.weak3EdgeTerm(c2, None))",
        description="weak 3-edge term of C2",
        **_TERM
    ),
    TestCaseSpec(
        id="is_cd_idempotent_lat2",
        method="Malcev.isCongruenceDistIdempotent",
        setup=_SETUP,
        call="Malcev.isCongruenceDistIdempotent(lat2, None)",
        description="lat2 is congruence distributive",
        **_BOOL
    ),
    TestCaseSpec(
        id="is_cm_idempotent_lat2",
        method="Malcev.isCongruenceModularIdempotent",
        setup=_SETUP,
        call="Malcev.isCongruenceModularIdempotent(lat2, None)",
        description="lat2 is congruence modular",
        **_BOOL
    ),
    TestCaseSpec(
        id="cm_variety_c3",
        method="Malcev.congruenceModularVariety",
        setup=_SETUP,
        call="Malcev.congruenceModularVariety(c3)",
        description="C3 generates a CM variety",
        **_BOOL
    ),
    TestCaseSpec(
        id="cm_variety_polin",
        method="Malcev.congruenceModularVariety",
        setup=_SETUP,
        call="Malcev.congruenceModularVariety(polin)",
        description="Polin algebra is not congruence modular",
        **_BOOL
    ),
    TestCaseSpec(
        id="sd_meet_idempotent_z3",
        method="Malcev.sdMeetIdempotent",
        setup=_SETUP,
        call="_ints(Malcev.sdMeetIdempotent(z3, None))",
        description="SD-meet witness on z3",
        **_LIST
    ),
    TestCaseSpec(
        id="find_day_quad_lat2",
        method="Malcev.findDayQuadrupleInSquare",
        setup=_SETUP,
        call="_ints(Malcev.findDayQuadrupleInSquare(lat2, None))",
        description="Day quadruple in lat2^2 if any",
        **_LIST
    ),
    TestCaseSpec(
        id="cyclic_term_idempotent_lat2",
        method="Malcev.cyclicTermIdempotent",
        setup=_SETUP,
        call="Malcev.cyclicTermIdempotent(lat2, 3)",
        description="cyclic term of arity 3 on lat2",
        **_BOOL
    ),
    TestCaseSpec(
        id="fixed_k_qwnu_lat2",
        method="Malcev.fixedKQwnu",
        setup=_SETUP,
        call="Malcev.fixedKQwnu(lat2, 3, None)",
        description="QWNU arity 3 on lat2",
        **_BOOL
    ),
    TestCaseSpec(
        id="fixed_k_edge_term_c2",
        method="Malcev.fixedKEdgeTerm",
        setup=_SETUP,
        call="_term(Malcev.fixedKEdgeTerm(c2, 2, None))",
        description="k-edge term of C2 for k=2",
        **_TERM
    ),
    TestCaseSpec(
        id="local_dist_level_c3",
        method="Malcev.localDistributivityLevel",
        setup=_SETUP,
        call="Malcev.localDistributivityLevel(0, 1, 2, c3)",
        description="local distributivity level on C3",
    ),
    TestCaseSpec(
        id="primality_terms_c2",
        method="Malcev.primalityTerms",
        setup=_SETUP,
        call="_terms(Malcev.primalityTerms(c2, None))",
        description="primality terms of C2 if any",
        xfail_reason=(
            "known Java bug: primalityTerms(alg, report) NPEs when report is null "
            "(semilatTerm calls report.addStartLine unconditionally)."
        ),
        **_LIST
    ),
    TestCaseSpec(
        id="algebras_find_nuf_lat2",
        method="Algebras.findNUF",
        setup=_SETUP,
        call="_term(Algebras.findNUF(lat2, 3))",
        description="Algebras.findNUF delegates to Malcev.nuTerm",
        **_TERM
    ),
    TestCaseSpec(
        id="algebras_jonsson_terms_lat2",
        method="Algebras.jonssonTerms",
        setup=_SETUP,
        call="_terms(Algebras.jonssonTerms(lat2))",
        description="Algebras.jonssonTerms delegates to Malcev",
        **_LIST
    ),
    TestCaseSpec(
        id="algebras_jonsson_level_lat2",
        method="Algebras.jonssonLevel",
        setup=_SETUP,
        call="Algebras.jonssonLevel(lat2)",
        description="Algebras.jonssonLevel delegates to Malcev",
    ),
]
