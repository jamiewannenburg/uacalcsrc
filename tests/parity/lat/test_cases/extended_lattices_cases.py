"""Wider org.uacalc.lat behavioral cases: more lattices, Con/Sub, factories."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_WIDE = r"""
import sys
from org.uacalc.alg.op import Operations, OperationSymbol
from org.uacalc.io import AlgebraIO
from org.uacalc.lat import Lattices, OrderedSets, BasicLattice, Order
from org.uacalc.alg import ProductAlgebra

def _make_int_op(name, arity, size, table):
    make = getattr(Operations, "makeIntOperation", None)
    if make is None:
        make = Operations.make_int_operation
    return make(OperationSymbol(name, arity), size, table)

def _chain_join(n):
    table = []
    for i in range(n):
        for j in range(n):
            table.append(i if i > j else j)
    return _make_int_op("v", 2, n, table)

def _chain_meet(n):
    table = []
    for i in range(n):
        for j in range(n):
            table.append(i if i < j else j)
    return _make_int_op("meet", 2, n, table)

def _bool_or(n):
    size = 1 << n
    table = []
    for i in range(size):
        for j in range(size):
            table.append(i | j)
    return _make_int_op("v", 2, size, table)

def _bool_and(n):
    size = 1 << n
    table = []
    for i in range(size):
        for j in range(size):
            table.append(i & j)
    return _make_int_op("meet", 2, size, table)

def _prod_max(n, m):
    size = n * m
    table = []
    for a in range(size):
        for b in range(size):
            ai, aj = a // m, a % m
            bi, bj = b // m, b % m
            ci = ai if ai > bi else bi
            cj = aj if aj > bj else bj
            table.append(ci * m + cj)
    return _make_int_op("v", 2, size, table)

def _labs(xs):
    if xs is None:
        return None
    out = []
    for x in list(xs):
        try:
            out.append(int(str(x)))
        except Exception:
            out.append(str(x))
    out.sort()
    return out

def _lab(x):
    if x is None:
        return None
    try:
        return int(str(x))
    except Exception:
        return str(x)

def _elt(lat, k):
    n = int(lat.cardinality())
    for i in range(n):
        e = lat.getElement(i)
        try:
            if int(str(e)) == k:
                return e
        except Exception:
            pass
    if not sys.platform.startswith("java"):
        return k
    return lat.getElement(k)

def _jlist(xs):
    if sys.platform.startswith("java"):
        try:
            from java.util import ArrayList
            out = ArrayList()
            for x in xs:
                out.add(x)
            return out
        except Exception:
            return list(xs)
    return list(xs)

def _op(alg, name):
    return alg.getOperation(OperationSymbol(name, 2))

def _jis(lat):
    fn = getattr(lat, "joinIrreducibles", None) or lat.join_irreducibles
    return list(fn())

def _mis(lat):
    fn = getattr(lat, "meetIrreducibles", None) or lat.meet_irreducibles
    return list(fn())

c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
n5alg = AlgebraIO.readAlgebraFile("resources/algebras/n5.ua")
m3alg = AlgebraIO.readAlgebraFile("resources/algebras/m3.ua")
ba2 = AlgebraIO.readAlgebraFile("resources/algebras/ba2.ua")

chain3 = Lattices.latticeFromJoin("chain3", _chain_join(3))
chain4 = Lattices.latticeFromJoin("chain4", _chain_join(4))
chain5 = Lattices.latticeFromJoin("chain5", _chain_join(5))
chain3m = Lattices.latticeFromMeet("chain3m", _chain_meet(3))
n5 = Lattices.latticeFromJoin("N5", _op(n5alg, "join"))
m3 = Lattices.latticeFromJoin("M3real", _op(m3alg, "join"))
bool2 = Lattices.latticeFromJoin("B2", _bool_or(2))
bool3 = Lattices.latticeFromJoin("B3", _bool_or(3))
bool3m = Lattices.latticeFromMeet("B3m", _bool_and(3))
prod23 = Lattices.latticeFromJoin("C2xC3", _prod_max(2, 3))
prod = ProductAlgebra("C2xC2", [lat2, lat2])
prod_join = _op(prod, "join")
prod_lat = Lattices.latticeFromJoin("C2xC2", prod_join)

