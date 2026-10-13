"""Smoke tests for ``org.uacalc.alg`` Algebra / SmallAlgebra / BasicAlgebra shim."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _ensure_python_org_on_path() -> None:
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


def test_org_uacalc_alg_import_smoke():
    _ensure_python_org_on_path()
    import org.uacalc.alg as alg  # noqa: PLC0415

    assert alg.__name__ == "org.uacalc.alg"
    assert hasattr(alg, "Algebra")
    assert hasattr(alg, "SmallAlgebra")
    assert hasattr(alg, "BasicAlgebra")
    assert alg.Algebra.CARDINALITY_UNKNOWN == -1
    assert str(alg.SmallAlgebra.AlgebraType.BASIC) == "BASIC"


def test_basic_algebra_int_constructor_and_instancecheck():
    _ensure_python_org_on_path()
    from org.uacalc.alg import Algebra, BasicAlgebra, SmallAlgebra  # noqa: PLC0415
    from org.uacalc.alg.op import Operations, OperationSymbol  # noqa: PLC0415

    op = Operations.makeIntOperation(OperationSymbol("id", 1), 2, [0, 1])
    alg = BasicAlgebra("Id2", 2, [op])
    assert isinstance(alg, BasicAlgebra)
    assert isinstance(alg, SmallAlgebra)
    assert isinstance(alg, Algebra)
    assert alg.getName() == "Id2"
    assert alg.cardinality() == 2
    assert str(alg.algebraType()) == "BASIC"
    assert alg.intUniverse() is True
    assert alg.getUniverseList() is None
    assert alg.getOperation(OperationSymbol("id", 1)).intValueAt([1]) == 1
