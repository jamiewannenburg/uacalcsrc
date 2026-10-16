"""Python-only: write then read of F(n) restores F(n)'s cardinality and tables.

Java AlgebraReader has no ``</freeAlgebra>`` handler (known Java bug), so these
checks are not dual-runtime golden cases. See KNOWN_DIFFERENCES.md.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
pytestmark = pytest.mark.behavioral


def _ensure_python_org_on_path() -> None:
    py_root = str(REPO_ROOT / "python")
    if py_root not in sys.path:
        sys.path.insert(0, py_root)


try:
    import uacalc_lib  # noqa: F401
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)

_ensure_python_org_on_path()


def _op_table(alg) -> list:
    ops = list(alg.operations())
    assert ops, "algebra has no operations"
    op = ops[0]
    n = int(alg.cardinality())
    ar = int(op.arity())
    iva = op.intValueAt if hasattr(op, "intValueAt") else op.int_value_at
    if ar == 0:
        return [int(iva([]))]
    if ar == 1:
        return [int(iva([i])) for i in range(n)]
    if ar == 2:
        return [int(iva([i, j])) for i in range(n) for j in range(n)]
    return []


@pytest.fixture(scope="module", autouse=True)
def _chdir_repo_root():
    old = os.getcwd()
    os.chdir(REPO_ROOT)
    yield
    os.chdir(old)


@pytest.mark.parametrize(
    "relpath,n_gens",
    [
        ("resources/algebras/cyclic2.ua", 1),
        ("resources/algebras/cyclic3.ua", 1),
        ("resources/algebras/lat2.ua", 1),
        ("resources/algebras/ba2.ua", 1),
    ],
)
def test_python_write_read_free_algebra_restores_fn(relpath, n_gens):
    from org.uacalc.alg import FreeAlgebra
    from org.uacalc.io import AlgebraIO

    base = AlgebraIO.readAlgebraFile(relpath)
    live = FreeAlgebra(base, n_gens)
    live.setName("F{0}".format(n_gens))
    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    try:
        AlgebraIO.writeAlgebraFile(live, path)
        read = AlgebraIO.readAlgebraFile(path)
    finally:
        os.unlink(path)

    assert int(read.cardinality()) == int(live.cardinality())
    assert _op_table(read) == _op_table(live)
