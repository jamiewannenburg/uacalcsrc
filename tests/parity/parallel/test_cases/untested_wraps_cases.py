"""Parity cases for wrapped org.uacalc.alg.parallel constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
import sys
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import BigProductAlgebra
from org.uacalc.alg.parallel import SingleClose
from org.uacalc.util import IntArray
from org.uacalc.terms import VariableImp
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
op = list(c2.operations())[0]
g1 = IntArray([1])
if sys.platform.startswith('java'):
    from java.util.concurrent import ConcurrentHashMap
    from java.util.concurrent.atomic import AtomicInteger
    mmap = ConcurrentHashMap()
    mmap.put(g1, VariableImp('x0'))
    sc = SingleClose([g1], mmap, op, 0, 0, AtomicInteger(1))
else:
    sc = SingleClose([g1], None, op, 0, 0, 1)

def _cls(o):
    n = type(o).__name__.split('.')[-1]
    if n.startswith('Py') and len(n) > 2:
        n = n[2:]
    return n
"""


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
    _c("ctor_single_close", "SingleClose.SingleClose",
       "_cls(sc)", "SingleClose constructor class name"),
]
