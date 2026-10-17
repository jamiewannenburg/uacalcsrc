"""Python-only typed XML write/read roundtrips for several algebras.

Dual-runtime goldens still compare Java write-then-read. These checks prove
the Rust writers plus org rebuild restore cardinality, kind, and Horner tables
for products, powers, quotients, subalgebras, and subproducts.
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
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity" / "io"))
from io_parity_helpers import normalize_xml_text, semantic_algebra_summary


def _write_read(alg):
    from org.uacalc.io import AlgebraIO

    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    try:
        AlgebraIO.writeAlgebraFile(alg, path)
        with open(path) as handle:
            xml = handle.read()
        read = AlgebraIO.readAlgebraFile(path)
        return read, xml
    finally:
        os.unlink(path)


@pytest.fixture(scope="module", autouse=True)
def _chdir_repo_root():
    old = os.getcwd()
    os.chdir(REPO_ROOT)
    yield
    os.chdir(old)


@pytest.fixture(scope="module")
def algebras():
    from org.uacalc.alg import (
        BigProductAlgebra,
        PowerAlgebra,
        ProductAlgebra,
        QuotientAlgebra,
        Subalgebra,
        SubProductAlgebra,
    )
    from org.uacalc.io import AlgebraIO
    from org.uacalc.util import IntArray

    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
    return {
        "c2": c2,
        "c3": c3,
        "prod_c2_c2": ProductAlgebra([c2, c2]),
        "prod_c2_c3": ProductAlgebra([c2, c3]),
        "prod_c2_c3_c2": ProductAlgebra([c2, c3, c2]),
        "pwr_c2_2": PowerAlgebra(c2, 2),
        "pwr_c3_2": PowerAlgebra(c3, 2),
        "pwr_c2_3": PowerAlgebra(c2, 3),
        "quot_c2": QuotientAlgebra(c2, list(c2.con().universe())[0]),
        "quot_c3": QuotientAlgebra(c3, list(c3.con().universe())[0]),
        "sub_c2": Subalgebra(c2, [0]),
        "sub_c3": Subalgebra(c3, [0]),
        "sub_c2_full": Subalgebra(c2, [0, 1]),
        "subprod_c2": SubProductAlgebra(
            "SP", BigProductAlgebra(c2, 2), [IntArray([0, 0]), IntArray([1, 1])]
        ),
        "subprod_c3": SubProductAlgebra(
            "SP3", BigProductAlgebra(c3, 2), [IntArray([0, 0]), IntArray([1, 1])]
        ),
    }


@pytest.mark.parametrize(
    "key,tags",
    [
        ("prod_c2_c2", ("productAlgebra", "factors", "basicAlgebra")),
        ("prod_c2_c3", ("productAlgebra", "factors", "basicAlgebra")),
        ("prod_c2_c3_c2", ("productAlgebra", "factors", "basicAlgebra")),
        ("pwr_c2_2", ("powerAlgebra", "root", "basicAlgebra")),
        ("pwr_c3_2", ("powerAlgebra", "root", "basicAlgebra")),
        ("pwr_c2_3", ("powerAlgebra", "root", "basicAlgebra")),
        ("quot_c2", ("quotientAlgebra", "superAlgebra", "congruence")),
        ("quot_c3", ("quotientAlgebra", "superAlgebra", "congruence")),
        ("sub_c2", ("subAlgebra", "superAlgebra", "subUniverse")),
        ("sub_c3", ("subAlgebra", "superAlgebra", "subUniverse")),
        ("sub_c2_full", ("subAlgebra", "superAlgebra", "subUniverse")),
        ("subprod_c2", ("subProductAlgebra", "bigProductAlgebra", "generators")),
        ("subprod_c3", ("subProductAlgebra", "bigProductAlgebra", "generators")),
    ],
)
def test_python_write_read_typed_algebra(algebras, key, tags):
    live = algebras[key]
    read, xml = _write_read(live)
    for tag in tags:
        assert "<" + tag + ">" in xml
    live_sum = semantic_algebra_summary(live)
    read_sum = semantic_algebra_summary(read)
    assert read_sum["cardinality"] == live_sum["cardinality"]
    assert read_sum["symbols"] == live_sum["symbols"]
    assert read_sum["arities"] == live_sum["arities"]
    assert read_sum["tables"] == live_sum["tables"]


@pytest.mark.parametrize(
    "key,fixture",
    [
        ("prod_c2_c2", "resources/special/product_c2_c2.ua"),
        ("pwr_c2_2", "resources/special/power_c2_sq.ua"),
        ("quot_c2", "resources/special/quotient_example.ua"),
        ("sub_c2", "resources/special/subalgebra_example.ua"),
        ("subprod_c2", "resources/special/subproduct_c2.ua"),
    ],
)
def test_python_write_matches_java_special_fixture(algebras, key, fixture):
    from org.uacalc.io import AlgebraIO

    live = algebras[key]
    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    try:
        AlgebraIO.writeAlgebraFile(live, path)
        with open(path) as handle:
            written = handle.read()
    finally:
        os.unlink(path)
    with open(fixture) as handle:
        java_xml = handle.read()
    assert normalize_xml_text(written) == normalize_xml_text(java_xml)
