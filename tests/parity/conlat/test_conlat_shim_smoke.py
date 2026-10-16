"""Smoke tests for ``org.uacalc.alg.conlat`` shim (core-alg-conlat slice)."""

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


def test_org_uacalc_alg_conlat_import_smoke():
    _ensure_python_org_on_path()
    import org.uacalc.alg.conlat as cl  # noqa: PLC0415

    assert cl.__name__ == "org.uacalc.alg.conlat"


def test_conlat_shim_public_names_match_uacalc_lib():
    """``org.uacalc.alg.conlat`` re-exports partition types (Jython package path)."""
    _ensure_python_org_on_path()
    import org.uacalc.alg as alg  # noqa: PLC0415
    import org.uacalc.alg.conlat as shim  # noqa: PLC0415

    expected = (
        "Partition",
        "BasicPartition",
        "CongruenceLattice",
        "PrintType",
        "BinaryRelation",
        "BasicBinaryRelation",
        "CentralityData",
        "Polymorphisms",
        "Subtrace",
        "TypeFinder",
    )
    for name in expected:
        if not hasattr(alg, name) and name == "PrintType":
            continue
        assert hasattr(shim, name), name


def test_conlat_minimal_if_bindings():
    _ensure_python_org_on_path()
    import org.uacalc.alg.conlat as shim  # noqa: PLC0415

    BP = getattr(shim, "BasicPartition", None)
    if BP is None:
        pytest.skip("BasicPartition not exposed on org.uacalc.alg.conlat shim")
    z = BP.zero(3)
    assert z is not None
    assert int(z.universeSize()) == 3
    one = BP.one(3)
    j = z.join(one)
    assert str(j) == str(one)
