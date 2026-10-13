"""Test case specifications for org.uacalc.alg.op behavioral parity.

Covers Operation instance methods (via table-based ops), Operations static
helpers, and SimilarityType.
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.alg.op import Operations, OperationSymbol, SimilarityType
def _op(name, arity, size, table):
    make = getattr(Operations, "makeIntOperation", None)
    if make is None:
        make = Operations.make_int_operation
    return make(OperationSymbol(name, arity), size, table)
xor2 = _op("xor", 2, 2, [0, 1, 1, 0])
and2 = _op("and", 2, 2, [0, 0, 0, 1])
or2 = _op("or", 2, 2, [0, 1, 1, 1])
id1 = _op("id", 1, 2, [0, 1])
not1 = _op("not", 1, 2, [1, 0])
c0 = Operations.makeConstantIntOperation(2, 0)
proj = _op("proj", 2, 2, [0, 0, 1, 1])
add3 = _op("add", 2, 3, [0, 1, 2, 1, 2, 0, 2, 0, 1])
disc = Operations.ternaryDiscriminator(2)
join = OperationSymbol("join", 2)
meet = OperationSymbol("meet", 2)
prod = OperationSymbol("prod", 2)
inv = OperationSymbol("inv", 1)
ident = OperationSymbol("id", 0)
st = SimilarityType([join, meet])
st_unsorted = SimilarityType([prod, inv, ident], False)
st_sorted = SimilarityType([prod, inv, ident], True)
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_OP = dict(skip_string_check=True, notes="Java Operation toString is Class@hex; values compared.")
_MAP = dict(skip_string_check=True, notes="Java Map toString vs Python dict.")
_LIST = dict(skip_string_check=True, notes="Java List toString vs Python list.")

TEST_CASES = [
    # --- Operation instance methods ---
    TestCaseSpec(
        id="op_arity_xor",
        method="Operation.arity",
        setup=_SETUP,
        call="xor2.arity()",
        description="xor arity is 2",
    ),
    TestCaseSpec(
        id="op_get_set_size_xor",
        method="Operation.getSetSize",
        setup=_SETUP,
        call="xor2.getSetSize()",
        description="xor set size is 2",
    ),
    TestCaseSpec(
        id="op_symbol_xor",
        method="Operation.symbol",
        setup=_SETUP,
        call="xor2.symbol()",
        description="xor symbol name and arity",
    ),
    TestCaseSpec(
        id="op_value_at_xor",
        method="Operation.valueAt",
        setup=_SETUP,
        call="xor2.valueAt([1, 0])",
        description="valueAt(List) for xor(1,0)",
    ),
    TestCaseSpec(
        id="op_int_value_at_list",
        method="Operation.intValueAt",
        setup=_SETUP,
        call="xor2.intValueAt([1, 1])",
        description="intValueAt(int[]) for xor(1,1)",
    ),
    TestCaseSpec(
        id="op_int_value_at_horner",
        method="Operation.intValueAt",
        setup=_SETUP,
        call="xor2.intValueAt(2)",
        description="intValueAt(Horner int) for xor table index 2",
    ),
    TestCaseSpec(
        id="op_make_table",
        method="Operation.makeTable",
        setup=_SETUP,
        call="xor2.makeTable()",
        description="makeTable is void",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="op_get_table",
        method="Operation.getTable",
        setup=_SETUP,
        call="xor2.getTable()",
        description="getTable() for xor",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="op_get_table_make",
        method="Operation.getTable",
        setup=_SETUP,
        call="xor2.getTable(True)",
        description="getTable(true) for xor",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="op_is_table_based",
        method="Operation.isTableBased",
        setup=_SETUP,
        call="xor2.isTableBased()",
        description="Java IntOperationImp inherits AbstractOperation.isTableBased()=false",
        xfail_reason=(
            "owner: Java IntOperationImp does not override isTableBased, so "
            "table-constructed ops report false; Python IntOperation reports true"
        ),
        **_BOOL
    ),
    TestCaseSpec(
        id="op_is_idempotent_and",
        method="Operation.isIdempotent",
        setup=_SETUP,
        call="and2.isIdempotent()",
        description="AND is idempotent",
        **_BOOL
    ),
    TestCaseSpec(
        id="op_is_idempotent_xor",
        method="Operation.isIdempotent",
        setup=_SETUP,
        call="xor2.isIdempotent()",
        description="XOR is not idempotent",
        **_BOOL
    ),
    TestCaseSpec(
        id="op_is_associative_xor",
        method="Operation.isAssociative",
        setup=_SETUP,
        call="xor2.isAssociative()",
        description="XOR is associative",
        **_BOOL
    ),
    TestCaseSpec(
        id="op_is_associative_proj",
        method="Operation.isAssociative",
        setup=_SETUP,
        call="proj.isAssociative()",
        description="Left projection is associative",
        **_BOOL
    ),
    TestCaseSpec(
        id="op_is_commutative_xor",
        method="Operation.isCommutative",
        setup=_SETUP,
        call="xor2.isCommutative()",
        description="XOR is commutative",
        **_BOOL
    ),
    TestCaseSpec(
        id="op_is_commutative_proj",
        method="Operation.isCommutative",
        setup=_SETUP,
        call="proj.isCommutative()",
        description="Left projection is not commutative",
        **_BOOL
    ),
    TestCaseSpec(
        id="op_is_totally_symmetric_xor",
        method="Operation.isTotallySymmetric",
        setup=_SETUP,
        call="xor2.isTotallySymmetric()",
        description="XOR is totally symmetric",
        **_BOOL
    ),
    TestCaseSpec(
        id="op_is_maltsev_disc",
        method="Operation.isMaltsev",
        setup=_SETUP,
        call="disc.isMaltsev()",
        description="Ternary discriminator is Maltsev",
        **_BOOL
    ),
    TestCaseSpec(
        id="op_is_maltsev_xor",
        method="Operation.isMaltsev",
        setup=_SETUP,
        call="xor2.isMaltsev()",
        description="Binary XOR is not Maltsev",
        **_BOOL
    ),
    TestCaseSpec(
        id="op_is_total",
        method="Operation.isTotal",
        setup=_SETUP,
        call="xor2.isTotal()",
        description="Table-based ops are total",
        **_BOOL
    ),
    # --- Operations property testers ---
    TestCaseSpec(
        id="ops_commutes_id_xor",
        method="Operations.commutes",
        setup=_SETUP,
        call="Operations.commutes(id1, xor2)",
        description="Identity unary commutes with xor",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_commutes_not_xor",
        method="Operations.commutes",
        setup=_SETUP,
        call="Operations.commutes(not1, xor2)",
        description="NOT commutes with xor",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_commutes_map",
        method="Operations.commutes",
        setup=_SETUP,
        call="Operations.commutes([0, 1], xor2, xor2)",
        description="Identity map is a homomorphism of xor",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_is_total",
        method="Operations.isTotal",
        setup=_SETUP,
        call="Operations.isTotal(xor2)",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_is_idempotent",
        method="Operations.isIdempotent",
        setup=_SETUP,
        call="Operations.isIdempotent(and2)",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_is_commutative",
        method="Operations.isCommutative",
        setup=_SETUP,
        call="Operations.isCommutative(or2)",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_is_totally_symmetric",
        method="Operations.isTotallySymmetric",
        setup=_SETUP,
        call="Operations.isTotallySymmetric(and2)",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_is_associative",
        method="Operations.isAssociative",
        setup=_SETUP,
        call="Operations.isAssociative(add3)",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_is_maltsev",
        method="Operations.isMaltsev",
        setup=_SETUP,
        call="Operations.isMaltsev(disc)",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_find_difference_same",
        method="Operations.findDifference",
        setup=_SETUP,
        call="Operations.findDifference(xor2, xor2)",
        description="equal ops have no difference",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ops_find_difference_diff",
        method="Operations.findDifference",
        setup=_SETUP,
        call="list(Operations.findDifference(xor2, and2))",
        description="xor vs and first difference",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ops_find_difference_arity",
        method="Operations.findDifference",
        setup=_SETUP,
        call="Operations.findDifference(xor2, id1)",
        description="different arities raise IllegalArgumentException",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="ops_equal_values_same",
        method="Operations.equalValues",
        setup=_SETUP,
        call="Operations.equalValues(xor2, xor2)",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_equal_values_diff",
        method="Operations.equalValues",
        setup=_SETUP,
        call="Operations.equalValues(xor2, and2)",
        **_BOOL
    ),
    TestCaseSpec(
        id="ops_make_map_keys",
        method="Operations.makeMap",
        setup=_SETUP
        + """