# Join semilattice with top but no bottom: Java adds -1.
join_no_bot = _make_int_op("v", 2, 3, [0, 2, 2, 2, 1, 2, 2, 2, 2])
lat_no_bot = Lattices.latticeFromJoin("nobot", join_no_bot)
bad_meet = _make_int_op("meet", 2, 2, [0, 0, 1, 0])

c3_bot = _elt(chain3, 0)
c3_mid = _elt(chain3, 1)
c3_top = _elt(chain3, 2)
n5_bot = _elt(n5, 0)
n5_top = _elt(n5, 4)
n5_a = _elt(n5, 1)
m3_bot = _elt(m3, 0)
m3_top = _elt(m3, 4)
b2_bot = _elt(bool2, 0)
b2_top = _elt(bool2, 3)
b3_bot = _elt(bool3, 0)
b3_top = _elt(bool3, 7)
"""

TEST_CASES = [
    TestCaseSpec(
        id="lattice_from_join_chain3_card",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call="chain3.cardinality()",
        description="3-chain from join table has cardinality 3",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_chain4_card",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call="chain4.cardinality()",
        description="4-chain from join table has cardinality 4",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_chain5_card",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call="chain5.cardinality()",
        description="5-chain from join table has cardinality 5",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_meet_chain3_card",
        method="Lattices.latticeFromMeet",
        setup=_WIDE,
        call="chain3m.cardinality()",
        description="3-chain from meet table has cardinality 3",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_n5_card",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call="n5.cardinality()",
        description="N5 from n5.ua join table has cardinality 5",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_m3_card",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call="m3.cardinality()",
        description="M3 from m3.ua join table has cardinality 5",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_bool2_card",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call="bool2.cardinality()",
        description="Boolean 2^2 (bitwise OR) has cardinality 4",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_bool3_card",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call="bool3.cardinality()",
        description="Boolean 2^3 (bitwise OR) has cardinality 8",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_meet_bool3_card",
        method="Lattices.latticeFromMeet",
        setup=_WIDE,
        call="bool3m.cardinality()",
        description="Boolean 2^3 from meet (bitwise AND) has cardinality 8",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_prod_c2c3_card",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call="prod23.cardinality()",
        description="C2 x C3 product join table has cardinality 6",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_prod_lat2xlat2_card",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call="prod_lat.cardinality()",
        description="latticeFromJoin of ProductAlgebra(lat2, lat2).join has cardinality 4",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_chain3_with_universe",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call='Lattices.latticeFromJoin("c3u", [0, 1, 2], _chain_join(3)).cardinality()',
        description="latticeFromJoin(name, universe, join) on a 3-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_meet_chain3_with_universe",
        method="Lattices.latticeFromMeet",
        setup=_WIDE,
        call='Lattices.latticeFromMeet("c3mu", [0, 1, 2], _chain_meet(3)).cardinality()',
        description="latticeFromMeet(name, universe, meet) on a 3-chain",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_join_adds_bottom",
        method="Lattices.latticeFromJoin",
        setup=_WIDE,
        call="lat_no_bot.cardinality()",
        description="Join with no zero: Java adds a bottom, cardinality 4",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="lattice_from_meet_not_ordered",
        method="Lattices.latticeFromMeet",
        setup=_WIDE,
        call='Lattices.latticeFromMeet("badm", bad_meet)',
        description="Non-lattice meet table: Java catches NonOrderedSetException and returns null",
        skip_string_check=True,
    ),
]

def _struct(lat_var, prefix, method, call, desc):
    return TestCaseSpec(
        id=prefix,
        method=method,
        setup=_WIDE,
        call=call,
        description=desc,
        skip_string_check=True,
    )


TEST_CASES.extend([
    _struct("chain3_zero", "chain3_zero", "BasicLattice.zero",
            "_lab(chain3.zero())", "Bottom of the 3-chain"),
    _struct("chain3_one", "chain3_one", "BasicLattice.one",
            "_lab(chain3.one())", "Top of the 3-chain"),
    _struct("chain3_atoms", "chain3_atoms", "BasicLattice.atoms",
            "_labs(chain3.atoms())", "Atoms of the 3-chain"),
    _struct("chain3_coatoms", "chain3_coatoms", "BasicLattice.coatoms",
            "_labs(chain3.coatoms())", "Coatoms of the 3-chain"),
    _struct("chain3_jis", "chain3_jis", "BasicLattice.joinIrreducibles",
            "_labs(_jis(chain3))", "Join-irreducibles of the 3-chain"),
    _struct("chain3_mis", "chain3_mis", "BasicLattice.meetIrreducibles",
            "_labs(_mis(chain3))", "Meet-irreducibles of the 3-chain"),
    _struct("chain3_filter_bot", "chain3_filter_bot", "BasicLattice.filter",
            "_labs(chain3.filter(c3_bot))", "Filter of 0 in the 3-chain"),
    _struct("chain3_filter_mid", "chain3_filter_mid", "BasicLattice.filter",
            "_labs(chain3.filter(c3_mid))", "Filter of 1 in the 3-chain"),
    _struct("chain3_ideal_top", "chain3_ideal_top", "BasicLattice.ideal",
            "_labs(chain3.ideal(c3_top))", "Ideal of 2 in the 3-chain"),
    _struct("chain3_ideal_mid", "chain3_ideal_mid", "BasicLattice.ideal",
            "_labs(chain3.ideal(c3_mid))", "Ideal of 1 in the 3-chain"),
    _struct("chain3_upper_covers_bot", "chain3_upper_covers_bot", "BasicLattice.upperCovers",
            "_labs(chain3.upperCovers(c3_bot))", "Upper covers of 0 in the 3-chain"),
    _struct("chain3_upper_covers_mid", "chain3_upper_covers_mid", "BasicLattice.upperCovers",
            "_labs(chain3.upperCovers(c3_mid))", "Upper covers of 1 in the 3-chain"),
    _struct("chain3_lower_covers_top", "chain3_lower_covers_top", "BasicLattice.lowerCovers",
            "_labs(chain3.lowerCovers(c3_top))", "Lower covers of 2 in the 3-chain"),
    _struct("chain3_leq_mid_top", "chain3_leq_mid_top", "BasicLattice.leq",
            "chain3.leq(c3_mid, c3_top)", "1 <= 2 in the 3-chain"),
    _struct("chain3_leq_top_mid", "chain3_leq_top_mid", "BasicLattice.leq",
            "chain3.leq(c3_top, c3_mid)", "2 <= 1 is false in the 3-chain"),
    _struct("chain3_join_list", "chain3_join_list", "BasicLattice.join",
            "_lab(chain3.join(_jlist([c3_bot, c3_mid, c3_top])))",
            "join([0,1,2]) is 2 in the 3-chain"),
    _struct("chain3_meet_list", "chain3_meet_list", "BasicLattice.meet",
            "_lab(chain3.meet(_jlist([c3_bot, c3_mid, c3_top])))",
            "meet([0,1,2]) is 0 in the 3-chain"),
    _struct("chain3_join_irreds_below_top", "chain3_join_irreds_below_top",
            "BasicLattice.joinIrredsBelow",
            "_labs(chain3.joinIrredsBelow(c3_top))",
            "joinIrredsBelow(2) in the 3-chain"),
    _struct("chain3_meet_irreds_above_bot", "chain3_meet_irreds_above_bot",
            "BasicLattice.meetIrredsAbove",
            "_labs(chain3.meetIrredsAbove(c3_bot))",
            "meetIrredsAbove(0) in the 3-chain"),
    _struct("chain3_find_join_irred", "chain3_find_join_irred",
            "BasicLattice.findJoinIrred",
            "_lab(chain3.findJoinIrred(c3_top, c3_mid))",
            "findJoinIrred(2, 1) in the 3-chain"),
    _struct("chain3_find_meet_irred", "chain3_find_meet_irred",
            "BasicLattice.findMeetIrred",
            "_lab(chain3.findMeetIrred(c3_bot, c3_mid))",
            "findMeetIrred(0, 1) in the 3-chain"),
    _struct("chain3_irred_join_decomp", "chain3_irred_join_decomp",
            "BasicLattice.irredundantJoinDecomposition",
            "_labs(chain3.irredundantJoinDecomposition(c3_top))",
            "irredundantJoinDecomposition of 2 in the 3-chain"),
    _struct("chain3_irred_meet_decomp", "chain3_irred_meet_decomp",
            "BasicLattice.irredundantMeetDecomposition",
            "_labs(chain3.irredundantMeetDecomposition(c3_bot))",
            "irredundantMeetDecomposition of 0 in the 3-chain"),
    _struct("chain3_con_card", "chain3_con_card", "BasicLattice.con",
            "chain3.con().cardinality()", "con() of the 3-chain"),
    _struct("chain3_sub_card", "chain3_sub_card", "BasicLattice.sub",
            "chain3.sub().cardinality()", "sub() of the 3-chain"),
    _struct("chain5_jis", "chain5_jis", "BasicLattice.joinIrreducibles",
            "_labs(_jis(chain5))", "Join-irreducibles of the 5-chain"),
    _struct("chain5_atoms", "chain5_atoms", "BasicLattice.atoms",
            "_labs(chain5.atoms())", "Atoms of the 5-chain"),
    _struct("chain5_join_list", "chain5_join_list", "BasicLattice.join",
            "_lab(chain5.join(_jlist([_elt(chain5, 0), _elt(chain5, 2), _elt(chain5, 4)])))",
            "join([0,2,4]) is 4 in the 5-chain"),
    _struct("n5_atoms", "n5_atoms", "BasicLattice.atoms",
            "_labs(n5.atoms())", "Atoms of N5"),
    _struct("n5_coatoms", "n5_coatoms", "BasicLattice.coatoms",
            "_labs(n5.coatoms())", "Coatoms of N5"),
    _struct("n5_jis", "n5_jis", "BasicLattice.joinIrreducibles",
            "_labs(_jis(n5))", "Join-irreducibles of N5"),
    _struct("n5_mis", "n5_mis", "BasicLattice.meetIrreducibles",
            "_labs(_mis(n5))", "Meet-irreducibles of N5"),
    _struct("n5_filter_a", "n5_filter_a", "BasicLattice.filter",
            "_labs(n5.filter(n5_a))", "Filter of element 1 in N5"),
    _struct("n5_ideal_a", "n5_ideal_a", "BasicLattice.ideal",
            "_labs(n5.ideal(n5_a))", "Ideal of element 1 in N5"),
    _struct("n5_upper_covers_bot", "n5_upper_covers_bot", "BasicLattice.upperCovers",
            "_labs(n5.upperCovers(n5_bot))", "Upper covers of 0 in N5"),
    _struct("n5_lower_covers_top", "n5_lower_covers_top", "BasicLattice.lowerCovers",
            "_labs(n5.lowerCovers(n5_top))", "Lower covers of 4 in N5"),
    _struct("n5_join_list", "n5_join_list", "BasicLattice.join",
            "_lab(n5.join(_jlist([n5_bot, n5_a, n5_top])))",
            "join([0,1,4]) in N5"),
    _struct("n5_meet_list", "n5_meet_list", "BasicLattice.meet",
            "_lab(n5.meet(_jlist([n5_bot, n5_a, n5_top])))",
            "meet([0,1,4]) in N5"),
    _struct("n5_leq_a_top", "n5_leq_a_top", "BasicLattice.leq",
            "n5.leq(n5_a, n5_top)", "1 <= 4 in N5"),
    _struct("n5_find_join_irred", "n5_find_join_irred", "BasicLattice.findJoinIrred",
            "_lab(n5.findJoinIrred(n5_top, n5_bot))",
            "findJoinIrred(top, bottom) in N5"),
    _struct("n5_irred_join_decomp", "n5_irred_join_decomp",
            "BasicLattice.irredundantJoinDecomposition",
            "_labs(n5.irredundantJoinDecomposition(n5_top))",
            "irredundantJoinDecomposition of top in N5"),
    _struct("n5_con_card", "n5_con_card", "BasicLattice.con",
            "n5.con().cardinality()", "con() of N5 as a BasicLattice"),
    _struct("n5_sub_card", "n5_sub_card", "BasicLattice.sub",
            "n5.sub().cardinality()", "sub() of N5 as a BasicLattice"),
    _struct("m3_atoms", "m3_atoms", "BasicLattice.atoms",
            "_labs(m3.atoms())", "Atoms of M3 (5-element diamond)"),
    _struct("m3_coatoms", "m3_coatoms", "BasicLattice.coatoms",
            "_labs(m3.coatoms())", "Coatoms of M3"),
    _struct("m3_jis", "m3_jis", "BasicLattice.joinIrreducibles",
            "_labs(_jis(m3))", "Join-irreducibles of M3"),
    _struct("m3_mis", "m3_mis", "BasicLattice.meetIrreducibles",
            "_labs(_mis(m3))", "Meet-irreducibles of M3"),
    _struct("m3_filter_bot", "m3_filter_bot", "BasicLattice.filter",
            "_labs(m3.filter(m3_bot))", "Filter of bottom in M3"),
    _struct("m3_ideal_top", "m3_ideal_top", "BasicLattice.ideal",
            "_labs(m3.ideal(m3_top))", "Ideal of top in M3"),
    _struct("m3_upper_covers_bot", "m3_upper_covers_bot", "BasicLattice.upperCovers",
            "_labs(m3.upperCovers(m3_bot))", "Upper covers of bottom in M3"),
    _struct("m3_join_list", "m3_join_list", "BasicLattice.join",
            "_lab(m3.join(_jlist([_elt(m3, 1), _elt(m3, 2), _elt(m3, 3)])))",
            "join of the three atoms in M3 is top"),
    _struct("m3_irred_join_decomp", "m3_irred_join_decomp",
            "BasicLattice.irredundantJoinDecomposition",
            "_labs(m3.irredundantJoinDecomposition(m3_top))",
            "irredundantJoinDecomposition of top in M3"),
    _struct("m3_con_card", "m3_con_card", "BasicLattice.con",
            "m3.con().cardinality()", "con() of M3 as a BasicLattice"),
    _struct("m3_sub_card", "m3_sub_card", "BasicLattice.sub",
            "m3.sub().cardinality()", "sub() of M3 as a BasicLattice"),
    _struct("bool2_atoms", "bool2_atoms", "BasicLattice.atoms",
            "_labs(bool2.atoms())", "Atoms of Boolean 2^2"),
    _struct("bool2_jis", "bool2_jis", "BasicLattice.joinIrreducibles",
            "_labs(_jis(bool2))", "Join-irreducibles of Boolean 2^2"),
    _struct("bool2_join_atoms", "bool2_join_atoms", "BasicLattice.join",
            "_lab(bool2.join(_jlist([_elt(bool2, 1), _elt(bool2, 2)])))",
            "join of the two atoms in Boolean 2^2 is top"),
    _struct("bool3_atoms", "bool3_atoms", "BasicLattice.atoms",
            "_labs(bool3.atoms())", "Atoms of Boolean 2^3"),
    _struct("bool3_coatoms", "bool3_coatoms", "BasicLattice.coatoms",
            "_labs(bool3.coatoms())", "Coatoms of Boolean 2^3"),
    _struct("bool3_jis", "bool3_jis", "BasicLattice.joinIrreducibles",
            "_labs(_jis(bool3))", "Join-irreducibles of Boolean 2^3"),
    _struct("bool3_mis", "bool3_mis", "BasicLattice.meetIrreducibles",
            "_labs(_mis(bool3))", "Meet-irreducibles of Boolean 2^3"),
    _struct("bool3_filter_bot", "bool3_filter_bot", "BasicLattice.filter",
            "_labs(bool3.filter(b3_bot))", "Filter of 0 in Boolean 2^3"),
    _struct("bool3_ideal_top", "bool3_ideal_top", "BasicLattice.ideal",
            "_labs(bool3.ideal(b3_top))", "Ideal of 7 in Boolean 2^3"),
    _struct("bool3_upper_covers_bot", "bool3_upper_covers_bot", "BasicLattice.upperCovers",
            "_labs(bool3.upperCovers(b3_bot))", "Upper covers of 0 in Boolean 2^3"),
    _struct("bool3_join_list", "bool3_join_list", "BasicLattice.join",
            "_lab(bool3.join(_jlist([_elt(bool3, 1), _elt(bool3, 2), _elt(bool3, 4)])))",
            "join of the three atoms in Boolean 2^3 is top"),
    _struct("bool3_meet_list", "bool3_meet_list", "BasicLattice.meet",
            "_lab(bool3.meet(_jlist([_elt(bool3, 3), _elt(bool3, 5), _elt(bool3, 6)])))",
            "meet of the three coatoms in Boolean 2^3 is bottom"),
    _struct("bool3_irred_join_decomp", "bool3_irred_join_decomp",
            "BasicLattice.irredundantJoinDecomposition",
            "_labs(bool3.irredundantJoinDecomposition(b3_top))",
            "irredundantJoinDecomposition of top in Boolean 2^3"),
    _struct("bool3_con_card", "bool3_con_card", "BasicLattice.con",
            "bool3.con().cardinality()", "con() of Boolean 2^3 as a BasicLattice"),
    _struct("prod23_atoms", "prod23_atoms", "BasicLattice.atoms",
            "_labs(prod23.atoms())", "Atoms of C2 x C3"),
    _struct("prod23_jis", "prod23_jis", "BasicLattice.joinIrreducibles",
            "_labs(_jis(prod23))", "Join-irreducibles of C2 x C3"),
    _struct("prod23_filter_bot", "prod23_filter_bot", "BasicLattice.filter",
            "_labs(prod23.filter(_elt(prod23, 0)))", "Filter of bottom in C2 x C3"),
    _struct("prod23_upper_covers_bot", "prod23_upper_covers_bot", "BasicLattice.upperCovers",
            "_labs(prod23.upperCovers(_elt(prod23, 0)))", "Upper covers of bottom in C2 x C3"),
    _struct("prod_lat_atoms", "prod_lat_atoms", "BasicLattice.atoms",
            "_labs(prod_lat.atoms())", "Atoms of ProductAlgebra(lat2,lat2) as a lattice"),
    _struct("prod_lat_jis", "prod_lat_jis", "BasicLattice.joinIrreducibles",
            "_labs(_jis(prod_lat))", "Join-irreducibles of lat2 x lat2"),
    _struct("prod_lat_card", "prod_lat_card", "BasicLattice.cardinality",
            "prod_lat.cardinality()", "Cardinality of lat2 x lat2 lattice"),
])

_CON_SUB = _WIDE + """
def _con_lat(alg, name):
    return BasicLattice(name, alg.con(), False)

