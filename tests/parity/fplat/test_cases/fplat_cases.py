"""Test case specifications for org.uacalc.fplat behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.fplat import PartiallyDefinedLattice
from org.uacalc.lat import Order
from org.uacalc.terms import VariableImp

def _name(v):
    if v is None:
        return v.getName()
    fn = getattr(v, 'getName', None) or getattr(v, 'get_name', None)
    if callable(fn):
        return str(fn())
    return str(v)

def _names(lst):
    if lst is None:
        return None
    out = []
    for group in lst:
        if group is None:
            out.append(None)
        else:
            out.append([_name(v) for v in list(group)])
    return out

def _field(obj, java_name, getter=None):
    if getter:
        fn = getattr(obj, getter, None)
        if callable(fn):
            return fn()
    if hasattr(obj, java_name):
        return getattr(obj, java_name)
    try:
        f = obj.getClass().getDeclaredField(java_name)
        f.setAccessible(True)
        return f.get(obj)
    except Exception:
        return None

def _in_groups(groups, names):
    got = _names(groups)
    if got is None:
        return False
    return list(names) in got

class NameOrder(Order):
    def leq(self, a, b):
        return _name(a) <= _name(b)

class AntiOrder(Order):
    def leq(self, a, b):
        return _name(a) == _name(b)

class ChainXYZ(Order):
    _rank = {'x': 0, 'y': 1, 'z': 2}
    def leq(self, a, b):
        return self._rank[_name(a)] <= self._rank[_name(b)]

class VeeOrder(Order):
    # a,b < c; a incomparable to b
    def leq(self, a, b):
        na, nb = _name(a), _name(b)
        if na == nb:
            return True
        if nb == 'c' and na in ('a', 'b'):
            return True
        return False

x = VariableImp('x')
y = VariableImp('y')
z = VariableImp('z')
a = VariableImp('a')
b = VariableImp('b')
c = VariableImp('c')
w = VariableImp('w')
nat = NameOrder()
anti = AntiOrder()
chain = ChainXYZ()
vee = VeeOrder()
empty_lat = PartiallyDefinedLattice('empty', nat, [], [])
named = PartiallyDefinedLattice('T', nat, [[x, y]], [[y, z]])
multi = PartiallyDefinedLattice('M', nat, [[x, y], [z, w]], [[x, z], [y, w]])
chain_lat = PartiallyDefinedLattice('C', chain, [[x, y], [y, z]], [[x, y]])
vee_lat = PartiallyDefinedLattice('V', vee, [[a, b]], [[a, c], [b, c]])
anti_lat = PartiallyDefinedLattice('A', anti, [], [])
null_order = PartiallyDefinedLattice('N', None, [], [])
null_lists = PartiallyDefinedLattice('NL', nat, None, None)
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_STR = dict(skip_string_check=True, notes="Java Object.toString is Class@hex.")
_NPE = dict(skip_string_check=True, notes="NPE message text differs; type matches.")
_ATTR = dict(skip_string_check=True, notes="Jython Order subclass: None.getName is AttributeError.")


def _c(cid, method, call, description, **kw):
    return TestCaseSpec(
        id=cid,
        method=method,
        setup=_SETUP,
        call=call,
        description=description,
        **kw
    )


TEST_CASES = [
    # --- leq via several orders ---
    _c("leq_name_x_y", "PartiallyDefinedLattice.leq", "named.leq(x, y)", "name order: x <= y", **_BOOL),
    _c("leq_name_y_x", "PartiallyDefinedLattice.leq", "named.leq(y, x)", "name order: y <= x is false", **_BOOL),
    _c("leq_name_x_x", "PartiallyDefinedLattice.leq", "named.leq(x, x)", "name order is reflexive", **_BOOL),
    _c("leq_name_a_c", "PartiallyDefinedLattice.leq", "empty_lat.leq(a, c)", "name order: a <= c", **_BOOL),
    _c("leq_name_c_a", "PartiallyDefinedLattice.leq", "empty_lat.leq(c, a)", "name order: c <= a is false", **_BOOL),
    _c("leq_chain_x_z", "PartiallyDefinedLattice.leq", "chain_lat.leq(x, z)", "custom chain x < y < z", **_BOOL),
    _c("leq_chain_z_x", "PartiallyDefinedLattice.leq", "chain_lat.leq(z, x)", "custom chain z not <= x", **_BOOL),
    _c("leq_chain_y_y", "PartiallyDefinedLattice.leq", "chain_lat.leq(y, y)", "custom chain reflexive", **_BOOL),
    _c("leq_anti_x_y", "PartiallyDefinedLattice.leq", "anti_lat.leq(x, y)", "antichain: distinct vars incomparable", **_BOOL),
    _c("leq_anti_x_x", "PartiallyDefinedLattice.leq", "anti_lat.leq(x, x)", "antichain is reflexive", **_BOOL),
    _c("leq_vee_a_c", "PartiallyDefinedLattice.leq", "vee_lat.leq(a, c)", "vee order: a <= c", **_BOOL),
    _c("leq_vee_b_c", "PartiallyDefinedLattice.leq", "vee_lat.leq(b, c)", "vee order: b <= c", **_BOOL),
    _c("leq_vee_a_b", "PartiallyDefinedLattice.leq", "vee_lat.leq(a, b)", "vee order: a incomparable to b", **_BOOL),
    _c("leq_vee_c_a", "PartiallyDefinedLattice.leq", "vee_lat.leq(c, a)", "vee order: c not <= a", **_BOOL),
    _c("leq_independent_of_joins", "PartiallyDefinedLattice.leq", "multi.leq(z, x)", "stored joins do not affect leq", **_BOOL),
    # --- join/meet lists where defined ---
    _c("joins_empty", "PartiallyDefinedLattice.getDefinedJoins", "_names(_field(empty_lat, 'definedJoins', 'getDefinedJoins'))", "empty defined joins"),
    _c("meets_empty", "PartiallyDefinedLattice.getDefinedMeets", "_names(_field(empty_lat, 'definedMeets', 'getDefinedMeets'))", "empty defined meets"),
    _c("joins_named", "PartiallyDefinedLattice.getDefinedJoins", "_names(_field(named, 'definedJoins', 'getDefinedJoins'))", "one defined join [x,y]"),
    _c("meets_named", "PartiallyDefinedLattice.getDefinedMeets", "_names(_field(named, 'definedMeets', 'getDefinedMeets'))", "one defined meet [y,z]"),
    _c("joins_multi", "PartiallyDefinedLattice.getDefinedJoins", "_names(_field(multi, 'definedJoins', 'getDefinedJoins'))", "two defined joins"),
    _c("meets_multi", "PartiallyDefinedLattice.getDefinedMeets", "_names(_field(multi, 'definedMeets', 'getDefinedMeets'))", "two defined meets"),
    _c("join_xy_defined", "PartiallyDefinedLattice.getDefinedJoins", "_in_groups(_field(named, 'definedJoins', 'getDefinedJoins'), ['x', 'y'])", "join x,y is defined", **_BOOL),
    _c("join_xz_not_defined", "PartiallyDefinedLattice.getDefinedJoins", "_in_groups(_field(named, 'definedJoins', 'getDefinedJoins'), ['x', 'z'])", "join x,z is not defined", **_BOOL),
    _c("meet_yz_defined", "PartiallyDefinedLattice.getDefinedMeets", "_in_groups(_field(named, 'definedMeets', 'getDefinedMeets'), ['y', 'z'])", "meet y,z is defined", **_BOOL),
    _c("meet_xy_not_defined", "PartiallyDefinedLattice.getDefinedMeets", "_in_groups(_field(named, 'definedMeets', 'getDefinedMeets'), ['x', 'y'])", "meet x,y is not defined", **_BOOL),
    _c("joins_null_lists", "PartiallyDefinedLattice.getDefinedJoins", "_field(null_lists, 'definedJoins', 'getDefinedJoins')", "null joins list is stored as null"),
    _c("meets_null_lists", "PartiallyDefinedLattice.getDefinedMeets", "_field(null_lists, 'definedMeets', 'getDefinedMeets')", "null meets list is stored as null"),
    _c("joins_chain", "PartiallyDefinedLattice.getDefinedJoins", "_names(_field(chain_lat, 'definedJoins', 'getDefinedJoins'))", "chain joins [x,y] and [y,z]"),
    _c("meets_vee", "PartiallyDefinedLattice.getDefinedMeets", "_names(_field(vee_lat, 'definedMeets', 'getDefinedMeets'))", "vee meets [a,c] and [b,c]"),
    # --- toString ---
    _c("toString_named", "PartiallyDefinedLattice.toString", "len(named.toString()) > 0", "toString is non-empty (Java Class@hex)", **_BOOL),
    _c("toString_empty", "PartiallyDefinedLattice.toString", "len(empty_lat.toString()) > 0", "toString of empty lattice is non-empty", **_BOOL),
    # --- edge cases ---
    _c("leq_null_order", "PartiallyDefinedLattice.leq", "null_order.leq(x, y)", "leq with null order NPEs", **_NPE),
    _c("leq_null_left", "PartiallyDefinedLattice.leq", "named.leq(None, y)", "leq null left: Order.getName on None", **_ATTR),
    _c("leq_null_right", "PartiallyDefinedLattice.leq", "named.leq(x, None)", "leq null right: Order.getName on None", **_ATTR),
    _c("ctor_empty_name", "PartiallyDefinedLattice.leq", "PartiallyDefinedLattice('', nat, [], []).leq(x, x)", "empty name still constructs", **_BOOL),
    _c("ctor_single_var_join", "PartiallyDefinedLattice.getDefinedJoins", "_names(_field(PartiallyDefinedLattice('S', nat, [[x]], [[y]]), 'definedJoins', 'getDefinedJoins'))", "single-variable join list"),
    _c("ctor_three_var_join", "PartiallyDefinedLattice.getDefinedJoins", "_names(_field(PartiallyDefinedLattice('S3', nat, [[x, y, z]], []), 'definedJoins', 'getDefinedJoins'))", "three-variable join list"),
]
