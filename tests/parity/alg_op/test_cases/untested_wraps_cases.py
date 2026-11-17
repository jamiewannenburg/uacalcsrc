"""Parity cases for wrapped org.uacalc.alg.op methods/constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.alg.op import (
    AbstractIntOperation, AbstractOperation, OperationSymbol,
    OperationWithDefaultValue, Operations, TermOperationImp,
)
from org.uacalc.io import AlgebraIO
from org.uacalc.terms import NonVariableTerm, VariableImp
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
plus = OperationSymbol("+", 2)
unary = OperationSymbol("u", 1)
xor = Operations.makeIntOperation(OperationSymbol("xor", 2), 2, [0, 1, 1, 0])
ow_def = OperationWithDefaultValue(OperationSymbol("f", 2), 2, 7)
ow_name = OperationWithDefaultValue("h", 2, 3, -1)
ow_tab = OperationWithDefaultValue("g", 2, 2, [-1, 0, 1, 1], 5)
aio_sym = AbstractIntOperation(OperationSymbol("*", 2), 3)
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

toi_c2 = TermOperationImp(NonVariableTerm(plus, _varlist(x, y)), _varlist(x, y), c2)

def _tab(op):
    t = op.getTable()
    if t is None:
        return None
    return [int(v) for v in list(t)]
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java array/List toString vs Python list.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")


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
    _c("ctor_aio", "AbstractIntOperation.AbstractIntOperation",
       "aio_sym.getSetSize()", "AbstractIntOperation constructor"),
    _c("ctor_os", "OperationSymbol.OperationSymbol",
       "plus.arity()", "OperationSymbol constructor arity"),
    _c("ctor_owdv", "OperationWithDefaultValue.OperationWithDefaultValue",
       "ow_def.getDefaultValue()", "OperationWithDefaultValue constructor"),
    _c("ctor_toi", "TermOperationImp.TermOperationImp",
       "toi_c2.intValueAt([0, 1])", "TermOperationImp constructor"),
    _c("ctor_ao_via_xor", "AbstractOperation.AbstractOperation",
       "xor.arity()", "table operation is an AbstractOperation"),
    _c("os_name_plus", "OperationSymbol.name", "plus.name()", "binary plus name"),
    _c("os_name_unary", "OperationSymbol.name", "unary.name()", "unary name"),
    _c("os_name_join", "OperationSymbol.name",
       "OperationSymbol('join', 2).name()", "join symbol name"),
    _c("ow_is_idempotent_set_default", "OperationWithDefaultValue.isIdempotentSet",
       "ow_name.isIdempotentSet()", "isIdempotentSet default is false", **_BOOL),
    _c("ow_is_idempotent_set_after", "OperationWithDefaultValue.isIdempotentSet",
       "(ow_name.setIdempotent(True), ow_name.isIdempotentSet())[1]",
       "isIdempotentSet after setIdempotent(True)", **_BOOL),
    _c("ow_make_idempotent", "OperationWithDefaultValue.makeIdempotent",
       "(ow_name.makeIdempotent(), _tab(ow_name)[0], _tab(ow_name)[4], _tab(ow_name)[8])[1:]",
       "makeIdempotent fills the diagonal of size 3", **_LIST),
    _c("ow_make_idempotent_size2", "OperationWithDefaultValue.makeIdempotent",
       "(ow_tab.makeIdempotent(), _tab(ow_tab)[0], _tab(ow_tab)[3])[1:]",
       "makeIdempotent fills the diagonal of size 2", **_LIST),
    _c("ow_get_total_table_default", "OperationWithDefaultValue.getTotalTable",
       "list(ow_def.getTotalTable())", "getTotalTable fills default 7", **_LIST),
    _c("ow_get_total_table_partial", "OperationWithDefaultValue.getTotalTable",
       "list(ow_tab.getTotalTable())", "getTotalTable fills default 5 at -1 cells", **_LIST),
    _c("ow_get_total_table_after_set", "OperationWithDefaultValue.getTotalTable",
       "(ow_def.setDefaultValue(1), list(ow_def.getTotalTable()))[1]",
       "getTotalTable after setDefaultValue(1)", **_LIST),
    _c("ow_update_random_len", "OperationWithDefaultValue.updateRandomValueTable",
       "(ow_def.updateRandomValueTable(), len(list(ow_def.getRandomValueTable())))[1]",
       "updateRandomValueTable length is algSize**arity"),
    _c("ow_update_random_len_size3", "OperationWithDefaultValue.updateRandomValueTable",
       "(ow_name.updateRandomValueTable(), len(list(ow_name.getRandomValueTable())))[1]",
       "updateRandomValueTable length for size 3 binary"),
]
