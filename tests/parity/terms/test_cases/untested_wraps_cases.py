"""Parity cases for wrapped org.uacalc.terms constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.terms import NonVariableTerm, VariableImp
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
        out.append(getter() if getter is not None else str(v))
    return ",".join(out)

def _syms(coll):
    if coll is None:
        return None
    parts = sorted([x.name() + "/" + str(int(x.arity())) for x in list(coll)])
    return ",".join(parts)

def _varlist(*vars):
    try:
        from java.util import ArrayList
        lst = ArrayList()
        for v in vars:
            lst.add(v)
        return lst
    except ImportError:
        return list(vars)

plus = OperationSymbol("+", 2)
x = VariableImp("x")
y = VariableImp("y")
fxy = NonVariableTerm(plus, _varlist(x, y))
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
"""

_SKIP = dict(skip_string_check=True)
_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")


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
    _c("ctor_variable_imp", "VariableImp.VariableImp",
       "x.getName()", "VariableImp constructor"),
    _c("ctor_variable_imp_y", "VariableImp.VariableImp",
       "y.getName()", "VariableImp('y') constructor"),
    _c("ctor_non_variable_term", "NonVariableTerm.NonVariableTerm",
       "str(fxy).replace(' ', '')", "NonVariableTerm constructor"),
    _c("inh_term_depth", "Term.depth", "int(fxy.depth())", "Term depth on compound term"),
    _c("inh_term_eval", "Term.eval",
       "int(fxy.eval(c2, _map((x, 1), (y, 0))))", "Term eval on cyclic2"),
    _c("inh_term_children", "Term.getChildren",
       "len(list(fxy.getChildren()))", "Term getChildren"),
    _c("inh_term_op_syms", "Term.getOperationSymbols",
       "_syms(fxy.getOperationSymbols())", "Term getOperationSymbols", **_SKIP),
    _c("inh_term_var_list", "Term.getVariableList",
       "_names(fxy.getVariableList())", "Term getVariableList"),
    _c("inh_term_int_eval", "Term.intEval",
       "int(fxy.intEval(c2, _map((x, 1), (y, 1))))", "Term intEval"),
    _c("inh_term_interp", "Term.interpretation",
       "int(fxy.interpretation(c2).arity())", "Term interpretation"),
    _c("inh_term_is_var", "Term.isaVariable", "x.isaVariable()", "Term isaVariable on variable", **_BOOL),
    _c("inh_term_lead", "Term.leadingOperationSymbol",
       "fxy.leadingOperationSymbol().name()", "Term leadingOperationSymbol"),
    _c("inh_term_length", "Term.length", "int(fxy.length())", "Term length"),
    _c("inh_term_substitute", "Term.substitute",
       "str(fxy.substitute(_map((x, y))))", "Term substitute"),
    _c("inh_term_tostr", "Term.toString", "fxy.toString()", "Term toString", **_SKIP),
    _c("inh_term_wsb", "Term.writeStringBuffer", "_wsb(fxy, 't=')", "Term writeStringBuffer"),
    _c("inh_nvt_hash", "NonVariableTerm.hashCode",
       "fxy.hashCode()", "NonVariableTerm hashCode",
       xfail_reason="Wrapper bug: NonVariableTerm.hashCode differs from Java on the same term tree"),
]