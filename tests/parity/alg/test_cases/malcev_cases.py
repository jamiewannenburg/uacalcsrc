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

def _ias(lst):
    if lst is None:
        return None
    return [_ints(x) for x in list(lst)]

def _sets(lst):
    if lst is None:
        return None
    return [sorted(int(x) for x in list(s)) for s in list(lst)]

def _cyclic_gens(vals):
    try:
        from jarray import array
        v = array(vals, 'i')
    except ImportError:
        v = vals
    return _ias(Malcev.makeCyclicGens(v))
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
    TestCaseSpec(
        id="day_quad_c2_0100",
        method="Malcev.dayQuadruple",
        setup=_SETUP,
        call="Malcev.dayQuadruple(0, 1, 0, 0, c2)",
        description="dayQuadruple(0,1,0,0) on C2",
        **_BOOL
    ),
    TestCaseSpec(
        id="day_quad_c2_0101",
        method="Malcev.dayQuadruple",
        setup=_SETUP,
        call="Malcev.dayQuadruple(0, 1, 0, 1, c2)",
        description="dayQuadruple(0,1,0,1) on C2",
        **_BOOL
    ),
    TestCaseSpec(
        id="day_quad_lat2_0011",
        method="Malcev.dayQuadruple",
        setup=_SETUP,
        call="Malcev.dayQuadruple(0, 0, 1, 1, lat2)",
        description="dayQuadruple(0,0,1,1) on lat2",
        **_BOOL
    ),
    TestCaseSpec(
        id="day_quad_c3_0120",
        method="Malcev.dayQuadruple",
        setup=_SETUP,
        call="Malcev.dayQuadruple(0, 1, 2, 0, c3)",
        description="dayQuadruple(0,1,2,0) on C3",
        **_BOOL
    ),
    TestCaseSpec(
        id="day_quad_null_alg",
        method="Malcev.dayQuadruple",
        setup=_SETUP,
        call="Malcev.dayQuadruple(0, 1, 0, 1, None)",
        description="dayQuadruple with null algebra NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="make_cyclic_gens_012",
        method="Malcev.makeCyclicGens",
        setup=_SETUP,
        call="_cyclic_gens([0, 1, 2])",
        description="makeCyclicGens of (0,1,2) including Java shared-array copies",
        **_LIST
    ),
    TestCaseSpec(
        id="make_cyclic_gens_01",
        method="Malcev.makeCyclicGens",
        setup=_SETUP,
        call="_cyclic_gens([0, 1])",
        description="makeCyclicGens of (0,1)",
        **_LIST
    ),
    TestCaseSpec(
        id="cm_for_idempotent_c2",
        method="Malcev.congruenceModularForIdempotent",
        setup=_SETUP,
        call="Malcev.congruenceModularForIdempotent(c2, None)",
        description="CM-for-idempotent on C2",
        **_BOOL
    ),
    TestCaseSpec(
        id="cm_for_idempotent_lat2",
        method="Malcev.congruenceModularForIdempotent",
        setup=_SETUP,
        call="Malcev.congruenceModularForIdempotent(lat2, None)",
        description="CM-for-idempotent on lat2",
        **_BOOL
    ),
    TestCaseSpec(
        id="cm_for_idempotent_c3",
        method="Malcev.congruenceModularForIdempotent",
        setup=_SETUP,
        call="Malcev.congruenceModularForIdempotent(c3, None)",
        description="CM-for-idempotent on C3",
        **_BOOL
    ),
    TestCaseSpec(
        id="type_set_idem_c2",
        method="Malcev.typeSetIdempotent",
        setup=_SETUP,
        call="_sets(Malcev.typeSetIdempotent(c2, None))",
        description="typeSetIdempotent bounds on C2",
        **_LIST
    ),
    TestCaseSpec(
        id="type_set_idem_lat2",
        method="Malcev.typeSetIdempotent",
        setup=_SETUP,
        call="_sets(Malcev.typeSetIdempotent(lat2, None))",
        description="typeSetIdempotent bounds on lat2",
        **_LIST
    ),
    TestCaseSpec(
        id="type_set_idem_c3",
        method="Malcev.typeSetIdempotent",
        setup=_SETUP,
        call="_sets(Malcev.typeSetIdempotent(c3, None))",
        description="typeSetIdempotent bounds on C3",
        **_LIST
    ),
    TestCaseSpec(
        id="omitted_ideal_c2",
        method="Malcev.omittedIdealIdempotent",
        setup=_SETUP,
        call="sorted(int(x) for x in list(Malcev.omittedIdealIdempotent(c2, None)))",
        description="omittedIdealIdempotent on C2",
        **_LIST
    ),
    TestCaseSpec(
        id="omitted_ideal_lat2",
        method="Malcev.omittedIdealIdempotent",
        setup=_SETUP,
        call="sorted(int(x) for x in list(Malcev.omittedIdealIdempotent(lat2, None)))",
        description="omittedIdealIdempotent on lat2",
        **_LIST
    ),
    TestCaseSpec(
        id="types_strict_simple_c2",
        method="Malcev.typesInSofAStrictlySimpleIdempotent",
        setup=_SETUP,
        call="sorted(int(x) for x in list(Malcev.typesInSofAStrictlySimpleIdempotent(c2, set(), None)))",
        description="types in strictly simple HS members of C2",
        **_LIST
    ),
    TestCaseSpec(
        id="types_in_s_c2",
        method="Malcev.typesInSofAIdempotent",
        setup=_SETUP,
        call="sorted(int(x) for x in list(Malcev.typesInSofAIdempotent(c2, set(), None)))",
        description="types in HS(C2) via meet-irredundant SI decomp",
        **_LIST
    ),
    TestCaseSpec(
        id="sd_idem_c2",
        method="Malcev.sdIdempotent",
        setup=_SETUP,
        call="_ints(Malcev.sdIdempotent(c2, None))",
        description="SD witness on C2",
        **_LIST
    ),
    TestCaseSpec(
        id="sd_idem_lat2",
        method="Malcev.sdIdempotent",
        setup=_SETUP,
        call="_ints(Malcev.sdIdempotent(lat2, None))",
        description="SD witness on lat2",
        **_LIST
    ),
    TestCaseSpec(
        id="cp_idem_c2",
        method="Malcev.cpIdempotent",
        setup=_SETUP,
        call="_ints(Malcev.cpIdempotent(c2, None))",
        description="CP witness on C2",
        **_LIST
    ),
    TestCaseSpec(
        id="cube_blocker_c2",
        method="Malcev.cubeTermBlockerIdempotent",
        setup=_SETUP,
        call="Malcev.cubeTermBlockerIdempotent(c2, None) is None",
        description="cube-term blocker search on C2 (group: none)",
        **_BOOL
    ),
    TestCaseSpec(
        id="cube_blocker_lat2",
        method="Malcev.cubeTermBlockerIdempotent",
        setup=_SETUP,
        call="(lambda b: None if b is None else [sorted(int(x) for x in list(b[0])), sorted(int(x) for x in list(b[1]))])(Malcev.cubeTermBlockerIdempotent(lat2, None))",
        description="cube-term blocker search on lat2",
        **_LIST
    ),
    TestCaseSpec(
        id="cube_blocker_op_c2",
        method="Malcev.cubeTermBlockerIdempotent",
        setup=_SETUP,
        call="Malcev.cubeTermBlockerIdempotent(list(c2.operations())[0], c2.sub().sg([0]), c2.sub().sg([0, 1]))",
        description="cube-term blocker of the C2 operation at C={0}, D=universe",
    ),
    TestCaseSpec(
        id="sd_path_c2",
        method="Malcev.sdPath",
        setup=_SETUP + r"""
from org.uacalc.alg import BigProductAlgebra, SubProductAlgebra
from org.uacalc.util import IntArray
bp3 = BigProductAlgebra(c2, 3)
g0 = IntArray([0, 0, 0])
g2 = IntArray([1, 1, 1])
gmid = IntArray([0, 0, 1])
sub = SubProductAlgebra("", bp3, [g0, g2, gmid])
path_univ = list(sub.getUniverseList())
""",
        call="_ias(Malcev.sdPath(path_univ, g0, g2))",
        description="sdPath on a tiny C2^3 subproduct",
        **_LIST
    ),
    TestCaseSpec(
        id="jonsson_level_path_npe",
        method="Malcev.jonssonLevelPath",
        setup=_SETUP,
        call="Malcev.jonssonLevelPath(None, None, None, False)",
        description="jonssonLevelPath(null, ...) NPE",
        expected_exception="NullPointerException",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="gumm_level_path_npe",
        method="Malcev.gummLevelPath",
        setup=_SETUP,
        call="Malcev.gummLevelPath(None, None, None, None)",
        description="gummLevelPath(null, ...) NPE",
        expected_exception="NullPointerException",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="hm_level_path_npe",
        method="Malcev.hagemannMitschkeLevelPath",
        setup=_SETUP,
        call="Malcev.hagemannMitschkeLevelPath(None, None, None)",
        description="hagemannMitschkeLevelPath(null, ...) NPE",
        expected_exception="NullPointerException",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="jonsson_level_aux_npe",
        method="Malcev.jonssonLevelAux",
        setup=_SETUP,
        call="Malcev.jonssonLevelAux(None, None, None)",
        description="jonssonLevelAux(null, ...) NPE",
        expected_exception="NullPointerException",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="nu_term_bad_c2",
        method="Malcev.nuTermIdempotent_Bad",
        setup=_SETUP,
        call="Malcev.nuTermIdempotent_Bad(c2, 3, None)",
        description="nuTermIdempotent_Bad Horowitz search on C2 arity 3",
        **_BOOL
    ),
    TestCaseSpec(
        id="fixed_k_edge_idem_c2",
        method="Malcev.fixedKEdgeIdempotent",
        setup=_SETUP,
        call="Malcev.fixedKEdgeIdempotent(c2, 2, None)",
        description="fixedKEdgeIdempotent level 2 on C2",
        **_BOOL
    ),
    TestCaseSpec(
        id="fixed_k_perm_idem_c2",
        method="Malcev.fixedKPermIdempotent",
        setup=_SETUP,
        call="Malcev.fixedKPermIdempotent(c2, 2, None)",
        description="fixedKPermIdempotent level 2 on C2",
        **_BOOL
    ),
    TestCaseSpec(
        id="perm_level_idem_c2",
        method="Malcev.permLevelIdempotent",
        setup=_SETUP,
        call="Malcev.permLevelIdempotent(c2, None)",
        description="permLevelIdempotent of C2",
    ),
]

