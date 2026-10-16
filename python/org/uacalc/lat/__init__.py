import sys

# Literal map for jython_contracts validate() (also applied below).
_CLASS_ALIASES = {
    "BasicLattice": {
        "getName": "name",
        "getUniverseList": "universe",
        "joinIrreducibles": "join_irreducibles",
        "meetIrreducibles": "meet_irreducibles",
        "getElement": "get_element",
        "elementIndex": "element_index",
        "algebraType": "algebra_type",
        "getPoset": "get_poset",
        "upperCovers": "upper_covers",
        "lowerCovers": "lower_covers",
        "joinIrredsBelow": "join_irreds_below",
        "meetIrredsAbove": "meet_irreds_above",
        "one": "one",
        "zero": "zero",
        "atoms": "atoms",
        "coatoms": "coatoms",
        "filter": "filter",
        "ideal": "ideal",
        "leq": "leq",
        "join": "join",
        "meet": "meet",
        "cardinality": "cardinality",
    },
    "SmallLattice": {
        "upperCoversIndices": "upper_covers_indices",
        "getName": "name",
        "getUniverseList": "universe",
    },
    "OrderedSet": {
        "getUpperCovers": "get_upper_covers",
        "getLowerCovers": "get_lower_covers",
    },
    "Order": {
        "leq": "leq",
    },
}

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
    from org.uacalc._exceptions import NullPointerException as _NullPointerException

    _maximals_divisibility = globals()["maximals_divisibility"]
    _maximals_prefix = globals()["maximals_prefix"]
    _maximals_natural_i32 = globals()["maximals_natural_i32"]
    _maximals_natural_string = globals()["maximals_natural_string"]
    _BasicLattice = globals()["BasicLattice"]
    _SmallLattice = globals().get("SmallLattice")
    _OrderedSet = globals().get("OrderedSet")
    from org.uacalc._exceptions import (
        UnsupportedOperationException as _UnsupportedOperationException,
    )

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
            # Java Lattices.dual throws NPE (comment: "this causes a npe").
            # uacalc_lib.dual is unchanged (Clone/reference stub); the org
            # wrapper matches Java.
            raise _NullPointerException(
                'Cannot invoke "java.lang.Integer.intValue()" because the '
                'return value of "java.util.HashMap.get(Object)" is null'
            )

        @staticmethod
        def conToSmallLattice(con):
            # Java always returns null after building (and discarding) an
            # OrderedSet. Null argument NPEs on con.universe().
            # uacalc_lib.con_to_small_lattice now returns PySmallLattice.
            if con is None:
                raise _NullPointerException(
                    'Cannot invoke "org.uacalc.alg.conlat.CongruenceLattice.'
                    'universe()" because "con" is null'
                )
            return None

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

    def _apply_aliases(cls, aliases):
        if cls is None:
            return
        for camel, snake in aliases.items():
            if hasattr(cls, camel):
                continue
            impl = getattr(cls, snake, None)
            if impl is None:
                continue
            try:
                setattr(cls, camel, impl)
            except (TypeError, AttributeError):
                pass

    _apply_aliases(_BasicLattice, _CLASS_ALIASES["BasicLattice"])
    _apply_aliases(_SmallLattice, _CLASS_ALIASES["SmallLattice"])
    _apply_aliases(_OrderedSet, _CLASS_ALIASES["OrderedSet"])

    if _BasicLattice is not None:
        _orig_join = getattr(_BasicLattice, "join", None)
        _orig_meet = getattr(_BasicLattice, "meet", None)

        def join(self, a, b=None, _join=_orig_join):
            # Java join(a,b) and join(List). Folding the list is dispatch,
            # not a reimplementation of the lattice operation.
            if b is None:
                items = list(a)
                if not items:
                    return self.zero()
                acc = items[0]
                for x in items[1:]:
                    acc = _join(self, acc, x)
                return acc
            return _join(self, a, b)

        def meet(self, a, b=None, _meet=_orig_meet):
            if b is None:
                items = list(a)
                if not items:
                    return self.one()
                acc = items[0]
                for x in items[1:]:
                    acc = _meet(self, acc, x)
                return acc
            return _meet(self, a, b)

        def getUniverseOrder(self):
            # Java BasicLattice.getUniverseOrder always returns null.
            return None

        def convertToDefaultValueOps(self):
            raise _UnsupportedOperationException("Only for basic algebras")

        def dual(self):
            # Instance dual delegates to Lattices.dual, which NPEs (known Java bug).
            return Lattices.dual(self)

        try:
            _BasicLattice.join = join
            _BasicLattice.meet = meet
            _BasicLattice.getUniverseOrder = getUniverseOrder
            _BasicLattice.convertToDefaultValueOps = convertToDefaultValueOps
            _BasicLattice.dual = dual
        except (TypeError, AttributeError):
            pass

    globals()["Lattices"] = Lattices
    globals()["OrderedSets"] = OrderedSets
    globals()["_CLASS_ALIASES"] = _CLASS_ALIASES
else:
    from org.uacalc.lat import *  # noqa: F403
