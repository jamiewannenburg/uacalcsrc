"""Test case specifications for org.uacalc.lat behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_MAKE_OPS = """
from org.uacalc.alg.op import Operations, OperationSymbol
from org.uacalc.lat import Lattices, OrderedSets
def _make_int_op(name, arity, size, table):
    make = getattr(Operations, "makeIntOperation", None)
    if make is None:
        make = Operations.make_int_operation
    return make(OperationSymbol(name, arity), size, table)
join2 = _make_int_op("v", 2, 2, [0, 1, 1, 1])
meet2 = _make_int_op("meet", 2, 2, [0, 0, 0, 1])
join_m3 = _make_int_op("v", 2, 4, [
    0, 1, 2, 3,
    1, 1, 3, 3,
    2, 3, 2, 3,
    3, 3, 3, 3,
])
bad_join = _make_int_op("v", 2, 2, [0, 0, 1, 0])
"""

TEST_CASES = [
    TestCaseSpec(
        id="lattice_from_join_2chain",
        method="Lattices.latticeFromJoin",
        setup=_MAKE_OPS,
        call='Lattices.latticeFromJoin("chain2j", join2)',
        description="Build 2-element chain from join operation",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_meet_2chain",
        method="Lattices.latticeFromMeet",
        setup=_MAKE_OPS,
        call='Lattices.latticeFromMeet("chain2m", meet2)',
        description="Build 2-element chain from meet operation",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_diamond",
        method="Lattices.latticeFromJoin",
        setup=_MAKE_OPS,
        call='Lattices.latticeFromJoin("M3", join_m3)',
        description="Build diamond M3 from join operation",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_with_universe",
        method="Lattices.latticeFromJoin",
        setup=_MAKE_OPS,
        call='Lattices.latticeFromJoin("chain2j3", [0, 1], join2)',
        description="latticeFromJoin(name, universe, join)",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_meet_with_universe",
        method="Lattices.latticeFromMeet",
        setup=_MAKE_OPS,
        call='Lattices.latticeFromMeet("chain2m3", [0, 1], meet2)',
        description="latticeFromMeet(name, universe, meet)",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_not_ordered",
        method="Lattices.latticeFromJoin",
        setup=_MAKE_OPS,
        call='Lattices.latticeFromJoin("bad", bad_join)',
        description="Non-lattice join table: Java catches NonOrderedSetException and returns null",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_cardinality",
        method="BasicLattice.cardinality",
        setup=_MAKE_OPS + """
lat = Lattices.latticeFromJoin("chain2j", join2)
""",
        call="lat.cardinality()",
        description="BasicLattice.cardinality of a 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_leq",
        method="BasicLattice.leq",
        setup=_MAKE_OPS + """
import sys
lat = Lattices.latticeFromJoin("chain2j", join2)
if sys.platform.startswith("java"):
    a = lat.getElement(0)
    b = lat.getElement(1)
else:
    a = 0
    b = 1
""",
        call="lat.leq(a, b)",
        description="0 <= 1 in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_join",
        method="BasicLattice.join",
        setup=_MAKE_OPS + """
import sys
lat = Lattices.latticeFromJoin("chain2j", join2)
if sys.platform.startswith("java"):
    a = lat.getElement(0)
    b = lat.getElement(1)
else:
    a = 0
    b = 1
""",
        call="lat.join(a, b)",
        description="join(0,1) is 1 in the 2-chain",
        skip_string_check=True,
        notes="Java returns a POElem that stringifies to 1; Python returns int 1.",
    ),
    TestCaseSpec(
        id="basic_lattice_meet",
        method="BasicLattice.meet",
        setup=_MAKE_OPS + """
import sys
lat = Lattices.latticeFromJoin("chain2j", join2)
if sys.platform.startswith("java"):
    a = lat.getElement(0)
    b = lat.getElement(1)
else:
    a = 0
    b = 1