_mm = Operations.makeMap([xor2, and2])
if hasattr(_mm, "keySet"):
    _mm_keys = sorted(str(k) for k in _mm.keySet())
else:
    _mm_keys = sorted(str(k) for k in _mm)
""",
        call="_mm_keys",
        description="makeMap keys are operation symbol names",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ops_make_int_operation_symbol",
        method="Operations.makeIntOperation",
        setup=_SETUP,
        call='Operations.makeIntOperation(OperationSymbol("f", 2), 2, [0, 1, 1, 0])',
        description="makeIntOperation(symbol, size, table)",
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_int_operation_name",
        method="Operations.makeIntOperation",
        setup=_SETUP,
        call='Operations.makeIntOperation("g", 1, 2, [1, 0])',
        description="makeIntOperation(name, arity, size, table)",
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_int_operation_from_op",
        method="Operations.makeIntOperation",
        setup=_SETUP,
        call="Operations.makeIntOperation(xor2)",
        description="makeIntOperation(Operation) table-izes",
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_int_operations",
        method="Operations.makeIntOperations",
        setup=_SETUP,
        call="[op.symbol().name() for op in Operations.makeIntOperations([xor2, and2])]",
        description="makeIntOperations preserves symbols",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ops_make_binary_int_operation",
        method="Operations.makeBinaryIntOperation",
        setup=_SETUP,
        call='Operations.makeBinaryIntOperation(OperationSymbol("b", 2), 2, [[0, 1], [1, 0]])',
        description="makeBinaryIntOperation from 2D table",
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_constant_int_operation",
        method="Operations.makeConstantIntOperation",
        setup=_SETUP,
        call="Operations.makeConstantIntOperation(3, 1)",
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_constant_int_operation_prefix",
        method="Operations.makeConstantIntOperation",
        setup=_SETUP,
        call='Operations.makeConstantIntOperation("k", 3, 2)',
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_constant_int_operations",
        method="Operations.makeConstantIntOperations",
        setup=_SETUP,
        call="[op.intValueAt([]) for op in Operations.makeConstantIntOperations(3)]",
        description="one constant op per element",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="ops_make_transposition",
        method="Operations.makeTransposition",
        setup=_SETUP,
        call="Operations.makeTransposition(3, 0, 2).intValueAt([0])",
        description="transposition swaps 0 and 2",
    ),
    TestCaseSpec(
        id="ops_make_full_cycle",
        method="Operations.makeFullCycle",
        setup=_SETUP,
        call="Operations.makeFullCycle(3).intValueAt([2])",
        description="full cycle 2 -> 0",
    ),
    TestCaseSpec(
        id="ops_ternary_discriminator",
        method="Operations.ternaryDiscriminator",
        setup=_SETUP,
        call="Operations.ternaryDiscriminator(2)",
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_random_operation_arity",
        method="Operations.makeRandomOperation",
        setup=_SETUP,
        call="Operations.makeRandomOperation(2, OperationSymbol('r', 2)).arity()",
        description="unseeded random op has requested arity",
    ),
    TestCaseSpec(
        id="ops_make_random_operations_count",
        method="Operations.makeRandomOperations",
        setup=_SETUP,
        call="len(Operations.makeRandomOperations(2, st, 1))",
        description="seeded random ops match similarity type length",
    ),
    TestCaseSpec(
        id="ops_make_derived_operation",
        method="Operations.makeDerivedOperation",
        setup=_SETUP,
        call="Operations.makeDerivedOperation(disc, [0, 1, 0], 2)",
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_jonsson_ternary",
        method="Operations.makeJonssonOperationsFromNUF",
        setup=_SETUP
        + """