_PATH_SETUP = _SETUP + r"""
from org.uacalc.util import IntArray
g0p = IntArray([0, 0, 1])
g2p = IntArray([1, 0, 0])
midp = [g0p, IntArray([0, 0, 0]), g2p]
firstp = [IntArray([0, 1, 0]), g2p]
hmsub = [g0p, g2p]
"""

_WIDE_SETUP = _SETUP + r"""
from org.uacalc.alg import BasicAlgebra
from org.uacalc.alg.op import OperationSymbol, Operations
from org.uacalc.example import Type1
n5 = AlgebraIO.readAlgebraFile("resources/algebras/n5.ua")
m3 = AlgebraIO.readAlgebraFile("resources/algebras/m3.ua")
ba2 = AlgebraIO.readAlgebraFile("resources/algebras/ba2.ua")
s3 = AlgebraIO.readAlgebraFile("resources/algebras/sym3.ua")
meet = Operations.makeIntOperation(OperationSymbol("m", 2), 2, [0, 0, 0, 1])
sem2 = BasicAlgebra("sem2", 2, [meet])
unary3 = Type1.cyclicPermutationAlgebra(3)
qstar = Operations.makeIntOperation(OperationSymbol("*", 2), 3, [0, 2, 1, 2, 1, 0, 1, 0, 2])
quasi3 = BasicAlgebra("quasi3", 3, [qstar])
rand2 = Algebras.makeRandomAlgebra(2, [1], 7)
rand_bin2 = Algebras.makeRandomAlgebra(2, [2], 11)
rand_bin = Algebras.makeRandomAlgebra(3, [2], 11)
rand_bin_3b = Algebras.makeRandomAlgebra(3, [2], 13)
rand_bin_3c = Algebras.makeRandomAlgebra(3, [2], 19)
rand_bin_3d = Algebras.makeRandomAlgebra(3, [2], 97)
"""

