# coding: utf-8
# Dual-runtime parity script for Terms / NonVariableTerm (~/uacalc get_subreducts, dmm).
from __future__ import print_function

from org.uacalc.alg.op import OperationSymbol
from org.uacalc.terms import Terms, NonVariableTerm, Variable, VariableImp


def test():
    t = Terms.stringToTerm("x")
    print("term=" + str(t))
    print("var_x=" + str(Variable.x))
    print("var_x_name=" + Variable.x.getName())
    c = NonVariableTerm.makeConstantTerm(OperationSymbol("e", 0))
    print("const=" + str(c))
    print("const_isa=" + str(c.isaVariable()).lower())
    print("valid_x=" + str(Terms.isValidVarString("x")).lower())
    print("valid_plus=" + str(Terms.isValidOpNameString("+")).lower())
    x = VariableImp("x")
    fsym = OperationSymbol("f", 2, True)
    nested = NonVariableTerm(fsym, [x, NonVariableTerm(fsym, [x, x])])
    print("flat=" + str(Terms.flatten(nested)))


if __name__ == "__main__":
    test()
