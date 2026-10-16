"""Test case specifications for org.uacalc.group behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.group import PermutationGroup
from org.uacalc.util import IntArray

def _arr(a):
    if a is None:
        return None
    for attr in ('getArray', 'toArray', 'to_array', 'get_array'):
        fn = getattr(a, attr, None)
        if callable(fn):
            try:
                return [int(x) for x in list(fn())]
            except TypeError:
                continue
    try:
        return [int(x) for x in list(a)]
    except TypeError:
        return str(a)

def _ia(vals):
    return IntArray([int(x) for x in list(vals)])

def _sym_name(op):
    s = op.symbol()
    fn = getattr(s, 'name', None)
    if callable(fn):
        return str(fn())
    return str(getattr(s, 'name', s))

def _op_info(op):
    arity = op.arity() if callable(getattr(op, 'arity', None)) else None
    size = None
    for attr in ('getSetSize', 'get_set_size'):
        fn = getattr(op, attr, None)
        if callable(fn):
            size = fn()
            break
    tabled = None
    for attr in ('isTableBased', 'is_table_based'):
        fn = getattr(op, attr, None)
        if callable(fn):
            tabled = fn()
            break
    table = None
    fn = getattr(op, 'getTable', None) or getattr(op, 'get_table', None)
    if callable(fn):
        try:
            table = fn()
        except TypeError:
            table = fn(False) if fn else None
    return [_sym_name(op), int(arity), int(size), bool(tabled), table]

def _close(gens):
    gens = list(gens)
    if not gens:
        return []
    n = len(_arr(gens[0]))
    ident = PermutationGroup.id(n)
    seen = []
    keys = set()
    def add(p):
        k = tuple(_arr(p))
        if k not in keys:
            keys.add(k)
            seen.append(p)
            return True
        return False
    add(ident)
    for g in gens:
        add(g)
        add(PermutationGroup.inv(g))
    changed = True
    while changed:
        changed = False
        current = list(seen)
        for a in current:
            for b in current:
                if add(PermutationGroup.prod(a, b)):
                    changed = True
    return [_arr(x) for x in seen]

def _cycle(n):
    return _ia([((i + 1) % n) for i in range(n)])

def _trans01(n):
    vals = list(range(n))
    vals[0], vals[1] = 1, 0
    return _ia(vals)

def _reflect(n):
    return _ia([((n - i) % n) for i in range(n)])

id0 = PermutationGroup.id(0)
id1 = PermutationGroup.id(1)
id2 = PermutationGroup.id(2)
id3 = PermutationGroup.id(3)
id4 = PermutationGroup.id(4)
id5 = PermutationGroup.id(5)
swap2 = _ia([1, 0])
trans3 = _ia([1, 0, 2])
cyc3 = _ia([1, 2, 0])
cyc4 = _ia([1, 2, 3, 0])
refl4 = _ia([0, 3, 2, 1])
klein_a = _ia([1, 0, 3, 2])
klein_b = _ia([2, 3, 0, 1])
s2 = PermutationGroup('S2', [swap2])
s3 = PermutationGroup('S3', [trans3, cyc3])
s3u = PermutationGroup('S3u', [trans3, cyc3], [id3, trans3, cyc3])
s1 = PermutationGroup('S1', [id1])
emptyg = PermutationGroup('Trivial', [])
named = PermutationGroup('G', [swap2])
pop6 = PermutationGroup.makeProdOp(6)
iop6 = PermutationGroup.makeInvOp(6)
dop6 = PermutationGroup.makeIdOp(6, 3)
dop0 = PermutationGroup.makeIdOp(1, 0)
"""

