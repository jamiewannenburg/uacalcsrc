# coding: utf-8
# Dual-runtime parity script for Equation (~/uacalc structural_completeness.py).
from __future__ import print_function

from org.uacalc.io import AlgebraIO
from org.uacalc.eq import Equation
from org.uacalc.terms import Terms


def test():
    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    left = Terms.stringToTerm("x")
    right = Terms.stringToTerm("x")
    eq = Equation(left, right)
    print("left=" + str(eq.leftSide()))
    print("right=" + str(eq.rightSide()))
    fail = eq.findFailureMap(alg)
    print("failure=" + str(fail))


if __name__ == "__main__":
    test()
