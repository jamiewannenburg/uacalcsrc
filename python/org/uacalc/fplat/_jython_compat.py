"""Jython-facing helpers for ``org.uacalc.fplat`` (CPython only).

Java ``PartiallyDefinedLattice(String name, Order<Variable> order,
List<List<Variable>> joins, List<List<Variable>> meets)`` stores the order
and the join/meet lists and delegates ``leq`` to the order. The name argument
is unused (no field). ``toString`` is the default ``Class@hex``.
"""

from __future__ import annotations

from typing import Any, List, Optional

from org.uacalc._exceptions import NullPointerException


def _install(g: dict) -> None:
    _LibPDL = g.get("PartiallyDefinedLattice")
    g["_LibPartiallyDefinedLattice"] = _LibPDL

    def _npe(msg: str = "") -> None:
        raise NullPointerException(msg)

    def _as_list(value: Any) -> Optional[List[Any]]:
        if value is None:
            return None
        return [list(group) if group is not None else None for group in list(value)]

    class PartiallyDefinedLattice(object):
        """Java ``org.uacalc.fplat.PartiallyDefinedLattice`` constructor + ``leq``."""

        def __init__(self, name: Any, order: Any, joins: Any, meets: Any) -> None:
            # Java stores order/joins/meets with no null checks; name is discarded.
            self._name = name
            self.order = order
            self.definedJoins = _as_list(joins) if joins is not None else None
            self.definedMeets = _as_list(meets) if meets is not None else None

        def leq(self, a: Any, b: Any) -> bool:
            if self.order is None:
                _npe(
                    'Cannot invoke "org.uacalc.lat.Order.leq(Object, Object)" '
                    'because "this.order" is null'
                )
            return bool(self.order.leq(a, b))

        def getDefinedJoins(self) -> Any:
            return self.definedJoins

        def getDefinedMeets(self) -> Any:
            return self.definedMeets

        def get_defined_joins(self) -> Any:
            return self.getDefinedJoins()

        def get_defined_meets(self) -> Any:
            return self.getDefinedMeets()

        def name(self) -> Any:
            return self._name

        def getName(self) -> Any:
            return self._name

        def toString(self) -> str:
            return str(self)

        def __str__(self) -> str:
            # Java Object.toString is Class@hex; keep a stable Python form.
            return "PartiallyDefinedLattice({0})".format(self._name)

        def __repr__(self) -> str:
            return "PartiallyDefinedLattice({0!r})".format(self._name)

    g["PartiallyDefinedLattice"] = PartiallyDefinedLattice
