# coding: utf-8
# Dual-runtime parity script for FreeAlgebra (Java/Jython source of truth).
#
# Known CPython / uacalc_lib gaps (do not hide; backend should match Java):
# - get_element / element_index in uacalc_lib/src/alg/free_algebra.rs always
#   return None (Java SubProductAlgebra.getElement / elementIndex work).
# - No getTerms / getTerm / getElementFromTerm / getProductAlgebra /
#   generators / getVariables on the binding (Java: SubProductAlgebra).
# - No operations() (only operations_count); getOperation therefore cannot
#   walk the op list the way GeneralAlgebra does.
# - new_with_progress ignores make_universe / thin_gens / decompose.
# - Default names differ (Java Free(1, C2) vs Rust F(1) over C2); this script
#   calls setName so name format is not the blocker.
# - get_idempotent_terms exists (snake_case) and returns strings, not Term
#   objects; Java getIdempotentTerms() returns List<Term>.
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import FreeAlgebra
from org.uacalc.alg.op import OperationSymbol


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


def _coords(elem):
    if elem is None:
        return "None"
    arr = None
    for attr in ("getArray", "get_array", "toArray", "to_array"):
        fn = getattr(elem, attr, None)
        if callable(fn):
            try:
                arr = fn()
                break
            except TypeError:
                continue
    if arr is None:
        try:
            arr = list(elem)
        except TypeError:
            return str(elem).replace(" ", "")
    return "[" + ",".join(str(int(x)) for x in arr) + "]"


def _term_str(term):
    if term is None:
        return "None"
    return str(term).replace(" ", "")


def _product_info(prod):
    if prod is None:
        return "None"
    parts = ["card=" + str(prod.cardinality())]
    nfac = None
    for attr in ("getNumberOfFactors", "get_number_of_factors", "numberOfFactors"):
        fn = getattr(prod, attr, None)
        if callable(fn):
            try:
                nfac = fn()
                break
            except TypeError:
                continue
        if fn is not None and not callable(fn):
            nfac = fn
            break
    if nfac is None:
        fac = getattr(prod, "factors", None)
        if callable(fac):
            try:
                nfac = len(_as_list(fac()))
            except Exception:
                nfac = None
    if nfac is not None:
        parts.append("factors=" + str(int(nfac)))
    return ",".join(parts)


def _op_table(alg, sym):
    op = alg.getOperation(sym)
    if op is None:
        return "None"
    n = int(alg.cardinality())
    cells = []
    for i in range(n):
        for j in range(n):
            cells.append(str(int(op.intValueAt([i, j]))))
    return ",".join(cells)


def _dump_free(label, f, plus_sym):
    f.setName(label)
    print(label + "_renamed=" + str(f.getName()))
    print(label + "_card=" + str(f.cardinality()))

    def _univ():
        items = _as_list(f.getUniverseList())
        return "[" + ",".join(_coords(e) for e in items) + "]"

    _show(label + "_universe", _univ)

    def _elems():
        n = int(f.cardinality())
        return "[" + ",".join(_coords(f.getElement(i)) for i in range(n)) + "]"

    _show(label + "_getElement", _elems)

    def _indices():
        items = _as_list(f.getUniverseList())
        return "[" + ",".join(str(f.elementIndex(e)) for e in items) + "]"

    _show(label + "_elementIndex", _indices)

    def _terms():
        terms = f.getTerms()
        return "[" + ",".join(_term_str(t) for t in _as_list(terms)) + "]"

    _show(label + "_getTerms", _terms)

    def _get_term_roundtrip():
        n = int(f.cardinality())
        parts = []
        for i in range(n):
            elem = f.getElement(i)
            term = f.getTerm(elem)
            back = f.getElementFromTerm(term)
            parts.append(
                str(i) + ":" + _term_str(term) + "->" + _coords(back)
            )
        return "[" + ",".join(parts) + "]"

    _show(label + "_term_roundtrip", _get_term_roundtrip)

    _show(label + "_product", lambda: _product_info(f.getProductAlgebra()))
    # SubProductAlgebra.superAlgebra() is the same BigProductAlgebra.
    _show(label + "_superAlgebra", lambda: _product_info(f.superAlgebra()))
    _show(label + "_algebraType", lambda: str(f.algebraType()))

    def _gens():
        gens = f.generators()
        return "[" + ",".join(_coords(g) for g in _as_list(gens)) + "]"

    _show(label + "_generators", _gens)

    def _vars():
        vs = f.getVariables()
        return "[" + ",".join(_term_str(v) for v in _as_list(vs)) + "]"

    _show(label + "_getVariables", _vars)

    def _idem():
        terms = f.getIdempotentTerms()
        return "[" + ",".join(_term_str(t) for t in _as_list(terms)) + "]"

    _show(label + "_getIdempotentTerms", _idem)

    def _nops():
        return str(len(_as_list(f.operations())))

    _show(label + "_nops", _nops)
    _show(label + "_op_table", lambda: _op_table(f, plus_sym))


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    plus_sym = OperationSymbol("+", 2)

    # Java: FreeAlgebra(alg, n) -> makeUniverse=true, thinGens=false.
    f = FreeAlgebra(c2, 1)
    _dump_free("F1", f, plus_sym)

    # Java: FreeAlgebra(alg, n, makeUniverse, thinGens).
    f_thin = FreeAlgebra(c2, 1, True, True)
    _dump_free("F1thin", f_thin, plus_sym)


if __name__ == "__main__":
    test()
