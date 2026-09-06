# coding: utf-8
# Dual-runtime parity script for ReductAlgebra (Java/Jython source of truth).
#
# Known CPython / uacalc_lib gaps (do not hide; backend should match Java):
# - PyO3 constructor only accepts strings and wraps each as VariableImp
#   (uacalc_lib/src/alg/reduct_algebra.rs). Java ReductAlgebra(alg, List<Term>)
#   calls term.interpretation(alg) for every *non-variable* Term.
# - org shim _terms_to_names stringifies Terms before the binding sees them,
#   so a real +(x,y) becomes a variable named "+(x,y)" and is skipped as an
#   operation — both sides then look like the empty/variable-term case.
# - super_algebra() always raises (placeholder); Java superAlgebra() returns
#   the original SmallAlgebra.
# - No operations() on the binding (only operations_count); getOperation walks
#   operations() the way GeneralAlgebra does.
# - Terms.stringToTerm cannot parse cyclic2's "+" (Java requires a leading
#   letter); the non-variable term is built with NonVariableTerm + the
#   algebra's OperationSymbol.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import ReductAlgebra
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.terms import Terms, NonVariableTerm, Variable


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def _as_list(obj):
    if obj is None:
        return []
    try:
        return list(obj)
    except TypeError:
        pass
    n = getattr(obj, "length", None)
    if n is not None and not callable(n):
        return [obj[i] for i in range(int(n))]
    return [obj]


def _first(seq):
    items = _as_list(seq)
    if not items:
        return None
    return items[0]


def _op_symbol_of(alg):
    op0 = _first(alg.operations())
    return op0.symbol()


def _is_var(term):
    for attr in ("isaVariable", "isa_variable"):
        fn = getattr(term, attr, None)
        if callable(fn):
            return bool(fn())
    return None


def _nops(alg):
    return str(len(_as_list(alg.operations())))


def _op_table(op, card):
    if op is None:
        return "None"
    n = int(card)
    cells = []
    for i in range(n):
        for j in range(n):
            cells.append(str(int(op.intValueAt([i, j]))))
    return ",".join(cells)


def _first_op(alg):
    ops = _as_list(alg.operations())
    if not ops:
        return None
    return ops[0]


def _first_op_sym(alg):
    op = _first_op(alg)
    if op is None:
        return "empty"
    return str(op.symbol()).replace(" ", "")


def _first_op_table(alg):
    return _op_table(_first_op(alg), alg.cardinality())


def _lookup_first_op_table(alg):
    op0 = _first_op(alg)
    if op0 is None:
        return "empty"
    looked = alg.getOperation(op0.symbol())
    return _op_table(looked, alg.cardinality())


def _super_info(alg):
    sup = alg.superAlgebra()
    return str(sup.getName()) + ":" + str(sup.cardinality())


def _plus_term(alg):
    # cyclic2's op is "+"; Terms.stringToTerm rejects non-letter op names.
    # Java ReductAlgebra interprets this NonVariableTerm as alg's + operation.
    return NonVariableTerm(_op_symbol_of(alg), [Variable.x, Variable.y])


def test():
    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    plus_sym = OperationSymbol("+", 2)
    plus = _plus_term(alg)
    print("plus_term=" + str(plus).replace(" ", ""))
    print("plus_is_var=" + str(_is_var(plus)))

    # Primary: non-variable term — Java builds one operation via interpretation.
    r = ReductAlgebra(alg, [plus])
    r.setName("Rplus")
    print("plus_renamed=" + str(r.getName()))
    print("plus_card=" + str(r.cardinality()))
    _show("plus_nops", lambda: _nops(r))
    # Java TermOperationImp names the op "\"+(x,y)\"", not "+".
    _show("plus_getOp_plus", lambda: r.getOperation(plus_sym))
    _show("plus_first_sym", lambda: _first_op_sym(r))
    _show("plus_op_table", lambda: _first_op_table(r))
    _show("plus_getOp_lookup", lambda: _lookup_first_op_table(r))
    _show("plus_super", lambda: _super_info(r))
    # Java ReductAlgebra.getUniverseList() returns null.
    _show("plus_univList", lambda: r.getUniverseList())
    _show("plus_algType", lambda: str(r.algebraType()))
    _show("plus_elem0", lambda: r.getElement(0))
    _show("plus_idx0", lambda: r.elementIndex(0))

    # Named constructor, same non-variable signature.
    named = ReductAlgebra("NamedPlus", alg, [plus])
    print("named=" + str(named.getName()))
    print("named_card=" + str(named.cardinality()))
    _show("named_nops", lambda: _nops(named))
    _show("named_super", lambda: _super_info(named))

    # Secondary: Java skips variable terms as operations (universe unchanged).
    var_term = Terms.stringToTerm("x")
    print("var_is_var=" + str(_is_var(var_term)))
    rvar = ReductAlgebra(alg, [var_term])
    rvar.setName("Rvar")
    print("var_renamed=" + str(rvar.getName()))
    print("var_card=" + str(rvar.cardinality()))
    _show("var_nops", lambda: _nops(rvar))
    _show("var_super", lambda: _super_info(rvar))

    # Empty term list: no operations, same universe.
    empty = ReductAlgebra("Empty", alg, [])
    print("empty_named=" + str(empty.getName()))
    print("empty_card=" + str(empty.cardinality()))
    _show("empty_nops", lambda: _nops(empty))
    _show("empty_super", lambda: _super_info(empty))


if __name__ == "__main__":
    test()
