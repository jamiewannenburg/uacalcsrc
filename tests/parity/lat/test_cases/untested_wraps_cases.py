"""Parity cases for wrapped org.uacalc.lat constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.alg.op import Operations, OperationSymbol
from org.uacalc.lat import Lattices, BasicLattice

def _make_int_op(name, arity, size, table):
    make = getattr(Operations, "makeIntOperation", None)
    if make is None:
        make = Operations.make_int_operation
    return make(OperationSymbol(name, arity), size, table)

join2 = _make_int_op("v", 2, 2, [0, 1, 1, 1])
lat = Lattices.latticeFromJoin("chain2j", join2)
"""

_ALG = dict(skip_string_check=True, notes="Java lattice toString is Class@hex.")


def _c(cid, method, call, description, **kw):
    return TestCaseSpec(
        id=cid,
        method=method,
        setup=_SETUP,
        call=call,
        description=description,
        **kw
    )


TEST_CASES = [
    _c("ctor_basic_lattice", "BasicLattice.BasicLattice",
       "lat.cardinality()", "BasicLattice via latticeFromJoin", **_ALG),
    _c("ctor_basic_lattice_named", "BasicLattice.BasicLattice",
       "BasicLattice('C', lat.con(), False).cardinality()",
       "BasicLattice from Con(chain2) constructor", **_ALG),
]