TEST_CASES.extend([
    TestCaseSpec(
        id="jonsson_level_path_midp",
        method="Malcev.jonssonLevelPath",
        setup=_PATH_SETUP,
        call="_ias(Malcev.jonssonLevelPath(midp, g0p, g2p, False))",
        description="jonssonLevelPath on a unique 3-vertex middleZero",
        **_LIST
    ),
    TestCaseSpec(
        id="jonsson_level_aux_midp",
        method="Malcev.jonssonLevelAux",
        setup=_PATH_SETUP,
        call="Malcev.jonssonLevelAux(midp, g0p, g2p)",
        description="jonssonLevelAux level of a unique 3-vertex middleZero",
    ),
    TestCaseSpec(
        id="gumm_level_path_midp",
        method="Malcev.gummLevelPath",
        setup=_PATH_SETUP,
        call="_ias(Malcev.gummLevelPath(midp, firstp, g0p, g2p))",
        description="gummLevelPath on a tiny firstOne/middleZero instance",
        **_LIST
    ),
    TestCaseSpec(
        id="hm_level_path_hmsub",
        method="Malcev.hagemannMitschkeLevelPath",
        setup=_PATH_SETUP,
        call="_ias(Malcev.hagemannMitschkeLevelPath(hmsub, g0p, g2p))",
        description="hagemannMitschkeLevelPath on {g0,g2}",
        **_LIST
    ),
    TestCaseSpec(
        id="nu_term_bad_lat2",
        method="Malcev.nuTermIdempotent_Bad",
        setup=_SETUP,
        call="Malcev.nuTermIdempotent_Bad(lat2, 3, None)",
        description="nuTermIdempotent_Bad on lat2 arity 3",
        **_BOOL
    ),
    TestCaseSpec(
        id="fixed_k_edge_idem_lat2",
        method="Malcev.fixedKEdgeIdempotent",
        setup=_SETUP,
        call="Malcev.fixedKEdgeIdempotent(lat2, 2, None)",
        description="fixedKEdgeIdempotent level 2 on lat2",
        **_BOOL
    ),
    TestCaseSpec(
        id="fixed_k_perm_idem_lat2",
        method="Malcev.fixedKPermIdempotent",
        setup=_SETUP,
        call="Malcev.fixedKPermIdempotent(lat2, 2, None)",
        description="lat2 is not 2-permutable",
        **_BOOL
    ),
    TestCaseSpec(
        id="fixed_k_edge_idem_level1",
        method="Malcev.fixedKEdgeIdempotent",
        setup=_SETUP,
        call="Malcev.fixedKEdgeIdempotent(c2, 1, None)",
        description="fixedKEdgeIdempotent level 1 is IAE",
        expected_exception="IllegalArgumentException",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="malcev_term_n5",
        method="Malcev.malcevTerm",
        setup=_WIDE_SETUP,
        call="_term(Malcev.malcevTerm(n5))",
        description="N5 has no Malcev term",
        **_NONE
    ),
    TestCaseSpec(
        id="malcev_term_m3",
        method="Malcev.malcevTerm",
        setup=_WIDE_SETUP,
        call="_term(Malcev.malcevTerm(m3))",
        description="M3 has no Malcev term",
        **_NONE
    ),
    TestCaseSpec(
        id="malcev_term_ba2",
        method="Malcev.malcevTerm",
        setup=_WIDE_SETUP,
        call="_term(Malcev.malcevTerm(ba2))",
        description="Malcev term of the 2-element Boolean algebra if any",
        **_TERM
    ),
    TestCaseSpec(
        id="malcev_term_sem2",
        method="Malcev.malcevTerm",
        setup=_WIDE_SETUP,
        call="_term(Malcev.malcevTerm(sem2))",
        description="2-element meet-semilattice has no Malcev term",
        **_NONE
    ),
    TestCaseSpec(
        id="malcev_term_s3",
        method="Malcev.malcevTerm",
        setup=_WIDE_SETUP,
        call="_term(Malcev.malcevTerm(s3))",
        description="Malcev term of S3 if any",
        **_TERM
    ),
    TestCaseSpec(
        id="malcev_term_quasi3",
        method="Malcev.malcevTerm",
        setup=_WIDE_SETUP,
        call="_term(Malcev.malcevTerm(quasi3))",
        description="Malcev term of a 3-element quasigroup if any",
        **_TERM
    ),
    TestCaseSpec(
        id="jonsson_level_n5",
        method="Malcev.jonssonLevel",
        setup=_WIDE_SETUP,
        call="Malcev.jonssonLevel(n5)",
        description="Jonsson level of N5",
    ),
    TestCaseSpec(
        id="jonsson_level_m3",
        method="Malcev.jonssonLevel",
        setup=_WIDE_SETUP,
        call="Malcev.jonssonLevel(m3)",
        description="Jonsson level of M3",
    ),
    TestCaseSpec(
        id="jonsson_level_ba2",
        method="Malcev.jonssonLevel",
        setup=_WIDE_SETUP,
        call="Malcev.jonssonLevel(ba2)",
        description="Jonsson level of ba2",
    ),
    TestCaseSpec(
        id="cm_variety_n5",
        method="Malcev.congruenceModularVariety",
        setup=_WIDE_SETUP,
        call="Malcev.congruenceModularVariety(n5)",
        description="N5 does not generate a CM variety",
        **_BOOL
    ),
    TestCaseSpec(
        id="cm_variety_m3",
        method="Malcev.congruenceModularVariety",
        setup=_WIDE_SETUP,
        call="Malcev.congruenceModularVariety(m3)",
        description="M3 generates a CM variety",
        **_BOOL
    ),
    TestCaseSpec(
        id="type_set_idem_n5",
        method="Malcev.typeSetIdempotent",
        setup=_WIDE_SETUP,
        call="_sets(Malcev.typeSetIdempotent(n5, None))",
        description="typeSetIdempotent of N5",
        **_LIST
    ),
    TestCaseSpec(
        id="type_set_idem_m3",
        method="Malcev.typeSetIdempotent",
        setup=_WIDE_SETUP,
        call="_sets(Malcev.typeSetIdempotent(m3, None))",
        description="typeSetIdempotent of M3",
        **_LIST
    ),
    TestCaseSpec(
        id="type_set_idem_ba2",
        method="Malcev.typeSetIdempotent",
        setup=_WIDE_SETUP,
        call="_sets(Malcev.typeSetIdempotent(ba2, None))",
        description="typeSetIdempotent of ba2",
        **_LIST
    ),
    TestCaseSpec(
        id="type_set_idem_sem2",
        method="Malcev.typeSetIdempotent",
        setup=_WIDE_SETUP,
        call="_sets(Malcev.typeSetIdempotent(sem2, None))",
        description="typeSetIdempotent of a 2-element semilattice",
        **_LIST
    ),
    TestCaseSpec(
        id="omitted_ideal_sem2",
        method="Malcev.omittedIdealIdempotent",
        setup=_WIDE_SETUP,
        call="sorted(int(x) for x in list(Malcev.omittedIdealIdempotent(sem2, None)))",
        description="omittedIdealIdempotent of a 2-element semilattice",
        **_LIST
    ),
    TestCaseSpec(
        id="types_in_s_lat2",
        method="Malcev.typesInSofAIdempotent",
        setup=_WIDE_SETUP,
        call="sorted(int(x) for x in list(Malcev.typesInSofAIdempotent(lat2, set(), None)))",
        description="typesInSofAIdempotent of lat2",
        **_LIST
    ),
    TestCaseSpec(
        id="types_robust_c2",
        method="Malcev.typesInSofAIRobustDecompdempotent",
        setup=_WIDE_SETUP,
        call="sorted(int(x) for x in list(Malcev.typesInSofAIRobustDecompdempotent(c2, set(), None)))",
        description="typesInSofAIRobustDecompdempotent of C2",
        **_LIST
    ),
    TestCaseSpec(
        id="perm_level_idem_c3",
        method="Malcev.permLevelIdempotent",
        setup=_WIDE_SETUP,
        call="Malcev.permLevelIdempotent(c3, None)",
        description="permLevelIdempotent of C3",
    ),
    TestCaseSpec(
        id="malcev_term_rand2",
        method="Malcev.malcevTerm",
        setup=_WIDE_SETUP,
        call="[rand2.cardinality(), _term(Malcev.malcevTerm(rand2))]",
        description="seeded random unary algebra of size 2: card and Malcev term",
        **_LIST
    ),
    TestCaseSpec(
        id="malcev_term_unary3",
        method="Malcev.malcevTerm",
        setup=_WIDE_SETUP,
        call="_term(Malcev.malcevTerm(unary3))",
        description="cyclic permutation algebra of size 3 has no Malcev term",
        **_NONE
    ),
    TestCaseSpec(
        id="malcev_term_rand_bin2",
        method="Malcev.malcevTerm",
        setup=_WIDE_SETUP,
        call="[rand_bin2.cardinality(), _term(Malcev.malcevTerm(rand_bin2))]",
        description="seeded random binary algebra of size 2: card and Malcev term",
        **_LIST
    ),
    TestCaseSpec(
        id="malcev_term_rand_bin",
        method="Malcev.malcevTerm",
        setup=_WIDE_SETUP,
        call="[rand_bin.cardinality(), _term(Malcev.malcevTerm(rand_bin))]",
        description="seeded random binary magma of size 3: card and Malcev term",
        timeout_seconds=120,
        **_LIST
    ),
    TestCaseSpec(
        id="type_set_idem_unary3",
        method="Malcev.typeSetIdempotent",
        setup=_WIDE_SETUP,
        call="_sets(Malcev.typeSetIdempotent(unary3, None))",
        description="typeSetIdempotent of a cyclic permutation algebra",
        **_LIST
    ),
    TestCaseSpec(
        id="omitted_ideal_n5",
        method="Malcev.omittedIdealIdempotent",
        setup=_WIDE_SETUP,
        call="sorted(int(x) for x in list(Malcev.omittedIdealIdempotent(n5, None)))",
        description="omittedIdealIdempotent of N5",
        **_LIST
    ),
    TestCaseSpec(
        id="omitted_ideal_ba2",
        method="Malcev.omittedIdealIdempotent",
        setup=_WIDE_SETUP,
        call="sorted(int(x) for x in list(Malcev.omittedIdealIdempotent(ba2, None)))",
        description="omittedIdealIdempotent of ba2",
        **_LIST
    ),
    TestCaseSpec(
        id="jonsson_level_sem2",
        method="Malcev.jonssonLevel",
        setup=_WIDE_SETUP,
        call="Malcev.jonssonLevel(sem2)",
        description="Jonsson level of a 2-element semilattice",
    ),
    TestCaseSpec(
        id="cm_variety_ba2",
        method="Malcev.congruenceModularVariety",
        setup=_WIDE_SETUP,
        call="Malcev.congruenceModularVariety(ba2)",
        description="ba2 generates a CM variety",
        **_BOOL
    ),
    TestCaseSpec(
        id="fixed_k_perm_idem_c3",
        method="Malcev.fixedKPermIdempotent",
        setup=_WIDE_SETUP,
        call="Malcev.fixedKPermIdempotent(c3, 2, None)",
        description="fixedKPermIdempotent level 2 on C3",
        **_BOOL
    ),
    TestCaseSpec(
        id="nu_term_bad_ba2",
        method="Malcev.nuTermIdempotent_Bad",
        setup=_WIDE_SETUP,
        call="Malcev.nuTermIdempotent_Bad(ba2, 3, None)",
        description="nuTermIdempotent_Bad on ba2 arity 3",
        **_BOOL
    ),
])

