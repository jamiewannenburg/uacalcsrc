"""Golden parity cases for leftover org.uacalc.alg wrappers."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import (
    BigProductAlgebra, Closer, MaltsevDecompositionIterator,
    MaltsevProductDecomposition, QuotientAlgebra, QuotientElement,
    SubProductAlgebra,
)
from org.uacalc.util import IntArray
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
n5 = AlgebraIO.readAlgebraFile("resources/algebras/n5.ua")
bp2 = BigProductAlgebra(c2, 2)
g00 = IntArray([0, 0])
g11 = IntArray([1, 1])
sp = SubProductAlgebra("SP", bp2, [g00, g11])
closer = Closer(bp2, [g00, g11])
cong = n5.con().Cg(0, 1)
decomp = MaltsevProductDecomposition(n5, cong)
q = QuotientAlgebra(c2, c2.con().Cg(0, 1))
qe = QuotientElement(q, 0)

def _ias(lst):
    if lst is None:
        return None
    out = []
    for x in list(lst):
        try:
            out.append([int(v) for v in list(x)])
        except TypeError:
            getter = getattr(x, "getArray", None) or getattr(x, "to_array", None) or getattr(x, "get_array", None)
            out.append([int(v) for v in getter()] if callable(getter) else x)
    return out
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List toString vs Python list.")
_ALG = dict(skip_string_check=True, notes="Java Algebra toString is Class@hex; values compared.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")

TEST_CASES = [
    TestCaseSpec(
        id="sp_transpose_two",
        method="SubProductAlgebra.transpose",
        setup=_SETUP,
        call="_ias(SubProductAlgebra.transpose([IntArray([0, 1]), IntArray([1, 0])]))",
        description="transpose of two length-2 IntArrays",
        **_LIST
    ),
    TestCaseSpec(
        id="sp_get_thin_default",
        method="SubProductAlgebra.getThinGenerators",
        setup=_SETUP,
        call="sp.getThinGenerators(False)",
        description="getThinGenerators default is false",
        **_BOOL
    ),
    TestCaseSpec(
        id="sp_set_get_thin",
        method="SubProductAlgebra.setThinGenerators",
        setup=_SETUP,
        call="sp.setThinGenerators(True) or sp.getThinGenerators(True)",
        description="setThinGenerators True then getThinGenerators",
        **_BOOL
    ),
    TestCaseSpec(
        id="sp_get_decompose_default",
        method="SubProductAlgebra.getDecompose",
        setup=_SETUP,
        call="sp.getDecompose()",
        description="getDecompose default is false",
        **_BOOL
    ),
    TestCaseSpec(
        id="sp_set_get_decompose",
        method="SubProductAlgebra.setDecompose",
        setup=_SETUP,
        call="sp.setDecompose(True) or sp.getDecompose()",
        description="setDecompose True then getDecompose",
        **_BOOL
    ),
    TestCaseSpec(
        id="sp_thin_generators",
        method="SubProductAlgebra.thinGenerators",
        setup=_SETUP,
        call="_ias(sp.thinGenerators())",
        description="thinGenerators of a 2-generated C2 power",
        **_LIST
    ),
    TestCaseSpec(
        id="sp_universe_from_relations_empty",
        method="SubProductAlgebra.universeFromRelations",
        setup=_SETUP,
        call="_ias(SubProductAlgebra.universeFromRelations(2, 2, {}))",
        description="universeFromRelations with empty rels is the full power",
        **_LIST
    ),
    TestCaseSpec(
        id="closer_count_func_apps",
        method="Closer.countFuncApplications",
        setup=_SETUP,
        call="closer.countFuncApplications(1, 2)",
        description="countFuncApplications from size 1 to 2 on C2^2",
    ),
    TestCaseSpec(
        id="closer_do_one_stage_null_map",
        method="Closer.doOneStagePartialClosure",
        setup=_SETUP,
        call="closer.doOneStagePartialClosure(None, 0, 1, 0, 1, False, [], None)",
        description="doOneStagePartialClosure IOBE on empty rawList before map is used",
        compare_exception_message=False,
        **_NONE
    ),
    TestCaseSpec(
        id="closer_do_one_stage_zero_ops",
        method="Closer.doOneStagePartialClosure",
        setup=_SETUP + """
