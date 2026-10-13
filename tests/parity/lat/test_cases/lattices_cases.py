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
        xfail_reason=(
            "Java Lattices.dual throws NullPointerException (known Java bug). "
            "Python dual currently raises ValueError about Clone/reference limits."
        ),
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
        xfail_reason=(
            "Java Lattices.conToSmallLattice always returns null (OrderedSet is "
            "built then discarded). Python raises ValueError: needs a PySmallLattice wrapper."
        ),
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
        xfail_reason=(
            "Java raises NullPointerException; Python raises ValueError "
            "(requires a CongruenceLattice instance)."
        ),
    ),
]
