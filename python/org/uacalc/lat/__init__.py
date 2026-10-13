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
    _maximals_prefix = globals()["maximals_prefix"]
    _maximals_natural_i32 = globals()["maximals_natural_i32"]
    _maximals_natural_string = globals()["maximals_natural_string"]
    _BasicLattice = globals()["BasicLattice"]

    def _join_defines_lattice(join):
        """True when *join* is a join-semilattice (library property checks).

        Java ``orderedSetFromFilters`` throws ``NonOrderedSetException`` when
        the induced filters are not a poset; a join-semilattice operation is
        idempotent, commutative, and associative.
        """
        if join is None:
            return False
        for camel, snake in (
            ("isIdempotent", "is_idempotent"),
            ("isCommutative", "is_commutative"),
            ("isAssociative", "is_associative"),
        ):
            fn = getattr(join, camel, None) or getattr(join, snake, None)
            if not callable(fn):
                return False
            try:
                if not bool(fn()):
                    return False
            except Exception:
                return False
        return True

    class Lattices(object):
        """Static facade matching Java ``org.uacalc.lat.Lattices``."""

        @staticmethod
        def latticeFromJoin(name, join_op_or_univ, join_op=None):
            # Java catches NonOrderedSetException and returns null. uacalc_lib
            # may still build a BasicLattice; the org wrapper matches Java.
            join = join_op_or_univ if join_op is None else join_op
            try:
                if join_op is None:
                    result = _lattice_from_join(name, join_op_or_univ)
                else:
                    result = _lattice_from_join_with_universe(
                        name, list(join_op_or_univ), join_op
                    )
            except ValueError:
                return None
            if not _join_defines_lattice(join):
                return None
            return result

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
            # Route only through uacalc_lib. Generic Order.leq is not bound.
            name = type(order).__name__ if order is not None else "DivisibilityOrder"
            items = list(elems)
            if name in ("DivisibilityOrder", "PyDivisibilityOrder"):
                return _maximals_divisibility([int(x) for x in items])
            if name in ("PrefixOrder", "PyPrefixOrder"):
                return _maximals_prefix([str(x) for x in items])
            if name in ("NaturalOrder", "PyNaturalOrder"):
                if items and isinstance(items[0], str):
                    return _maximals_natural_string(items)
                return _maximals_natural_i32([int(x) for x in items])
            raise NotImplementedError(
                "OrderedSets.maximals only routes DivisibilityOrder, PrefixOrder, "
                "and NaturalOrder through uacalc_lib; generic Order.leq is not bound"
            )

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
