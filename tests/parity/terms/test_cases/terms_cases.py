"""Test case specifications for org.uacalc.terms behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_IMPORTS = """
from org.uacalc.terms import Terms, NonVariableTerm, VariableImp, Variable
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.io import AlgebraIO

def _map(*pairs):
    try:
        from java.util import HashMap
        m = HashMap()
        for k, v in pairs:
            m.put(k, v)
        return m
    except ImportError:
        return dict(pairs)

def _wsb(term, prefix=""):
    try:
        from java.lang import StringBuffer
        sb = StringBuffer(prefix)
        term.writeStringBuffer(sb)
        return sb.toString()
    except ImportError:
        return term.writeStringBuffer(prefix)

def _names(lst):
    if lst is None:
        return None
    out = []
    for v in list(lst):
        getter = getattr(v, "getName", None)
        if getter is not None:
            out.append(getter())
        else:
            out.append(str(v))
    return ",".join(out)

def _syms(coll):
    if coll is None:
        return None
    parts = sorted([x.name() + "/" + str(int(x.arity())) for x in list(coll)])
    return ",".join(parts)

def _vals(op, n=2):
    ar = int(op.arity())
    iva = op.intValueAt
    if ar == 0:
        return [int(iva([]))]
    if ar == 1:
        return [int(iva([i])) for i in range(n)]
    return [int(iva([i, j])) for i in range(n) for j in range(n)]

def _varlist(*vars):
    try:
        from java.util import ArrayList
        lst = ArrayList()
        for v in vars:
            lst.add(v)
        return lst
    except ImportError:
        return list(vars)

c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
plus = OperationSymbol("+", 2)
x = VariableImp("x")
y = VariableImp("y")
z = VariableImp("z")
fxy = NonVariableTerm(plus, [x, y])
const_e = NonVariableTerm.makeConstantTerm(OperationSymbol("e", 0))
"""

TEST_CASES = [
    TestCaseSpec(
        id="string_to_term_variable",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("x0")',
        description="Parse a variable term",
    ),
    TestCaseSpec(
        id="string_to_term_unary_op",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("f(x0)")',
        description="Parse a term with unary operation",
    ),
    TestCaseSpec(
        id="string_to_term_binary_op",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("f(x0,x1)")',
        description="Parse a term with a valid binary operation name",
    ),
    TestCaseSpec(
        id="string_to_term_nested",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("f(g(x0,x1))")',
        description="Parse a nested term",
    ),
    TestCaseSpec(
        id="string_to_term_round_trip",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call="str(Terms.stringToTerm(str(Terms.stringToTerm('f(g(x0,x1))'))))",
        description="Parse, stringify, parse again",
    ),
    TestCaseSpec(
        id="string_to_term_plus_invalid",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("+(x0,x1)")',
        description="'+' is not a valid Java operation name",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="string_to_term_empty",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call='Terms.stringToTerm("")',
        description="Empty string is not a term",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="string_to_term_null",
        method="Terms.stringToTerm",
        setup=_IMPORTS,
        call="Terms.stringToTerm(None)",
        description="null string is IllegalArgumentException",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="make_constant_term_c",
        method="NonVariableTerm.makeConstantTerm",
        setup=_IMPORTS,
        call='NonVariableTerm.makeConstantTerm(OperationSymbol("c", 0))',
        description="Create constant term from a nullary OperationSymbol",
    ),
    TestCaseSpec(
        id="make_constant_term_e",
        method="NonVariableTerm.makeConstantTerm",
        setup=_IMPORTS,
        call='NonVariableTerm.makeConstantTerm(OperationSymbol("e", 0))',
        description="Create constant term e()",
    ),
    TestCaseSpec(
        id="is_valid_var_string_x0",
        method="Terms.isValidVarString",
        setup=_IMPORTS,
        call='Terms.isValidVarString("x0")',
        description="x0 is a valid variable name",
        skip_string_check=True,
        notes="Java str(true) vs Python str(True).",
    ),
    TestCaseSpec(
        id="is_valid_var_string_empty",
        method="Terms.isValidVarString",
        setup=_IMPORTS,
        call='Terms.isValidVarString("")',
        description="Empty string is not a valid variable name",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="is_valid_op_name_f",
        method="Terms.isValidOpNameString",
        setup=_IMPORTS,
        call='Terms.isValidOpNameString("f")',
        description="f is a valid operation name",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="is_valid_op_name_plus",
        method="Terms.isValidOpNameString",
        setup=_IMPORTS,
        call='Terms.isValidOpNameString("+")',
        description="'+' is not a valid operation name",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="flatten_associative",
        method="Terms.flatten",
        setup=_IMPORTS
        + """
