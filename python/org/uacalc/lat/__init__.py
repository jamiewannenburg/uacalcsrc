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
        "makeOrderedSet": "makeOrderedSet",
        "findJoinIrred": "findJoinIrred",
        "findMeetIrred": "findMeetIrred",
        "irredundantJoinDecomposition": "irredundantJoinDecomposition",
        "irredundantMeetDecomposition": "irredundantMeetDecomposition",
        "makeIrredundantJoin": "makeIrredundantJoin",
        "makeIrredundantMeet": "makeIrredundantMeet",
        "con": "con",
        "sub": "sub",
        "universe": "universe",
    },
    "SmallLattice": {
        "upperCoversIndices": "upper_covers_indices",
        "getName": "name",
        "getUniverseList": "universe",
    },
    "DiamondLattice": {
        "upperCoversIndices": "upper_covers_indices",
    },
    "BooleanLattice": {
        "upperCoversIndices": "upper_covers_indices",
    },
    "OrderedSet": {
        "getUpperCovers": "get_upper_covers",
        "getLowerCovers": "get_lower_covers",
        "univ": "univ",
        "card": "card",
        "leq": "leq",
        "filter": "filter",
        "ideal": "ideal",
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

    _maximals = globals()["maximals"]
    _BasicLattice = globals()["BasicLattice"]
    _SmallLattice = globals().get("SmallLattice")
    _OrderedSet = globals().get("OrderedSet")
    _DiamondLattice = globals().get("DiamondLattice")
    _BooleanLattice = globals().get("BooleanLattice")
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
            # Java catches NonOrderedSetException and returns null. A meet
            # table that is not a semilattice can still induce a poset
            # (unlike some join tables), so only map library failures to None.
            try:
                if meet_op is None:
                    return _lattice_from_meet(name, meet_op_or_univ)
                return _lattice_from_meet_with_universe(
                    name, list(meet_op_or_univ), meet_op
                )
            except ValueError:
                return None

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

    class Order(object):
        """Jython-style ``org.uacalc.lat.Order``: implement ``leq(a, b)``.

        Pass a subclass, any object with ``leq``, or wrap a two-argument
        callable as ``Order(leq_fn)``. ``OrderedSets.maximals`` accepts all
        three, matching Jython classes that implement the Java interface.
        """

        def __init__(self, leq=None):
            self._leq_fn = leq

        def leq(self, a, b):
            if self._leq_fn is not None:
                return bool(self._leq_fn(a, b))
            raise NotImplementedError("Order.leq")

    class OrderedSets(object):
        """Static facade matching Java ``org.uacalc.lat.OrderedSets``."""

        @staticmethod
        def maximals(elems, order):
            # Java NPEs on a null collection before calling leq.
            if elems is None:
                raise _NullPointerException(
                    'Cannot invoke "java.util.Collection.iterator()" because '
                    '"elems" is null'
                )
            # Java NPEs on a null order as soon as it compares two elements.
            # Empty / singleton collections never call leq.
            items = list(elems)
            if order is None and len(items) > 1:
                raise _NullPointerException(
                    'Cannot invoke "org.uacalc.lat.Order.leq(Object, Object)" '
                    'because "order" is null'
                )
            return list(_maximals(items, order))

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
    _apply_aliases(_DiamondLattice, _CLASS_ALIASES["DiamondLattice"])
    _apply_aliases(_BooleanLattice, _CLASS_ALIASES["BooleanLattice"])
    _apply_aliases(_OrderedSet, _CLASS_ALIASES["OrderedSet"])
    _apply_aliases(Order, _CLASS_ALIASES["Order"])

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

        def makeOrderedSet(self, lat):
            # Java builds a latdraw OrderedSet; Python returns uacalc_lib OrderedSet.
            if lat is None:
                raise _NullPointerException(
                    'Cannot invoke "org.uacalc.lat.Lattice.universe()" because '
                    '"lat" is null'
                )
            if _OrderedSet is None:
                raise _UnsupportedOperationException("OrderedSet is not bound")
            return _OrderedSet.from_lattice(lat)

        def _irreds(self, join=True):
            if join:
                fn = getattr(self, "joinIrreducibles", None) or self.join_irreducibles
            else:
                fn = getattr(self, "meetIrreducibles", None) or self.meet_irreducibles
            return list(fn())

        def _covers(self, v, upper=True):
            if upper:
                fn = getattr(self, "upperCovers", None) or self.upper_covers
            else:
                fn = getattr(self, "lowerCovers", None) or self.lower_covers
            return list(fn(v))

        def findJoinIrred(self, a, b):
            # Java: minimal join-irreducible below a and not below b, by
            # walking meet-irreducibles (BasicLattice.findJoinIrred).
            if self.leq(a, b):
                return None
            for e in _irreds(self, join=False):
                if not self.leq(a, e):
                    test = self.meet(a, e)
                    if not self.leq(test, b):
                        a = test
            return a

        def findMeetIrred(self, a, b):
            if self.leq(b, a):
                return None
            for e in _irreds(self, join=True):
                if not self.leq(e, a):
                    test = self.join(a, e)
                    if not self.leq(b, test):
                        a = test
            return a

        def makeIrredundantJoin(self, lst):
            items = list(lst)
            top = join(self, items)
            ans = []
            ans_join = self.zero()
            for i, a in enumerate(items):
                rest_join = join(self, items[i + 1 :])
                b = join(self, ans_join, rest_join)
                if b != top:
                    ans.append(a)
                    ans_join = join(self, ans_join, a)
            return ans

        def makeIrredundantMeet(self, lst):
            items = list(lst)
            bot = meet(self, items)
            ans = []
            ans_meet = self.one()
            for i, a in enumerate(items):
                rest_meet = meet(self, items[i + 1 :])
                b = meet(self, ans_meet, rest_meet)
                if b != bot:
                    ans.append(a)
                    ans_meet = meet(self, ans_meet, a)
            return ans

        def irredundantJoinDecomposition(self, v):
            decomp = []
            lc = _covers(self, v, upper=False)
            if not lc:
                return decomp
            join_so_far = self.zero()
            for lcov in lc:
                ji = findJoinIrred(self, v, lcov)
                if ji is not None and not self.leq(ji, join_so_far):
                    join_so_far = join(self, join_so_far, ji)
                    decomp.append(ji)
                    if self.leq(v, join_so_far):
                        break
            return makeIrredundantJoin(self, decomp)

        def irredundantMeetDecomposition(self, v):
            decomp = []
            uc = _covers(self, v, upper=True)
            if not uc:
                return decomp
            meet_so_far = self.one()
            for cov in uc:
                mi = findMeetIrred(self, v, cov)
                if mi is not None and not self.leq(meet_so_far, mi):
                    meet_so_far = meet(self, meet_so_far, mi)
                    decomp.append(mi)
                    if self.leq(meet_so_far, v):
                        break
            return makeIrredundantMeet(self, decomp)

        def _as_basic_algebra(self):
            from org.uacalc.alg import BasicAlgebra
            from org.uacalc.alg.op import Operations, OperationSymbol

            n = int(self.cardinality())
            join_table = []
            meet_table = []
            elems = [self.getElement(i) for i in range(n)]
            for ei in elems:
                for ej in elems:
                    join_table.append(int(self.elementIndex(join(self, ei, ej))))
                    meet_table.append(int(self.elementIndex(meet(self, ei, ej))))
            make = getattr(Operations, "makeIntOperation", None)
            if make is None:
                make = Operations.make_int_operation
            join_op = make(OperationSymbol("join", 2), n, join_table)
            meet_op = make(OperationSymbol("meet", 2), n, meet_table)
            name_fn = getattr(self, "getName", None) or self.name
            name = name_fn() if callable(name_fn) else name_fn
            return BasicAlgebra(str(name), n, [join_op, meet_op])

        def con(self):
            from org.uacalc.alg.conlat import CongruenceLattice

            return CongruenceLattice(_as_basic_algebra(self))

        def sub(self):
            from org.uacalc.alg.sublat import SubalgebraLattice

            alg = _as_basic_algebra(self)
            inner = getattr(alg, "_inner", alg)
            return SubalgebraLattice(inner)

        try:
            _BasicLattice.join = join
            _BasicLattice.meet = meet
            _BasicLattice.getUniverseOrder = getUniverseOrder
            _BasicLattice.convertToDefaultValueOps = convertToDefaultValueOps
            _BasicLattice.dual = dual
            _BasicLattice.makeOrderedSet = makeOrderedSet
            _BasicLattice.findJoinIrred = findJoinIrred
            _BasicLattice.findMeetIrred = findMeetIrred
            _BasicLattice.makeIrredundantJoin = makeIrredundantJoin
            _BasicLattice.makeIrredundantMeet = makeIrredundantMeet
            _BasicLattice.irredundantJoinDecomposition = irredundantJoinDecomposition
            _BasicLattice.irredundantMeetDecomposition = irredundantMeetDecomposition
            _BasicLattice.con = con
            _BasicLattice.sub = sub
        except (TypeError, AttributeError):
            pass

    globals()["Lattices"] = Lattices
    globals()["OrderedSets"] = OrderedSets
    globals()["Order"] = Order
    globals()["_CLASS_ALIASES"] = _CLASS_ALIASES
else:
    from org.uacalc.lat import *  # noqa: F403
