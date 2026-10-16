"""Golden parity cases for leftover org.uacalc.alg.op types."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.alg.op import (
    AbstractIntOperation, OperationSymbol, OperationWithDefaultValue,
    Operations, ParameterizedOperation, TermOperationImp,
)
from org.uacalc.io import AlgebraIO
from org.uacalc.terms import NonVariableTerm, VariableImp
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
plus2 = OperationSymbol("+", 2)
join2 = OperationSymbol("join", 2)
x = VariableImp("x")
y = VariableImp("y")

def _varlist(*vars):
    try:
        from java.util import ArrayList
        lst = ArrayList()
        for v in vars:
            lst.add(v)
        return lst
    except ImportError:
        return list(vars)

term_c2 = NonVariableTerm(plus2, _varlist(x, y))
term_lat = NonVariableTerm(join2, _varlist(x, y))
toi_c2 = TermOperationImp(term_c2, _varlist(x, y), c2)
toi_c3 = TermOperationImp(term_c2, _varlist(x, y), c3)
toi_lat = TermOperationImp(term_lat, _varlist(x, y), lat2)
toi_named = TermOperationImp("plusTerm", term_c2, _varlist(x, y), c2)
aio_sym = AbstractIntOperation(OperationSymbol("*", 2), 3)
aio_name = AbstractIntOperation("f", 1, 4)

def _set_parm(obj, name, value):
    try:
        f = obj.getClass().getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, value)
        return
    except Exception:
        pass
    setattr(obj, name, value)

parm = ParameterizedOperation()
_set_parm(parm, "symbolName", "m")
_set_parm(parm, "arityExp", "2")
_set_parm(parm, "setSizeExp", "3")
_set_parm(parm, "definitionExp", "x")
ow_def = OperationWithDefaultValue(OperationSymbol("f", 2), 2, 7)
ow_name = OperationWithDefaultValue("h", 2, 3, -1)
xor = Operations.makeIntOperation(OperationSymbol("xor", 2), 2, [0, 1, 1, 0])
ow_xor = OperationWithDefaultValue(xor)
ow_tab = OperationWithDefaultValue("g", 2, 2, [-1, 0, 1, 1], 5)

class PlusOp(AbstractIntOperation):
    def intValueAt(self, args):
        return (int(args[0]) + int(args[1])) % self.getSetSize()
plus_op = PlusOp("plus", 2, 3)

def _vars(lst):
    return [str(v) for v in list(lst)]

def _tab(op):
    t = op.getTable()
    if t is None:
        return None
    return [int(x) for x in list(t)]
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List/Set toString vs Python list.")
_OP = dict(skip_string_check=True, notes="Java Operation toString is Class@hex; values compared.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")

TEST_CASES = [
    TestCaseSpec(
        id="aio_sym_size",
        method="AbstractIntOperation.getSetSize",
        setup=_SETUP,
        call="aio_sym.getSetSize()",
        description="AbstractIntOperation(symbol, size) getSetSize",
    ),
    TestCaseSpec(
        id="aio_name_arity",
        method="AbstractIntOperation.arity",
        setup=_SETUP,
        call="[aio_name.getSetSize(), aio_name.arity()]",
        description="AbstractIntOperation(name, arity, size)",
        **_LIST
    ),
    TestCaseSpec(
        id="aio_value_at_uoe",
        method="AbstractIntOperation.valueAt",
        setup=_SETUP,
        call="aio_sym.valueAt([0, 1])",
        description="valueAt is UOE",
        expected_exception="UnsupportedOperationException",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="aio_int_value_at_uoe",
        method="AbstractIntOperation.intValueAt",
        setup=_SETUP,
        call="aio_sym.intValueAt([0, 1])",
        description="intValueAt is UOE unless subclassed",
        expected_exception="UnsupportedOperationException",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="aio_subclass_iva",
        method="AbstractIntOperation.intValueAt",
        setup=_SETUP,
        call="plus_op.intValueAt([1, 2])",
        description="subclass intValueAt plus mod 3",
    ),
    TestCaseSpec(
        id="toi_c2_term",
        method="TermOperation.getTerm",
        setup=_SETUP,
        call="str(toi_c2.getTerm()).replace(' ', '')",
        description="TermOperationImp getTerm on cyclic2 +",
    ),
    TestCaseSpec(
        id="toi_c2_vars",
        method="TermOperation.getOrderedVariables",
        setup=_SETUP,
        call="_vars(toi_c2.getOrderedVariables())",
        description="getOrderedVariables [x, y]",
        **_LIST
    ),
    TestCaseSpec(
        id="toi_c2_iva",
        method="TermOperationImp.intValueAt",
        setup=_SETUP,
        call="[toi_c2.intValueAt([0,0]), toi_c2.intValueAt([0,1]), toi_c2.intValueAt([1,0]), toi_c2.intValueAt([1,1])]",
        description="cyclic2 + table via TermOperationImp",
        **_LIST
    ),
    TestCaseSpec(
        id="toi_c2_value_at",
        method="TermOperationImp.valueAt",
        setup=_SETUP,
        call="toi_c2.valueAt([1, 1])",
        description="valueAt(List) is the Java interpretation stub (null)",
        **_NONE
    ),
    TestCaseSpec(
        id="toi_get_table_npe",
        method="TermOperationImp.getTable",
        setup=_SETUP,
        call="toi_c2.getTable()",
        description="getTable() NPEs until interpretation makeTable (Java stub)",
        expected_exception="NullPointerException",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="toi_get_table_true",
        method="TermOperationImp.getTable",
        setup=_SETUP,
        call="[int(x) for x in list(toi_c2.getTable(True))]",
        description="getTable(True) builds the + table on cyclic2",
        **_LIST
    ),
    TestCaseSpec(
        id="toi_c2_str",
        method="TermOperationImp.toString",
        setup=_SETUP,
        call="toi_c2.toString().replace(' ', '')",
        description="toString is the term",
    ),
    TestCaseSpec(
        id="toi_c3_iva",
        method="TermOperationImp.intValueAt",
        setup=_SETUP,
        call="[toi_c3.intValueAt([1,2]), toi_c3.intValueAt([2,2])]",
        description="cyclic3 + via TermOperationImp",
        **_LIST
    ),
    TestCaseSpec(
        id="toi_lat_iva",
        method="TermOperationImp.intValueAt",
        setup=_SETUP,
        call="[toi_lat.intValueAt([0,1]), toi_lat.intValueAt([1,1])]",
        description="lat2 join via TermOperationImp",
        **_LIST
    ),
    TestCaseSpec(
        id="toi_named_term",
        method="TermOperationImp.getTerm",
        setup=_SETUP,
        call="str(toi_named.getTerm()).replace(' ', '')",
        description="named TermOperationImp still exposes the term",
    ),
    TestCaseSpec(
        id="parm_sub",
        method="ParameterizedOperation.subParmValues",
        setup=_SETUP,
        call="ParameterizedOperation.subParmValues('n+1', {'n': '3'})",
        description="subParmValues is identity",
    ),
    TestCaseSpec(
        id="parm_make_op",
        method="ParameterizedOperation.makeOp",
        setup=_SETUP,
        call="parm.makeOp({'n': '1'}).intValueAt([1, 2])",
        description="makeOp intValueAt is Math.max",
        **_OP
    ),
    TestCaseSpec(
        id="ow_default_value",
        method="OperationWithDefaultValue.getDefaultValue",
        setup=_SETUP,
        call="ow_def.getDefaultValue()",
        description="default value 7",
    ),
    TestCaseSpec(
        id="ow_set_size",
        method="OperationWithDefaultValue.getSetSize",
        setup=_SETUP,
        call="ow_def.getSetSize()",
        description="OWDV getSetSize",
    ),
    TestCaseSpec(
        id="ow_is_total_filled",
        method="OperationWithDefaultValue.isTotal",
        setup=_SETUP,
        call="ow_def.isTotal()",
        description="defaultValue>=0 is total",
        **_BOOL
    ),
    TestCaseSpec(
        id="ow_iva_default",
        method="OperationWithDefaultValue.intValueAt",
        setup=_SETUP,
        call="ow_def.intValueAt([0, 1])",
        description="undefined cell returns default 7",
    ),
    TestCaseSpec(
        id="ow_value_at",
        method="OperationWithDefaultValue.valueAt",
        setup=_SETUP,
        call="int(ow_def.valueAt([1, 0]))",
        description="valueAt uses default",
    ),
    TestCaseSpec(
        id="ow_get_table",
        method="OperationWithDefaultValue.getTable",
        setup=_SETUP,
        call="_tab(ow_def)",
        description="partial table is all -1",
        **_LIST
    ),
    TestCaseSpec(
        id="ow_set_default",
        method="OperationWithDefaultValue.setDefaultValue",
        setup=_SETUP,
        call="(ow_def.setDefaultValue(1), ow_def.getDefaultValue(), ow_def.getTotalTable())[1:]",
        description="setDefaultValue then getTotalTable",
        **_LIST
    ),
    TestCaseSpec(
        id="ow_ordinary",
        method="OperationWithDefaultValue.makeOrdinaryOperation",
        setup=_SETUP,
        call="ow_def.makeOrdinaryOperation().intValueAt([0, 0])",
        description="makeOrdinaryOperation fills default",
        **_OP
    ),
    TestCaseSpec(
        id="ow_xor_iva",
        method="OperationWithDefaultValue.intValueAt",
        setup=_SETUP,
        call="[ow_xor.intValueAt([0,0]), ow_xor.intValueAt([1,0]), ow_xor.isTotal()]",
        description="OWDV wrapping xor table",
        **_LIST
    ),
    TestCaseSpec(
        id="ow_make_ordinary_list",
        method="OperationWithDefaultValue.makeOrdinary",
        setup=_SETUP,
        call="len(OperationWithDefaultValue.makeOrdinary([ow_xor]))",
        description="makeOrdinary Java duplicate-append bug, len 2",
    ),
    TestCaseSpec(
        id="ow_table_ctor",
        method="OperationWithDefaultValue.intValueAt",
        setup=_SETUP,
        call="[ow_tab.intValueAt([0,0]), ow_tab.intValueAt([1,0]), _tab(ow_tab)]",
        description="table ctor uses default 5 at -1 cells",
        **_LIST
    ),
    TestCaseSpec(
        id="ow_idempotent",
        method="OperationWithDefaultValue.setIdempotent",
        setup=_SETUP,
        call="(ow_name.setIdempotent(True), ow_name.isIdempotentSet(), _tab(ow_name)[0])[1:]",
        description="setIdempotent fills diagonal",
        **_LIST
    ),
    TestCaseSpec(
        id="ow_is_diagonal",
        method="OperationWithDefaultValue.isDiagonal",
        setup=_SETUP,
        call="ow_name.isDiagonal(0, 0)",
        description="isDiagonal(0,0) for binary",
        **_BOOL
    ),
    TestCaseSpec(
        id="ow_random_xfail",
        method="OperationWithDefaultValue.getRandomValueTable",
        setup=_SETUP,
        call="OperationWithDefaultValue(OperationSymbol('r', 2), 4, -2).getRandomValueTable()",
        description="defaultValue==-2 random table is not deterministic",
        xfail_reason="Java RandomGenerator (UI) vs Python random; defaultValue==-2 tables are not comparable",
        **_LIST
    ),
]