# Random magmas: Java returns quickly (typically null) for F(2)^2 searches
# when F(2) is modest. Time out a hang so CI fails rather than stalling.
# Size-3 seed 11 is the case PR #79 swapped away (Java ~10s, F(2)=409).
# Extra size-3 seeds were chosen so Java malcevTerm returns in <2s (F(2) << 500).
# Size-4 random magmas have huge F(2) even in Java (construction itself >20s),
# so they are not in this CI set. F(2)^3 searches on size-3 magmas are slow
# even in Java; those related searches are covered on the size-2 magma.
_MAGMA_TIMEOUT = dict(size2=30, size3=120)
_RANDOM_MAGMAS = (
    ("rand_bin2", 2, 11, "rand_bin2"),
    ("rand_bin", 3, 11, "rand_bin"),
    ("rand_bin_3b", 3, 13, "rand_bin_3b"),
    ("rand_bin_3c", 3, 19, "rand_bin_3c"),
    ("rand_bin_3d", 3, 97, "rand_bin_3d"),
)
_F2_SQUARED_SEARCHES = (
    ("malcev_term", "Malcev.malcevTerm", "_term(Malcev.malcevTerm({alg}))", _TERM),
    ("hagemann_mitschke", "Malcev.hagemannMitschkeTerms", "_terms(Malcev.hagemannMitschkeTerms({alg}))", _LIST),
)
_F2_CUBED_SEARCHES = (
    ("majority_term", "Malcev.majorityTerm", "_term(Malcev.majorityTerm({alg}))", _TERM),
    ("minority_term", "Malcev.minorityTerm", "_term(Malcev.minorityTerm({alg}))", _TERM),
    ("pixley_term", "Malcev.pixleyTerm", "_term(Malcev.pixleyTerm({alg}))", _TERM),
    ("nu_term", "Malcev.nuTerm", "_term(Malcev.nuTerm({alg}, 3))", _TERM),
    ("jonsson_terms", "Malcev.jonssonTerms", "_terms(Malcev.jonssonTerms({alg}))", _LIST),
    # gummTerms(alg) NPEs in Java (null ProgressReport); covered elsewhere as an xfail.
)

_random_magma_cases = []
for _alg, _n, _seed, _var in _RANDOM_MAGMAS:
    _timeout = _MAGMA_TIMEOUT["size2"] if _n == 2 else _MAGMA_TIMEOUT["size3"]
    _searches = list(_F2_SQUARED_SEARCHES)
    if _n == 2:
        _searches.extend(_F2_CUBED_SEARCHES)
    for _sid, _method, _call, _flags in _searches:
        if _alg == "rand_bin" and _sid == "malcev_term":
            continue  # already restored above as malcev_term_rand_bin
        if _alg == "rand_bin2" and _sid == "malcev_term":
            continue  # already present as malcev_term_rand_bin2
        _random_magma_cases.append(
            TestCaseSpec(
                id="{0}_{1}".format(_sid, _alg),
                method=_method,
                setup=_WIDE_SETUP,
                call=_call.format(alg=_var),
                description="seeded random binary magma of size {0} seed {1}: {2}".format(
                    _n, _seed, _method
                ),
                timeout_seconds=_timeout,
                **_flags
            )
        )

TEST_CASES.extend(_random_magma_cases)