""",
        call="lat.meet(a, b)",
        description="meet(0,1) is 0 in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_zero",
        method="BasicLattice.zero",
        setup=_MAKE_OPS + """
lat = Lattices.latticeFromJoin("chain2j", join2)
""",
        call="lat.zero()",
        description="Bottom element of the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_join_irreducibles",
        method="BasicLattice.joinIrreducibles",
        setup=_MAKE_OPS + """
lat = Lattices.latticeFromJoin("chain2j", join2)
""",
        call="list(lat.joinIrreducibles()) if hasattr(lat, 'joinIrreducibles') else list(lat.join_irreducibles())",
        description="Join-irreducibles of the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ordered_sets_maximals_divisibility",
        method="OrderedSets.maximals",
        setup=_MAKE_OPS + """
import sys
if sys.platform.startswith("java"):
    # Java has no DivisibilityOrder class; subclass Order with the same leq.
    from org.uacalc.lat import Order
    class _Div(Order):
        def leq(self, a, b):
            if a == 0:
                return True
            if b == 0:
                return a == 0
            return (b % a) == 0
    order = _Div()
else:
    from org.uacalc.lat import DivisibilityOrder
    order = DivisibilityOrder()
""",
        call="list(OrderedSets.maximals([2, 3, 6, 35, 175], order))",
        description="Maximals under divisibility via uacalc_lib.lat.maximals_divisibility",
    ),
    TestCaseSpec(
        id="lattices_dual",
        method="Lattices.dual",
        setup=_MAKE_OPS + """
lat = Lattices.latticeFromJoin("chain2j", join2)
""",
        call="Lattices.dual(lat)",
        description="Lattices.dual of a 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattices_con_to_small_lattice",
        method="Lattices.conToSmallLattice",
        setup=_MAKE_OPS + """
import sys
from org.uacalc.io import AlgebraIO
alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
if sys.platform.startswith("java"):
    from org.uacalc.alg.conlat import CongruenceLattice
    con = CongruenceLattice(alg)
    _ctors = Lattices.getDeclaredConstructors()
    _ctors[0].setAccessible(True)
    _helper = _ctors[0].newInstance()
    def _con_to_small():
        return _helper.conToSmallLattice(con)
else:
    from org.uacalc.alg import CongruenceLattice
    con = CongruenceLattice(alg)
    def _con_to_small():
        return Lattices.conToSmallLattice(con)
""",
        call="_con_to_small()",
        description="Lattices.conToSmallLattice on Con(C2); Java always returns null",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattices_con_to_small_lattice_null",
        method="Lattices.conToSmallLattice",
        setup=_MAKE_OPS + """
import sys
if sys.platform.startswith("java"):
    _ctors = Lattices.getDeclaredConstructors()
    _ctors[0].setAccessible(True)
    _helper = _ctors[0].newInstance()
    def _con_to_small():
        return _helper.conToSmallLattice(None)
else:
    def _con_to_small():
        return Lattices.conToSmallLattice(None)
""",
        call="_con_to_small()",
        description="conToSmallLattice(null) error case",
        expected_exception="NullPointerException",
    ),
]

_CHAIN = _MAKE_OPS + """
import sys
lat = Lattices.latticeFromJoin("chain2j", join2)
m3 = Lattices.latticeFromJoin("M3", join_m3)
def _labs(xs):
    if xs is None:
        return None
    return sorted([int(str(x)) for x in list(xs)])
def _lab(x):
    if x is None:
        return None
    try:
        return int(str(x))
    except Exception:
        return str(x)
if sys.platform.startswith("java"):
    a0 = lat.getElement(0)
    a1 = lat.getElement(1)
    try:
        from java.util import ArrayList
        join_args = ArrayList()
        join_args.add(a0)
        join_args.add(a1)
        empty_args = ArrayList()
    except Exception:
        join_args = [a0, a1]
        empty_args = []
