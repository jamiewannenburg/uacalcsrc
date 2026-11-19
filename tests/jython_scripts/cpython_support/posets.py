"""Jamie ``posets.py`` surface for CPython (``.lat`` via ``read_lat``, ``org.uacalc.lat.OrderedSet``)."""
from __future__ import annotations

from itertools import chain, combinations

from org.uacalc.lat import OrderedSet

from read_lat import parse_lat_file


def _label_key(label: int | str) -> tuple[int, int | str]:
    if isinstance(label, int):
        return (0, label)
    if isinstance(label, str) and label.lstrip("-").isdigit():
        return (0, int(label))
    return (1, label)


def _coerce_filters_for_uacalc(
    labels: list[int | str], filters: list[list[int | str]]
) -> tuple[list[int], list[list[int]]]:
    """Map LatDraw labels to ``OrderedSet.from_filters`` integer universe."""
    if not labels:
        return [], []
    native_int = all(isinstance(x, int) for x in labels)
    if native_int:
        iv = [int(x) for x in labels]
        return iv, [[int(x) for x in row] for row in filters]
    idx = {lab: i for i, lab in enumerate(labels)}

    def _map(lab: int | str) -> int:
        if lab in idx:
            return idx[lab]
        if isinstance(lab, str) and lab.lstrip("-").isdigit():
            return int(lab)
        raise KeyError(lab)

    iv = list(range(len(labels)))
    mapped = [[_map(x) for x in row] for row in filters]
    return iv, mapped


class _JamiePosetElement:
    def __init__(self, parent: "_JamieOrderedSet", index: int):
        self._parent = parent
        self._index = index

    def upperCovers(self):
        covers = self._parent._os.get_upper_covers(self._index)
        return [_JamiePosetElement(self._parent, c) for c in covers]

    def filter(self):
        return [self._parent._el(i) for i in self._parent._os.filter(self._index)]

    def label(self):
        if self._parent._labels and self._index < len(self._parent._labels):
            return self._parent._labels[self._index]
        return str(self._index)

    def __str__(self):
        return str(self.label())

    def __hash__(self):
        return hash(self._index)

    def __eq__(self, other):
        return isinstance(other, _JamiePosetElement) and other._index == self._index


class _JamieOrderedSet:
    """LatDraw-like element API over ``org.uacalc.lat.OrderedSet``."""

    def __init__(self, os: OrderedSet, labels: list[int | str], name: str):
        self._os = os
        self._labels = labels
        self._name = name

    def _el(self, index: int) -> _JamiePosetElement:
        return _JamiePosetElement(self, index)

    def univ(self):
        return [self._el(i) for i in self._os.universe()]

    def card(self):
        return self._os.cardinality()

    def name(self):
        return self._name

    def getName(self):
        return self._name


def _ordered_set_from_latdraw(name: str, labels: list[int | str], filters: list[list[int | str]]) -> _JamieOrderedSet:
    universe, filt = _coerce_filters_for_uacalc(labels, filters)
    os = OrderedSet.from_filters(universe, filt, name=name)
    return _JamieOrderedSet(os, list(labels), name)


def InputPoset(filename: str) -> OrderedSet:
    name, labels, filters = parse_lat_file(filename)
    return _ordered_set_from_latdraw(name, labels, filters)


def dict2poset(d, name):
    labels = sorted(d.keys())
    filters = []
    for n in labels:
        if isinstance(d[n], set):
            filters.append(sorted(list(d[n]), key=_label_key))
        else:
            filters.append(d[n])
    return _ordered_set_from_latdraw(name, labels, filters)


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def get_upsets_lattice(po):
    from dmm import AbstractOperation, BasicAlgebra

    univ = po.univ()
    filters = []
    for i in univ:
        filters.append(set(i.filter()))

    new_universe = []
    for els in powerset(univ):
        union = set()
        for el in els:
            union.update(set(po.filter(el)))
        found = False
        for new_el in new_universe:
            if new_el == union:
                found = True
                break
        if not found:
            new_universe.append(union)

    cardinality = len(new_universe)
    po_name = po.name() if callable(getattr(po, "name", None)) else po.name
    if po_name is None:
        po_name = ""

    class join_op(AbstractOperation):
        def intValueAt(self, args):
            union = new_universe[args[0]].union(new_universe[args[1]])
            for i, el in enumerate(new_universe):
                if el == union:
                    return i
            raise Exception(
                "Could not find union of {} and {}".format(
                    new_universe[args[0]], new_universe[args[1]]
                )
            )

    join = join_op("join", 2, cardinality)

    class meet_op(AbstractOperation):
        def intValueAt(self, args):
            intersection = new_universe[args[0]].intersection(new_universe[args[1]])
            for i, el in enumerate(new_universe):
                if el == intersection:
                    return i
            raise Exception(
                "Could not find intersection of {} and {}".format(
                    new_universe[args[0]], new_universe[args[1]]
                )
            )

    meet = meet_op("meet", 2, cardinality)
    return BasicAlgebra("dual({})".format(po_name), cardinality, [join, meet])


def PosetToLatFile(po):  # noqa: ARG001
    raise NotImplementedError("PosetToLatFile not needed for CPython PhD harness")