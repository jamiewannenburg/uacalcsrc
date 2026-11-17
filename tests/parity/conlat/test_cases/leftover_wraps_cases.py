"""Golden parity cases for leftover org.uacalc.alg.conlat wrappers."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.io import AlgebraIO
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
n5 = AlgebraIO.readAlgebraFile("resources/algebras/n5.ua")
con_c2 = c2.con()
con_n5 = n5.con()
zero_n5 = n5.con().zero()
one_n5 = n5.con().one()
jis_n5 = list(n5.con().joinIrreducibles())

def _par_arr(p):
    if p is None:
        return None
    fn = getattr(p, "toArray", None) or getattr(p, "to_array", None) or getattr(p, "getArray", None)
    if callable(fn):
        return [int(x) for x in list(fn())]
    return str(p)

def _par_list(lst):
    if lst is None:
        return None
    return [_par_arr(p) for p in list(lst)]
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List toString vs Python list.")
_LAT = dict(skip_string_check=True, notes="Java lattice toString is Class@hex; values compared.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")

TEST_CASES = [
    TestCaseSpec(
        id="cl_con_card",
        method="CongruenceLattice.con",
        setup=_SETUP,
        call="int(con_c2.con().cardinality())",
        description="Con(Con(C2)) cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="cl_sub_card",
        method="CongruenceLattice.sub",
        setup=_SETUP,
        call="int(con_c2.sub().cardinality()) if hasattr(con_c2.sub(), 'cardinality') else int(con_c2.sub().universeSize() if hasattr(con_c2.sub(), 'universeSize') else len(list(con_c2.sub().universe())))",
        description="Sub(Con(C2)) cardinality",
        **_LAT
    ),
    TestCaseSpec(
        id="cl_size_computed_after_univ",
        method="CongruenceLattice.getSizeComputed",
        setup=_SETUP,
        call="(con_c2.universe() and 1) * con_c2.getSizeComputed()",
        description="getSizeComputed after universe() of C2",
    ),
    TestCaseSpec(
        id="cl_make_universe_k_fresh",
        method="CongruenceLattice.getMakeUniverseK",
        setup=_SETUP,
        call="c2.con().getMakeUniverseK()",
        description="getMakeUniverseK starts at 0 on a fresh lattice",
    ),
    TestCaseSpec(
        id="cl_stop_make_universe",
        method="CongruenceLattice.stopMakeUniverse",
        setup=_SETUP,
        call="con_c2.stopMakeUniverse() or True",
        description="stopMakeUniverse is callable",
        **_BOOL
    ),
    TestCaseSpec(
        id="cl_sort_by_rank",
        method="CongruenceLattice.sortByRank",
        setup=_SETUP + """
lst = [n5.con().zero(), n5.con().one()] + list(n5.con().joinIrreducibles())[:2]
con_n5.sortByRank(lst)
""",
        call="[_par_arr(p) for p in lst]",
        description="sortByRank orders by descending numberOfBlocks",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_make_irredundant_meet",
        method="CongruenceLattice.makeIrredundantMeet",
        setup=_SETUP,
        call="_par_list(con_n5.makeIrredundantMeet(list(n5.con().meetIrreducibles())))",
        description="makeIrredundantMeet of N5 meet-irreducibles",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_irredundant_meet_old",
        method="CongruenceLattice.irredundantMeetDecompositionOld",
        setup=_SETUP,
        call="_par_list(con_n5.irredundantMeetDecompositionOld())",
        description="irredundantMeetDecompositionOld of N5",
        **_LIST
    ),
    TestCaseSpec(
        id="cl_find_l3_c2",
        method="CongruenceLattice.findL3Generators",
        setup=_SETUP,
        call="_par_list(con_c2.findL3Generators())",
        description="findL3Generators of C2",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_find_lxx_c2",
        method="CongruenceLattice.findLXXGenerators",
        setup=_SETUP,
        call="con_c2.findLXXGenerators()",
        description="findLXXGenerators of C2 returns null",
        **_NONE
    ),
    TestCaseSpec(
        id="cl_find_lpj10_c2",
        method="CongruenceLattice.findLPJ10Generators",
        setup=_SETUP,
        call="con_c2.findLPJ10Generators()",
        description="findLPJ10Generators of C2 returns null",
        **_NONE
    ),
]