def _sub_lat(alg, name):
    return BasicLattice(name, alg.sub())

def _jis_len(lat):
    return len(_jis(lat))

con_c2 = _con_lat(c2, "ConC2")
con_c3 = _con_lat(c3, "ConC3")
con_lat2 = _con_lat(lat2, "ConLat2")
con_n5 = _con_lat(n5alg, "ConN5")
con_m3 = _con_lat(m3alg, "ConM3")
con_ba2 = _con_lat(ba2, "ConBa2")
sub_c2 = _sub_lat(c2, "SubC2")
sub_c3 = _sub_lat(c3, "SubC3")
sub_lat2 = _sub_lat(lat2, "SubLat2")
sub_ba2 = _sub_lat(ba2, "SubBa2")
"""

TEST_CASES.extend([
    TestCaseSpec(
        id="basic_from_con_c2_card",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="con_c2.cardinality()",
        description="BasicLattice from Con(C2) cardinality",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_con_c2_jis",
        method="BasicLattice.joinIrreducibles",
        setup=_CON_SUB,
        call="_jis_len(con_c2)",
        description="BasicLattice from Con(C2) join-irreducible count",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_con_c3_card",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="con_c3.cardinality()",
        description="BasicLattice from Con(C3) cardinality",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_con_c3_jis",
        method="BasicLattice.joinIrreducibles",
        setup=_CON_SUB,
        call="_jis_len(con_c3)",
        description="BasicLattice from Con(C3) join-irreducible count",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_con_lat2_card",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="con_lat2.cardinality()",
        description="BasicLattice from Con(lat2) cardinality",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_con_n5_card",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="con_n5.cardinality()",
        description="BasicLattice from Con(N5) cardinality",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_con_n5_jis",
        method="BasicLattice.joinIrreducibles",
        setup=_CON_SUB,
        call="_jis_len(con_n5)",
        description="BasicLattice from Con(N5) join-irreducible count",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_con_m3_card",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="con_m3.cardinality()",
        description="BasicLattice from Con(M3) cardinality",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_con_m3_jis",
        method="BasicLattice.joinIrreducibles",
        setup=_CON_SUB,
        call="_jis_len(con_m3)",
        description="BasicLattice from Con(M3) join-irreducible count",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_con_ba2_card",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="con_ba2.cardinality()",
        description="BasicLattice from Con(ba2) cardinality",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_sub_c2_card",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="sub_c2.cardinality()",
        description="BasicLattice from Sub(C2) via Lattice constructor",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_sub_c3_card",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="sub_c3.cardinality()",
        description="BasicLattice from Sub(C3) via Lattice constructor",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_sub_lat2_card",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="sub_lat2.cardinality()",
        description="BasicLattice from Sub(lat2) via Lattice constructor",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="basic_from_sub_ba2_card",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="sub_ba2.cardinality()",
        description="BasicLattice from Sub(ba2) via Lattice constructor",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="con_get_basic_lattice_c3",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="c3.con().getBasicLattice().cardinality()",
        description="Con(C3).getBasicLattice() cardinality",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="sub_get_basic_lattice_c2",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="c2.sub().getBasicLattice().cardinality()",
        description="Sub(C2).getBasicLattice() cardinality",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="con_get_basic_lattice_n5",
        method="BasicLattice.cardinality",
        setup=_CON_SUB,
        call="n5alg.con().getBasicLattice().cardinality()",
        description="Con(N5).getBasicLattice() cardinality",
        skip_string_check=True,
    ),
])

_ORDER = r"""
from org.uacalc.lat import Order, OrderedSets
class _Div(Order):
    def leq(self, a, b):
        if a == 0:
            return True
        if b == 0:
            return a == 0
        return (b % a) == 0
