# coding: utf-8
# Dual-runtime parity script for SubalgebraLattice (~/uacalc get_subreducts / 2subalgebras).
from __future__ import print_function

from org.uacalc.io import AlgebraIO
from org.uacalc.alg.sublat import SubalgebraLattice


def _norm_set(s):
    # Jython BasicSet str is like "[0, 1]"; CPython uses "{0,1}".
    text = str(s).replace(" ", "")
    text = text.replace("[", "{").replace("]", "}")
    return text


def _card(obj):
    if hasattr(obj, "cardinality"):
        try:
            return obj.cardinality()
        except Exception:
            pass
    if hasattr(obj, "universeSize"):
        try:
            return obj.universeSize()
        except Exception:
            pass
    if hasattr(obj, "universe_size"):
        try:
            return obj.universe_size()
        except Exception:
            pass
    # Fallback: count digits in normalized set string
    text = _norm_set(obj)
    if text in ("{}", "[]", ""):
        return 0
    return text.count(",") + 1


def test():
    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    sl = SubalgebraLattice(alg)
    print("card=" + str(sl.cardinality()))
    items = sorted(_norm_set(x) for x in sl.iterator())
    print("universe=" + str(items))
    one = sl.Sg([0])
    print("sg0_card=" + str(_card(one)))


if __name__ == "__main__":
    test()
