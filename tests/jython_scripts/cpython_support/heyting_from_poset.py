"""``heyting_from_poset`` for CPython (Jamie ``phd_runtime/heyting_from_poset.py``)."""
from __future__ import annotations

from dmm import (
    AbstractOperation,
    BasicAlgebra,
    OperationSymbol,
    add_arrow_residuation,
    check_heyting,
    semi_lattice_maximal,
    semi_lattice_minimal,
)

from posets import get_upsets_lattice


def heyting_from_poset(po):
    lattice = get_upsets_lattice(po)
    join = lattice.getOperation(OperationSymbol("join", 2))
    meet = lattice.getOperation(OperationSymbol("meet", 2))

    class e_op(AbstractOperation):
        def intValueAt(self, args):
            return semi_lattice_maximal(lattice)

    e = e_op("e", 0, lattice.cardinality())

    class bot_op(AbstractOperation):
        def intValueAt(self, args):
            return semi_lattice_minimal(lattice)

    bot = bot_op("bot", 0, lattice.cardinality())

    alg = BasicAlgebra(lattice.getName() + "_*", lattice.cardinality(), [join, meet, e, bot])
    alg = add_arrow_residuation(alg, fusion_sym="meet")
    return alg


__all__ = ["heyting_from_poset", "check_heyting"]