class _Nat(Order):
    def leq(self, a, b):
        return a <= b
class _Rev(Order):
    def leq(self, a, b):
        return a >= b
class _Len(Order):
    def leq(self, a, b):
        return len(list(a)) <= len(list(b))
div_order = _Div()
nat_order = _Nat()
rev_order = _Rev()
len_order = _Len()
"""

TEST_CASES.extend([
    TestCaseSpec(
        id="order_leq_equal",
        method="Order.leq",
        setup=_ORDER,
        call="nat_order.leq(5, 5)",
        description="Natural Order.leq is reflexive",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="order_leq_reverse",
        method="Order.leq",
        setup=_ORDER,
        call="rev_order.leq(9, 3)",
        description="Reverse integer Order.leq(9, 3)",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="order_leq_div_false",
        method="Order.leq",
        setup=_ORDER,
        call="div_order.leq(4, 6)",
        description="4 does not divide 6",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ordered_sets_maximals_null_elems",
        method="OrderedSets.maximals",
        setup=_ORDER,
        call="OrderedSets.maximals(None, nat_order)",
        description="maximals(null, order) NPEs on the collection",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="ordered_sets_maximals_singleton",
        method="OrderedSets.maximals",
        setup=_ORDER,
        call="list(OrderedSets.maximals([7], nat_order))",
        description="maximals of a singleton",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ordered_sets_maximals_duplicates",
        method="OrderedSets.maximals",
        setup=_ORDER,
        call="list(OrderedSets.maximals([2, 2, 4], div_order))",
        description="maximals with duplicate elements under divisibility",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ordered_sets_maximals_reverse",
        method="OrderedSets.maximals",
        setup=_ORDER,
        call="list(OrderedSets.maximals([1, 4, 2, 8], rev_order))",
        description="maximals under reverse integer order",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ordered_sets_maximals_by_length",
        method="OrderedSets.maximals",
        setup=_ORDER,
        call="list(OrderedSets.maximals([[1], [1, 2], [9, 8, 7], [0, 0]], len_order))",
        description="maximals of lists ordered by length",
        skip_string_check=True,
    ),
])
