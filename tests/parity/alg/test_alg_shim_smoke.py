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


def test_product_power_quotient_subalgebra_constructors():
    _ensure_python_org_on_path()
    from org.uacalc.alg import (  # noqa: PLC0415
        Algebra,
        ProductAlgebra,
        PowerAlgebra,
        QuotientAlgebra,
        Subalgebra,
        SubProductAlgebra,
        BigProductAlgebra,
        SmallAlgebra,
    )
    from org.uacalc.io import AlgebraIO  # noqa: PLC0415

    c2 = AlgebraIO.readAlgebraFile(str(REPO_ROOT / "resources/algebras/cyclic2.ua"))
    prod = ProductAlgebra("C2xC2", [c2, c2])
    assert isinstance(prod, ProductAlgebra)
    assert isinstance(prod, SmallAlgebra)
    assert isinstance(prod, Algebra)
    assert prod.cardinality() == 4
    assert str(prod.algebraType()) == "PRODUCT"

    pwr = PowerAlgebra(c2, 2)
    assert isinstance(pwr, PowerAlgebra)
    assert pwr.getPower() == 2
    assert str(pwr.algebraType()) == "POWER"

    sub = Subalgebra("S", c2, [0])
    assert isinstance(sub, Subalgebra)
    assert sub.cardinality() == 1
    assert str(sub.algebraType()) == "SUBALGEBRA"

    cong = c2.con().Cg(0, 1)
    quot = QuotientAlgebra(c2, cong)
    assert isinstance(quot, QuotientAlgebra)
    assert quot.cardinality() == 1
    assert str(quot.algebraType()) == "QUOTIENT"

    bp = BigProductAlgebra(c2, 2)
    sp = SubProductAlgebra("SP", bp, [[0, 0], [1, 1]])
    assert isinstance(sp, SubProductAlgebra)
    assert sp.cardinality() == 2
    assert str(sp.algebraType()) == "SUBPRODUCT"


def test_free_hom_closer_algebras_constructors():
    _ensure_python_org_on_path()
    from org.uacalc.alg import (  # noqa: PLC0415
        FreeAlgebra,
        Homomorphism,
        Closer,
        Algebras,
        BigProductAlgebra,
        SmallAlgebra,
    )
    from org.uacalc.io import AlgebraIO  # noqa: PLC0415
    from org.uacalc.util import IntArray  # noqa: PLC0415

    c2 = AlgebraIO.readAlgebraFile(str(REPO_ROOT / "resources/algebras/cyclic2.ua"))
    f1 = FreeAlgebra(c2, 1)
    assert isinstance(f1, FreeAlgebra)
    assert isinstance(f1, SmallAlgebra)
    assert f1.cardinality() == 2
    assert str(f1.algebraType()) == "FREE"

    h = Homomorphism(c2, c2, {0: 0, 1: 1})
    assert isinstance(h, Homomorphism)
    assert str(h.kernel())

    bp = BigProductAlgebra(c2, 2)
    closer = Closer(bp, [IntArray([0, 0]), IntArray([1, 1])])
    assert isinstance(closer, Closer)
    assert closer.getAnswer() is None
    ans = closer.sgClose()
    assert ans is not None
    assert closer.getmaxSize() == -1

    trans = Algebras.fullTransformationSemigroup(2, False, False)
    assert trans.cardinality() == 4
    assert Algebras.unaryCloneAlgFromPartitions([c2.con().zero()], [c2.con().zero()]) is None