else:
    a0 = 0
    a1 = 1
    join_args = [a0, a1]
    empty_args = []
"""

_FILE_LATTICE = """
from org.uacalc.io import AlgebraIO
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.lat import Lattices, BasicLattice
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
join_sym = OperationSymbol("join", 2)
lat2_join = lat2.getOperation(join_sym)
"""

TEST_CASES.extend([
    TestCaseSpec(
        id="basic_lattice_one",
        method="BasicLattice.one",
        setup=_CHAIN,
        call="_lab(lat.one())",
        description="Top element of the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_atoms_chain",
        method="BasicLattice.atoms",
        setup=_CHAIN,
        call="_labs(lat.atoms())",
        description="Atoms of the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_atoms_diamond",
        method="BasicLattice.atoms",
        setup=_CHAIN,
        call="_labs(m3.atoms())",
        description="Atoms of the 4-element diamond",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_coatoms_chain",
        method="BasicLattice.coatoms",
        setup=_CHAIN,
        call="_labs(lat.coatoms())",
        description="Coatoms of the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_coatoms_diamond",
        method="BasicLattice.coatoms",
        setup=_CHAIN,
        call="_labs(m3.coatoms())",
        description="Coatoms of the 4-element diamond",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_meet_irreducibles",
        method="BasicLattice.meetIrreducibles",
        setup=_CHAIN,
        call="_labs(lat.meetIrreducibles() if hasattr(lat, 'meetIrreducibles') else lat.meet_irreducibles())",
        description="Meet-irreducibles of the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_filter",
        method="BasicLattice.filter",
        setup=_CHAIN,
        call="_labs(lat.filter(a0))",
        description="Filter of 0 in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_ideal",
        method="BasicLattice.ideal",
        setup=_CHAIN,
        call="_labs(lat.ideal(a1))",
        description="Ideal of 1 in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_upper_covers",
        method="BasicLattice.upperCovers",
        setup=_CHAIN,
        call="_labs(lat.upperCovers(a0) if hasattr(lat, 'upperCovers') else lat.upper_covers(a0))",
        description="Upper covers of 0 in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_lower_covers",
        method="BasicLattice.lowerCovers",
        setup=_CHAIN,
        call="_labs(lat.lowerCovers(a1) if hasattr(lat, 'lowerCovers') else lat.lower_covers(a1))",
        description="Lower covers of 1 in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_get_element",
        method="BasicLattice.getElement",
        setup=_CHAIN,
        call="_lab(lat.getElement(0))",
        description="getElement(0) of the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_element_index",
        method="BasicLattice.elementIndex",
        setup=_CHAIN,
        call="lat.elementIndex(a0) if hasattr(lat, 'elementIndex') else lat.element_index(a0)",
        description="elementIndex of bottom in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_algebra_type",
        method="BasicLattice.algebraType",
        setup=_CHAIN,
        call="str(lat.algebraType())",
        description="algebraType of a BasicLattice",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_get_universe_order",
        method="BasicLattice.getUniverseOrder",
        setup=_CHAIN,
        call="lat.getUniverseOrder()",
        description="getUniverseOrder always returns null/None",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_convert_to_default_value_ops",
        method="BasicLattice.convertToDefaultValueOps",
        setup=_CHAIN,
        call="lat.convertToDefaultValueOps()",
        description="convertToDefaultValueOps raises UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="basic_lattice_instance_dual",
        method="BasicLattice.dual",
        setup=_CHAIN,
        call="lat.dual()",
        description="Instance dual delegates to Lattices.dual (Java NPE)",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_get_poset",
        method="BasicLattice.getPoset",
        setup=_CHAIN + """
p = lat.getPoset()
if hasattr(p, "univ"):
    poset_card = len(list(p.univ()))
else:
    poset_card = p.cardinality()
