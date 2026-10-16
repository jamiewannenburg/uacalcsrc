# coding: utf-8
# Dual-runtime parity script for VariableImp / NonVariableTerm evaluation.
from __future__ import print_function

from org.uacalc.alg.op import OperationSymbol
from org.uacalc.io import AlgebraIO
from org.uacalc.terms import NonVariableTerm, VariableImp


def _map(*pairs):
    try:
        from java.util import HashMap
        m = HashMap()
        for k, v in pairs:
            m.put(k, v)
        return m
    except ImportError:
        return dict(pairs)


def _names(lst):
    if lst is None:
        return "null"
    out = []
    for v in list(lst):
        getter = getattr(v, "getName", None)
        out.append(getter() if getter is not None else str(v))
    return ",".join(out)


def _varlist(*vars):
    try:
        from java.util import ArrayList
        lst = ArrayList()
        for v in vars:
            lst.add(v)
        return lst
    except ImportError:
        return list(vars)


def _syms(coll):
    if coll is None:
        return "null"
    parts = sorted([x.name() + "/" + str(int(x.arity())) for x in list(coll)])
    return ",".join(parts)


def test():
    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    x = VariableImp("x")
    y = VariableImp("y")
    plus = OperationSymbol("+", 2)
    fxy = NonVariableTerm(plus, [x, y])
    print("name=" + x.getName())
    print("isa=" + str(x.isaVariable()).lower())
    print("lead=" + str(x.leadingOperationSymbol()))
    print("children=" + str(x.getChildren()))
    print("ops=" + _syms(x.getOperationSymbols()))
    print("vars=" + _names(x.getVariableList()))
    print("depth=" + str(x.depth()))
    print("len=" + str(x.length()))
    print("eval=" + str(int(x.intEval(alg, _map((x, 1))))))
    print("eval2=" + str(int(x.eval(alg, _map((x, 0))))))
    print("tostr=" + x.toString())
    try:
        from java.lang import StringBuffer
        sb = StringBuffer("v=")
        x.writeStringBuffer(sb)
        print("wsb=" + sb.toString())
    except ImportError:
        print("wsb=" + x.writeStringBuffer("v="))
    print("eq=" + str(x.equals(VariableImp("x"))).lower())
    print("hash=" + str(x.hashCode() == VariableImp("x").hashCode()).lower())
    print("sub=" + str(x.substitute(_map((x, y)))))
    op = x.interpretation(alg, _varlist(x, y), True)
    print("interp_ar=" + str(int(op.arity())))
    print("interp1_ar=" + str(int(x.interpretation(alg).arity())))
    print("fxy=" + str(fxy))
    print("fxy_lead=" + fxy.leadingOperationSymbol().name())
    print("fxy_ch=" + _names(fxy.getChildren()))
    print("fxy_ops=" + _syms(fxy.getOperationSymbols()))
    print("fxy_vars=" + _names(fxy.getVariableList()))
    print("fxy_depth=" + str(fxy.depth()))
    print("fxy_len=" + str(fxy.length()))
    print("fxy_eval=" + str(int(fxy.intEval(alg, _map((x, 1), (y, 1))))))
    print("fxy_eval2=" + str(int(fxy.eval(alg, _map((x, 1), (y, 0))))))
    print("fxy_interp=" + str(int(fxy.interpretation(alg, _varlist(x, y), True).arity())))
    print("fxy_interp1=" + str(int(fxy.interpretation(alg).arity())))
    print("fxy_sub=" + str(fxy.substitute(_map((x, y)))))
    try:
        from java.lang import StringBuffer
        sb2 = StringBuffer("t=")
        fxy.writeStringBuffer(sb2)
        print("fxy_wsb=" + sb2.toString())
    except ImportError:
        print("fxy_wsb=" + fxy.writeStringBuffer("t="))
    print("fxy_eq=" + str(fxy.equals(NonVariableTerm(plus, [x, y]))).lower())
    print("fxy_hash=" + str(fxy.hashCode() == NonVariableTerm(plus, [x, y]).hashCode()).lower())


if __name__ == "__main__":
    test()