try:
    from java.util.concurrent import ConcurrentHashMap
    from jarray import array as _jarray
    chm = ConcurrentHashMap()
    raw00 = _jarray([0, 0], 'i')
except ImportError:
    chm = {}
    raw00 = [0, 0]
""",
        call="closer.doOneStagePartialClosure(chm, 0, 0, 0, 0, False, [], None) or True",
        description="doOneStagePartialClosure with numOfOps=0 is a no-op",
        **_BOOL
    ),
    TestCaseSpec(
        id="closer_do_one_stage_worker",
        method="Closer.doOneStagePartialClosure",
        setup=_SETUP + """
try:
    from java.util.concurrent import ConcurrentHashMap
    from jarray import array as _jarray
    chm = ConcurrentHashMap()
    raw00 = _jarray([0, 0], 'i')
except ImportError:
    chm = {}
    raw00 = [0, 0]
""",
        call="closer.doOneStagePartialClosure(chm, 0, 1, 0, 1, False, [raw00], None) or True",
        description="doOneStagePartialClosure NPEs when termMap is null",
        compare_exception_message=False,
        **_NONE
    ),
    TestCaseSpec(
        id="mpd_get_algebra_card",
        method="MaltsevProductDecomposition.getAlgebra",
        setup=_SETUP,
        call="decomp.getAlgebra().cardinality()",
        description="getAlgebra returns the original algebra",
        **_ALG
    ),
    TestCaseSpec(
        id="mpd_set_algebra_roundtrip",
        method="MaltsevProductDecomposition.setAlgebra",
        setup=_SETUP,
        call="decomp.setAlgebra(c2) or decomp.getAlgebra().cardinality()",
        description="setAlgebra then getAlgebra cardinality",
        **_ALG
    ),
    TestCaseSpec(
        id="mpd_set_congruence_roundtrip",
        method="MaltsevProductDecomposition.setCongruence",
        setup=_SETUP,
        call="decomp.setCongruence(n5.con().zero()) or decomp.getCongruence().numberOfBlocks()",
        description="setCongruence then getCongruence",
    ),
    TestCaseSpec(
        id="mpd_set_block_algebras",
        method="MaltsevProductDecomposition.setBlockAlgebras",
        setup=_SETUP,
        call="decomp.setBlockAlgebras([]) or len(list(decomp.getBlockAlgebras()))",
        description="setBlockAlgebras empty list then getBlockAlgebras",
    ),
    TestCaseSpec(
        id="mpd_set_quotient_algebra",
        method="MaltsevProductDecomposition.setQuotientAlgebra",
        setup=_SETUP,
        call="decomp.setQuotientAlgebra(c2) or decomp.getQuotientAlgebra().cardinality()",
        description="setQuotientAlgebra then getQuotientAlgebra",
        **_ALG
    ),
    TestCaseSpec(
        id="mdi_has_next_n5",
        method="MaltsevDecompositionIterator.hasNext",
        setup=_SETUP,
        call="MaltsevDecompositionIterator(n5).hasNext()",
        description="idempotent N5 iterator hasNext",
        **_BOOL
    ),
    TestCaseSpec(
        id="mdi_next_cards_n5",
        method="MaltsevDecompositionIterator.next",
        setup=_SETUP + """
it = MaltsevDecompositionIterator(n5)
mdi_cards = []
while it.hasNext():
    mdi_cards.append(int(it.next().cardinality()))
""",
        call="mdi_cards",
        description="N5 MaltsevDecompositionIterator yields real algebras",
        **_LIST
    ),
    TestCaseSpec(
        id="mdi_remove_uoe",
        method="MaltsevDecompositionIterator.remove",
        setup=_SETUP,
        call="MaltsevDecompositionIterator(n5).remove()",
        description="remove() is UnsupportedOperationException",
        compare_exception_message=False,
        **_NONE
    ),
    TestCaseSpec(
        id="qe_construct_index",
        method="QuotientElement.getIndex",
        setup=_SETUP,
        call="qe.getIndex()",
        description="QuotientElement(q, 0).getIndex",
        **_ALG
    ),
]
