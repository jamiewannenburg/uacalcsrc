# coding: utf-8
# Dual-runtime parity script for BasicLattice / OrderedSets / Lattices extras.
from __future__ import print_function

from org.uacalc.alg.op import Operations, OperationSymbol
from org.uacalc.lat import Lattices, OrderedSets


def _make_int_op(name, arity, size, table):
    make = getattr(Operations, "makeIntOperation", None)
    if make is None:
        make = Operations.make_int_operation
    return make(OperationSymbol(name, arity), size, table)


def _lab(x):
    if x is None:
        return None
    try:
        return int(str(x))
    except Exception:
        return str(x)


def _labs(xs):
    if xs is None:
        return None
    return sorted([_lab(x) for x in list(xs)])


def test():
    join2 = _make_int_op("v", 2, 2, [0, 1, 1, 1])
    lat = Lattices.latticeFromJoin("chain2j", join2)
    print("name=" + str(lat.getName() if hasattr(lat, "getName") else lat.name()))
    print("card=" + str(lat.cardinality()))
    print("zero=" + str(_lab(lat.zero())))
    print("one=" + str(_lab(lat.one())))
    print("atoms=" + str(_labs(lat.atoms())))
    print("coatoms=" + str(_labs(lat.coatoms())))
    jis = lat.joinIrreducibles() if hasattr(lat, "joinIrreducibles") else lat.join_irreducibles()
    print("joinIrreducibles=" + str(_labs(jis)))
    mis = lat.meetIrreducibles() if hasattr(lat, "meetIrreducibles") else lat.meet_irreducibles()
    print("meetIrreducibles=" + str(_labs(mis)))
    print("universe=" + str(_labs(lat.getUniverseList())))
    e0 = lat.getElement(0)
    print("getElement0=" + str(_lab(e0)))
    print("elementIndex0=" + str(lat.elementIndex(e0)))
    print("algebraType=" + str(lat.algebraType()))
    print("leq=" + str(bool(lat.leq(e0, lat.getElement(1)))))
    print("join=" + str(_lab(lat.join(e0, lat.getElement(1)))))
    print("meet=" + str(_lab(lat.meet(e0, lat.getElement(1)))))
    uc = lat.upperCovers(e0) if hasattr(lat, "upperCovers") else lat.upper_covers(_lab(e0))
    print("upperCovers0=" + str(_labs(uc)))
    e1 = lat.getElement(1)
    lc = lat.lowerCovers(e1) if hasattr(lat, "lowerCovers") else lat.lower_covers(_lab(e1))
    print("lowerCovers1=" + str(_labs(lc)))
    print("filter0=" + str(_labs(lat.filter(e0))))
    print("ideal1=" + str(_labs(lat.ideal(e1))))
    jib = lat.joinIrredsBelow(e1) if hasattr(lat, "joinIrredsBelow") else lat.join_irreds_below(_lab(e1))
    print("joinIrredsBelow1=" + str(_labs(jib)))
    mia = lat.meetIrredsAbove(e0) if hasattr(lat, "meetIrredsAbove") else lat.meet_irreds_above(_lab(e0))
    print("meetIrredsAbove0=" + str(_labs(mia)))
    p = lat.getPoset()
    if hasattr(p, "univ"):
        print("posetCard=" + str(len(list(p.univ()))))
        print("posetUniv=" + str(_labs(p.univ())))
    else:
        print("posetCard=" + str(p.cardinality()))
        print("posetUniv=" + str(_labs(p.universe())))
    print("posetLeq=" + str(bool(p.leq(e0, e1))).lower())
    if hasattr(e0, "lowerCovers"):
        print("posetLowerCovers1=" + str(_labs(e1.lowerCovers())))
        print("posetFilter0=" + str(_labs(e0.filter())))
        print("posetIdeal1=" + str(_labs(e1.ideal())))
    else:
        lc = p.getLowerCovers(e1) if hasattr(p, "getLowerCovers") else p.get_lower_covers(e1)
        print("posetLowerCovers1=" + str(_labs(lc)))
        print("posetFilter0=" + str(_labs(p.filter(e0))))
        print("posetIdeal1=" + str(_labs(p.ideal(e1))))
    os2 = lat.makeOrderedSet(lat)
    if hasattr(os2, "card"):
        print("makeOrderedSetCard=" + str(os2.card()))
    else:
        print("makeOrderedSetCard=" + str(len(list(os2.univ()))))
    print("universeOrder=" + str(lat.getUniverseOrder()))
    print("findJoinIrred=" + str(_lab(lat.findJoinIrred(e1, e0))))
    print("findMeetIrred=" + str(_lab(lat.findMeetIrred(e0, e1))))
    print("irredundantJoinDecomp=" + str(_labs(lat.irredundantJoinDecomposition(e1))))
    print("irredundantMeetDecomp=" + str(_labs(lat.irredundantMeetDecomposition(e0))))
    print("makeIrredundantJoin=" + str(_labs(lat.makeIrredundantJoin(list(jis)))))
    print("makeIrredundantMeet=" + str(_labs(lat.makeIrredundantMeet(list(mis)))))
    con = lat.con()
    print("conCard=" + str(con.cardinality() if con is not None else None))
    sub = lat.sub()
    print("subCard=" + str(sub.cardinality() if sub is not None else None))

    try:
        from org.uacalc.lat import DivisibilityOrder
        order = DivisibilityOrder()
    except Exception:
        from org.uacalc.lat import Order
        class _Div(Order):
            def leq(self, a, b):
                if a == 0:
                    return True
                if b == 0:
                    return a == 0
                return (b % a) == 0
        order = _Div()
    print("maximals=" + str(list(OrderedSets.maximals([2, 3, 6, 35, 175], order))))

    dual_npe = False
    try:
        Lattices.dual(lat)
    except Exception:
        dual_npe = True
    except:
        dual_npe = True
    print("dualNpe=" + str(dual_npe).lower())

    con_null = True
    try:
        from org.uacalc.io import AlgebraIO
        alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
        sl = None
        try:
            sl = Lattices.conToSmallLattice(alg.con())
        except TypeError:
            _ctors = Lattices.getDeclaredConstructors()
            _ctors[0].setAccessible(True)
            _helper = _ctors[0].newInstance()
            sl = _helper.conToSmallLattice(alg.con())
        con_null = sl is None
    except Exception:
        con_null = True
    except:
        con_null = True
    print("conToSmallLatticeNull=" + str(con_null).lower())


if __name__ == "__main__":
    test()