nuf3 = _op("nuf", 3, 2, [0, 0, 0, 0, 0, 0, 0, 1])
""",
        call="len(Operations.makeJonssonOperationsFromNUF(nuf3))",
        description="ternary NUF yields one Jonsson operation",
    ),
    TestCaseSpec(
        id="ops_make_jonsson_binary",
        method="Operations.makeJonssonOperationsFromNUF",
        setup=_SETUP,
        call="Operations.makeJonssonOperationsFromNUF(xor2)",
        description="binary NUF: Java ArrayList(-1) IllegalArgumentException",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="ops_power",
        method="Operations.power",
        setup=_SETUP,
        call="Operations.power(2, 3)",
        description="power(2,3) == 8",
    ),
    TestCaseSpec(
        id="ops_make_left_shift",
        method="Operations.makeLeftShift",
        setup=_SETUP,
        call="Operations.makeLeftShift(2, 2)",
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_binary_left_shift",
        method="Operations.makeBinaryLeftShift",
        setup=_SETUP,
        call="Operations.makeBinaryLeftShift(2, 2)",
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_matrix_diagonal",
        method="Operations.makeMatrixDiagonalOp",
        setup=_SETUP,
        call="Operations.makeMatrixDiagonalOp(2, 2)",
        **_OP
    ),
    TestCaseSpec(
        id="ops_make_module_in_range",
        method="Operations.makeModuleOperation",
        setup=_SETUP,
        call="Operations.makeModuleOperation(3, [1, 0]).intValueAt([1, 2])",
        description="module op in-range evaluation",
    ),
    TestCaseSpec(
        id="ops_make_composition_op",
        method="Operations.makeCompositionOp",
        setup=_SETUP,
        call="Operations.makeCompositionOp(2, 4)",
        **_OP
    ),
    TestCaseSpec(
        id="ops_binary_op_to_csv",
        method="Operations.binaryOpToCSV",
        setup=_SETUP
        + r"""