""",
        call="poset_card",
        description="getPoset cardinality matches the lattice",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_join_list",
        method="BasicLattice.join",
        setup=_CHAIN,
        call="_lab(lat.join(join_args))",
        description="join(List) of {0,1} in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_join_empty_list",
        method="BasicLattice.join",
        setup=_CHAIN,
        call="_lab(lat.join(empty_args))",
        description="join([]) is zero",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_meet_list",
        method="BasicLattice.meet",
        setup=_CHAIN,
        call="_lab(lat.meet(join_args))",
        description="meet(List) of {0,1} in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_universe",
        method="BasicLattice.universe",
        setup=_CHAIN,
        call="_labs(lat.universe())",
        description="universe() of the 2-chain as sorted labels",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_get_universe_list",
        method="BasicLattice.getUniverseList",
        setup=_CHAIN,
        call="_labs(lat.getUniverseList())",
        description="getUniverseList of the 2-chain as sorted labels",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_join_irreds_below",
        method="BasicLattice.joinIrredsBelow",
        setup=_CHAIN,
        call="_labs(lat.joinIrredsBelow(a1))",
        description="joinIrredsBelow(1) in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_meet_irreds_above",
        method="BasicLattice.meetIrredsAbove",
        setup=_CHAIN,
        call="_labs(lat.meetIrredsAbove(a0))",
        description="meetIrredsAbove(0) in the 2-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_from_con_c2",
        method="BasicLattice.cardinality",
        setup=_FILE_LATTICE + """
con = c2.con()
con_lat = BasicLattice("ConC2", con, False)
""",
        call="con_lat.cardinality()",
        description="BasicLattice from Con(C2) cardinality",
        skip_string_check=True,
        xfail_reason=(
            "Owner/library: BasicLattice(name, CongruenceLattice, label) on "
            "Python yields cardinality 0; Java Con(C2) has cardinality 2."
        ),
    ),
    TestCaseSpec(
        id="lattice_from_join_lat2_file",
        method="Lattices.latticeFromJoin",
        setup=_FILE_LATTICE,
        call='Lattices.latticeFromJoin("from_lat2", lat2_join)',
        description="latticeFromJoin of join table from lat2.ua",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ordered_sets_maximals_prefix",
        method="OrderedSets.maximals",
        setup=_MAKE_OPS + """
import sys
if sys.platform.startswith("java"):
    from org.uacalc.lat import Order
    class _Pref(Order):
        def leq(self, a, b):
            sa = str(a)
            sb = str(b)
            return sb.startswith(sa)
    order = _Pref()
else:
    from org.uacalc.lat import PrefixOrder
    order = PrefixOrder()
""",
        call="list(OrderedSets.maximals(['ab', 'a', 'abc', 'xy'], order))",
        description="Maximals under prefix order",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ordered_sets_maximals_natural",
        method="OrderedSets.maximals",
        setup=_MAKE_OPS + """
import sys
if sys.platform.startswith("java"):
    from org.uacalc.lat import Order
    class _Nat(Order):
        def leq(self, a, b):
            return a <= b
    order = _Nat()
else:
    from org.uacalc.lat import NaturalOrder
    order = NaturalOrder()