x = VariableImp("x")
fsym = OperationSymbol("f", 2, True)
inner = NonVariableTerm(fsym, [x, x])
nested = NonVariableTerm(fsym, [x, inner])
""",
        call="Terms.flatten(nested)",
        description="Flatten associative nested f(x,f(x,x)) to f(x,x,x)",
    ),
    TestCaseSpec(
        id="variable_imp_x0",
        method="VariableImp.getName",
        setup=_IMPORTS + """
v = VariableImp("x0")
""",
        call="v.getName()",
        description="VariableImp constructor and getName",
    ),
    TestCaseSpec(
        id="variable_imp_isa_variable",
        method="VariableImp.isaVariable",
        setup=_IMPORTS + """
v = VariableImp("y")
""",
        call="v.isaVariable()",
        description="VariableImp.isaVariable is true",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="non_variable_isa_variable",
        method="NonVariableTerm.isaVariable",
        setup=_IMPORTS + """
t = NonVariableTerm.makeConstantTerm(OperationSymbol("c", 0))
""",
        call="t.isaVariable()",
        description="Constant term isaVariable is false",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="variable_xyz_constants",
        method="Variable.getName",
        setup=_IMPORTS,
        call="Variable.x.getName() + ',' + Variable.y.getName() + ',' + Variable.z.getName()",
        description="Variable.x/y/z interface constants",
    ),
    TestCaseSpec(
        id="variable_leading_op_null",
        method="VariableImp.leadingOperationSymbol",
        setup=_IMPORTS,
        call="x.leadingOperationSymbol()",
        description="Variable leadingOperationSymbol is null",
    ),
    TestCaseSpec(
        id="variable_children_null",
        method="VariableImp.getChildren",
        setup=_IMPORTS,
        call="x.getChildren()",
        description="Variable getChildren is null",
    ),
    TestCaseSpec(
        id="variable_op_symbols_empty",
        method="VariableImp.getOperationSymbols",
        setup=_IMPORTS,
        call="_syms(x.getOperationSymbols())",
        description="Variable getOperationSymbols is empty",
    ),
    TestCaseSpec(
        id="variable_depth_length",
        method="VariableImp.depth",
        setup=_IMPORTS,
        call="[x.depth(), x.length()]",
        description="Variable depth 0 and length 1",
    ),
    TestCaseSpec(
        id="variable_length",
        method="VariableImp.length",
        setup=_IMPORTS,
        call="x.length()",
        description="Variable length is 1",
    ),
    TestCaseSpec(
        id="variable_hash_code",
        method="VariableImp.hashCode",
        setup=_IMPORTS,
        call='x.hashCode() == VariableImp("x").hashCode()',
        description="Equal variables have the same hashCode",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="variable_get_variable_list",
        method="VariableImp.getVariableList",
        setup=_IMPORTS,
        call="_names(x.getVariableList())",
        description="Variable getVariableList is [self]",
    ),
    TestCaseSpec(
        id="variable_int_eval",
        method="VariableImp.intEval",
        setup=_IMPORTS,
        call="x.intEval(c2, _map((x, 1)))",
        description="Evaluate variable x at 1 in cyclic2",
    ),
    TestCaseSpec(
        id="variable_eval",
        method="VariableImp.eval",
        setup=_IMPORTS,
        call="int(x.eval(c2, _map((x, 0))))",
        description="eval of a variable is the assigned value",
    ),
    TestCaseSpec(
        id="variable_int_eval_missing",
        method="VariableImp.intEval",
        setup=_IMPORTS,
        call="x.intEval(c2, _map((y, 1)))",
        description="Missing variable assignment is NPE in Java",
        expected_exception="NullPointerException",
    ),
    TestCaseSpec(
        id="variable_to_string",
        method="VariableImp.toString",
        setup=_IMPORTS,
        call="x.toString()",
        description="Variable toString is the name",
    ),
    TestCaseSpec(
        id="variable_write_string_buffer",
        method="VariableImp.writeStringBuffer",
        setup=_IMPORTS,
        call='_wsb(x, "v=")',
        description="Variable writeStringBuffer appends the name",
    ),
    TestCaseSpec(
        id="variable_equals",
        method="VariableImp.equals",
        setup=_IMPORTS,
        call='x.equals(VariableImp("x"))',
        description="Variables with the same name are equal",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="variable_substitute",
        method="VariableImp.substitute",
        setup=_IMPORTS,
        call="str(x.substitute(_map((x, y))))",
        description="Substitute y for x on a variable",
    ),
    TestCaseSpec(
        id="variable_interpretation_projection",
        method="VariableImp.interpretation",
        setup=_IMPORTS,
        call="_vals(x.interpretation(c2, _varlist(x, y), True), 2)",
        description="Variable interpretation is a projection",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="variable_interpretation_one_arg",
        method="VariableImp.interpretation",
        setup=_IMPORTS,
        call="_vals(x.interpretation(c2), 2)",
        description="One-arg interpretation uses getVariableList order",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="nvt_leading_op",
        method="NonVariableTerm.leadingOperationSymbol",
        setup=_IMPORTS,
        call="fxy.leadingOperationSymbol().name() + '/' + str(int(fxy.leadingOperationSymbol().arity()))",
        description="Compound term leading operation symbol",
    ),
    TestCaseSpec(
        id="nvt_children",
        method="NonVariableTerm.getChildren",
        setup=_IMPORTS,
        call="_names(fxy.getChildren())",
        description="+(x,y) children are x then y",
    ),
    TestCaseSpec(
        id="nvt_op_symbols",
        method="NonVariableTerm.getOperationSymbols",
        setup=_IMPORTS,
        call="_syms(fxy.getOperationSymbols())",
        description="+(x,y) operation symbols",
    ),
    TestCaseSpec(
        id="nvt_depth_length",
        method="NonVariableTerm.depth",
        setup=_IMPORTS,
        call="[fxy.depth(), fxy.length(), const_e.depth(), const_e.length()]",
        description="Compound and constant depth/length",
    ),
    TestCaseSpec(
        id="nvt_length",
        method="NonVariableTerm.length",
        setup=_IMPORTS,
        call="fxy.length()",
        description="+(x,y) length is 3",
    ),
    TestCaseSpec(
        id="nvt_get_variable_list",
        method="NonVariableTerm.getVariableList",
        setup=_IMPORTS,
        call="_names(fxy.getVariableList())",
        description="+(x,y) variable list is [x, y]",
    ),
    TestCaseSpec(
        id="nvt_int_eval_cyclic2",
        method="NonVariableTerm.intEval",
        setup=_IMPORTS,
        call="fxy.intEval(c2, _map((x, 1), (y, 1)))",
        description="Evaluate +(x,y) at (1,1) on cyclic2",
    ),
    TestCaseSpec(
        id="nvt_eval_cyclic2",
        method="NonVariableTerm.eval",
        setup=_IMPORTS,
        call="int(fxy.eval(c2, _map((x, 1), (y, 0))))",
        description="Evaluate +(x,y) at (1,0) on cyclic2",
    ),
    TestCaseSpec(
        id="nvt_interpretation_values",
        method="NonVariableTerm.interpretation",
        setup=_IMPORTS,
        call="_vals(fxy.interpretation(c2, _varlist(x, y), True), 2)",
        description="Interpretation table of +(x,y) on cyclic2",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="nvt_interpretation_use_all_false",
        method="NonVariableTerm.interpretation",
        setup=_IMPORTS,
        call="int(fxy.interpretation(c2, _varlist(x, y, z), False).arity())",
        description="useAll=false arity is the term's variables",
    ),
    TestCaseSpec(
        id="nvt_interpretation_one_arg",
        method="NonVariableTerm.interpretation",
        setup=_IMPORTS,
        call="_vals(fxy.interpretation(c2), 2)",
        description="One-arg interpretation of +(x,y) on cyclic2",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="nvt_interpretation_missing_var",
        method="NonVariableTerm.interpretation",
        setup=_IMPORTS,
        call="fxy.interpretation(c2, _varlist(x), True)",
        description="varlist missing a term variable is IAE",
        expected_exception="IllegalArgumentException",
    ),
    TestCaseSpec(
        id="nvt_substitute",
        method="NonVariableTerm.substitute",
        setup=_IMPORTS,
        call="str(fxy.substitute(_map((x, y))))",
        description="Substitute y for x in +(x,y)",
    ),
    TestCaseSpec(
        id="nvt_to_string",
        method="NonVariableTerm.toString",
        setup=_IMPORTS,
        call="fxy.toString()",
        description="Compound term toString has no spaces after commas",
    ),
    TestCaseSpec(
        id="nvt_write_string_buffer",
        method="NonVariableTerm.writeStringBuffer",
        setup=_IMPORTS,
        call='_wsb(fxy, "t=")',
        description="Compound writeStringBuffer",
    ),
    TestCaseSpec(
        id="nvt_equals",
        method="NonVariableTerm.equals",
        setup=_IMPORTS,
        call="fxy.equals(NonVariableTerm(plus, [x, y]))",
        description="Equal compound terms compare equal",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="nvt_left_par",
        method="NonVariableTerm.LEFT_PAR",
        setup=_IMPORTS,
        call="NonVariableTerm.LEFT_PAR + NonVariableTerm.RIGHT_PAR + NonVariableTerm.COMMA",
        description="NonVariableTerm parenthesis/comma constants",
    ),
    TestCaseSpec(
        id="variable_interp_missing_var",
        method="VariableImp.interpretation",
        setup=_IMPORTS,
        call="int(x.interpretation(c2, _varlist(y), True).arity())",
        description="Java still builds a projection if the variable is omitted",
        xfail_reason=(
            "Known Java bug: VariableImp.interpretation with a varlist that "
            "omits the variable still returns a projection (index -1; later "
            "AIOOBE on eval). Python raises NullPointerException at construction. "
            "Java golden values are left unchanged."
        ),
    ),
]

_TAYLOR = _IMPORTS + r"""
from org.uacalc.terms import Taylor
from org.uacalc.util import IntArray