import sys
if sys.platform.startswith("java"):
    from java.io import ByteArrayOutputStream, PrintStream
    _buf = ByteArrayOutputStream()
    _out = PrintStream(_buf)
    def _csv_text():
        return str(_buf.toString())
else:
    try:
        from io import StringIO
    except ImportError:
        from StringIO import StringIO
    _out = StringIO()
    def _csv_text():
        return _out.getvalue()
Operations.binaryOpToCSV("xor", xor2, _out)
""",
        call="_csv_text()",
        description="binaryOpToCSV writes Java-format CSV",
    ),
    TestCaseSpec(
        id="ops_binary_op_to_csv_unary",
        method="Operations.binaryOpToCSV",
        setup=_SETUP
        + r"""
import sys
if sys.platform.startswith("java"):
    from java.io import ByteArrayOutputStream, PrintStream
    _out = PrintStream(ByteArrayOutputStream())
else:
    try:
        from io import StringIO
    except ImportError:
        from StringIO import StringIO
    _out = StringIO()
""",
        call='Operations.binaryOpToCSV("id", id1, _out)',
        description="binaryOpToCSV rejects non-binary ops",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="ops_is_total_null",
        method="Operations.isTotal",
        setup=_SETUP,
        call="Operations.isTotal(None)",
        description="null op is not OperationWithDefaultValue, so isTotal is true",
        **_BOOL
    ),
    # --- SimilarityType ---
    TestCaseSpec(
        id="sim_to_string",
        method="SimilarityType.toString",
        setup=_SETUP,
        call="str(st)",
        description="SimilarityType toString is (join, meet)",
    ),
    TestCaseSpec(
        id="sim_get_operation_symbols",
        method="SimilarityType.getOperationSymbols",
        setup=_SETUP,
        call="[str(s) for s in st.getOperationSymbols()]",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="sim_get_sorted_operation_symbols",
        method="SimilarityType.getSortedOperationSymbols",
        setup=_SETUP,
        call="[str(s) for s in st_unsorted.getSortedOperationSymbols()]",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="sim_input_size",
        method="SimilarityType.inputSize",
        setup=_SETUP,
        call="st.inputSize(3)",
        description="lattice type input size for |A|=3 is 9+9=18",
    ),
    TestCaseSpec(
        id="sim_input_size_empty",
        method="SimilarityType.inputSize",
        setup=_SETUP,
        call="SimilarityType([]).inputSize(5)",
        description="no operations: inputSize is algebra size",
    ),
    TestCaseSpec(
        id="sim_get_arities_map",
        method="SimilarityType.getAritiesMap",
        setup=_SETUP
        + """
_am = st.getAritiesMap()
_am_items = []
if hasattr(_am, "entrySet"):
    for _e in _am.entrySet():
        _am_items.append([int(_e.getKey()), int(_e.getValue())])
else:
    for _k in _am:
        _am_items.append([int(_k), int(_am[_k])])
