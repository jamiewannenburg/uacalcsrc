# coding: utf-8
# Dual-runtime parity script for org.uacalc.lat.Order and generic maximals.
from __future__ import print_function

from org.uacalc.lat import Order, OrderedSets


class Nat(Order):
    def leq(self, a, b):
        return a <= b


class Div(Order):
    def leq(self, a, b):
        if a == 0:
            return True
        if b == 0:
            return a == 0
        return (b % a) == 0


class PrefSeq(Order):
    def leq(self, a, b):
        sa = list(a)
        sb = list(b)
        n = len(sa)
        if n > len(sb):
            return False
        return sb[:n] == sa


def test():
    nat = Nat()
    div = Div()
    pref = PrefSeq()
    print("leq12=" + str(bool(nat.leq(1, 2))).lower())
    print("leq21=" + str(bool(nat.leq(2, 1))).lower())
    print("div26=" + str(bool(div.leq(2, 6))).lower())
    print("maxNat=" + str(list(OrderedSets.maximals([3, 1, 4, 2], nat))))
    print("maxDiv=" + str(list(OrderedSets.maximals([2, 3, 6, 35, 175], div))))
    print("maxPref=" + str(list(OrderedSets.maximals([[1], [1, 2], [1, 2, 3], [9]], pref))))
    print("maxEmpty=" + str(list(OrderedSets.maximals([], nat))))


if __name__ == "__main__":
    test()