_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")
_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List toString vs Python list.")
_ALG = dict(skip_string_check=True, notes="Java Algebra/Group toString is Class@hex; values compared.")
_OP = dict(skip_string_check=True, notes="Java Operation toString is Class@hex; values compared.")


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
    # --- id ---
    _c("id_0", "PermutationGroup.id", "_arr(PermutationGroup.id(0))", "identity of degree 0"),
    _c("id_1", "PermutationGroup.id", "_arr(PermutationGroup.id(1))", "identity of degree 1"),
    _c("id_2", "PermutationGroup.id", "_arr(PermutationGroup.id(2))", "identity of degree 2"),
    _c("id_3", "PermutationGroup.id", "_arr(PermutationGroup.id(3))", "identity of degree 3"),
    _c("id_5", "PermutationGroup.id", "_arr(PermutationGroup.id(5))", "identity of degree 5"),
    _c("id_0_toString", "PermutationGroup.id", "PermutationGroup.id(0).toString()", "toString of empty identity"),
    _c("id_1_toString", "PermutationGroup.id", "PermutationGroup.id(1).toString()", "toString of degree-1 identity"),
    _c("id_3_toString", "PermutationGroup.id", "PermutationGroup.id(3).toString()", "toString of degree-3 identity"),
    _c("id_neg", "PermutationGroup.id", "PermutationGroup.id(-1)", "negative degree identity"),
    # --- prod ---
    _c("prod_s2_self", "PermutationGroup.prod", "_arr(PermutationGroup.prod(swap2, swap2))", "swap * swap = id in S2"),
    _c("prod_s2_id_right", "PermutationGroup.prod", "_arr(PermutationGroup.prod(swap2, id2))", "p * id = p"),
    _c("prod_s2_id_left", "PermutationGroup.prod", "_arr(PermutationGroup.prod(id2, swap2))", "id * p = p"),
    _c("prod_s3_trans_cyc", "PermutationGroup.prod", "_arr(PermutationGroup.prod(trans3, cyc3))", "S3 transposition * 3-cycle"),
    _c("prod_s3_cyc_trans", "PermutationGroup.prod", "_arr(PermutationGroup.prod(cyc3, trans3))", "S3 3-cycle * transposition (non-commutative)"),
    _c("prod_s3_cyc_cyc", "PermutationGroup.prod", "_arr(PermutationGroup.prod(cyc3, cyc3))", "3-cycle squared"),
    _c("prod_empty", "PermutationGroup.prod", "_arr(PermutationGroup.prod(id0, id0))", "product of empty permutations"),
    _c("prod_deg1", "PermutationGroup.prod", "_arr(PermutationGroup.prod(id1, id1))", "product of degree-1 identities"),
    _c("prod_toString", "PermutationGroup.prod", "PermutationGroup.prod(trans3, cyc3).toString()", "toString of a product IntArray"),
    _c("prod_assoc_left", "PermutationGroup.prod", "_arr(PermutationGroup.prod(PermutationGroup.prod(trans3, cyc3), trans3))", "associativity left"),
    _c("prod_assoc_right", "PermutationGroup.prod", "_arr(PermutationGroup.prod(trans3, PermutationGroup.prod(cyc3, trans3)))", "associativity right"),
    _c("prod_null_left", "PermutationGroup.prod", "PermutationGroup.prod(None, id2)", "prod null left"),
    _c("prod_null_right", "PermutationGroup.prod", "PermutationGroup.prod(id2, None)", "prod null right"),
    _c("prod_not_intarray", "PermutationGroup.prod", "PermutationGroup.prod(id2, 'nope')", "prod ClassCastException"),
    _c("prod_short_right", "PermutationGroup.prod", "PermutationGroup.prod(id3, swap2)", "prod right permutation shorter (AIOOBE)"),
    _c("prod_oob_image", "PermutationGroup.prod", "PermutationGroup.prod(_ia([0, 1]), _ia([2, 0]))", "prod image out of bounds"),
    # --- inv ---
    _c("inv_id2", "PermutationGroup.inv", "_arr(PermutationGroup.inv(id2))", "inverse of identity"),
    _c("inv_id0", "PermutationGroup.inv", "_arr(PermutationGroup.inv(id0))", "inverse of empty"),
    _c("inv_id1", "PermutationGroup.inv", "_arr(PermutationGroup.inv(id1))", "inverse of degree-1 identity"),
    _c("inv_swap2", "PermutationGroup.inv", "_arr(PermutationGroup.inv(swap2))", "inverse of a transposition"),
    _c("inv_cyc3", "PermutationGroup.inv", "_arr(PermutationGroup.inv(cyc3))", "inverse of a 3-cycle"),
    _c("inv_cyc4", "PermutationGroup.inv", "_arr(PermutationGroup.inv(cyc4))", "inverse of a 4-cycle"),
    _c("inv_inv_cyc3", "PermutationGroup.inv", "_arr(PermutationGroup.inv(PermutationGroup.inv(cyc3)))", "inv(inv(p)) = p"),
    _c("inv_times_p", "PermutationGroup.prod", "_arr(PermutationGroup.prod(PermutationGroup.inv(cyc3), cyc3))", "inv(p)*p = id"),
    _c("p_times_inv", "PermutationGroup.prod", "_arr(PermutationGroup.prod(cyc3, PermutationGroup.inv(cyc3)))", "p*inv(p) = id"),
    _c("inv_toString", "PermutationGroup.inv", "PermutationGroup.inv(cyc3).toString()", "toString of an inverse IntArray"),
    _c("inv_null", "PermutationGroup.inv", "PermutationGroup.inv(None)", "inv null"),
    _c("inv_not_intarray", "PermutationGroup.inv", "PermutationGroup.inv(5)", "inv ClassCastException"),
    _c("inv_oob", "PermutationGroup.inv", "PermutationGroup.inv(_ia([0, 2]))", "inv image out of bounds"),
    _c("inv_non_perm", "PermutationGroup.inv", "_arr(PermutationGroup.inv(_ia([0, 0, 1])))", "inv of a non-permutation (Java leaves a 0)"),
    # --- make*Op ---
    _c("makeProdOp_info", "PermutationGroup.makeProdOp", "_op_info(pop6)", "makeProdOp symbol/arity/setSize", **_OP),
    _c("makeInvOp_info", "PermutationGroup.makeInvOp", "_op_info(iop6)", "makeInvOp symbol/arity/setSize", **_OP),
    _c("makeIdOp_info", "PermutationGroup.makeIdOp", "_op_info(dop6)", "makeIdOp symbol/arity/setSize", **_OP),
    _c("makeProdOp_value", "AbstractOperation.valueAt", "_arr(pop6.valueAt([trans3, cyc3]))", "makeProdOp.valueAt on S3 generators"),
    _c("makeInvOp_value", "AbstractOperation.valueAt", "_arr(iop6.valueAt([cyc3]))", "makeInvOp.valueAt on a 3-cycle"),
    _c("makeIdOp_value_list", "AbstractOperation.valueAt", "_arr(dop6.valueAt([id3]))", "makeIdOp.valueAt(List) returns identity"),
    _c("makeIdOp_value_empty", "AbstractOperation.valueAt", "_arr(dop6.valueAt([]))", "Jython empty list hits valueAt(int[][]) UOE"),
    _c("makeIdOp_value_null", "AbstractOperation.valueAt", "_arr(dop6.valueAt(None))", "Jython null hits valueAt(int[][]) UOE"),
    _c("makeIdOp_deg0", "AbstractOperation.valueAt", "_arr(dop0.valueAt([]))", "makeIdOp degree 0 empty args is UOE"),
    _c("makeProdOp_intValueAt", "PermutationGroup.makeProdOp", "pop6.intValueAt([0, 1])", "intValueAt is unsupported on group ops"),
    _c("makeProdOp_short_args", "AbstractOperation.valueAt", "pop6.valueAt([trans3])", "makeProdOp.valueAt short list"),
    _c("makeProdOp_null_args", "AbstractOperation.valueAt", "pop6.valueAt(None)", "makeProdOp.valueAt null"),
    _c("makeInvOp_null_args", "AbstractOperation.valueAt", "iop6.valueAt(None)", "makeInvOp.valueAt null"),
    # --- instance GeneralAlgebra shell ---
    _c("s2_getName", "PermutationGroup.getName", "s2.getName()", "getName of S2"),
    _c("s3_getName", "PermutationGroup.getName", "s3.getName()", "getName of S3"),
    _c("s1_getName", "PermutationGroup.getName", "s1.getName()", "getName of S1"),
    _c("empty_getName", "PermutationGroup.getName", "emptyg.getName()", "getName of empty-generator group"),
    _c("s2_cardinality", "PermutationGroup.cardinality", "s2.cardinality()", "Java never closes the group: cardinality -1"),
    _c("s3_cardinality", "PermutationGroup.cardinality", "s3.cardinality()", "S3 instance cardinality is -1"),
    _c("s3u_cardinality", "PermutationGroup.cardinality", "s3u.cardinality()", "universeList does not become the algebra universe"),
    _c("s1_cardinality", "PermutationGroup.cardinality", "s1.cardinality()", "degree-1 instance cardinality -1"),
    _c("empty_cardinality", "PermutationGroup.cardinality", "emptyg.cardinality()", "empty generators cardinality -1"),
    _c("s2_universe", "PermutationGroup.universe", "s2.universe()", "universe is null", **_NONE),
    _c("s3u_universe", "PermutationGroup.universe", "s3u.universe()", "universe still null with universeList", **_NONE),
    _c("s2_operations", "PermutationGroup.operations", "s2.operations()", "operations is null", **_NONE),
    _c("s2_inputSize", "PermutationGroup.inputSize", "s2.inputSize()", "inputSize is -1 when cardinality is -1"),
    _c("s2_parent", "PermutationGroup.parent", "s2.parent()", "parent is null", **_NONE),
    _c("s2_parents", "PermutationGroup.parents", "s2.parents()", "parents is null", **_NONE),
    _c("s2_getDescription", "PermutationGroup.getDescription", "s2.getDescription()", "description starts null", **_NONE),
    _c("setName_roundtrip", "PermutationGroup.setName", "(named.setName('H') or True) and named.getName()", "setName mutates getName", **_BOOL),
    _c("s2_isTotal", "PermutationGroup.isTotal", "s2.isTotal()", "isTotal NPE on null operations"),
    _c("s2_isUnary", "PermutationGroup.isUnary", "s2.isUnary()", "isUnary NPE on null operations"),
    _c("s2_isIdempotent", "PermutationGroup.isIdempotent", "s2.isIdempotent()", "isIdempotent NPE on null operations"),
    _c("s2_iterator", "PermutationGroup.iterator", "s2.iterator()", "iterator NPE on null universe"),
    _c("s2_similarityType", "PermutationGroup.similarityType", "s2.similarityType()", "similarityType NPE on null operations"),
    _c("s2_con", "PermutationGroup.con", "s2.con()", "con is UnsupportedOperationException"),
    _c("s2_sub", "PermutationGroup.sub", "s2.sub()", "sub is UnsupportedOperationException"),
    # --- group closure from generators ---
    _c("close_empty", "PermutationGroup.prod", "_close([])", "trivial generators: nothing to close", **_LIST),
    _c("close_s1", "PermutationGroup.prod", "_close([id1])", "degree-1 group from identity", **_LIST),
    _c("close_s2", "PermutationGroup.prod", "_close([swap2])", "S2 from a transposition", **_LIST),
    _c("close_s2_sorted", "PermutationGroup.prod", "sorted(_close([swap2]))", "S2 elements sorted", **_LIST),
    _c("close_s2_card", "PermutationGroup.prod", "len(_close([swap2]))", "S2 has order 2"),
    _c("close_s3", "PermutationGroup.prod", "_close([trans3, cyc3])", "S3 listing order from transposition+cycle", **_LIST),
    _c("close_s3_sorted", "PermutationGroup.prod", "sorted(_close([trans3, cyc3]))", "S3 elements sorted", **_LIST),
    _c("close_s3_card", "PermutationGroup.prod", "len(_close([trans3, cyc3]))", "S3 has order 6"),
    _c("close_s4_card", "PermutationGroup.prod", "len(_close([_trans01(4), _cycle(4)]))", "S4 has order 24"),
    _c("close_s4_sorted_head", "PermutationGroup.prod", "sorted(_close([_trans01(4), _cycle(4)]))[:4]", "S4 first sorted elements", **_LIST),
    _c("close_c2", "PermutationGroup.prod", "_close([_cycle(2)])", "cyclic group C2", **_LIST),
    _c("close_c3", "PermutationGroup.prod", "_close([_cycle(3)])", "cyclic group C3", **_LIST),
    _c("close_c4", "PermutationGroup.prod", "_close([_cycle(4)])", "cyclic group C4", **_LIST),
    _c("close_c5", "PermutationGroup.prod", "_close([_cycle(5)])", "cyclic group C5", **_LIST),
    _c("close_c6", "PermutationGroup.prod", "_close([_cycle(6)])", "cyclic group C6", **_LIST),
    _c("close_c3_card", "PermutationGroup.prod", "len(_close([_cycle(3)]))", "C3 has order 3"),
    _c("close_c5_card", "PermutationGroup.prod", "len(_close([_cycle(5)]))", "C5 has order 5"),
    _c("close_d3_card", "PermutationGroup.prod", "len(_close([_cycle(3), _reflect(3)]))", "dihedral D3 has order 6"),
    _c("close_d4", "PermutationGroup.prod", "_close([cyc4, refl4])", "dihedral D4 listing order", **_LIST),
    _c("close_d4_card", "PermutationGroup.prod", "len(_close([cyc4, refl4]))", "dihedral D4 has order 8"),
    _c("close_d5_card", "PermutationGroup.prod", "len(_close([_cycle(5), _reflect(5)]))", "dihedral D5 has order 10"),
    _c("close_d6_card", "PermutationGroup.prod", "len(_close([_cycle(6), _reflect(6)]))", "dihedral D6 has order 12"),
    _c("close_klein", "PermutationGroup.prod", "sorted(_close([klein_a, klein_b]))", "Klein four-group", **_LIST),
    _c("close_klein_card", "PermutationGroup.prod", "len(_close([klein_a, klein_b]))", "V4 has order 4"),
    _c("close_id_only_3", "PermutationGroup.prod", "_close([id3])", "trivial generators: identity only in degree 3", **_LIST),
    _c("close_two_equal_swaps", "PermutationGroup.prod", "len(_close([swap2, swap2]))", "duplicate generators still close to S2"),
]

# Symmetric groups of several degrees: listing order + cardinality.
for _n in (2, 3, 4):
    TEST_CASES.append(
        _c(
            "close_s{0}_from_trans_cycle".format(_n),
            "PermutationGroup.prod",
            "len(_close([_trans01({0}), _cycle({0})]))".format(_n),
            "S{0} order from (0 1) and n-cycle".format(_n),
        )
    )

# Extra cyclic listing (already have C2–C6; add sorted C4).
TEST_CASES.append(
    _c(
        "close_c4_sorted",
        "PermutationGroup.prod",
        "sorted(_close([_cycle(4)]))",
        "C4 elements sorted",
        **_LIST
    )
)