_am_items = sorted(_am_items)
""",
        call="_am_items",
        description="two binary ops",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="sim_get_max_arity",
        method="SimilarityType.getMaxArity",
        setup=_SETUP,
        call="st.getMaxArity()",
    ),
    TestCaseSpec(
        id="sim_arities_string",
        method="SimilarityType.aritiesString",
        setup=_SETUP,
        call="st.aritiesString()",
    ),
    TestCaseSpec(
        id="sim_equals",
        method="SimilarityType.equals",
        setup=_SETUP,
        call="st.equals(SimilarityType([meet, join]))",
        description="equals ignores order",
        **_BOOL
    ),
    TestCaseSpec(
        id="sim_lattice_constant",
        method="SimilarityType.LATTICE_SIMILARITY_TYPE",
        setup=_SETUP,
        call="str(SimilarityType.LATTICE_SIMILARITY_TYPE)",
        description="LATTICE_SIMILARITY_TYPE toString",
    ),
    TestCaseSpec(
        id="sim_group_constant",
        method="SimilarityType.GROUP_SIMILARITY_TYPE",
        setup=_SETUP,
        call="str(SimilarityType.GROUP_SIMILARITY_TYPE)",
        description="GROUP_SIMILARITY_TYPE toString",
    ),
    TestCaseSpec(
        id="sim_constructor_sort",
        method="SimilarityType",
        setup=_SETUP,
        call="str(st_sorted)",
        description="constructor with sort=True",
    ),
    TestCaseSpec(
        id="op_symbol_hash_code_join",
        method="OperationSymbol.hashCode",
        setup=_SETUP,
        call="join.hashCode()",
        description="Java OperationSymbol.hashCode is name.hashCode()+arity",
    ),
    TestCaseSpec(
        id="op_symbol_compare_to",
        method="OperationSymbol.compareTo",
        setup=_SETUP,
        call="prod.compareTo(inv)",
        description="compareTo: higher arity first (prod vs inv)",
    ),
    TestCaseSpec(
        id="sim_value_roundtrip",
        method="SimilarityType",
        setup=_SETUP
        + r"""
_payload = []
for _s in st.getOperationSymbols():
    _nm = _s.name() if callable(getattr(_s, "name", None)) else _s.name
    _ar = _s.arity() if callable(getattr(_s, "arity", None)) else _s.arity
    _payload.append([str(_nm), int(_ar)])
_st_rt = SimilarityType([OperationSymbol(_n, _a) for _n, _a in _payload])

def _java_hash(obj):
    hc = getattr(obj, "hashCode", None)
    if callable(hc):
        try:
            return int(hc())
        except TypeError:
            pass
    h = 1
    for _s in obj.getOperationSymbols():
        shc = getattr(_s, "hashCode", None)
        eh = int(shc()) if callable(shc) else 0
        h = 31 * h + eh
        h = ((h + (1 << 31)) % (1 << 32)) - (1 << 31)
    return int(h)

def _cmp_sym(a, b):
    ct = getattr(a, "compareTo", None)
    if callable(ct):
        return int(ct(b))
    if a < b:
        return -1
    if a > b:
        return 1
    return 0

_sorted_a = list(st.getSortedOperationSymbols())
_sorted_b = list(_st_rt.getSortedOperationSymbols())
_rt = {
    "equals": bool(st.equals(_st_rt)),
    "equals_rev": bool(_st_rt.equals(st)),
    "toString": str(st),
    "toString_rt": str(_st_rt),
    "hashCode": _java_hash(st),
    "hashCode_rt": _java_hash(_st_rt),
    "symbols": _payload,
    "sorted_compare": [_cmp_sym(a, b) for a, b in zip(_sorted_a, _sorted_b)],
    "similar": bool(st.equals(_st_rt) and str(st) == str(_st_rt)),
}
""",
        call="_rt",
        description="Round-trip SimilarityType via symbol name/arity: equals, hashCode, toString, compareTo",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="op_int_value_at_null",
        method="Operation.intValueAt",
        setup=_SETUP,
        call="xor2.intValueAt(None)",
        description="intValueAt(null) is NPE",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="op_value_at_null",
        method="Operation.valueAt",
        setup=_SETUP,
        call="xor2.valueAt(None)",
        description="valueAt(null) hits valueAt(int[][]) UnsupportedOperationException",
        expected_exception="UnsupportedOperationException",
    ),
    TestCaseSpec(
        id="op_int_value_at_bad_string",
        method="Operation.intValueAt",
        setup=_SETUP,
        call="xor2.intValueAt('bad')",
        description="intValueAt(non-int sequence) is TypeError",
        expected_exception="TypeError",
    ),
    TestCaseSpec(
        id="ops_make_int_operation_coerce",
        method="Operations.makeIntOperation",
        setup=_SETUP,
        call="Operations.makeIntOperation(1)",
        description="makeIntOperation(int) TypeError on coerce",
        expected_exception="TypeError",
    ),
    TestCaseSpec(
        id="ops_make_int_operations_class_cast",
        method="Operations.makeIntOperations",
        setup=_SETUP,
        call="Operations.makeIntOperations([1])",
        description="makeIntOperations([int]) ClassCastException",
        expected_exception="ClassCastException",
    ),
    TestCaseSpec(
        id="ops_is_idempotent_null",
        method="Operations.isIdempotent",
        setup=_SETUP,
        call="Operations.isIdempotent(None)",
        description="isIdempotent(null) is NPE",
        expected_exception="NullPointerException",
    ),
]
