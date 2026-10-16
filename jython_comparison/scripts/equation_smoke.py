# coding: utf-8
# Dual-runtime parity script for Equation (~/uacalc structural_completeness.py).
from __future__ import print_function

from org.uacalc.io import AlgebraIO
from org.uacalc.eq import Equation, Equations, Presentation
from org.uacalc.terms import Terms, NonVariableTerm, VariableImp
from org.uacalc.alg.op import OperationSymbol


def _names(lst):
    out = []
    for v in list(lst):
        getter = getattr(v, "getName", None)
        out.append(getter() if getter is not None else str(v))
    return ",".join(out)


def _syms(coll):
    parts = sorted([x.name() + "/" + str(int(x.arity())) for x in list(coll)])
    return ",".join(parts)


def _arr(a):
    if a is None:
        return "null"
    return ",".join([str(int(x)) for x in list(a)])


def _failmap(m):
    if m is None:
        return "null"
    items = m.entrySet() if hasattr(m, "entrySet") else m.items()
    parts = []
    for item in items:
        if hasattr(item, "getKey"):
            k, v = item.getKey(), item.getValue()
        else:
            k, v = item
        getter = getattr(k, "getName", None)
        name = getter() if getter is not None else str(k)
        parts.append(name + "=" + str(int(v)))
    parts.sort()
    return "{" + ",".join(parts) + "}"


def test():
    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    left = Terms.stringToTerm("x")
    right = Terms.stringToTerm("x")
    eq = Equation(left, right)
    print("left=" + str(eq.leftSide()))
    print("right=" + str(eq.rightSide()))
    print("tostring=" + eq.toString())
    print("vars=" + _names(eq.getVariableList()))
    print("failure=" + _failmap(eq.findFailureMap(alg)))
    print("find_fail=" + _arr(eq.findFailure(alg)))

    x = VariableImp("x")
    y = VariableImp("y")
    plus = OperationSymbol("+", 2)
    fxy = NonVariableTerm(plus, [x, y])
    eq_xy = Equation(x, y)
    eq_plus = Equation(fxy, x)
    print("xy=" + eq_xy.toString())
    print("xy_fail=" + _arr(eq_xy.findFailure(alg)))
    print("xy_map=" + _failmap(eq_xy.findFailureMap(alg)))
    print("plus_ops=" + _syms(eq_plus.getOperationSymbols()))
    print("plus_fail=" + _arr(eq_plus.findFailure(alg)))

    f = OperationSymbol("f", 2)
    g3 = OperationSymbol("g", 3)
    print("assoc=" + str(Equations.associativeLaw(f)))
    print("cyclic=" + str(Equations.cyclicLaw(g3)))
    print("sym=" + str(Equations.firstSecondSymmetricLaw(g3)))

    pres = Presentation([x, y], [eq_xy])
    print("pres_vars=" + _names(pres.getVariables()))
    print("pres_rels=" + ",".join([str(e) for e in list(pres.getRelations())]))


if __name__ == "__main__":
    test()
