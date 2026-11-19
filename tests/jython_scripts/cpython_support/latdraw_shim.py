"""Register ``org.latdraw.orderedset`` for CPython (Jamie scripts unchanged)."""
from __future__ import annotations

import sys
import types

from read_lat import parse_lat_file


def install_latdraw_shim() -> None:
    if "org.latdraw.orderedset" in sys.modules:
        return

    from cpython_support.posets import _ordered_set_from_latdraw

    class InputLattice:
        def __init__(self, path: str):
            self.name, self.labels, self.upperCoversList = parse_lat_file(path)

    class OrderedSet:
        @staticmethod
        def orderedSetFromFilters(name, labels, upperCoversList):
            return _ordered_set_from_latdraw(name, list(labels), list(upperCoversList))

    orderedset = types.ModuleType("org.latdraw.orderedset")
    orderedset.InputLattice = InputLattice
    orderedset.OrderedSet = OrderedSet

    if "org" not in sys.modules:
        sys.modules["org"] = types.ModuleType("org")
    sys.modules["org.latdraw"] = types.ModuleType("org.latdraw")
    sys.modules["org.latdraw.orderedset"] = orderedset