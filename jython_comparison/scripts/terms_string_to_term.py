# coding: utf-8
# Dual-runtime parity script for Terms / NonVariableTerm (~/uacalc get_subreducts, dmm).
from __future__ import print_function

from org.uacalc.alg.op import OperationSymbol
from org.uacalc.terms import Terms, NonVariableTerm, Variable


def test():
    t = Terms.stringToTerm("x")
    print("term=" + str(t))
    print("var_x=" + str(Variable.x))
    c = NonVariableTerm.makeConstantTerm(OperationSymbol("e", 0))
    print("const=" + str(c))


if __name__ == "__main__":
    test()