""",
        call="list(OrderedSets.maximals([3, 1, 4, 2], order))",
        description="Maximals under natural integer order",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_lattice_find_join_irred",
        method="BasicLattice.findJoinIrred",
        setup=_CHAIN,
        call="_lab(lat.findJoinIrred(a1, a0))",
        description="findJoinIrred(1, 0) in the 2-chain",
        skip_string_check=True,
        xfail_reason=(
            "Owner/library: findJoinIrred is not bound on PyBasicLattice. "
            "Java returns 1 on the 2-chain."
        ),
    ),
    TestCaseSpec(
        id="basic_lattice_find_meet_irred",
        method="BasicLattice.findMeetIrred",
        setup=_CHAIN,
        call="_lab(lat.findMeetIrred(a0, a1))",
        description="findMeetIrred(0, 1) in the 2-chain",
        skip_string_check=True,
        xfail_reason=(
            "Owner/library: findMeetIrred is not bound on PyBasicLattice. "
            "Java returns 0 on the 2-chain."
        ),
    ),
    TestCaseSpec(
        id="basic_lattice_irredundant_join_decomp",
        method="BasicLattice.irredundantJoinDecomposition",
        setup=_CHAIN,
        call="_labs(lat.irredundantJoinDecomposition(a1))",
        description="irredundantJoinDecomposition of 1 in the 2-chain",
        skip_string_check=True,
        xfail_reason=(
            "Owner/library: irredundantJoinDecomposition is not bound on "
            "PyBasicLattice."
        ),
    ),
    TestCaseSpec(
        id="basic_lattice_irredundant_meet_decomp",
        method="BasicLattice.irredundantMeetDecomposition",
        setup=_CHAIN,
        call="_labs(lat.irredundantMeetDecomposition(a0))",
        description="irredundantMeetDecomposition of 0 in the 2-chain",
        skip_string_check=True,
        xfail_reason=(
            "Owner/library: irredundantMeetDecomposition is not bound on "
            "PyBasicLattice."
        ),
    ),
    TestCaseSpec(
        id="basic_lattice_make_irredundant_join",
        method="BasicLattice.makeIrredundantJoin",
        setup=_CHAIN + """
jis = list(lat.joinIrreducibles() if hasattr(lat, 'joinIrreducibles') else lat.join_irreducibles())
""",
        call="_labs(lat.makeIrredundantJoin(jis))",
        description="makeIrredundantJoin of join-irreducibles",
        skip_string_check=True,
        xfail_reason=(
            "Owner/library: makeIrredundantJoin is not bound on PyBasicLattice."
        ),
    ),
    TestCaseSpec(
        id="basic_lattice_make_irredundant_meet",
        method="BasicLattice.makeIrredundantMeet",
        setup=_CHAIN + """
mis = list(lat.meetIrreducibles() if hasattr(lat, 'meetIrreducibles') else lat.meet_irreducibles())
""",
        call="_labs(lat.makeIrredundantMeet(mis))",
        description="makeIrredundantMeet of meet-irreducibles",
        skip_string_check=True,
        xfail_reason=(
            "Owner/library: makeIrredundantMeet is not bound on PyBasicLattice."
        ),
    ),
    TestCaseSpec(
        id="basic_lattice_con",
        method="BasicLattice.con",
        setup=_CHAIN,
        call="lat.con().cardinality() if lat.con() is not None else None",
        description="con() of a 2-chain BasicLattice",
        skip_string_check=True,
        xfail_reason=(
            "Owner/library: BasicLattice.con is not bound on PyBasicLattice. "
            "Java Con(chain2) has cardinality 2."
        ),
    ),
    TestCaseSpec(
        id="basic_lattice_sub",
        method="BasicLattice.sub",
        setup=_CHAIN,
        call="lat.sub().cardinality() if lat.sub() is not None else None",
        description="sub() of a 2-chain BasicLattice",
        skip_string_check=True,
        xfail_reason=(
            "Owner/library: BasicLattice.sub is not bound on PyBasicLattice. "
            "Java Sub(chain2) has cardinality 4."
        ),
    ),
    TestCaseSpec(
        id="ordered_set_upper_covers_via_poset",
        method="OrderedSet.getUpperCovers",
        setup=_CHAIN + """
p = lat.getPoset()
if sys.platform.startswith("java"):
    uc_vals = _labs(a0.upperCovers())
else:
    uc_vals = _labs(p.getUpperCovers(0) if hasattr(p, "getUpperCovers") else p.get_upper_covers(0))
""",
        call="uc_vals",
        description="Upper covers of 0 via poset (Java POElem, Python OrderedSet)",
        skip_string_check=True,
    ),
])