def _ia(obj):
    if obj is None:
        return None
    for attr in ("getArray", "to_array", "get_array"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            return [int(x) for x in fn()]
    try:
        return [int(x) for x in list(obj)]
    except TypeError:
        return str(obj)

mms = Taylor.markovicMcKenzieTerm()
sig = Taylor.siggersTerm()
ia0000 = IntArray([1, 0, 0, 0])
ia0011 = IntArray([0, 0, 1, 1])
inteqs4 = [[ia0000, ia0011], [IntArray([0, 0, 1, 0]), IntArray([0, 1, 0, 0])]]
t4 = Taylor(4, inteqs4)
t_sym = Taylor(OperationSymbol("mm", 4), inteqs4)
leaf = t4.termFromArray([0, 1, 0, 1])
"""

TEST_CASES.extend([
    TestCaseSpec(
        id="taylor_mms_term",
        method="Taylor.markovicMcKenzieTerm",
        setup=_TAYLOR,
        call="mms.arity()",
        description="markovicMcKenzieTerm() factory arity 4",
    ),
    TestCaseSpec(
        id="taylor_siggers_term",
        method="Taylor.siggersTerm",
        setup=_TAYLOR,
        call="sig.arity()",
        description="siggersTerm() factory arity 6",
    ),
    TestCaseSpec(
        id="taylor_mms_arity",
        method="Taylor.arity",
        setup=_TAYLOR,
        call="[mms.arity(), sig.arity()]",
        description="Markovic-McKenzie arity 4 and Siggers arity 6",
        **dict(skip_string_check=True, notes="list vs Java toString"),
    ),
    TestCaseSpec(
        id="taylor_mms_inteqs",
        method="Taylor.inteqs",
        setup=_TAYLOR,
        call="[[_ia(ia) for ia in list(pair)] for pair in list(mms.inteqs())]",
        description="Markovic-McKenzie integer equations",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="taylor_ctor_arity",
        method="Taylor.Taylor",
        setup=_TAYLOR,
        call="t4.arity()",
        description="Taylor(int, inteqs) arity",
    ),
    TestCaseSpec(
        id="taylor_ctor_sym",
        method="Taylor.Taylor",
        setup=_TAYLOR,
        call="t_sym.arity()",
        description="Taylor(OperationSymbol, inteqs) arity",
    ),
    TestCaseSpec(
        id="taylor_ctor_term_eqs",
        method="Taylor.Taylor",
        setup=_TAYLOR,
        call="Taylor(fxy, []).arity()",
        description="Taylor(Term, eqs) uses the term's leading symbol arity",
    ),
    TestCaseSpec(
        id="taylor_term_from_array",
        method="Taylor.termFromArray",
        setup=_TAYLOR,
        call="str(leaf).replace(' ', '')",
        description="termFromArray([0,1,0,1]) for arity 4",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="taylor_term_from_array_range",
        method="Taylor.termFromArray",
        setup=_TAYLOR,
        call="str(t4.termFromArray([9, 0, 1, 0, 1, 8], 1, 4)).replace(' ', '')",
        description="termFromArray(arr, start, len) skip prefix/suffix",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="taylor_canonical_form_var",
        method="Taylor.canonicalForm",
        setup=_TAYLOR,
        call="str(mms.canonicalForm(x))",
        description="canonicalForm of a variable is the variable",
    ),
    TestCaseSpec(
        id="taylor_canonical_form_leaf",
        method="Taylor.canonicalForm",
        setup=_TAYLOR,
        call="str(t4.canonicalForm(leaf)).replace(' ', '')",
        description="canonicalForm of a balanced mm-term",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="taylor_canonical_form_intarray",
        method="Taylor.canonicalForm",
        setup=_TAYLOR,
        call="_ia(mms.canonicalForm(IntArray([1, 0, 0, 0])))",
        description="canonicalForm(IntArray) of length arity via findRoot",
        skip_string_check=True,
        xfail_reason=(
            "Known Java bug: canonicalForm(IntArray) System.arraycopy's the "
            "IntArray object instead of getArray(), raising ArrayStoreException. "
            "CPython rewrites via findRoot."
        ),
    ),
    TestCaseSpec(
        id="taylor_lex_arrays",
        method="Taylor.lexicographicallyCompare",
        setup=_TAYLOR,
        call="[Taylor.lexicographicallyCompare(IntArray([0, 1]), IntArray([1, 0])), Taylor.lexicographicallyCompare([0, 0], [0, 0])]",
        description="static lexicographicallyCompare on IntArray and int[]",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="taylor_lex_terms",
        method="Taylor.lexicographicallyCompare",
        setup=_TAYLOR,
        call="mms.lexicographicallyCompare(x, y)",
        description="instance lexicographicallyCompare(x, y) is -1",
    ),
    TestCaseSpec(
        id="taylor_lex_len_mismatch",
        method="Taylor.lexicographicallyCompare",
        setup=_TAYLOR,
        call="Taylor.lexicographicallyCompare([0, 1], [0])",
        description="lexicographicallyCompare of unequal lengths is IAE",
        expected_exception="IllegalArgumentException",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="taylor_balanced",
        method="Taylor.makeBalancedTayorTerm",
        setup=_TAYLOR,
        call="str(mms.makeBalancedTayorTerm(OperationSymbol('f', 2), 1, _varlist(x, y))).replace(' ', '')",
        description="makeBalancedTayorTerm depth 1",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="taylor_interprets_java_null",
        method="Taylor.interprets",
        setup=_TAYLOR,
        call="mms.interprets(sig, 1)",
        description="Java interprets returns null even on success; match that",
        skip_string_check=True,
        notes="Known Java bug: interprets prints then return null.",
    ),
    TestCaseSpec(
        id="taylor_equations_null",
        method="Taylor.equations",
        setup=_TAYLOR,
        call="mms.equations()",
        description="inteqs-built Taylor.equations() is null",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="taylor_npe_canonical",
        method="Taylor.canonicalForm",
        setup=_TAYLOR,
        call="mms.canonicalForm(None)",
        description="canonicalForm(null) NPE",
        expected_exception="NullPointerException",
    ),
])
