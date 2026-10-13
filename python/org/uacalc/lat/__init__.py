import sys

is_jython = sys.platform.startswith("java")

if not is_jython:
    import uacalc_lib

    _lat = getattr(uacalc_lib, "lat")

    for _name in dir(_lat):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_lat, _name)

    _lattice_from_join = globals()["lattice_from_join"]
    _lattice_from_meet = globals()["lattice_from_meet"]
    _lattice_from_join_with_universe = globals()["lattice_from_join_with_universe"]
    _lattice_from_meet_with_universe = globals()["lattice_from_meet_with_universe"]
    _dual = globals()["dual"]
    _con_to_small_lattice = globals()["con_to_small_lattice"]
    _maximals_divisibility = globals()["maximals_divisibility"]
    _BasicLattice = globals()["BasicLattice"]

    class Lattices(object):
        """Static facade matching Java ``org.uacalc.lat.Lattices``."""

        @staticmethod
        def latticeFromJoin(name, join_op_or_univ, join_op=None):
            if join_op is None:
                return _lattice_from_join(name, join_op_or_univ)
            return _lattice_from_join_with_universe(name, list(join_op_or_univ), join_op)

        @staticmethod
        def latticeFromMeet(name, meet_op_or_univ, meet_op=None):
            if meet_op is None:
                return _lattice_from_meet(name, meet_op_or_univ)
            return _lattice_from_meet_with_universe(name, list(meet_op_or_univ), meet_op)

        @staticmethod
        def dual(lat):
            return _dual(lat)

        @staticmethod
        def conToSmallLattice(con):
            return _con_to_small_lattice(con)

    class OrderedSets(object):
        """Static facade matching Java ``org.uacalc.lat.OrderedSets``."""

        @staticmethod
        def maximals(elems, order):
            # Java dispatches on the Order implementation. DivisibilityOrder is
            # the order used by the Java OrderedSets.main example.
            if order is None or type(order).__name__ in ("DivisibilityOrder", "PyDivisibilityOrder"):
                return _maximals_divisibility(list(elems))
            if hasattr(order, "leq"):
                # Generic fallback: emulate Java OrderedSets.maximals.
                ans = []
                for candidate in list(elems):
                    new_ans = []
                    candidate_below = False
                    for elem in ans:
                        if order.leq(candidate, elem):
                            candidate_below = True
                            break
                        if not order.leq(elem, candidate):
                            new_ans.append(elem)
                    if not candidate_below:
                        ans = new_ans
                        ans.append(candidate)
                return ans
            raise TypeError("OrderedSets.maximals requires an Order with leq()")

    for _camel, _snake in (
        ("joinIrreducibles", "join_irreducibles"),
        ("getName", "name"),
        ("getUniverseList", "universe"),
    ):
        if not hasattr(_BasicLattice, _camel) and hasattr(_BasicLattice, _snake):
            try:
                setattr(_BasicLattice, _camel, getattr(_BasicLattice, _snake))
            except (TypeError, AttributeError):
                pass

    globals()["Lattices"] = Lattices
    globals()["OrderedSets"] = OrderedSets
else:
    from org.uacalc.lat import *  # noqa: F403
